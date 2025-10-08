# living-docs - API Documentation

> Автоматически сгенерированная документация API endpoints

**Всего endpoints:** 10
**Ресурсов:** 10
**Последнее обновление:** 2025-10-07

---

## 📋 Содержание

- [](#)
- [examples](#examples)
- [feedback](#feedback)
- [gaps](#gaps)
- [health](#health)
- [improvements](#improvements)
- [journey](#journey)
- [search](#search)
- [stats](#stats)
- [{page_id}](#{page_id})

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

## examples

### `POST` /examples/generate

**Файл:** `documentation.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/examples/generate" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

## feedback

### `POST` /feedback

**Файл:** `documentation.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/feedback" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

## gaps

### `GET` /gaps

**Файл:** `documentation.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/gaps" \
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

## improvements

### `GET` /improvements

**Файл:** `documentation.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/improvements" \
  -H "Authorization: Bearer <token>"
```

---

## journey

### `GET` /journey/{goal}

**Файл:** `documentation.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/journey/{goal}" \
  -H "Authorization: Bearer <token>"
```

---

## search

### `GET` /search

**Файл:** `documentation.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/search" \
  -H "Authorization: Bearer <token>"
```

---

## stats

### `GET` /stats

**Файл:** `main.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/stats" \
  -H "Authorization: Bearer <token>"
```

---

## {page_id}

### `GET` /{page_id}

**Файл:** `documentation.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/{page_id}" \
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
