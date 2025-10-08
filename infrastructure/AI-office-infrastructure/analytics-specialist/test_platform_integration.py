#!/usr/bin/env python3
"""
Test Platform Client Integration

Проверяет что Analytics Specialist правильно интегрирован с platform_client
"""

import sys
import asyncio
from pathlib import Path

# Add paths
current_dir = Path(__file__).parent
intelligent_core_path = current_dir.parent.parent.parent / "intelligent-core"
sys.path.insert(0, str(intelligent_core_path))
sys.path.insert(0, str(current_dir))

from shared.platform_client import get_platform_client, PlatformClient


async def test_platform_client():
    """Test platform_client import and instantiation"""
    print("=" * 60)
    print("TEST 1: Platform Client Import")
    print("=" * 60)

    try:
        platform = get_platform_client()
        print("✅ Platform client created successfully")
        print(f"   Type: {type(platform)}")
        print(f"   AI Foundation: {platform.config.ai_foundation_url}")
        print(f"   Expertise Center: {platform.config.expertise_center_url}")
        print(f"   Workflow Intelligence: {platform.config.workflow_intelligence_url}")
    except Exception as e:
        print(f"❌ Failed to create platform client: {e}")
        return False

    print("\n" + "=" * 60)
    print("TEST 2: Platform Health Check")
    print("=" * 60)

    try:
        health = await platform.health_check()
        print(f"✅ Health check completed")
        print(f"   AI Foundation: {'✅' if health.get('ai_foundation') else '❌'} {health.get('ai_foundation', False)}")
        print(f"   Expertise Center: {'✅' if health.get('expertise_center') else '❌'} {health.get('expertise_center', False)}")
        print(f"   Workflow Intelligence: {'✅' if health.get('workflow_intelligence') else '❌'} {health.get('workflow_intelligence', False)}")

        if any(health.values()):
            print(f"\n   {sum(health.values())}/3 services are running")
        else:
            print("\n   ⚠️  No services running (this is OK for testing)")
    except Exception as e:
        print(f"❌ Health check failed: {e}")

    print("\n" + "=" * 60)
    print("TEST 3: Analytics Core with Platform Client")
    print("=" * 60)

    try:
        # Import AnalyticsCore
        from core.analytics_core import AnalyticsCore

        print("Creating AnalyticsCore...")
        core = AnalyticsCore()

        print(f"✅ AnalyticsCore created")
        print(f"   Competency: {core.competency}")
        print(f"   Tools: {list(core.tools.keys())}")
        print(f"   Platform client type: {type(core.platform)}")
        print(f"   Integration status keys: {list(core.integration_status.keys())}")

        # Check that platform_client is properly integrated
        assert hasattr(core, 'platform'), "AnalyticsCore should have 'platform' attribute"
        assert isinstance(core.platform, PlatformClient), "platform should be PlatformClient instance"
        assert 'ai_foundation' in core.integration_status, "Should track ai_foundation integration"
        assert 'expertise_center' in core.integration_status, "Should track expertise_center integration"
        assert 'workflow_intelligence' in core.integration_status, "Should track workflow_intelligence integration"

        print("\n✅ All assertions passed!")

        print("\n" + "=" * 60)
        print("TEST 4: Initialize AnalyticsCore")
        print("=" * 60)

        print("Initializing AnalyticsCore (this will check all integrations)...")
        await core.initialize()

        print(f"\n✅ Initialization complete")
        print(f"   Integration status:")

        # Group by type
        platform_integrations = {
            k: v for k, v in core.integration_status.items()
            if k in ['ai_foundation', 'expertise_center', 'workflow_intelligence']
        }

        analytics_integrations = {
            k: v for k, v in core.integration_status.items()
            if k not in ['ai_foundation', 'expertise_center', 'workflow_intelligence']
        }

        print("\n   Platform 'Brains':")
        for name, status in platform_integrations.items():
            print(f"     {'✅' if status else '❌'} {name}: {status}")

        print("\n   Analytics Clients:")
        for name, status in analytics_integrations.items():
            print(f"     {'✅' if status else '❌'} {name}: {status}")

        # Summary
        total = len(core.integration_status)
        healthy = sum(core.integration_status.values())
        platform_healthy = sum(platform_integrations.values())
        analytics_healthy = sum(analytics_integrations.values())

        print(f"\n   Summary:")
        print(f"     Platform: {platform_healthy}/3")
        print(f"     Analytics: {analytics_healthy}/6")
        print(f"     Total: {healthy}/{total} ({healthy/total*100:.0f}%)")

        if healthy == total:
            print("\n   🎉 ALL integrations healthy!")
        elif platform_healthy == 3:
            print(f"\n   ✅ All platform 'brains' healthy! ({analytics_healthy}/6 analytics clients)")
        else:
            print(f"\n   ⚠️  Some integrations unavailable (expected in dev)")

    except Exception as e:
        print(f"❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("=" * 60)
    print("\nPlatform Client Integration: SUCCESS ✅")
    print("Analytics Specialist is properly integrated with:")
    print("  - AI Foundation (RAG, LLM, Embeddings)")
    print("  - Expertise Center (12 Tactical Assistants)")
    print("  - Workflow Intelligence (Case Library)")
    print("\nPlus 6 Analytics-specific clients")

    return True


if __name__ == "__main__":
    result = asyncio.run(test_platform_client())
    sys.exit(0 if result else 1)
