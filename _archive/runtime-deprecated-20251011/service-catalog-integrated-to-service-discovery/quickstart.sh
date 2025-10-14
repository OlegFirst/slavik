#!/bin/bash
# ============================================
# Service Catalog Integration - Quick Start
# ============================================
# This script sets up the complete service catalog integration

set -e  # Exit on error

echo "======================================================================="
echo "🚀 SERVICE CATALOG INTEGRATION - QUICK START"
echo "======================================================================="
echo ""

# Change to base directory
cd "$(dirname "$0")/../../.."
BASE_DIR=$(pwd)

echo "📂 Working directory: $BASE_DIR"
echo ""

# Step 1: Generate Catalog
echo "Step 1/3: Generating service catalog..."
echo "----------------------------------------"
python3 infrastructure/runtime/service-catalog/generate_catalog.py
echo ""

# Step 2: Generate Documentation
echo "Step 2/3: Generating documentation..."
echo "----------------------------------------"
python3 infrastructure/runtime/service-catalog/generate_docs.py
echo ""

# Step 3: Validation
echo "Step 3/3: Validating integration..."
echo "----------------------------------------"

# Check catalog file
if [ -f "infrastructure/runtime/service-catalog/service-catalog.yaml" ]; then
    CATALOG_SIZE=$(wc -c < infrastructure/runtime/service-catalog/service-catalog.yaml | awk '{print int($1/1024)}')
    echo "✅ Catalog generated: service-catalog.yaml (${CATALOG_SIZE} KB)"
else
    echo "❌ ERROR: Catalog file not found"
    exit 1
fi

# Check documentation files
if [ -f "docs/service-catalog/SERVICE_CATALOG.md" ]; then
    echo "✅ Markdown documentation generated"
else
    echo "❌ ERROR: Markdown documentation not found"
    exit 1
fi

if [ -f "docs/service-catalog/service-catalog.html" ]; then
    echo "✅ HTML documentation generated"
else
    echo "❌ ERROR: HTML documentation not found"
    exit 1
fi

if [ -f "docs/service-catalog/service-catalog.json" ]; then
    echo "✅ JSON export generated"
else
    echo "❌ ERROR: JSON export not found"
    exit 1
fi

# Check SERVICE_INFO.yaml files
PLATFORM_SERVICES=$(find platform-services -name "SERVICE_INFO.yaml" | wc -l | tr -d ' ')
INTELLIGENT_CORE=$(find intelligent-core -name "SERVICE_INFO.yaml" | wc -l | tr -d ' ')

echo "✅ Platform services: $PLATFORM_SERVICES SERVICE_INFO.yaml files"
echo "✅ Intelligent core: $INTELLIGENT_CORE SERVICE_INFO.yaml files"

TOTAL_SERVICES=$((PLATFORM_SERVICES + INTELLIGENT_CORE))
echo "✅ Total services documented: $TOTAL_SERVICES"

echo ""
echo "======================================================================="
echo "✅ INTEGRATION COMPLETE"
echo "======================================================================="
echo ""
echo "📁 Generated Files:"
echo "   - infrastructure/runtime/service-catalog/service-catalog.yaml"
echo "   - docs/service-catalog/SERVICE_CATALOG.md"
echo "   - docs/service-catalog/service-catalog.html"
echo "   - docs/service-catalog/service-catalog.json"
echo "   - docs/service-catalog/architecture-diagram.md"
echo ""
echo "🚀 Next Steps:"
echo ""
echo "   1. Start Service Discovery:"
echo "      cd infrastructure/runtime/service-discovery"
echo "      python3 main.py"
echo ""
echo "   2. View Documentation:"
echo "      open docs/service-catalog/service-catalog.html"
echo ""
echo "   3. Access Service Discovery API:"
echo "      curl http://localhost:8500/v2/catalog/services"
echo ""
echo "   4. View Grafana Dashboard:"
echo "      Import: infrastructure/runtime/service-catalog/grafana-dashboard.json"
echo ""
echo "📖 Full Documentation:"
echo "   - SERVICE_CATALOG_INTEGRATION_COMPLETE.md"
echo ""
echo "======================================================================="
