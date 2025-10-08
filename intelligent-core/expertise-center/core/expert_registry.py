"""
Expert Registry

Manages all experts (specialists, colleagues, analyzers) across domains.
"""

from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)


class ExpertRegistry:
    """
    Central registry for all AI experts

    Maintains:
    - Specialists (strategic experts)
    - Colleagues (tactical assistants)
    - Analyzers (heavy AI)
    """

    def __init__(self):
        self.specialists: Dict[str, Any] = {}
        self.colleagues: Dict[str, Any] = {}
        self.analyzers: Dict[str, Any] = {}
        self.domains: Dict[str, List[str]] = {}

    def register_specialist(
        self,
        specialist_id: str,
        specialist: Any,
        domain: str = "bcm"
    ):
        """Register a specialist"""
        self.specialists[specialist_id] = specialist
        if domain not in self.domains:
            self.domains[domain] = []
        if specialist_id not in self.domains[domain]:
            self.domains[domain].append(specialist_id)
        logger.info(f"Registered specialist: {specialist_id} ({domain})")

    def register_colleague(
        self,
        colleague_id: str,
        colleague: Any,
        domain: str = "bcm"
    ):
        """Register a colleague"""
        self.colleagues[colleague_id] = colleague
        if domain not in self.domains:
            self.domains[domain] = []
        if colleague_id not in self.domains[domain]:
            self.domains[domain].append(colleague_id)
        logger.info(f"Registered colleague: {colleague_id} ({domain})")

    def register_analyzer(
        self,
        analyzer_id: str,
        analyzer: Any,
        domain: str = "bcm"
    ):
        """Register an analyzer"""
        self.analyzers[analyzer_id] = analyzer
        if domain not in self.domains:
            self.domains[domain] = []
        if analyzer_id not in self.domains[domain]:
            self.domains[domain].append(analyzer_id)
        logger.info(f"Registered analyzer: {analyzer_id} ({domain})")

    def get_specialist(self, specialist_id: str) -> Optional[Any]:
        """Get specialist by ID"""
        return self.specialists.get(specialist_id)

    def get_colleague(self, colleague_id: str) -> Optional[Any]:
        """Get colleague by ID"""
        return self.colleagues.get(colleague_id)

    def get_analyzer(self, analyzer_id: str) -> Optional[Any]:
        """Get analyzer by ID"""
        return self.analyzers.get(analyzer_id)

    def get_domain_experts(self, domain: str) -> Dict[str, List[Any]]:
        """Get all experts for a domain"""
        expert_ids = self.domains.get(domain, [])
        return {
            "specialists": [self.specialists.get(eid) for eid in expert_ids if eid in self.specialists],
            "colleagues": [self.colleagues.get(eid) for eid in expert_ids if eid in self.colleagues],
            "analyzers": [self.analyzers.get(eid) for eid in expert_ids if eid in self.analyzers],
        }

    def list_all(self) -> Dict[str, int]:
        """List all registered experts"""
        return {
            "specialists": len(self.specialists),
            "colleagues": len(self.colleagues),
            "analyzers": len(self.analyzers),
            "domains": len(self.domains),
        }
