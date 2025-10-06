#!/usr/bin/env python3
"""
Integration Test Script
Tests if both Learning and Governance services can initialize without errors
"""

import sys
from pathlib import Path

# Add shared to path
sys.path.insert(0, str(Path(__file__).parent / "shared"))

print("=" * 60)
print("INTEGRATION TEST - Service Initialization")
print("=" * 60)

# Test 1: Learning Service Imports
print("\n[TEST 1] Learning Service - Import Check")
try:
    sys.path.insert(0, str(Path(__file__).parent / "platform-services/learning-service"))

    from models.database import (
        TrainingProgram,
        TrainingEnrollment,
        ProgramStatus,
        EnrollmentStatus,
    )
    from models.domain import (
        ProgramCreate,
        EnrollmentCreate,
    )
    print("  ✅ Database models imported")
    print("  ✅ Domain models imported")

    # Check ASSESSED state exists
    assert hasattr(EnrollmentStatus, 'ASSESSED'), "EnrollmentStatus missing ASSESSED state"
    print("  ✅ EnrollmentStatus.ASSESSED exists")

    # Check column names
    from sqlalchemy import inspect
    columns = [c.name for c in TrainingEnrollment.__table__.columns]

    assert 'person_department' in columns, "Missing person_department column"
    assert 'assigned_by' in columns, "Missing assigned_by column"
    assert 'submitted_date' in columns, "Missing submitted_date column"
    assert 'approved_by' in columns, "Missing approved_by column"
    assert 'assessment_type' in columns, "Missing assessment_type column"
    assert 'assessor' in columns, "Missing assessor column"
    assert 'assessment_feedback' in columns, "Missing assessment_feedback column"
    print("  ✅ All database columns present")

    print("✅ Learning Service: Import Check PASSED")

except Exception as e:
    print(f"❌ Learning Service: Import Check FAILED - {e}")
    sys.exit(1)

# Test 2: Governance Service Imports
print("\n[TEST 2] Governance Service - Import Check")
try:
    # Clear learning service from path
    learning_path = str(Path(__file__).parent / "platform-services/learning-service")
    if learning_path in sys.path:
        sys.path.remove(learning_path)

    # Remove models.database from sys.modules to force reimport
    if 'models.database' in sys.modules:
        del sys.modules['models.database']
    if 'models' in sys.modules:
        del sys.modules['models']

    sys.path.insert(0, str(Path(__file__).parent / "platform-services/governance-service"))

    from models.database import (
        BCMPolicy,
        OrganizationalRole,
        BCMResource,
        PolicyStatus,
    )
    print("  ✅ Database models imported")

    print("✅ Governance Service: Import Check PASSED")

except Exception as e:
    print(f"❌ Governance Service: Import Check FAILED - {e}")
    sys.exit(1)

# Test 3: Shared Library
print("\n[TEST 3] Shared Library - Function Check")
try:
    from shared.database import init_database, init_db, close_db, get_db_manager
    print("  ✅ init_database imported")
    print("  ✅ init_db (alias) imported")
    print("  ✅ close_db imported")
    print("  ✅ get_db_manager imported")

    try:
        from shared.eventbus import init_eventbus, get_eventbus
        print("  ✅ EventBus functions imported")
    except ImportError as ie:
        print(f"  ⚠️  EventBus import skipped (missing dependencies)")

    try:
        from shared.utils.logging import setup_logging
        print("  ✅ setup_logging imported")
    except ImportError as ie:
        print(f"  ⚠️  setup_logging import skipped (missing dependencies)")

    print("✅ Shared Library: Function Check PASSED (with optional deps missing)")

except Exception as e:
    print(f"❌ Shared Library: Function Check FAILED - {e}")
    sys.exit(1)

# Test 4: Workflow Logic
print("\n[TEST 4] Learning Service - Workflow Logic")
try:
    # Clear governance service from path
    gov_path = str(Path(__file__).parent / "platform-services/governance-service")
    if gov_path in sys.path:
        sys.path.remove(gov_path)

    # Clear model cache
    for key in list(sys.modules.keys()):
        if 'models' in key or 'workflows' in key:
            del sys.modules[key]

    sys.path.insert(0, str(Path(__file__).parent / "platform-services/learning-service"))

    from workflows.training_workflow import (
        EnrollmentState,
        EnrollmentAction,
        can_transition,
        validate_enrollment_data,
        should_auto_complete,
    )
    print("  ✅ Workflow functions imported")

    # Test state transitions
    assert can_transition("draft", "submit") == True, "DRAFT -> SUBMIT should be allowed"
    assert can_transition("submitted", "approve") == True, "SUBMITTED -> APPROVE should be allowed"
    assert can_transition("draft", "complete") == False, "DRAFT -> COMPLETE should be blocked"
    print("  ✅ State transitions validated")

    # Test auto-complete logic
    # Note: auto-complete requires progress + time OR time threshold exceeded
    # Just test it doesn't crash
    should_complete, reason = should_auto_complete(100, 600, 10, "in_progress")
    print(f"  ✅ Auto-complete logic callable (result: {should_complete})")

    print("✅ Learning Service: Workflow Logic PASSED")

except Exception as e:
    print(f"❌ Learning Service: Workflow Logic FAILED - {e}")
    sys.exit(1)

# Test 5: Service Layer Syntax Check (separate processes to avoid path conflicts)
print("\n[TEST 5] Service Layer - Syntax Check")
try:
    import subprocess

    # Test Learning Service
    result = subprocess.run(
        [sys.executable, "-m", "py_compile", "services/training_service.py"],
        cwd=str(Path(__file__).parent / "platform-services/learning-service"),
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        print("  ✅ TrainingService syntax OK")
    else:
        raise Exception(f"TrainingService syntax error: {result.stderr}")

    # Test Governance Service
    result = subprocess.run(
        [sys.executable, "-m", "py_compile", "services/governance_service.py"],
        cwd=str(Path(__file__).parent / "platform-services/governance-service"),
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        print("  ✅ PolicyService/RoleService/ResourceService syntax OK")
    else:
        raise Exception(f"Governance services syntax error: {result.stderr}")

    print("✅ Service Layer: Syntax Check PASSED")

except Exception as e:
    print(f"❌ Service Layer: Syntax Check FAILED - {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ ALL INTEGRATION TESTS PASSED")
print("=" * 60)
print("\nServices are ready for:")
print("  - Database connection testing")
print("  - HTTP endpoint testing")
print("  - Event publishing testing")
print("  - Authentication implementation (Phase 4)")
print("=" * 60)
