"""
FastAPI Routes for AI Experts

Endpoints:
- POST /experts/bcm-advisor/advise - Get BCM advice
- POST /experts/compliance-auditor/check - Check compliance
- POST /experts/strategic-planner/plan - Get strategic plan
- GET /experts/cases/search - Search case library
- POST /ml/predict - Predict workflow journey
- GET /learning/pending-rules - Get pending rules
- POST /learning/approve-rule - Approve rule
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai-experts", tags=["ai-experts"])


# Request/Response Models
class ExpertAdviceRequest(BaseModel):
    query: str
    context: Dict[str, Any]
    max_tokens: Optional[int] = 2000


class ExpertAdviceResponse(BaseModel):
    advice: str
    expert: str
    context_used: Dict[str, Any]


class CaseSearchRequest(BaseModel):
    query: str
    industry: Optional[str] = None
    org_size: Optional[str] = None
    module: Optional[str] = None
    max_results: Optional[int] = 5


class WorkflowPredictionRequest(BaseModel):
    org_context: Dict[str, Any]
    current_state: str
    current_progress: Dict[str, Any]


class RuleApprovalRequest(BaseModel):
    rule_id: str
    approved: bool
    reason: Optional[str] = None


# Expert Endpoints
@router.post("/bcm-advisor/advise", response_model=ExpertAdviceResponse)
async def get_bcm_advice(request: ExpertAdviceRequest):
    """
    Get advice from BCM Advisor expert

    The BCM Advisor specializes in:
    - Business Impact Analysis (BIA)
    - Dependency mapping
    - Recovery strategies
    """
    try:
        from ..specialists.bcm_advisor import BCMAdvisor

        # Initialize advisor (in production, use dependency injection)
        advisor = BCMAdvisor()

        advice = await advisor.advise(
            query=request.query,
            context=request.context,
            max_tokens=request.max_tokens
        )

        return ExpertAdviceResponse(
            advice=advice,
            expert="BCM Advisor",
            context_used=request.context
        )

    except Exception as e:
        logger.error(f"BCM Advisor error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/compliance-auditor/check")
async def check_compliance(request: ExpertAdviceRequest):
    """
    Get compliance check from Compliance Auditor expert

    The Compliance Auditor specializes in:
    - ISO 22301 compliance checking
    - Gap analysis
    - Evidence validation
    """
    try:
        from ..specialists.compliance_auditor import ComplianceAuditor

        auditor = ComplianceAuditor()

        advice = await auditor.advise(
            query=request.query,
            context=request.context,
            max_tokens=request.max_tokens
        )

        return ExpertAdviceResponse(
            advice=advice,
            expert="Compliance Auditor",
            context_used=request.context
        )

    except Exception as e:
        logger.error(f"Compliance Auditor error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/strategic-planner/plan")
async def get_strategic_plan(request: ExpertAdviceRequest):
    """
    Get strategic planning from Strategic Planner expert

    The Strategic Planner specializes in:
    - Timeline prediction
    - Resource planning
    - Maturity assessment
    """
    try:
        from ..specialists.strategic_planner import StrategicPlanner

        planner = StrategicPlanner()

        advice = await planner.advise(
            query=request.query,
            context=request.context,
            max_tokens=request.max_tokens
        )

        return ExpertAdviceResponse(
            advice=advice,
            expert="Strategic Planner",
            context_used=request.context
        )

    except Exception as e:
        logger.error(f"Strategic Planner error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Case Library Endpoints
@router.post("/cases/search")
async def search_cases(request: CaseSearchRequest):
    """
    Search case library for relevant examples
    """
    try:
        from ..tools.case_library_tool import CaseSearchTool

        tool = CaseSearchTool()

        results = await tool.execute(
            query=request.query,
            industry=request.industry,
            org_size=request.org_size,
            module=request.module,
            max_results=request.max_results
        )

        return results

    except Exception as e:
        logger.error(f"Case search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ML Endpoints
@router.post("/ml/predict")
async def predict_workflow(request: WorkflowPredictionRequest):
    """
    Predict workflow journey using ML models
    """
    try:
        from ..ml.predictive_models import WorkflowPredictor

        predictor = WorkflowPredictor()

        prediction = await predictor.predict_journey(
            org_context=request.org_context,
            current_state=request.current_state,
            current_progress=request.current_progress
        )

        return prediction

    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Learning Endpoints
@router.get("/learning/pending-rules")
async def get_pending_rules():
    """
    Get pending rules awaiting approval
    """
    try:
        from ..learning.self_learning_engine import SelfLearningEngine

        engine = SelfLearningEngine()

        pending_rules = engine.get_pending_rules()

        return {
            'count': len(pending_rules),
            'rules': pending_rules
        }

    except Exception as e:
        logger.error(f"Get pending rules error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/learning/approve-rule")
async def approve_rule(request: RuleApprovalRequest):
    """
    Approve or reject a pending rule
    """
    try:
        from ..learning.self_learning_engine import SelfLearningEngine

        engine = SelfLearningEngine()

        if request.approved:
            result = await engine.approve_rule(request.rule_id)
        else:
            result = await engine.reject_rule(
                request.rule_id,
                request.reason or "No reason provided"
            )

        return result

    except Exception as e:
        logger.error(f"Rule approval error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Health Check
@router.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {
        'status': 'healthy',
        'service': 'AI Experts',
        'version': '1.0.0'
    }
