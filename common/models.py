from enum import Enum
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

class JobStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class NodeStatus(str, Enum):
    ACTIVE = "active"
    BUSY = "busy"
    OFFLINE = "offline"
    ERROR = "error"

class ResourceRequirements(BaseModel):
    cpu_cores: int = Field(..., ge=1)
    memory_mb: int = Field(..., ge=128)
    gpu: bool = False
    docker_image: str
    timeout: int = 3600

class JobResult(BaseModel):
    exit_code: int
    stdout: str
    stderr: str
    execution_time_ms: int

class Job(BaseModel):
    id: str
    name: str
    command: str
    resource_requirements: ResourceRequirements
    priority: int = 0
    dependencies: List[str] = []
    status: JobStatus = JobStatus.QUEUED
    assigned_node: Optional[str] = None
    submitted_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[JobResult] = None
    retry_count: int = 0
    max_retries: int = 3

class NodeResources(BaseModel):
    cpu_total: int
    cpu_available: int
    memory_total_mb: int
    memory_available_mb: int
    disk_total_gb: float
    disk_free_gb: float
    gpu_available: bool = False
    cached_images: List[str] = []

class Node(BaseModel):
    id: str
    hostname: str
    ip_address: str
    ssh_port: int = 22
    ssh_user: str
    capabilities: Dict[str, Any] = {}
    status: NodeStatus = NodeStatus.OFFLINE
    resources: Optional[NodeResources] = None
    last_heartbeat: Optional[datetime] = None
    jobs_running: List[str] = []
    jobs_completed: int = 0
