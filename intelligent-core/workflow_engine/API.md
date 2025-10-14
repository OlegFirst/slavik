# workflow-engine - API Documentation

> Автоматически сгенерированная документация API endpoints

**Всего endpoints:** 10
**Ресурсов:** 6
**Последнее обновление:** 2025-10-07

---

## 📋 Содержание

- [health](#health)
- [instances](#instances)
- [metrics](#metrics)
- [processes](#processes)
- [tasks](#tasks)
- [users](#users)

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

## instances

### `GET` /instances

**Файл:** `main.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/instances" \
  -H "Authorization: Bearer <token>"
```

---

### `DELETE` /instances/{instance_id}

**Файл:** `main.py`

**Описание:**  
Удалить ресурс

**Пример запроса:**

```bash
curl -X DELETE \
  "http://localhost:8000/instances/{instance_id}" \
  -H "Authorization: Bearer <token>"
```

---

### `GET` /instances/{instance_id}/visual-state

**Файл:** `main.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/instances/{instance_id}/visual-state" \
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

## processes

### `GET` /processes

**Файл:** `main.py`

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

**Файл:** `main.py`

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

## tasks

### `POST` /tasks/{task_id}/assign

**Файл:** `main.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/tasks/{task_id}/assign" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

### `POST` /tasks/{task_id}/complete

**Файл:** `main.py`

**Описание:**  
Создать новый ресурс

**Пример запроса:**

```bash
curl -X POST \
  "http://localhost:8000/tasks/{task_id}/complete" \
  -H "Authorization: Bearer <token>"
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

---

## users

### `GET` /users/{user_email}/tasks

**Файл:** `main.py`

**Описание:**  
Получить детали по ID

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/users/{user_email}/tasks" \
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
