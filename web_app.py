"""Local HTML application and prediction API. Run: python web_app.py."""
import argparse
import csv
import io
import json
import math
import pickle
from functools import lru_cache
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pandas as pd

BASE = Path(__file__).resolve().parent
FEATURES = ['region', 'coop_member', 'farm_size_hectares', 'primary_crop',
            'mobile_money_inflow', 'subsidy_status', 'loan_amount_requested']
REGIONS = ['Dodoma', 'Arusha', 'Mbeya', 'Morogoro', 'Mwanza']
CROPS = ['Maize', 'Cashew', 'Coffee', 'Rice']


@lru_cache(maxsize=1)
def models():
    with (BASE / 'farmer_model.pkl').open('rb') as file:
        model = pickle.load(file)
    with (BASE / 'encoder.pkl').open('rb') as file:
        encoder = pickle.load(file)
    return model, encoder


def number(data, key, low, high):
    try:
        value = float(data[key])
    except (KeyError, ValueError, TypeError):
        raise ValueError(f'{key}: enter a valid number.') from None
    if not math.isfinite(value) or not low <= value <= high:
        raise ValueError(f'{key}: must be between {low:g} and {high:g}.')
    return value


def credit(data):
    row = dict(data)
    for key, choices in [('region', REGIONS), ('primary_crop', CROPS)]:
        if row.get(key) not in choices:
            raise ValueError(f'{key}: choose one of {", ".join(choices)}.')
    mappings = {
        'coop_member': {'yes': 1, 'no': 0, 'true': 1, 'false': 0, '1': 1, '0': 0},
        'subsidy_status': {'received': 1, 'pending': 1, 'not received': 0,
                           'not_received': 0, '1': 1, '0': 0},
    }
    for key, mapping in mappings.items():
        value = str(row.get(key, '')).strip().lower()
        if value not in mapping:
            raise ValueError(f'{key}: unsupported value.')
        row[key] = mapping[value]
    for key, low, high in [('farm_size_hectares', .5, 20),
                           ('mobile_money_inflow', 0, 1e12),
                           ('loan_amount_requested', 100000, 1e12)]:
        row[key] = number(row, key, low, high)
    model, encoder = models()
    frame = pd.DataFrame([row], columns=FEATURES)
    index = list(model.classes_).index(1)
    probability = float(model.predict_proba(encoder.transform(frame))[0, index])
    risk = 'VERY_HIGH' if probability > .7 else 'HIGH' if probability > .5 else 'MEDIUM' if probability > .3 else 'LOW'
    return {'pd': probability, 'pd_pct': probability * 100,
            'risk_category': risk, 'expected_loss': probability * .45 * row['loan_amount_requested']}


def yield_estimate(data):
    rain = number(data, 'rainfall', 200, 1500)
    temp = number(data, 'temperature', 5, 35)
    ph = number(data, 'soil_ph', 4.5, 8.5)
    nitrogen = number(data, 'nitrogen', 20, 250)
    size = number(data, 'farm_size_hectares', .5, 20)
    predicted = min(12, max(.5, 3.5 - (rain - 650) ** 2 / 50000 / 500
                           - (temp - 22) ** 2 / 20 / 100
                           - (ph - 6.5) ** 2 / .5 / 10 + math.log(nitrogen + 1) * .8 / 100))
    income = predicted * size * 300000
    return {'predicted_yield': predicted, 'production': predicted * size,
            'farm_income': income, 'repayment_capacity': income * .35}


def assess(data, mode):
    if not isinstance(data, dict):
        raise ValueError('Expected a JSON object.')
    if mode == 'yield':
        return yield_estimate(data)
    result = credit(data)
    if mode == 'credit':
        return result
    result.update(yield_estimate(data))
    requested = float(data['loan_amount_requested'])
    recommended = min(requested, result['repayment_capacity'])
    decision = 'Approve' if result['pd_pct'] < 15 and recommended >= requested * .95 else 'Conditional approval' if result['pd_pct'] < 30 and recommended >= requested * .8 else 'Reject / restructure'
    result.update(recommended_loan=recommended, decision=decision,
                  collateral= recommended * {'LOW': 1.2, 'MEDIUM': 1.5, 'HIGH': 2, 'VERY_HIGH': 2.5}[result['risk_category']])
    return result


class Handler(BaseHTTPRequestHandler):
    def send(self, status, body, content_type='application/json; charset=utf-8'):
        raw = json.dumps(body, allow_nan=False).encode() if isinstance(body, dict) else body
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(raw)))
        self.send_header('Connection', 'close')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.end_headers()
        for offset in range(0, len(raw), 65536):
            self.wfile.write(raw[offset:offset + 65536])
        self.wfile.flush()

    def do_GET(self):
        path = self.path.split('?')[0]
        if path == '/api/health':
            try:
                models()
                self.send(200, {'ready': True})
            except Exception:
                self.send(503, {'ready': False, 'error': 'Credit model unavailable. Check model files and Python dependencies.'})
            return
        files = {'/': ('index.html', 'text/html; charset=utf-8'),
                 '/styles.css': ('styles.css', 'text/css; charset=utf-8'),
                 '/app.js': ('app.js', 'text/javascript; charset=utf-8'),
                 '/mountains.jpg': ('mountains.jpg', 'image/jpeg')}
        if path not in files:
            self.send(404, {'error': 'Not found.'})
            return
        name, mime = files[path]
        file = BASE / 'web' / name
        if not file.is_file():
            self.send(404, {'error': 'Asset not found.'})
            return
        self.send(200, file.read_bytes(), mime)

    def do_POST(self):
        if self.path not in ['/api/integrated', '/api/credit', '/api/yield', '/api/batch']:
            self.send(404, {'error': 'Not found.'})
            return
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if not 0 < length <= 2_000_000:
                raise ValueError('Request must be between 1 byte and 2 MB.')
            raw = self.rfile.read(length).decode('utf-8-sig')
            if self.path == '/api/batch':
                reader = csv.DictReader(io.StringIO(raw))
                if not set(FEATURES).issubset(reader.fieldnames or []):
                    raise ValueError('CSV must include: ' + ', '.join(FEATURES))
                rows = list(reader)
                if not 1 <= len(rows) <= 1000:
                    raise ValueError('Upload between 1 and 1,000 rows.')
                results = []
                for index, row in enumerate(rows, 2):
                    try:
                        results.append({'row': index, **credit(row)})
                    except ValueError as error:
                        results.append({'row': index, 'error': str(error)})
                self.send(200, {'results': results})
            else:
                self.send(200, assess(json.loads(raw), self.path.rsplit('/', 1)[1]))
        except (ValueError, UnicodeError) as error:
            self.send(400, {'error': str(error)})
        except Exception:
            self.log_error('Prediction failed; check model compatibility.')
            self.send(503, {'error': 'Prediction unavailable. Check model files and Python dependencies.'})


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8000)
    args = parser.parse_args()
    print(f'Agri Horizon: http://127.0.0.1:{args.port}', flush=True)
    ThreadingHTTPServer(('127.0.0.1', args.port), Handler).serve_forever()
