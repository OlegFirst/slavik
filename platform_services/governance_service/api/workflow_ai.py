"""
Workflow Intelligence AI Endpoints
Provides context-aware AI advice and case-based learning
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from uuid import UUID

from shared.auth.jwt_handler import get_current_user
from shared.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/api/v1/governance", tags=["workflow-ai"])


class AIAdviceResponse(BaseModel):
    """AI advice response"""
    workflow_id: str
    current_stage: str
    ai_message: str
    similar_cases: list
    benchmarks: Optional[Dict[str, Any]]
    suggested_actions: list


@router.get("/{item_id}/ai-advice", response_model=AIAdviceResponse)
async def get_ai_advice(
    item_id: UUID,
    user_message: str = "What should I do next?",
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get context-aware AI advice"""
    import main

    if not main.workflow_engine or not main.workflow_storage:
        raise HTTPException(503, "Workflow Intelligence not initialized")

    try:
        context = await main.workflow_engine.get_context(
            workflow_id=str(item_id),
            tenant_id=current_user.tenant_id
        )

        similar_cases = await main.workflow_storage.find_similar_cases(
            module="governance",
            org_context={"industry": "general", "size": "medium"},
            current_stage=context.get("current_stage", "unknown"),
            limit=5
        )

        benchmarks = await main.workflow_storage.get_benchmarks(
            module="governance"
        )

        ai_message = f"Workflow Intelligence is tracking your progress for governance."

        return AIAdviceResponse(
            workflow_id=str(item_id),
            current_stage=context.get("current_stage", "unknown"),
            ai_message=ai_message,
            similar_cases=similar_cases,
            benchmarks=benchmarks,
            suggested_actions=context.get("available_actions", [])
        )

    except Exception as e:
        raise HTTPException(500, f"AI advice failed: {str(e)}")


@router.get("/benchmarks")
async def get_benchmarks(
    industry: Optional[str] = None,
    current_user = Depends(get_current_user)
):
    """Get benchmarks for workflows"""
    import main

    if not main.workflow_storage:
        raise HTTPException(503, "Workflow Intelligence not initialized")

    try:
        benchmarks = await main.workflow_storage.get_benchmarks(
            module="governance",
            industry=industry
        )

        return {
            "module": "governance",
            "industry": industry or "all",
            "benchmarks": benchmarks
        }

    except Exception as e:
        raise HTTPException(500, f"Benchmarks retrieval failed: {str(e)}")
