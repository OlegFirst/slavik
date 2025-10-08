# runtime - API Documentation

> Автоматически сгенерированная документация API endpoints

**Всего endpoints:** 9
**Ресурсов:** 5
**Последнее обновление:** 2025-10-07

---

## 📋 Содержание

- [](#)
- [api](#api)
- [health](#health)
- [stats](#stats)
- [workflows](#workflows)

---

## 

### `GET` /

**Файл:** `fastapi_integration.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/" \
  -H "Authorization: Bearer <token>"
```

---

## api

### `GET` /api/v1/channels/{channel_id}/messages

**Файл:** `main.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/api/v1/channels/{channel_id}/messages" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /api/v1/channels/{channel_id}/users

**Файл:** `main.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/api/v1/channels/{channel_id}/users" \
  -H "Authorization: Bearer <token>"
```

---

### `POST` /api/v1/notifications/broadcast

**Файл:** `main.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/api/v1/notifications/broadcast" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `GET` /api/v1/stats

**Файл:** `main.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/api/v1/stats" \
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

## stats

### `GET` /stats

**Файл:** `fastapi_integration.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/stats" \
  -H "Authorization: Bearer <token>"
```

---

## workflows

### `POST` /workflows

**Файл:** `fastapi_integration.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/workflows" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `POST` /workflows/{workflow_id}/complete

**Файл:** `fastapi_integration.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/workflows/{workflow_id}/complete" \
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
