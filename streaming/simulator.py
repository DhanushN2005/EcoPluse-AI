import time
import random
import json
import os
from datetime import datetime
from ecopulse_ai.config import SIMULATOR_INTERVAL, DATA_DIR

def generate_sensor_data():
    """Simulates real-time environmental sensor data."""
    base_aqi = 60
    base_pm25 = 20
    base_co2 = 400
    
    while True:
        # Occasional spikes
        spike_factor = 5.0 if random.random() > 0.95 else 1.0
        
        data = {
            "timestamp": datetime.now().isoformat(),
            "aqi": float(max(0.0, base_aqi + random.uniform(-5, 5) * spike_factor)),
            "pm25": float(max(0.0, base_pm25 + random.uniform(-2, 2) * spike_factor)),
            "co2": float(max(0.0, base_co2 + random.uniform(-10, 10) * spike_factor)),
            "temp": 25.0 + random.uniform(-2, 2),
            "humidity": 50.0 + random.uniform(-5, 5),
            "wind_speed": 10.0 + random.uniform(-3, 3),
            "traffic_density": float(random.uniform(0, 100)),
            "industrial_emission": float(random.uniform(0, 50) * spike_factor)
        }
        
        # Write to a JSONL file that Pathway will watch
        log_file = os.path.join(DATA_DIR, "sensor_stream.jsonl")
        with open(log_file, "a") as f:
            f.write(json.dumps(data) + "\n")
            
        time.sleep(SIMULATOR_INTERVAL)

if __name__ == "__main__":
    print("Environmental Sensor Simulator Started...")
    generate_sensor_data()
