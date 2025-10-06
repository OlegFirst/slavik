"""
Expert Registry

Central registry for all domain experts across the platform.
Manages expert registration, discovery, and retrieval.
"""

from typing import Dict, Any, Optional, List, Type
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ExpertInfo:
    """Expert metadata"""
    domain: str
    expertise: str
    expert_class: Type
    capabilities: List[str]
    tools: List[str]
    description: str


class ExpertRegistry:
    """
    Central registry for all experts

    Format: {domain}.{expertise} → ExpertInfo

    Examples:
        "bcm.bia" → BIASpecialist
        "bcm.risk" → RiskAnalyst
        "finance.audit" → FinanceAuditor
    """

    def __init__(self):
        self.experts: Dict[str, ExpertInfo] = {}
        self.domains: Dict[str, List[str]] = {}  # domain → [expertise types]
        self.logger = logger

    def register_expert(
        self,
        domain: str,
        expertise: str,
        expert_class: Type,
        capabilities: Optional[List[str]] = None,
        tools: Optional[List[str]] = None,
        description: str = ""
    ):
        """
        Register a domain expert

        Args:
            domain: Domain name (e.g., "bcm", "finance")
            expertise: Expertise area (e.g., "bia", "risk")
            expert_class: Expert class
            capabilities: List of capabilities
            tools: List of tools expert can use
            description: Expert description
        """
        key = f"{domain}.{expertise}"

        expert_info = ExpertInfo(
            domain=domain,
            expertise=expertise,
            expert_class=expert_class,
            capabilities=capabilities or [],
            tools=tools or [],
            description=description
        )

        self.experts[key] = expert_info

        # Track domain experts
        if domain not in self.domains:
            self.domains[domain] = []
        if expertise not in self.domains[domain]:
            self.domains[domain].append(expertise)

        self.logger.info(
            f"Registered expert: {key} with {len(capabilities or [])} capabilities"
        )

    def get_expert(
        self,
        domain: str,
        expertise: str
    ) -> Optional[Type]:
        """
        Get expert class by domain and expertise

        Args:
            domain: Domain name
            expertise: Expertise area

        Returns:
            Expert class or None
        """
        key = f"{domain}.{expertise}"
        expert_info = self.experts.get(key)

        if expert_info:
            return expert_info.expert_class

        self.logger.warning(f"Expert not found: {key}")
        return None

    def get_expert_info(
        self,
        domain: str,
        expertise: str
    ) -> Optional[ExpertInfo]:
        """Get full expert information"""
        key = f"{domain}.{expertise}"
        return self.experts.get(key)

    def find_experts_by_capability(
        self,
        capability: str
    ) -> List[ExpertInfo]:
        """
        Find all experts with a specific capability

        Args:
            capability: Capability to search for

        Returns:
            List of matching experts
        """
        matching = []

        for expert_info in self.experts.values():
            if capability.lower() in [c.lower() for c in expert_info.capabilities]:
                matching.append(expert_info)

        return matching

    def get_domain_experts(
        self,
        domain: str
    ) -> List[ExpertInfo]:
        """
        Get all experts for a domain

        Args:
            domain: Domain name

        Returns:
            List of domain experts
        """
        matching = []

        for key, expert_info in self.experts.items():
            if expert_info.domain == domain:
                matching.append(expert_info)

        return matching

    def list_domains(self) -> List[str]:
        """List all registered domains"""
        return list(self.domains.keys())

    def list_expertise(self, domain: str) -> List[str]:
        """List all expertise areas for a domain"""
        return self.domains.get(domain, [])

    def get_stats(self) -> Dict[str, Any]:
        """Get registry statistics"""
        return {
            "total_experts": len(self.experts),
            "total_domains": len(self.domains),
            "domains": {
                domain: {
                    "expertise_count": len(expertise_list),
                    "expertise_areas": expertise_list
                }
                for domain, expertise_list in self.domains.items()
            }
        }

    def search_experts(
        self,
        query: str,
        domain: Optional[str] = None
    ) -> List[ExpertInfo]:
        """
        Search experts by query string

        Args:
            query: Search query
            domain: Optional domain filter

        Returns:
            Matching experts
        """
        query_lower = query.lower()
        matching = []

        for expert_info in self.experts.values():
            # Apply domain filter if provided
            if domain and expert_info.domain != domain:
                continue

            # Search in expertise, capabilities, description
            if (
                query_lower in expert_info.expertise.lower() or
                query_lower in expert_info.description.lower() or
                any(query_lower in cap.lower() for cap in expert_info.capabilities)
            ):
                matching.append(expert_info)

        return matching

    def unregister_expert(
        self,
        domain: str,
        expertise: str
    ):
        """
        Unregister an expert

        Args:
            domain: Domain name
            expertise: Expertise area
        """
        key = f"{domain}.{expertise}"

        if key in self.experts:
            del self.experts[key]

            # Update domains tracking
            if domain in self.domains:
                if expertise in self.domains[domain]:
                    self.domains[domain].remove(expertise)

                # Remove domain if no experts left
                if not self.domains[domain]:
                    del self.domains[domain]

            self.logger.info(f"Unregistered expert: {key}")
        else:
            self.logger.warning(f"Cannot unregister - expert not found: {key}")

    def clear(self):
        """Clear all registered experts"""
        self.experts.clear()
        self.domains.clear()
        self.logger.info("Cleared all registered experts")
