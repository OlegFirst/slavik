"""
Tests for Smart Anonymizer

Test cases:
1. Direct identifiers removal
2. Quasi-identifier generalization
3. Risk score calculation
4. K-anonymity validation
"""

import pytest
from ..services.anonymizer import SmartAnonymizer, AnonymizationResult

@pytest.fixture
def anonymizer():
    """Create anonymizer instance"""
    return SmartAnonymizer(k_anonymity=5)

@pytest.fixture
def sample_case():
    """Sample case data with identifiable information"""
    return {
        "organization_name": "Acme Healthcare Inc",
        "organization_context": {
            "industry": "healthcare",
            "location": "Tallinn, Estonia",
            "employee_count": 150,
            "founded_date": "2015-03-15"
        },
        "module": "bia",
        "workflow_name": "Business Impact Analysis",
        "journey": [
            {
                "stage": "discovery",
                "started_at": "2025-10-01",
                "actions": [
                    {
                        "type": "process_identified",
                        "data": {
                            "process_name": "Emergency Department at Tallinn Hospital"
                        }
                    }
                ]
            }
        ],
        "metrics": {
            "processes_count": 25,
            "completed_successfully": True
        },
        "success_patterns": [
            "Strong executive sponsorship enabled rapid progress"
        ]
    }

@pytest.mark.asyncio
async def test_removes_direct_identifiers(anonymizer, sample_case):
    """Test that direct identifiers are removed"""

    result = await anonymizer.anonymize_case(sample_case)

    assert 'organization_name' not in result.anonymized_data
    assert 'organization_name' in result.removed_fields

@pytest.mark.asyncio
async def test_generalizes_location(anonymizer, sample_case):
    """Test location generalization"""

    result = await anonymizer.anonymize_case(sample_case)

    org = result.anonymized_data['organization_context']

    assert 'location' not in org
    assert 'region' in org
    assert org['region'] == 'northern_europe'

@pytest.mark.asyncio
async def test_generalizes_employee_count(anonymizer, sample_case):
    """Test employee count generalization to size"""

    result = await anonymizer.anonymize_case(sample_case)

    org = result.anonymized_data['organization_context']

    assert 'employee_count' not in org
    assert 'size' in org
    assert org['size'] == 'medium'  # 150 employees = medium

@pytest.mark.asyncio
async def test_generalizes_dates(anonymizer, sample_case):
    """Test date generalization to month/year"""

    result = await anonymizer.anonymize_case(sample_case)

    journey = result.anonymized_data['journey']
    assert journey[0]['started_at'] == '2025-10'  # YYYY-MM only

@pytest.mark.asyncio
async def test_generalizes_process_names(anonymizer, sample_case):
    """Test process name generalization"""

    result = await anonymizer.anonymize_case(sample_case)

    action = result.anonymized_data['journey'][0]['actions'][0]
    process_name = action['data']['process_name']

    assert 'Tallinn' not in process_name
    assert 'Hospital' not in process_name
    assert process_name == 'Emergency Services'

@pytest.mark.asyncio
async def test_creates_stable_hash(anonymizer, sample_case):
    """Test stable hash creation for linking"""

    result = await anonymizer.anonymize_case(sample_case)

    assert 'source_hash' in result.anonymized_data
    assert len(result.anonymized_data['source_hash']) == 16

@pytest.mark.asyncio
async def test_calculates_risk_score(anonymizer, sample_case):
    """Test risk score calculation"""

    result = await anonymizer.anonymize_case(sample_case)

    assert 0 <= result.risk_score <= 1.0

@pytest.mark.asyncio
async def test_preserves_utility(anonymizer, sample_case):
    """Test that utility is preserved (industry, success patterns, etc)"""

    result = await anonymizer.anonymize_case(sample_case)

    org = result.anonymized_data['organization_context']

    # Should preserve
    assert org['industry'] == 'healthcare'
    assert result.anonymized_data['module'] == 'bia'
    assert len(result.anonymized_data['success_patterns']) > 0

@pytest.mark.asyncio
async def test_rare_industry_increases_risk(anonymizer):
    """Test that rare industries increase risk score"""

    case = {
        "organization_context": {
            "industry": "nuclear",  # Rare
            "employee_count": 200
        },
        "module": "bia",
        "workflow_name": "Test"
    }

    result = await anonymizer.anonymize_case(case)

    assert result.risk_score > 0.2  # Should have elevated risk

@pytest.mark.asyncio
async def test_transformation_tracking(anonymizer, sample_case):
    """Test that transformations are tracked"""

    result = await anonymizer.anonymize_case(sample_case)

    assert len(result.transformed_fields) > 0
    assert 'organization_context.location' in result.transformed_fields
