import time
import requests
import socket
import psutil
import platform
import uuid
import sys
from common.models import Node, NodeStatus, NodeResources

class WorkerAgent:
    def __init__(self, master_url: str, node_id: str = None):
        self.master_url = master_url
        self.node_id = node_id or str(uuid.uuid4())
        self.hostname = socket.gethostname()
        self.ip_address = self._get_ip_address()
        self.running = False
        from worker.resource_reporter import ResourceReporter
        self.reporter = ResourceReporter()
        
    def _get_ip_address(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"

    def _collect_resources(self) -> NodeResources:
        return self.reporter.collect()

    def register(self):
        node = Node(
            id=self.node_id,
            hostname=self.hostname,
            ip_address=self.ip_address,
            ssh_user=os.getlogin() if hasattr(os, 'getlogin') else 'root', # Simple default
            resources=self._collect_resources(),
            status=NodeStatus.ACTIVE
        )
        
        try:
            print(f"Registering with master at {self.master_url}...")
            response = requests.post(f"{self.master_url}/api/nodes", json=node.dict())
            response.raise_for_status()
            print("Successfully registered.")
            return True
        except Exception as e:
            print(f"Registration failed: {e}")
            return False

    def heartbeat(self):
        try:
            # We can send metrics here too
            requests.post(f"{self.master_url}/api/nodes/{self.node_id}/heartbeat")
        except Exception as e:
            print(f"Heartbeat failed: {e}")

    def start(self):
        self.running = True
        if not self.register():
            print("Retrying registration in 5s...")
            time.sleep(5)
            if not self.register():
                print("Could not register. Exiting.")
                return

        print("Worker agent started. Sending heartbeats...")
        while self.running:
            self.heartbeat()
            time.sleep(10) # 10s heartbeat for now

if __name__ == "__main__":
    import os
    if len(sys.argv) > 1:
        MASTER_URL = sys.argv[1]
    else:
        MASTER_URL = "http://localhost:8000"
    
    agent = WorkerAgent(MASTER_URL)
    agent.start()



