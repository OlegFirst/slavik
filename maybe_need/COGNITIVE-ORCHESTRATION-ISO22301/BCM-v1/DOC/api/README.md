# 🔌 API Documentation

Полная документация API BCM Platform.

## 📚 Содержание

| Файл | Описание |
|------|----------|
| [BCM_API_REFERENCE_COMPREHENSIVE.md](BCM_API_REFERENCE_COMPREHENSIVE.md) | Comprehensive API референс всех 200+ endpoints |
| [API_DOCUMENTATION.md](API_DOCUMENTATION.md) | Детальная API документация |
| [API_ENDPOINTS_EXPORT.md](API_ENDPOINTS_EXPORT.md) | Экспорт всех API endpoints |

## 🎯 API Архитектура

### Базовые URL
```yaml
Base URL: https://bcm.your-domain.com/api
API Version: v1
Authentication: Bearer Token / OAuth 2.0
Rate Limiting: 1000 requests/hour per user
Content Type: application/json
```

### Основные категории API

#### 1. **Core Platform APIs** (:8069/api/v1)
- BCM модули Odoo
- Базовые CRUD операции
- Поиск и фильтрация

#### 2. **AI Services APIs**
- AI Orchestrator (:8000)
- Scenario Orchestrator (:8085)
- BIA Engine (:8082)
- Document Processor (:8083)
- Compliance Checker (:8084)

#### 3. **Integration APIs**
- EventBus (:8001)
- Auth Service (:8005)
- Notification Service (:8004)

#### 4. **Adapter APIs**
- Grafana Adapter (:8006)
- TheHive Adapter (:8007)
- LMS Adapter (:8008)

## 📖 Быстрый старт

### Аутентификация
```bash
curl -X POST https://bcm.your-domain.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "password": "pass"}'
```

### Базовый запрос
```bash
curl -X GET https://bcm.your-domain.com/api/v1/bcm/modules \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 🔗 Связанная документация

- [Frontend API Integration](../frontend/clean/02_API_INTEGRATION.md)
- [Backend Architecture](../architecture/BACKEND_ARCHITECTURE.md)
- [Integration Flows](../business_logic/INTEGRATION_FLOWS.md)

---

**Последнее обновление**: 2025-09-28