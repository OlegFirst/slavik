# BCM Document Processor

AI-powered document processing and analysis microservice for BCM Platform, providing intelligent extraction, classification, and compliance analysis of business continuity documentation.

## 🏗️ Architecture

```
BCM Platform → Document Processor → AI Analysis Engine
     ↓              ↓                    ↓
Document Upload → Text Extraction → NLP Processing → Compliance Analysis
     ↓              ↓                    ↓                 ↓
  Metadata → Structured Content → Entity Recognition → ISO 22301 Mapping
```

## 🚀 Features

### ✅ Multi-Format Document Processing
- **PDF documents** - Text and structure extraction with PyMuPDF
- **Word documents** - DOCX/DOC processing with table extraction
- **Excel files** - Spreadsheet data analysis and conversion
- **Images** - OCR text extraction with Tesseract
- **Plain text** - CSV, TXT, and structured text formats

### ✅ AI-Powered Analysis
- **Named Entity Recognition** - Extract people, organizations, locations
- **Key phrase extraction** - TF-IDF based important terms identification
- **Text summarization** - AI-generated document summaries
- **Topic classification** - Automatic BCM category assignment
- **Language detection** - Multi-language document support

### ✅ BCM-Specific Intelligence
- **ISO 22301 clause mapping** - Automatic standard compliance analysis
- **Risk indicator extraction** - Threat and vulnerability identification
- **Stakeholder analysis** - Key participant identification
- **Process mapping** - Business process reference extraction
- **Compliance scoring** - Automated BCM framework assessment

### ✅ Document Management
- **Metadata extraction** - File properties and structure analysis
- **Version control** - Document change tracking
- **Search capabilities** - Full-text and semantic search
- **Batch processing** - Multiple document handling
- **Real-time processing** - Immediate analysis results

## 📦 Components

### 1. Core Processor (`document_processor.py`)
- Multi-format document parsing and extraction
- AI-powered content analysis and classification
- BCM-specific pattern recognition and mapping
- REST API for document upload and analysis

### 2. NLP Engine
- SpaCy-based named entity recognition
- OpenAI integration for advanced summarization
- Custom BCM vocabulary and pattern matching
- Topic modeling and classification

### 3. Storage Layer
- PostgreSQL for document metadata and analysis results
- Redis for caching and task queue management
- Optional MinIO for scalable document storage
- Optional Elasticsearch for advanced search

### 4. Docker Stack
- Containerized deployment with all dependencies
- Scalable worker processes for heavy processing
- Optional monitoring and management interfaces
- Production-ready with health checks

## 🛠️ Setup & Deployment

### Prerequisites
- Docker & Docker Compose
- 4GB+ RAM (for AI models)
- OpenAI API key (optional, for advanced features)

### 1. Environment Configuration
```bash
# Copy and configure environment
cp .env.example .env

# Required variables
DOCUMENT_PROCESSOR_API_KEY=your_secure_api_key
DOC_PROCESSOR_DB_PASSWORD=secure_db_password
DOC_PROCESSOR_REDIS_PASSWORD=secure_redis_password
BCM_API_KEY=your_bcm_platform_api_key

# Optional AI features
OPENAI_API_KEY=your_openai_api_key
HUGGINGFACE_API_KEY=your_huggingface_key
```

### 2. Deploy Document Processor
```bash
# Start core service
docker-compose up -d

# Start with storage service
docker-compose --profile storage up -d

# Start with search capabilities
docker-compose --profile search up -d

# Start with worker and monitoring
docker-compose --profile worker --profile monitor up -d
```

### 3. Verify Deployment
```bash
# Check service health
curl http://localhost:8002/health

# Test document processing
curl -X POST -F "file=@test.pdf" \
  -H "Authorization: Bearer your_api_key" \
  http://localhost:8002/api/v1/documents/upload
```

## 🔧 API Usage

### Upload Document
```bash
POST /api/v1/documents/upload
Authorization: Bearer <api-key>
Content-Type: multipart/form-data

Form Data:
- file: document_file
- company_id: hospital-001
- document_type: policy (optional)
```

### Get Processing Status
```bash
GET /api/v1/documents/{document_id}/status
Authorization: Bearer <api-key>

Response:
{
  "document_id": "abc123...",
  "status": "processed",
  "processed_date": "2024-01-15T10:30:00Z",
  "analysis": {
    "bcm_category": "policy",
    "iso22301_clauses": ["4.1", "5.2", "6.1"],
    "compliance_score": 0.85,
    "key_phrases": ["business continuity", "risk management"]
  }
}
```

### Search Documents
```bash
POST /api/v1/documents/search
Authorization: Bearer <api-key>

{
  "query": "business continuity policy",
  "company_id": "hospital-001",
  "document_types": ["policy", "procedure"],
  "limit": 10
}
```

### Get Document Analysis
```bash
GET /api/v1/documents/{document_id}/analysis
Authorization: Bearer <api-key>

Response:
{
  "document_id": "abc123...",
  "bcm_analysis": {
    "category": "business_continuity_plan",
    "iso22301_clauses": ["8.2", "8.3", "8.4"],
    "risk_indicators": [
      {"indicator": "system_failure", "frequency": 5, "severity": "high"}
    ],
    "compliance_score": 0.92,
    "recommendations": [
      "Consider adding more detailed recovery procedures",
      "Include stakeholder communication plan"
    ]
  }
}
```

### Compare Documents
```bash
POST /api/v1/documents/compare
Authorization: Bearer <api-key>

{
  "document_id_1": "abc123...",
  "document_id_2": "def456...",
  "comparison_type": "compliance"
}
```

## 📊 Supported Document Types

### Office Documents
- **PDF** - Full text and structure extraction
- **DOCX/DOC** - Microsoft Word documents with tables
- **XLSX/XLS** - Excel spreadsheets with multiple sheets
- **PPT/PPTX** - PowerPoint presentations (via textract)

### Text Formats
- **TXT** - Plain text documents
- **CSV** - Comma-separated values
- **RTF** - Rich Text Format
- **HTML** - Web documents

### Images
- **PNG/JPG/JPEG** - OCR text extraction
- **TIFF** - Multi-page image documents
- **BMP/GIF** - Basic image formats

## 🧠 AI Analysis Capabilities

### Named Entity Recognition
- **People** - Authors, stakeholders, contacts
- **Organizations** - Companies, departments, vendors
- **Locations** - Facilities, sites, geographic references
- **Dates/Times** - Important deadlines and schedules
- **Technical Terms** - BCM-specific terminology

### BCM Classification
```json
{
  "document_categories": {
    "policy": ["policy", "governance", "framework"],
    "procedure": ["procedure", "process", "workflow"],
    "plan": ["plan", "strategy", "continuity", "recovery"],
    "risk_assessment": ["risk", "threat", "vulnerability"],
    "bia": ["business impact", "critical", "dependencies"],
    "exercise": ["exercise", "drill", "test", "simulation"]
  }
}
```

### ISO 22301 Mapping
- **Clause 4** - Context of the organization
- **Clause 5** - Leadership and commitment
- **Clause 6** - Planning and risk assessment
- **Clause 7** - Support and resources
- **Clause 8** - Operation and BIA
- **Clause 9** - Performance evaluation
- **Clause 10** - Improvement actions

### Compliance Scoring
```python
compliance_factors = {
    "iso_coverage": 0.4,      # ISO 22301 clause coverage
    "bcm_terminology": 0.3,   # BCM-specific language usage
    "risk_content": 0.2,      # Risk management elements
    "structure_quality": 0.1  # Document organization
}
```

## 📈 Performance & Scaling

### Processing Capabilities
- **Small documents** (<1MB): ~2-5 seconds
- **Medium documents** (1-10MB): ~10-30 seconds
- **Large documents** (>10MB): ~30-120 seconds
- **Batch processing**: 10-50 documents/minute

### Resource Requirements
- **Minimum**: 2GB RAM, 1 CPU core
- **Recommended**: 4GB RAM, 2 CPU cores
- **High-volume**: 8GB RAM, 4 CPU cores
- **Storage**: 50GB for models and cache

### Scaling Options
- **Horizontal scaling** with multiple worker processes
- **Load balancing** across processor instances
- **Distributed storage** with MinIO or S3
- **Search scaling** with Elasticsearch cluster

## 🔐 Security & Privacy

### Data Protection
- **Multi-tenant isolation** by company ID
- **Encrypted storage** for sensitive documents
- **Secure API authentication** with bearer tokens
- **Audit logging** for all processing activities

### Privacy Controls
- **Data retention** policies and automatic cleanup
- **PII detection** and masking capabilities
- **Secure deletion** of processed documents
- **GDPR compliance** features

## 🧪 Testing & Quality

### Unit Tests
```bash
# Test document processors
pytest tests/unit/test_document_processor.py

# Test NLP analysis
pytest tests/unit/test_nlp_analysis.py

# Test BCM classification
pytest tests/unit/test_bcm_analysis.py
```

### Integration Tests
```bash
# Test end-to-end processing
pytest tests/integration/test_document_workflow.py

# Test API endpoints
pytest tests/integration/test_api_endpoints.py
```

### Performance Tests
```bash
# Test processing speed
pytest tests/performance/test_processing_speed.py

# Test concurrent processing
pytest tests/performance/test_concurrent_processing.py
```

## 🔧 Troubleshooting

### Common Issues

#### OCR Processing Failures
```bash
# Check Tesseract installation
docker exec bcm-document-processor tesseract --version

# Test OCR on sample image
docker exec bcm-document-processor tesseract /app/test.png stdout
```

#### Memory Issues
```bash
# Check memory usage
docker stats bcm-document-processor

# Increase memory limits in docker-compose.yml
deploy:
  resources:
    limits:
      memory: 6G
```

#### Model Loading Problems
```bash
# Download SpaCy model manually
docker exec bcm-document-processor python -m spacy download en_core_web_sm

# Check model availability
docker exec bcm-document-processor python -c "import spacy; spacy.load('en_core_web_sm')"
```

#### Database Connection Issues
```bash
# Check PostgreSQL connectivity
docker exec bcm-doc-postgres pg_isready -U docprocessor

# Test Redis connection
docker exec bcm-doc-redis redis-cli ping
```

## 🚀 Production Deployment

### High Availability Setup
- **Multiple processor instances** behind load balancer
- **Database clustering** with read replicas
- **Redis Cluster** for distributed caching
- **Object storage** for document persistence

### Monitoring & Alerting
- **Processing metrics** - throughput, latency, errors
- **Resource monitoring** - CPU, memory, disk usage
- **Queue monitoring** - processing backlog and delays
- **Quality metrics** - analysis accuracy and confidence

### Backup & Recovery
- **Database backups** with point-in-time recovery
- **Document storage** backups and versioning
- **Model artifacts** backup and restoration
- **Configuration management** with version control

---

## 📚 Additional Resources

- [SpaCy NLP Documentation](https://spacy.io/usage)
- [OpenAI API Guide](https://platform.openai.com/docs)
- [PyMuPDF Documentation](https://pymupdf.readthedocs.io/)
- [BCM Document Standards](../../../docs/standards/)
