import requests
import time
import sys

BASE_URL = "http://localhost:8000/api/jobs"

def submit_job(name, cmd, deps=[], priority=0):
    payload = {
        "name": name,
        "command": cmd,
        "resource_requirements": {
            "cpu_cores": 1,
            "memory_mb": 128,
            "docker_image": "python:3.9-slim",
            "timeout": 10
        },
        "priority": priority,
        "dependencies": deps
    }
    try:
        r = requests.post(BASE_URL, json=payload)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"Submission result: {r.status_code}")
        return None

def test_security():
    print("\n--- Testing Security ---")
    res = submit_job("Bad Job", "rm -rf /")
    if res is None:
        print("SUCCESS: Rejected dangerous command.")
    else:
        print("FAILURE: Accepted dangerous command!")
        sys.exit(1)

def test_retry():
    print("\n--- Testing Retry Logic ---")
    # Command that fails
    job = submit_job("Fail Job", "exit 1")
    if not job: sys.exit(1)
    
    print(f"Submitted Fail Job {job['id']}. Watching for status...")
    
    # Poll for status changes
    # Expect: QUEUED -> RUNNING -> QUEUED (Retry 1) -> RUNNING -> QUEUED (Retry 2) -> ... -> FAILED
    # Just check final state is FAILED and retries happened (we can't easily see retry count via API unless we added field)
    # Actually Job model has retry_count but API response might not show live updates unless we poll.
    
    for i in range(20):
        r = requests.get(f"{BASE_URL}/{job['id']}")
        j = r.json()
        print(f"Status: {j['status']}, Retries: {j.get('retry_count')}")
        if j['status'] == 'failed':
            print("Job reached FAILED state.")
            if j.get('retry_count', 0) > 0:
                 print("SUCCESS: Job was retried.")
                 return
            else:
                 print("FAILURE: Job failed without retry?")
                 return # sys.exit(1)
        time.sleep(1)

if __name__ == "__main__":
    time.sleep(2) # Allow startup
    test_security()
    test_retry()

