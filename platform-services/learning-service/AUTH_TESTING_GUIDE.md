# JWT Authentication Testing Guide

## Overview
JWT authentication has been successfully implemented for the Learning Service. All 26 endpoints (20 in routes.py + 6 in analytics.py) are now protected with JWT authentication.

## Authentication Endpoints

### 1. Login to Get JWT Token

**Endpoint:** `POST /auth/token`

**Available Test Users:**

#### Admin User
```bash
curl -X POST "http://localhost:8003/auth/token" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```
- **Roles:** admin, bcm_manager
- **Tenant:** tenant_001
- **User ID:** admin_user_001

#### Manager User
```bash
curl -X POST "http://localhost:8003/auth/token" \
  -H "Content-Type: application/json" \
  -d '{"username": "manager", "password": "manager123"}'
```
- **Roles:** manager
- **Tenant:** tenant_001
- **User ID:** manager_user_001

#### Regular User
```bash
curl -X POST "http://localhost:8003/auth/token" \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "password": "user123"}'
```
- **Roles:** user
- **Tenant:** tenant_001
- **User ID:** regular_user_001

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

## Testing Protected Endpoints

### 2. Use Token in Requests

Save the token from the login response and use it in subsequent requests:

```bash
# Set token variable
TOKEN="your_token_here"

# Example: List Programs (Authenticated - All Users)
curl -X GET "http://localhost:8003/api/v1/learning/programs" \
  -H "Authorization: Bearer $TOKEN"

# Example: Create Program (Admin/BCM Manager Only)
curl -X POST "http://localhost:8003/api/v1/learning/programs" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "tenant_001",
    "program_code": "BCM-101",
    "program_name": "BCM Fundamentals",
    "description": "Introduction to Business Continuity Management",
    "program_type": "certification",
    "iso_clause": "7.2"
  }'

# Example: Get Training Metrics (Authenticated - All Users)
curl -X GET "http://localhost:8003/api/v1/learning/analytics/metrics" \
  -H "Authorization: Bearer $TOKEN"
```

## Protected Endpoints Summary

### Routes.py (20 endpoints)

#### Training Programs (6 endpoints)
1. `POST /programs` - **Admin/BCM Manager only**
2. `GET /programs/{program_id}` - Authenticated users
3. `PATCH /programs/{program_id}` - **Admin/BCM Manager only**
4. `POST /programs/{program_id}/publish` - **Admin/BCM Manager only**
5. `POST /programs/{program_id}/archive` - **Admin/BCM Manager only**
6. `GET /programs` - Authenticated users

#### Enrollments (10 endpoints)
7. `POST /enrollments` - Authenticated users
8. `GET /enrollments/{enrollment_id}` - Authenticated users
9. `POST /enrollments/{enrollment_id}/submit` - Authenticated users
10. `POST /enrollments/{enrollment_id}/approve` - **Admin/Manager only**
11. `POST /enrollments/{enrollment_id}/start` - Authenticated users
12. `PATCH /enrollments/{enrollment_id}/progress` - Authenticated users
13. `POST /enrollments/{enrollment_id}/complete` - Authenticated users
14. `POST /enrollments/{enrollment_id}/assess` - Authenticated users
15. `POST /enrollments/{enrollment_id}/certify` - Authenticated users
16. `GET /persons/{person_id}/enrollments` - Authenticated users

#### Gamification (4 endpoints)
17. `GET /persons/{person_id}/achievements` - Authenticated users
18. `GET /persons/{person_id}/points` - Authenticated users
19. `GET /leaderboard` - Authenticated users
20. `GET /persons/{person_id}/rank` - Authenticated users

### Analytics.py (6 endpoints)
21. `GET /analytics/metrics` - Authenticated users
22. `GET /analytics/programs/performance` - Authenticated users
23. `GET /analytics/departments/metrics` - Authenticated users
24. `GET /analytics/learners/{person_id}/profile` - Authenticated users
25. `GET /analytics/certifications/expiring` - Authenticated users
26. `GET /analytics/gamification/metrics` - Authenticated users

## Role-Based Access Control

### Admin/BCM Manager
Can access ALL endpoints, including:
- Create, update, publish, archive programs
- Approve enrollments
- All read operations

### Manager
Can access:
- All read operations
- Approve enrollments
- Cannot create/modify programs

### Regular User
Can access:
- All read operations
- Create and manage their own enrollments
- Cannot approve enrollments or manage programs

## Error Responses

### 401 Unauthorized (Missing or Invalid Token)
```json
{
  "detail": "Could not validate credentials: ..."
}
```

### 403 Forbidden (Insufficient Permissions)
```json
{
  "detail": "Access forbidden. Required roles: admin, bcm_manager. User roles: user"
}
```

## Complete Test Workflow

```bash
# 1. Login as admin
TOKEN=$(curl -s -X POST "http://localhost:8003/auth/token" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}' \
  | jq -r '.access_token')

# 2. Create a training program (admin only)
curl -X POST "http://localhost:8003/api/v1/learning/programs" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "tenant_001",
    "program_code": "TEST-001",
    "program_name": "Test Program",
    "description": "Test",
    "program_type": "awareness",
    "iso_clause": "7.2"
  }'

# 3. List programs (all authenticated users)
curl -X GET "http://localhost:8003/api/v1/learning/programs" \
  -H "Authorization: Bearer $TOKEN"

# 4. Get analytics (all authenticated users)
curl -X GET "http://localhost:8003/api/v1/learning/analytics/metrics" \
  -H "Authorization: Bearer $TOKEN"

# 5. Test as regular user (should fail for admin endpoints)
USER_TOKEN=$(curl -s -X POST "http://localhost:8003/auth/token" \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "password": "user123"}' \
  | jq -r '.access_token')

# This should return 403 Forbidden
curl -X POST "http://localhost:8003/api/v1/learning/programs" \
  -H "Authorization: Bearer $USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "tenant_001",
    "program_code": "TEST-002",
    "program_name": "Test",
    "description": "Test",
    "program_type": "awareness",
    "iso_clause": "7.2"
  }'
```

## Key Features

1. **Tenant Isolation**: `tenant_id` is automatically extracted from JWT token, preventing cross-tenant access
2. **Role-Based Access**: Different endpoints require different roles
3. **Token Expiration**: Tokens expire after 24 hours by default
4. **Secure**: Uses HS256 algorithm with secret key
5. **Clean Architecture**: All business logic preserved, authentication added as middleware layer

## Installation

Install required dependencies:
```bash
cd /Users/MD/AI-Platform-ISO/platform-services/learning-service
pip install -r requirements-auth.txt
```

## Environment Variables

Set the JWT secret key (optional, defaults to development key):
```bash
export JWT_SECRET_KEY="your-super-secret-key-change-in-production"
```
