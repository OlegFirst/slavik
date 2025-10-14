"""
Collective Agent API Endpoints

Endpoints:
- POST /collective-agents/create - Create new collective agent
- POST /collective-agents/{agent_id}/chat - Chat with agent
- GET /collective-agents/{agent_id} - Get agent details
- GET /collective-agents/active - Get active agents for org
- GET /collective-agents/{agent_id}/history - Get chat history
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from ..services.collective_agent_service import (
    CollectiveAgentService,
    InsufficientDataError,
    AgentNotFoundError,
    AgentExpiredError,
    UnauthorizedError
)
from ..dependencies import (
    get_db,
    get_current_user,
    get_collective_service
)

router = APIRouter(prefix="/collective-agents", tags=["collective-agents"])

# Request/Response Models

class CreateAgentRequest(BaseModel):
    """Request to create collective agent"""
    problem_type: str = Field(..., description="Type of problem (e.g., 'supply_chain_complexity')")
    min_orgs: int = Field(default=5, description="Minimum number of source organizations")

    class Config:
        json_schema_extra = {
            "example": {
                "problem_type": "supply_chain_complexity",
                "min_orgs": 5
            }
        }

class CreateAgentResponse(BaseModel):
    """Response from creating agent"""
    agent_id: str
    source_org_count: int
    problem_type: str
    expires_at: datetime
    message: str

    class Config:
        json_schema_extra = {
            "example": {
                "agent_id": "550e8400-e29b-41d4-a716-446655440000",
                "source_org_count": 7,
                "problem_type": "supply_chain_complexity",
                "expires_at": "2025-10-11T12:00:00",
                "message": "Collective Agent created from 7 organizations' experiences"
            }
        }

class ChatRequest(BaseModel):
    """Chat message request"""
    message: str = Field(..., description="User's question")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "How did you map Tier 2 supplier dependencies?"
            }
        }

class ChatResponse(BaseModel):
    """Chat message response"""
    message: str
    confidence: float
    source_count: int
    expires_at: str

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Organizations that addressed this typically started with Tier 1 suppliers...",
                "confidence": 0.85,
                "source_count": 7,
                "expires_at": "2025-10-11T12:00:00"
            }
        }

class AgentDetails(BaseModel):
    """Agent details"""
    agent_id: str
    problem_type: str
    source_org_count: int
    source_org_types: List[str]
    status: str
    created_at: datetime
    expires_at: datetime
    message_count: int
    last_interaction: Optional[datetime]

class ChatMessage(BaseModel):
    """Chat message"""
    role: str
    content: str
    created_at: datetime

# Endpoints

@router.post("/create", response_model=CreateAgentResponse, status_code=status.HTTP_201_CREATED)
async def create_collective_agent(
    request: CreateAgentRequest,
    current_user: dict = Depends(get_current_user),
    service: CollectiveAgentService = Depends(get_collective_service)
):
    """
    Create Collective Agent from similar organizations

    **What happens:**
    1. Platform finds organizations that solved this problem
    2. Extracts their approaches (fully anonymized)
    3. Creates temporary AI agent from collective wisdom
    4. You can chat with it for 7 days

    **Privacy:**
    - Source organizations NEVER revealed
    - Minimum 5 organizations required
    - All data anonymized before aggregation

    **Use case:**
    You're stuck on supply chain dependency mapping. Platform finds 7 organizations
    that completed it successfully. Creates agent you can ask questions like:
    "How did you map Tier 2 suppliers?" Agent responds with synthesized wisdom
    from all 7 organizations without revealing who they are.
    """

    try:
        agent_id = await service.create_collective_agent(
            problem_type=request.problem_type,
            requesting_org_id=current_user['org_id'],
            min_orgs=request.min_orgs
        )

        # Get agent details
        agent = await service.get_agent(agent_id)

        return CreateAgentResponse(
            agent_id=agent_id,
            source_org_count=agent.source_org_count,
            problem_type=agent.problem_type,
            expires_at=agent.expires_at,
            message=f"🤝 Collective Agent created from {agent.source_org_count} organizations' experiences"
        )

    except InsufficientDataError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/{agent_id}/chat", response_model=ChatResponse)
async def chat_with_agent(
    agent_id: str,
    request: ChatRequest,
    current_user: dict = Depends(get_current_user),
    service: CollectiveAgentService = Depends(get_collective_service)
):
    """
    Chat with Collective Agent

    **How it works:**
    - Agent represents collective wisdom of multiple organizations
    - NEVER reveals which organization did what
    - Speaks as: "Organizations that solved this typically..."
    - Synthesizes across all experiences

    **Example conversation:**
    ```
    You: "How did you map Tier 2 supplier dependencies?"

    Agent: "Organizations that addressed this typically started with
            Tier 1 suppliers and asked them to identify their critical
            suppliers. 5 out of 7 used supplier questionnaires, while
            2 conducted workshops. The common challenge was incomplete
            data, which they addressed by setting reasonable boundaries
            (e.g., top 80% of spend)."
    ```

    **Privacy:**
    - Agent will NEVER say "Hospital X did this..."
    - Only aggregate patterns and statistics
    - Full anonymity preserved
    """

    try:
        response = await service.chat(
            agent_id=agent_id,
            user_message=request.message,
            user_id=current_user['user_id']
        )

        return ChatResponse(**response)

    except AgentNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    except AgentExpiredError:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Agent has expired. Collective agents expire after 7 days."
        )
    except UnauthorizedError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this agent"
        )

@router.get("/{agent_id}", response_model=AgentDetails)
async def get_agent_details(
    agent_id: str,
    current_user: dict = Depends(get_current_user),
    service: CollectiveAgentService = Depends(get_collective_service)
):
    """
    Get Collective Agent details

    Returns information about the agent:
    - Source organization count (not identities)
    - Problem type
    - Expiration date
    - Usage stats
    """

    agent = await service.get_agent(agent_id)

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )

    # Check authorization
    if str(agent.requesting_org_id) != current_user['org_id']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )

    return AgentDetails(
        agent_id=str(agent.id),
        problem_type=agent.problem_type,
        source_org_count=agent.source_org_count,
        source_org_types=agent.source_org_types,
        status=agent.status.value,
        created_at=agent.created_at,
        expires_at=agent.expires_at,
        message_count=agent.message_count,
        last_interaction=agent.last_interaction
    )

@router.get("/active", response_model=List[AgentDetails])
async def get_active_agents(
    current_user: dict = Depends(get_current_user),
    service: CollectiveAgentService = Depends(get_collective_service)
):
    """
    Get all active Collective Agents for your organization

    Returns list of agents you can currently interact with
    """

    agents = await service.get_active_agents(current_user['org_id'])

    return [
        AgentDetails(
            agent_id=str(agent.id),
            problem_type=agent.problem_type,
            source_org_count=agent.source_org_count,
            source_org_types=agent.source_org_types,
            status=agent.status.value,
            created_at=agent.created_at,
            expires_at=agent.expires_at,
            message_count=agent.message_count,
            last_interaction=agent.last_interaction
        )
        for agent in agents
    ]

@router.get("/{agent_id}/history", response_model=List[ChatMessage])
async def get_chat_history(
    agent_id: str,
    current_user: dict = Depends(get_current_user),
    service: CollectiveAgentService = Depends(get_collective_service)
):
    """
    Get chat history with Collective Agent

    Returns all messages exchanged with the agent
    """

    agent = await service.get_agent(agent_id)

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )

    # Check authorization
    if str(agent.requesting_org_id) != current_user['org_id']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )

    # Get history
    history = await service._get_conversation_history(agent.id)

    return [
        ChatMessage(
            role=msg['role'],
            content=msg['content'],
            created_at=datetime.utcnow()  # Placeholder
        )
        for msg in history
    ]
