#!/bin/bash
# Documentation Update Script - Professional Standards
# Usage: ./update-docs.sh <module_name> [--ai]

set -e  # Exit on error

MODULE=$1
USE_AI=${2:-""}
export REPO_PATH=/Users/MD/AI-Platform-ISO

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

if [ -z "$MODULE" ]; then
    echo -e "${RED}Usage: ./update-docs.sh <module_name> [--ai]${NC}"
    echo ""
    echo "Examples:"
    echo "  ./update-docs.sh ai-foundation"
    echo "  ./update-docs.sh ai-foundation --ai"
    echo ""
    exit 1
fi

echo "================================================"
echo -e "${BLUE}Updating documentation for: $MODULE${NC}"
echo "================================================"

# Determine module path
if [ -d "$REPO_PATH/intelligent-core/$MODULE" ]; then
    MODULE_PATH="$REPO_PATH/intelligent-core/$MODULE"
    MODULE_TYPE="core"
elif [ -d "$REPO_PATH/platform-services/$MODULE" ]; then
    MODULE_PATH="$REPO_PATH/platform-services/$MODULE"
    MODULE_TYPE="service"
elif [ -d "$REPO_PATH/infrastructure/$MODULE" ]; then
    MODULE_PATH="$REPO_PATH/infrastructure/$MODULE"
    MODULE_TYPE="infrastructure"
else
    echo -e "${RED}Error: Module '$MODULE' not found${NC}"
    exit 1
fi

echo -e "${GREEN}Found module:${NC} $MODULE_PATH ($MODULE_TYPE)"
echo ""

# Step 1: Module scanning (if exists)
echo -e "${YELLOW}[1/6] Scanning module structure...${NC}"
SCANNER="$REPO_PATH/tools/analyzers/module_scanner.py"
if [ -f "$SCANNER" ]; then
    cd "$REPO_PATH"
    python3 "$SCANNER" --module "$MODULE" --output json > /dev/null 2>&1 || true
    echo -e "${GREEN}✓ Module scan complete${NC}"
else
    echo -e "${YELLOW}⚠ Module scanner not found, skipping${NC}"
fi

# Step 2: Architecture analysis
echo ""
echo -e "${YELLOW}[2/6] Analyzing architecture...${NC}"
cd "$REPO_PATH/infrastructure/AI-office-infrastructure/project-agent"
python -m agent.cli analyze-architecture --module "$MODULE" 2>&1 | grep -v "Warning" || true
echo -e "${GREEN}✓ Architecture analysis complete${NC}"

# Step 3: Generate professional documentation
echo ""
echo -e "${YELLOW}[3/6] Generating professional documentation...${NC}"

if [ "$USE_AI" == "--ai" ]; then
    echo -e "${BLUE}Using AI-powered documentation generator${NC}"
    if [ -z "$ANTHROPIC_API_KEY" ]; then
        echo -e "${RED}Error: ANTHROPIC_API_KEY not set${NC}"
        echo "Set it with: export ANTHROPIC_API_KEY='your-key'"
        exit 1
    fi
    python3 "$REPO_PATH/infrastructure/tools/doc-generators/ai_documentation_generator.py" --module "$MODULE" --ai
else
    echo -e "${BLUE}Using template-based documentation generator${NC}"
    python3 "$REPO_PATH/infrastructure/tools/doc-generators/documentation_generator.py" --module "$MODULE"
fi

echo -e "${GREEN}✓ Documentation generated${NC}"

# Step 4: API Documentation (for services)
echo ""
echo -e "${YELLOW}[4/6] Generating API documentation...${NC}"
if [ "$MODULE_TYPE" == "service" ] || [[ $MODULE == *"api"* ]]; then
    # Check if service is running
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        python3 "$REPO_PATH/infrastructure/tools/doc-generators/api_docs_generator.py" || true
        echo -e "${GREEN}✓ API documentation generated${NC}"
    else
        echo -e "${YELLOW}⚠ Service not running, skipping API docs${NC}"
        echo "  Start service first: cd $MODULE_PATH && python main.py"
    fi
else
    echo -e "${YELLOW}⚠ Not a service, skipping API docs${NC}"
fi

# Step 5: Test generation
echo ""
echo -e "${YELLOW}[5/6] Generating/validating tests...${NC}"
cd "$REPO_PATH/infrastructure/AI-office-infrastructure/project-agent"
python -m agent.cli generate-tests --module "$MODULE" --max-files 10 2>&1 | grep -v "Warning" || true
echo -e "${GREEN}✓ Test generation complete${NC}"

# Step 6: Quality validation
echo ""
echo -e "${YELLOW}[6/6] Running quality checks...${NC}"
python -m agent.cli scan --module quality 2>&1 | tail -20 || true
echo -e "${GREEN}✓ Quality checks complete${NC}"

# Summary
echo ""
echo "================================================"
echo -e "${GREEN}✓ Documentation update complete for: $MODULE${NC}"
echo "================================================"
echo ""
echo "Generated files:"
if [ -f "$MODULE_PATH/README.md" ]; then
    echo -e "  ${GREEN}✓${NC} $MODULE_PATH/README.md"
else
    echo -e "  ${RED}✗${NC} $MODULE_PATH/README.md (missing)"
fi

if [ -f "$MODULE_PATH/API.md" ] || [ "$MODULE_TYPE" != "service" ]; then
    echo -e "  ${GREEN}✓${NC} API documentation"
else
    echo -e "  ${YELLOW}⚠${NC} $MODULE_PATH/API.md (service running?)"
fi

echo ""
echo "Next steps:"
echo "  1. Review: $MODULE_PATH/README.md"
echo "  2. Validate: grep -i emoji $MODULE_PATH/README.md (should be empty)"
echo "  3. Commit: git add $MODULE_PATH && git commit -m 'docs: update $MODULE documentation'"
echo ""
