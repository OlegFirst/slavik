"""
Tests for Document Processor Service
"""
import pytest
import asyncio
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from fastapi.testclient import TestClient
from datetime import datetime

# Import the service components
try:
    from document_processor import (
        app,
        DocumentProcessor,
        DocumentMetadata,
        DocumentContent,
        BCMDocumentAnalysis,
        verify_api_key,
    )
except ImportError as e:
    import pytest
    pytest.skip(f"Skipping Document Processor tests due to missing dependencies: {e}", allow_module_level=True)

client = TestClient(app)


class TestDocumentProcessorAPI:
    """Test suite for Document Processor API"""
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "1.0.0"
        assert "services" in data
    
    def test_upload_document_no_file(self):
        """Test upload endpoint with no file"""
        app.dependency_overrides[verify_api_key] = lambda: "valid_key"
        response = client.post(
            "/api/v1/documents/upload",
            headers={"Authorization": "Bearer test_key"},
            data={"company_id": "test_company"}
        )
        app.dependency_overrides.clear()
        assert response.status_code == 422  # Validation error - no file

    def test_upload_document_invalid_api_key(self):
        """Test upload with invalid API key"""
        def invalid_key():
            from fastapi import HTTPException
            raise HTTPException(status_code=403, detail="Invalid API key")
        app.dependency_overrides[verify_api_key] = invalid_key

        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as tmp_file:
            tmp_file.write(b"Test content")
            tmp_file_path = tmp_file.name

        try:
            with open(tmp_file_path, 'rb') as f:
                response = client.post(
                    "/api/v1/documents/upload",
                    headers={"Authorization": "Bearer invalid_key"},
                    files={"file": ("test.txt", f, "text/plain")},
                    data={"company_id": "test_company"}
                )
            assert response.status_code == 403
        finally:
            app.dependency_overrides.clear()
            os.unlink(tmp_file_path)


@pytest.fixture
def processor():
    """Provide a fresh DocumentProcessor instance for each test."""
    return DocumentProcessor()


class TestDocumentProcessor:
    """Test the DocumentProcessor class directly"""
    
    def test_supported_formats(self, processor):
        """Test that all required formats are supported"""
        
        expected_formats = [
            'application/pdf',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/msword',
            'text/plain',
            'image/png',
            'image/jpeg'
        ]
        
        for format_type in expected_formats:
            assert format_type in processor.supported_formats
    
    @pytest.mark.asyncio
    async def test_process_text_document(self, processor):
        """Test processing a plain text document"""
        
        # Create temporary text file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp_file:
            test_content = """
            Business Continuity Policy
            
            This document outlines our business continuity framework and procedures.
            Risk assessment is critical for identifying threats and vulnerabilities.
            We must ensure recovery time objectives are met during incidents.
            """
            tmp_file.write(test_content)
            tmp_file_path = Path(tmp_file.name)
        
        try:
            # Create metadata
            metadata = DocumentMetadata(
                filename="test_policy.txt",
                file_size=len(test_content),
                mime_type="text/plain",
                file_hash="test_hash",
                upload_date=datetime.now(),
                company_id="test_company",
                document_type="policy"
            )
            
            # Process document
            result = await processor._process_text(tmp_file_path)
            
            assert "text" in result
            assert "Business Continuity Policy" in result["text"]
            assert result["structure"]["format"] == "plain_text"
            
        finally:
            if tmp_file_path.exists():
                tmp_file_path.unlink()
    
    def test_bcm_document_classification(self, processor):
        """Test BCM document classification"""
        
        test_cases = [
            ("policy governance framework standard", "policy"),
            ("procedure process workflow instruction", "procedure"),
            ("continuity plan recovery strategy", "plan"),
            ("risk assessment analysis threat", "risk_assessment"),
            ("business impact analysis bia critical", "bia"),
            ("exercise drill test simulation", "exercise"),
            ("unknown document type", "unknown")
        ]
        
        for text, expected_category in test_cases:
            result = processor._classify_bcm_document(text.lower())
            assert result == expected_category
    
    def test_iso22301_clause_mapping(self, processor):
        """Test mapping of content to ISO 22301 clauses"""
        
        test_cases = [
            ("organization context internal external", ["4.1"]),
            ("stakeholder interested party requirements", ["4.2"]),
            ("scope boundary applicability", ["4.3"]),
            ("leadership commitment top management", ["5.1"]),
            ("risk opportunity assessment", ["6.1"]),
            ("business impact bia analysis", ["8.2"]),
            ("monitoring measurement evaluation", ["9.1"]),
            ("audit internal audit", ["9.2"]),
        ]
        
        for text, expected_clauses in test_cases:
            result = processor._map_iso22301_clauses(text.lower())
            for clause in expected_clauses:
                assert clause in result
    
    def test_risk_indicators_extraction(self, processor):
        """Test extraction of risk indicators from text"""
        
        text = """
        This document identifies several threats to our operations.
        The vulnerability in our system could lead to significant impact.
        Risk of failure is high due to disruption potential.
        Security breach and cyber attack scenarios are outlined.
        """
        
        result = processor._extract_risk_indicators(text)
        
        # Should find multiple risk keywords
        indicators = [r["indicator"] for r in result]
        assert "threat" in indicators
        assert "vulnerability" in indicators
        assert "risk" in indicators
        assert "impact" in indicators
        
        # Check frequency counting
        for indicator in result:
            assert indicator["frequency"] > 0
            assert indicator["severity"] in ["low", "medium", "high"]
    
    def test_compliance_score_calculation(self, processor):
        """Test compliance score calculation"""
        
        # Text with good ISO coverage
        comprehensive_text = """
        organization context stakeholder scope leadership policy
        risk assessment business impact continuity monitoring audit
        """
        
        clauses = processor._map_iso22301_clauses(comprehensive_text)
        score = processor._calculate_compliance_score(comprehensive_text, clauses)
        
        assert 0 <= score <= 1
        assert score > 0.3  # Should have decent coverage
    
    def test_recommendations_generation(self, processor):
        """Test generation of BCM recommendations"""
        
        # Low compliance score
        recommendations = processor._generate_recommendations(
            category="policy",
            compliance_score=0.3,
            risk_indicators=[{"indicator": "risk", "severity": "low"}]
        )
        
        assert len(recommendations) > 0
        assert any("ISO 22301" in rec for rec in recommendations)
        
        # High risk scenario
        high_risk_indicators = [
            {"indicator": "threat", "severity": "high"} for _ in range(6)
        ]
        
        recommendations = processor._generate_recommendations(
            category="plan",
            compliance_score=0.8,
            risk_indicators=high_risk_indicators
        )
        
        assert any("risk indicators" in rec.lower() for rec in recommendations)
    
    def test_stakeholder_extraction(self, processor):
        """Test stakeholder extraction from entities"""
        
        entities = [
            {"text": "John Smith", "label": "PERSON"},
            {"text": "ABC Corporation", "label": "ORG"},
            {"text": "management", "label": "OTHER"},
            {"text": "employees", "label": "OTHER"},
        ]
        
        stakeholders = processor._extract_stakeholders(entities)
        
        assert "John Smith" in stakeholders
        assert "ABC Corporation" in stakeholders
        assert "management" in stakeholders
        assert "employees" in stakeholders
    
    def test_business_process_mapping(self, processor):
        """Test business process mapping"""
        
        text_with_processes = """
        Our IT operations and technology systems are critical.
        Human resources and personnel management processes.
        Finance and accounting procedures are essential.
        Customer service and support operations.
        Supply chain and vendor management.
        """
        
        processes = processor._map_business_processes(text_with_processes.lower())
        
        expected_processes = [
            "it_operations", "hr_management", "finance", 
            "customer_service", "supply_chain"
        ]
        
        for process in expected_processes:
            assert process in processes
    
    @pytest.mark.asyncio
    async def test_nlp_analysis(self, processor):
        """Test NLP analysis functionality"""
        
        sample_text = """
        This is a business continuity policy document.
        It covers risk management procedures and incident response.
        The document outlines recovery strategies and compliance requirements.
        Key stakeholders include management and operations teams.
        """
        
        # Mock the NLP model to avoid dependencies
        with patch('ai_services.document_processor.nlp_model') as mock_nlp:
            mock_doc = Mock()
            mock_ent = Mock()
            mock_ent.text = "business continuity"
            mock_ent.label_ = "CONCEPT"
            mock_ent.start_char = 10
            mock_ent.end_char = 28
            mock_doc.ents = [mock_ent]
            mock_nlp.return_value = mock_doc
            
            result = await processor._analyze_text(sample_text)
            
            assert "entities" in result
            assert "key_phrases" in result
            assert "topics" in result
            
            # Check topics extraction
            topics = result["topics"]
            assert "business_continuity" in topics
            assert "risk_management" in topics
            assert "compliance" in topics
    
    def test_critical_sections_identification(self, processor):
        """Test identification of critical document sections"""
        
        content = DocumentContent(
            document_id="test_doc",
            raw_text="Test content",
            structured_content={
                "paragraphs": [
                    {"text": "This is a critical process that requires immediate attention."},
                    {"text": "Normal operations continue as planned."},
                    {"text": "Essential services have priority recovery time of 2 hours."},
                    {"text": "Regular maintenance procedures."}
                ]
            },
            extracted_entities=[],
            key_phrases=[],
            compliance_tags=[]
        )
        
        critical_sections = processor._identify_critical_sections(content)
        
        # Should identify sections with keywords like 'critical', 'essential', 'priority', 'recovery time'
        assert len(critical_sections) >= 2
        
        for section in critical_sections:
            assert "section" in section
            assert "content" in section
            assert "importance" in section
            assert section["importance"] == "high"


class TestDocumentMetadata:
    """Test DocumentMetadata model"""
    
    def test_document_metadata_creation(self):
        """Test creation of DocumentMetadata"""
        metadata = DocumentMetadata(
            filename="test.pdf",
            file_size=1024,
            mime_type="application/pdf",
            file_hash="abcd1234",
            upload_date=datetime.now(),
            company_id="test_company",
            document_type="policy",
            classification="confidential",
            language="en",
            page_count=5
        )
        
        assert metadata.filename == "test.pdf"
        assert metadata.file_size == 1024
        assert metadata.mime_type == "application/pdf"
        assert metadata.document_type == "policy"
        assert metadata.page_count == 5
    
    def test_document_content_creation(self):
        """Test creation of DocumentContent"""
        content = DocumentContent(
            document_id="doc123",
            raw_text="Sample document text",
            structured_content={"pages": 1},
            extracted_entities=[{"text": "entity", "label": "TEST"}],
            key_phrases=["business continuity"],
            summary="Document summary",
            topics=["bcm"],
            compliance_tags=["iso22301"]
        )
        
        assert content.document_id == "doc123"
        assert len(content.extracted_entities) == 1
        assert "business continuity" in content.key_phrases
        assert "bcm" in content.topics


class TestErrorHandling:
    """Test error handling scenarios"""

    @pytest.mark.asyncio
    async def test_unsupported_file_format(self, processor):
        """Test handling of unsupported file formats"""
        
        metadata = DocumentMetadata(
            filename="test.xyz",
            file_size=100,
            mime_type="application/unknown",
            file_hash="hash123",
            upload_date=datetime.now(),
            company_id="test"
        )
        
        with tempfile.NamedTemporaryFile() as tmp_file:
            tmp_path = Path(tmp_file.name)
            
            with pytest.raises(ValueError, match="Unsupported file format"):
                await processor.process_document(tmp_path, metadata)
    
    def test_empty_text_analysis(self, processor):
        """Test analysis with empty text"""
        
        result = processor._extract_risk_indicators("")
        assert result == []
        
        result = processor._map_business_processes("")
        assert result == []
        
        result = processor._classify_bcm_document("")
        assert result == "unknown"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
