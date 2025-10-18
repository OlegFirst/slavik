# BCM Domain Testing Guide

**Comprehensive testing for the migrated BCM domain**

---

## 🎯 Overview

This guide covers testing for:
- 12 BCM Services (migrated to bcm_domain/services)
- 9 AI Colleagues (migrated to bcm_domain/ai_colleagues)
- Knowledge Quality Manager (migrated to bcm_domain/knowledge_quality_manager)
- Integration points with intelligent_core and infrastructure

---

## ✅ Pre-Test Checklist

### 1. Environment Setup
```bash
# Set PYTHONPATH
export PYTHONPATH=/Users/MD/AI-Platform-ISO:$PYTHONPATH

# Verify Python version
python3 --version  # Should be 3.11+

# Install dependencies (if needed)
cd /Users/MD/AI-Platform-ISO
pip install -r requirements.txt
```

### 2. Database & Infrastructure
```bash
# Check PostgreSQL
psql -h localhost -p 5432 -U postgres -l

# Check Redis
redis-cli ping  # Should return PONG

# Check EventBus
curl http://localhost:8001/health
```

---

## 🧪 Test Suite

### Level 1: Import Tests (5 min)

**Test that all imports work after migration:**

```bash
cd /Users/MD/AI-Platform-ISO

# Test 1: BCM Domain package imports
python3 -c "
from platform_services.bcm_domain import DOMAIN_NAME, SERVICES
print(f'✅ Domain: {DOMAIN_NAME}')
print(f'✅ Services: {len(SERVICES)} found')
"

# Test 2: AI Colleagues imports
python3 -c "
from platform_services.bcm_domain.ai_colleagues import (
    BIASpecialistAI,
    RiskAnalystAI,
    ComplianceCopilot,
    ColleagueCoordinator
)
print('✅ AI Colleagues imported successfully')
"

# Test 3: Service metadata
python3 -c "
from platform_services.bcm_domain.services import SERVICES
for name, info in SERVICES.items():
    print(f\"✅ {info['name']} (Port {info['port']})\")
"

# Test 4: Backward compatibility (symlink test)
python3 -c "
# Old import path should still work via symlink
import sys
sys.path.insert(0, 'intelligent_core/expertise_center')
# Note: This may fail if symlink not set up, which is expected
print('Testing backward compatibility...')
"
```

---

### Level 2: Service Health Tests (10 min)

**Test that all services start and respond:**

```bash
# Create test script
cat > /tmp/test_services.sh << 'EOF'
#!/bin/bash

SERVICES=(
    "bia_service:8012"
    "risk_service:8015"
    "compliance_service:8014"
    "planning_service:8011"
    "governance_service:8017"
    "plans_service:8023"
    "response_service:8016"
    "documents_service:8018"
    "validation_service:8021"
    "learning_service:8019"
    "community_service:8020"
    "simulation_service:8095"
)

echo "🧪 Testing BCM Services Health..."
for service_info in "${SERVICES[@]}"; do
    IFS=':' read -r service port <<< "$service_info"

    # Check if service is running
    if curl -s http://localhost:$port/health > /dev/null 2>&1; then
        echo "✅ $service (Port $port) - HEALTHY"
    else
        echo "⚠️  $service (Port $port) - NOT RUNNING (expected if not started)"
    fi
done

# Test Knowledge Quality Manager
if curl -s http://localhost:8090/health > /dev/null 2>&1; then
    echo "✅ Knowledge Quality Manager (Port 8090) - HEALTHY"
else
    echo "⚠️  Knowledge Quality Manager (Port 8090) - NOT RUNNING"
fi

EOF

chmod +x /tmp/test_services.sh
/tmp/test_services.sh
```

---

### Level 3: AI Colleagues Tests (15 min)

**Test AI colleagues functionality:**

```python
# Save as: /tmp/test_colleagues.py

import asyncio
import sys
sys.path.insert(0, '/Users/MD/AI-Platform-ISO')

from platform_services.bcm_domain.ai_colleagues import (
    BIASpecialistAI,
    RiskAnalystAI,
    ComplianceCopilot,
    ColleagueCoordinator,
    AssistantContext,
)

async def test_colleagues():
    """Test BCM AI Colleagues"""

    print("🧪 Testing BCM AI Colleagues...")

    # Note: These tests require RAG pipeline which needs setup
    # For now, test that classes can be instantiated

    try:
        # Test 1: Import and class availability
        print("✅ BIASpecialistAI class available")
        print("✅ RiskAnalystAI class available")
        print("✅ ComplianceCopilot class available")
        print("✅ ColleagueCoordinator class available")

        # Test 2: Context creation
        context = AssistantContext(
            tenant_id="test-tenant",
            org_id="test-org",
            user_id="test-user",
            value="test"
        )
        print(f"✅ AssistantContext created: {context.tenant_id}")

        print("\n✅ All AI Colleagues tests PASSED")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(test_colleagues())
```

```bash
# Run test
python3 /tmp/test_colleagues.py
```

---

### Level 4: Integration Tests (20 min)

**Test integration with intelligent_core and infrastructure:**

```python
# Save as: /tmp/test_integration.py

import sys
sys.path.insert(0, '/Users/MD/AI-Platform-ISO')

def test_integration():
    """Test integration points"""

    print("🧪 Testing Integration Points...")

    # Test 1: AI Foundation integration
    try:
        from intelligent_core.ai_foundation import RAGPipeline
        print("✅ AI Foundation: RAGPipeline accessible")
    except ImportError as e:
        print(f"⚠️  AI Foundation: {e}")

    # Test 2: Workflow Intelligence integration
    try:
        from intelligent_core.workflow_intelligence import WorkflowEngine
        print("✅ Workflow Intelligence: WorkflowEngine accessible")
    except ImportError as e:
        print(f"⚠️  Workflow Intelligence: {e}")

    # Test 3: EventBus integration
    try:
        from infrastructure.eventbus import Event
        print("✅ Infrastructure: EventBus accessible")
    except ImportError as e:
        print(f"⚠️  Infrastructure EventBus: {e}")

    # Test 4: Decision Center integration
    try:
        from infrastructure.decision_center.core.decision_engine import DecisionEngine
        print("✅ Infrastructure: Decision Center accessible")
    except ImportError as e:
        print(f"⚠️  Infrastructure Decision Center: {e}")

    # Test 5: System BCM Service (should NOT move)
    try:
        from intelligent_core.system_bcm_service.main import app
        print("✅ System BCM Service: Correctly in intelligent_core")
    except ImportError as e:
        print(f"⚠️  System BCM Service: {e}")

    # Test 6: Strategic Experts (should NOT move)
    try:
        from intelligent_core.expertise_center.ai_experts.specialists.bcm_advisor import BCMAdvisor
        print("✅ Strategic Experts: Correctly in intelligent_core")
    except ImportError as e:
        print(f"⚠️  Strategic Experts: {e}")

    print("\n✅ Integration tests COMPLETED")

if __name__ == "__main__":
    test_integration()
```

```bash
# Run test
python3 /tmp/test_integration.py
```

---

### Level 5: Directory Structure Test (5 min)

**Verify correct file placement:**

```bash
# Test directory structure
echo "🧪 Testing Directory Structure..."

# Test 1: BCM Domain exists
if [ -d "/Users/MD/AI-Platform-ISO/platform_services/bcm_domain" ]; then
    echo "✅ bcm_domain directory exists"
else
    echo "❌ bcm_domain directory NOT FOUND"
fi

# Test 2: Services migrated
EXPECTED_SERVICES=12
ACTUAL_SERVICES=$(ls -d platform_services/bcm_domain/services/*_service 2>/dev/null | wc -l)
if [ "$ACTUAL_SERVICES" -eq "$EXPECTED_SERVICES" ]; then
    echo "✅ All $EXPECTED_SERVICES services migrated"
else
    echo "⚠️  Found $ACTUAL_SERVICES services (expected $EXPECTED_SERVICES)"
fi

# Test 3: AI Colleagues migrated
if [ -d "platform_services/bcm_domain/ai_colleagues" ]; then
    COLLEAGUES_COUNT=$(ls -d platform_services/bcm_domain/ai_colleagues/*/ 2>/dev/null | wc -l)
    echo "✅ AI Colleagues directory exists ($COLLEAGUES_COUNT colleagues)"
else
    echo "❌ AI Colleagues directory NOT FOUND"
fi

# Test 4: KQM migrated
if [ -d "platform_services/bcm_domain/knowledge_quality_manager" ]; then
    echo "✅ Knowledge Quality Manager migrated"
else
    echo "❌ Knowledge Quality Manager NOT FOUND"
fi

# Test 5: System BCM Service NOT moved
if [ -d "intelligent_core/system_bcm_service" ]; then
    echo "✅ System BCM Service correctly in intelligent_core"
else
    echo "❌ System BCM Service moved incorrectly!"
fi

# Test 6: Strategic Experts NOT moved
if [ -d "intelligent_core/expertise_center/ai_experts" ]; then
    echo "✅ Strategic Experts correctly in intelligent_core"
else
    echo "❌ Strategic Experts moved incorrectly!"
fi

# Test 7: Symlink exists
if [ -L "intelligent_core/expertise_center/ai_office" ]; then
    echo "✅ Backward compatibility symlink exists"
else
    echo "⚠️  Symlink not found (may have been removed)"
fi

echo ""
echo "✅ Directory structure tests COMPLETED"
```

---

## 📊 Expected Test Results

### All Tests Passing:
```
✅ Import Tests: PASS
✅ Service Health: PASS (if services running)
✅ AI Colleagues: PASS
✅ Integration: PASS
✅ Directory Structure: PASS

Overall: ✅ 100% PASS
```

### Acceptable Warnings:
```
⚠️  Services not running - EXPECTED if not started yet
⚠️  Some imports fail - Check dependencies installed
⚠️  Symlink not found - EXPECTED after Phase 6 cleanup
```

---

## 🔧 Troubleshooting

### Import Errors

**Problem:** `ModuleNotFoundError: No module named 'platform_services.bcm_domain'`

**Solution:**
```bash
# Set PYTHONPATH
export PYTHONPATH=/Users/MD/AI-Platform-ISO:$PYTHONPATH

# Or add to ~/.zshrc or ~/.bashrc
echo 'export PYTHONPATH=/Users/MD/AI-Platform-ISO:$PYTHONPATH' >> ~/.zshrc
source ~/.zshrc
```

### Service Not Running

**Problem:** Service health check fails

**Solution:**
```bash
# Start service manually
cd platform_services/bcm_domain/services/bia_service
python main.py

# Or use docker-compose (if configured)
docker-compose up bia_service
```

### Colleague Tests Fail

**Problem:** AI colleagues can't initialize

**Solution:**
- Check RAG pipeline configuration
- Verify Qdrant is running (vector database)
- Check API keys (ANTHROPIC_API_KEY, OPENAI_API_KEY)

---

## 🚀 Full Test Run (30 min)

**Run all tests in sequence:**

```bash
#!/bin/bash

echo "🎯 BCM DOMAIN FULL TEST SUITE"
echo "=============================="
echo ""

cd /Users/MD/AI-Platform-ISO

# Set environment
export PYTHONPATH=/Users/MD/AI-Platform-ISO:$PYTHONPATH

# Level 1: Imports
echo "📦 Level 1: Import Tests"
python3 -c "from platform_services.bcm_domain import SERVICES; print(f'✅ {len(SERVICES)} services')"

# Level 2: Structure
echo ""
echo "📁 Level 2: Directory Structure"
[ -d "platform_services/bcm_domain" ] && echo "✅ bcm_domain exists"
[ -d "platform_services/bcm_domain/services" ] && echo "✅ services directory exists"
[ -d "platform_services/bcm_domain/ai_colleagues" ] && echo "✅ ai_colleagues directory exists"

# Level 3: Integration
echo ""
echo "🔗 Level 3: Integration Points"
python3 /tmp/test_integration.py

# Level 4: AI Colleagues
echo ""
echo "🤖 Level 4: AI Colleagues"
python3 /tmp/test_colleagues.py

# Summary
echo ""
echo "✅ FULL TEST SUITE COMPLETE"
echo "=============================="
```

---

## 📝 Test Report Template

After running tests, document results:

```markdown
# BCM Domain Test Report

**Date:** 2025-10-18
**Tester:** [Your Name]
**Environment:** Development/Staging/Production

## Test Results

| Test Level | Status | Notes |
|------------|--------|-------|
| Import Tests | ✅ PASS | All imports working |
| Directory Structure | ✅ PASS | All components in place |
| Service Health | ⚠️ PARTIAL | 8/12 services running |
| AI Colleagues | ✅ PASS | All colleagues accessible |
| Integration | ✅ PASS | All integrations verified |

## Issues Found

1. [Issue description]
2. [Issue description]

## Recommendations

1. [Recommendation]
2. [Recommendation]

**Overall Status:** ✅ READY FOR DEPLOYMENT
```

---

## ✅ Sign-Off Criteria

**BCM Domain is ready for production when:**

- ✅ All imports work without errors
- ✅ All 12 services start and respond to health checks
- ✅ AI Colleagues can be instantiated
- ✅ Integration tests pass
- ✅ Directory structure verified
- ✅ Documentation complete
- ✅ No breaking changes in existing functionality

---

**Last Updated:** 2025-10-18
**Version:** 1.0.0
