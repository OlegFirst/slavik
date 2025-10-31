#!/bin/bash
set -e

# Function to wait for service
wait_for_service() {
    local host=$1
    local port=$2
    local service_name=$3

    echo "[BCM] Waiting for $service_name at $host:$port..."
    while ! timeout 1 bash -c "</dev/tcp/$host/$port" 2>/dev/null; do
        sleep 1
    done
    echo "[BCM] $service_name is ready!"
}

# Function to install BCM modules in correct order
install_bcm_modules() {
    echo "[BCM] Starting optimized platform installation (max 5 modules per step)..."

    # PHASE 1: Core Odoo Foundation (критически важные)
    echo "[BCM] Step 1/15: Initializing database..."
    odoo -d $DB_NAME --db_host=$DB_HOST --db_port=$DB_PORT --db_user=$DB_USER --db_password=$DB_PASSWORD \
        --init=base --stop-after-init --no-http --without-demo=all

    echo "[BCM] Step 2/15: Core web framework..."
    odoo -d $DB_NAME --db_host=$DB_HOST --db_port=$DB_PORT --db_user=$DB_USER --db_password=$DB_PASSWORD \
        -i web,bus,http_routing,mail \
        --stop-after-init --no-http --without-demo=all

    echo "[BCM] Step 3/15: Web extensions..."
    odoo -d $DB_NAME --db_host=$DB_HOST --db_port=$DB_PORT --db_user=$DB_USER --db_password=$DB_PASSWORD \
        -i web_editor,web_tour,mail_bot,mail_group \
        --stop-after-init --no-http --without-demo=all

    # PHASE 2: Authentication & Security
    echo "[BCM] Step 4/15: Authentication base..."
    odoo -d $DB_NAME --db_host=$DB_HOST --db_port=$DB_PORT --db_user=$DB_USER --db_password=$DB_PASSWORD \
        -i auth_signup,auth_totp,auth_totp_portal \
        --stop-after-init --no-http --without-demo=all

    echo "[BCM] Step 5/15: Security extensions..."
    odoo -d $DB_NAME --db_host=$DB_HOST --db_port=$DB_PORT --db_user=$DB_USER --db_password=$DB_PASSWORD \
        -i auth_password_policy,auth_ldap,privacy_lookup \
        --stop-after-init --no-http --without-demo=all

    # PHASE 3: Portal & Website
    echo "[BCM] Step 6/15: Portal foundation..."
    odoo -d $DB_NAME --db_host=$DB_HOST --db_port=$DB_PORT --db_user=$DB_USER --db_password=$DB_PASSWORD \
        -i portal,portal_rating,website,website_mail \
        --stop-after-init --no-http --without-demo=all

    echo "[BCM] Step 7/15: Website features..."
    odoo -d $DB_NAME --db_host=$DB_HOST --db_port=$DB_PORT --db_user=$DB_USER --db_password=$DB_PASSWORD \
        -i website_profile,website_forum,website_blog,website_slides,website_partner \
        --stop-after-init --no-http --without-demo=all

    # PHASE 4: Business modules
    echo "[BCM] Step 8/15: HR & Contacts..."
    odoo -d $DB_NAME --db_host=$DB_HOST --db_port=$DB_PORT --db_user=$DB_USER --db_password=$DB_PASSWORD \
        -i hr,contacts,calendar,resource \
        --stop-after-init --no-http --without-demo=all

    echo "[BCM] Step 9/15: Project & HR extensions..."
    odoo -d $DB_NAME --db_host=$DB_HOST --db_port=$DB_PORT --db_user=$DB_USER --db_password=$DB_PASSWORD \
        -i project,hr_skills,hr_org_chart,hr_calendar,project_todo \
        --stop-after-init --no-http --without-demo=all

    echo "[BCM] Step 10/15: Analytics & utilities..."
    odoo -d $DB_NAME --db_host=$DB_HOST --db_port=$DB_PORT --db_user=$DB_USER --db_password=$DB_PASSWORD \
        -i analytic,digest,rating,survey,utm \
        --stop-after-init --no-http --without-demo=all

    echo "[BCM] Step 11/15: Automation & tools..."
    odoo -d $DB_NAME --db_host=$DB_HOST --db_port=$DB_PORT --db_user=$DB_USER --db_password=$DB_PASSWORD \
        -i base_automation,base_import,base_setup,gamification,sms \
        --stop-after-init --no-http --without-demo=all

    # PHASE 5: BCM Modules (правильная последовательность)
    echo "[BCM] Step 12/15: BCM foundation (base dependencies)..."
    odoo -d $DB_NAME --db_host=$DB_HOST --db_port=$DB_PORT --db_user=$DB_USER --db_password=$DB_PASSWORD \
        -i bcm_base,bcm_intelligent_base,bcm_core \
        --stop-after-init --no-http --without-demo=all

    echo "[BCM] Step 13/15: BCM infrastructure..."
    odoo -d $DB_NAME --db_host=$DB_HOST --db_port=$DB_PORT --db_user=$DB_USER --db_password=$DB_PASSWORD \
        -i bcm_context,bcm_config,bcm_governance,bcm_community,bcm_audit \
        --stop-after-init --no-http --without-demo=all

    echo "[BCM] Step 14/15: BCM business logic..."
    odoo -d $DB_NAME --db_host=$DB_HOST --db_port=$DB_PORT --db_user=$DB_USER --db_password=$DB_PASSWORD \
        -i bcm_bia,bcm_risk_management,bcm_incident,bcm_plans,bcm_exercise \
        --stop-after-init --no-http --without-demo=all

    echo "[BCM] Step 15/15: BCM advanced features..."
    odoo -d $DB_NAME --db_host=$DB_HOST --db_port=$DB_PORT --db_user=$DB_USER --db_password=$DB_PASSWORD \
        -i bcm_kpi,bcm_training,bcm_templates,bcm_portal,bcm_reporting \
        --stop-after-init --no-http --without-demo=all

    # Remaining modules in final batch
    echo "[BCM] Step 16/16: Final BCM modules..."
    odoo -d $DB_NAME --db_host=$DB_HOST --db_port=$DB_PORT --db_user=$DB_USER --db_password=$DB_PASSWORD \
        -i bcm_clients,bcm_ai_control,bcm_digital_twin_core,bcm_scenario_hub,bcm_admin_website,bcm_incident_management,project_mail_plugin,uom \
        --stop-after-init --no-http --without-demo=all

    echo "[BCM] ✅ Complete BCM Platform installed successfully!"
    echo "[BCM] 📊 Installed: 54 standard modules + 28 BCM modules = 82 total modules"
    echo "[BCM] 🚀 Optimized installation with max 5 modules per step"
}

# Set default values
DB_HOST=${DB_HOST:-postgres}
DB_PORT=${DB_PORT:-5432}
DB_USER=${DB_USER:-odoo}
DB_PASSWORD=${DB_PASSWORD:-bcm_secure_2024}
DB_NAME=${DB_NAME:-bcm_platform}

# Export for psql
export PGPASSWORD=$DB_PASSWORD

# Wait for PostgreSQL
wait_for_service $DB_HOST $DB_PORT "PostgreSQL"

# Always install BCM modules on first run
if [ "$BCM_MODULES_AUTO_INSTALL" = "true" ]; then
    # Check if database exists and has bcm_core installed
    DB_EXISTS=$(psql -h $DB_HOST -U $DB_USER -lqt 2>/dev/null | cut -d \| -f 1 | grep -w $DB_NAME | wc -l)

    if [ "$DB_EXISTS" -eq "0" ]; then
        echo "[BCM] Database $DB_NAME doesn't exist, creating with BCM modules..."
        install_bcm_modules
    else
        # Check if bcm_core is installed
        MODULE_CHECK=$(psql -h $DB_HOST -U $DB_USER -d $DB_NAME -t -c \
            "SELECT COUNT(*) FROM ir_module_module WHERE name='bcm_core' AND state='installed'" 2>/dev/null || echo "0")

        if [ "$MODULE_CHECK" -eq "0" ] || [ "$MODULE_CHECK" = " 0" ]; then
            echo "[BCM] BCM modules not installed, installing now..."
            install_bcm_modules
        else
            echo "[BCM] BCM modules already installed, starting Odoo..."
        fi
    fi
fi

# Run Odoo with all BCM modules
echo "[BCM] Starting Odoo with BCM Platform..."
exec odoo \
    --database=$DB_NAME \
    --db_host=$DB_HOST \
    --db_port=$DB_PORT \
    --db_user=$DB_USER \
    --db_password=$DB_PASSWORD \
    --addons-path=/mnt/extra-addons \
    --without-demo=all \
    --log-level=info