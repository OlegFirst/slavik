# validation-service - API Documentation

> Автоматически сгенерированная документация API endpoints

**Всего endpoints:** 50
**Ресурсов:** 15
**Последнее обновление:** 2025-10-07

---

## 📋 Содержание

- [analytics](#analytics)
- [api](#api)
- [audits](#audits)
- [capa](#capa)
- [cases](#cases)
- [exercises](#exercises)
- [health](#health)
- [insights](#insights)
- [kpi](#kpi)
- [kpis](#kpis)
- [management-reviews](#management-reviews)
- [recommendations](#recommendations)
- [reports](#reports)
- [scenarios](#scenarios)
- [status](#status)

---

## analytics

### `GET` /analytics/patterns

**Файл:** `workflow_ai.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/analytics/patterns" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /analytics/performance

**Файл:** `workflow_ai.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/analytics/performance" \
  -H "Authorization: Bearer <token>"
```

---

## api

### `GET` /api/compliance/check

**Файл:** `main.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/api/compliance/check" \
  -H "Authorization: Bearer <token>"
```

---

### `POST` /api/events/webhook

**Файл:** `main.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/api/events/webhook" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

## audits

### `GET` /audits

**Файл:** `routes.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/audits" \
  -H "Authorization: Bearer <token>"
```

---

### `POST` /audits

**Файл:** `routes.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/audits" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `GET` /audits/findings-analysis

**Файл:** `workflow_ai.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/audits/findings-analysis" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /audits/{audit_id}

**Файл:** `routes.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/audits/{audit_id}" \
  -H "Authorization: Bearer <token>"
```

---

### `PATCH` /audits/{audit_id}/close

**Файл:** `routes.py`

**Описание:**  
Операция PATCH

**Пример запроса:**

```bash
curl -X PATCH \
  "http://localhost:8000/audits/{audit_id}/close" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `POST` /audits/{audit_id}/findings

**Файл:** `routes.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/audits/{audit_id}/findings" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `GET` /audits/{audit_id}/report

**Файл:** `routes.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/audits/{audit_id}/report" \
  -H "Authorization: Bearer <token>"
```

---

## capa

### `GET` /capa

**Файл:** `routes.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/capa" \
  -H "Authorization: Bearer <token>"
```

---

### `POST` /capa

**Файл:** `routes.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/capa" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `GET` /capa/effectiveness

**Файл:** `workflow_ai.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/capa/effectiveness" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /capa/{capa_id}

**Файл:** `routes.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/capa/{capa_id}" \
  -H "Authorization: Bearer <token>"
```

---

### `PATCH` /capa/{capa_id}

**Файл:** `routes.py`

**Описание:**  
Операция PATCH

**Пример запроса:**

```bash
curl -X PATCH \
  "http://localhost:8000/capa/{capa_id}" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `POST` /capa/{capa_id}/verify

**Файл:** `routes.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/capa/{capa_id}/verify" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

## cases

### `GET` /cases/search

**Файл:** `workflow_ai.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/cases/search" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /cases/{case_id}/similar

**Файл:** `workflow_ai.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/cases/{case_id}/similar" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /cases/{case_id}/timeline

**Файл:** `workflow_ai.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/cases/{case_id}/timeline" \
  -H "Authorization: Bearer <token>"
```

---

## exercises

### `GET` /exercises

**Файл:** `routes.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/exercises" \
  -H "Authorization: Bearer <token>"
```

---

### `POST` /exercises

**Файл:** `routes.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/exercises" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `GET` /exercises/effectiveness

**Файл:** `workflow_ai.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/exercises/effectiveness" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /exercises/{exercise_id}

**Файл:** `routes.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/exercises/{exercise_id}" \
  -H "Authorization: Bearer <token>"
```

---

### `POST` /exercises/{exercise_id}/complete

**Файл:** `routes.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/exercises/{exercise_id}/complete" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `POST` /exercises/{exercise_id}/observations

**Файл:** `routes.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/exercises/{exercise_id}/observations" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `GET` /exercises/{exercise_id}/report

**Файл:** `routes.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/exercises/{exercise_id}/report" \
  -H "Authorization: Bearer <token>"
```

---

### `POST` /exercises/{exercise_id}/start

**Файл:** `routes.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/exercises/{exercise_id}/start" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

## health

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

**Файл:** `workflow_ai.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/health" \
  -H "Authorization: Bearer <token>"
```

---

## insights

### `GET` /insights

**Файл:** `workflow_ai.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/insights" \
  -H "Authorization: Bearer <token>"
```

---

## kpi

### `GET` /kpi/alerts

**Файл:** `routes.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/kpi/alerts" \
  -H "Authorization: Bearer <token>"
```

---

### `POST` /kpi/alerts/{alert_id}/acknowledge

**Файл:** `routes.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/kpi/alerts/{alert_id}/acknowledge" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `POST` /kpi/collect-now

**Файл:** `routes.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/kpi/collect-now" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

## kpis

### `GET` /kpis

**Файл:** `routes.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/kpis" \
  -H "Authorization: Bearer <token>"
```

---

### `POST` /kpis

**Файл:** `routes.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/kpis" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `GET` /kpis/dashboard

**Файл:** `routes.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/kpis/dashboard" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /kpis/{kpi_id}

**Файл:** `routes.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/kpis/{kpi_id}" \
  -H "Authorization: Bearer <token>"
```

---

### `PATCH` /kpis/{kpi_id}

**Файл:** `routes.py`

**Описание:**  
Операция PATCH

**Пример запроса:**

```bash
curl -X PATCH \
  "http://localhost:8000/kpis/{kpi_id}" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `POST` /kpis/{kpi_id}/measure

**Файл:** `routes.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/kpis/{kpi_id}/measure" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `GET` /kpis/{kpi_id}/trend

**Файл:** `routes.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/kpis/{kpi_id}/trend" \
  -H "Authorization: Bearer <token>"
```

---

## management-reviews

### `GET` /management-reviews

**Файл:** `routes.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/management-reviews" \
  -H "Authorization: Bearer <token>"
```

---

### `POST` /management-reviews

**Файл:** `routes.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/management-reviews" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `GET` /management-reviews/{review_id}/prepare

**Файл:** `routes.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/management-reviews/{review_id}/prepare" \
  -H "Authorization: Bearer <token>"
```

---

## recommendations

### `GET` /recommendations

**Файл:** `workflow_ai.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/recommendations" \
  -H "Authorization: Bearer <token>"
```

---

## reports

### `GET` /reports/compliance-status

**Файл:** `routes.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/reports/compliance-status" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /reports/performance-summary

**Файл:** `routes.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/reports/performance-summary" \
  -H "Authorization: Bearer <token>"
```

---

## scenarios

### `GET` /scenarios

**Файл:** `routes.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/scenarios" \
  -H "Authorization: Bearer <token>"
```

---

### `POST` /scenarios

**Файл:** `routes.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/scenarios" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

## status

### `GET` /status

**Файл:** `routes.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/status" \
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
