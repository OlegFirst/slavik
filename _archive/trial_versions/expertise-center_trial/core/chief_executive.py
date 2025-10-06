"""
Chief Executive AI (Expertise Center version)

AI Orchestrator - routes requests to appropriate domain experts.
Works as Layer 2 component that manages domain expertise.
"""

from typing import Dict, Any, Optional, List
import logging
from enum import Enum

logger = logging.getLogger(__name__)


class DomainType(str, Enum):
    """Domain types for classification"""
    BCM = "bcm"
    FINANCE = "finance"
    HR = "hr"
    OPERATIONS = "operations"
    UNKNOWN = "unknown"


class ChiefExecutiveAI:
    """
    AI Orchestrator for Expertise Center

    Responsibilities:
    1. Analyze user requests and determine domain + expertise
    2. Route to appropriate expert via expert_registry
    3. Delegate execution to domain experts
    4. Monitor and learn from interactions

    This is the main entry point for all AI expertise requests.
    """

    def __init__(
        self,
        expert_registry,
        domain_loader,
        llm_client: Optional[Any] = None
    ):
        """
        Initialize Chief Executive AI

        Args:
            expert_registry: ExpertRegistry instance
            domain_loader: DomainLoader instance
            llm_client: Optional LLM client for intent analysis
        """
        self.expert_registry = expert_registry
        self.domain_loader = domain_loader
        self.llm_client = llm_client
        self.logger = logger

        # Metrics
        self.total_requests = 0
        self.successful_routes = 0
        self.failed_routes = 0

        # Domain detection keywords
        self.domain_keywords = {
            DomainType.BCM: [
                "bia", "risk", "business impact", "recovery", "rto", "rpo",
                "incident", "disaster", "continuity", "bcm", "crisis",
                "exercise", "test", "plan", "business continuity",
                "resilience", "dependency", "threat", "vulnerability"
            ],
            DomainType.FINANCE: [
                "financial", "budget", "cost", "revenue", "profit",
                "accounting", "audit", "invoice", "payment", "transaction"
            ],
            DomainType.HR: [
                "employee", "staff", "hiring", "recruitment", "training",
                "performance", "payroll", "hr", "human resources"
            ],
            DomainType.OPERATIONS: [
                "operations", "process", "workflow", "efficiency",
                "optimization", "automation", "production"
            ]
        }

        # Expertise keywords (BCM-specific for now)
        self.expertise_keywords = {
            "bia": ["bia", "business impact", "criticality", "rto", "rpo", "mtd"],
            "risk": ["risk", "threat", "vulnerability", "likelihood", "impact", "fair"],
            "compliance": ["compliance", "audit", "standard", "iso", "regulation", "gap"],
            "response": ["response", "incident", "crisis", "emergency", "disaster"],
            "planning": ["planning", "strategy", "roadmap", "timeline"],
            "governance": ["governance", "policy", "framework", "oversight"],
            "learning": ["learning", "improvement", "lesson", "optimization"],
            "documents": ["document", "policy", "procedure", "template"],
            "validation": ["validation", "test", "exercise", "verification"]
        }

    async def handle_request(
        self,
        user_query: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Main entry point - handle user request

        Args:
            user_query: User's question or request
            context: Context information (user_id, organization, etc.)

        Returns:
            Response from appropriate expert
        """
        import time
        start_time = time.time()

        try:
            self.logger.info(f"Chief Executive AI processing: {user_query[:100]}...")
            self.total_requests += 1

            # Step 1: Detect domain and expertise
            domain, expertise, confidence = await self._detect_domain_expertise(
                user_query,
                context
            )

            self.logger.info(
                f"Detected: domain={domain}, expertise={expertise}, "
                f"confidence={confidence:.2f}"
            )

            # Step 2: Get expert from registry
            expert_class = self.expert_registry.get_expert(domain, expertise)

            if not expert_class:
                self.failed_routes += 1
                return await self._handle_no_expert(
                    user_query,
                    context,
                    domain,
                    expertise
                )

            # Step 3: Instantiate and delegate to expert
            expert_instance = self._instantiate_expert(
                expert_class,
                domain,
                expertise,
                context
            )

            result = await expert_instance.handle(user_query, context)

            # Step 4: Track success
            self.successful_routes += 1
            response_time = time.time() - start_time

            # Add metadata
            result["metadata"] = result.get("metadata", {})
            result["metadata"].update({
                "domain": domain,
                "expertise": expertise,
                "confidence": confidence,
                "response_time": response_time,
                "orchestrator": "ChiefExecutiveAI"
            })

            return result

        except Exception as e:
            self.failed_routes += 1
            response_time = time.time() - start_time

            self.logger.error(f"Chief Executive AI failed: {e}", exc_info=True)

            return {
                "success": False,
                "error": f"Request processing failed: {str(e)}",
                "metadata": {
                    "response_time": response_time,
                    "orchestrator": "ChiefExecutiveAI"
                }
            }

    async def _detect_domain_expertise(
        self,
        user_query: str,
        context: Dict[str, Any]
    ) -> tuple[str, str, float]:
        """
        Detect domain and expertise from user query

        Args:
            user_query: User's question
            context: Context information

        Returns:
            (domain, expertise, confidence)
        """
        query_lower = user_query.lower()

        # Step 1: Detect domain
        domain_scores = {}
        for domain, keywords in self.domain_keywords.items():
            score = sum(1 for kw in keywords if kw in query_lower)
            if score > 0:
                domain_scores[domain] = score

        # Default to BCM if no domain detected
        if not domain_scores:
            detected_domain = DomainType.BCM.value
            domain_confidence = 0.5
        else:
            detected_domain = max(domain_scores, key=domain_scores.get).value
            total_matches = sum(domain_scores.values())
            domain_confidence = domain_scores[detected_domain] / total_matches

        # Step 2: Detect expertise
        expertise_scores = {}
        for expertise, keywords in self.expertise_keywords.items():
            score = sum(1 for kw in keywords if kw in query_lower)
            if score > 0:
                expertise_scores[expertise] = score

        # Default expertise based on domain
        if not expertise_scores:
            # Use LLM if available
            if self.llm_client:
                detected_expertise = await self._llm_detect_expertise(
                    user_query,
                    detected_domain,
                    context
                )
                expertise_confidence = 0.7
            else:
                # Default to first available expertise in domain
                domain_experts = self.expert_registry.get_domain_experts(detected_domain)
                if domain_experts:
                    detected_expertise = domain_experts[0].expertise
                    expertise_confidence = 0.5
                else:
                    # Fallback to bia
                    detected_expertise = "bia"
                    expertise_confidence = 0.3
        else:
            detected_expertise = max(expertise_scores, key=expertise_scores.get)
            total_matches = sum(expertise_scores.values())
            expertise_confidence = expertise_scores[detected_expertise] / total_matches

        # Combined confidence
        overall_confidence = (domain_confidence + expertise_confidence) / 2

        return detected_domain, detected_expertise, overall_confidence

    async def _llm_detect_expertise(
        self,
        user_query: str,
        domain: str,
        context: Dict[str, Any]
    ) -> str:
        """Use LLM to detect expertise when keywords don't match"""

        # Get available expertise for domain
        domain_experts = self.expert_registry.get_domain_experts(domain)
        available_expertise = [exp.expertise for exp in domain_experts]

        if not available_expertise:
            return "bia"  # Default

        system_prompt = f"""You are analyzing user requests to determine expertise area.

Domain: {domain}
Available expertise areas: {', '.join(available_expertise)}

Respond with ONLY the expertise area name.
"""

        user_prompt = f"User query: {user_query}\n\nWhich expertise area?"

        try:
            response = await self.llm_client.query(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.1
            )

            detected = response.strip().lower()

            # Validate it's in available expertise
            if detected in available_expertise:
                return detected
            else:
                # Return first available
                return available_expertise[0]

        except Exception as e:
            self.logger.error(f"LLM expertise detection failed: {e}")
            return available_expertise[0] if available_expertise else "bia"

    def _instantiate_expert(
        self,
        expert_class,
        domain: str,
        expertise: str,
        context: Dict[str, Any]
    ):
        """
        Instantiate expert with proper dependencies

        Args:
            expert_class: Expert class to instantiate
            domain: Domain name
            expertise: Expertise area
            context: Request context

        Returns:
            Expert instance
        """
        # Get domain info for dependencies
        domain_info = self.domain_loader.get_domain_info(domain)

        # Prepare initialization kwargs
        init_kwargs = {
            "domain": domain,
            "expertise": expertise,
            "context": context
        }

        # Add domain-specific dependencies if available
        if domain_info:
            init_kwargs["tools"] = domain_info.get("tools", {})
            init_kwargs["organs"] = domain_info.get("organs", {})
            init_kwargs["knowledge"] = domain_info.get("knowledge", {})

        # Try to instantiate with various signatures
        try:
            # Try full kwargs
            return expert_class(**init_kwargs)
        except TypeError:
            try:
                # Try minimal kwargs
                return expert_class(domain=domain, expertise=expertise)
            except TypeError:
                try:
                    # Try no kwargs
                    return expert_class()
                except TypeError as e:
                    self.logger.error(
                        f"Cannot instantiate expert {expert_class.__name__}: {e}"
                    )
                    raise

    async def _handle_no_expert(
        self,
        user_query: str,
        context: Dict[str, Any],
        domain: str,
        expertise: str
    ) -> Dict[str, Any]:
        """
        Handle case when no expert is found

        Args:
            user_query: User query
            context: Context
            domain: Detected domain
            expertise: Detected expertise

        Returns:
            Error response with suggestions
        """
        self.logger.warning(
            f"No expert found for domain={domain}, expertise={expertise}"
        )

        # Try to find similar experts
        suggestions = self.expert_registry.search_experts(
            query=user_query,
            domain=domain
        )

        available_domains = self.expert_registry.list_domains()

        return {
            "success": False,
            "error": f"No expert available for {domain}.{expertise}",
            "suggestions": {
                "detected_domain": domain,
                "detected_expertise": expertise,
                "available_domains": available_domains,
                "similar_experts": [
                    {
                        "domain": exp.domain,
                        "expertise": exp.expertise,
                        "description": exp.description
                    }
                    for exp in suggestions[:3]  # Top 3 suggestions
                ],
                "recommendation": (
                    f"Try rephrasing your question or specify one of: "
                    f"{', '.join(available_domains)}"
                )
            }
        }

    def get_status(self) -> Dict[str, Any]:
        """Get Chief Executive AI status"""
        success_rate = (
            self.successful_routes / self.total_requests
            if self.total_requests > 0
            else 0.0
        )

        return {
            "name": "Chief Executive AI",
            "role": "AI Orchestrator for Expertise Center",
            "metrics": {
                "total_requests": self.total_requests,
                "successful_routes": self.successful_routes,
                "failed_routes": self.failed_routes,
                "success_rate": success_rate
            },
            "registry_stats": self.expert_registry.get_stats(),
            "loaded_domains": self.domain_loader.get_loaded_domains()
        }

    def reload_domains(self):
        """Reload all domains (useful for development)"""
        self.logger.info("Reloading all domains...")
        return self.domain_loader.load_all_domains()
