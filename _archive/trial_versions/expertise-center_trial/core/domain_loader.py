"""
Domain Loader

Dynamically loads domain plugins from the domains/ directory.
Discovers and registers experts, tools, organs, and knowledge sources.
"""

import os
import importlib.util
import inspect
from typing import Dict, Any, List, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class DomainLoader:
    """
    Dynamically loads domain plugins

    Scans domains/ directory and loads:
    - Experts from domains/{domain}/experts/
    - Tools from domains/{domain}/tools/
    - Organs from domains/{domain}/organs/
    - Knowledge from domains/{domain}/knowledge/
    """

    def __init__(
        self,
        expert_registry,
        domains_path: Optional[str] = None
    ):
        """
        Initialize Domain Loader

        Args:
            expert_registry: ExpertRegistry instance
            domains_path: Path to domains directory (auto-detected if None)
        """
        self.expert_registry = expert_registry
        self.logger = logger

        # Auto-detect domains path
        if domains_path is None:
            current_dir = Path(__file__).parent.parent
            self.domains_path = current_dir / "domains"
        else:
            self.domains_path = Path(domains_path)

        self.loaded_domains: Dict[str, Dict[str, Any]] = {}

    def discover_domains(self) -> List[str]:
        """
        Discover all available domains

        Returns:
            List of domain names
        """
        if not self.domains_path.exists():
            self.logger.warning(f"Domains path does not exist: {self.domains_path}")
            return []

        domains = []

        for item in self.domains_path.iterdir():
            if item.is_dir() and not item.name.startswith('_'):
                domains.append(item.name)

        self.logger.info(f"Discovered {len(domains)} domains: {domains}")
        return domains

    def load_domain(
        self,
        domain_name: str
    ) -> Dict[str, Any]:
        """
        Load a domain plugin

        Args:
            domain_name: Name of domain to load (e.g., "bcm")

        Returns:
            Domain metadata with loaded components
        """
        domain_path = self.domains_path / domain_name

        if not domain_path.exists():
            raise ValueError(f"Domain not found: {domain_name}")

        self.logger.info(f"Loading domain: {domain_name}")

        domain_info = {
            "name": domain_name,
            "path": str(domain_path),
            "experts": {},
            "tools": {},
            "organs": {},
            "knowledge": {}
        }

        # Load experts
        experts_path = domain_path / "experts"
        if experts_path.exists():
            domain_info["experts"] = self._load_experts(
                domain_name,
                experts_path
            )

        # Load tools
        tools_path = domain_path / "tools"
        if tools_path.exists():
            domain_info["tools"] = self._load_tools(
                domain_name,
                tools_path
            )

        # Load organs
        organs_path = domain_path / "organs"
        if organs_path.exists():
            domain_info["organs"] = self._load_organs(
                domain_name,
                organs_path
            )

        # Load knowledge
        knowledge_path = domain_path / "knowledge"
        if knowledge_path.exists():
            domain_info["knowledge"] = self._load_knowledge(
                domain_name,
                knowledge_path
            )

        # Store loaded domain
        self.loaded_domains[domain_name] = domain_info

        self.logger.info(
            f"Loaded domain '{domain_name}': "
            f"{len(domain_info['experts'])} experts, "
            f"{len(domain_info['tools'])} tools, "
            f"{len(domain_info['organs'])} organs"
        )

        return domain_info

    def _load_experts(
        self,
        domain_name: str,
        experts_path: Path
    ) -> Dict[str, Any]:
        """Load experts from domain/experts/"""
        experts = {}

        for py_file in experts_path.glob("*.py"):
            if py_file.name.startswith('_'):
                continue

            try:
                # Import module
                module_name = f"expertise_center.domains.{domain_name}.experts.{py_file.stem}"
                module = self._import_module(module_name, py_file)

                # Find expert classes
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    # Skip imported classes
                    if obj.__module__ != module.__name__:
                        continue

                    # Check if it's an expert (has handle method)
                    if hasattr(obj, 'handle'):
                        expertise_name = py_file.stem
                        experts[expertise_name] = obj

                        # Register with expert registry
                        capabilities = getattr(obj, 'capabilities', [])
                        tools = getattr(obj, 'tools', [])
                        description = getattr(obj, '__doc__', '') or ''

                        self.expert_registry.register_expert(
                            domain=domain_name,
                            expertise=expertise_name,
                            expert_class=obj,
                            capabilities=capabilities,
                            tools=tools,
                            description=description.strip()
                        )

                        self.logger.info(
                            f"Loaded expert: {domain_name}.{expertise_name}"
                        )

            except Exception as e:
                self.logger.error(
                    f"Failed to load expert from {py_file}: {e}"
                )

        return experts

    def _load_tools(
        self,
        domain_name: str,
        tools_path: Path
    ) -> Dict[str, Any]:
        """Load tools from domain/tools/"""
        tools = {}

        for py_file in tools_path.glob("*.py"):
            if py_file.name.startswith('_'):
                continue

            try:
                module_name = f"expertise_center.domains.{domain_name}.tools.{py_file.stem}"
                module = self._import_module(module_name, py_file)

                # Find tool classes
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if obj.__module__ != module.__name__:
                        continue

                    # Check if it's a tool (has execute/run method)
                    if hasattr(obj, 'execute') or hasattr(obj, 'run'):
                        tools[name] = obj
                        self.logger.info(f"Loaded tool: {domain_name}.{name}")

            except Exception as e:
                self.logger.error(f"Failed to load tools from {py_file}: {e}")

        return tools

    def _load_organs(
        self,
        domain_name: str,
        organs_path: Path
    ) -> Dict[str, Any]:
        """Load organs (LLM analyzers) from domain/organs/"""
        organs = {}

        for py_file in organs_path.glob("*.py"):
            if py_file.name.startswith('_'):
                continue

            try:
                module_name = f"expertise_center.domains.{domain_name}.organs.{py_file.stem}"
                module = self._import_module(module_name, py_file)

                # Find organ classes
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if obj.__module__ != module.__name__:
                        continue

                    # Check if it's an organ (has analyze method)
                    if hasattr(obj, 'analyze'):
                        organs[name] = obj
                        self.logger.info(f"Loaded organ: {domain_name}.{name}")

            except Exception as e:
                self.logger.error(f"Failed to load organs from {py_file}: {e}")

        return organs

    def _load_knowledge(
        self,
        domain_name: str,
        knowledge_path: Path
    ) -> Dict[str, Any]:
        """Load knowledge sources from domain/knowledge/"""
        knowledge = {}

        for py_file in knowledge_path.glob("*.py"):
            if py_file.name.startswith('_'):
                continue

            try:
                module_name = f"expertise_center.domains.{domain_name}.knowledge.{py_file.stem}"
                module = self._import_module(module_name, py_file)

                # Find knowledge classes
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if obj.__module__ != module.__name__:
                        continue

                    knowledge[name] = obj
                    self.logger.info(f"Loaded knowledge: {domain_name}.{name}")

            except Exception as e:
                self.logger.error(
                    f"Failed to load knowledge from {py_file}: {e}"
                )

        return knowledge

    def _import_module(self, module_name: str, file_path: Path):
        """Import a module from file path"""
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Cannot load module: {module_name}")

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def load_all_domains(self) -> Dict[str, Dict[str, Any]]:
        """
        Discover and load all available domains

        Returns:
            Dictionary of loaded domains
        """
        domains = self.discover_domains()

        for domain_name in domains:
            try:
                self.load_domain(domain_name)
            except Exception as e:
                self.logger.error(f"Failed to load domain '{domain_name}': {e}")

        return self.loaded_domains

    def get_domain_info(self, domain_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a loaded domain"""
        return self.loaded_domains.get(domain_name)

    def get_loaded_domains(self) -> List[str]:
        """Get list of loaded domain names"""
        return list(self.loaded_domains.keys())

    def reload_domain(self, domain_name: str) -> Dict[str, Any]:
        """
        Reload a domain (useful for development)

        Args:
            domain_name: Domain to reload

        Returns:
            Reloaded domain info
        """
        # Unregister existing experts
        if domain_name in self.loaded_domains:
            domain_info = self.loaded_domains[domain_name]
            for expertise_name in domain_info['experts'].keys():
                self.expert_registry.unregister_expert(domain_name, expertise_name)

        # Reload
        return self.load_domain(domain_name)
