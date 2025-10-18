# JWT Authentication - Planning Service

## Overview

The Planning Service now implements JWT token-based authentication to secure all API endpoints. This ensures that only authenticated users can access the service and enforces tenant isolation.

## Files Created

### 1. `auth/__init__.py`
- Module initialization
- Exports `UserContext` and `get_current_user`

### 2. `auth/models.py`
- `UserContext`: Pydantic model for user information extracted from JWT
- Fields: `user_id`, `tenant_id`, `email`, `roles`, `is_superadmin`

### 3. `auth/dependencies.py`
- `get_current_user()`: FastAPI dependency that validates JWT tokens
- `get_current_user_optional()`: Optional authentication (doesn't raise errors)
- Development mode bypass for easier testing

## Files Modified

### 1. `config.py`
Added JWT configuration settings:
- `JWT_PUBLIC_KEY`: RSA public key for token validation (RS256)
- `JWT_ALGORITHM`: Algorithm used (default: RS256)
- `JWT_AUDIENCE`: Expected audience in tokens
- `JWT_SECRET`: Fallback for HS256 symmetric keys

### 2. `api/routes.py`
Updated all endpoints to:
- Require authentication via `current_user: UserContext = Depends(get_current_user)`
- Remove manual `created_by`, `updated_by`, `tenant_id` query parameters
- Extract user info from JWT token instead
- Enforce tenant isolation (users can only access their tenant's data)

## Authentication Flow

### Production Mode (JWT Tokens)

```
1. Client requests endpoint with Authorization header
   → Authorization: Bearer <jwt_token>

2. get_current_user() dependency:
   → Extracts token from header
   → Validates signature using JWT_PUBLIC_KEY
   → Checks expiration
   → Verifies audience (if configured)
   → Extracts user claims (user_id, tenant_id, email, roles)

3. Returns UserContext object

4. Endpoint uses UserContext for:
   → created_by/updated_by fields
   → Tenant isolation
   → Role-based authorization (future)
```

### Development Mode (Bypass)

When `JWT_PUBLIC_KEY` is not set or equals `"PLACEHOLDER_DEV_MODE"`:

```
1. Client requests endpoint with dev headers:
   → X-Dev-User: user-123
   → X-Dev-Tenant: tenant-456

2. get_current_user() creates UserContext from headers
   → ⚠️  Logs warning about development mode
   → ⚠️  NEVER use in production!

3. Returns UserContext with dev data
```

## Token Requirements

JWT tokens MUST include these claims:

```json
{
  "sub": "user-unique-id",           // or "user_id"
  "tenant_id": "tenant-unique-id",   // Required for multi-tenancy
  "email": "user@example.com",       // User email
  "roles": ["bcm_manager", "strategy_editor"],  // User roles
  "is_superadmin": false,            // Admin flag
  "exp": 1234567890,                 // Expiration timestamp
  "aud": "bcm-platform"              // Audience (if JWT_AUDIENCE is set)
}
```

## Environment Variables

Add to `.env` file:

```bash
# Production - RSA Public Key (RS256)
JWT_PUBLIC_KEY="-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...
-----END PUBLIC KEY-----"
JWT_ALGORITHM=RS256
JWT_AUDIENCE=bcm-platform

# Development - Use symmetric key (HS256) or dev headers
JWT_PUBLIC_KEY=PLACEHOLDER_DEV_MODE
JWT_SECRET=your-secret-key-change-in-production
```

## API Usage Examples

### Development Mode (Using Headers)

```bash
# Create strategy
curl -X POST http://localhost:8011/strategies/ \
  -H "Content-Type: application/json" \
  -H "X-Dev-User: user-123" \
  -H "X-Dev-Tenant: tenant-456" \
  -d '{
    "name": "Data Center Recovery Strategy",
    "description": "Recovery strategy for primary data center",
    "tenant_id": "tenant-456",
    "strategy_type": "recovery",
    "priority": "high"
  }'

# List strategies (tenant_id comes from token)
curl -X GET http://localhost:8011/strategies/ \
  -H "X-Dev-User: user-123" \
  -H "X-Dev-Tenant: tenant-456"
```

### Production Mode (Using JWT Token)

```bash
# Get token from auth service first
TOKEN=$(curl -X POST http://auth-service/login \
  -d '{"username":"user@example.com","password":"secret"}' | jq -r '.access_token')

# Create strategy
curl -X POST http://localhost:8011/strategies/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "name": "Data Center Recovery Strategy",
    "description": "Recovery strategy for primary data center",
    "tenant_id": "tenant-456",
    "strategy_type": "recovery",
    "priority": "high"
  }'

# List strategies
curl -X GET http://localhost:8011/strategies/ \
  -H "Authorization: Bearer $TOKEN"
```

## Security Features

### 1. Tenant Isolation
- `tenant_id` always extracted from JWT token, not from request
- Users cannot access data from other tenants
- Returns 404 instead of 403 to avoid information leakage

### 2. Token Validation
- Signature verification using public key
- Expiration check
- Audience verification (optional)
- Required claims validation

### 3. Error Handling
- **401 Unauthorized**: Missing or invalid token
- **403 Forbidden**: Valid token but insufficient permissions
- **404 Not Found**: Resource doesn't exist or belongs to another tenant

### 4. Development Safety
- Development mode clearly logged with warnings
- Production mode enforced when JWT_PUBLIC_KEY is set
- No accidental bypass in production

## Testing

Run the test script:

```bash
cd /Users/MD/ISO-22301—копия/services/SERVICES/BCM/planning_service
python3 test_auth.py
```

## Migration from Previous Version

### Before (Insecure)
```python
@router.post("/")
async def create_strategy(
    strategy_data: StrategyCreate,
    created_by: str = Query(...),  # ❌ Client provides this
    tenant_id: str = Query(...),   # ❌ Client provides this
    service: StrategyService = Depends(get_strategy_service)
):
    return await service.create_strategy(strategy_data, created_by)
```

### After (Secure)
```python
@router.post("/")
async def create_strategy(
    strategy_data: StrategyCreate,
    current_user: UserContext = Depends(get_current_user),  # ✅ From JWT
    service: StrategyService = Depends(get_strategy_service)
):
    # ✅ created_by comes from token
    # ✅ tenant_id comes from token
    return await service.create_strategy(strategy_data, current_user.user_id)
```

## Endpoints Protected

All endpoints now require authentication:

- ✅ `POST /strategies/` - Create strategy
- ✅ `GET /strategies/` - List strategies (filtered by tenant)
- ✅ `GET /strategies/{id}` - Get strategy (tenant check)
- ✅ `PUT /strategies/{id}` - Update strategy (tenant check)
- ✅ `DELETE /strategies/{id}` - Delete strategy (tenant check)
- ✅ `POST /strategies/{id}/cost-benefit` - Cost-benefit analysis (tenant check)
- ✅ `POST /strategies/{id}/submit-review` - Submit for review (tenant check)
- ✅ `POST /strategies/{id}/approve` - Approve strategy (tenant check)

## Future Enhancements

1. **Role-Based Access Control (RBAC)**
   - Use `current_user.roles` for permission checks
   - Different roles: viewer, editor, approver, admin

2. **Audit Logging**
   - Log all authenticated actions
   - Track who did what and when

3. **Rate Limiting**
   - Per-user rate limits
   - Per-tenant rate limits

4. **Token Refresh**
   - Support refresh tokens
   - Automatic token renewal

## Troubleshooting

### "Missing authorization header"
- Add `Authorization: Bearer <token>` header
- Or use dev headers: `X-Dev-User` and `X-Dev-Tenant`

### "Invalid or expired token"
- Token has expired - get a new one
- Token signature invalid - check JWT_PUBLIC_KEY
- Wrong algorithm - verify JWT_ALGORITHM matches

### "Invalid token: missing tenant identifier"
- JWT doesn't include `tenant_id` claim
- Update token issuer to include tenant_id

### Development mode not working
- Set `JWT_PUBLIC_KEY=PLACEHOLDER_DEV_MODE` in .env
- Use both `X-Dev-User` and `X-Dev-Tenant` headers

## Support

For issues or questions:
1. Check this README
2. Review `auth/dependencies.py` for implementation details
3. Run `test_auth.py` to verify setup
4. Check service logs for authentication errors
