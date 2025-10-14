#!/usr/bin/env python3
"""
Intelligent Core - Smoke Test

Tests all 11 services health checks
"""

import asyncio
import httpx
from typing import List, Tuple
from datetime import datetime

# All intelligent-core services
SERVICES = [
    ("ai-orchestration", "http://localhost:8030/health"),
    ("community_intelligence", "http://localhost:8031/health"),
    ("predictive", "http://localhost:8032/health"),
    ("collective", "http://localhost:8033/health"),
    ("coordination-center", "http://localhost:8034/health"),
    ("expertise-center", "http://localhost:8035/health"),
    ("workflow-engine", "http://localhost:8036/health"),
    ("workflow_intelligence", "http://localhost:8037/health"),
    ("ai_workflow_optimizer", "http://localhost:8038/health"),
    ("event_intelligence", "http://localhost:8039/health"),
    ("learning-knowledge", "http://localhost:8040/health"),
]

async def check_service(name: str, url: str) -> Tuple[str, bool, str]:
    """
    Check single service

    Returns:
        (name, is_healthy, message)
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=5.0)
            if response.status_code == 200:
                data = response.json()
                status = data.get('status', 'unknown')
                if status == 'healthy':
                    return (name, True, f"✅ {name}: OK")
                else:
                    return (name, False, f"⚠️ {name}: status={status}")
            else:
                return (name, False, f"❌ {name}: HTTP {response.status_code}")
    except httpx.ConnectError:
        return (name, False, f"❌ {name}: Connection refused")
    except httpx.TimeoutException:
        return (name, False, f"❌ {name}: Timeout")
    except Exception as e:
        return (name, False, f"❌ {name}: {str(e)}")

async def main():
    """Run smoke test"""
    print("=" * 70)
    print("🧪 Intelligent Core - Smoke Test")
    print("=" * 70)
    print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 Testing {len(SERVICES)} services...")
    print()

    # Run all checks in parallel
    results = await asyncio.gather(*[
        check_service(name, url) for name, url in SERVICES
    ])

    # Print results
    healthy = []
    unhealthy = []

    for name, is_healthy, message in results:
        print(message)
        if is_healthy:
            healthy.append(name)
        else:
            unhealthy.append(name)

    # Summary
    print()
    print("=" * 70)
    print("📊 SUMMARY")
    print("=" * 70)
    print(f"Total Services: {len(SERVICES)}")
    print(f"✅ Healthy: {len(healthy)}")
    print(f"❌ Unhealthy: {len(unhealthy)}")
    print(f"Success Rate: {len(healthy)/len(SERVICES)*100:.1f}%")
    print()

    if unhealthy:
        print("⚠️ Unhealthy Services:")
        for service in unhealthy:
            port = next(url.split(':')[-1].split('/')[0] for name, url in SERVICES if name == service)
            print(f"  - {service} (port {port})")
        print()
        print("💡 Troubleshooting:")
        print("  1. Check if service is running: lsof -i :PORT")
        print("  2. Check logs: tail -f /tmp/SERVICE_NAME.log")
        print("  3. Restart service: python3 -m MODULE_NAME.main")
        print()

    if len(healthy) == len(SERVICES):
        print("🎉 ALL SERVICES HEALTHY!")
        print("✅ Ready for MVP launch!")
    else:
        print(f"⚠️ {len(unhealthy)} service(s) need attention")

    print()
    print(f"⏰ Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    # Exit code
    return 0 if len(healthy) == len(SERVICES) else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
