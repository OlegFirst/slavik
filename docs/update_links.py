#!/usr/bin/env python3
"""
Script to update all href links from dashes to underscores
Usage: cd /Users/MD/AI-Platform-ISO/docs && python3 update_links.py
"""

import os
import re
from pathlib import Path

# Change to docs directory
os.chdir('/Users/MD/AI-Platform-ISO/docs')

# Mapping of old names to new names
link_replacements = {
    'business-flow.html': 'business_flow.html',
    'bcm-philosophy.html': 'bcm_philosophy.html',
    'decision-center.html': 'decision_center.html',
    'mio-manager.html': 'mio_manager.html',
    'platform-overview.html': 'platform_overview.html',
    'workflow-intelligence.html': 'workflow_intelligence.html',
    'ai-foundation.html': 'ai_foundation.html',
    'eventbus-choreography.html': 'eventbus_choreography.html',
    'collective-intelligence.html': 'collective_intelligence.html',
    'expertise-center.html': 'expertise_center.html',
    'predictive-intelligence.html': 'predictive_intelligence.html',
    'governance-layer.html': 'governance_layer.html',
    'ace-service.html': 'ace_service.html',
    'service-catalog-visual.html': 'service_catalog_visual.html',
    'platform-services-overview.html': 'platform_services_overview.html'
}

print("="*60)
print("ОБНОВЛЕНИЕ ССЫЛОК В HTML ФАЙЛАХ")
print("="*60)
print()

# Get all HTML files
html_files = list(Path('.').glob('*.html'))
print(f"Найдено HTML файлов: {len(html_files)}")
print()

updated_files = 0
total_replacements = 0

for html_file in html_files:
    try:
        # Read file content
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content
        file_replacements = 0

        # Replace all old links with new links
        for old_link, new_link in link_replacements.items():
            # Match href="old-name.html"
            old_pattern = f'href="{old_link}"'
            new_pattern = f'href="{new_link}"'

            count = content.count(old_pattern)
            if count > 0:
                content = content.replace(old_pattern, new_pattern)
                file_replacements += count

        # Write back if changes were made
        if content != original_content:
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f" {html_file.name:35} - {file_replacements} замен")
            updated_files += 1
            total_replacements += file_replacements
        else:
            print(f"  {html_file.name:35} - без изменений")

    except Exception as e:
        print(f" Ошибка в {html_file}: {str(e)}")

print()
print("="*60)
print(f"РЕЗУЛЬТАТ:")
print(f"  Обновлено файлов: {updated_files}")
print(f"  Всего замен: {total_replacements}")
print("="*60)

# Verify no dashes remain in internal links
print()
print("Проверка оставшихся дефисов в ссылках...")
remaining_dashes = 0

for html_file in html_files:
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find href="something-with-dash.html"
    matches = re.findall(r'href="([a-z]+-[a-z-]+\.html)"', content)
    if matches:
        print(f"️  {html_file.name}: {matches}")
        remaining_dashes += len(matches)

if remaining_dashes == 0:
    print(" Дефисов не найдено - все ссылки обновлены!")
else:
    print(f"️  Найдено {remaining_dashes} ссылок с дефисами")

print()
print("Готово! Откройте index.html в браузере для проверки.")
