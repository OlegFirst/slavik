"""
Collaboration Mixin

Enables services to collaborate and make consensus decisions.
Supports distributed decision making and service coordination.
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import uuid

logger = logging.getLogger(__name__)


class ConsensusStrategy(Enum):
    """Strategy for reaching consensus"""
    UNANIMOUS = "unanimous"      # All must agree
    MAJORITY = "majority"        # >50% must agree
    QUORUM = "quorum"           # >= 2/3 must agree
    PRIMARY = "primary"         # Primary service decides
    WEIGHTED = "weighted"       # Weighted by expertise


class VoteType(Enum):
    """Type of vote in consensus"""
    APPROVE = "approve"
    REJECT = "reject"
    ABSTAIN = "abstain"
    DELEGATE = "delegate"


@dataclass
class Vote:
    """Vote from a service"""
    service: str
    vote: VoteType
    confidence: float = 1.0
    reasoning: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ConsensusRequest:
    """Request for consensus decision"""
    request_id: str
    initiator: str
    participants: List[str]
    context: Dict[str, Any]
    strategy: ConsensusStrategy = ConsensusStrategy.MAJORITY
    timeout_seconds: int = 30
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class CollaborationDecision:
    """Result of collaboration"""
    decision: str                           # "approved", "rejected", "timeout"
    votes: List[Vote] = field(default_factory=list)
    confidence: float = 0.0
    reasoning: str = ""
    consensus_reached: bool = False
    participants_responded: int = 0
    total_participants: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


class CollaborationMixin:
    """
    Mixin for service collaboration.

    Enables services to:
    - Request consensus from other services
    - Respond to consensus requests
    - Find alternative service handlers
    - Broadcast status changes
    - Coordinate distributed decisions

    Usage:
        collaboration = CollaborationMixin("bia")

        # Request consensus
        decision = await collaboration.request_consensus(
            ["risk", "compliance"],
            {"action": "approve_plan", "plan_id": 123}
        )

        # Find alternatives
        alternatives = await collaboration.find_alternative_handlers("bia.assessment")
    """

    def __init__(
        self,
        service_name: str,
        eventbus_client: Optional[Any] = None
    ):
        """
        Initialize collaboration mixin.

        Args:
            service_name: Service identifier
            eventbus_client: Optional EventBus client for communication
        """
        self.service_name = service_name
        self.eventbus = eventbus_client

        # State
        self._pending_requests: Dict[str, ConsensusRequest] = {}
        self._votes: Dict[str, List[Vote]] = {}  # request_id -> votes
        self._vote_handlers: Dict[str, callable] = {}
        self._service_registry: Dict[str, Set[str]] = {}  # service -> capabilities

        # Metrics
        self._metrics = {
            "consensus_requests": 0,
            "consensus_approved": 0,
            "consensus_rejected": 0,
            "consensus_timeout": 0,
            "votes_cast": 0
        }

        logger.info(f"CollaborationMixin initialized for {service_name}")

    def register_vote_handler(self, context_type: str, handler: callable):
        """
        Register a handler for vote requests.

        Args:
            context_type: Type of decision context (e.g., "plan_approval")
            handler: Async function that returns Vote
        """
        self._vote_handlers[context_type] = handler
        logger.debug(f"Registered vote handler for {context_type}")

    def register_service_capabilities(self, service: str, capabilities: Set[str]):
        """
        Register another service's capabilities.

        Args:
            service: Service name
            capabilities: Set of capability names
        """
        self._service_registry[service] = capabilities
        logger.debug(f"Registered {len(capabilities)} capabilities for {service}")

    async def request_consensus(
        self,
        participants: List[str],
        context: Dict[str, Any],
        strategy: ConsensusStrategy = ConsensusStrategy.MAJORITY,
        timeout_seconds: int = 30
    ) -> CollaborationDecision:
        """
        Request consensus from other services.

        Args:
            participants: List of service names to consult
            context: Decision context
            strategy: Consensus strategy
            timeout_seconds: Timeout for responses

        Returns:
            CollaborationDecision with result
        """
        self._metrics["consensus_requests"] += 1

        request_id = str(uuid.uuid4())
        request = ConsensusRequest(
            request_id=request_id,
            initiator=self.service_name,
            participants=participants,
            context=context,
            strategy=strategy,
            timeout_seconds=timeout_seconds
        )

        self._pending_requests[request_id] = request
        self._votes[request_id] = []

        # Broadcast consensus request
        if self.eventbus:
            await self._broadcast_consensus_request(request)

        # Wait for votes
        try:
            await asyncio.wait_for(
                self._collect_votes(request_id, len(participants)),
                timeout=timeout_seconds
            )
        except asyncio.TimeoutError:
            logger.warning(f"Consensus request {request_id} timed out")

        # Evaluate consensus
        decision = await self._evaluate_consensus(request_id, strategy)

        # Update metrics
        if decision.consensus_reached:
            if decision.decision == "approved":
                self._metrics["consensus_approved"] += 1
            else:
                self._metrics["consensus_rejected"] += 1
        else:
            self._metrics["consensus_timeout"] += 1

        # Cleanup
        del self._pending_requests[request_id]
        del self._votes[request_id]

        return decision

    async def cast_vote(self, request_id: str, context: Dict[str, Any]) -> Vote:
        """
        Cast vote for a consensus request.

        Args:
            request_id: Consensus request ID
            context: Decision context

        Returns:
            Vote
        """
        self._metrics["votes_cast"] += 1

        # Find appropriate handler
        context_type = context.get("type", "unknown")
        handler = self._vote_handlers.get(context_type)

        if handler:
            # Use custom handler
            vote = await handler(context)
        else:
            # Default: approve with low confidence
            vote = Vote(
                service=self.service_name,
                vote=VoteType.ABSTAIN,
                confidence=0.5,
                reasoning="No specific handler for this context"
            )

        # Broadcast vote if EventBus available
        if self.eventbus:
            await self._broadcast_vote(request_id, vote)

        return vote

    async def find_alternative_handlers(self, capability: str) -> List[str]:
        """
        Find other services that can handle a capability.

        Args:
            capability: Capability name

        Returns:
            List of service names
        """
        alternatives = []

        for service, capabilities in self._service_registry.items():
            if service == self.service_name:
                continue

            # Check if service has the capability
            if capability in capabilities:
                alternatives.append(service)
                continue

            # Check wildcard match
            for cap in capabilities:
                if self._match_capability(capability, cap):
                    alternatives.append(service)
                    break

        return alternatives

    async def find_related_services(self, event_type: str) -> List[str]:
        """
        Find services related to an event type.

        Args:
            event_type: Event type (e.g., "bia.assessment.completed")

        Returns:
            List of related service names
        """
        # Extract domain from event type
        domain = event_type.split(".")[0] if "." in event_type else event_type

        related = []

        # Common BCM service relationships
        relationships = {
            "bia": ["risk", "compliance", "plans"],
            "risk": ["bia", "compliance", "response"],
            "compliance": ["bia", "risk", "governance"],
            "plans": ["bia", "risk", "response"],
            "response": ["risk", "plans", "governance"]
        }

        if domain in relationships:
            related = relationships[domain]

        return [s for s in related if s != self.service_name]

    async def broadcast_status(self, status: str, metadata: Dict[str, Any]):
        """
        Broadcast status change to other services.

        Args:
            status: Status string (e.g., "healthy", "degraded", "down")
            metadata: Additional status information
        """
        if not self.eventbus:
            logger.debug("No EventBus available for status broadcast")
            return

        event = {
            "event_type": f"{self.service_name}.status.changed",
            "service": self.service_name,
            "status": status,
            "metadata": metadata,
            "timestamp": datetime.utcnow().isoformat()
        }

        await self.eventbus.publish(
            f"{self.service_name}.status",
            event
        )

        logger.info(f"Broadcasted status: {status}")

    async def handle_consensus_request(self, request: Dict[str, Any]):
        """
        Handle incoming consensus request.

        Args:
            request: Consensus request from another service
        """
        request_id = request.get("request_id")
        context = request.get("context", {})

        # Cast vote
        vote = await self.cast_vote(request_id, context)

        logger.info(f"Cast vote for {request_id}: {vote.vote.value} (confidence: {vote.confidence})")

    def get_metrics(self) -> Dict[str, Any]:
        """Get collaboration metrics"""
        return {
            **self._metrics,
            "service_name": self.service_name,
            "registered_services": len(self._service_registry),
            "pending_requests": len(self._pending_requests)
        }

    # Private methods

    async def _broadcast_consensus_request(self, request: ConsensusRequest):
        """Broadcast consensus request to participants"""
        event = {
            "event_type": "consensus.request",
            "request_id": request.request_id,
            "initiator": request.initiator,
            "participants": request.participants,
            "context": request.context,
            "strategy": request.strategy.value,
            "timeout_seconds": request.timeout_seconds
        }

        for participant in request.participants:
            topic = f"{participant}.consensus"
            await self.eventbus.publish(topic, event)

        logger.debug(f"Broadcasted consensus request {request.request_id} to {len(request.participants)} services")

    async def _broadcast_vote(self, request_id: str, vote: Vote):
        """Broadcast vote to initiator"""
        event = {
            "event_type": "consensus.vote",
            "request_id": request_id,
            "service": vote.service,
            "vote": vote.vote.value,
            "confidence": vote.confidence,
            "reasoning": vote.reasoning,
            "metadata": vote.metadata
        }

        # Send to consensus topic
        await self.eventbus.publish("consensus.votes", event)

        logger.debug(f"Broadcasted vote for {request_id}: {vote.vote.value}")

    async def _collect_votes(self, request_id: str, expected_votes: int):
        """
        Collect votes for a request.

        Waits until all expected votes are received.
        """
        while len(self._votes.get(request_id, [])) < expected_votes:
            await asyncio.sleep(0.1)

    async def _evaluate_consensus(
        self,
        request_id: str,
        strategy: ConsensusStrategy
    ) -> CollaborationDecision:
        """
        Evaluate consensus based on votes.

        Args:
            request_id: Request ID
            strategy: Consensus strategy

        Returns:
            CollaborationDecision
        """
        votes = self._votes.get(request_id, [])
        request = self._pending_requests.get(request_id)

        if not request:
            return CollaborationDecision(
                decision="rejected",
                reasoning="Request not found"
            )

        total_participants = len(request.participants)
        responded = len(votes)

        # Count votes
        approve_count = sum(1 for v in votes if v.vote == VoteType.APPROVE)
        reject_count = sum(1 for v in votes if v.vote == VoteType.REJECT)
        abstain_count = sum(1 for v in votes if v.vote == VoteType.ABSTAIN)

        # Calculate weighted confidence
        total_confidence = sum(v.confidence for v in votes if v.vote == VoteType.APPROVE)
        avg_confidence = total_confidence / approve_count if approve_count > 0 else 0.0

        # Determine consensus based on strategy
        consensus_reached = False
        decision = "rejected"
        reasoning = ""

        if strategy == ConsensusStrategy.UNANIMOUS:
            if approve_count == total_participants:
                consensus_reached = True
                decision = "approved"
                reasoning = "Unanimous approval"
            else:
                reasoning = f"Not unanimous: {approve_count}/{total_participants} approved"

        elif strategy == ConsensusStrategy.MAJORITY:
            if approve_count > total_participants / 2:
                consensus_reached = True
                decision = "approved"
                reasoning = f"Majority approval: {approve_count}/{total_participants}"
            else:
                reasoning = f"No majority: {approve_count}/{total_participants}"

        elif strategy == ConsensusStrategy.QUORUM:
            quorum = total_participants * 2 / 3
            if approve_count >= quorum:
                consensus_reached = True
                decision = "approved"
                reasoning = f"Quorum reached: {approve_count}/{total_participants}"
            else:
                reasoning = f"Quorum not reached: {approve_count}/{quorum:.0f}"

        elif strategy == ConsensusStrategy.WEIGHTED:
            # Weighted by confidence
            if total_confidence >= total_participants * 0.6:
                consensus_reached = True
                decision = "approved"
                reasoning = f"Weighted approval: {total_confidence:.2f}/{total_participants}"
            else:
                reasoning = f"Insufficient weighted votes: {total_confidence:.2f}/{total_participants}"

        # Handle timeout
        if responded < total_participants:
            reasoning += f" (only {responded}/{total_participants} responded)"

        return CollaborationDecision(
            decision=decision,
            votes=votes,
            confidence=avg_confidence,
            reasoning=reasoning,
            consensus_reached=consensus_reached,
            participants_responded=responded,
            total_participants=total_participants
        )

    def _match_capability(self, requested: str, available: str) -> bool:
        """Check if capability matches (supports wildcards)"""
        if requested == available:
            return True

        # Wildcard matching
        if "*" in available:
            import re
            pattern = available.replace(".", r"\.").replace("*", ".*")
            return bool(re.match(f"^{pattern}$", requested))

        return False


# Example vote handlers

async def approve_vote_handler(context: Dict[str, Any]) -> Vote:
    """Example: Always approve"""
    return Vote(
        service="example",
        vote=VoteType.APPROVE,
        confidence=1.0,
        reasoning="Auto-approved"
    )


async def ai_vote_handler(context: Dict[str, Any], ai_client) -> Vote:
    """Example: Use AI to make decision"""
    # This would call AI Orchestrator for intelligent decision
    prompt = f"Should we {context.get('action')}? Context: {context}"

    # TODO: Call AI Orchestrator
    # decision = await ai_client.decide(prompt)

    return Vote(
        service="ai",
        vote=VoteType.APPROVE,  # Placeholder
        confidence=0.8,
        reasoning="AI-based decision"
    )
