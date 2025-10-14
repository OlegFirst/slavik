# 🎯 Domain Knowledge Integration - Примеры использования

**Date**: 2025-10-06
**Status**: Integration Complete

---

## Как домены теперь используют learning-knowledge

Все базовые классы (BaseSpecialist, BaseTacticalAssistant, BaseAnalyzer) теперь имеют доступ к `self.knowledge` - адаптеру для получения доменных знаний из learning-knowledge.

---

## 📚 Доступные методы через self.knowledge

### 1. RTO Benchmarks (для BIA Specialist)
```python
# В BIA Specialist
async def get_rto_recommendation(self, industry: str, process_type: str):
    """Получить RTO benchmark для индустрии"""
    benchmarks = await self.knowledge.get_rto_benchmarks(
        industry=industry,
        process_type=process_type
    )
    return benchmarks
```

**Пример**:
```python
# Finance, Trading Platform
benchmarks = await self.knowledge.get_rto_benchmarks(
    industry="finance",
    process_type="trading"
)
# Вернет: {"trading_platform": "15 minutes", "confidence": 0.85}
```

---

### 2. Threat Scenarios (для Risk Analyst)
```python
# В Risk Analyst
async def get_threat_scenarios(self, industry: str, scenario_type: str = None):
    """Получить сценарии угроз для индустрии"""
    scenarios = await self.knowledge.get_threat_scenarios(
        industry=industry,
        scenario_type=scenario_type
    )
    return scenarios
```

**Пример**:
```python
# Healthcare, Ransomware
scenarios = await self.knowledge.get_threat_scenarios(
    industry="healthcare",
    scenario_type="ransomware"
)
# Вернет: список сценариев с вероятностью и воздействием
```

---

### 3. Plan Templates (для Plan Generator)
```python
# В Plan Generator
async def get_plan_template(self, plan_type: str, industry: str = None):
    """Получить шаблон плана"""
    templates = await self.knowledge.get_plan_templates(
        plan_type=plan_type,
        industry=industry
    )
    return templates
```

**Пример**:
```python
# BCP для производства
templates = await self.knowledge.get_plan_templates(
    plan_type="bcp",
    industry="manufacturing"
)
# Вернет: шаблон плана с секциями, специфичными для производства
```

---

### 4. ISO Standards (для Compliance Copilot)
```python
# В Compliance Copilot
async def get_iso_requirements(self, standard_id: str, clause: str = None):
    """Получить требования ISO стандарта"""
    standard = await self.knowledge.get_iso_standard(
        standard_id=standard_id,
        clause=clause
    )
    return standard
```

**Пример**:
```python
# ISO 22301, Clause 8.2.2 (BIA)
standard = await self.knowledge.get_iso_standard(
    standard_id="iso-22301",
    clause="8.2.2"
)
# Вернет: требования по BIA из ISO 22301
```

---

### 5. Similar Cases (для всех доменов)
```python
# В любом Specialist/Assistant/Analyzer
async def find_similar_cases(self, module: str, filters: dict, limit: int = 5):
    """Найти похожие кейсы"""
    cases = await self.knowledge.search_cases(
        module=module,
        filters=filters,
        limit=limit
    )
    return cases
```

**Пример**:
```python
# Найти похожие BIA для финансов
cases = await self.knowledge.search_cases(
    module="bia",
    filters={
        "industry": "finance",
        "size": "enterprise",
        "critical_process": "trading"
    },
    limit=5
)
# Вернет: 5 похожих BIA кейсов с контекстом
```

---

## 🎯 Реальный пример: BIA Specialist + Knowledge Integration

### До интеграции (старый код):
```python
class BIASpecialistAI(BaseTacticalAssistant):
    async def recommend_rto(self, process_name: str, industry: str):
        # Использовал только RAG (общий поиск)
        context = await self.rag.retrieve(
            query=f"RTO for {process_name} in {industry}"
        )
        # Нет доменных знаний!
        return {"rto": "unknown"}
```

### После интеграции (новый код):
```python
class BIASpecialistAI(BaseTacticalAssistant):
    async def recommend_rto(self, process_name: str, industry: str):
        # 1. Получить benchmark из knowledge base
        benchmarks = await self.knowledge.get_rto_benchmarks(
            industry=industry,
            process_type=process_name
        )

        # 2. Найти похожие кейсы
        similar_cases = await self.knowledge.search_cases(
            module="bia",
            filters={
                "industry": industry,
                "critical_process": process_name
            },
            limit=3
        )

        # 3. Получить ISO требования
        iso_guidance = await self.knowledge.get_iso_standard(
            standard_id="iso-22301",
            clause="8.2.2"
        )

        # 4. Использовать RAG для дополнительного контекста
        rag_context = await self.rag.retrieve(
            query=f"RTO best practices for {process_name}"
        )

        # 5. Скомбинировать все источники знаний
        recommendation = {
            "rto": benchmarks.get("rto", "4 hours"),
            "confidence": benchmarks.get("confidence", 0.7),
            "based_on": {
                "industry_benchmark": benchmarks,
                "similar_cases": len(similar_cases),
                "iso_guidance": iso_guidance.get("summary"),
                "rag_insights": rag_context
            }
        }

        return recommendation
```

**Результат**: Гораздо более умные рекомендации, основанные на:
- ✅ Индустриальных бенчмарках
- ✅ Реальных кейсах
- ✅ ISO стандартах
- ✅ RAG инсайтах

---

## 🔄 Пример использования во всех типах доменных экспертов

### 1. Specialist (Strategic Level)
```python
# BCM Advisor
class BCMAdvisor(BaseSpecialist):
    async def analyze(self, context, query):
        # Доступ к knowledge
        iso_standard = await self.knowledge.get_iso_standard("iso-22301")
        industry_cases = await self.knowledge.search_cases(
            module="governance",
            filters={"industry": context.get("industry")}
        )

        # Стратегический анализ с доменными знаниями
        ...
```

### 2. Tactical Assistant (Operational Level)
```python
# Plan Generator
class PlanGenerator(BaseTacticalAssistant):
    async def assist(self, task, context):
        # Доступ к knowledge
        template = await self.knowledge.get_plan_templates(
            plan_type="bcp",
            industry=context.get("industry")
        )

        # Генерация плана на основе шаблона
        ...
```

### 3. Analyzer (Heavy AI)
```python
# Risk Analyzer
class RiskAnalyzer(BaseAnalyzer):
    async def analyze(self, data, config):
        # Доступ к knowledge
        threats = await self.knowledge.get_threat_scenarios(
            industry=data.get("industry"),
            scenario_type="cyber"
        )

        # ML анализ с учетом доменных угроз
        ...
```

---

## 🎯 Доменная синхронизация: BCM Domain

### Структура BCM домена:

```
domains/bcm/
├── specialists/           # 3 стратегических эксперта
│   ├── bcm_advisor.py         → использует self.knowledge
│   ├── compliance_auditor.py  → использует self.knowledge
│   └── strategic_planner.py   → использует self.knowledge
│
├── tactical_assistants/   # 7 операционных ассистентов
│   ├── bia_specialist.py      → использует self.knowledge
│   ├── risk_analyst.py        → использует self.knowledge
│   ├── plan_generator.py      → использует self.knowledge
│   ├── incident_advisor.py    → использует self.knowledge
│   ├── exercise_designer.py   → использует self.knowledge
│   ├── compliance_copilot.py  → использует self.knowledge
│   └── documents_specialist.py→ использует self.knowledge
│
└── analyzers/             # 10 тяжелых AI анализаторов
    ├── governance_analyzer.py → использует self.knowledge
    ├── impact_analyzer.py     → использует self.knowledge
    ├── risk_analyzer.py       → использует self.knowledge
    ├── compliance_analyzer.py → использует self.knowledge
    └── ...                    → все используют self.knowledge
```

**Все 20 экспертов BCM домена теперь имеют доступ к:**
- ✅ RTO/RPO benchmarks
- ✅ Threat scenarios
- ✅ Plan templates
- ✅ ISO standards
- ✅ Similar cases
- ✅ KPI benchmarks
- ✅ Compliance requirements

---

## 🚀 Следующие шаги для других доменов

### HR Domain (когда создадим)
```python
# HR Specialist
class HRSpecialist(BaseTacticalAssistant):
    async def assist(self, task, context):
        # Будет использовать HR-specific knowledge
        hr_benchmarks = await self.knowledge.get_domain_knowledge(
            domain_type="hr",
            knowledge_type="benchmarks",
            industry=context.get("industry")
        )
```

### Finance Domain (когда создадим)
```python
# Finance Analyst
class FinanceAnalyzer(BaseAnalyzer):
    async def analyze(self, data, config):
        # Будет использовать Finance-specific knowledge
        financial_ratios = await self.knowledge.get_domain_knowledge(
            domain_type="finance",
            knowledge_type="ratios",
            industry=data.get("industry")
        )
```

---

## ✅ Итог

**Что изменилось:**
1. ✅ Все базовые классы (BaseSpecialist, BaseTacticalAssistant, BaseAnalyzer) имеют `self.knowledge`
2. ✅ Все 20 BCM экспертов автоматически получили доступ к доменным знаниям
3. ✅ Интеграция через learning_knowledge_adapter.py (HTTP API)
4. ✅ Доступ к RTO benchmarks, threat scenarios, templates, ISO standards, cases

**Как использовать:**
- Просто вызывайте `await self.knowledge.get_*()` в любом эксперте
- Все методы асинхронные
- Автоматическое кеширование через Redis
- Все знания из центрального learning-knowledge

**Статус:** ✅ Система доменности синхронизирована с learning-knowledge!
