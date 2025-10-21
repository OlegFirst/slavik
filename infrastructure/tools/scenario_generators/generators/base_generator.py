"""
Base Generator Class

Abstract base class for all scenario generators.
Provides common functionality for template loading, context building, and scenario generation.
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Any, Optional
import yaml

logger = logging.getLogger(__name__)


class BaseGenerator(ABC):
    """
    Abstract base class for scenario generators.

    All generators (L1, L2, L3, L4) inherit from this class.
    """

    def __init__(
        self,
        template_loader,
        registry,
        output_dir: str,
        level: int
    ):
        """
        Initialize base generator.

        Args:
            template_loader: TemplateLoader instance
            registry: ScenarioRegistry instance
            output_dir: Directory for generated scenarios
            level: Scenario level (1, 2, 3, or 4)
        """
        self.loader = template_loader
        self.registry = registry
        self.output_dir = Path(output_dir)
        self.level = level

        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Statistics
        self.stats = {
            "total": 0,
            "generated": 0,
            "failed": 0,
            "skipped": 0
        }

        logger.info(f"{self.__class__.__name__} initialized, output: {self.output_dir}")

    @abstractmethod
    def _get_catalog(self) -> List[Dict[str, Any]]:
        """
        Get catalog of items to generate scenarios for.

        Returns:
            List of catalog items (services, subsystems, systems, etc.)
        """
        pass

    @abstractmethod
    def _build_context(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build context for template from catalog item.

        Args:
            item: Catalog item

        Returns:
            Context dictionary for template placeholder replacement
        """
        pass

    @abstractmethod
    def _get_template_name(self, item: Dict[str, Any]) -> str:
        """
        Get template name for catalog item.

        Args:
            item: Catalog item

        Returns:
            Template filename
        """
        pass

    async def generate_one(self, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Generate scenario for one catalog item.

        Args:
            item: Catalog item

        Returns:
            Generated scenario or None if failed
        """
        try:
            # Build context
            context = self._build_context(item)

            # Get template name
            template_name = self._get_template_name(item)

            # Generate scenario from template
            scenario = self.loader.create_scenario_from_template(
                template_name,
                context,
                validate=True
            )

            # Add metadata
            self._enrich_scenario(scenario, item)

            return scenario

        except Exception as e:
            logger.error(f"Failed to generate scenario for {item.get('name', 'unknown')}: {e}", exc_info=True)
            self.stats["failed"] += 1
            return None

    def _enrich_scenario(self, scenario: Dict[str, Any], item: Dict[str, Any]):
        """
        Enrich scenario with additional metadata.

        Args:
            scenario: Generated scenario
            item: Source catalog item
        """
        # Add category if available
        if "category" in item:
            scenario["meta"]["category"] = item["category"]

        # Add source reference
        scenario["meta"]["source_item"] = item.get("name")

        # Add generation timestamp
        import datetime
        scenario["meta"]["generated_at"] = datetime.datetime.utcnow().isoformat()

    async def generate_all(self) -> List[str]:
        """
        Generate scenarios for all catalog items.

        Returns:
            List of generated scenario IDs
        """
        logger.info(f"Starting {self.__class__.__name__} scenario generation")

        catalog = self._get_catalog()
        self.stats["total"] = len(catalog)

        logger.info(f"Found {len(catalog)} items to generate at level {self.level}")

        generated_ids = []

        for item in catalog:
            try:
                # Generate scenario
                scenario = await self.generate_one(item)

                if scenario is None:
                    continue

                # Register in registry
                success = await self.registry.register(scenario)

                if not success:
                    logger.error(f"Failed to register scenario for {item.get('name')}")
                    self.stats["failed"] += 1
                    continue

                scenario_id = scenario["meta"]["id"]
                generated_ids.append(scenario_id)
                self.stats["generated"] += 1

                # Save to filesystem
                output_file = self._get_output_path(item)
                self._save_scenario_to_file(scenario, output_file)

                logger.info(f" Generated: {item.get('name')} ({scenario_id})")

            except Exception as e:
                logger.error(f" Failed to process {item.get('name', 'unknown')}: {e}", exc_info=True)
                self.stats["failed"] += 1
                continue

        self._log_statistics()

        return generated_ids

    def _get_output_path(self, item: Dict[str, Any]) -> Path:
        """
        Get output file path for scenario.

        Args:
            item: Catalog item

        Returns:
            Output file path
        """
        filename = f"{item.get('name', 'unknown')}.yaml"
        return self.output_dir / filename

    def _save_scenario_to_file(self, scenario: Dict[str, Any], filepath: Path):
        """
        Save scenario to YAML file.

        Args:
            scenario: Scenario dictionary
            filepath: Output file path
        """
        with open(filepath, 'w') as f:
            yaml.dump(scenario, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    def _log_statistics(self):
        """Log generation statistics."""
        logger.info("\n" + "="*70)
        logger.info(f"{self.__class__.__name__} GENERATION COMPLETE")
        logger.info("="*70)
        logger.info(f"Total items:      {self.stats['total']}")
        logger.info(f" Generated:     {self.stats['generated']}")
        logger.info(f" Failed:        {self.stats['failed']}")
        logger.info(f"⏭️  Skipped:       {self.stats['skipped']}")
        logger.info(f"Success rate:     {self.stats['generated'] / max(self.stats['total'], 1) * 100:.1f}%")
        logger.info("="*70)

    def get_statistics(self) -> Dict[str, int]:
        """
        Get generation statistics.

        Returns:
            Statistics dictionary
        """
        return self.stats.copy()
