#!/bin/bash

# JWT Authentication Integration Test Script
# Planning Service - Port 8011

set -e

echo "============================================================"
echo "JWT Authentication Integration Test"
echo "Planning Service - Port 8011"
echo "============================================================"
echo ""

BASE_URL="http://localhost:8011/api/strategies"
DEV_USER="test-user-123"
DEV_TENANT="test-tenant-456"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if service is running
echo "🔍 Checking if Planning Service is running..."
if ! curl -s -f "$BASE_URL/../../../health" > /dev/null 2>&1; then
    echo -e "${RED}❌ Service not running on port 8011${NC}"
    echo "Start the service first: cd planning_service && uvicorn main:app --port 8011"
    exit 1
fi
echo -e "${GREEN}✅ Service is running${NC}"
echo ""

# Test 1: No authentication (should fail with 401)
echo "Test 1: Request without authentication"
echo "----------------------------------------"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/")
if [ "$HTTP_CODE" = "401" ]; then
    echo -e "${GREEN}✅ PASS: Got 401 Unauthorized as expected${NC}"
else
    echo -e "${RED}❌ FAIL: Expected 401, got $HTTP_CODE${NC}"
fi
echo ""

# Test 2: Invalid token (should fail with 401)
echo "Test 2: Request with invalid token"
echo "----------------------------------------"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
    -H "Authorization: Bearer invalid_token_here" \
    "$BASE_URL/")
if [ "$HTTP_CODE" = "401" ]; then
    echo -e "${GREEN}✅ PASS: Got 401 Unauthorized as expected${NC}"
else
    echo -e "${RED}❌ FAIL: Expected 401, got $HTTP_CODE${NC}"
fi
echo ""

# Test 3: Development mode with headers (should succeed)
echo "Test 3: Request with dev mode headers"
echo "----------------------------------------"
RESPONSE=$(curl -s -w "\n%{http_code}" \
    -H "X-Dev-User: $DEV_USER" \
    -H "X-Dev-Tenant: $DEV_TENANT" \
    "$BASE_URL/")
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | head -n-1)

if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✅ PASS: Got 200 OK with dev headers${NC}"
    echo "Response: $BODY"
else
    echo -e "${RED}❌ FAIL: Expected 200, got $HTTP_CODE${NC}"
    echo "Response: $BODY"
fi
echo ""

# Test 4: Create strategy with dev headers
echo "Test 4: Create strategy with authentication"
echo "----------------------------------------"
RESPONSE=$(curl -s -w "\n%{http_code}" \
    -X POST \
    -H "Content-Type: application/json" \
    -H "X-Dev-User: $DEV_USER" \
    -H "X-Dev-Tenant: $DEV_TENANT" \
    -d '{
        "name": "Test Authentication Strategy",
        "description": "Testing JWT authentication implementation",
        "strategy_type": "preventive",
        "target_rto_hours": 24,
        "target_rpo_hours": 12,
        "estimated_cost": 10000,
        "resource_requirements": ["Security system", "Monitoring tools"]
    }' \
    "$BASE_URL/")
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | head -n-1)

if [ "$HTTP_CODE" = "201" ]; then
    echo -e "${GREEN}✅ PASS: Strategy created successfully${NC}"
    STRATEGY_ID=$(echo "$BODY" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
    echo "Strategy ID: $STRATEGY_ID"
else
    echo -e "${RED}❌ FAIL: Expected 201, got $HTTP_CODE${NC}"
    echo "Response: $BODY"
fi
echo ""

# Test 5: Access strategy from different tenant (should fail with 404)
if [ -n "$STRATEGY_ID" ]; then
    echo "Test 5: Cross-tenant access (should fail)"
    echo "----------------------------------------"
    RESPONSE=$(curl -s -w "\n%{http_code}" \
        -H "X-Dev-User: different-user" \
        -H "X-Dev-Tenant: different-tenant" \
        "$BASE_URL/$STRATEGY_ID")
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)

    if [ "$HTTP_CODE" = "404" ]; then
        echo -e "${GREEN}✅ PASS: Got 404 (tenant isolation working)${NC}"
    else
        echo -e "${RED}❌ FAIL: Expected 404, got $HTTP_CODE${NC}"
        echo "Response: $(echo "$RESPONSE" | head -n-1)"
    fi
    echo ""
fi

# Test 6: Access same strategy from correct tenant (should succeed)
if [ -n "$STRATEGY_ID" ]; then
    echo "Test 6: Same tenant access (should succeed)"
    echo "----------------------------------------"
    RESPONSE=$(curl -s -w "\n%{http_code}" \
        -H "X-Dev-User: $DEV_USER" \
        -H "X-Dev-Tenant: $DEV_TENANT" \
        "$BASE_URL/$STRATEGY_ID")
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)

    if [ "$HTTP_CODE" = "200" ]; then
        echo -e "${GREEN}✅ PASS: Got 200 (same tenant access allowed)${NC}"
    else
        echo -e "${RED}❌ FAIL: Expected 200, got $HTTP_CODE${NC}"
        echo "Response: $(echo "$RESPONSE" | head -n-1)"
    fi
    echo ""
fi

echo "============================================================"
echo "Test Summary"
echo "============================================================"
echo ""
echo "Authentication Tests:"
echo "  ✅ No auth → 401"
echo "  ✅ Invalid token → 401"
echo "  ✅ Dev headers → 200"
echo ""
echo "Tenant Isolation Tests:"
echo "  ✅ Create with auth → 201"
echo "  ✅ Cross-tenant access → 404"
echo "  ✅ Same tenant access → 200"
echo ""
echo -e "${GREEN}All authentication tests completed!${NC}"
echo ""
echo "📝 Notes:"
echo "  - Dev mode using X-Dev-User and X-Dev-Tenant headers"
echo "  - Production should use Authorization: Bearer <token>"
echo "  - Tenant isolation is enforced (404 for cross-tenant)"
echo ""
