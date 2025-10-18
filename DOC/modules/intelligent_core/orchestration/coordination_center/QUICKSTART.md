# Coordination Center - Quick Start Guide

**5-минутный гайд для запуска Coordination Center**

---

## 🎯 Что это?

Coordination Center - это **посредник между AI и инструментами BCM**.

```
AI мозг → Intent → Coordination Center → API calls → BCM Tools
```

**Зачем?**
- ✅ AI не имеет прямого доступа к API (безопасность)
- ✅ Все AI действия логируются (audit trail)
- ✅ Поддержка rollback (откат действий)
- ✅ Human-in-the-loop для критичных операций
- ✅ Rate limiting (защита от спама)

---

## 🚀 Запуск за 3 шага

### Шаг 1: Установка зависимостей

```bash
cd /Users/MD/AI-Platform-ISO/infrastructure/coordination-center

# Install dependencies
pip install -r requirements.txt
```

### Шаг 2: Конфигурация

Создайте `.env` файл:

```bash
cp .env.example .env
```

Измените на реальные значения:
```bash
# Не нужно менять для локального запуска
COORDINATION_PORT=8004
PLATFORM_GATEWAY_URL=http://localhost:8000
INTELLIGENCE_GATEWAY_URL=http://localhost:8035
```

### Шаг 3: Запуск

```bash
python main.py
```

**Готово!** Coordination Center запущен на http://localhost:8004

---

## 🧪 Проверка

### 1. Health Check

```bash
curl http://localhost:8004/coordination/health
```

Ответ:
```json
{
  "status": "healthy",
  "timestamp": "2025-10-02T18:00:00",
  "services": {
    "command_interpreter": true,
    "execution_tracker": true,
    "tool_registry": true,
    "security_layer": true
  }
}
```

### 2. Список доступных инструментов

```bash
curl http://localhost:8004/coordination/tools
```

Ответ:
```json
{
  "tools": [
    {
      "tool_id": "bia_tool",
      "name": "Business Impact Analysis Tool",
      "category": "bcm",
      "supported_actions": ["create", "read", "update", "list", "analyze"]
    },
    {
      "tool_id": "digital_twin",
      "name": "Digital Twin",
      "category": "intelligence",
      "supported_actions": ["create_org", "get_org", "impact_analysis"]
    }
  ],
  "total": 7
}
```

### 3. API Документация

Откройте в браузере:
```
http://localhost:8004/docs
```

---

## 💡 Пример использования

### AI создает BIA процесс

**1. AI отправляет Intent:**

```bash
curl -X POST http://localhost:8004/coordination/execute \
  -H "Content-Type: application/json" \
  -d '{
    "intent": {
      "action": "create_bia",
      "entity": "process",
      "params": {
        "name": "Patient Admission",
        "criticality": "high",
        "rto_hours": 2,
        "rpo_hours": 1
      },
      "context": {
        "tenant_id": "hospital_001",
        "user_id": "ai_agent"
      }
    }
  }'
```

**2. Coordination Center обрабатывает:**

- ✅ Проверяет permissions (AI может создавать BIA?)
- ✅ Проверяет rate limit (не превышен лимит запросов?)
- ✅ Парсит intent → находит BIA tool
- ✅ Транслирует в API call: `POST http://localhost:8000/api/bia/processes`
- ✅ Выполняет запрос
- ✅ Логирует действие в audit log
- ✅ Возвращает результат

**3. Ответ:**

```json
{
  "execution_id": "exec_abc123",
  "status": "completed",
  "steps": [
    {"step": 1, "action": "parse_intent", "status": "completed"},
    {"step": 2, "action": "validate_command", "status": "completed"},
    {"step": 3, "action": "execute_api_call", "status": "completed"},
    {"step": 4, "action": "store_result", "status": "completed"}
  ],
  "result": {
    "id": 123,
    "name": "Patient Admission",
    "criticality": "high"
  }
}
```

**4. Проверка статуса:**

```bash
curl http://localhost:8004/coordination/executions/exec_abc123
```

---

## 🔥 Продвинутые фичи

### Human-in-the-Loop для критичных действий

Некоторые действия требуют approve от человека:

```bash
# AI пытается удалить запись
curl -X POST http://localhost:8004/coordination/execute \
  -d '{
    "intent": {
      "action": "delete_bia",
      "entity": "process",
      "params": {"id": 123},
      "context": {"tenant_id": "hospital_001", "user_id": "ai_agent"}
    }
  }'
```

Ответ:
```json
{
  "execution_id": "exec_xyz789",
  "status": "requires_approval",
  "result": {"message": "Waiting for human approval"}
}
```

**Человек approve:**

```bash
curl -X POST http://localhost:8004/coordination/executions/exec_xyz789/approve \
  -d '{
    "approved": true,
    "approved_by": "john_doe",
    "reason": "Authorized by team lead"
  }'
```

### Rollback выполненного действия

```bash
curl -X POST http://localhost:8004/coordination/executions/exec_abc123/rollback \
  -d '{
    "reason": "Mistake in criticality level",
    "initiated_by": "admin_user"
  }'
```

### Audit Log

Все AI действия логируются:

```bash
curl http://localhost:8004/coordination/audit?tenant_id=hospital_001
```

Ответ:
```json
[
  {
    "execution_id": "exec_abc123",
    "action": "create_bia",
    "user_id": "ai_agent",
    "tenant_id": "hospital_001",
    "status": "completed",
    "timestamp": "2025-10-02T18:00:00"
  }
]
```

---

## 🐳 Docker запуск

### Только Coordination Center

```bash
docker-compose up -d
```

### С мониторингом (Prometheus + Grafana)

```bash
docker-compose -f docker-compose.yml -f docker-compose.monitoring.yml up -d
```

**Доступ:**
- Coordination Center: http://localhost:8004
- Prometheus: http://localhost:9091
- Grafana: http://localhost:3002 (admin/admin)

---

## 📊 Мониторинг

### Метрики Prometheus

```bash
curl http://localhost:8004/metrics
```

Основные метрики:
- `http_requests_total` - количество запросов
- `http_request_duration_seconds` - latency
- `coordination_executions_total` - количество выполнений
- `coordination_executions_failed_total` - количество ошибок

### Grafana Dashboard

1. Откройте http://localhost:3002
2. Login: admin/admin
3. Dashboard автоматически настроен

---

## 🧪 Тестирование

### E2E тест

```bash
# Запустите PLATFORM Gateway на localhost:8000
# Запустите Coordination Center на localhost:8004

# Запустите тест
python tests/test_e2e_bia_creation.py
```

Вы увидите:
```
Running E2E tests...

✅ Health check passed
✅ Found 7 tools
   - bia_tool: Business Impact Analysis Tool
   - risk_tool: Risk Assessment Tool
   - digital_twin: Digital Twin
   ...

✅ Test passed! BIA created via Coordination Center
   Execution ID: exec_abc123
   Result: {'id': 123, 'name': 'Patient Admission'}

✅ All tests passed!
```

---

## 🎯 Следующие шаги

1. **Интеграция с AI Orchestration**
   - AI Orchestrator → Coordination Center → BCM Tools

2. **Persistence в PostgreSQL**
   - Сейчас executions хранятся in-memory
   - Нужно добавить PostgreSQL storage

3. **WebSocket для real-time updates**
   - Real-time progress tracking для AI

4. **Dashboard UI**
   - Веб-интерфейс для мониторинга AI действий

---

## 🆘 Troubleshooting

### Coordination Center не стартует

```bash
# Проверьте порт 8004 свободен
lsof -i :8004

# Проверьте логи
docker-compose logs coordination-center
```

### API calls не доходят до PLATFORM

```bash
# Проверьте PLATFORM Gateway запущен
curl http://localhost:8000/health

# Проверьте URL в .env
echo $PLATFORM_GATEWAY_URL
```

---

## 📚 Документация

- **API Docs:** http://localhost:8004/docs
- **README:** [README.md](README.md)
- **Architecture:** `/Users/MD/AI-Platform-ISO/docs/INFRASTRUCTURE_ARCHITECTURE.md`

---

**Готово!** Coordination Center настроен и работает 🚀
