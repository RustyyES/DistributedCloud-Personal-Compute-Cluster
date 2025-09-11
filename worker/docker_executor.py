import docker
import os
import time
from typing import Dict, Tuple, Optional
from common.models import Job, JobResult

class DockerExecutor:
    def __init__(self):
        try:
            self.client = docker.from_env()
        except docker.errors.DockerException as e:
            print(f"Error connecting to Docker: {e}")
            self.client = None

    def run_job(self, job: Job, work_dir: str = "/tmp/dcloud") -> JobResult:
        if not self.client:
            return JobResult(exit_code=1, stdout="", stderr="Docker not available on worker", execution_time_ms=0)

        start_time = time.time()
        container = None
        
        # Prepare workspace
        job_dir = os.path.join(work_dir, job.id)
        os.makedirs(job_dir, exist_ok=True)
        
        try:
            # Pull image
            print(f"Pulling image {job.resource_requirements.docker_image}...")
            self.client.images.pull(job.resource_requirements.docker_image)
            
            # Limits
            # cpu_quota = job.resource_requirements.cpu_cores * 100000
            # mem_limit = f"{job.resource_requirements.memory_mb}m"
            
            print(f"Starting container for job {job.id}...")
            container = self.client.containers.run(
                image=job.resource_requirements.docker_image,
                command=job.command,
                # nano_cpus=int(job.resource_requirements.cpu_cores * 1e9), # docker-py might calculate this differently
                mem_limit=f"{job.resource_requirements.memory_mb}m",
                volumes={job_dir: {'bind': '/workspace', 'mode': 'rw'}},
                working_dir='/workspace',
                detach=True,
                # auto_remove=False # We want to read logs
            )
            
            # Wait for completion (handling timeout)
            # Simple wait for now
            result = container.wait(timeout=job.resource_requirements.timeout)
            exit_code = result.get('StatusCode', 1)
            
            stdout = container.logs(stdout=True, stderr=False).decode('utf-8')
            stderr = container.logs(stdout=False, stderr=True).decode('utf-8')
            
            end_time = time.time()
            return JobResult(
                exit_code=exit_code,
                stdout=stdout,
                stderr=stderr,
                execution_time_ms=int((end_time - start_time) * 1000)
            )

        except Exception as e:
            return JobResult(
                exit_code=1,
                stdout="",
                stderr=f"Execution failed: {str(e)}",
                execution_time_ms=int((time.time() - start_time) * 1000)
            )
        finally:
            if container:
                try:
                    container.remove(force=True)
                except:
                    pass
