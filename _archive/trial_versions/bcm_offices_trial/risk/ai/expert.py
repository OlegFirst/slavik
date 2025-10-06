"""
Risk Expert - Business Logic Layer for Risk Office

Integrates:
- RiskTools (DB operations)
- RiskOrgan (LLM analysis)
- RiskWorkflow (state machine)
- AIContextBuilder (full context for AI)
- Case Library (learning from patterns)
"""

import sys
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "workflow_intelligence"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "ai_experts"))

from workflow_intelligence.integration.ai_context_builder import AIContextBuilder
from workflow_intelligence.core.case_library.repository import CaseLibraryRepository


class RiskExpert:
    """
    Risk Expert - orchestrates risk assessment workflow

    Combines:
    - Tools for DB operations
    - Organ for LLM analysis
    - Workflow for state management
    - AI Context for intelligent recommendations
    """

    def __init__(
        self,
        tools,  # RiskTools
        organ,  # RiskOrgan
        workflow,  # RiskWorkflow
        case_repository: Optional[CaseLibraryRepository] = None
    ):
        """
        Initialize Risk Expert

        Args:
            tools: RiskTools instance for DB operations
            organ: RiskOrgan instance for LLM analysis
            workflow: RiskWorkflow instance (extends StateMachine)
            case_repository: Case library for learning
        """
        self.tools = tools
        self.organ = organ
        self.workflow = workflow
        self.case_repository = case_repository

        # AI Context Builder - uses existing workflow_intelligence
        self.ai_context = AIContextBuilder(
            workflow_engine=self.workflow,
            case_repository=case_repository
        )

    # ========================================================================
    # RISK IDENTIFICATION
    # ========================================================================

    async def identify_risks(
        self,
        process_id: str,
        org_context: Dict[str, Any],
        user_input: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Identify risks for a business process

        Args:
            process_id: Process to analyze
            org_context: Organization context (industry, size, etc)
            user_input: Optional user description

        Returns:
            Identified risks with AI recommendations
        """

        # 1. Get process data via Tools
        process_data = await self.tools.get_process(process_id)

        if not process_data:
            return {
                "success": False,
                "error": f"Process {process_id} not found"
            }

        # 2. Build FULL AI context (workflow + cases + benchmarks)
        ai_context = await self.ai_context.build_full_context(
            org_context=org_context,
            user_message=user_input or f"Identify risks for {process_data.get('name')}"
        )

        # 3. LLM analysis via Organ
        analysis = await self.organ.analyze({
            "process": process_data,
            "workflow_context": ai_context,
            "action": "identify_risks",
            "user_input": user_input
        })

        # 4. Save identified risks via Tools
        risks = analysis.get('insights', [])
        saved_risks = []

        for risk in risks:
            risk_id = await self.tools.save_risk({
                "process_id": process_id,
                "description": risk.get('description'),
                "threat": risk.get('threat'),
                "vulnerability": risk.get('vulnerability'),
                "category": risk.get('category', 'operational')
            })

            if risk_id:
                saved_risks.append(risk_id)

        # 5. Execute workflow action (auto-publishes event to EventBus)
        workflow_result = await self.workflow.execute_action(
            action="risks_identified",
            data={
                "risks": [{"id": r_id} for r_id in saved_risks],
                "process_id": process_id
            }
        )

        # 6. Record to Case Library for learning
        if self.case_repository and saved_risks:
            await self.case_repository.record_case({
                "industry": org_context.get('industry'),
                "module": "risk",
                "action_type": "identify_risks",
                "context": {
                    "process_type": process_data.get('type'),
                    "process_criticality": process_data.get('criticality')
                },
                "result": {
                    "risks_count": len(saved_risks),
                    "categories": [r.get('category') for r in risks]
                },
                "success": True
            })

        return {
            "success": True,
            "risks_identified": len(saved_risks),
            "risk_ids": saved_risks,
            "recommendations": analysis.get('recommendations', []),
            "workflow_state": workflow_result.get('current_state'),
            "ai_insights": analysis.get('metadata', {})
        }

    # ========================================================================
    # LIKELIHOOD ANALYSIS
    # ========================================================================

    async def analyze_likelihood(
        self,
        risk_ids: List[str],
        org_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze likelihood for identified risks

        Args:
            risk_ids: List of risk IDs to analyze
            org_context: Organization context

        Returns:
            Likelihood scores with reasoning
        """

        # 1. Get risks data via Tools
        risks_data = await self.tools.get_risks(risk_ids)

        if not risks_data:
            return {
                "success": False,
                "error": "No risks found"
            }

        # 2. Build AI context
        ai_context = await self.ai_context.build_full_context(
            org_context=org_context,
            user_message=f"Analyze likelihood for {len(risks_data)} risks"
        )

        # 3. LLM analysis via Organ
        analysis = await self.organ.analyze({
            "risks": risks_data,
            "workflow_context": ai_context,
            "action": "analyze_likelihood",
            "industry_benchmarks": ai_context.get('benchmarks', {})
        })

        # 4. Save likelihood scores via Tools
        likelihood_scores = {}

        for risk in risks_data:
            risk_id = risk.get('id')
            score_data = analysis.get('insights', {}).get(risk_id, {})

            await self.tools.save_likelihood_score({
                "risk_id": risk_id,
                "score": score_data.get('score', 3),  # 1-5
                "frequency_estimate": score_data.get('frequency'),
                "reasoning": score_data.get('reasoning'),
                "confidence": score_data.get('confidence', 0.7)
            })

            likelihood_scores[risk_id] = score_data

        # 5. Execute workflow action
        workflow_result = await self.workflow.execute_action(
            action="likelihood_analyzed",
            data={
                "risks": [{"id": r_id} for r_id in risk_ids],
                "likelihood_scores": likelihood_scores
            }
        )

        # 6. Record to Case Library
        if self.case_repository:
            await self.case_repository.record_case({
                "industry": org_context.get('industry'),
                "module": "risk",
                "action_type": "analyze_likelihood",
                "result": {
                    "avg_score": sum(s.get('score', 0) for s in likelihood_scores.values()) / len(likelihood_scores) if likelihood_scores else 0
                },
                "success": True
            })

        return {
            "success": True,
            "likelihood_scores": likelihood_scores,
            "workflow_state": workflow_result.get('current_state'),
            "recommendations": analysis.get('recommendations', [])
        }

    # ========================================================================
    # IMPACT CALCULATION
    # ========================================================================

    async def calculate_impact(
        self,
        risk_ids: List[str],
        org_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate impact for risks (financial, operational, reputational, regulatory)

        Args:
            risk_ids: List of risk IDs
            org_context: Organization context

        Returns:
            Impact scores by type
        """

        # 1. Get risks + likelihood data
        risks_data = await self.tools.get_risks_with_likelihood(risk_ids)

        # 2. Build AI context
        ai_context = await self.ai_context.build_full_context(
            org_context=org_context,
            user_message=f"Calculate impact for {len(risks_data)} risks"
        )

        # 3. LLM analysis via Organ
        analysis = await self.organ.analyze({
            "risks": risks_data,
            "workflow_context": ai_context,
            "action": "calculate_impact",
            "org_size": org_context.get('size'),
            "org_revenue": org_context.get('revenue')
        })

        # 4. Save impact scores via Tools
        impact_scores = {}

        for risk in risks_data:
            risk_id = risk.get('id')
            impact_data = analysis.get('insights', {}).get(risk_id, {})

            await self.tools.save_impact_scores({
                "risk_id": risk_id,
                "financial": impact_data.get('financial', 0),
                "operational": impact_data.get('operational', 0),
                "reputational": impact_data.get('reputational', 0),
                "regulatory": impact_data.get('regulatory', 0),
                "reasoning": impact_data.get('reasoning')
            })

            impact_scores[risk_id] = impact_data

        # 5. Execute workflow action
        workflow_result = await self.workflow.execute_action(
            action="impact_calculated",
            data={
                "risks": [{"id": r_id} for r_id in risk_ids],
                "impact_scores": impact_scores
            }
        )

        return {
            "success": True,
            "impact_scores": impact_scores,
            "workflow_state": workflow_result.get('current_state'),
            "recommendations": analysis.get('recommendations', [])
        }

    # ========================================================================
    # FAIR ANALYSIS
    # ========================================================================

    async def fair_analysis(
        self,
        risk_ids: List[str],
        org_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Perform FAIR (Factor Analysis of Information Risk) analysis

        Formula: TEF (Threat Event Frequency) × LM (Loss Magnitude) = ALE (Annual Loss Expectancy)

        Args:
            risk_ids: List of risk IDs
            org_context: Organization context

        Returns:
            FAIR metrics (TEF, LM, ALE) for each risk
        """

        # 1. Get risks with likelihood + impact
        risks_data = await self.tools.get_risks_full_analysis(risk_ids)

        # 2. Build AI context
        ai_context = await self.ai_context.build_full_context(
            org_context=org_context,
            user_message=f"Perform FAIR analysis for {len(risks_data)} risks"
        )

        # 3. LLM analysis via Organ
        analysis = await self.organ.analyze({
            "risks": risks_data,
            "workflow_context": ai_context,
            "action": "fair_analysis",
            "methodology": "FAIR",
            "org_revenue": org_context.get('revenue', 0)
        })

        # 4. Save FAIR metrics via Tools
        fair_metrics = {}

        for risk in risks_data:
            risk_id = risk.get('id')
            fair_data = analysis.get('insights', {}).get(risk_id, {})

            tef = fair_data.get('tef', 0)  # Threat Event Frequency
            lm = fair_data.get('lm', 0)    # Loss Magnitude
            ale = tef * lm                  # Annual Loss Expectancy

            await self.tools.save_fair_metrics({
                "risk_id": risk_id,
                "tef": tef,
                "lm": lm,
                "ale": ale,
                "reasoning": fair_data.get('reasoning')
            })

            fair_metrics[risk_id] = {
                "tef": tef,
                "lm": lm,
                "ale": ale
            }

        # 5. Execute workflow action
        workflow_result = await self.workflow.execute_action(
            action="fair_completed",
            data={
                "risks": [{"id": r_id} for r_id in risk_ids],
                "fair_metrics": fair_metrics
            }
        )

        return {
            "success": True,
            "fair_metrics": fair_metrics,
            "total_ale": sum(m['ale'] for m in fair_metrics.values()),
            "workflow_state": workflow_result.get('current_state'),
            "recommendations": analysis.get('recommendations', [])
        }

    # ========================================================================
    # TREATMENT PLANNING
    # ========================================================================

    async def plan_treatments(
        self,
        risk_ids: List[str],
        org_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Plan risk treatments (reduce, accept, transfer, avoid)

        Args:
            risk_ids: List of risk IDs
            org_context: Organization context

        Returns:
            Treatment plans for each risk
        """

        # 1. Get full risk analysis
        risks_data = await self.tools.get_risks_full_analysis(risk_ids)

        # 2. Build AI context
        ai_context = await self.ai_context.build_full_context(
            org_context=org_context,
            user_message=f"Plan treatments for {len(risks_data)} risks"
        )

        # 3. LLM analysis via Organ
        analysis = await self.organ.analyze({
            "risks": risks_data,
            "workflow_context": ai_context,
            "action": "plan_treatments",
            "budget": org_context.get('risk_budget'),
            "risk_appetite": org_context.get('risk_appetite')
        })

        # 4. Save treatment plans via Tools
        treatments = {}

        for risk in risks_data:
            risk_id = risk.get('id')
            treatment_data = analysis.get('insights', {}).get(risk_id, {})

            await self.tools.save_treatment_plan({
                "risk_id": risk_id,
                "treatment_type": treatment_data.get('treatment_type', 'reduce'),
                "actions": treatment_data.get('actions', []),
                "priority": treatment_data.get('priority', 'medium'),
                "estimated_cost": treatment_data.get('cost'),
                "expected_reduction": treatment_data.get('reduction'),
                "reasoning": treatment_data.get('reasoning')
            })

            treatments[risk_id] = treatment_data

        # 5. Execute workflow action
        workflow_result = await self.workflow.execute_action(
            action="treatments_planned",
            data={
                "risks": [{"id": r_id} for r_id in risk_ids],
                "treatments": treatments
            }
        )

        # 6. Record to Case Library
        if self.case_repository:
            await self.case_repository.record_case({
                "industry": org_context.get('industry'),
                "module": "risk",
                "action_type": "plan_treatments",
                "result": {
                    "treatments_count": len(treatments),
                    "treatment_types": [t.get('treatment_type') for t in treatments.values()]
                },
                "success": True
            })

        return {
            "success": True,
            "treatments": treatments,
            "workflow_state": workflow_result.get('current_state'),
            "recommendations": analysis.get('recommendations', [])
        }

    # ========================================================================
    # HELPER METHODS
    # ========================================================================

    async def get_workflow_status(self) -> Dict[str, Any]:
        """Get current workflow status"""
        return {
            "current_stage": self.workflow.current_state.name,
            "available_actions": self.workflow.get_available_actions(),
            "gaps": self.workflow.identify_gaps(),
            "metadata": self.workflow.current_state.metadata
        }

    async def get_risk_summary(self, risk_id: str) -> Dict[str, Any]:
        """Get complete risk summary"""
        return await self.tools.get_risk_summary(risk_id)
