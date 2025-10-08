#!/usr/bin/env python3
"""Test Infrastructure Connections"""

import os
import sys
from pathlib import Path

# Load .env
env_file = Path(__file__).parent.parent / '.env'
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value

print("🔍 Testing Infrastructure Connections")
print("=" * 60)

# Test PostgreSQL
print("\n1. PostgreSQL (Supabase)")
try:
    import subprocess
    db_url = os.getenv('DATABASE_URL')
    if db_url:
        result = subprocess.run(
            ['psql', db_url, '-c', 'SELECT 1'],
            capture_output=True,
            timeout=10
        )
        if result.returncode == 0:
            print("   ✅ Connected successfully")
        else:
            print(f"   ❌ Failed: {result.stderr.decode()[:100]}")
    else:
        print("   ❌ DATABASE_URL not set")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test Redis
print("\n2. Redis (Cloud)")
try:
    redis_url = os.getenv('REDIS_URL')
    if redis_url:
        result = subprocess.run(
            ['redis-cli', '-u', redis_url, 'ping'],
            capture_output=True,
            timeout=10
        )
        if 'PONG' in result.stdout.decode():
            print("   ✅ Connected successfully (PONG)")
        else:
            print(f"   ❌ Failed: {result.stderr.decode()[:100]}")
    else:
        print("   ❌ REDIS_URL not set")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test Qdrant
print("\n3. Qdrant Vector DB (Cloud)")
try:
    import httpx
    qdrant_url = os.getenv('QDRANT_URL')
    qdrant_key = os.getenv('QDRANT_API_KEY')

    if qdrant_url and qdrant_key:
        response = httpx.get(
            f"{qdrant_url}/collections",
            headers={"api-key": qdrant_key},
            timeout=10
        )
        if response.status_code == 200:
            collections = response.json().get('result', {}).get('collections', [])
            print(f"   ✅ Connected successfully")
            print(f"   📦 Collections: {len(collections)}")
            for col in collections:
                print(f"      - {col['name']}")
        else:
            print(f"   ❌ Failed: HTTP {response.status_code}")
    else:
        print("   ❌ QDRANT_URL or QDRANT_API_KEY not set")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test Anthropic API
print("\n4. Anthropic API (AI)")
try:
    import httpx
    api_key = os.getenv('ANTHROPIC_API_KEY')

    if api_key and api_key != 'YOUR_ANTHROPIC_KEY_HERE':
        # Simple validation - just check key format
        if api_key.startswith('sk-ant'):
            print(f"   ✅ API key configured ({api_key[:15]}...)")
        else:
            print(f"   ⚠️  Key format looks wrong")
    else:
        print("   ❌ ANTHROPIC_API_KEY not set")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 60)
print("✅ Infrastructure test complete!")
print("\nNext steps:")
print("  • If all ✅ - infrastructure ready!")
print("  • If any ❌ - check .env file")
print("\nStart services:")
print("  cd intelligent-core/ai-foundation")
print("  uvicorn main:app --host 0.0.0.0 --port 9001")
