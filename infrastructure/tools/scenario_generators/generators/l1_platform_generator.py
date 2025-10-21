"""
L1 Platform Generator

Generates test scenarios for platform services.
Uses golden_standard_l1.yaml template.
"""

import asyncio
import logging
from pathlib import Path
from typing import List, Dict, Any
import sys

# Add intelligent-core to path for templates/storage
intelligent_core_path = Path(__file__).parent.parent.parent.parent.parent / "intelligent-core" / "scenario-intelligence"
sys.path.insert(0, str(intelligent_core_path))

from generators.base_generator import BaseGenerator
from generators.platform_services_catalog import get_platform_services

logger = logging.getLogger(__name__)


class L1PlatformGenerator(BaseGenerator):
    """
    Generator for L1 Platform Service scenarios.

    Creates test scenarios for all 46 platform services.
    """

    def __init__(self, template_loader, registry, output_dir: str = "generated/l1/services"):
        super().__init__(
            template_loader=template_loader,
            registry=registry,
            output_dir=output_dir,
            level=1
        )

    def _get_catalog(self) -> List[Dict[str, Any]]:
        """
        Get platform services catalog.

        Returns:
            List of 46 platform service definitions
        """
        return get_platform_services()

    def _build_context(self, service: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build template context from service definition.

        Args:
            service: Service definition

        Returns:
            Context for template placeholder replacement
        """
        return {
            "service_name": service["name"],
            "port": service["port"],
            "criticality": service["criticality"],
            "subsystem_name": service["subsystem"],
            "internal_dependencies": ", ".join(service["internal_dependencies"]),
            "external_dependencies": ", ".join(service["external_dependencies"])
        }

    def _get_template_name(self, item: Dict[str, Any]) -> str:
        """
        Get template name for service.

        Args:
            item: Service definition

        Returns:
            Template filename
        """
        return "golden_standard_l1.yaml"


async def main():
    """Run L1 Platform Generator standalone."""
    from template_loader import TemplateLoader
    from storage.registry import ScenarioRegistry

    print("="*70)
    print("L1 PLATFORM GENERATOR")
    print("="*70)

    # Initialize components
    loader = TemplateLoader(templates_dir="templates")
    registry = ScenarioRegistry()

    # Create generator
    generator = L1PlatformGenerator(
        template_loader=loader,
        registry=registry,
        output_dir="generated/l1/services"
    )

    # Generate all scenarios
    scenario_ids = await generator.generate_all()

    # Print results
    stats = generator.get_statistics()
    print(f"\n Generated {stats['generated']}/{stats['total']} service scenarios")
    print(f" Saved to: generated/l1/services/")
    print(f" Scenario IDs: {len(scenario_ids)}")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    asyncio.run(main())
