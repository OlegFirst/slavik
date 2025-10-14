"""
E2E Test: AI creates BIA via Coordination Center

Workflow:
1. AI sends Intent to create BIA
2. Coordination Center parses intent
3. Coordination Center translates to API call
4. Coordination Center calls BIA service
5. BIA service creates record
6. Coordination Center returns result
"""
import httpx
import pytest


# Test configuration
COORDINATION_URL = "http://localhost:8004"
PLATFORM_URL = "http://localhost:8000"


@pytest.mark.asyncio
async def test_ai_creates_bia():
    """Test: AI creates BIA process via Coordination Center."""

    # AI Intent
    intent = {
        "action": "create_bia",
        "entity": "process",
        "params": {
            "name": "Patient Admission",
            "description": "Critical patient admission process",
            "criticality": "high",
            "rto_hours": 2,
            "rpo_hours": 1,
        },
        "context": {
            "tenant_id": "hospital_001",
            "user_id": "ai_agent",
            "session_id": "test_session_123",
        },
        "require_approval": False,
    }

    # Execute intent
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{COORDINATION_URL}/coordination/execute",
            json={"intent": intent},
            timeout=30.0,
        )

        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")

        assert response.status_code == 202  # Accepted

        execution = response.json()
        execution_id = execution["execution_id"]

        assert execution["status"] in ["completed", "running"]

        # Poll for completion (if still running)
        if execution["status"] == "running":
            import asyncio
            for _ in range(10):  # Poll up to 10 times
                await asyncio.sleep(1)

                status_response = await client.get(
                    f"{COORDINATION_URL}/coordination/executions/{execution_id}"
                )

                execution = status_response.json()
                print(f"Execution status: {execution['status']}")

                if execution["status"] == "completed":
                    break

        # Verify execution completed
        assert execution["status"] == "completed"
        assert execution["result"] is not None

        # Verify steps
        steps = execution["steps"]
        assert len(steps) >= 3  # validate, execute_api_call, store_result

        # Check each step completed
        for step in steps:
            assert step["status"] == "completed"

        print(f"✅ Test passed! BIA created via Coordination Center")
        print(f"   Execution ID: {execution_id}")
        print(f"   Result: {execution['result']}")


@pytest.mark.asyncio
async def test_list_tools():
    """Test: List available tools."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{COORDINATION_URL}/coordination/tools")

        assert response.status_code == 200

        data = response.json()
        tools = data["tools"]

        assert len(tools) > 0
        assert data["total"] > 0

        # Check BIA tool exists
        bia_tool = next((t for t in tools if t["tool_id"] == "bia_tool"), None)
        assert bia_tool is not None
        assert "create" in bia_tool["supported_actions"]

        print(f"✅ Found {len(tools)} tools")
        for tool in tools:
            print(f"   - {tool['tool_id']}: {tool['name']}")


@pytest.mark.asyncio
async def test_health_check():
    """Test: Health check."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{COORDINATION_URL}/coordination/health")

        assert response.status_code == 200

        health = response.json()
        assert health["status"] == "healthy"
        assert health["services"]["command_interpreter"] is True
        assert health["services"]["execution_tracker"] is True

        print("✅ Health check passed")


if __name__ == "__main__":
    import asyncio

    print("Running E2E tests...\n")

    asyncio.run(test_health_check())
    asyncio.run(test_list_tools())
    asyncio.run(test_ai_creates_bia())

    print("\n✅ All tests passed!")
