# Moodle LMS Integration for BCM Platform

Complete integration between Moodle LMS and the BCM Platform for comprehensive training, competency management, and certification tracking aligned with ISO 22301 Business Continuity Management standards.

## 🏗️ Architecture

```
BCM Platform (Odoo) ←→ Moodle Bridge Service ←→ Moodle LMS + PostgreSQL
                    ←→ Webhook Receiver      ←→ Redis + Elasticsearch
```

## 🚀 Features

### ✅ Training Management Integration
- **Automatic course creation** from BCM training programs
- **User enrollment** with BCM-specific roles and permissions
- **Multi-tenant isolation** through company-based segregation
- **Competency framework** aligned with ISO 22301 requirements
- **Certification tracking** with automated badge issuance

### ✅ Learning Analytics Integration
- **Real-time progress tracking** synced to BCM Platform
- **Completion status** updates for compliance reporting
- **Grade synchronization** for competency assessments
- **Training hours** tracking for regulatory compliance
- **Performance analytics** by department and role

### ✅ Real-time Webhooks
- **Course completion** notifications to BCM Platform
- **Enrollment tracking** for audit trails
- **Competency achievement** updates
- **Certificate issuance** notifications
- **Grade updates** for continuous assessment

### ✅ BCM-Specific Enhancements
- **ISO 22301 competency framework** with 8 core areas
- **BCM role mapping** (Coordinator, Team Leader, Member, Stakeholder)
- **Department-based training** assignments and tracking
- **Exercise integration** for tabletop and simulation training
- **Multi-language support** for international compliance

## 📦 Components

### 1. Moodle Client (`moodle_client.py`)
- Python client library for Moodle Web Services API
- BCM-specific user and course management
- Competency framework creation and management
- Grade and completion tracking

### 2. Bridge Service (`bridge_service.py`)
- FastAPI service providing REST endpoints
- Handles user ↔ course synchronization
- Background task processing for scalability
- Metrics and health monitoring

### 3. Webhook Handler (`webhooks.py`)
- Receives real-time updates from Moodle
- Processes completion, enrollment, and competency events
- Syncs changes back to BCM Platform
- Secure webhook verification with HMAC

### 4. Docker Stack (`docker-compose.moodle.yml`)
- Complete Moodle 4.3 deployment
- PostgreSQL + Redis backends
- Elasticsearch for global search
- Integration services with health checks

## 🔧 API Endpoints

### Bridge Service (Port 8092)

#### Create BCM User
```bash
POST /api/v1/user/create
Authorization: Bearer <bridge-api-key>

{
  "login": "john.doe",
  "first_name": "John",
  "last_name": "Doe",
  "email": "john.doe@company.com",
  "company_id": "hospital-001"
}
```

#### Create Training Course
```bash
POST /api/v1/training/create
Authorization: Bearer <bridge-api-key>

{
  "name": "ISO 22301 Foundation Training",
  "code": "ISO22301-FOUND",
  "description": "Foundational BCM training",
  "company_id": "hospital-001"
}
```

## 📊 BCM Competency Framework

### Core Areas (ISO 22301)
1. **BCM Policy and Strategy**
2. **Risk Assessment and BIA** 
3. **Business Continuity Planning**
4. **Incident Response Management**
5. **Crisis Communications**
6. **Exercise and Testing**
7. **Program Management**
8. **Regulatory Compliance**

## 🛠️ Setup

```bash
# Deploy Moodle stack
docker-compose -f docker-compose.moodle.yml up -d

# Check services
docker-compose -f docker-compose.moodle.yml ps

# Access Moodle at http://localhost:8080
# Bridge service at http://localhost:8092
# Webhook receiver at http://localhost:8093
```

## 📚 Resources

- [Moodle Web Services](https://docs.moodle.org/dev/Web_services)
- [ISO 22301:2019](https://www.iso.org/standard/75106.html)
- [BCM Platform API](../../../docs/api/)
