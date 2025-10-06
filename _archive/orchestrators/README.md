# Archived Orchestrators

**Дата архивирования:** 2025-10-04
**Причина:** Консолидация в единый Super-Orchestrator

**Результат:** Все уникальные компоненты извлечены в `/intelligent-core/ai-orchestration/`

---

## 📁 Что заархивировано

### 1. platform-orchestrator/ (116KB)
**Извлечено:**
- ✅ `orchestrator.py` → `ai-orchestration/tentacles/knowledge_orchestrator.py`
- ✅ `monitoring_api.py` → `ai-orchestration/api/monitoring_routes.py`

**Что было:**
- Workflow intelligence aggregation
- Cross-service benchmarks
- Health monitoring API
- Platform analytics

---

### 2. orchestration/ (33MB)
**Извлечено:**
- ✅ `ai_agent_router.py` → `ai-orchestration/muscles/agent_router.py`
- ✅ `model_router.py` → `ai-orchestration/muscles/model_selector.py`
- ✅ `anthropic_integration.py` → `ai-orchestration/muscles/llm_clients/anthropic_client.py`

**Что было:**
- AI Agent routing с load balancing
- Task complexity classification (FAST/MEDIUM/COMPLEX/HEAVY)
- Multi-model selection (local + cloud)
- BCM-specific prompts

---

### 3. bcm-intelligence/ (16KB)
**Извлечено:**
- ✅ `intelligence_engine.py` → Разделён на 3 AI Organs:
  - `ai-orchestration/muscles/ai_organs/plan_generator.py`
  - `ai-orchestration/muscles/ai_organs/emergency_response.py`
  - `ai-orchestration/muscles/ai_organs/compliance_guardian.py`

**Что было:**
- BCP/DRP plan generation from BIA
- Incident response suggestions
- Compliance gap analysis

---

### 4. orchestrator_обьединенный/ (400KB)
**Извлечено:**
- ✅ `models/*.py` → `ai-orchestration/models/`
  - ai_models.py
  - platform_models.py
  - scenario_models.py
  - deployment_models.py

**Что было:**
- Rich Pydantic models для AI, Platform, Scenarios
- Core/Platform/Control Center (дубликаты ai-orchestration)
- Test suite

---

## 📊 Статистика извлечения

| Директория | Файлов извлечено | Строк кода | Компоненты |
|------------|------------------|------------|------------|
| platform-orchestrator/ | 2 | ~500 | Monitoring, Knowledge aggregation |
| orchestration/ | 3 | ~800 | AI routing, Model selection |
| bcm-intelligence/ | 1→3 | ~1,200 | 3 AI Organs |
| orchestrator_обьединенный/ | 5 | ~600 | Pydantic models |
| **ИТОГО** | **11** | **~3,100** | **Все уникальные компоненты** |

---

## ✅ Гарантия полноты

**Все уникальные компоненты извлечены:**
- ✅ AI Agent Router (маршрутизация + load balancing)
- ✅ Model Selector (task complexity → model selection)
- ✅ Anthropic Client (Claude API)
- ✅ Knowledge Orchestrator (cross-service aggregation)
- ✅ Monitoring Routes (health checks)
- ✅ 3 AI Organs (Plan Generator, Emergency Response, Compliance Guardian)
- ✅ Pydantic Models (AI, Platform, Scenario, Deployment)

**Ничего не потеряно!**

---

## 🎯 Куда смотреть теперь

**Основной оркестратор:**
```
/intelligent-core/ai-orchestration/
```

**Документация:**
- [ORCHESTRATOR_CONSOLIDATION_ANALYSIS.md](../../ORCHESTRATOR_CONSOLIDATION_ANALYSIS.md) - Полный анализ
- [ORCHESTRATOR_CONSOLIDATION_STATUS.md](../../ORCHESTRATOR_CONSOLIDATION_STATUS.md) - Текущий статус

**Спецификация Super-Orchestrator:**
- [ORCHESTRATOR_SUPER_BRAIN_SPEC.md](../../ORCHESTRATOR_SUPER_BRAIN_SPEC.md) - Архитектура Brain + Muscles + Tentacles
- [EXTRACTED_FROM_ODOO/ADDITIONAL_PATTERNS.md](../../EXTRACTED_FROM_ODOO/ADDITIONAL_PATTERNS.md) - Дополнительные паттерны

---

## 🔄 Восстановление (если нужно)

Если понадобится что-то восстановить из архива:

```bash
# Посмотреть что было извлечено
cat /path/to/_archive/orchestrators/README.md

# Восстановить конкретный файл (НЕ РЕКОМЕНДУЕТСЯ)
# Лучше использовать новый consolidated код в ai-orchestration/
```

---

## ⚠️ Важно

**Не используй архивный код!**
Все компоненты улучшены и интегрированы в `/intelligent-core/ai-orchestration/`

**Если что-то не хватает:**
Проверь [ORCHESTRATOR_CONSOLIDATION_STATUS.md](../../ORCHESTRATOR_CONSOLIDATION_STATUS.md) - возможно, это в TODO для Phase 2

---

**Архивировано:** 2025-10-04
**Статус:** ✅ Complete - All unique code extracted
**Безопасно удалить:** Нет (храним как backup на 30 дней)
