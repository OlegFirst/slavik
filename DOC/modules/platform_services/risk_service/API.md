# risk-service - API Documentation

> Автоматически сгенерированная документация API endpoints

**Всего endpoints:** 30
**Ресурсов:** 15
**Последнее обновление:** 2025-10-07

---

## 📋 Содержание

- [](#)
- [analytics](#analytics)
- [api](#api)
- [assessments](#assessments)
- [cases](#cases)
- [critical-risks](#critical-risks)
- [health](#health)
- [insights](#insights)
- [public-risks](#public-risks)
- [recommendations](#recommendations)
- [reports](#reports)
- [risk-heat-map](#risk-heat-map)
- [risk-trends](#risk-trends)
- [risks](#risks)
- [treatment-plans](#treatment-plans)

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

## assessments

### `GET` /assessments

**Файл:** `routes.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/assessments" \
  -H "Authorization: Bearer <token>"
```

---

### `POST` /assessments

**Файл:** `routes.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/assessments" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `DELETE` /assessments/{risk_id}

**Файл:** `routes.py`

**Описание:**  
Удалить ресурс

**Пример запроса:**

```bash
curl -X DELETE \
  "http://localhost:8000/assessments/{risk_id}" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /assessments/{risk_id}

**Файл:** `routes.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/assessments/{risk_id}" \
  -H "Authorization: Bearer <token>"
```

---

### `PUT` /assessments/{risk_id}

**Файл:** `routes.py`

**Описание:**  
Обновить ресурс

**Пример запроса:**

```bash
curl -X PUT \
  "http://localhost:8000/assessments/{risk_id}" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `GET` /assessments/{risk_id}/fair-analysis

**Файл:** `routes.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/assessments/{risk_id}/fair-analysis" \
  -H "Authorization: Bearer <token>"
```

---

### `POST` /assessments/{risk_id}/fair-analysis

**Файл:** `routes.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/assessments/{risk_id}/fair-analysis" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `GET` /assessments/{risk_id}/matrix-position

**Файл:** `routes.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/assessments/{risk_id}/matrix-position" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /assessments/{risk_id}/monte-carlo

**Файл:** `routes.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/assessments/{risk_id}/monte-carlo" \
  -H "Authorization: Bearer <token>"
```

---

### `POST` /assessments/{risk_id}/monte-carlo

**Файл:** `routes.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/assessments/{risk_id}/monte-carlo" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `GET` /assessments/{risk_id}/treatment-plans

**Файл:** `routes.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/assessments/{risk_id}/treatment-plans" \
  -H "Authorization: Bearer <token>"
```

---

### `POST` /assessments/{risk_id}/treatment-plans

**Файл:** `routes.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/assessments/{risk_id}/treatment-plans" \
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

## critical-risks

### `POST` /critical-risks

**Файл:** `dependencies.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/critical-risks" \
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

## public-risks

### `GET` /public-risks

**Файл:** `dependencies.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/public-risks" \
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

### `GET` /reports

**Файл:** `routes.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/reports" \
  -H "Authorization: Bearer <token>"
```

---

## risk-heat-map

### `GET` /risk-heat-map

**Файл:** `routes.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/risk-heat-map" \
  -H "Authorization: Bearer <token>"
```

---

## risk-trends

### `GET` /risk-trends

**Файл:** `routes.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/risk-trends" \
  -H "Authorization: Bearer <token>"
```

---

## risks

### `GET` /risks

**Файл:** `dependencies.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/risks" \
  -H "Authorization: Bearer <token>"
```

---

## treatment-plans

### `PUT` /treatment-plans/{plan_id}

**Файл:** `routes.py`

**Описание:**  
Обновить ресурс

**Пример запроса:**

```bash
curl -X PUT \
  "http://localhost:8000/treatment-plans/{plan_id}" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
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
