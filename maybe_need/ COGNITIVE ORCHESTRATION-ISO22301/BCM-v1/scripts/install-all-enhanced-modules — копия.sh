#!/bin/bash

# Install and Update All Enhanced BCM Modules
echo "🔧 Installing/Updating Enhanced BCM Modules..."

echo "📋 Enhanced modules to install/update:"
echo "- bcm_community (NEW)"
echo "- bcm_scenario_hub (ENHANCED)"
echo "- bcm_templates (ENHANCED)"
echo "- bcm_exercise (ENHANCED)"
echo "- bcm_reporting (ENHANCED)"

echo ""
echo "📖 MANUAL INSTALLATION STEPS:"
echo "=============================="

echo ""
echo "1. 🌐 Open Odoo:"
echo "   http://localhost:8069"

echo ""
echo "2. 🔑 Login to bcm_auto database"

echo ""
echo "3. 🔄 Update Apps List:"
echo "   - Enable Developer Mode: Settings → Activate Developer Mode"
echo "   - Go to: Apps menu"
echo "   - Click: 'Update Apps List' button"
echo "   - Wait for completion"

echo ""
echo "4. 📦 Install NEW module:"
echo "   - Search: 'bcm_community'"
echo "   - Click: Install"

echo ""
echo "5. 🔄 Update ENHANCED modules:"
echo "   - Search: 'bcm_scenario_hub' → Click 'Upgrade'"
echo "   - Search: 'bcm_templates' → Click 'Upgrade'"
echo "   - Search: 'bcm_exercise' → Click 'Upgrade'"
echo "   - Search: 'bcm_reporting' → Click 'Upgrade'"

echo ""
echo "6. ✅ Verify installation:"
echo "   - Check menu: Community → Forum Integration"
echo "   - Check menu: Templates → BCM Templates"
echo "   - Check menu: Exercises → [Enhanced features]"
echo "   - Check menu: Reporting → Analytics Dashboard"

echo ""
echo "🎯 After installation:"
echo "- bcm_community will have Forum + Knowledge Base"
echo "- bcm_templates will have BPMN workflows"
echo "- bcm_exercise will have template integration"
echo "- bcm_reporting will have analytics dashboard"

echo ""
echo "🧪 Test enhanced functionality:"
echo "- Generate AI scenario: http://localhost:8085/scenarios/generate"
echo "- Check simulation services: http://localhost:8094/health"
echo "- View analytics: Reporting → Analytics Dashboard"
echo ""