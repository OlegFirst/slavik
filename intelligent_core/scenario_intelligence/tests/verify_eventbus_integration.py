#!/usr/bin/env python3
"""
EventBus Integration Verification Script

Verifies that EventBus integration is working correctly:
1. EventBus client can be initialized
2. Events can be created
3. Events can be published
4. Subscriptions can be set up
5. All components are properly integrated

Run this script to verify the integration is working.
"""

import asyncio
import logging
import sys
from pathlib import Path
from datetime import datetime

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "infrastructure"))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EventBusIntegrationVerifier:
    """Verify EventBus integration"""

    def __init__(self):
        self.results = []
        self.passed = 0
        self.failed = 0

    def test(self, name: str, passed: bool, message: str = ""):
        """Record test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        self.results.append({
            "name": name,
            "passed": passed,
            "message": message
        })
        if passed:
            self.passed += 1
            logger.info(f"{status}: {name}")
        else:
            self.failed += 1
            logger.error(f"{status}: {name} - {message}")

    async def verify_imports(self):
        """Test 1: Verify all imports work"""
        logger.info("\n" + "="*70)
        logger.info("TEST 1: Verify Imports")
        logger.info("="*70)

        try:
            from integrations.eventbus_client import ScenarioEventBusClient, get_eventbus_client
            self.test("Import ScenarioEventBusClient", True)
        except Exception as e:
            self.test("Import ScenarioEventBusClient", False, str(e))

        try:
            from events.scenario_events import (
                create_scenario_generated_event,
                create_scenario_executed_event,
                create_regeneration_triggered_event,
                ScenarioEventTypes,
                ScenarioLevel,
                ScenarioGenerationTrigger
            )
            self.test("Import event creators", True)
        except Exception as e:
            self.test("Import event creators", False, str(e))

        try:
            # Check if infrastructure EventBus is available
            from infrastructure.eventbus import create_eventbus, Event, EventPriority
            self.test("Import infrastructure EventBus", True)
        except Exception as e:
            self.test("Import infrastructure EventBus", False, str(e))

    async def verify_client_initialization(self):
        """Test 2: Verify client can be initialized"""
        logger.info("\n" + "="*70)
        logger.info("TEST 2: Client Initialization")
        logger.info("="*70)

        try:
            from integrations.eventbus_client import ScenarioEventBusClient

            # Test memory backend
            client = ScenarioEventBusClient(backend='memory')
            await client.initialize()

            is_connected = client.is_connected()
            self.test("Client initialization (memory backend)", is_connected)

            # Test health check
            health = await client.health_check()
            self.test(
                "Client health check",
                health["connected"] and health["backend"] == "memory"
            )

            await client.close()
            self.test("Client close", True)

        except Exception as e:
            self.test("Client initialization", False, str(e))

    async def verify_event_creation(self):
        """Test 3: Verify events can be created"""
        logger.info("\n" + "="*70)
        logger.info("TEST 3: Event Creation")
        logger.info("="*70)

        try:
            from events.scenario_events import (
                create_scenario_generated_event,
                create_scenario_executed_event,
                create_regeneration_triggered_event,
                create_regeneration_completed_event,
                ScenarioLevel,
                ScenarioGenerationTrigger
            )

            # Test scenario.generated event
            event1 = create_scenario_generated_event(
                scenario_ids=["test-1", "test-2"],
                level=ScenarioLevel.L1_PLATFORM,
                generator="l1_platform",
                trigger=ScenarioGenerationTrigger.MANUAL
            )
            self.test(
                "Create scenario.generated event",
                event1.count == 2 and event1.level == ScenarioLevel.L1_PLATFORM
            )

            # Test scenario.executed event
            event2 = create_scenario_executed_event(
                scenario_id="test-scenario",
                execution_id="exec-123",
                status="success",
                duration_ms=1500.0,
                steps_executed=5
            )
            self.test(
                "Create scenario.executed event",
                event2.status == "success" and event2.duration_ms == 1500.0
            )

            # Test regeneration.triggered event
            event3 = create_regeneration_triggered_event(
                trigger_event="service.added",
                affected_services=["new-service"],
                affected_levels=["l1_platform"],
                regeneration_id="regen-123"
            )
            self.test(
                "Create regeneration.triggered event",
                event3.regeneration_id == "regen-123"
            )

            # Test regeneration.completed event
            event4 = create_regeneration_completed_event(
                regeneration_id="regen-123",
                trigger_event="service.added",
                scenarios_generated=10,
                scenarios_updated=5,
                scenarios_deprecated=0,
                duration_ms=30000.0,
                status="success"
            )
            self.test(
                "Create regeneration.completed event",
                event4.scenarios_generated == 10 and event4.status == "success"
            )

        except Exception as e:
            self.test("Event creation", False, str(e))

    async def verify_event_publishing(self):
        """Test 4: Verify events can be published"""
        logger.info("\n" + "="*70)
        logger.info("TEST 4: Event Publishing")
        logger.info("="*70)

        try:
            from integrations.eventbus_client import ScenarioEventBusClient
            from events.scenario_events import (
                create_scenario_generated_event,
                create_scenario_executed_event,
                ScenarioLevel,
                ScenarioGenerationTrigger
            )

            client = ScenarioEventBusClient(backend='memory')
            await client.initialize()

            # Publish scenario.generated
            event1 = create_scenario_generated_event(
                scenario_ids=["test-1"],
                level=ScenarioLevel.L1_PLATFORM,
                generator="test",
                trigger=ScenarioGenerationTrigger.MANUAL
            )
            await client.publish_scenario_generated(event1)
            self.test("Publish scenario.generated event", True)

            # Publish scenario.executed
            event2 = create_scenario_executed_event(
                scenario_id="test",
                execution_id="exec-1",
                status="success",
                duration_ms=1000.0
            )
            await client.publish_scenario_executed(event2)
            self.test("Publish scenario.executed event", True)

            await client.close()

        except Exception as e:
            self.test("Event publishing", False, str(e))

    async def verify_subscriptions(self):
        """Test 5: Verify subscriptions can be set up"""
        logger.info("\n" + "="*70)
        logger.info("TEST 5: Event Subscriptions")
        logger.info("="*70)

        try:
            from integrations.eventbus_client import ScenarioEventBusClient

            client = ScenarioEventBusClient(backend='memory')
            await client.initialize()

            received_events = []

            async def test_callback(event):
                received_events.append(event)

            # Subscribe to catalog updates
            await client.subscribe_to_catalog_updates(test_callback)

            subscriptions = client.get_subscriptions()
            self.test(
                "Setup subscriptions",
                len(subscriptions) > 0,
                f"Subscriptions: {subscriptions}"
            )

            await client.close()

        except Exception as e:
            self.test("Event subscriptions", False, str(e))

    async def verify_generation_manager_integration(self):
        """Test 6: Verify Generation Manager integration"""
        logger.info("\n" + "="*70)
        logger.info("TEST 6: Generation Manager Integration")
        logger.info("="*70)

        try:
            # Check if GenerationManager has EventBus support
            sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent /
                                  "infrastructure" / "tools" / "scenario-generators"))

            # Import and check
            try:
                from managers.generation_manager import GenerationManager
                import inspect

                # Check if __init__ accepts eventbus_client
                init_signature = inspect.signature(GenerationManager.__init__)
                has_eventbus_param = 'eventbus_client' in init_signature.parameters

                self.test(
                    "GenerationManager has eventbus_client parameter",
                    has_eventbus_param
                )

                # Check if enable_eventbus parameter exists
                has_enable_param = 'enable_eventbus' in init_signature.parameters
                self.test(
                    "GenerationManager has enable_eventbus parameter",
                    has_enable_param
                )

            except ImportError as e:
                self.test(
                    "GenerationManager import",
                    False,
                    f"Could not import (expected if not in correct environment): {e}"
                )

        except Exception as e:
            self.test("Generation Manager integration", False, str(e))

    async def verify_scenario_engine_integration(self):
        """Test 7: Verify Scenario Engine integration"""
        logger.info("\n" + "="*70)
        logger.info("TEST 7: Scenario Engine Integration")
        logger.info("="*70)

        try:
            from engines.scenario_engine import ScenarioEngine
            import inspect

            # Check if __init__ accepts eventbus_client
            init_signature = inspect.signature(ScenarioEngine.__init__)
            has_eventbus_param = 'eventbus_client' in init_signature.parameters

            self.test(
                "ScenarioEngine has eventbus_client parameter",
                has_eventbus_param
            )

            # Check if _publish_execution_event method exists
            has_publish_method = hasattr(ScenarioEngine, '_publish_execution_event')
            self.test(
                "ScenarioEngine has _publish_execution_event method",
                has_publish_method
            )

        except Exception as e:
            self.test("Scenario Engine integration", False, str(e))

    async def verify_mio_manager_client(self):
        """Test 8: Verify MIO Manager client exists"""
        logger.info("\n" + "="*70)
        logger.info("TEST 8: MIO Manager Integration")
        logger.info("="*70)

        try:
            mio_path = Path(__file__).parent.parent.parent.parent.parent / \
                       "infrastructure" / "AI-office-infrastructure" / "mio-manager"
            sys.path.insert(0, str(mio_path))

            from integrations.scenario_intelligence_client import ScenarioIntelligenceClient
            import inspect

            # Check methods exist
            methods = [
                'subscribe_to_events',
                'handle_scenario_generated',
                'handle_scenario_executed',
                'handle_regeneration_triggered',
                'handle_regeneration_completed',
                'get_metrics',
                'get_health_status'
            ]

            for method in methods:
                has_method = hasattr(ScenarioIntelligenceClient, method)
                self.test(
                    f"ScenarioIntelligenceClient has {method}",
                    has_method
                )

        except Exception as e:
            self.test("MIO Manager client", False, str(e))

    async def verify_auto_regeneration_handler(self):
        """Test 9: Verify Auto-Regeneration Handler"""
        logger.info("\n" + "="*70)
        logger.info("TEST 9: Auto-Regeneration Handler")
        logger.info("="*70)

        try:
            handler_path = Path(__file__).parent.parent.parent.parent.parent / \
                          "infrastructure" / "tools" / "scenario-generators" / "managers"
            sys.path.insert(0, str(handler_path))

            from auto_regeneration_handler import AutoRegenerationHandler
            import inspect

            # Check methods exist
            methods = [
                'initialize',
                'handle_catalog_event',
                'handle_service_added',
                'handle_service_updated',
                'handle_service_removed'
            ]

            for method in methods:
                has_method = hasattr(AutoRegenerationHandler, method)
                self.test(
                    f"AutoRegenerationHandler has {method}",
                    has_method
                )

        except Exception as e:
            self.test("Auto-Regeneration Handler", False, str(e))

    def print_summary(self):
        """Print test summary"""
        logger.info("\n" + "="*70)
        logger.info("VERIFICATION SUMMARY")
        logger.info("="*70)

        total = self.passed + self.failed
        pass_rate = (self.passed / total * 100) if total > 0 else 0

        logger.info(f"Total Tests: {total}")
        logger.info(f"✅ Passed: {self.passed}")
        logger.info(f"❌ Failed: {self.failed}")
        logger.info(f"Pass Rate: {pass_rate:.1f}%")

        if self.failed > 0:
            logger.info("\nFailed Tests:")
            for result in self.results:
                if not result["passed"]:
                    logger.error(f"  - {result['name']}: {result['message']}")

        logger.info("\n" + "="*70)
        if self.failed == 0:
            logger.info("✅ ALL TESTS PASSED - EventBus integration is working!")
        else:
            logger.warning(f"⚠️  {self.failed} test(s) failed - Review errors above")
        logger.info("="*70)

        return self.failed == 0


async def main():
    """Run verification"""
    logger.info("="*70)
    logger.info("EventBus Integration Verification")
    logger.info("="*70)

    verifier = EventBusIntegrationVerifier()

    # Run all verification tests
    await verifier.verify_imports()
    await verifier.verify_client_initialization()
    await verifier.verify_event_creation()
    await verifier.verify_event_publishing()
    await verifier.verify_subscriptions()
    await verifier.verify_generation_manager_integration()
    await verifier.verify_scenario_engine_integration()
    await verifier.verify_mio_manager_client()
    await verifier.verify_auto_regeneration_handler()

    # Print summary
    success = verifier.print_summary()

    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
