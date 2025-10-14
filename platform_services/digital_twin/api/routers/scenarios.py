"""
Scenario Templates Endpoints

REST API endpoints for universal scenario library
"""

import json
import logging
from typing import List, Optional
from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Depends, Query, Request
from pydantic import BaseModel, Field

from storage import PostgreSQLStorage
from api.auth.dependencies import get_current_active_user, require_admin

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================
# REQUEST/RESPONSE MODELS
# ============================================

class ScenarioTemplateCreate(BaseModel):
    """Scenario template creation request"""
    name: str = Field(..., description="Scenario name")
    description: Optional[str] = None
    category: str = Field(..., description="BCM, Risk, Compliance")
    scenario_type: str = Field(..., description="cyber_attack, pandemic, etc.")
    detailed_scenario: Optional[str] = None
    parameters_template: Optional[dict] = None
    severity_levels: Optional[dict] = None
    tags: Optional[List[str]] = None
    is_public: bool = False


class ScenarioTemplateUpdate(BaseModel):
    """Scenario template update request"""
    name: Optional[str] = None
    description: Optional[str] = None
    detailed_scenario: Optional[str] = None
    parameters_template: Optional[dict] = None
    severity_levels: Optional[dict] = None
    tags: Optional[List[str]] = None
    is_public: Optional[bool] = None
    is_active: Optional[bool] = None


class ScenarioTemplateResponse(BaseModel):
    """Scenario template response"""
    id: str
    tenant_id: str
    name: str
    description: Optional[str]
    category: str
    scenario_type: str
    detailed_scenario: Optional[str]
    parameters_template: Optional[dict]
    severity_levels: Optional[dict]
    ai_generated: bool
    tags: Optional[List[str]]
    source: Optional[str]
    is_public: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ScenarioTemplateList(BaseModel):
    """Scenario template list response"""
    total: int
    items: List[ScenarioTemplateResponse]
    limit: int


class AIGenerationRequest(BaseModel):
    """AI scenario generation request"""
    context: dict = Field(..., description="Context for scenario generation")
    scenario_type: Optional[str] = None


# ============================================
# DEPENDENCIES
# ============================================

def get_storage(request: Request) -> PostgreSQLStorage:
    """Get storage dependency"""
    return request.app.state.app_state.storage


# ============================================
# ENDPOINTS
# ============================================

@router.post("/", response_model=ScenarioTemplateResponse, status_code=201)
async def create_scenario_template(
    scenario: ScenarioTemplateCreate,
    storage: PostgreSQLStorage = Depends(get_storage),
    current_user = Depends(get_current_active_user)
):
    """
    Create new scenario template

    Can be used WITHOUT organization - standalone scenario library
    """
    try:
        scenario_id = f"scenario-{uuid4().hex[:12]}"

        scenario_data = scenario.model_dump()
        scenario_data['id'] = scenario_id
        scenario_data['tenant_id'] = current_user.tenant_id
        scenario_data['source'] = 'user-created'

        scenario_model = await storage.create_scenario_template(scenario_data)

        logger.info(f"Created scenario template: {scenario_model.id} by {current_user.email}")

        return ScenarioTemplateResponse.model_validate(scenario_model)

    except Exception as e:
        logger.error(f"Failed to create scenario template: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=ScenarioTemplateList)
async def list_scenario_templates(
    category: Optional[str] = Query(None, description="Filter by category"),
    scenario_type: Optional[str] = Query(None, description="Filter by type"),
    is_public: Optional[bool] = Query(None, description="Include public scenarios"),
    limit: int = Query(100, ge=1, le=1000),
    storage: PostgreSQLStorage = Depends(get_storage),
    current_user = Depends(get_current_active_user)
):
    """
    List scenario templates

    Returns tenant's own scenarios + public scenarios if requested
    """
    try:
        scenarios = await storage.list_scenario_templates(
            tenant_id=current_user.tenant_id,
            category=category,
            scenario_type=scenario_type,
            is_public=is_public,
            limit=limit
        )

        items = [ScenarioTemplateResponse.model_validate(s) for s in scenarios]

        return ScenarioTemplateList(
            total=len(items),
            items=items,
            limit=limit
        )

    except Exception as e:
        logger.error(f"Failed to list scenario templates: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{scenario_id}", response_model=ScenarioTemplateResponse)
async def get_scenario_template(
    scenario_id: str,
    storage: PostgreSQLStorage = Depends(get_storage),
    current_user = Depends(get_current_active_user)
):
    """
    Get scenario template by ID

    Verifies ownership unless scenario is public
    """
    try:
        scenario = await storage.get_scenario_template(scenario_id)

        if not scenario:
            raise HTTPException(status_code=404, detail="Scenario not found")

        # Check ownership (allow public scenarios)
        if scenario.tenant_id != current_user.tenant_id and not scenario.is_public:
            raise HTTPException(status_code=403, detail="Not authorized to access this scenario")

        return ScenarioTemplateResponse.model_validate(scenario)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get scenario template: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{scenario_id}", response_model=ScenarioTemplateResponse)
async def update_scenario_template(
    scenario_id: str,
    updates: ScenarioTemplateUpdate,
    storage: PostgreSQLStorage = Depends(get_storage),
    current_user = Depends(get_current_active_user)
):
    """
    Update scenario template

    Only owner can update
    """
    try:
        # Verify ownership
        scenario = await storage.get_scenario_template(scenario_id)

        if not scenario:
            raise HTTPException(status_code=404, detail="Scenario not found")

        if scenario.tenant_id != current_user.tenant_id:
            raise HTTPException(status_code=403, detail="Not authorized to update this scenario")

        # Update
        update_data = updates.model_dump(exclude_unset=True)

        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")

        scenario_model = await storage.update_scenario_template(scenario_id, update_data)

        logger.info(f"Updated scenario template: {scenario_id}")

        return ScenarioTemplateResponse.model_validate(scenario_model)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update scenario template: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{scenario_id}")
async def delete_scenario_template(
    scenario_id: str,
    storage: PostgreSQLStorage = Depends(get_storage),
    current_user = Depends(require_admin)
):
    """
    Delete scenario template

    Admin only - deletes scenario and all related exercises/predictions
    """
    try:
        # Verify ownership
        scenario = await storage.get_scenario_template(scenario_id)

        if not scenario:
            raise HTTPException(status_code=404, detail="Scenario not found")

        if scenario.tenant_id != current_user.tenant_id:
            raise HTTPException(status_code=403, detail="Not authorized to delete this scenario")

        await storage.delete_scenario_template(scenario_id)

        logger.info(f"Deleted scenario template: {scenario_id}")

        return {"status": "deleted", "scenario_id": scenario_id}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete scenario template: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ai-generate", response_model=ScenarioTemplateResponse, status_code=201)
async def generate_scenario_with_ai(
    request: AIGenerationRequest,
    storage: PostgreSQLStorage = Depends(get_storage),
    current_user = Depends(get_current_active_user)
):
    """
    Generate scenario using AI (Scenario Orchestrator)

    Can be used WITHOUT organization - just provide context

    Example:
        {
            "context": {
                "industry": "healthcare",
                "size": "medium",
                "focus": "cyber security"
            },
            "scenario_type": "cyber_attack"
        }
    """
    try:
        # Import AI client
        from bridges.scenario_ai.client import ScenarioAIClient

        ai_client = ScenarioAIClient(base_url="http://scenario-ai:8002")
        generated = await ai_client.generate_scenario(
            request.context,
            request.scenario_type
        )

        # Create scenario from AI output
        scenario_id = f"scenario-ai-{uuid4().hex[:12]}"

        scenario_data = {
            'id': scenario_id,
            'tenant_id': current_user.tenant_id,
            'name': generated['title'],
            'description': generated.get('summary'),
            'category': 'BCM',
            'scenario_type': generated['scenario_type'],
            'detailed_scenario': generated['detailed_description'],
            'parameters_template': generated.get('parameters', {}),
            'severity_levels': generated.get('severity_levels'),
            'ai_generated': True,
            'ai_prompt': str(request.context),
            'source': 'ai-generated',
            'tags': generated.get('tags', [])
        }

        scenario_model = await storage.create_scenario_template(scenario_data)

        logger.info(f"AI-generated scenario created: {scenario_model.id}")

        return ScenarioTemplateResponse.model_validate(scenario_model)

    except Exception as e:
        logger.error(f"Failed to generate AI scenario: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"AI generation failed: {str(e)}")


@router.get("/types/available")
async def get_available_scenario_types():
    """
    Get list of available scenario types

    Returns all supported scenario types from SimulationEngine
    """
    from core.models.base import SimulationScenarioType

    types = [
        {
            "value": "funding_shock",
            "label": "Funding Shock",
            "description": "Loss of major funding source"
        },
        {
            "value": "staff_disruption",
            "label": "Staff Disruption",
            "description": "Loss of key personnel"
        },
        {
            "value": "supply_chain_break",
            "label": "Supply Chain Break",
            "description": "Critical supply chain failure"
        },
        {
            "value": "cyber_attack",
            "label": "Cyber Attack",
            "description": "Ransomware, DDoS, data breach"
        },
        {
            "value": "regulatory_change",
            "label": "Regulatory Change",
            "description": "New regulations affecting operations"
        },
        {
            "value": "reputation_crisis",
            "label": "Reputation Crisis",
            "description": "Public relations disaster"
        },
        {
            "value": "economic_downturn",
            "label": "Economic Downturn",
            "description": "Market recession or crash"
        },
        {
            "value": "natural_disaster",
            "label": "Natural Disaster",
            "description": "Earthquake, flood, hurricane, fire"
        },
        {
            "value": "pandemic",
            "label": "Pandemic",
            "description": "Disease outbreak"
        },
        {
            "value": "market_shift",
            "label": "Market Shift",
            "description": "Disruptive technology or competitor"
        },
        {
            "value": "custom",
            "label": "Custom Scenario",
            "description": "User-defined scenario"
        }
    ]

    return {
        "total": len(types),
        "types": types
    }


@router.get("/categories/available")
async def get_available_categories():
    """
    Get list of available scenario categories
    """
    categories = [
        {
            "value": "BCM",
            "label": "Business Continuity Management",
            "description": "Business continuity and disaster recovery"
        },
        {
            "value": "Risk",
            "label": "Risk Management",
            "description": "Risk assessment and mitigation"
        },
        {
            "value": "Compliance",
            "label": "Compliance & Audit",
            "description": "Regulatory compliance scenarios"
        },
        {
            "value": "Security",
            "label": "Security",
            "description": "Cyber and physical security"
        },
        {
            "value": "Operational",
            "label": "Operational",
            "description": "Day-to-day operations"
        }
    ]

    return {
        "total": len(categories),
        "categories": categories
    }


# ============================================
# ADVANCED AI ENDPOINTS (NEW)
# ============================================

class AdvancedAIRequest(BaseModel):
    """Advanced AI scenario generation request"""
    category: str = Field(..., description="Scenario category (cyber_attack, pandemic, etc.)")
    complexity: int = Field(3, ge=1, le=5, description="Complexity level 1-5")
    duration_hours: int = Field(4, ge=1, le=168, description="Duration in hours")
    participants: int = Field(10, ge=1, description="Number of participants")
    affected_systems: List[str] = Field(default_factory=list)
    custom_objectives: List[str] = Field(default_factory=list)
    organization_id: Optional[str] = None


class LearningFeedback(BaseModel):
    """Exercise outcome feedback for learning"""
    scenario_id: str
    effectiveness_score: float = Field(..., ge=0, le=10)
    lessons_learned: List[str]
    feedback: List[str]
    improvements: List[str] = Field(default_factory=list)


@router.post("/ai-generate-advanced", response_model=ScenarioTemplateResponse, status_code=201)
async def generate_scenario_advanced_ai(
    request: AdvancedAIRequest,
    storage: PostgreSQLStorage = Depends(get_storage),
    current_user = Depends(get_current_active_user)
):
    """
    Generate scenario using Advanced AI with historical context and learning

    This endpoint uses sophisticated AI with:
    - Historical context from past exercises
    - Similar real-world incident analysis
    - Sophisticated prompt engineering
    - Multi-LLM support (Gemma, OpenAI)

    Example:
        POST /api/v1/scenarios/ai-generate-advanced
        {
            "category": "cyber_attack",
            "complexity": 4,
            "duration_hours": 6,
            "participants": 15,
            "affected_systems": ["email", "crm", "database"],
            "custom_objectives": [
                "Test incident response procedures",
                "Evaluate communication protocols"
            ],
            "organization_id": "org-123"  // Optional
        }

    Returns:
        Fully generated scenario with timeline, injects, success metrics
    """
    try:
        from core.ai.advanced_scenario_generator import (
            AdvancedScenarioGenerator,
            ScenarioParameters
        )

        logger.info(f"Generating advanced AI scenario: {request.category} (complexity {request.complexity})")

        # Create AI generator
        ai_generator = AdvancedScenarioGenerator()

        # Prepare organization context if linked
        org_context = None
        if request.organization_id:
            org = await storage.get_organization(request.organization_id)
            if org:
                org_context = {
                    'industry': org.industry,
                    'size': org.employee_count,
                    'annual_revenue': org.annual_revenue
                }
                logger.info(f"Using organization context: {org.name} ({org.industry})")

        # Prepare parameters
        params = ScenarioParameters(
            category=request.category,
            complexity=request.complexity,
            duration_hours=request.duration_hours,
            participants=request.participants,
            affected_systems=request.affected_systems,
            custom_objectives=request.custom_objectives,
            organization_context=org_context
        )

        # Generate scenario with Advanced AI
        generated = await ai_generator.generate_scenario(params)

        # Create scenario template in database
        scenario_id = f"scenario-{uuid4().hex[:12]}"

        scenario_data = {
            'id': scenario_id,
            'tenant_id': current_user.tenant_id,
            'name': generated.title,
            'description': generated.description,
            'category': 'BCM',  # Primary category
            'scenario_type': request.category,
            'detailed_scenario': json.dumps({
                'timeline': generated.timeline,
                'injects': generated.injects,
                'success_metrics': generated.success_metrics
            }),
            'parameters_template': {
                'complexity': request.complexity,
                'duration_hours': request.duration_hours,
                'participants': request.participants
            },
            'ai_generated': True,
            'ai_prompt': json.dumps(generated.ai_metadata),
            'tags': [request.category, f'complexity-{request.complexity}', 'ai-generated'],
            'source': 'advanced-ai',
            'is_public': False,
            'is_active': True
        }

        scenario_model = await storage.create_scenario_template(scenario_data)

        logger.info(f"Advanced AI scenario created: {scenario_id} - {generated.title}")

        return ScenarioTemplateResponse.model_validate(scenario_model)

    except Exception as e:
        logger.error(f"Advanced AI generation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"AI generation failed: {str(e)}")


@router.post("/learn-from-exercise")
async def submit_learning_feedback(
    feedback: LearningFeedback,
    storage: PostgreSQLStorage = Depends(get_storage),
    current_user = Depends(get_current_active_user)
):
    """
    Submit exercise outcome feedback for AI learning

    This creates a learning loop - AI improves future scenarios based on:
    - Exercise effectiveness scores
    - Lessons learned
    - Participant feedback
    - Areas for improvement

    The feedback is sent to AI orchestrator for pattern analysis and
    used to improve future scenario generation.

    Example:
        POST /api/v1/scenarios/learn-from-exercise
        {
            "scenario_id": "scenario-abc123",
            "effectiveness_score": 8.5,
            "lessons_learned": [
                "Communication protocols worked well",
                "Need faster escalation procedures"
            ],
            "feedback": [
                "Scenario was realistic",
                "Timeline was appropriate"
            ],
            "improvements": [
                "Add more stakeholder injects",
                "Include media pressure scenarios"
            ]
        }
    """
    try:
        from core.ai.advanced_scenario_generator import AdvancedScenarioGenerator

        # Verify scenario exists and ownership
        scenario = await storage.get_scenario_template(feedback.scenario_id)

        if not scenario:
            raise HTTPException(status_code=404, detail="Scenario not found")

        if scenario.tenant_id != current_user.tenant_id:
            raise HTTPException(status_code=403, detail="Not authorized")

        # Create AI generator and submit learning
        ai_generator = AdvancedScenarioGenerator()

        outcomes = {
            'effectiveness_score': feedback.effectiveness_score,
            'lessons_learned': feedback.lessons_learned,
            'feedback': feedback.feedback,
            'improvements': feedback.improvements
        }

        success = await ai_generator.learn_from_exercise(
            feedback.scenario_id,
            outcomes
        )

        if success:
            logger.info(f"Learning feedback submitted for scenario: {feedback.scenario_id}")
            return {
                "status": "success",
                "message": "Learning feedback submitted successfully",
                "scenario_id": feedback.scenario_id
            }
        else:
            logger.warning(f"Learning feedback submission failed for: {feedback.scenario_id}")
            return {
                "status": "partial",
                "message": "Feedback stored locally but AI orchestrator unavailable",
                "scenario_id": feedback.scenario_id
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to submit learning feedback: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
