# 🔍 INTELLIGENT-CORE AUDIT & CLEANUP PLAN

**Дата:** 2025-10-04
**Цель:** Разобраться с дублированием и структурой

---

## 📊 ТЕКУЩЕЕ СОСТОЯНИЕ

### Найденные директории:

```
intelligent-core/
├── 🔴 community-intelligence-extracted/     # ПУСТАЯ или temporary
├── 🔴 workflow_intelligence_extracted/      # ПУСТАЯ или temporary
├── ✅ collective/                            # НОВАЯ (сегодня создана)
├── ✅ community_intelligence/                # ПОЛНАЯ (есть код)
├── ❓ ai_experts/                            # ПРОВЕРИТЬ
├── ✅ workflow_intelligence/                 # ПОЛНАЯ (есть код)
├── ❓ ai_workflow_optimizer/                 # ПРОВЕРИТЬ
├── ❓ Governance System/                     # ПРОВЕРИТЬ
├── ✅ living-docs/                           # НОВАЯ (сегодня создана)
├── ❓ bpmn-workflow/                         # ПРОВЕРИТЬ
└── ✅ predictive/                            # ПОЛНАЯ (есть код)
```

---

## 🎯 АНАЛИЗ ПО СЕРВИСАМ

### ✅ ПРАВИЛЬНО СОЗДАННЫЕ (Новые, сегодня)

#### 1. **collective/** (Port 8032)
- **Создано:** Сегодня
- **Назначение:** Collective Agent Networks - анонимная коллаборация
- **Файлы:** 10 Python файлов
- **Структура:**
  ```
  collective/
  ├── main.py (Port 8032)
  ├── services/
  │   ├── collective_agent_service.py
  │   ├── stuck_detector_service.py
  │   ├── anonymizer_service.py
  │   └── mcp_partisia_integration.py
  ├── api/
  │   ├── collective_agents.py
  │   └── stuck_detection.py
  └── models/database.py
  ```
- **Статус:** ✅ ОСТАВИТЬ КАК ЕСТЬ

#### 2. **living-docs/** (Port 8034)
- **Создано:** Сегодня
- **Назначение:** Living Documentation - самообучающаяся документация
- **Файлы:** 8 файлов
- **Структура:**
  ```
  living-docs/
  ├── main.py (Port 8034)
  ├── services/
  │   ├── documentation_evolution_engine.py
  │   ├── personalization_service.py
  │   └── ai_example_generator.py
  └── api/documentation.py
  ```
- **Статус:** ✅ ОСТАВИТЬ КАК ЕСТЬ

---

### ✅ СУЩЕСТВУЮЩИЕ ПОЛНЫЕ СЕРВИСЫ

#### 3. **community_intelligence/** (Port 8030)
- **Создано:** Вчера/ранее
- **Назначение:** Community-driven case contributions, peer review, reputation
- **Файлы:** ~20 Python файлов
- **Структура:**
  ```
  community_intelligence/
  ├── main.py (Port 8030)
  ├── services/
  │   ├── peer_review_service.py
  │   ├── reputation_engine.py
  │   ├── workflow_integration_service.py
  │   └── living_docs.py (???)
  ├── api/
  │   ├── contributions.py
  │   ├── reviews.py
  │   ├── reputation.py
  │   └── cases.py
  └── events/subscribers.py
  ```
- **⚠️ ПРОБЛЕМА:** Есть `services/living_docs.py` - дублирование с новым `living-docs/`?
- **Статус:** ⚠️ ПРОВЕРИТЬ И ОЧИСТИТЬ

#### 4. **predictive/** (Port 8031)
- **Создано:** Вчера
- **Назначение:** Predictive Journey - предсказывает путь организации
- **Файлы:** 5 Python файлов
- **Структура:**
  ```
  predictive/
  ├── main.py (Port 8031)
  └── services/
      ├── journey_predictor.py
      ├── demand_forecaster.py
      └── proactive_recommendations.py
  ```
- **Статус:** ✅ ОСТАВИТЬ КАК ЕСТЬ

#### 5. **workflow_intelligence/**
- **Назначение:** Workflow intelligence & optimization
- **Статус:** ❓ ПРОВЕРИТЬ содержимое

---

### 🔴 ПОДОЗРИТЕЛЬНЫЕ / ДУБЛИКАТЫ

#### 6. **community-intelligence-extracted/**
- **Содержимое:** Пустая или temporary
- **Решение:** 🗑️ УДАЛИТЬ (extracted = временная)

#### 7. **workflow_intelligence_extracted/**
- **Содержимое:** Пустая или temporary
- **Решение:** 🗑️ УДАЛИТЬ (extracted = временная)

---

### ❓ ТРЕБУЮТ ПРОВЕРКИ

#### 8. **ai_experts/**
- **Проверить:** Что это? Связано с чем?
- **Возможно:** Устаревший или дублирует collective?

#### 9. **ai_workflow_optimizer/**
- **Проверить:** Дублирует workflow_intelligence?

#### 10. **Governance System/**
- **Проверить:** Что это? Отдельный сервис?

#### 11. **bpmn-workflow/**
- **Проверить:** BPMN workflow engine?

#### 12. **bcm_ai_control/**
- **Проверить:** AI control center? Orchestration?

---

## 🎯 ПРЕДПОЛАГАЕМАЯ ПРАВИЛЬНАЯ СТРУКТУРА

### Основные сервисы (Ports):

```
intelligent-core/

# COMMUNITY & COLLABORATION
├── community_intelligence/          # Port 8030 - Community contributions
│   ├── Peer review
│   ├── Reputation system
│   ├── Case library
│   └── ❌ УБРАТЬ: living_docs.py (дубликат)

├── collective/                      # Port 8032 - Collective Agents
│   ├── Anonymous collaboration
│   ├── MPC integration
│   └── Partisia blockchain

# INTELLIGENCE & PREDICTION
├── predictive/                      # Port 8031 - Predictive Journey
│   ├── Journey prediction
│   ├── Demand forecasting
│   └── Proactive recommendations

├── living-docs/                     # Port 8034 - Living Documentation
│   ├── Self-evolving docs
│   ├── Personalization
│   └── AI examples

# WORKFLOW & OPTIMIZATION
├── workflow_intelligence/           # Workflow optimization
│   └── (проверить содержимое)

├── bpmn-workflow/                   # BPMN engine
│   └── (проверить если нужен)

# AI & CONTROL
├── bcm_ai_control/                  # AI orchestration center
│   └── (проверить назначение)

# GOVERNANCE (если нужен отдельно)
├── Governance System/               # Governance service
│   └── (проверить содержимое)

# 🗑️ УДАЛИТЬ
├── community-intelligence-extracted/  # ❌ TEMPORARY
├── workflow_intelligence_extracted/   # ❌ TEMPORARY
├── ai_experts/                        # ❓ ПРОВЕРИТЬ если дубликат
└── ai_workflow_optimizer/             # ❓ ПРОВЕРИТЬ если дубликат
```

---

## 🔍 ДЕТАЛЬНАЯ ПРОВЕРКА НУЖНА ДЛЯ:

### 1. community_intelligence/services/living_docs.py
**Вопрос:** Это старая версия living-docs?
**Действие:** Проверить и удалить если дубликат

### 2. ai_experts/
**Вопрос:** Что делает? Связано с collective?
**Действие:** Проверить содержимое и назначение

### 3. ai_workflow_optimizer/
**Вопрос:** Дублирует workflow_intelligence?
**Действие:** Проверить и объединить или удалить

### 4. Governance System/
**Вопрос:** Отдельный сервис или часть чего-то?
**Действие:** Проверить назначение

### 5. workflow_intelligence/ vs ai_workflow_optimizer/
**Вопрос:** Два сервиса делают одно и то же?
**Действие:** Определить разницу или объединить

---

## 📋 ПЛАН ДЕЙСТВИЙ

### ШАГ 1: Проверка содержимого
```bash
# Проверим что в каждой директории
1. community_intelligence/services/living_docs.py - что там?
2. ai_experts/ - для чего?
3. ai_workflow_optimizer/ - дубликат?
4. Governance System/ - что делает?
5. workflow_intelligence/ - основной или дубликат?
6. bpmn-workflow/ - нужен?
7. bcm_ai_control/ - orchestrator?
```

### ШАГ 2: Определить дубликаты
```
Сравнить:
- community_intelligence vs collective (разные!)
- workflow_intelligence vs ai_workflow_optimizer (может дубликат?)
- living-docs vs community_intelligence/services/living_docs.py (дубликат!)
```

### ШАГ 3: Очистка
```bash
# Точно удалить:
rm -rf community-intelligence-extracted/
rm -rf workflow_intelligence_extracted/

# Возможно удалить (после проверки):
# - ai_experts/ (если дубликат collective)
# - ai_workflow_optimizer/ (если дубликат workflow_intelligence)
# - community_intelligence/services/living_docs.py (дубликат living-docs/)
```

### ШАГ 4: Реорганизация
```
Четкая структура:
1. Port 8030 - Community Intelligence (peer review, reputation)
2. Port 8031 - Predictive Journey (prediction, forecasting)
3. Port 8032 - Collective Agents (anonymous collaboration)
4. Port 8034 - Living Documentation (self-evolving docs)
5. TBD - Workflow Intelligence (optimization)
6. TBD - AI Control Center (orchestration)
7. TBD - Governance (if separate service)
```

---

## ⚠️ КРИТИЧЕСКИЕ ВОПРОСЫ

1. **living_docs дубликат?**
   - `community_intelligence/services/living_docs.py` VS `living-docs/`
   - Нужно проверить старый файл и удалить

2. **ai_experts VS collective?**
   - Оба про AI agents?
   - Объединить или оставить отдельно?

3. **workflow_intelligence VS ai_workflow_optimizer?**
   - Два сервиса делают одно?
   - Объединить в один?

4. **Governance System - что это?**
   - Отдельный микросервис?
   - Часть platform-services?

---

## 🎯 РЕКОМЕНДАЦИИ

### Минимальная очистка (safe):
```bash
# 100% можно удалить:
rm -rf intelligent-core/community-intelligence-extracted/
rm -rf intelligent-core/workflow_intelligence_extracted/

# Проверить и возможно удалить:
# community_intelligence/services/living_docs.py (если старая версия)
```

### Полная реорганизация (после проверки):
```
Оставить 4 ЧЕТКИХ сервиса:
1. community_intelligence/ (Port 8030)
2. predictive/ (Port 8031)
3. collective/ (Port 8032)
4. living-docs/ (Port 8034)

+ Добавить если нужны:
5. workflow_intelligence/ (TBD port)
6. bcm_ai_control/ (orchestrator)
7. governance_system/ (если отдельный сервис)
```

---

## 🔄 СЛЕДУЮЩИЕ ШАГИ

**Сейчас мне нужно:**
1. Проверить содержимое подозрительных директорий
2. Сравнить дубликаты
3. Предложить финальную структуру

**Партнер, давай я проверю:**
- `community_intelligence/services/living_docs.py` - что там?
- `ai_experts/` - для чего?
- `ai_workflow_optimizer/` - дубликат?
- `workflow_intelligence/` - что делает?

**Продолжить детальную проверку?** 🔍
