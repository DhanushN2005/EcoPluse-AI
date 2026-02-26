from flask import Flask, render_template, jsonify, request
import requests
import os
import sys

# Ensure parent directory is in path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ecopulse_ai.config import STREAM_HOST, STREAM_PORT, OPENAI_API_KEY
from ecopulse_ai.analytics.alerts import get_alert_status
from ecopulse_ai.analytics.prediction import get_aqi_forecast
from ecopulse_ai.rag.copilot import ask_copilot

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/metrics')
def get_metrics():
    """Proxies and enhances metrics from the Pathway/Shim pipeline."""
    try:
        response = requests.get(f"http://{STREAM_HOST}:{STREAM_PORT}/health_metrics")
        data = response.json()
        if not data:
            return jsonify({"error": "No data available"}), 404
        
        latest = data[-1]
        alerts = get_alert_status(latest)
        
        # Get history for forecasting
        aqi_history = [d['aqi'] for d in data[-50:]]
        forecast = get_aqi_forecast(aqi_history)
        
        return jsonify({
            "latest": latest,
            "alerts": alerts,
            "forecast": forecast,
            "history": data[-50:]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    query = data.get('query')
    
    try:
        # Get current context for the LLM
        r = requests.get(f"http://{STREAM_HOST}:{STREAM_PORT}/health_metrics")
        latest_data = r.json()[-1] if r.json() else {}
        alerts = get_alert_status(latest_data)
        
        response = ask_copilot(query, latest_data, alerts)
        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
