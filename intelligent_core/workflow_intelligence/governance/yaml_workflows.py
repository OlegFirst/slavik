"""
YAML-based Governance Workflows

Declarative workflow definitions with validation and security checkpoints
"""

from typing import Dict, Any, List
import yaml
from pathlib import Path
from dataclasses import dataclass


@dataclass
class WorkflowCheckpoint:
    """Checkpoint in workflow"""
    checkpoint_type: str  # validation, security, compliance
    rules: Dict[str, Any]
    description: str = ""


@dataclass
class WorkflowStage:
    """Stage in workflow"""
    name: str
    checkpoints: List[WorkflowCheckpoint]
    required_permissions: List[str] = None
    iso_clause: str = None


class YAMLWorkflowEngine:
    """
    YAML-based workflow engine

    Loads workflow definitions from YAML files and validates execution
    """

    def __init__(self, definitions_path: str = None):
        """
        Initialize YAML workflow engine

        Args:
            definitions_path: Path to workflow definitions directory
        """
        self.definitions_path = definitions_path or "./workflows/definitions"
        self.workflows: Dict[str, Dict[str, Any]] = {}

    def load_workflow(self, module: str) -> Dict[str, Any]:
        """
        Load workflow definition from YAML

        Args:
            module: Module name (e.g., "bia", "risk", "planning")

        Returns:
            Workflow definition dict
        """

        yaml_path = Path(self.definitions_path) / f"{module}_workflow.yaml"

        if not yaml_path.exists():
            # Return default minimal workflow
            return self._get_default_workflow(module)

        with open(yaml_path, 'r') as f:
            workflow_def = yaml.safe_load(f)

        self.workflows[module] = workflow_def
        return workflow_def

    def _get_default_workflow(self, module: str) -> Dict[str, Any]:
        """Get default workflow for module"""
        return {
            'name': f'{module.upper()} Workflow',
            'module': module,
            'stages': [
                {
                    'name': 'initialize',
                    'checkpoints': []
                },
                {
                    'name': 'execute',
                    'checkpoints': []
                },
                {
                    'name': 'complete',
                    'checkpoints': []
                }
            ]
        }

    async def validate_stage(
        self,
        module: str,
        stage_name: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate workflow stage checkpoints

        Args:
            module: Module name
            stage_name: Current stage
            context: Workflow context

        Returns:
            {
                "valid": bool,
                "checkpoint_results": [...],
                "errors": [...]
            }
        """

        workflow = self.workflows.get(module)
        if not workflow:
            workflow = self.load_workflow(module)

        # Find stage
        stage = None
        for s in workflow.get('stages', []):
            if s['name'] == stage_name:
                stage = s
                break

        if not stage:
            return {
                "valid": True,
                "checkpoint_results": [],
                "errors": [],
                "note": f"Stage {stage_name} not found in workflow definition"
            }

        # Validate checkpoints
        checkpoint_results = []
        errors = []

        for checkpoint in stage.get('checkpoints', []):
            result = await self._validate_checkpoint(checkpoint, context)
            checkpoint_results.append(result)

            if not result['passed']:
                errors.append(result['error'])

        return {
            "valid": len(errors) == 0,
            "checkpoint_results": checkpoint_results,
            "errors": errors
        }

    async def _validate_checkpoint(
        self,
        checkpoint: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate single checkpoint"""

        checkpoint_type = checkpoint.get('type')
        rules = checkpoint.get('rules', {})

        if checkpoint_type == 'validation':
            return self._validate_data(rules, context)
        elif checkpoint_type == 'security':
            return self._validate_security(rules, context)
        elif checkpoint_type == 'compliance':
            return self._validate_compliance(rules, context)

        return {
            "checkpoint_type": checkpoint_type,
            "passed": True,
            "error": None
        }

    def _validate_data(
        self,
        rules: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate data rules"""

        errors = []
        context_data = context.get('data', {})

        # Check required fields
        for field in rules.get('required_fields', []):
            if field not in context_data or not context_data[field]:
                errors.append(f"Missing required field: {field}")

        # Check minimum counts
        for field, min_count in rules.get('min_counts', {}).items():
            if field in context_data:
                items = context_data[field]
                if isinstance(items, list) and len(items) < min_count:
                    errors.append(f"{field} requires at least {min_count} items")

        return {
            "checkpoint_type": "validation",
            "passed": len(errors) == 0,
            "error": "; ".join(errors) if errors else None
        }

    def _validate_security(
        self,
        rules: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate security rules"""

        # Security validation would check permissions, etc
        # Simplified for now

        return {
            "checkpoint_type": "security",
            "passed": True,
            "error": None
        }

    def _validate_compliance(
        self,
        rules: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate compliance rules"""

        errors = []

        # Check ISO clause requirements
        if 'iso_clause' in rules:
            required_docs = rules.get('required_documentation', False)
            if required_docs and not context.get('documentation'):
                errors.append(f"ISO {rules['iso_clause']}: Documentation required")

        return {
            "checkpoint_type": "compliance",
            "passed": len(errors) == 0,
            "error": "; ".join(errors) if errors else None
        }


# Example YAML workflow definition:
EXAMPLE_BIA_WORKFLOW = """
name: "BIA Workflow"
module: "bia"
iso_clause: "8.2.2"

stages:
  - name: "identify_processes"
    checkpoints:
      - type: "validation"
        rules:
          required_fields: ["process_name", "process_owner", "description"]
          min_counts:
            processes: 3

      - type: "security"
        rules:
          check_permissions: ["bia.process.create"]

  - name: "assess_impact"
    checkpoints:
      - type: "validation"
        rules:
          required_fields: ["financial_impact", "operational_impact"]

      - type: "compliance"
        rules:
          iso_clause: "8.2.2"
          required_documentation: true

  - name: "define_requirements"
    checkpoints:
      - type: "validation"
        rules:
          required_fields: ["rto", "rpo", "mtpd"]
"""
