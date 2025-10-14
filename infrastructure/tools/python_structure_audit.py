#!/usr/bin/env python3
"""
Python Project Structure Audit
================================

Finds and reports critical Python import issues:
1. Directories with dashes (cannot be imported)
2. Missing __init__.py files
3. Suggests fixes

Author: AI Platform ISO Team
Date: 2025-10-14
"""

import os
from pathlib import Path
from typing import List, Tuple, Set
import json

# Directories to exclude from audit
EXCLUDE_DIRS = {
    '.git', '__pycache__', 'node_modules', 'venv', '.venv',
    'dist', 'build', '.egg-info', '.pytest_cache',
    '_archive-deprecated-2025-10-10', 'docs-gh-pages', 'docs-website',
    'frontend-twin'  # Frontend projects don't need __init__.py
}

# File patterns that indicate a Python package
PYTHON_INDICATORS = {'.py'}

# Directories that should NOT be Python packages (even if they contain .py files)
NON_PYTHON_DIRS = {
    'scripts', 'tests', 'examples', 'docs', 'migrations',
    'config', 'static', 'templates', 'public'
}


def is_excluded(path: Path) -> bool:
    """Check if path should be excluded from audit"""
    parts = path.parts
    return any(excluded in parts for excluded in EXCLUDE_DIRS)


def has_python_files(directory: Path) -> bool:
    """Check if directory contains Python files"""
    if not directory.is_dir():
        return False

    try:
        for item in directory.iterdir():
            if item.is_file() and item.suffix == '.py':
                return True
    except PermissionError:
        return False

    return False


def has_subdirs_with_python(directory: Path, max_depth: int = 2) -> bool:
    """Check if directory has subdirectories with Python files"""
    if not directory.is_dir() or max_depth <= 0:
        return False

    try:
        for item in directory.iterdir():
            if item.is_dir() and not is_excluded(item):
                if has_python_files(item):
                    return True
                if has_subdirs_with_python(item, max_depth - 1):
                    return True
    except PermissionError:
        return False

    return False


def should_be_python_package(directory: Path) -> bool:
    """Determine if directory should be a Python package"""
    # Has Python files directly
    if has_python_files(directory):
        return True

    # Has subdirectories with Python files
    if has_subdirs_with_python(directory):
        return True

    return False


def find_directories_with_dashes(root: Path) -> List[Tuple[Path, str]]:
    """Find all directories with dashes in their names"""
    issues = []

    for dirpath, dirnames, filenames in os.walk(root):
        # Remove excluded directories from walk
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]

        current = Path(dirpath)

        # Check if current directory has dash
        if '-' in current.name and not is_excluded(current):
            # Check if it's a Python package or should be
            if should_be_python_package(current):
                suggested = current.name.replace('-', '_')
                issues.append((current, suggested))

    return issues


def find_missing_init_files(root: Path) -> List[Tuple[Path, str]]:
    """Find directories that should have __init__.py but don't"""
    issues = []

    for dirpath, dirnames, filenames in os.walk(root):
        # Remove excluded directories from walk
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]

        current = Path(dirpath)

        # Skip if excluded or non-Python directory
        if is_excluded(current) or current.name in NON_PYTHON_DIRS:
            continue

        # Check if should be Python package
        if should_be_python_package(current):
            init_file = current / '__init__.py'
            if not init_file.exists():
                reason = "has Python files" if has_python_files(current) else "has Python subdirectories"
                issues.append((current, reason))

    return issues


def generate_rename_plan(dash_issues: List[Tuple[Path, str]]) -> List[dict]:
    """Generate a plan for renaming directories"""
    plan = []

    for old_path, new_name in dash_issues:
        new_path = old_path.parent / new_name

        # Skip if this is the project root itself
        if old_path == PROJECT_ROOT:
            plan.append({
                'old_path': str(old_path),
                'new_path': str(new_path),
                'old_import': 'PROJECT_ROOT',
                'new_import': 'AI_Platform_ISO (root rename)',
                'priority': 'critical',
                'note': 'Root directory rename - requires special handling'
            })
            continue

        # Find all imports that would be affected
        try:
            relative_old = old_path.relative_to(PROJECT_ROOT)
            relative_new = new_path.relative_to(PROJECT_ROOT) if new_path.is_relative_to(PROJECT_ROOT) else new_path.relative_to(new_path.parent.parent)
        except ValueError:
            # Handle case where path is outside PROJECT_ROOT
            relative_old = old_path.name
            relative_new = new_name

        old_import = str(relative_old).replace('/', '.')
        new_import = str(relative_new).replace('/', '.')

        plan.append({
            'old_path': str(old_path),
            'new_path': str(new_path),
            'old_import': old_import,
            'new_import': new_import,
            'priority': 'high' if 'infrastructure' in str(old_path) or 'intelligent-core' in str(old_path) else 'medium'
        })

    return plan


def generate_init_plan(init_issues: List[Tuple[Path, str]]) -> List[dict]:
    """Generate a plan for creating __init__.py files"""
    plan = []

    for directory, reason in init_issues:
        relative = directory.relative_to(PROJECT_ROOT)

        plan.append({
            'directory': str(directory),
            'relative_path': str(relative),
            'reason': reason,
            'priority': 'high' if 'infrastructure' in str(directory) or 'intelligent-core' in str(directory) else 'medium'
        })

    return plan


def print_report(dash_issues, init_issues, rename_plan, init_plan):
    """Print comprehensive audit report"""
    print("\n" + "=" * 80)
    print("PYTHON PROJECT STRUCTURE AUDIT REPORT")
    print("=" * 80)
    print(f"\nProject Root: {PROJECT_ROOT}")
    print(f"Date: 2025-10-14\n")

    # Summary
    print("=" * 80)
    print("EXECUTIVE SUMMARY")
    print("=" * 80)
    print(f"\n🚨 CRITICAL ISSUES FOUND:")
    print(f"   • Directories with dashes: {len(dash_issues)}")
    print(f"   • Missing __init__.py files: {len(init_issues)}")
    print(f"\n📊 IMPACT:")
    print(f"   • Affected modules cannot be imported")
    print(f"   • Tests will fail")
    print(f"   • Infrastructure coordinator cannot start")
    print(f"\n⚠️  PRIORITY: HIGH - Blocks Phase 1.2 Verification Testing")

    # Dash issues
    print("\n" + "=" * 80)
    print("ISSUE 1: DIRECTORIES WITH DASHES (Cannot be imported in Python)")
    print("=" * 80)
    print(f"\nFound {len(dash_issues)} directories with dashes:\n")

    # Group by priority
    high_priority = [x for x in rename_plan if x['priority'] == 'high']
    medium_priority = [x for x in rename_plan if x['priority'] == 'medium']

    if high_priority:
        print("HIGH PRIORITY (Infrastructure/Intelligent-Core):")
        for i, item in enumerate(high_priority, 1):
            relative = Path(item['old_path']).relative_to(PROJECT_ROOT)
            print(f"{i}. {relative}")
            print(f"   → {item['new_import']}")
        print()

    if medium_priority:
        print(f"MEDIUM PRIORITY ({len(medium_priority)} items) - see audit_report.json for full list")

    # Init issues
    print("\n" + "=" * 80)
    print("ISSUE 2: MISSING __init__.py FILES")
    print("=" * 80)
    print(f"\nFound {len(init_issues)} directories missing __init__.py:\n")

    high_priority_init = [x for x in init_plan if x['priority'] == 'high']
    medium_priority_init = [x for x in init_plan if x['priority'] == 'medium']

    if high_priority_init:
        print("HIGH PRIORITY (Top 20):")
        for i, item in enumerate(high_priority_init[:20], 1):
            print(f"{i}. {item['relative_path']}")
            print(f"   Reason: {item['reason']}")

        if len(high_priority_init) > 20:
            print(f"\n   ... and {len(high_priority_init) - 20} more (see audit_report.json)")
        print()

    # Recommendations
    print("\n" + "=" * 80)
    print("RECOMMENDATIONS")
    print("=" * 80)
    print("\n1. IMMEDIATE ACTION (Day 1):")
    print("   • Fix critical infrastructure directories:")
    print("     - infrastructure/policy-engine → infrastructure/policy_engine")
    print("     - infrastructure/AI-office-infrastructure → infrastructure/ai_office_infrastructure")
    print("     - intelligent-core → intelligent_core")
    print("   • Create missing __init__.py in infrastructure/ and intelligent-core/")
    print("\n2. SHORT TERM (This Week):")
    print("   • Fix all high-priority dash directories")
    print("   • Create all high-priority __init__.py files")
    print("   • Update imports in affected files")
    print("\n3. MEDIUM TERM (Next Week):")
    print("   • Fix remaining directories")
    print("   • Standardize naming convention project-wide")
    print("   • Add linting rules to prevent future issues")

    # Tools
    print("\n" + "=" * 80)
    print("AUTOMATED TOOLS")
    print("=" * 80)
    print("\nGenerated scripts:")
    print("  • fix_dash_directories.sh - Rename all directories")
    print("  • create_init_files.sh - Create all __init__.py files")
    print("  • update_imports.py - Update imports after rename")
    print("  • audit_report.json - Full details")

    print("\n" + "=" * 80 + "\n")


def save_json_report(dash_issues, init_issues, rename_plan, init_plan, output_file):
    """Save detailed report as JSON"""
    report = {
        'audit_date': '2025-10-14',
        'project_root': str(PROJECT_ROOT),
        'summary': {
            'directories_with_dashes': len(dash_issues),
            'missing_init_files': len(init_issues),
            'high_priority_renames': len([x for x in rename_plan if x['priority'] == 'high']),
            'high_priority_inits': len([x for x in init_plan if x['priority'] == 'high'])
        },
        'issues': {
            'directories_with_dashes': rename_plan,
            'missing_init_files': init_plan
        }
    }

    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\n✅ Detailed report saved to: {output_file}")


if __name__ == '__main__':
    PROJECT_ROOT = Path('/Users/MD/AI-Platform-ISO')

    print("\n🔍 Starting Python project structure audit...")
    print(f"📁 Scanning: {PROJECT_ROOT}\n")

    # Run audit
    print("Step 1: Finding directories with dashes...")
    dash_issues = find_directories_with_dashes(PROJECT_ROOT)
    print(f"   Found {len(dash_issues)} issues")

    print("Step 2: Finding missing __init__.py files...")
    init_issues = find_missing_init_files(PROJECT_ROOT)
    print(f"   Found {len(init_issues)} issues")

    print("Step 3: Generating fix plans...")
    rename_plan = generate_rename_plan(dash_issues)
    init_plan = generate_init_plan(init_issues)
    print("   Plans generated")

    # Print report
    print_report(dash_issues, init_issues, rename_plan, init_plan)

    # Save JSON
    output_file = PROJECT_ROOT / 'infrastructure/tools/audit_report.json'
    save_json_report(dash_issues, init_issues, rename_plan, init_plan, output_file)

    print("✅ Audit complete!")
    print("\n📋 Next steps:")
    print("   1. Review audit_report.json")
    print("   2. Run fix_dash_directories.sh (CAREFUL - backs up first)")
    print("   3. Run create_init_files.sh")
    print("   4. Run update_imports.py")
    print("   5. Test imports: python3 -m pytest")
