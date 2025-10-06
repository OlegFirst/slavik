#!/bin/bash
# Script to integrate Workflow Intelligence into BCM services

echo "🔄 Integrating Workflow Intelligence into BCM Services..."
echo ""

# Services to integrate
SERVICES=("plans_service" "bia-service" "compliance-service")

for SERVICE in "${SERVICES[@]}"; do
    echo "📦 Integrating into $SERVICE..."

    # Check if service exists
    if [ ! -d "/Users/MD/AI-Platform-ISO/platform-services/$SERVICE" ]; then
        echo "⚠️  Service $SERVICE not found, skipping..."
        continue
    fi

    # Create workflow_ai.py file for service
    MODULE_NAME=$(echo $SERVICE | sed 's/-/_/g' | sed 's/_service//')

    cat > "/Users/MD/AI-Platform-ISO/platform-services/$SERVICE/api/workflow_ai.py" << 'WORKFLOW_AI_EOF'
"""
Workflow Intelligence AI Endpoints
Provides context-aware AI advice and case-based learning
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from uuid import UUID

from ..auth.dependencies import get_current_user
from ..database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix=f"/api/v1/MODULE_PLACEHOLDER", tags=["workflow-ai"])


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
    from ..main import workflow_engine, workflow_storage

    if not workflow_engine or not workflow_storage:
        raise HTTPException(503, "Workflow Intelligence not initialized")

    try:
        context = await workflow_engine.get_context(
            workflow_id=str(item_id),
            tenant_id=current_user.tenant_id
        )

        similar_cases = await workflow_storage.find_similar_cases(
            module="MODULE_PLACEHOLDER",
            org_context={"industry": "general", "size": "medium"},
            current_stage=context.get("current_stage", "unknown"),
            limit=5
        )

        benchmarks = await workflow_storage.get_benchmarks(
            module="MODULE_PLACEHOLDER"
        )

        ai_message = f"Workflow Intelligence is tracking your progress for MODULE_PLACEHOLDER."

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
    from ..main import workflow_storage

    if not workflow_storage:
        raise HTTPException(503, "Workflow Intelligence not initialized")

    try:
        benchmarks = await workflow_storage.get_benchmarks(
            module="MODULE_PLACEHOLDER",
            industry=industry
        )

        return {
            "module": "MODULE_PLACEHOLDER",
            "industry": industry or "all",
            "benchmarks": benchmarks
        }

    except Exception as e:
        raise HTTPException(500, f"Benchmarks retrieval failed: {str(e)}")
WORKFLOW_AI_EOF

    # Replace MODULE_PLACEHOLDER with actual module name
    sed -i '' "s/MODULE_PLACEHOLDER/$MODULE_NAME/g" "/Users/MD/AI-Platform-ISO/platform-services/$SERVICE/api/workflow_ai.py"

    echo "✅ Created workflow_ai.py for $SERVICE (module: $MODULE_NAME)"
done

echo ""
echo "✅ Workflow Intelligence integration templates created!"
echo ""
echo "📝 Next steps:"
echo "1. Add to main.py for each service:"
echo "   - Import: from workflow_intelligence import PostgresStorageAdapter, WorkflowEngine, CaseCollector"
echo "   - Initialize in lifespan startup"
echo "   - Include router: app.include_router(workflow_ai_router)"
echo ""
echo "2. See Planning Service for complete example"
echo "3. Update requirements.txt to include workflow-intelligence"
