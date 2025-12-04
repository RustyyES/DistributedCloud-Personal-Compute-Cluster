from prometheus_client import start_http_server, Gauge, Counter, Summary
import time
import threading

# Metrics definitions
JOB_QUEUE_SIZE = Gauge('dcloud_job_queue_size', 'Number of jobs in queue')
ACTIVE_NODES = Gauge('dcloud_active_nodes', 'Number of active worker nodes')
CLUSTER_CPU_TOTAL = Gauge('dcloud_cluster_cpu_total', 'Total CPU cores in cluster')
CLUSTER_CPU_USED = Gauge('dcloud_cluster_cpu_used', 'Used CPU cores in cluster')
JOBS_COMPLETED = Counter('dcloud_jobs_completed_total', 'Total number of completed jobs')
JOBS_FAILED = Counter('dcloud_jobs_failed_total', 'Total number of failed jobs')
JOB_DURATION = Summary('dcloud_job_duration_seconds', 'Time spent processing jobs')

class MetricsServer:
    def __init__(self, port=9090):
        self.port = port
        self.running = False
        
    def start(self):
        start_http_server(self.port)
        self.running = True
        print(f"Metrics server started on port {self.port}")

    def update_cluster_stats(self, cluster_manager):
        """Periodic update of gauge metrics"""
        while self.running:
            try:
                nodes = cluster_manager.list_nodes()
                active = [n for n in nodes if n.status == 'active']
                ACTIVE_NODES.set(len(active))
                
                total_cpu = sum(n.resources.cpu_total for n in active if n.resources)
                avail_cpu = sum(n.resources.cpu_available for n in active if n.resources)
                
                CLUSTER_CPU_TOTAL.set(total_cpu)
                CLUSTER_CPU_USED.set(total_cpu - avail_cpu)
                
            except Exception as e:
                print(f"Error updating metrics: {e}")
            
            time.sleep(15)

    def track_job_completion(self, job):
        JOBS_COMPLETED.inc()
        if job.result:
             # ms to seconds
            JOB_DURATION.observe(job.result.execution_time_ms / 1000.0)

    def track_job_failure(self, job):
        JOBS_FAILED.inc()



