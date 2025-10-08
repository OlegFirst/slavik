#!/usr/bin/env python3
"""
Verify EventBus integration across all platform services
"""

import os
import re
from pathlib import Path

def check_eventbus_integration():
    """Check EventBus integration in intelligent-core services"""

    services_dir = Path("/Users/MD/AI-Platform-ISO/intelligent-core")

    # Services from docker-compose.yml
    services = {
        "intelligent-core-main": services_dir,
        "ai-foundation": services_dir / "ai-foundation" / "learning-knowledge",
        "community-intelligence": services_dir / "community_intelligence",
        "ai-orchestration": services_dir / "orchestration" / "ai-orchestration",
        "coordination-center": services_dir / "orchestration" / "coordination-center"
    }

    results = []

    for service_name, service_path in services.items():
        main_py = service_path / "main.py"
        if not main_py.exists():
            # Try api/main.py
            main_py = service_path / "api" / "main.py"

        if main_py.exists():
            content = main_py.read_text()

            has_import = bool(re.search(r'from shared\.eventbus import|import.*eventbus', content, re.IGNORECASE))
            has_init = bool(re.search(r'init_eventbus|get_eventbus|EventBusClient', content))
            has_publish = bool(re.search(r'\.publish\(|eventbus\.publish', content))
            has_subscribe = bool(re.search(r'\.subscribe\(|eventbus\.subscribe', content))

            integration_status = "✅" if (has_import or has_init) else "❌"

            results.append({
                "service": service_name,
                "status": integration_status,
                "has_import": has_import,
                "has_init": has_init,
                "has_publish": has_publish,
                "has_subscribe": has_subscribe,
                "main_py": str(main_py)
            })
        else:
            results.append({
                "service": service_name,
                "status": "⚠️",
                "has_import": False,
                "has_init": False,
                "has_publish": False,
                "has_subscribe": False,
                "main_py": f"NOT FOUND: {main_py}"
            })

    # Print results
    print("\n" + "="*80)
    print("EventBus Integration Status - Intelligent Core Services")
    print("="*80)

    for result in results:
        print(f"\n{result['status']} {result['service']}")
        print(f"   Import:    {'✓' if result['has_import'] else '✗'}")
        print(f"   Init:      {'✓' if result['has_init'] else '✗'}")
        print(f"   Publish:   {'✓' if result['has_publish'] else '✗'}")
        print(f"   Subscribe: {'✓' if result['has_subscribe'] else '✗'}")
        print(f"   Main: {result['main_py']}")

    # Summary
    integrated = sum(1 for r in results if r['status'] == "✅")
    total = len(results)

    print("\n" + "="*80)
    print(f"Summary: {integrated}/{total} services have EventBus integration")
    print("="*80)

    # Check RabbitMQ configuration
    print("\n" + "="*80)
    print("RabbitMQ Configuration Check")
    print("="*80)

    env_file = Path("/Users/MD/AI-Platform-ISO/.env")
    if env_file.exists():
        env_content = env_file.read_text()
        if "RABBITMQ_URL" in env_content:
            rabbitmq_url = [line for line in env_content.split('\n') if 'RABBITMQ_URL=' in line and not line.startswith('#')]
            if rabbitmq_url:
                print(f"✅ RABBITMQ_URL configured: {rabbitmq_url[0]}")
            else:
                print("❌ RABBITMQ_URL not configured in .env")
        else:
            print("❌ RABBITMQ_URL not found in .env")
    else:
        print("❌ .env file not found")

    # Check docker-compose
    docker_compose = services_dir / "docker-compose.yml"
    if docker_compose.exists():
        compose_content = docker_compose.read_text()
        if "rabbitmq:" in compose_content and not re.search(r'#.*rabbitmq:', compose_content):
            print("✅ RabbitMQ configured in docker-compose.yml")
        else:
            print("❌ RabbitMQ not configured in docker-compose.yml")

    return integrated, total

if __name__ == "__main__":
    integrated, total = check_eventbus_integration()
    print(f"\n{'🎉 PASS' if integrated == total else '⚠️  INCOMPLETE'}: {integrated}/{total} services integrated")
