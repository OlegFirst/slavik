"""
Community API Router

Endpoints for Community Level features:
- Twin matching
- Knowledge exchange
- People matching
- Privacy settings
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel

from core.community.twin_matching_engine import TwinMatchingEngine
from core.community.knowledge_exchange_db import KnowledgeExchangeServiceDB
from core.community.people_matching_db import PeopleMatchingServiceDB
from core.community.models import (
    TwinMatch,
    MatchFilters,
    Learning,
    LearningContribution,
    LearningQuery,
    LearningFeedback,
    PeerMatch,
    PeerCriteria,
    UserNetworkingProfile,
    PrivacySettings,
    CommunityStats,
    IndustryType,
    OrganizationSize,
    BCMMaturityLevel,
)

from api.dependencies import (
    get_twin_matching,
    get_knowledge_exchange_service,
    get_people_matching_service
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/community", tags=["community"])


# ============================================
# TWIN MATCHING ENDPOINTS
# ============================================

@router.post("/twins/find-matches", response_model=List[TwinMatch])
async def find_matching_twins(
    twin_id: str,
    filters: Optional[MatchFilters] = None,
    matching: TwinMatchingEngine = Depends(get_twin_matching)
):
    """
    Find matching organization twins

    Args:
        twin_id: Source twin ID
        filters: Optional matching filters

    Returns:
        List of matching twins sorted by similarity
    """
    logger.info(f"Finding matches for twin: {twin_id}")

    # TODO: Get twin and all candidates from database
    # For now, return empty list
    # In real implementation:
    # twin = await get_twin_from_db(twin_id)
    # all_twins = await get_all_twins_from_db()
    # matches = await matching.find_matches(twin, all_twins, filters)

    return []


@router.get("/twins/similarity/{twin_id_a}/{twin_id_b}")
async def calculate_twin_similarity(
    twin_id_a: str,
    twin_id_b: str,
    matching: TwinMatchingEngine = Depends(get_twin_matching)
):
    """
    Calculate similarity between two twins

    Returns:
        SimilarityScore with breakdown
    """
    logger.info(f"Calculating similarity: {twin_id_a} <-> {twin_id_b}")

    # TODO: Get twins from database and calculate similarity
    # twin_a = await get_twin_from_db(twin_id_a)
    # twin_b = await get_twin_from_db(twin_id_b)
    # similarity = await matching.calculate_similarity(twin_a, twin_b)

    raise HTTPException(status_code=501, detail="Not implemented - requires database integration")


# ============================================
# KNOWLEDGE EXCHANGE ENDPOINTS
# ============================================

@router.post("/knowledge/contribute", response_model=Learning)
async def contribute_learning(
    twin_id: str,
    contribution: LearningContribution,
    industry: IndustryType,
    size_category: OrganizationSize,
    maturity_level: BCMMaturityLevel,
    knowledge: KnowledgeExchangeServiceDB = Depends(get_knowledge_exchange_service)
):
    """
    Contribute a learning to community pool

    Args:
        twin_id: Contributing organization (kept private)
        contribution: Learning details
        industry: Organization industry
        size_category: Organization size
        maturity_level: BCM maturity

    Returns:
        Created learning (anonymized)
    """
    logger.info(f"Receiving learning contribution from twin: {twin_id}")

    learning = await knowledge.contribute_learning(
        twin_id=twin_id,
        contribution=contribution,
        industry=industry,
        size_category=size_category,
        maturity_level=maturity_level
    )

    return learning


@router.post("/knowledge/query", response_model=List[Learning])
async def query_learnings(
    query: LearningQuery,
    knowledge: KnowledgeExchangeServiceDB = Depends(get_knowledge_exchange_service)
):
    """
    Query relevant learnings

    Args:
        query: Learning query with context and filters

    Returns:
        List of relevant learnings
    """
    logger.info(f"Querying learnings: {query.context[:50]}...")

    learnings = await knowledge.get_relevant_learnings(query)

    return learnings


@router.get("/knowledge/topic/{topic}", response_model=List[Learning])
async def get_learnings_by_topic(
    topic: str,
    industry: Optional[IndustryType] = None,
    size_category: Optional[OrganizationSize] = None,
    min_effectiveness: float = Query(default=0.7, ge=0.0, le=1.0),
    limit: int = Query(default=10, ge=1, le=50),
    knowledge: KnowledgeExchangeServiceDB = Depends(get_knowledge_exchange_service)
):
    """Get learnings by topic"""
    learnings = await knowledge.get_learning_by_topic(
        topic=topic,
        industry=industry,
        size_category=size_category,
        min_effectiveness=min_effectiveness,
        limit=limit
    )

    return learnings


@router.get("/knowledge/top", response_model=List[Learning])
async def get_top_learnings(
    industry: Optional[IndustryType] = None,
    limit: int = Query(default=20, ge=1, le=100),
    knowledge: KnowledgeExchangeServiceDB = Depends(get_knowledge_exchange_service)
):
    """Get top learnings by usage and effectiveness"""
    learnings = await knowledge.get_top_learnings(
        industry=industry,
        limit=limit
    )

    return learnings


@router.post("/knowledge/feedback")
async def submit_learning_feedback(
    feedback: LearningFeedback,
    twin_id: str,
    knowledge: KnowledgeExchangeServiceDB = Depends(get_knowledge_exchange_service)
):
    """Submit feedback on applied learning"""
    learning = await knowledge.submit_feedback(feedback, twin_id)

    return {
        "learning_id": learning.learning_id,
        "times_used": learning.times_used,
        "success_rate": learning.success_rate,
        "message": "Feedback submitted successfully"
    }


@router.get("/knowledge/statistics")
async def get_knowledge_statistics(
    knowledge: KnowledgeExchangeServiceDB = Depends(get_knowledge_exchange_service)
):
    """Get community knowledge exchange statistics"""
    stats = await knowledge.get_community_statistics()
    return stats


# ============================================
# PEOPLE MATCHING ENDPOINTS
# ============================================

@router.post("/people/profile", response_model=UserNetworkingProfile)
async def create_networking_profile(
    profile: UserNetworkingProfile,
    twin_id: str,
    people: PeopleMatchingServiceDB = Depends(get_people_matching_service)
):
    """Create or update networking profile"""
    logger.info(f"Creating profile for user: {profile.user_id}")

    created_profile = await people.create_profile(profile, twin_id)

    return created_profile


@router.get("/people/profile/{user_id}", response_model=UserNetworkingProfile)
async def get_networking_profile(
    user_id: str,
    people: PeopleMatchingServiceDB = Depends(get_people_matching_service)
):
    """Get user networking profile"""
    profile = await people.get_profile(user_id)

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    return profile


@router.put("/people/profile/{user_id}", response_model=UserNetworkingProfile)
async def update_networking_profile(
    user_id: str,
    updates: dict,
    people: PeopleMatchingServiceDB = Depends(get_people_matching_service)
):
    """Update networking profile"""
    profile = await people.update_profile(user_id, updates)

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    return profile


@router.delete("/people/profile/{user_id}")
async def delete_networking_profile(
    user_id: str,
    people: PeopleMatchingServiceDB = Depends(get_people_matching_service)
):
    """Delete networking profile"""
    deleted = await people.delete_profile(user_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Profile not found")

    return {"message": "Profile deleted successfully"}


@router.post("/people/find-peers", response_model=List[PeerMatch])
async def find_peers(
    user_id: str,
    criteria: PeerCriteria,
    people: PeopleMatchingServiceDB = Depends(get_people_matching_service)
):
    """
    Find matching peers

    Args:
        user_id: User seeking peers
        criteria: Matching criteria

    Returns:
        List of matching peers
    """
    logger.info(f"Finding peers for user: {user_id}")

    # TODO: Get all twins from database for organization similarity
    all_twins = []  # Placeholder
    peers = await people.find_peers(user_id, criteria, all_twins)

    return peers


@router.get("/people/find-mentors/{user_id}", response_model=List[PeerMatch])
async def find_mentors(
    user_id: str,
    role: Optional[str] = None,
    max_results: int = Query(default=10, ge=1, le=50),
    people: PeopleMatchingServiceDB = Depends(get_people_matching_service)
):
    """Find potential mentors"""
    logger.info(f"Finding mentors for user: {user_id}")

    # TODO: Get all twins from database for organization similarity
    all_twins = []  # Placeholder
    mentors = await people.find_mentors(user_id, all_twins, role, max_results)

    return mentors


@router.get("/people/find-collaborators/{user_id}", response_model=List[PeerMatch])
async def find_collaborators(
    user_id: str,
    max_results: int = Query(default=10, ge=1, le=50),
    people: PeopleMatchingServiceDB = Depends(get_people_matching_service)
):
    """Find collaboration opportunities"""
    logger.info(f"Finding collaborators for user: {user_id}")

    # TODO: Get all twins from database for organization similarity
    all_twins = []  # Placeholder
    collaborators = await people.find_collaboration_opportunities(user_id, all_twins, max_results)

    return collaborators


@router.get("/people/statistics")
async def get_network_statistics(
    people: PeopleMatchingServiceDB = Depends(get_people_matching_service)
):
    """Get networking statistics"""
    stats = await people.get_network_statistics()
    return stats


# ============================================
# COMMUNITY STATISTICS
# ============================================

@router.get("/statistics", response_model=CommunityStats)
async def get_community_statistics(
    twin_matching: TwinMatchingEngine = Depends(get_twin_matching),
    knowledge: KnowledgeExchangeServiceDB = Depends(get_knowledge_exchange_service),
    people: PeopleMatchingServiceDB = Depends(get_people_matching_service)
):
    """Get overall community statistics"""

    # TODO: Implement comprehensive stats from database
    # For now, return aggregated in-memory stats

    knowledge_stats = await knowledge.get_community_statistics()
    network_stats = await people.get_network_statistics()

    stats = CommunityStats(
        # Twin statistics (placeholders)
        total_twins=0,
        active_twins=0,
        twins_by_industry={},
        twins_by_size={},
        twins_by_maturity={},

        # Knowledge exchange
        total_learnings=knowledge_stats['total_learnings'],
        learnings_by_topic=knowledge_stats['learnings_by_topic'],
        avg_effectiveness_score=knowledge_stats['avg_effectiveness_score'],
        total_times_applied=knowledge_stats['total_applications'],

        # People matching
        total_professionals=network_stats['total_professionals'],
        professionals_by_role=network_stats['professionals_by_role'],
        active_mentorships=0,  # TODO: track active connections
        active_collaborations=0,

        # Engagement (placeholders)
        monthly_active_twins=0,
        monthly_contributions=0,
        monthly_matches=0,
    )

    return stats


# ============================================
# PRIVACY SETTINGS
# ============================================

@router.post("/privacy/settings", response_model=PrivacySettings)
async def update_privacy_settings(
    settings: PrivacySettings
):
    """Update user privacy settings"""
    logger.info(f"Updating privacy settings for user: {settings.user_id}")

    # TODO: Store in database
    # await save_privacy_settings(settings)

    return settings


@router.get("/privacy/settings/{user_id}", response_model=PrivacySettings)
async def get_privacy_settings(
    user_id: str
):
    """Get user privacy settings"""

    # TODO: Get from database
    # settings = await get_privacy_settings_from_db(user_id)

    # Return default settings for now
    return PrivacySettings(user_id=user_id)


# ============================================
# HEALTH CHECK
# ============================================

@router.get("/health")
async def community_health_check():
    """Health check for community services"""
    return {
        "status": "healthy",
        "services": {
            "twin_matching": "operational",
            "knowledge_exchange": "operational",
            "people_matching": "operational"
        }
    }
