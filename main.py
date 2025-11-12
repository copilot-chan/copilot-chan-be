import os
import signal
import sys
from dotenv import load_dotenv
import subprocess
from multiprocessing import Process

load_dotenv()

def run_agent_server():
    # Choose command based on IS_DEV
    is_dev = os.getenv("IS_DEV", "false").lower() == "true"

    # Get port from LOCAL_AGENT_PORT environment variable, default to 8001 if not set
    port = int(os.getenv("LOCAL_AGENT_PORT", 8001))
    

    cmd = ["adk", "web" if is_dev else "api_server", "--host", "127.0.0.1", "--port", str(port)]
    
    # add --verbose if IS_DEV=true
    if os.getenv("IS_DEV", "false").lower() == "true":
        cmd.append("--verbose")
        
    # add --session_service_uri from DB_URL
    db_url = os.getenv("DB_URL")
    if db_url:
        cmd.extend(["--session_service_uri", db_url])
        
    cmd.append("./agents")
    
    # Add project root to PYTHONPATH
    env = os.environ.copy()
    env["PYTHONPATH"] = os.path.abspath(os.path.dirname(__file__)) + os.pathsep + env.get("PYTHONPATH", "")
    
    process = subprocess.Popen(cmd, env=env)
    process.communicate()

def run_client_app():
    import uvicorn

    is_dev = os.getenv("IS_DEV", "false").lower() == "true"
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=is_dev)

def main():
    processes = []
    
    # Create 2 processes
    p1 = Process(target=run_agent_server)
    p2 = Process(target=run_client_app)
    processes.extend([p1, p2])

    for p in processes:
        p.start()
    
    # Handle Ctrl+C cleanly
    def signal_handler(sig, frame):
        print("\n[INFO] Ctrl+C detected. Terminating both servers...")
        for p in processes:
            if p.is_alive():
                p.terminate()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    # Wait for both processes
    try:
        for p in processes:
            p.join()
    except KeyboardInterrupt:
        signal_handler(None, None)

if __name__ == "__main__":
   main()
