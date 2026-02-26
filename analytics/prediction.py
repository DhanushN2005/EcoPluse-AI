import numpy as np
from sklearn.linear_model import LinearRegression

def get_aqi_forecast(history, n_steps=5):
    """Predicts next AQI values based on linear regression of history."""
    if len(history) < 5:
        return "Insufficient data"
    
    y = np.array(history).reshape(-1, 1)
    X = np.arange(len(history)).reshape(-1, 1)
    
    model = LinearRegression()
    model.fit(X, y)
    
    # Predict next step
    next_step = len(history)
    prediction = model.predict([[next_step]])[0][0]
    
    return round(prediction, 2)

def calculate_volatility(history):
    if len(history) < 5: return 0.0
    return np.std(history)
