# ai_workflow_optimizer - API Documentation

> Автоматически сгенерированная документация API endpoints

**Всего endpoints:** 7
**Ресурсов:** 2
**Последнее обновление:** 2025-10-07

---

## 📋 Содержание

- [api](#api)
- [health](#health)

---

## api

### `GET` /api/v1/analyze/bottlenecks/{process_id}

**Файл:** `main.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/api/v1/analyze/bottlenecks/{process_id}" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /api/v1/detect/anomalies/{process_id}

**Файл:** `main.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/api/v1/detect/anomalies/{process_id}" \
  -H "Authorization: Bearer <token>"
```

---

### `POST` /api/v1/models/retrain

**Файл:** `main.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/api/v1/models/retrain" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `GET` /api/v1/models/status

**Файл:** `main.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/api/v1/models/status" \
  -H "Authorization: Bearer <token>"
```

---

### `POST` /api/v1/optimize/performance

**Файл:** `main.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/api/v1/optimize/performance" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `GET` /api/v1/optimize/resources/{process_id}

**Файл:** `main.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/api/v1/optimize/resources/{process_id}" \
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
