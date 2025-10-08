# gateway - API Documentation

> Автоматически сгенерированная документация API endpoints

**Всего endpoints:** 10
**Ресурсов:** 5
**Последнее обновление:** 2025-10-07

---

## 📋 Содержание

- [api](#api)
- [auth](#auth)
- [health](#health)
- [metrics](#metrics)
- [query](#query)

---

## api

### `POST` /api/v1/gateway/ai/analyze

**Файл:** `main.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/api/v1/gateway/ai/analyze" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `POST` /api/v1/gateway/ai/optimize

**Файл:** `main.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/api/v1/gateway/ai/optimize" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `GET` /api/v1/gateway/services

**Файл:** `main.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/api/v1/gateway/services" \
  -H "Authorization: Bearer <token>"
```

---

## auth

### `POST` /auth/odoo

**Файл:** `main.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/auth/odoo" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `DELETE` /auth/odoo/session/{session_id}

**Файл:** `main.py`

**Описание:**  
Удалить ресурс

**Пример запроса:**

```bash
curl -X DELETE \
  "http://localhost:8000/auth/odoo/session/{session_id}" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /auth/odoo/session/{session_id}

**Файл:** `main.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/auth/odoo/session/{session_id}" \
  -H "Authorization: Bearer <token>"
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

### `GET` /health/databases

**Файл:** `main.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/health/databases" \
  -H "Authorization: Bearer <token>"
```

---

## metrics

### `GET` /metrics

**Файл:** `main.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/metrics" \
  -H "Authorization: Bearer <token>"
```

---

## query

### `POST` /query

**Файл:** `main.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/query" \
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
