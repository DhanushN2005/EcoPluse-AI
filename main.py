import subprocess
import time
import sys
import os
import webbrowser

def get_env():
    """Environment with correct PYTHONPATH to treat 'ecopulse_ai' as a package."""
    env = os.environ.copy()
    # Path to the directory containing 'ecopulse_ai'
    # Current script is at: e:/Hack for Green/ecopulse_ai/main.py
    # Root dir of project: e:/Hack for Green/ecopulse_ai
    # To import 'ecopulse_ai.xxx', we need 'e:/Hack for Green' in path.
    root_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(root_dir)
    env["PYTHONPATH"] = parent_dir + os.pathsep + env.get("PYTHONPATH", "")
    return env

def start():
    print("""
    ========================================================
    EC-PULSE AI - Real-Time Environmental Intelligence
    ========================================================
    Architecture: Kafka + Pathway + Flask + Climate Copilot
    ========================================================
    """)
    
    env = get_env()
    processes = []
    
    try:
        # 1. Start Kafka Producer (Simulator)
        print("[INIT] Starting Kafka Producer...")
        p_prod = subprocess.Popen([sys.executable, "-m", "ecopulse_ai.kafka.producer"], env=env)
        processes.append(p_prod)
        
        time.sleep(3)
        
        # 2. Start Pathway Pipeline (Handles real OR shim automatically)
        print("[INIT] Starting Streaming Engine...")
        p_pipe = subprocess.Popen([sys.executable, "-m", "ecopulse_ai.streaming.pathway_pipeline"], env=env)
        processes.append(p_pipe)
        
        time.sleep(8) # Allow time for Shim/Pathway to bind port 8080
        
        # 3. Start Flask API
        print("[INIT] Starting Web Interface (Port 5000)...")
        p_api = subprocess.Popen([sys.executable, "-m", "ecopulse_ai.api.app"], env=env)
        processes.append(p_api)

        # 4. Wait for API to warm up
        print("[INFO] Warming up system...")
        time.sleep(8)
        
        print("\n[SUCCESS] EcoPulse AI is operational.")
        print(">> Dashboard: http://127.0.0.1:5000")
        
        # Open browser
        webbrowser.open("http://127.0.0.1:5000")
        
        # Keep alive
        while True:
            time.sleep(1)
            # Check if critical processes died
            if p_api.poll() is not None:
                print("[ERROR] Web Interface process terminated unexpectedly.")
                break
            if p_pipe.poll() is not None:
                print("[ERROR] Streaming Engine process terminated unexpectedly.")
                break
                
    except KeyboardInterrupt:
        print("\n[SHUTDOWN] Terminating system components...")
    except Exception as e:
        print(f"\n[ERROR] System failure: {e}")
    finally:
        for p in processes:
            try:
                p.terminate()
            except:
                pass
        sys.exit(0)

if __name__ == "__main__":
    start()
