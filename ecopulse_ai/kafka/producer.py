"""
EcoPulse AI Sensor Stream Simulator (Kafka Producer).
Simulates a multi-sensor environmental telemetry mesh and publishes high-fidelity
JSON data to the Apache Kafka broker.
"""

import json
import logging
import random
import time
from datetime import datetime
from typing import Any, Dict, Generator, Optional

from confluent_kafka import Message, Producer

from ecopulse_ai.config import KAFKA_BOOTSTRAP_SERVERS, KAFKA_TOPIC, SIMULATOR_INTERVAL

# Configure module-level logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("Kafka-Producer")


def delivery_report(err: Optional[Exception], msg: Message) -> None:
    """
    Reports the success or failure of a message delivery.

    Args:
        err (Optional[Exception]): The error if delivery failed.
        msg (Message): The Kafka message object.
    """
    if err is not None:
        logger.error(f"Message delivery failed: {err}")
    else:
        logger.debug(f"Message delivered to {msg.topic()} [{msg.partition()}]")


def generate_sensor_data() -> Generator[Dict[str, Any], None, None]:
    """
    Generates a continuous stream of realistic environmental sensor data using a random walk.

    Yields:
        Dict[str, Any]: A dictionary containing telemetry data.
    """
    # Initialize base values
    aqi = random.uniform(40, 60)
    pm25 = random.uniform(10, 25)
    co2 = random.uniform(380, 450)
    temp = random.uniform(22, 28)
    humidity = random.uniform(40, 60)
    wind_speed = random.uniform(5, 15)
    traffic = random.uniform(20, 40)
    industrial = random.uniform(10, 30)

    logger.info("Starting sensor data generation loop...")

    while True:
        # Apply random walk to simulate natural variance
        aqi += random.uniform(-2, 2)
        pm25 += random.uniform(-1, 1)
        co2 += random.uniform(-5, 5)
        temp += random.uniform(-0.1, 0.1)

        # Occasional spikes to simulate environmental incidents
        if random.random() < 0.05:
            aqi += random.uniform(30, 70)
            pm25 += random.uniform(20, 50)
            logger.warning("Simulated pollution spike detected in sensor stream.")

        # Bound values to realistic extremes
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
            "industrial_index": round(industrial, 2),
        }
        yield data
        time.sleep(SIMULATOR_INTERVAL)


def run_producer() -> None:
    """
    Connects to the Kafka broker and publishes simulated telemetry data.
    """
    logger.info(f"Initializing Kafka producer for topic: {KAFKA_TOPIC}")
    conf = {"bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS}

    try:
        producer = Producer(conf)
    except Exception as e:
        logger.critical(f"Failed to connect to Kafka at {KAFKA_BOOTSTRAP_SERVERS}: {e}")
        return

    try:
        for data in generate_sensor_data():
            producer.produce(
                KAFKA_TOPIC, key=str(time.time()), value=json.dumps(data), callback=delivery_report
            )
            producer.poll(0)
            logger.info(f"Sent Telemetry -> AQI: {data['aqi']} | CO2: {data['co2']}")
    except KeyboardInterrupt:
        logger.info("Producer shutting down by user request.")
    except Exception as e:
        logger.error(f"Production loop failed: {e}")
    finally:
        logger.info("Flushing Kafka producer...")
        producer.flush()


if __name__ == "__main__":
    run_producer()
