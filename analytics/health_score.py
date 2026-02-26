def calculate_composite_health(aqi, co2, pm25, hum):
    """Calculates an environmental health score from 0-100."""
    # Penalty weights
    aqi_penalty = (max(0, aqi - 50) / 300) * 40
    co2_penalty = (max(0, co2 - 400) / 1000) * 30
    pm25_penalty = (max(0, pm25 - 15) / 100) * 30
    
    score = 100 - (aqi_penalty + co2_penalty + pm25_penalty)
    return max(0, min(100, round(score, 1)))
