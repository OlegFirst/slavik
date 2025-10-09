#!/usr/bin/env python3
"""
Comprehensive EventBus Integration Verification
================================================

Scans ALL intelligent-core services and verifies:
- EventBus import
- init_event_bus() call
- publish_event() usage
- @subscribe_to() usage
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple

def scan_file(file_path: Path) -> Dict:
    """Scan a single file for EventBus integration"""
    try:
        content = file_path.read_text()
    except Exception as e:
        return {"error": str(e)}

    # Check for imports
    has_import = bool(
        re.search(r'from shared\.event_bus import', content) or
        re.search(r'from shared\.eventbus import', content)
    )

    # Check for initialization
    has_init = bool(
        re.search(r'init_event_bus\(', content) or
        re.search(r'await init_event_bus', content)
    )

    # Check for publish
    has_publish = bool(
        re.search(r'await publish_event\(', content) or
        re.search(r'publish_event\(', content)
    )

    # Check for subscribe decorators
    has_subscribe = bool(
        re.search(r'@subscribe_to\(', content)
    )

    # Count occurrences
    publish_count = len(re.findall(r'publish_event\(', content))
    subscribe_count = len(re.findall(r'@subscribe_to\(', content))

    return {
        "has_import": has_import,
        "has_init": has_init,
        "has_publish": has_publish,
        "has_subscribe": has_subscribe,
        "publish_count": publish_count,
        "subscribe_count": subscribe_count
    }


def find_all_services() -> List[Tuple[str, Path]]:
    """Find all services in intelligent-core"""
    intelligent_core = Path("/Users/MD/AI-Platform-ISO/intelligent-core")

    services = []

    # Top-level main.py
    main_py = intelligent_core / "main.py"
    if main_py.exists():
        services.append(("intelligent-core-main", main_py))

    # Subdirectories with main.py
    for subdir in intelligent_core.iterdir():
        if not subdir.is_dir():
            continue

        # Skip __pycache__, .git, venv, etc
        if subdir.name.startswith('.') or subdir.name in ['__pycache__', 'venv', 'node_modules']:
            continue

        # Direct main.py
        main_py = subdir / "main.py"
        if main_py.exists():
            services.append((subdir.name, main_py))

        # Check service/ subdirectory
        service_main = subdir / "service" / "main.py"
        if service_main.exists():
            services.append((subdir.name, service_main))

        # Check api/ subdirectory
        api_main = subdir / "api" / "main.py"
        if api_main.exists():
            services.append((subdir.name, api_main))

        # Check nested directories (e.g., orchestration/ai-orchestration)
        for nested in subdir.iterdir():
            if nested.is_dir() and not nested.name.startswith('.'):
                nested_main = nested / "main.py"
                if nested_main.exists():
                    services.append((f"{subdir.name}/{nested.name}", nested_main))

    return services


def main():
    """Main verification"""
    print("=" * 80)
    print("EventBus Integration Verification - ALL Intelligent Core Services")
    print("=" * 80)

    services = find_all_services()

    # Sort by name
    services.sort(key=lambda x: x[0])

    results = []

    for service_name, main_py in services:
        scan_result = scan_file(main_py)

        if "error" in scan_result:
            status = "❌"
        elif scan_result["has_import"] or scan_result["has_init"]:
            status = "✅"
        else:
            status = "⚠️"

        results.append({
            "service": service_name,
            "status": status,
            "main_py": str(main_py),
            **scan_result
        })

    # Print results
    for r in results:
        print(f"\n{r['status']} {r['service']}")
        print(f"   Path: {r['main_py']}")

        if "error" in r:
            print(f"   Error: {r['error']}")
        else:
            print(f"   Import:    {'✓' if r['has_import'] else '✗'}")
            print(f"   Init:      {'✓' if r['has_init'] else '✗'}")
            print(f"   Publish:   {'✓' if r['has_publish'] else '✗'} ({r['publish_count']} calls)")
            print(f"   Subscribe: {'✓' if r['has_subscribe'] else '✗'} ({r['subscribe_count']} decorators)")

    # Summary
    integrated = sum(1 for r in results if r['status'] == '✅')
    total = len(results)
    warning = sum(1 for r in results if r['status'] == '⚠️')
    error = sum(1 for r in results if r['status'] == '❌')

    print("\n" + "=" * 80)
    print("Summary")
    print("=" * 80)
    print(f"✅ Integrated:     {integrated}/{total} ({integrated/total*100:.0f}%)")
    print(f"⚠️  Not integrated: {warning}/{total}")
    print(f"❌ Errors:         {error}/{total}")

    # Event statistics
    total_publishers = sum(r.get('publish_count', 0) for r in results)
    total_subscribers = sum(r.get('subscribe_count', 0) for r in results)

    print("\n" + "=" * 80)
    print("Event Statistics")
    print("=" * 80)
    print(f"📤 Total publish_event calls: {total_publishers}")
    print(f"📥 Total @subscribe_to decorators: {total_subscribers}")

    # Integration health
    integration_health = (integrated / total) * 100 if total > 0 else 0

    print("\n" + "=" * 80)
    print(f"Integration Health: {integration_health:.0f}%")
    print("=" * 80)

    if integration_health >= 80:
        print("🎉 EXCELLENT - Event-driven architecture fully deployed")
    elif integration_health >= 50:
        print("👍 GOOD - Most services integrated, some work remaining")
    elif integration_health >= 30:
        print("⚠️  NEEDS WORK - Many services still need integration")
    else:
        print("❌ CRITICAL - EventBus integration incomplete")

    print("\n" + "=" * 80)

    # Success/failure
    if integration_health >= 80:
        print("✅ PASS")
    else:
        print(f"⚠️  INCOMPLETE - {total - integrated} services need EventBus integration")

    print("=" * 80)


if __name__ == "__main__":
    main()
