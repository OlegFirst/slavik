"""
Scenario Flow Manager
=====================

Manages the full lifecycle of AI-generated scenarios from creation to execution.

Orchestrates:
- AI scenario generation
- Odoo BCM Scenario Hub integration
- JaamSim configuration file creation
- Exercise record creation
- NICS setup preparation
- Local fallback storage

Adapted from: /simulation/exercise_simulators/scenario_flow_manager.py
"""

import asyncio
import httpx
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
import os

from ..core.ai_scenario_generator import (
    AIScenarioGenerator,
    GeneratedScenario,
    ScenarioParameters,
    ScenarioType
)

logger = logging.getLogger(__name__)


class ScenarioFlowManager:
    """
    Manages the complete lifecycle of AI-generated BCM exercise scenarios

    Flow:
    1. AI generation via AIScenarioGenerator
    2. Save to Odoo BCM Scenario Hub (or local fallback)
    3. Create JaamSim configuration files
    4. Prepare NICS setup
    5. Create exercise records
    6. Track scenario status
    """

    def __init__(
        self,
        ai_orchestrator_url: str = None,
        model_runner_url: str = None,
        odoo_url: str = None,
        jaamsim_templates_dir: str = None,
        scenarios_dir: str = None
    ):
        """
        Initialize Scenario Flow Manager

        Args:
            ai_orchestrator_url: AI Orchestrator service URL
            model_runner_url: Model Runner service URL
            odoo_url: Odoo BCM Hub URL
            jaamsim_templates_dir: Directory for JaamSim templates
            scenarios_dir: Directory for local scenario storage
        """
        self.ai_generator = AIScenarioGenerator(
            ai_orchestrator_url=ai_orchestrator_url,
            model_runner_url=model_runner_url
        )

        self.odoo_url = odoo_url or os.getenv("ODOO_URL", "http://odoo:8069")

        self.jaamsim_templates_dir = Path(
            jaamsim_templates_dir or os.getenv(
                "JAAMSIM_TEMPLATES_DIR",
                "/opt/jaamsim/templates"
            )
        )

        self.scenarios_dir = Path(
            scenarios_dir or os.getenv(
                "SCENARIOS_DIR",
                "/tmp/bcm_scenarios"
            )
        )

        # Create directories if needed
        self.scenarios_dir.mkdir(parents=True, exist_ok=True)

    async def create_and_deploy_scenario(
        self,
        params: ScenarioParameters
    ) -> Dict[str, Any]:
        """
        Complete scenario lifecycle: Generation → Storage → Deployment

        Args:
            params: Scenario generation parameters

        Returns:
            Complete deployment result with IDs and file paths
        """
        logger.info(
            f"Starting scenario creation: {params.category} "
            f"(complexity {params.complexity})"
        )

        # Step 1: AI-generate scenario
        scenario = await self.ai_generator.generate_scenario(params)
        logger.info(f"Generated scenario: {scenario.title}")

        # Step 2: Save to BCM Scenario Hub (Odoo) or locally
        scenario_id = await self._save_to_odoo_scenario_hub(scenario, params)

        # Step 3: Create JaamSim configuration file if needed
        jaamsim_file = None
        if scenario.jaamsim_config:
            jaamsim_file = await self._create_jaamsim_file(
                scenario,
                scenario_id
            )

        # Step 4: NICS setup is already in scenario.nics_setup
        nics_setup = scenario.nics_setup

        # Step 5: Create exercise record for execution
        exercise_id = await self._create_exercise_record(
            scenario,
            scenario_id,
            jaamsim_file,
            params
        )

        result = {
            "status": "success",
            "scenario_id": scenario_id,
            "exercise_id": exercise_id,
            "scenario_title": scenario.title,
            "scenario_description": scenario.description,
            "scenario_category": scenario.category,
            "scenario_type": scenario.scenario_type,
            "jaamsim_file": str(jaamsim_file) if jaamsim_file else None,
            "nics_setup_available": nics_setup is not None,
            "nics_setup": nics_setup,
            "timeline_events": len(scenario.timeline),
            "injects_count": len(scenario.injects),
            "success_metrics_count": len(scenario.success_metrics),
            "ai_generated": True,
            "created_at": datetime.now().isoformat()
        }

        logger.info(f"Scenario deployment complete: {scenario_id}")
        return result

    async def _save_to_odoo_scenario_hub(
        self,
        scenario: GeneratedScenario,
        params: ScenarioParameters
    ) -> str:
        """
        Save AI-generated scenario to Odoo BCM Scenario Hub

        Falls back to local storage if Odoo unavailable.
        """
        # Convert to Odoo format
        odoo_data = {
            "title": scenario.title,
            "category": scenario.category,
            "level": (
                "full_scale" if scenario.scenario_type == ScenarioType.FULL_SCALE
                else "simulation" if scenario.scenario_type == ScenarioType.SIMULATION
                else "functional" if scenario.scenario_type == ScenarioType.FUNCTIONAL
                else "tabletop"
            ),
            "content_md": self._format_scenario_content(scenario),
            "meta_description": scenario.description,
            "meta_duration": params.duration_hours,
            "meta_participants": params.participants,
            "meta_complexity": params.complexity,
            "is_published": False,  # Start as draft
            "is_ai_generated": True,
            "ai_generation_params": {
                "complexity": params.complexity,
                "duration_hours": params.duration_hours,
                "participants": params.participants,
                "affected_systems": params.affected_systems,
                "custom_objectives": params.custom_objectives,
                "generated_at": datetime.now().isoformat(),
                "ai_model": "gemma3:latest"
            }
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{self.odoo_url}/api/v1/bcm_scenario_hub/scenarios",
                    json=odoo_data,
                    headers={"Content-Type": "application/json"}
                )

                if response.status_code in (200, 201):
                    result = response.json()
                    scenario_id = str(result.get('id', result.get('scenario_id')))
                    logger.info(f"Scenario saved to Odoo: {scenario_id}")
                    return scenario_id
                else:
                    logger.warning(
                        f"Failed to save scenario to Odoo: {response.status_code}"
                    )
                    raise Exception(f"Odoo save failed: {response.text}")

        except Exception as e:
            logger.warning(f"Error saving to Odoo: {e}. Using local fallback.")
            return await self._save_locally(scenario, params)

    def _format_scenario_content(self, scenario: GeneratedScenario) -> str:
        """
        Format scenario as Markdown for Odoo BCM Scenario Hub
        """
        content = f"""# {scenario.title}

## Description
{scenario.description}

**Category**: {scenario.category}
**Type**: {scenario.scenario_type}

## Timeline

"""

        for event in scenario.timeline:
            time = event.get('time', 'N/A')
            description = event.get('event', 'Event description')
            event_type = event.get('type', 'action')

            content += f"**{time}** - {description} *({event_type})*\n\n"

        content += "\n## Exercise Injects\n\n"

        for inject in scenario.injects:
            inject_type = inject.get('type', 'notification')
            inject_content = inject.get('content', 'Inject content')
            timing = inject.get('timing', 'During exercise')

            content += f"### {inject_type.title()} - {timing}\n{inject_content}\n\n"

        content += "\n## Success Metrics\n\n"

        for metric in scenario.success_metrics:
            content += f"- {metric}\n"

        if scenario.jaamsim_config:
            content += "\n## JaamSim Configuration Available\n\n"
            content += " JaamSim simulation configuration has been generated.\n\n"
            content += "```\n"
            content += scenario.jaamsim_config[:500]
            if len(scenario.jaamsim_config) > 500:
                content += "\n... (truncated)\n"
            content += "```\n"

        if scenario.nics_setup:
            content += "\n## NICS Setup Available\n\n"
            content += " NICS (Incident Command System) setup has been prepared.\n\n"
            content += f"**Incident Type**: {scenario.nics_setup.get('incident_type', 'N/A')}\n\n"

        return content

    async def _create_jaamsim_file(
        self,
        scenario: GeneratedScenario,
        scenario_id: str
    ) -> Path:
        """
        Create JaamSim configuration file on disk
        """
        filename = f"ai_generated_{scenario_id}_{scenario.category}.cfg"
        jaamsim_file = self.jaamsim_templates_dir / filename

        # Ensure directory exists
        self.jaamsim_templates_dir.mkdir(parents=True, exist_ok=True)

        # Write configuration
        with open(jaamsim_file, 'w', encoding='utf-8') as f:
            f.write(f"# AI Generated JaamSim Configuration\n")
            f.write(f"# Scenario: {scenario.title}\n")
            f.write(f"# Generated: {datetime.now().isoformat()}\n")
            f.write(f"# Category: {scenario.category}\n")
            f.write(f"# Scenario ID: {scenario_id}\n\n")
            f.write(scenario.jaamsim_config)

        logger.info(f"JaamSim file created: {jaamsim_file}")
        return jaamsim_file

    async def _create_exercise_record(
        self,
        scenario: GeneratedScenario,
        scenario_id: str,
        jaamsim_file: Optional[Path],
        params: ScenarioParameters
    ) -> str:
        """
        Create exercise record for scenario execution
        """
        exercise_data = {
            "scenario_id": scenario_id,
            "title": f"Exercise: {scenario.title}",
            "exercise_type": scenario.scenario_type,
            "status": "planned",
            "category": scenario.category,
            "complexity": params.complexity,
            "configuration": {
                "jaamsim_file": str(jaamsim_file) if jaamsim_file else None,
                "nics_setup": scenario.nics_setup,
                "timeline": scenario.timeline,
                "injects": scenario.injects,
                "success_metrics": scenario.success_metrics,
                "duration_hours": params.duration_hours,
                "participants_count": params.participants,
                "affected_systems": params.affected_systems,
                "custom_objectives": params.custom_objectives
            },
            "scheduled_date": None,  # Will be set later
            "created_by": "AI_SCENARIO_GENERATOR",
            "ai_generated": True,
            "created_at": datetime.now().isoformat()
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{self.odoo_url}/api/v1/bcm_exercises",
                    json=exercise_data,
                    headers={"Content-Type": "application/json"}
                )

                if response.status_code in (200, 201):
                    result = response.json()
                    exercise_id = str(result.get('id', result.get('exercise_id')))
                    logger.info(f"Exercise record created: {exercise_id}")
                    return exercise_id
                else:
                    logger.warning(
                        f"Failed to create exercise record: {response.status_code}"
                    )
                    raise Exception(f"Exercise creation failed: {response.text}")

        except Exception as e:
            logger.warning(
                f"Error creating exercise in Odoo: {e}. Using local fallback."
            )
            # Fallback: save locally
            exercise_id = f"local_exercise_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            local_file = self.scenarios_dir / f"exercise_{exercise_id}.json"

            with open(local_file, 'w', encoding='utf-8') as f:
                json.dump(exercise_data, f, indent=2, ensure_ascii=False)

            logger.info(f"Exercise saved locally: {local_file}")
            return exercise_id

    async def _save_locally(
        self,
        scenario: GeneratedScenario,
        params: ScenarioParameters
    ) -> str:
        """
        Fallback: Save scenario locally when Odoo unavailable
        """
        scenario_id = f"local_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        local_file = self.scenarios_dir / f"scenario_{scenario_id}.json"

        scenario_data = {
            "id": scenario_id,
            "title": scenario.title,
            "description": scenario.description,
            "category": scenario.category,
            "scenario_type": scenario.scenario_type,
            "complexity": params.complexity,
            "duration_hours": params.duration_hours,
            "participants": params.participants,
            "timeline": scenario.timeline,
            "injects": scenario.injects,
            "success_metrics": scenario.success_metrics,
            "jaamsim_config": scenario.jaamsim_config,
            "nics_setup": scenario.nics_setup,
            "created_at": datetime.now().isoformat(),
            "ai_generated": True,
            "source": "local_fallback"
        }

        with open(local_file, 'w', encoding='utf-8') as f:
            json.dump(scenario_data, f, indent=2, ensure_ascii=False)

        logger.info(f"Scenario saved locally: {local_file}")
        return scenario_id

    async def get_scenario_status(self, scenario_id: str) -> Dict[str, Any]:
        """
        Get scenario status and details

        Args:
            scenario_id: Scenario identifier

        Returns:
            Scenario status and metadata
        """
        # Try Odoo first
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    f"{self.odoo_url}/api/v1/bcm_scenario_hub/scenarios/{scenario_id}"
                )

                if response.status_code == 200:
                    return response.json()

        except Exception as e:
            logger.warning(f"Error getting scenario status from Odoo: {e}")

        # Fallback: check local files
        local_file = self.scenarios_dir / f"scenario_{scenario_id}.json"
        if local_file.exists():
            with open(local_file, 'r', encoding='utf-8') as f:
                return json.load(f)

        return {"error": "Scenario not found", "scenario_id": scenario_id}

    async def list_available_scenarios(
        self,
        category: Optional[str] = None,
        ai_generated_only: bool = True
    ) -> List[Dict[str, Any]]:
        """
        List all available scenarios

        Args:
            category: Filter by category (optional)
            ai_generated_only: Only include AI-generated scenarios

        Returns:
            List of scenario summaries
        """
        scenarios = []

        # Get from Odoo
        try:
            params = {}
            if ai_generated_only:
                params['ai_generated'] = 'true'
            if category:
                params['category'] = category

            query_string = '&'.join(f"{k}={v}" for k, v in params.items())
            url = f"{self.odoo_url}/api/v1/bcm_scenario_hub/scenarios"
            if query_string:
                url += f"?{query_string}"

            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url)

                if response.status_code == 200:
                    result = response.json()
                    odoo_scenarios = result.get('results', result.get('scenarios', []))
                    scenarios.extend(odoo_scenarios)
                    logger.info(f"Retrieved {len(odoo_scenarios)} scenarios from Odoo")

        except Exception as e:
            logger.warning(f"Error getting scenarios from Odoo: {e}")

        # Add local scenarios
        for local_file in self.scenarios_dir.glob("scenario_*.json"):
            try:
                with open(local_file, 'r', encoding='utf-8') as f:
                    scenario = json.load(f)

                    # Apply filters
                    if ai_generated_only and not scenario.get('ai_generated', False):
                        continue
                    if category and scenario.get('category') != category:
                        continue

                    scenario['source'] = 'local'
                    scenarios.append(scenario)
            except Exception as e:
                logger.error(f"Error reading local scenario {local_file}: {e}")

        logger.info(f"Total scenarios available: {len(scenarios)}")
        return scenarios

    async def delete_scenario(self, scenario_id: str) -> bool:
        """
        Delete a scenario

        Args:
            scenario_id: Scenario identifier

        Returns:
            True if deleted successfully
        """
        deleted = False

        # Try Odoo first
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.delete(
                    f"{self.odoo_url}/api/v1/bcm_scenario_hub/scenarios/{scenario_id}"
                )

                if response.status_code in (200, 204):
                    logger.info(f"Scenario deleted from Odoo: {scenario_id}")
                    deleted = True

        except Exception as e:
            logger.warning(f"Error deleting scenario from Odoo: {e}")

        # Delete local file if exists
        local_file = self.scenarios_dir / f"scenario_{scenario_id}.json"
        if local_file.exists():
            local_file.unlink()
            logger.info(f"Local scenario file deleted: {local_file}")
            deleted = True

        # Delete associated exercise file
        exercise_file = self.scenarios_dir / f"exercise_local_exercise_*.json"
        for ex_file in self.scenarios_dir.glob(f"exercise_*_{scenario_id}.json"):
            ex_file.unlink()
            logger.info(f"Associated exercise file deleted: {ex_file}")

        return deleted
