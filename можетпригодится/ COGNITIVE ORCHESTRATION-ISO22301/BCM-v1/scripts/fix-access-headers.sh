#!/bin/bash

echo "🔧 Fixing access file headers..."

# Fix all access files
for file in /Users/MD/ISO-22301/core/odoo-18.0/addons/bcm_*/security/ir.model.access.csv; do
    if [ -f "$file" ]; then
        # Fix header only if it has the wrong format
        if head -1 "$file" | grep -q "id,name,id,group_id:id"; then
            module=$(basename $(dirname $(dirname "$file")))
            echo "📝 Fixing header in $module..."
            sed -i '' '1s/id,name,id,group_id:id/id,name,model_id,group_id:id/' "$file"
            echo "✅ Fixed $module header"
        fi
    fi
done

echo "🎉 All headers fixed!"