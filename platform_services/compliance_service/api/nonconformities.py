"""
Nonconformities API
Provides endpoints for nonconformity management and RCA (Root Cause Analysis)
ISO 22301 Clause 10.1 - Nonconformity and Corrective Action
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any
from uuid import UUID
import logging

from compliance.database.connection import get_db
from compliance.models.enums import RCAMethod
from compliance.workflows.nonconformity_workflow import NonconformityWorkflow
from compliance.repositories.nonconformity_repository import NonconformityRepository
from compliance.services.rca_templates import RCATemplateFactory

logger = logging.getLogger(__name__)
router = APIRouter()


# Dependency injection factories
def get_nc_repository(db: AsyncSession = Depends(get_db)) -> NonconformityRepository:
    """Get Nonconformity repository with database session"""
    return NonconformityRepository(db)


async def get_nc_workflow(
    db: AsyncSession = Depends(get_db)
) -> NonconformityWorkflow:
    """Dependency to get nonconformity workflow instance"""
    repository = NonconformityRepository(db)
    return NonconformityWorkflow(repository=repository)


# =============================================================================
# RCA ENDPOINTS - ISO 22301 Clause 10.1
# =============================================================================

@router.post("/nonconformities/{nc_id}/rca/start")
async def start_rca_process(
    nc_id: UUID,
    rca_method: RCAMethod,
    rca_lead: str,
    rca_team: List[str] = [],
    tenant_id: str = Query(..., description="Tenant identifier"),
    workflow: NonconformityWorkflow = Depends(get_nc_workflow)
):
    """
    Start RCA (Root Cause Analysis) process with template.

    Creates appropriate RCA template based on selected method:
    - 5_whys: Ask "Why?" 5 times to drill down to root cause
    - fishbone: Categorize causes by 6M framework (People, Process, Technology, etc.)
    - fault_tree: Top-down deductive analysis with probability

    Args:
        nc_id: Nonconformity ID
        rca_method: RCA method (5_whys, fishbone, fault_tree)
        rca_lead: Person leading the RCA
        rca_team: Team members participating in RCA
        tenant_id: Tenant identifier

    Returns:
        RCA template and instructions
    """
    try:
        result = await workflow.start_rca(
            nc_id=nc_id,
            rca_method=rca_method,
            rca_lead=rca_lead,
            rca_team=rca_team,
            tenant_id=tenant_id
        )

        logger.info(f"RCA started for NC {nc_id} using {rca_method.value} method by {rca_lead}")

        return {
            "status": "success",
            "message": f"RCA process started using {rca_method.value} method",
            "data": result
        }

    except ValueError as e:
        logger.error(f"Validation error starting RCA for NC {nc_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to start RCA for NC {nc_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start RCA: {str(e)}"
        )


@router.post("/nonconformities/{nc_id}/rca/complete")
async def complete_rca_process(
    nc_id: UUID,
    completed_template: Dict[str, Any],
    actor_id: str,
    tenant_id: str = Query(..., description="Tenant identifier"),
    workflow: NonconformityWorkflow = Depends(get_nc_workflow)
):
    """
    Complete RCA with filled template.

    Extracts root causes from completed template and transitions NC to
    Corrective Action state.

    Args:
        nc_id: Nonconformity ID
        completed_template: Filled RCA template data
        actor_id: Person completing the RCA
        tenant_id: Tenant identifier

    Returns:
        Identified root causes and summary
    """
    try:
        result = await workflow.complete_rca(
            nc_id=nc_id,
            completed_template=completed_template,
            actor_id=actor_id,
            tenant_id=tenant_id
        )

        logger.info(f"RCA completed for NC {nc_id} by {actor_id}, identified {len(result.get('root_causes', []))} root causes")

        return {
            "status": "success",
            "message": "RCA completed successfully",
            "data": result
        }

    except ValueError as e:
        logger.error(f"Validation error completing RCA for NC {nc_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to complete RCA for NC {nc_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to complete RCA: {str(e)}"
        )


@router.get("/rca/templates/{method}")
async def get_rca_template(
    method: RCAMethod,
    problem_statement: str = Query(..., description="Description of the problem/nonconformity")
):
    """
    Get blank RCA template for specified method.

    Useful for clients to understand template structure before starting RCA.

    Args:
        method: RCA method (5_whys, fishbone, fault_tree)
        problem_statement: Description of the problem

    Returns:
        Blank RCA template with instructions
    """
    try:
        template = RCATemplateFactory.create_template(method, problem_statement)

        instructions = {
            RCAMethod.FIVE_WHYS: {
                "title": "5 Whys Method",
                "description": "Ask 'Why?' 5 times to drill down to root cause. Each answer becomes the next question.",
                "steps": [
                    "1. State the problem clearly in problem_statement",
                    "2. Ask 'Why did this happen?' and fill why_1",
                    "3. Take the answer from why_1 and ask 'Why?' again, fill why_2",
                    "4. Continue for why_3, why_4, why_5",
                    "5. The last 'Why' typically reveals the root cause",
                    "6. Optionally specify root_cause explicitly"
                ],
                "example": {
                    "problem_statement": "Server downtime occurred",
                    "why_1": "Database connection failed",
                    "why_2": "Connection pool was exhausted",
                    "why_3": "Too many concurrent requests",
                    "why_4": "Load balancer misconfigured",
                    "why_5": "Configuration not updated after deployment"
                }
            },
            RCAMethod.FISHBONE: {
                "title": "Fishbone (Ishikawa) Diagram",
                "description": "Categorize causes into 6M categories: People, Process, Technology, Environment, Materials, Measurement",
                "steps": [
                    "1. State the problem in problem_statement",
                    "2. For each 6M category, add causes as FishboneCause objects",
                    "3. Each cause has description and optional sub_causes list",
                    "4. Causes with sub_causes are likely root causes"
                ],
                "categories": {
                    "people": "Human factors, training, skills, competency",
                    "process": "Procedures, workflows, policies",
                    "technology": "Systems, tools, infrastructure",
                    "environment": "Physical conditions, external factors",
                    "materials": "Resources, inputs, supplies",
                    "measurement": "Metrics, monitoring, detection"
                }
            },
            RCAMethod.FAULT_TREE: {
                "title": "Fault Tree Analysis",
                "description": "Build tree of contributing factors with AND/OR gates and probabilities",
                "steps": [
                    "1. Top event is the problem (already in problem_statement)",
                    "2. Add children to top_event representing contributing factors",
                    "3. Set gate_type: 'AND' (all must occur) or 'OR' (at least one occurs)",
                    "4. For leaf nodes, set probability (0.0-1.0)",
                    "5. Tree auto-calculates total probability"
                ],
                "gate_types": {
                    "AND": "All child events must occur for parent to occur (multiply probabilities)",
                    "OR": "At least one child event must occur (combine probabilities)"
                }
            }
        }

        return {
            "method": method.value,
            "template": RCATemplateFactory.template_to_dict(template),
            "instructions": instructions.get(method, {"description": "Complete the RCA template"})
        }

    except Exception as e:
        logger.error(f"Failed to create RCA template for {method}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create template: {str(e)}"
        )


# =============================================================================
# HELPER ENDPOINTS
# =============================================================================

@router.get("/rca/methods")
async def get_rca_methods():
    """
    Get list of available RCA methods.

    Returns:
        Available RCA methods with descriptions
    """
    return {
        "methods": [
            {
                "value": RCAMethod.FIVE_WHYS.value,
                "label": "5 Whys",
                "description": "Ask 'Why?' 5 times to drill down to root cause",
                "best_for": "Simple, straightforward problems with clear cause-effect chains",
                "complexity": "Low"
            },
            {
                "value": RCAMethod.FISHBONE.value,
                "label": "Fishbone (Ishikawa) Diagram",
                "description": "Categorize causes by 6M framework",
                "best_for": "Complex problems with multiple contributing factors",
                "complexity": "Medium"
            },
            {
                "value": RCAMethod.FAULT_TREE.value,
                "label": "Fault Tree Analysis",
                "description": "Top-down deductive analysis with probability",
                "best_for": "Critical systems requiring quantitative risk analysis",
                "complexity": "High"
            }
        ]
    }
