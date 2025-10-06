#!/usr/bin/env python3
"""
Script to move shared/ to infrastructure/shared/
AND update all imports automatically

⚠️ WARNING: Run this ONLY if you're sure you want to move!
⚠️ Backup everything first!

Usage:
    python3 move_shared_script.py --dry-run   # See what would change
    python3 move_shared_script.py --execute   # Actually do it
"""

import os
import re
import shutil
import argparse
from pathlib import Path

BASE_DIR = Path("/Users/MD/AI-Platform-ISO")
SHARED_DIR = BASE_DIR / "shared"
NEW_LOCATION = BASE_DIR / "infrastructure" / "shared"

def find_python_files_with_shared_imports(root_dir):
    """Find all .py files that import from shared"""
    files_to_update = []

    for root, dirs, files in os.walk(root_dir):
        # Skip __pycache__ and hidden directories
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']

        for file in files:
            if file.endswith('.py'):
                filepath = Path(root) / file
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if 'from shared' in content or 'import shared' in content:
                            files_to_update.append(filepath)
                except Exception as e:
                    print(f"⚠️  Error reading {filepath}: {e}")

    return files_to_update

def update_imports_in_file(filepath, dry_run=True):
    """Update shared imports to infrastructure.shared"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content

        # Pattern 1: from shared.module import ...
        content = re.sub(
            r'from shared\.([a-zA-Z_][a-zA-Z0-9_\.]*)',
            r'from infrastructure.shared.\1',
            content
        )

        # Pattern 2: import shared
        content = re.sub(
            r'import shared',
            r'import infrastructure.shared',
            content
        )

        if content != original_content:
            if dry_run:
                print(f"📝 Would update: {filepath}")
                # Show first change as example
                lines_old = original_content.split('\n')
                lines_new = content.split('\n')
                for i, (old, new) in enumerate(zip(lines_old, lines_new)):
                    if old != new:
                        print(f"   Line {i+1}:")
                        print(f"   - {old}")
                        print(f"   + {new}")
                        break
            else:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✅ Updated: {filepath}")
            return True
        return False
    except Exception as e:
        print(f"❌ Error updating {filepath}: {e}")
        return False

def move_shared_directory(dry_run=True):
    """Move shared/ to infrastructure/shared/"""
    if dry_run:
        print(f"📦 Would move:")
        print(f"   FROM: {SHARED_DIR}")
        print(f"   TO:   {NEW_LOCATION}")
        return

    # Create infrastructure directory if not exists
    NEW_LOCATION.parent.mkdir(parents=True, exist_ok=True)

    # Move
    print(f"📦 Moving shared/ to infrastructure/shared/...")
    shutil.move(str(SHARED_DIR), str(NEW_LOCATION))
    print(f"✅ Moved!")

def update_setup_py(dry_run=True):
    """Update setup.py package name"""
    setup_file = NEW_LOCATION / "setup.py" if not dry_run else SHARED_DIR / "setup.py"

    try:
        with open(setup_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Update package name
        new_content = content.replace(
            'name="bcm-shared"',
            'name="bcm-infrastructure-shared"'
        )

        if dry_run:
            if content != new_content:
                print("📝 Would update setup.py:")
                print("   - name=\"bcm-shared\"")
                print("   + name=\"bcm-infrastructure-shared\"")
        else:
            with open(setup_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print("✅ Updated setup.py")
    except Exception as e:
        print(f"⚠️  Could not update setup.py: {e}")

def main():
    parser = argparse.ArgumentParser(description='Move shared/ to infrastructure/shared/')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without doing it')
    parser.add_argument('--execute', action='store_true', help='Actually perform the move')
    args = parser.parse_args()

    if not args.dry_run and not args.execute:
        print("❌ Please specify either --dry-run or --execute")
        parser.print_help()
        return

    dry_run = args.dry_run

    print("=" * 60)
    print("🔄 MOVING shared/ to infrastructure/shared/")
    print("=" * 60)
    print()

    if dry_run:
        print("🔍 DRY RUN MODE - No changes will be made")
    else:
        print("⚠️  EXECUTE MODE - Changes will be made!")
        response = input("Are you sure? Type 'yes' to continue: ")
        if response.lower() != 'yes':
            print("❌ Aborted")
            return

    print()

    # Step 1: Find all files to update
    print("Step 1: Finding Python files with 'from shared' imports...")
    files_to_update = find_python_files_with_shared_imports(BASE_DIR)
    print(f"Found {len(files_to_update)} files to update")
    print()

    # Step 2: Update imports
    print("Step 2: Updating imports in all files...")
    updated_count = 0
    for filepath in files_to_update:
        if update_imports_in_file(filepath, dry_run):
            updated_count += 1
    print(f"{'Would update' if dry_run else 'Updated'} {updated_count} files")
    print()

    # Step 3: Move directory
    print("Step 3: Moving shared/ directory...")
    move_shared_directory(dry_run)
    print()

    # Step 4: Update setup.py
    print("Step 4: Updating setup.py...")
    update_setup_py(dry_run)
    print()

    print("=" * 60)
    if dry_run:
        print("✅ DRY RUN COMPLETE")
        print()
        print("To actually perform the move, run:")
        print("    python3 move_shared_script.py --execute")
    else:
        print("✅ MOVE COMPLETE!")
        print()
        print("Next steps:")
        print("1. Test all services:")
        print("   cd platform-services && ./start.sh")
        print()
        print("2. Run tests:")
        print("   pytest")
        print()
        print("3. If everything works, commit the changes")
        print("   If something breaks, restore from backup!")
    print("=" * 60)

if __name__ == "__main__":
    main()
