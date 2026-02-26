import os
from dotenv import load_dotenv

load_dotenv()

# System Config
PROJECT_NAME = "EcoPulse AI"
DEBUG = True

# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
KAFKA_TOPIC = "environmental_stream"

# Pathway & Streaming
STREAM_HOST = "127.0.0.1"
STREAM_PORT = 8080
SIMULATOR_INTERVAL = 1.0  # seconds

# API & Server
API_HOST = "0.0.0.0"
API_PORT = 5000

# LLM Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "sxxxxxxxxxxxxxxxxxxxxxx")
# Environmental Thresholds
THRESHOLDS = {
    "AQI": {"warning": 100, "critical": 200, "emergency": 300},
    "PM25": {"warning": 35, "critical": 75, "emergency": 150},
    "CO2": {"warning": 1000, "critical": 2000, "emergency": 5000}
}

# Path Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
REPORT_DIR = os.path.join(BASE_DIR, "reports_output")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)
