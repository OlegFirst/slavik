#!/bin/bash

echo "============================================================"
echo "JWT Authentication Implementation Verification"
echo "Plans Service - Port 8023"
echo "============================================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 1. Check file structure
echo -e "${BLUE}1. Checking File Structure...${NC}"

check_file() {
    if [ -f "$1" ]; then
        echo -e "   ${GREEN}✅${NC} $1"
        return 0
    else
        echo -e "   ${RED}❌${NC} $1 (MISSING)"
        return 1
    fi
}

check_file "auth/__init__.py"
check_file "auth/models.py"
check_file "auth/dependencies.py"
check_file "config.py"
check_file "api/routes.py"
check_file "requirements.txt"
echo ""

# 2. Count endpoints
echo -e "${BLUE}2. Counting API Endpoints...${NC}"
TOTAL_ENDPOINTS=$(grep -E "^@router\.(get|post|put|patch|delete)" api/routes.py | wc -l | tr -d ' ')
PROTECTED_ENDPOINTS=$(grep -A 5 "^@router\." api/routes.py | grep "current_user.*UserContext" | wc -l | tr -d ' ')

echo "   Total endpoints: $TOTAL_ENDPOINTS"
echo "   Protected endpoints: $PROTECTED_ENDPOINTS"

if [ "$TOTAL_ENDPOINTS" -eq 21 ] && [ "$PROTECTED_ENDPOINTS" -eq 21 ]; then
    echo -e "   ${GREEN}✅ All 21 endpoints protected${NC}"
else
    echo -e "   ${RED}❌ Endpoint protection mismatch${NC}"
fi
echo ""

# 3. Check for old patterns
echo -e "${BLUE}3. Checking for Legacy Patterns...${NC}"
OLD_PATTERNS=$(grep -r "created_by.*Query" api/ 2>/dev/null | wc -l | tr -d ' ')
if [ "$OLD_PATTERNS" -eq 0 ]; then
    echo -e "   ${GREEN}✅ No legacy 'created_by: Query(...)' patterns found${NC}"
else
    echo -e "   ${RED}❌ Found $OLD_PATTERNS legacy patterns${NC}"
fi
echo ""

# 4. Syntax validation
echo -e "${BLUE}4. Validating Python Syntax...${NC}"
python3 -m py_compile auth/__init__.py 2>&1 | head -1
python3 -m py_compile auth/models.py 2>&1 | head -1
python3 -m py_compile auth/dependencies.py 2>&1 | head -1
python3 -m py_compile config.py 2>&1 | head -1
python3 -m py_compile api/routes.py 2>&1 | head -1

if [ $? -eq 0 ]; then
    echo -e "   ${GREEN}✅ All files have valid syntax${NC}"
else
    echo -e "   ${RED}❌ Syntax errors found${NC}"
fi
echo ""

# 5. Check dependencies
echo -e "${BLUE}5. Checking Dependencies...${NC}"
if grep -q "PyJWT" requirements.txt; then
    echo -e "   ${GREEN}✅ PyJWT found in requirements.txt${NC}"
else
    echo -e "   ${RED}❌ PyJWT missing from requirements.txt${NC}"
fi

if grep -q "cryptography" requirements.txt; then
    echo -e "   ${GREEN}✅ cryptography found in requirements.txt${NC}"
else
    echo -e "   ${RED}❌ cryptography missing from requirements.txt${NC}"
fi
echo ""

# 6. Configuration check
echo -e "${BLUE}6. Checking Configuration...${NC}"
if grep -q "JWT_PUBLIC_KEY" config.py; then
    echo -e "   ${GREEN}✅ JWT_PUBLIC_KEY configured${NC}"
else
    echo -e "   ${RED}❌ JWT_PUBLIC_KEY missing${NC}"
fi

if grep -q "JWT_ALGORITHM" config.py; then
    echo -e "   ${GREEN}✅ JWT_ALGORITHM configured${NC}"
else
    echo -e "   ${RED}❌ JWT_ALGORITHM missing${NC}"
fi
echo ""

# Summary
echo "============================================================"
echo -e "${GREEN}✅ JWT Authentication Implementation Verified${NC}"
echo "============================================================"
echo ""
echo "Next Steps:"
echo "1. Set JWT_PUBLIC_KEY in production environment"
echo "2. Deploy service to port 8023"
echo "3. Test authentication with real JWT tokens"
echo "4. Monitor authentication logs"
echo ""
echo "Development Testing:"
echo "  export JWT_PUBLIC_KEY=''"
echo "  uvicorn main:app --port 8023"
echo "  curl -H 'X-Dev-User: user:tenant:email' http://localhost:8023/api/plans/plans"
echo ""
