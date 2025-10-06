"""
Procedure Dependency Validation
Validates procedure dependencies and detects cycles
"""

from typing import List, Dict, Set, Optional
import logging

logger = logging.getLogger(__name__)


class ProcedureDependencyValidator:
    """Validates procedure dependencies and detects circular references"""

    @staticmethod
    def validate_dependencies(
        plan_id: int,
        new_procedure_id: int,
        prerequisite_ids: List[int],
        existing_procedures: List[Dict]
    ) -> tuple[bool, Optional[str]]:
        """
        Validate procedure dependencies for cycles

        Args:
            plan_id: ID of the plan
            new_procedure_id: ID of the new procedure being added
            prerequisite_ids: List of prerequisite procedure IDs
            existing_procedures: List of existing procedures with their dependencies

        Returns:
            (is_valid, error_message)
        """
        # 1. Check all prerequisites exist and belong to same plan
        existing_ids = {p['procedure_id'] for p in existing_procedures}

        for prereq_id in prerequisite_ids:
            if prereq_id not in existing_ids:
                return False, f"Prerequisite procedure {prereq_id} not found in plan {plan_id}"

        # 2. Build dependency graph
        dependency_graph = {}
        for proc in existing_procedures:
            proc_id = proc['procedure_id']
            prereqs = proc.get('prerequisite_procedure_ids') or []
            dependency_graph[proc_id] = prereqs

        # Add new procedure to graph
        dependency_graph[new_procedure_id] = prerequisite_ids

        # 3. Detect cycles using DFS
        has_cycle, cycle_path = ProcedureDependencyValidator._detect_cycle(
            dependency_graph,
            new_procedure_id
        )

        if has_cycle:
            cycle_str = " → ".join(map(str, cycle_path))
            return False, f"Circular dependency detected: {cycle_str}"

        return True, None

    @staticmethod
    def _detect_cycle(
        graph: Dict[int, List[int]],
        start_node: int
    ) -> tuple[bool, List[int]]:
        """
        Detect cycles in dependency graph using DFS

        Returns:
            (has_cycle, cycle_path)
        """
        visited: Set[int] = set()
        rec_stack: Set[int] = set()
        path: List[int] = []

        def dfs(node: int) -> bool:
            """Depth-first search to detect cycles"""
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            # Visit all dependencies
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    # Cycle detected - add the cycle-closing node
                    path.append(neighbor)
                    return True

            rec_stack.remove(node)
            path.pop()
            return False

        has_cycle = dfs(start_node)

        if has_cycle:
            # Extract the cycle from path
            cycle_start_idx = path.index(path[-1])
            cycle_path = path[cycle_start_idx:]
            return True, cycle_path

        return False, []

    @staticmethod
    def get_execution_order(
        procedures: List[Dict]
    ) -> List[int]:
        """
        Calculate optimal execution order based on dependencies
        Returns list of procedure IDs in execution order (topological sort)

        Args:
            procedures: List of procedures with their dependencies

        Returns:
            List of procedure IDs in execution order

        Raises:
            ValueError: If circular dependency is detected
        """
        # Build dependency graph
        graph = {}
        in_degree = {}

        for proc in procedures:
            proc_id = proc['procedure_id']
            graph[proc_id] = proc.get('prerequisite_procedure_ids') or []
            in_degree[proc_id] = 0

        # Calculate in-degrees
        for proc_id in graph:
            for prereq in graph[proc_id]:
                if prereq in in_degree:
                    in_degree[prereq] += 1

        # Topological sort using Kahn's algorithm
        queue = [proc_id for proc_id in in_degree if in_degree[proc_id] == 0]
        execution_order = []

        while queue:
            # Process node with no dependencies
            current = queue.pop(0)
            execution_order.append(current)

            # Reduce in-degree for dependent procedures
            for proc_id in graph:
                if current in graph[proc_id]:
                    in_degree[proc_id] -= 1
                    if in_degree[proc_id] == 0:
                        queue.append(proc_id)

        # If not all procedures are in execution order, there's a cycle
        if len(execution_order) != len(procedures):
            raise ValueError("Circular dependency detected in procedures")

        return execution_order

    @staticmethod
    def validate_no_self_reference(
        procedure_id: int,
        prerequisite_ids: List[int]
    ) -> tuple[bool, Optional[str]]:
        """Check if procedure references itself"""
        if procedure_id in prerequisite_ids:
            return False, f"Procedure {procedure_id} cannot depend on itself"
        return True, None
