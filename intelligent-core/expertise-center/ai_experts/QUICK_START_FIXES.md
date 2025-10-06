# AI Experts Module - Quick Start Fix Guide

## IMMEDIATE ISSUE: Module Won't Import

```bash
$ python3 -c "import ai_experts"
ModuleNotFoundError: No module named 'ai_experts.ml.predictive_models'
```

**Root Cause:** `__init__.py` imports modules that don't exist yet

---

## Fix 1: Make Module Importable (5 minutes)

Edit `/Users/MD/AI-Platform-ISO/intelligent-core/ai_experts/__init__.py`:

```python
"""
AI Experts & ML Subsystem

Provides:
- AI Expert Agents (BCM Advisor, Compliance Auditor, Strategic Planner)
- RAG Pipeline (Knowledge retrieval + generation)
- ML Models (prediction, anomaly detection)
- Self-learning from Case Library
"""

__version__ = "1.0.0"

# Base classes
from .base.expert_agent import ExpertAgent

# Specialists (working)
from .specialists.bcm_advisor import BCMAdvisor
from .specialists.compliance_auditor import ComplianceAuditor
from .specialists.strategic_planner import StrategicPlanner

# TODO: Uncomment when implemented
# from .ml.predictive_models import WorkflowPredictor
# from .rag.pipeline import RAGPipeline

__all__ = [
    "ExpertAgent",
    "BCMAdvisor",
    "ComplianceAuditor",
    "StrategicPlanner",
    # "WorkflowPredictor",  # TODO
    # "RAGPipeline"         # TODO
]
```

**Test:**
```bash
cd /Users/MD/AI-Platform-ISO/intelligent-core
python3 -c "from ai_experts import BCMAdvisor; print('✅ Import works!')"
```

---

## Fix 2: Create Tool Stubs (1 hour)

### Step 1: Create `tools/base_tool.py`

```python
"""Base Tool for AI Experts"""
from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseTool(ABC):
    """Base class for AI expert tools"""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute tool logic"""
        pass

    def to_anthropic_tool(self) -> dict:
        """Convert to Anthropic tool format"""
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self._get_input_schema()
        }

    @abstractmethod
    def _get_input_schema(self) -> dict:
        """Return JSON schema for tool inputs"""
        pass
```

### Step 2: Create `tools/bia_tools.py` (Stub)

```python
"""BIA Tools"""
from .base_tool import BaseTool
from typing import Dict, Any

class BIAAnalysisTool(BaseTool):
    def __init__(self, workflow_engine):
        super().__init__(
            name="bia_analysis",
            description="Analyze Business Impact Analysis data"
        )
        self.workflow_engine = workflow_engine

    async def execute(self, **kwargs) -> Dict[str, Any]:
        # TODO: Implement BIA analysis logic
        return {"status": "stub", "message": "BIA analysis not implemented yet"}

    def _get_input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "workflow_id": {"type": "string"},
                "analysis_type": {"type": "string"}
            }
        }

class DependencyMapperTool(BaseTool):
    def __init__(self, case_library):
        super().__init__(
            name="dependency_mapper",
            description="Map process dependencies"
        )
        self.case_library = case_library

    async def execute(self, **kwargs) -> Dict[str, Any]:
        # TODO: Implement
        return {"status": "stub"}

    def _get_input_schema(self) -> dict:
        return {"type": "object", "properties": {}}
```

### Step 3: Create other tool files similarly

- `tools/compliance_tools.py` (3 tools)
- `tools/strategic_tools.py` (3 tools)
- `tools/case_library_tool.py` (1 tool)
- `tools/__init__.py`

---

## Fix 3: Create RAG Pipeline Stub (30 minutes)

### Create `rag/pipeline.py`

```python
"""RAG Pipeline Stub"""
from typing import List, Dict, Any

class RAGPipeline:
    """Retrieval-Augmented Generation pipeline (stub)"""

    def __init__(self, knowledge_sources: list):
        self.knowledge_sources = knowledge_sources

    async def retrieve(
        self,
        query: str,
        context: dict,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant knowledge (stub implementation)
        
        TODO: Implement:
        1. Generate embeddings
        2. Hybrid search (vector + keyword)
        3. Re-rank by relevance
        4. Return top-k
        """
        return [
            {
                "source": "stub",
                "content": f"Placeholder knowledge for: {query}",
                "relevance": 0.9
            }
        ]
```

### Create `rag/__init__.py`

```python
from .pipeline import RAGPipeline
__all__ = ["RAGPipeline"]
```

---

## Fix 4: Update Main `__init__.py` Again

```python
# After creating RAG stub
from .rag.pipeline import RAGPipeline

__all__ = [
    "ExpertAgent",
    "BCMAdvisor",
    "ComplianceAuditor",
    "StrategicPlanner",
    "RAGPipeline"
]
```

---

## Testing After Fixes

```python
# test_basic_import.py
from ai_experts import BCMAdvisor, RAGPipeline

# Mock dependencies
class MockKnowledgeGraph:
    pass

class MockCaseLibrary:
    pass

# Initialize
kg = MockKnowledgeGraph()
case_lib = MockCaseLibrary()

advisor = BCMAdvisor(case_library=case_lib, knowledge_graph=kg)
print(f"✅ BCM Advisor initialized: {advisor.name}")
print(f"   Tools: {list(advisor.tools.keys())}")
print(f"   Temperature: {advisor.temperature}")

# Test RAG
rag = RAGPipeline([kg])
import asyncio
results = asyncio.run(rag.retrieve("test query", {}))
print(f"✅ RAG Pipeline works: {len(results)} results")
```

**Expected Output:**
```
✅ BCM Advisor initialized: BCM Advisor
   Tools: ['bia_analysis', 'dependency_mapper', 'case_search']
   Temperature: 0.3
✅ RAG Pipeline works: 1 results
```

---

## Priority Order

1. **Fix imports** (5 min) - IMMEDIATE
2. **Create tool stubs** (1 hour) - TODAY
3. **Create RAG stub** (30 min) - TODAY
4. **Test end-to-end** (15 min) - TODAY

**Total Time:** ~2 hours to get module functional (with stubs)

---

## What Works After These Fixes

✅ Module can be imported
✅ Experts can be initialized
✅ Tools are available (stub implementations)
✅ RAG pipeline works (returns placeholder data)
✅ Can test expert.advise() method
✅ No import errors

## What Still Needs Implementation

❌ Tool logic (BIA analysis, compliance checks, etc.)
❌ RAG embeddings and search
❌ ML models
❌ Learning engine
❌ API endpoints
❌ Tests

But at least the module is FUNCTIONAL and can be developed incrementally!

---

**Next:** Start implementing real tool logic, beginning with highest priority (BIA tools)
