#!/usr/bin/env python3
"""
Fix Infrastructure Directories with Dashes
==========================================

Safely renames infrastructure directories from kebab-case to snake_case.

Features:
- Uses git mv to preserve history
- Dry-run mode
- Automatic backup
- Rollback capability
- Progress reporting

Author: AI Platform ISO Team
Date: 2025-10-14
"""

import os
import json
import subprocess
from pathlib import Path
from typing import List, Dict, Tuple
import argparse
from datetime import datetime
import shutil

PROJECT_ROOT = Path('/Users/MD/AI-Platform-ISO')
AUDIT_REPORT_PATH = PROJECT_ROOT / 'infrastructure/tools/audit_report.json'
BACKUP_ROOT = Path('/Users/MD/AI-Platform-ISO-backup-20251014')


def load_infrastructure_renames() -> List[Dict]:
    """Load infrastructure directories that need renaming from audit report"""
    with open(AUDIT_REPORT_PATH, 'r') as f:
        report = json.load(f)

    # Get all rename plans
    all_renames = report['issues']['directories_with_dashes']

    # Filter for infrastructure only, high priority
    infra_renames = [
        item for item in all_renames
        if 'infrastructure' in item['old_path']
        and item['priority'] == 'high'
        and '_archive' not in item['old_path']  # Skip archives
        and 'tests/' not in item['old_path']  # Skip test dirs for now
    ]

    return infra_renames


def check_git_status() -> bool:
    """Check if we're in a git repository with clean state"""
    try:
        result = subprocess.run(
            ['git', 'status', '--porcelain'],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=True
        )

        if result.stdout.strip():
            print("⚠️  WARNING: Git working directory is not clean!")
            print("Uncommitted changes detected:")
            print(result.stdout)
            return False

        return True
    except subprocess.CalledProcessError:
        print("❌ ERROR: Not in a git repository or git command failed")
        return False


def create_backup(dry_run: bool = True) -> bool:
    """Create backup of entire project"""
    if dry_run:
        print(f"  [DRY-RUN] Would create backup at {BACKUP_ROOT}")
        return True

    if BACKUP_ROOT.exists():
        print(f"  ⏭️  Backup already exists at {BACKUP_ROOT}")
        return True

    print(f"  📦 Creating backup at {BACKUP_ROOT}...")
    try:
        shutil.copytree(
            PROJECT_ROOT,
            BACKUP_ROOT,
            ignore=shutil.ignore_patterns(
                '.git', '__pycache__', '*.pyc', 'node_modules',
                'venv', '.venv', '*.egg-info', '.pytest_cache'
            )
        )
        print(f"  ✅ Backup created successfully")
        return True
    except Exception as e:
        print(f"  ❌ Backup failed: {e}")
        return False


def rename_directory(old_path: str, new_path: str, dry_run: bool = True) -> Tuple[bool, str]:
    """
    Rename directory using git mv

    Returns:
        (success, message)
    """
    old_path_obj = Path(old_path)
    new_path_obj = Path(new_path)

    # Validate
    if not old_path_obj.exists():
        return (False, f"Source doesn't exist: {old_path}")

    if new_path_obj.exists():
        return (False, f"Target already exists: {new_path}")

    if dry_run:
        return (True, f"Would rename: {old_path_obj.name} → {new_path_obj.name}")

    # Use git mv to preserve history
    try:
        # Make sure parent directory exists
        new_path_obj.parent.mkdir(parents=True, exist_ok=True)

        result = subprocess.run(
            ['git', 'mv', str(old_path_obj), str(new_path_obj)],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=True
        )

        return (True, f"Renamed: {old_path_obj.name} → {new_path_obj.name}")

    except subprocess.CalledProcessError as e:
        # If git mv fails, try regular move (might not be in git)
        try:
            shutil.move(str(old_path_obj), str(new_path_obj))
            return (True, f"Renamed (non-git): {old_path_obj.name} → {new_path_obj.name}")
        except Exception as e2:
            return (False, f"Failed: {e2}")


def sort_renames_by_depth(renames: List[Dict]) -> List[Dict]:
    """
    Sort renames by depth (deepest first) to avoid conflicts

    Example: Rename /a/b/c-d before /a/b-c
    """
    return sorted(renames, key=lambda x: x['old_path'].count('/'), reverse=True)


def main():
    parser = argparse.ArgumentParser(
        description='Fix infrastructure directories with dashes'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without executing'
    )
    parser.add_argument(
        '--execute',
        action='store_true',
        help='Actually rename directories (creates backup first)'
    )
    parser.add_argument(
        '--skip-backup',
        action='store_true',
        help='Skip backup creation (dangerous!)'
    )
    parser.add_argument(
        '--skip-git-check',
        action='store_true',
        help='Skip git clean check (use if you have pending changes)'
    )
    parser.add_argument(
        '--yes', '-y',
        action='store_true',
        help='Automatically answer yes to confirmation prompts'
    )

    args = parser.parse_args()

    dry_run = not args.execute
    mode_str = "DRY-RUN" if dry_run else "EXECUTE"

    print("\n" + "=" * 80)
    print(f"FIX INFRASTRUCTURE DIRECTORIES - {mode_str} MODE")
    print("=" * 80)
    print()

    # Load renames
    if not AUDIT_REPORT_PATH.exists():
        print(f"❌ ERROR: Audit report not found at {AUDIT_REPORT_PATH}")
        return 1

    print(f"Loading rename plan from audit report...")
    renames = load_infrastructure_renames()
    print(f"Found {len(renames)} infrastructure directories to rename")
    print()

    if not renames:
        print("✅ No infrastructure directories need renaming!")
        return 0

    # Sort by depth (deepest first)
    renames = sort_renames_by_depth(renames)

    # Check git status (only in execute mode)
    if not dry_run and not args.skip_git_check:
        print("Checking git status...")
        if not check_git_status():
            print("\n⚠️  Git working directory is not clean!")
            print("Use --skip-git-check to bypass this check")
            return 1
        print()

    # Create backup (only in execute mode)
    if not dry_run and not args.skip_backup:
        print("Creating backup...")
        if not create_backup(dry_run=False):
            print("\n❌ Backup failed! Aborting.")
            return 1
        print()

    # Preview renames
    print("=" * 80)
    print("RENAME PLAN")
    print("=" * 80)
    print()

    for i, rename in enumerate(renames, 1):
        old_rel = Path(rename['old_path']).relative_to(PROJECT_ROOT)
        new_rel = Path(rename['new_path']).relative_to(PROJECT_ROOT)
        print(f"{i}. {old_rel}")
        print(f"   → {new_rel}")
        print()

    if dry_run:
        print("=" * 80)
        print("⚠️  DRY-RUN MODE - No changes will be made")
        print("=" * 80)
        print()
        print("To execute, run:")
        print(f"  python3 {Path(__file__).name} --execute")
        print()
        return 0

    # Confirm
    if not args.yes:
        print("=" * 80)
        print("⚠️  READY TO EXECUTE")
        print("=" * 80)
        print()
        print(f"This will rename {len(renames)} directories using git mv")
        print(f"Backup location: {BACKUP_ROOT}")
        print()
        response = input("Proceed? [y/N]: ")
        if response.lower() != 'y':
            print("Aborted.")
            return 1
        print()
    else:
        print("\n🚀 Auto-confirming (--yes flag)")
        print()

    # Execute renames
    print("=" * 80)
    print("EXECUTING RENAMES")
    print("=" * 80)
    print()

    success_count = 0
    fail_count = 0
    failed_items = []

    for i, rename in enumerate(renames, 1):
        old_path = rename['old_path']
        new_path = rename['new_path']

        old_rel = Path(old_path).relative_to(PROJECT_ROOT)
        print(f"[{i}/{len(renames)}] {old_rel}")

        success, message = rename_directory(old_path, new_path, dry_run=False)

        if success:
            print(f"  ✅ {message}")
            success_count += 1
        else:
            print(f"  ❌ {message}")
            fail_count += 1
            failed_items.append({
                'old_path': old_path,
                'new_path': new_path,
                'error': message
            })

        print()

    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()
    print(f"Total: {len(renames)}")
    print(f"Successful: {success_count}")
    print(f"Failed: {fail_count}")
    print()

    if failed_items:
        print("Failed items:")
        for item in failed_items:
            print(f"  - {Path(item['old_path']).name}: {item['error']}")
        print()

    if fail_count > 0:
        print("=" * 80)
        print("⚠️  SOME RENAMES FAILED")
        print("=" * 80)
        print()
        print("To rollback:")
        print(f"  rm -rf {PROJECT_ROOT}")
        print(f"  cp -r {BACKUP_ROOT} {PROJECT_ROOT}")
        print()
        return 1

    print("=" * 80)
    print("✅ ALL RENAMES COMPLETED")
    print("=" * 80)
    print()
    print("Next steps:")
    print("  1. Update imports: python3 infrastructure/tools/update_infrastructure_imports.py")
    print("  2. Test imports: python3 -c 'from infrastructure.policy_engine import get_policy_engine'")
    print("  3. Run Test 1.1: python3 infrastructure/policy_engine/test_policy_engine_loading.py")
    print("  4. Commit: git add . && git commit -m 'Rename infrastructure directories to snake_case'")
    print()

    return 0


if __name__ == '__main__':
    exit(main())
