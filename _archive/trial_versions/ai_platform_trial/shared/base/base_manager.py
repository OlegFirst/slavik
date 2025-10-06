"""
Base Manager Class

Unified base for TOP Managers in the platform
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class BaseManager(ABC):
    """
    Base class for TOP Managers

    Managers coordinate experts in their segment.
    They receive requests from Chief Executive AI and delegate to appropriate experts.

    Management levels:
    - Level 0: Chief Executive AI (CEO)
    - Level 1: TOP Managers (this class) - Segment coordinators
    - Level 2: Experts - Domain specialists
    """

    def __init__(
        self,
        name: str,
        segment: str,  # 'governance', 'platform', or 'domain'
        description: str,
        experts: Optional[List[Any]] = None,
        llm_client: Optional[Any] = None
    ):
        """
        Initialize Manager

        Args:
            name: Manager name (e.g., "Governance Manager")
            segment: Segment this manager oversees
            description: Manager's responsibilities
            experts: List of Expert instances under this manager
            llm_client: AI client for decision-making
        """
        self.name = name
        self.segment = segment
        self.description = description
        self.experts = experts or []
        self.llm_client = llm_client
        self.logger = logger

        # Metrics
        self.requests_handled = 0
        self.avg_response_time = 0.0
        self.delegation_efficiency = 1.0

    @abstractmethod
    async def handle(
        self,
        user_query: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Handle request by delegating to appropriate expert

        Args:
            user_query: User's question or request
            context: Context information

        Returns:
            Response from delegated expert
        """
        pass

    async def select_expert(
        self,
        user_query: str,
        context: Dict[str, Any]
    ) -> Optional[Any]:
        """
        Select the best expert to handle this request

        Args:
            user_query: User's question
            context: Context information

        Returns:
            Selected expert or None
        """
        if not self.experts:
            return None

        # Get confidence scores from all experts
        expert_scores = []

        for expert in self.experts:
            try:
                score = expert.can_handle(user_query, context)
                expert_scores.append((expert, score))
            except Exception as e:
                self.logger.error(
                    f"Error getting score from expert '{expert.name}': {e}"
                )
                expert_scores.append((expert, 0.0))

        # Sort by score
        expert_scores.sort(key=lambda x: x[1], reverse=True)

        # Return best expert if confidence is high enough
        best_expert, best_score = expert_scores[0]

        if best_score >= 0.3:  # Minimum confidence threshold
            self.logger.info(
                f"Manager '{self.name}' selected expert '{best_expert.name}' "
                f"with confidence {best_score:.2f}"
            )
            return best_expert
        else:
            self.logger.warning(
                f"No expert in segment '{self.segment}' can handle request "
                f"with sufficient confidence (best: {best_score:.2f})"
            )
            return None

    async def delegate(
        self,
        expert: Any,
        user_query: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Delegate request to expert

        Args:
            expert: Expert to delegate to
            user_query: User's question
            context: Context information

        Returns:
            Expert's response
        """
        import time

        start_time = time.time()

        try:
            self.logger.info(
                f"Manager '{self.name}' delegating to expert '{expert.name}'"
            )

            result = await expert.handle_request(user_query, context)

            # Track success
            response_time = time.time() - start_time
            self._track_delegation(success=True, response_time=response_time)

            return result

        except Exception as e:
            # Track failure
            response_time = time.time() - start_time
            self._track_delegation(success=False, response_time=response_time)

            self.logger.error(
                f"Delegation to expert '{expert.name}' failed: {e}"
            )

            return {
                "success": False,
                "error": f"Expert '{expert.name}' failed: {str(e)}",
                "expert": expert.name
            }

    def add_expert(self, expert: Any):
        """Add expert to this manager's team"""
        if expert.segment != self.segment:
            raise ValueError(
                f"Expert segment '{expert.segment}' does not match "
                f"manager segment '{self.segment}'"
            )

        self.experts.append(expert)
        self.logger.info(
            f"Added expert '{expert.name}' to manager '{self.name}'"
        )

    def remove_expert(self, expert_name: str):
        """Remove expert from this manager's team"""
        self.experts = [e for e in self.experts if e.name != expert_name]
        self.logger.info(
            f"Removed expert '{expert_name}' from manager '{self.name}'"
        )

    def get_expert_by_name(self, expert_name: str) -> Optional[Any]:
        """Get expert by name"""
        for expert in self.experts:
            if expert.name == expert_name:
                return expert
        return None

    def _track_delegation(self, success: bool, response_time: float):
        """Track delegation metrics"""
        self.requests_handled += 1

        # Update average response time
        if self.avg_response_time == 0:
            self.avg_response_time = response_time
        else:
            self.avg_response_time = (
                self.avg_response_time * 0.9 + response_time * 0.1
            )

        # Update delegation efficiency
        if success:
            self.delegation_efficiency = (
                self.delegation_efficiency * 0.95 + 1.0 * 0.05
            )
        else:
            self.delegation_efficiency = (
                self.delegation_efficiency * 0.95 + 0.0 * 0.05
            )

    def get_info(self) -> Dict[str, Any]:
        """Get manager information"""
        return {
            "name": self.name,
            "segment": self.segment,
            "description": self.description,
            "experts": [expert.get_info() for expert in self.experts],
            "metrics": {
                "requests_handled": self.requests_handled,
                "avg_response_time": self.avg_response_time,
                "delegation_efficiency": self.delegation_efficiency
            }
        }

    def get_status(self) -> Dict[str, Any]:
        """Get manager status summary"""
        return {
            "name": self.name,
            "segment": self.segment,
            "total_experts": len(self.experts),
            "expert_names": [expert.name for expert in self.experts],
            "metrics": {
                "requests_handled": self.requests_handled,
                "avg_response_time": self.avg_response_time,
                "delegation_efficiency": self.delegation_efficiency
            }
        }
