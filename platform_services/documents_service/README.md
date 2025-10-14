# Documents Service - Production

**ISO 22301 Clause 7.5 - Documented Information Management**

Production-ready microservice for comprehensive document lifecycle management with AI/NLP capabilities, approval workflows, and retention policies.

## Overview

This service provides enterprise-grade document management with:

- **Document Lifecycle Management**: DRAFT → REVIEW → APPROVED → PUBLISHED → ARCHIVED
- **AI/NLP Processing**: Text extraction, auto-classification, entity recognition, summarization
- **Version Control**: Full version history with comparison capabilities
- **Approval Workflows**: Multi-stage approval chains with role-based approvers
- **Retention Policies**: Automated archival and destruction per ISO 22301 and HIPAA
- **Security**: Classification levels, access control, audit logging
- **Event-Driven**: Integration with other BCM platform services

## Architecture

### 4-Tier Architecture

```
documents/
├── models/              # Data layer
│   ├── database.py      # SQLAlchemy models (8 core tables)
│   ├── domain.py        # Pydantic request/response models
│   └── __init__.py
├── repositories/        # Data access layer
│   ├── repository.py    # Database operations (7 repositories)
│   └── __init__.py
├── services/            # Business logic layer
│   ├── document_service.py  # Document operations & processing
│   └── __init__.py
├── api/                 # Presentation layer
│   ├── routes.py        # All API endpoints
│   ├── schemas.py       # Additional schemas
│   └── __init__.py
├── workflows/           # State machines
│   ├── lifecycle_workflow.py
│   ├── approval_workflow.py
│   ├── retention_workflow.py
│   └── __init__.py
├── core/                # AI/NLP processors
│   ├── extractor.py     # DocumentExtractor (PDF, DOCX, Excel, images)
│   ├── classifier.py    # AI document classification
│   ├── analyzer.py      # NLP analysis & summarization
│   ├── comparator.py    # Version comparison
│   └── __init__.py
├── events/              # Event bus integration
│   ├── eventbus.py      # RabbitMQ client
│   ├── publishers.py    # Event publishers
│   ├── handlers.py      # Event handlers
│   └── __init__.py
├── integrations/        # Cross-service integration
│   ├── plans.py         # Plans service integration
│   ├── governance.py    # Governance service integration
│   ├── validation.py    # Validation service integration
│   └── __init__.py
├── config.py            # Configuration (pydantic_settings)
├── main.py              # FastAPI application
└── requirements.txt     # Dependencies
```

## Database Schema

### Core Tables (8)

1. **documents** - Main document entity with lifecycle
2. **document_access** - Complete audit trail
3. **document_shares** - Collaboration and sharing
4. **document_approvals** - Approval workflow tracking
5. **document_tags** - Taxonomy and categorization
6. **document_tag_associations** - Many-to-many tags
7. **document_comparisons** - Version diff tracking
8. **document_retention_policies** - Compliance retention

All tables use `documents` schema with proper indexing.

## Key Features

### 1. Document Lifecycle (ISO 7.5)

**States**: DRAFT → UNDER_REVIEW → APPROVED → PUBLISHED → ARCHIVED → SUPERSEDED/OBSOLETE

**Validations**:
- Submit for review: Requires title, file, owner
- Approve: Requires all approvals complete
- Publish: Must be approved
- Archive: Can archive from most states
- Supersede: Only published documents

### 2. Approval Workflows

**Multi-stage approval chains**:
- Stage 1: Technical Reviewer (48h SLA)
- Stage 2: Quality Assurance (24h SLA)
- Stage 3: Compliance Officer (72h SLA)
- Stage 4: Management (120h SLA)
- Stage 5: Executive (168h SLA)

**Priority calculation** based on:
- Document classification (0-40 points)
- Document type (0-30 points)
- Due date proximity (0-30 points)

### 3. Retention Policies

**ISO 22301 retention periods**:
- Policy: 7 years
- Procedure: 5 years
- Plans: 5 years
- Risk assessments: 7 years
- BIA: 7 years
- Exercise reports: 5 years
- Audit reports: 7 years
- Management reviews: 7 years

**HIPAA compliance**: Minimum 6 years for health-related documents

**Retention phases**:
1. ACTIVE - Document in use
2. ARCHIVED - Moved to archive storage
3. PENDING_DESTRUCTION - Scheduled for destruction
4. DESTROYED - Permanently removed
5. LEGAL_HOLD - Litigation hold applied

### 4. AI/NLP Processing

**DocumentExtractor**:
- PDF text extraction (PyMuPDF, pdfplumber)
- DOCX processing (python-docx)
- Excel processing (openpyxl)
- Image OCR (pytesseract)
- Page count, word count

**DocumentClassifier**:
- Auto-classify document type (policy, procedure, plan, etc.)
- Suggest classification level (public, internal, confidential, etc.)
- Map to ISO 22301 clauses
- Map to BCI GPG practices
- Determine if controlled document
- Determine if requires approval

**DocumentAnalyzer**:
- Named entity recognition (spaCy)
- Key phrase extraction (TF-IDF)
- AI summarization (OpenAI GPT)
- Readability analysis
- ISO compliance analysis

**DocumentComparator**:
- Version comparison with diff
- Similarity scoring
- Track additions, deletions, modifications
- Structural change detection

## API Endpoints

### Document CRUD
- `POST /api/documents/documents` - Create document
- `POST /api/documents/documents/{id}/upload` - Upload file
- `GET /api/documents/documents/{id}` - Get document
- `GET /api/documents/documents/{id}/download` - Download file
- `GET /api/documents/documents` - List documents
- `PATCH /api/documents/documents/{id}` - Update metadata
- `DELETE /api/documents/documents/{id}` - Soft delete

### Lifecycle Workflow
- `POST /api/documents/documents/{id}/workflow/{action}` - Execute workflow action
- `GET /api/documents/documents/{id}/workflow/status` - Get workflow status

### Version Control
- `POST /api/documents/documents/{id}/version` - Create new version
- `GET /api/documents/documents/{id}/versions` - Get all versions
- `POST /api/documents/compare` - Compare two versions

### Sharing & Collaboration
- `POST /api/documents/documents/{id}/share` - Share document
- `GET /api/documents/documents/{id}/shares` - Get shares

### Approval Workflow
- `POST /api/documents/documents/{id}/approvals` - Request approval
- `POST /api/documents/approvals/{id}/respond` - Approve/reject
- `GET /api/documents/documents/{id}/approvals` - Get approvals

### Retention Policies
- `POST /api/documents/retention-policies` - Create policy
- `GET /api/documents/retention-policies` - List policies
- `GET /api/documents/documents/{id}/retention` - Get retention status

### Integrations
- `GET /api/documents/plans/{id}/documents` - Get plan documents
- `GET /api/documents/iso-coverage` - Get ISO clause coverage

### Audit
- `GET /api/documents/documents/{id}/access-log` - Get access log

## Configuration

Environment variables (`.env`):

```env
# Service
SERVICE_NAME=documents
SERVICE_PORT=8024

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/bcm_platform

# Storage
STORAGE_PATH=./storage/documents
MAX_FILE_SIZE=104857600  # 100MB

# EventBus
EVENTBUS_URL=amqp://guest:guest@localhost:5672/

# Orchestrator
ORCHESTRATOR_URL=http://localhost:8002
REGISTER_WITH_ORCHESTRATOR=true

# AI Services
AI_INTELLIGENCE_URL=http://localhost:8000
OPENAI_API_KEY=sk-...

# Retention
DEFAULT_RETENTION_YEARS=7
ARCHIVE_AFTER_DAYS=365
```

## Events

### Published Events
- `document.uploaded` - File uploaded and processed
- `document.approved` - Document approved
- `document.published` - Document published
- `document.archived` - Document archived
- `document.shared` - Document shared
- `document.version.created` - New version created

### Subscribed Events
- `governance.policy.created` - Create policy document
- `governance.policy.updated` - Update policy references
- `plans.plan.created` - Link plan documents
- `plans.plan.updated` - Update plan documents
- `validation.exercise.completed` - Create exercise report

## Integration Points

### Plans Service
- Get all documents for a plan
- Check plan document completeness
- Validate required documents exist

### Governance Service
- Get policy documents
- Get ISO 22301 clause coverage
- Track compliance documents

### Validation Service
- Create exercise reports
- Get validation documents summary
- Link evidence documents

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Install spaCy model
python -m spacy download en_core_web_sm

# Set up database
# Tables will be created automatically on first run

# Create .env file
cp .env.example .env
# Edit .env with your configuration

# Run service
python main.py
```

## Usage

```bash
# Start service
uvicorn main:app --host 0.0.0.0 --port 8024

# Access API documentation
http://localhost:8024/docs

# Health check
curl http://localhost:8024/health
```

## Business Logic Preserved

All business logic from the original 1563-line main.py has been preserved:

✅ **Document Lifecycle** - Full state machine with validation
✅ **Approval Workflows** - Multi-stage chains with priority calculation
✅ **Retention Management** - ISO 22301 and HIPAA compliance
✅ **AI/NLP Processing** - Extraction, classification, analysis, comparison
✅ **Version Control** - History tracking and diff generation
✅ **Access Control** - Classification levels and permissions
✅ **Audit Logging** - Complete access trail
✅ **Event Integration** - Publish/subscribe with other services
✅ **Cross-module Integration** - Plans, Governance, Validation

## No Mocks or Stubs

All mocks and stubs have been removed. The service connects to:

- **Real PostgreSQL database** via SQLAlchemy async
- **Real RabbitMQ EventBus** via aio-pika
- **Real file storage** on disk
- **Real AI services** (OpenAI API)
- **Real service integrations** via HTTP

## Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test
pytest tests/test_lifecycle.py
```

## Performance

- **Async database** operations with connection pooling
- **Background processing** for AI/NLP operations
- **File streaming** for large documents
- **Caching** for frequently accessed documents
- **Event-driven** for cross-service communication

## Security

- **Classification levels**: Public, Internal, Confidential, Restricted, Highly Restricted
- **Access control**: Role-based permissions
- **Audit logging**: Complete access trail
- **File integrity**: SHA-256 hash verification
- **Secure sharing**: Time-limited access tokens

## ISO 22301 Compliance

This service implements ISO 22301:2019 requirements:

- **7.5.1** General requirements for documented information
- **7.5.2** Creating and updating documents
- **7.5.3** Control of documented information
- **7.5.3 a)** Availability and suitability for use
- **7.5.3 b)** Adequate protection
- **7.5.3 c)** Distribution, access, retrieval
- **7.5.3 d)** Storage and preservation
- **7.5.3 e)** Control of changes
- **7.5.3 f)** Retention and disposition

## Support

For issues or questions, contact the BCM Platform team.

---

**Version**: 1.0.0
**Port**: 8024
**Schema**: documents
**ISO Clause**: 7.5
