import unittest
from common.models import Node, NodeStatus, NodeResources, Job, ResourceRequirements
from master.load_balancer import LoadBalancer

class TestLoadBalancer(unittest.TestCase):
    def setUp(self):
        self.lb = LoadBalancer()
        self.nodes = [
            Node(
                id="n1", hostname="h1", ip_address="1.2.3.4", ssh_user="u",
                status=NodeStatus.ACTIVE,
                resources=NodeResources(
                    cpu_total=4, cpu_available=4, # 0% load
                    memory_total_mb=8000, memory_available_mb=8000,
                    disk_total_gb=100, disk_free_gb=100
                )
            ),
            Node(
                id="n2", hostname="h2", ip_address="1.2.3.5", ssh_user="u",
                status=NodeStatus.ACTIVE,
                resources=NodeResources(
                    cpu_total=4, cpu_available=1, # 75% load
                    memory_total_mb=8000, memory_available_mb=2000,
                    disk_total_gb=100, disk_free_gb=100
                )
            )
        ]

    def test_select_idle_node(self):
        job = Job(
            id="j1", name="test", command="echo",
            resource_requirements=ResourceRequirements(cpu_cores=1, memory_mb=100, docker_image="img")
        )
        selected = self.lb.select_node(self.nodes, job)
        self.assertEqual(selected.id, "n1")

    def test_load_calculation(self):
        score_n1 = self.lb._calculate_load_score(self.nodes[0])
        score_n2 = self.lb._calculate_load_score(self.nodes[1])
        # n1: 0% cpu, 0% mem -> 0.0
        # n2: 75% cpu, 75% mem -> 0.75
        self.assertAlmostEqual(score_n1, 0.0)
        self.assertAlmostEqual(score_n2, 0.75)

    def test_requirements_check(self):
        # Job needing 5 cores (available) should fail on n1 (only 4)
        job = Job(
            id="j2", name="big", command="echo",
            resource_requirements=ResourceRequirements(cpu_cores=5, memory_mb=100, docker_image="img")
        )
        selected = self.lb.select_node(self.nodes, job)
        self.assertIsNone(selected)

if __name__ == '__main__':
    unittest.main()
