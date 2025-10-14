# Scenario Auto-Generation Architecture - Full Integration

**Дата**: 2025-10-12
**Версия**: 2.0.0 (с полной интеграцией)

---

## 🎯 Концепция

**Единая система автогенерации сценариев** с полным циклом:

```
SERVICE_CATALOG_DETAILED.yaml
         ↓
    [Generator Engine] ← управляется Project Agent
         ↓
    YAML Scenarios (L1-L4)
         ↓
    ┌────┴────┬──────────┬─────────────┐
    ↓         ↓          ↓             ↓
[PostgreSQL] [Qdrant]  [Registry]  [AI Colleagues]
    ↓         ↓          ↓             ↓
    └─────────┴──────────┴─────────────┘
                 ↓
          [AI Intelligence Core]
     (Predictive, Community, Workflow)
                 ↓
        [Priorities & Feedback]
                 ↓
          [Project Agent]
                 ↓
        [Re-generation cycle]
```

---

## 🏗️ Архитектура

### Компоненты системы:

```
intelligent-core/scenario-intelligence/
├── engines/
│   └── generator_engine.py          # 🆕 Главный движок генерации
│
├── learning/
│   ├── auto_generator.py            # 🆕 ОБНОВЛЕН - полная интеграция
│   ├── pattern_detector.py          # Детектор паттернов
│   └── predictor.py                 # Предсказатель приоритетов
│
├── integration/
│   ├── catalog_adapter.py           # 🆕 SERVICE_CATALOG_DETAILED.yaml
│   ├── project_agent_adapter.py     # 🆕 Project Agent управление
│   ├── ai_colleagues_adapter.py     # 🆕 Распределение на AI коллег
│   ├── intelligence_core_adapter.py # 🆕 Predictive + Community + Workflow
│   ├── orchestrator_adapter.py      # ✅ AI generation (есть)
│   └── incident_adapter.py          # ✅ Real incidents (есть)
│
└── workflows/
    └── autogeneration_workflow.py   # 🆕 Полный цикл генерации
```

---

## 📊 DATA FLOW - Полный цикл

### ЭТАП 1: Source Data (Исходные данные)

```yaml
# /infrastructure/SERVICE_CATALOG_DETAILED.yaml
services:
  - name: bia-service
    port: 8001
    capabilities: ["create_bia", "calculate_impact"]
    dependencies: ["postgresql", "audit-service"]
    kpis:
      - name: bia_creation_time_ms
        threshold_warning: 5000
```

### ЭТАП 2: Catalog Parsing (Парсинг каталога)

```python
# /integration/catalog_adapter.py
catalog = CatalogAdapter()
services = await catalog.load_services()
# → 45 services loaded
```

### ЭТАП 3: Scenario Generation (Генерация сценариев)

```python
# /learning/auto_generator.py
generator = ScenarioAutoGenerator()

# L1 - Module scenarios (из каталога)
l1_scenarios = await generator.generate_l1_from_catalog()
# → 45 L1 scenarios (по одному на сервис)

# L2 - Subsystem scenarios (группировка)
l2_scenarios = await generator.generate_l2_from_subsystems()
# → 8 L2 scenarios (Platform, AI Office, Security, etc)

# L3 - Inter-system scenarios (взаимодействия)
l3_scenarios = await generator.generate_l3_from_dependencies()
# → 10 L3 scenarios

# L4 - User scenarios (AI-powered)
l4_scenarios = await generator.generate_l4_from_orchestrator()
# → AI-generated через Scenario Orchestrator
```

### ЭТАП 4: Multi-Storage Save (Сохранение в 4 места)

```python
# /workflows/autogeneration_workflow.py
workflow = AutoGenerationWorkflow()

for scenario in all_scenarios:
    # 1. PostgreSQL (persistence)
    await db_manager.save_scenario(scenario)

    # 2. Qdrant RAG (semantic search)
    await rag_storage.index_scenario(scenario)

    # 3. In-memory Registry (fast access)
    registry.register(scenario)

    # 4. File system (YAML backup)
    await save_yaml(scenario, f"scenarios/{scenario['meta']['level']}/")
```

### ЭТАП 5: AI Colleagues Distribution (Распределение на коллег)

```python
# /integration/ai_colleagues_adapter.py
colleagues = AIColleaguesAdapter()

# Отправить сценарии всем AI коллегам для изучения
await colleagues.distribute_scenarios(
    scenarios=all_scenarios,
    targets=[
        "mio-manager",       # MIO Manager изучает сценарии
        "analytics-specialist", # Analytics анализирует
        "devops-agent",      # DevOps проверяет инфраструктуру
        "project-agent"      # Project Agent координирует
    ]
)
```

### ЭТАП 6: Intelligence Core Learning (Изучение в AI ядре)

```python
# /integration/intelligence_core_adapter.py
intelligence = IntelligenceCoreAdapter()

# 1. Predictive Service - предсказание failures
predictions = await intelligence.predictive.analyze_scenarios(all_scenarios)
# → Предсказывает какие сценарии могут упасть

# 2. Community Intelligence - коллективное решение
priorities = await intelligence.community.vote_on_priorities(all_scenarios)
# → Голосование AI коллег: что важнее?

# 3. Workflow Intelligence - оптимизация процессов
optimizations = await intelligence.workflow.optimize_execution_order(all_scenarios)
# → Оптимальный порядок выполнения
```

### ЭТАП 7: Priority Calculation (Расчет приоритетов)

```python
# /learning/predictor.py
predictor = ScenarioPredictor()

priorities = predictor.calculate_priorities(
    scenarios=all_scenarios,
    predictions=predictions,        # От Predictive
    community_votes=priorities,     # От Community
    optimizations=optimizations     # От Workflow
)

# Результат:
# {
#   "scenario_id": "l1-bia-service-create-bia",
#   "priority": "HIGH",
#   "confidence": 0.92,
#   "reasons": [
#     "High failure prediction (0.85)",
#     "Critical business value",
#     "Community vote: 8/10"
#   ]
# }
```

### ЭТАП 8: Project Agent Control (Управление)

```python
# /integration/project_agent_adapter.py
project_agent = ProjectAgentAdapter()

# Создать задачи на основе приоритетов
tasks = await project_agent.create_tasks_from_scenarios(
    scenarios=all_scenarios,
    priorities=priorities
)

# Project Agent распределяет работу:
# 1. HIGH priority → немедленное тестирование
# 2. MEDIUM priority → плановое тестирование
# 3. LOW priority → фоновое тестирование

# Отслеживание прогресса
progress = await project_agent.track_scenario_execution()
```

### ЭТАП 9: Feedback Loop (Обратная связь)

```python
# После выполнения сценариев
execution_results = await scenario_engine.get_recent_executions()

# Отправить результаты обратно в систему
await intelligence.predictive.learn_from_results(execution_results)
await intelligence.community.update_voting_weights(execution_results)
await intelligence.workflow.optimize_from_results(execution_results)

# Re-calculate priorities
new_priorities = predictor.recalculate(
    previous_priorities=priorities,
    execution_results=execution_results
)

# Project Agent обновляет задачи
await project_agent.update_task_priorities(new_priorities)
```

---

## 🔧 Реализация

### 1. Generator Engine (Главный движок)

```python
# /engines/generator_engine.py

from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class GeneratorEngine:
    """
    Главный движок генерации сценариев
    Управляется Project Agent
    """

    def __init__(self):
        # Adapters
        from integration.catalog_adapter import get_catalog_adapter
        from integration.project_agent_adapter import get_project_agent_adapter
        from integration.ai_colleagues_adapter import get_ai_colleagues_adapter
        from integration.intelligence_core_adapter import get_intelligence_core_adapter

        self.catalog = get_catalog_adapter()
        self.project_agent = get_project_agent_adapter()
        self.colleagues = get_ai_colleagues_adapter()
        self.intelligence = get_intelligence_core_adapter()

        # Storage
        from storage.registry import get_registry
        from integration.database_integration import get_db_manager
        from integration.rag_integration import get_rag_storage

        self.registry = get_registry()
        self.db = get_db_manager()
        self.rag = get_rag_storage()

        # Learning
        from learning.auto_generator import ScenarioAutoGenerator
        from learning.predictor import ScenarioPredictor

        self.auto_generator = ScenarioAutoGenerator()
        self.predictor = ScenarioPredictor()

    async def run_full_generation_cycle(self) -> Dict[str, Any]:
        """
        Полный цикл генерации сценариев

        Returns:
            Результаты генерации и статистика
        """
        logger.info("=" * 70)
        logger.info("🚀 Starting Full Scenario Generation Cycle")
        logger.info("=" * 70)

        results = {
            "started_at": datetime.now().isoformat(),
            "scenarios_generated": 0,
            "scenarios_saved": 0,
            "ai_colleagues_notified": 0,
            "priorities_calculated": 0,
            "tasks_created": 0,
            "status": "in_progress"
        }

        try:
            # ЭТАП 1: Load catalog
            logger.info("📚 ЭТАП 1: Loading service catalog...")
            services = await self.catalog.load_services()
            logger.info(f"   ✅ Loaded {len(services)} services")

            # ЭТАП 2: Generate scenarios
            logger.info("🔨 ЭТАП 2: Generating scenarios...")

            # L1 - Module scenarios
            l1_scenarios = await self.auto_generator.generate_l1_from_catalog(services)
            logger.info(f"   ✅ Generated {len(l1_scenarios)} L1 scenarios")

            # L2 - Subsystem scenarios
            l2_scenarios = await self.auto_generator.generate_l2_from_subsystems(services)
            logger.info(f"   ✅ Generated {len(l2_scenarios)} L2 scenarios")

            # L3 - Inter-system scenarios
            l3_scenarios = await self.auto_generator.generate_l3_from_dependencies(services)
            logger.info(f"   ✅ Generated {len(l3_scenarios)} L3 scenarios")

            # L4 - User scenarios (AI-powered)
            l4_scenarios = await self.auto_generator.generate_l4_from_orchestrator(
                categories=["cyber", "operational", "natural"]
            )
            logger.info(f"   ✅ Generated {len(l4_scenarios)} L4 scenarios")

            all_scenarios = l1_scenarios + l2_scenarios + l3_scenarios + l4_scenarios
            results["scenarios_generated"] = len(all_scenarios)

            # ЭТАП 3: Save to all storages
            logger.info("💾 ЭТАП 3: Saving to storages...")
            saved_count = await self._save_to_all_storages(all_scenarios)
            results["scenarios_saved"] = saved_count
            logger.info(f"   ✅ Saved {saved_count} scenarios to 4 storages")

            # ЭТАП 4: Distribute to AI colleagues
            logger.info("🤝 ЭТАП 4: Distributing to AI colleagues...")
            notified = await self.colleagues.distribute_scenarios(all_scenarios)
            results["ai_colleagues_notified"] = len(notified)
            logger.info(f"   ✅ Notified {len(notified)} AI colleagues")

            # ЭТАП 5: Send to Intelligence Core
            logger.info("🧠 ЭТАП 5: Sending to Intelligence Core...")

            # Predictive analysis
            predictions = await self.intelligence.predictive.analyze_scenarios(all_scenarios)
            logger.info(f"   ✅ Predictive analysis complete")

            # Community voting
            votes = await self.intelligence.community.vote_on_priorities(all_scenarios)
            logger.info(f"   ✅ Community voting complete")

            # Workflow optimization
            optimizations = await self.intelligence.workflow.optimize_execution_order(all_scenarios)
            logger.info(f"   ✅ Workflow optimization complete")

            # ЭТАП 6: Calculate priorities
            logger.info("🎯 ЭТАП 6: Calculating priorities...")
            priorities = self.predictor.calculate_priorities(
                scenarios=all_scenarios,
                predictions=predictions,
                community_votes=votes,
                optimizations=optimizations
            )
            results["priorities_calculated"] = len(priorities)
            logger.info(f"   ✅ Calculated priorities for {len(priorities)} scenarios")

            # ЭТАП 7: Send to Project Agent
            logger.info("📋 ЭТАП 7: Creating tasks in Project Agent...")
            tasks = await self.project_agent.create_tasks_from_scenarios(
                scenarios=all_scenarios,
                priorities=priorities
            )
            results["tasks_created"] = len(tasks)
            logger.info(f"   ✅ Created {len(tasks)} tasks")

            # ЭТАП 8: Complete
            results["status"] = "success"
            results["completed_at"] = datetime.now().isoformat()

            logger.info("=" * 70)
            logger.info("✅ Full Generation Cycle Complete!")
            logger.info(f"   Scenarios: {results['scenarios_generated']}")
            logger.info(f"   Saved: {results['scenarios_saved']}")
            logger.info(f"   AI Colleagues: {results['ai_colleagues_notified']}")
            logger.info(f"   Tasks: {results['tasks_created']}")
            logger.info("=" * 70)

            return results

        except Exception as e:
            logger.error(f"❌ Generation cycle failed: {e}")
            results["status"] = "failed"
            results["error"] = str(e)
            results["completed_at"] = datetime.now().isoformat()
            raise

    async def _save_to_all_storages(self, scenarios: List[Dict[str, Any]]) -> int:
        """Save scenarios to all 4 storages"""
        saved_count = 0

        for scenario in scenarios:
            try:
                # 1. PostgreSQL
                await self.db.save_scenario(scenario)

                # 2. Qdrant RAG
                await self.rag.index_scenario(scenario)

                # 3. In-memory Registry
                self.registry.register(scenario)

                # 4. YAML file (backup)
                level = scenario["meta"]["level"]
                scenario_id = scenario["meta"]["id"]
                yaml_path = f"/intelligent-core/scenario-intelligence/scenarios/level{level}-generated/{scenario_id}.yaml"
                await self._save_yaml(scenario, yaml_path)

                saved_count += 1

            except Exception as e:
                logger.error(f"Failed to save scenario {scenario.get('meta', {}).get('id')}: {e}")

        return saved_count

    async def _save_yaml(self, scenario: Dict[str, Any], path: str):
        """Save scenario as YAML file"""
        import yaml
        from pathlib import Path

        file_path = Path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, 'w') as f:
            yaml.dump(scenario, f, default_flow_style=False, allow_unicode=True)


# Global instance
_generator_engine = None


def get_generator_engine() -> GeneratorEngine:
    """Get or create global Generator Engine"""
    global _generator_engine

    if _generator_engine is None:
        _generator_engine = GeneratorEngine()

    return _generator_engine
```

---

## 📋 API для Project Agent

```python
# API endpoints для управления из Project Agent

from fastapi import APIRouter
from engines.generator_engine import get_generator_engine

router = APIRouter(prefix="/generator", tags=["generator"])


@router.post("/run-full-cycle")
async def run_full_generation_cycle():
    """
    Запустить полный цикл генерации сценариев

    Управляется Project Agent
    """
    engine = get_generator_engine()
    results = await engine.run_full_generation_cycle()
    return results


@router.post("/generate-l1")
async def generate_l1_scenarios():
    """Generate только L1 scenarios из SERVICE_CATALOG"""
    engine = get_generator_engine()
    services = await engine.catalog.load_services()
    scenarios = await engine.auto_generator.generate_l1_from_catalog(services)

    # Save to storages
    await engine._save_to_all_storages(scenarios)

    return {"scenarios_generated": len(scenarios)}


@router.post("/regenerate-with-priorities")
async def regenerate_with_priorities(execution_results: Dict):
    """
    Re-generate scenarios на основе execution results

    Feedback loop - система учится и улучшается
    """
    engine = get_generator_engine()

    # Learn from results
    await engine.intelligence.predictive.learn_from_results(execution_results)

    # Recalculate priorities
    new_priorities = engine.predictor.recalculate(execution_results)

    # Update Project Agent tasks
    await engine.project_agent.update_task_priorities(new_priorities)

    return {"priorities_updated": len(new_priorities)}
```

---

## 🔄 Continuous Generation Loop

```python
# Непрерывный цикл генерации и улучшения

async def continuous_generation_loop():
    """
    Непрерывный цикл:
    1. Generate scenarios
    2. Execute scenarios
    3. Collect results
    4. Learn from results
    5. Re-generate with improvements
    6. Repeat
    """
    engine = get_generator_engine()

    while True:
        try:
            # 1. Full generation cycle
            results = await engine.run_full_generation_cycle()

            # 2. Wait for executions (controlled by Project Agent)
            await asyncio.sleep(3600)  # 1 hour

            # 3. Collect execution results
            execution_results = await scenario_engine.get_recent_executions()

            # 4. Learn and improve
            if execution_results:
                # Send to Intelligence Core для learning
                await engine.intelligence.predictive.learn_from_results(execution_results)
                await engine.intelligence.community.update_voting_weights(execution_results)

                # Recalculate priorities
                new_priorities = engine.predictor.recalculate(execution_results)

                # Update Project Agent
                await engine.project_agent.update_task_priorities(new_priorities)

                logger.info(f"✅ Learning cycle complete. Updated {len(new_priorities)} priorities")

        except Exception as e:
            logger.error(f"❌ Continuous loop error: {e}")
            await asyncio.sleep(300)  # 5 min before retry
```

---

## 📊 Метрики и мониторинг

```python
# Prometheus metrics для генератора

from prometheus_client import Counter, Histogram, Gauge

# Generation metrics
scenarios_generated_total = Counter(
    'scenarios_generated_total',
    'Total scenarios generated',
    ['level', 'type']
)

generation_duration_seconds = Histogram(
    'scenario_generation_duration_seconds',
    'Time to generate scenarios',
    ['level']
)

scenarios_in_storage = Gauge(
    'scenarios_in_storage_total',
    'Total scenarios in storage',
    ['storage_type']  # postgresql, qdrant, registry, yaml
)

ai_colleagues_notified = Counter(
    'ai_colleagues_notified_total',
    'AI colleagues notified about scenarios',
    ['colleague_name']
)

priorities_calculated = Histogram(
    'scenario_priority_score',
    'Scenario priority scores',
    ['scenario_level']
)
```

---

**Продолжение следует...**
**Статус**: Архитектура готова, начинаем реализацию?
