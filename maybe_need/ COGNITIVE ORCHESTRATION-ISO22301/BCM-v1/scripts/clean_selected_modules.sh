#!/bin/bash

# Script to clean selected unnecessary Odoo modules

ADDONS_DIR="/Users/MD/ISO-22301/core/odoo-18.0/addons"

# List of modules to REMOVE (as requested by user)
MODULES_TO_REMOVE=(
    # Manufacturing and stock
    "project_mrp"
    "project_mrp_account"
    "project_mrp_sale"
    "project_mrp_stock_landed_costs"
    "project_stock"
    "project_stock_account"
    "project_stock_landed_costs"
    "project_purchase"
    "project_purchase_stock"

    # Other modules
    "snailmail"
    "base_geolocalize"
    "base_iban"
    "base_vat"
    "base_sparse_field"
    "project_timesheet_holidays"
    "mail_bot_hr"
    "website_slides_forum"
    "website_slides_survey"
    "mail_plugin"
    "base_address_extended"
)

echo "🧹 Cleaning selected unnecessary Odoo modules"
echo "============================================="
echo ""

# Count modules before cleaning
BEFORE_COUNT=$(ls -d $ADDONS_DIR/*/ 2>/dev/null | wc -l)
echo "📦 Modules before cleaning: $BEFORE_COUNT"

# Remove selected modules
REMOVED_COUNT=0
for module in "${MODULES_TO_REMOVE[@]}"; do
    if [ -d "$ADDONS_DIR/$module" ]; then
        echo "  ❌ Removing: $module"
        rm -rf "$ADDONS_DIR/$module"
        ((REMOVED_COUNT++))
    else
        echo "  ⚠️  Not found: $module"
    fi
done

# Count modules after cleaning
AFTER_COUNT=$(ls -d $ADDONS_DIR/*/ 2>/dev/null | wc -l)

echo ""
echo "============================================="
echo "✅ Cleaning complete!"
echo "📊 Statistics:"
echo "  - Modules before: $BEFORE_COUNT"
echo "  - Modules removed: $REMOVED_COUNT"
echo "  - Modules after: $AFTER_COUNT"