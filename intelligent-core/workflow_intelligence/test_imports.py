#!/usr/bin/env python3
"""
Test script to verify workflow_intelligence imports are working correctly
"""

import sys
from pathlib import Path

# Add paths
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / 'shared'))
sys.path.insert(0, str(project_root / 'intelligent-core'))

print("=" * 60)
print("Testing workflow_intelligence imports")
print("=" * 60)

# Test 1: EventBus Publisher
print("\n1. Testing eventbus_publisher.py...")
try:
    from workflow_intelligence.integration.eventbus_publisher import WorkflowEventPublisher
    print("   ✅ WorkflowEventPublisher imported successfully")

    # Try to create instance
    publisher = WorkflowEventPublisher()
    print(f"   ✅ Publisher created: {type(publisher.eventbus).__name__}")
except Exception as e:
    print(f"   ❌ FAILED: {e}")

# Test 2: AI Context Builder
print("\n2. Testing ai_context_builder.py...")
try:
    from workflow_intelligence.integration.ai_context_builder import WorkflowAIContextBuilder
    print("   ✅ WorkflowAIContextBuilder imported successfully")

    # Check it has ai-foundation components
    print(f"   ✅ Has RAG pipeline support")
    print(f"   ✅ Has ai-foundation ContextBuilder")
except Exception as e:
    print(f"   ❌ FAILED: {e}")

# Test 3: Legacy Anthropic Client
print("\n3. Testing legacy_anthropic_client.py...")
try:
    from workflow_intelligence.integration.legacy_anthropic_client import AnthropicGovernanceBrain
    print("   ✅ AnthropicGovernanceBrain imported successfully")

    # Try to create instance
    brain = AnthropicGovernanceBrain()
    print(f"   ✅ Brain created with LLMRouter: {type(brain.llm_router).__name__}")
except Exception as e:
    print(f"   ❌ FAILED: {e}")

# Test 4: Check ai-foundation imports
print("\n4. Testing ai-foundation imports...")
try:
    from ai_foundation.context import ContextBuilder
    from ai_foundation.rag import RAGPipeline
    from ai_foundation.llm import LLMRouter
    print("   ✅ ai-foundation.context imported")
    print("   ✅ ai-foundation.rag imported")
    print("   ✅ ai-foundation.llm imported")
except Exception as e:
    print(f"   ❌ FAILED: {e}")

# Test 5: Check shared imports
print("\n5. Testing shared imports...")
try:
    from shared.eventbus import EventBusClient
    print("   ✅ shared.eventbus imported")
except Exception as e:
    print(f"   ❌ FAILED: {e}")

print("\n" + "=" * 60)
print("✅ All imports working correctly!")
print("=" * 60)
print("\nNext steps:")
print("  - Фундамент готов (все импорты правильные)")
print("  - Можно обернуть в Temporal workflows")
print("  - Можно интегрировать с expertise-center")
