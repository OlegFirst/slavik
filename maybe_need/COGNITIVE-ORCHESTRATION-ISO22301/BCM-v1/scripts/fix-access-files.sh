#!/bin/bash

echo "🔧 Fixing BCM module access files - standardizing format..."

# List of modules with old format
modules=(
    "bcm_audit"
    "bcm_bia"
    "bcm_clients"
    "bcm_config"
    "bcm_context"
    "bcm_core"
    "bcm_incident"
    "bcm_incident_management"
    "bcm_intelligent_base"
    "bcm_kpi"
    "bcm_plans"
    "bcm_reporting"
    "bcm_risk_management"
    "bcm_scenario_hub"
    "bcm_templates"
)

for module in "${modules[@]}"; do
    file="/Users/MD/ISO-22301/core/odoo-18.0/addons/${module}/security/ir.model.access.csv"
    if [ -f "$file" ]; then
        echo "📝 Fixing $module..."
        # Replace model_id/id with model_id and group_id/id with group_id:id
        sed -i '' 's/model_id\/id/model_id/g' "$file"
        sed -i '' 's/group_id\/id/group_id:id/g' "$file"
        # Remove model_ prefix from model references
        sed -i '' 's/model_\([a-zA-Z_]*\)/\1/g' "$file"
        echo "✅ Fixed $module"
    fi
done

echo "🎉 All BCM module access files standardized!"