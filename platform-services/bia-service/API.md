# bia-service - API Documentation

> Автоматически сгенерированная документация API endpoints

**Всего endpoints:** 31
**Ресурсов:** 12
**Последнее обновление:** 2025-10-07

---

## 📋 Содержание

- [api](#api)
- [benchmarks](#benchmarks)
- [disruptions](#disruptions)
- [health](#health)
- [metrics](#metrics)
- [processes](#processes)
- [reports](#reports)
- [single-points-of-failure](#single-points-of-failure)
- [summary](#summary)
- [suppliers](#suppliers)
- [what-if-analysis](#what-if-analysis)
- [{item_id}](#{item_id})

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

## disruptions

### `POST` /disruptions

**Файл:** `supply_chain_api.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/disruptions" \
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

## metrics

### `GET` /metrics/cache

**Файл:** `main.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/metrics/cache" \
  -H "Authorization: Bearer <token>"
```

---

## processes

### `GET` /processes

**Файл:** `connection.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/processes" \
  -H "Authorization: Bearer <token>"
```

---

### `POST` /processes

**Файл:** `routes.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/processes" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `DELETE` /processes/bulk

**Файл:** `routes.py`

**Описание:**  
Удалить ресурс

**Пример запроса:**

```bash
curl -X DELETE \
  "http://localhost:8000/processes/bulk" \
  -H "Authorization: Bearer <token>"
```

---

### `PATCH` /processes/bulk

**Файл:** `routes.py`

**Описание:**  
Операция PATCH

**Пример запроса:**

```bash
curl -X PATCH \
  "http://localhost:8000/processes/bulk" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `POST` /processes/bulk

**Файл:** `routes.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/processes/bulk" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `POST` /processes/bulk/validate

**Файл:** `routes.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/processes/bulk/validate" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `DELETE` /processes/{process_id}

**Файл:** `routes.py`

**Описание:**  
Удалить ресурс

**Пример запроса:**

```bash
curl -X DELETE \
  "http://localhost:8000/processes/{process_id}" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /processes/{process_id}

**Файл:** `routes.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/processes/{process_id}" \
  -H "Authorization: Bearer <token>"
```

---

### `PUT` /processes/{process_id}

**Файл:** `routes.py`

**Описание:**  
Обновить ресурс

**Пример запроса:**

```bash
curl -X PUT \
  "http://localhost:8000/processes/{process_id}" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `POST` /processes/{process_id}/complete

**Файл:** `routes.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/processes/{process_id}/complete" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `POST` /processes/{process_id}/discover-dependencies

**Файл:** `routes.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/processes/{process_id}/discover-dependencies" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `GET` /processes/{process_id}/fields/{field_name}

**Файл:** `history.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/processes/{process_id}/fields/{field_name}" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /processes/{process_id}/snapshot/{version}

**Файл:** `history.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/processes/{process_id}/snapshot/{version}" \
  -H "Authorization: Bearer <token>"
```

---

### `POST` /processes/{process_id}/suggest-rto

**Файл:** `routes.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/processes/{process_id}/suggest-rto" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

## reports

### `GET` /reports/critical-processes

**Файл:** `routes.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/reports/critical-processes" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /reports/dependencies

**Файл:** `routes.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/reports/dependencies" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /reports/summary

**Файл:** `routes.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/reports/summary" \
  -H "Authorization: Bearer <token>"
```

---

## single-points-of-failure

### `GET` /single-points-of-failure

**Файл:** `supply_chain_api.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/single-points-of-failure" \
  -H "Authorization: Bearer <token>"
```

---

## summary

### `GET` /summary

**Файл:** `supply_chain_api.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/summary" \
  -H "Authorization: Bearer <token>"
```

---

## suppliers

### `GET` /suppliers

**Файл:** `supply_chain_api.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/suppliers" \
  -H "Authorization: Bearer <token>"
```

---

### `POST` /suppliers

**Файл:** `supply_chain_api.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/suppliers" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `GET` /suppliers/{supplier_id}

**Файл:** `supply_chain_api.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/suppliers/{supplier_id}" \
  -H "Authorization: Bearer <token>"
```

---

### `PATCH` /suppliers/{supplier_id}

**Файл:** `supply_chain_api.py`

**Описание:**  
Операция PATCH

**Пример запроса:**

```bash
curl -X PATCH \
  "http://localhost:8000/suppliers/{supplier_id}" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `GET` /suppliers/{supplier_id}/risk-profile

**Файл:** `supply_chain_api.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/suppliers/{supplier_id}/risk-profile" \
  -H "Authorization: Bearer <token>"
```

---

## what-if-analysis

### `POST` /what-if-analysis

**Файл:** `supply_chain_api.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/what-if-analysis" \
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
