#!/usr/bin/env python3
"""
Environment verification script
Проверяет что все необходимые переменные окружения настроены
"""

import os
import sys
from typing import Dict, List, Tuple

# Required environment variables для 3 core modules
REQUIRED_VARS = {
    "critical": [
        "DATABASE_URL",
        "REDIS_URL",
        "QDRANT_URL",
        "QDRANT_API_KEY",
    ],
    "ai_services": [
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
    ],
    "security": [
        "JWT_SECRET",
    ],
    "optional": [
        "EVENTBUS_TRANSPORT",
        "PROMETHEUS_URL",
        "GRAFANA_URL",
    ]
}

def check_var(var_name: str) -> Tuple[bool, str]:
    """Check if environment variable is set and not empty"""
    value = os.getenv(var_name)
    if not value:
        return False, "❌ NOT SET"

    # Mask sensitive values
    if "KEY" in var_name or "SECRET" in var_name or "PASSWORD" in var_name:
        masked = value[:8] + "..." if len(value) > 8 else "***"
        return True, f"✅ SET ({masked})"

    return True, f"✅ SET ({value[:50]}...)" if len(value) > 50 else f"✅ SET ({value})"

def verify_environment() -> bool:
    """Verify all environment variables"""
    print("🔍 Environment Verification")
    print("=" * 60)

    all_ok = True

    # Check critical vars
    print("\n📌 CRITICAL (Required for core modules):")
    for var in REQUIRED_VARS["critical"]:
        ok, status = check_var(var)
        print(f"  {var:30} {status}")
        if not ok:
            all_ok = False

    # Check AI service vars
    print("\n🤖 AI SERVICES (At least one required):")
    ai_ok = False
    for var in REQUIRED_VARS["ai_services"]:
        ok, status = check_var(var)
        print(f"  {var:30} {status}")
        if ok:
            ai_ok = True

    if not ai_ok:
        print("  ⚠️  WARNING: No AI service keys configured!")
        all_ok = False

    # Check security vars
    print("\n🔒 SECURITY:")
    for var in REQUIRED_VARS["security"]:
        ok, status = check_var(var)
        print(f"  {var:30} {status}")
        if not ok:
            all_ok = False

    # Check optional vars
    print("\n📝 OPTIONAL (Recommended but not required):")
    for var in REQUIRED_VARS["optional"]:
        ok, status = check_var(var)
        print(f"  {var:30} {status}")

    print("\n" + "=" * 60)

    if all_ok:
        print("✅ Environment verification PASSED!")
        print("\nℹ️  Next steps:")
        print("  1. Run: ./infrastructure/scripts/test_connections.sh")
        print("  2. Run: ./infrastructure/scripts/start_all.sh")
        return True
    else:
        print("❌ Environment verification FAILED!")
        print("\n⚠️  Missing required variables. Please:")
        print("  1. Copy .env.example to .env")
        print("  2. Fill in all required values")
        print("  3. Run this script again")
        return False

def generate_jwt_secret():
    """Generate a random JWT secret"""
    import secrets
    return secrets.token_hex(32)

def suggest_fixes():
    """Suggest how to fix missing variables"""
    print("\n💡 Quick Fixes:")

    if not os.getenv("JWT_SECRET"):
        secret = generate_jwt_secret()
        print(f"\n  JWT_SECRET (add to .env):")
        print(f"  JWT_SECRET={secret}")

    if not os.getenv("REDIS_URL"):
        print(f"\n  REDIS_URL (local Redis):")
        print(f"  REDIS_URL=redis://localhost:6379")
        print(f"  # Or run: docker run -d -p 6379:6379 redis:7-alpine")

    if not os.getenv("EVENTBUS_TRANSPORT"):
        print(f"\n  EVENTBUS_TRANSPORT (start simple):")
        print(f"  EVENTBUS_TRANSPORT=memory")
        print(f"  # Change to 'redis' for production")

if __name__ == "__main__":
    success = verify_environment()

    if not success:
        suggest_fixes()
        sys.exit(1)

    sys.exit(0)
