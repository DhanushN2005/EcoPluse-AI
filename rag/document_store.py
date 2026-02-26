# Simple knowledge base for environmental guidelines
GUIDELINES = {
    "AQI_MODERATE": "Keep windows closed if possible. Use air purifiers.",
    "AQI_UNHEALTHY": "Avoid outdoor exercise. Mask up if going outside.",
    "CO2_HIGH": "Increase ventilation. Open windows for 10 minutes.",
    "HEAT_WAVE": "Stay hydrated. Keep indoors. Use fans/AC."
}

def get_guideline(key):
    return GUIDELINES.get(key, "Follow standard safety protocols.")
