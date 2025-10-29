# API SPECIFICATION v3.0 - Digital Twin Standalone
## Enhanced with 30 Simulation Experiments and AnyLogic Integration

**Version**: 3.0.0  
**Date**: August 16, 2025  
**Base URL**: `http://localhost:3000/api`  
**Authentication**: JWT Bearer Token  
**Content-Type**: `application/json`

---

## OVERVIEW

The Digital Twin Standalone API v3.0 provides comprehensive access to 30 simulation experiments across 4 categories, enhanced with AnyLogic Pypeline integration for professional-grade hybrid simulation capabilities.

### Categories of Experiments

1. **External Adapters (4)**: SimPy, Mesa, EpiNow2, AnyLogic Pypeline
2. **Digital Twin Scenarios (22)**: Operational, crisis, growth, integration scenarios
3. **Internal Engines (4)**: Theory of change, capacity optimization, routing, BCM

---

## AUTHENTICATION

### JWT Token Authentication
```bash
Authorization: Bearer <jwt_token>
```

All endpoints require valid JWT authentication except `/health` and `/experiments` (GET).

---

## CORE ENDPOINTS

### 1. System Health
```http
GET /api/health
```

**Response**:
```json
{
  "status": "healthy",
  "version": "3.0.0",
  "timestamp": "2025-08-16T10:00:00Z",
  "services": {
    "database": "connected",
    "simulation_engine": "active",
    "anylogic_pypeline": "ready",
    "external_adapters": {
      "simpy": "available",
      "mesa": "available", 
      "epinow2": "available",
      "anylogic": "ready"
    }
  }
}
```

### 2. List All Experiments
```http
GET /api/impact/simulations/experiments
```

**Response**:
```json
{
  "count": 30,
  "categories": {
    "external_adapters": 4,
    "digital_twin_scenarios": 22,
    "internal_engines": 4
  },
  "experiments": [
    {
      "id": "anylogic_hybrid",
      "type": "external",
      "category": "hybrid_simulation",
      "name": "AnyLogic Pypeline",
      "description": "Professional hybrid simulation with ML/AI integration",
      "capabilities": ["agent_based", "system_dynamics", "discrete_event", "ml_integration"],
      "estimated_duration": "2-5 minutes",
      "accuracy_target": ">85%"
    },
    {
      "id": "simpy_queue",
      "type": "external", 
      "category": "discrete_event",
      "name": "SimPy Queue Simulation",
      "description": "Service delivery queue optimization",
      "capabilities": ["process_modeling", "resource_allocation"],
      "estimated_duration": "1-3 minutes"
    },
    // ... 28 more experiments
  ]
}
```

---

## SIMULATION EXECUTION

### 3. Execute Simulation Experiment
```http
POST /api/impact/simulations/run
```

**Request Body**:
```json
{
  "experiment": "anylogic_hybrid",
  "organization_id": "org_123",
  "parameters": {
    "simulation_mode": "hybrid",
    "ml_enabled": true,
    "paradigms": ["agent_based", "system_dynamics"],
    "agents_count": 1000,
    "simulation_time": 365,
    "optimization_target": "impact_maximization",
    "ml_models": ["donation_prediction", "impact_forecasting"]
  },
  "options": {
    "confidence_level": 0.95,
    "iterations": 100,
    "seed": 42
  }
}
```

**Response**:
```json
{
  "simulation_id": "sim_789",
  "status": "completed",
  "experiment": "anylogic_hybrid",
  "execution_time": "3.2 minutes",
  "results": {
    "confidence_score": 0.87,
    "predictions": {
      "impact_score": 8.5,
      "efficiency_gain": "35%",
      "cost_optimization": "22%",
      "beneficiary_reach": "+1250 people"
    },
    "ml_insights": {
      "donor_behavior_prediction": {
        "retention_probability": 0.78,
        "donation_increase": "15%",
        "acquisition_cost": "$45/donor"
      },
      "impact_forecasting": {
        "12_month_projection": 9.2,
        "risk_factors": ["funding_volatility", "staff_turnover"],
        "opportunities": ["digital_expansion", "partnership_growth"]
      }
    },
    "paradigm_results": {
      "agent_based": {
        "individual_behaviors": "analyzed",
        "interaction_patterns": "mapped",
        "emergence_effects": "identified"
      },
      "system_dynamics": {
        "feedback_loops": "validated",
        "delays_identified": ["funding_to_impact", "training_to_efficiency"],
        "leverage_points": ["staff_training", "process_automation"]
      }
    },
    "optimization_recommendations": [
      {
        "category": "operational",
        "action": "Implement automated client intake system",
        "impact": "+18% efficiency",
        "confidence": 0.92
      },
      {
        "category": "strategic", 
        "action": "Expand partnerships with educational institutions",
        "impact": "+400 beneficiaries",
        "confidence": 0.84
      }
    ]
  },
  "metadata": {
    "execution_timestamp": "2025-08-16T10:15:00Z",
    "resource_usage": {
      "cpu_time": "156 seconds",
      "memory_peak": "1.8 GB",
      "ml_training_time": "45 seconds"
    }
  }
}
```

### 4. External Adapter Simulation
```http
POST /api/impact/simulations/run
```

**SimPy Queue Example**:
```json
{
  "experiment": "simpy_queue",
  "organization_id": "org_123",
  "parameters": {
    "queue_type": "client_services",
    "arrival_rate": 12,
    "service_rate": 15,
    "servers": 3,
    "simulation_time": 480
  }
}
```

**Mesa ABM Example**:
```json
{
  "experiment": "mesa_abm",
  "organization_id": "org_123", 
  "parameters": {
    "model_type": "stakeholder_network",
    "agents_count": 500,
    "interaction_radius": 3,
    "steps": 1000,
    "network_topology": "small_world"
  }
}
```

---

## ORGANIZATION MANAGEMENT

### 5. Create Organization
```http
POST /api/organizations
```

**Request Body**:
```json
{
  "name": "Hope Foundation",
  "type": "healthcare",
  "mission": "Providing healthcare access to underserved communities",
  "size": 45,
  "annual_budget": 2500000,
  "contact_info": {
    "email": "contact@hopefoundation.org",
    "phone": "+1-555-0123",
    "address": "123 Main St, City, State 12345"
  },
  "operational_data": {
    "departments": [
      {"name": "Healthcare Services", "staff": 25, "budget": 1500000},
      {"name": "Outreach", "staff": 12, "budget": 600000},
      {"name": "Administration", "staff": 8, "budget": 400000}
    ],
    "technology_stack": ["CRM", "EMR", "Fundraising_Platform"],
    "key_metrics": {
      "patients_served_monthly": 1200,
      "average_service_cost": 85,
      "donor_retention_rate": 0.72
    }
  }
}
```

### 6. Create Digital Twin
```http
POST /api/digital-twins
```

**Request Body**:
```json
{
  "organization_id": "org_123",
  "name": "Hope Foundation Digital Twin",
  "configuration": {
    "simulation_capabilities": ["all_30_experiments"],
    "ml_models_enabled": true,
    "anylogic_integration": true,
    "update_frequency": "daily",
    "accuracy_target": 0.85
  }
}
```

---

## ML/AI ENHANCED ENDPOINTS

### 7. Train ML Models
```http
POST /api/ml/models/train
```

**Request Body**:
```json
{
  "organization_id": "org_123",
  "models": [
    {
      "type": "donation_prediction",
      "algorithm": "xgboost",
      "features": ["donor_history", "seasonal_patterns", "campaign_type"],
      "target": "donation_amount"
    },
    {
      "type": "impact_forecasting", 
      "algorithm": "lstm",
      "features": ["service_metrics", "budget_allocation", "staff_efficiency"],
      "target": "impact_score"
    }
  ],
  "training_options": {
    "validation_split": 0.2,
    "cross_validation": true,
    "hyperparameter_tuning": true
  }
}
```

### 8. Get ML Predictions
```http
POST /api/ml/predictions
```

**Request Body**:
```json
{
  "organization_id": "org_123",
  "model_type": "donation_prediction",
  "input_data": {
    "donor_segment": "major_donors",
    "campaign_type": "annual_appeal",
    "timing": "year_end",
    "economic_indicators": "stable"
  },
  "prediction_horizon": "12_months"
}
```

---

## ANYLOGIC SPECIFIC ENDPOINTS

### 9. AnyLogic Model Configuration
```http
POST /api/anylogic/configure
```

**Request Body**:
```json
{
  "organization_id": "org_123",
  "model_configuration": {
    "paradigms": ["agent_based", "system_dynamics", "discrete_event"],
    "agents": {
      "donors": {"count": 500, "behavior_model": "empirical"},
      "staff": {"count": 45, "interaction_model": "network"},
      "beneficiaries": {"count": 1200, "service_model": "queue_based"}
    },
    "system_dynamics": {
      "variables": ["funding_level", "service_capacity", "impact_generation"],
      "feedback_loops": ["quality_reputation", "efficiency_funding"],
      "delays": ["training_effect", "campaign_results"]
    },
    "discrete_events": {
      "processes": ["client_intake", "service_delivery", "outcome_measurement"],
      "resources": ["staff_time", "equipment", "facilities"]
    },
    "ml_integration": {
      "prediction_models": ["donation_forecasting", "demand_prediction"],
      "optimization_algorithms": ["genetic_algorithm", "linear_programming"],
      "learning_components": ["adaptive_parameters", "pattern_recognition"]
    }
  }
}
```

### 10. AnyLogic Experiment Status
```http
GET /api/anylogic/experiments/{experiment_id}/status
```

**Response**:
```json
{
  "experiment_id": "exp_456",
  "status": "running",
  "progress": 0.65,
  "current_step": 6500,
  "total_steps": 10000,
  "estimated_completion": "2 minutes",
  "resource_usage": {
    "cpu_percent": 85,
    "memory_mb": 1600,
    "ml_training_progress": 0.80
  },
  "intermediate_results": {
    "agents_active": 545,
    "system_state": "stable",
    "ml_accuracy_current": 0.83
  }
}
```

---

## REPORTING AND ANALYTICS

### 11. Generate Comprehensive Report
```http
POST /api/reports/generate
```

**Request Body**:
```json
{
  "organization_id": "org_123",
  "report_type": "comprehensive_simulation_analysis",
  "experiments_included": ["anylogic_hybrid", "automation", "crisis"],
  "ml_insights": true,
  "comparison_analysis": true,
  "format": "pdf",
  "sections": [
    "executive_summary",
    "simulation_results",
    "ml_predictions", 
    "optimization_recommendations",
    "risk_assessment",
    "implementation_roadmap"
  ]
}
```

### 12. Export Data
```http
GET /api/exports/{organization_id}
```

**Query Parameters**:
- `format`: csv, json, excel
- `data_type`: simulation_results, ml_models, organization_profile
- `date_range`: ISO 8601 date range
- `experiments`: comma-separated experiment IDs

---

## ERROR HANDLING

### Standard Error Response
```json
{
  "error": {
    "code": "SIMULATION_FAILED",
    "message": "AnyLogic simulation timeout after 10 minutes",
    "details": {
      "experiment": "anylogic_hybrid",
      "step_reached": 7500,
      "total_steps": 10000,
      "resource_exhaustion": "memory_limit"
    },
    "timestamp": "2025-08-16T10:30:00Z",
    "request_id": "req_789"
  }
}
```

### Error Codes
| Code | Description | HTTP Status |
|------|-------------|-------------|
| `EXPERIMENT_NOT_FOUND` | Requested experiment ID not available | 404 |
| `SIMULATION_TIMEOUT` | Simulation exceeded time limit | 408 |
| `ML_MODEL_TRAINING_FAILED` | Machine learning model training error | 500 |
| `ANYLOGIC_CONNECTION_ERROR` | AnyLogic Pypeline connection failed | 503 |
| `INSUFFICIENT_DATA` | Not enough data for ML training | 400 |
| `RESOURCE_EXHAUSTED` | System resources (CPU/memory) exceeded | 507 |

---

## RATE LIMITING

| Endpoint Category | Rate Limit | Window |
|------------------|------------|--------|
| **Simulation Execution** | 10 requests | 1 hour |
| **ML Training** | 5 requests | 1 hour |
| **AnyLogic Operations** | 3 requests | 30 minutes |
| **Standard API** | 100 requests | 1 hour |

---

## WEBHOOKS

### Simulation Completion Webhook
```json
{
  "event": "simulation.completed",
  "simulation_id": "sim_789",
  "organization_id": "org_123",
  "experiment": "anylogic_hybrid",
  "status": "success",
  "execution_time": "3.2 minutes",
  "confidence_score": 0.87,
  "webhook_url": "https://your-app.com/webhooks/simulation",
  "timestamp": "2025-08-16T10:15:00Z"
}
```

---

## PAGINATION

All list endpoints support pagination:

```http
GET /api/simulations?page=1&limit=20&sort=created_at&order=desc
```

**Response includes**:
```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 150,
    "pages": 8,
    "has_next": true,
    "has_prev": false
  }
}
```

---

## VERSIONING

API versioning is handled through URL path:
- Current: `/api/v3/...`
- Previous: `/api/v2/...` (deprecated)
- Legacy: `/api/v1/...` (sunset 2025-12-31)

---

**Document Information:**
- Version: 3.0.0
- Last Updated: August 16, 2025
- Maintainer: Digital Twin Development Team
- Next Review: November 16, 2025