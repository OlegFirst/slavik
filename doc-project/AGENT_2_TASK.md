# ТЗ для Агента #2 (Терминал 2)

## Задача
1. Создать 4 Engines + Tools
2. Рефакторинг 10 Analyzers (миграция из ai_organs)

## ЧАСТЬ 1: Engines

### Engines для создания
1. Performance Engine (performance_engine/)
2. Learning Engine (learning_engine/)
3. Scenario Engine (scenario_engine/)
4. Lifecycle Engine (lifecycle_engine/)

### Шаблоны
- `/Users/MD/AI-Platform-ISO/intelligent-core/bcm_ai/engines/base_engine.py` - базовый класс
- `/Users/MD/AI-Platform-ISO/intelligent-core/bcm_ai/engines/risk_engine/risk_engine.py` - пример
- `/Users/MD/AI-Platform-ISO/TZ_AI_BCM_PLATFORM.md` - секция 6.3

### Детали по Engines

#### 1. Performance Engine
**Actions:**
- `analyze_kpis` - анализ KPI
- `identify_trends` - выявление трендов
- `recommend_improvements` - рекомендации по улучшению

**Tools:** `performance_tools.py`
```python
async def get_kpis(org_id: str, period: str) -> list
    # SELECT * FROM monitoring.kpis WHERE org_id=? AND period=?

async def calculate_metrics(kpi_data: dict) -> dict
    # Analytics logic

async def save_performance_report(report: dict) -> str
    # INSERT INTO monitoring.performance_reports
```

#### 2. Learning Engine
**Actions:**
- `assess_training_needs` - оценка потребностей в обучении
- `recommend_training` - рекомендации по обучению
- `track_learning_progress` - отслеживание прогресса

**Tools:** `learning_tools.py`
```python
async def get_training_history(org_id: str) -> list
    # SELECT * FROM learning.training_sessions WHERE org_id=?

async def assess_competency_gaps(org_id: str) -> dict
    # Complex analysis

async def save_learning_plan(plan: dict) -> str
    # INSERT INTO learning.learning_plans
```

#### 3. Scenario Engine
**Actions:**
- `generate_scenario` - генерация сценария
- `adapt_scenario_to_org` - адаптация к организации
- `evaluate_scenario_realism` - оценка реалистичности

**Tools:** `scenario_tools.py`
```python
async def get_historical_scenarios(org_id: str) -> list
    # SELECT * FROM exercises.scenarios WHERE org_id=?

async def save_scenario(scenario_data: dict) -> str
    # INSERT INTO exercises.scenarios

async def get_threat_intelligence(threat_type: str) -> dict
    # External API or DB query
```

#### 4. Lifecycle Engine
**Actions:**
- `monitor_lifecycle_health` - мониторинг здоровья жизненного цикла
- `identify_stagnation` - выявление застоя
- `recommend_next_actions` - рекомендации следующих действий

**Tools:** `lifecycle_tools.py`
```python
async def get_lifecycle_status(org_id: str) -> dict
    # SELECT * FROM monitoring.lifecycle_status WHERE org_id=?

async def get_activity_log(org_id: str, period: str) -> list
    # SELECT * FROM audit.activity_log WHERE org_id=? AND period=?

async def save_health_check(health_data: dict) -> str
    # INSERT INTO monitoring.health_checks
```

## ЧАСТЬ 2: Analyzers (рефакторинг)

### Задача
Мигрировать 10 Analyzers из `/intelligent-core/ai-orchestration/muscles/ai_organs/` в `/intelligent-core/bcm_ai/analyzers/`

### Шаблоны
- `/Users/MD/AI-Platform-ISO/intelligent-core/bcm_ai/analyzers/base_analyzer.py` - базовый класс
- `/Users/MD/AI-Platform-ISO/intelligent-core/bcm_ai/analyzers/risk_analyzer.py` - пример
- `/Users/MD/AI-Platform-ISO/TZ_AI_BCM_PLATFORM.md` - секция 6.4

### Миграция (старое → новое)

```
/ai-orchestration/muscles/ai_organs/risk_advisor.py
  → /bcm_ai/analyzers/risk_analyzer.py  ✅ (уже создан главным Клодом)

/ai-orchestration/muscles/ai_organs/impact_oracle.py
  → /bcm_ai/analyzers/impact_analyzer.py

/ai-orchestration/muscles/ai_organs/compliance_guardian.py
  → /bcm_ai/analyzers/compliance_analyzer.py

/ai-orchestration/muscles/ai_organs/governance_brain.py
  → /bcm_ai/analyzers/governance_analyzer.py

/ai-orchestration/muscles/ai_organs/emergency_response.py
  → /bcm_ai/analyzers/emergency_analyzer.py

/ai-orchestration/muscles/ai_organs/plan_generator.py
  → /bcm_ai/analyzers/planning_analyzer.py

/ai-orchestration/muscles/ai_organs/performance_analyst.py
  → /bcm_ai/analyzers/performance_analyzer.py

/ai-orchestration/muscles/ai_organs/learning_coach.py
  → /bcm_ai/analyzers/learning_analyzer.py

/ai-orchestration/muscles/ai_organs/scenario_creator.py
  → /bcm_ai/analyzers/scenario_analyzer.py

/ai-orchestration/muscles/ai_organs/lifecycle_monitor.py
  → /bcm_ai/analyzers/lifecycle_analyzer.py
```

### Алгоритм рефакторинга

Для каждого Analyzer:

1. **Прочитай старый файл** из `/ai-orchestration/muscles/ai_organs/`
2. **Создай новый файл** в `/bcm_ai/analyzers/`
3. **Примени шаблон:**

```python
from typing import Dict, Any
from .base_analyzer import BaseAnalyzer

class [Name]Analyzer(BaseAnalyzer):
    """[Description]"""

    def _build_system_prompt(self) -> str:
        # Возьми из старого _build_system_prompt() или создай новый
        return """You are [Name] Analyzer..."""

    def _build_user_prompt(self, context: Dict[str, Any]) -> str:
        # Адаптируй логику из старого analyze() метода
        # Используй context вместо прямых параметров
        pass

    def _calculate_confidence(
        self,
        parsed: Dict[str, Any],
        context: Dict[str, Any]
    ) -> float:
        # Базовая логика или специфичная
        score = 0.5
        if parsed.get('insights'):
            score += 0.25
        if parsed.get('recommendations'):
            score += 0.25
        return min(score, 1.0)
```

4. **Сохрани промпты** - возьми лучшие части из старого кода
5. **Убери зависимости** - не используй httpx, Digital Twin, BaseAIOrgan
6. **Unified interface** - только `analyze(context)` метод

### Важно

- **НЕ удаляй старые файлы** - только читай и создавай новые
- **Используй BaseAnalyzer** - не копируй BaseAIOrgan
- **Structured output** - JSON с insights и recommendations
- **Все методы async** - кроме _build_*_prompt()

## Начинай когда готов!

После завершения сообщи: "✅ Agent 2 completed: 4 Engines + 10 Analyzers migrated"
