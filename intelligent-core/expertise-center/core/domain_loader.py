"""
Domain Loader

Loads domain plugins dynamically.
"""

import importlib
import logging
from typing import Dict, Any, List
from pathlib import Path

logger = logging.getLogger(__name__)


class DomainLoader:
    """
    Loads domain plugins from domains/ directory

    Each domain is a plugin that provides:
    - Specialists (strategic experts)
    - Colleagues (tactical assistants)
    - Analyzers (heavy AI)
    - Knowledge (domain-specific knowledge)
    - Services config
    """

    def __init__(self, domains_path: str = "intelligent-core/expertise-center/domains"):
        self.domains_path = Path(domains_path)
        self.loaded_domains: Dict[str, Any] = {}

    async def load_domain(self, domain_name: str) -> Dict[str, Any]:
        """
        Load a domain plugin

        Args:
            domain_name: Domain to load (e.g., 'bcm', 'hr', 'finance')

        Returns:
            Domain configuration
        """
        logger.info(f"Loading domain: {domain_name}")

        domain_path = self.domains_path / domain_name
        if not domain_path.exists():
            logger.error(f"Domain not found: {domain_name}")
            return {}

        # Import domain module
        try:
            module_name = f"intelligent_core.expertise_center.domains.{domain_name}"
            domain_module = importlib.import_module(module_name)

            # Get domain configuration
            domain_config = {
                "name": domain_name,
                "module": domain_module,
                "specialists": self._load_experts(domain_path / "specialists"),
                "colleagues": self._load_experts(domain_path / "colleagues"),
                "analyzers": self._load_experts(domain_path / "analyzers"),
            }

            self.loaded_domains[domain_name] = domain_config
            logger.info(f"Domain loaded: {domain_name}")
            return domain_config

        except Exception as e:
            logger.error(f"Failed to load domain {domain_name}: {e}")
            return {}

    def _load_experts(self, experts_path: Path) -> List[str]:
        """Load expert files from directory"""
        if not experts_path.exists():
            return []

        expert_files = [
            f.stem for f in experts_path.glob("*.py")
            if f.stem != "__init__" and not f.stem.startswith("_")
        ]
        return expert_files

    def get_loaded_domains(self) -> List[str]:
        """Get list of loaded domains"""
        return list(self.loaded_domains.keys())

    def get_domain_config(self, domain_name: str) -> Dict[str, Any]:
        """Get configuration for a loaded domain"""
        return self.loaded_domains.get(domain_name, {})
