# 🚨 КРИТИЧЕСКИЕ КОНФЛИКТЫ ПОРТОВ
## Дата: 2025-10-11

---

## ❌ INTELLIGENT-CORE: НЕСООТВЕТСТВИЯ ПОРТОВ

| Service | Port in CATALOG | Port in FILESYSTEM | Status | Conflict? |
|---------|-----------------|-------------------|--------|-----------|
| **collective** | ❌ NOT IN CATALOG | **8032** | Missing | ⚠️ YES |
| **predictive** | **8031** | **8032** | In catalog | ⚠️ CONFLICT with collective! |
| **event_intelligence** | **8032** | **8039** | In catalog | ⚠️ WRONG PORT! |
| **workflow-engine** | **8030** | **8036** | In catalog | ⚠️ WRONG PORT! |
| **workflow_intelligence** | **8028** | **8037** | In catalog | ⚠️ WRONG PORT! |
| **ai_workflow_optimizer** | ❌ NOT IN CATALOG | **8038** | Missing | ✅ No conflict |
| **ai-foundation** | N/A (library) | **8040** | In catalog | ⚠️ NOT A LIBRARY? |
| **community_intelligence** | **8030** | **8030** | In catalog | ⚠️ CONFLICT with workflow-engine (catalog 8030)! |
| **system-bcm-service** | **8050** | **8050** | In catalog | ✅ OK |
| **ai-orchestration** | **8002** | ? (need to check) | In catalog | ? |

---

## 🔥 КРИТИЧЕСКИЕ КОНФЛИКТЫ

### Конфликт 1: Port 8032
- **collective** (filesystem) → 8032
- **predictive** (filesystem) → 8032
- **event_intelligence** (catalog) → 8032, но (filesystem) → 8039

**РЕАЛЬНОСТЬ:**
- collective И predictive оба используют 8032 в коде!
- event_intelligence использует 8039 в коде, но в каталоге написано 8032!

### Конфликт 2: Port 8030
- **workflow-engine** (catalog) → 8030, но (filesystem) → 8036
- **community_intelligence** (filesystem) → 8030

### Конфликт 3: Неправильные порты в каталоге
- **event_intelligence:** 8032 (catalog) ≠ 8039 (filesystem)
- **workflow-engine:** 8030 (catalog) ≠ 8036 (filesystem)
- **workflow_intelligence:** 8028 (catalog) ≠ 8037 (filesystem)

---

## 📊 ПРАВИЛЬНАЯ КАРТА ПОРТОВ (из файловой системы)

### Intelligent-Core (фактические порты):
```
8002  - ai-orchestration (нужно проверить)
8030  - community_intelligence ✅
8032  - collective ⚠️ CONFLICT
8032  - predictive ⚠️ CONFLICT
8036  - workflow-engine (в каталоге ошибочно 8030)
8037  - workflow_intelligence (в каталоге ошибочно 8028)
8038  - ai_workflow_optimizer (не в каталоге)
8039  - event_intelligence (в каталоге ошибочно 8032)
8040  - ai-foundation (в каталоге "library", но есть порт!)
8050  - system-bcm-service ✅
```

---

## ⚠️ PLATFORM-SERVICES: НЕТ ПОРТОВ В MAIN.PY

Все platform-services не имеют явных портов в main.py!

Возможные причины:
1. Порты задаются через environment variables
2. Порты в SERVICE_INFO.yaml (для 6 сервисов)
3. Порты в docker-compose.yml

**Проверим SERVICE_INFO.yaml:**

```bash
grep -h "port:" /Users/MD/AI-Platform-ISO/platform-services/*/SERVICE_INFO.yaml 2>/dev/null
```

---

## 🔧 ПЛАН ИСПРАВЛЕНИЙ

### Шаг 1: Исправить порты в каталоге для Intelligent-Core

```yaml
# ИСПРАВИТЬ:
workflow_intelligence:  8028 → 8037
community_intelligence: 8030 → 8030 ✅
predictive:            8031 → 8032 (но конфликт!)
event_intelligence:    8032 → 8039
workflow-engine:       8030 → 8036
ai-orchestration:      8002 → 8002 (проверить)
system-bcm-service:    8050 → 8050 ✅

# ДОБАВИТЬ:
collective:            ??? → 8032 (конфликт с predictive!)
ai_workflow_optimizer: ??? → 8038
ai-foundation:         ??? → 8040 (или это не сервис?)
```

### Шаг 2: Решить конфликт Port 8032

**Варианты:**
1. Изменить порт для `collective` на 8034 или 8035
2. Изменить порт для `predictive` на 8031 (как в каталоге)
3. Проверить какой сервис РЕАЛЬНО работает на 8032

### Шаг 3: Проверить порты platform-services

Читать SERVICE_INFO.yaml для каждого сервиса.

---

## 🎯 РЕКОМЕНДАЦИЯ

**ОСТАНОВИТЬ ВСЕ ПРАВКИ КАТАЛОГА!**

Сначала нужно:
1. ✅ Проверить какие порты РЕАЛЬНО используются в production/docker-compose
2. ✅ Решить конфликты портов (8032, 8030)
3. ✅ Обновить каталог с правильными портами
4. ✅ Добавить пропущенные сервисы

**Без этого каталог будет содержать НЕВЕРНУЮ информацию!**
