# Coordinator Subsystem Architecture Diagram

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          AI Platform Services                               │
│  (AI Services Management, Compliance, Workflow Intelligence, etc.)          │
└────────────────────────────────────┬────────────────────────────────────────┘
                                      │
                                      ▼
        ┌─────────────────────────────────────────────────────────┐
        │                                                         │
        │        SubsystemCoordinator (Brain/Hub)               │
        │                                                         │
        │  ┌────────────────────────────────────────────────┐   │
        │  │  Registration & Discovery                      │   │
        │  ├────────────────────────────────────────────────┤   │
        │  │  • register_ml()                               │   │
        │  │  • register_rag()                              │   │
        │  │  • register_learning()                         │   │
        │  │  • list_ml_subsystems()                        │   │
        │  │  • get_subsystem_by_domain()                   │   │
        │  └────────────────────────────────────────────────┘   │
        │                                                         │
        │  ┌────────────────────────────────────────────────┐   │
        │  │  Coordination Methods                          │   │
        │  ├────────────────────────────────────────────────┤   │
        │  │  • coordinate_ml_prediction()                  │   │
        │  │  • coordinate_rag_retrieval()                  │   │
        │  │  • coordinate_learning()                       │   │
        │  └────────────────────────────────────────────────┘   │
        │                                                         │
        │  ┌────────────────────────────────────────────────┐   │
        │  │  Health Monitoring                             │   │
        │  ├────────────────────────────────────────────────┤   │
        │  │  • check_all_health()                          │   │
        │  │  • get_coordinator_status()                    │   │
        │  └────────────────────────────────────────────────┘   │
        │                                                         │
        └─┬───────────────────────────┬───────────────────────┬──┘
          │                           │                       │
          ▼                           ▼                       ▼
    ┌──────────────┐          ┌──────────────┐        ┌──────────────┐
    │ ML Subsystems│          │ RAG Subsystems│        │Learning      │
    │              │          │               │        │Subsystems    │
    ├──────────────┤          ├──────────────┤        ├──────────────┤
    │• workflow_ml │          │• workflow_rag │        │• workflow_   │
    │• expertise_ml│          │• expertise_rag│        │  learning    │
    │• orchestr_ml │          │• compliance_rag        │• expertise_  │
    │• compliance_ │          │• orchestr_rag │        │  learning    │
    │  ml          │          │               │        │• compliance_ │
    └──────────────┘          └──────────────┘        │  learning    │
                                                      └──────────────┘

         (Nerves - Everywhere, Domain-Specific)
```

## Data Flow: ML Prediction Coordination

```
Service Request
      │
      ▼
┌──────────────────────────────┐
│ coordinator.coordinate_ml_   │
│ prediction(features, ...)    │
└──────────────────────────────┘
      │
      ├──► [Query ML Subsystem 1] ──► Prediction 1 (confidence 0.89)
      │
      ├──► [Query ML Subsystem 2] ──► Prediction 2 (confidence 0.85)
      │
      ├──► [Query ML Subsystem 3] ──► Prediction 3 (confidence 0.91)
      │
      ▼
┌──────────────────────────────┐
│ Aggregate Results:           │
│ • weighted_average           │
│ • voting                      │
│ • ensemble                    │
└──────────────────────────────┘
      │
      ▼
┌──────────────────────────────────────┐
│ Return Aggregated Result:            │
│ {                                    │
│   'predictions': [1, 2, 3],          │
│   'aggregated': {...},               │
│   'confidence': 0.88,                │
│   'subsystems_used': [1, 2, 3],      │
│   'timestamp': '...'                 │
│ }                                    │
└──────────────────────────────────────┘
```

## Data Flow: RAG Retrieval Coordination

```
Service Request
      │
      ▼
┌──────────────────────────────┐
│ coordinator.coordinate_rag_  │
│ retrieval(query, ...)        │
└──────────────────────────────┘
      │
      ├──► [Query RAG Subsystem 1] ──► Documents A, B, C
      │
      ├──► [Query RAG Subsystem 2] ──► Documents B, D, E
      │
      ├──► [Query RAG Subsystem 3] ──► Documents E, F
      │
      ▼
┌──────────────────────────────┐
│ Deduplicate:                 │
│ A, B, C, D, E, F (6 unique)  │
└──────────────────────────────┘
      │
      ▼
┌──────────────────────────────┐
│ Rerank by Score:             │
│ A (0.95), D (0.92), F (0.88) │
└──────────────────────────────┘
      │
      ▼
┌──────────────────────────────────────┐
│ Return Results:                      │
│ {                                    │
│   'results': [A, D, F, ...],         │
│   'results_by_subsystem': {...},     │
│   'total_results': 6,                │
│   'subsystems_used': [1, 2, 3],      │
│   'timestamp': '...'                 │
│ }                                    │
└──────────────────────────────────────┘
```

## Data Flow: Learning Coordination

```
Platform Experiences Event
      │
      ▼
┌──────────────────────────────┐
│ coordinator.coordinate_      │
│ learning(data, ...)          │
└──────────────────────────────┘
      │
      ├──► [Teach Learning Subsystem 1]
      │    └──► Discovers Pattern A (3 patterns, 1 rule)
      │
      ├──► [Teach Learning Subsystem 2]
      │    └──► Discovers Pattern B (2 patterns, 1 rule)
      │
      ├──► [Teach Learning Subsystem 3]
      │    └──► Discovers Pattern C (4 patterns, 2 rules)
      │
      ▼
┌──────────────────────────────┐
│ Aggregate Learning:          │
│ • Total patterns: 9          │
│ • Total rules: 4             │
└──────────────────────────────┘
      │
      ▼
┌──────────────────────────────────────┐
│ Return Learning Results:             │
│ {                                    │
│   'results_by_subsystem': {...},     │
│   'total_patterns': 9,               │
│   'total_rules': 4,                  │
│   'subsystems_used': [1, 2, 3],      │
│   'timestamp': '...'                 │
│ }                                    │
└──────────────────────────────────────┘
```

## Health Monitoring Flow

```
Periodic or On-Demand Health Check
      │
      ▼
┌──────────────────────────────┐
│ coordinator.check_all_health()
└──────────────────────────────┘
      │
      ├──► [Check ML Subsystems]
      │    ├──► workflow_ml: healthy ✅
      │    ├──► expertise_ml: degraded ⚠
      │    └──► orchestration_ml: healthy ✅
      │
      ├──► [Check RAG Subsystems]
      │    ├──► workflow_rag: healthy ✅
      │    ├──► compliance_rag: healthy ✅
      │    └──► learning_rag: healthy ✅
      │
      ├──► [Check Learning Subsystems]
      │    ├──► workflow_learning: healthy ✅
      │    └──► compliance_learning: healthy ✅
      │
      ▼
┌──────────────────────────────────────┐
│ Return Health Status:                │
│ {                                    │
│   'overall_healthy': false,          │
│   'ml': {...},                       │
│   'rag': {...},                      │
│   'learning': {...},                 │
│   'unhealthy_subsystems': [          │
│     'ml:expertise_ml'                │
│   ],                                 │
│   'timestamp': '...'                 │
│ }                                    │
└──────────────────────────────────────┘
```

## Subsystem Registration and Discovery

```
┌────────────────────────────────────────────────────────────┐
│ Step 1: Subsystem Implementation                           │
├────────────────────────────────────────────────────────────┤
│                                                             │
│  class WorkflowMLSubsystem(IMLSubsystem):                  │
│      def get_metadata(self):                              │
│          return {'name': 'workflow_ml', ...}              │
│      def predict(self, features):                         │
│          return {'subsystem': 'workflow_ml', ...}         │
│      # ... other methods ...                              │
│                                                             │
└────────────────────────────────────────────────────────────┘
            │
            ▼
┌────────────────────────────────────────────────────────────┐
│ Step 2: Register with Coordinator                         │
├────────────────────────────────────────────────────────────┤
│                                                             │
│  coordinator = get_global_coordinator()                   │
│  workflow_ml = WorkflowMLSubsystem()                      │
│  coordinator.register_ml('workflow_ml', workflow_ml)      │
│                                                             │
└────────────────────────────────────────────────────────────┘
            │
            ▼
┌────────────────────────────────────────────────────────────┐
│ Step 3: Discovery and Usage                               │
├────────────────────────────────────────────────────────────┤
│                                                             │
│  # Find what's available                                  │
│  ml_subsystems = coordinator.list_ml_subsystems()         │
│                                                             │
│  # Find by domain                                         │
│  workflow_ml = coordinator.get_subsystem_by_domain(       │
│      'ml', 'workflow'                                     │
│  )                                                         │
│                                                             │
│  # Use coordinator                                        │
│  result = coordinator.coordinate_ml_prediction(           │
│      features={...}                                       │
│  )                                                         │
│                                                             │
└────────────────────────────────────────────────────────────┘
```

## Error Handling and Resilience

```
┌─────────────────────────────────────────────────────────┐
│ Coordinator Resilience Pattern                          │
└─────────────────────────────────────────────────────────┘

For Each Subsystem Query:
    │
    ├──► try:
    │    │
    │    ├──► Call subsystem.method()
    │    │
    │    └──► Add result to list
    │
    ├──► except Exception as e:
    │    │
    │    ├──► Log error with subsystem name
    │    │
    │    ├──► Continue to next subsystem
    │    │
    │    └──► DON'T crash entire coordinator
    │
    ▼

Result: Partial results from healthy subsystems
        Unhealthy subsystems gracefully skipped
        No single failure crashes entire system
```

## Component Relationships

```
┌─────────────────────────────────────────────────────────┐
│                SubsystemCoordinator                     │
│                                                         │
│  Registries:                                           │
│  ├── ml_subsystems: Dict[str, IMLSubsystem]           │
│  ├── rag_subsystems: Dict[str, IRAGSubsystem]         │
│  └── learning_subsystems: Dict[str, ILearningSubsystem]
│                                                         │
│  Metadata Caches:                                      │
│  ├── _ml_metadata: Dict[str, Dict[str, Any]]          │
│  ├── _rag_metadata: Dict[str, Dict[str, Any]]         │
│  └── _learning_metadata: Dict[str, Dict[str, Any]]    │
│                                                         │
│  Health Tracking:                                      │
│  ├── _health_cache: Dict[str, Dict[str, Any]]         │
│  └── _last_health_check: Optional[datetime]           │
│                                                         │
└─────────────────────────────────────────────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
    ┌────────────┐      ┌────────────┐      ┌────────────┐
    │ IMLSubsystem      │IRAGSubsystem     │ILearning   │
    ├────────────┤      ├────────────┤      │Subsystem   │
    │protocol    │      │protocol    │      ├────────────┤
    │interface   │      │interface   │      │protocol    │
    └────────────┘      └────────────┘      │interface   │
         ▲                    ▲              └────────────┘
         │                    │                    ▲
    ┌────────────┐      ┌────────────┐      ┌────────────┐
    │Implementation     │Implementation    │Implementation
    │Example:           │Example:          │Example:
    │BaseMLSubsystem    │(custom)          │(custom)
    └────────────┘      └────────────┘      └────────────┘
```

## Singleton Pattern Flow

```
Application Start
      │
      ▼
┌──────────────────────────────────┐
│ import get_global_coordinator()  │
└──────────────────────────────────┘
      │
      ▼
┌──────────────────────────────────┐
│ Call get_global_coordinator()    │
└──────────────────────────────────┘
      │
      ├──► _global_coordinator is None?
      │    │
      │    ├─── YES ──► Create new instance
      │    │           Set _global_coordinator
      │    │           Return instance
      │    │
      │    └─── NO ──► Return existing instance
      │
      ▼
Used throughout application lifetime
(Single instance, thread-safe lazy init)
```

## Aggregation Strategies Comparison

```
┌────────────────────────────────────────────────────────────┐
│ ML Prediction Aggregation Strategies                      │
└────────────────────────────────────────────────────────────┘

Input: 3 predictions
├── Prediction 1: 4.2 (confidence 0.89)
├── Prediction 2: 4.5 (confidence 0.85)
└── Prediction 3: 4.3 (confidence 0.91)

Aggregation Methods:
│
├─► weighted_average:
│   └─► Result: 4.3 (average weighted by confidence)
│       Confidence: 0.88 (average confidence)
│
├─► voting:
│   └─► Result: 4.2 or 4.3 or 4.5 (highest vote)
│       Confidence: varies based on vote weight
│
└─► ensemble:
    └─► Result: [4.2, 4.5, 4.3] (all predictions)
        Confidence: 0.88 (average confidence)
```

This architecture enables true federated intelligence - coordination without monopoly,
centralization without centralized control.
