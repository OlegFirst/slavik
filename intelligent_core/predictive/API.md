# predictive - API Documentation

> Автоматически сгенерированная документация API endpoints

**Всего endpoints:** 7
**Ресурсов:** 7
**Последнее обновление:** 2025-10-07

---

## 📋 Содержание

- [](#)
- [certification](#certification)
- [expert-demand](#expert-demand)
- [health](#health)
- [journey](#journey)
- [recommendations](#recommendations)
- [similar-organizations](#similar-organizations)

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

## certification

### `GET` /certification/{org_id}

**Файл:** `predictions.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/certification/{org_id}" \
  -H "Authorization: Bearer <token>"
```

---

## expert-demand

### `GET` /expert-demand

**Файл:** `predictions.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/expert-demand" \
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

## journey

### `GET` /journey/{org_id}

**Файл:** `predictions.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/journey/{org_id}" \
  -H "Authorization: Bearer <token>"
```

---

## recommendations

### `GET` /recommendations/{org_id}

**Файл:** `predictions.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/recommendations/{org_id}" \
  -H "Authorization: Bearer <token>"
```

---

## similar-organizations

### `GET` /similar-organizations/{org_id}

**Файл:** `predictions.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/similar-organizations/{org_id}" \
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
