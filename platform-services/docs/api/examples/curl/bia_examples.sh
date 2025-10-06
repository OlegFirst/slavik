#!/bin/bash
# BIA Service API Examples using cURL
# ISO 22301:2019 Clause 8.2.2 - Business Impact Analysis

# Configuration
BASE_URL="http://localhost:8012"
TENANT_ID="tenant-123"
USER_ID="user-456"

# Development mode authentication header
DEV_USER='{"sub":"user-456","tenant_id":"tenant-123","permissions":["BIA_VIEW","BIA_CREATE","BIA_UPDATE","BIA_DELETE","BIA_COMPLETE","BIA_AI_SUGGEST"]}'

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "BIA Service API Examples"
echo "ISO 22301:2019 Clause 8.2.2"
echo "=========================================="
echo ""

# Example 1: Health Check
echo -e "${BLUE}1. Health Check${NC}"
echo "GET $BASE_URL/health"
curl -s -X GET "$BASE_URL/health" | jq '.'
echo ""

# Example 2: Create BIA Process
echo -e "${BLUE}2. Create BIA Process${NC}"
echo "POST $BASE_URL/api/bia/processes"
curl -s -X POST "$BASE_URL/api/bia/processes" \
  -H "X-Dev-User: $DEV_USER" \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "'"$TENANT_ID"'",
    "name": "Payment Processing System",
    "description": "Core payment processing for customer transactions",
    "department": "Finance Operations",
    "process_owner": "jane.smith@company.com",
    "criticality": "CRITICAL",
    "rto_hours": 2,
    "rpo_hours": 1,
    "mtpd_hours": 4,
    "financial_impact": {
      "1_hour": 50000,
      "4_hours": 200000,
      "24_hours": 1200000
    },
    "dependencies": [
      {
        "type": "technology",
        "name": "Payment Gateway API",
        "criticality": 5,
        "required": true
      }
    ],
    "industry": "FINANCIAL_SERVICES"
  }' | jq '.'
echo ""

# Example 3: List BIA Processes
echo -e "${BLUE}3. List BIA Processes (filter by criticality)${NC}"
echo "GET $BASE_URL/api/bia/processes?tenant_id=$TENANT_ID&criticality=CRITICAL"
curl -s -X GET "$BASE_URL/api/bia/processes?tenant_id=$TENANT_ID&criticality=CRITICAL" \
  -H "X-Dev-User: $DEV_USER" | jq '.'
echo ""

# Example 4: Get BIA Process by ID
echo -e "${BLUE}4. Get BIA Process by ID${NC}"
echo "GET $BASE_URL/api/bia/processes/1?tenant_id=$TENANT_ID"
curl -s -X GET "$BASE_URL/api/bia/processes/1?tenant_id=$TENANT_ID" \
  -H "X-Dev-User: $DEV_USER" | jq '.'
echo ""

# Example 5: Update BIA Process
echo -e "${BLUE}5. Update BIA Process (change RTO)${NC}"
echo "PUT $BASE_URL/api/bia/processes/1?tenant_id=$TENANT_ID"
curl -s -X PUT "$BASE_URL/api/bia/processes/1?tenant_id=$TENANT_ID" \
  -H "X-Dev-User: $DEV_USER" \
  -H "Content-Type: application/json" \
  -d '{
    "rto_hours": 1,
    "description": "Updated with stricter 1-hour RTO based on financial impact analysis"
  }' | jq '.'
echo ""

# Example 6: AI RTO Suggestion
echo -e "${BLUE}6. AI-Powered RTO/RPO Suggestion${NC}"
echo "POST $BASE_URL/api/bia/processes/1/suggest-rto?tenant_id=$TENANT_ID"
curl -s -X POST "$BASE_URL/api/bia/processes/1/suggest-rto?tenant_id=$TENANT_ID" \
  -H "X-Dev-User: $DEV_USER" | jq '.'
echo ""

# Example 7: AI Dependency Discovery
echo -e "${BLUE}7. AI Dependency Discovery${NC}"
echo "POST $BASE_URL/api/bia/processes/1/discover-dependencies?tenant_id=$TENANT_ID"
curl -s -X POST "$BASE_URL/api/bia/processes/1/discover-dependencies?tenant_id=$TENANT_ID" \
  -H "X-Dev-User: $DEV_USER" | jq '.'
echo ""

# Example 8: Bulk Create Processes
echo -e "${BLUE}8. Bulk Create BIA Processes${NC}"
echo "POST $BASE_URL/api/bia/processes/bulk?tenant_id=$TENANT_ID"
curl -s -X POST "$BASE_URL/api/bia/processes/bulk?tenant_id=$TENANT_ID" \
  -H "X-Dev-User: $DEV_USER" \
  -H "Content-Type: application/json" \
  -d '{
    "processes": [
      {
        "tenant_id": "'"$TENANT_ID"'",
        "name": "Email System",
        "criticality": "HIGH",
        "rto_hours": 8,
        "rpo_hours": 4,
        "mtpd_hours": 24
      },
      {
        "tenant_id": "'"$TENANT_ID"'",
        "name": "CRM System",
        "criticality": "MEDIUM",
        "rto_hours": 24,
        "rpo_hours": 12,
        "mtpd_hours": 72
      }
    ],
    "max_concurrency": 10
  }' | jq '.'
echo ""

# Example 9: Complete BIA Process
echo -e "${BLUE}9. Mark BIA Process as Completed${NC}"
echo "POST $BASE_URL/api/bia/processes/1/complete?tenant_id=$TENANT_ID"
curl -s -X POST "$BASE_URL/api/bia/processes/1/complete?tenant_id=$TENANT_ID" \
  -H "X-Dev-User: $DEV_USER" | jq '.'
echo ""

# Example 10: Summary Report
echo -e "${BLUE}10. Get BIA Summary Report${NC}"
echo "GET $BASE_URL/api/bia/reports/summary?tenant_id=$TENANT_ID"
curl -s -X GET "$BASE_URL/api/bia/reports/summary?tenant_id=$TENANT_ID" \
  -H "X-Dev-User: $DEV_USER" | jq '.'
echo ""

# Example 11: Critical Processes Report
echo -e "${BLUE}11. Get Critical Processes Report${NC}"
echo "GET $BASE_URL/api/bia/reports/critical-processes?tenant_id=$TENANT_ID"
curl -s -X GET "$BASE_URL/api/bia/reports/critical-processes?tenant_id=$TENANT_ID" \
  -H "X-Dev-User: $DEV_USER" | jq '.'
echo ""

# Example 12: Dependencies Report
echo -e "${BLUE}12. Get Dependencies Mapping Report${NC}"
echo "GET $BASE_URL/api/bia/reports/dependencies?tenant_id=$TENANT_ID"
curl -s -X GET "$BASE_URL/api/bia/reports/dependencies?tenant_id=$TENANT_ID" \
  -H "X-Dev-User: $DEV_USER" | jq '.'
echo ""

# Example 13: Delete BIA Process
echo -e "${BLUE}13. Delete BIA Process${NC}"
echo "DELETE $BASE_URL/api/bia/processes/1?tenant_id=$TENANT_ID"
curl -s -X DELETE "$BASE_URL/api/bia/processes/1?tenant_id=$TENANT_ID" \
  -H "X-Dev-User: $DEV_USER" | jq '.'
echo ""

echo -e "${GREEN}=========================================="
echo "All BIA API examples completed!"
echo "==========================================${NC}"

# Production JWT Example (commented out)
: '
# For production, replace X-Dev-User header with JWT Bearer token:

JWT_TOKEN="your_jwt_token_here"

curl -X GET "$BASE_URL/api/bia/processes?tenant_id=$TENANT_ID" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json"
'
