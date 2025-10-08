# Import Migration Guide - Workflow Intelligence

**Дата**: 2025-10-06
**Цель**: Исправить импорты согласно V7 Architecture
**Статус**: 🚧 В процессе

---

## 🎯 Проблема

Текущие импорты в `workflow_intelligence/` не соответствуют V7 архитектуре:

**V7 Architecture (правильная)**:
```
intelligent-core/
├── ai-foundation/           # ✅ Shared AI Infrastructure (RAG, ML, Learning)
├── workflow_intelligence/   # ✅ THE BRAIN (Workflow Engine)
└── shared/                  # ✅ Common libraries (eventbus, database, cache, auth)
```

**Dependency Flow (правильный)**:
```
workflow_intelligence → ai-foundation (для RAG, ML, Learning, Context, LLM)
workflow_intelligence → shared (для eventbus, database, cache, auth)
```

---

## 🔍 Найденные Проблемы

### 1. ❌ WRONG: Импорт из infrastructure/

**Файл**: `integration/eventbus_publisher.py` (lines 25-26)

```python
# ❌ WRONG (текущий):
from infrastructure.eventbus import Event, EventPriority
from infrastructure.eventbus.factory import create_eventbus
```

**Проблема**:
- `infrastructure/` это ОТДЕЛЬНЫЙ слой в проекте (deployment, monitoring, etc)
- EventBus лежит в `shared/eventbus/` для использования всеми модулями

**✅ CORRECT (должно быть)**:
```python
from shared.eventbus import EventBus
from shared.eventbus.publisher import publish_event
from shared.eventbus.client import EventBusClient
```

---

### 2. ⚠️ MISSING: Нет использования ai-foundation

**Проблема**:
- `ai-foundation/` уже создан и готов
- Но `workflow_intelligence/` его не использует
- Нужно добавить импорты для RAG, ML, Learning, Context

**Где добавить**:

**a) integration/ai_context_builder.py**
```python
# ✅ ДОБАВИТЬ:
from ai_foundation.context import ContextBuilder
from ai_foundation.rag import RAGPipeline

# Использовать для построения контекста с RAG
```

**b) workflows/bia_workflow.py** (если есть AI логика)
```python
# ✅ ДОБАВИТЬ:
from ai_foundation.rag import RAGPipeline
from ai_foundation.learning import SelfLearningEngine

# Использовать для анализа процессов
```

**c) integration/legacy_anthropic_client.py**
```python
# ✅ ДОБАВИТЬ:
from ai_foundation.llm import LLMRouter

# Заменить прямой вызов Anthropic на LLMRouter
```

---

## 📋 План Исправления

### Phase 1: Исправить существующие импорты (30 минут)

#### Задача 1.1: Исправить eventbus_publisher.py

**Файл**: `integration/eventbus_publisher.py`

**Изменения**:

```python
# ДО (lines 24-26):
try:
    from infrastructure.eventbus import Event, EventPriority
    from infrastructure.eventbus.factory import create_eventbus
except ImportError:
    # Fallback for development
    ...

# ПОСЛЕ:
import sys
from pathlib import Path

# Add shared to path
shared_path = Path(__file__).parent.parent.parent.parent / 'shared'
sys.path.insert(0, str(shared_path))

try:
    from shared.eventbus.client import EventBusClient
    from shared.eventbus.publisher import publish_event
except ImportError:
    # Fallback for development
    class EventBusClient:
        async def publish(self, topic, data):
            print(f"[MOCK EventBus] {topic}: {data}")

    async def publish_event(topic, data, priority='normal'):
        print(f"[MOCK EventBus] {topic}: {data}")
```

**Обновить методы класса**:

```python
class WorkflowEventPublisher:
    def __init__(self, eventbus_client=None):
        """
        Args:
            eventbus_client: EventBusClient from shared/eventbus/
        """
        self.eventbus = eventbus_client

    async def publish_state_changed(
        self,
        workflow_id: str,
        from_state: str,
        to_state: str,
        context: Dict[str, Any],
        tenant_id: str
    ):
        """Publish state transition event"""

        if self.eventbus:
            await publish_event(
                topic='workflow.state_changed',
                data={
                    'workflow_id': workflow_id,
                    'from_state': from_state,
                    'to_state': to_state,
                    'context': context,
                    'tenant_id': tenant_id,
                    'module': context.get('module', 'unknown')
                },
                priority='normal'
            )
```

---

#### Задача 1.2: Обновить ai_context_builder.py

**Файл**: `integration/ai_context_builder.py`

**Добавить импорты** (после line 26):

```python
from typing import Dict, Any, List, Optional

# ✅ ДОБАВИТЬ:
import sys
from pathlib import Path

# Add ai-foundation to path
ai_foundation_path = Path(__file__).parent.parent.parent / 'ai-foundation'
sys.path.insert(0, str(ai_foundation_path))

from ai_foundation.context import ContextBuilder
from ai_foundation.rag import RAGPipeline
```

**Обновить класс** (использовать ai-foundation):

```python
class AIContextBuilder:
    """
    Построитель контекста для AI Advisor

    Uses ai-foundation/context for building rich context
    """

    def __init__(
        self,
        workflow_engine,  # StateMachine
        case_repository,  # CaseRepository
        rag_pipeline: Optional[RAGPipeline] = None  # ✅ ДОБАВИТЬ
    ):
        self.workflow = workflow_engine
        self.cases = case_repository
        self.rag = rag_pipeline or RAGPipeline()  # ✅ ДОБАВИТЬ

        # Use ai-foundation ContextBuilder
        self.context_builder = ContextBuilder()  # ✅ ДОБАВИТЬ

    async def build_full_context(
        self,
        org_context: Dict[str, Any],
        user_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """Построить полный контекст для AI"""

        # 1. Use ai-foundation ContextBuilder
        base_context = await self.context_builder.build_context(
            workflow_state=self.workflow.get_context(),
            org_context=org_context
        )

        # 2. Enrich with case library data
        similar_cases = await self.cases.find_similar_cases(...)

        # 3. Use RAG for retrieving relevant knowledge
        if self.rag:
            relevant_knowledge = await self.rag.retrieve(
                query=user_message or f"Best practices for {org_context['industry']}",
                top_k=5
            )
            base_context['knowledge_base'] = relevant_knowledge

        return base_context
```

---

#### Задача 1.3: Обновить legacy_anthropic_client.py

**Файл**: `integration/legacy_anthropic_client.py`

**Добавить импорты** (после line 12):

```python
import os
from typing import Dict, Any, Optional

# ✅ ДОБАВИТЬ:
import sys
from pathlib import Path

# Add ai-foundation to path
ai_foundation_path = Path(__file__).parent.parent.parent / 'ai-foundation'
sys.path.insert(0, str(ai_foundation_path))

from ai_foundation.llm import LLMRouter
```

**Обновить класс** (использовать LLMRouter):

```python
class AnthropicGovernanceBrain:
    """Anthropic Claude integration for governance intelligence"""

    def __init__(self):
        # ✅ USE LLMRouter instead of direct Anthropic client
        self.llm_router = LLMRouter()

        # Keep legacy API key for backward compatibility
        self.api_key = os.getenv('ANTHROPIC_API_KEY')

        if not self.api_key:
            logger.warning('Anthropic API key not configured - using fallback local AI')

    async def governance_analysis(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Strategic governance analysis via LLMRouter"""

        try:
            # ✅ Use LLMRouter (supports multiple providers)
            result = await self.llm_router.generate(
                prompt=self._build_governance_prompt(prompt, context),
                model='claude-3-sonnet-20240229',
                temperature=0.3,
                max_tokens=4000
            )

            return {
                'analysis': result['text'],
                'confidence': 0.95,
                'reasoning': 'LLMRouter strategic governance analysis',
                'model_used': result['model'],
                'tokens_used': result.get('usage', {}).get('output_tokens', 0)
            }

        except Exception as e:
            logger.error(f'LLMRouter governance analysis failed: {e}')
            return await self._fallback_local_analysis(prompt, context)
```

---

### Phase 2: Добавить импорты shared/ (30 минут)

#### Задача 2.1: Добавить database imports

**Где нужно**:
- `case_library/repository.py` (уже использует SQLAlchemy, проверить что используется shared/database)
- `storage/postgres_adapter.py` (проверить что используется shared/database)

**Проверить**:
```python
# ✅ ДОЛЖНО БЫТЬ:
from shared.database import get_session, DatabaseManager
from shared.cache import CacheManager
```

#### Задача 2.2: Добавить auth imports

**Где нужно**:
- `auth/middleware.py` (проверить что используется shared/auth)
- `auth/decorators.py` (проверить что используется shared/auth)

**Проверить**:
```python
# ✅ ДОЛЖНО БЫТЬ:
from shared.auth import AuthContext, PermissionSet
from shared.auth.jwt import verify_token
```

---

### Phase 3: Обновить __init__.py (15 минут)

#### Задача 3.1: Обновить workflow_intelligence/__init__.py

**Добавить экспорты для ai-foundation и shared**:

```python
"""
Workflow Intelligence - THE BRAIN

Workflow engine with managed autonomy.

Dependencies:
- ai-foundation: RAG, ML, Learning, Context, LLM
- shared: eventbus, database, cache, auth
"""

__version__ = "5.0.0"

# Core Workflow Engine
from .core.workflow_engine import (
    WorkflowEngine,
    WorkflowState,
    WorkflowTransition,
)

from .core.state_machine import StateMachine

# Case Library
from .case_library.models import (
    WorkflowCase,
    OrganizationContext,
    WorkflowStepRecord,
    WorkflowMetrics,
)

from .case_library.collector import CaseCollector
from .case_library.repository import CaseRepository

# Integration Layer
from .integration.eventbus_publisher import WorkflowEventPublisher
from .integration.ai_context_builder import AIContextBuilder
from .integration.bia_adapter import BIAWorkflowAdapter

# Storage
from .storage import PostgresStorageAdapter, StorageAdapter

# Auth
from .auth import (
    require_workflow_permission,
    require_tenant,
    WorkflowPermissions,
)

__all__ = [
    # Core
    "WorkflowEngine",
    "WorkflowState",
    "WorkflowTransition",
    "StateMachine",
    # Case Library
    "WorkflowCase",
    "OrganizationContext",
    "WorkflowStepRecord",
    "WorkflowMetrics",
    "CaseCollector",
    "CaseRepository",
    # Integration
    "WorkflowEventPublisher",
    "AIContextBuilder",
    "BIAWorkflowAdapter",
    # Storage
    "PostgresStorageAdapter",
    "StorageAdapter",
    # Auth
    "require_workflow_permission",
    "require_tenant",
    "WorkflowPermissions",
]
```

---

## ✅ Checklist

### Перед началом:
- [x] ai-foundation/ создан и проверен (✅ DONE)
- [x] shared/ существует (✅ DONE)
- [ ] Сделать git commit текущего состояния
- [ ] Создать ветку `feature/fix-workflow-intelligence-imports`

### Phase 1: Исправить eventbus
- [ ] Обновить integration/eventbus_publisher.py
- [ ] Протестировать WorkflowEventPublisher
- [ ] Обновить integration/bia_adapter.py (если есть eventbus)

### Phase 2: Добавить ai-foundation
- [ ] Обновить integration/ai_context_builder.py
- [ ] Обновить integration/legacy_anthropic_client.py
- [ ] Протестировать интеграцию с ai-foundation

### Phase 3: Проверить shared
- [ ] Проверить database imports
- [ ] Проверить auth imports
- [ ] Проверить cache imports

### Phase 4: Обновить __init__.py
- [ ] Добавить экспорты integration layer
- [ ] Проверить все импорты работают

### Phase 5: Тестирование
- [ ] Запустить тесты workflow_intelligence
- [ ] Проверить интеграцию с ai-foundation
- [ ] Проверить интеграцию с shared/eventbus

---

## 🚀 Следующий шаг

**ПОСЛЕ исправления импортов** можно будет:
1. Обернуть workflow_intelligence в Temporal workflows
2. Добавить интеграцию с expertise-center
3. Развернуть все вместе

**НО СНАЧАЛА** - нужно исправить фундамент (импорты).

---

## 📊 Измеримый результат

**ДО (текущее состояние)**:
```
workflow_intelligence/
  ├── integration/
  │   ├── eventbus_publisher.py  ❌ infrastructure.eventbus
  │   ├── ai_context_builder.py  ⚠️ нет ai-foundation
  │   └── legacy_anthropic_client.py  ⚠️ прямой вызов Anthropic
```

**ПОСЛЕ (целевое состояние)**:
```
workflow_intelligence/
  ├── integration/
  │   ├── eventbus_publisher.py  ✅ shared.eventbus
  │   ├── ai_context_builder.py  ✅ ai_foundation.context + rag
  │   └── legacy_anthropic_client.py  ✅ ai_foundation.llm
```

**Метрики успеха**:
- ✅ Все импорты используют правильные пути (ai-foundation, shared)
- ✅ Нет импортов из infrastructure (кроме infrastructure-специфичных сервисов)
- ✅ Все тесты проходят
- ✅ Можно легко обернуть в Temporal (следующий шаг)
