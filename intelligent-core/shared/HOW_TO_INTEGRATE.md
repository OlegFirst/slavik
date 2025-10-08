# 🚀 Как Интегрировать Новый Сервис с Platform Client

**Для всех сервисов в `intelligent-core/`**

---

## 🎯 Цель

Каждый сервис должен **автоматически** подключаться к 3 ключевым "мозгам" платформы:

1. **AI Foundation** (RAG, LLM, Embeddings) - порт 8040
2. **Expertise Center** (12 Tactical Assistants + 10 Analyzers) - порт 8035
3. **Workflow Intelligence** (Case Library + ML Analysis) - порт 8037

---

## ✅ Решение: Platform Client

**Файл:** `intelligent-core/shared/platform_client.py`

**Один импорт → всё работает!**

---

## 📋 Инструкция (3 шага)

### Шаг 1: Импортировать Platform Client

```python
# В main.py или core файле сервиса:
import sys
from pathlib import Path

# Добавить intelligent-core в path (если нужно)
intelligent_core_path = Path(__file__).parent.parent
sys.path.insert(0, str(intelligent_core_path))

from shared.platform_client import get_platform_client, PlatformClient
```

---

### Шаг 2: Использовать в Сервисе

```python
class MyService:
    def __init__(self):
        # АВТОМАТИЧЕСКАЯ интеграция с 3 "мозгами"
        self.platform: PlatformClient = get_platform_client()

        # Ваши специфичные клиенты (опционально)
        self.my_client = MySpecificClient()

    async def initialize(self):
        """Проверить доступность платформы"""
        health = await self.platform.health_check()

        print(f"AI Foundation: {'✅' if health['ai_foundation'] else '❌'}")
        print(f"Expertise Center: {'✅' if health['expertise_center'] else '❌'}")
        print(f"Workflow Intelligence: {'✅' if health['workflow_intelligence'] else '❌'}")

        if all(health.values()):
            print("✅ All platform 'brains' connected!")
        else:
            print("⚠️  Some services unavailable (graceful degradation)")
```

---

### Шаг 3: Использовать "Мозги" Платформы

#### AI Foundation - RAG, LLM, Embeddings

```python
# Поиск знаний через RAG
knowledge = await self.platform.ai.search_knowledge(
    query="How to implement BIA analysis?",
    limit=5
)

# AI анализ через LLM
analysis = await self.platform.ai.ask(
    query="Analyze this risk scenario",
    context={"scenario": scenario_data}
)

# Векторизация для similarity search
embeddings = await self.platform.ai.get_embeddings(
    text="Process execution pattern"
)
```

---

#### Expertise Center - 12 Tactical Assistants

```python
# Универсальный запрос к любому эксперту
response = await self.platform.experts.query_expert(
    expert_type="bia_specialist",  # или risk_analyst, compliance_copilot, etc.
    query="Analyze process criticality",
    context={"process_id": "P-123", "data": {...}},
    organization_id="org-456"  # опционально
)

# Специализированные методы
bia_result = await self.platform.experts.bia_analysis({
    "process_id": "P-123",
    "metrics": {...}
})

risk_result = await self.platform.experts.risk_assessment({
    "threat_id": "T-456",
    "impact": {...}
})

compliance_result = await self.platform.experts.compliance_check({
    "standard": "ISO 22301",
    "clause": "8.4",
    "evidence": {...}
})
```

**Доступные эксперты:**
- `bia_specialist` - BIA анализ
- `risk_analyst` - Риск-анализ
- `compliance_copilot` - Compliance проверки
- `incident_advisor` - Управление инцидентами
- `plan_generator` - Генерация планов
- `project_manager` - Управление проектами
- `exercise_designer` - Проектирование учений
- `documents_specialist` - Работа с документами
- `governance_specialist` - Governance
- `learning_specialist` - Обучение
- `validation_specialist` - Валидация
- `response_specialist` - Реагирование

---

#### Workflow Intelligence - Case Library + ML

```python
# Добавить кейс в библиотеку
case_id = await self.platform.workflows.add_case(
    case_data={
        "type": "bia_analysis",
        "organization_id": "org-123",
        "findings": [...],
        "resolution": [...],
        "success": True
    },
    module="bia",  # или risk, compliance, etc.
    source="platform",
    metadata={"duration_mins": 45}
)

# Получить кейс
case = await self.platform.workflows.get_case(case_id)

# Поиск похожих кейсов
similar_cases = await self.platform.workflows.search_cases({
    "module": "bia",
    "tags": ["critical_process", "manufacturing"],
    "success": True
})

# ML-анализ workflow
analysis = await self.platform.workflows.analyze_workflow(
    workflow_id="wf-789",
    workflow_data={
        "steps": [...],
        "duration": 120,
        "resources": [...]
    },
    context={"organization_type": "manufacturing"}
)

# Получить ML рекомендации
recommendations = await self.platform.workflows.get_recommendations(
    workflow_data={
        "current_state": {...},
        "goal": "reduce_duration"
    }
)
```

---

## 🎨 Полный Пример: Новый Сервис

```python
# my_new_service/main.py

from fastapi import FastAPI
from shared.platform_client import get_platform_client

app = FastAPI(title="My New Service")

# Глобальный platform client
platform = get_platform_client()


@app.on_event("startup")
async def startup():
    """Проверка интеграции при старте"""
    print("🔄 Checking platform integration...")

    health = await platform.health_check()

    if all(health.values()):
        print("✅ All platform 'brains' connected!")
    else:
        print(f"⚠️  Platform status: {health}")
        print("   Service will work with reduced capabilities")


@app.post("/analyze")
async def analyze(data: dict):
    """Пример использования всех 3 'мозгов'"""

    # 1. Поиск знаний (AI Foundation)
    knowledge = await platform.ai.search_knowledge(
        query=f"How to handle {data['type']}?",
        limit=3
    )

    # 2. Консультация с экспертом (Expertise Center)
    expert_analysis = await platform.experts.query_expert(
        expert_type="bia_specialist",
        query=f"Analyze {data['type']}",
        context={"data": data, "knowledge": knowledge}
    )

    # 3. Проверка похожих кейсов (Workflow Intelligence)
    similar_cases = await platform.workflows.search_cases({
        "module": "bia",
        "tags": [data['type']]
    })

    # 4. AI-powered финальный анализ
    final_analysis = await platform.ai.ask(
        query="Combine all insights into actionable recommendations",
        context={
            "knowledge": knowledge,
            "expert": expert_analysis,
            "cases": similar_cases
        }
    )

    # 5. Сохранить результат в Case Library
    case_id = await platform.workflows.add_case(
        case_data={
            "type": data['type'],
            "analysis": final_analysis,
            "sources": ["knowledge", "expert", "cases"]
        },
        module="my_service",
        source="platform"
    )

    return {
        "analysis": final_analysis,
        "case_id": case_id,
        "sources_used": {
            "knowledge_items": len(knowledge),
            "expert_consulted": True,
            "similar_cases": len(similar_cases)
        }
    }
```

---

## 🔧 Конфигурация

### Environment Variables (опционально)

Platform Client автоматически использует defaults, но можно переопределить:

```bash
# .env или docker-compose.yml
AI_FOUNDATION_URL=http://localhost:8040
EXPERTISE_CENTER_URL=http://localhost:8035
WORKFLOW_INTELLIGENCE_URL=http://localhost:8037
```

### Custom Config

```python
from shared.platform_client import get_platform_client, PlatformConfig

# Кастомная конфигурация
config = PlatformConfig(
    ai_foundation_url="http://custom-ai:8040",
    expertise_center_url="http://custom-experts:8035",
    workflow_intelligence_url="http://custom-workflows:8037",
    default_timeout=60.0
)

platform = get_platform_client(config)
```

---

## ✅ Health Monitoring

### Проверка Доступности

```python
# Простая проверка
health = await platform.health_check()
# {'ai_foundation': True, 'expertise_center': True, 'workflow_intelligence': True}

# Готовность платформы (все сервисы работают)
is_ready = await platform.is_ready()
# True если все 3 "мозга" доступны
```

### Graceful Degradation

```python
async def my_analysis(data):
    """Пример graceful degradation"""

    # Попробовать AI Foundation
    try:
        knowledge = await platform.ai.search_knowledge(data['query'])
    except Exception as e:
        print(f"AI Foundation unavailable: {e}")
        knowledge = []  # Fallback

    # Попробовать Expertise Center
    try:
        expert = await platform.experts.query_expert("bia_specialist", data['query'])
    except Exception as e:
        print(f"Expertise Center unavailable: {e}")
        expert = {"fallback": "using_local_rules"}

    # Продолжить работу с доступными данными
    return combine_results(knowledge, expert)
```

---

## 🎯 Best Practices

### 1. **Всегда используйте Platform Client**

❌ **НЕ ДЕЛАЙТЕ ТАК:**
```python
# Ручное создание клиентов
self.ai_client = AIFoundationClient(url="...")
self.expert_client = ExpertiseCenterClient(url="...")
```

✅ **ДЕЛАЙТЕ ТАК:**
```python
# Используйте platform_client
self.platform = get_platform_client()
```

---

### 2. **Проверяйте Health при Startup**

```python
@app.on_event("startup")
async def startup():
    health = await platform.health_check()

    if not all(health.values()):
        logger.warning(f"Some platform services unavailable: {health}")
```

---

### 3. **Используйте Все 3 "Мозга"**

Максимальная польза когда комбинируете:

```python
# 1. Знания (AI Foundation)
knowledge = await platform.ai.search_knowledge(query)

# 2. Экспертиза (Expertise Center)
expert = await platform.experts.query_expert("specialist", query, context)

# 3. Опыт (Workflow Intelligence)
cases = await platform.workflows.search_cases({"tags": tags})

# Комбинируйте!
result = combine(knowledge, expert, cases)
```

---

### 4. **Сохраняйте Результаты в Case Library**

```python
# После успешного выполнения
await platform.workflows.add_case(
    case_data={
        "type": "my_analysis",
        "input": input_data,
        "output": results,
        "success": True
    },
    module="my_service",
    source="platform"
)

# Будущие анализы смогут учиться из этого!
```

---

## 📊 Мониторинг Интеграции

### Пример Health Check Endpoint

```python
@app.get("/health")
async def health():
    """Health check с platform integration status"""
    platform_health = await platform.health_check()

    return {
        "service": "my_service",
        "status": "healthy",
        "platform_integration": {
            "ai_foundation": platform_health['ai_foundation'],
            "expertise_center": platform_health['expertise_center'],
            "workflow_intelligence": platform_health['workflow_intelligence'],
            "overall": all(platform_health.values())
        },
        "capabilities": {
            "knowledge_search": platform_health['ai_foundation'],
            "expert_consultation": platform_health['expertise_center'],
            "case_learning": platform_health['workflow_intelligence']
        }
    }
```

---

## 🚀 Примеры по Доменам

### BIA Service
```python
# BIA анализ с полной интеграцией
async def analyze_business_impact(process_id: str):
    # Знания об ISO 22301 BIA
    knowledge = await platform.ai.search_knowledge(
        "ISO 22301 business impact analysis requirements"
    )

    # BIA Specialist анализ
    bia_analysis = await platform.experts.bia_analysis({
        "process_id": process_id,
        "organization_context": {...}
    })

    # Похожие BIA кейсы
    similar = await platform.workflows.search_cases({
        "module": "bia",
        "tags": ["critical_process"]
    })

    return combine_bia_insights(knowledge, bia_analysis, similar)
```

---

### Risk Service
```python
# Риск-анализ с полной интеграцией
async def assess_risk(threat_id: str):
    # Знания о threat
    threat_knowledge = await platform.ai.search_knowledge(
        f"threat {threat_id} mitigation strategies"
    )

    # Risk Analyst консультация
    risk_assessment = await platform.experts.risk_assessment({
        "threat_id": threat_id,
        "likelihood": "high",
        "impact": {...}
    })

    # Похожие риски
    similar_risks = await platform.workflows.search_cases({
        "module": "risk",
        "tags": [threat_id]
    })

    return combine_risk_analysis(threat_knowledge, risk_assessment, similar_risks)
```

---

### Compliance Service
```python
# Compliance проверка с полной интеграцией
async def check_compliance(standard: str, clause: str):
    # Знания о стандарте
    standard_knowledge = await platform.ai.search_knowledge(
        f"{standard} clause {clause} requirements"
    )

    # Compliance Copilot проверка
    compliance_check = await platform.experts.compliance_check({
        "standard": standard,
        "clause": clause,
        "evidence": {...}
    })

    # Похожие compliance кейсы
    similar_checks = await platform.workflows.search_cases({
        "module": "compliance",
        "tags": [standard, clause]
    })

    return combine_compliance_results(standard_knowledge, compliance_check, similar_checks)
```

---

## ❓ FAQ

### Q: Что если сервис недоступен?
**A:** Platform Client использует graceful degradation. Сервис продолжит работать с доступными компонентами.

### Q: Как добавить новый "мозг"?
**A:** Обновить `platform_client.py` - добавить новый client класс и метод в `PlatformClient`.

### Q: Нужно ли использовать все 3 "мозга"?
**A:** Нет, используйте те которые нужны. Но комбинация всех 3 дает максимальную пользу.

### Q: Как тестировать без запущенных сервисов?
**A:** Platform Client проверяет health и работает с graceful degradation. Можно использовать моки.

### Q: Можно ли добавить специфичные клиенты?
**A:** Да! Platform Client для общих "мозгов", специфичные клиенты - дополнительно.

---

## 📚 Документация

- **platform_client.py** - Исходный код с docstrings
- **INTEGRATION_TEMPLATE.md** - Шаблон интеграции
- **Analytics Specialist** - Пример реальной интеграции

---

## ✅ Checklist для Нового Сервиса

- [ ] Импортировать `get_platform_client`
- [ ] Создать `self.platform` в `__init__`
- [ ] Добавить `health_check()` в startup
- [ ] Использовать `platform.ai` для знаний
- [ ] Использовать `platform.experts` для экспертизы
- [ ] Использовать `platform.workflows` для кейсов
- [ ] Сохранять результаты в Case Library
- [ ] Добавить graceful degradation
- [ ] Протестировать с/без запущенных сервисов
- [ ] Документировать integration status

---

**Создано:** 2025-10-08
**Автор:** Claude + MD
**Статус:** ✅ ГОТОВО К ИСПОЛЬЗОВАНИЮ

**Используйте везде!** 🚀
