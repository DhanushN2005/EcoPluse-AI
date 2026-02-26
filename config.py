"""
Configuration management for the EcoPulse AI system.
This module handles environment variables, system constants, and directory initialization.
"""

import os
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# --- System Metadata ---
PROJECT_NAME: str = "EcoPulse AI"
VERSION: str = "1.0.0"
DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

# --- Kafka Broker Configuration ---
# The entry point for all environmental telemetry streams
KAFKA_BOOTSTRAP_SERVERS: str = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
KAFKA_TOPIC: str = "environmental_stream"

# --- Pathway & Streaming Engine ---
# Host and port for the sub-second analytics engine
STREAM_HOST: str = "127.0.0.1"
STREAM_PORT: int = 8080
SIMULATOR_INTERVAL: float = 1.0  # Seconds between sensor readings

# --- Presentation Layer (Flask API) ---
API_HOST: str = "0.0.0.0"
API_PORT: int = 5000

# --- AI Intelligence (OpenAI) ---
# SECURE: Always use environment variables for keys. 
# Do not hardcode secret keys in version control.
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "SECURE_KEY_PLACEHOLDER")

# --- Environmental Thresholds ---
# Defines the safety boundaries for city-wide alerts
THRESHOLDS: Dict[str, Dict[str, int]] = {
    "AQI": {"warning": 100, "critical": 200, "emergency": 300},
    "PM25": {"warning": 35, "critical": 75, "emergency": 150},
    "CO2": {"warning": 1000, "critical": 2000, "emergency": 5000}
}

# --- Filesystem Path Configuration ---
BASE_DIR: str = os.path.dirname(os.path.abspath(__file__))
DATA_DIR: str = os.path.join(BASE_DIR, "data")
REPORT_DIR: str = os.path.join(BASE_DIR, "reports_output")

# Ensure critical directories exist on startup
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)
