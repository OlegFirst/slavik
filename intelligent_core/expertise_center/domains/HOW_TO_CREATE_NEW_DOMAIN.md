# 🔌 Как создать новый домен (HR, Finance, и т.д.)

**Version**: 1.0
**Date**: 2025-10-06

---

## 📋 Что такое домен?

Домен = Плагин с экспертами для конкретной области (BCM, HR, Finance, Legal, IT, и т.д.)

Каждый домен содержит:
- **Specialists** (3-5 шт) - Стратегические эксперты
- **Tactical Assistants** (5-10 шт) - Операционные ассистенты
- **Analyzers** (5-10 шт) - Тяжелые AI анализаторы

---

## 🏗️ Структура нового домена

```
expertise-center/domains/
└── {domain_name}/                    # Например: hr, finance, legal
    ├── __init__.py                   # Метаданные домена
    │
    ├── specialists/                  # Стратегические эксперты
    │   ├── __init__.py
    │   ├── {domain}_advisor.py       # Главный советник
    │   ├── compliance_specialist.py  # Compliance эксперт
    │   └── strategic_planner.py      # Стратегический планировщик
    │
    ├── tactical_assistants/          # Операционные ассистенты
    │   ├── __init__.py
    │   ├── {domain}_specialist_1.py
    │   ├── {domain}_specialist_2.py
    │   └── ...
    │
    ├── analyzers/                    # Тяжелые AI анализаторы
    │   ├── __init__.py
    │   ├── {domain}_analyzer_1.py
    │   ├── {domain}_analyzer_2.py
    │   └── ...
    │
    ├── README.md                     # Описание домена
    └── KNOWLEDGE_INTEGRATION_EXAMPLE.md  # Примеры использования knowledge
```

---

## 🚀 Шаги создания нового домена

### Шаг 1: Создать структуру папок

```bash
cd /Users/MD/AI-Platform-ISO/intelligent-core/expertise-center/domains

# Создать папки для нового домена (например, HR)
mkdir -p hr/specialists
mkdir -p hr/tactical_assistants
mkdir -p hr/analyzers

# Создать __init__.py файлы
touch hr/__init__.py
touch hr/specialists/__init__.py
touch hr/tactical_assistants/__init__.py
touch hr/analyzers/__init__.py
```

### Шаг 2: Создать метаданные домена (__init__.py)

```python
# hr/__init__.py
"""
HR Domain Plugin

Provides HR-specific experts:
- 3 Specialists (strategic)
- 7 Tactical Assistants (operational)
- 8 Analyzers (heavy AI)
"""

__version__ = "1.0.0"
__domain__ = "hr"
__description__ = "Human Resources Management Domain"

# Domain-specific configuration
DOMAIN_CONFIG = {
    "name": "hr",
    "display_name": "Human Resources",
    "version": "1.0.0",
    "specialists": [
        "hr_advisor",
        "compliance_specialist",
        "strategic_planner"
    ],
    "tactical_assistants": [
        "recruitment_specialist",
        "onboarding_specialist",
        "performance_analyst",
        "training_coordinator",
        "benefits_advisor",
        "employee_relations",
        "workforce_planner"
    ],
    "analyzers": [
        "talent_analyzer",
        "turnover_analyzer",
        "engagement_analyzer",
        "compensation_analyzer",
        "skills_gap_analyzer",
        "diversity_analyzer",
        "performance_analyzer",
        "workforce_analyzer"
    ]
}
```

### Шаг 3: Создать первого Specialist

```python
# hr/specialists/hr_advisor.py
"""
HR Advisor AI

Strategic HR expert providing high-level HR guidance.
"""

import logging
from typing import Dict, Any

from expertise_center.shared.base import BaseSpecialist

logger = logging.getLogger(__name__)


class HRAdvisorAI(BaseSpecialist):
    """
    HR Advisor AI - Strategic Human Resources Expert

    Specializes in:
    - HR strategy and planning
    - Organizational development
    - Talent management
    - Workforce planning
    - HR compliance and governance
    """

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(
            specialist_id="hr_advisor",
            name="HR Advisor AI",
            specialty="Strategic Human Resources Management",
            domain="hr"
        )

        # AI Foundation integrations inherited from BaseSpecialist:
        # self.rag, self.llm, self.context_builder, self.knowledge

        self.config = config or {}
        logger.info("HR Advisor AI initialized!")

    async def analyze(self, context: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Strategic HR analysis"""

        # 1. Get HR-specific knowledge from learning-knowledge
        hr_benchmarks = await self.knowledge.get_domain_knowledge(
            domain_type="hr",
            knowledge_type="benchmarks",
            industry=context.get("industry"),
            size=context.get("company_size")
        )

        # 2. Find similar HR cases
        similar_cases = await self.knowledge.search_cases(
            module="hr_strategy",
            filters={
                "industry": context.get("industry"),
                "size": context.get("company_size")
            },
            limit=5
        )

        # 3. Use RAG for additional insights
        rag_context = await self.rag.retrieve(query=query)

        # 4. Generate strategic analysis
        analysis_prompt = f"""
        Context: {context}
        Query: {query}
        HR Benchmarks: {hr_benchmarks}
        Similar Cases: {len(similar_cases)} found
        RAG Context: {rag_context}

        Provide strategic HR analysis and recommendations.
        """

        analysis = await self.llm.generate(
            prompt=analysis_prompt,
            model="strategic"
        )

        return {
            "analysis": analysis,
            "benchmarks": hr_benchmarks,
            "similar_cases": similar_cases,
            "confidence": 0.85
        }

    async def recommend(self, analysis: Dict[str, Any]) -> list:
        """Generate strategic HR recommendations"""
        # Implementation here
        return []
```

### Шаг 4: Создать первого Tactical Assistant

```python
# hr/tactical_assistants/recruitment_specialist.py
"""
Recruitment Specialist AI

Tactical assistant for recruitment and hiring.
"""

import logging
from typing import Dict, Any

from expertise_center.shared.base import BaseTacticalAssistant

logger = logging.getLogger(__name__)


class RecruitmentSpecialistAI(BaseTacticalAssistant):
    """
    Recruitment Specialist AI - Hiring Expert

    Specializes in:
    - Job description creation
    - Candidate screening
    - Interview questions
    - Hiring process optimization
    """

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(
            assistant_id="recruitment_specialist",
            name="Recruitment Specialist AI",
            specialty="Recruitment & Hiring",
            domain="hr"
        )

        # AI Foundation + Knowledge integrations inherited
        # self.rag, self.llm, self.context_builder, self.knowledge

        self.config = config or {}

    async def assist(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Provide recruitment assistance"""

        # Get job market benchmarks from knowledge base
        market_data = await self.knowledge.get_domain_knowledge(
            domain_type="hr",
            knowledge_type="salary_benchmarks",
            role=context.get("role"),
            industry=context.get("industry")
        )

        # Get similar job descriptions
        similar_jobs = await self.knowledge.search_cases(
            module="recruitment",
            filters={
                "role": context.get("role"),
                "level": context.get("level")
            }
        )

        # Generate assistance
        result = {
            "task": task,
            "market_data": market_data,
            "similar_jobs": similar_jobs,
            "recommendations": []
        }

        return result

    async def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate recruitment data"""
        # Implementation here
        return {"valid": True}
```

### Шаг 5: Создать первого Analyzer

```python
# hr/analyzers/talent_analyzer.py
"""
Talent Analyzer

Heavy AI analysis for talent management.
"""

import logging
from typing import Dict, Any

from expertise_center.shared.base import BaseAnalyzer

logger = logging.getLogger(__name__)


class TalentAnalyzer(BaseAnalyzer):
    """
    Talent Analyzer - AI-powered talent analysis

    Analyzes:
    - Skills gaps
    - Succession planning
    - High-potential identification
    - Talent retention risks
    """

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(
            analyzer_id="talent_analyzer",
            name="Talent Analyzer",
            analysis_type="talent_management",
            domain="hr"
        )

        # AI Foundation + Knowledge integrations inherited
        # self.rag, self.llm, self.predictor, self.anomaly_detector, self.knowledge

        self.config = config or {}

    async def analyze(self, data: Dict[str, Any], config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Perform talent analysis"""

        # Get industry talent benchmarks
        benchmarks = await self.knowledge.get_domain_knowledge(
            domain_type="hr",
            knowledge_type="talent_benchmarks",
            industry=data.get("industry")
        )

        # Use ML predictor for retention risk
        retention_risk = await self.predictor.predict(
            model="retention",
            data=data
        )

        # Detect anomalies in performance data
        anomalies = await self.anomaly_detector.detect(
            data=data.get("performance_data")
        )

        return {
            "benchmarks": benchmarks,
            "retention_risk": retention_risk,
            "anomalies": anomalies,
            "insights": []
        }

    async def extract_insights(self, analysis: Dict[str, Any]) -> list:
        """Extract key insights"""
        # Implementation here
        return []
```

---

## 🔗 Автоматическая интеграция с learning-knowledge

**Важно**: Все базовые классы уже интегрированы с learning-knowledge!

Когда вы наследуете от:
- `BaseSpecialist`
- `BaseTacticalAssistant`
- `BaseAnalyzer`

Вы автоматически получаете доступ к:

```python
# Доступно во всех классах
self.knowledge.get_domain_knowledge()    # Доменные знания
self.knowledge.get_rto_benchmarks()      # RTO benchmarks
self.knowledge.get_threat_scenarios()    # Сценарии угроз
self.knowledge.get_plan_templates()      # Шаблоны планов
self.knowledge.get_iso_standard()        # ISO стандарты
self.knowledge.search_cases()            # Похожие кейсы
self.knowledge.get_kpi_benchmarks()      # KPI benchmarks
self.knowledge.get_compliance_requirements()  # Compliance
```

**Никакой дополнительной настройки не требуется!**

---

## 📝 Регистрация домена

После создания домена, он автоматически обнаружится через `DomainLoader`:

```python
# В core/domain_loader.py
loader = DomainLoader()
hr_domain = await loader.load_domain("hr")

# Домен готов к использованию!
```

---

## 🎯 Пример: Создание Finance Domain

```bash
# Создать структуру
mkdir -p finance/{specialists,tactical_assistants,analyzers}

# Создать экспертов
touch finance/specialists/cfo_advisor.py
touch finance/specialists/audit_specialist.py
touch finance/specialists/investment_strategist.py

touch finance/tactical_assistants/budget_analyst.py
touch finance/tactical_assistants/accounts_payable_specialist.py
touch finance/tactical_assistants/treasury_manager.py

touch finance/analyzers/financial_analyzer.py
touch finance/analyzers/cash_flow_analyzer.py
touch finance/analyzers/risk_analyzer.py
```

Все эти эксперты автоматически получат доступ к:
- ✅ Financial benchmarks
- ✅ Industry ratios
- ✅ Regulatory requirements
- ✅ Similar financial cases
- ✅ Best practices

---

## ✅ Чеклист создания нового домена

- [ ] Создать структуру папок
- [ ] Создать `__init__.py` с метаданными
- [ ] Создать 3-5 Specialists (стратегический уровень)
- [ ] Создать 5-10 Tactical Assistants (операционный уровень)
- [ ] Создать 5-10 Analyzers (тяжелый AI)
- [ ] Создать README.md с описанием домена
- [ ] Создать KNOWLEDGE_INTEGRATION_EXAMPLE.md с примерами
- [ ] Протестировать загрузку домена через DomainLoader
- [ ] Добавить доменные знания в learning-knowledge API

---

## 🚀 Готовые домены

| Домен | Статус | Экспертов | Описание |
|-------|--------|-----------|----------|
| **BCM** | ✅ Complete | 20 | Business Continuity Management |
| **HR** | 📝 Template | 0 | Human Resources |
| **Finance** | 📝 Template | 0 | Finance & Accounting |
| **Legal** | 📝 Future | 0 | Legal & Compliance |
| **IT** | 📝 Future | 0 | IT Management |

---

## 📚 Дополнительные ресурсы

- [Base Classes Documentation](../shared/base/README.md)
- [BCM Domain Example](bcm/KNOWLEDGE_INTEGRATION_EXAMPLE.md)
- [Learning Knowledge API](../../ai-foundation/learning-knowledge/api/README.md)

---

**Статус**: ✅ Готово к созданию новых доменов!
