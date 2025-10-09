# Phase 1.1: Governance Layer - Quick Start 🚀

**Статус:** ✅ Реализовано и готово к интеграции
**Время до работы:** ~30 минут

---

## 🎯 Что Это Дает

**До Phase 1.1:**
- Auto-Recovery мог работать бесконечно ❌
- Цели hardcoded в коде ❌
- Нет escalation ❌
- Минимальный audit ❌

**После Phase 1.1:**
- Auto-Recovery **останавливается** после max attempts ✅
- Политики в **YAML** (легко менять) ✅
- **Escalation** с уведомлениями ✅
- **ISO 22301** compliant audit ✅

---

## ⚡ Быстрый Старт (3 команды)

### 1. Проверить Установку

```bash
cd /Users/MD/AI-Platform-ISO/infrastructure/decision-center

# Проверить что файлы есть
ls -la
# Должны увидеть:
# decision_center.py
# policy_engine.py
# policies.yaml
# escalation_manager.py
# notification_service.py
```

### 2. Запустить Пример

```bash
# Установить зависимости (если нужно)
pip3 install pydantic pyyaml aiofiles

# Запустить пример
python3 EXAMPLE_USAGE.py
```

**Ожидаемый вывод:**
```
=== Example 1: Basic Decision ===
Decision: APPROVED
Can proceed: True
Reasoning: Service: database, Attempt: 1/2...

=== Example 2: Escalation ===
Escalation created: esc_xxx
Service blocked: True

=== Example 3: Policy Query ===
Database RTO: 120 seconds
Max attempts: 2
```

### 3. Посмотреть Audit Logs

```bash
# Логи создаются автоматически
ls -la audit_logs/
cat audit_logs/audit_$(date +%Y-%m-%d).jsonl | jq .
```

---

## 🔧 Интеграция с Auto-Recovery

### Шаг 1: Импорт

Добавить в начало `auto_recovery.py`:

```python
from infrastructure.decision_center import (
    InfrastructureDecisionCenter,
    EscalationManager,
    NotificationService
)
```

### Шаг 2: Инициализация

В `__init__()` класса AutoRecovery:

```python
def __init__(self, eventbus, decision_center=None, escalation_manager=None):
    self.eventbus = eventbus
    self.decision_center = decision_center
    self.escalation_manager = escalation_manager
    # ... остальное
```

### Шаг 3: Проверка Перед Recovery

В методе `_execute_recovery()`, перед попыткой recovery:

```python
async def _execute_recovery(self, strategy: RecoveryStrategy) -> bool:

    # НОВОЕ: Проверка с Decision Center
    if self.decision_center:
        decision, can_proceed = await self.decision_center.decide_recovery_action(
            service_name=strategy.service_name,
            action_type=strategy.strategy_type,
            current_attempt=attempt
        )

        if not can_proceed:
            logger.warning(f"Recovery blocked by Decision Center: {decision.reasoning}")
            return False

    # Существующая логика recovery
    for attempt in range(1, strategy.max_attempts + 1):
        # ...
```

### Шаг 4: Обновить Infrastructure Coordinator

В `infrastructure_coordinator.py`:

```python
async def start(self):
    # Создать Decision Center
    self.decision_center = InfrastructureDecisionCenter(
        eventbus=self.eventbus
    )

    # Создать Escalation Manager
    self.notification_service = NotificationService(eventbus=self.eventbus)
    self.escalation_manager = EscalationManager(
        eventbus=self.eventbus,
        notification_service=self.notification_service
    )

    # Передать в Auto-Recovery
    self.auto_recovery = AutoRecovery(
        eventbus=self.eventbus,
        decision_center=self.decision_center,
        escalation_manager=self.escalation_manager
    )

    # Остальная логика
```

---

## 📝 Настройка Политик

### Редактировать policies.yaml

```bash
cd /Users/MD/AI-Platform-ISO/infrastructure/decision-center
nano policies.yaml
```

### Пример: Изменить Max Attempts для Database

```yaml
recovery:
  critical_services:
    database:
      priority: 1
      rto_seconds: 120
      max_auto_attempts: 2  # ← Измените здесь
      escalate_immediately: false
```

### Hot Reload (без перезапуска)

```python
from infrastructure.decision_center import get_policy_engine

engine = get_policy_engine()
engine.reload_policies()  # Перезагрузит policies.yaml
```

---

## 📧 Настройка Уведомлений

### Email (SMTP)

Создать `.env` файл:

```bash
cd /Users/MD/AI-Platform-ISO/infrastructure/decision-center
cat > .env << EOF
# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=bcm-platform@company.com

# Recipients
OPS_TEAM_EMAIL=ops@company.com
DBA_TEAM_EMAIL=dba@company.com
EOF
```

### Slack

Добавить в `.env`:

```bash
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

### Тестировать Notifications

```bash
cd /Users/MD/AI-Platform-ISO/infrastructure/decision-center
python3 << EOF
import asyncio
from notification_service import NotificationService
from infrastructure.eventbus import create_eventbus

async def test():
    bus = create_eventbus('redis')
    ns = NotificationService(eventbus=bus)

    await ns.send_notification(
        title="Test Notification",
        message="Escalation test",
        priority="high",
        channels=["email", "console"]
    )

    print("✅ Notification sent!")

asyncio.run(test())
EOF
```

---

## 🗄️ Database Setup (Опционально)

### Создать Audit Logs Table

```bash
# Supabase
psql $DATABASE_URL << EOF
CREATE TABLE decision_audit_logs (
    log_id UUID PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    decision_id VARCHAR(255) NOT NULL,
    service_name VARCHAR(255) NOT NULL,
    action VARCHAR(100) NOT NULL,
    reasoning TEXT,
    outcome VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_service ON decision_audit_logs(service_name);
CREATE INDEX idx_audit_timestamp ON decision_audit_logs(timestamp);
EOF
```

### Настроить Connection

В `.env`:

```bash
DATABASE_URL=postgresql://user:pass@host:5432/dbname
# или
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=xxx
```

---

## 🧪 Тестирование

### Тест 1: Decision Making

```bash
cd /Users/MD/AI-Platform-ISO/infrastructure/decision-center
python3 << 'EOF'
import asyncio
from decision_center import InfrastructureDecisionCenter
from infrastructure.eventbus import create_eventbus

async def test():
    bus = create_eventbus('redis')
    dc = InfrastructureDecisionCenter(eventbus=bus)

    # Test decision
    decision, can_proceed = await dc.decide_recovery_action(
        service_name='database',
        action_type='restart',
        current_attempt=1
    )

    print(f"Outcome: {decision.outcome.value}")
    print(f"Can proceed: {can_proceed}")
    print(f"Reasoning: {decision.reasoning}")

asyncio.run(test())
EOF
```

### Тест 2: Escalation

```bash
python3 << 'EOF'
import asyncio
from escalation_manager import EscalationManager
from notification_service import NotificationService
from infrastructure.eventbus import create_eventbus

async def test():
    bus = create_eventbus('redis')
    ns = NotificationService(eventbus=bus)
    em = EscalationManager(eventbus=bus, notification_service=ns)

    # Test escalation
    esc = await em.escalate(
        service_name='eventbus',
        reason='max_attempts_reached',
        severity='high',
        context={'attempts': 3}
    )

    print(f"Escalation ID: {esc.escalation_id}")
    print(f"Recovery blocked: {em.is_recovery_blocked('eventbus')}")

asyncio.run(test())
EOF
```

### Тест 3: Policy Engine

```bash
python3 << 'EOF'
from policy_engine import PolicyEngine

engine = PolicyEngine("policies.yaml")
engine.load_policies()

# Get policy
policy = engine.get_recovery_policy("database")
print(f"Database RTO: {policy['rto_seconds']}s")
print(f"Max attempts: {policy['max_auto_attempts']}")

# Get threshold
cpu_critical = engine.get_threshold("cpu", "critical")
print(f"CPU critical threshold: {cpu_critical}%")
EOF
```

---

## 📊 Мониторинг

### Проверить Audit Logs

```bash
# Последние решения
cd /Users/MD/AI-Platform-ISO/infrastructure/decision-center/audit_logs
tail -f audit_$(date +%Y-%m-%d).jsonl | jq .
```

### Статистика Решений

```python
from decision_center import InfrastructureDecisionCenter

dc = InfrastructureDecisionCenter()
stats = await dc.get_stats()

print(f"Total decisions: {stats['total_decisions']}")
print(f"Approval rate: {stats['approval_rate']:.1f}%")
print(f"Active escalations: {stats['active_escalations']}")
```

### EventBus Events

```bash
# Подписаться на decision events
python3 << 'EOF'
import asyncio
from infrastructure.eventbus import create_eventbus

async def monitor():
    bus = create_eventbus('redis')

    async def handler(event):
        print(f"📢 {event.type}: {event.data}")

    await bus.subscribe('infrastructure.decision.*', handler)
    await bus.subscribe('infrastructure.escalation.*', handler)

    await asyncio.sleep(300)  # 5 minutes

asyncio.run(monitor())
EOF
```

---

## 🔍 Troubleshooting

### Issue 1: "Module not found"

```bash
# Проверить PYTHONPATH
export PYTHONPATH=/Users/MD/AI-Platform-ISO:$PYTHONPATH
```

### Issue 2: "Policy validation failed"

```bash
# Проверить YAML syntax
python3 -c "
import yaml
with open('policies.yaml') as f:
    yaml.safe_load(f)
print('✅ YAML valid')
"
```

### Issue 3: "Database connection failed"

```bash
# Проверить DATABASE_URL
echo $DATABASE_URL

# Или работать без database (только file logging)
# Audit Logger автоматически упадет на file-only mode
```

### Issue 4: "Notifications not sending"

```bash
# Проверить env variables
env | grep SMTP
env | grep SLACK

# Тестировать console notifications (всегда работают)
# В policies.yaml:
notifications:
  channels:
    console:
      enabled: true
```

---

## 📖 Документация

### Основные Документы

- [Complete Summary](doc-project/PHASE_1.1_GOVERNANCE_COMPLETE.md) - полная сводка
- [Decision Center README](infrastructure/decision-center/README.md) - user guide
- [Policy Engine Docs](infrastructure/decision-center/IMPLEMENTATION_SUMMARY.md)
- [Escalation Integration](infrastructure/decision-center/ESCALATION_INTEGRATION_SUMMARY.md)

### Примеры Кода

- [Example Usage](infrastructure/decision-center/EXAMPLE_USAGE.py)
- [Policy Configuration](infrastructure/decision-center/policies.yaml)

---

## ✅ Чеклист Интеграции

- [ ] Файлы проверены (decision_center.py существует)
- [ ] Пример запущен (EXAMPLE_USAGE.py работает)
- [ ] Политики настроены (policies.yaml отредактирован)
- [ ] Auto-Recovery модифицирован (decision center интегрирован)
- [ ] Infrastructure Coordinator обновлен (escalation manager добавлен)
- [ ] Notifications настроены (.env файл создан)
- [ ] Database table создана (опционально)
- [ ] Тесты пройдены (decision, escalation, policy)
- [ ] EventBus events мониторятся
- [ ] Audit logs проверены

---

## 🎯 Следующие Шаги

### Сейчас (Quick Win - 1 час)
1. ✅ Запустить EXAMPLE_USAGE.py
2. ✅ Проверить audit logs
3. ✅ Протестировать policy engine

### Сегодня (Integration - 4 часа)
1. Модифицировать auto_recovery.py
2. Обновить infrastructure_coordinator.py
3. Тестировать end-to-end

### Завтра (Production - 1 день)
1. Настроить notifications
2. Создать database table
3. Deploy в test environment

### На Неделе (Phase 1.5 - AI Integration)
1. AI Orchestrator integration
2. Expertise Center consultation
3. Predictive intelligence

---

**Phase 1.1 готова к работе, партнер!** 🎉

**Что дальше?**
- Запустить примеры? → `python3 EXAMPLE_USAGE.py`
- Интегрировать сейчас? → Модифицировать auto_recovery.py
- Phase 1.5 (AI)? → Следующий этап

**Выбирай!** 🚀
