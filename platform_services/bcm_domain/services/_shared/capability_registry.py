"""
Capability Registry

Tracks service capabilities, versions, and expertise levels.
Enables intelligent capability matching for event routing.
"""

import logging
from typing import Dict, Any, Optional, List, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import re

logger = logging.getLogger(__name__)


class ExpertiseLevel(Enum):
    """Service expertise level for a capability"""
    EXPERT = "expert"          # Primary handler
    PROFICIENT = "proficient"  # Can handle well
    CAPABLE = "capable"        # Can handle
    LEARNING = "learning"      # Learning/experimental


@dataclass
class Capability:
    """
    Service capability definition.

    Represents a specific capability that a service can provide.
    """
    name: str                          # e.g., "bia.assessment"
    service: str                       # Service that provides it
    version: str = "1.0.0"            # Capability version
    expertise: ExpertiseLevel = ExpertiseLevel.CAPABLE
    enabled: bool = True              # Can be disabled
    description: str = ""
    tags: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)
    registered_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class CapabilityMatch:
    """
    Result of capability matching.

    Contains the matched capability and matching score.
    """
    capability: Capability
    score: float                       # 0.0 to 1.0
    reason: str = ""                   # Why it matched
    matched_tags: Set[str] = field(default_factory=set)


class CapabilityRegistry:
    """
    Registry for service capabilities.

    Tracks what each service can do and helps route events
    to the most appropriate service.

    Features:
    - Capability registration and discovery
    - Pattern matching (e.g., "bia.*" matches "bia.assessment")
    - Tag-based matching
    - Expertise-based ranking
    - Version compatibility
    - A/B testing support

    Usage:
        registry = CapabilityRegistry()

        # Register capabilities
        registry.register(Capability(
            name="bia.assessment",
            service="bia",
            expertise=ExpertiseLevel.EXPERT
        ))

        # Find capabilities
        matches = registry.find_capabilities("bia.assessment.completed")
    """

    def __init__(self):
        """Initialize capability registry"""
        self._capabilities: Dict[str, List[Capability]] = {}  # name -> [capabilities]
        self._service_capabilities: Dict[str, Set[str]] = {}  # service -> {capability names}
        self._tags_index: Dict[str, Set[str]] = {}            # tag -> {capability names}

        logger.info("CapabilityRegistry initialized")

    def register(self, capability: Capability):
        """
        Register a capability.

        Args:
            capability: Capability to register
        """
        # Add to main registry
        if capability.name not in self._capabilities:
            self._capabilities[capability.name] = []
        self._capabilities[capability.name].append(capability)

        # Index by service
        if capability.service not in self._service_capabilities:
            self._service_capabilities[capability.service] = set()
        self._service_capabilities[capability.service].add(capability.name)

        # Index by tags
        for tag in capability.tags:
            if tag not in self._tags_index:
                self._tags_index[tag] = set()
            self._tags_index[tag].add(capability.name)

        logger.info(f"Registered capability: {capability.name} for service {capability.service}")

    def unregister(self, capability_name: str, service: str):
        """
        Unregister a capability.

        Args:
            capability_name: Name of capability
            service: Service name
        """
        if capability_name in self._capabilities:
            self._capabilities[capability_name] = [
                c for c in self._capabilities[capability_name]
                if c.service != service
            ]

            if not self._capabilities[capability_name]:
                del self._capabilities[capability_name]

        if service in self._service_capabilities:
            self._service_capabilities[service].discard(capability_name)

        logger.info(f"Unregistered capability: {capability_name} for service {service}")

    def get_capability(self, capability_name: str, service: Optional[str] = None) -> Optional[Capability]:
        """
        Get a specific capability.

        Args:
            capability_name: Name of capability
            service: Optional service filter

        Returns:
            Capability or None
        """
        if capability_name not in self._capabilities:
            return None

        capabilities = self._capabilities[capability_name]

        if service:
            for cap in capabilities:
                if cap.service == service:
                    return cap
            return None

        # Return highest expertise
        return max(capabilities, key=lambda c: self._expertise_score(c.expertise))

    def find_capabilities(
        self,
        pattern: str,
        tags: Optional[Set[str]] = None,
        min_expertise: Optional[ExpertiseLevel] = None,
        enabled_only: bool = True
    ) -> List[CapabilityMatch]:
        """
        Find capabilities matching pattern and filters.

        Args:
            pattern: Capability name pattern (supports wildcards)
            tags: Optional tags to match
            min_expertise: Minimum expertise level
            enabled_only: Only return enabled capabilities

        Returns:
            List of CapabilityMatch objects, sorted by score
        """
        matches = []

        # Find matching capabilities
        for cap_name, capabilities in self._capabilities.items():
            # Pattern matching
            if not self._match_pattern(cap_name, pattern):
                continue

            for cap in capabilities:
                # Filter enabled
                if enabled_only and not cap.enabled:
                    continue

                # Filter expertise
                if min_expertise and self._expertise_score(cap.expertise) < self._expertise_score(min_expertise):
                    continue

                # Calculate match score
                score, reason, matched_tags = self._calculate_match_score(cap, pattern, tags)

                if score > 0:
                    matches.append(CapabilityMatch(
                        capability=cap,
                        score=score,
                        reason=reason,
                        matched_tags=matched_tags
                    ))

        # Sort by score (highest first)
        matches.sort(key=lambda m: m.score, reverse=True)

        return matches

    def list_capabilities(self, service: Optional[str] = None) -> List[str]:
        """
        List all capability names.

        Args:
            service: Optional service filter

        Returns:
            List of capability names
        """
        if service:
            return sorted(self._service_capabilities.get(service, set()))
        return sorted(self._capabilities.keys())

    def get_services_for_capability(self, capability_name: str) -> List[str]:
        """
        Get all services that provide a capability.

        Args:
            capability_name: Capability name

        Returns:
            List of service names
        """
        if capability_name not in self._capabilities:
            return []

        return [cap.service for cap in self._capabilities[capability_name]]

    def get_service_capabilities(self, service: str) -> List[Capability]:
        """
        Get all capabilities for a service.

        Args:
            service: Service name

        Returns:
            List of Capability objects
        """
        if service not in self._service_capabilities:
            return []

        capabilities = []
        for cap_name in self._service_capabilities[service]:
            caps = self._capabilities.get(cap_name, [])
            capabilities.extend([c for c in caps if c.service == service])

        return capabilities

    def find_by_tag(self, tag: str) -> List[Capability]:
        """
        Find capabilities by tag.

        Args:
            tag: Tag to search for

        Returns:
            List of Capability objects
        """
        if tag not in self._tags_index:
            return []

        capabilities = []
        for cap_name in self._tags_index[tag]:
            capabilities.extend(self._capabilities.get(cap_name, []))

        return capabilities

    def enable_capability(self, capability_name: str, service: str):
        """Enable a capability"""
        cap = self.get_capability(capability_name, service)
        if cap:
            cap.enabled = True
            logger.info(f"Enabled capability: {capability_name} for {service}")

    def disable_capability(self, capability_name: str, service: str):
        """Disable a capability"""
        cap = self.get_capability(capability_name, service)
        if cap:
            cap.enabled = False
            logger.info(f"Disabled capability: {capability_name} for {service}")

    # Private methods

    def _match_pattern(self, capability_name: str, pattern: str) -> bool:
        """
        Match capability name against pattern.

        Supports:
        - Exact match: "bia.assessment" == "bia.assessment"
        - Wildcard: "bia.*" matches "bia.assessment", "bia.analysis"
        - Prefix: "bia" matches "bia.assessment"
        """
        # Exact match
        if capability_name == pattern:
            return True

        # Wildcard pattern
        if "*" in pattern:
            regex = pattern.replace(".", r"\.").replace("*", ".*")
            return bool(re.match(f"^{regex}$", capability_name))

        # Prefix match
        if capability_name.startswith(pattern + "."):
            return True

        return False

    def _calculate_match_score(
        self,
        capability: Capability,
        pattern: str,
        tags: Optional[Set[str]] = None
    ) -> tuple[float, str, Set[str]]:
        """
        Calculate match score for capability.

        Returns:
            (score, reason, matched_tags)
        """
        score = 0.0
        reasons = []
        matched_tags = set()

        # Base score from pattern match
        if capability.name == pattern:
            score += 1.0
            reasons.append("exact match")
        elif capability.name.startswith(pattern.replace("*", "")):
            score += 0.8
            reasons.append("prefix match")
        else:
            score += 0.5
            reasons.append("pattern match")

        # Expertise bonus
        expertise_score = self._expertise_score(capability.expertise)
        score += expertise_score * 0.3
        reasons.append(f"{capability.expertise.value} expertise")

        # Tag matching bonus
        if tags:
            common_tags = capability.tags & tags
            if common_tags:
                tag_bonus = len(common_tags) / len(tags) * 0.5
                score += tag_bonus
                matched_tags = common_tags
                reasons.append(f"matched {len(common_tags)} tags")

        # Enabled bonus
        if capability.enabled:
            score += 0.1
        else:
            score *= 0.5  # Penalty for disabled

        return score, ", ".join(reasons), matched_tags

    def _expertise_score(self, expertise: ExpertiseLevel) -> float:
        """Convert expertise level to numeric score"""
        scores = {
            ExpertiseLevel.EXPERT: 1.0,
            ExpertiseLevel.PROFICIENT: 0.8,
            ExpertiseLevel.CAPABLE: 0.6,
            ExpertiseLevel.LEARNING: 0.3
        }
        return scores.get(expertise, 0.5)


# Built-in capability definitions for common patterns

BCM_CAPABILITIES = {
    "bia": [
        "bia.assessment.create",
        "bia.assessment.update",
        "bia.assessment.complete",
        "bia.process.create",
        "bia.process.analyze",
        "bia.criticality.assess",
        "bia.rto.calculate",
        "bia.dependencies.map"
    ],
    "risk": [
        "risk.assessment.create",
        "risk.assessment.analyze",
        "risk.scenario.evaluate",
        "risk.mitigation.plan",
        "risk.monitoring.track"
    ],
    "compliance": [
        "compliance.assessment.create",
        "compliance.gap.analyze",
        "compliance.evidence.collect",
        "compliance.audit.prepare"
    ],
    "response": [
        "response.incident.create",
        "response.incident.activate",
        "response.team.notify",
        "response.action.track"
    ],
    "plans": [
        "plans.create",
        "plans.review",
        "plans.approve",
        "plans.test"
    ]
}
