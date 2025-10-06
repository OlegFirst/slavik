"""
Risk Office - Complete BCM Risk Management Module

Components:
- RiskService: Main service (orchestrates everything)
- RiskWorkflow: State machine (extends workflow_intelligence)
- RiskExpert: Business logic
- RiskSpecialist: Conversational interface
- RiskOrgan: LLM analysis
- RiskTools: Database operations

Usage:
    >>> from bcm_offices.risk import RiskService
    >>>
    >>> service = RiskService(
    ...     db_session=supabase_client,
    ...     llm_router=llm_router,
    ...     event_bus=event_bus,
    ...     org_context={'industry': 'fintech', 'size': 'medium'}
    ... )
    >>>
    >>> # Chat interface
    >>> response = await service.chat(
    ...     "Identify risks for our payment processing",
    ...     context={'process_id': 'proc_123'}
    ... )
    >>>
    >>> # Direct API
    >>> risks = await service.identify_risks('proc_123')
    >>> likelihood = await service.analyze_likelihood(risk_ids)
    >>> impact = await service.calculate_impact(risk_ids)
    >>> fair = await service.fair_analysis(risk_ids)
    >>> treatments = await service.plan_treatments(risk_ids)
"""

from .services.risk_service import RiskService
from .workflow.risk_workflow import RiskWorkflow, RiskStage
from .ai.expert import RiskExpert
from .ai.specialist import RiskSpecialist
from .ai.organ import RiskOrgan
from .tools.risk_tools import RiskTools

__all__ = [
    'RiskService',
    'RiskWorkflow',
    'RiskStage',
    'RiskExpert',
    'RiskSpecialist',
    'RiskOrgan',
    'RiskTools'
]
