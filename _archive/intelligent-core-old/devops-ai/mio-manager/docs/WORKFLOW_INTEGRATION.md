# 🔄 Workflow Intelligence Integration

**Дата:** 2025-10-03
**Статус:** ✅ Интегрировано

---

## 🎯 Что это?

MIO Manager теперь интегрирован с:
1. **Workflow Intelligence Engine** - State Machine + AI Advisor + Case Library
2. **AI Workflow Optimizer** - ML-модели для предсказаний

Это означает, что MIO Manager больше не просто обнаруживает проблемы, а **автоматически реагирует** на них с использованием AI и ML.

---

## 🏗️ Архитектура

```
┌───────────────────────────────────────────────────────────────┐
│                    MIO MANAGER (Port 8046)                    │
│                  Управляющий центр платформы                  │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│  1. Automation Toolkit обнаруживает проблему                 │
│     ↓                                                         │
│  2. Automated Response Engine создаёт воркфлоу               │
│     ↓                                                         │
│  3. Workflow Intelligence: AI рекомендации                   │
│     ↓                                                         │
│  4. Workflow Optimizer: ML предсказания                      │
│     ↓                                                         │
│  5. Автоматическая реакция (managed autonomy)                │
│     ↓                                                         │
│  6. Делегирование Orchestrator (если нужно)                  │
│     ↓                                                         │
│  7. Мониторинг progress + сохранение в БД                    │
│     ↓                                                         │
│  8. После успеха → сохранение case для обучения              │
│                                                               │
└───────────────────────────────────────────────────────────────┘
         │                      │                      │
         ▼                      ▼                      ▼
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│   WORKFLOW       │  │   AI WORKFLOW    │  │   AI             │
│   INTELLIGENCE   │  │   OPTIMIZER      │  │   ORCHESTRATOR   │
│                  │  │                  │  │                  │
│ Port 8050        │  │ Port 8051        │  │ Port 8001        │
│                  │  │                  │  │                  │
│ - State Machine  │  │ - ML Predictor   │  │ - Task           │
│ - AI Advisor     │  │ - Anomaly Detect │  │   Delegation     │
│ - Case Library   │  │ - Bottleneck     │  │ - AI Agents      │
│ - ML Predictor   │  │   Analysis       │  │                  │
│ - Governance     │  │ - Resource       │  │                  │
│                  │  │   Optimization   │  │                  │
└──────────────────┘  └──────────────────┘  └──────────────────┘
```

---

## 📦 Новые компоненты

### 1. WorkflowIntelligenceClient
**Файл:** `integrations/workflow_intelligence_client.py`

**Методы:**
- `create_incident_workflow()` - Создать workflow для инцидента
- `transition_workflow()` - Переместить workflow в следующее состояние
- `get_ai_recommendations()` - Получить AI рекомендации
- `save_successful_case()` - Сохранить case для обучения
- `find_similar_cases()` - Найти похожие cases
- `predict_resolution_time()` - Предсказать время на исправление
- `check_governance_rules()` - Проверить против правил

### 2. WorkflowOptimizerClient
**Файл:** `integrations/workflow_optimizer_client.py`

**Методы:**
- `predict_execution_time()` - Предсказать время выполнения
- `detect_anomalies()` - Обнаружить anomalies
- `analyze_bottlenecks()` - Анализ узких мест
- `optimize_resources()` - Оптимизация ресурсов
- `predict_success_probability()` - Вероятность успеха
- `record_execution()` - Записать выполнение для ML

### 3. AutomatedResponseEngine
**Файл:** `workflows/automated_response_engine.py`

**Воркфлоу реакций:**
- `handle_security_incident()` - Security проблемы
- `handle_service_down()` - Падение сервиса
- И другие...

---

## 🔄 Workflow Example: Security Incident

### Сценарий: Bandit находит 5 HIGH security issues

**Шаг 1: Обнаружение**
```python
# Automation Toolkit запускает security scan
scan_result = await toolkit_manager.run_security_scan()
# {
#   'high_severity': 5,
#   'high_issues': [...]
# }
```

**Шаг 2: Автоматическая реакция**
```python
# AutomationToolkitManager вызывает response engine
response = await response_engine.handle_security_incident(
    scan_result=scan_result,
    report_id=report_id
)
```

**Шаг 3: Создание Workflow** (Workflow Intelligence)
```python
# Создаётся incident workflow
workflow = await wf_intelligence.create_incident_workflow(
    incident_type="security",
    incident_data=scan_result,
    severity="high"
)
# workflow_id: "wf-sec-123"
# current_state: "detected"
```

**Шаг 4: Поиск похожих cases**
```python
# Ищем похожие успешные cases
similar_cases = await wf_intelligence.find_similar_cases(
    incident_type="security",
    incident_data=scan_result,
    limit=3
)
# Найдено 2 похожих case где проблема была решена
```

**Шаг 5: AI рекомендации**
```python
# Получаем AI рекомендации
ai_recommendations = await wf_intelligence.get_ai_recommendations(
    workflow_id="wf-sec-123",
    current_context={...}
)
# [
#   {
#     'recommendation': 'Apply SQL injection protection',
#     'confidence': 0.92,
#     'based_on_case': 'case-456'
#   }
# ]
```

**Шаг 6: ML предсказание**
```python
# Предсказываем время на исправление
prediction = await wf_optimizer.predict_execution_time(
    process_type="security_fix",
    process_data={...}
)
# predicted_minutes: 45
# confidence: 0.87
```

**Шаг 7: Issue Tracking**
```python
# Создаём issues в БД
for issue in scan_result['high_issues']:
    issue_id = ActionsRepository.create_issue(
        issue_type="security",
        severity=IssueSeverity.HIGH,
        description=issue['issue_text'],
        discovered_by_report_id=report_id
    )
```

**Шаг 8: Автоматическое действие**

Если **severity = CRITICAL**:
- Enable Circuit Breaker для affected services
- Create emergency task → Orchestrator
- Priority: CRITICAL

Если **severity = HIGH/MEDIUM**:
- Create task с AI рекомендациями
- Delegate to Orchestrator
- Priority: HIGH/MEDIUM

```python
# HIGH severity → создаём задачу
task = await orchestrator.delegate_task({
    "task_type": "security_fix",
    "priority": "high",
    "workflow_id": "wf-sec-123",
    "details": {
        "high_severity_count": 5,
        "ai_recommendations": ai_recommendations[:5],
        "high_issues": scan_result['high_issues']
    }
})
```

**Шаг 9: Transition Workflow**
```python
# Переводим workflow в следующее состояние
await wf_intelligence.transition_workflow(
    workflow_id="wf-sec-123",
    to_state="task_created",
    action_data={"task_id": task['task_id']}
)
```

**Шаг 10: Мониторинг**
```python
# MIO Manager периодически проверяет статус
status = await wf_intelligence.get_workflow_status("wf-sec-123")
# {
#   'current_state': 'in_progress',
#   'assigned_to': 'ai_agent_security_123'
# }
```

**Шаг 11: После успеха**
```python
# Сохраняем successful case
await wf_intelligence.save_successful_case(
    workflow_id="wf-sec-123",
    incident_type="security",
    resolution_data={
        "actions_taken": [...],
        "time_to_resolve_minutes": 42
    },
    outcome_metrics={
        "success": True,
        "high_issues_fixed": 5
    }
)
# Этот case будет использоваться для:
# - Обучения ML моделей
# - Рекомендаций в похожих ситуациях
```

---

## 🎯 Типы воркфлоу

### 1. Security Incident Workflow

**States:**
```
detected → analyzing → task_created → delegated →
in_progress → resolved → closed
```

**Severity-based actions:**
- **CRITICAL** (≥5 HIGH issues):
  - Enable Circuit Breaker
  - Emergency task → Orchestrator
  - Immediate alert

- **HIGH** (3-4 HIGH issues):
  - Create task with AI recommendations
  - Delegate to Orchestrator
  - Monitor progress

- **MEDIUM** (1-2 HIGH issues):
  - Create task
  - Normal priority delegation

- **LOW** (0 HIGH issues):
  - Log only

### 2. Service Down Workflow

**States:**
```
detected → root_cause_analysis → restart_attempted →
escalated → in_progress → resolved → closed
```

**Actions:**
1. Root cause analysis (dependency graph)
2. Automatic restart attempt
3. Enable Circuit Breaker
4. Delegate to Orchestrator if restart failed

### 3. High Complexity Workflow

**States:**
```
detected → analyzing → recommendation_created →
refactoring_planned → in_progress → resolved
```

**Actions:**
1. Identify high complexity functions
2. AI recommendations for refactoring
3. Create refactoring task
4. Optional: delegate to Orchestrator

### 4. Circular Dependency Workflow

**States:**
```
detected → analyzing → solution_proposed →
refactoring → testing → resolved
```

**Actions:**
1. Analyze circular dependencies
2. Find similar resolved cases
3. AI recommendations
4. Create refactoring task

---

## 📊 Что записывается в БД

### MIO Actions
```python
{
    "action_id": "act-123",
    "action_type": "alert_sent",
    "target_service": "security",
    "status": "completed",
    "action_details": {
        "workflow_id": "wf-sec-123",
        "high_severity_count": 5,
        "ai_recommendations": [...]
    },
    "success": True
}
```

### Task Delegations
```python
{
    "task_id": "task-456",
    "task_type": "security_fix",
    "priority": "high",
    "task_details": {...},
    "status": "pending",
    "mio_action_id": "act-123"
}
```

### Issue Tracking
```python
{
    "issue_id": "issue-789",
    "issue_type": "security",
    "severity": "high",
    "description": "SQL injection vulnerability",
    "status": "open",
    "discovered_by_report_id": "report-123",
    "resolved_by_action_id": null  # Заполнится после исправления
}
```

---

## 🚀 Как запустить

### 1. Запустить все сервисы

```bash
# Workflow Intelligence
cd /Users/MD/AI-Platform-ISO/intelligent-core/workflow-intelligence
python3 main.py  # Port 8050

# AI Workflow Optimizer
cd /Users/MD/AI-Platform-ISO/intelligent-core/ai_workflow_optimizer
python3 main.py  # Port 8051

# MIO Manager
cd /Users/MD/AI-Platform-ISO/intelligent-core/mio-manager
python3 main.py  # Port 8046
```

### 2. MIO Manager автоматически подключится

При обнаружении проблемы MIO Manager:
1. ✅ Создаст workflow в Workflow Intelligence
2. ✅ Получит AI рекомендации
3. ✅ Получит ML предсказания
4. ✅ Выполнит автоматическую реакцию
5. ✅ Сохранит всё в БД

---

## ⚙️ Конфигурация

**Файл:** `config.py`

```python
# Workflow Intelligence
WORKFLOW_INTELLIGENCE_URL = "http://localhost:8050"

# AI Workflow Optimizer
WORKFLOW_OPTIMIZER_URL = "http://localhost:8051"

# Orchestrator
ORCHESTRATOR_URL = "http://localhost:8001"

# Gateway
GATEWAY_URL = "http://localhost:8000"
```

---

## 📈 Managed Autonomy

MIO Manager использует **Managed Autonomy** из Workflow Intelligence:

### Что может делать автоматически:
✅ Создавать workflows
✅ Получать AI рекомендации
✅ Логировать в БД
✅ Создавать задачи (LOW/MEDIUM priority)
✅ Отправлять alerts

### Что требует проверки через Governance:
⚠️  Enable Circuit Breaker (проверка правил)
⚠️  Emergency tasks (CRITICAL priority)
⚠️  Restart сервисов

### Что делегируется Orchestrator:
🤝 Исправление security issues
🤝 Refactoring кода
🤝 Исправление circular dependencies

---

## ✅ Что интегрировано

| Компонент | Статус | Функция |
|-----------|--------|---------|
| **WorkflowIntelligenceClient** | ✅ | Создание workflows, AI рекомендации |
| **WorkflowOptimizerClient** | ✅ | ML предсказания, anomaly detection |
| **AutomatedResponseEngine** | ✅ | Автоматические реакции на проблемы |
| **Security Incident Workflow** | ✅ | Полный workflow для security issues |
| **Service Down Workflow** | 🚧 | В процессе (базовая структура готова) |
| **Database Integration** | ✅ | Все actions/tasks/issues сохраняются |
| **Case Learning** | ✅ | Успешные cases сохраняются для ML |

---

## 🎉 Результат

MIO Manager теперь:

✅ **Обнаруживает** проблемы (Automation Toolkit)
✅ **Создаёт workflows** (Workflow Intelligence)
✅ **Получает AI рекомендации** (AI Advisor + Case Library)
✅ **Предсказывает** время и вероятность успеха (ML)
✅ **Автоматически реагирует** (Managed Autonomy)
✅ **Делегирует** задачи (Orchestrator)
✅ **Учится** на опыте (Case Library)
✅ **Сохраняет** всё в БД (Full persistence)

**Это полноценная интеллектуальная система с самообучением!** 🧠
