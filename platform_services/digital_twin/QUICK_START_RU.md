# Digital Twin - Быстрый старт 🚀

## Что мы сделали

Digital Twin теперь это **личный кабинет пользователя** с интеграцией во все сервисы платформы:

✅ **System Clone** - Создание цифровых копий сервисов
✅ **Multi-tenancy** - Разделение по организациям
✅ **JWT Authentication** - Безопасная авторизация
✅ **Platform Discovery** - Автоматическое обнаружение 13 сервисов
✅ **Simulation Integration** - Доступ к 7 движкам симуляции
✅ **BCM Integration** - Управление непрерывностью бизнеса
✅ **Data Collection** - 8 методов сбора данных организации

---

## Как запустить

### 1. Установка зависимостей

```bash
cd /Users/MD/AI-Platform-ISO/platform_services/D_T/digital_twin

# Если нужно установить зависимости
pip3 install fastapi uvicorn httpx pyjwt pydantic sqlalchemy redis
```

### 2. Запуск сервиса

```bash
PORT=8096 python3 -m uvicorn api.app:app --reload
```

Сервис запустится на http://localhost:8096

### 3. Проверка

Открой в браузере:
- **Swagger UI:** http://localhost:8096/docs
- **ReDoc:** http://localhost:8096/redoc
- **Health:** http://localhost:8096/api/v1/health

---

## Новые API endpoints

### 📊 Platform Topology (Топология платформы)

```bash
# Обнаружить все сервисы
curl http://localhost:8096/api/v1/topology \
  -H "Authorization: Bearer $TOKEN"

# Граф зависимостей
curl http://localhost:8096/api/v1/topology/graph \
  -H "Authorization: Bearer $TOKEN"

# Анализ критичности сервиса
curl http://localhost:8096/api/v1/topology/critical-services \
  -H "Authorization: Bearer $TOKEN"

# Что будет если eventbus упадёт?
curl http://localhost:8096/api/v1/topology/impact-analysis/eventbus \
  -H "Authorization: Bearer $TOKEN"
```

### 🔄 System Clone (Цифровое зеркало)

```bash
# Создать зеркало сервиса
curl -X POST http://localhost:8096/api/v1/system-clone/create \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "service_name": "eventbus",
    "deep_discovery": true
  }'

# Клонировать всю платформу
curl -X POST http://localhost:8096/api/v1/system-clone/clone-platform \
  -H "Authorization: Bearer $TOKEN"

# Сравнить зеркало с живым сервисом
curl http://localhost:8096/api/v1/system-clone/eventbus/compare \
  -H "Authorization: Bearer $TOKEN"
```

**Для чего нужен System Clone:**
- **What-if анализ** - протестировать изменения на копии
- **Backup конфигурации** - сохранить состояние сервиса
- **Документация** - автогенерация API документации
- **Disaster Recovery** - быстрое восстановление

### 🎯 Simulation Service (7 движков симуляции)

```bash
# Проверить здоровье simulation_service
curl http://localhost:8096/api/v1/platform-bridges/simulation-service/health \
  -H "Authorization: Bearer $TOKEN"

# Список доступных движков
curl http://localhost:8096/api/v1/platform-bridges/simulation-service/engines \
  -H "Authorization: Bearer $TOKEN"

# Monte Carlo симуляция
curl -X POST http://localhost:8096/api/v1/platform-bridges/simulation-service/monte-carlo \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Анализ времени восстановления",
    "variables": {
      "recovery_time": {
        "distribution": "normal",
        "mean": 48,
        "std": 12
      },
      "financial_impact": {
        "distribution": "uniform",
        "min": 100000,
        "max": 500000
      }
    },
    "iterations": 10000
  }'

# Генерация AI сценария
curl -X POST http://localhost:8096/api/v1/platform-bridges/simulation-service/scenarios/generate \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "category": "cyber",
    "complexity": 4,
    "industry": "finance",
    "organization_size": "large"
  }'
```

**7 доступных движков:**
1. **JaamSim** - Дискретная симуляция событий
2. **Monte Carlo** - Вероятностный анализ
3. **Scenario** - Исполнение BCM сценариев
4. **What-If** - Анализ решений
5. **BCM Queue** - Теория массового обслуживания (M/M/c)
6. **Advanced BIA** - Мульти-ресурсный BIA
7. **JaamSim Client** - Оркестратор BCM учений

### 🛡️ System BCM (Непрерывность бизнеса)

```bash
# Здоровье BCM сервиса
curl http://localhost:8096/api/v1/platform-bridges/system-bcm/health \
  -H "Authorization: Bearer $TOKEN"

# Статус BCM
curl http://localhost:8096/api/v1/platform-bridges/system-bcm/status \
  -H "Authorization: Bearer $TOKEN"

# Запустить BCM цикл вручную
curl -X POST http://localhost:8096/api/v1/platform-bridges/system-bcm/cycle/trigger \
  -H "Authorization: Bearer $TOKEN"

# Запустить восстановление сервиса
curl -X POST http://localhost:8096/api/v1/platform-bridges/system-bcm/recovery/trigger \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "service": "api-gateway",
    "incident_type": "failure"
  }'

# Общий статус непрерывности платформы
curl http://localhost:8096/api/v1/platform-bridges/system-bcm/platform-continuity \
  -H "Authorization: Bearer $TOKEN"
```

**BCM Цикл включает:**
1. **Health Check** - Проверка всех сервисов
2. **Analyze** - Выявление проблем
3. **Improve** - Применение улучшений
4. **Verify** - Проверка результата

### 📝 Data Collection (Сбор данных организации)

```bash
# Список методов сбора
curl http://localhost:8096/api/v1/data-collection/methods \
  -H "Authorization: Bearer $TOKEN"

# Список категорий данных
curl http://localhost:8096/api/v1/data-collection/categories \
  -H "Authorization: Bearer $TOKEN"

# Начать сессию сбора
curl -X POST http://localhost:8096/api/v1/data-collection/sessions \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "organization_id": "org-123",
    "collection_plan": {
      "methods": ["interview", "api_extraction"],
      "categories": ["structure", "processes", "technology"],
      "quality_threshold": 0.7
    }
  }'

# Собрать данные
curl -X POST http://localhost:8096/api/v1/data-collection/collect \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "session-abc",
    "method": "interview",
    "category": "structure",
    "data": {
      "departments": [
        {"name": "IT", "size": 50},
        {"name": "Finance", "size": 30}
      ]
    }
  }'

# Статус сессии
curl http://localhost:8096/api/v1/data-collection/sessions/session-abc/status \
  -H "Authorization: Bearer $TOKEN"

# Завершить сессию
curl -X POST http://localhost:8096/api/v1/data-collection/sessions/session-abc/complete \
  -H "Authorization: Bearer $TOKEN"
```

**8 методов сбора:**
1. **interview** - Интервью со стейкхолдерами
2. **document_analysis** - Парсинг документов
3. **system_integration** - Внешние системы
4. **survey** - Опросы и анкеты
5. **observation** - Прямое наблюдение
6. **api_extraction** - Извлечение через API
7. **database_query** - Запросы к БД
8. **file_upload** - Загрузка файлов (JSON, CSV, Excel)

**10 категорий данных:**
1. **structure** - Организационная структура
2. **processes** - Бизнес-процессы
3. **technology** - Технологическая инфраструктура
4. **financial** - Финансовые данные
5. **hr** - Человеческие ресурсы
6. **operations** - Операционные данные
7. **compliance** - Комплаенс
8. **strategic** - Стратегическое планирование
9. **performance** - Метрики производительности
10. **stakeholders** - Информация о стейкхолдерах

---

## Multi-tenancy и аутентификация

### Получение JWT токена

```bash
# Логин (через auth service на порту 8001)
TOKEN=$(curl -X POST "http://localhost:8001/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "password"
  }' | jq -r '.access_token')

echo "Токен: $TOKEN"
```

### Формат JWT токена

```json
{
  "sub": "user-id",
  "email": "user@example.com",
  "organization_id": "org-123",
  "tenant_id": "tenant-456",
  "role": "admin"
}
```

### Роли и права

**Роли:**
- **admin** - Все права (*)
- **manager** - Создание, чтение, обновление
- **user** - Чтение
- **viewer** - Только просмотр

**Примеры прав:**
- `simulations.create` - Создание симуляций
- `digital_twin.update` - Обновление Digital Twin
- `topology.read` - Просмотр топологии

### Row-Level Security (RLS)

Все запросы к БД автоматически фильтруются:
- По `tenant_id` - изоляция по тенантам
- По `organization_id` - доступ к своей организации
- По `user_id` - пользовательские права

---

## Тестирование полного flow

### Сценарий 1: Обнаружение и клонирование платформы

```bash
# 1. Получить токен
TOKEN=$(curl -X POST "http://localhost:8001/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "password"}' \
  | jq -r '.access_token')

# 2. Обнаружить платформу
curl http://localhost:8096/api/v1/topology \
  -H "Authorization: Bearer $TOKEN" | jq

# 3. Найти критичные сервисы
curl http://localhost:8096/api/v1/topology/critical-services \
  -H "Authorization: Bearer $TOKEN" | jq

# 4. Клонировать платформу
curl -X POST http://localhost:8096/api/v1/system-clone/clone-platform \
  -H "Authorization: Bearer $TOKEN" | jq
```

### Сценарий 2: Monte Carlo симуляция восстановления

```bash
# 1. Проверить доступность simulation_service
curl http://localhost:8096/api/v1/platform-bridges/simulation-service/health \
  -H "Authorization: Bearer $TOKEN" | jq

# 2. Запустить Monte Carlo
curl -X POST http://localhost:8096/api/v1/platform-bridges/simulation-service/monte-carlo \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Recovery Time Analysis",
    "variables": {
      "recovery_time": {"distribution": "normal", "mean": 48, "std": 12},
      "cost": {"distribution": "uniform", "min": 50000, "max": 200000}
    },
    "iterations": 5000
  }' | jq
```

### Сценарий 3: Полный цикл сбора данных

```bash
# 1. Начать сессию
SESSION=$(curl -X POST http://localhost:8096/api/v1/data-collection/sessions \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "organization_id": "org-123",
    "collection_plan": {
      "methods": ["interview"],
      "categories": ["structure", "processes"],
      "quality_threshold": 0.7
    }
  }' | jq -r '.session_id')

# 2. Собрать данные по структуре
curl -X POST http://localhost:8096/api/v1/data-collection/collect \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"session_id\": \"$SESSION\",
    \"method\": \"interview\",
    \"category\": \"structure\",
    \"data\": {
      \"departments\": [{\"name\": \"IT\", \"size\": 50}]
    }
  }" | jq

# 3. Статус сессии
curl http://localhost:8096/api/v1/data-collection/sessions/$SESSION/status \
  -H "Authorization: Bearer $TOKEN" | jq

# 4. Завершить сессию
curl -X POST http://localhost:8096/api/v1/data-collection/sessions/$SESSION/complete \
  -H "Authorization: Bearer $TOKEN" | jq
```

---

## Проверка работы с другими сервисами

### Запуск необходимых сервисов

```bash
# 1. simulation_service (Port 8095)
cd /Users/MD/AI-Platform-ISO/platform_services/simulation_service
PORT=8095 python3 main.py

# 2. system_bcm_service (Port 8050)
cd /Users/MD/AI-Platform-ISO/intelligent_core/system_bcm_service
PORT=8050 python3 main.py

# 3. eventbus (Port 8055)
cd /Users/MD/AI-Platform-ISO/infrastructure/eventbus
PORT=8055 npm run dev

# 4. auth service (Port 8001)
cd /Users/MD/AI-Platform-ISO/infrastructure/security/auth
PORT=8001 python3 main.py
```

### Проверка интеграции

```bash
# Здоровье всех bridges
curl http://localhost:8096/api/v1/platform-bridges/health \
  -H "Authorization: Bearer $TOKEN" | jq
```

---

## Swagger UI

Открой http://localhost:8096/docs и увидишь:

### Группы endpoints:

1. **authentication** - JWT авторизация
2. **organizations** - Управление организациями
3. **simulations** - Симуляции (старый API)
4. **system-clone** - 🆕 System Clone (новый)
5. **topology** - 🆕 Platform Topology (новый)
6. **integrations/bridges** - 🆕 Platform Bridges (новый)
7. **data-collection** - 🆕 Data Collection (новый)
8. **health** - Health checks

### Как пользоваться Swagger UI:

1. Нажми **Authorize** (вверху справа)
2. Вставь JWT токен: `Bearer <твой_токен>`
3. Теперь можешь тестировать любой endpoint прямо в браузере!

---

## Что дальше?

### Обязательно протестировать:
- [x] Запустить Digital Twin
- [ ] Получить JWT токен
- [ ] Обнаружить платформу через /topology
- [ ] Создать System Clone через /system-clone/create
- [ ] Запустить Monte Carlo через /platform-bridges/simulation-service/monte-carlo
- [ ] Проверить BCM статус через /platform-bridges/system-bcm/status

### Опционально:
- [ ] Запустить simulation_service и протестировать все 7 движков
- [ ] Запустить system_bcm_service и протестировать BCM цикл
- [ ] Создать полную сессию data collection
- [ ] Протестировать multi-tenancy с разными пользователями

---

## Troubleshooting

### Ошибка: "401 Unauthorized"

```bash
# Проверь токен
echo $TOKEN

# Получи новый токен
TOKEN=$(curl -X POST "http://localhost:8001/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "password"}' \
  | jq -r '.access_token')
```

### Ошибка: "Service unavailable"

```bash
# Проверь что сервисы запущены
lsof -i :8095  # simulation_service
lsof -i :8050  # system_bcm_service
lsof -i :8055  # eventbus
```

### Ошибка: "Module not found"

```bash
# Установи зависимости
cd /Users/MD/AI-Platform-ISO/platform_services/D_T/digital_twin
pip3 install -r requirements.txt
```

---

## Документы

- `MULTI_TENANT_API_COMPLETE.md` - Полная техническая документация (EN)
- `SYSTEM_CLONE_INTEGRATION_COMPLETE.md` - System Clone документация
- `CONTEXT_RESTORATION_MEMO.md` - Memo для восстановления контекста

---

**Готово к использованию!** 🎉

Вопросы? Проверь `/docs` или `MULTI_TENANT_API_COMPLETE.md`
