# Anomaly detection logic
import numpy as np

def z_score_anomaly(value, mean, std):
    if std == 0: return False
    z = (value - mean) / std
    return abs(z) > 3.0

def detect_spikes(current, previous, threshold=50):
    return (current - previous) > threshold
