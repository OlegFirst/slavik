#!/bin/bash

# Safe BCM Module Installation Script
# Устанавливает модули по одному с изоляцией ошибок

ODOO_CONFIG="/etc/odoo/odoo.conf"
DB_NAME="odoo"
LOG_FILE="/tmp/bcm_install.log"

echo "🚀 Safe BCM Module Installation Started $(date)" | tee $LOG_FILE

# BCM модули в порядке зависимостей
BCM_MODULES=(
    "bcm_base"
    "bcm_core"
    "bcm_clients"
    "bcm_governance"
    "bcm_incident"
    "bcm_incident_management"
    "bcm_risk_management"
    "bcm_bia"
    "bcm_plans"
    "bcm_training"
    "bcm_exercise"
    "bcm_templates"
    "bcm_reporting"
    "bcm_kpi"
    "bcm_audit"
    "bcm_portal"
    "bcm_scenario_hub"
    "bcm_community"
    "bcm_config"
    "bcm_context"
    "bcm_intelligent_base"
    "bcm_admin_website"
    "bcm_ai_control"
)

install_module_safe() {
    local module_name=$1
    local attempt=1
    local max_attempts=3

    echo "📦 Installing module: $module_name (attempt $attempt/$max_attempts)" | tee -a $LOG_FILE

    while [ $attempt -le $max_attempts ]; do
        # Try to install the module
        if docker exec iso-22301-odoo-1 odoo shell -d $DB_NAME --no-http <<EOF 2>&1 | tee -a $LOG_FILE
try:
    env['ir.module.module'].search([('name', '=', '$module_name')]).button_immediate_install()
    env.cr.commit()
    print("✅ SUCCESS: Module $module_name installed")
except Exception as e:
    print(f"❌ ERROR: Module $module_name failed: {e}")
    env.cr.rollback()
    import traceback
    traceback.print_exc()
EOF
        then
            if grep -q "SUCCESS: Module $module_name installed" $LOG_FILE; then
                echo "✅ Module $module_name installed successfully" | tee -a $LOG_FILE
                return 0
            fi
        fi

        echo "⚠️  Attempt $attempt failed for $module_name" | tee -a $LOG_FILE
        attempt=$((attempt + 1))

        if [ $attempt -le $max_attempts ]; then
            echo "🔄 Retrying in 5 seconds..." | tee -a $LOG_FILE
            sleep 5
        fi
    done

    echo "❌ Module $module_name FAILED after $max_attempts attempts" | tee -a $LOG_FILE
    return 1
}

# Pre-installation validation
echo "🔍 Running pre-installation validation..." | tee -a $LOG_FILE
if ! /Users/MD/ISO-22301/scripts/validate-bcm-modules.sh; then
    echo "🚨 Validation failed! Fix XML errors before installation." | tee -a $LOG_FILE
    exit 1
fi

# Install modules one by one
successful_modules=0
failed_modules=0
failed_module_list=""

for module in "${BCM_MODULES[@]}"; do
    if install_module_safe "$module"; then
        successful_modules=$((successful_modules + 1))
    else
        failed_modules=$((failed_modules + 1))
        failed_module_list="$failed_module_list $module"
    fi
    echo "---" | tee -a $LOG_FILE
done

# Summary
echo "📊 INSTALLATION SUMMARY:" | tee -a $LOG_FILE
echo "✅ Successful installations: $successful_modules" | tee -a $LOG_FILE
echo "❌ Failed installations: $failed_modules" | tee -a $LOG_FILE

if [ $failed_modules -gt 0 ]; then
    echo "🚨 Failed modules:$failed_module_list" | tee -a $LOG_FILE
    echo "💡 These modules can be fixed and installed individually later" | tee -a $LOG_FILE
fi

echo "🏁 Installation process completed $(date)" | tee -a $LOG_FILE

# Show installed modules
echo "📋 Currently installed BCM modules:" | tee -a $LOG_FILE
docker exec iso-22301-odoo-1 odoo shell -d $DB_NAME --no-http <<EOF 2>&1 | tee -a $LOG_FILE
installed = env['ir.module.module'].search([('name', 'like', 'bcm_'), ('state', '=', 'installed')])
for module in installed:
    print(f"✅ {module.name}")
EOF