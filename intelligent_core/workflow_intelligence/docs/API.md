# workflow_intelligence - API Documentation

> Автоматически сгенерированная документация API endpoints

**Всего endpoints:** 1
**Ресурсов:** 1
**Последнее обновление:** 2025-10-07

---

## 📋 Содержание

- [api](#api)

---

## api

### `GET` /api/compliance/check

**Файл:** `service_integration_template.py`

**Описание:**  
Получить список

**Пример запроса:**

```bash
curl -X GET \
  "http://localhost:8000/api/compliance/check" \
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
