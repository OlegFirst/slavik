# Shared - API Reference

**Version**: 1.0.0
**Last Updated**: 2025-10-09

## Base URL

N/A (library module)

## Authentication

Bearer token (JWT) required for all endpoints.

```
Authorization: Bearer <token>
```

## Endpoints

### Health Check

```
GET /health
```

Response:
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

## Error Responses

Standard HTTP status codes:
- 200: Success
- 400: Bad Request
- 401: Unauthorized
- 404: Not Found
- 500: Internal Server Error

---

**Document Control**
- Version: 1.0.0
- Author: AI Platform Team
