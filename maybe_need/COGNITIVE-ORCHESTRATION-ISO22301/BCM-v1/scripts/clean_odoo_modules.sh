#!/bin/bash

# Script to clean unnecessary Odoo modules for BCM Platform

ADDONS_DIR="/Users/MD/ISO-22301/core/odoo-18.0/addons"

# List of modules to REMOVE
MODULES_TO_REMOVE=(
    # Localizations
    "l10n_ch"
    "l10n_ua"

    # E-commerce and payments
    "website_payment"
    "website_payment_authorize"
    "website_membership"
    "website_customer"

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

    # Accounting
    "project_account"
    "project_sale_expense"
    "project_hr_expense"

    # Specific integrations
    "website_jitsi"
    "website_twitter"
    "website_google_map"
    "website_hr_recruitment"
    "website_mass_mailing"
    "website_links"
    "website_cf_turnstile"
    "google_gmail"
    "google_account"
    "web_unsplash"
    "snailmail"
    "partner_autocomplete"
    "phone_validation"

    # Test modules
    "test_simple"
    "web_fix"
    "web_hierarchy"

    # CRM modules (we have our own CRM bridge)
    "iap_crm"
    "iap"
    "iap_mail"

    # Other
    "project_timesheet_holidays"
    "mail_bot_hr"
    "website_slides_forum"
    "website_slides_survey"
    "mail_plugin"
    "base_address_extended"
    "base_geolocalize"
    "base_iban"
    "base_vat"
    "base_sparse_field"
    "base_import_module"
    "base_install_request"
    "resource_mail"
    "hr_gamification"
    "html_editor"
)

echo "🧹 Cleaning unnecessary Odoo modules for BCM Platform"
echo "======================================================="
echo ""

# Count modules before cleaning
BEFORE_COUNT=$(ls -d $ADDONS_DIR/*/ 2>/dev/null | wc -l)
echo "📦 Modules before cleaning: $BEFORE_COUNT"

# Remove unnecessary modules
REMOVED_COUNT=0
for module in "${MODULES_TO_REMOVE[@]}"; do
    if [ -d "$ADDONS_DIR/$module" ]; then
        echo "  ❌ Removing: $module"
        rm -rf "$ADDONS_DIR/$module"
        ((REMOVED_COUNT++))
    else
        echo "  ⚠️  Not found: $module (already removed?)"
    fi
done

# Count modules after cleaning
AFTER_COUNT=$(ls -d $ADDONS_DIR/*/ 2>/dev/null | wc -l)

echo ""
echo "======================================================="
echo "✅ Cleaning complete!"
echo "📊 Statistics:"
echo "  - Modules before: $BEFORE_COUNT"
echo "  - Modules removed: $REMOVED_COUNT"
echo "  - Modules after: $AFTER_COUNT"
echo ""

# List remaining non-BCM modules
echo "📋 Remaining standard modules:"
ls -d $ADDONS_DIR/*/ | grep -v bcm_ | xargs -n1 basename | sort | sed 's/^/  ✅ /'
echo ""
echo "📋 BCM modules:"
ls -d $ADDONS_DIR/bcm_*/ 2>/dev/null | xargs -n1 basename | sort | sed 's/^/  🔷 /'