# 🧠 AI Organs - Роль и Назначение

**Дата**: October 5, 2025
**Вопрос**: Что такое Organs и зачем они нужны?

---

## 🎯 Что такое AI Organs?

**AI Organs** = **Specialized Workers** (специализированные исполнители задач)

### Метафора: Как в организме человека

```
Человек:
👤 Мозг (Brain) → принимает решения, думает
❤️ Сердце (Heart) → перекачивает кровь (execution)
🫁 Лёгкие (Lungs) → дышат (execution)
🧠 Печень (Liver) → фильтрует (execution)

AI Платформа:
🤖 AI Expert (Specialist) → консультирует, общается с пользователем
🔮 Impact Oracle (Organ) → ВЫЧИСЛЯЕТ impact (heavy math)
🛡️ Compliance Guardian (Organ) → ПРОВЕРЯЕТ compliance (automation)
📊 Performance Analyst (Organ) → АНАЛИЗИРУЕТ данные (processing)
```

---

## 📊 Разница: Specialists vs Organs

### AI Specialists (Эксперты)

**Роль**: User-facing консультанты
- ✅ Общаются с пользователем
- ✅ Дают qualitative советы
- ✅ Используют RAG для контекста
- ✅ Synthesize информацию
- ❌ НЕ делают heavy computations сами

**Пример**:
```
User: "Как рассчитать RTO для emergency department?"
  ↓
BIA Specialist (Expert):
"Для emergency department в healthcare обычно RTO 1-4 часа.
Это зависит от типа больницы, доступных ресурсов...
Давайте рассчитаем для вашего случая."
```

### AI Organs (Органы)

**Роль**: Execution workers (исполнители)
- ✅ Выполняют конкретные задачи
- ✅ Heavy computations
- ✅ Automation
- ✅ Data processing
- ❌ НЕ общаются с пользователем напрямую

**Пример**:
```python
Impact Oracle (Organ):
input: process_data, disruption_scenario
output: {
  "financial_impact_min": 100000,
  "financial_impact_max": 500000,
  "rto_recommended": 4,
  "rpo_recommended": 1,
  "severity": "critical"
}
```

---

## 🔄 Как они работают вместе?

### Pattern: Specialist ИСПОЛЬЗУЕТ Organs

```
User Query
    ↓
┌─────────────────────────────┐
│ BIA Specialist (Expert)     │
│ - Понимает вопрос           │
│ - Даёт контекст             │
│ - Synthesize ответ          │
└────────┬────────────────────┘
         │ uses
         ▼
┌─────────────────────────────┐
│ Impact Oracle (Organ)       │
│ - Вычисляет impact          │
│ - Рекомендует RTO/RPO       │
│ - Quantitative analysis     │
└─────────────────────────────┘
```

**Код**:
```python
class BIASpecialist(ExpertAgent):
    def __init__(self, rag_pipeline, organs):
        self.rag = rag_pipeline
        self.impact_oracle = organs['impact_oracle']  # Organ как tool

    async def advise(self, query, context):
        # 1. RAG для qualitative context
        rag_context = await self.rag.process_query(
            "Best practices for RTO determination"
        )

        # 2. Organ для quantitative analysis
        impact_analysis = await self.impact_oracle.analyze({
            'process_data': context['process'],
            'disruption_scenario': 'complete_outage'
        })

        # 3. Synthesize
        return {
            'advice': rag_context.content,  # Qualitative
            'calculations': impact_analysis,  # Quantitative
            'recommendation': self._combine(rag_context, impact_analysis)
        }
```

---

## 📋 10 AI Organs и их роли

| Organ | Emoji | Роль | Используется кем |
|-------|-------|------|------------------|
| **Impact Oracle** 🔮 | Predictive BIA | Вычисляет impact, RTO/RPO | BIA Specialist |
| **Compliance Guardian** 🛡️ | Compliance checks | Проверяет ISO 22301 соответствие | Compliance Auditor |
| **Risk Advisor** ⚖️ | Risk treatment | Рекомендует risk treatments | Risk Analyst |
| **Plan Generator** 📝 | Document generation | Генерирует BC plan documents | Planning Specialist |
| **Scenario Creator** 🎭 | Scenario generation | Создаёт exercise scenarios | Exercise Designer |
| **Emergency Response** 🚨 | Incident handling | Автоматизирует incident response | Incident Expert |
| **Governance Brain** 🧠 | Governance decisions | Governance rule application | Compliance Auditor |
| **Learning Coach** 📚 | Learning optimization | Оптимизирует learning paths | Knowledge Manager |
| **Lifecycle Monitor** 🔄 | Lifecycle tracking | Отслеживает BCM lifecycle | All Specialists |
| **Performance Analyst** 📊 | Performance analysis | Анализирует BCM performance | Predictive Analyst |

---

## 🎯 Три Способа Работы

### 1. Specialist → Organ (Direct)

**Когда**: Нужны heavy computations

```python
class BIASpecialist:
    async def calculate_impact(self, process):
        # Direct call to organ
        return await self.impact_oracle.analyze({
            'process_data': process
        })
```

### 2. Specialist → Tool → Organ (Layered)

**Когда**: Нужна structured interface

```python
class BIASpecialist:
    async def analyze_bia(self, process):
        # Tool wraps organ
        result = await self.bia_tool.execute({
            'process': process
        })
        # Tool internally uses Impact Oracle
```

### 3. Specialist → Multiple Organs (Orchestrated)

**Когда**: Сложная задача требует нескольких organs

```python
class ComplianceAuditor:
    async def full_compliance_check(self, org_data):
        # Multiple organs in parallel
        compliance = await self.compliance_guardian.analyze(org_data)
        governance = await self.governance_brain.analyze(org_data)
        lifecycle = await self.lifecycle_monitor.analyze(org_data)

        # Synthesize
        return self._combine(compliance, governance, lifecycle)
```

---

## 💡 Зачем разделять Specialists и Organs?

### Причина 1: Разделение ответственности

```
Specialist = "ЧТО делать" (консультация)
Organ = "КАК делать" (execution)
```

### Причина 2: Reusability

```
Impact Oracle (один organ)
  ↑
  используется:
  - BIA Specialist
  - Risk Analyst
  - Planning Specialist
  - Predictive Analyst
```

### Причина 3: Scalability

```
Добавить новый Specialist → легко (просто консультант)
Добавить новый Organ → легко (просто worker)

Specialist может использовать ЛЮБЫЕ organs
Organ может быть использован ЛЮБЫМИ specialists
```

### Причина 4: Testing

```
Test Specialist → mock organs
Test Organ → isolated unit tests
```

---

## 🤔 Вопрос: Нужны ли Organs в ai_experts?

### Вариант A: ДА, нужны! (РЕКОМЕНДУЮ)

**Архитектура**:
```
ai_experts/
├── specialists/          # 11 AI Experts (user-facing)
│   ├── bia_specialist.py
│   ├── risk_analyst.py
│   └── ...
│
├── organs/               # 10 Workers (execution)
│   ├── impact_oracle.py
│   ├── compliance_guardian.py
│   └── ...
│
├── tools/                # Structured tools (wrappers)
│   ├── bia_tools.py      # May use organs internally
│   └── ...
```

**Как работает**:
```python
# Specialist использует и tools И organs

class BIASpecialist(ExpertAgent):
    def __init__(self, tools, organs):
        self.tools = tools  # Structured tools для Anthropic
        self.organs = organs  # Heavy workers для computations

    async def advise(self, query, context):
        # Use tool (structured)
        tool_result = await self.bia_tool.execute(context)

        # Use organ (heavy computation)
        organ_result = await self.impact_oracle.analyze(context)

        # Combine
        return self._synthesize(tool_result, organ_result)
```

**Преимущества**:
- ✅ Specialists = консультанты (qualitative)
- ✅ Tools = structured interface (для Anthropic)
- ✅ Organs = heavy workers (quantitative)
- ✅ Best of all worlds

---

### Вариант B: НЕТ, заменить на tools (альтернатива)

**Архитектура**:
```
ai_experts/
├── specialists/
├── tools/               # Tools заменяют organs
│   ├── bia_tools.py     # Вся логика внутри
│   └── ...
```

**Как работает**:
```python
class BIASpecialist(ExpertAgent):
    def __init__(self, tools):
        self.tools = tools  # Только tools

    async def advise(self, query, context):
        # Tools делают всё
        result = await self.bia_tool.execute(context)
```

**Недостатки**:
- ❌ Tools перегружены логикой
- ❌ Сложнее reuse
- ❌ Тяжелее тестировать

---

## ✅ Моя Рекомендация

### **Вариант A: Specialists + Tools + Organs**

**Три слоя**:
```
Layer 1: Specialists (консультанты, user-facing)
    ↓ uses
Layer 2: Tools (structured interface, Anthropic tool calling)
    ↓ uses
Layer 3: Organs (execution workers, heavy computations)
```

**Пример**:
```python
# Layer 1: Specialist
class BIASpecialist(ExpertAgent):
    tools = [BIAAnalysisTool]  # Layer 2
    organs = {'impact_oracle': ImpactOracle()}  # Layer 3

# Layer 2: Tool
class BIAAnalysisTool(BaseTool):
    def __init__(self, impact_oracle):
        self.oracle = impact_oracle  # Uses organ

    async def execute(self, params):
        # Structured interface
        # Heavy work delegated to organ
        return await self.oracle.analyze(params)

# Layer 3: Organ
class ImpactOracle(BaseOrgan):
    async def analyze(self, context):
        # Pure execution (heavy math)
        return calculations
```

**Роли**:
- **Specialist** = консультант (talks to user)
- **Tool** = structured interface (Anthropic format)
- **Organ** = worker (does heavy lifting)

---

## 🎯 Финальное Решение

### ai_experts структура:

```
ai_experts/
├── specialists/          # 11 консультантов
│   ├── chief_bcm_advisor.py
│   ├── bia_specialist.py
│   ├── risk_analyst.py
│   └── ...
│
├── tools/                # Structured tools (Anthropic format)
│   ├── bia_tools.py
│   ├── compliance_tools.py
│   └── ...
│
├── organs/               # Execution workers
│   ├── impact_oracle.py
│   ├── compliance_guardian.py
│   ├── risk_advisor.py
│   └── ...
│
├── base/
│   ├── expert_agent.py   # Base для specialists
│   ├── base_tool.py      # Base для tools
│   └── base_organ.py     # Base для organs
```

**Integration**:
```python
# Specialist USES tools AND organs

specialist = BIASpecialist(
    tools=[BIAAnalysisTool(impact_oracle)],  # Tools wrap organs
    organs={'impact_oracle': ImpactOracle()}  # Direct organ access
)

# Flexible usage:
result1 = await specialist.use_tool('bia_analysis', params)  # Via tool
result2 = await specialist.organs['impact_oracle'].analyze(params)  # Direct
```

---

## 📝 Summary

**AI Organs** = специализированные workers для execution

**Роль**:
- ❌ НЕ консультанты (не общаются с пользователем)
- ✅ Execution workers (делают heavy work)
- ✅ Используются Specialists как helpers
- ✅ Reusable across specialists

**Решение**:
- ✅ Мигрировать organs из ai-office в ai_experts
- ✅ Specialists используют organs через tools ИЛИ напрямую
- ✅ Три слоя: Specialists → Tools → Organs

**Преимущества**:
- ✅ Clear separation of concerns
- ✅ Reusability
- ✅ Scalability
- ✅ Testability

---

**Generated**: October 5, 2025
**Purpose**: Объяснить роль AI Organs
**Answer**: Organs = execution workers, используются Specialists
