"""
Living Documentation API Endpoints

Interactive, personalized, self-evolving documentation API
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

router = APIRouter(prefix="/docs", tags=["living-documentation"])

# Request/Response Models

class GetDocRequest(BaseModel):
    """Request personalized documentation"""
    page_id: str
    user_id: str
    personalize: bool = True

class GenerateExampleRequest(BaseModel):
    """Request AI-generated example"""
    topic: str
    context: dict = Field(default_factory=dict)
    format_type: str = "detailed"  # detailed, quick, step_by_step, visual

class FeedbackRequest(BaseModel):
    """Submit feedback on documentation"""
    page_id: str
    user_id: str
    helpful: bool
    comment: Optional[str] = None

class SearchRequest(BaseModel):
    """Smart search request"""
    query: str
    user_id: str
    limit: int = 10

# Endpoints

@router.get("/{page_id}")
async def get_documentation(
    page_id: str,
    user_id: str,
    personalize: bool = True,
    current_user: dict = Depends(lambda: {"user_id": "user-123"})
):
    """
    Get documentation page (personalized)

    **Personalization:**
    - Industry-specific examples
    - Complexity adjusted to user level
    - Related content based on user's journey

    **Example:**
    ```
    GET /docs/rto-calculation?user_id=user-123&personalize=true
    ```

    Returns:
    - Personalized content
    - Relevant examples
    - Next steps
    - Interactive elements
    """

    # Get personalized documentation
    # In production: Use PersonalizationService

    return {
        "page_id": page_id,
        "title": "RTO Calculation Guide",
        "content": "Personalized content for healthcare...",
        "examples": [
            {
                "id": "ex-1",
                "title": "Emergency Department RTO",
                "content": "Hospital ER typically...",
                "industry_specific": True
            }
        ],
        "next_steps": [
            {
                "action": "calculate_your_rto",
                "title": "Calculate Your RTO",
                "tool": "rto_calculator"
            }
        ],
        "personalization": {
            "industry": "healthcare",
            "level": "beginner",
            "customized": True
        }
    }

@router.post("/examples/generate")
async def generate_example(
    request: GenerateExampleRequest,
    current_user: dict = Depends(lambda: {"user_id": "user-123"})
):
    """
    Generate AI-powered example on demand

    **Magic:**
    - User asks for specific example
    - AI generates it in seconds
    - Based on real data from collective intelligence
    - Fully personalized

    **Example Request:**
    ```json
    {
        "topic": "bia_process_identification",
        "context": {
            "industry": "healthcare",
            "org_type": "hospital",
            "specific_area": "supply_chain"
        },
        "format_type": "detailed"
    }
    ```

    **Example Response:**
    Complete BIA example for hospital supply chain with:
    - Critical processes identified
    - Dependencies mapped
    - RTOs calculated
    - Based on real hospital data!
    """

    # Generate example using AI
    # In production: Use AIExampleGenerator

    return {
        "topic": request.topic,
        "content": """
# Business Impact Analysis: Hospital Supply Chain

## Critical Processes Identified:
1. **Medical Supply Procurement** (RTO: 24h)
   - Dependencies: Primary suppliers, warehouse, receiving
   - Impact if down: Cannot restock critical supplies

2. **Pharmacy Operations** (RTO: 4h)
   - Dependencies: Supply chain, EHR access, staff
   - Impact if down: Cannot dispense medications

... (complete example)
        """,
        "explanation": "This approach prioritizes patient-facing processes...",
        "interactive_elements": [
            {
                "type": "wizard",
                "title": "Identify Your Processes",
                "action": "start_process_wizard"
            }
        ],
        "metadata": {
            "based_on_real_data": True,
            "source_count": 7,
            "generated_at": datetime.utcnow().isoformat()
        }
    }

@router.post("/feedback")
async def submit_feedback(
    request: FeedbackRequest,
    current_user: dict = Depends(lambda: {"user_id": "user-123"})
):
    """
    Submit feedback on documentation

    **Learning Loop:**
    - User votes helpful/not helpful
    - System learns what works
    - AI improves low-rated content
    - Quality improves over time

    Negative feedback triggers immediate review!
    """

    # Track feedback
    # In production: Use DocumentationEvolutionEngine

    if not request.helpful:
        # Flag for improvement
        logger.warning(f"Page {request.page_id} marked not helpful by {request.user_id}")

    return {
        "status": "feedback_received",
        "message": "Thank you! Your feedback helps improve documentation.",
        "will_improve": not request.helpful
    }

@router.get("/search")
async def smart_search(
    query: str,
    user_id: str,
    limit: int = 10,
    current_user: dict = Depends(lambda: {"user_id": "user-123"})
):
    """
    Smart AI-powered search

    **Intelligence:**
    - Understands intent (not just keywords)
    - Personalizes results for user
    - Learns from click patterns
    - Suggests related content

    **Example:**
    ```
    Query: "emergency department downtime"

    Traditional: Shows docs with those words
    Smart: Understands user wants RTO for ER
           Shows: RTO calculator, ER examples, case studies
    ```
    """

    # AI-powered search
    # In production: Use semantic search + personalization

    return {
        "query": query,
        "results": [
            {
                "id": "rto-calculation",
                "title": "Calculating RTO for Emergency Services",
                "snippet": "Emergency departments typically...",
                "relevance": 0.95,
                "type": "guide",
                "personalized": True
            },
            {
                "id": "ex-hospital-er",
                "title": "Case Study: Hospital ER Recovery",
                "snippet": "How a 300-bed hospital...",
                "relevance": 0.88,
                "type": "example"
            },
            {
                "id": "tool-rto-calc",
                "title": "Interactive RTO Calculator",
                "snippet": "Calculate RTO for your processes",
                "relevance": 0.82,
                "type": "tool"
            }
        ],
        "suggestions": [
            "RPO for emergency services",
            "24/7 operations recovery",
            "Healthcare BIA examples"
        ]
    }

@router.get("/journey/{goal}")
async def get_personalized_journey(
    goal: str,
    user_id: str,
    current_user: dict = Depends(lambda: {"user_id": "user-123"})
):
    """
    Get personalized learning journey

    **Not just one page - entire path!**

    Different paths for:
    - Beginner vs expert
    - Small clinic vs large hospital
    - Different goals (BIA, ISO certification, etc.)

    **Example:**
    ```
    GET /docs/journey/complete_bia?user_id=user-123
    ```

    Returns customized journey with:
    - Personalized steps
    - Estimated time
    - Progress tracking
    - Interactive tools
    """

    # Build personalized journey
    # In production: Use UserJourneyPersonalizer

    return {
        "goal": goal,
        "personalized_for": {
            "industry": "healthcare",
            "level": "beginner",
            "org_size": "medium"
        },
        "total_estimated_time": "4-8 hours",
        "completion_percentage": 0.35,
        "steps": [
            {
                "id": "bcm_basics",
                "title": "BCM Fundamentals",
                "type": "learning",
                "status": "completed",
                "estimated_time": "1 hour"
            },
            {
                "id": "process_id",
                "title": "Identify Critical Processes (Healthcare)",
                "type": "interactive_tool",
                "status": "in_progress",
                "estimated_time": "30-60 min"
            },
            {
                "id": "impact_analysis",
                "title": "Analyze Business Impact",
                "type": "guided_workflow",
                "status": "pending",
                "estimated_time": "1-2 hours"
            }
        ],
        "next_action": {
            "step_id": "process_id",
            "title": "Continue with Process Identification",
            "action": "resume_wizard"
        }
    }

@router.get("/gaps")
async def get_knowledge_gaps(
    days: int = 7,
    min_searches: int = 3
):
    """
    Get detected knowledge gaps

    **Admin endpoint:** Shows what documentation is missing

    Detects gaps from:
    - Searches with no results
    - Frequently asked questions
    - User confusion points

    **Example Response:**
    ```json
    {
        "gaps": [
            {
                "topic": "tier 3 supplier dependencies",
                "user_count": 15,
                "search_queries": ["tier 3 suppliers", "indirect dependencies"],
                "priority": "high"
            }
        ]
    }
    ```

    System will auto-generate missing topics!
    """

    # Detect gaps
    # In production: Use DocumentationEvolutionEngine

    return {
        "gaps_detected": 3,
        "gaps": [
            {
                "topic": "Remote Work BCM",
                "user_count": 12,
                "search_queries": [
                    "bcm for remote workers",
                    "distributed team continuity"
                ],
                "priority": "high",
                "auto_generation_scheduled": True
            },
            {
                "topic": "Pandemic-Specific BIA",
                "user_count": 10,
                "search_queries": [
                    "pandemic bia",
                    "covid business impact"
                ],
                "priority": "medium",
                "auto_generation_scheduled": True
            }
        ]
    }

@router.get("/improvements")
async def get_improvement_queue():
    """
    Get improvement queue

    **Admin endpoint:** Shows pages flagged for improvement

    Flagged based on:
    - Low engagement
    - Negative feedback
    - High bounce rate
    - Missing examples

    AI will automatically improve these!
    """

    return {
        "improvements_needed": 5,
        "queue": [
            {
                "page_id": "rto-calculation",
                "issues": ["too_short", "no_examples"],
                "priority": 8,
                "analytics": {
                    "avg_time": 35,
                    "helpful_rate": 0.3,
                    "bounce_rate": 0.75
                },
                "ai_improvement_status": "in_progress"
            }
        ]
    }

import logging
logger = logging.getLogger(__name__)
