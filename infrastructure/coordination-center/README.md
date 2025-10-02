# Coordination Center - Руки для мозгов

## Concept

Coordination Center - это **посредник между Intelligent Core (мозги) и Execution Engine (инструменты)**.

### Проблема:
AI не должен напрямую вызывать API endpoints потому что:
- Tight coupling между AI и бизнес-логикой
- AI должен знать все API endpoints
- Невозможно отменить/откатить решения AI
- Сложность аудита и контроля

### Решение:
```
Intelligent Core → Intent/Command → Coordination Center → API Calls → Execution Engine
                                    (трансляция, валидация,
                                     безопасность, трекинг)
```

## Components

### 1. Command Interpreter
**Задача:** Получает Intent от AI и транслирует в конкретные API calls

```python
# AI отправляет высокоуровневую команду
intent = {
    "type": "create_bia",
    "params": {"org_id": 123, "scope": "IT"},
    "reasoning": "High risk detected, need impact analysis"
}

# Command Interpreter транслирует в API calls
commands = [
    {
        "service": "bia",
        "endpoint": "/api/bia/processes",
        "method": "POST",
        "params": {
            "organization_id": 123,
            "process_name": "IT Infrastructure",
            "scope": "IT",
            "created_by": "ai-agent"
        }
    }
]
```

### 2. Tool Registry
**Задача:** Каталог всех доступных инструментов для AI

```python
tools = {
    "create_bia_process": {
        "service": "bia",
        "endpoint": "/api/bia/processes",
        "method": "POST",
        "requires_approval": False,
        "timeout": 30,
        "retry": 3
    },
    "activate_incident_plan": {
        "service": "response",
        "endpoint": "/api/incidents/{id}/activate",
        "method": "POST",
        "requires_approval": True,  # Human approval needed
        "timeout": 60,
        "retry": 1
    },
    # ... all tools
}
```

### 3. Execution Tracker
**Задача:** Отслеживает статус выполнения команд

```python
execution = {
    "id": "exec-123",
    "intent_id": "intent-456",
    "status": "in_progress",  # pending, in_progress, completed, failed
    "steps": [
        {
            "tool": "create_bia_process",
            "status": "completed",
            "result": {"id": "bia-789"},
            "timestamp": "2025-10-02T12:00:00Z"
        },
        {
            "tool": "notify_stakeholders",
            "status": "in_progress",
            "timestamp": "2025-10-02T12:00:05Z"
        }
    ],
    "can_rollback": True
}
```

### 4. Security Layer
**Задача:** Контроль безопасности AI действий

- Проверка прав AI на действие
- Rate limiting (AI не может спамить)
- Human-in-the-loop для критичных операций
- Audit log всех AI решений

```python
class SecurityLayer:
    async def validate_intent(self, intent: Intent, ai_agent: Agent):
        # 1. Check AI permissions
        if not ai_agent.has_permission(intent.type):
            raise PermissionDenied("AI agent not allowed for this action")

        # 2. Check rate limits
        if await self.is_rate_limited(ai_agent.id):
            raise RateLimitExceeded("AI agent exceeded rate limit")

        # 3. Check if requires human approval
        if intent.is_critical:
            approval = await self.get_human_approval(intent)
            if not approval:
                raise ApprovalRequired("Human approval needed")

        # 4. Audit log
        await self.audit_log.record(ai_agent.id, intent)

        return True
```

## API

### Execute Intent

```python
POST /coordination/execute

{
    "intent": {
        "type": "create_bia",
        "params": {...},
        "reasoning": "High risk detected",
        "priority": "high",
        "requires_approval": false
    },
    "ai_agent_id": "ai-001"
}

Response:
{
    "execution_id": "exec-123",
    "status": "in_progress",
    "estimated_time": 30,
    "tracking_url": "/coordination/executions/exec-123"
}
```

### Get Execution Status

```python
GET /coordination/executions/{execution_id}

Response:
{
    "id": "exec-123",
    "status": "completed",
    "steps": [...],
    "results": {...},
    "duration": 25.3
}
```

### Rollback Execution

```python
POST /coordination/executions/{execution_id}/rollback

Response:
{
    "status": "rolled_back",
    "reverted_steps": [...]
}
```

## Implementation Plan

1. **Command Interpreter** (2-3 hours)
   - Intent parser
   - Command translator
   - Parameter enrichment

2. **Tool Registry** (1-2 hours)
   - Tool definitions
   - Dynamic tool loading
   - Tool validation

3. **Execution Tracker** (2-3 hours)
   - Execution state management
   - Step tracking
   - Rollback mechanism

4. **Security Layer** (2-3 hours)
   - Permission system
   - Rate limiting
   - Approval workflow
   - Audit logging

**Total:** 8-11 hours
