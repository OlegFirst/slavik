# 🔄 BPMN Workflow - Полный Анализ

**Дата:** 5 октября 2025
**Местоположение:** `/intelligent-core/bpmn-workflow/`
**Размер:** 2 файла Python (main.py + mock_data.py), ~480 строк

---

## 🎯 Назначение

**BPMN Workflow Service** - координация и оркестрация бизнес-процессов на основе BPMN 2.0 стандарта.

**Port:** 8003
**Technology:** FastAPI + BPMN Engine + State Machine

---

## 📊 Что Такое BPMN?

**BPMN (Business Process Model and Notation)** - международный стандарт для моделирования бизнес-процессов.

### BPMN Elements:

```xml
<startEvent>        ← Начало процесса
<userTask>          ← Задача для пользователя
<serviceTask>       ← Автоматическая задача
<sequenceFlow>      ← Переход между задачами
<gateway>           ← Ветвление (if/else)
<endEvent>          ← Завершение процесса
```

### Пример BPMN Процесса:

```
START → Assess Impact → Activate Team → Execute Plan → Monitor → END
```

---

## 🏗️ Архитектура

### Core Components:

```python
1. BPMNEngine
   - deploy_process()      # Загрузить BPMN процесс
   - start_process()       # Запустить новый instance
   - complete_task()       # Завершить задачу
   - find_next_activities() # Найти следующие шаги

2. Data Models
   - BPMNProcess          # Определение процесса (BPMN XML)
   - ProcessInstance      # Конкретное выполнение процесса
   - Task                 # Отдельная задача в процессе
```

### Process Flow:

```
1. Deploy BPMN Process (XML)
   ↓
2. Start Process Instance
   ↓
3. Create Initial Tasks (from startEvent)
   ↓
4. User Completes Task
   ↓
5. Engine Finds Next Tasks (via sequenceFlow)
   ↓
6. Create Next Tasks
   ↓
7. Repeat 4-6 until endEvent
   ↓
8. Process Instance Completed
```

---

## 🔍 Бизнес-Логика

### 1. Deploy Process (Загрузка BPMN)

```python
async def deploy_process(process: BPMNProcess) -> str:
    """
    Загружает BPMN процесс в систему

    Input:
    {
        "name": "BCM Incident Response",
        "bpmn_xml": "<?xml version='1.0'?>...",
        "tenant_id": "tenant_001",
        "version": "1.0"
    }

    Logic:
    1. Validate BPMN XML (проверка структуры)
    2. Parse XML (убедиться что валидный BPMN)
    3. Store process definition
    4. Publish event: "bpmn.process.deployed"

    Output:
    {
        "process_id": "uuid-123",
        "status": "deployed"
    }
    """
```

**Валидация XML:**
```python
root = ET.fromstring(process.bpmn_xml)
if root.tag != "{http://www.omg.org/spec/BPMN/20100524/MODEL}definitions":
    raise ValueError("Invalid BPMN XML format")
```

---

### 2. Start Process (Запуск Instance)

```python
async def start_process(process_id, tenant_id, variables):
    """
    Запускает новый instance процесса

    Input:
    {
        "process_id": "proc_001",
        "tenant_id": "tenant_001",
        "variables": {
            "incident_id": 123,
            "severity": "high"
        }
    }

    Logic:
    1. Find process definition
    2. Create new ProcessInstance
    3. Parse BPMN XML
    4. Find <startEvent> elements
    5. Find tasks connected to startEvent (via <sequenceFlow>)
    6. Create initial tasks
    7. Publish event: "bpmn.instance.started"

    Output:
    {
        "instance_id": "uuid-456"
    }
    """
```

**Example BPMN Flow:**
```xml
<startEvent id="start_incident">
  <outgoing>seq_1</outgoing>  ← Reference to sequenceFlow
</startEvent>

<sequenceFlow id="seq_1"
              sourceRef="start_incident"
              targetRef="assess_impact"/>  ← Points to first task

<userTask id="assess_impact" name="Assess Impact">
  <incoming>seq_1</incoming>
  <outgoing>seq_2</outgoing>
</userTask>
```

**Engine Logic:**
```python
# 1. Find startEvent
start_events = root.findall(".//bpmn:startEvent", ns)

# 2. Find outgoing sequence flows
outgoing = start_events[0].findall("bpmn:outgoing", ns)  # → "seq_1"

# 3. Find sequence flow with id="seq_1"
seq_flow = root.find(f".//bpmn:sequenceFlow[@id='seq_1']", ns)

# 4. Get targetRef from sequence flow
target_ref = seq_flow.get("targetRef")  # → "assess_impact"

# 5. Find task with id="assess_impact"
target_task = root.find(f".//*[@id='assess_impact']", ns)

# 6. Create Task
create_task(instance_id, {
    "activity_id": "assess_impact",
    "name": "Assess Impact",
    "task_type": "USERTASK"
})
```

---

### 3. Complete Task (Завершение Задачи)

```python
async def complete_task(task_id, tenant_id, variables, completed_by):
    """
    Завершает задачу и двигает процесс дальше

    Input:
    {
        "task_id": "task_789",
        "variables": {
            "impact_level": "critical",
            "affected_systems": ["CRM", "ERP"]
        },
        "completed_by": "user_001"
    }

    Logic:
    1. Find task by task_id
    2. Verify tenant_id (security)
    3. Mark task as COMPLETED
    4. Update instance variables (merge with new variables)
    5. Find current BPMN element (activity_id)
    6. Find next activities (via sequenceFlow)
    7. IF next activities exist:
         - Create next tasks
       ELSE:
         - Mark instance as COMPLETED (reached endEvent)
    8. Publish event: "bpmn.task.completed"

    Output:
    {
        "status": "completed",
        "next_tasks": [...]
    }
    """
```

**Process Variables Flow:**
```python
# Task 1: Assess Impact
variables = {"impact_level": "critical"}

# Task 2: Activate Team (inherits variables from Task 1)
variables = {
    "impact_level": "critical",  # ← from Task 1
    "team_activated": true,      # ← new from Task 2
    "team_members": ["user1", "user2"]
}

# Task 3: Execute Plan (inherits all previous)
variables = {
    "impact_level": "critical",
    "team_activated": true,
    "team_members": ["user1", "user2"],
    "recovery_started_at": "2025-10-05T10:00:00"
}
```

---

### 4. Find Next Activities (Навигация по BPMN)

```python
async def find_next_activities(root, current_element, instance_id):
    """
    Находит следующие шаги процесса

    Logic:
    1. Find <outgoing> elements in current activity
    2. For each outgoing:
         a. Find <sequenceFlow> with matching id
         b. Get targetRef from sequenceFlow
         c. Find target activity by targetRef
         d. Extract activity details (id, name, type)
    3. Return list of next activities

    Example:
    Current: <userTask id="assess_impact">
               <outgoing>seq_2</outgoing>
             </userTask>

    Step 1: outgoing = "seq_2"
    Step 2: <sequenceFlow id="seq_2"
                          sourceRef="assess_impact"
                          targetRef="activate_team"/>
    Step 3: targetRef = "activate_team"
    Step 4: <userTask id="activate_team" name="Activate Response Team">

    Return:
    [
        {
            "activity_id": "activate_team",
            "name": "Activate Response Team",
            "task_type": "USERTASK"
        }
    ]
    """
```

---

## 📡 API Endpoints

### 1. Deploy Process
```http
POST /api/bpmn/processes
Content-Type: application/json

{
  "name": "BCM Incident Response",
  "description": "Standard incident response workflow",
  "bpmn_xml": "<?xml version='1.0' encoding='UTF-8'?>...",
  "tenant_id": "tenant_001",
  "version": "1.0"
}
```

**Response:**
```json
{
  "process_id": "proc_001",
  "status": "deployed"
}
```

---

### 2. Start Process Instance
```http
POST /api/bpmn/instances
Content-Type: application/json

{
  "process_id": "proc_001",
  "tenant_id": "tenant_001",
  "variables": {
    "incident_id": 123,
    "severity": "high",
    "incident_type": "data_breach"
  },
  "started_by": "user_001"
}
```

**Response:**
```json
{
  "instance_id": "inst_456",
  "status": "ACTIVE",
  "current_activities": ["assess_impact"]
}
```

---

### 3. Get Process Instance
```http
GET /api/bpmn/instances/inst_456?tenant_id=tenant_001
```

**Response:**
```json
{
  "id": "inst_456",
  "process_id": "proc_001",
  "status": "ACTIVE",
  "current_activities": ["assess_impact"],
  "variables": {
    "incident_id": 123,
    "severity": "high",
    "incident_type": "data_breach"
  },
  "started_by": "user_001",
  "started_at": "2025-10-05T10:00:00Z"
}
```

---

### 4. Get Tasks
```http
GET /api/bpmn/tasks?instance_id=inst_456&tenant_id=tenant_001
```

**Response:**
```json
{
  "tasks": [
    {
      "id": "task_789",
      "process_instance_id": "inst_456",
      "activity_id": "assess_impact",
      "name": "Assess Impact",
      "task_type": "USERTASK",
      "status": "ACTIVE",
      "assignee": null,
      "created_at": "2025-10-05T10:00:00Z"
    }
  ]
}
```

---

### 5. Complete Task
```http
POST /api/bpmn/tasks/task_789/complete
Content-Type: application/json

{
  "tenant_id": "tenant_001",
  "variables": {
    "impact_level": "critical",
    "affected_systems": ["CRM", "ERP"],
    "estimated_downtime": 240
  },
  "completed_by": "user_001"
}
```

**Response:**
```json
{
  "status": "completed",
  "next_activities": [
    {
      "activity_id": "activate_team",
      "name": "Activate Response Team",
      "task_type": "USERTASK"
    }
  ]
}
```

---

## 🔄 BCM Workflow Examples

### Example 1: Incident Response Workflow

**BPMN Diagram:**
```
START (Incident Detected)
  ↓
Assess Impact (userTask)
  ↓
Activate Response Team (userTask)
  ↓
Execute Recovery Plan (userTask)
  ↓
Monitor Recovery (userTask)
  ↓
END (Incident Resolved)
```

**Process Flow:**
```python
# 1. Deploy process
deploy_process({
    "name": "BCM Incident Response",
    "bpmn_xml": INCIDENT_RESPONSE_BPMN
})

# 2. Incident occurs → Start process
instance_id = start_process("proc_incident_response", {
    "incident_id": 123,
    "severity": "high",
    "affected_service": "Payment Processing"
})

# 3. Task 1: Assess Impact
task_1 = get_tasks(instance_id)[0]  # "Assess Impact"
complete_task(task_1.id, {
    "impact_level": "critical",
    "estimated_revenue_loss": 50000,
    "affected_customers": 1500
})

# 4. Task 2: Activate Team (auto-created after Task 1 completion)
task_2 = get_tasks(instance_id)[0]  # "Activate Response Team"
complete_task(task_2.id, {
    "team_activated": true,
    "team_lead": "john.doe",
    "team_members": ["alice", "bob", "charlie"]
})

# 5. Task 3: Execute Plan
task_3 = get_tasks(instance_id)[0]  # "Execute Recovery Plan"
complete_task(task_3.id, {
    "recovery_plan": "BC-PLAN-001",
    "recovery_started_at": "2025-10-05T10:30:00Z",
    "rto_target": 4  # hours
})

# 6. Task 4: Monitor Recovery
task_4 = get_tasks(instance_id)[0]  # "Monitor Recovery"
complete_task(task_4.id, {
    "service_restored": true,
    "actual_downtime": 3.5,  # hours
    "rto_met": true
})

# 7. Process completes (endEvent reached)
# instance.status = "COMPLETED"
```

---

### Example 2: BIA Review Workflow

```
START
  ↓
Gather Process Data (userTask)
  ↓
Analyze Dependencies (serviceTask - automatic)
  ↓
Calculate RTO/RPO (serviceTask - automatic)
  ↓
Review Results (userTask)
  ↓
Approve BIA (userTask)
  ↓
END
```

---

### Example 3: Plan Approval Workflow (with Gateway)

```
START
  ↓
Manager Review (userTask)
  ↓
[Gateway: Approved?]
  ├─ YES → Director Review (userTask)
  │         ↓
  │       [Gateway: Approved?]
  │         ├─ YES → Publish Plan → END
  │         └─ NO → Request Changes → Manager Review
  │
  └─ NO → Request Changes → Manager Review
```

---

## 🔗 Интеграция с Платформой

### Current Status: ⚠️ PARTIALLY INTEGRATED

**Проблема:** BPMN Service изолирован, не интегрирован с BCM сервисами

### Как Должно Быть:

**1. BIA Service Integration:**
```python
# bia-service/services/bia_service.py

import httpx

async def start_bia_workflow(bia_id: int):
    """Start BPMN workflow for BIA process"""

    # Start BPMN workflow
    async with httpx.AsyncClient() as client:
        response = await client.post(
            'http://bpmn-workflow:8003/api/bpmn/instances',
            json={
                'process_id': 'bia_review_process',
                'tenant_id': current_tenant_id,
                'variables': {
                    'bia_id': bia_id,
                    'organization_id': org_id,
                    'review_type': 'annual'
                }
            }
        )

        instance = response.json()
        return instance['instance_id']

async def complete_bia_step(instance_id, step_data):
    """Complete current step in BIA workflow"""

    # Get current task
    tasks = await get_workflow_tasks(instance_id)
    current_task = tasks[0]

    # Complete task
    await client.post(
        f'http://bpmn-workflow:8003/api/bpmn/tasks/{current_task.id}/complete',
        json={
            'tenant_id': current_tenant_id,
            'variables': step_data
        }
    )
```

**2. Incident Response Integration:**
```python
# response-service/services/incident_service.py

async def activate_incident_response(incident_id: int):
    """Activate BPMN incident response workflow"""

    instance_id = await bpmn_client.start_process(
        'incident_response_process',
        variables={
            'incident_id': incident_id,
            'severity': incident.severity,
            'incident_type': incident.type
        }
    )

    # Store instance_id with incident
    incident.workflow_instance_id = instance_id
    await db.commit()

    return instance_id
```

**3. EventBus Integration:**
```python
# BPMN Service already publishes events:
await publish_event("bpmn.instance.started", tenant_id, {...})
await publish_event("bpmn.task.completed", tenant_id, {...})
await publish_event("bpmn.instance.completed", tenant_id, {...})

# Other services can subscribe:
eventbus.subscribe("bpmn.task.completed", handle_workflow_step)
```

---

## 💡 Выводы

### ✅ Strengths:
1. **BPMN 2.0 Standard** - международный стандарт для процессов
2. **Clean Architecture** - BPMNEngine + Data Models
3. **Multi-tenancy** - tenant_id isolation
4. **EventBus Ready** - publishes workflow events
5. **Process Variables** - state передается между шагами
6. **Validation** - проверка BPMN XML

### ⚠️ Gaps:
1. **Not Integrated** - не используется BCM сервисами
2. **In-Memory Storage** - нет persistence (данные теряются при рестарте)
3. **Limited BPMN Support** - только базовые элементы (startEvent, userTask, endEvent)
4. **No Gateway Support** - нет if/else ветвления
5. **No Parallel Execution** - нет parallelGateway
6. **No Service Tasks** - нет автоматических задач
7. **No Timers** - нет scheduled tasks

### 🆚 vs Workflow Intelligence

| Аспект | BPMN Workflow | Workflow Intelligence |
|--------|---------------|----------------------|
| **Стандарт** | BPMN 2.0 (visual) | Custom State Machine |
| **Назначение** | Process orchestration | Workflow tracking + AI |
| **Визуализация** | ✅ BPMN diagrams | ❌ Code-based |
| **AI Integration** | ❌ Нет | ✅ Case Library + AI Advisor |
| **Persistence** | ⚠️ In-memory | ✅ PostgreSQL |
| **Status** | ⚠️ Not integrated | ✅ Integrated |

---

## 🎯 Рекомендации

### Вариант 1: Использовать BPMN для визуального моделирования

**Преимущество:** Визуальные BPMN диаграммы для бизнес-пользователей

**Интеграция:**
```
BPMN Workflow (визуальное моделирование)
  ↓ generates execution plan
Workflow Intelligence (выполнение + AI)
  ↓ tracks execution
Case Library (самообучение)
```

### Вариант 2: Заменить на Production BPMN Engine

**Использовать готовый BPMN engine:**
- **Camunda** - enterprise BPMN/DMN engine
- **Temporal** - workflow orchestration (Uber)
- **Prefect** - modern workflow engine

### Вариант 3 (РЕКОМЕНДАЦИЯ): Архивировать

**Почему:**
- ❌ Workflow Intelligence уже есть и работает
- ❌ BPMN Service не интегрирован
- ❌ In-memory storage (не production-ready)
- ❌ Limited BPMN support
- ✅ Workflow Intelligence покрывает те же use cases

**Место в архитектуре:**
```
_archive/bpmn-workflow/  ← Архивировать
```

**Если понадобится визуальное моделирование позже:**
- Использовать Camunda BPMN Engine
- Или интегрировать BPMN.io (только визуализация)

---

## ❓ Решение

**Что делать с BPMN Workflow:**

1. **Архивировать** в `_archive/` (у нас есть Workflow Intelligence) ✅
2. **Интегрировать** с BCM сервисами (много работы, дублирует WF Intelligence) ⚠️
3. **Заменить** на Camunda/Temporal (если нужен визуальный BPMN) 🔄

**МОЯ РЕКОМЕНДАЦИЯ:** Вариант 1 - Архивировать

**Почему:**
- Workflow Intelligence уже реализован и интегрирован
- BPMN визуализация - не критична для MVP
- Можно добавить позже если нужно

Согласен? 😊
