# BCM Platform API Documentation

## Обзор API

ISO 22301 BCM Platform предоставляет RESTful API для интеграции с внешними системами и построения пользовательских интерфейсов.

### Base URL
```
https://api.bcm-platform.com/api/v1
```

### Аутентификация
```http
Authorization: Bearer <JWT_TOKEN>
X-Client-ID: <CLIENT_ID>
Content-Type: application/json
```

## Основные API эндпоинты

### Business Impact Analysis (BIA) API

#### Список бизнес-процессов
```http
GET /bcm/bia/processes
```

**Response:**
```json
{
  "count": 150,
  "results": [
    {
      "id": "uuid-1234",
      "name": "Order Processing",
      "criticality_level": "critical",
      "rto_hours": 4,
      "rpo_hours": 1,
      "financial_impact_hourly": 50000.00
    }
  ]
}
```

#### AI-оптимизация RTO/RPO
```http
POST /bcm/bia/optimize-rto-rpo
```

### Risk Management API

#### Список рисков
```http
GET /bcm/risk/risks
```

#### AI анализ рисков
```http
POST /bcm/risk/ai-analysis
```

### Incident Management API

#### Регистрация инцидента
```http
POST /bcm/incident/report
```

#### Эскалация инцидента
```http
POST /bcm/incident/{incident_id}/escalate
```

### Plans Management API

#### Активация плана
```http
POST /bcm/plans/{plan_id}/activate
```

### AI Analytics API

#### Запуск AI анализа
```http
POST /bcm/ai/trigger-analysis
```

#### Получение результатов AI
```http
GET /bcm/ai/analysis/{analysis_id}/results
```

## Обработка ошибок

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input parameters",
    "request_id": "req-12345"
  }
}
```

## Rate Limits

- **Standard**: 1000 requests/hour  
- **Premium**: 5000 requests/hour
- **Enterprise**: 20000 requests/hour