#!/bin/bash
# Quick test script for Phase 4 features

BASE_URL="http://localhost:8031"

echo "🧪 Testing AI Intelligence Layer - Phase 4"
echo "=========================================="
echo ""

# Test 1: Health check
echo "1️⃣ Testing health endpoint..."
curl -s "$BASE_URL/health" | python3 -m json.tool
echo ""

# Test 2: List colleagues
echo "2️⃣ Listing AI colleagues..."
curl -s "$BASE_URL/api/ai/colleagues" | python3 -m json.tool
echo ""

# Test 3: Test all components
echo "3️⃣ Testing all components..."
curl -s "$BASE_URL/api/ai/test" | python3 -m json.tool
echo ""

# Test 4: Auto-routing (should route to Risk Analyst)
echo "4️⃣ Testing auto-routing with risk query..."
curl -s -X POST "$BASE_URL/api/ai/coordinate" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are our top 5 risks according to FAIR methodology?",
    "tenant_id": "demo",
    "colleague_type": "auto"
  }' | python3 -m json.tool
echo ""

# Test 5: Manual routing to BIA Specialist
echo "5️⃣ Testing manual routing to BIA Specialist..."
curl -s -X POST "$BASE_URL/api/ai/coordinate" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What should be the RTO for our order processing system?",
    "tenant_id": "demo",
    "colleague_type": "bia_specialist"
  }' | python3 -m json.tool
echo ""

# Test 6: Coordinator stats
echo "6️⃣ Getting coordinator statistics..."
curl -s "$BASE_URL/api/ai/coordinator/stats" | python3 -m json.tool
echo ""

# Test 7: EventBus stats
echo "7️⃣ Getting EventBus statistics..."
curl -s "$BASE_URL/api/ai/eventbus/stats" | python3 -m json.tool
echo ""

# Test 8: Execute workflow
echo "8️⃣ Testing cross-colleague workflow (risk→bia→plans)..."
curl -s -X POST "$BASE_URL/api/ai/workflow" \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_name": "risk_to_plans",
    "initial_query": "Analyze ransomware risk and generate recovery plans",
    "tenant_id": "demo"
  }' | python3 -m json.tool
echo ""

echo "✅ Phase 4 testing complete!"
