import logging

logger = logging.getLogger("Analytics-Health")

def calculate_composite_health(aqi: float, co2: float, pm25: float, hum: float) -> float:
    """
    Calculates a composite Environmental Health Score (EHS) from 0 to 100.
    
    The score is weighted based on the severity of different pollutants:
    - AQI: 40% weight
    - CO2: 30% weight
    - PM2.5: 30% weight
    
    Args:
        aqi (float): Air Quality Index reading.
        co2 (float): Carbon Dioxide levels in ppm.
        pm25 (float): Particulate Matter 2.5 concentration.
        hum (float): Relative humidity percentage.
        
    Returns:
        float: A value between 0.0 (Hazardous) and 100.0 (Optimal).
    """
    # Calculate weighted penalties for exceeding baseline 'safe' levels
    aqi_penalty = (max(0, float(aqi) - 50) / 300) * 40
    co2_penalty = (max(0, float(co2) - 400) / 1000) * 30
    pm25_penalty = (max(0, float(pm25) - 15) / 100) * 30
    
    score = 100.0 - (aqi_penalty + co2_penalty + pm25_penalty)
    
    # Boundary enforcement
    final_score = max(0.0, min(100.0, round(score, 1)))
    logger.debug(f"Computed Health Score: {final_score} (AQI: {aqi}, CO2: {co2}, PM25: {pm25})")
    
    return final_score
