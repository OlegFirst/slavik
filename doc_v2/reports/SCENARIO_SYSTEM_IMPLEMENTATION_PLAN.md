# 🎬 Система Сценариев - План Реализации

## Зачем это нужно?

### Проблемы без системы сценариев:
- ❌ Сложно тестировать 50+ микросервисов
- ❌ Ручное тестирование интеграций
- ❌ Нет живой документации
- ❌ Регрессии находятся поздно
- ❌ Новые разработчики долго разбираются

### С системой сценариев:
- ✅ Автотесты генерируются из сценариев
- ✅ Документация обновляется автоматически
- ✅ AI может сам находить проблемы
- ✅ Онбординг за 1 час
- ✅ Регрессии находятся сразу

---

## 🏗️ Архитектура

### 4 уровня сценариев:

```
Уровень 1: Модульные сценарии
├── vault-get-secret
├── retention-check-policy
├── archive-export-data
└── partitioning-create-partition

Уровень 2: Системные сценарии
├── data-retention-workflow
├── security-vault-rotation
└── monitoring-alert-flow

Уровень 3: Межсистемные интеграции
├── vault → audit → notification
├── retention → archive → cleanup
└── monitoring → alert → escalation

Уровень 4: Пользовательские workflows
├── analyst-creates-bia
├── admin-manages-users
└── auditor-generates-report
```

---

## 📋 План Реализации

### Фаза 1: Фундамент (1-2 недели)

#### 1.1 Scenario Definition Language (SDL)
```yaml
# scenario-schema.yml
scenario:
  id: string              # уникальный ID
  name: string            # человекочитаемое имя
  level: 1|2|3|4         # уровень сценария
  module: string          # модуль (для уровня 1)
  system: string          # система (для уровня 2)
  systems: [string]       # системы (для уровня 3-4)

  preconditions:          # что должно быть до
    - condition: string
      check: string

  steps:                  # шаги сценария
    - action: string
      module: string
      params: object
      expected: object

  postconditions:         # что должно быть после
    - condition: string
      validate: string

  rollback:               # откат при ошибке
    - action: string
```

#### 1.2 Scenario Engine (выполнение сценариев)
```python
# scenario-engine/engine.py
class ScenarioEngine:
    def load_scenario(self, scenario_id: str) -> Scenario
    def validate_preconditions(self, scenario: Scenario) -> bool
    def execute_step(self, step: Step) -> StepResult
    def validate_postconditions(self, scenario: Scenario) -> bool
    def rollback(self, scenario: Scenario, step_index: int) -> bool
    def generate_report(self, execution: Execution) -> Report
```

#### 1.3 Scenario Storage (хранение в RAG)
```python
# Интеграция с Qdrant
from intelligent_core.ai_foundation.rag import QdrantClient

class ScenarioRAG:
    def store_scenario(self, scenario: Scenario):
        # Сохранить сценарий в Qdrant
        embedding = self.embed(scenario.to_text())
        self.qdrant.upsert(
            collection="scenarios",
            points=[{
                "id": scenario.id,
                "vector": embedding,
                "payload": scenario.to_dict()
            }]
        )

    def find_similar_scenarios(self, query: str) -> List[Scenario]:
        # Найти похожие сценарии
        results = self.qdrant.search(
            collection="scenarios",
            query_vector=self.embed(query),
            limit=5
        )
        return [Scenario.from_dict(r.payload) for r in results]
```

---

### Фаза 2: Базовые Сценарии (1 неделя)

#### 2.1 Модульные сценарии (Уровень 1)

**Vault Module:**
```yaml
# scenarios/level1/vault/get-secret.yml
scenario:
  id: "vault-get-secret"
  name: "Получение секрета из Vault"
  level: 1
  module: "vault"

  preconditions:
    - condition: "vault_accessible"
      check: "curl http://localhost:8062/health"
    - condition: "secret_exists"
      check: "secret 'jwt-secret' exists"

  steps:
    - action: "get_secret"
      params:
        name: "jwt-secret"
      expected:
        status: 200
        value_length: ">= 64"

  postconditions:
    - condition: "secret_returned"
      validate: "response.value != null"
```

**Retention Module:**
```yaml
# scenarios/level1/retention/check-policy.yml
scenario:
  id: "retention-check-policy"
  name: "Проверка политики хранения"
  level: 1
  module: "retention"

  steps:
    - action: "get_policy"
      params:
        schema: "public"
        table: "audit_logs"
      expected:
        retention_days: 365
        archive_days: 90
```

**Archive Module:**
```yaml
# scenarios/level1/archive/export-data.yml
scenario:
  id: "archive-export-data"
  name: "Экспорт данных в архив"
  level: 1
  module: "archive"

  preconditions:
    - condition: "old_data_exists"
      check: "SELECT COUNT(*) FROM public.audit_logs WHERE created_at < NOW() - INTERVAL '90 days'"

  steps:
    - action: "export_to_archive"
      params:
        schema: "public"
        table: "audit_logs"
        days_old: 90
        dry_run: true
      expected:
        records_to_archive: ">= 0"
        success: true
```

#### 2.2 Системные сценарии (Уровень 2)

**Data Retention Workflow:**
```yaml
# scenarios/level2/data-retention-workflow.yml
scenario:
  id: "data-retention-full-workflow"
  name: "Полный цикл управления данными"
  level: 2
  system: "data-retention"
  uses_modules: ["retention", "archive", "partitioning"]

  steps:
    - module: "retention"
      action: "check_status"
      expected:
        tables_needing_archive: ">= 0"

    - module: "archive"
      action: "export_old_data"
      params:
        schema: "public"
        table: "audit_logs"
        days_old: 90
      expected:
        success: true

    - module: "retention"
      action: "cleanup_old_data"
      params:
        schema: "public"
        table: "audit_logs"
      expected:
        records_deleted: ">= 0"
```

**Security Vault Rotation:**
```yaml
# scenarios/level2/security-vault-rotation.yml
scenario:
  id: "security-vault-rotation"
  name: "Ротация секретов в Vault"
  level: 2
  system: "security"
  uses_modules: ["vault", "audit"]

  steps:
    - module: "vault"
      action: "rotate_secret"
      params:
        name: "jwt-secret"
        new_value: "generate_random(64)"
      expected:
        success: true

    - module: "audit"
      action: "log_event"
      params:
        event_type: "secret_rotated"
        resource: "jwt-secret"
      expected:
        logged: true
```

#### 2.3 Межсистемные сценарии (Уровень 3)

**Security Incident Response:**
```yaml
# scenarios/level3/security-incident-response.yml
scenario:
  id: "security-incident-response"
  name: "Реакция на инцидент безопасности"
  level: 3
  systems: ["vault", "audit", "notification", "monitoring"]

  trigger:
    event: "failed_auth_threshold_exceeded"
    condition: "failed_auth_count > 5 IN last_5_minutes"

  workflow:
    - system: "audit"
      action: "create_incident"
      params:
        severity: "critical"
        type: "bruteforce_attempt"

    - system: "vault"
      action: "rotate_secret"
      params:
        name: "jwt-secret"
      condition: "incident.severity == 'critical'"

    - system: "notification"
      action: "alert_admins"
      params:
        channel: "slack"
        message: "Security incident detected"

    - system: "monitoring"
      action: "create_dashboard_annotation"
      params:
        text: "Security incident: secret rotated"
```

**Data Lifecycle Management:**
```yaml
# scenarios/level3/data-lifecycle-management.yml
scenario:
  id: "data-lifecycle-management"
  name: "Управление жизненным циклом данных"
  level: 3
  systems: ["retention", "archive", "partitioning", "monitoring"]

  schedule: "0 2 * * *"  # Daily at 2 AM

  workflow:
    - system: "retention"
      action: "check_all_policies"
      output: "tables_needing_action"

    - system: "archive"
      action: "export_old_data"
      input: "tables_needing_action.archive"
      foreach: "table IN tables_needing_action.archive"

    - system: "partitioning"
      action: "create_future_partitions"
      foreach: "table IN partitioned_tables"

    - system: "partitioning"
      action: "drop_old_partitions"
      foreach: "table IN partitioned_tables"

    - system: "monitoring"
      action: "record_metrics"
      params:
        metric: "data_lifecycle_execution"
        status: "completed"
```

#### 2.4 Пользовательские workflows (Уровень 4)

**BIA Analyst Workflow:**
```yaml
# scenarios/level4/analyst-creates-bia.yml
scenario:
  id: "analyst-creates-bia-assessment"
  name: "Аналитик создает BIA оценку"
  level: 4
  user_role: "bcm-analyst"

  user_story: |
    Как BCM-аналитик
    Я хочу создать новую BIA оценку
    Чтобы оценить критичность бизнес-процессов

  steps:
    - ui: "login"
      params:
        username: "analyst@company.com"
        password: "test_password"
      expected:
        authenticated: true

    - ui: "navigate_to_bia"
      expected:
        page: "/bia/assessments"

    - ui: "click_create_assessment"

    - ui: "fill_form"
      params:
        process_name: "Financial Reporting"
        criticality: "high"
        rto: "4 hours"
        rpo: "1 hour"

    - api: "create_assessment"
      expected:
        status: 201
        assessment_id: "exists"

    - system: "validate_bia_data"
      expected:
        validation_errors: 0

    - ai: "suggest_improvements"
      expected:
        suggestions_count: ">= 1"

    - notification: "notify_stakeholders"
      params:
        stakeholders: ["manager@company.com"]
      expected:
        notifications_sent: 1
```

---

### Фаза 3: Автоматизация (1-2 недели)

#### 3.1 Auto-Test Generation
```python
# scenario-automation/test_generator.py
class ScenarioTestGenerator:
    def generate_pytest(self, scenario: Scenario) -> str:
        """Генерирует pytest из сценария"""
        test_code = f"""
import pytest
from scenario_engine import ScenarioEngine

def test_{scenario.id}():
    engine = ScenarioEngine()
    scenario = engine.load_scenario("{scenario.id}")

    # Preconditions
    assert engine.validate_preconditions(scenario)

    # Execute steps
    results = engine.execute(scenario)

    # Postconditions
    assert engine.validate_postconditions(scenario)
    assert results.success
"""
        return test_code

    def generate_all_tests(self):
        """Генерирует тесты для всех сценариев"""
        scenarios = self.load_all_scenarios()
        for scenario in scenarios:
            test_code = self.generate_pytest(scenario)
            self.save_test(f"tests/generated/test_{scenario.id}.py", test_code)
```

#### 3.2 Live Documentation
```python
# scenario-automation/doc_generator.py
class ScenarioDocGenerator:
    def generate_markdown(self, scenario: Scenario) -> str:
        """Генерирует Markdown документацию"""
        doc = f"""
# {scenario.name}

**ID**: `{scenario.id}`
**Уровень**: {scenario.level}
**Модуль**: {scenario.module}

## Описание
{scenario.description}

## Шаги

"""
        for i, step in enumerate(scenario.steps, 1):
            doc += f"{i}. **{step.action}**\n"
            if step.params:
                doc += f"   - Параметры: `{step.params}`\n"
            if step.expected:
                doc += f"   - Ожидается: `{step.expected}`\n"

        return doc

    def generate_mermaid_diagram(self, scenario: Scenario) -> str:
        """Генерирует Mermaid диаграмму"""
        diagram = "graph TD\n"
        for i, step in enumerate(scenario.steps):
            diagram += f"  Step{i}[{step.action}]\n"
            if i > 0:
                diagram += f"  Step{i-1} --> Step{i}\n"
        return diagram
```

#### 3.3 AI-Powered Scenario Generation
```python
# scenario-automation/ai_generator.py
from intelligent_core.ai_foundation.llm import LLMRouter

class AIScenarioGenerator:
    def __init__(self):
        self.llm = LLMRouter()
        self.rag = ScenarioRAG()

    async def generate_scenario_from_description(self, description: str) -> Scenario:
        """AI генерирует сценарий из описания"""

        # Найти похожие сценарии
        similar = self.rag.find_similar_scenarios(description)

        # Промпт для AI
        prompt = f"""
На основе описания и похожих сценариев, создай новый сценарий в YAML формате:

Описание: {description}

Похожие сценарии:
{self._format_scenarios(similar)}

Сгенерируй YAML сценарий с:
- id, name, level, module/system
- preconditions
- steps
- postconditions
"""

        # Запрос к Claude
        response = await self.llm.query(
            system_prompt="Ты эксперт по созданию сценариев тестирования",
            user_prompt=prompt,
            task_type="content_generation"
        )

        # Парсинг YAML
        scenario_yaml = self._extract_yaml(response)
        return Scenario.from_yaml(scenario_yaml)
```

---

### Фаза 4: Интеграция с Knowledge System (1 неделя)

#### 4.1 Scenario → RAG Integration
```python
# Автоматическое обновление RAG при изменении сценария
class ScenarioRAGSync:
    def on_scenario_created(self, scenario: Scenario):
        # Сохранить в Qdrant
        self.rag.store_scenario(scenario)

        # Извлечь знания из сценария
        knowledge = self.extract_knowledge(scenario)
        self.knowledge_base.add_entries(knowledge)

    def extract_knowledge(self, scenario: Scenario) -> List[Knowledge]:
        """Извлекает знания из сценария"""
        knowledge = []

        # Паттерны использования модулей
        for step in scenario.steps:
            knowledge.append({
                "type": "module_usage",
                "module": step.module,
                "action": step.action,
                "params": step.params,
                "context": scenario.name
            })

        # Зависимости между модулями
        if len(scenario.steps) > 1:
            for i in range(len(scenario.steps) - 1):
                knowledge.append({
                    "type": "module_dependency",
                    "from": scenario.steps[i].module,
                    "to": scenario.steps[i+1].module,
                    "workflow": scenario.id
                })

        return knowledge
```

#### 4.2 Expertise System Integration
```python
# Сценарии используют Domain Expertise
class ExpertiseEnabledScenario:
    def execute_step_with_expertise(self, step: Step):
        # Получить экспертизу по домену
        domain = self.get_domain(step.module)
        expert_knowledge = self.expertise_system.get_knowledge(domain)

        # Валидация шага на основе экспертизы
        if not expert_knowledge.validate_step(step):
            raise ValidationError(f"Step {step.action} violates {domain} best practices")

        # Выполнить с учетом экспертных рекомендаций
        recommendations = expert_knowledge.get_recommendations(step)
        return self.execute_with_recommendations(step, recommendations)
```

---

### Фаза 5: Continuous Learning (ongoing)

#### 5.1 Scenario Execution Analytics
```python
# Аналитика выполнения сценариев
class ScenarioAnalytics:
    def record_execution(self, scenario: Scenario, result: ExecutionResult):
        # Сохранить метрики
        self.metrics.record({
            "scenario_id": scenario.id,
            "success": result.success,
            "duration": result.duration,
            "failed_step": result.failed_step if not result.success else None,
            "timestamp": datetime.now()
        })

    def find_problematic_scenarios(self) -> List[Scenario]:
        """Находит сценарии с частыми ошибками"""
        return self.db.query("""
            SELECT scenario_id, COUNT(*) as failures
            FROM scenario_executions
            WHERE success = false
            AND timestamp > NOW() - INTERVAL '7 days'
            GROUP BY scenario_id
            HAVING COUNT(*) > 5
            ORDER BY failures DESC
        """)

    def suggest_improvements(self, scenario: Scenario) -> List[str]:
        """AI предлагает улучшения на основе истории"""
        history = self.get_execution_history(scenario.id)

        prompt = f"""
Сценарий {scenario.id} падает {len(history.failures)} раз за неделю.
Типичные ошибки: {history.common_errors}

Предложи улучшения:
"""

        suggestions = await self.llm.query(prompt)
        return suggestions
```

#### 5.2 Auto-Fix Scenarios
```python
# Автоматическое исправление сценариев
class ScenarioAutoFix:
    async def fix_failing_scenario(self, scenario: Scenario):
        """AI пытается исправить падающий сценарий"""

        # Получить историю ошибок
        failures = self.analytics.get_failures(scenario.id)

        # Попросить AI исправить
        fixed_scenario = await self.ai_generator.fix_scenario(
            scenario=scenario,
            failures=failures
        )

        # Протестировать исправленный сценарий
        test_result = await self.engine.test_scenario(fixed_scenario)

        if test_result.success:
            # Сохранить исправленную версию
            self.save_scenario(fixed_scenario)

            # Уведомить команду
            self.notify_team(f"Scenario {scenario.id} auto-fixed!")

        return fixed_scenario
```

---

## 📊 Структура проекта

```
intelligent-core/
├── scenario-engine/
│   ├── engine.py              # Движок выполнения
│   ├── schema.py              # Схема сценария
│   ├── validator.py           # Валидация
│   └── executor.py            # Выполнение шагов
│
├── scenario-automation/
│   ├── test_generator.py     # Генерация тестов
│   ├── doc_generator.py      # Генерация документации
│   └── ai_generator.py       # AI генерация сценариев
│
├── scenario-analytics/
│   ├── metrics.py            # Метрики выполнения
│   ├── analytics.py          # Аналитика
│   └── auto_fix.py           # Авто-исправление
│
└── scenarios/
    ├── level1/               # Модульные
    │   ├── vault/
    │   ├── retention/
    │   └── archive/
    ├── level2/               # Системные
    │   ├── data-retention-workflow.yml
    │   └── security-vault-rotation.yml
    ├── level3/               # Межсистемные
    │   ├── security-incident-response.yml
    │   └── data-lifecycle-management.yml
    └── level4/               # Пользовательские
        ├── analyst-creates-bia.yml
        └── admin-manages-users.yml
```

---

## 🚀 Quick Start

### 1. Создать первый сценарий
```bash
# Создать сценарий вручную
cat > scenarios/level1/vault/get-secret.yml << 'EOF'
scenario:
  id: "vault-get-secret"
  name: "Получение секрета из Vault"
  level: 1
  module: "vault"
  steps:
    - action: "get_secret"
      params: {name: "jwt-secret"}
      expected: {status: 200}
EOF
```

### 2. Выполнить сценарий
```python
from scenario_engine import ScenarioEngine

engine = ScenarioEngine()
scenario = engine.load_scenario("vault-get-secret")
result = engine.execute(scenario)

print(f"Success: {result.success}")
```

### 3. Сгенерировать тесты
```python
from scenario_automation import ScenarioTestGenerator

generator = ScenarioTestGenerator()
generator.generate_all_tests()

# Запустить тесты
# pytest tests/generated/
```

### 4. AI генерирует новый сценарий
```python
from scenario_automation import AIScenarioGenerator

ai_gen = AIScenarioGenerator()
scenario = await ai_gen.generate_scenario_from_description(
    "Пользователь создает новый BIA assessment и получает AI рекомендации"
)
```

---

## ✅ Польза системы

### Для разработчиков:
- ✅ Автотесты генерируются автоматически
- ✅ Документация всегда актуальна
- ✅ Легко добавлять новые сценарии
- ✅ AI помогает находить баги

### Для QA:
- ✅ Все сценарии покрыты тестами
- ✅ Регрессии находятся сразу
- ✅ Можно тестировать интеграции
- ✅ E2E тесты из сценариев

### Для новых разработчиков:
- ✅ Вся система в сценариях
- ✅ Понятно как работают интеграции
- ✅ Видно все workflows
- ✅ Онбординг за 1 час

### Для бизнеса:
- ✅ Меньше багов в продакшене
- ✅ Быстрее выпуски
- ✅ Живая документация
- ✅ Compliance из коробки

---

## 🎯 Приоритеты

### Фаза 1 (обязательно):
1. ✅ Scenario Definition Language
2. ✅ Scenario Engine
3. ✅ 10-20 базовых сценариев уровня 1-2

### Фаза 2 (важно):
4. ✅ Auto-test generation
5. ✅ RAG integration
6. ✅ 5-10 сценариев уровня 3

### Фаза 3 (полезно):
7. ✅ AI scenario generation
8. ✅ Auto-fix scenarios
9. ✅ Continuous learning

---

## 📈 Метрики успеха

- **Test Coverage**: 80%+ (из сценариев)
- **Scenarios Count**: 50+ к концу месяца
- **Auto-generated tests**: 100+ тестов
- **Documentation coverage**: 100% модулей
- **AI-generated scenarios**: 10+ в месяц
- **Auto-fixed scenarios**: 5+ в месяц

---

**Вывод**: Это НЕ излишне, а **необходимо** для системы вашего масштаба!
