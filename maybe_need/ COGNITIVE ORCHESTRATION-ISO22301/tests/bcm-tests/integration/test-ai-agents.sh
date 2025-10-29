#!/bin/bash

# Test Script for AI Agent Orchestration Platform
# BCM Platform - Docker AI Agent Integration Test

set -e

echo "🤖 Testing BCM Platform AI Agent Orchestration"
echo "=============================================="

# Test 1: Start core infrastructure
echo "📦 Step 1: Starting core infrastructure..."
docker-compose up -d postgres redis rabbitmq
sleep 5

echo "✅ Core infrastructure status:"
docker-compose ps postgres redis rabbitmq

# Test 2: Start AI Orchestrator
echo ""
echo "🧠 Step 2: Starting AI Orchestrator..."
docker-compose up -d ai_orchestrator
sleep 10

echo "✅ AI Orchestrator health check:"
curl -f http://localhost:8000/health || echo "❌ Orchestrator not ready"

# Test 3: Start supporting AI services
echo ""
echo "🔧 Step 3: Starting AI agent services..."
docker-compose up -d unified_ai github_app pdca_assistant
sleep 15

# Test 4: Health check all AI agents
echo ""
echo "🏥 Step 4: Health checking all AI agents..."
echo "Orchestrator:"
curl -s http://localhost:8000/health | jq .status || echo "❌ Failed"

echo "Unified AI:"
curl -s http://localhost:8090/health | jq .status || echo "❌ Failed"

echo "GitHub App:"
curl -s http://localhost:8001/health | jq .status || echo "❌ Failed"

echo "PDCA Assistant:"
curl -s http://localhost:8010/health | jq .status || echo "❌ Failed"

# Test 5: Test AI Agent routing
echo ""
echo "🔀 Step 5: Testing AI Agent routing..."

echo "Testing PDCA capability:"
curl -X POST http://localhost:8000/ai/process \
  -H "Content-Type: application/json" \
  -d '{
    "capability": "pdca",
    "data": {"phase": "plan", "context": "risk_assessment"},
    "context": {"user": "test", "priority": "high"}
  }' || echo "❌ PDCA routing failed"

echo ""
echo "Testing BIA capability:"
curl -X POST http://localhost:8000/ai/process \
  -H "Content-Type: application/json" \
  -d '{
    "capability": "bia",
    "data": {"business_process": "customer_service", "impact_criteria": ["financial", "operational"]},
    "context": {"tenant": "test_org"}
  }' || echo "❌ BIA routing failed"

# Test 6: Check agent analytics
echo ""
echo "📊 Step 6: Checking AI agent analytics..."
curl -s http://localhost:8000/ai/agents/analytics | jq .analytics.agents || echo "❌ Analytics failed"

# Test 7: Agent discovery and health
echo ""
echo "🔍 Step 7: Agent discovery and health monitoring..."
curl -s http://localhost:8000/ai/agents/health | jq .healthy_count || echo "❌ Health monitoring failed"

echo ""
echo "🎉 AI Agent Platform Test Complete!"
echo "=================================="

# Show running services
echo "📋 Currently running services:"
docker-compose ps ai_orchestrator unified_ai github_app pdca_assistant

echo ""
echo "🌐 Available endpoints:"
echo "• Main Orchestrator: http://localhost:8000/docs"
echo "• AI Agent Health: http://localhost:8000/ai/agents/health"
echo "• AI Agent Analytics: http://localhost:8000/ai/agents/analytics"
echo "• GitHub Integration: http://localhost:8001/"
echo "• PDCA Assistant: http://localhost:8010/"
echo "• Unified AI: http://localhost:8090/"

echo ""
echo "✨ Ready for intelligent BCM orchestration!"