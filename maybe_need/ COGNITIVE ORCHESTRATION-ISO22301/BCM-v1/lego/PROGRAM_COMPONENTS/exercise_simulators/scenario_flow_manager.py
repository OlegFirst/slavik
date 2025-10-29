# -*- coding: utf-8 -*-
"""
Scenario Flow Manager
Управляет потоком AI-генерированных сценариев от создания до исполнения
"""

import asyncio
import httpx
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
import os

from ai_scenario_generator import AIScenarioGenerator, GeneratedScenario, ScenarioParameters

logger = logging.getLogger(__name__)

class ScenarioFlowManager:
    """Управляет полным жизненным циклом AI-сценариев"""

    def __init__(self):
        self.ai_generator = AIScenarioGenerator()
        self.odoo_url = os.getenv("ODOO_URL", "http://odoo:8069")
        self.jaamsim_templates_dir = Path("/opt/jaamsim/templates")
        self.scenarios_dir = Path("/app/scenarios")
        self.scenarios_dir.mkdir(exist_ok=True)

    async def create_and_deploy_scenario(self, params: ScenarioParameters) -> Dict[str, Any]:
        """Полный цикл: Генерация → Сохранение в Odoo → Подготовка для симуляции"""

        logger.info(f"Starting scenario creation: {params.category} - complexity {params.complexity}")

        # Шаг 1: AI генерация сценария
        scenario = await self.ai_generator.generate_scenario(params)

        # Шаг 2: Сохранение в BCM Scenario Hub (Odoo)
        odoo_scenario_id = await self._save_to_odoo_scenario_hub(scenario)

        # Шаг 3: Создание JaamSim конфигурации (если нужно)
        jaamsim_file = None
        if scenario.jaamsim_config:
            jaamsim_file = await self._create_jaamsim_file(scenario, odoo_scenario_id)

        # Шаг 4: Подготовка NICS setup (если нужно)
        nics_setup = scenario.nics_setup

        # Шаг 5: Создание exercise record для выполнения
        exercise_id = await self._create_exercise_record(scenario, odoo_scenario_id, jaamsim_file)

        return {
            "status": "success",
            "scenario_id": odoo_scenario_id,
            "exercise_id": exercise_id,
            "scenario_title": scenario.title,
            "jaamsim_file": str(jaamsim_file) if jaamsim_file else None,
            "nics_setup": nics_setup,
            "ai_generated": True,
            "created_at": datetime.now().isoformat()
        }

    async def _save_to_odoo_scenario_hub(self, scenario: GeneratedScenario) -> str:
        """Сохраняет AI-сценарий в Odoo BCM Scenario Hub"""

        # Конвертируем в формат Odoo
        odoo_data = {
            "title": scenario.title,
            "category": scenario.category,
            "level": "full" if scenario.scenario_type == "simulation" else "tabletop",
            "content_md": self._format_scenario_content(scenario),
            "meta_description": scenario.description,
            "meta_duration": self._extract_duration(scenario),
            "meta_participants": self._extract_participants(scenario),
            "is_published": False,  # Начинаем как черновик
            "is_ai_generated": True,
            "ai_generation_params": {
                "complexity": getattr(scenario, 'complexity', 3),
                "generated_at": datetime.now().isoformat(),
                "ai_model": "gemma3:latest"
            }
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.odoo_url}/api/v1/bcm_scenario_hub/scenarios",
                    json=odoo_data,
                    headers={"Content-Type": "application/json"}
                )

                if response.status_code == 201:
                    result = response.json()
                    scenario_id = result.get('id')
                    logger.info(f"Scenario saved to Odoo: {scenario_id}")
                    return str(scenario_id)
                else:
                    logger.error(f"Failed to save scenario to Odoo: {response.status_code}")
                    raise Exception(f"Odoo save failed: {response.text}")

        except Exception as e:
            logger.error(f"Error saving to Odoo: {e}")
            # Fallback: сохраняем локально
            return await self._save_locally(scenario)

    def _format_scenario_content(self, scenario: GeneratedScenario) -> str:
        """Форматирует сценарий в Markdown для Odoo"""

        content = f"""# {scenario.title}

## Описание
{scenario.description}

## Временная шкала

"""

        for event in scenario.timeline:
            time = event.get('time', 'N/A')
            description = event.get('event', 'Event description')
            event_type = event.get('type', 'action')

            content += f"**{time}** - {description} _{event_type}_\n\n"

        content += "\n## Инжекты упражнения\n\n"

        for inject in scenario.injects:
            inject_type = inject.get('type', 'notification')
            inject_content = inject.get('content', 'Inject content')
            timing = inject.get('timing', 'During exercise')

            content += f"### {inject_type.title()} ({timing})\n{inject_content}\n\n"

        content += "\n## Критерии успеха\n\n"

        for metric in scenario.success_metrics:
            content += f"- {metric}\n"

        if scenario.jaamsim_config:
            content += "\n## JaamSim Configuration\n\n```\n"
            content += scenario.jaamsim_config[:500] + "...\n```\n"

        return content

    async def _create_jaamsim_file(self, scenario: GeneratedScenario, scenario_id: str) -> Path:
        """Создает JaamSim файл конфигурации"""

        filename = f"ai_generated_{scenario_id}_{scenario.category}.cfg"
        jaamsim_file = self.jaamsim_templates_dir / filename

        # Убеждаемся что директория существует
        self.jaamsim_templates_dir.mkdir(parents=True, exist_ok=True)

        # Записываем конфигурацию
        with open(jaamsim_file, 'w', encoding='utf-8') as f:
            f.write(f"# AI Generated JaamSim Configuration\n")
            f.write(f"# Scenario: {scenario.title}\n")
            f.write(f"# Generated: {datetime.now().isoformat()}\n")
            f.write(f"# Category: {scenario.category}\n\n")
            f.write(scenario.jaamsim_config)

        logger.info(f"JaamSim file created: {jaamsim_file}")
        return jaamsim_file

    async def _create_exercise_record(self, scenario: GeneratedScenario, scenario_id: str, jaamsim_file: Optional[Path]) -> str:
        """Создает запись упражнения для выполнения"""

        exercise_data = {
            "scenario_id": scenario_id,
            "title": f"Exercise: {scenario.title}",
            "exercise_type": scenario.scenario_type,
            "status": "planned",
            "configuration": {
                "jaamsim_file": str(jaamsim_file) if jaamsim_file else None,
                "nics_setup": scenario.nics_setup,
                "timeline": scenario.timeline,
                "injects": scenario.injects,
                "success_metrics": scenario.success_metrics
            },
            "scheduled_date": None,  # Будет назначено позже
            "created_by": "AI_GENERATOR",
            "ai_generated": True
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.odoo_url}/api/v1/bcm_exercises",
                    json=exercise_data,
                    headers={"Content-Type": "application/json"}
                )

                if response.status_code == 201:
                    result = response.json()
                    exercise_id = result.get('id')
                    logger.info(f"Exercise record created: {exercise_id}")
                    return str(exercise_id)
                else:
                    logger.error(f"Failed to create exercise record: {response.status_code}")
                    raise Exception(f"Exercise creation failed: {response.text}")

        except Exception as e:
            logger.error(f"Error creating exercise: {e}")
            # Fallback: сохраняем локально
            exercise_id = f"local_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            local_file = self.scenarios_dir / f"exercise_{exercise_id}.json"

            with open(local_file, 'w', encoding='utf-8') as f:
                json.dump(exercise_data, f, indent=2, ensure_ascii=False)

            return exercise_id

    async def _save_locally(self, scenario: GeneratedScenario) -> str:
        """Fallback: локальное сохранение сценария"""

        scenario_id = f"local_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        local_file = self.scenarios_dir / f"scenario_{scenario_id}.json"

        scenario_data = {
            "id": scenario_id,
            "title": scenario.title,
            "description": scenario.description,
            "category": scenario.category,
            "scenario_type": scenario.scenario_type,
            "timeline": scenario.timeline,
            "injects": scenario.injects,
            "success_metrics": scenario.success_metrics,
            "jaamsim_config": scenario.jaamsim_config,
            "nics_setup": scenario.nics_setup,
            "created_at": datetime.now().isoformat(),
            "ai_generated": True
        }

        with open(local_file, 'w', encoding='utf-8') as f:
            json.dump(scenario_data, f, indent=2, ensure_ascii=False)

        logger.info(f"Scenario saved locally: {local_file}")
        return scenario_id

    def _extract_duration(self, scenario: GeneratedScenario) -> int:
        """Извлекает продолжительность упражнения из временной шкалы"""

        if not scenario.timeline:
            return 4  # Default 4 hours

        try:
            last_event = scenario.timeline[-1]
            time_str = last_event.get('time', '4:00')
            # Простая логика парсинга времени
            if ':' in time_str:
                hours = int(time_str.split(':')[0])
                return max(hours, 1)
        except:
            pass

        return 4

    def _extract_participants(self, scenario: GeneratedScenario) -> int:
        """Извлекает количество участников из сценария"""

        # Пытаемся найти упоминания участников в описании
        description = scenario.description.lower()

        if '20' in description or 'twenty' in description:
            return 20
        elif '15' in description or 'fifteen' in description:
            return 15
        elif '10' in description or 'ten' in description:
            return 10

        return 8  # Default

    async def get_scenario_status(self, scenario_id: str) -> Dict[str, Any]:
        """Получает статус сценария"""

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.odoo_url}/api/v1/bcm_scenario_hub/scenarios/{scenario_id}"
                )

                if response.status_code == 200:
                    return response.json()

        except Exception as e:
            logger.error(f"Error getting scenario status: {e}")

        # Fallback: проверяем локальные файлы
        local_file = self.scenarios_dir / f"scenario_{scenario_id}.json"
        if local_file.exists():
            with open(local_file, 'r', encoding='utf-8') as f:
                return json.load(f)

        return {"error": "Scenario not found"}

    async def list_available_scenarios(self) -> List[Dict[str, Any]]:
        """Получает список доступных сценариев"""

        scenarios = []

        # Получаем из Odoo
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.odoo_url}/api/v1/bcm_scenario_hub/scenarios?ai_generated=true"
                )

                if response.status_code == 200:
                    scenarios.extend(response.json().get('results', []))

        except Exception as e:
            logger.error(f"Error getting scenarios from Odoo: {e}")

        # Добавляем локальные
        for local_file in self.scenarios_dir.glob("scenario_*.json"):
            try:
                with open(local_file, 'r', encoding='utf-8') as f:
                    scenario = json.load(f)
                    scenario['source'] = 'local'
                    scenarios.append(scenario)
            except Exception as e:
                logger.error(f"Error reading local scenario {local_file}: {e}")

        return scenarios

# Global instance
scenario_flow_manager = ScenarioFlowManager()