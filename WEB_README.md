# Agri Horizon web app

HTML, CSS and vanilla JavaScript frontend with a local Python prediction API. No Streamlit or Node build is needed.

From this directory:

```powershell
python -m pip install -r requirements-web.txt
python web_app.py
```

Open http://127.0.0.1:8000. Use `python web_app.py --port 8001` for another port. Open the server URL, not the HTML file directly.

The server resolves assets relative to its own file, so it can also be launched from another working directory. It binds to localhost and is intended for local use; public deployment needs a production server, access control and HTTPS.

## Connected predictions

- Credit scoring loads the existing `farmer_model.pkl` and `encoder.pkl`, preserves the feature order and binary mappings, and uses the default class's probability.
- Integrated assessment preserves the original Streamlit yield formula, income assumptions, thresholds and collateral factors. The yield formula is not a trained model. No additional notebook models are silently substituted or trained.
- CSV scoring accepts the seven model features, returns validation errors per row and exports scores with original CSV row numbers. Download a template in the app. Limit: 1,000 rows / 2 MB.
- Individual reports download as JSON, including inputs and a timestamp. Editing inputs clears stale results.

The interface shows empty results until a real API request succeeds. Missing or incompatible model files produce an explicit error. Only load trusted pickle artifacts.

## Visual assets

The mountain background is a real photograph downloaded from Unsplash (`photo-1464822759023-fed622ff2c3b`), stored locally in `web/mountains.jpg`. Source: https://images.unsplash.com/photo-1464822759023-fed622ff2c3b. Google Fonts enhance typography when online; local sans-serif fonts are the fallback. The photograph, UI and predictions work without an external image service at runtime.

## Verify

```powershell
python -m unittest test_web_app.py
node --check web/app.js
```
