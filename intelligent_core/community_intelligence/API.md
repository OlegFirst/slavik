# community_intelligence - API Documentation

> Автоматически сгенерированная документация API endpoints

**Всего endpoints:** 36
**Ресурсов:** 23
**Последнее обновление:** 2025-10-07

---

## 📋 Содержание

- [](#)
- [annotations](#annotations)
- [clauses](#clauses)
- [contributions](#contributions)
- [from-workflow](#from-workflow)
- [guidance](#guidance)
- [health](#health)
- [insights](#insights)
- [leaderboard](#leaderboard)
- [marketplace](#marketplace)
- [my](#my)
- [pending](#pending)
- [preview-anonymization](#preview-anonymization)
- [reputation](#reputation)
- [search](#search)
- [similar](#similar)
- [stats](#stats)
- [timeline](#timeline)
- [transactions](#transactions)
- [{case_id}](#{case_id})
- [{contribution_id}](#{contribution_id})
- [{review_id}](#{review_id})
- [{user_id}](#{user_id})

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

## annotations

### `POST` /annotations

**Файл:** `routes.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/annotations" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `POST` /annotations/{annotation_id}/vote

**Файл:** `routes.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/annotations/{annotation_id}/vote" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

## clauses

### `GET` /clauses/search

**Файл:** `routes.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/clauses/search" \
  -H "Authorization: Bearer <token>"
```

---

## contributions

### `POST` /contributions

**Файл:** `routes.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/contributions" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `GET` /contributions/pending-reviews

**Файл:** `routes.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/contributions/pending-reviews" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /contributions/{contribution_id}

**Файл:** `routes.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/contributions/{contribution_id}" \
  -H "Authorization: Bearer <token>"
```

---

### `POST` /contributions/{contribution_id}/review

**Файл:** `routes.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/contributions/{contribution_id}/review" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

## from-workflow

### `POST` /from-workflow/{workflow_id}

**Файл:** `contributions.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/from-workflow/{workflow_id}" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

## guidance

### `GET` /guidance/{clause_id}

**Файл:** `routes.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/guidance/{clause_id}" \
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

### `GET` /health

**Файл:** `routes.py`

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

### `GET` /insights/similar-orgs/{org_id}

**Файл:** `routes.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/insights/similar-orgs/{org_id}" \
  -H "Authorization: Bearer <token>"
```

---

## leaderboard

### `GET` /leaderboard/global

**Файл:** `reputation.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/leaderboard/global" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /leaderboard/{module}

**Файл:** `reputation.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/leaderboard/{module}" \
  -H "Authorization: Bearer <token>"
```

---

## marketplace

### `GET` /marketplace/demand-forecast

**Файл:** `routes.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/marketplace/demand-forecast" \
  -H "Authorization: Bearer <token>"
```

---

## my

### `GET` /my

**Файл:** `reviews.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/my" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /my

**Файл:** `contributions.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/my" \
  -H "Authorization: Bearer <token>"
```

---

## pending

### `GET` /pending

**Файл:** `reviews.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/pending" \
  -H "Authorization: Bearer <token>"
```

---

## preview-anonymization

### `POST` /preview-anonymization

**Файл:** `contributions.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/preview-anonymization" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

## reputation

### `GET` /reputation/leaderboard

**Файл:** `routes.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/reputation/leaderboard" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /reputation/{user_id}

**Файл:** `routes.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/reputation/{user_id}" \
  -H "Authorization: Bearer <token>"
```

---

## search

### `GET` /search

**Файл:** `cases.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/search" \
  -H "Authorization: Bearer <token>"
```

---

## similar

### `GET` /similar/for-workflow

**Файл:** `cases.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/similar/for-workflow" \
  -H "Authorization: Bearer <token>"
```

---

## stats

### `GET` /stats/community

**Файл:** `routes.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/stats/community" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /stats/impact

**Файл:** `routes.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/stats/impact" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /stats/overview

**Файл:** `cases.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/stats/overview" \
  -H "Authorization: Bearer <token>"
```

---

## timeline

### `POST` /timeline/predict

**Файл:** `routes.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/timeline/predict" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `GET` /timeline/{org_id}/next-steps

**Файл:** `routes.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/timeline/{org_id}/next-steps" \
  -H "Authorization: Bearer <token>"
```

---

## transactions

### `GET` /transactions/{user_id}

**Файл:** `reputation.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/transactions/{user_id}" \
  -H "Authorization: Bearer <token>"
```

---

## {case_id}

### `GET` /{case_id}

**Файл:** `cases.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/{case_id}" \
  -H "Authorization: Bearer <token>"
```

---

## {contribution_id}

### `DELETE` /{contribution_id}

**Файл:** `contributions.py`

**Описание:**  
Удалить ресурс

**Пример запроса:**

```bash
curl -X DELETE \
  "http://localhost:8000/{contribution_id}" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /{contribution_id}

**Файл:** `contributions.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/{contribution_id}" \
  -H "Authorization: Bearer <token>"
```

---

## {review_id}

### `GET` /{review_id}

**Файл:** `reviews.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/{review_id}" \
  -H "Authorization: Bearer <token>"
```

---

## {user_id}

### `GET` /{user_id}

**Файл:** `reputation.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/{user_id}" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /{user_id}/expertise/{module}

**Файл:** `reputation.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/{user_id}/expertise/{module}" \
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
