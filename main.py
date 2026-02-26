import subprocess
import time
import sys
import os
import webbrowser
import logging
from typing import List, Dict

# Configure professional logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("EcoPulse-Orchestrator")

def get_env() -> Dict[str, str]:
    """
    Environment with correct PYTHONPATH to treat 'ecopulse_ai' as a package.
    
    Returns:
        Dict[str, str]: A copy of the system environment with updated PYTHONPATH.
    """
    env = os.environ.copy()
    root_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(root_dir)
    env["PYTHONPATH"] = parent_dir + os.pathsep + env.get("PYTHONPATH", "")
    return env

def start() -> None:
    """
    Starts the EcoPulse AI system components in orchestrated sequence.
    """
    logger.info("Initializing EC-PULSE AI System Components...")
    
    env = get_env()
    processes: List[subprocess.Popen] = []
    
    try:
        # 1. Start Kafka Producer (Simulator)
        logger.info("Starting Sensor Stream Simulator (Kafka Producer)...")
        p_prod = subprocess.Popen([sys.executable, "-m", "ecopulse_ai.kafka.producer"], env=env)
        processes.append(p_prod)
        
        time.sleep(3)
        
        # 2. Start Pathway Pipeline (Handles real OR shim automatically)
        logger.info("Starting Streaming Analytics Engine (Pathway/Shim)...")
        p_pipe = subprocess.Popen([sys.executable, "-m", "ecopulse_ai.streaming.pathway_pipeline"], env=env)
        processes.append(p_pipe)
        
        time.sleep(8) # Allow time for Shim/Pathway to bind port 8080
        
        # 3. Start Flask API
        logger.info("Starting Presentation Layer (Flask API on Port 5000)...")
        p_api = subprocess.Popen([sys.executable, "-m", "ecopulse_ai.api.app"], env=env)
        processes.append(p_api)

        # 4. Wait for API to warm up
        logger.info("System warm-up phase in progress...")
        time.sleep(8)
        
        logger.info("EcoPulse AI is now operational.")
        logger.info(">> Administrative Dashboard: http://127.0.0.1:5000")
        
        # Open browser automatically for better user experience
        webbrowser.open("http://127.0.0.1:5000")
        
        # Monitor processes for health
        while True:
            time.sleep(1)
            if p_api.poll() is not None:
                logger.error("Presentation Layer (Web Interface) terminated unexpectedly.")
                break
            if p_pipe.poll() is not None:
                logger.error("Analytics Engine terminated unexpectedly.")
                break
                
    except KeyboardInterrupt:
        logger.info("Shutdown signal received. Terminating system components...")
    except Exception as e:
        logger.critical(f"System-level failure detected: {e}", exc_info=True)
    finally:
        for p in processes:
            try:
                p.terminate()
                logger.debug(f"Process {p.pid} terminated.")
            except Exception as cleanup_error:
                logger.warning(f"Error while terminating process: {cleanup_error}")
        sys.exit(0)

if __name__ == "__main__":
    start()

if __name__ == "__main__":
    start()
