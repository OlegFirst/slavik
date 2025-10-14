# ⚡ КРАТКАЯ СВОДКА: Что исправить в каталоге

## 🎯 PLATFORM-SERVICES

### ✅ ЧТО ПРАВИЛЬНО (6 сервисов - НЕ ТРОГАТЬ):
- compliance-service (8014)
- documents-service (8024)
- governance-service (8025)
- plans_service (8023)
- response-service (8027)
- risk-service (8026)

### ❌ ЧТО НЕПРАВИЛЬНО (4 сервиса - ИСПРАВИТЬ):

#### 1. bia_service → bia-service
```yaml
# БЫЛО:
bia_service:
  port: 8020  ❌ НЕВЕРНО

# ДОЛЖНО БЫТЬ:
bia-service:
  port: 8012  ✅ ПРАВИЛЬНО
```

#### 2. strategy_service → learning-service
```yaml
# БЫЛО:
strategy_service:
  port: 8021
  # Директория НЕ существует! ❌

# ДОЛЖНО БЫТЬ:
learning-service:
  port: 8021
  path: /platform-services/learning-service/ ✅
```

#### 3. exercises_service → validation-service
```yaml
# БЫЛО:
exercises_service:
  port: 8022
  # Директория НЕ существует! ❌

# ДОЛЖНО БЫТЬ:
validation-service:
  port: 8022
  path: /platform-services/validation-service/ ✅
```

#### 4. marketplace_service → marketplace-service
```yaml
# БЫЛО:
marketplace_service:
  port: 8019  ❌ НЕВЕРНО

# ДОЛЖНО БЫТЬ:
marketplace-service:
  port: 8032  ✅ ПРАВИЛЬНО
  path: /platform-services/community-service/marketplace/
```

### ⚠️ ЧТО ДОБАВИТЬ (5 новых сервисов):

1. **portal-service**
   - Port: 8031
   - Path: /platform-services/community-service/portal/
   - Status: ACTIVE

2. **planning_service**
   - Port: 8011
   - Path: /platform-services/planning_service/
   - Status: ACTIVE (104 файла!)

3. **living-docs**
   - Port: 8034
   - Path: /platform-services/living-docs/
   - Status: ACTIVE

4. **ml-pipeline**
   - Port: 8091
   - Path: /platform-services/ml-pipeline/
   - Status: ACTIVE

5. **AI-services-management**
   - Port: TBD (нужно определить)
   - Path: /platform-services/AI-services-management/
   - Status: ACTIVE

---

## 🎯 INTELLIGENT-CORE

### ❌ ЧТО ИСПРАВИТЬ:

#### 1. Naming issue: ai_orchestration
```yaml
# БЫЛО:
ai_orchestration:
  path: ???

# ДОЛЖНО БЫТЬ:
ai_orchestration:
  path: /intelligent-core/orchestration/ai-orchestration/
  # ИЛИ переименовать ключ:
orchestration.ai_orchestration:
```

### ⚠️ ЧТО ДОБАВИТЬ (вы возьмёте на себя):

1. **collective**
   - Port: 8034 (или другой, чтобы избежать конфликта)
   - Path: /intelligent-core/collective/

2. **ai_workflow_optimizer**
   - Port: 8038
   - Path: /intelligent-core/ai_workflow_optimizer/

---

## 📊 ИТОГО:

### Platform-Services:
- ✅ Оставить как есть: **6 сервисов**
- ❌ Исправить: **4 сервиса**
- ⚠️ Добавить: **5 сервисов**
- **ИТОГО после исправлений: 15 сервисов**

### Intelligent-Core:
- ✅ Оставить как есть: **9 сервисов**
- ❌ Исправить naming: **1 сервис**
- ⚠️ Добавить (ваша задача): **2 сервиса**
- **ИТОГО после исправлений: 12 сервисов**

### ВСЕГО в каталоге будет:
- Infrastructure: 19
- Platform-Services: **15** (было 10)
- Intelligent-Core: **12** (было 10)
- **GRAND TOTAL: ~46 сервисов** (было 45)

---

## 🚀 СЛЕДУЮЩИЙ ШАГ:

**ВЫ:** Добавляете collective + ai_workflow_optimizer (2 сервиса)

**Я:** Исправляю platform-services (4 сервиса) + добавляю 5 новых

**Затем:** Обновляем metadata в каталоге
