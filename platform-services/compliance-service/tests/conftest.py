"""
Pytest Configuration and Fixtures for Compliance Service Tests
Comprehensive test fixtures for audit, nonconformity, RCA, and workflow tests
"""

import pytest
import asyncio
from typing import AsyncGenerator, Generator, Dict, Any, List
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from models.database import Base
from models.enums import (
    AuditType, AuditStatus, AuditScope, NonconformityType,
    NonconformitySeverity, NonconformityStatus, EvidenceType,
    RCAMethod, CorrectiveActionStatus
)


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def db_engine():
    """Create test database engine with in-memory SQLite"""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        poolclass=NullPool,
        echo=False
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    await engine.dispose()


@pytest.fixture
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session"""
    async_session = async_sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture
def tenant_id() -> str:
    """Test tenant ID"""
    return "test-tenant-compliance-123"


@pytest.fixture
def user_id() -> str:
    """Test user ID"""
    return "test-user-auditor-456"


@pytest.fixture
def mock_cache():
    """Mock Redis cache"""
    cache_mock = AsyncMock()
    cache_mock.get.return_value = None
    cache_mock.set.return_value = True
    cache_mock.delete.return_value = True
    cache_mock.clear.return_value = True
    return cache_mock


@pytest.fixture
def mock_eventbus():
    """Mock event bus for testing event publishing"""
    eventbus_mock = AsyncMock()
    eventbus_mock.publish.return_value = True
    return eventbus_mock


@pytest.fixture
def mock_audit_logger():
    """Mock audit logger"""
    audit_mock = AsyncMock()
    audit_mock.log_create.return_value = None
    audit_mock.log_update.return_value = None
    audit_mock.log_delete.return_value = None
    audit_mock.log_state_transition.return_value = None
    return audit_mock


# ==================== AUDIT FIXTURES ====================

@pytest.fixture
def sample_audit_create_data(tenant_id: str) -> Dict[str, Any]:
    """Sample audit creation data"""
    return {
        "tenant_id": tenant_id,
        "audit_title": "ISO 22301 Annual Internal Audit",
        "audit_type": AuditType.INTERNAL.value,
        "audit_scope": AuditScope.FULL_SYSTEM.value,
        "audit_standard": "ISO 22301:2019",
        "planned_start_date": datetime.now() + timedelta(days=7),
        "planned_end_date": datetime.now() + timedelta(days=14),
        "lead_auditor_id": "auditor-001",
        "audit_team": ["auditor-001", "auditor-002", "auditor-003"],
        "audit_objectives": [
            "Verify BCMS implementation",
            "Assess policy compliance",
            "Identify improvement opportunities"
        ],
        "audit_criteria": [
            "ISO 22301 Clause 4-10",
            "Company BCM Policy",
            "Previous audit findings"
        ],
        "departments_in_scope": ["IT", "Operations", "Finance"],
        "status": AuditStatus.PLANNED.value
    }


@pytest.fixture
def sample_audit_with_findings(tenant_id: str) -> Dict[str, Any]:
    """Sample audit with findings"""
    return {
        "tenant_id": tenant_id,
        "audit_title": "Quarterly Compliance Review",
        "audit_type": AuditType.INTERNAL.value,
        "audit_scope": AuditScope.PROCESS.value,
        "audit_standard": "ISO 22301:2019",
        "planned_start_date": datetime.now() - timedelta(days=30),
        "planned_end_date": datetime.now() - timedelta(days=23),
        "actual_start_date": datetime.now() - timedelta(days=30),
        "actual_end_date": datetime.now() - timedelta(days=23),
        "lead_auditor_id": "auditor-001",
        "audit_team": ["auditor-001", "auditor-002"],
        "findings": [
            {
                "finding_id": str(uuid4()),
                "finding_type": "nonconformity",
                "severity": "major",
                "description": "BIA not updated in 18 months",
                "clause_reference": "ISO 22301:2019 Clause 8.2.2",
                "evidence": ["Document review", "Interview notes"]
            },
            {
                "finding_id": str(uuid4()),
                "finding_type": "observation",
                "description": "Plan testing frequency could be improved",
                "clause_reference": "ISO 22301:2019 Clause 8.5",
                "evidence": ["Test records"]
            }
        ],
        "status": AuditStatus.COMPLETED.value
    }


# ==================== NONCONFORMITY FIXTURES ====================

@pytest.fixture
def sample_nonconformity_create_data(tenant_id: str) -> Dict[str, Any]:
    """Sample nonconformity creation data"""
    return {
        "tenant_id": tenant_id,
        "nc_title": "BIA Documentation Out of Date",
        "nc_type": NonconformityType.MAJOR.value,
        "severity": NonconformitySeverity.HIGH.value,
        "description": "Business Impact Analysis has not been updated for 18 months, violating ISO 22301 requirement for annual review",
        "clause_reference": "ISO 22301:2019 Clause 8.2.2",
        "detected_date": datetime.now() - timedelta(days=2),
        "detected_by": "auditor-001",
        "department": "IT Operations",
        "process_affected": "Business Continuity Planning",
        "immediate_action_taken": "Temporary mitigation: Scheduled emergency BIA update meeting",
        "containment_complete": False,
        "status": NonconformityStatus.OPEN.value
    }


@pytest.fixture
def sample_nonconformity_with_rca(tenant_id: str) -> Dict[str, Any]:
    """Sample nonconformity with RCA completed"""
    return {
        "tenant_id": tenant_id,
        "nc_title": "Backup Test Failures",
        "nc_type": NonconformityType.MAJOR.value,
        "severity": NonconformitySeverity.CRITICAL.value,
        "description": "Monthly backup restoration test failed for 3 consecutive months",
        "clause_reference": "ISO 22301:2019 Clause 8.4.2",
        "detected_date": datetime.now() - timedelta(days=10),
        "detected_by": "system-admin-002",
        "department": "IT Infrastructure",
        "rca_method": RCAMethod.FIVE_WHYS.value,
        "rca_template_data": {
            "problem_statement": "Backup restoration test failed",
            "why_1": "Why did the backup fail? - Corrupted backup files",
            "why_2": "Why were files corrupted? - Storage system errors",
            "why_3": "Why storage errors? - Insufficient disk space",
            "why_4": "Why insufficient space? - No monitoring alerts configured",
            "why_5": "Why no alerts? - Oversight during system setup",
            "root_cause": "Lack of proper system monitoring and alerting"
        },
        "root_causes": ["Inadequate system monitoring", "Insufficient capacity planning"],
        "status": NonconformityStatus.RCA_COMPLETE.value
    }


# ==================== RCA TEMPLATE FIXTURES ====================

@pytest.fixture
def sample_five_whys_template() -> Dict[str, Any]:
    """Sample 5 Whys RCA template"""
    return {
        "problem_statement": "Plan testing was not completed on schedule",
        "why_1": "Why was testing not completed? - Insufficient staff availability",
        "why_2": "Why insufficient staff? - Key personnel were reassigned",
        "why_3": "Why were they reassigned? - Urgent project took priority",
        "why_4": "Why did urgent project conflict? - Poor resource planning",
        "why_5": "Why poor planning? - No formal resource allocation process",
        "root_cause": "Lack of formal resource allocation and priority management process"
    }


@pytest.fixture
def sample_fishbone_template() -> Dict[str, Any]:
    """Sample Fishbone diagram RCA template"""
    return {
        "problem_statement": "Emergency notification system failed during test",
        "people": [
            {
                "description": "Inadequate training",
                "sub_causes": ["New staff not trained", "No refresher training"]
            },
            {
                "description": "Lack of ownership",
                "sub_causes": ["Unclear responsibilities"]
            }
        ],
        "process": [
            {
                "description": "No testing procedure",
                "sub_causes": ["Procedure never documented", "No review cycle"]
            }
        ],
        "technology": [
            {
                "description": "System compatibility issues",
                "sub_causes": ["Software version mismatch", "Integration not tested"]
            },
            {
                "description": "Insufficient capacity",
                "sub_causes": ["Undersized for user load"]
            }
        ],
        "environment": [
            {
                "description": "Network issues",
                "sub_causes": ["Firewall blocking alerts"]
            }
        ],
        "materials": [],
        "measurement": [
            {
                "description": "No performance metrics",
                "sub_causes": ["No monitoring configured"]
            }
        ]
    }


@pytest.fixture
def sample_fault_tree_template() -> Dict[str, Any]:
    """Sample Fault Tree Analysis template"""
    return {
        "problem_statement": "Critical system unavailability",
        "top_event": {
            "id": "top",
            "description": "Critical system unavailable",
            "gate_type": "OR",
            "probability": None,
            "children": [
                {
                    "id": "hw_failure",
                    "description": "Hardware failure",
                    "gate_type": "AND",
                    "probability": None,
                    "children": [
                        {
                            "id": "server_fail",
                            "description": "Server failure",
                            "gate_type": "AND",
                            "probability": 0.05,
                            "children": []
                        },
                        {
                            "id": "storage_fail",
                            "description": "Storage failure",
                            "gate_type": "AND",
                            "probability": 0.03,
                            "children": []
                        }
                    ]
                },
                {
                    "id": "sw_failure",
                    "description": "Software failure",
                    "gate_type": "AND",
                    "probability": 0.10,
                    "children": []
                }
            ]
        }
    }


# ==================== EVIDENCE FIXTURES ====================

@pytest.fixture
def sample_evidence_items() -> List[Dict[str, Any]]:
    """Sample evidence items"""
    return [
        {
            "evidence_type": EvidenceType.DOCUMENT.value,
            "title": "BIA Documentation Review",
            "description": "Reviewed BIA documents dated 2022-01-15",
            "file_path": "/evidence/bia_review_2022.pdf",
            "collected_by": "auditor-001",
            "collected_date": datetime.now() - timedelta(days=5)
        },
        {
            "evidence_type": EvidenceType.INTERVIEW.value,
            "title": "Interview with BCM Coordinator",
            "description": "Discussed BIA update process and timeline",
            "notes": "Coordinator confirmed last update was 18 months ago",
            "collected_by": "auditor-002",
            "collected_date": datetime.now() - timedelta(days=4)
        },
        {
            "evidence_type": EvidenceType.SCREENSHOT.value,
            "title": "BIA System Screenshot",
            "description": "Screenshot showing last modification date",
            "file_path": "/evidence/bia_system_screen.png",
            "collected_by": "auditor-001",
            "collected_date": datetime.now() - timedelta(days=3)
        }
    ]


# ==================== CORRECTIVE ACTION FIXTURES ====================

@pytest.fixture
def sample_corrective_actions() -> List[Dict[str, Any]]:
    """Sample corrective actions"""
    return [
        {
            "action_id": str(uuid4()),
            "action_description": "Update BIA documentation immediately",
            "action_type": "immediate",
            "responsible_person": "bcm-manager-001",
            "target_date": datetime.now() + timedelta(days=14),
            "status": CorrectiveActionStatus.IN_PROGRESS.value,
            "estimated_cost": 5000.0
        },
        {
            "action_id": str(uuid4()),
            "action_description": "Implement automated BIA review reminders",
            "action_type": "preventive",
            "responsible_person": "it-admin-002",
            "target_date": datetime.now() + timedelta(days=30),
            "status": CorrectiveActionStatus.PLANNED.value,
            "estimated_cost": 2000.0
        },
        {
            "action_id": str(uuid4()),
            "action_description": "Conduct BIA training for all process owners",
            "action_type": "corrective",
            "responsible_person": "training-coordinator-003",
            "target_date": datetime.now() + timedelta(days=45),
            "status": CorrectiveActionStatus.PLANNED.value,
            "estimated_cost": 10000.0
        }
    ]


# ==================== WORKFLOW VALIDATION FIXTURES ====================

@pytest.fixture
def valid_workflow_transitions() -> Dict[str, List[str]]:
    """Valid workflow state transitions"""
    return {
        "planned": ["in_progress", "cancelled"],
        "in_progress": ["fieldwork", "cancelled"],
        "fieldwork": ["reporting", "in_progress"],
        "reporting": ["under_review", "fieldwork"],
        "under_review": ["completed", "reporting"],
        "completed": [],  # Terminal state
        "cancelled": []   # Terminal state
    }


@pytest.fixture
def sample_bulk_audits(tenant_id: str) -> List[Dict[str, Any]]:
    """Sample bulk audits for testing bulk operations"""
    return [
        {
            "tenant_id": tenant_id,
            "audit_title": f"Audit {i}",
            "audit_type": AuditType.INTERNAL.value,
            "audit_scope": AuditScope.PROCESS.value,
            "audit_standard": "ISO 22301:2019",
            "planned_start_date": datetime.now() + timedelta(days=i*7),
            "planned_end_date": datetime.now() + timedelta(days=i*7 + 5),
            "lead_auditor_id": f"auditor-{i % 3 + 1}",
            "status": AuditStatus.PLANNED.value
        }
        for i in range(1, 11)
    ]
