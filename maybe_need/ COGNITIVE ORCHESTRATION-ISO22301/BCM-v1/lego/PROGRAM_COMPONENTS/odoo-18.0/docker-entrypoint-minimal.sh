#!/bin/bash
set -e

echo "[BCM] Minimal installation - only working modules"

# Set database credentials
export DB_HOST=${DB_HOST:-postgres}
export DB_PORT=${DB_PORT:-5432}
export DB_USER=${DB_USER:-odoo}
export DB_PASSWORD=${DB_PASSWORD:-postgres123}
export DB_NAME=${DB_NAME:-bcm_minimal}
export PGPASSWORD=$DB_PASSWORD

# Wait for PostgreSQL
echo "[BCM] Waiting for PostgreSQL..."
while ! pg_isready -h $DB_HOST -p $DB_PORT -U $DB_USER >/dev/null 2>&1; do
    sleep 1
done
echo "[BCM] PostgreSQL ready!"

# Create database
createdb -h $DB_HOST -p $DB_PORT -U $DB_USER $DB_NAME 2>/dev/null || true

# Install only base Odoo
echo "[BCM] Installing Odoo base..."
odoo -d $DB_NAME --db_host=$DB_HOST --db_port=$DB_PORT \
     --db_user=$DB_USER --db_password=$DB_PASSWORD \
     --init=base,web,mail --stop-after-init --no-http \
     --without-demo=all --log-level=error 2>/dev/null || true

# Install ONLY working BCM modules
echo "[BCM] Installing minimal BCM modules..."
WORKING_MODULES="bcm_base,bcm_core,bcm_config,bcm_context,bcm_audit,bcm_clients,bcm_plans,bcm_exercise,bcm_kpi,bcm_training,bcm_templates,bcm_reporting,bcm_admin_website"

odoo -d $DB_NAME --db_host=$DB_HOST --db_port=$DB_PORT \
     --db_user=$DB_USER --db_password=$DB_PASSWORD \
     -i $WORKING_MODULES \
     --stop-after-init --no-http --without-demo=all \
     --addons-path=/mnt/extra-addons \
     --log-level=error 2>/dev/null || true

# Start Odoo
echo "[BCM] Starting Odoo with minimal BCM modules..."
exec odoo \
    --database=$DB_NAME \
    --db_host=$DB_HOST \
    --db_port=$DB_PORT \
    --db_user=$DB_USER \
    --db_password=$DB_PASSWORD \
    --addons-path=/mnt/extra-addons \
    --without-demo=all \
    --log-level=info