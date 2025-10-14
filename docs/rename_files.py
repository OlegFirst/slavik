#!/usr/bin/env python3
"""
Script to rename all HTML files from dashes to underscores
Usage: cd /Users/MD/AI-Platform-ISO/docs && python3 rename_files.py
"""

import os
import shutil
from pathlib import Path

# Change to docs directory
os.chdir('/Users/MD/AI-Platform-ISO/docs')

# List of files to rename
files_to_rename = [
    'business-flow.html',
    'bcm-philosophy.html',
    'decision-center.html',
    'mio-manager.html',
    'platform-overview.html',
    'workflow-intelligence.html',
    'ai-foundation.html',
    'eventbus-choreography.html',
    'collective-intelligence.html',
    'expertise-center.html',
    'predictive-intelligence.html',
    'governance-layer.html',
    'ace-service.html',
    'service-catalog-visual.html',
    'platform-services-overview.html'
]

print("="*60)
print("ПЕРЕИМЕНОВАНИЕ HTML ФАЙЛОВ")
print("="*60)
print()

renamed_count = 0
errors = []

for old_name in files_to_rename:
    try:
        new_name = old_name.replace('-', '_')

        if os.path.exists(old_name):
            shutil.move(old_name, new_name)
            print(f"✓ {old_name:35} → {new_name}")
            renamed_count += 1
        else:
            print(f"✗ Файл не найден: {old_name}")
            errors.append(f"File not found: {old_name}")
    except Exception as e:
        print(f"✗ Ошибка: {old_name} - {str(e)}")
        errors.append(f"{old_name}: {str(e)}")

print()
print("="*60)
print(f"РЕЗУЛЬТАТ: Переименовано {renamed_count} из {len(files_to_rename)} файлов")
print("="*60)

if errors:
    print(f"\n❌ Ошибки ({len(errors)}):")
    for err in errors:
        print(f"  - {err}")
else:
    print("\n✅ ВСЕ ФАЙЛЫ УСПЕШНО ПЕРЕИМЕНОВАНЫ!")
    print()
    print("Следующий шаг:")
    print("  python3 update_links.py")
