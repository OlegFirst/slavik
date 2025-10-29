"""
BCM Platform AI Prompts Library
Integrates assistant documentation as functional prompts
"""

import json
import os
from typing import Dict, Any
from pathlib import Path

class BCMPromptsLibrary:
    """Central prompts library for all AI services"""

    def __init__(self):
        self.prompts_path = Path(__file__).parent
        self.assistant_docs_path = Path(__file__).parent.parent.parent.parent / "docs" / "assistant_docs_v2"
        self.prompts = self._load_all_prompts()

    def _load_all_prompts(self) -> Dict[str, Any]:
        """Load prompts from assistant docs and local files"""
        prompts = {}

        # Load from assistant_docs_v2 (your existing prompts)
        try:
            system_prompt_file = self.assistant_docs_path / "assistant_prompts" / "system_prompt.md"
            if system_prompt_file.exists():
                with open(system_prompt_file, 'r', encoding='utf-8') as f:
                    prompts['system_prompt'] = f.read()

            guardrails_file = self.assistant_docs_path / "assistant_prompts" / "guardrails.md"
            if guardrails_file.exists():
                with open(guardrails_file, 'r', encoding='utf-8') as f:
                    prompts['guardrails'] = f.read()

            intents_file = self.assistant_docs_path / "assistant_prompts" / "intents.md"
            if intents_file.exists():
                with open(intents_file, 'r', encoding='utf-8') as f:
                    prompts['intents'] = f.read()

        except Exception as e:
            print(f"Warning: Could not load assistant docs: {e}")

        # Load workflow-specific prompts
        prompts.update(self._load_workflow_prompts())

        return prompts

    def _load_workflow_prompts(self) -> Dict[str, str]:
        """Load workflow-specific prompts"""
        return {
            "incident_analysis": """
            Вы - эксперт по анализу инцидентов BCM платформы.

            КОНТЕКСТ: Анализ инцидента для системы непрерывности бизнеса
            ЗАДАЧА: Провести комплексный анализ и дать рекомендации

            АНАЛИЗИРУЙТЕ:
            1. Категория инцидента (operational, security, technology, natural)
            2. Уровень критичности (low, medium, high, critical)
            3. Затронутые бизнес-процессы
            4. Оценка времени восстановления
            5. Необходимые ресурсы для устранения

            ПРЕДОСТАВЬТЕ:
            - Классификация инцидента
            - План реагирования
            - Команда реагирования
            - Временные рамки
            - Уроки для предотвращения

            ФОРМАТ: Структурированный JSON с четкими действиями
            """,

            "bia_generation": """
            Вы - специалист по анализу влияния на бизнес (BIA).

            КОНТЕКСТ: Создание BIA для критического бизнес-процесса
            ЦЕЛЬ: Определить RTO, RPO и план восстановления

            АНАЛИЗИРУЙТЕ:
            1. Финансовое влияние остановки процесса
            2. Операционные зависимости
            3. Регуляторные требования
            4. Репутационные риски

            РАССЧИТАЙТЕ:
            - Maximum Tolerable Period of Disruption (MTPD)
            - Recovery Time Objective (RTO)
            - Recovery Point Objective (RPO)
            - Minimum resources needed

            УЧТИТЕ российские требования и ISO 22301:2019
            """,

            "pdca_guidance": """
            Вы - PDCA-навигатор для непрерывного улучшения BCM.

            ФАЗА: {current_phase}
            КОНТЕКСТ: {business_context}

            PLAN: Анализ текущего состояния, планирование улучшений
            DO: Контроль реализации, мониторинг прогресса
            CHECK: Анализ результатов, сбор метрик
            ACT: Внедрение улучшений, корректировка процессов

            ПРЕДЛОЖИТЕ:
            - Следующий логический шаг
            - Необходимые ресурсы
            - Критерии успеха
            - Потенциальные риски

            ОСНОВЫВАЙТЕСЬ на данных KPI и событиях системы
            """,

            "scenario_planning": """
            Вы - эксперт по планированию сценариев BCM.

            ЗАДАЧА: Создание реалистичных сценариев нарушений

            ГЕНЕРИРУЙТЕ сценарии учитывая:
            1. Отраслевые угрозы
            2. Географические факторы
            3. Сезонные особенности
            4. Технологические зависимости
            5. Цепочки поставок

            ДЛЯ КАЖДОГО СЦЕНАРИЯ:
            - Триггерное событие
            - Временная шкала развития
            - Каскадные эффекты
            - Влияние на ресурсы
            - Сложность восстановления

            ФОРМАТ: Детальные сценарии с количественными оценками
            """
        }

    def get_prompt(self, prompt_name: str, **kwargs) -> str:
        """Get prompt with variable substitution"""
        prompt_template = self.prompts.get(prompt_name, "")
        return prompt_template.format(**kwargs)

    def get_system_prompt(self) -> str:
        """Get main system prompt for assistant"""
        return self.prompts.get('system_prompt', 'You are a BCM platform assistant.')

    def get_guardrails(self) -> str:
        """Get safety guardrails"""
        return self.prompts.get('guardrails', '')

    def list_available_prompts(self) -> list:
        """List all available prompts"""
        return list(self.prompts.keys())

# Global instance
bcm_prompts = BCMPromptsLibrary()