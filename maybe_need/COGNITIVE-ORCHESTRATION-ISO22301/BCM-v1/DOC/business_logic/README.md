# 💼 Business Logic Documentation

Бизнес-процессы, workflows и правила BCM Platform.

## 📚 Содержание

| Файл | Описание | Строк |
|------|----------|-------|
| [WORKFLOWS.md](WORKFLOWS.md) | Все бизнес-процессы модулей | ~440 |
| [USER_JOURNEYS.md](USER_JOURNEYS.md) | Пользовательские сценарии | ~580 |
| [INTEGRATION_FLOWS.md](INTEGRATION_FLOWS.md) | Интеграции между модулями и сервисами | ~830 |
| [BUSINESS_RULES.md](BUSINESS_RULES.md) | Бизнес-правила и ограничения | ~750 |
| [PDCA_PROCESSES.md](PDCA_PROCESSES.md) | PDCA циклы | ~660 |

## 🎯 Категории бизнес-логики

### 1. Workflows
**Файл**: [WORKFLOWS.md](WORKFLOWS.md)

Содержит детальное описание всех бизнес-процессов:
- Risk Management workflow
- BIA workflow
- Incident Management workflow
- Plan activation workflow
- Exercise workflow
- Audit workflow

### 2. User Journeys
**Файл**: [USER_JOURNEYS.md](USER_JOURNEYS.md)

Пользовательские сценарии для разных ролей:
- BCM Manager
- Risk Manager
- Incident Response Team
- Auditor
- Executive
- Employee

### 3. Integration Flows
**Файл**: [INTEGRATION_FLOWS.md](INTEGRATION_FLOWS.md)

Потоки интеграции:
- Odoo ↔ AI Services
- Odoo ↔ External Systems (TheHive, Moodle)
- EventBus flows
- Real-time updates

### 4. Business Rules
**Файл**: [BUSINESS_RULES.md](BUSINESS_RULES.md)

Бизнес-правила:
- Валидация данных
- Расчёты (RTO/RPO, риски)
- Права доступа
- Ограничения

### 5. PDCA Processes
**Файл**: [PDCA_PROCESSES.md](PDCA_PROCESSES.md)

PDCA циклы (Plan-Do-Check-Act):
- BCM lifecycle
- Continuous improvement
- Management review cycles

## 🎯 Для разных ролей

### Project Manager
1. [USER_JOURNEYS.md](USER_JOURNEYS.md) - понять пользовательские сценарии
2. [WORKFLOWS.md](WORKFLOWS.md) - понять бизнес-процессы
3. [PDCA_PROCESSES.md](PDCA_PROCESSES.md) - понять циклы улучшения

### QA Engineer
1. [BUSINESS_RULES.md](BUSINESS_RULES.md) - понять правила валидации
2. [USER_JOURNEYS.md](USER_JOURNEYS.md) - создать тестовые сценарии
3. [WORKFLOWS.md](WORKFLOWS.md) - понять end-to-end процессы

### Backend Developer
1. [INTEGRATION_FLOWS.md](INTEGRATION_FLOWS.md) - понять интеграции
2. [BUSINESS_RULES.md](BUSINESS_RULES.md) - реализовать правила
3. [WORKFLOWS.md](WORKFLOWS.md) - реализовать процессы

### Frontend Developer
1. [USER_JOURNEYS.md](USER_JOURNEYS.md) - понять UX flows
2. [WORKFLOWS.md](WORKFLOWS.md) - понять UI flows
3. [BUSINESS_RULES.md](BUSINESS_RULES.md) - валидация на UI

## 🔗 Связанная документация

- [Frontend Business Flows](../frontend/clean/05_BUSINESS_FLOWS.md)
- [Architecture](../architecture/)
- [Modules Documentation](../modules/)

---

**Последнее обновление**: 2025-09-28