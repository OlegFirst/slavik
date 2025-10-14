"""
Test L4 Workflow Generator

Quick test to verify L4 generator functionality.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add intelligent-core to path
intelligent_core_path = Path(__file__).parent.parent.parent.parent / "intelligent-core" / "scenario-intelligence"
sys.path.insert(0, str(intelligent_core_path))
sys.path.insert(0, str(Path(__file__).parent))

from template_loader import TemplateLoader
from storage.registry import ScenarioRegistry
from generators.l4_workflow_generator import L4WorkflowGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_l4_generator():
    """Test L4 Workflow Generator."""

    print("="*70)
    print("L4 WORKFLOW GENERATOR TEST")
    print("="*70)
    print()

    # Initialize components
    print("Initializing components...")
    templates_path = intelligent_core_path / "templates"
    loader = TemplateLoader(templates_dir=str(templates_path))
    registry = ScenarioRegistry()

    # Create generator
    print("Creating L4 Workflow Generator...")
    generator = L4WorkflowGenerator(
        template_loader=loader,
        registry=registry,
        output_dir=str(intelligent_core_path / "generated" / "l4")
    )

    # Check LLM availability
    if generator.llm_router:
        print("✅ LLM Router initialized")
        provider_info = generator.llm_router.get_provider_info()
        print(f"   Available providers:")
        for provider, info in provider_info.items():
            status = "✅" if info['available'] else "❌"
            print(f"   {status} {provider}: {info['available']}")
    else:
        print("⚠️  LLM Router not available - using fallback generation")

    print()
    print("="*70)
    print("WORKFLOW CATALOG")
    print("="*70)

    # Get catalog
    catalog = generator._get_catalog()
    print(f"\nTotal workflows defined: {len(catalog)}")
    print("\nWorkflow categories:")

    categories = {}
    for workflow in catalog:
        cat = workflow['category']
        categories[cat] = categories.get(cat, 0) + 1

    for cat, count in sorted(categories.items()):
        print(f"  - {cat}: {count} workflows")

    print("\nSample workflows:")
    for i, workflow in enumerate(catalog[:5], 1):
        print(f"\n{i}. {workflow['name']}")
        print(f"   Persona: {workflow['persona']}")
        print(f"   Goal: {workflow['goal']}")
        print(f"   Complexity: {workflow['complexity']}")
        print(f"   Duration: {workflow['duration_estimate']}")
        print(f"   Systems: {', '.join(workflow['involved_systems'][:3])}")

    print()
    print("="*70)
    print("GENERATING SCENARIOS (Limited Test)")
    print("="*70)
    print()

    # Generate a few scenarios for testing
    test_workflows = catalog[:3]  # Test first 3 workflows
    generated_count = 0
    failed_count = 0

    for workflow in test_workflows:
        print(f"\nGenerating: {workflow['name']}")
        try:
            scenario = await generator.generate_one(workflow)
            if scenario:
                # Register in registry
                success = await registry.register(scenario)
                if success:
                    scenario_id = scenario['meta']['id']
                    print(f"  ✅ Generated: {scenario_id}")

                    # Show some details
                    print(f"     Level: {scenario['meta']['level']}")
                    print(f"     Type: {scenario['meta']['type']}")
                    print(f"     Workflow: {scenario['meta']['workflow']}")
                    print(f"     Scenarios: {len(scenario['test_scenarios'])}")

                    generated_count += 1
                else:
                    print(f"  ❌ Failed to register scenario")
                    failed_count += 1
            else:
                print(f"  ❌ Failed to generate scenario")
                failed_count += 1
        except Exception as e:
            print(f"  ❌ Error: {e}")
            failed_count += 1

    print()
    print("="*70)
    print("TEST RESULTS")
    print("="*70)
    print(f"Total workflows tested: {len(test_workflows)}")
    print(f"✅ Successfully generated: {generated_count}")
    print(f"❌ Failed: {failed_count}")
    print(f"Success rate: {generated_count / len(test_workflows) * 100:.1f}%")

    # Show registry stats
    print()
    print("Registry statistics:")

    # Get all scenarios
    all_scenarios = await registry.list_all()
    print(f"  Total scenarios in registry: {len(all_scenarios)}")

    # Filter L4
    l4_scenarios = [s for s in all_scenarios if s.get('meta', {}).get('level') == 4]
    print(f"  L4 scenarios: {len(l4_scenarios)}")

    if l4_scenarios:
        print()
        print("Generated L4 scenarios:")
        for scenario in l4_scenarios[:5]:
            meta = scenario.get('meta', {})
            print(f"  - {meta.get('id')} ({meta.get('workflow')})")

    print()
    print("="*70)
    print("TEST COMPLETE")
    print("="*70)


if __name__ == "__main__":
    asyncio.run(test_l4_generator())
