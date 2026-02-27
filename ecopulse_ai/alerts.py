import logging
from typing import List, Dict, Any
from ecopulse_ai.config import THRESHOLDS

logger = logging.getLogger("Analytics-Alerts")


def get_alert_status(current_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Evaluates current environmental telemetry against predefined safety thresholds.

    Args:
        current_data (Dict[str, Any]): Dictionary containing sensor readings (aqi, co2, etc.).

    Returns:
        List[Dict[str, Any]]: A list of active alert dictionaries with severity and recommendations.
    """
    alerts: List[Dict[str, Any]] = []

    # Air Quality Index (AQI) Evaluation
    aqi = float(current_data.get("aqi", 0))
    if aqi >= THRESHOLDS["AQI"]["emergency"]:
        alerts.append(
            {
                "type": "AQI",
                "level": "Emergency",
                "value": aqi,
                "msg": "Hazardous air quality! Immediate shelter advised. Cease all outdoor activities.",
            }
        )
    elif aqi >= THRESHOLDS["AQI"]["critical"]:
        alerts.append(
            {
                "type": "AQI",
                "level": "Critical",
                "value": aqi,
                "msg": "Very unhealthy air levels detected. High-risk groups should remain indoors.",
            }
        )
    elif aqi >= THRESHOLDS["AQI"]["warning"]:
        alerts.append(
            {
                "type": "AQI",
                "level": "Warning",
                "value": aqi,
                "msg": "Air quality is deteriorating. Moderate health risks for sensitive individuals.",
            }
        )

    # Carbon Dioxide (CO2) Evaluation
    co2 = float(current_data.get("co2", 0))
    if co2 >= THRESHOLDS["CO2"]["warning"]:
        alerts.append(
            {
                "type": "CO2",
                "level": "Warning",
                "value": co2,
                "msg": "High carbon dioxide levels detected. Ventilation and air circulation required.",
            }
        )

    logger.debug(f"Calculated {len(alerts)} active alerts for current data state.")
    return alerts
