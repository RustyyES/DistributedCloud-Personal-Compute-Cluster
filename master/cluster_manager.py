from typing import Dict, List, Optional
from datetime import datetime, timedelta
from common.models import Node, NodeStatus
from common.exceptions import NodeNotFoundError

class ClusterManager:
    def __init__(self):
        # In-memory registry for now, will move to DB later
        self.nodes: Dict[str, Node] = {}

    def register_node(self, node: Node) -> Node:
        """Register a new node or update existing one"""
        node.last_heartbeat = datetime.utcnow()
        node.status = NodeStatus.ACTIVE
        self.nodes[node.id] = node
        print(f"Node registered: {node.id} ({node.hostname})")
        return node

    def get_node(self, node_id: str) -> Node:
        """Get node by ID"""
        if node_id not in self.nodes:
            raise NodeNotFoundError(f"Node {node_id} not found")
        return self.nodes[node_id]

    def list_nodes(self) -> List[Node]:
        """List all registered nodes"""
        return list(self.nodes.values())

    def update_heartbeat(self, node_id: str):
        """Update last heartbeat for a node"""
        if node_id in self.nodes:
            self.nodes[node_id].last_heartbeat = datetime.utcnow()
            self.nodes[node_id].status = NodeStatus.ACTIVE
        else:
            raise NodeNotFoundError(f"Cannot update heartbeat: Node {node_id} not known")

    def deregister_node(self, node_id: str):
        """Remove a node from the cluster"""
        if node_id in self.nodes:
            del self.nodes[node_id]
            print(f"Node deregistered: {node_id}")

    def get_active_nodes(self) -> List[Node]:
        """Get list of active nodes (heartbeat within last 90s)"""
        cutoff = datetime.utcnow() - timedelta(seconds=90)
        active_nodes = []
        for node in self.nodes.values():
            if node.last_heartbeat and node.last_heartbeat > cutoff:
                active_nodes.append(node)
            else:
                if node.status != NodeStatus.OFFLINE:
                    node.status = NodeStatus.OFFLINE
                    print(f"Node {node.id} marked as OFFLINE (missed heartbeat)")
        return active_nodes
