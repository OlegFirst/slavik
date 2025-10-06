"""
Chief Executive AI

Top-level coordinator for all AI operations on the platform
"""

from typing import Dict, Any, Optional, List
import logging
from enum import Enum

logger = logging.getLogger(__name__)


class IntentSegment(str, Enum):
    """Request segment classification"""
    GOVERNANCE = "governance"
    PLATFORM = "platform"
    DOMAIN = "domain"
    UNKNOWN = "unknown"


class Intent:
    """User intent analysis"""

    def __init__(
        self,
        segment: IntentSegment,
        confidence: float,
        keywords: List[str],
        suggested_manager: str
    ):
        self.segment = segment
        self.confidence = confidence
        self.keywords = keywords
        self.suggested_manager = suggested_manager


class ChiefExecutiveAI:
    """
    Chief Executive AI - Top coordinator

    Responsibilities:
    - Analyze user requests and determine intent
    - Route to appropriate TOP Manager (Governance, Platform, Domain)
    - Monitor overall platform performance
    - Escalate complex multi-segment requests
    - Learn from user feedback

    This is Level 0 of the management hierarchy.
    """

    def __init__(
        self,
        governance_manager: Optional[Any] = None,
        platform_manager: Optional[Any] = None,
        domain_manager: Optional[Any] = None,
        llm_client: Optional[Any] = None
    ):
        """
        Initialize Chief Executive AI

        Args:
            governance_manager: Manager for governance segment
            platform_manager: Manager for platform segment
            domain_manager: Manager for domain/BCM segment
            llm_client: AI client for intent analysis
        """
        self.managers = {
            "governance": governance_manager,
            "platform": platform_manager,
            "domain": domain_manager
        }
        self.llm_client = llm_client
        self.logger = logger

        # Metrics
        self.total_requests = 0
        self.routing_accuracy = 1.0
        self.avg_response_time = 0.0

        # Intent classification keywords
        self.segment_keywords = {
            IntentSegment.GOVERNANCE: [
                "compliance", "audit", "governance", "policy", "regulation",
                "iso 22301", "iso 27001", "gdpr", "sox", "certification",
                "framework", "standard", "requirement", "control"
            ],
            IntentSegment.PLATFORM: [
                "workflow", "deployment", "performance", "monitoring",
                "automation", "integration", "api", "service", "architecture",
                "scalability", "reliability", "learning", "optimization",
                "mio", "orchestration", "pipeline"
            ],
            IntentSegment.DOMAIN: [
                "bia", "risk", "business impact", "recovery", "rto", "rpo",
                "incident", "disaster", "continuity", "bcm", "crisis",
                "exercise", "test", "plan", "strategy", "process",
                "dependency", "threat", "vulnerability", "supply chain"
            ]
        }

    async def handle_request(
        self,
        user_query: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Handle user request (main entry point)

        Args:
            user_query: User's question or request
            context: Context information (user_id, organization, etc.)

        Returns:
            Response from appropriate manager/expert
        """
        import time

        start_time = time.time()

        try:
            self.logger.info(f"Chief Executive AI processing request: {user_query[:100]}...")

            # Step 1: Analyze intent
            intent = await self.analyze_intent(user_query, context)

            self.logger.info(
                f"Intent: {intent.segment} (confidence: {intent.confidence:.2f})"
            )

            # Step 2: Route to appropriate manager
            if intent.segment == IntentSegment.GOVERNANCE:
                result = await self._route_to_governance(user_query, context, intent)
            elif intent.segment == IntentSegment.PLATFORM:
                result = await self._route_to_platform(user_query, context, intent)
            elif intent.segment == IntentSegment.DOMAIN:
                result = await self._route_to_domain(user_query, context, intent)
            else:
                # Unknown intent - try all managers
                result = await self._handle_unknown_intent(user_query, context)

            # Step 3: Track metrics
            response_time = time.time() - start_time
            self._track_request(
                success=result.get("success", True),
                response_time=response_time
            )

            # Add metadata
            result["metadata"] = {
                "intent": intent.segment.value,
                "confidence": intent.confidence,
                "response_time": response_time,
                "routed_to": intent.suggested_manager
            }

            return result

        except Exception as e:
            response_time = time.time() - start_time
            self._track_request(success=False, response_time=response_time)

            self.logger.error(f"Chief Executive AI request failed: {e}")

            return {
                "success": False,
                "error": f"Failed to process request: {str(e)}",
                "metadata": {
                    "response_time": response_time
                }
            }

    async def analyze_intent(
        self,
        user_query: str,
        context: Dict[str, Any]
    ) -> Intent:
        """
        Analyze user intent to determine segment

        Args:
            user_query: User's question
            context: Context information

        Returns:
            Intent analysis
        """
        query_lower = user_query.lower()

        # Keyword-based classification
        segment_scores = {
            IntentSegment.GOVERNANCE: 0.0,
            IntentSegment.PLATFORM: 0.0,
            IntentSegment.DOMAIN: 0.0
        }

        matched_keywords = {
            IntentSegment.GOVERNANCE: [],
            IntentSegment.PLATFORM: [],
            IntentSegment.DOMAIN: []
        }

        # Count keyword matches
        for segment, keywords in self.segment_keywords.items():
            for keyword in keywords:
                if keyword in query_lower:
                    segment_scores[segment] += 1
                    matched_keywords[segment].append(keyword)

        # Determine best segment
        if all(score == 0 for score in segment_scores.values()):
            # No keywords matched - use LLM if available
            if self.llm_client:
                return await self._llm_intent_analysis(user_query, context)
            else:
                # Default to domain (BCM) segment
                return Intent(
                    segment=IntentSegment.DOMAIN,
                    confidence=0.5,
                    keywords=[],
                    suggested_manager="domain"
                )

        # Get segment with highest score
        best_segment = max(segment_scores, key=segment_scores.get)
        best_score = segment_scores[best_segment]
        total_matches = sum(segment_scores.values())

        confidence = best_score / total_matches if total_matches > 0 else 0.5

        return Intent(
            segment=best_segment,
            confidence=confidence,
            keywords=matched_keywords[best_segment],
            suggested_manager=best_segment.value
        )

    async def _llm_intent_analysis(
        self,
        user_query: str,
        context: Dict[str, Any]
    ) -> Intent:
        """
        Use LLM for intent analysis when keywords don't match

        Args:
            user_query: User's question
            context: Context information

        Returns:
            LLM-based intent analysis
        """
        system_prompt = """You are the Chief Executive AI analyzing user intent.

Classify the request into one of three segments:
1. GOVERNANCE - Compliance, audits, policies, regulations, standards
2. PLATFORM - Workflows, deployment, performance, technical architecture
3. DOMAIN - Business continuity, BIA, risk, recovery, incidents

Respond with ONLY the segment name and confidence (0.0-1.0).
Format: SEGMENT|CONFIDENCE|KEYWORDS
Example: DOMAIN|0.85|bia,recovery,rto
"""

        user_prompt = f"""User query: {user_query}

Context: {context}

Classify this request."""

        try:
            response = await self.llm_client.query(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.1
            )

            # Parse response
            parts = response.strip().split("|")
            segment_str = parts[0].strip().lower()
            confidence = float(parts[1].strip()) if len(parts) > 1 else 0.7
            keywords = parts[2].strip().split(",") if len(parts) > 2 else []

            # Map to enum
            segment_map = {
                "governance": IntentSegment.GOVERNANCE,
                "platform": IntentSegment.PLATFORM,
                "domain": IntentSegment.DOMAIN
            }

            segment = segment_map.get(segment_str, IntentSegment.UNKNOWN)

            return Intent(
                segment=segment,
                confidence=confidence,
                keywords=keywords,
                suggested_manager=segment.value
            )

        except Exception as e:
            self.logger.error(f"LLM intent analysis failed: {e}")
            # Fallback to domain
            return Intent(
                segment=IntentSegment.DOMAIN,
                confidence=0.5,
                keywords=[],
                suggested_manager="domain"
            )

    async def _route_to_governance(
        self,
        user_query: str,
        context: Dict[str, Any],
        intent: Intent
    ) -> Dict[str, Any]:
        """Route to Governance Manager"""
        manager = self.managers["governance"]

        if not manager:
            return {
                "success": False,
                "error": "Governance Manager not available"
            }

        self.logger.info("Routing to Governance Manager")
        return await manager.handle(user_query, context)

    async def _route_to_platform(
        self,
        user_query: str,
        context: Dict[str, Any],
        intent: Intent
    ) -> Dict[str, Any]:
        """Route to Platform Manager"""
        manager = self.managers["platform"]

        if not manager:
            return {
                "success": False,
                "error": "Platform Manager not available"
            }

        self.logger.info("Routing to Platform Manager")
        return await manager.handle(user_query, context)

    async def _route_to_domain(
        self,
        user_query: str,
        context: Dict[str, Any],
        intent: Intent
    ) -> Dict[str, Any]:
        """Route to Domain/BCM Manager"""
        manager = self.managers["domain"]

        if not manager:
            return {
                "success": False,
                "error": "Domain Manager not available"
            }

        self.logger.info("Routing to Domain/BCM Manager")
        return await manager.handle(user_query, context)

    async def _handle_unknown_intent(
        self,
        user_query: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Handle requests with unknown intent

        Try each manager in order: domain -> governance -> platform
        """
        self.logger.warning("Unknown intent - trying all managers")

        for segment in ["domain", "governance", "platform"]:
            manager = self.managers[segment]
            if manager:
                try:
                    result = await manager.handle(user_query, context)
                    if result.get("success", False):
                        return result
                except Exception as e:
                    self.logger.error(
                        f"Manager '{segment}' failed on unknown intent: {e}"
                    )
                    continue

        return {
            "success": False,
            "error": "No manager could handle this request"
        }

    def _track_request(self, success: bool, response_time: float):
        """Track request metrics"""
        self.total_requests += 1

        # Update average response time
        if self.avg_response_time == 0:
            self.avg_response_time = response_time
        else:
            self.avg_response_time = (
                self.avg_response_time * 0.9 + response_time * 0.1
            )

        # Update routing accuracy
        if success:
            self.routing_accuracy = self.routing_accuracy * 0.95 + 1.0 * 0.05
        else:
            self.routing_accuracy = self.routing_accuracy * 0.95 + 0.0 * 0.05

    def get_status(self) -> Dict[str, Any]:
        """Get Chief Executive AI status"""
        return {
            "name": "Chief Executive AI",
            "role": "Top coordinator for all AI operations",
            "managers": {
                segment: manager.get_status() if manager else None
                for segment, manager in self.managers.items()
            },
            "metrics": {
                "total_requests": self.total_requests,
                "routing_accuracy": self.routing_accuracy,
                "avg_response_time": self.avg_response_time
            }
        }

    def set_manager(self, segment: str, manager: Any):
        """Set or update a manager"""
        if segment not in ["governance", "platform", "domain"]:
            raise ValueError(f"Invalid segment: {segment}")

        self.managers[segment] = manager
        self.logger.info(f"Set {segment} manager: {manager.name}")

    def get_manager(self, segment: str) -> Optional[Any]:
        """Get manager by segment"""
        return self.managers.get(segment)
