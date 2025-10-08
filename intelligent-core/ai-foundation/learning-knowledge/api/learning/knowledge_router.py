"""
Knowledge Base Integration API Router

Endpoints for gap→knowledge mapping and learning paths
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from engines.knowledge_integrator import (
    KnowledgeIntegrator,
    LearningPathGenerator,
    GapEffectivenessTracker
)

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize engines
knowledge_integrator = KnowledgeIntegrator()
path_generator = LearningPathGenerator(knowledge_integrator)
effectiveness_tracker = GapEffectivenessTracker()


# =====================================================
# Request/Response Models
# =====================================================

class GapMappingRequest(BaseModel):
    """Request for gap→knowledge mapping"""
    exercise_gaps: List[str]


class LearningPathRequest(BaseModel):
    """Request for learning path generation"""
    user_id: str
    exercise_gaps: List[str]
    current_competency_score: float
    target_competency_score: float


class EffectivenessRecordRequest(BaseModel):
    """Record effectiveness of a resource"""
    gap_keyword: str
    resource_id: str
    gap_resolved: bool


# =====================================================
# Endpoints
# =====================================================

@router.post("/gaps/map-to-knowledge")
async def map_gaps_to_knowledge(request: GapMappingRequest):
    """
    Map exercise gaps to knowledge base resources

    Returns:
    - Knowledge topics to study
    - Recommended resources
    - Priority levels
    """
    try:
        mappings = knowledge_integrator.map_gaps_to_knowledge(
            exercise_gaps=request.exercise_gaps
        )

        return {
            'total_gaps': len(request.exercise_gaps),
            'mappings': mappings
        }

    except Exception as e:
        logger.error(f"Error mapping gaps to knowledge: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/learning-paths/generate")
async def generate_learning_path(request: LearningPathRequest):
    """
    Generate personalized learning path

    Based on:
    - Identified gaps
    - Current competency
    - Target competency
    """
    try:
        learning_path = path_generator.generate_learning_path(
            user_id=request.user_id,
            exercise_gaps=request.exercise_gaps,
            current_competency_score=request.current_competency_score,
            target_competency_score=request.target_competency_score
        )

        return learning_path

    except Exception as e:
        logger.error(f"Error generating learning path: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/learning-paths/save")
async def save_learning_path(
    user_id: str,
    path_data: dict
):
    """
    Save learning path to database

    Stores in learning.learning_paths and learning.user_learning_progress
    """
    try:
        # TODO: Implement database save
        # INSERT INTO learning.learning_paths
        # INSERT INTO learning.user_learning_progress

        return {
            "message": "Learning path saved",
            "user_id": user_id,
            "note": "Database save not yet implemented"
        }

    except Exception as e:
        logger.error(f"Error saving learning path: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/learning-paths/{user_id}")
async def get_user_learning_paths(
    user_id: str,
    status: Optional[str] = Query(None, description="Filter by status")
):
    """
    Get user's learning paths

    TODO: Fetch from database (learning.user_learning_progress)
    """
    # Placeholder
    return {
        "message": "User learning paths",
        "user_id": user_id,
        "status": status,
        "note": "Database fetch not yet implemented"
    }


@router.post("/learning-paths/{path_id}/progress")
async def update_learning_progress(
    path_id: str,
    user_id: str,
    current_step: int,
    completion_percentage: float
):
    """
    Update user's progress on a learning path

    Updates learning.user_learning_progress
    """
    try:
        # TODO: Implement database update
        # UPDATE learning.user_learning_progress

        return {
            "message": "Learning progress updated",
            "path_id": path_id,
            "user_id": user_id,
            "current_step": current_step,
            "completion_percentage": completion_percentage,
            "note": "Database update not yet implemented"
        }

    except Exception as e:
        logger.error(f"Error updating learning progress: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/effectiveness/record")
async def record_resource_effectiveness(request: EffectivenessRecordRequest):
    """
    Record effectiveness of a resource in resolving a gap

    Tracks which resources work best
    """
    try:
        # Record recommendation
        effectiveness_tracker.record_recommendation(
            gap_keyword=request.gap_keyword,
            resource_id=request.resource_id
        )

        # Record resolution
        effectiveness_tracker.record_resolution(
            gap_keyword=request.gap_keyword,
            resource_id=request.resource_id,
            gap_resolved=request.gap_resolved
        )

        return {
            "message": "Effectiveness recorded",
            "gap_keyword": request.gap_keyword,
            "resource_id": request.resource_id,
            "resolved": request.gap_resolved
        }

    except Exception as e:
        logger.error(f"Error recording effectiveness: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/effectiveness/report")
async def get_effectiveness_report():
    """
    Get effectiveness report

    Which gap→resource mappings work best
    """
    try:
        report = effectiveness_tracker.get_effectiveness_report()
        return report

    except Exception as e:
        logger.error(f"Error generating effectiveness report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/effectiveness/{gap_keyword}/best-resources")
async def get_best_resources_for_gap(
    gap_keyword: str,
    min_recommendations: int = Query(3, description="Minimum times recommended")
):
    """
    Get most effective resources for a specific gap

    Based on historical effectiveness data
    """
    try:
        resources = effectiveness_tracker.get_most_effective_resources(
            gap_keyword=gap_keyword,
            min_recommendations=min_recommendations
        )

        return {
            "gap_keyword": gap_keyword,
            "best_resources": resources
        }

    except Exception as e:
        logger.error(f"Error getting best resources: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/gap-mappings")
async def list_gap_mappings():
    """
    List all available gap→knowledge mappings

    TODO: Fetch from database (learning.gap_knowledge_mappings)
    """
    # Placeholder - return current mappings
    return {
        "message": "Gap→Knowledge mappings",
        "available_categories": list(knowledge_integrator.gap_keyword_mappings.keys()),
        "note": "Fetch from database for stored mappings"
    }


@router.post("/gap-mappings/create")
async def create_gap_mapping(
    gap_keyword: str,
    gap_category: str,
    knowledge_article_ids: List[str],
    recommended_resources: List[dict]
):
    """
    Create new gap→knowledge mapping

    Stores in learning.gap_knowledge_mappings
    """
    try:
        # TODO: Implement database insert
        # INSERT INTO learning.gap_knowledge_mappings

        return {
            "message": "Gap mapping created",
            "gap_keyword": gap_keyword,
            "gap_category": gap_category,
            "note": "Database insert not yet implemented"
        }

    except Exception as e:
        logger.error(f"Error creating gap mapping: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/resources/recommend")
async def recommend_resources(
    gaps: List[str] = Query(..., description="List of gaps to address"),
    limit: int = Query(5, description="Max resources to return")
):
    """
    Get recommended resources for multiple gaps

    Prioritized and deduplicated
    """
    try:
        all_resources = []

        for gap in gaps:
            mappings = knowledge_integrator.map_gaps_to_knowledge([gap])

            for mapping in mappings:
                for resource in mapping['recommended_resources']:
                    resource['gap_addressed'] = gap
                    resource['gap_priority'] = mapping['priority']
                    all_resources.append(resource)

        # Sort by priority (within resource priority)
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        all_resources.sort(
            key=lambda x: (
                priority_order.get(x.get('gap_priority', 'medium'), 3),
                x.get('priority', 99)
            )
        )

        # Deduplicate by title
        seen_titles = set()
        unique_resources = []

        for resource in all_resources:
            title = resource.get('title')
            if title not in seen_titles:
                seen_titles.add(title)
                unique_resources.append(resource)

        return {
            'total_gaps': len(gaps),
            'recommended_resources': unique_resources[:limit]
        }

    except Exception as e:
        logger.error(f"Error recommending resources: {e}")
        raise HTTPException(status_code=500, detail=str(e))
