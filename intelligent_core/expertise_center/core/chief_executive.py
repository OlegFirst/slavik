"""
Chief Executive - Main Orchestrator for Expertise Center

Coordinates all domain experts (specialists, colleagues, analyzers).
"""

import logging
from typing import Dict, Any, Optional, List

from .expert_registry import ExpertRegistry
from .domain_loader import DomainLoader

logger = logging.getLogger(__name__)


class ChiefExecutive:
    """
    Chief Executive Orchestrator

    Responsibilities:
    - Load and manage domain plugins
    - Coordinate specialists, colleagues, analyzers
    - Route queries to appropriate experts
    - Integrate with ai-foundation (RAG, LLM, ML)
    """

    def __init__(self):
        self.registry = ExpertRegistry()
        self.domain_loader = DomainLoader()
        self.loaded_domains: List[str] = []

    async def initialize(self, domains: List[str] = None):
        """
        Initialize expertise center

        Args:
            domains: List of domains to load (default: ['bcm'])
        """
        if domains is None:
            domains = ['bcm']

        logger.info(f"Initializing Expertise Center with domains: {domains}")

        for domain in domains:
            await self.load_domain(domain)

        logger.info(f"Expertise Center initialized: {self.registry.list_all()}")

    async def load_domain(self, domain_name: str):
        """Load a domain plugin"""
        domain_config = await self.domain_loader.load_domain(domain_name)
        if domain_config:
            self.loaded_domains.append(domain_name)
            logger.info(f"Domain {domain_name} loaded successfully")
        else:
            logger.error(f"Failed to load domain: {domain_name}")

    async def query_specialist(
        self,
        specialist_id: str,
        context: Dict[str, Any],
        query: str
    ) -> Dict[str, Any]:
        """
        Query a strategic specialist

        Args:
            specialist_id: Specialist ID
            context: Query context
            query: Strategic question

        Returns:
            Strategic analysis
        """
        specialist = self.registry.get_specialist(specialist_id)
        if not specialist:
            logger.error(f"Specialist not found: {specialist_id}")
            return {"error": "Specialist not found"}

        return await specialist.analyze(context, query)

    async def ask_colleague(
        self,
        colleague_id: str,
        task: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Ask a tactical colleague

        Args:
            colleague_id: Colleague ID
            task: Task description
            context: Task context

        Returns:
            Task assistance
        """
        colleague = self.registry.get_colleague(colleague_id)
        if not colleague:
            logger.error(f"Colleague not found: {colleague_id}")
            return {"error": "Colleague not found"}

        return await colleague.assist(task, context)

    async def run_analyzer(
        self,
        analyzer_id: str,
        data: Dict[str, Any],
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Run heavy analyzer

        Args:
            analyzer_id: Analyzer ID
            data: Data to analyze
            config: Analysis config

        Returns:
            Analysis results
        """
        analyzer = self.registry.get_analyzer(analyzer_id)
        if not analyzer:
            logger.error(f"Analyzer not found: {analyzer_id}")
            return {"error": "Analyzer not found"}

        return await analyzer.analyze(data, config)

    async def get_domain_capabilities(self, domain: str) -> Dict[str, Any]:
        """Get all capabilities for a domain"""
        experts = self.registry.get_domain_experts(domain)

        capabilities = {
            "domain": domain,
            "specialists": [
                {
                    "id": s.specialist_id,
                    "name": s.name,
                    "capabilities": await s.get_capabilities()
                }
                for s in experts.get("specialists", []) if s
            ],
            "colleagues": [
                {
                    "id": c.colleague_id,
                    "name": c.name,
                    "specialty": c.specialty,
                    "capabilities": await c.get_capabilities()
                }
                for c in experts.get("colleagues", []) if c
            ],
            "analyzers": [
                {
                    "id": a.analyzer_id,
                    "name": a.name,
                    "type": a.analysis_type,
                }
                for a in experts.get("analyzers", []) if a
            ],
        }

        return capabilities

    def get_status(self) -> Dict[str, Any]:
        """Get expertise center status"""
        return {
            "loaded_domains": self.loaded_domains,
            "experts": self.registry.list_all(),
        }
