import requests
import time
import json

def verify_optimization():
    print("Waiting for node registration...")
    time.sleep(5)
    
    # 1. Check if cached_images are reported
    try:
        r = requests.get("http://localhost:8000/api/nodes")
        nodes = r.json()
        if not nodes:
            print("FAILURE: No nodes registered.")
            return
        
        node = nodes[0]
        resources = node.get('resources', {})
        images = resources.get('cached_images', [])
        
        print(f"Node {node['id']} reports {len(images)} cached images.")
        if len(images) > 0:
            print(f"Sample images: {images[:3]}")
            print("SUCCESS: Cached images reporting works.")
        else:
            print("WARNING: No images found (Docker might be empty or reporting failed).")
            # This is not necessarily a failure if docker is empty.
    except Exception as e:
        print(f"FAILURE: API check failed: {e}")

    # 2. Submit a job to verify SSH Pooling doesn't break things
    print("\nSubmitting a job to test execution with SSH Pooling...")
    payload = {
        "name": "Pool Test",
        "command": "echo 'Hello Pool'",
        "resource_requirements": {
            "cpu_cores": 0.1,
            "memory_mb": 64,
            "docker_image": "python:3.9-slim", # Hope this exists or pulls
            "timeout": 20
        }
    }
    
    try:
        r = requests.post("http://localhost:8000/api/jobs", json=payload)
        job = r.json()
        job_id = job['id']
        print(f"Job {job_id} submitted.")
        
        for i in range(15):
            r = requests.get(f"http://localhost:8000/api/jobs/{job_id}")
            j = r.json()
            status = j['status']
            print(f"Status: {status}")
            if status == 'completed':
                print("SUCCESS: Job completed.")
                break
            if status == 'failed':
                 print(f"FAILURE: Job failed. Result: {j.get('result')}")
                 break
            time.sleep(1)
            
    except Exception as e:
        print(f"FAILURE: Job submission failed: {e}")

if __name__ == "__main__":
    verify_optimization()

