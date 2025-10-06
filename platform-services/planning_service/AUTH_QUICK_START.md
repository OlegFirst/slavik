# JWT Authentication Quick Start Guide
## Planning Service

**2-Minute Setup Guide for Developers**

---

## TL;DR

```bash
# Development Mode (No token needed)
curl -H "X-Dev-User: user-123" \
     -H "X-Dev-Tenant: tenant-456" \
     http://localhost:8011/api/strategies/

# Production Mode (JWT token required)
curl -H "Authorization: Bearer <your-jwt-token>" \
     http://localhost:8011/api/strategies/
```

---

## Quick Setup

### For Local Development

**1. No configuration needed!**
   - Default config already enables dev mode
   - Just use the dev headers

**2. Make requests with headers:**
```bash
# GET request
curl http://localhost:8011/api/strategies/ \
  -H "X-Dev-User: your-user-id" \
  -H "X-Dev-Tenant: your-tenant-id"

# POST request
curl -X POST http://localhost:8011/api/strategies/ \
  -H "Content-Type: application/json" \
  -H "X-Dev-User: your-user-id" \
  -H "X-Dev-Tenant: your-tenant-id" \
  -d '{"name":"Test","strategy_type":"preventive","target_rto_hours":24}'
```

### For Production

**1. Add to .env:**
```bash
JWT_ALGORITHM=RS256
JWT_PUBLIC_KEY=-----BEGIN PUBLIC KEY-----
... your RSA public key ...
-----END PUBLIC KEY-----
JWT_AUDIENCE=bcm-platform
```

**2. Make requests with JWT:**
```bash
curl http://localhost:8011/api/strategies/ \
  -H "Authorization: Bearer eyJhbGciOiJSUzI1NiIs..."
```

---

## Token Requirements

Your JWT must include:

```json
{
  "sub": "user-123",              // User ID
  "tenant_id": "tenant-456",      // Tenant ID (REQUIRED!)
  "email": "user@example.com",
  "roles": ["bcm_manager"],
  "exp": 1696348800               // Expiration
}
```

---

## Common Issues

### 401 Unauthorized

**Problem:** Missing or invalid authentication

**Solutions:**
- **Dev mode:** Add X-Dev-User and X-Dev-Tenant headers
- **Production:** Add valid Authorization: Bearer token
- **Check:** Token not expired
- **Check:** Token signature valid

### 404 Not Found (but resource exists)

**Problem:** Cross-tenant access

**Solution:** Resource belongs to different tenant. Use correct tenant_id in your token/headers.

---

## Testing

Run the test suite:
```bash
# Model tests
python3 test_auth.py

# Integration tests (requires service running)
./test_auth_integration.sh
```

---

## Code Examples

### Python (httpx)

```python
import httpx

# Development mode
headers = {
    "X-Dev-User": "user-123",
    "X-Dev-Tenant": "tenant-456"
}

async with httpx.AsyncClient() as client:
    response = await client.get(
        "http://localhost:8011/api/strategies/",
        headers=headers
    )
    strategies = response.json()

# Production mode
headers = {
    "Authorization": f"Bearer {your_jwt_token}"
}

async with httpx.AsyncClient() as client:
    response = await client.get(
        "http://localhost:8011/api/strategies/",
        headers=headers
    )
    strategies = response.json()
```

### JavaScript (fetch)

```javascript
// Development mode
const response = await fetch('http://localhost:8011/api/strategies/', {
  headers: {
    'X-Dev-User': 'user-123',
    'X-Dev-Tenant': 'tenant-456'
  }
});
const strategies = await response.json();

// Production mode
const response = await fetch('http://localhost:8011/api/strategies/', {
  headers: {
    'Authorization': `Bearer ${yourJwtToken}`
  }
});
const strategies = await response.json();
```

---

## API Endpoints Protected

All 8 endpoints require authentication:

- `POST   /api/strategies/` - Create strategy
- `GET    /api/strategies/` - List strategies
- `GET    /api/strategies/{id}` - Get strategy
- `PUT    /api/strategies/{id}` - Update strategy
- `DELETE /api/strategies/{id}` - Delete strategy
- `POST   /api/strategies/{id}/cost-benefit` - Cost-benefit analysis
- `POST   /api/strategies/{id}/submit-review` - Submit for review
- `POST   /api/strategies/{id}/approve` - Approve strategy

---

## Configuration Reference

```python
# .env file
JWT_ALGORITHM=RS256                    # RS256 or HS256
JWT_PUBLIC_KEY=PLACEHOLDER_DEV_MODE    # Public key or placeholder
JWT_AUDIENCE=bcm-platform              # Expected audience
JWT_SECRET=fallback-secret             # Fallback for HS256
```

---

## Need Help?

- **Full documentation:** See `JWT_AUTH_IMPLEMENTATION_REPORT.md`
- **Verification:** See `JWT_AUTH_VERIFICATION.md`
- **Integration tests:** Run `./test_auth_integration.sh`
- **Unit tests:** Run `python3 test_auth.py`

---

**Quick Start Complete! You're ready to use the Planning Service.**
