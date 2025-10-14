# collective - API Documentation

> Автоматически сгенерированная документация API endpoints

**Всего endpoints:** 9
**Ресурсов:** 7
**Последнее обновление:** 2025-10-07

---

## 📋 Содержание

- [](#)
- [accept-help](#accept-help)
- [active](#active)
- [check](#check)
- [create](#create)
- [health](#health)
- [{agent_id}](#{agent_id})

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

## accept-help

### `POST` /accept-help

**Файл:** `stuck_detection.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/accept-help" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

## active

### `GET` /active

**Файл:** `collective_agents.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/active" \
  -H "Authorization: Bearer <token>"
```

---

## check

### `GET` /check

**Файл:** `stuck_detection.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/check" \
  -H "Authorization: Bearer <token>"
```

---

## create

### `POST` /create

**Файл:** `collective_agents.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/create" \
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

## {agent_id}

### `GET` /{agent_id}

**Файл:** `collective_agents.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/{agent_id}" \
  -H "Authorization: Bearer <token>"
```

---

### `POST` /{agent_id}/chat

**Файл:** `collective_agents.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/{agent_id}/chat" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `GET` /{agent_id}/history

**Файл:** `collective_agents.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/{agent_id}/history" \
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
