# 🤔 Где Должны Быть Tools?

## Вопрос: Tools в топовых Specialists или в модулях?

### Вариант 1: Tools ТОЛЬКО у топовых Specialists (текущий)
```
intelligent-core/ai_experts/
├── specialists/              # 3 топовых
│   ├── bcm_advisor.py       # Координатор BIA/Risk/Planning
│   ├── compliance_auditor.py
│   └── strategic_planner.py
└── tools/                    # ВСЕ Tools здесь
    ├── bia_tools.py
    ├── compliance_tools.py
    └── strategic_tools.py

platform-services/bia-service/
└── colleague/bia_specialist.py
    └── НЕТ Tools → делегирует BCMAdvisor
```

**Проблема**: Коллега в модуле для ПРОСТОГО расчёта BIA → вызывает топовый Specialist → overhead

---

### Вариант 2: Tools В МОДУЛЯХ (там где нужны)
```
platform-services/bia-service/
├── colleague/bia_specialist.py
├── organs/impact_oracle.py
└── tools/                    # Tools МОДУЛЯ
    ├── bia_analysis.py      # BIAAnalysisTool
    ├── dependency_mapper.py
    └── impact_calculator.py

platform-services/compliance-service/
└── tools/                    # Tools МОДУЛЯ
    ├── compliance_check.py
    ├── gap_analysis.py
    └── evidence_validator.py
```

**Плюс**: Коллега сразу использует Tools, без делегирования

**Минус**: Дублирование Tools между модулями?

---

## 📊 Анализ: Какие Tools Где Нужны

### BIA Tools

| Tool | Где используется | Частота |
|------|------------------|---------|
| **BIAAnalysisTool** | bia-service, planning-service, risk-service | ⚡⚡⚡ ЧАСТО |
| **DependencyMapperTool** | bia-service, planning-service | ⚡⚡ СРЕДНЕ |
| **ImpactCalculatorTool** | bia-service, risk-service | ⚡⚡⚡ ЧАСТО |

**Вывод**: BIA Tools нужны в **нескольких** модулях → кандидат на shared

---

### Compliance Tools

| Tool | Где используется | Частота |
|------|------------------|---------|
| **ComplianceCheckTool** | compliance-service, governance-service | ⚡⚡⚡ ЧАСТО |
| **GapAnalysisTool** | compliance-service, governance-service | ⚡⚡ СРЕДНЕ |
| **EvidenceValidatorTool** | compliance-service, documents-service | ⚡⚡ СРЕДНЕ |

**Вывод**: Compliance Tools в основном в compliance-service → можно в модуле

---

### Strategic Tools

| Tool | Где используется | Частота |
|------|------------------|---------|
| **TimelinePredictorTool** | planning-service, learning-service | ⚡ РЕДКО |
| **ResourcePlannerTool** | planning-service, governance-service | ⚡ РЕДКО |
| **MaturityAssessmentTool** | governance-service, validation-service | ⚡⚡ СРЕДНЕ |

**Вывод**: Strategic Tools редко нужны → остаются у топовых Specialists

---

### Case Library Tools

| Tool | Где используется | Частота |
|------|------------------|---------|
| **CaseSearchTool** | ВСЕ модули | ⚡⚡⚡ ВЕЗДЕ |
| **BestPracticeLibraryTool** | ВСЕ модули | ⚡⚡⚡ ВЕЗДЕ |

**Вывод**: Case Library Tools нужны ВЕЗДЕ → точно shared!

---

## 💡 Оптимальное Решение

### Уровень 1: SHARED Tools (используются везде)
```
shared/tools/                 # Общие для всех
├── case_search.py           # CaseSearchTool
└── best_practices.py        # BestPracticeLibraryTool
```

**Используют**: ВСЕ модули и Specialists

---

### Уровень 2: MODULE-SPECIFIC Tools (частые в модуле)
```
platform-services/bia-service/tools/
├── bia_analysis.py          # BIAAnalysisTool - ЧАСТО в BIA
├── dependency_mapper.py     # DependencyMapperTool
└── impact_calculator.py     # ImpactCalculatorTool

platform-services/compliance-service/tools/
├── compliance_check.py      # ComplianceCheckTool - ЧАСТО в Compliance
├── gap_analysis.py          # GapAnalysisTool
└── evidence_validator.py    # EvidenceValidatorTool

platform-services/risk-service/tools/
└── impact_calculator.py     # Может переиспользовать из shared
```

**Используют**: Коллеги в модуле, Specialists (если координируют)

---

### Уровень 3: SPECIALIST-ONLY Tools (редкие, стратегические)
```
intelligent-core/ai_experts/tools/
├── timeline_predictor.py    # TimelinePredictorTool - РЕДКО
├── resource_planner.py      # ResourcePlannerTool - РЕДКО
└── maturity_assessment.py   # MaturityAssessmentTool
```

**Используют**: ТОЛЬКО топовые Specialists (для стратегии, координации)

---

## 🎯 Итоговая Архитектура Tools

```
┌─────────────────────────────────────────────────────────┐
│              shared/tools/                              │
│  ┌────────────────┐  ┌────────────────────────────┐    │
│  │ CaseSearchTool │  │ BestPracticeLibraryTool    │    │
│  └────────────────┘  └────────────────────────────┘    │
│                                                         │
│  Используют: ВСЕ (модули + specialists)                │
└─────────────────────────────────────────────────────────┘
                          ↑
        ┌─────────────────┼─────────────────┐
        ↓                 ↓                 ↓
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ bia-service  │  │compliance-   │  │ risk-service │
│              │  │service       │  │              │
│ tools/       │  │ tools/       │  │ tools/       │
│ ├─bia_...    │  │ ├─compliance │  │ ├─impact_... │
│ ├─dependency │  │ ├─gap_...    │  │              │
│ └─impact_... │  │ └─evidence   │  │              │
│              │  │              │  │              │
│ Используют:  │  │ Используют:  │  │ Используют:  │
│ - Colleague  │  │ - Colleague  │  │ - Colleague  │
│ - BCMAdvisor │  │ - CompAuditor│  │ - BCMAdvisor │
└──────────────┘  └──────────────┘  └──────────────┘
                          ↑
                          │
┌─────────────────────────────────────────────────────────┐
│       intelligent-core/ai_experts/tools/                │
│  ┌────────────────┐  ┌────────────────────────────┐    │
│  │TimelinePredictor│ │ ResourcePlanner            │    │
│  └────────────────┘  └────────────────────────────┘    │
│                                                         │
│  Используют: ТОЛЬКО топовые Specialists                │
│  (для стратегии, координации, предиктивности)          │
└─────────────────────────────────────────────────────────┘
```

---

## 📋 Распределение Tools

### SHARED (2 инструмента)
- ✅ CaseSearchTool
- ✅ BestPracticeLibraryTool

**Где**: `/shared/tools/`
**Кто использует**: Все

---

### MODULE-SPECIFIC (6-8 инструментов)

**bia-service/tools/**:
- ✅ BIAAnalysisTool
- ✅ DependencyMapperTool
- ✅ ImpactCalculatorTool

**compliance-service/tools/**:
- ✅ ComplianceCheckTool
- ✅ GapAnalysisTool
- ✅ EvidenceValidatorTool

**risk-service/tools/**:
- ✅ ImpactCalculatorTool (или shared)
- ✅ RiskCalculationTool (если специфичный)

**planning-service/tools/**:
- ✅ DependencyMapperTool (или shared)
- ✅ PlanGeneratorTool

---

### SPECIALIST-ONLY (3 инструмента)
- ✅ TimelinePredictorTool
- ✅ ResourcePlannerTool
- ✅ MaturityAssessmentTool

**Где**: `/intelligent-core/ai_experts/tools/`
**Кто использует**: Только топовые Specialists

---

## 🔄 Как Это Работает

### Сценарий 1: Простой BIA расчёт (внутри модуля)
```
User: "Calculate BIA for payment processing"
     ↓
bia-service/colleague/bia_specialist.py
     ↓ (использует локальный Tool)
bia-service/tools/bia_analysis.py
     ↓
Result → User
```
**Эффективно**: Без делегирования, быстро

---

### Сценарий 2: Комплексная стратегия (нужен топовый Specialist)
```
User: "Create BCM program roadmap with timeline and resources"
     ↓
planning-service/colleague/plan_generator.py
     ↓ (слишком сложно, делегирует)
ai_experts/specialists/strategic_planner.py
     ↓ (использует специальные Tools)
tools/timeline_predictor.py + tools/resource_planner.py
     ↓
Result → planning-service → User
```
**Эффективно**: Специалист координирует, имеет доступ к стратегическим Tools

---

### Сценарий 3: Поиск похожих кейсов (shared tool)
```
Любой модуль/colleague
     ↓
shared/tools/case_search.py
     ↓
Case Library
     ↓
Result
```
**Эффективно**: Один Tool, все используют

---

## ✅ Рекомендация

### Вариант 3: ГИБРИДНЫЙ (оптимальный)

1. **Shared Tools** → `/shared/tools/`
   - CaseSearchTool, BestPracticeLibraryTool
   - Используют ВСЕ

2. **Module Tools** → `/platform-services/{service}/tools/`
   - Частые Tools для этого модуля
   - Используют Коллеги в модуле

3. **Specialist Tools** → `/intelligent-core/ai_experts/tools/`
   - Редкие, стратегические Tools
   - Используют ТОЛЬКО топовые Specialists

**Плюсы**:
- ✅ Нет дублирования (shared)
- ✅ Быстро (модульные Tools без делегирования)
- ✅ Стратегия централизована (specialist Tools)

**Это эффективно?** 🤔
