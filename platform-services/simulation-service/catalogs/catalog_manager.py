"""
Catalog Manager for Simulation Templates

Manages loading, searching, and updating simulation templates from:
- Built-in templates (/catalogs/simulation-templates/)
- User-created templates (database)
- AI-generated templates
- Community-contributed templates
- External sources
"""

import logging
import json
from pathlib import Path
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from models.pydantic_models import Scenario, ScenarioCategory
from storage.repositories.scenario_repository import ScenarioRepository

logger = logging.getLogger(__name__)


class CatalogManager:
    """
    Manages simulation template catalog

    Sources:
    1. Built-in templates (JSON files)
    2. Database (user-created)
    3. AI-generated (via scenario generator)
    4. Community (via Community Intelligence)
    5. External (imported)
    """

    def __init__(
        self,
        scenario_repo: ScenarioRepository,
        catalog_path: Optional[Path] = None
    ):
        """
        Initialize catalog manager

        Args:
            scenario_repo: Scenario repository
            catalog_path: Path to catalog directory (default: /catalogs/simulation-templates/)
        """
        self.scenario_repo = scenario_repo

        if catalog_path is None:
            # Default path
            catalog_path = Path(__file__).parent.parent.parent.parent.parent.parent / "catalogs" / "simulation-templates"

        self.catalog_path = Path(catalog_path)
        self._builtin_templates: Dict[str, Dict] = {}
        self._loaded = False

    async def load_builtin_templates(self) -> int:
        """
        Load built-in templates from catalog directory

        Returns:
            Number of templates loaded
        """
        if not self.catalog_path.exists():
            logger.warning(f"Catalog path does not exist: {self.catalog_path}")
            return 0

        count = 0
        try:
            for template_file in self.catalog_path.glob("*.json"):
                try:
                    with open(template_file, 'r', encoding='utf-8') as f:
                        template_data = json.load(f)
                        template_id = template_data.get('id')

                        if template_id:
                            self._builtin_templates[template_id] = template_data
                            count += 1
                            logger.debug(f"Loaded template: {template_id}")
                        else:
                            logger.warning(f"Template missing id: {template_file.name}")

                except Exception as e:
                    logger.error(f"Failed to load template {template_file.name}: {e}")

            self._loaded = True
            logger.info(f"Loaded {count} built-in templates from {self.catalog_path}")
            return count

        except Exception as e:
            logger.error(f"Failed to load built-in templates: {e}")
            return 0

    async def get_template_by_id(
        self,
        session: AsyncSession,
        template_id: str
    ) -> Optional[Dict]:
        """
        Get template by ID (searches all sources)

        Args:
            session: Database session
            template_id: Template ID

        Returns:
            Template data or None
        """
        # 1. Check built-in templates
        if template_id in self._builtin_templates:
            return self._builtin_templates[template_id]

        # 2. Check database (user-created, AI-generated, community)
        scenario = await self.scenario_repo.get_by_id(session, template_id)
        if scenario:
            return self._scenario_to_template(scenario)

        return None

    async def search_templates(
        self,
        session: AsyncSession,
        query: Optional[str] = None,
        category: Optional[ScenarioCategory] = None,
        tags: Optional[List[str]] = None,
        min_quality: float = 0.0,
        source: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict]:
        """
        Search templates across all sources

        Args:
            session: Database session
            query: Search query (matches name, description)
            category: Filter by category
            tags: Filter by tags
            min_quality: Minimum quality score
            source: Filter by source (builtin, ai_generated, community, user)
            limit: Maximum results

        Returns:
            List of matching templates
        """
        results = []

        # 1. Search built-in templates
        if not source or source == "builtin":
            for template_data in self._builtin_templates.values():
                if self._matches_criteria(template_data, query, category, tags):
                    results.append(template_data)

        # 2. Search database
        if not source or source in ["ai_generated", "community", "user", "custom"]:
            db_scenarios = await self._search_database(
                session, category, tags, min_quality, limit
            )

            for scenario in db_scenarios:
                # Filter by source if specified
                if source and scenario.source != source:
                    continue

                # Filter by query if specified
                if query and not self._matches_query(scenario, query):
                    continue

                results.append(self._scenario_to_template(scenario))

        # Sort by quality/usage
        results.sort(key=lambda x: (
            x.get('metadata', {}).get('average_rating') or 0,
            x.get('metadata', {}).get('usage_count', 0)
        ), reverse=True)

        return results[:limit]

    async def create_template_from_scenario(
        self,
        session: AsyncSession,
        scenario: Scenario,
        source: str = "custom"
    ) -> str:
        """
        Create template from scenario and store in database

        Args:
            session: Database session
            scenario: Scenario instance
            source: Template source (ai_generated, custom, community)

        Returns:
            Template ID
        """
        # Update source
        scenario.source = source

        # Save to database
        scenario_orm = await self.scenario_repo.create(session, scenario)

        logger.info(f"Created template {scenario_orm.id} from {source}")
        return scenario_orm.id

    async def import_from_community(
        self,
        session: AsyncSession,
        community_template_id: str,
        community_client
    ) -> Optional[str]:
        """
        Import template from Community Intelligence

        Args:
            session: Database session
            community_template_id: Community template ID
            community_client: Community Intelligence client

        Returns:
            Local template ID or None
        """
        try:
            # Fetch from community
            template_data = await community_client.get_template(community_template_id)

            if not template_data:
                logger.warning(f"Community template not found: {community_template_id}")
                return None

            # Convert to Scenario
            scenario = self._template_to_scenario(template_data, source="community")

            # Save to database
            scenario_orm = await self.scenario_repo.create(session, scenario)

            logger.info(f"Imported community template: {scenario_orm.id}")
            return scenario_orm.id

        except Exception as e:
            logger.error(f"Failed to import community template: {e}")
            return None

    async def export_to_catalog(
        self,
        session: AsyncSession,
        template_id: str,
        filename: Optional[str] = None
    ) -> bool:
        """
        Export template to catalog directory (for sharing/backup)

        Args:
            session: Database session
            template_id: Template ID
            filename: Optional custom filename

        Returns:
            True if exported successfully
        """
        try:
            # Get template
            template = await self.get_template_by_id(session, template_id)
            if not template:
                logger.error(f"Template not found: {template_id}")
                return False

            # Generate filename
            if not filename:
                filename = f"{template_id}.json"

            # Export path
            export_path = self.catalog_path / filename

            # Write JSON
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(template, f, indent=2, ensure_ascii=False)

            logger.info(f"Exported template to: {export_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to export template: {e}")
            return False

    async def get_statistics(self, session: AsyncSession) -> Dict:
        """
        Get catalog statistics

        Returns:
            Statistics dictionary
        """
        # Built-in count
        builtin_count = len(self._builtin_templates)

        # Database counts by source
        # TODO: Implement count by source in repository
        total_db = await self.scenario_repo.count(session)

        return {
            "total_templates": builtin_count + total_db,
            "builtin": builtin_count,
            "database": total_db,
            "sources": {
                "builtin": builtin_count,
                "custom": 0,  # TODO
                "ai_generated": 0,  # TODO
                "community": 0,  # TODO
                "external": 0  # TODO
            }
        }

    # Helper methods

    def _matches_criteria(
        self,
        template: Dict,
        query: Optional[str],
        category: Optional[ScenarioCategory],
        tags: Optional[List[str]]
    ) -> bool:
        """Check if template matches search criteria"""

        # Category filter
        if category and template.get('category') != category.value:
            return False

        # Tags filter
        if tags:
            template_tags = template.get('metadata', {}).get('tags', [])
            if not any(tag in template_tags for tag in tags):
                return False

        # Query filter
        if query:
            query_lower = query.lower()
            name = template.get('name', '').lower()
            description = template.get('description', '').lower()

            if query_lower not in name and query_lower not in description:
                return False

        return True

    def _matches_query(self, scenario, query: str) -> bool:
        """Check if scenario matches query"""
        query_lower = query.lower()
        return (
            query_lower in scenario.name.lower() or
            query_lower in scenario.description.lower()
        )

    async def _search_database(
        self,
        session: AsyncSession,
        category: Optional[ScenarioCategory],
        tags: Optional[List[str]],
        min_quality: float,
        limit: int
    ) -> List:
        """Search database scenarios"""

        if category:
            # Search by category
            return await self.scenario_repo.list_by_category(
                session, category, min_quality, limit
            )
        elif tags:
            # Search by tags
            return await self.scenario_repo.search_by_tags(
                session, tags, None, limit
            )
        else:
            # List all
            return await self.scenario_repo.list_all(session, limit)

    def _scenario_to_template(self, scenario) -> Dict:
        """Convert Scenario ORM to template dict"""
        return {
            "id": scenario.id,
            "name": scenario.name,
            "description": scenario.description,
            "category": scenario.category.value,
            "exercise_type": scenario.exercise_type.value,
            "difficulty": scenario.complexity_level,
            "duration_minutes": scenario.duration_minutes,

            "parameters": {
                "configurable_fields": [],  # TODO: Extract from scenario
                "default_values": {},
                "constraints": {}
            },

            "scenario": {
                "incidents": scenario.incidents,
                "affected_processes": scenario.affected_processes,
                "success_criteria": scenario.success_criteria
            },

            "resources": {
                "required_participants": scenario.required_participants,
                "available_resources": scenario.available_resources
            },

            "metadata": {
                "created_by": scenario.source,
                "version": "1.0",
                "usage_count": scenario.usage_count,
                "average_rating": scenario.quality_score,
                "tags": scenario.tags,
                "last_updated": scenario.created_at.isoformat()
            }
        }

    def _template_to_scenario(self, template: Dict, source: str = "external") -> Scenario:
        """Convert template dict to Scenario model"""
        from models.pydantic_models import ExerciseType

        return Scenario(
            id=template.get('id', ''),
            name=template['name'],
            description=template['description'],
            category=ScenarioCategory(template['category']),
            exercise_type=ExerciseType(template.get('exercise_type', 'simulation')),
            duration_minutes=template['duration_minutes'],
            complexity_level=template.get('difficulty', 1),

            incidents=template.get('scenario', {}).get('incidents', []),
            affected_processes=template.get('scenario', {}).get('affected_processes', []),
            success_criteria=template.get('scenario', {}).get('success_criteria', []),
            key_metrics=template.get('scenario', {}).get('key_metrics', []),

            required_participants=template.get('resources', {}).get('required_participants', 1),
            available_resources=template.get('resources', {}).get('available_resources', {}),

            tags=template.get('metadata', {}).get('tags', []),
            source=source,
            quality_score=template.get('metadata', {}).get('average_rating'),
            usage_count=template.get('metadata', {}).get('usage_count', 0),

            created_by="system",
            organization_id="system"
        )
