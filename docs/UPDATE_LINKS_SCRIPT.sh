#!/bin/bash

# Script to update all href links from dashes to underscores
# Usage: cd /Users/MD/AI-Platform-ISO/docs && bash UPDATE_LINKS_SCRIPT.sh

echo "Starting link update process..."
echo "========================================"

# Change to docs directory
cd /Users/MD/AI-Platform-ISO/docs || exit 1

# Backup original files first
echo "Creating backups..."
for file in *.html; do
    cp "$file" "$file.backup"
done
echo "✓ Backups created (*.html.backup)"
echo ""

# Update links in ALL HTML files
echo "Updating links..."

# Use sed to replace all dash-based links with underscore-based links
find . -name "*.html" -not -name "*.backup" -type f -exec sed -i '' \
    -e 's/href="business-flow\.html"/href="business_flow.html"/g' \
    -e 's/href="bcm-philosophy\.html"/href="bcm_philosophy.html"/g' \
    -e 's/href="decision-center\.html"/href="decision_center.html"/g' \
    -e 's/href="mio-manager\.html"/href="mio_manager.html"/g' \
    -e 's/href="platform-overview\.html"/href="platform_overview.html"/g' \
    -e 's/href="workflow-intelligence\.html"/href="workflow_intelligence.html"/g' \
    -e 's/href="ai-foundation\.html"/href="ai_foundation.html"/g' \
    -e 's/href="eventbus-choreography\.html"/href="eventbus_choreography.html"/g' \
    -e 's/href="collective-intelligence\.html"/href="collective_intelligence.html"/g' \
    -e 's/href="expertise-center\.html"/href="expertise_center.html"/g' \
    -e 's/href="predictive-intelligence\.html"/href="predictive_intelligence.html"/g' \
    -e 's/href="governance-layer\.html"/href="governance_layer.html"/g' \
    -e 's/href="ace-service\.html"/href="ace_service.html"/g' \
    -e 's/href="service-catalog-visual\.html"/href="service_catalog_visual.html"/g' \
    -e 's/href="platform-services-overview\.html"/href="platform_services_overview.html"/g' \
    {} \;

echo "✓ Links updated in all HTML files"
echo ""

# Verify no more dashes remain in links (excluding external links)
echo "Verifying changes..."
echo "Remaining dash-based internal links:"
grep -r 'href="[a-z-]*-[a-z-]*\.html"' *.html --color=never | grep -v "\.backup" | wc -l
echo ""

echo "========================================"
echo "Link update complete!"
echo ""
echo "To verify manually:"
echo "  grep -r 'href=\".*-.*\.html\"' *.html | grep -v backup"
echo ""
echo "If everything looks good, delete backups:"
echo "  rm *.html.backup"
