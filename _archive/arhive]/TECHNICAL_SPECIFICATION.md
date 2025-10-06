# TECHNICAL SPECIFICATION - Services Improvement
Дата: 3 октября 2025

## 🎯 ЦЕЛЬ

Завершить миграцию Validation и Documents сервисов до production-ready состояния, исправив критические пробелы и добавив необходимую функциональность.

**Текущий статус:** 90% Complete
**Целевой статус:** 100% Production-Ready

---

## 📦 SCOPE OF WORK

### Phase 1: Critical Fixes (Week 1)
1. Complete Validation API Routes
2. Create Shared Library
3. Implement Service Layer
4. Fix Database Pooling
5. Add Document Security

### Phase 2: Performance & Security (Week 2)
6. Error Handling
7. Caching Strategy
8. Authentication & Authorization
9. Background Processing
10. Monitoring & Metrics

---

## 🔴 TASK 1: Complete Validation API Routes

### Objective
Implement all 35+ missing API endpoints в Validation Service

### Current State
**File:** `/Users/MD/AI-Platform-ISO/services/validation/api/routes.py`
**Lines 182-193:** Massive TODO list
**Implemented:** 4 endpoints (10%)
**Missing:** 35+ endpoints (90%)

### Source
**Original file:** `/Users/MD/ISO-22301—копия/services/SERVICES/BCM/validation/main.py`
**Lines:** 100-2168 (all endpoint logic)

### Requirements

#### 1.1 KPI Endpoints (10 endpoints)
```python
@router.post("/kpis", response_model=KPIResponse)
async def create_kpi(kpi: KPICreate, db: AsyncSession = Depends(get_db)):
    """Create new KPI definition"""
    # Business logic from original main.py lines 900-950

@router.get("/kpis", response_model=List[KPIResponse])
async def list_kpis(tenant_id: str, category: Optional[KPICategory] = None, db: AsyncSession = Depends(get_db)):
    """List KPIs with filters"""
    # Business logic from original main.py lines 951-1000

@router.get("/kpis/{kpi_id}", response_model=KPIResponse)
async def get_kpi(kpi_id: int, db: AsyncSession = Depends(get_db)):
    """Get KPI by ID"""

@router.patch("/kpis/{kpi_id}", response_model=KPIResponse)
async def update_kpi(kpi_id: int, updates: KPIUpdate, db: AsyncSession = Depends(get_db)):
    """Update KPI"""

@router.post("/kpis/{kpi_id}/measure", response_model=MeasurementResponse)
async def record_measurement(kpi_id: int, measurement: MeasurementCreate, db: AsyncSession = Depends(get_db)):
    """Record KPI measurement"""
    # Calculate status, check thresholds, create alerts

@router.get("/kpis/{kpi_id}/trend")
async def get_kpi_trend(kpi_id: int, period_days: int = 30, db: AsyncSession = Depends(get_db)):
    """Get KPI trend analysis"""
    # Use workflow/kpi_calculations.py::calculate_kpi_trend

@router.get("/kpis/dashboard")
async def get_kpi_dashboard(tenant_id: str, db: AsyncSession = Depends(get_db)):
    """Get KPI dashboard with all metrics"""
    # Use workflow/kpi_calculations.py::get_kpi_summary

@router.post("/kpi/collect-now")
async def trigger_kpi_collection(tenant_id: str, db: AsyncSession = Depends(get_db)):
    """Manually trigger KPI collection"""
    # Call Celery task: tasks/kpi_collector.py

@router.get("/kpi/alerts")
async def get_kpi_alerts(tenant_id: str, status: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    """Get KPI alerts"""

@router.post("/kpi/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: int, db: AsyncSession = Depends(get_db)):
    """Acknowledge KPI alert"""
```

#### 1.2 Audit Endpoints (6 endpoints)
```python
@router.post("/audits", response_model=AuditResponse)
async def create_audit(audit: AuditCreate, db: AsyncSession = Depends(get_db)):
    """Create audit plan"""
    # Business logic from original main.py lines 1400-1450

@router.get("/audits", response_model=List[AuditResponse])
async def list_audits(tenant_id: str, status: Optional[AuditStatus] = None, db: AsyncSession = Depends(get_db)):
    """List audits"""

@router.get("/audits/{audit_id}", response_model=AuditResponse)
async def get_audit(audit_id: int, db: AsyncSession = Depends(get_db)):
    """Get audit details"""

@router.post("/audits/{audit_id}/findings", response_model=FindingResponse)
async def add_finding(audit_id: int, finding: FindingCreate, db: AsyncSession = Depends(get_db)):
    """Add audit finding"""
    # Auto-create CAPA if severity is high

@router.get("/audits/{audit_id}/report")
async def generate_audit_report(audit_id: int, db: AsyncSession = Depends(get_db)):
    """Generate audit report"""

@router.patch("/audits/{audit_id}/close")
async def close_audit(audit_id: int, db: AsyncSession = Depends(get_db)):
    """Close audit"""
    # Validate workflow transition
```

#### 1.3 CAPA Endpoints (5 endpoints)
```python
@router.post("/capa", response_model=CAPAResponse)
async def create_capa(capa: CAPACreate, db: AsyncSession = Depends(get_db)):
    """Create CAPA"""
    # Calculate due_date based on priority
    # Business logic from original main.py lines 1800-1850

@router.get("/capa", response_model=List[CAPAResponse])
async def list_capa(tenant_id: str, status: Optional[CAPAStatus] = None, db: AsyncSession = Depends(get_db)):
    """List CAPAs"""

@router.get("/capa/{capa_id}", response_model=CAPAResponse)
async def get_capa(capa_id: int, db: AsyncSession = Depends(get_db)):
    """Get CAPA details"""

@router.patch("/capa/{capa_id}", response_model=CAPAResponse)
async def update_capa(capa_id: int, updates: CAPAUpdate, db: AsyncSession = Depends(get_db)):
    """Update CAPA"""

@router.post("/capa/{capa_id}/verify")
async def verify_capa(capa_id: int, verification: VerificationCreate, db: AsyncSession = Depends(get_db)):
    """Verify CAPA effectiveness"""
    # Workflow validation: can_verify_capa
```

#### 1.4 Management Review Endpoints (3 endpoints)
```python
@router.post("/management-reviews", response_model=ManagementReviewResponse)
async def create_review(review: ManagementReviewCreate, db: AsyncSession = Depends(get_db)):
    """Create management review"""
    # Business logic from original main.py lines 2100-2150

@router.get("/management-reviews", response_model=List[ManagementReviewResponse])
async def list_reviews(tenant_id: str, db: AsyncSession = Depends(get_db)):
    """List management reviews"""

@router.get("/management-reviews/{review_id}/prepare")
async def auto_prepare_review(review_id: int, db: AsyncSession = Depends(get_db)):
    """Auto-prepare review inputs"""
    # Collect 8 required inputs from all modules:
    # 1. Previous review actions status
    # 2. External/internal issues
    # 3. BCMS performance (KPIs)
    # 4. Feedback from interested parties
    # 5. Audit results
    # 6. Exercise results
    # 7. Nonconformities and CAPAs
    # 8. Opportunities for improvement
```

#### 1.5 Exercise Endpoints (remaining 5)
```python
@router.post("/exercises/{exercise_id}/complete")
async def complete_exercise(exercise_id: int, db: AsyncSession = Depends(get_db)):
    """Complete exercise"""
    # Workflow validation: can_complete_exercise
    # Calculate duration
    # Business logic from original main.py lines 200-250

@router.post("/exercises/{exercise_id}/observations")
async def add_observation(exercise_id: int, observation: ObservationCreate, db: AsyncSession = Depends(get_db)):
    """Add exercise observation"""

@router.get("/exercises/{exercise_id}/report")
async def generate_exercise_report(exercise_id: int, db: AsyncSession = Depends(get_db)):
    """Generate exercise report"""
    # Create document via documents service

@router.post("/scenarios", response_model=ScenarioResponse)
async def create_scenario(scenario: ScenarioCreate, db: AsyncSession = Depends(get_db)):
    """Create exercise scenario"""

@router.get("/scenarios", response_model=List[ScenarioResponse])
async def list_scenarios(tenant_id: str, exercise_type: Optional[ExerciseType] = None, db: AsyncSession = Depends(get_db)):
    """List exercise scenarios"""
```

#### 1.6 Reporting Endpoints (2 endpoints)
```python
@router.get("/reports/performance-summary")
async def get_performance_summary(tenant_id: str, period_start: datetime, period_end: datetime, db: AsyncSession = Depends(get_db)):
    """Get performance summary report"""
    # Aggregate KPIs, exercises, audits, CAPAs

@router.get("/reports/compliance-status")
async def get_compliance_status(tenant_id: str, db: AsyncSession = Depends(get_db)):
    """Get compliance status report"""
    # Calculate compliance scores, ISO clause coverage
```

### Deliverables
- [ ] Updated `/services/validation/api/routes.py` with all endpoints
- [ ] Updated `/services/validation/api/schemas.py` with response models
- [ ] Each endpoint tested and working
- [ ] Documentation comments for each endpoint

### Success Criteria
- All 35+ endpoints implemented
- All endpoints return proper status codes
- Workflow validations applied
- Business logic preserved from original

---

## 🔧 TASK 2: Create Shared Library

### Objective
Create `/shared/` directory with reusable modules для всех сервисов

### Current State
**Directory:** `/Users/MD/AI-Platform-ISO/shared/` - DOES NOT EXIST
**Problem:** Both services reference shared modules that don't exist

### Requirements

#### 2.1 Directory Structure
```
/Users/MD/AI-Platform-ISO/shared/
├── __init__.py
├── database/
│   ├── __init__.py
│   ├── connection.py      # Async connection pool manager
│   ├── session.py         # Session factory
│   └── base.py            # Base SQLAlchemy model
├── eventbus/
│   ├── __init__.py
│   ├── client.py          # RabbitMQ async client
│   ├── publisher.py       # Event publishing
│   └── subscriber.py      # Event subscription
├── auth/
│   ├── __init__.py
│   ├── jwt.py             # JWT token handling
│   ├── middleware.py      # FastAPI auth middleware
│   └── permissions.py     # RBAC implementation
├── cache/
│   ├── __init__.py
│   └── redis_cache.py     # Redis caching with decorator
├── models/
│   ├── __init__.py
│   └── common.py          # Common Pydantic models
├── exceptions/
│   ├── __init__.py
│   └── custom.py          # Custom exception classes
├── utils/
│   ├── __init__.py
│   ├── logging.py         # Structured logging
│   ├── metrics.py         # Prometheus metrics
│   └── validators.py      # Common validators
├── config.py              # Shared configuration
└── requirements.txt       # Shared dependencies
```

#### 2.2 Key Implementations

**shared/database/connection.py:**
```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from typing import AsyncGenerator, Optional

class DatabaseManager:
    """Async database connection manager with pooling"""

    def __init__(self, database_url: str, pool_size: int = 20, max_overflow: int = 10):
        self.engine = create_async_engine(
            database_url,
            echo=False,
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_pre_ping=True,
            pool_recycle=3600,
            future=True
        )

        self.session_factory = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False
        )

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.session_factory() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    async def dispose(self):
        await self.engine.dispose()

# Global instance
_db_manager: Optional[DatabaseManager] = None

def init_database(database_url: str, pool_size: int = 20) -> DatabaseManager:
    global _db_manager
    _db_manager = DatabaseManager(database_url, pool_size)
    return _db_manager

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for database session"""
    async for session in _db_manager.get_session():
        yield session
```

**shared/cache/redis_cache.py:**
```python
import redis.asyncio as redis
from typing import Optional, Any, Callable
import json
from functools import wraps

class RedisCache:
    """Async Redis cache manager"""

    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url)

    async def get(self, key: str) -> Optional[Any]:
        value = await self.redis.get(key)
        if value:
            return json.loads(value)
        return None

    async def set(self, key: str, value: Any, ttl: int = 3600):
        await self.redis.setex(key, ttl, json.dumps(value, default=str))

    async def delete(self, key: str):
        await self.redis.delete(key)

    async def exists(self, key: str) -> bool:
        return await self.redis.exists(key)

    async def close(self):
        await self.redis.close()

# Global instance
_cache: Optional[RedisCache] = None

def init_cache(redis_url: str) -> RedisCache:
    global _cache
    _cache = RedisCache(redis_url)
    return _cache

def cached(ttl: int = 3600, key_prefix: str = ""):
    """Decorator for caching function results"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{key_prefix}:{func.__name__}:{args}:{kwargs}"

            # Try cache
            cached_value = await _cache.get(cache_key)
            if cached_value is not None:
                return cached_value

            # Execute function
            result = await func(*args, **kwargs)

            # Cache result
            await _cache.set(cache_key, result, ttl)

            return result
        return wrapper
    return decorator
```

**shared/auth/jwt.py:**
```python
from datetime import datetime, timedelta
from typing import Optional, Dict
import jwt
from fastapi import HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

class JWTManager:
    """JWT token manager"""

    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm

    def create_token(
        self,
        user_id: str,
        tenant_id: str,
        role: str,
        expires_hours: int = 24
    ) -> str:
        exp = datetime.utcnow() + timedelta(hours=expires_hours)
        payload = {
            "user_id": user_id,
            "tenant_id": tenant_id,
            "role": role,
            "exp": exp,
            "iat": datetime.utcnow()
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def verify_token(self, token: str) -> Dict:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(401, "Token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(401, "Invalid token")

# Global instance
_jwt_manager: Optional[JWTManager] = None

def init_jwt(secret_key: str) -> JWTManager:
    global _jwt_manager
    _jwt_manager = JWTManager(secret_key)
    return _jwt_manager

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict:
    """FastAPI dependency for current user from JWT"""
    token = credentials.credentials
    payload = _jwt_manager.verify_token(token)
    return payload
```

**shared/exceptions/custom.py:**
```python
from fastapi import HTTPException
from typing import Optional, Dict
from datetime import datetime
from pydantic import BaseModel

class ErrorResponse(BaseModel):
    """Standard error response"""
    error_code: str
    message: str
    details: Optional[Dict] = None
    timestamp: datetime

class BCMException(Exception):
    """Base exception for BCM platform"""
    def __init__(self, message: str, code: str = None, details: Dict = None):
        self.message = message
        self.code = code or self.__class__.__name__
        self.details = details
        super().__init__(self.message)

class ValidationException(BCMException):
    """Business validation failed"""
    pass

class ResourceNotFoundException(BCMException):
    """Resource not found"""
    pass

class DuplicateResourceException(BCMException):
    """Resource already exists"""
    pass

class WorkflowException(BCMException):
    """Workflow transition not allowed"""
    pass

class SecurityException(BCMException):
    """Security violation"""
    pass

class PermissionDeniedException(BCMException):
    """User lacks required permission"""
    pass

class ExternalServiceException(BCMException):
    """External service failed"""
    pass
```

**shared/utils/logging.py:**
```python
import logging
import json
from datetime import datetime
from typing import Dict, Any

class StructuredLogger:
    """Structured JSON logger"""

    def __init__(self, service_name: str):
        self.service_name = service_name
        self.logger = logging.getLogger(service_name)

    def log(self, level: str, message: str, **kwargs):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "service": self.service_name,
            "level": level,
            "message": message,
            **kwargs
        }
        self.logger.log(
            getattr(logging, level.upper()),
            json.dumps(log_entry)
        )

    def info(self, message: str, **kwargs):
        self.log("info", message, **kwargs)

    def error(self, message: str, **kwargs):
        self.log("error", message, **kwargs)

    def warning(self, message: str, **kwargs):
        self.log("warning", message, **kwargs)

    def debug(self, message: str, **kwargs):
        self.log("debug", message, **kwargs)
```

### Deliverables
- [ ] Complete `/shared/` directory structure
- [ ] All modules implemented and tested
- [ ] Documentation for each module
- [ ] Example usage in README
- [ ] requirements.txt with dependencies

### Success Criteria
- Both services can import from shared
- Database pooling works
- Caching works
- JWT authentication works
- Tests pass

---

## 🎯 TASK 3: Implement KPI Service

### Objective
Complete `/services/validation/services/kpi_service.py`

### Source
**Original:** `/Users/MD/ISO-22301—копия/services/SERVICES/BCM/validation/main.py`
**Lines:** 900-1400 (KPI logic)

### Requirements

**kpi_service.py structure:**
```python
class KPIService:
    def __init__(self, repository: ValidationRepository):
        self.repo = repository

    async def create_kpi(self, kpi_data: Dict) -> KPIDB:
        """Create new KPI with threshold validation"""
        # 1. Validate thresholds based on performance_direction
        # 2. Check for duplicates
        # 3. Create KPI
        # 4. Publish event

    async def record_measurement(self, kpi_id: int, value: float, measured_by: str) -> KPIMeasurementDB:
        """Record KPI measurement"""
        # 1. Get KPI
        # 2. Create measurement
        # 3. Calculate status (use workflows/kpi_calculations.py)
        # 4. Check thresholds -> create alert if needed
        # 5. Update KPI current_value

    async def get_kpi_trend(self, kpi_id: int, period_days: int = 30):
        """Get KPI trend analysis"""
        # Use workflows/kpi_calculations.py::calculate_kpi_trend

    async def get_dashboard(self, tenant_id: str):
        """Generate KPI dashboard"""
        # Use workflows/kpi_calculations.py::get_kpi_summary

    async def create_alert(self, kpi: KPIDB, value: float, severity: str):
        """Create KPI alert"""
        # 1. Create alert record
        # 2. Send email notification (if enabled)
        # 3. Publish event

    async def acknowledge_alert(self, alert_id: int, acknowledged_by: str):
        """Acknowledge alert"""

    def _validate_thresholds(self, kpi_data: Dict):
        """Validate threshold configuration"""
        # For higher_better: critical < warning < target
        # For lower_better: target < warning < critical
        # For target_value: target with +/- tolerance
```

### Deliverables
- [ ] Complete kpi_service.py (300+ lines)
- [ ] All methods implemented
- [ ] Integration with workflows/kpi_calculations.py
- [ ] Event publishing
- [ ] Email alerting (if enabled)

---

## 🔍 TASK 4: Implement Audit Service

### Objective
Complete `/services/validation/services/audit_service.py`

### Source
**Original:** `/Users/MD/ISO-22301—копия/services/SERVICES/BCM/validation/main.py`
**Lines:** 1400-1800 (Audit logic)

### Requirements

**audit_service.py structure:**
```python
class AuditService:
    def __init__(self, repository: ValidationRepository):
        self.repo = repository

    async def create_audit(self, audit_data: Dict) -> AuditPlanDB:
        """Create audit plan"""
        # 1. Validate audit scope
        # 2. Set default status = PLANNED
        # 3. Create audit plan
        # 4. Publish event

    async def start_fieldwork(self, audit_id: int):
        """Start audit fieldwork"""
        # Workflow validation: can_start_audit

    async def add_finding(self, audit_id: int, finding_data: Dict) -> AuditFindingDB:
        """Add audit finding"""
        # 1. Create finding
        # 2. If severity is high -> auto-create CAPA
        # 3. Publish event

    async def generate_report(self, audit_id: int):
        """Generate audit report"""
        # 1. Get audit with all findings
        # 2. Calculate ISO clause coverage
        # 3. Group findings by severity
        # 4. Generate report document

    async def close_audit(self, audit_id: int):
        """Close audit"""
        # Workflow validation: can_issue_report
```

### Deliverables
- [ ] Complete audit_service.py (200+ lines)
- [ ] All methods implemented
- [ ] Auto-CAPA creation for high findings
- [ ] Report generation
- [ ] Event publishing

---

## 🚀 TASK 5: Add Document Security

### Objective
Add virus scanning and encryption to Documents Service

### Requirements

#### 5.1 Virus Scanner

**File:** `/services/documents/core/virus_scanner.py`

```python
import aiofiles
import subprocess
import asyncio
from typing import Tuple, Optional

class VirusScanner:
    """ClamAV-based virus scanner"""

    async def scan_file(self, file_path: str) -> Tuple[bool, Optional[str]]:
        """
        Scan file for viruses
        Returns: (is_clean, threat_name)
        """
        try:
            process = await asyncio.create_subprocess_exec(
                "clamdscan",
                "--no-summary",
                file_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            if process.returncode == 0:
                return True, None  # Clean
            elif process.returncode == 1:
                threat = self._parse_threat(stdout.decode())
                return False, threat
            else:
                raise Exception(f"Scan failed: {stderr.decode()}")

        except FileNotFoundError:
            # ClamAV not installed
            logger.warning("ClamAV not found, skipping scan")
            return True, None

    def _parse_threat(self, output: str) -> str:
        if "FOUND" in output:
            parts = output.split(":")
            if len(parts) >= 2:
                return parts[1].strip().replace(" FOUND", "")
        return "Unknown threat"
```

#### 5.2 File Encryption

**File:** `/services/documents/core/encryption.py`

```python
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
import base64
import os

class DocumentEncryption:
    """File encryption for classified documents"""

    def __init__(self, master_key: str):
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'bcm-platform-salt',
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(master_key.encode()))
        self.cipher = Fernet(key)

    def encrypt_file(self, file_path: str) -> str:
        """Encrypt file in-place"""
        with open(file_path, 'rb') as f:
            plaintext = f.read()

        ciphertext = self.cipher.encrypt(plaintext)

        encrypted_path = f"{file_path}.enc"
        with open(encrypted_path, 'wb') as f:
            f.write(ciphertext)

        os.remove(file_path)
        return encrypted_path

    def decrypt_file(self, encrypted_path: str) -> bytes:
        """Decrypt and return content"""
        with open(encrypted_path, 'rb') as f:
            ciphertext = f.read()

        plaintext = self.cipher.decrypt(ciphertext)
        return plaintext
```

#### 5.3 Integration

Update `/services/documents/services/document_service.py`:

```python
async def upload_file(self, file: UploadFile):
    # 1. Save temp file
    temp_path = await self._save_temp(file)

    # 2. Virus scan
    scanner = VirusScanner()
    is_clean, threat = await scanner.scan_file(temp_path)
    if not is_clean:
        os.remove(temp_path)
        raise SecurityException(f"Malicious file detected: {threat}")

    # 3. Move to permanent storage
    final_path = self._get_storage_path(document_id)
    os.rename(temp_path, final_path)

    # 4. Encrypt if classified
    if document.classification in ["confidential", "secret", "top_secret"]:
        encryption = DocumentEncryption(settings.ENCRYPTION_KEY)
        final_path = encryption.encrypt_file(final_path)
        document.is_encrypted = True

    document.file_path = final_path
    await self.doc_repo.update(document)
```

### Deliverables
- [ ] virus_scanner.py implemented
- [ ] encryption.py implemented
- [ ] Integration in document_service.py
- [ ] Add is_encrypted field to Document model
- [ ] Configuration for ENCRYPTION_KEY
- [ ] Tests

---

## 📊 SUCCESS METRICS

### Performance
- API response time: < 1000ms
- Database query time: < 100ms
- Concurrent requests: 100+
- Memory usage: < 2GB per service

### Quality
- Code coverage: > 80%
- All endpoints working
- No critical security issues
- All workflows validated

### Functionality
- All 40+ endpoints implemented
- All service layer complete
- Security enabled
- Caching working
- Monitoring active

---

## 🛠️ DEVELOPMENT GUIDELINES

### Code Style
- Python 3.11+
- Type hints everywhere
- Async/await for I/O
- Pydantic for validation
- SQLAlchemy async for DB

### Testing
- Unit tests for services
- Integration tests for API
- Mock external dependencies
- Test workflow transitions

### Documentation
- Docstrings for all functions
- API documentation (Swagger)
- README for each module
- Code comments for complex logic

### Error Handling
- Custom exceptions
- Proper HTTP status codes
- Structured error responses
- Logging for all errors

---

## 📅 TIMELINE

### Week 1: Critical
- Day 1-2: Complete Validation API Routes
- Day 3-4: Create Shared Library
- Day 5: Implement KPI Service
- Day 6: Implement Audit Service
- Day 7: Add Document Security

### Week 2: Testing & Integration
- Day 1-2: Integration testing
- Day 3-4: Bug fixes
- Day 5: Documentation
- Day 6-7: Performance testing

---

**Последнее обновление:** 3 октября 2025
**Статус:** ✅ Ready for Implementation
