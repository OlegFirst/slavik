# Event Intelligence System - Deployment Guide 🚀

**Полное руководство по развёртыванию и настройке саморазвивающейся системы управления событиями**

---

## 📋 Содержание

1. [Обзор системы](#обзор-системы)
2. [Архитектура](#архитектура)
3. [Установка](#установка)
4. [Конфигурация](#конфигурация)
5. [Интеграции](#интеграции)
6. [Мониторинг](#мониторинг)
7. [Поддержка](#поддержка)

---

## 🎯 Обзор системы

### Что это?

**Event Intelligence System** - саморазвивающаяся платформа для управления событиями, которая:

- ✅ Автоматически обнаруживает события в коде
- ✅ Находит пробелы и несоответствия
- ✅ Предлагает улучшения на основе ML
- ✅ Исправляет проблемы автоматически
- ✅ Непрерывно мониторит качество архитектуры

### Зачем нужна?

Без Event Intelligence:
- ❌ События определяются вручную
- ❌ Pробелы обнаруживаются случайно
- ❌ Документация устаревает
- ❌ Качество архитектуры деградирует

С Event Intelligence:
- ✅ Автоматическое обнаружение событий
- ✅ Проактивное выявление проблем
- ✅ Актуальная документация
- ✅ Постоянное улучшение архитектуры

---

## 🏗️ Архитектура

### Компоненты системы

```
┌────────────────────────────────────────────────────────────────┐
│                    EVENT INTELLIGENCE SYSTEM                    │
└────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
┌───────▼────────┐  ┌────────▼────────┐  ┌────────▼─────────┐
│   Intelligence │  │   Auto-Fixer    │  │ Continuous       │
│   System       │  │                 │  │ Monitor          │
│                │  │                 │  │                  │
│ • Scan code    │  │ • Fix gaps      │  │ • Watch changes  │
│ • Analyze gaps │  │ • Generate code │  │ • Detect regress │
│ • Suggest      │  │ • Create PRs    │  │ • Export metrics │
└────────┬───────┘  └────────┬────────┘  └────────┬─────────┘
         │                   │                    │
         └───────────────────┼────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
┌───────▼────────┐  ┌───────▼────────┐  ┌──────▼──────┐
│ AI Workflow    │  │  Predictive    │  │  Monitoring │
│ Optimizer      │  │  Service       │  │  Dashboard  │
│                │  │                │  │             │
│ • Optimize     │  │ • ML Predict   │  │ • Grafana   │
│   workflows    │  │ • Anomalies    │  │ • Prometheus│
└────────────────┘  └────────────────┘  └─────────────┘
```

### Потоки данных

```
Code Changes → Event Intelligence Scan → Analysis Report
                                              │
                    ┌─────────────────────────┼─────────────────────┐
                    │                         │                     │
                    ▼                         ▼                     ▼
            Auto-Fix Suggestions      ML Recommendations     Metrics Export
                    │                         │                     │
                    ▼                         ▼                     ▼
              Apply Fixes            Update Predictions      Grafana/Alerting
```

---

## 📦 Установка

### 1. Предварительные требования

```bash
# Python 3.11+
python3 --version

# Зависимости
pip install pyyaml
```

### 2. Установка Event Intelligence

```bash
cd /Users/MD/AI-Platform-ISO

# Проверка структуры
ls tools/event_intelligence/
# Должны быть:
# - event_intelligence_system.py
# - auto_fixer.py
# - continuous_monitor.py
# - README.md
```

### 3. Первый запуск

```bash
# Базовое сканирование
python3 tools/event_intelligence/event_intelligence_system.py \
    --scan \
    --validate \
    --suggest \
    --report infrastructure/eventbus/events/intelligence_report.json

# Проверка результата
cat infrastructure/eventbus/events/intelligence_report.json | head -50
```

**Ожидаемый output:**
```
📊 EVENT INTELLIGENCE SYSTEM - SUMMARY
======================================================================
📋 Schema Events: 21
💻 Code Events: 45
⚠️ Gaps Found: 121
   - Critical: 4
   - Warning: 24
   - Info: 93
💡 Potential Events: 525
```

---

## ⚙️ Конфигурация

### 1. AsyncAPI Schema

Файл: `infrastructure/eventbus/events/asyncapi.yaml`

```yaml
asyncapi: 3.0.0
info:
  title: BCM Platform Event Architecture
  version: 1.0.0

channels:
  # Добавьте ваши события здесь
  your.event.name:
    address: your.event.name
    messages:
      YourEvent:
        payload:
          type: object
          properties:
            # ... schema
```

### 2. CI/CD Configuration

**GitHub Actions:** `.github/workflows/event_intelligence_ci.yml`

```yaml
on:
  push:
    branches: [ main, develop ]
  schedule:
    - cron: '0 9 * * *'  # Ежедневно в 9:00 UTC
```

**Customization:**
```yaml
# Изменить частоту сканирования
schedule:
  - cron: '0 */4 * * *'  # Каждые 4 часа

# Добавить уведомления
- name: Send Slack notification
  if: failure()
  run: |
    curl -X POST $SLACK_WEBHOOK_URL \
      -d '{"text": "Event Intelligence CI failed!"}'
```

### 3. Continuous Monitor

**Запуск как systemd service:**

```bash
# /etc/systemd/system/event-intelligence-monitor.service
[Unit]
Description=Event Intelligence Continuous Monitor
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/Users/MD/AI-Platform-ISO
ExecStart=/usr/bin/python3 tools/event_intelligence/continuous_monitor.py --watch --interval 3600
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Запуск
sudo systemctl enable event-intelligence-monitor
sudo systemctl start event-intelligence-monitor

# Проверка
sudo systemctl status event-intelligence-monitor
```

---

## 🔗 Интеграции

### 1. AI Workflow Optimizer

**Файл:** `intelligent-core/ai_workflow_optimizer/integrations/event_intelligence_integration.py`

**Использование:**

```python
from ai_workflow_optimizer.integrations.event_intelligence_integration import (
    get_event_intelligence_insights
)

# В вашем workflow optimizer
async def optimize_workflow():
    insights = await get_event_intelligence_insights()

    # Анализ
    gaps = insights['workflow_events_analysis']['workflow_gaps']
    optimizations = insights['optimizations']

    # Применение
    for opt in optimizations:
        if opt['priority'] == 'high':
            await apply_optimization(opt)
```

**API endpoints:**

```python
# FastAPI integration
from fastapi import APIRouter

router = APIRouter()

@router.get("/event-intelligence/insights")
async def get_insights():
    return await get_event_intelligence_insights()
```

### 2. Predictive Service

**Файл:** `intelligent-core/predictive/integrations/event_intelligence_learning.py`

**Использование:**

```python
from predictive.integrations.event_intelligence_learning import (
    get_event_intelligence_predictions
)

# В Predictive Service
async def update_predictions():
    predictions = await get_event_intelligence_predictions()

    # ML learning
    future_gaps = predictions['predictions']['items']
    anomalies = predictions['anomalies']['items']

    # Update models
    for prediction in future_gaps:
        await ml_model.learn_from_prediction(prediction)
```

**Scheduled job:**

```python
# В main.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()

@scheduler.scheduled_job('cron', hour='*/6')  # Каждые 6 часов
async def update_event_predictions():
    predictions = await get_event_intelligence_predictions()
    logger.info(f"Updated predictions: {predictions['summary']}")

scheduler.start()
```

### 3. Prometheus Metrics

**Конфигурация Prometheus:**

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'event_intelligence'
    static_configs:
      - targets: ['localhost:9090']
    file_sd_configs:
      - files:
        - '/Users/MD/AI-Platform-ISO/infrastructure/eventbus/events/metrics.prom'
```

**Экспорт метрик:**

```bash
# Разово
python3 tools/event_intelligence/continuous_monitor.py --export-metrics

# Непрерывно (через monitor)
python3 tools/event_intelligence/continuous_monitor.py --watch
```

**Доступные метрики:**

```prometheus
event_intelligence_schema_events          # События в схеме
event_intelligence_code_events            # События в коде
event_intelligence_gaps_total             # Всего gaps
event_intelligence_gaps_critical          # Критические gaps
event_intelligence_gaps_warning           # Предупреждения
event_intelligence_coverage_percent       # Процент покрытия
event_intelligence_last_scan_timestamp    # Время последнего scan
```

---

## 📊 Мониторинг

### 1. Grafana Dashboard

**Импорт dashboard:**

```json
{
  "dashboard": {
    "title": "Event Intelligence",
    "panels": [
      {
        "title": "Event Coverage",
        "targets": [{
          "expr": "event_intelligence_coverage_percent"
        }],
        "type": "gauge"
      },
      {
        "title": "Critical Gaps",
        "targets": [{
          "expr": "event_intelligence_gaps_critical"
        }],
        "type": "stat"
      },
      {
        "title": "Gaps Trend",
        "targets": [{
          "expr": "event_intelligence_gaps_total"
        }],
        "type": "graph"
      }
    ]
  }
}
```

### 2. Alerting Rules

```yaml
# prometheus-alerts.yml
groups:
  - name: event_intelligence
    rules:
      - alert: CriticalEventGaps
        expr: event_intelligence_gaps_critical > 5
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Critical event gaps: {{ $value }}"
          description: "Event architecture has {{ $value }} critical gaps"

      - alert: EventCoverageLow
        expr: event_intelligence_coverage_percent < 70
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Low event coverage: {{ $value }}%"
```

### 3. Slack Notifications

```python
# tools/event_intelligence/notifications.py
import requests

def send_slack_notification(webhook_url: str, message: str):
    """Отправка уведомления в Slack"""
    payload = {
        "text": message,
        "username": "Event Intelligence Bot",
        "icon_emoji": ":robot_face:"
    }
    requests.post(webhook_url, json=payload)

# Использование в monitor
if len(critical_gaps) > 5:
    send_slack_notification(
        SLACK_WEBHOOK_URL,
        f"⚠️ Critical: {len(critical_gaps)} event gaps detected!"
    )
```

---

## 🛠️ Troubleshooting

### Проблема 1: Scan не находит события

**Решение:**

```bash
# Проверка путей
ls -la intelligent-core/

# Проверка прав доступа
chmod +x tools/event_intelligence/*.py

# Запуск с debug
python3 tools/event_intelligence/event_intelligence_system.py \
    --scan --validate \
    --project-root $(pwd)
```

### Проблема 2: Auto-fixer не создаёт файлы

**Решение:**

```bash
# Проверка report
cat infrastructure/eventbus/events/intelligence_report.json | jq '.gaps | length'

# Dry-run для проверки
python3 tools/event_intelligence/auto_fixer.py \
    --fix-subscribers \
    --dry-run

# Проверка прав на запись
ls -la intelligent-core/event_handlers/
```

### Проблема 3: Continuous Monitor не экспортирует метрики

**Решение:**

```bash
# Проверка формата метрик
cat infrastructure/eventbus/events/metrics.prom

# Должен быть валидный Prometheus format:
# event_intelligence_schema_events 21

# Проверка процесса
ps aux | grep continuous_monitor

# Перезапуск
pkill -f continuous_monitor
python3 tools/event_intelligence/continuous_monitor.py --watch &
```

---

## 📚 Best Practices

### 1. Регулярное использование

```bash
# Ежедневно (автоматически через CI/CD)
- Event Intelligence scan
- Review critical gaps
- Apply high-priority fixes

# Еженедельно
- Trend analysis
- Review ML recommendations
- Update AsyncAPI schema

# Ежемесячно
- Architectural review
- Optimize event patterns
- Update monitoring dashboards
```

### 2. Workflow для команды

```
1. Developer commits code
   ↓
2. CI/CD runs Event Intelligence scan
   ↓
3. PR commented with results
   ↓
4. Team reviews critical gaps
   ↓
5. Apply fixes or add to backlog
   ↓
6. Merge to main
   ↓
7. Monitor watches for regressions
```

### 3. Интеграция с Planning

```markdown
## Sprint Planning

Event Intelligence Insights:
- 4 critical gaps to fix (2 story points)
- 12 high-priority potential events (5 story points)
- ML recommends: Add subscribers for X, Y, Z events

Action items:
- [ ] Fix critical gaps (Sprint Goal)
- [ ] Implement 5 high-confidence potential events
- [ ] Review and update AsyncAPI schema
```

---

## 🚀 Deployment Checklist

### Initial Setup

- [ ] Install dependencies
- [ ] Run first scan
- [ ] Review results
- [ ] Configure AsyncAPI schema
- [ ] Setup CI/CD integration

### Continuous Operation

- [ ] Enable Continuous Monitor
- [ ] Configure Prometheus scraping
- [ ] Setup Grafana dashboards
- [ ] Configure alerting rules
- [ ] Setup Slack notifications

### Team Onboarding

- [ ] Share documentation with team
- [ ] Setup access to dashboards
- [ ] Train on using auto-fixer
- [ ] Establish review process
- [ ] Define SLAs for fixing gaps

---

## 📞 Support & Resources

### Documentation

- [Event Intelligence README](../tools/event_intelligence/README.md)
- [EventBus Documentation](../infrastructure/eventbus/events/README.md)
- [AsyncAPI Specification](../infrastructure/eventbus/events/asyncapi.yaml)

### Tools & Scripts

```bash
# Quick scan
./scripts/event_intelligence_scan.sh

# Generate report
./scripts/generate_event_report.sh

# Fix gaps
./scripts/auto_fix_events.sh
```

### Contacts

- **Architecture Questions:** [@architecture-team](...)
- **Event Intelligence Issues:** [GitHub Issues](...)
- **Monitoring Support:** [@devops-team](...)

---

## 🎉 Success Metrics

После успешного развёртывания вы должны увидеть:

✅ **Event Coverage > 85%**
- Большинство событий реализованы

✅ **Critical Gaps < 5**
- Критические проблемы решены

✅ **Weekly Trend: Improving**
- Качество архитектуры растёт

✅ **ML Recommendations Applied: 70%+**
- AI предложения внедряются

✅ **CI/CD Integration: Green**
- Автоматическая валидация работает

---

**🤖 Платформа готова к саморазвитию!**

Теперь Event Intelligence System будет:
- Автоматически находить проблемы
- Предлагать улучшения
- Мониторить качество
- Обучаться на данных

**Следующие шаги:** [Интеграция с AI Lab](./AI_LAB_INTEGRATION.md)
