"""
EcoPulse AI Streaming Analytics Engine.
Handles real-time environmental data processing using either Pathway (for production)
or a lightweight Flask-based Shim (for Windows/local development).
"""

import json
import logging
import math
import os
import threading
from datetime import datetime
from typing import Any, Dict, List, Optional

from confluent_kafka import Consumer, KafkaError
from flask import Flask, Response, jsonify, request

from ecopulse_ai.config import (
    KAFKA_BOOTSTRAP_SERVERS,
    KAFKA_TOPIC,
    STREAM_HOST,
    STREAM_PORT,
    THRESHOLDS,
)

# Configure module-level logging
logger = logging.getLogger("Pathway-Pipeline")


def apply_simulation(aqi: float, params: Dict[str, Any]) -> float:
    """
    Predictively adjusts AQI based on hypothetical urban planning simulations.

    Args:
        aqi (float): The baseline AQI.
        params (Dict[str, Any]): Simulation coefficients (traffic, industrial, green cover).

    Returns:
        float: The simulated AQI value.
    """
    traffic_reduction = float(params.get("traffic_reduction", 0)) / 100
    industrial_restriction = float(params.get("industrial_restriction", 0)) / 100
    green_cover_bonus = float(params.get("green_cover", 0)) / 100

    # Business Logic: Weights for predictive AQI improvement
    impacted_aqi = aqi * (1 - (traffic_reduction * 0.4))
    impacted_aqi *= 1 - (industrial_restriction * 0.5)
    impacted_aqi *= 1 - (green_cover_bonus * 0.2)
    return round(impacted_aqi, 2)


def compute_attribution(
    traffic: float, industrial: float, wind: float, temp: float
) -> Dict[str, float]:
    """
    Identifies the primary sources of environmental pollution based on telemetry.
    """
    traffic_coeff = traffic * 1.5
    industrial_coeff = industrial * 2.0
    dispersion_penalty = max(0, 15 - wind) * 5
    temp_inversion = max(0, temp - 25) * 2 if temp > 25 else 0

    total_impact = max(1, traffic_coeff + industrial_coeff + dispersion_penalty + temp_inversion)

    return {
        "traffic": round((traffic_coeff / total_impact) * 100, 1),
        "industrial": round((industrial_coeff / total_impact) * 100, 1),
        "wind_impact": round((dispersion_penalty / total_impact) * 100, 1),
        "temp_inversion": round((temp_inversion / total_impact) * 100, 1),
    }


def compute_alerts(aqi: float) -> str:
    """
    Determines the safety severity level based on AQI and peak-hour adjustments.
    """
    hour = datetime.now().hour
    is_peak = (8 <= hour <= 10) or (17 <= hour <= 19)
    # Apply a 20% stricter threshold during peak transit hours
    warning_threshold = THRESHOLDS["AQI"]["warning"] * (1.2 if is_peak else 1.0)

    if aqi >= THRESHOLDS["AQI"]["emergency"]:
        return "Emergency"
    if aqi >= THRESHOLDS["AQI"]["critical"]:
        return "Critical"
    if aqi >= warning_threshold:
        return "Warning"
    return "Optimal"


def compute_carbon_footprint(traffic: float, industrial: float) -> Dict[str, float]:
    """
    Estimates the carbon output based on sensor inputs.
    """
    return {
        "traffic_load": round(traffic * 0.45, 2),
        "industrial_load": round(industrial * 1.2, 2),
        "total_equivalent": round((traffic * 0.45 + industrial * 1.2) * 24, 1),
    }


def calculate_analytics(
    record: Dict[str, Any],
    history: Optional[List[Dict[str, Any]]] = None,
    simulation_params: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Orchestrates the full analytical transformation of a raw sensor record.
    """
    # Defensive type conversion
    try:
        aqi = float(record.get("aqi", 0))
        co2 = float(record.get("co2", 0))
        pm25 = float(record.get("pm25", 0))
        traffic = float(record.get("traffic_density", 0))
        industrial = float(record.get("industrial_index", 0))
        wind = float(record.get("wind_speed", 0))
        temp = float(record.get("temperature", 0))
        humidity = float(record.get("humidity", 0))
    except (ValueError, TypeError) as e:
        logger.error(f"Integrity error in sensor record: {e}")
        return record

    # Apply Simulation Shifting
    if simulation_params:
        aqi = apply_simulation(aqi, simulation_params)
        record["is_simulated"] = True
        record["aqi"] = aqi

    # Core Analytics
    record["attribution"] = compute_attribution(traffic, industrial, wind, temp)
    record["severity"] = compute_alerts(aqi)
    record["carbon_footprint"] = compute_carbon_footprint(traffic, industrial)

    # Momentum & Spatiotemporal Trends
    if history and len(history) > 0:
        record["aqi_momentum"] = round(aqi - history[-1].get("aqi", aqi), 2)
    else:
        record["aqi_momentum"] = 0.0

    record["heat_pollution_index"] = round(temp * aqi / 100, 2)
    record["dispersion_factor"] = round(10.0 / (wind + 1.0), 2)

    # Statistical Volatility
    if history and len(history) >= 10:
        recent_aqi = [h.get("aqi", 0) for h in history[-10:]] + [aqi]
        mean = sum(recent_aqi) / len(recent_aqi)
        var = sum((x - mean) ** 2 for x in recent_aqi) / len(recent_aqi)
        record["volatility"] = round(math.sqrt(var), 2)
    else:
        record["volatility"] = 0.0

    # Composite Health Index (EHS)
    record["health_score"] = max(0, 100 - (aqi / 5 + co2 / 50 + pm25 / 2))

    return record


def run_shim_pipeline() -> None:
    """
    Initializes and starts the Flask-based Windows Shim for the Pathway engine.
    """
    app = Flask("Pathway_Shim")
    state: Dict[str, List[Dict[str, Any]]] = {"data": []}

    def kafka_consumer_worker() -> None:
        """Background thread for non-blocking Kafka ingestion."""
        conf = {
            "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS,
            "group.id": "pathway-shim-group",
            "auto.offset.reset": "latest",
        }
        try:
            consumer = Consumer(conf)
            consumer.subscribe([KAFKA_TOPIC])
            logger.info("Kafka Connection established. Listening for telemetry...")
        except Exception as e:
            logger.critical(f"Failed to initialize Kafka Consumer: {e}")
            return

        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() != KafkaError._PARTITION_EOF:
                    logger.error(f"Kafka transport error: {msg.error()}")
                continue

            try:
                record = json.loads(msg.value().decode("utf-8"))
                enriched = calculate_analytics(record, history=state["data"])
                state["data"].append(enriched)

                # Keep state bounded to prevent memory leaks
                if len(state["data"]) > 100:
                    state["data"].pop(0)
            except Exception as e:
                logger.error(f"Analytical processing failure: {e}")

    @app.route("/")
    def status() -> str:
        return "EcoPulse AI Analytics Engine: Active"

    @app.route("/environmental_metrics")
    def get_metrics() -> Response:
        """Fetches telemetry with optional on-the-fly simulation support."""
        if request.args.get("traffic_reduction") and state["data"]:
            simulated = calculate_analytics(
                state["data"][-1].copy(), history=state["data"], simulation_params=request.args
            )
            return jsonify([simulated])
        return jsonify(state["data"])

    @app.route("/district_comparison")
    def get_district_comparison() -> Response:
        if not state["data"]:
            return jsonify([])
        latest = state["data"][-1]
        base = float(latest.get("aqi", 0))
        return jsonify(
            [
                {
                    "name": "Central Business District",
                    "aqi": base,
                    "vulnerability": "High",
                    "risk": "Traffic",
                    "trend": "Rising",
                },
                {
                    "name": "Industrial North",
                    "aqi": round(base * 1.3, 2),
                    "vulnerability": "Critical",
                    "risk": "Industrial",
                    "trend": "Stable",
                },
                {
                    "name": "Residential South",
                    "aqi": round(base * 0.7, 2),
                    "vulnerability": "Low",
                    "risk": "Dust",
                    "trend": "Falling",
                },
                {
                    "name": "Green Belt West",
                    "aqi": round(base * 0.5, 2),
                    "vulnerability": "Minimal",
                    "risk": "None",
                    "trend": "Optimal",
                },
            ]
        )

    @app.route("/national_metrics")
    def get_national_metrics() -> Response:
        if not state["data"]:
            return jsonify([])
        base = float(state["data"][-1].get("aqi", 0))
        return jsonify(
            [
                {"id": "IN-MH", "name": "Maharashtra", "aqi": round(base * 1.1, 2)},
                {"id": "IN-DL", "name": "Delhi", "aqi": round(base * 1.8, 2)},
                {"id": "IN-KA", "name": "Karnataka", "aqi": round(base * 0.8, 2)},
                {"id": "IN-KL", "name": "Kerala", "aqi": round(base * 0.5, 2)},
            ]
        )

    threading.Thread(target=kafka_consumer_worker, daemon=True).start()
    app.run(host=STREAM_HOST, port=STREAM_PORT, debug=False, use_reloader=False)


if __name__ == "__main__":
    run_shim_pipeline()
