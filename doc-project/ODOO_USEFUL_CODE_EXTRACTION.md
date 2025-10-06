# Odoo Modules - Extraction полезного кода для v2.0

## Анализ: Что можно переиспользовать

После детального анализа `bcm_ai_control` найдено **много полезной логики** которую стоит портировать в v2.0!

---

## 1. AI Organ Coordination Patterns ✅

### Что нашли (v1.0):
**Файл**: `models/ai_organ_coordinator.py`

```python
class BCMAIOrganCoordinator:
    """Digital Organism Coordination"""
    
    # ✅ ПОЛЕЗНО: Список всех 10 AI Organs
    ai_organs = [
        {'type': 'governance_brain', 'name': '🧠 Governance Brain'},
        {'type': 'emergency_response', 'name': '🚨 Emergency Response'},
        {'type': 'impact_oracle', 'name': '🔮 Impact Oracle'},
        {'type': 'scenario_creator', 'name': '🎭 Scenario Creator'},
        {'type': 'risk_advisor', 'name': '⚠️ Risk Advisor'},
        {'type': 'compliance_guardian', 'name': '🛡️ Compliance Guardian'},
        {'type': 'performance_analyst', 'name': '📈 Performance Analyst'},
        {'type': 'learning_coach', 'name': '🎓 Learning Coach'},
        {'type': 'plan_generator', 'name': '📋 Plan Generator'},
        {'type': 'lifecycle_monitor', 'name': '📊 Lifecycle Monitor'}
    ]
    
    # ✅ ПОЛЕЗНО: Organism Personality concept
    organism_personality = [
        ('analytical', '🧮 Analytical - Data-driven decisions'),
        ('creative', '🎨 Creative - Innovative solutions'),
        ('protective', '🛡️ Protective - Risk-averse approach'),
        ('adaptive', '🔄 Adaptive - Learning-focused'),
        ('balanced', '⚖️ Balanced - Holistic approach')
    ]
    
    # ✅ ПОЛЕЗНО: Consciousness Level tracking
    consciousness_level = 0.0 - 1.0  # Organism maturity metric
    
    # ✅ ПОЛЕЗНО: Collective Decision Making
    def action_coordinate_ai_decision(self, decision_context):
        """Координация решений между AI organs"""
        # 1. Determine required organs
        required_organs = self._determine_required_organs(context)
        
        # 2. Collect input from each organ
        organ_inputs = {}
        for organ_type in required_organs:
            organ_input = self._get_organ_input(organ_type, context)
            organ_inputs[organ_type] = organ_input
        
        # 3. Synthesize collective decision
        collective_decision = self._synthesize_collective_decision(
            organ_inputs, 
            decision_context
        )
        
        # 4. Update collective wisdom
        self._update_collective_wisdom(context, collective_decision)
        
        return collective_decision
    
    # ✅ ПОЛЕЗНО: Evolution trigger logic
    def action_trigger_organism_evolution(self):
        """Trigger evolutionary upgrade"""
        evolution_threshold = 0.9
        
        if self.consciousness_level >= evolution_threshold:
            # Trigger evolution
            new_capabilities = self._evolve_organism_capabilities()
            self.consciousness_level = min(1.0, self.consciousness_level + 0.1)
            
            # Log evolution event
            evolution_events.append({
                'timestamp': datetime.now(),
                'type': 'capability_evolution',
                'new_capabilities': new_capabilities
            })
```

### Как портировать в v2.0:

**Создать**: `intelligent-core/ai-orchestration/decision_center/collective_coordinator.py`

```python
from typing import List, Dict, Any
from enum import Enum
from dataclasses import dataclass

class OrganismPersonality(Enum):
    """Platform operational personality"""
    ANALYTICAL = "analytical"      # Data-driven
    CREATIVE = "creative"          # Innovative
    PROTECTIVE = "protective"      # Risk-averse
    ADAPTIVE = "adaptive"          # Learning-focused
    BALANCED = "balanced"          # Holistic

@dataclass
class AIOrganConfig:
    """AI Organ configuration"""
    type: str
    name: str
    emoji: str
    provider: str  # 'anthropic', 'openai', 'local'

class CollectiveCoordinator:
    """
    Координация коллективных решений между AI organs
    
    Портировано из bcm_ai_control
    """
    
    # Все 10 AI Organs (из Odoo v1.0)
    AI_ORGANS = [
        AIOrganConfig('governance_brain', 'Governance Brain', '🧠', 'anthropic'),
        AIOrganConfig('emergency_response', 'Emergency Response', '🚨', 'local'),
        AIOrganConfig('impact_oracle', 'Impact Oracle', '🔮', 'local'),
        AIOrganConfig('scenario_creator', 'Scenario Creator', '🎭', 'local'),
        AIOrganConfig('risk_advisor', 'Risk Advisor', '⚠️', 'local'),
        AIOrganConfig('compliance_guardian', 'Compliance Guardian', '🛡️', 'local'),
        AIOrganConfig('performance_analyst', 'Performance Analyst', '📈', 'local'),
        AIOrganConfig('learning_coach', 'Learning Coach', '🎓', 'local'),
        AIOrganConfig('plan_generator', 'Plan Generator', '📋', 'local'),
        AIOrganConfig('lifecycle_monitor', 'Lifecycle Monitor', '📊', 'local')
    ]
    
    def __init__(
        self,
        personality: OrganismPersonality = OrganismPersonality.BALANCED
    ):
        self.personality = personality
        self.consciousness_level = 0.3  # Start at 30%
        self.collective_wisdom = {}
        self.organs = {}  # Initialized organs
    
    async def coordinate_decision(
        self, 
        decision_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Коллективное решение от множества AI organs
        
        Steps:
        1. Determine which organs needed
        2. Gather input from each organ
        3. Synthesize collective decision
        4. Update collective wisdom
        """
        
        # 1. Determine required organs based on context
        required = self._determine_required_organs(decision_context)
        
        # 2. Gather inputs in parallel
        organ_inputs = await asyncio.gather(*[
            self._get_organ_input(organ_type, decision_context)
            for organ_type in required
        ])
        
        # 3. Synthesize decision
        decision = self._synthesize_decision(organ_inputs, decision_context)
        
        # 4. Update wisdom
        self._update_collective_wisdom(decision_context, decision)
        
        return decision
    
    def _determine_required_organs(self, context: Dict) -> List[str]:
        """Determine which organs to consult"""
        task_type = context.get('task_type')
        
        # Mapping tasks to organs (from Odoo logic)
        task_organ_mapping = {
            'risk_assessment': ['risk_advisor', 'impact_oracle', 'governance_brain'],
            'bia_analysis': ['impact_oracle', 'performance_analyst'],
            'scenario_planning': ['scenario_creator', 'impact_oracle', 'risk_advisor'],
            'plan_generation': ['plan_generator', 'compliance_guardian'],
            'incident_response': ['emergency_response', 'risk_advisor', 'plan_generator']
        }
        
        return task_organ_mapping.get(task_type, ['governance_brain'])
    
    async def trigger_evolution(self) -> bool:
        """
        Trigger organism evolution
        Returns: True if evolution occurred
        """
        EVOLUTION_THRESHOLD = 0.9
        
        if self.consciousness_level >= EVOLUTION_THRESHOLD:
            # Evolve capabilities
            new_capabilities = await self._evolve_capabilities()
            
            # Increase consciousness
            self.consciousness_level = min(1.0, self.consciousness_level + 0.1)
            
            # Log evolution
            self.collective_wisdom['evolution_events'] = [
                *self.collective_wisdom.get('evolution_events', []),
                {
                    'timestamp': datetime.utcnow(),
                    'type': 'capability_evolution',
                    'new_capabilities': new_capabilities,
                    'consciousness_level': self.consciousness_level
                }
            ]
            
            return True
        
        return False
```

---

## 2. Anthropic Integration с Usage Tracking ✅

### Что нашли (v1.0):
**Файл**: `models/anthropic_integration.py`

```python
class BCMAnthropicIntegration:
    """Anthropic Claude integration with tracking"""
    
    # ✅ ПОЛЕЗНО: Model selection
    model_name = [
        ('claude-3-5-sonnet-20241022', 'Claude 3.5 Sonnet (Latest)'),
        ('claude-3-5-haiku-20241022', 'Claude 3.5 Haiku (Fast)'),
        ('claude-3-opus-20240229', 'Claude 3 Opus (Most Capable)')
    ]
    
    # ✅ ПОЛЕЗНО: Usage tracking
    daily_token_usage = 0
    monthly_token_usage = 0
    daily_cost = 0.0
    monthly_cost = 0.0
    
    # ✅ ПОЛЕЗНО: Rate limiting
    requests_per_minute = 50
    daily_request_limit = 1000
    
    # ✅ ПОЛЕЗНО: Health monitoring
    api_health_status = ['healthy', 'degraded', 'error', 'rate_limited']
    
    # ✅ ПОЛЕЗНО: Proper API call with error handling
    def call_claude_api(self, user_message, system_prompt=None, context=None):
        """Call Claude with proper error handling"""
        
        # Prepare messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        if context:
            context_message = f"Context: {json.dumps(context)}\n\n{user_message}"
            messages.append({"role": "user", "content": context_message})
        else:
            messages.append({"role": "user", "content": user_message})
        
        # API Request
        headers = {
            'x-api-key': api_key,
            'content-type': 'application/json',
            'anthropic-version': '2023-06-01'
        }
        
        payload = {
            'model': self.model_name,
            'max_tokens': self.max_tokens,
            'temperature': self.temperature,
            'messages': messages
        }
        
        response = requests.post(
            f'{self.api_base_url}/v1/messages',
            headers=headers,
            json=payload,
            timeout=60
        )
        
        # ✅ ПОЛЕЗНО: Proper error handling
        if response.status_code == 200:
            result = response.json()
            content = result.get('content', [{}])[0].get('text', '')
            
            # ✅ ПОЛЕЗНО: Update usage stats
            self._update_usage_stats(result.get('usage', {}))
            
            return {'success': True, 'content': content, 'usage': result.get('usage')}
        
        elif response.status_code == 429:
            self.api_health_status = 'rate_limited'
            return {
                'success': False,
                'error': 'Rate limit exceeded',
                'retry_after': response.headers.get('retry-after', 60)
            }
        
        else:
            return {'success': False, 'error': f'API error {response.status_code}'}
    
    # ✅ ПОЛЕЗНО: Cost calculation
    def _update_usage_stats(self, usage_data):
        """Track token usage and costs"""
        input_tokens = usage_data.get('input_tokens', 0)
        output_tokens = usage_data.get('output_tokens', 0)
        
        # Pricing (Claude 3.5 Sonnet)
        cost_per_1k_input = 0.003   # $3 per 1M
        cost_per_1k_output = 0.015  # $15 per 1M
        
        call_cost = (
            (input_tokens * cost_per_1k_input / 1000) + 
            (output_tokens * cost_per_1k_output / 1000)
        )
        
        self.daily_token_usage += (input_tokens + output_tokens)
        self.daily_cost += call_cost
```

### Как портировать в v2.0:

**Создать**: `intelligent-core/ai-office/llm/anthropic_client.py`

```python
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import httpx
import logging

logger = logging.getLogger(__name__)

@dataclass
class UsageStats:
    """LLM usage statistics"""
    daily_tokens: int = 0
    monthly_tokens: int = 0
    daily_cost: float = 0.0
    monthly_cost: float = 0.0
    last_reset: datetime = None

class AnthropicClient:
    """
    Anthropic Claude client with usage tracking
    
    Портировано из bcm_ai_control/anthropic_integration.py
    """
    
    MODELS = {
        'sonnet': 'claude-3-5-sonnet-20241022',
        'haiku': 'claude-3-5-haiku-20241022',
        'opus': 'claude-3-opus-20240229'
    }
    
    # Pricing (per 1M tokens)
    PRICING = {
        'claude-3-5-sonnet-20241022': {'input': 3.0, 'output': 15.0},
        'claude-3-5-haiku-20241022': {'input': 0.8, 'output': 4.0},
        'claude-3-opus-20240229': {'input': 15.0, 'output': 75.0}
    }
    
    def __init__(
        self,
        api_key: str,
        model: str = 'sonnet',
        max_tokens: int = 4096,
        temperature: float = 0.7,
        requests_per_minute: int = 50,
        daily_limit: int = 1000
    ):
        self.api_key = api_key
        self.model = self.MODELS.get(model, model)
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.requests_per_minute = requests_per_minute
        self.daily_limit = daily_limit
        
        self.usage_stats = UsageStats(last_reset=datetime.utcnow())
        self.health_status = 'healthy'
        
        self.client = httpx.AsyncClient(
            base_url='https://api.anthropic.com',
            headers={
                'x-api-key': api_key,
                'content-type': 'application/json',
                'anthropic-version': '2023-06-01'
            },
            timeout=60.0
        )
    
    async def call(
        self,
        user_message: str,
        system_prompt: Optional[str] = None,
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Call Claude API with proper error handling
        
        Returns:
            {'success': bool, 'content': str, 'usage': dict, 'error': str}
        """
        
        try:
            # Build messages
            messages = []
            
            if context:
                context_msg = f"Context: {json.dumps(context, indent=2)}\n\n{user_message}"
                messages.append({"role": "user", "content": context_msg})
            else:
                messages.append({"role": "user", "content": user_message})
            
            # Payload
            payload = {
                'model': self.model,
                'max_tokens': self.max_tokens,
                'temperature': self.temperature,
                'messages': messages
            }
            
            if system_prompt:
                payload['system'] = system_prompt
            
            # API call
            response = await self.client.post('/v1/messages', json=payload)
            
            # Handle response
            if response.status_code == 200:
                result = response.json()
                content = result.get('content', [{}])[0].get('text', '')
                usage = result.get('usage', {})
                
                # Update usage stats
                self._update_usage_stats(usage)
                
                self.health_status = 'healthy'
                
                return {
                    'success': True,
                    'content': content,
                    'model': result.get('model'),
                    'usage': usage
                }
            
            elif response.status_code == 429:
                self.health_status = 'rate_limited'
                return {
                    'success': False,
                    'error': 'Rate limit exceeded',
                    'retry_after': int(response.headers.get('retry-after', 60))
                }
            
            else:
                self.health_status = 'error'
                return {
                    'success': False,
                    'error': f'API error {response.status_code}: {response.text}'
                }
        
        except httpx.TimeoutException:
            return {
                'success': False,
                'error': 'API request timeout'
            }
        
        except Exception as e:
            logger.error(f'Anthropic API call failed: {e}')
            return {
                'success': False,
                'error': str(e)
            }
    
    def _update_usage_stats(self, usage: Dict):
        """Update token usage and cost tracking"""
        input_tokens = usage.get('input_tokens', 0)
        output_tokens = usage.get('output_tokens', 0)
        
        # Get pricing for current model
        pricing = self.PRICING.get(self.model, {'input': 3.0, 'output': 15.0})
        
        # Calculate cost
        cost = (
            (input_tokens * pricing['input'] / 1_000_000) +
            (output_tokens * pricing['output'] / 1_000_000)
        )
        
        # Update stats
        self.usage_stats.daily_tokens += (input_tokens + output_tokens)
        self.usage_stats.monthly_tokens += (input_tokens + output_tokens)
        self.usage_stats.daily_cost += cost
        self.usage_stats.monthly_cost += cost
        
        # Check if need to reset daily stats
        if (datetime.utcnow() - self.usage_stats.last_reset) > timedelta(days=1):
            self.usage_stats.daily_tokens = 0
            self.usage_stats.daily_cost = 0.0
            self.usage_stats.last_reset = datetime.utcnow()
    
    def get_usage_stats(self) -> Dict:
        """Get current usage statistics"""
        return {
            'daily_tokens': self.usage_stats.daily_tokens,
            'monthly_tokens': self.usage_stats.monthly_tokens,
            'daily_cost': round(self.usage_stats.daily_cost, 4),
            'monthly_cost': round(self.usage_stats.monthly_cost, 2),
            'health_status': self.health_status,
            'model': self.model
        }
```

---

## 3. EventBus Integration Pattern ✅

### Что нашли (v1.0):
**Файл**: `bcm_base/models/eventbus_integration.py`

```python
class BCMEventBusIntegration:
    """EventBus integration pattern"""
    
    # ✅ ПОЛЕЗНО: Standard event publishing
    def publish_module_event(self, event_type, event_data, priority='normal'):
        """Publish events to ecosystem"""
        event_payload = {
            'source_module': self._name,
            'event_type': event_type,
            'event_data': event_data,
            'priority': priority,
            'timestamp': datetime.now().isoformat(),
            'company_id': company.id,
            'user_id': user.id
        }
        
        response = requests.post(
            'http://eventbus:8001/api/events/publish',
            json=event_payload,
            timeout=5
        )
    
    # ✅ ПОЛЕЗНО: Cross-module workflow triggers
    def trigger_cross_module_workflow(self, workflow_type, workflow_data):
        """Trigger workflows across modules"""
        
        workflow_triggers = {
            'risk_to_bia': {
                'target_module': 'bcm.bia',
                'event_type': 'risk_assessment_complete',
                'priority': 'high'
            },
            'bia_to_plans': {
                'target_module': 'bcm.plans',
                'event_type': 'bia_analysis_complete',
                'priority': 'high'
            },
            'plans_to_exercise': {
                'target_module': 'bcm.exercise',
                'event_type': 'plans_updated',
                'priority': 'medium'
            },
            'incident_to_scenario': {
                'target_module': 'bcm.scenario',
                'event_type': 'incident_lessons_available',
                'priority': 'medium'
            },
            'governance_to_all': {
                'target_module': 'all',
                'event_type': 'governance_decision',
                'priority': 'critical'
            }
        }
        
        trigger = workflow_triggers.get(workflow_type)
        if trigger:
            return self.publish_module_event(
                trigger['event_type'],
                workflow_data,
                trigger['priority']
            )
```

### Как портировать в v2.0:

**Уже есть**: `infrastructure/eventbus/` но можно добавить эти workflow patterns!

**Дополнить**: `infrastructure/eventbus/workflow_triggers.py`

```python
from enum import Enum
from typing import Dict, Any

class WorkflowTriggerType(Enum):
    """Cross-module workflow triggers (from Odoo v1.0)"""
    RISK_TO_BIA = "risk_to_bia"
    BIA_TO_PLANS = "bia_to_plans"
    PLANS_TO_EXERCISE = "plans_to_exercise"
    INCIDENT_TO_SCENARIO = "incident_to_scenario"
    GOVERNANCE_TO_ALL = "governance_to_all"

class WorkflowTriggerRegistry:
    """
    Registry of cross-module workflow triggers
    
    Портировано из bcm_base/eventbus_integration.py
    """
    
    TRIGGERS = {
        WorkflowTriggerType.RISK_TO_BIA: {
            'target_module': 'bia',
            'event_type': 'risk_assessment_complete',
            'priority': 'high',
            'description': 'Risk assessment completed → trigger BIA'
        },
        WorkflowTriggerType.BIA_TO_PLANS: {
            'target_module': 'plans',
            'event_type': 'bia_analysis_complete',
            'priority': 'high',
            'description': 'BIA completed → trigger plan generation'
        },
        WorkflowTriggerType.PLANS_TO_EXERCISE: {
            'target_module': 'exercise',
            'event_type': 'plans_updated',
            'priority': 'medium',
            'description': 'Plans updated → trigger exercise scheduling'
        },
        WorkflowTriggerType.INCIDENT_TO_SCENARIO: {
            'target_module': 'scenario',
            'event_type': 'incident_lessons_available',
            'priority': 'medium',
            'description': 'Incident lessons → create scenarios'
        },
        WorkflowTriggerType.GOVERNANCE_TO_ALL: {
            'target_module': 'all',
            'event_type': 'governance_decision',
            'priority': 'critical',
            'description': 'Governance decision → broadcast to all'
        }
    }
    
    @classmethod
    def get_trigger(cls, trigger_type: WorkflowTriggerType) -> Dict[str, Any]:
        """Get trigger configuration"""
        return cls.TRIGGERS.get(trigger_type)
```

---

## 4. Memory Layer Synchronization ✅

### Что нашли (v1.0):

```python
def _synchronize_memory_layers(self):
    """Synchronize 3-layer memory system"""
    
    # Layer 1: PostgreSQL (immediate memory)
    layer1_status = self._check_postgresql_memory()
    
    # Layer 2: Redis (session memory)
    layer2_status = self._check_redis_memory()
    
    # Layer 3: Supabase (long-term memory)
    layer3_status = self._check_supabase_memory()
    
    return all([layer1_status, layer2_status, layer3_status])
```

### Как портировать в v2.0:

**Уже частично есть** в `ai-orchestration/memory/` но можно добавить sync logic!

---

## Итого: Что портируем

### ✅ Высокий приоритет (делаем сейчас):

1. **CollectiveCoordinator** - координация AI organs
   - Файл: `ai-orchestration/decision_center/collective_coordinator.py`
   - Из: `ai_organ_coordinator.py`

2. **AnthropicClient с tracking** - LLM клиент с мониторингом
   - Файл: `ai-office/llm/anthropic_client.py`
   - Из: `anthropic_integration.py`

3. **WorkflowTriggerRegistry** - cross-module triggers
   - Файл: `infrastructure/eventbus/workflow_triggers.py`
   - Из: `eventbus_integration.py`

### ⚠️ Средний приоритет (потом):

4. **Organism Personality Config** - конфигурационные профили
5. **Consciousness Level Metric** - platform health score
6. **Evolution Triggers** - auto-upgrade logic

### ❌ Низкий приоритет (опционально):

7. Dashboard metrics visualization
8. Odoo-specific UI patterns

---

**Хочешь чтобы я создал эти 3 модуля сейчас?** 🚀

1. CollectiveCoordinator
2. AnthropicClient (improved)
3. WorkflowTriggerRegistry

---

**Дата**: 2025-10-04  
**Статус**: Полезный код найден  
**Действие**: Портировать 3 ключевых модуля в v2.0
