# plans_service - API Documentation

> Автоматически сгенерированная документация API endpoints

**Всего endpoints:** 34
**Ресурсов:** 11
**Последнее обновление:** 2025-10-07

---

## 📋 Содержание

- [](#)
- [activations](#activations)
- [api](#api)
- [benchmarks](#benchmarks)
- [contact-lists](#contact-lists)
- [exercises](#exercises)
- [health](#health)
- [metrics](#metrics)
- [plans](#plans)
- [procedures](#procedures)
- [{item_id}](#{item_id})

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

## activations

### `GET` /activations

**Файл:** `routes.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/activations" \
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

## benchmarks

### `GET` /benchmarks

**Файл:** `workflow_ai.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/benchmarks" \
  -H "Authorization: Bearer <token>"
```

---

## contact-lists

### `GET` /contact-lists

**Файл:** `routes.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/contact-lists" \
  -H "Authorization: Bearer <token>"
```

---

### `POST` /contact-lists

**Файл:** `routes.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/contact-lists" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

## exercises

### `POST` /exercises/schedule

**Файл:** `bulk_operations.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/exercises/schedule" \
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

**Файл:** `health.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/health" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /health/detailed

**Файл:** `health.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/health/detailed" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /health/live

**Файл:** `health.py`

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

**Файл:** `health.py`

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

**Файл:** `metrics.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/metrics" \
  -H "Authorization: Bearer <token>"
```

---

## plans

### `GET` /plans

**Файл:** `routes.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/plans" \
  -H "Authorization: Bearer <token>"
```

---

### `POST` /plans

**Файл:** `bulk_operations.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/plans" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `POST` /plans

**Файл:** `routes.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/plans" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `DELETE` /plans/{plan_id}

**Файл:** `routes.py`

**Описание:**  
Удалить ресурс

**Пример запроса:**

```bash
curl -X DELETE \
  "http://localhost:8000/plans/{plan_id}" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /plans/{plan_id}

**Файл:** `routes.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/plans/{plan_id}" \
  -H "Authorization: Bearer <token>"
```

---

### `PUT` /plans/{plan_id}

**Файл:** `routes.py`

**Описание:**  
Обновить ресурс

**Пример запроса:**

```bash
curl -X PUT \
  "http://localhost:8000/plans/{plan_id}" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `POST` /plans/{plan_id}/activate

**Файл:** `routes.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/plans/{plan_id}/activate" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `POST` /plans/{plan_id}/activate-real

**Файл:** `routes.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/plans/{plan_id}/activate-real" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `POST` /plans/{plan_id}/approve

**Файл:** `routes.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/plans/{plan_id}/approve" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `GET` /plans/{plan_id}/procedures

**Файл:** `routes.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/plans/{plan_id}/procedures" \
  -H "Authorization: Bearer <token>"
```

---

### `POST` /plans/{plan_id}/procedures

**Файл:** `routes.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/plans/{plan_id}/procedures" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `DELETE` /plans/{plan_id}/procedures/{procedure_id}

**Файл:** `routes.py`

**Описание:**  
Удалить ресурс

**Пример запроса:**

```bash
curl -X DELETE \
  "http://localhost:8000/plans/{plan_id}/procedures/{procedure_id}" \
  -H "Authorization: Bearer <token>"
```

---

### `PUT` /plans/{plan_id}/procedures/{procedure_id}

**Файл:** `routes.py`

**Описание:**  
Обновить ресурс

**Пример запроса:**

```bash
curl -X PUT \
  "http://localhost:8000/plans/{plan_id}/procedures/{procedure_id}" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `GET` /plans/{plan_id}/resources

**Файл:** `routes.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/plans/{plan_id}/resources" \
  -H "Authorization: Bearer <token>"
```

---

### `POST` /plans/{plan_id}/resources

**Файл:** `routes.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/plans/{plan_id}/resources" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `GET` /plans/{plan_id}/reviews

**Файл:** `routes.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/plans/{plan_id}/reviews" \
  -H "Authorization: Bearer <token>"
```

---

### `POST` /plans/{plan_id}/reviews

**Файл:** `routes.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/plans/{plan_id}/reviews" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `POST` /plans/{plan_id}/submit-review

**Файл:** `routes.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/plans/{plan_id}/submit-review" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `GET` /plans/{plan_id}/workflow

**Файл:** `routes.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/plans/{plan_id}/workflow" \
  -H "Authorization: Bearer <token>"
```

---

## procedures

### `POST` /procedures/validate

**Файл:** `bulk_operations.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/procedures/validate" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

## {item_id}

### `GET` /{item_id}/ai-advice

**Файл:** `workflow_ai.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/{item_id}/ai-advice" \
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
