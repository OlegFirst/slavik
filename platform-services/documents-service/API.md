# documents-service - API Documentation

> Автоматически сгенерированная документация API endpoints

**Всего endpoints:** 30
**Ресурсов:** 12
**Последнее обновление:** 2025-10-07

---

## 📋 Содержание

- [](#)
- [analytics](#analytics)
- [api](#api)
- [approvals](#approvals)
- [benchmarks](#benchmarks)
- [documents](#documents)
- [health](#health)
- [iso-coverage](#iso-coverage)
- [plans](#plans)
- [retention-policies](#retention-policies)
- [search](#search)
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

## analytics

### `GET` /analytics/compliance

**Файл:** `routes.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/analytics/compliance" \
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

## approvals

### `POST` /approvals/{approval_id}/respond

**Файл:** `routes.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/approvals/{approval_id}/respond" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
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

## documents

### `GET` /documents

**Файл:** `routes.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/documents" \
  -H "Authorization: Bearer <token>"
```

---

### `POST` /documents

**Файл:** `routes.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/documents" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `POST` /documents/compare

**Файл:** `routes.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/documents/compare" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `DELETE` /documents/{document_id}

**Файл:** `routes.py`

**Описание:**  
Удалить ресурс

**Пример запроса:**

```bash
curl -X DELETE \
  "http://localhost:8000/documents/{document_id}" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /documents/{document_id}

**Файл:** `routes.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/documents/{document_id}" \
  -H "Authorization: Bearer <token>"
```

---

### `PATCH` /documents/{document_id}

**Файл:** `routes.py`

**Описание:**  
Операция PATCH

**Пример запроса:**

```bash
curl -X PATCH \
  "http://localhost:8000/documents/{document_id}" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `GET` /documents/{document_id}/access-log

**Файл:** `routes.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/documents/{document_id}/access-log" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /documents/{document_id}/approvals

**Файл:** `routes.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/documents/{document_id}/approvals" \
  -H "Authorization: Bearer <token>"
```

---

### `POST` /documents/{document_id}/approvals

**Файл:** `routes.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/documents/{document_id}/approvals" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `GET` /documents/{document_id}/download

**Файл:** `routes.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/documents/{document_id}/download" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /documents/{document_id}/retention

**Файл:** `routes.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/documents/{document_id}/retention" \
  -H "Authorization: Bearer <token>"
```

---

### `POST` /documents/{document_id}/share

**Файл:** `routes.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/documents/{document_id}/share" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `GET` /documents/{document_id}/shares

**Файл:** `routes.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/documents/{document_id}/shares" \
  -H "Authorization: Bearer <token>"
```

---

### `POST` /documents/{document_id}/upload

**Файл:** `routes.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/documents/{document_id}/upload" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `POST` /documents/{document_id}/version

**Файл:** `routes.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/documents/{document_id}/version" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `GET` /documents/{document_id}/versions

**Файл:** `routes.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/documents/{document_id}/versions" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /documents/{document_id}/workflow/status

**Файл:** `routes.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/documents/{document_id}/workflow/status" \
  -H "Authorization: Bearer <token>"
```

---

### `POST` /documents/{document_id}/workflow/{action}

**Файл:** `routes.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/documents/{document_id}/workflow/{action}" \
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

## iso-coverage

### `GET` /iso-coverage

**Файл:** `routes.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/iso-coverage" \
  -H "Authorization: Bearer <token>"
```

---

## plans

### `GET` /plans/{plan_id}/documents

**Файл:** `routes.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/plans/{plan_id}/documents" \
  -H "Authorization: Bearer <token>"
```

---

## retention-policies

### `GET` /retention-policies

**Файл:** `routes.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/retention-policies" \
  -H "Authorization: Bearer <token>"
```

---

### `POST` /retention-policies

**Файл:** `routes.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/retention-policies" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

## search

### `GET` /search

**Файл:** `routes.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/search" \
  -H "Authorization: Bearer <token>"
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
