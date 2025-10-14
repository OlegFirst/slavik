"""
Test Template Loader Integration with Registry

This test validates:
1. TemplateLoader can load templates correctly
2. Templates can be filled with context
3. Integration with ScenarioRegistry works
4. Specialized templates are loaded correctly
"""

import asyncio
import sys
from pathlib import Path
import logging

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from template_loader import TemplateLoader, RegistryTemplateIntegration
from storage.registry import ScenarioRegistry

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_1_load_base_templates():
    """Test 1: Load all base templates"""
    print("\n" + "="*70)
    print("TEST 1: Load Base Templates")
    print("="*70)

    loader = TemplateLoader(templates_dir="templates")

    base_templates = [
        "golden_standard_l1.yaml",
        "golden_standard_l1_application.yaml",
        "golden_standard_l2.yaml",
        "golden_standard_l3.yaml",
        "golden_standard_l4.yaml"
    ]

    results = {}

    for template_name in base_templates:
        try:
            template = loader.load(template_name)
            scenario_count = len(template.get('test_scenarios', []))
            results[template_name] = {
                'status': 'OK',
                'scenarios': scenario_count,
                'level': template.get('meta', {}).get('level')
            }
            print(f"✅ {template_name}: {scenario_count} scenarios, level {results[template_name]['level']}")
        except Exception as e:
            results[template_name] = {'status': 'FAILED', 'error': str(e)}
            print(f"❌ {template_name}: {e}")

    success_count = sum(1 for r in results.values() if r['status'] == 'OK')
    print(f"\n📊 Result: {success_count}/{len(base_templates)} templates loaded successfully")

    return success_count == len(base_templates)


async def test_2_load_specialized_templates():
    """Test 2: Load specialized L3 templates"""
    print("\n" + "="*70)
    print("TEST 2: Load Specialized L3 Templates")
    print("="*70)

    loader = TemplateLoader(templates_dir="templates")

    categories = [
        "infrastructure",
        "security",
        "reliability",
        "ai",
        "operations",
        "intelligence",
        "business",
        "orchestration",
        "quality",
        "frontend",
        "infrastructure_management"
    ]

    results = {}

    for category in categories:
        try:
            template = loader.load_specialized(category)
            scenario_count = len(template.get('test_scenarios', []))
            results[category] = {
                'status': 'OK',
                'scenarios': scenario_count,
                'category': template.get('meta', {}).get('category')
            }
            print(f"✅ {category}: {scenario_count} scenarios")
        except Exception as e:
            results[category] = {'status': 'FAILED', 'error': str(e)}
            print(f"❌ {category}: {e}")

    success_count = sum(1 for r in results.values() if r['status'] == 'OK')
    print(f"\n📊 Result: {success_count}/{len(categories)} specialized templates loaded")

    return success_count == len(categories)


async def test_3_template_placeholder_replacement():
    """Test 3: Placeholder replacement works correctly"""
    print("\n" + "="*70)
    print("TEST 3: Template Placeholder Replacement")
    print("="*70)

    loader = TemplateLoader(templates_dir="templates")

    # Load L1 template
    template = loader.load("golden_standard_l1.yaml")

    # Context for mio-manager service
    context = {
        "service_name": "mio-manager",
        "port": 8025,
        "criticality": "critical",
        "subsystem_name": "ai_office",
        "internal_dependencies": "service-discovery, eventbus",
        "external_dependencies": "postgresql, redis"
    }

    # Fill template
    filled = loader.fill_template(template, context)

    # Verify replacements
    meta_id = filled.get('meta', {}).get('id', '')

    checks = {
        'service_name_in_id': 'mio-manager' in meta_id,
        'port_replaced': str(8025) in str(filled),
        'criticality_replaced': 'critical' in str(filled),
        'template_structure_preserved': 'test_scenarios' in filled and 'monitoring' in filled
    }

    for check_name, result in checks.items():
        status = "✅" if result else "❌"
        print(f"{status} {check_name}: {result}")

    all_passed = all(checks.values())
    print(f"\n📊 Result: {'PASS' if all_passed else 'FAIL'}")

    return all_passed


async def test_4_registry_integration():
    """Test 4: Integration with ScenarioRegistry"""
    print("\n" + "="*70)
    print("TEST 4: Registry Integration")
    print("="*70)

    # Initialize systems
    registry = ScenarioRegistry()
    loader = TemplateLoader(templates_dir="templates")

    # Create scenario from template
    context = {
        "service_name": "analytics-specialist",
        "port": 8030,
        "criticality": "high",
        "subsystem_name": "ai_office",
        "internal_dependencies": "service-discovery, eventbus",
        "external_dependencies": "postgresql"
    }

    scenario = loader.create_scenario_from_template(
        "golden_standard_l1.yaml",
        context,
        validate=True
    )

    # Register in ScenarioRegistry
    success = await registry.register(scenario)

    if not success:
        print("❌ Failed to register scenario")
        return False

    print(f"✅ Scenario registered successfully")

    # Retrieve from registry
    scenario_id = scenario.get('meta', {}).get('id')
    retrieved = await registry.get_scenario_by_id(scenario_id)

    if retrieved is None:
        print("❌ Failed to retrieve scenario")
        return False

    print(f"✅ Scenario retrieved: {scenario_id}")

    # Verify data
    checks = {
        'meta_preserved': 'meta' in retrieved,
        'test_scenarios_preserved': 'test_scenarios' in retrieved,
        'service_name_correct': 'analytics-specialist' in str(retrieved),
        'level_correct': retrieved.get('meta', {}).get('level') == 1
    }

    for check_name, result in checks.items():
        status = "✅" if result else "❌"
        print(f"{status} {check_name}: {result}")

    all_passed = all(checks.values())
    print(f"\n📊 Result: {'PASS' if all_passed else 'FAIL'}")

    return all_passed


async def test_5_bulk_registration():
    """Test 5: Bulk registration from catalog"""
    print("\n" + "="*70)
    print("TEST 5: Bulk Registration from Catalog")
    print("="*70)

    # Initialize systems
    registry = ScenarioRegistry()
    loader = TemplateLoader(templates_dir="templates")

    # Simulate service catalog
    services_catalog = [
        {"name": "mio-manager", "port": 8025, "criticality": "critical", "subsystem": "ai_office"},
        {"name": "analytics-specialist", "port": 8030, "criticality": "high", "subsystem": "ai_office"},
        {"name": "devops-agent", "port": 8035, "criticality": "medium", "subsystem": "ai_office"}
    ]

    registered_count = 0

    for service in services_catalog:
        context = {
            "service_name": service["name"],
            "port": service["port"],
            "criticality": service["criticality"],
            "subsystem_name": service["subsystem"],
            "internal_dependencies": "service-discovery, eventbus",
            "external_dependencies": "postgresql"
        }

        scenario = loader.create_scenario_from_template(
            "golden_standard_l1.yaml",
            context
        )

        success = await registry.register(scenario)
        if success:
            registered_count += 1
            print(f"✅ Registered: {service['name']}")
        else:
            print(f"❌ Failed: {service['name']}")

    # Get statistics
    stats = await registry.get_statistics()

    print(f"\n📊 Registry Statistics:")
    print(f"   Total scenarios: {stats['total_scenarios']}")
    print(f"   By level: {stats['by_level']}")

    success = registered_count == len(services_catalog)
    print(f"\n📊 Result: {registered_count}/{len(services_catalog)} registered {'PASS' if success else 'FAIL'}")

    return success


async def test_6_specialized_category_selection():
    """Test 6: Specialized template selection by category"""
    print("\n" + "="*70)
    print("TEST 6: Specialized Template Selection")
    print("="*70)

    loader = TemplateLoader(templates_dir="templates")

    test_cases = [
        {"category": "security", "expected_in_meta": "security"},
        {"category": "ai", "expected_in_meta": "ai"},
        {"category": "infrastructure", "expected_in_meta": "infrastructure"},
        {"category": "nonexistent_category", "should_fallback": True}
    ]

    results = []

    for test_case in test_cases:
        category = test_case["category"]
        template = loader.load_specialized(category)

        meta_category = template.get('meta', {}).get('category', '')

        if test_case.get('should_fallback'):
            # Should fallback to general L3
            passed = template.get('meta', {}).get('level') == 3
            result_msg = "Fallback to general L3" if passed else "Failed to fallback"
        else:
            # Should match expected category
            expected = test_case.get('expected_in_meta', '')
            passed = expected in meta_category
            result_msg = f"Category: {meta_category}"

        status = "✅" if passed else "❌"
        print(f"{status} {category}: {result_msg}")
        results.append(passed)

    all_passed = all(results)
    print(f"\n📊 Result: {sum(results)}/{len(test_cases)} category selections correct {'PASS' if all_passed else 'FAIL'}")

    return all_passed


async def test_7_template_validation():
    """Test 7: Template validation"""
    print("\n" + "="*70)
    print("TEST 7: Template Validation")
    print("="*70)

    loader = TemplateLoader(templates_dir="templates")

    # Load a valid template
    valid_template = loader.load("golden_standard_l1.yaml")

    # Test valid template
    is_valid = loader.validate_template(valid_template)
    print(f"{'✅' if is_valid else '❌'} Valid template validation: {is_valid}")

    # Test invalid template (missing required keys)
    invalid_template = {"meta": {"level": 1}}
    is_invalid = not loader.validate_template(invalid_template)
    print(f"{'✅' if is_invalid else '❌'} Invalid template rejected: {is_invalid}")

    passed = is_valid and is_invalid
    print(f"\n📊 Result: {'PASS' if passed else 'FAIL'}")

    return passed


async def run_all_tests():
    """Run all integration tests"""
    print("\n" + "="*70)
    print("TEMPLATE LOADER INTEGRATION TEST SUITE")
    print("="*70)

    tests = [
        ("Load Base Templates", test_1_load_base_templates),
        ("Load Specialized Templates", test_2_load_specialized_templates),
        ("Placeholder Replacement", test_3_template_placeholder_replacement),
        ("Registry Integration", test_4_registry_integration),
        ("Bulk Registration", test_5_bulk_registration),
        ("Category Selection", test_6_specialized_category_selection),
        ("Template Validation", test_7_template_validation)
    ]

    results = {}

    for test_name, test_func in tests:
        try:
            result = await test_func()
            results[test_name] = result
        except Exception as e:
            logger.error(f"Test '{test_name}' crashed: {e}", exc_info=True)
            results[test_name] = False

    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")

    passed = sum(1 for r in results.values() if r)
    total = len(results)

    print(f"\n📊 Overall: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 ALL TESTS PASSED!")
        return True
    else:
        print(f"⚠️  {total - passed} test(s) failed")
        return False


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
