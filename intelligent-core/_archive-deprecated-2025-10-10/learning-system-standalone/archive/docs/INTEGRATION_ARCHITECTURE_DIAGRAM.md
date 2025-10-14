# Learning System Platform Integration - Visual Architecture

## High-Level Architecture

```
╔════════════════════════════════════════════════════════════════════════════╗
║                        AI PLATFORM ECOSYSTEM                                ║
╚════════════════════════════════════════════════════════════════════════════╝

┌──────────────────────────────────────────────────────────────────────────────┐
│                          INTELLIGENT CORE SERVICES                           │
│                                                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │
│  │  Learning   │  │    Risk     │  │ Compliance  │  │  Documents  │  ...  │
│  │   System    │  │   Service   │  │   Service   │  │   Service   │       │
│  │  Port 8033  │  │  Port 8031  │  │  Port 8032  │  │  Port 8034  │       │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘       │
│         │                │                 │                 │              │
│         └────────────────┴─────────────────┴─────────────────┘              │
│                                    │                                         │
│                          Все используют                                     │
│                                    ↓                                         │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│                     SHARED INTEGRATIONS LAYER                                │
│                      (/shared/integrations/)                                 │
│                                                                              │
│  ┌─────────────────┐  ┌──────────────────┐  ┌─────────────────┐           │
│  │  RAGConnector   │  │ MLPlatformClient │  │ KnowledgeClient │           │
│  │                 │  │                  │  │                 │           │
│  │ - search_       │  │ - predict()      │  │ - create_       │           │
│  │   knowledge()   │  │ - submit_        │  │   article()     │           │
│  │ - add_          │  │   feedback()     │  │ - search()      │           │
│  │   knowledge()   │  │ - get_model_     │  │ - list_by_      │           │
│  │                 │  │   performance()  │  │   category()    │           │
│  └─────────────────┘  └──────────────────┘  └─────────────────┘           │
│         │                      │                      │                     │
└─────────┼──────────────────────┼──────────────────────┼─────────────────────┘
          │                      │                      │
          ↓                      ↓                      ↓
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│   RAG SERVICE    │  │   ML PLATFORM    │  │   KB SERVICE     │
│   Port 8050      │  │   Port 8060      │  │   Port 8040      │
│                  │  │                  │  │                  │
│ ┌──────────────┐ │  │ ┌──────────────┐ │  │ ┌──────────────┐ │
│ │ Vector DB    │ │  │ │ Model        │ │  │ │ PostgreSQL   │ │
│ │ (Qdrant/     │ │  │ │ Registry     │ │  │ │              │ │
│ │  Pinecone)   │ │  │ │ (MLflow)     │ │  │ │ Articles     │ │
│ └──────────────┘ │  │ └──────────────┘ │  │ │ Procedures   │ │
│ ┌──────────────┐ │  │ ┌──────────────┐ │  │ │ Guidelines   │ │
│ │ Embeddings   │ │  │ │ Feature      │ │  │ └──────────────┘ │
│ │ (OpenAI)     │ │  │ │ Store        │ │  │                  │
│ └──────────────┘ │  │ └──────────────┘ │  │                  │
└──────────────────┘  └──────────────────┘  └──────────────────┘
```

## Learning System Detailed Architecture

```
╔════════════════════════════════════════════════════════════════════════════╗
║                    LEARNING SYSTEM SERVICE (Port 8033)                      ║
╚════════════════════════════════════════════════════════════════════════════╝

┌──────────────────────────────────────────────────────────────────────────────┐
│                              API LAYER                                       │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │ platform_integration_router.py                                     │    │
│  │                                                                    │    │
│  │  RAG Endpoints:                ML Endpoints:                      │    │
│  │  • POST /rag/search            • POST /ml/predict-success         │    │
│  │  • POST /rag/add-knowledge     • POST /ml/submit-feedback         │    │
│  │                                • GET  /ml/performance              │    │
│  │  KB Endpoints:                 Unified:                           │    │
│  │  • POST /kb/create-path        • POST /unified/predict-recommend  │    │
│  │  • POST /kb/auto-create        • GET  /status                     │    │
│  └────────────────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────────────────┘
                                      ↓
┌──────────────────────────────────────────────────────────────────────────────┐
│                          INTEGRATED ENGINES                                  │
│                                                                              │
│  ┌──────────────────────────────────┐  ┌──────────────────────────────┐    │
│  │ IntegratedKnowledgeConnector     │  │ IntegratedMLPredictor        │    │
│  │                                  │  │                              │    │
│  │ Uses: RAGConnector +             │  │ Uses: MLPlatformClient       │    │
│  │       KnowledgeClient            │  │                              │    │
│  │                                  │  │ Models:                      │    │
│  │ Features:                        │  │ • exercise_success_predictor │    │
│  │ • search_resources_for_gap()     │  │ • exercise_difficulty_scorer │    │
│  │ • create_learning_path()         │  │ • exercise_time_estimator    │    │
│  │ • auto_create_from_pattern()     │  │                              │    │
│  │ • sync_external_knowledge()      │  │ Features:                    │    │
│  │                                  │  │ • predict_success()          │    │
│  │ External Sync:                   │  │ • predict_difficulty()       │    │
│  │ • ISO standards                  │  │ • submit_actual_result()     │    │
│  │ • Threat intelligence            │  │ • get_model_performance()    │    │
│  └──────────────────────────────────┘  └──────────────────────────────┘    │
│                │                                     │                       │
└────────────────┼─────────────────────────────────────┼───────────────────────┘
                 │                                     │
                 ↓                                     ↓
┌──────────────────────────────────────────────────────────────────────────────┐
│                        SHARED INTEGRATIONS                                   │
│                                                                              │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐          │
│  │  RAGConnector    │  │ MLPlatformClient │  │ KnowledgeClient  │          │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘          │
└──────────────────────────────────────────────────────────────────────────────┘
```

## Knowledge Flow Architecture

```
╔════════════════════════════════════════════════════════════════════════════╗
║                          KNOWLEDGE FLOW                                     ║
╚════════════════════════════════════════════════════════════════════════════╝

┌─────────────────────────────────────────────────────────────────────────────┐
│                        KNOWLEDGE SOURCES                                    │
│                                                                             │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐           │
│  │ Exercises  │  │  Patterns  │  │    ISO     │  │  Threats   │           │
│  │  Results   │  │  Detected  │  │  Standards │  │   Feeds    │           │
│  └────────────┘  └────────────┘  └────────────┘  └────────────┘           │
│        │               │                │               │                   │
│        └───────────────┴────────────────┴───────────────┘                   │
│                                │                                            │
│                                ↓                                            │
│                  ┌──────────────────────────┐                               │
│                  │  Learning System         │                               │
│                  │  (Auto-create knowledge) │                               │
│                  └──────────────────────────┘                               │
│                                │                                            │
│                    ┌───────────┴───────────┐                                │
│                    ↓                       ↓                                │
│        ┌────────────────────┐   ┌────────────────────┐                     │
│        │  Knowledge Base    │   │    RAG Service     │                     │
│        │  (Structured)      │   │   (Semantic)       │                     │
│        │                    │   │                    │                     │
│        │  - Articles        │   │  - Vector DB       │                     │
│        │  - Procedures      │   │  - Embeddings      │                     │
│        │  - Guidelines      │   │  - Similarity      │                     │
│        └────────────────────┘   └────────────────────┘                     │
│                    │                       │                                │
│                    └───────────┬───────────┘                                │
│                                ↓                                            │
│                  ┌──────────────────────────┐                               │
│                  │  Unified Knowledge Base  │                               │
│                  │  (All Platform Services) │                               │
│                  └──────────────────────────┘                               │
│                                │                                            │
│        ┌───────────────────────┼───────────────────────┐                    │
│        ↓                       ↓                       ↓                    │
│  ┌──────────┐           ┌──────────┐           ┌──────────┐                │
│  │ Learning │           │   Risk   │           │Documents │                │
│  │  System  │           │ Service  │           │ Service  │    ...         │
│  └──────────┘           └──────────┘           └──────────┘                │
│                                                                             │
│  All services search and contribute to unified knowledge                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

## ML Feedback Loop Architecture

```
╔════════════════════════════════════════════════════════════════════════════╗
║                        ML FEEDBACK LOOP                                     ║
╚════════════════════════════════════════════════════════════════════════════╝

┌─────────────────────────────────────────────────────────────────────────────┐
│                        ALL PLATFORM SERVICES                                │
│                                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐                   │
│  │ Learning │  │   Risk   │  │Compliance│  │Documents │  ...               │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘                   │
│       │             │              │             │                          │
│       │  (1) Predict                                                        │
│       ├─────────────┼──────────────┼─────────────┤                          │
│       ↓             ↓              ↓             ↓                          │
│                                                                             │
│              ┌────────────────────────────────┐                             │
│              │      ML PLATFORM SERVICE       │                             │
│              │         (Port 8060)            │                             │
│              │                                │                             │
│              │  ┌──────────────────────────┐  │                             │
│              │  │   Model Registry         │  │                             │
│              │  │                          │  │                             │
│              │  │  Models:                 │  │                             │
│              │  │  • exercise_success_v3   │  │                             │
│              │  │  • risk_probability_v2   │  │                             │
│              │  │  • compliance_gap_v4     │  │                             │
│              │  │  • ...                   │  │                             │
│              │  └──────────────────────────┘  │                             │
│              │                                │                             │
│              │  ┌──────────────────────────┐  │                             │
│              │  │   Feature Store          │  │                             │
│              │  └──────────────────────────┘  │                             │
│              │                                │                             │
│              │  ┌──────────────────────────┐  │                             │
│              │  │   Feedback Collector     │  │                             │
│              │  │   (Predictions + Actuals)│  │                             │
│              │  └──────────────────────────┘  │                             │
│              │                                │                             │
│              │  ┌──────────────────────────┐  │                             │
│              │  │   Auto-Retraining        │  │                             │
│              │  │   (When threshold met)   │  │                             │
│              │  └──────────────────────────┘  │                             │
│              └────────────────────────────────┘                             │
│                           ↑                                                 │
│       │  (2) Submit feedback                                                │
│       ├─────────────┼──────────────┼─────────────┤                          │
│       │             │              │             │                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐                   │
│  │ Learning │  │   Risk   │  │Compliance│  │Documents │  ...               │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘                   │
│                                                                             │
│  All services benefit from shared learning                                 │
│  More feedback = Better models for everyone                                │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Unified Workflow Example

```
╔════════════════════════════════════════════════════════════════════════════╗
║              UNIFIED WORKFLOW: Predict + Recommend                          ║
╚════════════════════════════════════════════════════════════════════════════╝

User Request: "Plan new cyber incident exercise"
      │
      ↓
┌────────────────────────────────────────────────────┐
│ Step 1: ML Prediction                              │
│                                                    │
│  POST /ml/predict-success                          │
│  {                                                 │
│    scenario_type: "cyber_incident",                │
│    team_size: 12,                                  │
│    avg_competency: 0.55  // LOW                    │
│  }                                                 │
│                                                    │
│  → ML Platform Client                              │
│    → Model: exercise_success_predictor             │
│      → Features: scenario, team, history           │
│                                                    │
│  Response:                                         │
│  {                                                 │
│    predicted_score: 64.5,                          │
│    risk_level: "MEDIUM",  // ← TRIGGER             │
│    confidence: 0.78                                │
│  }                                                 │
└────────────────────────────────────────────────────┘
      │
      │ Risk is MEDIUM/HIGH
      ↓
┌────────────────────────────────────────────────────┐
│ Step 2: RAG Search for Resources                   │
│                                                    │
│  RAGConnector.search_knowledge(                    │
│    query: "cyber incident training",               │
│    context: {user_id, competency_level},           │
│    filters: {type: "training_material"}            │
│  )                                                 │
│                                                    │
│  → RAG Service                                     │
│    → Vector DB semantic search                     │
│    → Finds relevant resources from:                │
│      • Learning System patterns                    │
│      • Documents Service                           │
│      • Knowledge Base articles                     │
│      • ISO standards                               │
│      • Best practices                              │
│                                                    │
│  Response:                                         │
│  [                                                 │
│    {title: "Cyber Response Training", score: 0.92} │
│    {title: "Escalation Procedures", score: 0.88}  │
│    ...                                             │
│  ]                                                 │
└────────────────────────────────────────────────────┘
      │
      ↓
┌────────────────────────────────────────────────────┐
│ Step 3: Create Learning Path                       │
│                                                    │
│  IntegratedKnowledgeConnector.                     │
│    create_learning_path_from_resources(            │
│      user_id, gap, resources                       │
│    )                                               │
│                                                    │
│  → Sorts by relevance + difficulty                 │
│  → Structures into phases                          │
│  → Estimates time                                  │
│                                                    │
│  Response:                                         │
│  {                                                 │
│    path: [                                         │
│      {order: 1, title: "...", duration: 4h},       │
│      {order: 2, title: "...", duration: 2h},       │
│      ...                                           │
│    ],                                              │
│    total_hours: 12                                 │
│  }                                                 │
└────────────────────────────────────────────────────┘
      │
      ↓
┌────────────────────────────────────────────────────┐
│ Final Response to User                             │
│                                                    │
│  {                                                 │
│    prediction: {                                   │
│      predicted_score: 64.5,                        │
│      risk_level: "medium",                         │
│      recommendations: [...]                        │
│    },                                              │
│    learning_resources: [                           │
│      {title: "...", type: "...", hours: ...},      │
│      ...                                           │
│    ],                                              │
│    workflow: "unified_predict_recommend"           │
│  }                                                 │
│                                                    │
│  User gets:                                        │
│  ✓ Prediction with risk level                     │
│  ✓ Personalized learning resources                │
│  ✓ Structured learning path                       │
│  ✓ Time estimates                                 │
└────────────────────────────────────────────────────┘
```

## Component Interaction Diagram

```
╔════════════════════════════════════════════════════════════════════════════╗
║                      COMPONENT INTERACTIONS                                 ║
╚════════════════════════════════════════════════════════════════════════════╝

Learning System Components:
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│  ┌─────────────────┐                                                        │
│  │     API         │  FastAPI Router                                        │
│  │   platform_     │  • Receives HTTP requests                              │
│  │  integration_   │  • Validates input                                     │
│  │    router.py    │  • Returns responses                                   │
│  └─────────────────┘                                                        │
│         │                                                                   │
│         ↓                                                                   │
│  ┌─────────────────────────────────┐                                        │
│  │      Integrated Engines         │                                        │
│  │                                 │                                        │
│  │  ┌───────────────────────────┐  │                                        │
│  │  │ IntegratedKnowledge       │  │  Learning System specific logic        │
│  │  │ Connector                 │  │  • search_resources_for_gap()          │
│  │  │                           │  │  • create_learning_path()              │
│  │  │ Uses: RAGConnector +      │  │  • auto_create_from_pattern()          │
│  │  │       KnowledgeClient     │  │                                        │
│  │  └───────────────────────────┘  │                                        │
│  │                                 │                                        │
│  │  ┌───────────────────────────┐  │                                        │
│  │  │ IntegratedMLPredictor     │  │  Learning System specific logic        │
│  │  │                           │  │  • predict_exercise_success()          │
│  │  │ Uses: MLPlatformClient    │  │  • predict_difficulty()                │
│  │  │                           │  │  • submit_actual_result()              │
│  │  └───────────────────────────┘  │                                        │
│  └─────────────────────────────────┘                                        │
│         │                │                                                  │
│         ↓                ↓                                                  │
└─────────────────────────────────────────────────────────────────────────────┘

Shared Components Layer:
┌─────────────────────────────────────────────────────────────────────────────┐
│                         /shared/integrations/                               │
│                                                                             │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐             │
│  │RAGConnector  │      │MLPlatform    │      │Knowledge     │             │
│  │              │      │Client        │      │Client        │             │
│  │• Semantic    │      │• Predictions │      │• CRUD ops    │             │
│  │  search      │      │• Feedback    │      │• Structured  │             │
│  │• Add         │      │• Performance │      │  metadata    │             │
│  │  knowledge   │      │• Features    │      │• Categories  │             │
│  │• Fallback    │      │• Fallback    │      │• Tags        │             │
│  └──────────────┘      └──────────────┘      └──────────────┘             │
│         │                     │                      │                     │
│         │                     │                      │                     │
│         ↓                     ↓                      ↓                     │
└─────────────────────────────────────────────────────────────────────────────┘

Platform Services:
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐             │
│  │ RAG Service  │      │ ML Platform  │      │ KB Service   │             │
│  │ Port 8050    │      │ Port 8060    │      │ Port 8040    │             │
│  │              │      │              │      │              │             │
│  │• Vector DB   │      │• Models      │      │• PostgreSQL  │             │
│  │• Embeddings  │      │• Registry    │      │• Articles    │             │
│  │• Similarity  │      │• Features    │      │• Procedures  │             │
│  │              │      │• Retraining  │      │              │             │
│  └──────────────┘      └──────────────┘      └──────────────┘             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Deployment Architecture

```
╔════════════════════════════════════════════════════════════════════════════╗
║                      DEPLOYMENT ARCHITECTURE                                ║
╚════════════════════════════════════════════════════════════════════════════╝

┌─────────────────────────────────────────────────────────────────────────────┐
│                            KUBERNETES CLUSTER                               │
│                                                                             │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │                      INTELLIGENT CORE NAMESPACE                    │    │
│  │                                                                    │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │    │
│  │  │  Learning    │  │    Risk      │  │  Compliance  │   ...      │    │
│  │  │   System     │  │   Service    │  │   Service    │            │    │
│  │  │              │  │              │  │              │            │    │
│  │  │  Deployment  │  │  Deployment  │  │  Deployment  │            │    │
│  │  │  Replicas: 3 │  │  Replicas: 2 │  │  Replicas: 2 │            │    │
│  │  │  Port: 8033  │  │  Port: 8031  │  │  Port: 8032  │            │    │
│  │  └──────────────┘  └──────────────┘  └──────────────┘            │    │
│  │         │                 │                  │                    │    │
│  │         └─────────────────┴──────────────────┘                    │    │
│  │                           │                                        │    │
│  │                    Uses Shared Config                             │    │
│  │                           ↓                                        │    │
│  │                                                                    │    │
│  │              ┌────────────────────────────┐                        │    │
│  │              │   Shared ConfigMap         │                        │    │
│  │              │                            │                        │    │
│  │              │  RAG_SERVICE_URL: ...      │                        │    │
│  │              │  ML_PLATFORM_URL: ...      │                        │    │
│  │              │  KB_SERVICE_URL: ...       │                        │    │
│  │              └────────────────────────────┘                        │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │                     PLATFORM SERVICES NAMESPACE                    │    │
│  │                                                                    │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │    │
│  │  │ RAG Service  │  │ ML Platform  │  │  KB Service  │            │    │
│  │  │              │  │              │  │              │            │    │
│  │  │  StatefulSet │  │  Deployment  │  │  StatefulSet │            │    │
│  │  │  Replicas: 2 │  │  Replicas: 3 │  │  Replicas: 2 │            │    │
│  │  │  Port: 8050  │  │  Port: 8060  │  │  Port: 8040  │            │    │
│  │  └──────────────┘  └──────────────┘  └──────────────┘            │    │
│  │         │                 │                  │                    │    │
│  │         ↓                 ↓                  ↓                    │    │
│  │  ┌──────────┐      ┌──────────┐      ┌──────────┐                │    │
│  │  │ Qdrant   │      │ MLflow   │      │PostgreSQL│                │    │
│  │  │ Vector DB│      │ Registry │      │          │                │    │
│  │  │  PVC     │      │   PVC    │      │   PVC    │                │    │
│  │  └──────────┘      └──────────┘      └──────────┘                │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

This architecture shows the complete integration between Learning System and shared platform components with visual diagrams for easy understanding.
