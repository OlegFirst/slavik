#!/bin/bash
# Initialize Odoo with BCM modules - FIXED VERSION

echo "🔧 Initializing Odoo BCM Platform with 20 modules..."

# Wait for containers
sleep 10

# Create database and admin user automatically
docker exec iso-22301-odoo-1 odoo \
  --database=bcm_auto \
  --db_host=postgres \
  --db_port=5432 \
  --db_user=odoo \
  --db_password=postgres123 \
  --addons-path=/mnt/extra-addons \
  --init=base,web,bcm_core,bcm_base,bcm_incident,bcm_bia,bcm_training,bcm_portal,bcm_config,bcm_context,bcm_plans,bcm_reporting,bcm_clients,bcm_kpi,bcm_templates,bcm_audit,bcm_governance,bcm_risk_management,bcm_intelligent_base,bcm_incident_management,bcm_scenario_hub \
  --load-language=en_US \
  --without-demo=all \
  --stop-after-init

echo "✅ Odoo BCM Platform auto-initialized!"
echo "🔗 URL: http://localhost:8069/web?db=bcm_auto"
echo "👤 Login: admin"
echo "🔑 Password: admin"
echo ""
echo "🤖 AI Assistant v2 + 20 BCM модулей готовы!"