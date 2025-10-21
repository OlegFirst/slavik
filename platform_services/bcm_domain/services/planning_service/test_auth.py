"""
Test script for JWT authentication in Planning Service

This script demonstrates how to use the authentication system

Note: Run this from the parent directory:
  cd /Users/MD/ISO-22301—копия/services/SERVICES/BCM/
  python3 -m planning_service.test_auth

Or install the package and run normally.
"""

import asyncio
from pydantic import BaseModel, Field
from typing import List

# Standalone UserContext for testing (mirrors auth.models.UserContext)
class UserContext(BaseModel):
    """User context extracted from JWT token"""
    user_id: str = Field(..., description="User ID from JWT token")
    tenant_id: str = Field(..., description="Tenant ID for multi-tenancy")
    email: str = Field(..., description="User email address")
    roles: List[str] = Field(default_factory=list, description="User roles")
    is_superadmin: bool = Field(default=False, description="Superadmin flag")


async def test_dev_mode():
    """Test development mode authentication"""
    print("Testing Development Mode (UserContext Model)...")
    print("=" * 60)

    # Simulate what dev mode headers would create
    try:
        user = UserContext(
            user_id="test-user-123",
            tenant_id="test-tenant-456",
            email="test-user-123@dev.local",
            roles=["bcm_manager", "strategy_editor"],
            is_superadmin=False
        )
        print(" Dev mode user context created!")
        print(f"   User ID: {user.user_id}")
        print(f"   Tenant ID: {user.tenant_id}")
        print(f"   Email: {user.email}")
        print(f"   Roles: {user.roles}")
        print(f"   Is Superadmin: {user.is_superadmin}")
        print("\n   This simulates X-Dev-User and X-Dev-Tenant headers")
    except Exception as e:
        print(f" Dev mode simulation failed: {e}")

    print()


async def test_token_extraction():
    """Test token claim extraction"""
    print("Testing Token Claim Extraction (Simulated)...")
    print("=" * 60)

    # Simulate JWT token claims
    token_claims = {
        "sub": "user-abc-123",
        "tenant_id": "tenant-xyz-789",
        "email": "user@example.com",
        "roles": ["bcm_manager", "strategy_approver"],
        "is_superadmin": False
    }

    try:
        user = UserContext(
            user_id=token_claims["sub"],
            tenant_id=token_claims["tenant_id"],
            email=token_claims["email"],
            roles=token_claims["roles"],
            is_superadmin=token_claims["is_superadmin"]
        )
        print(" Token claims extracted successfully!")
        print(f"   User ID: {user.user_id}")
        print(f"   Tenant ID: {user.tenant_id}")
        print(f"   Email: {user.email}")
        print(f"   Roles: {user.roles}")
        print("\n   This simulates JWT token validation")
    except Exception as e:
        print(f" Token extraction failed: {e}")

    print()


async def test_user_context_model():
    """Test UserContext model"""
    print("Testing UserContext Model...")
    print("=" * 60)

    user = UserContext(
        user_id="user-abc",
        tenant_id="tenant-xyz",
        email="test@example.com",
        roles=["bcm_manager", "strategy_editor"],
        is_superadmin=False
    )

    print(" UserContext model created successfully!")
    print(f"   Model: {user}")
    print(f"   JSON: {user.model_dump_json(indent=2)}")

    print()


async def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("JWT Authentication Test Suite - Planning Service")
    print("=" * 60 + "\n")

    await test_user_context_model()
    await test_dev_mode()
    await test_token_extraction()

    print("=" * 60)
    print("Test suite completed!")
    print("=" * 60 + "\n")

    print(" How Authentication Works:")
    print("   1. Dev Mode: Use X-Dev-User and X-Dev-Tenant headers")
    print("   2. Production: Use 'Authorization: Bearer <token>' header")
    print("   3. Token must include: sub/user_id, tenant_id, email, roles")
    print("   4. Configure JWT_PUBLIC_KEY in .env for production")
    print()
    print(" To test with running service:")
    print("   curl -X GET http://localhost:8011/strategies/ \\")
    print("     -H 'X-Dev-User: user-123' \\")
    print("     -H 'X-Dev-Tenant: tenant-456'")
    print()


if __name__ == "__main__":
    asyncio.run(main())
