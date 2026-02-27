"""
EcoPulse AI Unified Orchestrator.

Main entry point for launching the integrated smart-city
environmental intelligence system.
"""

import subprocess
import time
import sys
import os
import webbrowser
import logging
from typing import List, Dict

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("EcoPulse-Orchestrator")


def get_env() -> Dict[str, str]:
    """
    Construct environment variables with correct PYTHONPATH
    so ecopulse_ai is resolvable as a package.
    """
    env = os.environ.copy()
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    env["PYTHONPATH"] = project_root + os.pathsep + env.get("PYTHONPATH", "")
    return env


def main() -> None:
    """
    Launch and supervise all EcoPulse AI system components.
    """
    logger.info("Initializing EcoPulse AI (v1.0.0) System Stack...")
    env = get_env()
    processes: List[subprocess.Popen] = []

    try:
        logger.info("Stage 1: Starting Kafka Sensor Simulator...")
        p_prod = subprocess.Popen(
            [sys.executable, "-m", "ecopulse_ai.kafka.producer"], env=env
        )
        processes.append(p_prod)
        time.sleep(3)

        logger.info("Stage 2: Starting Pathway Streaming Engine...")
        p_pipe = subprocess.Popen(
            [sys.executable, "-m", "ecopulse_ai.streaming.pathway_pipeline"], env=env
        )
        processes.append(p_pipe)
        time.sleep(8)

        logger.info("Stage 3: Launching Flask Web Interface...")
        p_api = subprocess.Popen(
            [sys.executable, "-m", "ecopulse_ai.api.app"], env=env
        )
        processes.append(p_api)

        logger.info("EcoPulse AI fully operational at http://127.0.0.1:5000")

        if os.getenv("GITHUB_ACTIONS") != "true":
            webbrowser.open("http://127.0.0.1:5000")

        while True:
            time.sleep(2)
            for p in processes:
                if p.poll() is not None:
                    raise RuntimeError("One or more system components stopped.")

    except KeyboardInterrupt:
        logger.info("Shutdown requested by user.")
    except Exception as exc:
        logger.critical("Fatal orchestrator failure", exc_info=exc)
    finally:
        logger.info("Shutting down all components...")
        for p in processes:
            try:
                p.terminate()
            except Exception:
                pass
        sys.exit(0)


if __name__ == "__main__":
    main()