# Coordinator Implementation Guide

## Quick Start for Subsystem Developers

### 1. Implement Your Subsystem

Create your subsystem by implementing the appropriate protocol interface.

#### Example: Workflow ML Subsystem

```python
# workflow_intelligence/ml/workflow_ml_subsystem.py

from ai_foundation.protocols import IMLSubsystem, MLDataStandard
from typing import Dict, Any
import pandas as pd
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class WorkflowMLSubsystem(IMLSubsystem):
    """ML subsystem for workflow predictions."""
    
    def __init__(self):
        self.name = "workflow_ml"
        self.domain = "workflow"
        self.version = "1.0.0"
        self._models = {}
        self._last_prediction = None
        self._last_training = None
        self._error_count = 0
    
    def get_metadata(self) -> Dict[str, Any]:
        """Return subsystem metadata."""
        return {
            'name': self.name,
            'domain': self.domain,
            'version': self.version,
            'capabilities': [
                'duration_prediction',
                'bottleneck_detection',
                'anomaly_detection'
            ],
            'models': ['workflow_duration', 'workflow_efficiency'],
            'status': 'active'
        }
    
    def predict(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Make workflow prediction."""
        try:
            # Your domain-specific prediction logic here
            prediction_value = self._run_prediction(features)
            confidence = 0.87  # Calculate your confidence
            
            self._last_prediction = datetime.utcnow()
            
            # Use standard format
            return MLDataStandard.format_prediction(
                subsystem_name=self.name,
                domain=self.domain,
                prediction=prediction_value,
                confidence=confidence,
                model_used='workflow_duration_v1',
                explanation={'features_used': list(features.keys())}
            )
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            self._error_count += 1
            raise
    
    def train(self, data: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
        """Train models."""
        # Your training logic here
        self._last_training = datetime.utcnow()
        
        return MLDataStandard.format_training_result(
            success=True,
            model_id='workflow_duration_v2',
            metrics={'accuracy': 0.92, 'f1_score': 0.89},
            duration=45.5
        )
    
    def evaluate(self, test_data: pd.DataFrame) -> Dict[str, Any]:
        """Evaluate model performance."""
        # Your evaluation logic here
        return {
            'accuracy': 0.91,
            'precision': 0.92,
            'recall': 0.89,
            'f1_score': 0.90,
            'domain_metrics': {'bottleneck_detection_accuracy': 0.85},
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }
    
    def register_with_coordinator(self, coordinator: Any) -> bool:
        """Register with coordinator."""
        try:
            return coordinator.register_ml(self.name, self)
        except Exception as e:
            logger.error(f"Registration failed: {e}")
            return False
    
    def get_health_status(self) -> Dict[str, Any]:
        """Report health status."""
        return {
            'healthy': self._error_count < 10,
            'status': 'healthy' if self._error_count < 10 else 'degraded',
            'last_prediction': self._last_prediction.isoformat() + 'Z' if self._last_prediction else None,
            'last_training': self._last_training.isoformat() + 'Z' if self._last_training else None,
            'model_count': len(self._models),
            'error_rate': self._error_count / max(1, self._prediction_count),
            'issues': [] if self._error_count < 10 else ['High error rate']
        }
    
    def get_capabilities(self) -> list:
        """Return capabilities."""
        return self.get_metadata()['capabilities']
    
    # Internal method
    def _run_prediction(self, features: Dict[str, Any]):
        """Your actual prediction logic."""
        # Implement your ML model prediction here
        return {'duration_hours': 4.5, 'confidence': 0.87}
```

### 2. Register Your Subsystem

In your service startup code:

```python
# workflow_intelligence/main.py

from ai_foundation import get_global_coordinator
from .ml.workflow_ml_subsystem import WorkflowMLSubsystem
from .rag.workflow_rag_subsystem import WorkflowRAGSubsystem
from .learning.workflow_learning_subsystem import WorkflowLearningSubsystem

def setup_subsystems():
    """Register subsystems with coordinator."""
    coordinator = get_global_coordinator()
    
    # Register ML subsystem
    workflow_ml = WorkflowMLSubsystem()
    coordinator.register_ml('workflow_ml', workflow_ml)
    logger.info("Workflow ML subsystem registered")
    
    # Register RAG subsystem
    workflow_rag = WorkflowRAGSubsystem()
    coordinator.register_rag('workflow_rag', workflow_rag)
    logger.info("Workflow RAG subsystem registered")
    
    # Register Learning subsystem
    workflow_learning = WorkflowLearningSubsystem()
    coordinator.register_learning('workflow_learning', workflow_learning)
    logger.info("Workflow Learning subsystem registered")

@app.on_event("startup")
async def startup():
    setup_subsystems()
```

### 3. Use the Coordinator

In any service that needs coordinated AI capabilities:

```python
# Some platform service

from ai_foundation import get_global_coordinator

def analyze_workflow(workflow_data):
    """Analyze workflow using all available ML subsystems."""
    coordinator = get_global_coordinator()
    
    # Get predictions from all ML subsystems
    result = coordinator.coordinate_ml_prediction(
        features=workflow_data,
        aggregation='weighted_average'
    )
    
    predictions = result['aggregated']['prediction']
    confidence = result['confidence']
    subsystems_used = result['subsystems_used']
    
    logger.info(f"Prediction: {predictions}, Confidence: {confidence}")
    logger.info(f"Subsystems used: {subsystems_used}")
    
    return {
        'prediction': predictions,
        'confidence': confidence,
        'details': result['predictions']
    }

def search_knowledge(query):
    """Search across all knowledge bases."""
    coordinator = get_global_coordinator()
    
    # Get documents from all RAG subsystems
    result = coordinator.coordinate_rag_retrieval(
        query=query,
        config={'top_k': 5}
    )
    
    documents = result['results']
    logger.info(f"Found {result['total_results']} documents from {len(result['subsystems_used'])} subsystems")
    
    return documents

def learn_from_events(events):
    """Teach all learning subsystems."""
    coordinator = get_global_coordinator()
    
    # All subsystems learn independently
    result = coordinator.coordinate_learning(
        data=events,
        config={'mode': 'unsupervised', 'min_pattern_confidence': 0.75}
    )
    
    logger.info(f"Total patterns discovered: {result['total_patterns']}")
    logger.info(f"Total rules generated: {result['total_rules']}")
    
    return result
```

---

## Common Patterns

### Pattern 1: Conditional Subsystem Querying

```python
# Use only subsystems from specific domain
coordinator = get_global_coordinator()

# Find subsystems in specific domain
compliance_ml = coordinator.get_subsystem_by_domain('ml', 'compliance')

# Query only those subsystems
result = coordinator.coordinate_ml_prediction(
    features=data,
    subsystems=compliance_ml,  # Only compliance ML subsystems
    aggregation='voting'
)
```

### Pattern 2: Discovery Before Use

```python
# Discover what's available
coordinator = get_global_coordinator()

ml_subsystems = coordinator.list_ml_subsystems()
rag_subsystems = coordinator.list_rag_subsystems()

# Check capabilities
for subsystem in ml_subsystems:
    print(f"Subsystem: {subsystem['name']}")
    print(f"Domain: {subsystem['domain']}")
    print(f"Capabilities: {subsystem['capabilities']}")

# Use only subsystems with required capability
capable_subsystems = [
    s['name'] for s in ml_subsystems 
    if 'duration_prediction' in s['capabilities']
]

result = coordinator.coordinate_ml_prediction(
    features=data,
    subsystems=capable_subsystems
)
```

### Pattern 3: Health Monitoring Integration

```python
# Monitor subsystem health
coordinator = get_global_coordinator()

def health_check_route():
    """Provide health status of all AI subsystems."""
    health = coordinator.check_all_health()
    
    return {
        'overall_healthy': health['overall_healthy'],
        'subsystems': {
            'ml': health['ml'],
            'rag': health['rag'],
            'learning': health['learning']
        },
        'unhealthy': health['unhealthy_subsystems'],
        'checked_at': health['timestamp']
    }
```

### Pattern 4: Graceful Degradation

```python
# Coordinator handles failures gracefully
coordinator = get_global_coordinator()

# Even if some subsystems fail, others contribute
result = coordinator.coordinate_ml_prediction(
    features=data
)

if result['subsystems_used']:
    # Some subsystems succeeded
    logger.info(f"Got predictions from {len(result['subsystems_used'])} subsystems")
    use_prediction(result['aggregated']['prediction'])
else:
    # All subsystems failed
    logger.warning("All ML subsystems failed")
    use_fallback_prediction()
```

### Pattern 5: Result Aggregation Strategies

```python
# Choose aggregation strategy based on use case
coordinator = get_global_coordinator()

# For critical decisions: use voting (more conservative)
critical_result = coordinator.coordinate_ml_prediction(
    features=data,
    aggregation='voting'  # Requires agreement
)

# For exploratory analysis: use ensemble (see all options)
exploratory_result = coordinator.coordinate_ml_prediction(
    features=data,
    aggregation='ensemble'  # See all predictions
)

# For general use: weighted average (balanced)
general_result = coordinator.coordinate_ml_prediction(
    features=data,
    aggregation='weighted_average'  # Default, balanced
)
```

---

## Best Practices

### 1. Always Implement Health Reporting

```python
def get_health_status(self) -> Dict[str, Any]:
    """Return health status so coordinator can monitor."""
    return {
        'healthy': self.is_operational(),
        'status': self._determine_status(),
        'last_prediction': self._last_prediction_time,
        'error_rate': self._calculate_error_rate(),
        'issues': self._identify_issues(),
        'model_count': len(self._models)
    }
```

### 2. Use Standard Data Formats

```python
from ai_foundation import MLDataStandard, RAGDataStandard, LearningDataStandard

# For ML predictions
result = MLDataStandard.format_prediction(
    subsystem_name='my_ml',
    domain='my_domain',
    prediction=value,
    confidence=0.85,
    model_used='model_v1'
)

# For RAG retrieval
results = [
    RAGDataStandard.format_document(
        content=doc_content,
        doc_id='doc_123',
        score=0.92,
        metadata={'type': 'best_practice'},
        source='my_kb'
    )
]

# For Learning results
patterns = [
    LearningDataStandard.format_pattern(
        pattern_id='pat_123',
        description='When X happens, Y follows',
        confidence=0.88,
        frequency=42,
        conditions={'X': 'value'},
        actions={'Y': 'action'}
    )
]
```

### 3. Log Subsystem Status

```python
import logging

logger = logging.getLogger(__name__)

class MySubsystem(IMLSubsystem):
    def predict(self, features):
        try:
            logger.debug(f"Making prediction with {len(features)} features")
            result = self._predict(features)
            logger.info(f"Prediction successful: {result['prediction']}")
            return result
        except Exception as e:
            logger.error(f"Prediction failed: {e}", exc_info=True)
            raise
```

### 4. Handle Timeouts Gracefully

```python
import time

def predict(self, features, timeout=5):
    """Make prediction with timeout."""
    start = time.time()
    try:
        result = self._run_prediction(features)
        elapsed = time.time() - start
        if elapsed > timeout * 0.8:  # Warn if approaching timeout
            logger.warning(f"Prediction took {elapsed}s (timeout: {timeout}s)")
        return result
    except TimeoutError:
        logger.error("Prediction timed out")
        self._error_count += 1
        raise
```

### 5. Cache Frequently Used Queries

```python
from functools import lru_cache
import hashlib

class MyRAGSubsystem(IRAGSubsystem):
    @lru_cache(maxsize=100)
    def retrieve(self, query_hash: str, top_k: int = 5):
        """Retrieve with caching."""
        # Cache works because query is hashed
        # In real implementation, hash the query before passing
        return self._actual_retrieve(query_hash, top_k)
    
    def retrieve(self, query: str, config: Dict = None):
        """Public method with caching."""
        query_hash = hashlib.md5(query.encode()).hexdigest()
        top_k = config.get('top_k', 5) if config else 5
        return self._cached_retrieve(query_hash, top_k)
```

---

## Troubleshooting

### Issue: Subsystem Not Found

```python
# Problem
result = coordinator.coordinate_ml_prediction(
    subsystems=['my_subsystem']  # Not registered
)
# Returns: empty predictions list

# Solution: Check if registered
registered = coordinator.list_ml_subsystems()
names = [s['name'] for s in registered]
print(f"Available: {names}")

# Register if missing
if 'my_subsystem' not in names:
    coordinator.register_ml('my_subsystem', my_instance)
```

### Issue: Low Confidence Scores

```python
# Check individual subsystem predictions
result = coordinator.coordinate_ml_prediction(subsystems=['my_subsystem'])

for pred in result['predictions']:
    print(f"{pred['subsystem']}: {pred['confidence']}")

# If consistently low, check subsystem training
# Retrain if needed
```

### Issue: No Results from RAG

```python
# Check if documents are indexed
rag = coordinator.rag_subsystems['my_rag']
health = rag.get_health_status()
print(f"Documents indexed: {health['document_count']}")

# If 0, need to index documents
# Check RAG implementation for indexing
```

### Issue: Subsystem Health Degraded

```python
# Get detailed health status
health = coordinator.check_all_health()

for subsystem_type in ['ml', 'rag', 'learning']:
    for name, status in health[subsystem_type].items():
        if not status['healthy']:
            print(f"{subsystem_type}:{name}")
            print(f"  Status: {status['status']}")
            print(f"  Issues: {status.get('issues', [])}")
```

---

## Testing Your Subsystem

```python
# test_my_subsystem.py

import pytest
from my_module import MyMLSubsystem
from ai_foundation import get_global_coordinator

@pytest.fixture
def subsystem():
    return MyMLSubsystem()

@pytest.fixture
def coordinator():
    return get_global_coordinator()

def test_metadata(subsystem):
    """Test metadata format."""
    metadata = subsystem.get_metadata()
    assert 'name' in metadata
    assert 'domain' in metadata
    assert 'capabilities' in metadata
    assert isinstance(metadata['capabilities'], list)

def test_prediction_format(subsystem):
    """Test prediction returns correct format."""
    features = {'test': 'data'}
    result = subsystem.predict(features)
    
    assert 'subsystem' in result
    assert 'domain' in result
    assert 'prediction' in result
    assert 'confidence' in result
    assert 0.0 <= result['confidence'] <= 1.0
    assert 'timestamp' in result

def test_health_status(subsystem):
    """Test health reporting."""
    health = subsystem.get_health_status()
    
    assert 'healthy' in health
    assert isinstance(health['healthy'], bool)
    assert 'status' in health
    assert 'error_rate' in health
    assert 0.0 <= health['error_rate'] <= 1.0

def test_register_with_coordinator(subsystem, coordinator):
    """Test registration."""
    success = subsystem.register_with_coordinator(coordinator)
    assert success
    
    # Verify registration
    subsystems = coordinator.list_ml_subsystems()
    names = [s['name'] for s in subsystems]
    assert subsystem.get_metadata()['name'] in names

def test_coordinator_coordination(subsystem, coordinator):
    """Test coordinator can use subsystem."""
    subsystem.register_with_coordinator(coordinator)
    
    result = coordinator.coordinate_ml_prediction(
        features={'test': 'data'}
    )
    
    assert len(result['predictions']) > 0
    assert 'aggregated' in result
    assert subsystem.get_metadata()['name'] in result['subsystems_used']
```

---

## Migration Guide: From Monolithic to Federated

If migrating from old centralized architecture:

### Old Way (Don't Do This)
```python
# Everything in one place
from ai_foundation import WorkflowPredictor, RAGPipeline, SelfLearningEngine

predictor = WorkflowPredictor()
rag = RAGPipeline()
learner = SelfLearningEngine()

result = predictor.predict(data)  # Only one predictor
```

### New Way (Federated)
```python
# Each module provides its own subsystems
from ai_foundation import get_global_coordinator

coordinator = get_global_coordinator()

# All registered subsystems contribute
result = coordinator.coordinate_ml_prediction(data)

# Benefits:
# - Multiple ML models contribute predictions
# - Easy to add new subsystems
# - Graceful failure handling
# - Extensible aggregation strategies
```

**Status**: Ready for production implementation
