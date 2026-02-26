import json
import time
import random
from datetime import datetime
from confluent_kafka import Producer
import sys
import os

# Ensure parent directory is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import KAFKA_BOOTSTRAP_SERVERS, KAFKA_TOPIC, SIMULATOR_INTERVAL

def delivery_report(err, msg):
    if err is not None:
        print(f'[ERROR] Message delivery failed: {err}')
    else:
        pass # Successful delivery

def generate_sensor_data():
    """Generates realistic environmental sensor data."""
    # Base values
    aqi = random.uniform(40, 60)
    pm25 = random.uniform(10, 25)
    co2 = random.uniform(380, 450)
    temp = random.uniform(22, 28)
    humidity = random.uniform(40, 60)
    wind_speed = random.uniform(5, 15)
    traffic = random.uniform(20, 40)
    industrial = random.uniform(10, 30)

    while True:
        # Add random walk
        aqi += random.uniform(-2, 2)
        pm25 += random.uniform(-1, 1)
        co2 += random.uniform(-5, 5)
        temp += random.uniform(-0.1, 0.1)
        
        # Occasional spikes
        if random.random() < 0.05:
            aqi += random.uniform(30, 70)
            pm25 += random.uniform(20, 50)
            print("[SPIKE] Pollution spike detected!")

        # Keep within bounds
        aqi = max(10, min(500, aqi))
        pm25 = max(1, min(300, pm25))
        co2 = max(300, min(2000, co2))

        data = {
            "timestamp": datetime.now().isoformat(),
            "aqi": round(aqi, 2),
            "pm25": round(pm25, 2),
            "co2": round(co2, 2),
            "temperature": round(temp, 2),
            "humidity": round(humidity, 2),
            "wind_speed": round(wind_speed, 2),
            "traffic_density": round(traffic, 2),
            "industrial_index": round(industrial, 2)
        }
        yield data
        time.sleep(SIMULATOR_INTERVAL)

def run_producer():
    print(f"[KAFKA] Starting producer for topic: {KAFKA_TOPIC}")
    conf = {'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS}
    
    try:
        producer = Producer(conf)
    except Exception as e:
        print(f"[ERROR] Failed to connect to Kafka: {e}")
        print("[INFO] Make sure Kafka is running at localhost:9092")
        return

    for data in generate_sensor_data():
        try:
            producer.produce(
                KAFKA_TOPIC, 
                key=str(time.time()), 
                value=json.dumps(data),
                callback=delivery_report
            )
            producer.poll(0)
            print(f"[SENT] AQI: {data['aqi']} | CO2: {data['co2']}")
        except Exception as e:
            print(f"[ERROR] Production failed: {e}")
            break

if __name__ == "__main__":
    run_producer()
