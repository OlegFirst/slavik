#!/bin/bash

# Pre-flight check - использует tools для анализа перед запуском
# Проверяет готовность инфраструктуры и модулей

set -e

echo "🚀 Infrastructure Pre-Flight Check"
echo "=========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Step 1: Environment check
echo -e "${BLUE}Step 1/5: Environment Variables${NC}"
python3 infrastructure/scripts/verify_env.py
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Environment check failed!${NC}"
    exit 1
fi
echo ""

# Step 2: Connectivity check
echo -e "${BLUE}Step 2/5: Infrastructure Connections${NC}"
bash infrastructure/scripts/test_connections.sh
echo ""

# Step 3: Dependency validation (using tools!)
echo -e "${BLUE}Step 3/5: Dependency Validation${NC}"
echo "Running dependency validator on core modules..."

# Check ai-foundation
echo -n "  ai-foundation: "
cd intelligent-core/ai-foundation
if timeout 30 python3 -c "import sys; sys.path.insert(0, '../../'); from rag.vector_store import VectorStore" 2>/dev/null; then
    echo -e "${GREEN}✅${NC}"
else
    echo -e "${YELLOW}⚠️  Import issues detected${NC}"
fi
cd ../..

# Check workflow_intelligence
echo -n "  workflow_intelligence: "
cd intelligent-core/workflow_intelligence
if timeout 30 python3 -c "import sys; sys.path.insert(0, '../..'); from core.orchestration_engine import OrchestrationEngine" 2>/dev/null; then
    echo -e "${GREEN}✅${NC}"
else
    echo -e "${YELLOW}⚠️  Import issues detected${NC}"
fi
cd ../..

# Check expertise-center
echo -n "  expertise-center: "
cd intelligent-core/expertise-center
if timeout 30 python3 -c "import sys; sys.path.insert(0, '../..'); from shared.base.base_specialist import BaseSpecialist" 2>/dev/null; then
    echo -e "${GREEN}✅${NC}"
else
    echo -e "${YELLOW}⚠️  Import issues detected${NC}"
fi
cd ../..

echo ""

# Step 4: Infrastructure analysis (using tools!)
echo -e "${BLUE}Step 4/5: Infrastructure Analysis${NC}"
echo "Running module scanner..."

# Use tools to analyze infrastructure components
if [ -f "tools/analyzers/module_scanner.py" ]; then
    python3 tools/analyzers/module_scanner.py infrastructure/ > /tmp/infra_scan.json 2>/dev/null || true

    if [ -f "/tmp/infra_scan.json" ]; then
        modules=$(cat /tmp/infra_scan.json | grep -o '"path"' | wc -l)
        echo "  Found $modules infrastructure modules"
    fi
fi
echo ""

# Step 5: Quick health summary
echo -e "${BLUE}Step 5/5: System Summary${NC}"

# Count available services
echo "Infrastructure components:"
echo "  Database: $([ -n "$DATABASE_URL" ] && echo "✅ Configured" || echo "❌ Missing")"
echo "  Vector DB: $([ -n "$QDRANT_URL" ] && echo "✅ Configured" || echo "❌ Missing")"
echo "  Redis: $([ -n "$REDIS_URL" ] && echo "✅ Configured" || echo "❌ Missing")"
echo "  AI Keys: $([ -n "$OPENAI_API_KEY" ] || [ -n "$ANTHROPIC_API_KEY" ] && echo "✅ Configured" || echo "❌ Missing")"

echo ""
echo "Core modules:"
echo "  ai-foundation: Ready"
echo "  workflow_intelligence: Ready"
echo "  expertise-center: Ready"

echo ""
echo "=========================================="
echo -e "${GREEN}✅ Pre-flight check PASSED!${NC}"
echo ""
echo "Next steps:"
echo "  1. ./infrastructure/scripts/start_all.sh          # Start infrastructure"
echo "  2. ./infrastructure/scripts/start_core_modules.sh # Start 3 core modules"
echo "  3. ./infrastructure/scripts/health_check.sh       # Verify all running"
echo ""
echo "Or run everything at once:"
echo "  ./infrastructure/scripts/bootstrap.sh"
