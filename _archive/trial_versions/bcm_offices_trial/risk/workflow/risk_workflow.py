"""
Risk Workflow Engine
====================

Extends: workflow_intelligence.core.state_machine.StateMachine

Risk assessment workflow with FAIR methodology:
- Identify risks
- Analyze likelihood
- Calculate impact
- FAIR analysis (TEF × LM = ALE)
- Treatment planning
"""

import sys
from pathlib import Path
from typing import Dict, Any, List

# Add workflow_intelligence to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "workflow_intelligence"))

from core.state_machine import (
    StateMachine,
    StateTransition,
    WorkflowState,
    ValidationError,
    TransitionError
)
from datetime import datetime


class RiskStage:
    """Risk workflow stages"""
    NOT_STARTED = "not_started"
    IDENTIFY_RISKS = "identify_risks"
    ANALYZE_LIKELIHOOD = "analyze_likelihood"
    CALCULATE_IMPACT = "calculate_impact"
    FAIR_ANALYSIS = "fair_analysis"
    TREATMENT_PLANNING = "treatment_planning"
    REVIEW_RESULTS = "review_results"
    COMPLETED = "completed"


class RiskWorkflow(StateMachine):
    """
    Risk Assessment Workflow

    Extends StateMachine from workflow_intelligence

    Stages:
    1. NOT_STARTED → IDENTIFY_RISKS (start)
    2. IDENTIFY_RISKS → ANALYZE_LIKELIHOOD (min 1 risk)
    3. ANALYZE_LIKELIHOOD → CALCULATE_IMPACT (likelihood scored)
    4. CALCULATE_IMPACT → FAIR_ANALYSIS (impact calculated)
    5. FAIR_ANALYSIS → TREATMENT_PLANNING (FAIR complete)
    6. TREATMENT_PLANNING → REVIEW_RESULTS (treatment defined)
    7. REVIEW_RESULTS → COMPLETED (or back to IDENTIFY_RISKS)
    """

    def __init__(self, risk_workflow_id: str, org_context: Dict[str, Any]):
        """
        Initialize Risk Workflow

        Args:
            risk_workflow_id: Unique workflow ID
            org_context: Organization context (industry, size, etc)
        """
        super().__init__(
            workflow_id=risk_workflow_id,
            initial_state=RiskStage.NOT_STARTED
        )

        self.org_context = org_context
        self._setup_transitions()
        self._setup_requirements()

    def _setup_transitions(self):
        """Define all transitions for Risk workflow"""

        # NOT_STARTED → IDENTIFY_RISKS
        self.define_transition(
            from_state=RiskStage.NOT_STARTED,
            to_state=RiskStage.IDENTIFY_RISKS,
            on_enter=self._on_start_identify_risks
        )

        # IDENTIFY_RISKS → ANALYZE_LIKELIHOOD
        self.define_transition(
            from_state=RiskStage.IDENTIFY_RISKS,
            to_state=RiskStage.ANALYZE_LIKELIHOOD,
            condition=lambda data: len(data.get('risks', [])) >= 1,
            validators=[self._validate_risks],
            required_data=['risks'],
            on_exit=self._on_exit_identify_risks
        )

        # ANALYZE_LIKELIHOOD → CALCULATE_IMPACT
        self.define_transition(
            from_state=RiskStage.ANALYZE_LIKELIHOOD,
            to_state=RiskStage.CALCULATE_IMPACT,
            validators=[self._validate_likelihood],
            required_data=['risks', 'likelihood_scores']
        )

        # CALCULATE_IMPACT → FAIR_ANALYSIS
        self.define_transition(
            from_state=RiskStage.CALCULATE_IMPACT,
            to_state=RiskStage.FAIR_ANALYSIS,
            validators=[self._validate_impact],
            required_data=['risks', 'likelihood_scores', 'impact_scores']
        )

        # FAIR_ANALYSIS → TREATMENT_PLANNING
        self.define_transition(
            from_state=RiskStage.FAIR_ANALYSIS,
            to_state=RiskStage.TREATMENT_PLANNING,
            validators=[self._validate_fair],
            required_data=['risks', 'fair_metrics']
        )

        # TREATMENT_PLANNING → REVIEW_RESULTS
        self.define_transition(
            from_state=RiskStage.TREATMENT_PLANNING,
            to_state=RiskStage.REVIEW_RESULTS,
            validators=[self._validate_treatments],
            required_data=['risks', 'treatments']
        )

        # REVIEW_RESULTS → COMPLETED
        self.define_transition(
            from_state=RiskStage.REVIEW_RESULTS,
            to_state=RiskStage.COMPLETED,
            on_enter=self._on_complete
        )

        # REVIEW_RESULTS → IDENTIFY_RISKS (allow going back)
        self.define_transition(
            from_state=RiskStage.REVIEW_RESULTS,
            to_state=RiskStage.IDENTIFY_RISKS
        )

    def _setup_requirements(self):
        """Define requirements for each stage"""
        self.stage_requirements = {
            RiskStage.IDENTIFY_RISKS: {
                "min_risks": 1,
                "required_fields": ["description", "threat", "vulnerability"]
            },
            RiskStage.ANALYZE_LIKELIHOOD: {
                "required_fields": ["likelihood_score", "frequency_estimate"]
            },
            RiskStage.CALCULATE_IMPACT: {
                "required_impact_types": [
                    "financial", "operational", "reputational", "regulatory"
                ]
            },
            RiskStage.FAIR_ANALYSIS: {
                "required_fields": ["tef", "lm", "ale"],
                "min_ale": 0
            },
            RiskStage.TREATMENT_PLANNING: {
                "required_fields": ["treatment_type", "actions", "priority"]
            }
        }

    # ========================================================================
    # VALIDATORS
    # ========================================================================

    def _validate_risks(self, data: Dict[str, Any]) -> bool:
        """Validate risks identified"""
        risks = data.get('risks', [])

        if len(risks) < 1:
            raise ValidationError("At least 1 risk must be identified")

        required_fields = self.stage_requirements[RiskStage.IDENTIFY_RISKS]["required_fields"]

        for risk in risks:
            for field in required_fields:
                if not risk.get(field):
                    raise ValidationError(f"Risk missing required field: {field}")

        return True

    def _validate_likelihood(self, data: Dict[str, Any]) -> bool:
        """Validate likelihood scores"""
        likelihood_scores = data.get('likelihood_scores', {})
        risks = data.get('risks', [])

        for risk in risks:
            risk_id = risk.get('id')
            if risk_id not in likelihood_scores:
                raise ValidationError(f"Risk {risk_id} missing likelihood score")

            score = likelihood_scores[risk_id]
            if not (1 <= score.get('score', 0) <= 5):
                raise ValidationError(f"Likelihood score must be 1-5, got {score.get('score')}")

        return True

    def _validate_impact(self, data: Dict[str, Any]) -> bool:
        """Validate impact calculations"""
        impact_scores = data.get('impact_scores', {})
        required_types = self.stage_requirements[RiskStage.CALCULATE_IMPACT]["required_impact_types"]

        for risk_id, impacts in impact_scores.items():
            for impact_type in required_types:
                if impact_type not in impacts:
                    raise ValidationError(f"Risk {risk_id} missing {impact_type} impact")

        return True

    def _validate_fair(self, data: Dict[str, Any]) -> bool:
        """Validate FAIR analysis"""
        fair_metrics = data.get('fair_metrics', {})
        required_fields = self.stage_requirements[RiskStage.FAIR_ANALYSIS]["required_fields"]

        for risk_id, metrics in fair_metrics.items():
            for field in required_fields:
                if field not in metrics:
                    raise ValidationError(f"Risk {risk_id} missing FAIR metric: {field}")

            # Validate FAIR formula: TEF × LM = ALE
            tef = metrics.get('tef', 0)
            lm = metrics.get('lm', 0)
            ale = metrics.get('ale', 0)

            expected_ale = tef * lm
            if abs(ale - expected_ale) > 0.01:
                raise ValidationError(
                    f"Risk {risk_id} ALE calculation error: {tef} × {lm} ≠ {ale}"
                )

        return True

    def _validate_treatments(self, data: Dict[str, Any]) -> bool:
        """Validate risk treatments"""
        treatments = data.get('treatments', {})
        required_fields = self.stage_requirements[RiskStage.TREATMENT_PLANNING]["required_fields"]

        for risk_id, treatment in treatments.items():
            for field in required_fields:
                if field not in treatment:
                    raise ValidationError(f"Risk {risk_id} treatment missing: {field}")

            # Validate treatment type
            valid_types = ["reduce", "accept", "transfer", "avoid"]
            if treatment.get('treatment_type') not in valid_types:
                raise ValidationError(
                    f"Invalid treatment type: {treatment.get('treatment_type')}"
                )

        return True

    # ========================================================================
    # HOOKS
    # ========================================================================

    async def _on_start_identify_risks(self, state: WorkflowState):
        """Hook: entering IDENTIFY_RISKS stage"""
        state.metadata['started_at'] = datetime.utcnow().isoformat()
        state.metadata['industry'] = self.org_context.get('industry')

    async def _on_exit_identify_risks(self, state: WorkflowState):
        """Hook: exiting IDENTIFY_RISKS stage"""
        risks_count = len(state.data.get('risks', []))
        state.metadata['risks_identified'] = risks_count

    async def _on_complete(self, state: WorkflowState):
        """Hook: workflow completed"""
        state.metadata['completed_at'] = datetime.utcnow().isoformat()
        state.metadata['total_risks'] = len(state.data.get('risks', []))
        state.metadata['treatments_planned'] = len(state.data.get('treatments', {}))

    # ========================================================================
    # CONTEXT FOR AI
    # ========================================================================

    def get_available_actions(self) -> List[Dict[str, Any]]:
        """
        Get available actions for current stage

        Returns actions user can take (for UI + AI)
        """
        current_stage = self.current_state.name

        actions = []

        if current_stage == RiskStage.IDENTIFY_RISKS:
            actions.extend([
                {
                    "id": "add_risk",
                    "label": "Add Risk",
                    "type": "primary"
                },
                {
                    "id": "ai_suggest_risks",
                    "label": "AI: Suggest Risks",
                    "type": "secondary",
                    "requires_ai": True
                }
            ])

        elif current_stage == RiskStage.ANALYZE_LIKELIHOOD:
            actions.append({
                "id": "ai_analyze_likelihood",
                "label": "AI: Analyze Likelihood",
                "type": "primary",
                "requires_ai": True
            })

        elif current_stage == RiskStage.CALCULATE_IMPACT:
            actions.append({
                "id": "ai_calculate_impact",
                "label": "AI: Calculate Impact",
                "type": "primary",
                "requires_ai": True
            })

        elif current_stage == RiskStage.FAIR_ANALYSIS:
            actions.append({
                "id": "ai_fair_analysis",
                "label": "AI: FAIR Analysis",
                "type": "primary",
                "requires_ai": True
            })

        elif current_stage == RiskStage.TREATMENT_PLANNING:
            actions.append({
                "id": "ai_suggest_treatments",
                "label": "AI: Suggest Treatments",
                "type": "primary",
                "requires_ai": True
            })

        return actions

    def identify_gaps(self) -> List[Dict[str, str]]:
        """
        Identify what's missing for current stage

        Used by AI Context Builder
        """
        current_stage = self.current_state.name
        data = self.current_state.data
        gaps = []

        requirements = self.stage_requirements.get(current_stage, {})

        if current_stage == RiskStage.IDENTIFY_RISKS:
            min_risks = requirements.get("min_risks", 1)
            current_risks = len(data.get('risks', []))

            if current_risks < min_risks:
                gaps.append({
                    "type": "insufficient_data",
                    "message": f"Need {min_risks} risks, have {current_risks}",
                    "severity": "critical"
                })

        elif current_stage == RiskStage.ANALYZE_LIKELIHOOD:
            risks = data.get('risks', [])
            likelihood_scores = data.get('likelihood_scores', {})

            missing = len(risks) - len(likelihood_scores)
            if missing > 0:
                gaps.append({
                    "type": "missing_analysis",
                    "message": f"{missing} risks need likelihood analysis",
                    "severity": "high"
                })

        # ... аналогично для других stages

        return gaps
