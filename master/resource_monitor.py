from typing import Dict, List, Optional
from common.models import Node, NodeResources

class ResourceMonitor:
    def __init__(self, cluster_manager):
        self.cluster_manager = cluster_manager

    def get_cluster_stats(self) -> Dict[str, Any]:
        """Aggregate resources across the cluster"""
        nodes = self.cluster_manager.list_nodes()
        
        total_cpu = 0
        available_cpu = 0
        total_mem = 0
        available_mem = 0
        total_gpu_nodes = 0
        
        active_nodes_count = 0

        for node in nodes:
            if node.resources: # Using lazy check if they are active? 
                # We typically only count active nodes
                # But let's check status just in case
                # NodeStatus is defined in common/models
                if node.status == "active": # Or use Enum
                   active_nodes_count += 1
                   total_cpu += node.resources.cpu_total
                   available_cpu += node.resources.cpu_available
                   total_mem += node.resources.memory_total_mb
                   available_mem += node.resources.memory_available_mb
                   if node.resources.gpu_available:
                       total_gpu_nodes += 1

        return {
            "nodes_active": active_nodes_count,
            "total_cpu_cores": total_cpu,
            "available_cpu_cores": available_cpu,
            "total_memory_mb": total_mem,
            "available_memory_mb": available_mem,
            "gpu_nodes": total_gpu_nodes
        }
