from datetime import datetime
import sys
import os

# Ensure parent directory is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import THRESHOLDS

def get_alert_status(current_data):
    """Checks current data against thresholds and returns active alerts."""
    alerts = []
    
    # AQI Check
    aqi = current_data.get('aqi', 0)
    if aqi >= THRESHOLDS["AQI"]["emergency"]:
        alerts.append({"type": "AQI", "level": "Emergency", "value": aqi, "msg": "Hazardous air quality! Immediate shelter advised."})
    elif aqi >= THRESHOLDS["AQI"]["critical"]:
        alerts.append({"type": "AQI", "level": "Critical", "value": aqi, "msg": "Very unhealthy air levels detected."})
    elif aqi >= THRESHOLDS["AQI"]["warning"]:
        alerts.append({"type": "AQI", "level": "Warning", "value": aqi, "msg": "Air quality is deteriorating."})

    # CO2 Check
    co2 = current_data.get('co2', 0)
    if co2 >= THRESHOLDS["CO2"]["warning"]:
        alerts.append({"type": "CO2", "level": "Warning", "value": co2, "msg": "High carbon dioxide levels. Ventilation needed."})

    return alerts
