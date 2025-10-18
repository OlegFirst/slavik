# Quick Start Guide - Next Session

**📍 You are here**: Phase 1 - Core Infrastructure (40% complete)
**🎯 Next task**: Task 1.1 - Pydantic Models
**⏱️ Estimated time**: 2-3 hours

---

## 🚀 Start Coding in 5 Minutes

### 1. Read Context (2 minutes)
```bash
cd /Users/MD/AI-Platform-ISO/platform-services/simulation/simulation-service

# Read this first (already done if you're reading this!)
cat QUICK_START.md

# Then skim these
head -100 PROJECT_MEMO.md  # Get the big picture
head -50 IMPLEMENTATION_ROADMAP.md  # See the phases
```

### 2. Check Status (1 minute)
```bash
# What files exist?
ls -la

# Git status
git status

# Directory structure
tree -L 2 -I 'venv|__pycache__'
```

### 3. Setup Environment (2 minutes)
```bash
# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import fastapi, sqlalchemy, pydantic; print('✅ Dependencies OK')"
```

### 4. Start Task 1.1 (NOW!)
```bash
# Create models directory
mkdir -p models tests/unit/models

# Create init files
touch models/__init__.py
touch tests/__init__.py
touch tests/unit/__init__.py
touch tests/unit/models/__init__.py

# Create main files
touch models/pydantic_models.py
touch tests/unit/models/test_pydantic_models.py

# Open in editor
code models/pydantic_models.py  # Or vim, nano, etc.
```

---

## 📝 Task 1.1: Pydantic Models - Step by Step

### What You're Building

A file with Pydantic models for:
- ✅ TaskSpecification (NEW)
- ✅ VisualizationConfig (NEW)
- ✅ IntegrationConfig (NEW)
- ✅ Simulation (from simulation2/models.py)
- ✅ Scenario (from simulation2/models.py)
- ✅ SimulationResult (from simulation2/models.py)

### Step 1: Copy Base Models (10 min)

```bash
# Find the source file
SOURCE="/Users/MD/AI-Platform-ISO/platform-services/simulation/simulation/simulation2/models.py"

# Copy as base
cp "$SOURCE" models/pydantic_models.py

# Open it
code models/pydantic_models.py
```

### Step 2: Add TaskSpecification (30 min)

Add this to `models/pydantic_models.py`:

```python
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum
import uuid


class EngineType(str, Enum):
    """Simulation engine types"""
    JAAMSIM = "jaamsim"
    SIMPY = "simpy"
    MONTE_CARLO = "monte_carlo"
    WHAT_IF = "what_if"
    WORKFLOW = "workflow"


class TaskSpecification(BaseModel):
    """
    AI-generated task specification for simulation

    This model represents a complete specification for a simulation,
    including the goal, constraints, context, and execution parameters.
    """

    id: str = Field(
        default_factory=lambda: f"spec_{uuid.uuid4().hex[:12]}",
        description="Unique specification identifier"
    )

    goal: str = Field(
        ...,
        description="Primary objective of the simulation",
        min_length=10,
        max_length=500
    )

    constraints: Dict[str, Any] = Field(
        default_factory=dict,
        description="Constraints for simulation execution"
    )

    context: Dict[str, Any] = Field(
        default_factory=dict,
        description="Context information for simulation"
    )

    engine_preference: Optional[EngineType] = Field(
        default=None,
        description="Preferred simulation engine"
    )

    max_duration: Optional[int] = Field(
        default=3600,
        description="Maximum simulation duration in seconds",
        ge=60,
        le=28800  # 8 hours max
    )

    processes: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Process definitions for simulation"
    )

    resources: Dict[str, int] = Field(
        default_factory=dict,
        description="Resource allocations"
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Creation timestamp"
    )

    created_by: str = Field(
        ...,
        description="User ID who created this specification"
    )

    organization_id: str = Field(
        ...,
        description="Organization ID"
    )

    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata"
    )

    @field_validator('goal')
    @classmethod
    def validate_goal(cls, v: str) -> str:
        """Validate goal is not empty and reasonable"""
        if not v.strip():
            raise ValueError("Goal cannot be empty")
        if len(v.strip()) < 10:
            raise ValueError("Goal too short, provide more detail")
        return v.strip()

    @field_validator('max_duration')
    @classmethod
    def validate_duration(cls, v: Optional[int]) -> Optional[int]:
        """Validate duration is reasonable"""
        if v is not None and v < 60:
            raise ValueError("Duration must be at least 60 seconds")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "goal": "Test BIA process resilience under cyber incident",
                "constraints": {
                    "max_duration": 7200,
                    "participants": 10,
                    "complexity": "high"
                },
                "context": {
                    "organization_type": "hospital",
                    "organization_size": "large",
                    "previous_exercises": []
                },
                "engine_preference": "jaamsim",
                "max_duration": 7200,
                "created_by": "user_123",
                "organization_id": "org_456"
            }
        }
```

### Step 3: Add VisualizationConfig (20 min)

```python
class DashboardType(str, Enum):
    """Dashboard visualization types"""
    REAL_TIME = "real_time"
    SUMMARY = "summary"
    DETAILED = "detailed"
    EXECUTIVE = "executive"


class ChartType(str, Enum):
    """Chart types for visualization"""
    LINE = "line"
    BAR = "bar"
    PIE = "pie"
    SCATTER = "scatter"
    HEATMAP = "heatmap"
    GANTT = "gantt"


class VisualizationConfig(BaseModel):
    """
    Configuration for simulation visualization

    Controls how simulation results are displayed in real-time
    and in final reports.
    """

    dashboard_type: DashboardType = Field(
        default=DashboardType.REAL_TIME,
        description="Type of dashboard to display"
    )

    metrics: List[str] = Field(
        default_factory=lambda: ["progress", "events", "resources"],
        description="Metrics to track and display"
    )

    update_interval: int = Field(
        default=5,
        description="Update interval in seconds",
        ge=1,
        le=60
    )

    chart_types: List[ChartType] = Field(
        default_factory=lambda: [ChartType.LINE, ChartType.BAR],
        description="Chart types to use"
    )

    enable_3d: bool = Field(
        default=False,
        description="Enable 3D visualization"
    )

    enable_real_time_streaming: bool = Field(
        default=True,
        description="Enable WebSocket streaming"
    )

    max_datapoints: int = Field(
        default=1000,
        description="Maximum datapoints to display",
        ge=100,
        le=10000
    )

    class Config:
        json_schema_extra = {
            "example": {
                "dashboard_type": "real_time",
                "metrics": ["progress", "events", "resources", "incidents"],
                "update_interval": 5,
                "chart_types": ["line", "bar", "heatmap"],
                "enable_3d": false,
                "enable_real_time_streaming": true
            }
        }
```

### Step 4: Add IntegrationConfig (15 min)

```python
class IntegrationConfig(BaseModel):
    """
    Configuration for platform integrations

    Controls which platform services are enabled for this simulation
    and what auto-integration features should be active.
    """

    eventbus_enabled: bool = Field(
        default=True,
        description="Enable EventBus integration"
    )

    orchestrator_enabled: bool = Field(
        default=True,
        description="Enable AI Orchestrator integration"
    )

    workflow_enabled: bool = Field(
        default=True,
        description="Enable Workflow Intelligence integration"
    )

    knowledge_enabled: bool = Field(
        default=True,
        description="Enable Knowledge Center integration"
    )

    community_enabled: bool = Field(
        default=True,
        description="Enable Community Intelligence integration"
    )

    predictive_enabled: bool = Field(
        default=False,
        description="Enable Predictive Journey integration"
    )

    digital_twin_enabled: bool = Field(
        default=False,
        description="Enable Digital Twin integration"
    )

    auto_pdca: bool = Field(
        default=True,
        description="Automatically create PDCA cycle after simulation"
    )

    auto_knowledge_storage: bool = Field(
        default=True,
        description="Automatically store knowledge in Knowledge Center"
    )

    auto_community_contribution: bool = Field(
        default=True,
        description="Automatically contribute to Community Intelligence"
    )

    auto_contribution_min_quality_score: float = Field(
        default=8.0,
        description="Minimum quality score for auto-contribution",
        ge=0.0,
        le=10.0
    )

    class Config:
        json_schema_extra = {
            "example": {
                "eventbus_enabled": true,
                "orchestrator_enabled": true,
                "workflow_enabled": true,
                "knowledge_enabled": true,
                "community_enabled": true,
                "auto_pdca": true,
                "auto_knowledge_storage": true,
                "auto_community_contribution": true,
                "auto_contribution_min_quality_score": 8.0
            }
        }
```

### Step 5: Write Tests (45 min)

Create `tests/unit/models/test_pydantic_models.py`:

```python
import pytest
from pydantic import ValidationError
from models.pydantic_models import (
    TaskSpecification,
    VisualizationConfig,
    IntegrationConfig,
    EngineType,
    DashboardType,
    ChartType
)


class TestTaskSpecification:
    """Tests for TaskSpecification model"""

    def test_create_valid_specification(self):
        """Test creating a valid specification"""
        spec = TaskSpecification(
            goal="Test BIA process resilience",
            constraints={"max_duration": 3600},
            context={"type": "hospital"},
            created_by="user_123",
            organization_id="org_456"
        )

        assert spec.goal == "Test BIA process resilience"
        assert spec.constraints["max_duration"] == 3600
        assert spec.created_by == "user_123"
        assert spec.id.startswith("spec_")

    def test_goal_too_short(self):
        """Test validation fails for short goal"""
        with pytest.raises(ValidationError) as exc:
            TaskSpecification(
                goal="Test",  # Too short
                created_by="user_123",
                organization_id="org_456"
            )
        assert "Goal too short" in str(exc.value)

    def test_max_duration_validation(self):
        """Test duration validation"""
        with pytest.raises(ValidationError):
            TaskSpecification(
                goal="Test BIA process resilience",
                max_duration=30,  # Too short
                created_by="user_123",
                organization_id="org_456"
            )

    def test_default_values(self):
        """Test default values are set"""
        spec = TaskSpecification(
            goal="Test BIA process resilience",
            created_by="user_123",
            organization_id="org_456"
        )

        assert spec.constraints == {}
        assert spec.context == {}
        assert spec.processes == []
        assert spec.max_duration == 3600


class TestVisualizationConfig:
    """Tests for VisualizationConfig model"""

    def test_create_with_defaults(self):
        """Test creating with default values"""
        config = VisualizationConfig()

        assert config.dashboard_type == DashboardType.REAL_TIME
        assert "progress" in config.metrics
        assert config.update_interval == 5
        assert config.enable_real_time_streaming is True

    def test_custom_metrics(self):
        """Test custom metrics configuration"""
        config = VisualizationConfig(
            metrics=["custom1", "custom2"],
            chart_types=[ChartType.LINE, ChartType.HEATMAP]
        )

        assert config.metrics == ["custom1", "custom2"]
        assert ChartType.HEATMAP in config.chart_types

    def test_update_interval_validation(self):
        """Test update interval bounds"""
        with pytest.raises(ValidationError):
            VisualizationConfig(update_interval=0)  # Too low

        with pytest.raises(ValidationError):
            VisualizationConfig(update_interval=100)  # Too high


class TestIntegrationConfig:
    """Tests for IntegrationConfig model"""

    def test_all_enabled_by_default(self):
        """Test core integrations enabled by default"""
        config = IntegrationConfig()

        assert config.eventbus_enabled is True
        assert config.orchestrator_enabled is True
        assert config.workflow_enabled is True
        assert config.auto_pdca is True

    def test_optional_integrations_disabled(self):
        """Test optional integrations disabled by default"""
        config = IntegrationConfig()

        assert config.predictive_enabled is False
        assert config.digital_twin_enabled is False

    def test_quality_score_validation(self):
        """Test quality score bounds"""
        with pytest.raises(ValidationError):
            IntegrationConfig(auto_contribution_min_quality_score=15.0)  # Too high

        config = IntegrationConfig(auto_contribution_min_quality_score=7.5)
        assert config.auto_contribution_min_quality_score == 7.5


def test_model_serialization():
    """Test all models can be serialized to JSON"""
    spec = TaskSpecification(
        goal="Test serialization",
        created_by="user_123",
        organization_id="org_456"
    )

    json_data = spec.model_dump_json()
    assert "Test serialization" in json_data

    # Should be able to parse back
    spec2 = TaskSpecification.model_validate_json(json_data)
    assert spec2.goal == spec.goal
```

### Step 6: Run Tests (5 min)

```bash
# Run tests
pytest tests/unit/models/test_pydantic_models.py -v

# Check coverage
pytest tests/unit/models/test_pydantic_models.py --cov=models --cov-report=term-missing

# Should see something like:
# ✅ test_create_valid_specification PASSED
# ✅ test_goal_too_short PASSED
# ✅ test_max_duration_validation PASSED
# ... etc
```

### Step 7: Check Off in Checklist

Open `IMPLEMENTATION_CHECKLIST.md` and mark Task 1.1 items as done:
- [x] Copy simulation2/models.py as base
- [x] Create TaskSpecification model
- [x] Create VisualizationConfig model
- [x] Create IntegrationConfig model
- [x] Write unit tests
- [x] Test coverage > 80%

---

## ✅ Task 1.1 Complete! What's Next?

### You just built:
- ✅ Type-safe Pydantic models
- ✅ Field validation
- ✅ Example data
- ✅ Comprehensive tests
- ✅ 80%+ coverage

### Next Task: 1.2 - SQLAlchemy ORM Models

Create `models/orm_models.py` to persist these models to PostgreSQL.

**Estimated time**: 3-4 hours

**Quick start for Task 1.2**:
```bash
# Create the file
touch models/orm_models.py

# Open it
code models/orm_models.py

# Follow IMPLEMENTATION_CHECKLIST.md Task 1.2
```

---

## 📚 Reference Documents

### Must Read
- **IMPLEMENTATION_CHECKLIST.md** - Your step-by-step guide
- **PROJECT_MEMO.md** - Complete project context

### Reference as Needed
- **IMPLEMENTATION_ROADMAP.md** - Phased plan
- **INTEGRATION_REQUIREMENTS.md** - Integration specs
- **README.md** - Service overview

---

## 💡 Tips for Success

### 1. Work Incrementally
- ✅ Complete one task at a time
- ✅ Test each component before moving on
- ✅ Commit frequently

### 2. Follow the Checklist
- ✅ Open IMPLEMENTATION_CHECKLIST.md
- ✅ Find your current task
- ✅ Check off each sub-item
- ✅ Don't skip steps

### 3. Test Everything
- ✅ Write tests as you code (TDD)
- ✅ Aim for 80%+ coverage
- ✅ Run tests before committing

### 4. Document as You Go
- ✅ Add docstrings to all functions
- ✅ Update README if needed
- ✅ Comment complex logic

### 5. Ask for Help
- ✅ Check PROJECT_MEMO.md for context
- ✅ Check INTEGRATION_REQUIREMENTS.md for integration details
- ✅ Re-read this QUICK_START.md when stuck

---

## 🎯 Success Criteria for Today

### Minimum (2-3 hours)
- [ ] Task 1.1 complete (Pydantic Models)
- [ ] Tests passing
- [ ] Coverage > 80%

### Good Progress (4-5 hours)
- [ ] Task 1.1 complete
- [ ] Task 1.2 started (ORM Models)
- [ ] Database schema designed

### Excellent (6-8 hours)
- [ ] Task 1.1 complete
- [ ] Task 1.2 complete
- [ ] Task 1.3 started (Database Layer)

---

## 🚨 Common Issues & Solutions

### Issue: Import errors
```bash
# Solution: Verify virtual environment is activated
which python  # Should show path in venv/
source venv/bin/activate
```

### Issue: Tests not found
```bash
# Solution: Add __init__.py files
touch tests/__init__.py
touch tests/unit/__init__.py
touch tests/unit/models/__init__.py
```

### Issue: Type checking errors
```bash
# Solution: Install type stubs
pip install types-python-dateutil types-redis
```

---

## 📞 Quick Commands Reference

```bash
# Navigate to project
cd /Users/MD/AI-Platform-ISO/platform-services/simulation/simulation-service

# Activate environment
source venv/bin/activate

# Run tests
pytest tests/unit/ -v

# Check coverage
pytest --cov=models --cov-report=term-missing

# Type check
mypy models/

# Format code
black models/

# Lint
flake8 models/

# Run all quality checks
pytest && mypy . && black --check . && flake8 .
```

---

**Ready to code? Start with Task 1.1 now!** 🚀

Open `models/pydantic_models.py` and begin implementing!
