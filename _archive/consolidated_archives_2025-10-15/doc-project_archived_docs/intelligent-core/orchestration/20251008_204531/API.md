# orchestration - API Documentation

> Автоматически сгенерированная документация API endpoints

**Всего endpoints:** 80
**Ресурсов:** 18
**Последнее обновление:** 2025-10-07

---

## 📋 Содержание

- [](#)
- [admin](#admin)
- [alerts](#alerts)
- [analytics](#analytics)
- [api](#api)
- [audit](#audit)
- [benchmarks](#benchmarks)
- [cases](#cases)
- [dashboard](#dashboard)
- [execute](#execute)
- [executions](#executions)
- [health](#health)
- [metrics](#metrics)
- [performance](#performance)
- [status](#status)
- [storage](#storage)
- [tools](#tools)
- [trends](#trends)

---

## 

### `GET` /

**Файл:** `main.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/" \
  -H "Authorization: Bearer <token>"
```

---

## admin

### `POST` /admin/clear-cache

**Файл:** `knowledge_orchestrator.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/admin/clear-cache" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `GET` /admin/stats

**Файл:** `knowledge_orchestrator.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/admin/stats" \
  -H "Authorization: Bearer <token>"
```

---

### `POST` /admin/sync-benchmarks

**Файл:** `knowledge_orchestrator.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/admin/sync-benchmarks" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

## alerts

### `GET` /alerts/active

**Файл:** `monitoring_routes.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/alerts/active" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /alerts/history

**Файл:** `monitoring_routes.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/alerts/history" \
  -H "Authorization: Bearer <token>"
```

---

## analytics

### `GET` /analytics/cross-service-learning

**Файл:** `knowledge_orchestrator.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/analytics/cross-service-learning" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /analytics/platform

**Файл:** `knowledge_orchestrator.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/analytics/platform" \
  -H "Authorization: Bearer <token>"
```

---

## api

### `GET` /api/actions

**Файл:** `pdca_assistant.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/api/actions" \
  -H "Authorization: Bearer <token>"
```

---

### `POST` /api/actions/{action_id}/execute

**Файл:** `pdca_assistant.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/api/actions/{action_id}/execute" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `POST` /api/message

**Файл:** `pdca_assistant.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/api/message" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `POST` /api/phase/update

**Файл:** `pdca_assistant.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/api/phase/update" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `POST` /api/v1/ai/agent/process

**Файл:** `main.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/api/v1/ai/agent/process" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `GET` /api/v1/ai/agents/analytics

**Файл:** `main.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/api/v1/ai/agents/analytics" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /api/v1/ai/agents/health

**Файл:** `main.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/api/v1/ai/agents/health" \
  -H "Authorization: Bearer <token>"
```

---

### `POST` /api/v1/ai/analyze/incident

**Файл:** `main.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/api/v1/ai/analyze/incident" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `POST` /api/v1/ai/analyze/process-risk

**Файл:** `main.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/api/v1/ai/analyze/process-risk" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `GET` /api/v1/ai/decisions

**Файл:** `main.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/api/v1/ai/decisions" \
  -H "Authorization: Bearer <token>"
```

---

### `POST` /api/v1/ai/decisions/{decision_id}/approve

**Файл:** `main.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/api/v1/ai/decisions/{decision_id}/approve" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `POST` /api/v1/ai/decisions/{decision_id}/reject

**Файл:** `main.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/api/v1/ai/decisions/{decision_id}/reject" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `POST` /api/v1/ai/nlp/query

**Файл:** `main.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/api/v1/ai/nlp/query" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `GET` /api/v1/ai/rules

**Файл:** `main.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/api/v1/ai/rules" \
  -H "Authorization: Bearer <token>"
```

---

### `POST` /api/v1/ai/rules/{rule_name}/disable

**Файл:** `main.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/api/v1/ai/rules/{rule_name}/disable" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `POST` /api/v1/ai/rules/{rule_name}/enable

**Файл:** `main.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/api/v1/ai/rules/{rule_name}/enable" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `GET` /api/v1/ai/status

**Файл:** `main.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/api/v1/ai/status" \
  -H "Authorization: Bearer <token>"
```

---

### `POST` /api/v1/auth/refresh-token

**Файл:** `main.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/api/v1/auth/refresh-token" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `POST` /api/v1/auth/token-exchange

**Файл:** `main.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/api/v1/auth/token-exchange" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `POST` /api/v1/bcm/audit/start

**Файл:** `main.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/api/v1/bcm/audit/start" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `POST` /api/v1/bcm/bia/start

**Файл:** `main.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/api/v1/bcm/bia/start" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `POST` /api/v1/bcm/incident/report

**Файл:** `main.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/api/v1/bcm/incident/report" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `POST` /api/v1/claude/analyze-changes

**Файл:** `main.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/api/v1/claude/analyze-changes" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `POST` /api/v1/claude/create-pr

**Файл:** `main.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/api/v1/claude/create-pr" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `POST` /api/v1/claude/generate-config

**Файл:** `main.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/api/v1/claude/generate-config" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `GET` /api/v1/deployment/history

**Файл:** `main.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/api/v1/deployment/history" \
  -H "Authorization: Bearer <token>"
```

---

### `POST` /api/v1/deployment/orchestrate

**Файл:** `main.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/api/v1/deployment/orchestrate" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `POST` /api/v1/events/publish

**Файл:** `main.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/api/v1/events/publish" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `GET` /api/v1/platform/services

**Файл:** `main.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/api/v1/platform/services" \
  -H "Authorization: Bearer <token>"
```

---

### `POST` /api/v1/platform/services/{service}/restart

**Файл:** `main.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/api/v1/platform/services/{service}/restart" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `POST` /api/v1/platform/services/{service}/start

**Файл:** `main.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/api/v1/platform/services/{service}/start" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `GET` /api/v1/platform/services/{service}/status

**Файл:** `main.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/api/v1/platform/services/{service}/status" \
  -H "Authorization: Bearer <token>"
```

---

### `POST` /api/v1/platform/services/{service}/stop

**Файл:** `main.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/api/v1/platform/services/{service}/stop" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `GET` /api/v1/platform/status

**Файл:** `main.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/api/v1/platform/status" \
  -H "Authorization: Bearer <token>"
```

---

### `POST` /api/v1/scenario/generate

**Файл:** `main.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/api/v1/scenario/generate" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `GET` /api/v1/scenario/learning/stats

**Файл:** `main.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/api/v1/scenario/learning/stats" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /api/v1/scenario/status

**Файл:** `main.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/api/v1/scenario/status" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /api/v1/scenario/{scenario_id}

**Файл:** `main.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/api/v1/scenario/{scenario_id}" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /api/v1/scenario/{scenario_id}/learning

**Файл:** `main.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/api/v1/scenario/{scenario_id}/learning" \
  -H "Authorization: Bearer <token>"
```

---

### `POST` /api/v1/system/orchestrator/{orchestrator}/restart

**Файл:** `main.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/api/v1/system/orchestrator/{orchestrator}/restart" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `POST` /api/v1/system/restart

**Файл:** `main.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/api/v1/system/restart" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `GET` /api/v1/system/status

**Файл:** `main.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/api/v1/system/status" \
  -H "Authorization: Bearer <token>"
```

---

### `POST` /api/v1/workflows/start

**Файл:** `main.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/api/v1/workflows/start" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

## audit

### `GET` /audit

**Файл:** `routes.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/audit" \
  -H "Authorization: Bearer <token>"
```

---

## benchmarks

### `GET` /benchmarks/all

**Файл:** `knowledge_orchestrator.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/benchmarks/all" \
  -H "Authorization: Bearer <token>"
```

---

## cases

### `GET` /cases/search

**Файл:** `knowledge_orchestrator.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/cases/search" \
  -H "Authorization: Bearer <token>"
```

---

## dashboard

### `GET` /dashboard/business

**Файл:** `monitoring_routes.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/dashboard/business" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /dashboard/errors

**Файл:** `monitoring_routes.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/dashboard/errors" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /dashboard/performance

**Файл:** `monitoring_routes.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/dashboard/performance" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /dashboard/quality

**Файл:** `monitoring_routes.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/dashboard/quality" \
  -H "Authorization: Bearer <token>"
```

---

## execute

### `POST` /execute

**Файл:** `routes.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/execute" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

## executions

### `GET` /executions

**Файл:** `routes.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/executions" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /executions/{execution_id}

**Файл:** `routes.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/executions/{execution_id}" \
  -H "Authorization: Bearer <token>"
```

---

### `POST` /executions/{execution_id}/approve

**Файл:** `routes.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/executions/{execution_id}/approve" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `POST` /executions/{execution_id}/rollback

**Файл:** `routes.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/executions/{execution_id}/rollback" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

## health

### `GET` /health

**Файл:** `pdca_assistant.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/health" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /health

**Файл:** `main.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/health" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /health

**Файл:** `knowledge_orchestrator.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/health" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /health

**Файл:** `monitoring_routes.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/health" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /health

**Файл:** `routes.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/health" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /health/live

**Файл:** `monitoring_routes.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/health/live" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /health/ready

**Файл:** `monitoring_routes.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/health/ready" \
  -H "Authorization: Bearer <token>"
```

---

## metrics

### `GET` /metrics

**Файл:** `monitoring_routes.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/metrics" \
  -H "Authorization: Bearer <token>"
```

---

## performance

### `GET` /performance/bottlenecks

**Файл:** `monitoring_routes.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/performance/bottlenecks" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /performance/slow-queries

**Файл:** `monitoring_routes.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/performance/slow-queries" \
  -H "Authorization: Bearer <token>"
```

---

## status

### `GET` /status

**Файл:** `knowledge_orchestrator.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/status" \
  -H "Authorization: Bearer <token>"
```

---

## storage

### `GET` /storage/capacity

**Файл:** `monitoring_routes.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/storage/capacity" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /storage/size

**Файл:** `monitoring_routes.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/storage/size" \
  -H "Authorization: Bearer <token>"
```

---

## tools

### `GET` /tools

**Файл:** `routes.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/tools" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /tools/{tool_id}

**Файл:** `routes.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/tools/{tool_id}" \
  -H "Authorization: Bearer <token>"
```

---

## trends

### `GET` /trends/learning

**Файл:** `monitoring_routes.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/trends/learning" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /trends/usage

**Файл:** `monitoring_routes.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/trends/usage" \
  -H "Authorization: Bearer <token>"
```

---


## 🔗 Интеграция

### Authentication
```python
headers = {
    "Authorization": "Bearer <token>",
    "Content-Type": "application/json"
}
```

### Base URL
```
http://localhost:8000  # Development
https://api.example.com  # Production
```

---

**Сгенерировано:** 2025-10-07 05:07
**Инструмент:** `tools/generators/documentation_generator.py`
