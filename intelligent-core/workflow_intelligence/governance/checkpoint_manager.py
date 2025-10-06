"""
Checkpoints System
==================

Extracted from: /Users/MD/AI-Platform-ISO/SESSION_SUMMARY.md
Source lines: 2964-3300
Date extracted: 2025-10-04

Description:
-----------
Checkpoint management system for mandatory validation points in workflows.
Integrates with Rules Engine and Creative Zones to provide managed autonomy.

Features:
- Mandatory validation checkpoints
- Integration with Rules Engine
- Escalation logic
- Next steps generation
- BIA-specific checkpoints

Philosophy:
- Checkpoint = обязательная валидация перед переходом
- Creative Zone = AI свободен в методах, но не в целях
- Escalation = critical violations → человек решает

Dependencies:
- rules_engine_extracted.py (RulesEngine, RuleViolation, RuleSeverity)
- creative_zones_extracted.py (CreativeZonesManager)
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Checkpoint:
    """Обязательная точка валидации"""
    checkpoint_id: str
    name: str
    stage: str
    description: str
    rules_to_check: List[str]  # Rule IDs
    can_skip: bool = False
    escalation_required: bool = False


class CheckpointManager:
    """
    Управление checkpoints

    Checkpoint = обязательная валидация перед переходом
    Creative Zone = AI свободен в методах, но не в целях
    """

    def __init__(
        self,
        rules_engine,  # RulesEngine
        creative_zones  # CreativeZonesManager
    ):
        self.rules = rules_engine
        self.zones = creative_zones
        self.checkpoints: Dict[str, Checkpoint] = {}

    def register_checkpoint(self, checkpoint: Checkpoint):
        """Зарегистрировать checkpoint"""
        self.checkpoints[checkpoint.checkpoint_id] = checkpoint

    async def validate_checkpoint(
        self,
        checkpoint_id: str,
        context: Dict[str, Any]
    ) -> tuple[bool, List, Dict[str, Any]]:  # tuple[bool, List[RuleViolation], Dict[str, Any]]
        """
        Валидировать checkpoint

        Returns:
            (passed, violations, guidance)
        """
        checkpoint = self.checkpoints.get(checkpoint_id)
        if not checkpoint:
            raise ValueError(f"Unknown checkpoint: {checkpoint_id}")

        # Validate specific rules for this checkpoint
        violations = []
        for rule_id in checkpoint.rules_to_check:
            rule = self.rules.rules.get(rule_id)
            if rule:
                is_valid, message = rule.validation_fn(context)
                if not is_valid:
                    # Note: In production, import RuleViolation from rules_engine_extracted
                    violation = {
                        'rule_id': rule.rule_id,
                        'rule_name': rule.name,
                        'severity': rule.severity,
                        'message': message,
                        'context': context,
                        'timestamp': datetime.utcnow().isoformat()
                    }
                    violations.append(violation)

        # Check if can proceed
        critical_violations = [
            v for v in violations
            if v['severity'].value in ['critical', 'high']
        ]

        can_proceed = len(critical_violations) == 0 or checkpoint.can_skip
        needs_escalation = checkpoint.escalation_required and len(violations) > 0

        # Generate guidance
        guidance = {
            'checkpoint': checkpoint.name,
            'passed': can_proceed,
            'violations': [
                {
                    'rule': v['rule_name'],
                    'severity': v['severity'].value,
                    'message': v['message']
                }
                for v in violations
            ],
            'needs_escalation': needs_escalation,
            'next_steps': self._generate_next_steps(checkpoint, violations)
        }

        return can_proceed, violations, guidance

    def is_checkpoint(self, stage: str) -> bool:
        """Проверить является ли stage checkpoint"""
        return any(c.stage == stage for c in self.checkpoints.values())

    def is_creative_zone(self, stage: str) -> bool:
        """Проверить является ли stage creative zone"""
        return self.zones.is_creative_zone(stage, "")

    def get_stage_mode(self, stage: str) -> str:
        """Получить режим для stage"""
        if self.is_checkpoint(stage):
            return "checkpoint"  # Жесткая валидация
        elif self.is_creative_zone(stage):
            return "creative"    # AI свобода
        else:
            return "standard"     # Обычное выполнение

    def _generate_next_steps(
        self,
        checkpoint: Checkpoint,
        violations: List[Dict]
    ) -> List[str]:
        """Сгенерировать next steps для исправления"""
        next_steps = []

        for violation in violations:
            message = violation.get('message', '')
            rule_name = violation.get('rule_name', '')

            if 'minimum' in message.lower():
                next_steps.append(f"Add more data to meet {rule_name}")
            elif 'missing' in message.lower():
                next_steps.append(f"Provide missing: {rule_name}")
            elif 'rationale' in message.lower():
                next_steps.append(f"Add detailed rationale for {rule_name}")
            else:
                next_steps.append(f"Fix: {message}")

        return next_steps


class BIACheckpoints:
    """Checkpoints для BIA workflow"""

    @staticmethod
    def get_all_checkpoints() -> List[Checkpoint]:
        return [
            Checkpoint(
                checkpoint_id="bia_cp_001",
                name="Process Identification Complete",
                stage="identify_processes",
                description="Validate minimum processes identified before moving forward",
                rules_to_check=[
                    "bia_mand_001",  # Minimum 3 processes
                    "bia_mand_002",  # At least one Tier 1
                    "bia_bp_001"     # Process owners
                ],
                can_skip=False,
                escalation_required=False
            ),

            Checkpoint(
                checkpoint_id="bia_cp_002",
                name="Dependencies Mapped",
                stage="analyze_dependencies",
                description="Validate dependency mapping complete",
                rules_to_check=[
                    "bia_const_003",  # Tier 1 dependencies
                    "bia_bp_002"      # Dependency details
                ],
                can_skip=False,
                escalation_required=True  # Tier 1 violations need human
            ),

            Checkpoint(
                checkpoint_id="bia_cp_003",
                name="Impact Assessment Complete",
                stage="assess_impact",
                description="Validate all impacts assessed",
                rules_to_check=[
                    "bia_const_002",  # Financial impact exists
                    "bia_mand_003"    # All impact types
                ],
                can_skip=False,
                escalation_required=False
            ),

            Checkpoint(
                checkpoint_id="bia_cp_004",
                name="RTO Determination Valid",
                stage="determine_rto",
                description="Validate RTO decisions",
                rules_to_check=[
                    "bia_const_001",  # No RTO < 1h without justification
                    "bia_mand_004",   # RTO rationale
                    "bia_bp_003"      # RPO/RTO alignment
                ],
                can_skip=False,
                escalation_required=True  # RTO violations need human review
            ),

            Checkpoint(
                checkpoint_id="bia_cp_005",
                name="Final BIA Validation",
                stage="review_results",
                description="Complete BIA validation before completion",
                rules_to_check=[
                    # All constitution rules
                    "bia_const_001",
                    "bia_const_002",
                    "bia_const_003",
                    # All mandatory rules
                    "bia_mand_001",
                    "bia_mand_002",
                    "bia_mand_003",
                    "bia_mand_004"
                ],
                can_skip=False,
                escalation_required=True
            )
        ]
