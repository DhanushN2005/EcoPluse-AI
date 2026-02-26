import json
import os
import sys
import time
import math
from datetime import datetime
from flask import Flask, jsonify, request
import threading
from confluent_kafka import Consumer, KafkaError

# Ensure parent directory is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import KAFKA_BOOTSTRAP_SERVERS, KAFKA_TOPIC, STREAM_HOST, STREAM_PORT, THRESHOLDS

# PATHWAY SHIM FOR WINDOWS
try:
    import pathway as pw
    if not hasattr(pw, 'Schema'): raise ImportError()
    USE_PATHWAY = True
except (ImportError, AttributeError):
    USE_PATHWAY = False

def calculate_analytics(record, history=None, simulation_params=None):
    """Core analytics logic combining OLD and NEW features."""
    aqi = record['aqi']
    co2 = record['co2']
    pm25 = record['pm25']
    traffic = record['traffic_density']
    industrial = record['industrial_index']
    wind = record['wind_speed']
    temp = record['temperature']
    humidity = record['humidity']

    # Apply simulation impact if provided (NEW)
    if simulation_params:
        traffic_reduction = float(simulation_params.get('traffic_reduction', 0)) / 100
        industrial_restriction = float(simulation_params.get('industrial_restriction', 0)) / 100
        green_cover_bonus = float(simulation_params.get('green_cover', 0)) / 100
        
        # Predictive impact
        aqi = aqi * (1 - (traffic_reduction * 0.4)) * (1 - (industrial_restriction * 0.5)) * (1 - (green_cover_bonus * 0.2))
        record['is_simulated'] = True
        record['aqi'] = round(aqi, 2)

    # 1. Root Cause Attribution Engine (NEW)
    traffic_coeff = traffic * 1.5
    industrial_coeff = industrial * 2.0
    dispersion_penalty = max(0, 15 - wind) * 5
    temp_inversion = max(0, temp - 25) * 2 if temp > 25 else 0
    total_impact = max(1, traffic_coeff + industrial_coeff + dispersion_penalty + temp_inversion)
    
    record['attribution'] = {
        "traffic": round((traffic_coeff / total_impact) * 100, 1),
        "industrial": round((industrial_coeff / total_impact) * 100, 1),
        "wind_impact": round((dispersion_penalty / total_impact) * 100, 1),
        "temp_inversion": round((temp_inversion / total_impact) * 100, 1)
    }

    # 2. Adaptive Alert Thresholds (NEW)
    hour = datetime.now().hour
    is_peak = (8 <= hour <= 10) or (17 <= hour <= 19)
    current_thresholds = THRESHOLDS["AQI"]["warning"] * (1.2 if is_peak else 1.0)
    
    record['severity'] = "Emergency" if aqi >= THRESHOLDS["AQI"]["emergency"] else \
                       "Critical" if aqi >= THRESHOLDS["AQI"]["critical"] else \
                       "Warning" if aqi >= current_thresholds else "Optimal"

    # 3. Carbon Footprint Estimator (NEW)
    record['carbon_footprint'] = {
        "traffic_load": round(traffic * 0.45, 2),
        "industrial_load": round(industrial * 1.2, 2),
        "total_equivalent": round((traffic * 0.45 + industrial * 1.2) * 24, 1)
    }

    # 4. Old Features: Momentum, Heat Index, Dispersion
    if history and len(history) > 1:
        record['aqi_momentum'] = round(aqi - history[-1]['aqi'], 2)
    else:
        record['aqi_momentum'] = 0.0

    record['heat_pollution_index'] = round(temp * aqi / 100, 2)
    record['dispersion_factor'] = round(10.0 / (wind + 1.0), 2)
    
    # Simple Volatility (Std Dev of last 10)
    if history and len(history) >= 10:
        recent_aqi = [h['aqi'] for h in history[-10:]] + [aqi]
        mean = sum(recent_aqi) / len(recent_aqi)
        var = sum((x - mean)**2 for x in recent_aqi) / len(recent_aqi)
        record['volatility'] = round(math.sqrt(var), 2)
    else:
        record['volatility'] = 0.0

    # 5. Composite Health Score
    record['health_score'] = max(0, 100 - (aqi/5 + co2/50 + pm25/2))
    
    return record

def run_shim_pipeline():
    app = Flask("Pathway_Shim")
    state = {"data": []}

    def kafka_loop():
        conf = {
            'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
            'group.id': 'pathway-shim-group',
            'auto.offset.reset': 'latest'
        }
        consumer = Consumer(conf)
        consumer.subscribe([KAFKA_TOPIC])

        print(f"[SHIM] Consuming from Kafka: {KAFKA_TOPIC}")
        while True:
            msg = consumer.poll(1.0)
            if msg is None: continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF: continue
                else: print(msg.error()); break

            try:
                record = json.loads(msg.value().decode('utf-8'))
                # Pass state["data"] (history) to calculate analytics
                record = calculate_analytics(record, history=state["data"])
                
                state["data"].append(record)
                if len(state["data"]) > 100: state["data"].pop(0)
            except Exception as e:
                print(f"[SHIM ERROR] {e}")

    @app.route("/")
    def shim_index():
        return "EcoPulse AI Pathway Shim is Active. Metrics at /environmental_metrics"

    @app.route("/environmental_metrics")
    def get_metrics():
        sim_traffic = request.args.get('traffic_reduction')
        if sim_traffic and state["data"]:
            sim_params = request.args
            latest = state["data"][-1].copy()
            simulated = calculate_analytics(latest, history=state["data"], simulation_params=sim_params)
            return jsonify([simulated])
            
        return jsonify(state["data"])

    @app.route("/district_comparison")
    def get_district_comparison():
        if not state["data"]: return jsonify({})
        latest = state["data"][-1]
        
        # Simulate 4 major districts with variations
        districts = [
            {"name": "Central Business District", "aqi": latest['aqi'], "vulnerability": "High", "risk": "Traffic", "trend": "Rising"},
            {"name": "Industrial North", "aqi": round(latest['aqi'] * 1.3, 2), "vulnerability": "Critical", "risk": "Industrial", "trend": "Stable"},
            {"name": "Residential South", "aqi": round(latest['aqi'] * 0.7, 2), "vulnerability": "Low", "risk": "Dust", "trend": "Falling"},
            {"name": "Green Belt West", "aqi": round(latest['aqi'] * 0.5, 2), "vulnerability": "Minimal", "risk": "None", "trend": "Optimal"}
        ]
        return jsonify(districts)

    @app.route("/national_metrics")
    def get_national_metrics():
        if not state["data"]: return jsonify([])
        latest_aqi = state["data"][-1]['aqi']
        
        states = [
            {"id": "IN-MH", "name": "Maharashtra", "aqi": round(latest_aqi * 1.1, 2)},
            {"id": "IN-DL", "name": "Delhi", "aqi": round(latest_aqi * 1.8, 2)},
            {"id": "IN-KA", "name": "Karnataka", "aqi": round(latest_aqi * 0.8, 2)},
            {"id": "IN-TN", "name": "Tamil Nadu", "aqi": round(latest_aqi * 0.7, 2)},
            {"id": "IN-WB", "name": "West Bengal", "aqi": round(latest_aqi * 1.4, 2)},
            {"id": "IN-UP", "name": "Uttar Pradesh", "aqi": round(latest_aqi * 1.6, 2)},
            {"id": "IN-GJ", "name": "Gujarat", "aqi": round(latest_aqi * 1.2, 2)},
            {"id": "IN-RJ", "name": "Rajasthan", "aqi": round(latest_aqi * 1.3, 2)},
            {"id": "IN-TS", "name": "Telangana", "aqi": round(latest_aqi * 0.9, 2)},
            {"id": "IN-KL", "name": "Kerala", "aqi": round(latest_aqi * 0.5, 2)}
        ]
        return jsonify(states)

    threading.Thread(target=kafka_loop, daemon=True).start()
    print(f"[SHIM] Serving Metrics at http://{STREAM_HOST}:{STREAM_PORT}/environmental_metrics")
    app.run(host=STREAM_HOST, port=STREAM_PORT, debug=False, use_reloader=False)

if __name__ == "__main__":
    run_shim_pipeline()
