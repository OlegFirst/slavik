#!/usr/bin/env python3
"""
Manual API Testing Script for Decision Center

This script tests the Decision Center API manually without pytest.
Run with: python3 test_api_manual.py

Requirements:
- Decision Center API running on http://localhost:8080
- Optional: ANTHROPIC_API_KEY for real AI testing
"""

import asyncio
import httpx
import os
import json
from datetime import datetime


BASE_URL = "http://localhost:8080"


async def test_health_check():
    """Test health check endpoint"""
    print("\n" + "=" * 80)
    print("TEST 1: Health Check")
    print("=" * 80)

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/health")

        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "ai_hub" in data["components"]

        print(" Health check PASSED")


async def test_ai_status():
    """Test AI Hub status endpoint"""
    print("\n" + "=" * 80)
    print("TEST 2: AI Hub Status")
    print("=" * 80)

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/api/v1/ai/status")

        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")

        assert response.status_code == 200
        assert "tier1_strategic" in data
        assert "tier2_operational" in data
        assert "tier3_quick" in data
        assert "api_available" in data

        if os.getenv('ANTHROPIC_API_KEY'):
            print(" AI Hub status - API key detected")
            print(f"   API Available: {data['api_available']}")
            if data['api_available']:
                print(f"   Tier 2 enabled: {data['tier2_operational']['enabled']}")
                print(f"   Tier 3 enabled: {data['tier3_quick']['enabled']}")
        else:
            print("️  AI Hub status - No API key, fallback mode")
            print(f"   API Available: {data['api_available']}")
            print(f"   Fallback mode: {data.get('fallback_mode')}")

        print(" AI status PASSED")


async def test_simple_decision():
    """Test simple auto-approval decision"""
    print("\n" + "=" * 80)
    print("TEST 3: Simple Auto-Approval Decision")
    print("=" * 80)

    request_data = {
        "service": "redis",
        "action": "restart",
        "reason": "High memory usage detected",
        "priority": 2,
        "context": {
            "recovery_attempts": 0,
            "memory_percent": 85
        },
        "requester": "test_script"
    }

    print(f"Request: {json.dumps(request_data, indent=2)}")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/api/v1/decisions",
            json=request_data,
            timeout=30.0
        )

        print(f"\nStatus: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")

        assert response.status_code == 200
        assert data["outcome"] == "approved"
        assert data["decision_type"] == "auto_approved"
        assert "Auto-approved" in data["justification"]

        print(" Simple decision PASSED")
        print(f"   Decision ID: {data['decision_id']}")
        print(f"   Outcome: {data['outcome']}")
        print(f"   Decided by: {data['decided_by']}")


async def test_ai_consultation_decision():
    """Test decision that triggers AI consultation"""
    print("\n" + "=" * 80)
    print("TEST 4: AI Consultation Decision")
    print("=" * 80)

    request_data = {
        "service": "database",
        "action": "restart",
        "reason": "repeated failure with unknown root cause",  # Triggers AI
        "priority": 2,
        "context": {
            "recovery_attempts": 2,
            "downtime_seconds": 180,
            "memory_percent": 95,
            "recent_failures": [
                {"timestamp": "2025-01-15T10:00:00Z", "type": "high_memory"},
                {"timestamp": "2025-01-15T10:05:00Z", "type": "high_memory"}
            ]
        },
        "requester": "test_script"
    }

    print(f"Request: {json.dumps(request_data, indent=2)}")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/api/v1/decisions",
            json=request_data,
            timeout=30.0
        )

        print(f"\nStatus: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")

        assert response.status_code == 200
        assert data["outcome"] in ["approved", "escalated", "pending"]

        if data["decided_by"] == "ai":
            print(" AI consultation TRIGGERED")
            print(f"   Model: {data['metadata'].get('ai_model')}")
            print(f"   Confidence: {data['metadata'].get('confidence')}")
            print(f"   Decision type: {data['decision_type']}")
        else:
            print("️  AI consultation NOT triggered (fallback mode)")
            print(f"   Decision type: {data['decision_type']}")

        print(" AI consultation test PASSED")


async def test_escalation_decision():
    """Test decision that triggers escalation"""
    print("\n" + "=" * 80)
    print("TEST 5: Escalation Decision")
    print("=" * 80)

    request_data = {
        "service": "database",
        "action": "restart",
        "reason": "Service repeatedly failing after multiple restarts",
        "priority": 1,
        "context": {
            "recovery_attempts": 3,  # Exceeds max_auto_attempts
            "downtime_seconds": 300,
            "recent_failures": [1, 2, 3, 4, 5]  # Pattern detected
        },
        "requester": "test_script"
    }

    print(f"Request: {json.dumps(request_data, indent=2)}")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/api/v1/decisions",
            json=request_data,
            timeout=30.0
        )

        print(f"\nStatus: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")

        assert response.status_code == 200
        # Should be escalated or rejected (if no escalation manager)
        assert data["outcome"] in ["escalated", "rejected"]

        if data["outcome"] == "escalated":
            print(" Escalation TRIGGERED")
        else:
            print("️  Escalation → Rejected (no escalation manager in MVP)")

        print(" Escalation test PASSED")


async def test_get_policies():
    """Test get policies endpoint"""
    print("\n" + "=" * 80)
    print("TEST 6: Get Service Policies")
    print("=" * 80)

    service = "database"

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/api/v1/policies/{service}")

        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")

        assert response.status_code == 200
        assert "max_auto_attempts" in data or "default" in data

        print(" Get policies PASSED")


async def run_all_tests():
    """Run all tests"""
    print("\n")
    print("=" * 80)
    print("DECISION CENTER API MANUAL TESTS")
    print("=" * 80)
    print(f"Base URL: {BASE_URL}")
    print(f"Time: {datetime.now().isoformat()}")

    api_key = os.getenv('ANTHROPIC_API_KEY')
    if api_key:
        print(f"API Key:  Detected (will test real AI)")
    else:
        print(f"API Key: ️  Not set (will test fallback only)")

    print("=" * 80)

    try:
        # Run tests in sequence
        await test_health_check()
        await test_ai_status()
        await test_simple_decision()
        await test_ai_consultation_decision()
        await test_escalation_decision()
        await test_get_policies()

        # Summary
        print("\n" + "=" * 80)
        print("ALL TESTS PASSED! ")
        print("=" * 80)

    except Exception as e:
        print("\n" + "=" * 80)
        print(f"TEST FAILED: {e}")
        print("=" * 80)
        raise


if __name__ == "__main__":
    """
    Usage:
        # Start Decision Center first:
        cd infrastructure/decision_center
        python3 -m api.main

        # Then run tests (in another terminal):
        python3 test_api_manual.py

        # With API key:
        ANTHROPIC_API_KEY="sk-ant-..." python3 test_api_manual.py
    """
    asyncio.run(run_all_tests())
