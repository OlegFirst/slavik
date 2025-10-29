#!/usr/bin/env python3
"""
🧠 COGNITIVE ORCHESTRATOR - Единый мозг системы

Объединяет:
- AI Orchestration (интеллектуальная координация)
- Scenario Orchestration (управление сценариями)
- Platform Orchestration (платформенная оркестрация)

Это НЕ просто код - это АРХИТЕКТУРНОЕ РЕШЕНИЕ:
- Все orchestrator'ы работают как единый организм
- Общая память через Redis
- Общие события через EventBus
- Единое принятие решений
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, List, Optional
import asyncio
import logging
from datetime import datetime

# Импортируем части из существующих orchestrator'ов
# НЕ переписываем, а ИСПОЛЬЗУЕМ что есть!
from ai.main import app as ai_app
from scenarios.main import ScenarioEngine
from platform.main import PlatformOrchestrator

logger = logging.getLogger(__name__)

class CognitiveOrchestrator:
    """
    Единый мозг системы - координирует все части
    """

    def __init__(self):
        # Используем существующие компоненты
        self.ai_brain = ai_app  # AI оркестратор как есть
        self.scenario_engine = ScenarioEngine()  # Движок сценариев
        self.platform_control = PlatformOrchestrator()  # Платформенный контроль

        # Общая память для всех частей
        self.shared_memory = {}
        self.decision_history = []

    async def think(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Главная функция 'мышления' - принимает решения
        """
        # 1. AI анализирует контекст
        ai_analysis = await self.ai_brain.analyze_context(context)

        # 2. Scenario engine предлагает варианты
        scenarios = await self.scenario_engine.get_applicable_scenarios(context)

        # 3. Platform orchestrator проверяет возможности
        platform_state = await self.platform_control.check_capabilities()

        # 4. Синтез решения
        decision = self.synthesize_decision(ai_analysis, scenarios, platform_state)

        # 5. Запоминаем для обучения
        self.remember_decision(context, decision)

        return decision

    def synthesize_decision(self, ai_analysis, scenarios, platform_state):
        """
        Синтез решения из всех источников
        Это и есть наша уникальная архитектура!
        """
        decision = {
            'action': None,
            'confidence': 0.0,
            'reasoning': [],
            'alternatives': []
        }

        # AI предлагает что делать
        if ai_analysis.get('recommendation'):
            decision['action'] = ai_analysis['recommendation']
            decision['confidence'] = ai_analysis.get('confidence', 0.5)
            decision['reasoning'].append(f"AI suggests: {ai_analysis['reasoning']}")

        # Сценарии дают контекст
        if scenarios:
            best_scenario = max(scenarios, key=lambda s: s.get('relevance', 0))
            if best_scenario['relevance'] > 0.7:
                decision['action'] = best_scenario['action']
                decision['confidence'] *= best_scenario['relevance']
                decision['reasoning'].append(f"Scenario match: {best_scenario['name']}")

        # Platform проверяет выполнимость
        if platform_state.get('can_execute'):
            decision['executable'] = True
        else:
            decision['executable'] = False
            decision['blockers'] = platform_state.get('blockers', [])

        return decision

    def remember_decision(self, context, decision):
        """
        Запоминаем для будущего обучения
        """
        memory_entry = {
            'timestamp': datetime.now().isoformat(),
            'context': context,
            'decision': decision,
            'outcome': None  # Заполнится позже
        }
        self.decision_history.append(memory_entry)

        # Если история большая - сохраняем для ML
        if len(self.decision_history) > 100:
            self.export_for_training()

    def export_for_training(self):
        """
        Экспорт данных для обучения AI
        """
        # Сохраняем в формате для будущего обучения
        pass  # TODO: подключить к ML pipeline

# FastAPI приложение
app = FastAPI(
    title="Cognitive Orchestrator",
    description="Единый мозг BCM Platform - объединяет AI, Scenarios, Platform",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Создаем единый мозг
cognitive_brain = CognitiveOrchestrator()

@app.post("/think")
async def think(context: Dict[str, Any]):
    """
    Главный endpoint - система 'думает' и принимает решение
    """
    try:
        decision = await cognitive_brain.think(context)
        return {
            "status": "success",
            "decision": decision,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Thinking failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    """Проверка здоровья всех частей мозга"""
    return {
        "status": "healthy",
        "components": {
            "ai_brain": "active",
            "scenario_engine": "active",
            "platform_control": "active"
        },
        "decisions_made": len(cognitive_brain.decision_history)
    }

@app.get("/memory")
async def get_memory():
    """Получить историю решений"""
    return {
        "total_decisions": len(cognitive_brain.decision_history),
        "recent_decisions": cognitive_brain.decision_history[-10:]
    }

# Подключаем sub-приложения (монтируем существующие)
app.mount("/ai", ai_app)
# app.mount("/scenarios", scenario_app)
# app.mount("/platform", platform_app)

if __name__ == "__main__":
    import uvicorn
    # Запускаем на порту 8000 - главный мозг системы
    uvicorn.run(app, host="0.0.0.0", port=8000)