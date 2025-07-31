from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import os

router = APIRouter()

# Setup templates
templates_dir = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=templates_dir)

# Dependency to get globals from app (mock dependency for now, 
# in real app we'd inject the manager/scheduler)
# We will attach them to app.state or use global imports if we must.
# For simplicity, we import the instances from api_server if possible 
# BUT avoiding circular import is key.
# Ideally api_server imports dashboard, not vice versa.
# So we need a way to access data.
# We'll use the API endpoints themselves or shared singleton?
# Shared singleton is easiest for this scale.

from master.cluster_manager import ClusterManager
from master.job_scheduler import JobScheduler

# We need a way to get the SAME instance as the main server.
# One way: pass them to the router or helper.
# For this "Phase 3", we will assume the main app mounts this and shares the reference.
# But `router` doesn't easily accept args at module level.
# We will use a "get_context" dep.

context = {} # Will be populated by api_server.py

def get_context():
    return context

@router.get("/", response_class=HTMLResponse)
async def dashboard_home(request: Request, ctx: dict = Depends(get_context)):
    cluster_manager: ClusterManager = ctx.get('cluster_manager')
    job_scheduler: JobScheduler = ctx.get('job_scheduler')
    
    nodes = cluster_manager.list_nodes() if cluster_manager else []
    jobs = job_scheduler.list_jobs() if job_scheduler else []
    
    # Calculate stats
    total_cpu = sum(n.resources.cpu_total for n in nodes if n.resources and n.status == 'active')
    used_cpu = sum(n.resources.cpu_total - n.resources.cpu_available for n in nodes if n.resources and n.status == 'active')
    
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "nodes": nodes, 
        "jobs": jobs,
        "stats": {
            "node_count": len(nodes),
            "job_count": len(jobs),
            "cpu_usage": f"{used_cpu}/{total_cpu}" if total_cpu else "0/0"
        }
    })
