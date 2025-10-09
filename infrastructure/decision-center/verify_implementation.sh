#!/bin/bash

echo "Policy Engine Implementation Verification"
echo "=========================================="
echo ""

# Check all required files exist
echo "Checking files..."
files=(
    "policy_engine.py"
    "policy_validator.py"
    "policy_models.py"
    "policies.yaml"
    "test_policy_engine.py"
    "example_usage.py"
    "README.md"
    "IMPLEMENTATION_SUMMARY.md"
    "requirements.txt"
    "__init__.py"
)

all_present=true
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✓ $file"
    else
        echo "  ✗ $file MISSING"
        all_present=false
    fi
done

if [ "$all_present" = true ]; then
    echo ""
    echo "✓ All implementation files present!"
else
    echo ""
    echo "✗ Some files are missing"
    exit 1
fi

# Check file sizes
echo ""
echo "File sizes:"
echo "  policy_engine.py:    $(wc -l < policy_engine.py) lines"
echo "  policy_validator.py: $(wc -l < policy_validator.py) lines"
echo "  policy_models.py:    $(wc -l < policy_models.py) lines"
echo "  policies.yaml:       $(wc -l < policies.yaml) lines"
echo "  README.md:           $(wc -l < README.md) lines"

# Check YAML syntax
echo ""
echo "Validating YAML syntax..."
if python3 -c "import yaml; yaml.safe_load(open('policies.yaml'))" 2>/dev/null; then
    echo "  ✓ policies.yaml has valid YAML syntax"
else
    echo "  ✗ policies.yaml has YAML syntax errors"
    exit 1
fi

# Check Python syntax
echo ""
echo "Checking Python syntax..."
for pyfile in policy_engine.py policy_validator.py policy_models.py; do
    if python3 -m py_compile "$pyfile" 2>/dev/null; then
        echo "  ✓ $pyfile syntax OK"
    else
        echo "  ✗ $pyfile has syntax errors"
        exit 1
    fi
done

echo ""
echo "=========================================="
echo "✓ Implementation verification complete!"
echo "=========================================="
echo ""
echo "Summary:"
echo "  - All 10 implementation files present"
echo "  - YAML syntax valid"
echo "  - Python syntax valid"
echo "  - Ready for integration"
echo ""
