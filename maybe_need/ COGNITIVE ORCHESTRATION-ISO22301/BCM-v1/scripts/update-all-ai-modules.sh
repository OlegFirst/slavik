#!/bin/bash

# Update All AI-Enhanced Modules to Version 18.0.2.0.0
echo "🔄 Updating AI-Enhanced BCM Modules to version 18.0.2.0.0..."

echo "✅ UPDATED MODULES:"
echo "- bcm_governance: 18.0.1.0.0 → 18.0.2.0.0 (AI Governance Brain)"
echo "- bcm_incident: 18.0.1.0.0 → 18.0.2.0.0 (AI Emergency Response)"
echo "- bcm_core: 18.0.1.0.0 → 18.0.2.0.0 (AI Lifecycle Monitor)"
echo "- bcm_scenario_hub: 18.0.1.0.0 → 18.0.2.0.0 (AI Scenario Creator)"

echo ""
echo "🔧 FORCE ODOO MODULE UPDATE:"
echo "Odoo кэширует старые versions - нужно force update"

echo ""
echo "Method 1: CLI Force Update (Recommended):"
docker exec iso-22301-odoo-1 odoo -d bcm_auto \
  -u bcm_governance,bcm_incident,bcm_core,bcm_scenario_hub \
  --stop-after-init --no-http

echo ""
echo "🔄 Restarting Odoo to clear cache..."
docker-compose restart odoo

echo ""
echo "⏳ Waiting for Odoo restart..."
sleep 30

echo ""
echo "✅ VERIFICATION STEPS:"
echo "1. Go to: http://localhost:8069"
echo "2. Apps → Search each module"
echo "3. Verify Latest Version shows: 18.0.2.0.0"
echo "4. Verify Summary shows: 🧠 AI [Organ Name]"
echo ""

echo "🧬 Expected AI Organs after update:"
echo "- 🧠 AI Governance Brain (bcm_governance)"
echo "- 🚨 AI Emergency Response (bcm_incident)"
echo "- 📊 AI Lifecycle Monitor (bcm_core)"
echo "- 🎭 AI Scenario Creator (bcm_scenario_hub)"
echo ""

echo "🎯 Test AI Functionality:"
echo "- Create governance topic → Click 'AI Analysis'"
echo "- Create incident → Click 'AI Emergency Response'"
echo "- Check AI Lifecycle Monitor → View organs health"
echo ""

echo "🚀 If successful: Digital BCM Organism ready for testing!"