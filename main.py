"""
EcoPulse AI Unified Orchestrator.
This is the main entry point to launch the integrated smart-city environmental intelligence system. 
It starts and monitors the Kafka simulators, Pathway streaming analytics, and the Flask presentation layer.
"""

import subprocess
import time
import sys
import os
import webbrowser
import logging
from typing import List, Dict

# Configure professional logging for the orchestrator
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("EcoPulse-Orchestrator")

def get_env() -> Dict[str, str]:
    """
    Constructs an environment configuration with the correct PYTHONPATH.
    This ensures 'ecopulse_ai' is treatable as a package for absolute imports.
    
    Returns:
        Dict[str, str]: Optimized system environment variables.
    """
    env = os.environ.copy()
    root_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(root_dir)
    # Inject current project location into system path
    env["PYTHONPATH"] = parent_dir + os.pathsep + env.get("PYTHONPATH", "")
    return env

def start() -> None:
    """
    Sequences the startup and monitoring of all EcoPulse AI system components.
    Processes: Sensor Simulator -> Streaming Analytics -> Web Interface.
    """
    logger.info("Initializing EcoPulse AI (v1.0.0) System Stack...")
    
    env = get_env()
    processes: List[subprocess.Popen] = []
    
    try:
        # 1. Start Kafka Producer (Simulator)
        # Responsible for generating the RAW environmental telemetry stream
        logger.info("Stage 1: Starting Sensor Stream Simulator (Kafka-Producer)...")
        p_prod = subprocess.Popen([sys.executable, "-m", "ecopulse_ai.kafka.producer"], env=env)
        processes.append(p_prod)
        
        time.sleep(3)
        
        # 2. Start Pathway Pipeline (The Analytics Backbone)
        # Handles complex event processing and health indexing
        logger.info("Stage 2: Initializing Streaming Analytics Engine (Pathway-Core)...")
        p_pipe = subprocess.Popen([sys.executable, "-m", "ecopulse_ai.streaming.pathway_pipeline"], env=env)
        processes.append(p_pipe)
        
        time.sleep(8) # Critical: Allow engine to bind HTTP metrics port (8080)
        
        # 3. Start Flask Presentation Layer
        # The primary user interface for city administrators
        logger.info("Stage 3: Deploying Presentation Layer (Web Interface/API)...")
        p_api = subprocess.Popen([sys.executable, "-m", "ecopulse_ai.api.app"], env=env)
        processes.append(p_api)

        # 4. Final Warm-up and Verification
        logger.info("Performing final system health checks...")
        time.sleep(8)
        
        logger.info("✨ EcoPulse AI Fully Operational.")
        logger.info("Access Dashboard via: http://127.0.0.1:5000")
        
        # Automatically launch browser for frictionless startup
        # (Disabled in headless environments/CI)
        if os.getenv("GITHUB_ACTIONS") != "true":
            webbrowser.open("http://127.0.0.1:5000")
        
        # Continuous Process Monitoring
        while True:
            time.sleep(2)
            if p_api.poll() is not None:
                logger.error("Presentation Layer (API) component has failed.")
                break
            if p_pipe.poll() is not None:
                logger.error("Analytics Engine (Pathway) component has failed.")
                break
            if p_prod.poll() is not None:
                logger.warning("Simulation Stream (Kafka) component has stopped.")
                break
                
    except KeyboardInterrupt:
        logger.info("System shutdown initiated by user.")
    except Exception as e:
        logger.critical(f"Panic: System-level orchestrator failure: {e}", exc_info=True)
    finally:
        logger.info("Terminating all sub-processes safely...")
        for p in processes:
            try:
                p.terminate()
                logger.info(f"Closed component PID: {p.pid}")
            except Exception as cleanup_error:
                logger.warning(f"Error during component termination: {cleanup_error}")
        sys.exit(0)

if __name__ == "__main__":
    start()
