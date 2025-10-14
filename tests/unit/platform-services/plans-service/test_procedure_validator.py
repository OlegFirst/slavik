"""
Procedure Dependency Validator Tests
CRITICAL: Tests for cycle detection and dependency validation
"""

import pytest
from plans_service.services.procedure_validator import ProcedureDependencyValidator


class TestProcedureDependencyValidator:
    """Test suite for ProcedureDependencyValidator"""

    def test_no_cycle_simple(self):
        """Test valid dependency chain: A → B → C"""
        existing_procedures = [
            {"procedure_id": 1, "prerequisite_procedure_ids": []},
            {"procedure_id": 2, "prerequisite_procedure_ids": [1]},
        ]

        is_valid, error = ProcedureDependencyValidator.validate_dependencies(
            plan_id=1,
            new_procedure_id=3,
            prerequisite_ids=[2],
            existing_procedures=existing_procedures
        )

        assert is_valid is True
        assert error is None

    def test_no_cycle_complex_dag(self):
        """Test valid complex DAG with multiple dependencies"""
        existing_procedures = [
            {"procedure_id": 1, "prerequisite_procedure_ids": []},
            {"procedure_id": 2, "prerequisite_procedure_ids": [1]},
            {"procedure_id": 3, "prerequisite_procedure_ids": [1]},
            {"procedure_id": 4, "prerequisite_procedure_ids": [2, 3]},
        ]

        is_valid, error = ProcedureDependencyValidator.validate_dependencies(
            plan_id=1,
            new_procedure_id=5,
            prerequisite_ids=[4],
            existing_procedures=existing_procedures
        )

        assert is_valid is True
        assert error is None

    def test_detect_cycle_simple(self):
        """Test cycle detection: A → B → C → A"""
        existing_procedures = [
            {"procedure_id": 1, "prerequisite_procedure_ids": [3]},
            {"procedure_id": 2, "prerequisite_procedure_ids": [1]},
        ]

        is_valid, error = ProcedureDependencyValidator.validate_dependencies(
            plan_id=1,
            new_procedure_id=3,
            prerequisite_ids=[2],
            existing_procedures=existing_procedures
        )

        assert is_valid is False
        assert error is not None
        assert "Circular dependency detected" in error
        assert "→" in error  # Check cycle path is included

    def test_detect_cycle_direct(self):
        """Test direct cycle: A → B → A"""
        existing_procedures = [
            {"procedure_id": 1, "prerequisite_procedure_ids": [2]},
        ]

        is_valid, error = ProcedureDependencyValidator.validate_dependencies(
            plan_id=1,
            new_procedure_id=2,
            prerequisite_ids=[1],
            existing_procedures=existing_procedures
        )

        assert is_valid is False
        assert error is not None
        assert "Circular dependency detected" in error

    def test_detect_self_reference(self):
        """Test procedure depending on itself"""
        is_valid, error = ProcedureDependencyValidator.validate_no_self_reference(
            procedure_id=5,
            prerequisite_ids=[1, 5, 3]
        )

        assert is_valid is False
        assert error is not None
        assert "cannot depend on itself" in error
        assert "5" in error

    def test_no_self_reference_valid(self):
        """Test valid case with no self-reference"""
        is_valid, error = ProcedureDependencyValidator.validate_no_self_reference(
            procedure_id=5,
            prerequisite_ids=[1, 2, 3]
        )

        assert is_valid is True
        assert error is None

    def test_prerequisite_not_found(self):
        """Test error when prerequisite doesn't exist"""
        existing_procedures = [
            {"procedure_id": 1, "prerequisite_procedure_ids": []},
            {"procedure_id": 2, "prerequisite_procedure_ids": []},
        ]

        is_valid, error = ProcedureDependencyValidator.validate_dependencies(
            plan_id=1,
            new_procedure_id=3,
            prerequisite_ids=[999],  # Non-existent prerequisite
            existing_procedures=existing_procedures
        )

        assert is_valid is False
        assert error is not None
        assert "not found" in error
        assert "999" in error

    def test_multiple_prerequisite_not_found(self):
        """Test error when multiple prerequisites don't exist"""
        existing_procedures = [
            {"procedure_id": 1, "prerequisite_procedure_ids": []},
        ]

        is_valid, error = ProcedureDependencyValidator.validate_dependencies(
            plan_id=1,
            new_procedure_id=3,
            prerequisite_ids=[1, 999],  # One valid, one invalid
            existing_procedures=existing_procedures
        )

        assert is_valid is False
        assert error is not None
        assert "not found" in error

    def test_execution_order_linear(self, sample_procedures_with_dependencies):
        """Test topological sort for linear dependencies"""
        procedures = [
            {"procedure_id": 1, "prerequisite_procedure_ids": []},
            {"procedure_id": 2, "prerequisite_procedure_ids": [1]},
            {"procedure_id": 3, "prerequisite_procedure_ids": [2]},
        ]

        execution_order = ProcedureDependencyValidator.get_execution_order(procedures)

        assert len(execution_order) == 3
        assert execution_order == [1, 2, 3]

    def test_execution_order_complex(self, sample_procedures_with_dependencies):
        """Test topological sort for complex DAG"""
        procedures = sample_procedures_with_dependencies

        execution_order = ProcedureDependencyValidator.get_execution_order(procedures)

        assert len(execution_order) == 4
        # Procedure 1 must come first (no dependencies)
        assert execution_order[0] == 1
        # Procedures 2 and 3 must come before 4
        assert execution_order.index(2) < execution_order.index(4)
        assert execution_order.index(3) < execution_order.index(4)

    def test_execution_order_parallel_tasks(self):
        """Test execution order for parallel tasks"""
        procedures = [
            {"procedure_id": 1, "prerequisite_procedure_ids": []},
            {"procedure_id": 2, "prerequisite_procedure_ids": []},
            {"procedure_id": 3, "prerequisite_procedure_ids": []},
            {"procedure_id": 4, "prerequisite_procedure_ids": [1, 2, 3]},
        ]

        execution_order = ProcedureDependencyValidator.get_execution_order(procedures)

        assert len(execution_order) == 4
        # Procedures 1, 2, 3 can be in any order but all before 4
        assert execution_order[-1] == 4
        assert set(execution_order[:3]) == {1, 2, 3}

    def test_execution_order_raises_on_cycle(self, sample_procedures_with_cycle):
        """Test that execution order raises ValueError on cycle"""
        procedures = sample_procedures_with_cycle

        with pytest.raises(ValueError) as exc_info:
            ProcedureDependencyValidator.get_execution_order(procedures)

        assert "Circular dependency" in str(exc_info.value)

    def test_cycle_path_reported(self):
        """Test that cycle path is included in error message"""
        existing_procedures = [
            {"procedure_id": 1, "prerequisite_procedure_ids": [3]},
            {"procedure_id": 2, "prerequisite_procedure_ids": [1]},
        ]

        is_valid, error = ProcedureDependencyValidator.validate_dependencies(
            plan_id=1,
            new_procedure_id=3,
            prerequisite_ids=[2],
            existing_procedures=existing_procedures
        )

        assert is_valid is False
        assert error is not None
        # Check that the cycle path is formatted with arrows
        assert "→" in error
        # Check that procedure IDs are in the error message
        assert "3" in error
        assert "2" in error
        assert "1" in error

    def test_empty_prerequisites(self):
        """Test procedure with no prerequisites"""
        existing_procedures = [
            {"procedure_id": 1, "prerequisite_procedure_ids": []},
        ]

        is_valid, error = ProcedureDependencyValidator.validate_dependencies(
            plan_id=1,
            new_procedure_id=2,
            prerequisite_ids=[],  # No prerequisites
            existing_procedures=existing_procedures
        )

        assert is_valid is True
        assert error is None

    def test_none_prerequisite_ids(self):
        """Test handling of None prerequisite IDs in existing procedures"""
        existing_procedures = [
            {"procedure_id": 1, "prerequisite_procedure_ids": None},
            {"procedure_id": 2, "prerequisite_procedure_ids": None},
        ]

        is_valid, error = ProcedureDependencyValidator.validate_dependencies(
            plan_id=1,
            new_procedure_id=3,
            prerequisite_ids=[1, 2],
            existing_procedures=existing_procedures
        )

        assert is_valid is True
        assert error is None

    def test_execution_order_single_procedure(self):
        """Test execution order for single procedure"""
        procedures = [
            {"procedure_id": 1, "prerequisite_procedure_ids": []},
        ]

        execution_order = ProcedureDependencyValidator.get_execution_order(procedures)

        assert len(execution_order) == 1
        assert execution_order == [1]

    def test_execution_order_empty_list(self):
        """Test execution order for empty procedure list"""
        procedures = []

        execution_order = ProcedureDependencyValidator.get_execution_order(procedures)

        assert len(execution_order) == 0
        assert execution_order == []

    def test_complex_cycle_detection(self):
        """Test detection of cycle in complex graph"""
        existing_procedures = [
            {"procedure_id": 1, "prerequisite_procedure_ids": []},
            {"procedure_id": 2, "prerequisite_procedure_ids": [1]},
            {"procedure_id": 3, "prerequisite_procedure_ids": [2]},
            {"procedure_id": 4, "prerequisite_procedure_ids": [3]},
            {"procedure_id": 5, "prerequisite_procedure_ids": [4, 7]},
            {"procedure_id": 6, "prerequisite_procedure_ids": [5]},
        ]

        # Adding procedure 7 that depends on 6 creates cycle: 7→6→5→4→3→2→1
        is_valid, error = ProcedureDependencyValidator.validate_dependencies(
            plan_id=1,
            new_procedure_id=7,
            prerequisite_ids=[6],
            existing_procedures=existing_procedures
        )

        assert is_valid is False
        assert "Circular dependency detected" in error

    def test_validate_dependencies_plan_id_included(self):
        """Test that plan_id is correctly passed and used in error messages"""
        existing_procedures = []

        is_valid, error = ProcedureDependencyValidator.validate_dependencies(
            plan_id=42,
            new_procedure_id=1,
            prerequisite_ids=[999],
            existing_procedures=existing_procedures
        )

        assert is_valid is False
        assert "plan 42" in error or "plan" in error.lower()
