"""
Simple smoke tests to verify test framework works
"""
import pytest


def test_basic_math():
    """Basic test to verify pytest works"""
    assert 2 + 2 == 4
    assert "BCM" in "BCM Platform"


def test_sample_data_validation(sample_business_process):
    """Test that fixtures work properly"""
    process = sample_business_process
    
    assert process["id"] == 1
    assert process["name"] == "IT Operations"
    assert 1 <= process["criticality"] <= 5
    assert process["rto_hours"] > 0


def test_bcm_document_analysis(sample_bcm_document_text):
    """Test BCM document content analysis"""
    text = sample_bcm_document_text.lower()
    
    # Verify ISO 22301 content is present
    assert "iso 22301" in text
    assert "business continuity" in text
    assert "risk assessment" in text
    assert "business impact" in text
    
    # Count key terms
    bcm_terms = [
        "continuity", "risk", "incident", "recovery", 
        "stakeholder", "threat", "vulnerability"
    ]
    
    found_terms = sum(1 for term in bcm_terms if term in text)
    assert found_terms >= 5  # Should find most BCM terms


class TestBCMLogic:
    """Test BCM business logic without external dependencies"""
    
    def test_risk_score_calculation(self):
        """Test risk score calculation logic"""
        def calculate_risk_score(criticality, dependencies, rto_hours):
            base_score = criticality * 2
            dependency_factor = len(dependencies) * 0.5
            rto_factor = max(0, 24 - rto_hours) * 0.1
            return base_score + dependency_factor + rto_factor
        
        # Test low risk
        low_risk = calculate_risk_score(
            criticality=1, dependencies=[], rto_hours=72
        )
        assert low_risk <= 5
        
        # Test high risk
        high_risk = calculate_risk_score(
            criticality=5, dependencies=[1,2,3,4,5], rto_hours=1
        )
        assert high_risk >= 14  # 5*2 + 5*0.5 + (24-1)*0.1 = 10 + 2.5 + 2.3 = 14.8
    
    def test_incident_classification(self):
        """Test incident classification logic"""
        def classify_incident(title, description):
            text = f"{title} {description}".lower()
            
            if any(word in text for word in ["hack", "breach", "cyber", "attack"]):
                return "security"
            elif any(word in text for word in ["server", "network", "system", "database"]):
                return "technology"
            elif any(word in text for word in ["process", "workflow", "operation"]):
                return "operational"
            else:
                return "unknown"
        
        test_cases = [
            ("Security Breach", "Hacker attack detected", "security"),
            ("Server Down", "Database server crashed", "technology"),  
            ("Process Failure", "Workflow stopped", "operational"),
            ("Random Issue", "Something happened", "unknown")
        ]
        
        for title, description, expected in test_cases:
            result = classify_incident(title, description)
            assert result == expected
    
    def test_iso22301_compliance_score(self):
        """Test ISO 22301 compliance scoring"""
        def calculate_compliance_score(document_text, iso_clauses):
            total_possible_clauses = 23  # Total ISO 22301 clauses
            covered_clauses = len(set(iso_clauses))
            base_score = covered_clauses / total_possible_clauses
            
            # Bonus for comprehensive content
            bonus = 0
            if "policy" in document_text and "procedure" in document_text:
                bonus += 0.1
            if "risk" in document_text and "assessment" in document_text:
                bonus += 0.1
                
            return min(1.0, base_score + bonus)
        
        # Test high compliance document
        high_compliance_text = "policy procedure risk assessment business continuity"
        high_clauses = [f"{i}.{j}" for i in range(4, 11) for j in range(1, 4)]
        
        score = calculate_compliance_score(high_compliance_text, high_clauses)
        assert score > 0.8
        
        # Test low compliance
        low_score = calculate_compliance_score("basic document", ["4.1"])
        assert low_score < 0.2


@pytest.mark.asyncio
async def test_async_functionality():
    """Test async functionality works"""
    import asyncio
    
    async def mock_ai_analysis(text):
        await asyncio.sleep(0.01)  # Simulate processing
        return {
            "entities": ["business continuity", "ISO 22301"],
            "classification": "policy",
            "confidence": 0.95
        }
    
    result = await mock_ai_analysis("BCM policy document")
    
    assert result["classification"] == "policy"
    assert result["confidence"] > 0.9
    assert len(result["entities"]) == 2


def test_data_validation():
    """Test data validation logic"""
    def validate_business_process(process_data):
        errors = []
        
        if not isinstance(process_data.get("id"), int):
            errors.append("ID must be integer")
        
        if not process_data.get("name"):
            errors.append("Name is required")
            
        criticality = process_data.get("criticality")
        if not isinstance(criticality, int) or not (1 <= criticality <= 5):
            errors.append("Criticality must be 1-5")
            
        rto = process_data.get("rto_hours")
        if not isinstance(rto, int) or rto <= 0:
            errors.append("RTO must be positive integer")
            
        return errors
    
    # Valid process
    valid_process = {
        "id": 1,
        "name": "Test Process",
        "criticality": 3,
        "rto_hours": 24
    }
    assert validate_business_process(valid_process) == []
    
    # Invalid process
    invalid_process = {
        "id": "not_int",
        "name": "",
        "criticality": 10,
        "rto_hours": -5
    }
    errors = validate_business_process(invalid_process)
    assert len(errors) == 4


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
