# AI Foundation - Quick Start Guide

**Quick reference for using the federated AI architecture**

---

## 🚀 Quick Start (5 minutes)

### Step 1: Extend Base Classes

```python
# your_module/ml/your_ml_subsystem.py
from intelligent_core.ai_foundation.ml import BaseMLSubsystem
from intelligent_core.ai_foundation.protocols import MLDataStandard

class YourMLSubsystem(BaseMLSubsystem):
    def __init__(self):
        super().__init__()
        self.name = "your_ml"
        self.domain = "your_domain"

    def predict(self, features: Dict[str, Any]) -> Dict[str, Any]:
        # Add your domain-specific prediction logic
        prediction = self._your_prediction_logic(features)

        return MLDataStandard.format_prediction(
            subsystem_name=self.name,
            domain=self.domain,
            prediction=prediction,
            confidence=0.85,
            model_used='your_model_v1',
            explanation={'your': 'metadata'}
        )
```

### Step 2: Register with Coordinator

```python
# your_module/initialization.py
from intelligent_core.ai_foundation.coordinator import get_global_coordinator
from .ml.your_ml_subsystem import YourMLSubsystem

def initialize_your_module_ai():
    coordinator = get_global_coordinator()

    your_ml = YourMLSubsystem()
    your_ml.register_with_coordinator(coordinator)

    print(f"✅ {your_ml.name} registered")
```

### Step 3: Use Federated Predictions

```python
# Anywhere in your code
from intelligent_core.ai_foundation.coordinator import get_global_coordinator

coordinator = get_global_coordinator()

# This queries ALL registered ML subsystems and aggregates results
result = coordinator.coordinate_ml_prediction(
    features={'your': 'features'},
    aggregation='weighted_average'
)

print(f"Prediction: {result['prediction']}")
print(f"Confidence: {result['confidence']}")
print(f"Subsystems used: {len(result['subsystems'])}")
```

---

## 📚 Three Subsystem Types

### 1. ML Subsystem (Machine Learning)

**Extend:** `BaseMLSubsystem`
**Protocol:** `IMLSubsystem`

**Key methods to implement:**
```python
def predict(features) -> prediction
def train(data, config) -> training_result
def evaluate(test_data) -> metrics
```

**Use for:**
- Predictions
- Classifications
- Forecasting
- Anomaly detection

---

### 2. RAG Subsystem (Retrieval-Augmented Generation)

**Extend:** `BaseRAGSubsystem`
**Protocol:** `IRAGSubsystem`

**Key methods to implement:**
```python
def retrieve(query, config) -> retrieval_result
def index_document(document) -> indexing_result
def build_context(query, max_tokens) -> context
```

**Use for:**
- Knowledge retrieval
- Semantic search
- Context building for LLMs
- Document management

---

### 3. Learning Subsystem (Self-Learning)

**Extend:** `BaseLearningSubsystem`
**Protocol:** `ILearningSubsystem`

**Key methods to implement:**
```python
def learn_from_data(data, config) -> learning_result
def detect_patterns(data) -> patterns
def generate_rules(patterns) -> rules
def predict_from_patterns(context) -> prediction
```

**Use for:**
- Pattern detection
- Rule generation
- Continuous learning
- Feedback loops

---

## 🎯 Common Patterns

### Pattern 1: Domain-Specific ML

```python
class WorkflowMLSubsystem(BaseMLSubsystem):
    def predict(self, features):
        prediction_type = features.get('type')

        if prediction_type == 'duration':
            return self._predict_duration(features)
        elif prediction_type == 'bottleneck':
            return self._predict_bottleneck(features)
        else:
            return super().predict(features)  # Fallback to base
```

### Pattern 2: Enhanced RAG Retrieval

```python
class WorkflowRAGSubsystem(BaseRAGSubsystem):
    def retrieve(self, query, config=None):
        # Add domain-specific filters
        config = config or {}
        config['filters'] = {
            'domain': 'workflow',
            'status': 'approved'
        }

        # Call base retrieval
        result = super().retrieve(query, config)

        # Enhance results with domain metadata
        for doc in result['results']:
            doc['workflow_metadata'] = self._get_workflow_metadata(doc['id'])

        return result
```

### Pattern 3: Pattern-Based Learning

```python
class WorkflowLearningSubsystem(BaseLearningSubsystem):
    def learn_from_data(self, data, config=None):
        # Pre-process domain-specific data
        workflow_data = self._extract_workflow_features(data)

        # Call base learning
        result = super().learn_from_data(workflow_data, config)

        # Add domain-specific patterns
        workflow_patterns = self._detect_workflow_patterns(workflow_data)
        result['patterns'].extend(workflow_patterns)

        return result
```

---

## 🔄 Coordinator Methods

### ML Coordination

```python
coordinator.coordinate_ml_prediction(
    features: Dict,
    aggregation: str = 'weighted_average'  # or 'voting', 'stacking'
) -> aggregated_prediction
```

### RAG Coordination

```python
coordinator.coordinate_rag_retrieval(
    query: str,
    config: Dict = None
) -> merged_results
```

### Learning Coordination

```python
coordinator.coordinate_learning(
    data: List[Dict],
    config: Dict = None
) -> aggregated_patterns
```

---

## 📊 Data Formats

### ML Prediction Format

```python
{
    'subsystem': 'your_ml',
    'domain': 'your_domain',
    'prediction': {...},  # Your prediction data
    'confidence': 0.85,
    'model_used': 'your_model',
    'explanation': {...},
    'timestamp': '2025-10-24T10:30:00Z'
}
```

### RAG Retrieval Format

```python
{
    'subsystem': 'your_rag',
    'domain': 'your_domain',
    'query': 'search query',
    'results': [
        {
            'id': 'doc_123',
            'content': 'document content',
            'score': 0.92,
            'metadata': {...},
            'source': 'knowledge_base'
        }
    ],
    'result_count': 5,
    'timestamp': '2025-10-24T10:30:00Z'
}
```

### Learning Pattern Format

```python
{
    'id': 'pattern_123',
    'description': 'Human-readable description',
    'confidence': 0.87,
    'frequency': 127,
    'conditions': {'when': 'this'},
    'actions': {'do': 'that'}
}
```

---

## 🛠️ Utilities

### Health Checking

```python
# Check subsystem health
subsystem = YourMLSubsystem()
health = subsystem.get_health_status()

print(f"Healthy: {health['healthy']}")
print(f"Status: {health['status']}")
print(f"Error rate: {health['error_rate']:.2%}")
```

### Metadata Access

```python
# Get subsystem metadata
metadata = subsystem.get_metadata()

print(f"Name: {metadata['name']}")
print(f"Domain: {metadata['domain']}")
print(f"Capabilities: {metadata['capabilities']}")
```

### Capability Discovery

```python
# Get all registered subsystems
coordinator = get_global_coordinator()
subsystems = coordinator.get_all_subsystems()

print("ML Subsystems:")
for name, subsystem in subsystems['ml'].items():
    print(f"  - {name}: {subsystem.domain}")

print("RAG Subsystems:")
for name, subsystem in subsystems['rag'].items():
    print(f"  - {name}: {subsystem.domain}")
```

---

## 🐛 Debugging

### Enable Logging

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('intelligent_core.ai_foundation')
```

### Check Registration

```python
coordinator = get_global_coordinator()

# List all registered subsystems
print(f"ML subsystems: {list(coordinator.ml_subsystems.keys())}")
print(f"RAG subsystems: {list(coordinator.rag_subsystems.keys())}")
print(f"Learning subsystems: {list(coordinator.learning_subsystems.keys())}")
```

### Test Subsystem

```python
# Test ML subsystem
subsystem = YourMLSubsystem()

# Test prediction
result = subsystem.predict({'test': 'data'})
print(f"Prediction successful: {result.get('prediction') is not None}")

# Test health
health = subsystem.get_health_status()
print(f"Subsystem healthy: {health['healthy']}")
```

---

## 📝 Checklist: Adding New Module

- [ ] Create `your_module/ml/your_ml_subsystem.py`
- [ ] Create `your_module/rag/your_rag_subsystem.py`
- [ ] Create `your_module/learning/your_learning_subsystem.py`
- [ ] Extend base classes
- [ ] Implement required protocols
- [ ] Add domain-specific logic
- [ ] Create initialization function
- [ ] Register with coordinator
- [ ] Test predictions
- [ ] Test retrieval
- [ ] Test learning
- [ ] Check health status
- [ ] Document capabilities

---

## 🎓 Learning Path

1. **Read:** `AI_FOUNDATION_PHILOSOPHY.md` - Understand the vision
2. **Read:** `FEDERATION_IMPLEMENTATION_GUIDE.md` - Architecture details
3. **Study:** `examples/module_integration_example.py` - Working example
4. **Implement:** Your module's subsystems
5. **Test:** End-to-end with coordinator
6. **Deploy:** Register on module initialization

---

## 💡 Best Practices

### 1. Always Use Standard Formats
```python
# Good
return MLDataStandard.format_prediction(...)

# Bad
return {'my': 'custom', 'format': True}
```

### 2. Implement Fallbacks
```python
def predict(self, features):
    try:
        return self._advanced_prediction(features)
    except Exception as e:
        logger.warning(f"Advanced prediction failed: {e}")
        return super().predict(features)  # Fallback to base
```

### 3. Add Domain Metadata
```python
def get_metadata(self):
    metadata = super().get_metadata()
    metadata['domain_specific'] = {
        'workflow_types': ['bia', 'risk', 'incident'],
        'supported_predictions': ['duration', 'bottleneck']
    }
    return metadata
```

### 4. Monitor Health
```python
def predict(self, features):
    try:
        result = self._predict(features)
        self._prediction_count += 1
        self._last_prediction = datetime.utcnow()
        return result
    except Exception as e:
        self._error_count += 1
        raise
```

---

## 🔗 Links

- **Complete Example:** `examples/module_integration_example.py`
- **Protocols:** `protocols/iml_subsystem.py`, `irag_subsystem.py`, `ilearning_subsystem.py`
- **Base Classes:** `ml/base_ml_subsystem.py`, `rag/base_rag_subsystem.py`, `learning/base_learning_subsystem.py`
- **Coordinator:** `coordinator/subsystem_coordinator.py`

---

## ❓ FAQ

**Q: Do I need to implement all three subsystem types?**
A: No, implement only what your module needs. If you only need ML, just implement ML.

**Q: Can I use base subsystems directly?**
A: Yes, but they're generic. Better to extend with domain-specific logic.

**Q: How does aggregation work?**
A: Coordinator queries all subsystems, then combines results using weighted average, voting, or stacking.

**Q: What if my subsystem fails?**
A: Coordinator has fallback mechanisms. Other subsystems continue working.

**Q: Can I register multiple subsystems from one module?**
A: Yes! Register as many as you need with unique names.

---

**Quick Start Complete! Ready to build? See `examples/module_integration_example.py` for full working code.** 🚀
