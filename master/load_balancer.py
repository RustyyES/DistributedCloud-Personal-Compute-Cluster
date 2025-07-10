from typing import List, Optional
from common.models import Node, Job, NodeStatus

class LoadBalancer:
    def __init__(self):
        pass

    def select_node(self, nodes: List[Node], job: Job) -> Optional[Node]:
        """
        Select the best node for the job based on load score and constraints.
        """
        candidates = []
        for node in nodes:
            if node.status != NodeStatus.ACTIVE:
                continue
            
            # Check hard constraints
            if not self._satisfies_requirements(node, job):
                continue
                
            score = self._calculate_load_score(node, job)
            # Filter overloaded nodes (load > 0.9)
            if score > 0.9:
                continue
                
            candidates.append((score, node))
        
        if not candidates:
            return None
            
        # Sort by score ascending (lower is better)
        candidates.sort(key=lambda x: x[0])
        return candidates[0][1]

    def _satisfies_requirements(self, node: Node, job: Job) -> bool:
        reqs = job.resource_requirements
        if not node.resources:
            return False
            
        if node.resources.cpu_available < reqs.cpu_cores:
            return False
            
        if node.resources.memory_available_mb < reqs.memory_mb:
            return False
            
        if reqs.gpu and not node.resources.gpu_available:
            return False
            
        return True

    def _calculate_load_score(self, node: Node, job: Job = None) -> float:
        """
        Calculate load score: (cpu_used/total)*0.6 + (mem_used/total)*0.4
        Lower is better.
        If job is provided, we can subtract a 'locality bonus' to prefer this node.
        """
        if not node.resources or node.resources.cpu_total == 0 or node.resources.memory_total_mb == 0:
            return 1.0 # Treat as full if no resource info
            
        cpu_usage = 1.0 - (node.resources.cpu_available / node.resources.cpu_total)
        mem_usage = 1.0 - (node.resources.memory_available_mb / node.resources.memory_total_mb)
        
        score = (cpu_usage * 0.6) + (mem_usage * 0.4)
        
        # Locality Bonus
        if job and job.resource_requirements.docker_image:
             if job.resource_requirements.docker_image in node.resources.cached_images:
                 # Reduce score by 0.2 to prioritize this node (even if slightly more loaded)
                 # e.g. 0.5 (50% load) becomes 0.3, beating an idle node (0.0)? 
                 # Maybe simpler: Small bonus.
                 # If idle node is 0.0, we want to beat it? 
                 # Pulling image takes ~10-60s. 
                 # Idle node is instant start + pull.
                 # Busy node is wait + no pull.
                 # Let's say we prefer locality unless node is very busy.
                 score -= 0.15 
        
        return score


