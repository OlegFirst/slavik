"""
Pytest configuration and fixtures for BCM Platform tests
"""
import pytest
import asyncio
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, AsyncMock
from datetime import datetime


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_redis():
    """Mock Redis client"""
    redis_mock = AsyncMock()
    redis_mock.ping.return_value = "PONG"
    redis_mock.setex.return_value = True
    redis_mock.get.return_value = None
    return redis_mock


@pytest.fixture
def mock_db_engine():
    """Mock database engine"""
    engine_mock = AsyncMock()
    return engine_mock


@pytest.fixture
def sample_business_process():
    """Sample business process for testing"""
    return {
        "id": 1,
        "name": "IT Operations",
        "description": "Core IT infrastructure management",
        "criticality": 4,
        "rto_hours": 4,
        "rpo_hours": 1,
        "dependencies": [2, 3],
        "resources_required": ["servers", "network", "staff"]
    }


@pytest.fixture
def sample_incident():
    """Sample incident for testing"""
    return {
        "id": 1,
        "title": "Database Server Outage",
        "description": "Primary database server has crashed and is unresponsive. System administrators are investigating.",
        "category": "technology",
        "severity": "high",
        "affected_processes": [1, 2, 3],
        "estimated_impact": 25000,
        "created_at": datetime.now().isoformat()
    }


@pytest.fixture
def sample_document_metadata():
    """Sample document metadata for testing"""
    return {
        "filename": "bcm_policy.pdf",
        "file_size": 1048576,  # 1MB
        "mime_type": "application/pdf",
        "file_hash": "sha256:abc123def456",
        "upload_date": datetime.now(),
        "company_id": "test_company",
        "document_type": "policy",
        "classification": "internal",
        "language": "en",
        "page_count": 10
    }


@pytest.fixture
def sample_bcm_document_text():
    """Sample BCM document text for testing"""
    return """
    Business Continuity Management Policy
    
    1. Introduction
    This policy establishes the framework for business continuity management
    in accordance with ISO 22301:2019 standard. Our organization is committed
    to maintaining resilience and ensuring continuity of critical operations.
    
    2. Scope and Objectives
    This policy applies to all business processes, stakeholders, and operations
    within our organization. The primary objectives include:
    - Risk assessment and threat identification
    - Business impact analysis (BIA) implementation
    - Recovery time objective (RTO) and recovery point objective (RPO) definition
    - Incident response and emergency procedures
    
    3. Risk Management
    We conduct regular risk assessments to identify threats, vulnerabilities,
    and potential impacts on our critical business processes. Risk mitigation
    strategies are developed and maintained for all identified risks.
    
    4. Business Impact Analysis
    Critical business functions are identified and analyzed for potential
    impacts during disruptions. Dependencies between processes are mapped
    to ensure comprehensive continuity planning.
    
    5. Incident Management
    All incidents are classified according to severity levels and managed
    through our established incident response procedures. Critical incidents
    require immediate escalation to senior management and stakeholders.
    
    6. Testing and Exercises
    Regular testing of continuity plans through tabletop exercises, drills,
    and simulations ensures our preparedness and identifies improvement areas.
    
    7. Training and Awareness
    All personnel receive appropriate training on business continuity procedures
    and their roles during incidents. Regular awareness programs maintain
    organizational readiness.
    
    8. Monitoring and Review
    Continuous monitoring of our business continuity management system ensures
    effectiveness and compliance with ISO 22301 requirements. Regular audits
    and management reviews drive continual improvement.
    """


@pytest.fixture
def temp_document_file(sample_bcm_document_text):
    """Create temporary document file for testing"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp_file:
        tmp_file.write(sample_bcm_document_text)
        temp_path = Path(tmp_file.name)
    
    yield temp_path
    
    # Cleanup
    if temp_path.exists():
        temp_path.unlink()


@pytest.fixture
def mock_nlp_model():
    """Mock spaCy NLP model"""
    nlp_mock = Mock()
    
    # Mock document with entities
    doc_mock = Mock()
    
    # Sample entities
    entity_mock = Mock()
    entity_mock.text = "business continuity"
    entity_mock.label_ = "CONCEPT"
    entity_mock.start_char = 0
    entity_mock.end_char = 18
    
    entity2_mock = Mock()
    entity2_mock.text = "ISO 22301"
    entity2_mock.label_ = "STANDARD"
    entity2_mock.start_char = 50
    entity2_mock.end_char = 59
    
    doc_mock.ents = [entity_mock, entity2_mock]
    nlp_mock.return_value = doc_mock
    
    return nlp_mock


@pytest.fixture
def api_headers():
    """Standard API headers for testing"""
    return {
        "Authorization": "Bearer test_api_key",
        "Content-Type": "application/json"
    }


@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response"""
    response_mock = Mock()
    choice_mock = Mock()
    choice_mock.text = "This document provides a comprehensive overview of business continuity procedures and risk management strategies."
    response_mock.choices = [choice_mock]
    
    async_response = AsyncMock()
    async_response.return_value = response_mock
    
    return async_response


@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch):
    """Setup test environment variables"""
    monkeypatch.setenv("TESTING", "true")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/15")  # Test DB
    monkeypatch.setenv("DATABASE_URL", "sqlite:///test.db")
    monkeypatch.setenv("DOCUMENT_PROCESSOR_API_KEY", "test_api_key")
    monkeypatch.setenv("AI_ORCHESTRATOR_URL", "http://localhost:8000")
    monkeypatch.setenv("UPLOAD_DIR", "/tmp/test_uploads")


@pytest.fixture
def cleanup_temp_files():
    """Cleanup temporary files after tests"""
    temp_files = []
    
    def add_temp_file(file_path):
        temp_files.append(Path(file_path))
    
    yield add_temp_file
    
    # Cleanup
    for file_path in temp_files:
        if file_path.exists():
            file_path.unlink()


@pytest.fixture
def mock_huggingface_pipeline():
    """Mock Hugging Face transformers pipeline"""
    pipeline_mock = Mock()
    pipeline_mock.return_value = [
        {
            "label": "POLICY",
            "score": 0.95
        }
    ]
    return pipeline_mock


@pytest.fixture
def sample_iso_clauses():
    """Sample ISO 22301 clauses mapping"""
    return {
        "4.1": ["organization", "context", "internal", "external"],
        "4.2": ["stakeholder", "interested party", "requirements"],
        "5.1": ["leadership", "commitment", "top management"],
        "6.1": ["risk", "opportunity", "assessment"],
        "8.2": ["business impact", "bia", "analysis"],
        "9.1": ["monitoring", "measurement", "evaluation"],
        "9.2": ["audit", "internal audit"]
    }


class MockAsyncSession:
    """Mock database session for testing"""
    
    def __init__(self):
        self.committed = False
        self.rolled_back = False
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
    
    async def commit(self):
        self.committed = True
    
    async def rollback(self):
        self.rolled_back = True


@pytest.fixture
def mock_db_session():
    """Mock database session"""
    return MockAsyncSession()


@pytest.fixture
def bcm_test_data():
    """Sample BCM test data for comprehensive testing"""
    return {
        "processes": [
            {
                "id": 1,
                "name": "Customer Service Operations",
                "criticality": 5,
                "rto_hours": 2,
                "dependencies": [2, 3]
            },
            {
                "id": 2,
                "name": "Payment Processing",
                "criticality": 5,
                "rto_hours": 1,
                "dependencies": [3]
            },
            {
                "id": 3,
                "name": "Data Center Operations",
                "criticality": 4,
                "rto_hours": 4,
                "dependencies": []
            }
        ],
        "incidents": [
            {
                "id": 1,
                "type": "security",
                "severity": "critical",
                "description": "Suspected cyber attack on customer database"
            },
            {
                "id": 2,
                "type": "operational",
                "severity": "high",
                "description": "Power outage affecting main facility"
            }
        ],
        "documents": [
            {
                "type": "policy",
                "iso_clauses": ["4.1", "4.2", "5.1"],
                "compliance_score": 0.85
            },
            {
                "type": "procedure",
                "iso_clauses": ["8.2", "8.3"],
                "compliance_score": 0.72
            }
        ]
    }
