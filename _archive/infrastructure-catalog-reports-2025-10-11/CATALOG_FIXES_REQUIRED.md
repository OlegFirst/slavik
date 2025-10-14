# Исправления каталога SERVICE_CATALOG_DETAILED.yaml

## Дата анализа: 2025-10-11

## ❌ ПРОБЛЕМЫ ОБНАРУЖЕНЫ

### 1. **Intelligent-Core: Naming несоответствие**

**Проблема:**
- В каталоге: `ai_orchestration`
- В директории: `/intelligent-core/orchestration/ai-orchestration/`

**Решение:** Изменить в каталоге на `orchestration.ai_orchestration` или просто указать правильный путь

---

### 2. **Intelligent-Core: Пропущенные сервисы**

#### 2.1 `collective` ⚠️
- **Директория:** `/intelligent-core/collective/`
- **Файлы:** main.py (9,371 bytes), README.md, KPI.yaml, API.md
- **Статус:** НЕТ в каталоге, НЕТ SERVICE_INFO.yaml
- **Описание:** Collective intelligence service (из README.md)
- **Порт:** Неизвестен (нужно проверить main.py)

#### 2.2 `ai_workflow_optimizer` ⚠️
- **Директория:** `/intelligent-core/ai_workflow_optimizer/`
- **Файлы:** main.py (45,329 bytes), README.md, KPI.yaml, API.md
- **Статус:** НЕТ в каталоге, НЕТ SERVICE_INFO.yaml
- **Описание:** AI workflow optimizer service
- **Порт:** Неизвестен (нужно проверить main.py)

---

### 3. **Platform-Services: Описаны НЕВЕРНЫЕ сервисы**

#### ✅ Правильно описаны (6 сервисов):
1. `compliance-service` - ✅ есть SERVICE_INFO.yaml
2. `documents-service` - ✅ есть SERVICE_INFO.yaml
3. `governance-service` - ✅ есть SERVICE_INFO.yaml
4. `plans_service` - ✅ есть SERVICE_INFO.yaml
5. `response-service` - ✅ есть SERVICE_INFO.yaml
6. `risk-service` - ✅ есть SERVICE_INFO.yaml

#### ⚠️ ПРОПУЩЕНЫ сервисы с main.py (7 сервисов):

1. **`bia-service`**
   - Есть main.py
   - НЕТ SERVICE_INFO.yaml
   - НЕТ в каталоге

2. **`learning-service`**
   - Есть main.py
   - НЕТ SERVICE_INFO.yaml
   - НЕТ в каталоге

3. **`living-docs`**
   - Есть main.py
   - НЕТ SERVICE_INFO.yaml
   - НЕТ в каталоге

4. **`ml-pipeline`**
   - Есть main.py
   - НЕТ SERVICE_INFO.yaml
   - НЕТ в каталоге

5. **`planning_service`**
   - Есть main.py (44 files)
   - НЕТ SERVICE_INFO.yaml
   - НЕТ в каталоге

6. **`validation-service`**
   - Есть main.py
   - НЕТ SERVICE_INFO.yaml
   - НЕТ в каталоге

7. **`AI-services-management`**
   - Есть main.py
   - НЕТ SERVICE_INFO.yaml
   - НЕТ в каталоге

#### 🤔 Дополнительные сервисы в директории:
- `community-service` - есть main.py (20 файлов)
- `simulation` - есть main.py

---

## 📊 ИТОГОВАЯ СТАТИСТИКА

### Текущее состояние каталога:
- **Intelligent-Core в каталоге:** 10 сервисов
  - ✅ Правильно: 9
  - ❌ Naming issue: 1 (ai_orchestration)
  - ⚠️ Пропущено: 2 (collective, ai_workflow_optimizer)

- **Platform-Services в каталоге:** 10 сервисов
  - ✅ Правильно описаны: 6 (с SERVICE_INFO.yaml)
  - ❌ НЕВЕРНО описаны: 4 (bia_service, strategy_service, exercises_service, marketplace_service)
  - ⚠️ Пропущено: 7+ (bia-service, learning-service, planning_service, и др.)

### Фактическое состояние в файловой системе:
- **Intelligent-Core:** ~12-15 активных сервисов
- **Platform-Services:** ~13+ активных сервисов

---

## 🔧 ПЛАН ИСПРАВЛЕНИЙ

### Этап 1: Исправить Intelligent-Core
1. ✅ Исправить naming для `ai_orchestration` → указать путь `orchestration/ai-orchestration`
2. ⚠️ Добавить `collective` (прочитать main.py, найти порт, описать)
3. ⚠️ Добавить `ai_workflow_optimizer` (прочитать main.py, найти порт, описать)

### Этап 2: Исправить Platform-Services
1. ⚠️ Проверить какие из 4 описанных сервисов РЕАЛЬНО существуют:
   - bia_service (в каталоге) vs bia-service (в директории) ← **РАЗНЫЕ?**
   - strategy_service ← ГДЕ?
   - exercises_service ← ГДЕ?
   - marketplace_service ← ГДЕ?

2. ⚠️ Добавить пропущенные сервисы (если они активны):
   - learning-service
   - planning_service
   - living-docs
   - ml-pipeline
   - validation-service
   - community-service

### Этап 3: Финальная валидация
1. Сверить каждый сервис в каталоге с файловой системой
2. Обновить metadata (total_services, active_services)
3. Создать отчет о расхождениях

---

## 🚨 КРИТИЧЕСКИЕ ВОПРОСЫ

1. **bia_service vs bia-service** - это один и тот же сервис или разные?
2. **strategy_service, exercises_service, marketplace_service** - где эти сервисы? Deprecated?
3. **Какие сервисы действительно АКТИВНЫ и должны быть в каталоге?**

---

## 📝 ИСТОЧНИК ПРОБЛЕМЫ

> "как удто бы другую диреткорию описали причем сбой у тебя. я посомтрел команада описаывала правильно это в какой-то мопентначал перепиывать описаное"

**Анализ:**
- Команда описала правильно 6 сервисов с SERVICE_INFO.yaml
- В какой-то момент я добавил 4 сервиса (bia_service, strategy_service, exercises_service, marketplace_service) из ДРУГОГО источника
- Эти 4 сервиса не имеют SERVICE_INFO.yaml и возможно устаревшие/deprecated

**Вывод:** Нужно УДАЛИТЬ описания 4 сомнительных сервисов и заменить их на РЕАЛЬНЫЕ сервисы из директории.
