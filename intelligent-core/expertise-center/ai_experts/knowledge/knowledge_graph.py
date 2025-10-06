"""
Knowledge Graph for ISO 22301 and BCI

Connects ISO clauses, BCI practices, evidence requirements, and platform services
in a queryable graph structure for AI Experts.
"""

from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class NodeType(Enum):
    """Types of nodes in knowledge graph"""
    ISO_CLAUSE = "iso_clause"
    BCI_PRACTICE = "bci_practice"
    EVIDENCE = "evidence"
    AUDIT_QUESTION = "audit_question"
    PLATFORM_SERVICE = "platform_service"
    REQUIREMENT = "requirement"


class RelationType(Enum):
    """Types of relationships in knowledge graph"""
    REQUIRES = "requires"  # Clause requires evidence
    ASKS = "asks"  # Clause asks audit question
    IMPLEMENTS = "implements"  # Platform service implements clause
    MAPS_TO = "maps_to"  # BCI practice maps to ISO clause
    DEPENDS_ON = "depends_on"  # Clause depends on another clause
    RELATED_TO = "related_to"  # General relationship


@dataclass
class Node:
    """Node in knowledge graph"""
    id: str
    type: NodeType
    properties: Dict[str, Any]

    def __hash__(self):
        return hash(self.id)


@dataclass
class Edge:
    """Edge in knowledge graph"""
    from_node: str
    to_node: str
    relation_type: RelationType
    properties: Dict[str, Any] = None

    def __hash__(self):
        return hash((self.from_node, self.to_node, self.relation_type.value))


class KnowledgeGraph:
    """
    Knowledge Graph for ISO 22301 + BCI + Platform

    Provides structured navigation of BCM knowledge for AI Experts.
    """

    def __init__(self):
        self.nodes: Dict[str, Node] = {}
        self.edges: Set[Edge] = set()
        self._adjacency: Dict[str, List[Edge]] = {}  # For fast lookups

    def add_node(self, node: Node):
        """Add node to graph"""
        self.nodes[node.id] = node
        if node.id not in self._adjacency:
            self._adjacency[node.id] = []

    def add_edge(self, edge: Edge):
        """Add edge to graph"""
        self.edges.add(edge)

        # Update adjacency list
        if edge.from_node not in self._adjacency:
            self._adjacency[edge.from_node] = []
        self._adjacency[edge.from_node].append(edge)

    def get_node(self, node_id: str) -> Optional[Node]:
        """Get node by ID"""
        return self.nodes.get(node_id)

    def get_neighbors(
        self,
        node_id: str,
        relation_type: Optional[RelationType] = None
    ) -> List[Node]:
        """
        Get neighboring nodes

        Args:
            node_id: Source node ID
            relation_type: Filter by relation type (optional)

        Returns:
            List of connected nodes
        """

        if node_id not in self._adjacency:
            return []

        edges = self._adjacency[node_id]

        if relation_type:
            edges = [e for e in edges if e.relation_type == relation_type]

        neighbor_ids = [e.to_node for e in edges]
        return [self.nodes[nid] for nid in neighbor_ids if nid in self.nodes]

    def get_iso_clause_evidence(self, clause_number: str) -> List[str]:
        """Get evidence requirements for ISO clause"""

        clause_id = f"iso-{clause_number}"
        evidence_nodes = self.get_neighbors(clause_id, RelationType.REQUIRES)

        return [node.properties.get('name', '') for node in evidence_nodes]

    def get_iso_clause_audit_questions(self, clause_number: str) -> List[str]:
        """Get audit questions for ISO clause"""

        clause_id = f"iso-{clause_number}"
        question_nodes = self.get_neighbors(clause_id, RelationType.ASKS)

        return [node.properties.get('question', '') for node in question_nodes]

    def get_platform_services_for_clause(self, clause_number: str) -> List[str]:
        """Get platform services that implement ISO clause"""

        clause_id = f"iso-{clause_number}"
        service_nodes = self.get_neighbors(clause_id, RelationType.IMPLEMENTS)

        return [node.properties.get('service_name', '') for node in service_nodes]

    def get_bci_practice_for_clause(self, clause_number: str) -> Optional[str]:
        """Get BCI Professional Practice for ISO clause"""

        clause_id = f"iso-{clause_number}"

        # Find BCI practice that this clause maps to
        for edge in self.edges:
            if edge.to_node == clause_id and edge.relation_type == RelationType.MAPS_TO:
                practice_node = self.get_node(edge.from_node)
                if practice_node:
                    return practice_node.properties.get('practice_id')

        return None

    def get_related_clauses(self, clause_number: str) -> List[str]:
        """Get related ISO clauses"""

        clause_id = f"iso-{clause_number}"
        related_nodes = self.get_neighbors(clause_id, RelationType.RELATED_TO)

        return [
            node.properties.get('clause_number', '')
            for node in related_nodes
            if node.type == NodeType.ISO_CLAUSE
        ]

    def query(
        self,
        node_type: Optional[NodeType] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Node]:
        """
        Query nodes by type and properties

        Args:
            node_type: Filter by node type
            filters: Filter by properties (e.g., {'category': 'operation'})

        Returns:
            List of matching nodes
        """

        results = list(self.nodes.values())

        # Filter by type
        if node_type:
            results = [n for n in results if n.type == node_type]

        # Filter by properties
        if filters:
            for key, value in filters.items():
                results = [
                    n for n in results
                    if n.properties.get(key) == value
                ]

        return results

    def get_statistics(self) -> Dict[str, Any]:
        """Get graph statistics"""

        stats = {
            'total_nodes': len(self.nodes),
            'total_edges': len(self.edges),
            'nodes_by_type': {},
            'edges_by_type': {}
        }

        # Count nodes by type
        for node in self.nodes.values():
            node_type = node.type.value
            stats['nodes_by_type'][node_type] = stats['nodes_by_type'].get(node_type, 0) + 1

        # Count edges by type
        for edge in self.edges:
            edge_type = edge.relation_type.value
            stats['edges_by_type'][edge_type] = stats['edges_by_type'].get(edge_type, 0) + 1

        return stats


class KnowledgeGraphBuilder:
    """Build Knowledge Graph from ISO/BCI data"""

    def __init__(self):
        self.graph = KnowledgeGraph()

    def build_from_iso_clauses(self, clauses: List[Any]) -> KnowledgeGraph:
        """
        Build knowledge graph from ISO clauses

        Args:
            clauses: List of ISO22301Clause objects

        Returns:
            KnowledgeGraph
        """

        logger.info(f"Building knowledge graph from {len(clauses)} ISO clauses...")

        for clause in clauses:
            # Add ISO clause node
            clause_node = Node(
                id=f"iso-{clause.clause_number}",
                type=NodeType.ISO_CLAUSE,
                properties={
                    'clause_number': clause.clause_number,
                    'title': clause.clause_title,
                    'category': self._get_category(clause.clause_number),
                    'description': clause.description
                }
            )
            self.graph.add_node(clause_node)

            # Add requirement nodes
            for i, requirement in enumerate(clause.requirements):
                req_node = Node(
                    id=f"req-{clause.clause_number}-{i}",
                    type=NodeType.REQUIREMENT,
                    properties={
                        'text': requirement,
                        'clause': clause.clause_number
                    }
                )
                self.graph.add_node(req_node)

                # Link clause to requirement
                self.graph.add_edge(Edge(
                    from_node=clause_node.id,
                    to_node=req_node.id,
                    relation_type=RelationType.REQUIRES
                ))

            # Add evidence nodes
            for i, evidence in enumerate(clause.evidence_needed):
                ev_node = Node(
                    id=f"evidence-{clause.clause_number}-{i}",
                    type=NodeType.EVIDENCE,
                    properties={
                        'name': evidence,
                        'clause': clause.clause_number
                    }
                )
                self.graph.add_node(ev_node)

                # Link clause to evidence
                self.graph.add_edge(Edge(
                    from_node=clause_node.id,
                    to_node=ev_node.id,
                    relation_type=RelationType.REQUIRES
                ))

            # Add audit question nodes
            for i, question in enumerate(clause.audit_questions):
                q_node = Node(
                    id=f"audit-{clause.clause_number}-{i}",
                    type=NodeType.AUDIT_QUESTION,
                    properties={
                        'question': question,
                        'clause': clause.clause_number
                    }
                )
                self.graph.add_node(q_node)

                # Link clause to audit question
                self.graph.add_edge(Edge(
                    from_node=clause_node.id,
                    to_node=q_node.id,
                    relation_type=RelationType.ASKS
                ))

        # Add BCI Professional Practices
        self._add_bci_practices()

        # Add clause dependencies
        self._add_clause_dependencies()

        stats = self.graph.get_statistics()
        logger.info(f"✅ Knowledge graph built: {stats['total_nodes']} nodes, {stats['total_edges']} edges")

        return self.graph

    def _add_bci_practices(self):
        """Add BCI Professional Practices and map to ISO clauses"""

        bci_mappings = {
            'PP1': {
                'title': 'Establishing BCMS',
                'iso_clauses': ['4.1', '4.2', '4.3', '4.4', '5.1', '5.2', '5.3', '6.1', '6.2']
            },
            'PP2': {
                'title': 'Embracing BC',
                'iso_clauses': ['7.1', '7.2', '7.3', '7.4']
            },
            'PP3': {
                'title': 'Analysis',
                'iso_clauses': ['8.2.2', '8.2.3']
            },
            'PP4': {
                'title': 'Design',
                'iso_clauses': ['8.3']
            },
            'PP5': {
                'title': 'Implementation',
                'iso_clauses': ['8.4.2', '8.4.4']
            },
            'PP6': {
                'title': 'Validation',
                'iso_clauses': ['8.5', '9.1', '9.2', '9.3']
            }
        }

        for practice_id, data in bci_mappings.items():
            # Add BCI practice node
            practice_node = Node(
                id=f"bci-{practice_id.lower()}",
                type=NodeType.BCI_PRACTICE,
                properties={
                    'practice_id': practice_id,
                    'title': data['title']
                }
            )
            self.graph.add_node(practice_node)

            # Link to ISO clauses
            for clause_number in data['iso_clauses']:
                clause_id = f"iso-{clause_number}"
                if clause_id in self.graph.nodes:
                    self.graph.add_edge(Edge(
                        from_node=practice_node.id,
                        to_node=clause_id,
                        relation_type=RelationType.MAPS_TO
                    ))

    def _add_clause_dependencies(self):
        """Add dependencies between ISO clauses"""

        # Some clauses naturally depend on others
        dependencies = {
            '8.2.2': ['4.3'],  # BIA depends on scope definition
            '8.2.3': ['4.3'],  # Risk assessment depends on scope
            '8.3': ['8.2.2', '8.2.3'],  # Strategy depends on BIA and risk
            '8.4.4': ['8.3'],  # Plans depend on strategy
            '8.5': ['8.4.4'],  # Exercises depend on plans
            '9.2': ['8.5'],  # Audit depends on exercises
            '10.1': ['9.2'],  # Corrective action depends on audit
        }

        for clause, depends_on in dependencies.items():
            from_id = f"iso-{clause}"
            for dep_clause in depends_on:
                to_id = f"iso-{dep_clause}"

                if from_id in self.graph.nodes and to_id in self.graph.nodes:
                    self.graph.add_edge(Edge(
                        from_node=from_id,
                        to_node=to_id,
                        relation_type=RelationType.DEPENDS_ON
                    ))

    def _get_category(self, clause_number: str) -> str:
        """Get category for clause number"""

        if clause_number.startswith('4.'):
            return 'context'
        elif clause_number.startswith('5.'):
            return 'leadership'
        elif clause_number.startswith('6.'):
            return 'planning'
        elif clause_number.startswith('7.'):
            return 'support'
        elif clause_number.startswith('8.'):
            return 'operation'
        elif clause_number.startswith('9.'):
            return 'performance'
        elif clause_number.startswith('10.'):
            return 'improvement'
        else:
            return 'other'


# Example usage
if __name__ == "__main__":
    from .iso_loader import ISO22301Loader

    # Load ISO clauses
    loader = ISO22301Loader()
    clauses = loader.load_all_clauses()

    # Build knowledge graph
    builder = KnowledgeGraphBuilder()
    kg = builder.build_from_iso_clauses(clauses)

    # Print statistics
    stats = kg.get_statistics()
    print(f"\n📊 Knowledge Graph Statistics:")
    print(f"  Total Nodes: {stats['total_nodes']}")
    print(f"  Total Edges: {stats['total_edges']}")
    print(f"\n  Nodes by Type:")
    for node_type, count in stats['nodes_by_type'].items():
        print(f"    {node_type}: {count}")
    print(f"\n  Edges by Type:")
    for edge_type, count in stats['edges_by_type'].items():
        print(f"    {edge_type}: {count}")

    # Example queries
    print(f"\n\n🔍 Example Queries:")

    # Evidence for BIA
    evidence = kg.get_iso_clause_evidence('8.2.2')
    print(f"\n  Evidence for Clause 8.2.2 (BIA):")
    for ev in evidence:
        print(f"    - {ev}")

    # BCI practice for BIA
    practice = kg.get_bci_practice_for_clause('8.2.2')
    print(f"\n  BCI Practice for Clause 8.2.2: {practice}")

    # All operation clauses
    operation_clauses = kg.query(
        node_type=NodeType.ISO_CLAUSE,
        filters={'category': 'operation'}
    )
    print(f"\n  Operation Clauses ({len(operation_clauses)}):")
    for clause in operation_clauses:
        print(f"    - {clause.properties['clause_number']}: {clause.properties['title']}")
