import csv
import io
import json
import threading
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from unittest.mock import patch

import pandas as pd
import web_app as app


PROFILE = dict(region='Dodoma', coop_member='Yes', farm_size_hectares=5,
               primary_crop='Maize', mobile_money_inflow=500000,
               subsidy_status='Pending', loan_amount_requested=2000000,
               rainfall=650, temperature=22, soil_ph=6.5, nitrogen=120)


class PredictionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = app.ThreadingHTTPServer(('127.0.0.1', 0), app.Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f'http://127.0.0.1:{cls.server.server_port}'

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def post(self, path, data):
        body = data.encode() if isinstance(data, str) else json.dumps(data).encode()
        try:
            with urlopen(Request(self.base + path, data=body), timeout=30) as response:
                return response.status, json.load(response)
        except HTTPError as error:
            with error:
                return error.code, json.load(error)

    def test_real_model_matches_direct_inference(self):
        row = {**PROFILE, 'coop_member': 1, 'subsidy_status': 1}
        model, encoder = app.models()
        expected = model.predict_proba(encoder.transform(pd.DataFrame([row], columns=app.FEATURES)))[0, list(model.classes_).index(1)]
        status, result = self.post('/api/integrated', PROFILE)
        self.assertEqual(status, 200)
        self.assertAlmostEqual(result['pd'], expected)
        self.assertAlmostEqual(result['expected_loss'], expected * .45 * 2000000)
        self.assertLessEqual(result['recommended_loan'], 2000000)
        self.assertEqual(result['recommended_loan'], min(2000000, result['farm_income'] * .35))

    def test_invalid_values_rejected(self):
        for field, value in [('region', 'Unknown'), ('coop_member', 'perhaps'),
                             ('loan_amount_requested', -1), ('rainfall', float('nan'))]:
            status, result = self.post('/api/integrated', {**PROFILE, field: value})
            self.assertEqual(status, 400)
            self.assertIn(field, result['error'])
        self.assertEqual(self.post('/api/credit', [1, 2])[0], 400)
        self.assertEqual(self.post('/api/credit', '{invalid')[0], 400)

    def test_yield_independent_of_credit_model(self):
        with patch.object(app, 'models', side_effect=FileNotFoundError):
            status, result = self.post('/api/yield', PROFILE)
            self.assertEqual(status, 200)
            self.assertGreater(result['predicted_yield'], 3)
            self.assertEqual(self.post('/api/credit', PROFILE)[0], 503)

    def test_csv_partial_errors_and_schema(self):
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=app.FEATURES, extrasaction='ignore')
        writer.writeheader()
        writer.writerow(PROFILE)
        writer.writerow({**PROFILE, 'region': 'Unknown'})
        status, result = self.post('/api/batch', output.getvalue())
        self.assertEqual(status, 200)
        self.assertIn('pd_pct', result['results'][0])
        self.assertEqual(result['results'][1]['row'], 3)
        self.assertIn('error', result['results'][1])
        self.assertEqual(self.post('/api/batch', 'region\nDodoma')[0], 400)

    def test_static_assets_and_health(self):
        for path in ['/', '/app.js', '/styles.css', '/mountains.jpg', '/api/health']:
            with urlopen(self.base + path) as response:
                self.assertEqual(response.status, 200)
                self.assertGreater(len(response.read()), 0)
        with self.assertRaises(HTTPError) as context:
            urlopen(self.base + '/farmer_model.pkl')
        self.assertEqual(context.exception.code, 404)
        context.exception.close()


if __name__ == '__main__':
    unittest.main()
