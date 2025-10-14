#!/usr/bin/env python3
"""
Tests for Database operations
"""

import pytest
import sys
from pathlib import Path
from datetime import datetime

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database import init_database, get_db
from models.database import (
    AnalysisReport, AnalysisType,
    ServiceDiscovery,
    SecurityScanResult,
    MIOAction, ActionType, ActionStatus,
    IssueTracking, IssueSeverity
)
from repositories import ReportsRepository, ActionsRepository


@pytest.fixture(scope="module")
def setup_database():
    """Setup test database"""
    # Initialize database
    init_database()
    yield
    # Cleanup if needed


def test_database_initialization(setup_database):
    """Test that database tables are created"""
    with get_db() as db:
        # Test that we can query tables
        result = db.query(AnalysisReport).count()
        assert result >= 0  # Should not raise error


def test_save_security_scan(setup_database):
    """Test saving security scan result"""
    scan_id = ReportsRepository.save_security_scan(
        high_count=3,
        medium_count=5,
        low_count=2,
        high_issues=[
            {"issue_text": "SQL injection", "filename": "test.py", "line_number": 42}
        ],
        all_issues=[]
    )

    assert scan_id is not None
    assert len(scan_id) > 0


def test_create_action(setup_database):
    """Test creating MIO action"""
    action_id = ActionsRepository.create_action(
        action_type=ActionType.ALERT_SENT,
        target_service="test-service",
        action_details={"test": "data"},
        triggered_by="test"
    )

    assert action_id is not None
    assert len(action_id) > 0


def test_create_issue(setup_database):
    """Test creating issue"""
    issue_id = ActionsRepository.create_issue(
        issue_type="security",
        severity=IssueSeverity.HIGH,
        description="Test security issue",
        affected_service="test-service",
        issue_details={"test": "data"}
    )

    assert issue_id is not None
    assert len(issue_id) > 0


def test_get_open_issues(setup_database):
    """Test getting open issues"""
    issues = ActionsRepository.get_open_issues()
    assert isinstance(issues, list)


def test_action_stats(setup_database):
    """Test action statistics"""
    stats = ActionsRepository.get_action_stats()
    assert "total" in stats
    assert "completed" in stats
    assert "failed" in stats
    assert "pending" in stats


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
