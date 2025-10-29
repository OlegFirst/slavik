#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}[BCM]${NC} ISO 22301 Business Continuity Management Platform"
echo -e "${GREEN}[BCM]${NC} Optimized installation with 28 BCM modules"

# Set database credentials
export DB_HOST=${DB_HOST:-postgres}
export DB_PORT=${DB_PORT:-5432}
export DB_USER=${DB_USER:-odoo}
export DB_PASSWORD=${DB_PASSWORD:-postgres123}
export DB_NAME=${DB_NAME:-bcm_platform}
export PGPASSWORD=$DB_PASSWORD

# Function to wait for PostgreSQL
wait_for_postgres() {
    echo -e "${YELLOW}[BCM]${NC} Waiting for PostgreSQL at $DB_HOST:$DB_PORT..."
    while ! pg_isready -h $DB_HOST -p $DB_PORT -U $DB_USER >/dev/null 2>&1; do
        sleep 1
    done
    echo -e "${GREEN}[BCM]${NC} PostgreSQL is ready!"
}

# Function to install all BCM modules efficiently
install_all_bcm_modules() {
    echo -e "${GREEN}[BCM]${NC} Installing all 28 BCM modules in optimized batches..."

    # Create database if not exists
    createdb -h $DB_HOST -p $DB_PORT -U $DB_USER $DB_NAME 2>/dev/null || true

    # List of all BCM modules
    BCM_MODULES=(
        # Foundation (3 modules)
        bcm_base
        bcm_intelligent_base
        bcm_core

        # Infrastructure (5 modules)
        bcm_context
        bcm_config
        bcm_governance
        bcm_community
        bcm_audit

        # Business Logic (5 modules)
        bcm_bia
        bcm_risk_management
        bcm_incident
        bcm_plans
        bcm_exercise

        # Advanced Features (5 modules)
        bcm_kpi
        bcm_training
        bcm_templates
        bcm_portal
        bcm_reporting

        # Additional Modules (10 modules)
        bcm_clients
        bcm_ai_control
        bcm_digital_twin_core
        bcm_scenario_hub
        bcm_admin_website
        bcm_incident_management
        bcm_compliance
        bcm_recovery
        bcm_supplier
        bcm_communication
    )

    # Step 1: Initialize Odoo base
    echo -e "${YELLOW}[BCM]${NC} Step 1/5: Initializing Odoo base system..."
    odoo -d $DB_NAME --db_host=$DB_HOST --db_port=$DB_PORT \
         --db_user=$DB_USER --db_password=$DB_PASSWORD \
         --init=base --stop-after-init --no-http --without-demo=all \
         --addons-path=/mnt/extra-addons \
         --log-level=warn 2>/dev/null || true

    # Step 2: Install core web modules
    echo -e "${YELLOW}[BCM]${NC} Step 2/5: Installing core web framework..."
    odoo -d $DB_NAME --db_host=$DB_HOST --db_port=$DB_PORT \
         --db_user=$DB_USER --db_password=$DB_PASSWORD \
         -i web,mail,bus,portal \
         --stop-after-init --no-http --without-demo=all \
         --addons-path=/mnt/extra-addons \
         --log-level=warn 2>/dev/null || true

    # Step 3: Install all BCM modules in one shot
    echo -e "${YELLOW}[BCM]${NC} Step 3/5: Installing all 28 BCM modules..."

    # Join all modules with comma
    MODULE_LIST=$(IFS=,; echo "${BCM_MODULES[*]}")

    odoo -d $DB_NAME --db_host=$DB_HOST --db_port=$DB_PORT \
         --db_user=$DB_USER --db_password=$DB_PASSWORD \
         -i $MODULE_LIST \
         --stop-after-init --no-http --without-demo=all \
         --addons-path=/mnt/extra-addons \
         --log-level=warn 2>/dev/null || {

        echo -e "${YELLOW}[BCM]${NC} Batch installation failed, installing modules individually..."

        # Fallback: Install modules one by one
        for module in "${BCM_MODULES[@]}"; do
            echo -e "${YELLOW}[BCM]${NC}   Installing $module..."
            odoo -d $DB_NAME --db_host=$DB_HOST --db_port=$DB_PORT \
                 --db_user=$DB_USER --db_password=$DB_PASSWORD \
                 -i $module \
                 --stop-after-init --no-http --without-demo=all \
                 --addons-path=/mnt/extra-addons \
                 --log-level=error 2>/dev/null || echo -e "${RED}[BCM]${NC}   Warning: $module installation failed"
        done
    }

    # Step 4: Mark all modules as installed and auto_install
    echo -e "${YELLOW}[BCM]${NC} Step 4/5: Activating all BCM modules..."
    psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME << EOF
        -- Mark all BCM modules as installed
        UPDATE ir_module_module
        SET state = 'installed',
            demo = false,
            auto_install = true
        WHERE name LIKE 'bcm_%';
EOF

    # Step 5: Verify installation
    echo -e "${YELLOW}[BCM]${NC} Step 5/5: Verifying module installation..."
    MODULE_COUNT=$(psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -t -c \
        "SELECT COUNT(*) FROM ir_module_module WHERE name LIKE 'bcm_%' AND state='installed'" 2>/dev/null)

    echo -e "${GREEN}[BCM]${NC} ✅ Successfully installed $MODULE_COUNT BCM modules!"

    # List installed modules
    echo -e "${GREEN}[BCM]${NC} Installed modules:"
    psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -t -c \
        "SELECT '  • ' || name FROM ir_module_module WHERE name LIKE 'bcm_%' AND state='installed' ORDER BY name"
}

# Main execution
wait_for_postgres

# Check if BCM modules need installation
if [ "$BCM_AUTO_INSTALL" = "true" ]; then
    # Check if database exists
    DB_EXISTS=$(psql -h $DB_HOST -p $DB_PORT -U $DB_USER -lqt 2>/dev/null | cut -d \| -f 1 | grep -w $DB_NAME | wc -l)

    if [ "$DB_EXISTS" -eq "0" ]; then
        echo -e "${GREEN}[BCM]${NC} Fresh installation detected, installing all modules..."
        install_all_bcm_modules
    else
        # Check module count
        MODULE_COUNT=$(psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -t -c \
            "SELECT COUNT(*) FROM ir_module_module WHERE name LIKE 'bcm_%' AND state='installed'" 2>/dev/null || echo "0")

        if [ "$MODULE_COUNT" -lt "28" ]; then
            echo -e "${YELLOW}[BCM]${NC} Only $MODULE_COUNT/28 modules installed, completing installation..."
            install_all_bcm_modules
        else
            echo -e "${GREEN}[BCM]${NC} ✅ All $MODULE_COUNT BCM modules already active!"
        fi
    fi
else
    echo -e "${YELLOW}[BCM]${NC} Auto-install disabled, starting with existing configuration..."
fi

# Start Odoo
echo -e "${GREEN}[BCM]${NC} Starting Odoo with BCM Platform..."
echo -e "${GREEN}[BCM]${NC} Access Odoo at: http://localhost:8069"
echo -e "${GREEN}[BCM]${NC} Default credentials: admin / admin123"

exec odoo \
    --database=$DB_NAME \
    --db_host=$DB_HOST \
    --db_port=$DB_PORT \
    --db_user=$DB_USER \
    --db_password=$DB_PASSWORD \
    --addons-path=/mnt/extra-addons \
    --without-demo=all \
    --log-level=info