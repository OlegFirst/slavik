"""
Test script for JWT authentication
Run this to verify JWT implementation works correctly
"""

import sys
import os
from pathlib import Path

# Set PYTHONPATH to include shared directory
shared_path = str(Path(__file__).parent.parent.parent / "shared")
sys.path.insert(0, shared_path)
os.environ['PYTHONPATH'] = shared_path

# Import JWT functions directly from the module file
import importlib.util
jwt_handler_path = Path(shared_path) / "auth" / "jwt_handler.py"
spec = importlib.util.spec_from_file_location("jwt_handler", jwt_handler_path)
jwt_handler = importlib.util.module_from_spec(spec)
spec.loader.exec_module(jwt_handler)

create_access_token = jwt_handler.create_access_token
verify_token = jwt_handler.verify_token
get_current_user = jwt_handler.get_current_user


def test_jwt_functions():
    """Test JWT token creation, verification, and user extraction"""

    print("=" * 60)
    print("Testing JWT Authentication")
    print("=" * 60)

    # Test 1: Create token
    print("\n1. Creating JWT token...")
    token = create_access_token(
        user_id='test_user_123',
        tenant_id='tenant_456',
        roles=['admin', 'bcm_manager']
    )
    print(f"    Token created successfully!")
    print(f"   Token (first 60 chars): {token[:60]}...")

    # Test 2: Verify token
    print("\n2. Verifying JWT token...")
    try:
        payload = verify_token(token)
        print(f"    Token verified successfully!")
        print(f"   Payload: {payload}")
    except Exception as e:
        print(f"    Verification failed: {e}")
        return False

    # Test 3: Extract user from token
    print("\n3. Extracting user information...")
    try:
        user = get_current_user(token)
        print(f"    User extracted successfully!")
        print(f"   User ID: {user['user_id']}")
        print(f"   Tenant ID: {user['tenant_id']}")
        print(f"   Roles: {user['roles']}")
    except Exception as e:
        print(f"    User extraction failed: {e}")
        return False

    # Test 4: Test with invalid token
    print("\n4. Testing with invalid token...")
    try:
        verify_token("invalid.token.here")
        print("    Should have failed!")
        return False
    except Exception as e:
        print(f"    Correctly rejected invalid token")

    print("\n" + "=" * 60)
    print(" All JWT tests passed!")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = test_jwt_functions()
    sys.exit(0 if success else 1)
