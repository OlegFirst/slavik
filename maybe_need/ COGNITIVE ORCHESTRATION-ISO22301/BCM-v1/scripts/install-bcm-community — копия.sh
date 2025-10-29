#!/bin/bash

# Install bcm_community module in Odoo
echo "🔧 Installing bcm_community module in Odoo..."

# Method 1: CLI installation (if available)
echo "Attempting CLI installation..."
docker exec iso-22301-odoo-1 odoo -d bcm_auto -i bcm_community --stop-after-init --no-http 2>/dev/null

if [ $? -eq 0 ]; then
    echo "✅ bcm_community module installed successfully via CLI"
else
    echo "⚠️ CLI installation not available, use manual installation:"
    echo ""
    echo "Manual Installation Steps:"
    echo "1. Open: http://localhost:8069"
    echo "2. Login to bcm_auto database"
    echo "3. Go to: Apps menu"
    echo "4. Search for: bcm_community"
    echo "5. Click: Install"
    echo ""
    echo "OR using developer mode:"
    echo "1. Enable developer mode"
    echo "2. Go to: Apps → Update Apps List"
    echo "3. Search: bcm_community"
    echo "4. Install the module"
fi

echo ""
echo "📋 Module files created at:"
echo "- /core/odoo-18.0/addons/bcm_community/__manifest__.py"
echo "- /core/odoo-18.0/addons/bcm_community/models/"
echo "- /core/odoo-18.0/addons/bcm_community/views/"
echo "- /core/odoo-18.0/addons/bcm_community/security/"
echo ""
echo "🎯 After installation, check:"
echo "- Menu: Community → Forum Integration"
echo "- Community → Forum Topics"
echo ""