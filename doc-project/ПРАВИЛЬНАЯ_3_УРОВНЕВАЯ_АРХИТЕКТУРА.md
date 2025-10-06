# ✅ ПРАВИЛЬНАЯ 3-Уровневая AI Архитектура

## 🎯 Роли Компонентов (как задумано)

### Level 1: ОРГАНЫ - Поиск/Анализ (в модулях)
**Где**: `/platform-services/{service}/organs/`

**Роль**: Система поиска и LLM анализа внутри модуля

**Характеристики**:
- LLM prompts (system/user)
- Специализированный анализ
- **НЕТ взаимодействия с пользователем**
- Используются Коллегами и Специалистами

**Пример - Risk Service**:
```
platform-services/risk-service/
└── organs/
    └── risk_advisor.py          # Из ai-office/organs/
        └── analyze(context) → LLM analysis
```

---

### Level 2: КОЛЛЕГИ - Менеджеры Модулей (в модулях)
**Где**: `/platform-services/{service}/colleague/`

**Роль**: Менеджеры модулей, общаются с пользователями

**Характеристики**:
- ✅ Диалог с пользователем
- ✅ PDCA integration
- ✅ RAG pipeline
- ✅ Управляют органами (внутри модуля)
- ✅ Связь с главным AI мозгом (ChiefExecutiveAI)
- ❌ НЕТ Tools (делегируют Специалистам)

**Пример - Risk Service**:
```
platform-services/risk-service/
└── colleague/
    └── risk_analyst.py          # Из ai-office/ВСМ-colleagues/
        ├── chat(message) → диалог
        ├── использует organs/risk_advisor
        └── делегирует к Specialists (если нужны Tools)
```

---

### Level 3: СПЕЦИАЛИСТЫ - Верхний AI Слой (над модулями)
**Где**: `/intelligent-core/ai_experts/specialists/`

**Роль**: Верхний уровень AI с Tools и межмодульной интеграцией

**Характеристики**:
- ✅ **Tools** (DB операции, внешние интеграции)
- ✅ Knowledge Graph
- ✅ Case Library
- ✅ Передача в другие AI (обучение, предиктивность)
- ✅ Межмодульная координация

**Пример**:
```
intelligent-core/ai_experts/specialists/
├── bcm_advisor.py               # Координирует BIA/Planning/Risk
├── compliance_auditor.py        # Координирует Compliance/Governance
└── strategic_planner.py         # Стратегия, предиктивность
```

---

## 🔄 Как Это Работает

### Сценарий 1: Простой запрос внутри модуля

```
User: "Identify risks for payment processing"
     ↓
ChiefExecutiveAI (routing)
     ↓
platform-services/risk-service/colleague/risk_analyst.py
     ↓ (использует)
platform-services/risk-service/organs/risk_advisor.py
     ↓ (LLM analysis)
Result → User
```

**В модуле**:
- Коллега (RiskAnalyst) - диалог
- Орган (RiskAdvisor) - LLM анализ
- БЕЗ выхода из модуля

---

### Сценарий 2: Сложный запрос с Tools

```
User: "Calculate BIA impact and create compliance report"
     ↓
ChiefExecutiveAI (routing)
     ↓
platform-services/bia-service/colleague/bia_specialist.py
     ↓ (нужны Tools для расчётов)
intelligent-core/ai_experts/specialists/bcm_advisor.py
     ↓ (использует Tools)
ai_experts/tools/bia_tools.py → BIAAnalysisTool
     ↓ (нужен Compliance)
platform-services/compliance-service/colleague/compliance_copilot.py
     ↓
Result → User
```

**Межмодульная координация**:
- Коллега BIA → Специалист BCM (для Tools)
- Специалист BCM → Коллега Compliance (для отчёта)
- Специалист → Обучение/Предиктивность

---

### Сценарий 3: Обучение и предиктивность

```
Specialist bcm_advisor.py
     ↓ (после выполнения задачи)
передаёт в Learning AI
     ↓
intelligent-core/community_intelligence/
     ↓ (анализ паттернов)
Case Library обновляется
     ↓
Predictive Analytics
```

---

## 📋 Структура Каждого Сервиса

```
platform-services/risk-service/
│
├── main.py                      # FastAPI app
├── api/
│   ├── routes.py                # REST endpoints
│   └── ai_routes.py             # AI chat endpoint
│
├── colleague/                    # МЕНЕДЖЕР МОДУЛЯ
│   └── risk_analyst.py          # Из ai-office/ВСМ-colleagues/
│       ├── chat(message)        # Диалог с пользователем
│       ├── pdca_context         # PDCA integration
│       ├── rag_pipeline         # RAG
│       └── использует organs/
│
├── organs/                       # ПОИСК/АНАЛИЗ
│   └── risk_advisor.py          # Из ai-office/organs/
│       └── analyze(context)     # LLM prompts
│
├── services/                     # Бизнес-логика
├── models/                       # DB models
└── workflow_integration.py       # workflow_intelligence
```

---

## 🌐 Интеграция Специалистов (Level 3)

```
intelligent-core/ai_experts/
│
├── specialists/                  # ВЕРХНИЙ AI СЛОЙ
│   ├── bcm_advisor.py
│   │   └── координирует: BIA + Risk + Planning
│   ├── compliance_auditor.py
│   │   └── координирует: Compliance + Governance + Audit
│   └── strategic_planner.py
│       └── координирует: Strategy + Predictive + Learning
│
├── tools/                        # TOOLS (только для Specialists)
│   ├── bia_tools.py             # BIAAnalysisTool, DependencyMapper
│   ├── compliance_tools.py      # ComplianceCheck, GapAnalysis
│   └── strategic_tools.py       # StrategicAnalysis, Scenarios
│
└── base/
    └── expert_agent.py          # BaseExpert
```

---

## 🔗 Связи Между Уровнями

### Коллега → Орган (внутри модуля)
```python
# platform-services/risk-service/colleague/risk_analyst.py
class RiskAnalystAI(BaseAIColleague):
    def __init__(self, rag_pipeline):
        self.organ = RiskAdvisor()  # Свой орган

    async def chat(self, message):
        # 1. PDCA context
        # 2. RAG retrieval
        # 3. Используем орган для анализа
        analysis = await self.organ.analyze({
            "scenario": message,
            "context": self.pdca_context
        })
        return self._format_response(analysis)
```

### Коллега → Специалист (для Tools)
```python
# Когда нужны Tools
class RiskAnalystAI(BaseAIColleague):
    async def chat(self, message):
        if self._needs_tools(message):
            # Делегируем Специалисту
            specialist = BCMAdvisor(case_library, kg)
            result = await specialist.advise(message, context)
            return result
        else:
            # Используем свой орган
            return await self.organ.analyze(...)
```

### Специалист → Другие AI
```python
# intelligent-core/ai_experts/specialists/bcm_advisor.py
class BCMAdvisor(ExpertAgent):
    async def advise(self, query, context):
        # 1. Используем Tools
        bia_result = await self.tools['bia_analysis'].execute(context)

        # 2. Передаём в обучение
        await learning_ai.learn_from_case({
            "action": "bia_analysis",
            "result": bia_result,
            "industry": context['industry']
        })

        # 3. Получаем предиктивность
        predictions = await predictive_ai.predict_next_risks(context)

        # 4. Возвращаем комплексный результат
        return {
            "bia": bia_result,
            "predictions": predictions,
            "recommendations": self._generate_recommendations(...)
        }
```

---

## 🎯 Итоговая Архитектура

```
┌─────────────────────────────────────────────────────────┐
│          intelligent-core/ai_experts/                   │
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │BCM Advisor   │  │Compliance    │  │Strategic     │ │
│  │(Specialist)  │  │Auditor       │  │Planner       │ │
│  │              │  │(Specialist)  │  │(Specialist)  │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│         ↕                  ↕                 ↕          │
│  ┌──────────────────────────────────────────────────┐ │
│  │           Tools (BIA, Compliance, Strategic)     │ │
│  └──────────────────────────────────────────────────┘ │
│         ↕                  ↕                 ↕          │
│  ┌──────────────────────────────────────────────────┐ │
│  │  Learning AI + Predictive AI + Case Library     │ │
│  └──────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
                          ↕
┌─────────────────────────────────────────────────────────┐
│              ai_platform (ChiefExecutiveAI)            │
│                     Routing Layer                       │
└─────────────────────────────────────────────────────────┘
                          ↕
┌─────────────────────────────────────────────────────────┐
│              platform-services/                         │
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │risk-service  │  │bia-service   │  │compliance-   │ │
│  │              │  │              │  │service       │ │
│  │ colleague/   │  │ colleague/   │  │ colleague/   │ │
│  │ ├─analyst    │  │ ├─specialist │  │ ├─copilot    │ │
│  │ organs/      │  │ organs/      │  │ organs/      │ │
│  │ └─advisor    │  │ └─oracle     │  │ └─guardian   │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────┘
                          ↕
┌─────────────────────────────────────────────────────────┐
│           workflow_intelligence (Infrastructure)        │
└─────────────────────────────────────────────────────────┘
```

---

## 📝 Пример Потока

### Запрос: "Calculate BIA and identify risks for payment processing"

**Шаг 1**: ChiefExecutiveAI → routing
- Intent: BIA + Risk
- Route to: DomainManager

**Шаг 2**: DomainManager → bia-service
```
POST http://localhost:8041/api/v1/ai/chat
{
  "message": "Calculate BIA for payment processing",
  "context": {...}
}
```

**Шаг 3**: bia-service/colleague/bia_specialist.py
- Простой анализ? → использует organs/impact_oracle.py
- Нужны расчёты? → делегирует к BCMAdvisor (Specialist)

**Шаг 4**: ai_experts/specialists/bcm_advisor.py
- Использует BIAAnalysisTool (Tools)
- Сохраняет в Case Library
- Передаёт в Learning AI

**Шаг 5**: Нужен Risk?
- BCMAdvisor → вызывает risk-service/colleague/risk_analyst.py
- RiskAnalyst → использует organs/risk_advisor.py

**Шаг 6**: Predictive AI
- Анализирует паттерны
- Предсказывает следующие риски

**Результат** → User

---

## ✅ Итого: Роли Чёткие

| Уровень | Компонент | Где | Роль |
|---------|-----------|-----|------|
| **Level 1** | **Органы** | `platform-services/{service}/organs/` | Поиск/LLM анализ внутри модуля |
| **Level 2** | **Коллеги** | `platform-services/{service}/colleague/` | Менеджеры модулей, диалог с пользователем |
| **Level 3** | **Специалисты** | `intelligent-core/ai_experts/specialists/` | Верхний AI с Tools, межмодульная координация |

**Органы** → используются Коллегами
**Коллеги** → менеджеры модулей, связь с главным мозгом
**Специалисты** → Tools + обучение + предиктивность + межмодульная работа

**Эффективно!** ✅
