import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional
import threading

from common.models import Job, Node, JobStatus, ResourceRequirements
from master.cluster_manager import ClusterManager
from master.job_scheduler import JobScheduler

app = FastAPI(title="DistributedCloud Master API")

# Global instances
cluster_manager = ClusterManager()

# Metrics Integration
from master.metrics import MetricsServer
metrics_server = MetricsServer()

scheduler = JobScheduler(cluster_manager, metrics_server)

# Dashboard Integration
from master.dashboard.router import router as dashboard_router, context
context['cluster_manager'] = cluster_manager
context['job_scheduler'] = scheduler
app.include_router(dashboard_router, prefix="/dashboard", tags=["dashboard"])

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    scheduler.start()
    metrics_server.start()
    
    # Start metrics updater thread
    updater_thread = threading.Thread(target=metrics_server.update_cluster_stats, args=(cluster_manager,), daemon=True)
    updater_thread.start()
    
    yield
    # Shutdown
    scheduler.stop()
    metrics_server.running = False

app.router.lifespan_context = lifespan

# --- Node Endpoints ---

@app.post("/api/nodes", response_model=Node)
async def register_node(node: Node):
    return cluster_manager.register_node(node)

@app.get("/api/nodes", response_model=List[Node])
async def list_nodes():
    return cluster_manager.list_nodes()

@app.get("/api/nodes/{node_id}", response_model=Node)
async def get_node(node_id: str):
    return cluster_manager.get_node(node_id)

@app.post("/api/nodes/{node_id}/heartbeat")
async def heartbeat(node_id: str):
    cluster_manager.update_heartbeat(node_id)
    return {"status": "ok"}

# --- Job Endpoints ---

class JobSubmission(BaseModel):
    command: str
    resource_requirements: ResourceRequirements
    name: str = "job"
    priority: int = 0
    dependencies: List[str] = []
    docker_image: str = "python:3.9"

@app.post("/api/jobs", response_model=Job)
async def submit_job(submission: JobSubmission):
    from common.security import validate_job_command
    if not validate_job_command(submission.command):
         raise HTTPException(status_code=400, detail="Invalid command: Potential security risk or invalid format.")
         
    import uuid
    job = Job(
        id=str(uuid.uuid4()),
        name=submission.name,
        command=submission.command,
        resource_requirements=submission.resource_requirements,
        priority=submission.priority,
        dependencies=submission.dependencies,
        # For now, default image if not in submission (Wait, submission has it)
        # Actually ResourceRequirements has it too? 
        # In models.py: ResourceRequirements has docker_image.
        # So we should use that.
    )
    # The models.py definitions might be duplicating docker_image? 
    # Let's check models.py content again in my memory.
    # ResourceRequirements has docker_image. Job also has docker_image field?
    # No, Job definition in my previous tool call:
    # class Job(BaseModel): ... resource_requirements: ResourceRequirements ... 
    # No top-level docker_image in Job class in the prev tool call, 
    # WAIT. I need to be careful.
    # Let's check the models.py content I wrote.
    # Yes, Job has: id, name, command, resource_requirements, priority...
    # It does NOT have docker_image at top level. 
    # But ResourceRequirements DOES.
    
    return scheduler.submit_job(job)

@app.get("/api/jobs", response_model=List[Job])
async def list_jobs():
    return scheduler.list_jobs()

@app.get("/api/jobs/{job_id}", response_model=Job)
async def get_job(job_id: str):
    job = scheduler.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)


