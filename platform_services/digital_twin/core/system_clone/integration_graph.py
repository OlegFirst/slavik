"""
Integration Graph
Analyzes and visualizes service integration patterns

Features:
- Dependency graph analysis
- Critical path identification
- Impact analysis for changes
- Integration health monitoring
"""

import logging
from typing import Dict, Any, Optional, List, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict, deque

logger = logging.getLogger(__name__)


@dataclass
class IntegrationEdge:
    """Edge in integration graph"""
    from_service: str
    to_service: str
    integration_type: str = "api"  # api, eventbus, database
    weight: float = 1.0  # Importance weight
    latency_ms: Optional[float] = None
    error_rate: float = 0.0


@dataclass
class ServiceNode:
    """Node in integration graph"""
    name: str
    incoming_edges: List[IntegrationEdge] = field(default_factory=list)
    outgoing_edges: List[IntegrationEdge] = field(default_factory=list)
    criticality_score: float = 0.0  # 0-1, how critical is this service
    is_running: bool = False


class IntegrationGraph:
    """
    Integration Graph Analyzer

    Analyzes service integration patterns and dependencies.
    Provides impact analysis, critical path identification,
    and integration health monitoring.

    Features:
    - Dependency graph construction
    - Transitive dependency analysis
    - Critical service identification
    - Impact assessment for changes
    - Integration health scoring
    """

    def __init__(self):
        """Initialize integration graph"""
        self.nodes: Dict[str, ServiceNode] = {}
        self.edges: List[IntegrationEdge] = []
        self.adjacency_list: Dict[str, List[str]] = defaultdict(list)
        self.reverse_adjacency: Dict[str, List[str]] = defaultdict(list)

    def add_service(self, service_name: str, is_running: bool = False):
        """
        Add service node to graph

        Args:
            service_name: Name of service
            is_running: Whether service is currently running
        """
        if service_name not in self.nodes:
            self.nodes[service_name] = ServiceNode(
                name=service_name,
                is_running=is_running
            )
        else:
            self.nodes[service_name].is_running = is_running

    def add_integration(
        self,
        from_service: str,
        to_service: str,
        integration_type: str = "api",
        weight: float = 1.0
    ):
        """
        Add integration edge between services

        Args:
            from_service: Source service
            to_service: Target service
            integration_type: Type of integration
            weight: Importance weight
        """
        # Ensure nodes exist
        self.add_service(from_service)
        self.add_service(to_service)

        # Create edge
        edge = IntegrationEdge(
            from_service=from_service,
            to_service=to_service,
            integration_type=integration_type,
            weight=weight
        )

        self.edges.append(edge)

        # Update node edges
        self.nodes[from_service].outgoing_edges.append(edge)
        self.nodes[to_service].incoming_edges.append(edge)

        # Update adjacency lists
        self.adjacency_list[from_service].append(to_service)
        self.reverse_adjacency[to_service].append(from_service)

    def get_dependencies(self, service_name: str) -> List[str]:
        """
        Get direct dependencies of service

        Args:
            service_name: Service to check

        Returns:
            List of service names this service depends on
        """
        return self.adjacency_list.get(service_name, [])

    def get_dependents(self, service_name: str) -> List[str]:
        """
        Get services that depend on this service

        Args:
            service_name: Service to check

        Returns:
            List of service names that depend on this service
        """
        return self.reverse_adjacency.get(service_name, [])

    def get_transitive_dependencies(self, service_name: str) -> Set[str]:
        """
        Get all transitive dependencies (BFS)

        Args:
            service_name: Service to check

        Returns:
            Set of all services this service depends on (directly or indirectly)
        """
        visited = set()
        queue = deque([service_name])

        while queue:
            current = queue.popleft()
            if current in visited or current == service_name:
                continue

            visited.add(current)

            # Add direct dependencies to queue
            for dep in self.adjacency_list.get(current, []):
                if dep not in visited:
                    queue.append(dep)

        return visited

    def get_transitive_dependents(self, service_name: str) -> Set[str]:
        """
        Get all services that transitively depend on this service

        Args:
            service_name: Service to check

        Returns:
            Set of all services that depend on this service (directly or indirectly)
        """
        visited = set()
        queue = deque([service_name])

        while queue:
            current = queue.popleft()
            if current in visited or current == service_name:
                continue

            visited.add(current)

            # Add services that depend on current
            for dependent in self.reverse_adjacency.get(current, []):
                if dependent not in visited:
                    queue.append(dependent)

        return visited

    def calculate_criticality_scores(self):
        """
        Calculate criticality score for each service

        Criticality is based on:
        - Number of dependents (higher = more critical)
        - Depth in dependency tree (lower = more critical)
        - Integration type importance
        """
        for service_name in self.nodes:
            # Count direct and transitive dependents
            direct_dependents = len(self.get_dependents(service_name))
            transitive_dependents = len(self.get_transitive_dependents(service_name))

            # More dependents = more critical
            dependent_score = (direct_dependents * 0.6 + transitive_dependents * 0.4) / max(
                len(self.nodes), 1
            )

            # Normalize to 0-1
            self.nodes[service_name].criticality_score = min(dependent_score, 1.0)

    def get_critical_services(self, threshold: float = 0.5) -> List[str]:
        """
        Get services above criticality threshold

        Args:
            threshold: Criticality threshold (0-1)

        Returns:
            List of critical service names
        """
        self.calculate_criticality_scores()

        return [
            name for name, node in self.nodes.items()
            if node.criticality_score >= threshold
        ]

    def assess_impact_if_service_fails(self, service_name: str) -> Dict[str, Any]:
        """
        Assess impact if a service fails

        Args:
            service_name: Service to assess

        Returns:
            Impact assessment
        """
        if service_name not in self.nodes:
            return {"error": f"Service {service_name} not found"}

        # Get all services that would be affected
        affected_services = self.get_transitive_dependents(service_name)

        # Categorize by impact level
        direct_impact = set(self.get_dependents(service_name))
        indirect_impact = affected_services - direct_impact

        return {
            "service": service_name,
            "total_affected": len(affected_services),
            "direct_impact": {
                "count": len(direct_impact),
                "services": list(direct_impact)
            },
            "indirect_impact": {
                "count": len(indirect_impact),
                "services": list(indirect_impact)
            },
            "criticality_score": self.nodes[service_name].criticality_score,
            "is_critical": self.nodes[service_name].criticality_score >= 0.5
        }

    def find_critical_path(self, from_service: str, to_service: str) -> Optional[List[str]]:
        """
        Find critical path between two services (BFS)

        Args:
            from_service: Start service
            to_service: End service

        Returns:
            Path as list of service names, or None if no path exists
        """
        if from_service not in self.nodes or to_service not in self.nodes:
            return None

        # BFS to find shortest path
        queue = deque([(from_service, [from_service])])
        visited = {from_service}

        while queue:
            current, path = queue.popleft()

            if current == to_service:
                return path

            for neighbor in self.adjacency_list.get(current, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))

        return None  # No path found

    def detect_circular_dependencies(self) -> List[List[str]]:
        """
        Detect circular dependencies in graph

        Returns:
            List of circular dependency cycles
        """
        cycles = []
        visited = set()
        rec_stack = set()

        def dfs(node: str, path: List[str]):
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in self.adjacency_list.get(node, []):
                if neighbor not in visited:
                    if dfs(neighbor, path.copy()):
                        return True
                elif neighbor in rec_stack:
                    # Found cycle
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    cycles.append(cycle)

            rec_stack.remove(node)
            return False

        for node in self.nodes:
            if node not in visited:
                dfs(node, [])

        return cycles

    def get_integration_health(self) -> Dict[str, Any]:
        """
        Get overall integration health

        Returns:
            Integration health metrics
        """
        total_services = len(self.nodes)
        running_services = sum(1 for node in self.nodes.values() if node.is_running)

        total_integrations = len(self.edges)

        # Calculate health based on running services with working integrations
        healthy_integrations = sum(
            1 for edge in self.edges
            if self.nodes[edge.from_service].is_running
            and self.nodes[edge.to_service].is_running
        )

        health_percentage = (
            healthy_integrations / total_integrations * 100
            if total_integrations > 0 else 0
        )

        # Detect issues
        circular_deps = self.detect_circular_dependencies()

        return {
            "total_services": total_services,
            "running_services": running_services,
            "service_availability": running_services / total_services * 100 if total_services > 0 else 0,
            "total_integrations": total_integrations,
            "healthy_integrations": healthy_integrations,
            "integration_health_percentage": health_percentage,
            "has_circular_dependencies": len(circular_deps) > 0,
            "circular_dependency_count": len(circular_deps),
            "critical_services": self.get_critical_services()
        }

    def export_graph(self) -> Dict[str, Any]:
        """
        Export graph for visualization

        Returns:
            Graph data with nodes and edges
        """
        self.calculate_criticality_scores()

        nodes = []
        for name, node in self.nodes.items():
            nodes.append({
                "id": name,
                "label": name,
                "is_running": node.is_running,
                "criticality_score": node.criticality_score,
                "is_critical": node.criticality_score >= 0.5,
                "incoming_count": len(node.incoming_edges),
                "outgoing_count": len(node.outgoing_edges)
            })

        edges = []
        for edge in self.edges:
            edges.append({
                "from": edge.from_service,
                "to": edge.to_service,
                "type": edge.integration_type,
                "weight": edge.weight,
                "latency_ms": edge.latency_ms,
                "error_rate": edge.error_rate
            })

        return {
            "nodes": nodes,
            "edges": edges,
            "metadata": {
                "total_nodes": len(nodes),
                "total_edges": len(edges),
                "generated_at": datetime.utcnow().isoformat()
            },
            "health": self.get_integration_health()
        }

    def get_service_summary(self, service_name: str) -> Dict[str, Any]:
        """
        Get detailed summary for a service

        Args:
            service_name: Service to summarize

        Returns:
            Service summary with dependencies and impact
        """
        if service_name not in self.nodes:
            return {"error": f"Service {service_name} not found"}

        node = self.nodes[service_name]

        return {
            "name": service_name,
            "is_running": node.is_running,
            "criticality_score": node.criticality_score,
            "is_critical": node.criticality_score >= 0.5,
            "dependencies": {
                "direct": self.get_dependencies(service_name),
                "transitive": list(self.get_transitive_dependencies(service_name)),
                "count": len(self.get_transitive_dependencies(service_name))
            },
            "dependents": {
                "direct": self.get_dependents(service_name),
                "transitive": list(self.get_transitive_dependents(service_name)),
                "count": len(self.get_transitive_dependents(service_name))
            },
            "impact_if_fails": self.assess_impact_if_service_fails(service_name)
        }
