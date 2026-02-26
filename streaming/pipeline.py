import os
import json
import time
from datetime import datetime

try:
    import pathway as pw
    # Verify it's the real pathway by checking for essential submodules
    if not hasattr(pw, 'io') or not hasattr(pw, 'run'):
        raise ImportError("Real Pathway not detected")
    USE_PATHWAY = True
except (ImportError, RuntimeError):
    # Fallback for Windows environments without real Pathway
    USE_PATHWAY = False
    print("[WARN] Real Pathway not detected or incompatible. Using EcoPulse Stream Shim (Windows Compatibility).")

from ecopulse_ai.config import DATA_DIR, STREAM_PORT, STREAM_HOST
from ecopulse_ai.streaming.features import compute_health_score
from ecopulse_ai.analytics.alerts import classify_alert

def run_real_pipeline():
    """The original Pathway streaming logic."""
    import pathway as pw
    log_file = os.path.join(DATA_DIR, "sensor_stream.jsonl")
    
    raw_data = pw.io.jsonlines.read(
        log_file,
        schema=None,
        mode="streaming",
        autocommit_duration_ms=1000
    )

    stream = raw_data.select(
        timestamp=pw.this.timestamp,
        aqi=pw.cast(pw.this.aqi, pw.Type.FLOAT),
        pm25=pw.cast(pw.this.pm25, pw.Type.FLOAT),
        co2=pw.cast(pw.this.co2, pw.Type.FLOAT),
        temp=pw.cast(pw.this.temp, pw.Type.FLOAT),
        humidity=pw.cast(pw.this.humidity, pw.Type.FLOAT),
        wind_speed=pw.cast(pw.this.wind_speed, pw.Type.FLOAT),
        traffic_density=pw.cast(pw.this.traffic_density, pw.Type.FLOAT),
        industrial_emission=pw.cast(pw.this.industrial_emission, pw.Type.FLOAT)
    )

    health_stream = stream.select(
        pw.this.timestamp,
        pw.this.aqi,
        pw.this.pm25,
        pw.this.co2,
        pw.this.humidity,
        health_score=pw.apply(compute_health_score, pw.this.aqi, pw.this.pm25, pw.this.co2, pw.this.humidity)
    )

    # Rolling window
    rolling_metrics = stream.windowby(
        pw.temporal.sliding(pw.duration(seconds=30), step=pw.duration(seconds=1))
    ).reduce(
        timestamp=pw.reducers.max(pw.this.timestamp),
        avg_aqi=pw.reducers.avg(pw.this.aqi),
        avg_pm25=pw.reducers.avg(pw.this.pm25),
        avg_co2=pw.reducers.avg(pw.this.co2)
    )

    pw.io.http.expose(health_stream, host=STREAM_HOST, port=STREAM_PORT, endpoint="health_metrics")
    pw.io.http.expose(rolling_metrics, host=STREAM_HOST, port=STREAM_PORT, endpoint="rolling_metrics")

    pw.run()

def run_shim_pipeline():
    """Mocking Pathway's incremental computation logic for Windows."""
    from flask import Flask, jsonify
    import threading

    app = Flask("EcoPulse_Shim")
    log_file = os.path.join(DATA_DIR, "sensor_stream.jsonl")
    
    processed_count = 0
    stateful_data = []

    def update_loop():
        nonlocal processed_count
        while True:
            if os.path.exists(log_file):
                with open(log_file, "r") as f:
                    lines = f.readlines()
                    if len(lines) > processed_count:
                        for line in lines[processed_count:]:
                            try:
                                record = json.loads(line)
                                # Incremental computation
                                record['health_score'] = compute_health_score(
                                    record['aqi'], record['pm25'], record['co2'], record['humidity']
                                )
                                stateful_data.append(record)
                            except: pass
                        processed_count = len(lines)
            time.sleep(1)

    @app.route("/health_metrics")
    def get_health():
        return jsonify(stateful_data[-50:])

    @app.route("/rolling_metrics")
    def get_rolling():
        # Simple rolling mock
        if not stateful_data: return jsonify([])
        recent = stateful_data[-30:]
        summary = {
            "timestamp": recent[-1]['timestamp'],
            "avg_aqi": sum(d['aqi'] for d in recent) / len(recent),
            "avg_pm25": sum(d['pm25'] for d in recent) / len(recent)
        }
        return jsonify([summary])

    threading.Thread(target=update_loop, daemon=True).start()
    print(f"[SHIM] Serving EcoPulse Metrics at http://{STREAM_HOST}:{STREAM_PORT}")
    app.run(host=STREAM_HOST, port=STREAM_PORT, debug=False, use_reloader=False)

def run_pipeline():
    if USE_PATHWAY:
        run_real_pipeline()
    else:
        run_shim_pipeline()

if __name__ == "__main__":
    run_pipeline()
