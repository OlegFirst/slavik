#!/usr/bin/env python3
"""
Create Missing __init__.py Files
=================================

Safely creates all missing __init__.py files in Python packages.

Features:
- Dry-run mode (preview changes)
- Scope filtering (high-priority only, or all)
- Smart content generation
- Progress reporting
- Safe execution (checks before writing)

Author: AI Platform ISO Team
Date: 2025-10-14
"""

import os
import json
from pathlib import Path
from typing import List, Dict
import argparse
from datetime import datetime

# Load audit report
AUDIT_REPORT_PATH = Path(__file__).parent / 'audit_report.json'


def load_audit_report() -> Dict:
    """Load the audit report JSON"""
    with open(AUDIT_REPORT_PATH, 'r') as f:
        return json.load(f)


def generate_init_content(directory: Path, reason: str) -> str:
    """
    Generate appropriate content for __init__.py based on directory context

    Args:
        directory: Directory path
        reason: Reason why __init__.py is needed

    Returns:
        Content for __init__.py file
    """
    dir_name = directory.name
    parent_parts = directory.parts

    # Determine module type from path
    is_api = 'api' in dir_name.lower()
    is_models = 'models' in dir_name.lower()
    is_services = 'services' in dir_name.lower()
    is_utils = 'utils' in dir_name.lower()
    is_config = 'config' in dir_name.lower()
    is_tests = 'tests' in str(directory) or 'test' in dir_name

    # Base content
    content = f'"""\n{dir_name.replace("_", " ").replace("-", " ").title()} Module\n'

    # Add description based on type
    if is_api:
        content += '\nAPI endpoints and routes.\n'
    elif is_models:
        content += '\nData models and schemas.\n'
    elif is_services:
        content += '\nBusiness logic and service implementations.\n'
    elif is_utils:
        content += '\nUtility functions and helpers.\n'
    elif is_config:
        content += '\nConfiguration and settings.\n'
    elif is_tests:
        content += '\nTest suite.\n'
    else:
        content += f'\n{dir_name} package.\n'

    content += '"""\n\n'

    # For test directories, minimal content
    if is_tests:
        return content

    # For non-test packages, add __all__ placeholder
    content += '# TODO: Add imports and define __all__\n'
    content += '__all__ = []\n'

    return content


def create_init_file(directory: Path, reason: str, dry_run: bool = True) -> bool:
    """
    Create __init__.py file in directory

    Args:
        directory: Directory to create __init__.py in
        reason: Reason for creation
        dry_run: If True, don't actually create file

    Returns:
        True if file was created (or would be created in dry-run)
    """
    init_file = directory / '__init__.py'

    # Check if already exists
    if init_file.exists():
        print(f"  ⏭️  SKIP: {init_file} (already exists)")
        return False

    # Check if directory exists
    if not directory.exists():
        print(f"  ❌ ERROR: {directory} (directory doesn't exist)")
        return False

    # Generate content
    content = generate_init_content(directory, reason)

    if dry_run:
        print(f"  ✅ WOULD CREATE: {init_file}")
        print(f"     Content preview: {len(content)} bytes")
        return True
    else:
        try:
            with open(init_file, 'w') as f:
                f.write(content)
            print(f"  ✅ CREATED: {init_file}")
            return True
        except Exception as e:
            print(f"  ❌ ERROR: {init_file} - {e}")
            return False


def filter_by_scope(issues: List[Dict], scope: str) -> List[Dict]:
    """
    Filter issues by scope

    Args:
        issues: List of __init__.py issues
        scope: 'high', 'medium', or 'all'

    Returns:
        Filtered list
    """
    if scope == 'all':
        return issues
    elif scope == 'high':
        return [item for item in issues if item['priority'] == 'high']
    elif scope == 'medium':
        return [item for item in issues if item['priority'] == 'medium']
    else:
        raise ValueError(f"Invalid scope: {scope}")


def main():
    parser = argparse.ArgumentParser(
        description='Create missing __init__.py files in Python packages'
    )
    parser.add_argument(
        '--scope',
        choices=['high', 'medium', 'all'],
        default='high',
        help='Scope of files to create (default: high)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without creating files'
    )
    parser.add_argument(
        '--execute',
        action='store_true',
        help='Actually create files (default is dry-run)'
    )

    args = parser.parse_args()

    # Determine mode
    dry_run = not args.execute
    mode_str = "DRY-RUN" if dry_run else "EXECUTE"

    print("\n" + "=" * 80)
    print(f"CREATE MISSING __init__.py FILES - {mode_str} MODE")
    print("=" * 80)
    print(f"\nScope: {args.scope}")
    print(f"Mode: {'Preview only' if dry_run else '⚠️  WILL CREATE FILES'}")
    print()

    # Load audit report
    if not AUDIT_REPORT_PATH.exists():
        print(f"❌ ERROR: Audit report not found at {AUDIT_REPORT_PATH}")
        print("Run python_structure_audit.py first!")
        return 1

    print(f"Loading audit report from {AUDIT_REPORT_PATH}...")
    report = load_audit_report()

    # Get __init__.py issues
    init_issues = report['issues']['missing_init_files']
    print(f"Total issues in report: {len(init_issues)}")

    # Filter by scope
    filtered_issues = filter_by_scope(init_issues, args.scope)
    print(f"Issues in scope '{args.scope}': {len(filtered_issues)}")
    print()

    if not filtered_issues:
        print("No issues to fix!")
        return 0

    # Create files
    print("=" * 80)
    print("CREATING FILES")
    print("=" * 80)
    print()

    created = 0
    skipped = 0
    errors = 0

    for i, issue in enumerate(filtered_issues, 1):
        directory = Path(issue['directory'])
        reason = issue['reason']
        priority = issue['priority']

        print(f"[{i}/{len(filtered_issues)}] {directory.relative_to(Path.cwd()) if directory.is_relative_to(Path.cwd()) else directory}")
        print(f"  Priority: {priority} | Reason: {reason}")

        result = create_init_file(directory, reason, dry_run=dry_run)

        if result:
            created += 1
        else:
            if (directory / '__init__.py').exists():
                skipped += 1
            else:
                errors += 1

        print()

    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()
    print(f"Total issues: {len(filtered_issues)}")
    if dry_run:
        print(f"Would create: {created}")
    else:
        print(f"Created: {created}")
    print(f"Skipped (already exist): {skipped}")
    print(f"Errors: {errors}")
    print()

    if dry_run:
        print("=" * 80)
        print("⚠️  DRY-RUN MODE - No files were created")
        print("=" * 80)
        print()
        print("To actually create files, run:")
        print(f"  python3 {Path(__file__).name} --scope={args.scope} --execute")
        print()
    else:
        print("=" * 80)
        print("✅ FILES CREATED")
        print("=" * 80)
        print()
        print("Next steps:")
        print("  1. Test imports: python3 -c 'import infrastructure.policy_engine'")
        print("  2. Run tests: python3 -m pytest")
        print("  3. Commit changes: git add . && git commit -m 'Add missing __init__.py files'")
        print()

    return 0 if errors == 0 else 1


if __name__ == '__main__':
    exit(main())
