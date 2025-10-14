#!/bin/bash

# Script to rename all HTML files from dashes to underscores
# Usage: cd /Users/MD/AI-Platform-ISO/docs && bash RENAME_FILES_SCRIPT.sh

echo "Starting file rename process..."
echo "========================================"

# Change to docs directory
cd /Users/MD/AI-Platform-ISO/docs || exit 1

# Rename files
mv business-flow.html business_flow.html 2>/dev/null && echo "✓ business-flow.html → business_flow.html" || echo "✗ business-flow.html (not found or error)"
mv bcm-philosophy.html bcm_philosophy.html 2>/dev/null && echo "✓ bcm-philosophy.html → bcm_philosophy.html" || echo "✗ bcm-philosophy.html (not found or error)"
mv decision-center.html decision_center.html 2>/dev/null && echo "✓ decision-center.html → decision_center.html" || echo "✗ decision-center.html (not found or error)"
mv mio-manager.html mio_manager.html 2>/dev/null && echo "✓ mio-manager.html → mio_manager.html" || echo "✗ mio-manager.html (not found or error)"
mv platform-overview.html platform_overview.html 2>/dev/null && echo "✓ platform-overview.html → platform_overview.html" || echo "✗ platform-overview.html (not found or error)"
mv workflow-intelligence.html workflow_intelligence.html 2>/dev/null && echo "✓ workflow-intelligence.html → workflow_intelligence.html" || echo "✗ workflow-intelligence.html (not found or error)"
mv ai-foundation.html ai_foundation.html 2>/dev/null && echo "✓ ai-foundation.html → ai_foundation.html" || echo "✗ ai-foundation.html (not found or error)"
mv eventbus-choreography.html eventbus_choreography.html 2>/dev/null && echo "✓ eventbus-choreography.html → eventbus_choreography.html" || echo "✗ eventbus-choreography.html (not found or error)"
mv collective-intelligence.html collective_intelligence.html 2>/dev/null && echo "✓ collective-intelligence.html → collective_intelligence.html" || echo "✗ collective-intelligence.html (not found or error)"
mv expertise-center.html expertise_center.html 2>/dev/null && echo "✓ expertise-center.html → expertise_center.html" || echo "✗ expertise-center.html (not found or error)"
mv predictive-intelligence.html predictive_intelligence.html 2>/dev/null && echo "✓ predictive-intelligence.html → predictive_intelligence.html" || echo "✗ predictive-intelligence.html (not found or error)"
mv governance-layer.html governance_layer.html 2>/dev/null && echo "✓ governance-layer.html → governance_layer.html" || echo "✗ governance-layer.html (not found or error)"
mv ace-service.html ace_service.html 2>/dev/null && echo "✓ ace-service.html → ace_service.html" || echo "✗ ace-service.html (not found or error)"
mv service-catalog-visual.html service_catalog_visual.html 2>/dev/null && echo "✓ service-catalog-visual.html → service_catalog_visual.html" || echo "✗ service-catalog-visual.html (not found or error)"
mv platform-services-overview.html platform_services_overview.html 2>/dev/null && echo "✓ platform-services-overview.html → platform_services_overview.html" || echo "✗ platform-services-overview.html (not found or error)"

echo ""
echo "========================================"
echo "Rename process complete!"
echo ""
echo "Next step: Update all links in HTML files"
echo "Run: bash UPDATE_LINKS_SCRIPT.sh"
