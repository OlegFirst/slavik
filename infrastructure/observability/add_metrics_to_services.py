#!/usr/bin/env python3
"""
Add /metrics endpoint to all intelligent-core services
========================================================

This script automatically adds Prometheus metrics endpoint to services
that don't have it yet.

Usage:
    python3 add_metrics_to_services.py --dry-run  # Preview changes
    python3 add_metrics_to_services.py            # Apply changes
"""

import os
import sys
from pathlib import Path
from typing import List, Tuple

# Services that need /metrics endpoint
SERVICES_TO_UPDATE = [
    {
        "name": "expertise-center",
        "path": "intelligent-core/expertise-center/service/main.py",
        "port": 8035
    },
    {
        "name": "community-intelligence",
        "path": "intelligent-core/community_intelligence/main.py",
        "port": 8031
    },
    {
        "name": "predictive",
        "path": "intelligent-core/predictive/main.py",
        "port": 8032
    },
    {
        "name": "collective",
        "path": "intelligent-core/collective/main.py",
        "port": 8033
    },
    {
        "name": "coordination-center",
        "path": "intelligent-core/orchestration/coordination-center/main.py",
        "port": 8034
    },
    {
        "name": "workflow-engine",
        "path": "intelligent-core/workflow-engine/workflow/api/main.py",
        "port": 8036
    },
    {
        "name": "ai-workflow-optimizer",
        "path": "intelligent-core/ai_workflow_optimizer/main.py",
        "port": 8038
    },
    {
        "name": "event-intelligence",
        "path": "intelligent-core/event_intelligence/main.py",
        "port": 8039
    },
    {
        "name": "ai-foundation",
        "path": "intelligent-core/ai-foundation/learning-knowledge/api/main.py",
        "port": 8040
    }
]

# Metrics endpoint template
METRICS_IMPORT = """from prometheus_client import generate_latest, CONTENT_TYPE_LATEST"""

METRICS_ENDPOINT = """
@app.get("/metrics")
async def metrics():
    \"\"\"Prometheus metrics endpoint for monitoring\"\"\"
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )
"""


def find_project_root() -> Path:
    """Find the AI-Platform-ISO root directory"""
    current = Path.cwd()

    # Try current directory
    if (current / "intelligent-core").exists():
        return current

    # Try parent directories
    for parent in current.parents:
        if (parent / "intelligent-core").exists():
            return parent

    # Default fallback
    return Path("/Users/MD/AI-Platform-ISO")


def check_has_metrics(file_path: Path) -> bool:
    """Check if file already has /metrics endpoint"""
    if not file_path.exists():
        return False

    content = file_path.read_text()
    return "@app.get(\"/metrics\")" in content or "prometheus_client" in content


def analyze_imports(content: str) -> Tuple[int, bool]:
    """
    Find where to insert prometheus import

    Returns:
        (line_number, needs_response_import)
    """
    lines = content.split('\n')

    # Find last import line
    last_import_line = 0
    has_response_import = False

    for i, line in enumerate(lines):
        stripped = line.strip()

        if stripped.startswith('from fastapi import'):
            if 'Response' in stripped:
                has_response_import = True
            last_import_line = i
        elif stripped.startswith('import ') or stripped.startswith('from '):
            last_import_line = i

    return last_import_line, has_response_import


def analyze_endpoints(content: str) -> int:
    """Find where to insert metrics endpoint (before last line or at EOF)"""
    lines = content.split('\n')

    # Find last @app decorator
    last_endpoint = 0

    for i, line in enumerate(lines):
        if line.strip().startswith('@app.'):
            last_endpoint = i

    # If found endpoints, add after the last one
    if last_endpoint > 0:
        # Find end of last endpoint function
        for i in range(last_endpoint, len(lines)):
            # Look for next function or EOF
            if i > last_endpoint and (lines[i].startswith('def ') or lines[i].startswith('@')):
                return i

        # If no next function found, add at end
        return len(lines)

    # No endpoints found, add at end
    return len(lines)


def add_metrics_to_file(file_path: Path, dry_run: bool = False) -> bool:
    """
    Add /metrics endpoint to a service file

    Returns:
        True if changes were made (or would be made in dry-run)
    """
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return False

    if check_has_metrics(file_path):
        print(f"✅ Already has metrics: {file_path.name}")
        return False

    content = file_path.read_text()

    # Analyze where to insert
    import_line, needs_response = analyze_imports(content)
    endpoint_line = analyze_endpoints(content)

    lines = content.split('\n')

    # Add Response import if needed
    if needs_response:
        print(f"   └─ Response already imported")
    else:
        # Find FastAPI import and add Response
        for i, line in enumerate(lines):
            if 'from fastapi import' in line and 'Response' not in line:
                # Add Response to existing import
                lines[i] = line.rstrip() + ", Response"
                print(f"   └─ Added Response to FastAPI import")
                break

    # Add prometheus import after last import
    lines.insert(import_line + 1, METRICS_IMPORT)
    print(f"   └─ Added prometheus_client import at line {import_line + 1}")

    # Add metrics endpoint
    # Adjust endpoint_line because we inserted import
    adjusted_endpoint_line = endpoint_line + 1
    lines.insert(adjusted_endpoint_line, METRICS_ENDPOINT)
    print(f"   └─ Added /metrics endpoint at line {adjusted_endpoint_line}")

    new_content = '\n'.join(lines)

    if dry_run:
        print(f"   └─ [DRY RUN] Would write changes to {file_path}")
        return True
    else:
        # Create backup
        backup_path = file_path.with_suffix('.py.bak')
        file_path.rename(backup_path)
        print(f"   └─ Backup created: {backup_path.name}")

        # Write new content
        file_path.write_text(new_content)
        print(f"   └─ ✅ Changes written to {file_path.name}")
        return True


def main():
    """Main function"""
    dry_run = '--dry-run' in sys.argv

    if dry_run:
        print("🔍 DRY RUN MODE - No files will be modified\n")
    else:
        print("⚡ APPLYING CHANGES - Files will be modified\n")

    project_root = find_project_root()
    print(f"📁 Project root: {project_root}\n")

    modified_count = 0
    skipped_count = 0
    error_count = 0

    for service in SERVICES_TO_UPDATE:
        print(f"🔧 {service['name']} (port {service['port']})")

        file_path = project_root / service['path']

        try:
            if add_metrics_to_file(file_path, dry_run):
                modified_count += 1
            else:
                skipped_count += 1
        except Exception as e:
            print(f"   └─ ❌ ERROR: {e}")
            error_count += 1

        print()

    # Summary
    print("=" * 60)
    print("📊 SUMMARY:")
    print(f"   ✅ Modified: {modified_count}")
    print(f"   ⏭️  Skipped: {skipped_count}")
    print(f"   ❌ Errors: {error_count}")
    print("=" * 60)

    if dry_run and modified_count > 0:
        print("\n💡 Run without --dry-run to apply changes")
    elif modified_count > 0:
        print("\n✅ All changes applied successfully!")
        print("\n📋 Next steps:")
        print("   1. Restart services to enable /metrics endpoints")
        print("   2. Test metrics: curl http://localhost:PORT/metrics")
        print("   3. Restart Prometheus to scrape new metrics")
        print("      cd infrastructure/observability")
        print("      docker-compose -f docker-compose.monitoring.yml restart prometheus")
        print("   4. Check Grafana dashboards: http://localhost:3000")


if __name__ == "__main__":
    main()
