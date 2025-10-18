# AI Colleagues Import Fix Note

## Issue

AI colleagues were copied from `ai_office` with old relative imports:
```python
from core import RAGPipeline
from colleagues.base import BaseAIColleague
```

## Temporary Solution

The colleagues work when imported via the package interface:
```python
from platform_services.bcm_domain.ai_colleagues import BIASpecialistAI
```

This works because `__init__.py` handles the imports correctly.

## Permanent Solution (Future)

Update all colleague files to use absolute imports:

```python
# OLD (relative)
from core import RAGPipeline
from colleagues.base import BaseAIColleague

# NEW (absolute)
from intelligent_core.ai_foundation import RAGPipeline
from platform_services.bcm_domain.ai_colleagues.base.base_colleague import BaseAIColleague
```

**Files to update:**
- bia_specialist/bia_specialist.py
- risk_analyst/risk_analyst.py
- compliance_copilot/compliance_copilot.py
- exercise_designer/exercise_designer.py
- incident_advisor/incident_advisor.py
- plan_generator/plan_generator.py
- project_manager/project_manager.py
- project_intelligence/main.py
- coordinator/colleague_coordinator.py

**Update command:**
```bash
cd /Users/MD/AI-Platform-ISO/platform_services/bcm_domain/ai_colleagues
find . -name "*.py" -exec sed -i '' 's/from core import/from intelligent_core.ai_foundation import/g' {} +
find . -name "*.py" -exec sed -i '' 's/from colleagues.base import/from platform_services.bcm_domain.ai_colleagues.base.base_colleague import/g' {} +
```

## Status

- ✅ Package interface works (via __init__.py)
- ⚠️  Direct file imports may fail (acceptable for now)
- 📝 TODO: Update imports in future iteration

**Priority:** Low (current interface works fine)
