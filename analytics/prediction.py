import numpy as np
import logging
from typing import List, Union
from sklearn.linear_model import LinearRegression

logger = logging.getLogger("Analytics-Prediction")

def get_aqi_forecast(history: List[float], n_steps: int = 5) -> Union[float, str]:
    """
    Predicts future AQI values using a linear regression model based on historical trends.
    
    Args:
        history (List[float]): A list of past AQI values.
        n_steps (int): The number of future steps to project (default: 5).
        
    Returns:
        Union[float, str]: The predicted AQI value or a status string if data is insufficient.
    """
    if len(history) < 5:
        logger.debug("Insufficient history data for accurate forecast.")
        return "Insufficient data"
    
    try:
        y = np.array(history).reshape(-1, 1)
        X = np.arange(len(history)).reshape(-1, 1)
        
        model = LinearRegression()
        model.fit(X, y)
        
        # Predict the next temporal step
        next_step = len(history)
        prediction = model.predict([[next_step]])[0][0]
        
        return round(float(prediction), 2)
    except Exception as e:
        logger.error(f"Prediction model failure: {e}")
        return "Prediction Error"

def calculate_volatility(history: List[float]) -> float:
    """
    Calculates the statistical volatility (standard deviation) of the historical data.
    
    Args:
        history (List[float]): A list of past AQI values.
        
    Returns:
        float: The calculated standard deviation.
    """
    if len(history) < 5: 
        return 0.0
    return float(np.std(history))
