# 🧠 Концепция `/ai_experts` - Топовый AI Слой

## 🎯 Главная Идея

**AI Experts** = Топовый интеллектуальный слой над всеми BCM модулями

**Философия**: Гибридная AI/ML система с "managed autonomy"
- 1 foundation model (Claude) для всего
- Специализированные агенты для доменов
- RAG для контекста
- ML для предсказаний и обучения

---

## 📦 Архитектура (5 подсистем)

```
ai_experts/
├── 1. SPECIALISTS          # 3 топовых эксперта
├── 2. TOOLS               # 12 инструментов
├── 3. RAG                 # Retrieval-Augmented Generation
├── 4. ML                  # Machine Learning модели
└── 5. LEARNING            # Самообучение
```

---

## 1️⃣ SPECIALISTS - Топовые Эксперты (3 штуки)

### Роль: Координация НЕСКОЛЬКИХ модулей + стратегия

#### **BCM Advisor** (`specialists/bcm_advisor.py`)
**Координирует**: BIA + Risk + Planning

**Экспертиза**:
- Business Impact Analysis
- Recovery strategies (RTO/RPO)
- Process dependencies
- BCM planning

**Tools**:
- BIAAnalysisTool - расчёт критичности
- DependencyMapperTool - карта зависимостей
- CaseSearchTool - похожие кейсы

**Temperature**: 0.3 (factual, но с пониманием бизнеса)

**Когда вызывается**:
- BIA-service нужен сложный расчёт
- Planning-service создаёт стратегию
- Risk-service анализирует dependencies

---

#### **Compliance Auditor** (`specialists/compliance_auditor.py`)
**Координирует**: Compliance + Governance + Audit

**Экспертиза**:
- ISO 22301 clause-by-clause
- Gap analysis
- Evidence validation
- Audit preparation

**Tools**:
- ComplianceCheckTool - проверка соответствия
- GapAnalysisTool - анализ пробелов
- EvidenceValidatorTool - валидация доказательств

**Temperature**: 0.2 (максимально точный, стандарты)

**Когда вызывается**:
- Compliance-service проверяет соответствие
- Governance-service оценивает политики
- Documents-service валидирует evidence

---

#### **Strategic Planner** (`specialists/strategic_planner.py`)
**Координирует**: Planning + Learning + Maturity + Predictive

**Экспертиза**:
- BCM program roadmap
- Resource planning
- Maturity assessment
- Executive communication

**Tools**:
- TimelinePredictorTool - сроки внедрения
- ResourcePlannerTool - планирование ресурсов
- MaturityAssessmentTool - уровень зрелости

**Temperature**: 0.4 (стратегическое мышление)

**Когда вызывается**:
- Planning-service создаёт roadmap
- Learning-service оценивает прогресс
- Governance-service планирует ресурсы

---

## 2️⃣ TOOLS - Инструменты (12 штук)

### Категории:

#### **BIA Tools** (3 инструмента)
1. **BIAAnalysisTool** - анализ критичности процессов
   - Input: process_name, industry, description
   - Output: criticality (critical/important/normal), RTO, RPO, impact over time

2. **DependencyMapperTool** - карта зависимостей
   - Input: process_name
   - Output: upstream/downstream dependencies, critical path

3. **ImpactCalculatorTool** - расчёт impact
   - Input: process, downtime_hours, revenue
   - Output: financial/operational/reputational/regulatory impact

---

#### **Compliance Tools** (3 инструмента)
4. **ComplianceCheckTool** - проверка ISO 22301
   - Input: organization_id, clauses
   - Output: compliance_score, compliant/non-compliant clauses

5. **GapAnalysisTool** - gap analysis
   - Input: organization_id
   - Output: missing elements, remediation priority, action plan

6. **EvidenceValidatorTool** - валидация evidence
   - Input: clause, evidence_items
   - Output: quality assessment, completeness check

---

#### **Strategic Tools** (3 инструмента)
7. **TimelinePredictorTool** - прогноз сроков
   - Input: org_size, current_maturity, target_maturity
   - Output: estimated_months, phases breakdown

8. **ResourcePlannerTool** - планирование ресурсов
   - Input: program_scope, org_size, timeline
   - Output: staff allocation, budget, skills needed

9. **MaturityAssessmentTool** - оценка зрелости
   - Input: organization_id
   - Output: maturity level (1-5), improvement roadmap

---

#### **Case Library Tools** (2 инструмента)
10. **CaseSearchTool** - поиск похожих кейсов
    - Input: query, filters (industry, size)
    - Output: similar cases, success patterns, lessons learned

11. **BestPracticeLibraryTool** - библиотека best practices
    - Input: domain, industry
    - Output: proven approaches, ISO recommendations

---

#### **Base** (1 класс)
12. **BaseTool** - базовый класс для всех Tools
    - Валидация параметров
    - Async execution
    - Error handling

---

## 3️⃣ RAG - Retrieval-Augmented Generation

### Роль: Контекстуализация AI ответов

#### **Источники знаний** (3 типа):
1. **Knowledge Graph** - ISO стандарты, clauses, требования
2. **Case Library** - успешные кейсы, паттерны, решения
3. **Community Annotations** - практические интерпретации, комментарии

#### **Pipeline** (`rag/pipeline.py`):
```
User Query
    ↓
1. Embeddings (rag/embeddings.py)
   - Преобразование query в вектор
    ↓
2. Hybrid Search (rag/retrieval.py)
   - Semantic search (vector similarity)
   - Keyword search (BM25-like)
   - Filtered (industry, module)
    ↓
3. Re-ranking (rag/reranking.py)
   - Recency weight
   - Relevance score
   - Source priority (ISO > Cases > Annotations)
    ↓
4. Top-K chunks (обычно 3-5)
    ↓
5. Inject в LLM context
```

#### **Особенности**:
- **Hybrid**: semantic + keyword (лучше чем только semantic)
- **Filtered**: по industry, module (релевантность)
- **Re-ranked**: свежие + авторитетные источники выше
- **Source priority**: ISO стандарты > кейсы > комментарии

---

## 4️⃣ ML - Machine Learning Модели

### Роль: Предсказания и аномалии

#### **Workflow Predictor** (`ml/predictive_models.py`)

**Предсказывает**:
1. **Stage Duration** (Random Forest Regressor)
   - Сколько займёт текущий stage
   - На основе: industry, org_size, maturity, historical patterns

2. **Stuck Probability** (Gradient Boosting Classifier)
   - Вероятность что workflow застрянет
   - Факторы: complexity, team_experience, dependencies

3. **Expert Help Needed** (Gradient Boosting Classifier)
   - Нужна ли помощь AI эксперта
   - Признаки: challenges, error_rate, stage_repeats

4. **Total Completion Time**
   - Общее время до завершения workflow
   - Sum of predicted stage durations

**Training**:
- Данные: минимум 50 completed workflows
- Features: org context + stage info + historical patterns
- Target accuracy: R² > 0.7 (regression), Accuracy > 0.75 (classification)

---

#### **Anomaly Detection** (`ml/anomaly_detection.py`)

**Выявляет**:
- Необычное поведение workflow
- Подозрительные паттерны использования
- Потенциальные ошибки/проблемы

**Методы**:
- Isolation Forest
- One-Class SVM
- Autoencoders (для сложных паттернов)

---

#### **Training Pipeline** (`ml/training_pipeline.py`)

**Orchestration**:
1. Collect training data (completed workflows)
2. Feature engineering (extract relevant features)
3. Train models (Random Forest, Gradient Boosting)
4. Validate (cross-validation, holdout)
5. Deploy (if accuracy meets threshold)
6. Monitor (drift detection, periodic retraining)

---

## 5️⃣ LEARNING - Самообучающаяся Система

### Роль: Автоматическое улучшение на основе опыта

#### **Self-Learning Engine** (`learning/self_learning_engine.py`)

**Процесс**:
```
1. Workflow Completed
        ↓
2. Auto-collect (anonymized)
        ↓
3. Extract Patterns (ML)
   - Успешные подходы
   - Частые проблемы
   - Эффективные решения
        ↓
4. Update Benchmarks
   - Industry benchmarks
   - Best practices
   - Time estimates
        ↓
5. IF pattern frequency > 10 AND success_rate > 80%
        ↓
6. Suggest New Rule
   - Автоматическое предложение правила
   - ТРЕБУЕТ human approval ✅
        ↓
7. Rule Approved → Apply to future workflows
```

**Supervised Elements** (защита от ошибок):
- Peer review для quality control
- Human approval для новых правил
- Admin oversight для pattern → rule

---

#### **Pattern Extractor** (`learning/pattern_extractor.py`)

**Извлекает**:
1. **Success Patterns**
   - Что работает хорошо
   - Какие подходы эффективны
   - Best practices по индустриям

2. **Failure Patterns**
   - Частые ошибки
   - Проблемные этапы
   - Warning signs

3. **Optimization Opportunities**
   - Где можно ускорить
   - Где можно автоматизировать
   - Где избыточность

**ML Methods**:
- Clustering (похожие паттерны)
- Association rules (что с чем связано)
- Sequence mining (типичные последовательности)

---

#### **Rule Generator** (`learning/rule_generator.py`)

**Генерирует правила** на основе паттернов:

**Типы правил**:
1. **Validation Rules**
   - "Для финтех всегда требовать RTO < 4 часа для payment processing"

2. **Recommendation Rules**
   - "Если org_size=large → рекомендовать dedicated BCM team"

3. **Automation Rules**
   - "Если BIA criticality=critical → автоматически создать recovery plan"

4. **Warning Rules**
   - "Если planning stage > 5 дней → предложить помощь эксперта"

**Format**:
```python
{
    "rule_id": "rule_123",
    "condition": "industry=healthcare AND process_type=patient_care",
    "action": "set_rto_max_4_hours",
    "confidence": 0.89,
    "support": 47,  # кол-во успешных применений
    "requires_approval": True
}
```

---

## 🔄 Как Всё Работает Вместе

### Сценарий 1: Простой запрос (BIA calculation)

```
User: "Calculate BIA for payment processing"
    ↓
bia-service/colleague (Level 2)
    ↓ (нужен расчёт)
ai_experts/specialists/bcm_advisor (Level 3)
    ↓ (использует)
tools/bia_analysis.py → расчёт RTO/RPO
    +
rag/pipeline.py → контекст из ISO + Cases
    ↓
Result → User
```

---

### Сценарий 2: Комплексная задача (BCM program planning)

```
User: "Create BCM program roadmap"
    ↓
planning-service/colleague (Level 2)
    ↓ (слишком сложно)
ai_experts/specialists/strategic_planner (Level 3)
    ↓ (использует)
1. tools/timeline_predictor.py → сроки
2. tools/resource_planner.py → ресурсы
3. tools/maturity_assessment.py → текущий уровень
    +
4. rag/pipeline.py → best practices из Cases
    +
5. ml/predictive_models.py → предсказание challenges
    ↓
Комплексный roadmap → User
```

---

### Сценарий 3: Самообучение

```
BIA Workflow Completed (успешно)
    ↓
learning/self_learning_engine.py
    ↓
1. Collect: {industry: fintech, process: payment, rto: 2h, success: true}
    ↓
2. learning/pattern_extractor.py
   - Находит паттерн: "fintech payment → always RTO < 4h"
    ↓
3. IF frequency > 10 AND success_rate > 80%
    ↓
4. learning/rule_generator.py
   - Предлагает правило: "Для fintech payment устанавливать RTO max 4 часа"
    ↓
5. Human Review → APPROVE
    ↓
6. Правило применяется автоматически в будущих BIA для fintech
```

---

## 📊 Статус Реализации (22%)

### ✅ Реализовано (7 файлов, 520 строк):
- base/expert_agent.py - базовый класс
- specialists/ - 3 специалиста (заглушки с структурой)
- tools/base_tool.py - базовый класс Tools
- tools/bia_tools.py, compliance_tools.py, strategic_tools.py - частично

### ❌ НЕ реализовано (34 файла):
- RAG pipeline - полностью отсутствует
- ML models - полностью отсутствует
- Learning engine - полностью отсутствует
- API endpoints - отсутствуют
- Tests - отсутствуют

### 🔧 Критические проблемы:
1. **Imports broken** - модуль не импортируется
2. **9 Tools missing** - только базовые классы
3. **RAG missing** - нет retrieval
4. **ML missing** - нет предсказаний
5. **No tests** - нет тестов

---

## 🎯 Ключевая Функциональность

### Что Делает AI Experts:

1. **Координация** (Specialists)
   - Управляют несколькими модулями
   - Сложная бизнес-логика
   - Стратегические решения

2. **Экспертиза** (Tools)
   - BIA calculations
   - Compliance checks
   - Resource planning
   - Timeline predictions

3. **Контекст** (RAG)
   - ISO стандарты
   - Успешные кейсы
   - Best practices

4. **Предсказания** (ML)
   - Stage duration
   - Stuck probability
   - Expert help needed

5. **Самообучение** (Learning)
   - Паттерны из workflows
   - Автоматические правила
   - Continuous improvement

---

## 💡 Место в Архитектуре

```
User Request
    ↓
ai_platform/chief (routing)
    ↓
platform-services/{module}/colleague (Level 2 - модуль)
    ↓
НЕТ Tools? → простой анализ через organs
ЕСТЬ Tools? → делегирует ↓
    ↓
ai_experts/specialists (Level 3 - топ)
    ↓ (использует)
    ├── Tools (DB операции, расчёты)
    ├── RAG (контекст из KG + Cases)
    ├── ML (предсказания)
    └── Learning (самообучение)
    ↓
Result → colleague → User
```

---

## ✅ Резюме

**AI Experts** = "Мозг платформы"

**Роль**:
- Топовый интеллектуальный слой
- Координация нескольких модулей
- Сложная аналитика + предсказания
- Самообучение на опыте

**Когда используется**:
- Сложные расчёты (BIA, Compliance, Planning)
- Межмодульная координация
- Стратегические решения
- Предсказания и оптимизация

**НЕ используется**:
- Простой диалог (это коллеги в модулях)
- Базовый LLM анализ (это органы в модулях)
- CRUD операции (это services в модулях)

**Статус**: 22% реализации, но **архитектура продумана правильно** ✅
