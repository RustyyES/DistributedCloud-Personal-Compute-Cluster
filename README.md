# Distributed Cloud - Personal Compute Cluster ☁️💻

Hi there! 👋 This is my project, **Distributed Cloud**. It's a system that lets you connect multiple computers (like your laptop, your old desktop, and maybe a Raspberry Pi) into a single "cluster" that can run tasks together.

Think of it like building your own mini supercomputer using the devices you already have at home! 

##  What does it do?

Instead of running a heavy program on just one computer, this system lets you:
1.  **Submit a Job**: You send a command (like a Python script or a Docker container) to the "Master" node.
2.  **Schedule**: The Master looks at all your connected "Worker" nodes and decides which one is the least busy.
3.  **Execute**: The job runs on that worker using Docker (so it's safe and isolated).
4.  **Get Results**: The output comes back to you!

## How it works (The Phases)

I built this project in 5 main phases involving a lot of learning! 

### Phase 1: The Core Infrastructure 
I started by building the basics.
-   **Master Node**: The brain of the operation. It keeps a registry of all workers.
-   **Worker Agent**: A small program that runs on each computer (`worker/agent.py`). It tells the Master "Hey, I'm here and ready to work!".
-   **SSH Communication**: I used SSH to securely send commands from Master to Workers, just like how servers talk in the real world.

### Phase 2: Resource Management 
Initially, I just sent jobs to random nodes. But that's not efficient!
-   **Monitoring**: Each worker now checks its CPU, Memory, and Disk usage (`worker/resource_reporter.py`).
-   **Load Balancing**: The Master picks the *best* node for the job (the one with the most free resources).

### Phase 3: Advanced Scheduling via DAGs 
Real programs often have steps (Step B usually needs Step A to finish first).
-   **DAGs (Directed Acyclic Graphs)**: I added support for job dependencies. You can say "Run this job ONLY after that one finishes."
-   **Priority Queue**: Important jobs get to cut the line! 
-   **Dashboard**: I made a cool web dashboard (`http://localhost:8000/dashboard`) to see everything happening in real-time.

### Phase 4: Making it Robust 
Things break. Computers crash. Wifi disconnects.
-   **Retries**: If a job fails, the system automatically retries it.
-   **Failover**: If a worker goes offline while running a job, the Master detects it and moves the job to another worker.
-   **Security**: Added checks to prevent dangerous commands (like `rm -rf /` ).

### Phase 5: Optimization 
Finally, I made it fast.
-   **SSH Pooling**: Instead of connecting every single time (which is slow), I keep connections open.
-   **Locality Caching**: If Node A already has the Docker image for a job, the scheduler prefers Node A. This saves huge download times!

## How to Run It

### 1. Setup
Make sure you have **Python 3.9+** and **Docker** installed.

```bash
# Install dependencies
pip install -r requirements.txt
```

### 2. Start the Master
The Master manages the cluster.
```bash
python -m master.api_server
```
Visit the dashboard at `http://localhost:8000/dashboard`!

### 3. Start a Worker
Run this on any computer you want to join the cluster.
```bash
# Point it to your Master's IP
python -m worker.agent http://localhost:8000
```

### 4. Submit a Job
You can use `curl` or a python script.
```bash
curl -X POST http://localhost:8000/api/jobs \
  -H "Content-Type: application/json" \
  -d '{"name": "test-job", "command": "echo Hello form the cloud!", "resource_requirements": {"cpu_cores": 1, "memory_mb": 100}}'
```

## Project Structure

-   `master/`: Code for the Master node (API, Scheduler, Dashboard).
-   `worker/`: Code for Worker nodes (Agent, Executor).
-   `common/`: Shared code (Models, SSH utilities).
-   `tests/`: Unit tests and verification scripts.

## Technologies Used
-   **Python** (The main language)
-   **FastAPI** (For the API and Dashboard logic)
-   **Docker** (For running jobs safely)
-   **Paramiko** (For SSH magic)
-   **Jinja2 & TailwindCSS** (For the pretty dashboard)
-   **Prometheus** (For metrics)

---
*Created with ❤️ and lots of coffee ☕.*






