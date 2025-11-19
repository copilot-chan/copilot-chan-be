import os
import signal
import sys
from dotenv import load_dotenv
import subprocess
from multiprocessing import Process
import time

from mem0 import MemoryClient

from app.config import settings

load_dotenv()

# Try to import pyngrok, but don't fail if not present (unless needed)
try:
    from pyngrok import ngrok
except ImportError:
    ngrok = None


def run_agent_server():
    # Choose command based on IS_DEV
    is_dev = settings.IS_DEV

    # Get port from LOCAL_AGENT_PORT environment variable, default to 8001 if not set
    port = settings.LOCAL_AGENT_PORT
    

    cmd = ["adk", "web" if is_dev else "api_server", "--port", str(port)]
    
    # add --verbose if IS_DEV=true
    if settings.IS_DEV:
        cmd.append("--verbose")
        
    # add --session_service_uri from DB_URL
    db_url = settings.DB_URL
    if db_url:
        cmd.extend(["--session_service_uri", db_url])
        
    cmd.append("./agents")
    
    # Add project root to PYTHONPATH
    env = os.environ.copy()
    env["PYTHONPATH"] = os.path.abspath(os.path.dirname(__file__)) + os.pathsep + env.get("PYTHONPATH", "")
    
    process = subprocess.Popen(cmd, env=env)
    process.communicate()

def run_client_app():
    is_dev = settings.IS_DEV
    host = "127.0.0.1" if is_dev else "0.0.0.0"
    cmd = ["uvicorn", "app.main:app", "--host", host, "--port", str(settings.CLIENT_PORT)]
    subprocess.run(cmd)

def setup_webhook():
    """
    Setup Mem0 webhook.
    Returns the webhook_id if created, or None.
    """
    webhook_id = None
    public_url = None
    
    if settings.IS_DEV:
        if ngrok:
            try:
                # Open a ngrok tunnel to the client port
                http_tunnel = ngrok.connect(settings.CLIENT_PORT)
                public_url = http_tunnel.public_url
                print(f"[INFO] Ngrok tunnel started: {public_url}")
            except Exception as e:
                print(f"[ERROR] Failed to start ngrok: {e}")
        else:
            print("[WARNING] pyngrok not installed. Skipping automatic webhook setup in DEV mode.")
    else:
        public_url = settings.WEBHOOK_HOST

    if public_url:
        try:
            # Initialize synchronous Mem0 client for setup
            client = MemoryClient()
            webhook_url = f"{public_url}/memory/webhook"
            
            print(f"[INFO] Registering webhook: {webhook_url}")
            
            # Create webhook
            # Note: We might want to check if it already exists or just create a new one.
            # For simplicity, we create a new one.
            webhook = client.create_webhook(
                url=webhook_url,
                name=f"Copilot-Chan Webhook ({'DEV' if settings.IS_DEV else 'PROD'})",
                event_types=["memory_add", "memory_update", "memory_delete"],
                project_id=settings.MEM0_PROJECT_ID
            )
            webhook_id = webhook.get("webhook_id")
            print(f"[INFO] Webhook created with ID: {webhook_id}")
            
        except Exception as e:
            print(f"[ERROR] Failed to register webhook: {e}")
            
    return webhook_id

def cleanup_webhook(webhook_id):
    if webhook_id:
        try:
            client = MemoryClient()
            client.delete_webhook(webhook_id)
            print(f"[INFO] Webhook {webhook_id} deleted.")
        except Exception as e:
            print(f"[ERROR] Failed to delete webhook: {e}")

def main():
    # Setup webhook before starting servers
    webhook_id = setup_webhook()

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
        
        # Cleanup webhook
        cleanup_webhook(webhook_id)
        
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
