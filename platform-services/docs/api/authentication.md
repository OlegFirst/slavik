# Authentication & Authorization Guide

## Overview

The BCM Platform uses **JWT (JSON Web Token)** Bearer authentication for all API endpoints. In development mode, you can use the `X-Dev-User` header for testing purposes.

---

## Authentication Methods

### Production: JWT Bearer Token

All API requests must include a valid JWT token in the Authorization header:

```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     http://localhost:8012/api/bia/processes
```

### Development: X-Dev-User Header

For development and testing, use the `X-Dev-User` header with a JSON user context:

```bash
curl -H 'X-Dev-User: {"sub":"user-123","tenant_id":"tenant-abc","permissions":["BIA_VIEW"]}' \
     http://localhost:8012/api/bia/processes
```

---

## JWT Token Structure

```json
{
  "sub": "user-123",              // User ID (subject)
  "tenant_id": "tenant-abc",      // Tenant identifier (for multi-tenancy)
  "permissions": [                // RBAC permissions array
    "BIA_VIEW",
    "BIA_CREATE",
    "COMPLIANCE_VIEW"
  ],
  "email": "user@company.com",    // Optional: user email
  "name": "John Doe",             // Optional: user full name
  "roles": ["BCM_MANAGER"],       // Optional: user roles
  "exp": 1735689600,              // Token expiration (Unix timestamp)
  "iat": 1735603200               // Token issued at (Unix timestamp)
}
```

### Required Claims

- **sub** (Subject): Unique user identifier
- **tenant_id**: Tenant identifier for data isolation
- **permissions**: Array of permission strings for RBAC

### Optional Claims

- **email**: User's email address
- **name**: User's full name
- **roles**: User's role names
- **exp**: Expiration time
- **iat**: Issued at time

---

## Multi-Tenancy & Data Isolation

### Tenant Isolation Model

Every API request is automatically filtered by `tenant_id` from the JWT token. This ensures:

- Users can only access data belonging to their tenant
- No cross-tenant data leakage
- Automatic row-level security

### How It Works

1. **JWT Extraction**: Service extracts `tenant_id` from JWT
2. **Query Filtering**: All database queries automatically filter by `tenant_id`
3. **Response Validation**: Responses validated to ensure tenant match
4. **Error Handling**: 403 Forbidden if tenant mismatch detected

### Example

```python
# User with tenant_id="tenant-abc" tries to access resource from tenant-xyz
GET /api/bia/processes/123?tenant_id=tenant-xyz

# Result: 403 Forbidden
{
  "detail": "Access denied - tenant mismatch"
}
```

---

## Role-Based Access Control (RBAC)

### Permission Model

The platform uses **permission-based RBAC**. Each endpoint requires specific permissions.

### Permission Naming Convention

```
<SERVICE>_<ACTION>
```

Examples:
- `BIA_VIEW` - View BIA processes
- `BIA_CREATE` - Create BIA processes
- `COMPLIANCE_EDIT` - Edit compliance records
- `PLAN_ACTIVATE` - Activate BC plans

---

## Service Permissions

### BIA Service (Port 8012)

| Permission | Description | Endpoints |
|------------|-------------|-----------|
| `BIA_VIEW` | View BIA processes and reports | GET /api/bia/processes, GET /api/bia/reports/* |
| `BIA_CREATE` | Create BIA processes | POST /api/bia/processes |
| `BIA_UPDATE` | Update BIA processes | PUT /api/bia/processes/{id} |
| `BIA_DELETE` | Delete BIA processes | DELETE /api/bia/processes/{id} |
| `BIA_COMPLETE` | Mark BIA as completed | POST /api/bia/processes/{id}/complete |
| `BIA_AI_SUGGEST` | Use AI features | POST /api/bia/processes/{id}/suggest-rto |

### Compliance Service (Port 8014)

| Permission | Description | Endpoints |
|------------|-------------|-----------|
| `COMPLIANCE_VIEW` | View compliance data | GET /api/assessments, GET /api/evidence |
| `COMPLIANCE_EDIT` | Edit compliance data | POST/PUT /api/evidence, POST /api/assessments |
| `AUDIT_MANAGE` | Manage audits | POST /api/audit/audits, POST /api/audit/audits/{id}/findings |
| `NC_MANAGE` | Manage nonconformities | POST /api/nonconformities, POST /api/nonconformities/{id}/rca/start |

### Planning Service (Port 8011)

| Permission | Description | Endpoints |
|------------|-------------|-----------|
| `STRATEGY_VIEW` | View strategies | GET /api/strategies |
| `STRATEGY_CREATE` | Create/edit strategies | POST /api/strategies, PUT /api/strategies/{id} |
| `STRATEGY_APPROVE` | Approve strategies | POST /api/strategies/{id}/approve |

### Plans Service (Port 8023)

| Permission | Description | Endpoints |
|------------|-------------|-----------|
| `PLAN_VIEW` | View BC plans | GET /api/plans/plans |
| `PLAN_CREATE` | Create/edit plans | POST /api/plans/plans, PUT /api/plans/plans/{id} |
| `PLAN_APPROVE` | Approve plans | POST /api/plans/plans/{id}/approve |
| `PLAN_ACTIVATE` | Activate plans | POST /api/plans/plans/{id}/activate |

---

## Permission Checking

### How Permission Checks Work

1. **Endpoint Decoration**: Each endpoint decorated with `@require_permission(Permission.XXX)`
2. **JWT Parsing**: Service extracts permissions from JWT
3. **Permission Check**: Verifies required permission exists
4. **Access Decision**: Allow (200) or Deny (403)

### Example: Python Implementation

```python
from shared.auth import require_permission, Permission

@router.post("/processes", response_model=BIAProcess)
@require_permission(Permission.BIA_CREATE)
async def create_bia_process(
    process: BIAProcessCreate,
    current_user: dict = Depends(get_current_user)
):
    # Permission check passed - user has BIA_CREATE
    return await service.create_process(process)
```

---

## Error Responses

### 401 Unauthorized

Missing or invalid JWT token:

```json
{
  "detail": "Not authenticated",
  "error_code": "MISSING_TOKEN"
}
```

### 403 Forbidden

#### Insufficient Permissions

```json
{
  "detail": "Insufficient permissions. Required: BIA_CREATE",
  "error_code": "PERMISSION_DENIED",
  "required_permission": "BIA_CREATE",
  "user_permissions": ["BIA_VIEW"]
}
```

#### Tenant Mismatch

```json
{
  "detail": "Access denied - tenant mismatch",
  "error_code": "TENANT_MISMATCH",
  "user_tenant": "tenant-abc",
  "resource_tenant": "tenant-xyz"
}
```

---

## Security Best Practices

### JWT Token Management

1. **Secure Storage**
   - Store tokens in httpOnly cookies (web apps)
   - Use secure storage (mobile apps)
   - Never log tokens

2. **Token Expiration**
   - Set reasonable expiration (e.g., 1 hour)
   - Implement token refresh mechanism
   - Clear expired tokens

3. **Token Validation**
   - Verify signature
   - Check expiration
   - Validate claims

### API Security

1. **HTTPS Only**
   - Always use HTTPS in production
   - Redirect HTTP to HTTPS

2. **Rate Limiting**
   - Implement rate limiting per user/IP
   - Prevent brute force attacks

3. **Input Validation**
   - Validate all input data
   - Sanitize user inputs
   - Use Pydantic models for validation

---

## Examples

### Python Example

```python
import requests
import json

# JWT Token (from your auth service)
jwt_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

headers = {
    "Authorization": f"Bearer {jwt_token}",
    "Content-Type": "application/json"
}

response = requests.post(
    "http://localhost:8012/api/bia/processes",
    headers=headers,
    json={
        "tenant_id": "tenant-123",
        "name": "Payment Processing",
        "criticality": "CRITICAL",
        "rto_hours": 2,
        "rpo_hours": 1,
        "mtpd_hours": 4
    }
)

if response.status_code == 201:
    print("Success:", response.json())
elif response.status_code == 401:
    print("Authentication failed - invalid token")
elif response.status_code == 403:
    print("Permission denied:", response.json()["detail"])
```

### JavaScript (Axios) Example

```javascript
const axios = require('axios');

const jwtToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...';

axios.post('http://localhost:8012/api/bia/processes', {
  tenant_id: 'tenant-123',
  name: 'Payment Processing',
  criticality: 'CRITICAL',
  rto_hours: 2,
  rpo_hours: 1,
  mtpd_hours: 4
}, {
  headers: {
    'Authorization': `Bearer ${jwtToken}`,
    'Content-Type': 'application/json'
  }
})
.then(response => {
  console.log('Success:', response.data);
})
.catch(error => {
  if (error.response.status === 401) {
    console.error('Authentication failed');
  } else if (error.response.status === 403) {
    console.error('Permission denied:', error.response.data.detail);
  }
});
```

### cURL Example (Development)

```bash
# Development mode with X-Dev-User header
curl -X POST http://localhost:8012/api/bia/processes \
  -H 'X-Dev-User: {"sub":"user-123","tenant_id":"tenant-abc","permissions":["BIA_CREATE","BIA_VIEW"]}' \
  -H 'Content-Type: application/json' \
  -d '{
    "tenant_id": "tenant-abc",
    "name": "Payment Processing",
    "criticality": "CRITICAL",
    "rto_hours": 2,
    "rpo_hours": 1,
    "mtpd_hours": 4
  }'
```

### cURL Example (Production)

```bash
# Production mode with JWT Bearer token
JWT_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

curl -X POST http://localhost:8012/api/bia/processes \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "tenant_id": "tenant-abc",
    "name": "Payment Processing",
    "criticality": "CRITICAL",
    "rto_hours": 2,
    "rpo_hours": 1,
    "mtpd_hours": 4
  }'
```

---

## Testing Authentication

### Unit Tests

```python
import pytest
from fastapi.testclient import TestClient

def test_missing_token():
    """Test request without token returns 401"""
    response = client.get("/api/bia/processes")
    assert response.status_code == 401

def test_insufficient_permissions():
    """Test user without required permission returns 403"""
    headers = {
        "X-Dev-User": json.dumps({
            "sub": "user-123",
            "tenant_id": "tenant-abc",
            "permissions": ["BIA_VIEW"]  # Missing BIA_CREATE
        })
    }
    response = client.post("/api/bia/processes", headers=headers, json={...})
    assert response.status_code == 403

def test_tenant_isolation():
    """Test user cannot access other tenant's data"""
    headers = {
        "X-Dev-User": json.dumps({
            "sub": "user-123",
            "tenant_id": "tenant-abc",
            "permissions": ["BIA_VIEW"]
        })
    }
    # Try to access tenant-xyz resource
    response = client.get("/api/bia/processes/1?tenant_id=tenant-xyz", headers=headers)
    assert response.status_code == 403
```

---

## Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| 401 Unauthorized | Missing/invalid JWT | Check Authorization header format |
| 403 Forbidden - Permission | Missing permission | Request permission from admin |
| 403 Forbidden - Tenant | Tenant mismatch | Ensure tenant_id in JWT matches resource |
| Token expired | JWT exp claim passed | Refresh token or re-authenticate |

### Debug Checklist

1. ✅ Check JWT token is present in Authorization header
2. ✅ Verify JWT format: `Bearer <token>`
3. ✅ Decode JWT and check claims (use jwt.io)
4. ✅ Verify tenant_id in JWT matches requested resource
5. ✅ Check permissions array includes required permission
6. ✅ Verify token hasn't expired (exp claim)

---

## Next Steps

- [API Reference](api_reference.md) - Complete API documentation
- [Integration Guide](integration_guide.md) - Integration patterns
- [Error Handling](error_handling.md) - Error codes and handling
- [Postman Collection](postman_collection.json) - Pre-configured API tests
