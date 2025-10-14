"""
Template Loader - Integration Bridge
Connects my templates system with other team's Registry

Created: 2025-10-12
Purpose: Merge point between Architecture 2.0 and MVP
"""

import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)


class TemplateLoader:
    """
    Load and manage golden standard templates.

    Integrates with existing Registry and storage systems.
    """

    def __init__(self, templates_dir: str = "templates"):
        """
        Initialize template loader.

        Args:
            templates_dir: Path to templates directory
        """
        self.templates_dir = Path(templates_dir)
        self.templates_cache: Dict[str, Dict] = {}

        # Validate templates directory exists
        if not self.templates_dir.exists():
            raise FileNotFoundError(f"Templates directory not found: {self.templates_dir}")

        logger.info(f"TemplateLoader initialized with dir: {self.templates_dir}")

    def load(self, template_name: str) -> Dict:
        """
        Load a template by name.

        Args:
            template_name: Name of template file (e.g., "golden_standard_l1.yaml")

        Returns:
            Template dictionary
        """
        # Check cache first
        if template_name in self.templates_cache:
            logger.debug(f"Loading template from cache: {template_name}")
            return self.templates_cache[template_name]

        # Load from file
        template_path = self.templates_dir / template_name

        if not template_path.exists():
            raise FileNotFoundError(f"Template not found: {template_path}")

        with open(template_path, 'r') as f:
            template = yaml.safe_load(f)

        # Cache it
        self.templates_cache[template_name] = template

        logger.info(f"Loaded template: {template_name}")
        return template

    def load_specialized(self, category: str) -> Dict:
        """
        Load specialized L3 template by category.

        Args:
            category: System category (infrastructure, security, ai, etc.)

        Returns:
            Specialized template or fallback to general
        """
        specialized_path = self.templates_dir / "l3-specialized" / f"l3_{category}_system.yaml"

        if specialized_path.exists():
            logger.info(f"Loading specialized template for category: {category}")
            with open(specialized_path, 'r') as f:
                return yaml.safe_load(f)
        else:
            # Fallback to general L3 template
            logger.warning(f"Specialized template not found for {category}, using general L3")
            return self.load("golden_standard_l3.yaml")

    def list_templates(self) -> List[str]:
        """
        List all available templates.

        Returns:
            List of template filenames
        """
        base_templates = list(self.templates_dir.glob("golden_standard_*.yaml"))
        specialized_templates = list((self.templates_dir / "l3-specialized").glob("l3_*.yaml"))

        all_templates = [t.name for t in base_templates] + \
                       [f"l3-specialized/{t.name}" for t in specialized_templates]

        return all_templates

    def get_template_for_level(self, level: int, category: Optional[str] = None) -> Dict:
        """
        Get appropriate template for scenario level.

        Args:
            level: Scenario level (1, 2, 3, 4)
            category: Optional category for L3 specialized templates

        Returns:
            Template dictionary
        """
        if level == 1:
            # L1 has two templates - need to know if service or application
            # Default to service template
            return self.load("golden_standard_l1.yaml")

        elif level == 2:
            return self.load("golden_standard_l2.yaml")

        elif level == 3:
            if category:
                return self.load_specialized(category)
            else:
                return self.load("golden_standard_l3.yaml")

        elif level == 4:
            return self.load("golden_standard_l4.yaml")

        else:
            raise ValueError(f"Invalid level: {level}. Must be 1, 2, 3, or 4")

    def validate_template(self, template: Dict) -> bool:
        """
        Validate template structure.

        Args:
            template: Template dictionary

        Returns:
            True if valid
        """
        required_keys = ["meta", "description", "test_scenarios", "monitoring"]

        for key in required_keys:
            if key not in template:
                logger.error(f"Template missing required key: {key}")
                return False

        # Validate meta
        if "level" not in template["meta"]:
            logger.error("Template meta missing 'level'")
            return False

        # Validate test_scenarios is list
        if not isinstance(template["test_scenarios"], list):
            logger.error("test_scenarios must be a list")
            return False

        logger.debug("Template validation passed")
        return True

    def fill_template(self, template: Dict, context: Dict[str, Any]) -> Dict:
        """
        Fill template placeholders with context values.

        Args:
            template: Template dictionary
            context: Context values for placeholder replacement

        Returns:
            Filled template
        """
        import copy
        import re

        filled = copy.deepcopy(template)

        def replace_placeholders(obj: Any) -> Any:
            """Recursively replace placeholders in template."""
            if isinstance(obj, dict):
                return {k: replace_placeholders(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [replace_placeholders(item) for item in obj]
            elif isinstance(obj, str):
                # Replace {placeholder} with context value
                pattern = r'\{([^}]+)\}'
                matches = re.findall(pattern, obj)

                for match in matches:
                    if match in context:
                        obj = obj.replace(f"{{{match}}}", str(context[match]))

                return obj
            else:
                return obj

        filled = replace_placeholders(filled)

        logger.info(f"Filled template with {len(context)} context values")
        return filled

    def create_scenario_from_template(
        self,
        template_name: str,
        context: Dict[str, Any],
        validate: bool = True
    ) -> Dict:
        """
        Create a scenario from template with context.

        Args:
            template_name: Name of template
            context: Context values
            validate: Whether to validate template

        Returns:
            Generated scenario
        """
        # Load template
        template = self.load(template_name)

        # Validate if requested
        if validate:
            if not self.validate_template(template):
                raise ValueError(f"Template validation failed: {template_name}")

        # Fill with context
        scenario = self.fill_template(template, context)

        logger.info(f"Created scenario from template: {template_name}")
        return scenario


# Integration with existing Registry
class RegistryTemplateIntegration:
    """
    Integration layer between TemplateLoader and existing Registry.

    Allows existing code to work with templates seamlessly.
    """

    def __init__(self, registry, template_loader: TemplateLoader):
        """
        Initialize integration.

        Args:
            registry: Existing Registry instance
            template_loader: TemplateLoader instance
        """
        self.registry = registry
        self.loader = template_loader

        logger.info("RegistryTemplateIntegration initialized")

    def register_from_template(
        self,
        template_name: str,
        context: Dict[str, Any],
        scenario_id: Optional[str] = None
    ) -> str:
        """
        Create scenario from template and register it.

        Args:
            template_name: Template to use
            context: Context for placeholder replacement
            scenario_id: Optional scenario ID (generated if not provided)

        Returns:
            Scenario ID
        """
        # Create scenario from template
        scenario = self.loader.create_scenario_from_template(template_name, context)

        # Use provided ID or generate from meta
        if scenario_id is None:
            scenario_id = scenario.get("meta", {}).get("id", "generated-scenario")

        # Register in existing Registry
        self.registry.register(scenario_id, scenario)

        logger.info(f"Registered scenario from template: {scenario_id}")
        return scenario_id

    def bulk_register_from_catalog(
        self,
        catalog: Dict,
        template_name: str,
        context_builder: callable
    ) -> List[str]:
        """
        Bulk register scenarios from catalog.

        Args:
            catalog: Service/System catalog
            template_name: Template to use
            context_builder: Function that builds context from catalog entry

        Returns:
            List of registered scenario IDs
        """
        registered_ids = []

        for item in catalog.get("items", []):
            # Build context for this item
            context = context_builder(item)

            # Create and register
            scenario_id = self.register_from_template(template_name, context)
            registered_ids.append(scenario_id)

        logger.info(f"Bulk registered {len(registered_ids)} scenarios")
        return registered_ids


# Example usage functions
def example_load_l1_template():
    """Example: Load L1 service template."""
    loader = TemplateLoader()
    template = loader.load("golden_standard_l1.yaml")
    print(f"Loaded template with {len(template['test_scenarios'])} scenarios")


def example_create_scenario_from_template():
    """Example: Create scenario from template with context."""
    loader = TemplateLoader()

    # Context from service catalog
    context = {
        "service_name": "mio-manager",
        "port": 8025,
        "criticality": "critical",
        "subsystem_name": "ai_office",
        "internal_dependencies": ["service-discovery", "eventbus"],
        "external_dependencies": ["postgresql", "redis"]
    }

    scenario = loader.create_scenario_from_template(
        "golden_standard_l1.yaml",
        context
    )

    print(f"Created scenario: {scenario['meta']['id']}")
    print(f"Test scenarios: {len(scenario['test_scenarios'])}")


def example_integration_with_registry():
    """Example: Integrate with existing Registry."""
    from registry import InMemoryRegistry  # Their Registry

    # Initialize both systems
    registry = InMemoryRegistry()
    loader = TemplateLoader()
    integration = RegistryTemplateIntegration(registry, loader)

    # Create and register from template
    context = {
        "service_name": "analytics-specialist",
        "port": 8030,
        "criticality": "high",
        "subsystem_name": "ai_office"
    }

    scenario_id = integration.register_from_template(
        "golden_standard_l1.yaml",
        context
    )

    # Retrieve from registry (using their API)
    scenario = registry.get(scenario_id)
    print(f"Retrieved scenario: {scenario['meta']['name']}")


if __name__ == "__main__":
    # Run examples
    print("=== Template Loader Examples ===\n")

    print("1. Loading template:")
    example_load_l1_template()

    print("\n2. Creating scenario from template:")
    example_create_scenario_from_template()

    print("\n3. Integration with Registry:")
    # example_integration_with_registry()  # Uncomment when Registry available

    print("\n=== Examples complete ===")
