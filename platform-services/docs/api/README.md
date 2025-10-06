# BCM Platform API Documentation

Complete API documentation for the ISO 22301:2019 compliant Business Continuity Management Platform.

## 📚 Documentation Files

### Main Documentation Portal
- **[index.html](index.html)** - Main documentation portal (open in browser)

### Service Documentation
1. **BIA Service (Port 8012)** - ISO 22301 Clause 8.2.2
   - Enhanced OpenAPI: http://localhost:8012/docs
   - Service documentation with examples and schemas

2. **Compliance Service (Port 8014)** - ISO 22301 Clauses 9.2, 10.1, 10.2
   - Enhanced OpenAPI: http://localhost:8014/docs
   - RCA methods documentation (5 Whys, Fishbone, Fault Tree)

3. **Planning Service (Port 8011)** - ISO 22301 Clause 8.3
   - Enhanced OpenAPI: http://localhost:8011/docs
   - Financial modeling examples (NPV, ROI, Payback)

4. **Plans Service (Port 8023)** - ISO 22301 Clause 8.4
   - Enhanced OpenAPI: http://localhost:8023/docs
   - Procedure dependency workflows

### Authentication & Security
- **[authentication.md](authentication.md)** - JWT authentication, RBAC, tenant isolation

### Integration & Workflows
- **[workflows.md](workflows.md)** - Cross-service workflows with sequence diagrams
  - BIA → Strategy → Plan workflow
  - Audit → Gap → NC → CAPA → Improvement workflow
  - Plan activation workflow
  - Testing & exercise workflow

### API Reference
- **[postman_collection.json](postman_collection.json)** - Complete Postman collection
  - All 4 services
  - Pre-configured variables
  - Sample requests with test data

### Code Examples

#### Python Examples
- **[examples/python/create_bia_process.py](examples/python/create_bia_process.py)** - Create comprehensive BIA process
- **[examples/python/complete_audit_lifecycle.py](examples/python/complete_audit_lifecycle.py)** - Full audit → NC → RCA → CAPA workflow

#### cURL Examples
- **[examples/curl/bia_examples.sh](examples/curl/bia_examples.sh)** - All BIA endpoints with examples

## 🚀 Quick Start

### 1. View Documentation Portal
Open in browser:
```bash
open docs/api/index.html
```

### 2. Import Postman Collection
1. Open Postman
2. Import `postman_collection.json`
3. Set variables: `base_url`, `tenant_id`, `user_id`
4. Start testing APIs

### 3. Run Python Examples
```bash
# Install dependencies
pip install requests

# Run BIA example
python examples/python/create_bia_process.py

# Run audit lifecycle example
python examples/python/complete_audit_lifecycle.py
```

### 4. Run cURL Examples
```bash
# Make executable
chmod +x examples/curl/bia_examples.sh

# Run all BIA examples
./examples/curl/bia_examples.sh
```

## 🔐 Authentication

### Development Mode (X-Dev-User Header)
```bash
curl -H 'X-Dev-User: {"sub":"user-123","tenant_id":"tenant-abc","permissions":["BIA_VIEW"]}' \
     http://localhost:8012/api/bia/processes
```

### Production Mode (JWT Bearer Token)
```bash
JWT_TOKEN="your_jwt_token_here"
curl -H "Authorization: Bearer $JWT_TOKEN" \
     http://localhost:8012/api/bia/processes
```

## 📊 Services Overview

| Service | Port | ISO Clause | Endpoints | Key Features |
|---------|------|------------|-----------|--------------|
| **BIA** | 8012 | 8.2.2 | 16 | AI-powered RTO suggestions, bulk operations, dependency mapping |
| **Compliance** | 8014 | 9.2, 10.1, 10.2 | 40+ | RCA (3 methods), audit management, CAPA tracking |
| **Planning** | 8011 | 8.3 | 8 | NPV/ROI calculations, strategy workflow, cost-benefit analysis |
| **Plans** | 8023 | 8.4 | 25+ | Procedure dependencies, activation tracking, contact lists |

## 📖 API Documentation Structure

### OpenAPI Enhancements (in each service's main.py)

All services now include:
- ✅ Comprehensive descriptions with examples
- ✅ Request/response schemas with examples
- ✅ Error response documentation
- ✅ Authentication requirements
- ✅ ISO 22301 compliance mapping
- ✅ Workflow state machines
- ✅ OpenAPI tags for organization

### Example: BIA Service OpenAPI Features

**Enhanced Description:**
- Core features overview
- 16 API endpoints listed by category
- Authentication & authorization details
- ISO 22301 Clause 8.2.2 compliance checklist
- Request/response examples in Swagger UI
- Error codes documentation

**OpenAPI Tags:**
- BIA - Process management
- AI Analysis - AI-powered features
- Bulk Operations - High-performance bulk ops
- Reporting - Reports and analytics

### Example: Compliance Service OpenAPI Features

**RCA Method Documentation:**
- 5 Whys method with example
- Fishbone (Ishikawa) diagram with 6M categories
- Fault Tree Analysis with probability calculations

**Workflow State Machine:**
```
IDENTIFIED → RCA_IN_PROGRESS → CORRECTIVE_ACTION → VERIFICATION → CLOSED
                                                  ↓
                                              REOPENED
```

## 🔗 Integration Patterns

### Event-Driven Architecture
Services communicate via EventBus (RabbitMQ):
- `bia.analysis.completed` → triggers strategy creation
- `planning.strategy.approved` → enables plan creation
- `plans.activation.started` → incident response
- `compliance.audit.completed` → gap analysis

### Cross-Service Workflows
1. **BIA → Strategy → Plan**: Complete BC lifecycle
2. **Audit → NC → RCA → CAPA**: Compliance improvement
3. **Plan Activation**: Real incident response
4. **Exercise → Review → Improve**: Continuous improvement

## 📝 Documentation Coverage

### ✅ Completed Documentation

1. **OpenAPI Specs Enhanced** (4 services)
   - BIA Service with AI analysis examples
   - Compliance Service with RCA templates
   - Planning Service with financial calculations
   - Plans Service with dependency workflows

2. **API Documentation Portal** (index.html)
   - Service overview cards
   - Quick start guide
   - Authentication examples
   - Resource links

3. **Postman Collection** (postman_collection.json)
   - All 4 services
   - 50+ pre-configured requests
   - Environment variables
   - Dev mode authentication

4. **Authentication Guide** (authentication.md)
   - JWT structure and validation
   - RBAC permissions by service
   - Tenant isolation model
   - Security best practices
   - Code examples (Python, JS, cURL)

5. **Workflow Documentation** (workflows.md)
   - 5 complete workflows with sequence diagrams
   - State machines
   - Integration points
   - Event catalog

6. **Code Examples**
   - Python: BIA creation, audit lifecycle
   - cURL: Complete BIA examples
   - All examples with syntax validation

## 🎯 Key Features Documented

### BIA Service
- 16 API endpoints
- AI-powered RTO/RPO suggestions
- Bulk operations (create/update/delete)
- Dependency discovery
- Multi-industry support (Healthcare, Finance, IT, etc.)
- WHO tier classification
- Financial impact analysis (1 hour to 1 month)

### Compliance Service
- 40+ API endpoints
- 3 RCA methods (5 Whys, Fishbone, Fault Tree)
- Internal audit management (ISO 9.2)
- Nonconformity lifecycle (ISO 10.1)
- CAPA tracking
- Improvement initiatives (ISO 10.2)
- Workflow state machines

### Planning Service
- 8 API endpoints
- Cost-benefit analysis (NPV, ROI, Payback)
- Strategy approval workflow
- Financial modeling
- Resource planning

### Plans Service
- 25+ API endpoints
- Procedure dependency graphs
- Plan activation tracking
- Contact list management (ISO 8.4.3)
- Review and maintenance
- Version control

## 🔍 Error Handling

Standardized across all services:
- `400` - Validation error
- `401` - Unauthorized (missing/invalid JWT)
- `403` - Forbidden (tenant mismatch or permission denied)
- `404` - Resource not found
- `409` - Conflict (invalid state transition)
- `422` - Business rule violation
- `500` - Internal server error

## 📊 API Coverage Summary

| Service | Total Endpoints | Documented | Examples | Tests in Postman |
|---------|----------------|------------|----------|------------------|
| BIA | 16 | ✅ 16 | ✅ 13 | ✅ 12 |
| Compliance | 40+ | ✅ 40+ | ✅ 10 | ✅ 6 |
| Planning | 8 | ✅ 8 | ✅ 5 | ✅ 5 |
| Plans | 25+ | ✅ 25+ | ✅ 8 | ✅ 5 |
| **Total** | **89+** | **✅ 89+** | **✅ 36** | **✅ 28** |

## 🛠️ Next Steps

### For Developers
1. Import Postman collection
2. Review service-specific documentation
3. Run Python examples
4. Explore OpenAPI docs at /docs endpoints

### For Integrators
1. Read authentication guide
2. Review workflows documentation
3. Check integration patterns
4. Test with Postman collection

### For QA/Testing
1. Use Postman collection for API testing
2. Validate error scenarios
3. Test workflow state machines
4. Verify tenant isolation

## 📞 Support

- **Swagger UI**: Access at `http://localhost:<port>/docs`
- **ReDoc**: Access at `http://localhost:<port>/redoc`
- **Health Checks**: `http://localhost:<port>/health`

## 🔄 Version Information

- **API Version**: 1.0.0
- **ISO 22301 Version**: 2019
- **Documentation Version**: 1.0
- **Last Updated**: 2024-10-03

---

**Generated with comprehensive API documentation for ISO 22301:2019 BCM Platform**
