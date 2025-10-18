# response-service - API Documentation

> Автоматически сгенерированная документация API endpoints

**Всего endpoints:** 18
**Ресурсов:** 14
**Последнее обновление:** 2025-10-07

---

## 📋 Содержание

- [](#)
- [analytics](#analytics)
- [api](#api)
- [cases](#cases)
- [critical-incidents](#critical-incidents)
- [health](#health)
- [incidents](#incidents)
- [insights](#insights)
- [live](#live)
- [metrics](#metrics)
- [playbooks](#playbooks)
- [public-incidents](#public-incidents)
- [ready](#ready)
- [recommendations](#recommendations)

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

## critical-incidents

### `POST` /critical-incidents

**Файл:** `dependencies.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/critical-incidents" \
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

## incidents

### `GET` /incidents

**Файл:** `dependencies.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/incidents" \
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

## live

### `GET` /live

**Файл:** `main.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/live" \
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

## playbooks

### `GET` /playbooks/recommend

**Файл:** `workflow_ai.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/playbooks/recommend" \
  -H "Authorization: Bearer <token>"
```

---

## public-incidents

### `GET` /public-incidents

**Файл:** `dependencies.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/public-incidents" \
  -H "Authorization: Bearer <token>"
```

---

## ready

### `GET` /ready

**Файл:** `main.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/ready" \
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
