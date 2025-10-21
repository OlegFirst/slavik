"""
Generation Manager

Orchestrates scenario generation across all levels (L1, L2, L3, L4).
Manages dependencies, progress tracking, and coordination.
"""

import asyncio
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import sys
import uuid

# Add paths to intelligent-core and generators
intelligent_core_path = Path(__file__).parent.parent.parent.parent.parent / "intelligent-core" / "scenario-intelligence"
sys.path.insert(0, str(intelligent_core_path))
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import from intelligent_core (templates and storage)
from template_loader import TemplateLoader
from storage.registry import ScenarioRegistry

# Import EventBus integration
try:
    from integrations.eventbus_client import ScenarioEventBusClient
    from events.scenario_events import (
        create_scenario_generated_event,
        ScenarioGenerationTrigger,
        ScenarioLevel
    )
    EVENTBUS_AVAILABLE = True
except ImportError:
    EVENTBUS_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("EventBus integration not available")

# Try to import PostgreSQL and Qdrant storages (optional)
try:
    from storage.postgres_storage import PostgresScenarioStorage
except ImportError:
    PostgresScenarioStorage = None
    logger.warning("PostgreSQL storage not available (install asyncpg)")

try:
    from storage.qdrant_storage import QdrantScenarioStorage
except ImportError:
    QdrantScenarioStorage = None
    logger.warning("Qdrant storage not available (install qdrant-client sentence-transformers)")

# Import from local generators
from generators.l1_platform_generator import L1PlatformGenerator
from generators.l1_application_generator import L1ApplicationGenerator
from generators.l2_subsystem_generator import L2SubsystemGenerator
from generators.l3_system_generator import L3SystemGenerator
from generators.l4_workflow_generator import L4WorkflowGenerator

logger = logging.getLogger(__name__)


class GenerationManager:
    """
    Manages the complete scenario generation process.

    Coordinates all generators (L1, L2, L3, L4) and handles:
    - Sequential generation (L1 -> L2 -> L3 -> L4)
    - Progress tracking
    - Statistics collection
    - Error handling and recovery
    """

    def __init__(
        self,
        template_loader: Optional[TemplateLoader] = None,
        registry: Optional[ScenarioRegistry] = None,
        postgres_storage: Optional['PostgresScenarioStorage'] = None,
        qdrant_storage: Optional['QdrantScenarioStorage'] = None,
        output_base_dir: str = "generated",
        enable_postgres: bool = True,
        enable_qdrant: bool = False,  # Disabled by default (требует Qdrant server)
        database_url: Optional[str] = None,
        eventbus_client: Optional['ScenarioEventBusClient'] = None,
        enable_eventbus: bool = True
    ):
        """
        Initialize generation manager.

        Args:
            template_loader: TemplateLoader instance (creates new if None)
            registry: ScenarioRegistry instance (creates new if None)
            postgres_storage: PostgreSQL storage (creates new if None and enabled)
            qdrant_storage: Qdrant storage (creates new if None and enabled)
            output_base_dir: Base directory for generated scenarios
            enable_postgres: Enable PostgreSQL storage (default: True)
            enable_qdrant: Enable Qdrant storage (default: False)
            database_url: PostgreSQL connection string (if None, uses env)
            eventbus_client: ScenarioEventBusClient instance (creates new if None and enabled)
            enable_eventbus: Enable EventBus integration (default: True)
        """
        # Get absolute path to templates in intelligent-core
        if template_loader is None:
            intelligent_core_path = Path(__file__).parent.parent.parent.parent.parent / "intelligent-core" / "scenario-intelligence"
            templates_path = intelligent_core_path / "templates"
            self.loader = TemplateLoader(templates_dir=str(templates_path))
        else:
            self.loader = template_loader

        # In-memory registry (всегда используется)
        self.registry = registry or ScenarioRegistry()

        # PostgreSQL storage (опционально)
        self.postgres_storage = None
        if enable_postgres and PostgresScenarioStorage is not None:
            if postgres_storage:
                self.postgres_storage = postgres_storage
            elif database_url or 'DATABASE_URL' in os.environ:
                url = database_url or os.getenv('DATABASE_URL')
                self.postgres_storage = PostgresScenarioStorage(connection_string=url)
                logger.info("PostgreSQL storage enabled")

        # Qdrant storage (опционально)
        self.qdrant_storage = None
        if enable_qdrant and QdrantScenarioStorage is not None:
            if qdrant_storage:
                self.qdrant_storage = qdrant_storage
            else:
                self.qdrant_storage = QdrantScenarioStorage()
                logger.info("Qdrant storage enabled")

        # EventBus integration (опционально)
        self.eventbus_client = None
        if enable_eventbus and EVENTBUS_AVAILABLE:
            if eventbus_client:
                self.eventbus_client = eventbus_client
            else:
                self.eventbus_client = ScenarioEventBusClient()
                logger.info("EventBus integration enabled")
        elif enable_eventbus and not EVENTBUS_AVAILABLE:
            logger.warning("EventBus requested but not available")

        # Output to intelligent-core/scenario-intelligence/generated
        if output_base_dir == "generated":
            intelligent_core_path = Path(__file__).parent.parent.parent.parent.parent / "intelligent-core" / "scenario-intelligence"
            self.output_base_dir = intelligent_core_path / "generated"
        else:
            self.output_base_dir = Path(output_base_dir)

        # Generation state
        self.state = {
            "status": "idle",  # idle, running, completed, failed
            "current_level": None,
            "started_at": None,
            "completed_at": None,
            "progress": {
                "l1_platform": {"status": "pending", "generated": 0, "total": 0},
                "l1_applications": {"status": "pending", "generated": 0, "total": 0},
                "l2_subsystems": {"status": "pending", "generated": 0, "total": 0},
                "l3_systems": {"status": "pending", "generated": 0, "total": 0},
                "l4_workflows": {"status": "pending", "generated": 0, "total": 0}
            }
        }

        # Statistics
        self.stats = {
            "total_scenarios": 0,
            "total_time_seconds": 0,
            "by_level": {},
            "errors": []
        }

        logger.info("GenerationManager initialized")

    async def initialize_storages(self):
        """Initialize PostgreSQL, Qdrant, and EventBus if enabled."""
        if self.postgres_storage:
            await self.postgres_storage.initialize()
            logger.info(" PostgreSQL storage initialized")

        if self.qdrant_storage:
            await self.qdrant_storage.initialize()
            logger.info(" Qdrant storage initialized")

        if self.eventbus_client:
            await self.eventbus_client.initialize()
            logger.info(" EventBus client initialized")

    async def close_storages(self):
        """Close storage connections."""
        if self.postgres_storage:
            await self.postgres_storage.close()

        if self.eventbus_client:
            await self.eventbus_client.close()

    async def _save_to_storages(self, scenarios: List[Dict[str, Any]]):
        """
        Save scenarios to PostgreSQL and/or Qdrant.

        Args:
            scenarios: List of scenario IDs to save
        """
        if not scenarios:
            return

        # Получить полные сценарии из registry
        full_scenarios = []
        for scenario_id in scenarios:
            scenario = await self.registry.get_scenario_by_id(scenario_id)
            if scenario:
                full_scenarios.append(scenario)

        if not full_scenarios:
            return

        # Save to PostgreSQL
        if self.postgres_storage:
            try:
                result = await self.postgres_storage.bulk_register(full_scenarios)
                logger.info(f" PostgreSQL: {result['success']} scenarios saved, {result['failed']} failed")
                if result['errors']:
                    for error in result['errors'][:5]:  # First 5 errors
                        logger.error(f"  - {error}")
            except Exception as e:
                logger.error(f" PostgreSQL save failed: {e}")

        # Save to Qdrant
        if self.qdrant_storage:
            try:
                result = await self.qdrant_storage.bulk_register(full_scenarios)
                logger.info(f" Qdrant: {result['success']} scenarios indexed, {result['failed']} failed")
            except Exception as e:
                logger.error(f" Qdrant save failed: {e}")

    async def generate_all(self, levels: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Generate scenarios for all levels.

        Args:
            levels: List of levels to generate (default: all)
                   Options: ["l1_platform", "l1_applications", "l2", "l3", "l4"]

        Returns:
            Generation report with statistics
        """
        self.state["status"] = "running"
        self.state["started_at"] = datetime.utcnow().isoformat()

        # Default to all levels
        if levels is None:
            levels = ["l1_platform", "l1_applications", "l2", "l3", "l4"]

        logger.info(f"Starting complete generation for levels: {levels}")

        # Initialize storages first
        await self.initialize_storages()

        try:
            # L1 Platform Services
            if "l1_platform" in levels:
                scenario_ids = await self._generate_l1_platform()
                await self._save_to_storages(scenario_ids)

            # L1 Applications
            if "l1_applications" in levels:
                scenario_ids = await self._generate_l1_applications()
                await self._save_to_storages(scenario_ids)

            # L2 Subsystems
            if "l2" in levels:
                scenario_ids = await self._generate_l2_subsystems()
                await self._save_to_storages(scenario_ids)

            # L3 Systems
            if "l3" in levels:
                scenario_ids = await self._generate_l3_systems()
                await self._save_to_storages(scenario_ids)

            # L4 Workflows
            if "l4" in levels:
                scenario_ids = await self._generate_l4_workflows()
                await self._save_to_storages(scenario_ids)

            self.state["status"] = "completed"

        except Exception as e:
            logger.error(f"Generation failed: {e}", exc_info=True)
            self.state["status"] = "failed"
            self.stats["errors"].append(str(e))

        finally:
            self.state["completed_at"] = datetime.utcnow().isoformat()
            self._calculate_final_statistics()
            # Close storages
            await self.close_storages()

        return self._generate_report()

    async def _generate_l1_platform(self) -> List[str]:
        """Generate L1 Platform Service scenarios.

        Returns:
            List of generated scenario IDs
        """
        logger.info("\n" + "="*70)
        logger.info("GENERATING L1 PLATFORM SERVICES")
        logger.info("="*70)

        self.state["current_level"] = "l1_platform"
        self.state["progress"]["l1_platform"]["status"] = "running"

        try:
            generator = L1PlatformGenerator(
                self.loader,
                self.registry,
                output_dir=str(self.output_base_dir / "l1" / "services")
            )

            generated_ids = await generator.generate_all()

            # Update progress
            gen_stats = generator.get_statistics()
            self.state["progress"]["l1_platform"].update({
                "status": "completed",
                "generated": gen_stats["generated"],
                "total": gen_stats["total"],
                "failed": gen_stats["failed"]
            })

            self.stats["by_level"]["l1_platform"] = gen_stats
            self.stats["total_scenarios"] += gen_stats["generated"]

            logger.info(f" L1 Platform: {gen_stats['generated']}/{gen_stats['total']} scenarios")

            # Publish EventBus event
            if self.eventbus_client and EVENTBUS_AVAILABLE:
                try:
                    event = create_scenario_generated_event(
                        scenario_ids=generated_ids,
                        level=ScenarioLevel.L1_PLATFORM,
                        generator="l1_platform",
                        trigger=ScenarioGenerationTrigger.MANUAL,
                        metadata={
                            "stats": gen_stats,
                            "total": gen_stats["total"],
                            "failed": gen_stats["failed"]
                        }
                    )
                    await self.eventbus_client.publish_scenario_generated(event)
                except Exception as e:
                    logger.warning(f"Failed to publish EventBus event: {e}")

            return generated_ids

        except Exception as e:
            logger.error(f"L1 Platform generation failed: {e}", exc_info=True)
            self.state["progress"]["l1_platform"]["status"] = "failed"
            self.stats["errors"].append(f"L1 Platform: {str(e)}")
            raise

    async def _generate_l1_applications(self) -> List[str]:
        """Generate L1 Application scenarios.

        Returns:
            List of generated scenario IDs
        """
        logger.info("\n" + "="*70)
        logger.info("GENERATING L1 APPLICATIONS")
        logger.info("="*70)

        self.state["current_level"] = "l1_applications"
        self.state["progress"]["l1_applications"]["status"] = "running"

        try:
            generator = L1ApplicationGenerator(
                self.loader,
                self.registry,
                output_dir=str(self.output_base_dir / "l1" / "applications")
            )

            generated_ids = await generator.generate_all()

            # Update progress
            gen_stats = generator.get_statistics()
            self.state["progress"]["l1_applications"].update({
                "status": "completed",
                "generated": gen_stats["generated"],
                "total": gen_stats["total"],
                "failed": gen_stats["failed"]
            })

            self.stats["by_level"]["l1_applications"] = gen_stats
            self.stats["total_scenarios"] += gen_stats["generated"]

            logger.info(f" L1 Applications: {gen_stats['generated']}/{gen_stats['total']} scenarios")

            return generated_ids

        except Exception as e:
            logger.error(f"L1 Applications generation failed: {e}", exc_info=True)
            self.state["progress"]["l1_applications"]["status"] = "failed"
            self.stats["errors"].append(f"L1 Applications: {str(e)}")
            raise

    async def _generate_l2_subsystems(self) -> List[str]:
        """Generate L2 Subsystem scenarios.

        Returns:
            List of generated scenario IDs
        """
        logger.info("\n" + "="*70)
        logger.info("GENERATING L2 SUBSYSTEMS")
        logger.info("="*70)

        self.state["current_level"] = "l2_subsystems"
        self.state["progress"]["l2_subsystems"]["status"] = "running"

        try:
            generator = L2SubsystemGenerator(
                self.loader,
                self.registry,
                output_dir=str(self.output_base_dir / "l2")
            )

            generated_ids = await generator.generate_all()

            # Update progress
            gen_stats = generator.get_statistics()
            self.state["progress"]["l2_subsystems"].update({
                "status": "completed",
                "generated": gen_stats["generated"],
                "total": gen_stats["total"],
                "failed": gen_stats["failed"]
            })

            self.stats["by_level"]["l2_subsystems"] = gen_stats
            self.stats["total_scenarios"] += gen_stats["generated"]

            logger.info(f" L2 Subsystems: {gen_stats['generated']}/{gen_stats['total']} scenarios")

            return generated_ids

        except Exception as e:
            logger.error(f"L2 Subsystems generation failed: {e}", exc_info=True)
            self.state["progress"]["l2_subsystems"]["status"] = "failed"
            self.stats["errors"].append(f"L2 Subsystems: {str(e)}")
            raise

    async def _generate_l3_systems(self) -> List[str]:
        """Generate L3 System scenarios.

        Returns:
            List of generated scenario IDs
        """
        logger.info("\n" + "="*70)
        logger.info("GENERATING L3 SYSTEMS")
        logger.info("="*70)

        self.state["current_level"] = "l3_systems"
        self.state["progress"]["l3_systems"]["status"] = "running"

        try:
            generator = L3SystemGenerator(
                self.loader,
                self.registry,
                output_dir=str(self.output_base_dir / "l3")
            )

            generated_ids = await generator.generate_all()

            # Update progress
            gen_stats = generator.get_statistics()
            self.state["progress"]["l3_systems"].update({
                "status": "completed",
                "generated": gen_stats["generated"],
                "total": gen_stats["total"],
                "failed": gen_stats["failed"]
            })

            self.stats["by_level"]["l3_systems"] = gen_stats
            self.stats["total_scenarios"] += gen_stats["generated"]

            logger.info(f" L3 Systems: {gen_stats['generated']}/{gen_stats['total']} scenarios")

            return generated_ids

        except Exception as e:
            logger.error(f"L3 Systems generation failed: {e}", exc_info=True)
            self.state["progress"]["l3_systems"]["status"] = "failed"
            self.stats["errors"].append(f"L3 Systems: {str(e)}")
            raise

    async def _generate_l4_workflows(self) -> List[str]:
        """Generate L4 Workflow scenarios (AI-powered).

        Returns:
            List of generated scenario IDs
        """
        logger.info("\n" + "="*70)
        logger.info("GENERATING L4 WORKFLOWS (AI-POWERED)")
        logger.info("="*70)

        self.state["current_level"] = "l4_workflows"
        self.state["progress"]["l4_workflows"]["status"] = "running"

        try:
            generator = L4WorkflowGenerator(
                self.loader,
                self.registry,
                output_dir=str(self.output_base_dir / "l4")
            )

            generated_ids = await generator.generate_all()

            # Update progress
            gen_stats = generator.get_statistics()
            self.state["progress"]["l4_workflows"].update({
                "status": "completed",
                "generated": gen_stats["generated"],
                "total": gen_stats["total"],
                "failed": gen_stats["failed"]
            })

            self.stats["by_level"]["l4_workflows"] = gen_stats
            self.stats["total_scenarios"] += gen_stats["generated"]

            logger.info(f" L4 Workflows: {gen_stats['generated']}/{gen_stats['total']} scenarios")

            # Publish EventBus event
            if self.eventbus_client and EVENTBUS_AVAILABLE:
                try:
                    event = create_scenario_generated_event(
                        scenario_ids=generated_ids,
                        level=ScenarioLevel.L4_WORKFLOW,
                        generator="l4_workflow",
                        trigger=ScenarioGenerationTrigger.MANUAL,
                        metadata={
                            "stats": gen_stats,
                            "total": gen_stats["total"],
                            "failed": gen_stats["failed"]
                        }
                    )
                    await self.eventbus_client.publish_scenario_generated(event)
                except Exception as e:
                    logger.warning(f"Failed to publish EventBus event: {e}")

            return generated_ids

        except Exception as e:
            logger.error(f"L4 Workflows generation failed: {e}", exc_info=True)
            self.state["progress"]["l4_workflows"]["status"] = "failed"
            self.stats["errors"].append(f"L4 Workflows: {str(e)}")
            raise

    def _calculate_final_statistics(self):
        """Calculate final generation statistics."""
        if self.state["started_at"] and self.state["completed_at"]:
            started = datetime.fromisoformat(self.state["started_at"])
            completed = datetime.fromisoformat(self.state["completed_at"])
            self.stats["total_time_seconds"] = (completed - started).total_seconds()

    def _generate_report(self) -> Dict[str, Any]:
        """
        Generate final report.

        Returns:
            Report dictionary with all statistics
        """
        return {
            "status": self.state["status"],
            "started_at": self.state["started_at"],
            "completed_at": self.state["completed_at"],
            "duration_seconds": self.stats["total_time_seconds"],
            "total_scenarios_generated": self.stats["total_scenarios"],
            "progress": self.state["progress"],
            "statistics_by_level": self.stats["by_level"],
            "errors": self.stats["errors"],
            "registry_stats": None  # Will be filled if registry available
        }

    async def get_progress(self) -> Dict[str, Any]:
        """
        Get current generation progress.

        Returns:
            Current state and progress
        """
        return {
            "status": self.state["status"],
            "current_level": self.state["current_level"],
            "progress": self.state["progress"],
            "total_scenarios": self.stats["total_scenarios"]
        }

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get generation statistics.

        Returns:
            Statistics dictionary
        """
        return self.stats.copy()


async def main():
    """Run generation manager standalone."""
    print("="*70)
    print("SCENARIO GENERATION MANAGER")
    print("="*70)

    # Initialize manager
    manager = GenerationManager(
        output_base_dir="generated"
    )

    # Generate all scenarios
    report = await manager.generate_all(levels=["l1_platform"])

    # Print report
    print("\n" + "="*70)
    print("GENERATION REPORT")
    print("="*70)
    print(f"Status: {report['status']}")
    print(f"Duration: {report['duration_seconds']:.1f}s")
    print(f"Total scenarios: {report['total_scenarios_generated']}")
    print("\nProgress by level:")
    for level, progress in report['progress'].items():
        print(f"  {level}: {progress['status']} "
              f"({progress.get('generated', 0)}/{progress.get('total', 0)})")

    if report['errors']:
        print(f"\n️  Errors ({len(report['errors'])}):")
        for error in report['errors']:
            print(f"  - {error}")

    print("\n" + "="*70)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
