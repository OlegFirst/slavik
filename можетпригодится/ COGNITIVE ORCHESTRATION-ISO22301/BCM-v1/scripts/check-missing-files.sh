#!/bin/bash

# Check for missing files in BCM modules
echo "🔍 Checking BCM modules for missing files..."

for module in /Users/MD/ISO-22301/core/odoo-18.0/addons/bcm_*; do
  if [ -f "$module/__manifest__.py" ]; then
    module_name=$(basename "$module")
    echo "=== Checking $module_name ==="

    cd "$module"
    python3 -c "
import os
exec(open('__manifest__.py').read())
missing = []
for file_path in locals().get('__data__', locals().get('data', [])):
    if not os.path.exists(file_path):
        missing.append(file_path)
        print(f'❌ MISSING: {file_path}')
if missing:
    print(f'📊 Total missing: {len(missing)}')
else:
    print('✅ All files exist')
    " 2>/dev/null
    echo ""
  fi
done