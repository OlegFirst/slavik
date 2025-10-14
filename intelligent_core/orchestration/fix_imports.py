#!/usr/bin/env python3
"""
Fix imports in ai-orchestration module
Replace intelligent_core.ai_orchestration with relative imports
"""

import os
import re
from pathlib import Path

def fix_imports_in_file(file_path: Path) -> bool:
    """Fix imports in a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original = content

        # Replace absolute imports with relative imports
        # Pattern 1: from intelligent_core.ai_orchestration.X import Y
        content = re.sub(
            r'from intelligent_core\.ai_orchestration\.([a-z_]+(?:\.[a-z_]+)*) import',
            r'from .\1 import',
            content
        )

        # Pattern 2: from intelligent_core.ai_orchestration import X
        content = re.sub(
            r'from intelligent_core\.ai_orchestration import',
            r'from . import',
            content
        )

        # Pattern 3: import intelligent_core.ai_orchestration.X
        content = re.sub(
            r'import intelligent_core\.ai_orchestration\.([a-z_]+)',
            r'from . import \1',
            content
        )

        if content != original:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Fix imports in all Python files"""
    ai_orchestration_dir = Path(__file__).parent / "ai-orchestration"

    if not ai_orchestration_dir.exists():
        print(f"Directory not found: {ai_orchestration_dir}")
        return

    fixed_count = 0
    total_count = 0

    # Process all Python files
    for py_file in ai_orchestration_dir.rglob("*.py"):
        if py_file.name == "__pycache__":
            continue

        total_count += 1
        if fix_imports_in_file(py_file):
            fixed_count += 1
            print(f"✅ Fixed: {py_file.relative_to(ai_orchestration_dir)}")
        else:
            print(f"⏭️  Skipped: {py_file.relative_to(ai_orchestration_dir)}")

    print(f"\n📊 Summary: {fixed_count}/{total_count} files fixed")

if __name__ == "__main__":
    main()
