"""Tests for Risk Assessor"""
import pytest
import sys
sys.path.insert(0, '../src')

from risk_assessment import RiskAssessor

def test_risk_assessment():
    """Test risk assessment"""
    assessor = RiskAssessor()
    result = assessor.assess({'likelihood': 8, 'impact': 9})

    assert result['score'] == 72
    assert result['level'] == 'high'

def test_risk_level():
    """Test risk level calculation"""
    assessor = RiskAssessor()

    # Test different levels
    assert assessor._get_risk_level(90) == 'critical'
    assert assessor._get_risk_level(70) == 'high'
    assert assessor._get_risk_level(50) == 'medium'
    assert assessor._get_risk_level(30) == 'low'
