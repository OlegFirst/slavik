# EXPERIMENT LAB & EMERGENT LEARNING ARCHITECTURE

**Дата:** 2025-10-05
**Версия:** 1.0
**Статус:** Архитектурный дизайн (к реализации)

---

## Проблема: Саморазвитие AI Платформы

### Множество Сценариев и Триггеров

Experiment Lab НЕ ограничивается одним сценарием. Вот **все возможные способы** инициации экспериментов:

#### 1. AI-Initiated (Автоматическое обнаружение)
AI Colleague анализирует данные и обнаруживает паттерн:
- **Пример:** МиО Specialist видит 80% healthcare организаций застревают на `assess_impact` 5+ дней
- **Триггер:** Pattern detection в Case Library → Escalation в Super-Orchestrator
- **Approval:** Super-Orchestrator оценивает evidence → автоматически отправляет в Experiment Lab

#### 2. User-Requested (Пользовательский запрос)
Пользователь напрямую просит о новой функциональности:
- **Пример:** "Мне нужны шаблоны для анализа supply chain risks в контексте BCM"
- **Триггер:** User request через UI/Chat → Intent Analyzer распознаёт как feature request
- **Approval:** Human review (если низкий risk) ИЛИ сразу в Experiment Lab

#### 3. Post-Learning Application (После обучения)
AI применил learned pattern к новому домену и обнаружил нехватку:
- **Пример:** МиО предложил finance templates, но их не существует → инициирует создание
- **Триггер:** Self-Modifying Toolkit обнаруживает missing capability при попытке применить паттерн
- **Approval:** Автоматически (based on existing pattern success)

#### 4. Monitoring-Triggered (Мониторинг производительности)
Система мониторинга обнаруживает деградацию или узкое место:
- **Пример:** API endpoint `/api/bia/analyze` стал slow (> 5s), влияет на 100+ организаций
- **Триггер:** Performance monitoring → Alert → Analysis показывает нужна оптимизация
- **Approval:** Автоматически для performance improvements (если есть rollback)

#### 5. Compliance-Driven (Изменение стандартов)
Обновление ISO стандарта или новое regulatory requirement:
- **Пример:** ISO 22301:2026 вышел с новыми требованиями к cyber resilience
- **Триggер:** External event (human notification) → Compliance Copilot анализирует gap
- **Approval:** Human review обязателен (compliance critical)

#### 6. Competitive Intelligence (Анализ рынка)
Платформа обнаруживает что конкуренты имеют feature которого нет у нас:
- **Пример:** Web scraping показывает competitor добавил "AI-powered RTO calculator"
- **Триggер:** Competitive analysis service → Feature gap identified
- **Approval:** Human review + business decision

#### 7. A/B Testing Results (Результаты тестирования)
A/B тест показал что альтернативный подход работает лучше:
- **Пример:** В тесте UX flow A vs B, flow B дал 40% improvement в completion rate
- **Триггер:** A/B test conclusion → статистически значимый результат
- **Approval:** Автоматически деплоить winning variant

#### 8. Error Pattern Recognition (Распознавание паттернов ошибок)
Повторяющиеся ошибки указывают на системную проблему:
- **Пример:** 50+ пользователей получили error "Invalid RTO value" в одном контексте
- **Триggер:** Error tracking service → pattern recognized → root cause analysis
- **Approval:** Автоматически для bug fixes

#### 9. Proactive Optimization (Проактивная оптимизация)
AI обнаруживает возможность улучшения до того как стало проблемой:
- **Пример:** ML анализ показывает что 30% BIA workflows могут быть на 2 дня короче
- **Триggер:** Proactive analysis → opportunity identified
- **Approval:** Human review (это enhancement, не fix)

#### 10. Cross-Domain Learning Transfer (Перенос знаний между доменами)
Успешный паттерн из одного домена применим к другому:
- **Пример:** Healthcare templates успешны → можно создать для education sector
- **Триggер:** Pattern applicability analysis → high confidence match
- **Approval:** Автоматически (based on proven pattern)

**Вопрос:** Как AI платформа обрабатывает ВСЕ эти сценарии единообразно?

---

## Решение: Universal Experiment Pipeline

### Унифицированная Обработка Всех Сценариев

Все 10 типов триггеров обрабатываются через **единый pipeline**:

```
┌─────────────────────────────────────────────────────────────────┐
│ UNIVERSAL EXPERIMENT INTAKE                                     │
│                                                                   │
│ Любой источник → ExperimentProposal (стандартизированный)      │
└────────────────────────┬──────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ PROPOSAL CLASSIFICATION & ROUTING                               │
│                                                                   │
│ ExperimentProposal содержит:                                     │
│ {                                                                │
│   "id": "exp_2025_10_05_001",                                   │
│   "type": "feature|optimization|bugfix|compliance|learning",    │
│   "source": "ai_colleague|user|monitoring|ab_test|...",         │
│   "priority": "critical|high|medium|low",                       │
│   "evidence": {...},  // Доказательства необходимости           │
│   "hypothesis": "...", // Что мы хотим достичь                  │
│   "risk_level": "high|medium|low",                              │
│   "requires_human_approval": bool,                              │
│   "auto_deploy_allowed": bool,                                  │
│   "rollback_strategy": {...}                                    │
│ }                                                                │
│                                                                   │
│ Router определяет:                                               │
│ - Нужно ли human approval?                                      │
│ - Какой validation pipeline?                                     │
│ - Какой deployment strategy?                                     │
└────────────────────────┬──────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ DYNAMIC EXPERIMENT WORKFLOW                                     │
│                                                                   │
│ Workflow адаптируется к типу эксперимента:                      │
│                                                                   │
│ ┌────────────────────────────────────────────────────────────┐  │
│ │ Type: FEATURE (user-requested или AI-initiated)            │  │
│ │ Workflow:                                                   │  │
│ │ 1. Hypothesis Refinement (AI анализ)                       │  │
│ │ 2. Prototype Generation (Code Generator)                   │  │
│ │ 3. Full Validation (security + functionality)              │  │
│ │ 4. Human Review (обязательно!)                             │  │
│ │ 5. Staged Rollout (beta → production)                      │  │
│ └────────────────────────────────────────────────────────────┘  │
│                                                                   │
│ ┌────────────────────────────────────────────────────────────┐  │
│ │ Type: BUGFIX (error pattern recognition)                   │  │
│ │ Workflow:                                                   │  │
│ │ 1. Root Cause Analysis (автоматически)                     │  │
│ │ 2. Fix Generation (Code Generator)                         │  │
│ │ 3. Regression Testing (Test Runner)                        │  │
│ │ 4. Auto-deploy (если tests pass + low risk)               │  │
│ │ 5. Monitor (rollback если проблемы)                        │  │
│ └────────────────────────────────────────────────────────────┘  │
│                                                                   │
│ ┌────────────────────────────────────────────────────────────┐  │
│ │ Type: OPTIMIZATION (monitoring-triggered)                  │  │
│ │ Workflow:                                                   │  │
│ │ 1. Performance Analysis (Profiler)                         │  │
│ │ 2. Optimization Strategy (AI suggests)                     │  │
│ │ 3. A/B Test Setup (compare old vs new)                    │  │
│ │ 4. Gradual Rollout (10% → 50% → 100%)                     │  │
│ │ 5. Auto-deploy (если metrics improve)                     │  │
│ └────────────────────────────────────────────────────────────┘  │
│                                                                   │
│ ┌────────────────────────────────────────────────────────────┐  │
│ │ Type: COMPLIANCE (standards update)                        │  │
│ │ Workflow:                                                   │  │
│ │ 1. Gap Analysis (Compliance Copilot)                       │  │
│ │ 2. Solution Design (с reference к стандарту)              │  │
│ │ 3. Legal Review (human обязательно!)                      │  │
│ │ 4. Compliance Validation (audit trail)                     │  │
│ │ 5. Manual Deploy (только после approval)                  │  │
│ └────────────────────────────────────────────────────────────┘  │
│                                                                   │
│ ┌────────────────────────────────────────────────────────────┐  │
│ │ Type: LEARNING_TRANSFER (cross-domain pattern)             │  │
│ │ Workflow:                                                   │  │
│ │ 1. Pattern Adaptation (modify для нового домена)           │  │
│ │ 2. Quick Prototype (на базе существующего)                │  │
│ │ 3. Lightweight Validation (уже проверенный паттерн)        │  │
│ │ 4. Auto-deploy (high confidence)                           │  │
│ │ 5. Monitor & Learn (обновить паттерн если нужно)          │  │
│ └────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### Матрица Принятия Решений

```python
APPROVAL_MATRIX = {
    # Type, Risk, Source → Approval Strategy

    ("feature", "high", "user"): {
        "human_approval": True,
        "review_by": ["product_owner", "tech_lead"],
        "deployment": "staged_rollout"
    },

    ("feature", "medium", "ai_colleague"): {
        "human_approval": True,
        "review_by": ["tech_lead"],
        "deployment": "canary_release"
    },

    ("bugfix", "low", "error_pattern"): {
        "human_approval": False,  # Auto!
        "validation": "regression_tests",
        "deployment": "auto_with_rollback"
    },

    ("bugfix", "high", "error_pattern"): {
        "human_approval": True,
        "review_by": ["tech_lead"],
        "deployment": "manual_deploy"
    },

    ("optimization", "low", "monitoring"): {
        "human_approval": False,  # Auto!
        "validation": "a_b_test",
        "deployment": "gradual_rollout"
    },

    ("compliance", "*", "*"): {
        "human_approval": True,  # ВСЕГДА!
        "review_by": ["compliance_officer", "legal"],
        "deployment": "manual_deploy"
    },

    ("learning_transfer", "low", "ai_colleague"): {
        "human_approval": False,  # Auto!
        "validation": "pattern_replay",
        "deployment": "auto_deploy"
    }
}
```

### Пример: Обработка 3 Разных Сценариев

#### Сценарий A: User Request Feature

```
User: "Мне нужны шаблоны для supply chain risk analysis"

1. Intent Analyzer:
   └→ type="feature", source="user", priority="medium"

2. Proposal Generator:
   └→ {
       "hypothesis": "User needs supply_chain risk templates",
       "evidence": {"user_request": true, "domain": "supply_chain"},
       "risk_level": "medium",
       "requires_human_approval": true
   }

3. Router:
   └→ Workflow: FEATURE (full pipeline)
   └→ Approval: Human review by tech_lead

4. Experiment Lab:
   └→ Phase 1: Hypothesis Refinement
      AI анализирует: "Какие конкретно templates нужны?"
      Консультируется с Risk Analyst AI
      Refinement: "Need 5 templates: supplier_failure, logistics_disruption,
                   quality_issues, geopolitical_risk, cyber_supply_chain"

   └→ Phase 2: Prototype Generation
      Code Generator создает supply_chain_risk_templates.py

   └→ Phase 3: Validation
      Security scan ✓
      Functional tests (нет исторических данных - создает synthetic)

   └→ Phase 4: Human Review
      Tech Lead review: "Looks good, но добавить template для pandemic impact"
      Experiment Lab возвращает в Phase 2 с модификацией

   └→ Phase 5: Deployment
      Staged rollout: beta users → all users

   └→ Phase 6: Learning
      Pattern extracted: "supply_chain domain templates created"
      МиО Specialist обновлен
```

#### Сценарий B: Monitoring-Triggered Optimization

```
Performance Monitor: API /api/bia/analyze slow (avg 5.2s, was 1.5s)

1. Alert Analyzer:
   └→ type="optimization", source="monitoring", priority="high"

2. Proposal Generator:
   └→ {
       "hypothesis": "Database query N+1 problem detected",
       "evidence": {"affected_users": 120, "degradation": "3.5x slower"},
       "risk_level": "low",  # Optimization, не breaking change
       "requires_human_approval": false,
       "auto_deploy_allowed": true
   }

3. Router:
   └→ Workflow: OPTIMIZATION (A/B test pipeline)
   └→ Approval: Auto (если metrics improve)

4. Experiment Lab:
   └→ Phase 1: Performance Analysis
      Profiler AI анализирует: "Query делает 50 DB calls, можно 1"

   └→ Phase 2: Fix Generation
      Code Generator оптимизирует query (добавляет eager loading)

   └→ Phase 3: A/B Test
      10% traffic на новую версию
      Metrics: 5.2s → 1.3s (75% improvement!)

   └→ Phase 4: Gradual Rollout
      Auto-expand: 10% → 25% → 50% → 100%
      No human approval needed!

   └→ Phase 5: Learning
      Pattern: "N+1 query optimization успешен"
      Platform Intelligence AI обновлен для проактивного поиска таких паттернов
```

#### Сценарий C: Post-Learning Application

```
МиО Specialist (во время консультации с education клиентом):
"Вижу вы застряли на assess_impact. У меня есть education templates? НЕТ!"

1. Self-Modifying Toolkit:
   └→ type="learning_transfer", source="ai_colleague", priority="medium"

2. Proposal Generator:
   └→ {
       "hypothesis": "Education templates needed, can adapt from healthcare",
       "evidence": {
           "base_pattern": "exp_healthcare_001",
           "success_rate": 0.77,
           "domain_similarity": 0.65  # Education близок к healthcare
       },
       "risk_level": "low",  # Proven pattern
       "requires_human_approval": false,
       "auto_deploy_allowed": true
   }

3. Router:
   └→ Workflow: LEARNING_TRANSFER (quick adaptation)
   └→ Approval: Auto (proven pattern)

4. Experiment Lab:
   └→ Phase 1: Pattern Adaptation
      AI берет healthcare template structure
      Адаптирует категории:
      Healthcare: Patient Safety → Education: Student Safety
      Healthcare: Clinical Ops → Education: Academic Operations

   └→ Phase 2: Quick Prototype
      Generate education_impact_templates.py (90% reuse)

   └→ Phase 3: Lightweight Validation
      Pattern replay (использует education cases из Case Library)
      Improvement detected: delay reduction 60% (lower than healthcare but good)

   └→ Phase 4: Auto-Deploy
      No human review (proven pattern + low risk)
      Deploy immediately

   └→ МиО возвращается к пользователю через 30 минут:
      "✅ Education-specific templates ready! Applying now..."
```

---

## Архитектурная Концепция

```
┌─────────────────────────────────────────────────────────────────┐
│ САМОРАЗВИВАЮЩАЯСЯ AI ЭКОСИСТЕМА                                 │
│                                                                   │
│ 1. AI Colleague обнаруживает паттерн → Escalation               │
│ 2. Super-Orchestrator оценивает → Experiment Lab                │
│ 3. Experiment Lab создает прототип в sandbox                    │
│ 4. Validation проверяет безопасность/эффективность              │
│ 5. Human утверждает → Deployment в production                   │
│ 6. Success Pattern Extractor извлекает знание                   │
│ 7. AI Colleagues автоматически обновлены                        │
│ 8. Применяют знание проактивно → обнаруживают новые паттерны   │
│                                                                   │
│ → ЦИКЛ ПОВТОРЯЕТСЯ с НОВЫМ знанием! (Эмерджентное обучение)    │
└─────────────────────────────────────────────────────────────────┘
```

---

## Полная Цепочка: От Проблемы до Автоматического Применения

### ДЕНЬ 1: Обнаружение и Escalation

```
МиО Specialist анализирует Case Library:
├── Обнаружен паттерн: healthcare delay в assess_impact
├── Evidence: 47 кейсов, avg delay 5.3 дня
├── Root cause: нехватка domain-specific templates
└── Escalation → Super-Orchestrator

Super-Orchestrator принимает решение:
├── Evidence достаточно? ✓ (47 кейсов)
├── Критично? ✓ (5.3 дня задержки)
├── Безопасно экспериментировать? ✓
└── Решение: "Передать в Experiment Lab"
```

### ДЕНЬ 1-2: Experiment Lab Workflow

#### Phase 1: Hypothesis Refinement (автоматически)
```
Experiment Coordinator AI:
├── Анализирует Case Library детально
├── Консультируется с Domain Expert AI
├── Формирует точную гипотезу:
│   "Healthcare impact требует 3 категории:
│    - Patient Safety Impact
│    - Regulatory Compliance Impact
│    - Clinical Operations Impact"
└── Переход к Phase 2
```

#### Phase 2: Prototype Generation (автоматически)
```
Code Generator Service (через EventBus):
├── Получает команду: "generate_code"
├── Создает в SANDBOX:
│   /experiment_lab/sandbox/exp_2025_10_05_healthcare_001/
│   ├── prototype/healthcare_impact_templates.py
│   ├── tests/test_templates.py
│   └── experiment_config.yaml
├── Constitution Rule: НЕ трогать production!
└── Возвращает: generated_code → Experiment Lab
```

#### Phase 3: Validation (автоматически)
```
Test Runner Service (через EventBus):
├── Получает команду: "run_validation"
├── Replay 47 historical healthcare cases через прототип
├── Проверки:
│   ✓ Security scan passed
│   ✓ Constitution compliance OK
│   ✓ Performance OK
│   ✓ Delay reduction: 5.3 → 1.2 дня (77% улучшение!)
│   ✓ 45/47 кейсов улучшились
└── Возвращает: validation_results → Experiment Lab
```

#### Phase 4: Human Review Checkpoint ⚠️
```
Experiment Lab генерирует отчет:

📊 EXPERIMENT RESULTS
ID: exp_2025_10_05_healthcare_001
Proposed by: МиО Specialist AI

Evidence:
- 47 cases affected
- Average delay: 5.3 days

Prototype Created:
- healthcare_impact_templates.py (237 lines)

Validation Results:
✓ 77% delay reduction (5.3→1.2 days)
✓ 45/47 cases improved
✓ Security passed
✓ No breaking changes

Recommendation: APPROVE for production

[Approve] [Reject] [Modify]
```

#### Phase 5: Deployment (после human approval)
```
Deployment Service (через EventBus):
├── Получает команду: "deploy_module"
├── Из sandbox → production:
│   /intelligent-core/domain-specialists/healthcare/
│   └── impact_templates.py
├── Регистрирует модуль в Workflow Engine
├── Обновляет AI Colleague toolkit
├── Создает мониторинг
└── Возвращает: deployment_complete
```

### ДЕНЬ 2-3: Автоматическая Интеграция Знаний

```
Learning Integration Service (автоматически):

1. Pattern Extraction:
   ├── Что сработало: Domain-specific templates (не generic)
   ├── Когда применять: delay > 3 days в assess_impact
   ├── Где еще: finance, manufacturing, retail
   └── Ожидаемый результат: 70-80% улучшение

2. Tool Generation (AI генерирует код!):
   @ai_tool(
       name="suggest_domain_impact_templates",
       auto_activate=True  # ⭐ КЛЮЧЕВОЕ!
   )
   async def suggest_domain_templates(...):
       # Проактивно предлагает domain templates
       # ИЛИ инициирует новый эксперимент если нет

3. Auto-Integration в МиО Specialist:
   await colleague_toolkit.add_tool(
       colleague_id="mio_specialist",
       tool=suggest_domain_templates,
       activation="immediate",
       priority="high"
   )

4. Update Decision Tree:
   # МиО Specialist теперь АВТОМАТИЧЕСКИ проверяет это условие
   if stage == "assess_impact" and time > 3 days:
       suggestion = await self.tools.suggest_domain_templates(context)
```

### ДЕНЬ 4: Первое Автоматическое Применение

```
Новый клиент: Finance организация

Day 7 в BIA: МиО Specialist автоматически активируется:

💡 "I notice you've been in 'Assess Impact' stage for 3 days.
   Based on 47 similar cases, finance organizations benefit from
   domain-specific impact categories:

   • Regulatory Compliance Impact
   • Financial Loss Impact
   • Customer Trust Impact

   This reduced assessment time by 77% in healthcare.
   Would you like me to apply finance-specific templates?"

User: "Apply Templates"

МиО проверяет: finance templates exist? НЕТ!

САМОРАЗВИТИЕ активируется:
├── "Templates don't exist yet. Based on healthcare success,
│    I can create them. Shall I proceed?"
├── User: "Yes"
└── Автоматически инициирует НОВЫЙ эксперимент:
    await experiment_lab.create_experiment(
        type="domain_templates_generation",
        domain="finance",
        based_on_pattern="exp_healthcare_001",
        initiator="mio_specialist_auto"
    )

2 часа спустя:
✅ "Finance-specific impact templates are ready! Applying now..."
```

### WEEK 1-6: Эмерджентное Саморазвитие

```
Week 1: Healthcare templates (human experiment)
Week 2: Finance templates (AI-initiated, auto)
Week 3: Manufacturing templates (AI-initiated, auto)

Week 4: МиО обнаруживает МЕТА-ПАТТЕРН:
        "Для ЛЮБОЙ индустрии нужны специфичные категории"

Week 5: МиО создает UNIVERSAL TOOL:
        "Domain Template Generator"
        → При новой индустрии - автоматически генерирует templates

Week 6: Platform САМОСТОЯТЕЛЬНО поддерживает ВСЕ индустрии!
        Без единой строки кода от программиста!
```

---

## Архитектура: Разделение Ответственностей

### Principle: Business Logic ≠ Execution

```
┌─────────────────────────────────────────────────────────────────┐
│ LAYER 1: BUSINESS LOGIC                                         │
│ /platform-services/experiment-lab/                              │
│                                                                   │
│ Ответственность:                                                 │
│ ✓ Управление жизненным циклом эксперимента                      │
│ ✓ Валидация гипотез                                             │
│ ✓ Принятие решений (готов к deployment?)                       │
│ ✓ Emit команды через EventBus                                   │
│                                                                   │
│ НЕ делает:                                                       │
│ ✗ Генерацию кода (→ Code Generator Service)                    │
│ ✗ Запуск тестов (→ Test Runner Service)                        │
│ ✗ Deployment (→ Deployment Service)                             │
└────────────────────────┬──────────────────────────────────────────┘
                         │ EventBus Commands
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ LAYER 2: EXECUTION SERVICES                                     │
│                                                                   │
│ ┌──────────────────────────────────────────────────────────────┐│
│ │ Code Generator Service                                        ││
│ │ Слушает: "code_generator.generate"                           ││
│ │ Делает: LLM генерация кода в sandbox                         ││
│ │ Возвращает: "experiment_lab.code_generated"                   ││
│ └──────────────────────────────────────────────────────────────┘│
│                                                                   │
│ ┌──────────────────────────────────────────────────────────────┐│
│ │ Test Runner Service                                           ││
│ │ Слушает: "test_runner.validate"                              ││
│ │ Делает: pytest, security scan, case replay                    ││
│ │ Возвращает: "experiment_lab.validation_results"               ││
│ └──────────────────────────────────────────────────────────────┘│
│                                                                   │
│ ┌──────────────────────────────────────────────────────────────┐│
│ │ Deployment Service                                            ││
│ │ Слушает: "deployment.deploy"                                 ││
│ │ Делает: Копирование, регистрация, rollback setup            ││
│ │ Возвращает: "experiment_lab.deployment_complete"              ││
│ └──────────────────────────────────────────────────────────────┘│
│                                                                   │
│ ┌──────────────────────────────────────────────────────────────┐│
│ │ Learning Integration Service                                  ││
│ │ Слушает: "learning.integrate_experiment_success"             ││
│ │ Делает: Pattern extraction, toolkit update                    ││
│ │ Возвращает: "experiment_lab.learning_complete"                ││
│ └──────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

### EventBus Communication Pattern

```python
# Experiment Lab координирует через команды:

# 1. Генерация кода
await eventbus.emit("code_generator.generate", {
    "experiment_id": exp_id,
    "spec": code_spec,
    "reply_to": "experiment_lab.code_generated"
})

# 2. Валидация
await eventbus.emit("test_runner.validate", {
    "experiment_id": exp_id,
    "spec": validation_spec,
    "reply_to": "experiment_lab.validation_results"
})

# 3. Deployment
await eventbus.emit("deployment.deploy", {
    "experiment_id": exp_id,
    "spec": deployment_spec,
    "reply_to": "experiment_lab.deployment_complete"
})

# 4. Learning Integration
await eventbus.emit("learning.integrate_experiment_success", {
    "experiment_id": exp_id,
    "spec": learning_spec
})
```

---

## Ключевые Компоненты

### 1. Experiment Coordinator (Бизнес-логика)

```python
class ExperimentCoordinator:
    """
    Управляет жизненным циклом эксперимента.
    НЕ выполняет работу - КООРДИНИРУЕТ через EventBus.
    """

    async def create_experiment(self, proposal: ExperimentProposal) -> str:
        # Валидация proposal (бизнес-правила)
        # Создание experiment record
        # Запуск Phase 1

    async def _start_hypothesis_refinement(self, experiment):
        # Emit: "intelligence.analyze_cases"
        # Ждет: "experiment_lab.hypothesis_results"

    async def _start_prototype_generation(self, experiment):
        # Emit: "code_generator.generate"
        # Ждет: "experiment_lab.code_generated"

    async def _start_validation(self, experiment):
        # Emit: "test_runner.validate"
        # Ждет: "experiment_lab.validation_results"

    async def _request_human_review(self, experiment):
        # Emit: "ui.show_review_request"
        # Ждет: "experiment_lab.human_decision"

    async def _start_deployment(self, experiment):
        # Emit: "deployment.deploy"
        # Ждет: "experiment_lab.deployment_complete"
```

### 2. Self-Modifying Toolkit (Автоматическое обучение)

```python
class SelfModifyingToolkit:
    """
    Toolkit который AI Colleague может САМ расширять
    на основе успешных экспериментов.

    КРИТИЧНО для перехода знаний в практику!
    """

    async def integrate_experiment_tool(
        self,
        experiment_id: str,
        pattern: Dict[str, Any],
        auto_activate: bool = True
    ):
        # 1. Генерировать executable tool из паттерна
        tool_code = await self._generate_tool_code(pattern)

        # 2. Безопасно загрузить (sandbox первый раз)
        tool = await self._safe_load_tool(tool_code)

        # 3. Валидировать
        validation = await self._validate_tool(tool)

        # 4. Добавить в toolkit
        self.tools[pattern["name"]] = tool

        # 5. Обновить decision tree (автоматически!)
        if auto_activate:
            await self._add_to_decision_tree(pattern)

        # Теперь AI Colleague АВТОМАТИЧЕСКИ использует новый инструмент!

    async def execute_decision_tree(self, context: WorkflowContext):
        """
        Вызывается автоматически при каждом взаимодействии.
        Проверяет ВСЕ learned patterns и применяет проактивно!
        """
        for branch in self.decision_tree.branches:
            if await branch.condition.evaluate(context):
                tool = self.tools.get(branch.action["function"])
                return await tool.execute(context)
```

### 3. AI Colleague Integration (Автоматическая подписка)

```python
class MIOSpecialist(AIColleague):
    """
    МиО Specialist с саморазвивающимся toolkit
    """

    def __init__(self):
        super().__init__()
        self.toolkit = SelfModifyingToolkit("mio_specialist")

        # ⭐ Подписка на успешные эксперименты
        self.event_bus.subscribe(
            event_type="experiment_success",
            handler=self._on_experiment_success
        )

    async def _on_experiment_success(self, event):
        """
        Автоматически вызывается когда Experiment Lab завершает эксперимент!
        """
        experiment_id = event["experiment_id"]
        pattern = event["success_pattern"]

        if self._is_relevant_to_me(pattern):
            # Автоматически интегрировать новый инструмент!
            await self.toolkit.integrate_experiment_tool(
                experiment_id=experiment_id,
                pattern=pattern,
                auto_activate=True  # Сразу начать использовать!
            )

    async def process_consultation(self, message, context):
        """
        ⭐ СНАЧАЛА проверяем learned patterns (проактивно!)
        """
        # 1. Проверить decision tree
        proactive_action = await self.toolkit.execute_decision_tree(context)

        if proactive_action:
            # Нашли подходящий learned pattern!
            return proactive_action

        # 2. Обычная обработка
        return await super().process_consultation(message, context)
```

---

## Управляемая Автономия для Экспериментов

### Constitution для Experiment Lab

```yaml
experiment_constitution:
  rules:
    - rule_1: "НИКОГДА не трогать production код напрямую"
    - rule_2: "Всегда работать в sandbox"
    - rule_3: "Validation обязательна (security + performance + constitution)"
    - rule_4: "Human approval для deployment в production"
    - rule_5: "Мониторинг после deployment обязателен"
    - rule_6: "Rollback план всегда готов"
    - rule_7: "Каждый эксперимент → Case Library для обучения"

creative_zones:
  - zone: "hypothesis_refinement"
    freedom_level: HIGH
    description: "AI свободно анализирует данные и формирует гипотезы"

  - zone: "code_generation"
    freedom_level: MEDIUM
    description: "AI генерирует код с ограничениями"
    constraints:
      - no_db_schema_changes
      - no_auth_bypass
      - max_lines: 500

  - zone: "deployment"
    freedom_level: LOW
    description: "Только после human approval"

checkpoints:
  - name: "before_sandbox_creation"
    validation: "hypothesis_has_evidence"

  - name: "before_code_generation"
    validation: "sandbox_isolated"

  - name: "before_validation"
    validation: "code_security_scan"

  - name: "before_human_review"
    validation: "all_tests_passed"

  - name: "before_deployment"
    validation: "human_approved"
```

---

## Структура Директорий

```
platform-services/
│
├── experiment-lab/                    # КООРДИНАТОР
│   ├── core/
│   │   ├── experiment_coordinator.py  # Управление экспериментом
│   │   ├── proposal_validator.py      # Валидация proposals
│   │   └── report_generator.py        # Генерация отчетов
│   ├── models/
│   │   └── experiment.py              # Data models
│   └── main.py                        # FastAPI service
│
├── code-generator/                    # ИСПОЛНИТЕЛЬ
│   ├── core/
│   │   ├── llm_generator.py           # LLM генерация
│   │   ├── template_engine.py         # Шаблоны кода
│   │   └── sandbox_writer.py          # Запись в sandbox
│   └── main.py
│
├── test-runner/                       # ИСПОЛНИТЕЛЬ
│   ├── runners/
│   │   ├── pytest_runner.py           # Pytest
│   │   ├── security_scanner.py        # Security
│   │   └── case_replayer.py           # Replay historical cases
│   └── main.py
│
├── deployment/                        # ИСПОЛНИТЕЛЬ
│   ├── core/
│   │   ├── file_mover.py              # Копирование файлов
│   │   ├── registry_updater.py        # Регистрация модулей
│   │   └── rollback_manager.py        # Rollback
│   └── main.py
│
└── learning-integration/              # ИСПОЛНИТЕЛЬ
    ├── core/
    │   ├── pattern_extractor.py       # Извлечение паттернов
    │   ├── tool_generator.py          # Генерация AI tools
    │   ├── toolkit_updater.py         # Обновление AI toolkits
    │   └── decision_tree_updater.py   # Обновление decision logic
    └── main.py
```

---

## Цикл Эмерджентного Обучения

```
┌─────────────────────────────────────────────────────────────────┐
│ EMERGENT LEARNING LOOP                                          │
│                                                                   │
│ 1. AI Colleague работает                                        │
│    └→ обнаруживает паттерн проблемы в Case Library             │
│                                                                   │
│ 2. Escalates в Super-Orchestrator с evidence                    │
│    └→ Super-Orchestrator оценивает критичность                 │
│                                                                   │
│ 3. Experiment Lab создает решение                               │
│    └→ hypothesis → prototype → validation → human review       │
│                                                                   │
│ 4. Deployment в production                                      │
│    └→ новый модуль доступен                                    │
│                                                                   │
│ 5. Success Pattern Extractor извлекает знание                   │
│    └→ ЧТО сработало, КОГДА применять, ГДЕ ЕЩЕ применимо       │
│                                                                   │
│ 6. Learning Integration обновляет AI Colleagues                 │
│    └→ новый инструмент + обновленная decision logic            │
│                                                                   │
│ 7. AI Colleagues применяют знание АВТОМАТИЧЕСКИ                 │
│    └→ проактивно предлагают при matching условиях              │
│                                                                   │
│ 8. При новом домене - инициируют НОВЫЙ эксперимент             │
│    └→ используя learned pattern как основу                     │
│                                                                   │
│ → GOTO 1 с НОВЫМ знанием и НОВЫМИ возможностями!               │
│                                                                   │
│ Результат: Платформа САМОСТОЯТЕЛЬНО расширяет свои capability  │
│            без программиста!                                     │
└─────────────────────────────────────────────────────────────────┘
```

---

## Ключевые Инсайты

### 1. Разделение Business Logic и Execution
- **Experiment Lab** = координатор (ЧТО делать)
- **Services** = исполнители (КАК делать)
- **EventBus** = коммуникация

### 2. От Знания к Практике БЕЗ человека
- Success Pattern → Executable Tool (AI генерирует!)
- Auto-Integration в AI Colleague toolkit
- Auto-Activation через decision tree
- Проактивное применение при matching условиях

### 3. Эмерджентное Обучение
- Week 1: Healthcare (human)
- Week 2: Finance (AI-initiated)
- Week 3: Manufacturing (AI-initiated)
- Week 4: Meta-pattern discovered
- Week 5: Universal tool created
- Week 6: Полная автономия для всех индустрий!

### 4. Управляемая Автономия
- Constitution предотвращает саморазрушение
- Creative Zones дают свободу думать
- Checkpoints обеспечивают безопасность
- Human approval для критичных решений

### 5. Sandbox-First подход
- ВСЕ эксперименты в изолированном окружении
- Production никогда не под риском
- Validation перед deployment
- Rollback всегда доступен

---

## Следующие Шаги (к реализации)

1. **Сначала:** Определить полную архитектуру AI экосистемы
2. **Потом:** Реализовать Experiment Lab как часть экосистемы
3. **Приоритет:** Workflow Intelligence Engine (краеугольный камень)
4. **После:** Experiment Lab для саморазвития

---

## Вопросы для Архитектуры

- Как Experiment Lab интегрируется с Workflow Intelligence Engine?
- Какие еще компоненты нужны для полной AI экосистемы?
- Где граница между "базовой платформой" и "саморазвитием"?
- Как обеспечить безопасность AI-generated кода?

---

**Вывод:** Experiment Lab + Emergent Learning = механизм **саморазвития платформы**.
AI платформа не просто выполняет задачи - она **сама себя улучшает** на основе опыта.
