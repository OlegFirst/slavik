"""
Workflow Intelligence AI Endpoints for Planning Service
Provides context-aware AI advice and case-based learning
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from uuid import UUID

from ..auth.dependencies import get_current_user
from ..database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/api/v1/planning", tags=["workflow-ai"])


class AIAdviceRequest(BaseModel):
    """Request for AI advice"""
    user_message: Optional[str] = "What should I do next?"


class AIAdviceResponse(BaseModel):
    """AI advice response"""
    workflow_id: str
    current_stage: str
    ai_message: str
    similar_cases: list
    benchmarks: Optional[Dict[str, Any]]
    suggested_actions: list


@router.get("/strategies/{strategy_id}/ai-advice", response_model=AIAdviceResponse)
async def get_ai_advice(
    strategy_id: UUID,
    user_message: str = "What should I do next?",
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get context-aware AI advice for strategy

    Based on:
    - Current workflow state
    - Similar successful cases
    - Industry benchmarks
    """
    from ..main import workflow_engine, ai_advisor, workflow_storage

    if not workflow_engine or not workflow_storage:
        raise HTTPException(
            status_code=503,
            detail="Workflow Intelligence not initialized"
        )

    try:
        # Get workflow context
        context = await workflow_engine.get_context(
            workflow_id=str(strategy_id),
            tenant_id=current_user.tenant_id
        )

        # Find similar cases
        similar_cases = await workflow_storage.find_similar_cases(
            module="planning",
            org_context={
                "industry": current_user.organization.industry if hasattr(current_user, 'organization') else "general",
                "size": "medium"  # TODO: Get from user context
            },
            current_stage=context.get("current_stage", "unknown"),
            limit=5
        )

        # Get benchmarks
        benchmarks = await workflow_storage.get_benchmarks(
            module="planning",
            industry=current_user.organization.industry if hasattr(current_user, 'organization') else None
        )

        # Generate AI advice (if AI Advisor is enabled)
        ai_message = "Workflow Intelligence is tracking your progress. "

        if similar_cases:
            ai_message += f"Based on {len(similar_cases)} similar cases, "
            avg_duration = sum(c.get('total_duration_days', 0) for c in similar_cases) / len(similar_cases)
            ai_message += f"this typically takes {int(avg_duration)} days. "

        if benchmarks and benchmarks.get('success_rate'):
            ai_message += f"Success rate for this workflow: {int(benchmarks['success_rate'] * 100)}%. "

        # Suggested actions based on context
        suggested_actions = []
        if context.get("gaps"):
            suggested_actions = [f"Address gap: {gap}" for gap in context.get("gaps", [])]
        elif context.get("available_actions"):
            suggested_actions = context.get("available_actions", [])

        return AIAdviceResponse(
            workflow_id=str(strategy_id),
            current_stage=context.get("current_stage", "unknown"),
            ai_message=ai_message,
            similar_cases=similar_cases,
            benchmarks=benchmarks,
            suggested_actions=suggested_actions
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI advice failed: {str(e)}")


@router.post("/strategies/{strategy_id}/complete-case")
async def complete_and_create_case(
    strategy_id: UUID,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Mark strategy as complete and create learning case

    This case will be available to all services for learning
    """
    from ..main import case_collector, workflow_storage

    if not case_collector or not workflow_storage:
        raise HTTPException(
            status_code=503,
            detail="Workflow Intelligence not initialized"
        )

    try:
        # TODO: Mark strategy as completed in your service logic
        # strategy = await service.complete(strategy_id)

        # Create case for learning
        case = await case_collector.create_case(
            workflow_id=str(strategy_id),
            module="planning",
            tenant_id=current_user.tenant_id
        )

        # Save to shared database (accessible by all services)
        await workflow_storage.save_case(
            case_id=case.case_id,
            module="planning",
            case_data=case.dict(),
            tenant_id=current_user.tenant_id
        )

        return {
            "strategy_id": str(strategy_id),
            "case_collected": True,
            "case_id": case.case_id,
            "message": "Strategy completed and case saved for platform learning"
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Case creation failed: {str(e)}"
        )


@router.get("/benchmarks")
async def get_planning_benchmarks(
    industry: Optional[str] = None,
    org_size: Optional[str] = None,
    current_user = Depends(get_current_user)
):
    """
    Get benchmarks for planning workflows

    Based on real data from all completed workflows across the platform
    """
    from ..main import workflow_storage

    if not workflow_storage:
        raise HTTPException(
            status_code=503,
            detail="Workflow Intelligence not initialized"
        )

    try:
        benchmarks = await workflow_storage.get_benchmarks(
            module="planning",
            industry=industry,
            org_size=org_size
        )

        return {
            "module": "planning",
            "industry": industry or "all",
            "org_size": org_size or "all",
            "benchmarks": benchmarks
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Benchmarks retrieval failed: {str(e)}"
        )
