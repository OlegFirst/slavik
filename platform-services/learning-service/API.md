# learning-service - API Documentation

> Автоматически сгенерированная документация API endpoints

**Всего endpoints:** 34
**Ресурсов:** 15
**Последнее обновление:** 2025-10-07

---

## 📋 Содержание

- [](#)
- [api](#api)
- [auth](#auth)
- [benchmarks](#benchmarks)
- [certifications](#certifications)
- [departments](#departments)
- [enrollments](#enrollments)
- [gamification](#gamification)
- [health](#health)
- [leaderboard](#leaderboard)
- [learners](#learners)
- [metrics](#metrics)
- [persons](#persons)
- [programs](#programs)
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

### `GET` /api/governance/policies

**Файл:** `connection.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/api/governance/policies" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /api/learning/programs

**Файл:** `connection.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/api/learning/programs" \
  -H "Authorization: Bearer <token>"
```

---

## auth

### `POST` /auth/token

**Файл:** `main.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/auth/token" \
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

## certifications

### `GET` /certifications/expiring

**Файл:** `analytics.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/certifications/expiring" \
  -H "Authorization: Bearer <token>"
```

---

## departments

### `GET` /departments/metrics

**Файл:** `analytics.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/departments/metrics" \
  -H "Authorization: Bearer <token>"
```

---

## enrollments

### `POST` /enrollments

**Файл:** `routes.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/enrollments" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `GET` /enrollments/{enrollment_id}

**Файл:** `routes.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/enrollments/{enrollment_id}" \
  -H "Authorization: Bearer <token>"
```

---

### `POST` /enrollments/{enrollment_id}/approve

**Файл:** `routes.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/enrollments/{enrollment_id}/approve" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `POST` /enrollments/{enrollment_id}/assess

**Файл:** `routes.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/enrollments/{enrollment_id}/assess" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `POST` /enrollments/{enrollment_id}/certify

**Файл:** `routes.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/enrollments/{enrollment_id}/certify" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `POST` /enrollments/{enrollment_id}/complete

**Файл:** `routes.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/enrollments/{enrollment_id}/complete" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `PATCH` /enrollments/{enrollment_id}/progress

**Файл:** `routes.py`

**Описание:**  
Операция PATCH

**Пример запроса:**

```bash
curl -X PATCH \
  "http://localhost:8000/enrollments/{enrollment_id}/progress" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `POST` /enrollments/{enrollment_id}/start

**Файл:** `routes.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/enrollments/{enrollment_id}/start" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `POST` /enrollments/{enrollment_id}/submit

**Файл:** `routes.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/enrollments/{enrollment_id}/submit" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

## gamification

### `GET` /gamification/metrics

**Файл:** `analytics.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/gamification/metrics" \
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

## leaderboard

### `GET` /leaderboard

**Файл:** `routes.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/leaderboard" \
  -H "Authorization: Bearer <token>"
```

---

## learners

### `GET` /learners/{person_id}/profile

**Файл:** `analytics.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/learners/{person_id}/profile" \
  -H "Authorization: Bearer <token>"
```

---

## metrics

### `GET` /metrics

**Файл:** `analytics.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/metrics" \
  -H "Authorization: Bearer <token>"
```

---

## persons

### `GET` /persons/{person_id}/achievements

**Файл:** `routes.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/persons/{person_id}/achievements" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /persons/{person_id}/enrollments

**Файл:** `routes.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/persons/{person_id}/enrollments" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /persons/{person_id}/points

**Файл:** `routes.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/persons/{person_id}/points" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /persons/{person_id}/rank

**Файл:** `routes.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/persons/{person_id}/rank" \
  -H "Authorization: Bearer <token>"
```

---

## programs

### `GET` /programs

**Файл:** `routes.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/programs" \
  -H "Authorization: Bearer <token>"
```

---

### `POST` /programs

**Файл:** `routes.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/programs" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `GET` /programs/performance

**Файл:** `analytics.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/programs/performance" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /programs/{program_id}

**Файл:** `routes.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/programs/{program_id}" \
  -H "Authorization: Bearer <token>"
```

---

### `PATCH` /programs/{program_id}

**Файл:** `routes.py`

**Описание:**  
Операция PATCH

**Пример запроса:**

```bash
curl -X PATCH \
  "http://localhost:8000/programs/{program_id}" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `POST` /programs/{program_id}/archive

**Файл:** `routes.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/programs/{program_id}/archive" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `POST` /programs/{program_id}/publish

**Файл:** `routes.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/programs/{program_id}/publish" \
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
