#!/bin/bash
# AI-Platform-ISO: Complete Analysis Pipeline
# Время выполнения: ~5 минут

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

echo "🚀 AI-Platform-ISO Complete Analysis Pipeline"
echo "=============================================="
echo ""

# 1. AST Analysis
echo "📊 STEP 1: AST Analysis (Functions, Classes, Endpoints)"
echo "--------------------------------------------------------"
python3 tools/analyzers/ast_analyzer.py
echo ""

# 2. Dependency Mapping
echo "🔗 STEP 2: Dependency Mapping"
echo "--------------------------------------------------------"
python3 tools/analyzers/dependency_mapper.py
echo ""

# 3. Complexity Analysis
echo "📈 STEP 3: Code Complexity Analysis"
echo "--------------------------------------------------------"
radon cc platform-services/ -a -s | head -50
radon mi platform-services/ -s | head -50
echo ""

# 4. Security Scan
echo "🔒 STEP 4: Security Scan (Bandit)"
echo "--------------------------------------------------------"
bandit -r platform-services/ -f json -o tools/reports/security_scan.json || true
bandit -r platform-services/ -ll | head -30
echo ""

# 5. Code Quality
echo "✨ STEP 5: Code Quality (Pylint)"
echo "--------------------------------------------------------"
pylint platform-services/*/  --output-format=json > tools/reports/pylint_report.json || true
echo "✅ Pylint report saved to tools/reports/pylint_report.json"
echo ""

# 6. Generate Dashboards
echo "🎨 STEP 6: Generate Interactive Dashboards"
echo "--------------------------------------------------------"
python3 tools/dashboards/module_dashboard.py
echo ""

# 7. Generate Tests
echo "🧪 STEP 7: Generate Test Scaffolds"
echo "--------------------------------------------------------"
python3 tools/generators/test_generator.py
echo ""

# 8. Summary
echo "📋 ANALYSIS COMPLETE!"
echo "=============================================="
echo ""
echo "Generated Reports:"
echo "  📄 tools/reports/ast_analysis.json"
echo "  📄 tools/reports/ast_analysis.md"
echo "  📄 tools/reports/dependencies.json"
echo "  📄 tools/reports/dependencies.md"
echo "  📄 tools/reports/security_scan.json"
echo "  📄 tools/reports/pylint_report.json"
echo "  📊 tools/reports/dependency_graph.png"
echo "  📊 tools/reports/dependency_graph.graphml"
echo ""
echo "Interactive Dashboards:"
echo "  🎨 tools/reports/dashboard.html"
echo "  🎨 tools/reports/endpoint_map.html"
echo "  🎨 tools/reports/dependency_network.html"
echo ""
echo "Next Steps:"
echo "  1. Open dashboards in browser"
echo "  2. Review security scan results"
echo "  3. Check for circular dependencies"
echo "  4. Generate API documentation: ./tools/generate_docs.sh"
echo ""
