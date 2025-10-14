# BCM Incident Module Integration Analysis

**Date:** 2025-10-13
**Analyzed Directory:** `/platform-services/simulation/scenarios/bcm_incident/`
**Purpose:** Extract useful patterns and capabilities for Simulation & Modeling Service

---

## 📋 Executive Summary

The `bcm_incident` module is an **Odoo ERP module** for managing Business Continuity incidents with advanced features including:

- **AI Commander** for intelligent incident classification and response
- **Digital Twin Integration** capabilities
- **Crisis Management workflows**
- **Mobile response coordination**
- **EventBus integration patterns**

### Key Finding: ⚠️ **Different Technology Stack**

**Important:** This is an **Odoo 18.0 module** (Python ERP framework), NOT a FastAPI microservice like our Simulation Service.

**However**, it contains **extremely valuable patterns** that we can adapt:
- Incident data models
- AI classification logic
- Response workflow patterns
- Integration APIs
- EventBus communication patterns

---

## 🗂️ Files Analyzed

### Core Models (Python/Odoo):

1. **`models/bcm_incident_unified.py`** (1,518 lines)
   - Unified incident management model
   - Combines basic + advanced incident management
   - AI-powered classification and recommendations
   - Digital Twin integration hooks
   - **Backward compatibility wrappers** for legacy APIs

2. **`models/bcm_incident_integration_api.py`** (290 lines)
   - Integration APIs for external systems
   - Hook registration system
   - Digital Twin sync methods
   - AI recommendation engine interface

3. **`models/ai_communication_models.py`** (197 lines)
   - Crisis communication planning models
   - AI response templates
   - Classification and escalation rules
   - Learning pattern storage

4. **`__manifest__.py`** (206 lines)
   - Odoo module manifest
   - Dependencies, views, data files
   - External dependencies (requests, geopy, numpy)

5. **`migration/migration_script.py`** (447 lines)
   - Database migration tool
   - Handles merging two incident modules
   - Data validation and backup logic

---

## 🎯 Valuable Patterns to Extract

### 1. **Incident Classification System**

**Source:** `bcm_incident_unified.py:656-689`

```python
def _ai_classify_incident(self):
    """AI classification using keyword matching"""

    keywords_map = {
        'cyber': ['hack', 'breach', 'malware', 'ransomware', 'phishing', 'ddos'],
        'operational': ['outage', 'failure', 'down', 'unavailable', 'performance'],
        'natural': ['earthquake', 'flood', 'fire', 'storm', 'hurricane'],
        'supply_chain': ['supplier', 'delivery', 'logistics', 'procurement'],
        'health_safety': ['injury', 'accident', 'safety', 'emergency', 'medical']
    }

    # Match keywords in description/title
    # Calculate confidence score
    # Return classification + confidence
```

**Value for Simulation Service:**
- Can classify simulation scenarios automatically
- Helps select appropriate simulation engines
- Improves scenario template matching

### 2. **AI Risk Scoring**

**Source:** `bcm_incident_unified.py:756-780`

```python
def _ai_calculate_risk_score(self):
    """Multi-factor risk scoring"""
    score = 0

    # Severity weights
    severity_scores = {'low': 10, 'medium': 30, 'high': 60, 'critical': 90}
    score += severity_scores.get(self.severity, 30)

    # Type modifiers
    type_modifiers = {
        'cyber': 1.5,
        'health_safety': 1.4,
        'natural': 1.3,
        'operational': 1.0,
        'supply_chain': 0.8
    }
    score *= type_modifiers.get(self.incident_type, 1.0)

    # Time factor (older incidents = higher risk)
    hours_since = (datetime.now() - self.detected_at).total_seconds() / 3600
    if hours_since > 24:
        score *= 1.2

    return min(100, score)
```

**Value for Simulation Service:**
- Risk-based prioritization of simulations
- Automatic complexity level assignment
- Scenario severity assessment

### 3. **Emergency Response Plan Generation**

**Source:** `bcm_incident_unified.py:1240-1363`

```python
def _generate_ai_emergency_response_plan(self):
    """Generate AI-powered emergency response plan"""

    # Try external AI orchestrator first
    ai_result = self._make_external_ai_call(
        endpoint='/api/emergency-plan',
        data={
            'incident_type': self.incident_type,
            'severity': self.severity,
            'description': self.description,
            'affected_systems': self.affected_systems,
            'business_impact': self.business_impact
        }
    )

    if ai_result and ai_result.get('status') != 'error':
        # Use AI-generated plan
        self.write({
            'ai_recommendations': ai_result.get('emergency_plan', ''),
            'ai_risk_score': ai_result.get('risk_assessment', 0)
        })
        return

    # Fallback: Generate from templates based on incident type
    emergency_plans = {
        'cyber': """CYBER INCIDENT EMERGENCY RESPONSE PLAN...""",
        'operational': """OPERATIONAL INCIDENT EMERGENCY RESPONSE PLAN...""",
        'natural': """NATURAL DISASTER EMERGENCY RESPONSE PLAN...""",
    }

    plan = emergency_plans.get(self.incident_type, default_plan)
    self.write({'ai_recommendations': plan.strip()})
```

**Value for Simulation Service:**
- Template-based scenario generation with AI enhancement
- Fallback mechanisms when AI unavailable
- Structured response planning

### 4. **EventBus Integration Pattern**

**Source:** `bcm_incident_unified.py:1467-1487`

```python
def send_event_to_eventbus(self, event_type, data):
    """
    Send event to EventBus service

    Original method from bcm_core that was preserved during module unification
    """
    try:
        import logging
        _logger = logging.getLogger(__name__)

        # Log event (simple version)
        _logger.info(f"Event sent: {event_type} - {data}")

        # TODO: Integration with external EventBus service

    except Exception as e:
        _logger.error(f"Failed to send event: {e}")
```

**Value for Simulation Service:**
- Pattern for EventBus communication
- Simple logging fallback
- Error handling approach

### 5. **Integration API Design**

**Source:** `bcm_incident_integration_api.py:19-86`

```python
class BCMIncidentIntegrationAPI(models.AbstractModel):
    """API for external integrations"""

    @api.model
    def register_incident_hook(self, module_name, hook_type, callback):
        """Register integration hooks"""
        hooks = self.env['ir.config_parameter'].get_param('hooks', '{}')
        hooks = json.loads(hooks)
        if module_name not in hooks:
            hooks[module_name] = {}
        hooks[module_name][hook_type] = str(callback)
        self.env['ir.config_parameter'].set_param('hooks', json.dumps(hooks))

    @api.model
    def get_incident_data_for_integration(self, incident_id):
        """Get structured incident data"""
        incident = self.env['bcm.incident'].browse(incident_id)
        return {
            'id': incident.id,
            'incident_number': incident.incident_number,
            'severity': incident.severity,
            'status': incident.status,
            'ai_classification': incident.ai_classification,
            'ai_confidence': incident.ai_classification_confidence,
            'ai_risk_score': incident.ai_risk_score,
            # ... more fields
        }
```

**Value for Simulation Service:**
- Hook registration pattern for plugins
- Structured data export for integrations
- Configuration-based integration management

### 6. **Digital Twin Simulation Triggering**

**Source:** `bcm_incident_integration_api.py:88-122`

```python
@api.model
def trigger_incident_simulation(self, incident_id):
    """Launch simulation for Digital Twin"""
    incident = self.env['bcm.incident'].browse(incident_id)

    # Check if Digital Twin module available
    if 'bcm.digital.twin.simulation' in self.env:
        simulation = self.env['bcm.digital.twin.simulation'].create({
            'name': f"Simulation for {incident.name}",
            'related_incident': incident.id,
            'simulation_type': 'crisis_management',
            'scenario_description': incident.description,
        })
        simulation.action_start_simulation()

        return {
            'success': True,
            'simulation_id': simulation.id,
            'message': f"Simulation {simulation.name} started"
        }
    else:
        return {'success': False, 'error': 'Digital Twin module not installed'}
```

**Value for Simulation Service:**
- Pattern for triggering simulations from incidents
- Module capability checking
- Structured response format

### 7. **Effectiveness Scoring**

**Source:** `bcm_incident_unified.py:1135-1160`

```python
def _calculate_effectiveness_score(self):
    """Calculate response effectiveness"""
    score = 50.0  # Base score

    # RTO compliance
    if self.target_rto and self.actual_rto:
        if self.actual_rto <= self.target_rto:
            score += 30.0  # Met target
        else:
            penalty = min(20.0, (self.actual_rto - self.target_rto) / self.target_rto * 20)
            score -= penalty

    # Escalation penalty
    score -= (self.escalation_level * 5.0)

    # AI confidence bonus
    if self.ai_classification_confidence:
        score += (self.ai_classification_confidence / 100.0) * 10.0

    # Post-incident review bonus
    if self.post_incident_review_completed:
        score += 10.0

    return max(0.0, min(100.0, score))
```

**Value for Simulation Service:**
- Multi-factor effectiveness calculation
- RTO/RPO performance tracking
- Quality scoring for simulation results

### 8. **Learning Progress Assessment**

**Source:** `bcm_incident_unified.py:1162-1185`

```python
def _assess_learning_progress(self):
    """Assess learning from incidents"""
    progress = 0.0

    # Similar incidents handling
    similar_count = len(self.ai_similar_incidents)
    if similar_count > 0:
        progress += min(40.0, similar_count * 10.0)

    # AI recommendations usage
    if self.ai_recommendations:
        progress += 20.0

    # Lessons learned documentation
    if self.lessons_learned:
        progress += 25.0

    # Preventive measures
    if self.preventive_measures:
        progress += 15.0

    return min(100.0, progress)
```

**Value for Simulation Service:**
- Pattern for learning accumulation metrics
- Progress tracking methodology
- Knowledge capture assessment

---

## 🔧 Recommended Integrations for Simulation Service

### Priority 1: **Scenario Classification Engine**

**What:** Adapt the AI classification system for scenario analysis

**Implementation:**
```python
# simulation-service/core/scenario_classifier.py

from typing import Dict, Tuple
import re

class ScenarioClassifier:
    """Classify simulation scenarios automatically"""

    CATEGORY_KEYWORDS = {
        'cyber': ['hack', 'breach', 'malware', 'ransomware', 'phishing', 'ddos'],
        'operational': ['outage', 'failure', 'down', 'unavailable', 'performance'],
        'natural': ['earthquake', 'flood', 'fire', 'storm', 'hurricane'],
        'supply_chain': ['supplier', 'delivery', 'logistics', 'procurement'],
        'health_safety': ['injury', 'accident', 'safety', 'emergency', 'medical'],
        'pandemic': ['epidemic', 'pandemic', 'outbreak', 'virus', 'disease'],
        'infrastructure': ['power', 'water', 'utilities', 'facilities']
    }

    COMPLEXITY_INDICATORS = {
        'high': ['multiple', 'widespread', 'critical', 'cascade', 'complex'],
        'medium': ['moderate', 'limited', 'contained', 'local'],
        'low': ['minor', 'simple', 'single', 'isolated']
    }

    def classify_scenario(
        self,
        title: str,
        description: str
    ) -> Tuple[str, int, float]:
        """
        Classify scenario by category, complexity, and confidence

        Returns:
            (category, complexity_level, confidence_score)
        """
        text = f"{title.lower()} {description.lower()}"

        # Category classification
        category_scores = {}
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            matches = sum(1 for kw in keywords if kw in text)
            if matches > 0:
                category_scores[category] = matches

        if not category_scores:
            return ('general', 3, 0.5)

        best_category = max(category_scores, key=category_scores.get)
        max_matches = category_scores[best_category]
        confidence = min(0.95, 0.5 + (max_matches * 0.15))

        # Complexity assessment
        complexity = self._assess_complexity(text)

        return (best_category, complexity, confidence)

    def _assess_complexity(self, text: str) -> int:
        """Assess scenario complexity (1-5)"""
        complexity_score = 3  # Default medium

        for level, indicators in self.COMPLEXITY_INDICATORS.items():
            matches = sum(1 for ind in indicators if ind in text)
            if level == 'high' and matches > 0:
                complexity_score = min(5, complexity_score + matches)
            elif level == 'low' and matches > 0:
                complexity_score = max(1, complexity_score - matches)

        return max(1, min(5, complexity_score))

    def calculate_risk_score(
        self,
        category: str,
        complexity: int,
        severity: str
    ) -> float:
        """Calculate risk score (0-100)"""

        # Base severity scores
        severity_scores = {
            'low': 10,
            'medium': 30,
            'high': 60,
            'critical': 90
        }
        score = severity_scores.get(severity, 30)

        # Category modifiers
        category_modifiers = {
            'cyber': 1.5,
            'health_safety': 1.4,
            'natural': 1.3,
            'pandemic': 1.4,
            'operational': 1.0,
            'supply_chain': 0.9,
            'infrastructure': 1.2
        }
        score *= category_modifiers.get(category, 1.0)

        # Complexity factor
        score *= (0.8 + (complexity * 0.1))

        return min(100.0, score)
```

**Benefits:**
- Automatic scenario categorization
- Complexity assessment for engine selection
- Risk-based prioritization

---

### Priority 2: **EventBus Event Models**

**What:** Create typed event models for simulation lifecycle

**Implementation:**
```python
# simulation-service/models/event_models.py

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime

class SimulationEvent(BaseModel):
    """Base simulation event"""
    event_type: str
    simulation_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    data: Dict[str, Any]
    source_service: str = "simulation-service"

class SimulationStartedEvent(SimulationEvent):
    """Simulation started event"""
    event_type: str = "simulation.started"
    scenario_id: str
    engine_used: str
    estimated_duration_seconds: int

class SimulationCompletedEvent(SimulationEvent):
    """Simulation completed event"""
    event_type: str = "simulation.completed"
    status: str  # completed, failed, cancelled
    duration_seconds: int
    success_rate: float
    quality_score: float

class SimulationFailedEvent(SimulationEvent):
    """Simulation failed event"""
    event_type: str = "simulation.failed"
    error_message: str
    error_type: str
    stack_trace: Optional[str] = None

class LearningCapturedEvent(SimulationEvent):
    """Learning captured from simulation"""
    event_type: str = "simulation.learning_captured"
    scenario_id: str
    lessons_learned: list[str]
    recommendations: list[str]
    effectiveness_score: float
```

**Benefits:**
- Type-safe event communication
- Clear event contracts
- Easy EventBus integration

---

### Priority 3: **Response Plan Generator**

**What:** Template-based simulation plan generation with AI fallback

**Implementation:**
```python
# simulation-service/core/plan_generator.py

from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class SimulationPlanGenerator:
    """Generate simulation execution plans"""

    RESPONSE_TEMPLATES = {
        'cyber': {
            'phases': [
                'Detection & Initial Assessment',
                'Containment & Isolation',
                'Eradication & Recovery',
                'Post-Incident Analysis'
            ],
            'actions': [
                'Isolate affected systems',
                'Preserve digital evidence',
                'Reset compromised credentials',
                'Apply security patches',
                'Monitor for lateral movement'
            ],
            'kpis': ['Time to detection', 'Containment time', 'Data loss', 'Recovery time']
        },
        'operational': {
            'phases': [
                'Impact Assessment',
                'Failover Activation',
                'Service Restoration',
                'Validation & Monitoring'
            ],
            'actions': [
                'Assess business impact',
                'Activate backup systems',
                'Redirect operations',
                'Monitor system stability'
            ],
            'kpis': ['System availability', 'Recovery time', 'User impact', 'Service quality']
        },
        'natural': {
            'phases': [
                'Safety & Evacuation',
                'Damage Assessment',
                'Emergency Response',
                'Recovery Operations'
            ],
            'actions': [
                'Ensure personnel safety',
                'Contact emergency services',
                'Assess facility damage',
                'Activate alternate sites'
            ],
            'kpis': ['Personnel safety', 'Facility status', 'Recovery time', 'Business resumption']
        }
    }

    async def generate_plan(
        self,
        category: str,
        complexity: int,
        duration_hours: int,
        participants: int,
        ai_client: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Generate simulation execution plan

        Args:
            category: Scenario category
            complexity: Complexity level (1-5)
            duration_hours: Exercise duration
            participants: Number of participants
            ai_client: Optional AI orchestrator client for enhancement

        Returns:
            Simulation plan dictionary
        """

        # Try AI generation first
        if ai_client:
            try:
                ai_plan = await self._generate_with_ai(
                    ai_client,
                    category,
                    complexity,
                    duration_hours,
                    participants
                )
                if ai_plan:
                    logger.info(f"Generated simulation plan using AI for {category}")
                    return ai_plan
            except Exception as e:
                logger.warning(f"AI plan generation failed, using template: {e}")

        # Fallback to template
        return self._generate_from_template(
            category,
            complexity,
            duration_hours,
            participants
        )

    def _generate_from_template(
        self,
        category: str,
        complexity: int,
        duration_hours: int,
        participants: int
    ) -> Dict[str, Any]:
        """Generate from template"""

        template = self.RESPONSE_TEMPLATES.get(
            category,
            self.RESPONSE_TEMPLATES['operational']  # Default
        )

        # Adjust phases based on complexity
        phases = template['phases'][:3] if complexity <= 2 else template['phases']

        # Adjust actions based on complexity
        action_count = min(complexity * 2, len(template['actions']))
        actions = template['actions'][:action_count]

        # Calculate phase durations
        phase_duration = duration_hours / len(phases)

        plan = {
            'category': category,
            'complexity': complexity,
            'total_duration_hours': duration_hours,
            'participant_count': participants,
            'phases': [
                {
                    'name': phase,
                    'duration_hours': phase_duration,
                    'sequence': idx + 1
                }
                for idx, phase in enumerate(phases)
            ],
            'actions': [
                {
                    'action': action,
                    'priority': idx + 1,
                    'estimated_time_minutes': 15 * (idx + 1)
                }
                for idx, action in enumerate(actions)
            ],
            'kpis': template['kpis'],
            'generated_by': 'template',
            'template_version': '1.0'
        }

        return plan

    async def _generate_with_ai(
        self,
        ai_client,
        category: str,
        complexity: int,
        duration_hours: int,
        participants: int
    ) -> Optional[Dict[str, Any]]:
        """Generate using AI Orchestrator"""

        try:
            response = await ai_client.generate_simulation_plan(
                category=category,
                complexity=complexity,
                duration_hours=duration_hours,
                participants=participants
            )

            if response and response.get('success'):
                return {
                    **response.get('plan', {}),
                    'generated_by': 'ai',
                    'ai_model': response.get('model_used')
                }

            return None

        except Exception as e:
            logger.error(f"AI plan generation error: {e}")
            return None
```

**Benefits:**
- Structured simulation planning
- AI enhancement with template fallback
- Complexity-aware plan generation

---

## 📊 Integration Value Summary

| Pattern | Effort | Value | Priority | Status |
|---------|--------|-------|----------|--------|
| Scenario Classifier | Medium | High | 1 | **Recommended** |
| EventBus Event Models | Low | High | 2 | **Recommended** |
| Response Plan Generator | Medium | High | 3 | **Recommended** |
| Risk Scoring Engine | Low | Medium | 4 | Optional |
| Effectiveness Calculator | Low | Medium | 5 | Optional |
| Learning Assessment | Medium | High | 6 | **For Phase 2** |
| Hook System | High | Low | 7 | Future |
| Migration Tools | N/A | Low | 8 | Not Applicable |

---

## ⚠️ Important Notes

### **Technology Stack Differences**

The BCM Incident module is built for **Odoo 18.0** (ERP framework), which has:
- ORM-based models (not Pydantic)
- XML view definitions
- Built-in RLS through Odoo security
- PostgreSQL with Odoo conventions

Our Simulation Service uses:
- **FastAPI** + **Pydantic v2**
- **SQLAlchemy 2.0** async ORM
- **PostgreSQL** with manual RLS
- **REST APIs** instead of Odoo RPC

**We cannot directly import or use the Odoo code**, but we can **adapt the patterns and logic**.

### **What We Can Reuse:**

✅ **Business Logic Patterns:**
- Classification algorithms
- Risk scoring formulas
- Effectiveness calculations
- Event structures

✅ **Data Models (concepts):**
- Incident fields → Scenario fields
- AI confidence scores
- Learning progress metrics

✅ **Integration Patterns:**
- EventBus communication
- Hook systems
- External API calls

### **What We Cannot Reuse:**

❌ **Odoo-Specific Code:**
- `@api.model` decorators
- Odoo ORM methods (`self.env`, `browse`, `search`)
- XML view definitions
- Odoo security rules

❌ **Direct Imports:**
- `from odoo import models, fields, api`
- Cannot use Odoo modules in FastAPI

---

## 🎯 Recommended Next Steps

### **Immediate (Next 30 minutes):**

1. ✅ **Create `ScenarioClassifier`** - Adapt classification logic
2. ✅ **Create `SimulationEvent` models** - Type-safe events
3. ✅ **Create `SimulationPlanGenerator`** - Template-based plans

### **Phase 2 (After MVP):**

4. **Learning Accumulation System** - Track simulation improvements
5. **Risk Scoring Engine** - Automated risk assessment
6. **Effectiveness Calculator** - Quality metrics

---

## 📝 Conclusion

The BCM Incident module contains **valuable business logic patterns** that can significantly enhance our Simulation Service, particularly:

1. **Scenario Classification** - Automatic categorization
2. **Response Planning** - Structured execution plans
3. **Risk Assessment** - Multi-factor scoring
4. **Learning Tracking** - Progress metrics

While we **cannot directly use the Odoo code**, we can **adapt the algorithms and patterns** to our FastAPI/SQLAlchemy architecture.

**Estimated Implementation Time:** 2-3 hours for Priority 1-3 items

**Value Delivered:**
- Smarter scenario selection
- Better simulation planning
- Improved quality assessment
- Type-safe event communication

---

**Analysis Complete** ✅
**Ready for Implementation** 🚀
