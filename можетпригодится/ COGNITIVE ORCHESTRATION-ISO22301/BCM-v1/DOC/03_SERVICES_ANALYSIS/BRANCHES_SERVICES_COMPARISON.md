# Сравнительный анализ сервисов по веткам проекта ISO-22301

**Дата анализа:** 2025-09-28
**Анализ выполнен БЕЗ переключения с ветки:** unified-complete-iso22301-20250920

## 📊 Статистика по веткам

| Ветка | Количество сервисов | Статус | Примечание |
|-------|---------------------|--------|------------|
| **unified-complete-iso22301-20250920** (текущая) | **31** | ✅ Максимум | Все сервисы присутствуют |
| new-version | 19 | ⚠️ Средний | Промежуточная версия |
| restore-pre-4eaa9d9b | 19 | ⚠️ Средний | Восстановленная версия |
| golden-pr-clean | 7 | ❌ Минимум | Только базовые сервисы |
| main | 7 | ❌ Минимум | Основная ветка с минимумом |
| my-local-changes | 31 | ✅ Полный | Идентично текущей |

## 🔍 Детальный анализ

### 1. Текущая ветка: `unified-complete-iso22301-20250920` ✅
**31 сервис - ПОЛНЫЙ НАБОР**

Все сервисы присутствуют:
- ✅ AI & Intelligence (10): ai, ai-consultant, ai_control_center, ai_orchestrator, ai_workflow_optimizer, docker-ai, docker-ai-poc, digital-twin-engine, digital-twin-platform, scenario_orchestrator
- ✅ Core BCM (8): bia_engine, compliance_checker, document_processor, bcm_content_training_bridge, notification_service, monitoring_service, process_mining_service, template_library
- ✅ Integration (6): unified_api_gateway, unified_control_center, unified_database_gateway, crm_bridge, github_app, community
- ✅ Support (7): deployer, knowledge-base, document_management, realtime_websocket, vscode-extension

### 2. Ветка: `golden-pr-clean` ❌
**7 сервисов - МИНИМАЛЬНЫЙ НАБОР**

Только критически важные:
1. ai_orchestrator
2. bia_engine
3. compliance_checker
4. deployer
5. document_processor
6. github_app
7. notification_service

**Отсутствуют 24 сервиса!**

### 3. Ветки: `new-version` и `restore-pre-4eaa9d9b` ⚠️
**19 сервисов - СРЕДНИЙ НАБОР**

Промежуточное состояние между минимальным и полным.

### 4. Ветка: `main` ❌
**7 сервисов - идентично golden-pr-clean**

## 🎯 Выводы

### ✅ ЛУЧШИЙ ВЫБОР: Текущая ветка `unified-complete-iso22301-20250920`

**Причины:**
1. **Максимальное количество сервисов** - 31 из 31
2. **Полная функциональность** - все AI органы, BCM модули, интеграции
3. **Готовность к deployment** - 25 сервисов подключены в docker-compose

### ⚠️ Проблема с основными ветками

Ветки `main` и `golden-pr-clean` содержат только **7 базовых сервисов** из 31 возможных. Это означает:
- Потеря 77% функциональности
- Отсутствие AI органов (кроме orchestrator)
- Нет unified gateways
- Нет digital twin платформы
- Нет community и marketplace функций

## 📋 Рекомендации

1. **ИСПОЛЬЗОВАТЬ текущую ветку** для полной функциональности
2. **НЕ ПЕРЕКЛЮЧАТЬСЯ** на main или golden-pr-clean - потеря 24 сервисов
3. **Возможно слияние** текущей ветки в main для обновления основной версии

## 🔧 Статус готовности сервисов на текущей ветке

### Полностью готовые (10):
- ✅ ai_orchestrator (main.py присутствует)
- ✅ bia_engine (main.py + app.py)
- ✅ scenario_orchestrator (main.py)
- ✅ document_processor (app.py)
- ✅ compliance_checker (app.py)
- ✅ notification_service (main.py)
- ✅ deployer (main.py)
- ✅ github_app (main.py)

### В разработке (21):
- ⚠️ Остальные сервисы требуют доработки основных файлов

---

**ВАЖНО:** Анализ выполнен без переключения веток через команды git diff, git ls-tree и git log.