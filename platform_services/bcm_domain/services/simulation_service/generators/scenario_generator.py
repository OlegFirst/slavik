"""
Scenario Generator - Universal Specification Builder

UNIVERSAL solution for generating simulation specifications from multiple sources:
- /catalogs data (for internal platform testing)
- Digital Twin data (when available)
- User profile data
- Uploaded documents
- Natural language input
- Template customization

Supports multiple generation modes:
- AI-powered generation from natural language
- Template-based customization
- Data-driven generation from metrics
- Hybrid approach combining multiple sources
"""

import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
import json

from models.pydantic_models import (
    TaskSpecification,
    Scenario,
    ScenarioCategory,
    ExerciseType,
    EngineType
)
from integration.foundation_client import AIFoundationClient
from integration.orchestrator_client import AIOrchestratorClient
from catalogs.catalog_manager import CatalogManager
from config.settings import Settings

logger = logging.getLogger(__name__)


class ScenarioGenerator:
    """
    Universal scenario and specification generator

    Input Sources (UNIVERSAL):
    1. Natural language description
    2. /catalogs data (platform knowledge)
    3. Digital Twin (organization model) - when available
    4. User profile data
    5. Uploaded documents (policies, procedures)
    6. Existing templates (customization)
    7. Historical data (past simulations)

    Generation Modes:
    - AI-powered: LLM generates from description
    - Template-based: Customize existing template
    - Data-driven: Generate from metrics/data
    - Hybrid: Combine multiple approaches

    Tool Selection:
    - User can select modeling tool/engine
    - System recommends based on task
    - Automatic selection based on requirements
    """

    def __init__(
        self,
        settings: Settings,
        ai_foundation_client: AIFoundationClient,
        ai_orchestrator_client: AIOrchestratorClient,
        catalog_manager: CatalogManager
    ):
        """
        Initialize scenario generator

        Args:
            settings: Application settings
            ai_foundation_client: AI Foundation client for LLM/RAG
            ai_orchestrator_client: AI Orchestrator client for validation
            catalog_manager: Catalog manager for templates
        """
        self.settings = settings
        self.ai_foundation = ai_foundation_client
        self.ai_orchestrator = ai_orchestrator_client
        self.catalog_manager = catalog_manager

        # Load catalog knowledge
        self.catalog_path = Path(settings.catalog_path) if hasattr(settings, 'catalog_path') else None

    # ========================================================================
    # MAIN GENERATION METHODS
    # ========================================================================

    async def generate_from_natural_language(
        self,
        user_input: str,
        organization_context: Optional[Dict] = None,
        constraints: Optional[Dict] = None,
        user_preferences: Optional[Dict] = None,
        session = None
    ) -> Optional[TaskSpecification]:
        """
        Generate specification from natural language description

        UNIVERSAL approach that can use:
        - Catalogs data for context
        - Digital Twin data (if available)
        - User profile
        - Uploaded documents

        Args:
            user_input: Natural language description
            organization_context: Organization data from Digital Twin/profile/catalogs
            constraints: User-specified constraints
            user_preferences: User preferences (engine preference, duration, etc.)
            session: Database session for catalog access

        Returns:
            Generated TaskSpecification or None
        """
        logger.info("Generating specification from natural language")

        try:
            # Step 1: Gather context from multiple sources
            context = await self._gather_context(
                user_input,
                organization_context,
                session
            )

            # Step 2: Use LLM to generate specification
            specification = await self.ai_foundation.generate_specification(
                user_input=user_input,
                organization_context=context,
                constraints=constraints,
                reference_data=context.get("reference_data")
            )

            if not specification:
                logger.error("LLM generation failed")
                return None

            # Step 3: Apply user preferences
            if user_preferences:
                specification = self._apply_preferences(specification, user_preferences)

            # Step 4: Validate with AI Orchestrator
            validation = await self.ai_orchestrator.validate_specification(
                specification=specification,
                context=context
            )

            if not validation.get("is_valid", False):
                logger.warning(f"Generated specification has issues: {validation.get('suggestions')}")
                # Apply suggestions to improve
                specification = await self._apply_suggestions(specification, validation)

            # Step 5: Recommend engine (user can override)
            if not specification.engine_preference:
                engine_recommendation = await self.ai_foundation.recommend_engine(specification)
                if engine_recommendation:
                    specification.engine_preference = EngineType(
                        engine_recommendation.get("recommended_engine", "simpy")
                    )

            logger.info(f"Specification generated successfully: {specification.id}")
            return specification

        except Exception as e:
            logger.error(f"Specification generation failed: {e}")
            return None

    async def generate_from_template(
        self,
        template_id: str,
        customization: Dict[str, Any],
        organization_context: Optional[Dict] = None,
        session = None
    ) -> Optional[TaskSpecification]:
        """
        Generate specification by customizing existing template

        Args:
            template_id: Template ID (from catalog or community)
            customization: Customization parameters
            organization_context: Organization context
            session: Database session

        Returns:
            Generated TaskSpecification or None
        """
        logger.info(f"Generating specification from template: {template_id}")

        try:
            # Get template
            template = await self.catalog_manager.get_template_by_id(session, template_id)
            if not template:
                logger.error(f"Template not found: {template_id}")
                return None

            # Convert template to specification with customizations
            specification = self._template_to_specification(
                template,
                customization,
                organization_context
            )

            # Validate
            validation = await self.ai_orchestrator.validate_specification(
                specification=specification,
                context={"template_id": template_id}
            )

            if validation.get("is_valid", False):
                logger.info(f"Specification generated from template: {specification.id}")
                return specification
            else:
                logger.warning(f"Template customization has issues: {validation.get('suggestions')}")
                return specification  # Return anyway, let user decide

        except Exception as e:
            logger.error(f"Template-based generation failed: {e}")
            return None

    async def generate_from_data(
        self,
        data_sources: Dict[str, Any],
        generation_goal: str,
        organization_context: Optional[Dict] = None,
        session = None
    ) -> Optional[TaskSpecification]:
        """
        Generate specification from data/metrics

        Data sources can include:
        - Uploaded documents (BIA, risk assessments)
        - Historical metrics
        - Digital Twin data
        - Catalog knowledge

        Args:
            data_sources: Dictionary of data sources
            generation_goal: What to generate (e.g., "test BIA process")
            organization_context: Organization context
            session: Database session

        Returns:
            Generated TaskSpecification or None
        """
        logger.info("Generating specification from data sources")

        try:
            # Extract key information from data
            extracted_data = await self._extract_data(data_sources)

            # Use LLM to synthesize specification
            user_input = f"{generation_goal}\n\nBased on provided data:\n{json.dumps(extracted_data, indent=2)}"

            specification = await self.generate_from_natural_language(
                user_input=user_input,
                organization_context=organization_context,
                session=session
            )

            return specification

        except Exception as e:
            logger.error(f"Data-driven generation failed: {e}")
            return None

    async def generate_scenario(
        self,
        specification: TaskSpecification,
        session = None
    ) -> Optional[Scenario]:
        """
        Generate detailed scenario from specification

        Uses:
        - Similar scenarios from catalog
        - AI generation for unique scenarios
        - Template customization

        Args:
            specification: Task specification
            session: Database session

        Returns:
            Generated Scenario or None
        """
        logger.info("Generating scenario from specification")

        try:
            # Step 1: Search for similar scenarios
            similar = await self.catalog_manager.search_templates(
                session=session,
                query=specification.goal,
                limit=5
            )

            # Step 2: If good match found, customize it
            if similar and similar[0].get('metadata', {}).get('average_rating', 0) >= 8.0:
                logger.info(f"Using similar scenario as base: {similar[0]['id']}")
                return self._customize_scenario(similar[0], specification)

            # Step 3: Otherwise, generate new scenario with AI
            logger.info("Generating new scenario with AI")
            scenario_data = await self._ai_generate_scenario(specification)

            if scenario_data:
                scenario = Scenario(**scenario_data)
                return scenario

            return None

        except Exception as e:
            logger.error(f"Scenario generation failed: {e}")
            return None

    # ========================================================================
    # TOOL/ENGINE SELECTION
    # ========================================================================

    async def recommend_tools(
        self,
        specification: TaskSpecification
    ) -> Dict[str, Any]:
        """
        Recommend modeling tools and engines

        User can:
        - Accept recommendation
        - Choose from alternatives
        - Specify their own preference

        Args:
            specification: Task specification

        Returns:
            Tool recommendations with alternatives
        """
        logger.info("Recommending modeling tools")

        # Get AI recommendation
        engine_rec = await self.ai_foundation.recommend_engine(specification)

        # Get Orchestrator recommendation
        orchestrator_rec = await self.ai_orchestrator.suggest_engine(specification)

        # Build recommendation with alternatives
        recommendation = {
            "primary_recommendation": {
                "engine": engine_rec.get("recommended_engine", "simpy"),
                "confidence": engine_rec.get("confidence", 0.5),
                "reasoning": engine_rec.get("reasoning", "")
            },
            "alternatives": [
                {
                    "engine": "jaamsim",
                    "suitable_for": "Complex discrete event simulations with visualization",
                    "pros": ["Detailed visualization", "Industrial-grade", "Complex workflows"],
                    "cons": ["Steeper learning curve", "Longer setup time"]
                },
                {
                    "engine": "simpy",
                    "suitable_for": "Process-based simulations",
                    "pros": ["Easy to use", "Fast execution", "Good for resource modeling"],
                    "cons": ["Limited built-in visualization"]
                },
                {
                    "engine": "monte_carlo",
                    "suitable_for": "Risk analysis and probabilistic scenarios",
                    "pros": ["Statistical rigor", "Uncertainty quantification"],
                    "cons": ["Requires probability distributions"]
                },
                {
                    "engine": "what_if",
                    "suitable_for": "Quick impact analysis",
                    "pros": ["Very fast", "Simple scenarios", "Decision support"],
                    "cons": ["Limited complexity"]
                },
                {
                    "engine": "workflow",
                    "suitable_for": "Platform workflow testing",
                    "pros": ["Real platform integration", "Actual workflow execution"],
                    "cons": ["Requires workflow definitions"]
                }
            ],
            "orchestrator_suggestion": orchestrator_rec,
            "user_can_override": True
        }

        return recommendation

    def select_tool(
        self,
        specification: TaskSpecification,
        user_choice: Optional[str] = None
    ) -> EngineType:
        """
        Select final tool/engine

        Args:
            specification: Task specification
            user_choice: User's engine choice (overrides recommendation)

        Returns:
            Selected engine type
        """
        if user_choice:
            try:
                return EngineType(user_choice)
            except ValueError:
                logger.warning(f"Invalid user choice: {user_choice}, using preference")

        if specification.engine_preference:
            return specification.engine_preference

        # Default
        return EngineType.SIMPY

    # ========================================================================
    # CONTEXT GATHERING (UNIVERSAL)
    # ========================================================================

    async def _gather_context(
        self,
        user_input: str,
        organization_context: Optional[Dict],
        session
    ) -> Dict[str, Any]:
        """
        Gather context from multiple sources

        Sources:
        1. Catalog knowledge (/catalogs)
        2. Digital Twin (if available)
        3. User profile
        4. Similar scenarios
        5. Domain knowledge
        """
        context = {
            "catalog_knowledge": {},
            "digital_twin": {},
            "similar_scenarios": [],
            "domain_knowledge": [],
            "reference_data": {}
        }

        # 1. Catalog knowledge
        if self.catalog_path and self.catalog_path.exists():
            context["catalog_knowledge"] = self._load_catalog_context()

        # 2. Digital Twin data (if provided)
        if organization_context and "digital_twin" in organization_context:
            context["digital_twin"] = organization_context["digital_twin"]

        # 3. Search similar scenarios
        similar = await self.ai_foundation.rag_search_scenarios(
            query=user_input,
            context=organization_context,
            limit=5
        )
        context["similar_scenarios"] = similar

        # 4. Domain knowledge
        # Extract domain from user input or organization context
        domain = self._extract_domain(user_input, organization_context)
        if domain:
            domain_knowledge = await self.ai_foundation.retrieve_domain_knowledge(
                domain=domain,
                query=user_input,
                limit=3
            )
            context["domain_knowledge"] = domain_knowledge

        return context

    def _load_catalog_context(self) -> Dict:
        """Load context from catalogs"""
        catalog_data = {
            "available_templates": [],
            "modeling_approaches": [],
            "platform_capabilities": []
        }

        try:
            # Load README or index if exists
            readme_path = self.catalog_path / "simulation-templates" / "README.md"
            if readme_path.exists():
                with open(readme_path, 'r', encoding='utf-8') as f:
                    catalog_data["description"] = f.read()

            # Count available templates
            template_count = len(list((self.catalog_path / "simulation-templates").glob("*.json")))
            catalog_data["template_count"] = template_count

        except Exception as e:
            logger.warning(f"Failed to load catalog context: {e}")

        return catalog_data

    def _extract_domain(
        self,
        user_input: str,
        organization_context: Optional[Dict]
    ) -> Optional[str]:
        """Extract domain from input"""
        # Simple keyword matching
        domains = {
            "cyber": ["cyber", "ransomware", "hacking", "malware"],
            "disaster_recovery": ["disaster", "recovery", "failover", "datacenter"],
            "pandemic": ["pandemic", "disease", "epidemic", "health"],
            "supply_chain": ["supply", "vendor", "supplier", "logistics"]
        }

        user_input_lower = user_input.lower()
        for domain, keywords in domains.items():
            if any(kw in user_input_lower for kw in keywords):
                return domain

        return None

    # ========================================================================
    # HELPER METHODS
    # ========================================================================

    def _apply_preferences(
        self,
        specification: TaskSpecification,
        preferences: Dict[str, Any]
    ) -> TaskSpecification:
        """Apply user preferences to specification"""
        if "max_duration" in preferences:
            specification.max_duration = preferences["max_duration"]

        if "engine_preference" in preferences:
            specification.engine_preference = EngineType(preferences["engine_preference"])

        if "complexity_level" in preferences:
            specification.constraints["complexity_level"] = preferences["complexity_level"]

        return specification

    async def _apply_suggestions(
        self,
        specification: TaskSpecification,
        validation: Dict
    ) -> TaskSpecification:
        """Apply validation suggestions to improve specification"""
        suggestions = validation.get("suggestions", [])

        # Use LLM to enhance based on suggestions
        if suggestions:
            enhanced = await self.ai_foundation.enhance_specification(
                specification=specification,
                enhancement_type="auto"
            )
            if enhanced:
                return enhanced

        return specification

    def _template_to_specification(
        self,
        template: Dict,
        customization: Dict[str, Any],
        organization_context: Optional[Dict]
    ) -> TaskSpecification:
        """Convert template to specification with customizations"""
        spec_data = {
            "goal": customization.get("goal", template.get("name", "")),
            "constraints": template.get("parameters", {}).get("default_values", {}),
            "context": {
                "template_id": template["id"],
                "category": template.get("category"),
                **customization.get("context", {})
            },
            "expected_outcomes": template.get("scenario", {}).get("success_criteria", []),
            "max_duration": template.get("duration_minutes", 60) * 60,
            "created_by": customization.get("created_by", "user"),
            "organization_id": customization.get("organization_id", "")
        }

        # Apply customizations
        spec_data.update(customization)

        return TaskSpecification(**spec_data)

    def _customize_scenario(
        self,
        base_scenario: Dict,
        specification: TaskSpecification
    ) -> Scenario:
        """Customize scenario based on specification"""
        # Start with base scenario data
        scenario_data = base_scenario.copy()

        # Customize with specification data
        scenario_data["name"] = specification.goal[:100]
        scenario_data["description"] = specification.goal

        return Scenario(**scenario_data)

    async def _ai_generate_scenario(
        self,
        specification: TaskSpecification
    ) -> Optional[Dict]:
        """Use AI to generate completely new scenario"""
        # This would call LLM to generate scenario structure
        # For now, return a basic structure

        scenario_data = {
            "name": specification.goal[:100],
            "description": specification.goal,
            "category": self._infer_category(specification),
            "exercise_type": ExerciseType.SIMULATION,
            "duration_minutes": specification.max_duration // 60,
            "complexity_level": 3,

            "incidents": [],
            "affected_processes": [],
            "success_criteria": specification.expected_outcomes or [],
            "key_metrics": [],

            "required_participants": 1,
            "available_resources": {},

            "tags": [],
            "source": "ai_generated",
            "created_by": specification.created_by,
            "organization_id": specification.organization_id
        }

        return scenario_data

    def _infer_category(self, specification: TaskSpecification) -> ScenarioCategory:
        """Infer category from specification"""
        goal_lower = specification.goal.lower()

        if any(kw in goal_lower for kw in ["cyber", "ransomware", "hack"]):
            return ScenarioCategory.CYBER_SECURITY
        elif any(kw in goal_lower for kw in ["disaster", "recovery"]):
            return ScenarioCategory.DISASTER_RECOVERY
        elif any(kw in goal_lower for kw in ["pandemic", "disease"]):
            return ScenarioCategory.PANDEMIC
        elif any(kw in goal_lower for kw in ["supply", "vendor"]):
            return ScenarioCategory.SUPPLY_CHAIN
        else:
            return ScenarioCategory.OPERATIONAL

    async def _extract_data(self, data_sources: Dict[str, Any]) -> Dict:
        """Extract relevant information from data sources"""
        extracted = {
            "metrics": {},
            "processes": [],
            "risks": [],
            "resources": {}
        }

        # Extract from different source types
        for source_type, source_data in data_sources.items():
            if source_type == "documents":
                # Parse documents
                pass
            elif source_type == "metrics":
                extracted["metrics"] = source_data
            elif source_type == "digital_twin":
                extracted["processes"] = source_data.get("processes", [])
                extracted["resources"] = source_data.get("resources", {})

        return extracted
