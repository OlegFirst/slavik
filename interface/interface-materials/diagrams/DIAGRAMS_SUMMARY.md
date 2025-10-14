# Сводка по диаграммам платформы

**Дата создания**: 2025-10-09
**Статус**: ✅ Готово
**Всего диаграмм**: 36 Mermaid диаграмм

---

## 📁 Структура папки diagrams/

```
doc-project/diagrams/
├── README.md                          # Полная документация по всем диаграммам
│
├── architecture/                      # 24 диаграммы
│   ├── platform-architecture.mmd      # Основная архитектурная диаграмма
│   └── ARCHITECTURE_VISUALIZATIONS_01-23.mmd  # 23 визуализации из документации
│
├── user-scenarios/                    # 4 диаграммы 🆕
│   ├── BCM_USER_JOURNEY.mmd          # Пользовательский путь BCM
│   ├── BIA_DETAILED_WORKFLOW.mmd     # Workflow BIA с AI
│   ├── ADMIN_SERVICE_MONITORING.mmd  # Админ-панель мониторинга
│   └── RISK_ASSESSMENT_FLOW.mmd      # Процесс оценки рисков
│
├── dependencies/                      # 1 диаграмма 🆕
│   └── SERVICE_DEPENDENCIES_DETAILED.mmd  # Граф зависимостей сервисов
│
├── flows/                            # 3 диаграммы 🆕
│   ├── EVENTBUS_MESSAGE_FLOW.mmd     # Поток сообщений EventBus
│   ├── DATA_FLOW_COMPLETE.mmd        # Полный поток данных
│   └── AI_ORCHESTRATION_FLOW.mmd     # Оркестрация AI
│
├── integration/                       # 4 диаграммы
│   ├── SPRINT_1_ASSEMBLY_PLAN_01.mmd
│   ├── ИНСТРУМЕНТЫ_ДОКУМЕНТАЦИИ_АНАЛИЗ_01.mmd
│   ├── DOCUMENTATION_UPDATE_PLAN_01.mmd
│   └── PHASE1_SYSTEM_BCM_COMPLETE_01.mmd
│
└── business-processes/                # 1 диаграмма
    └── DOC_GENERATORS_UPDATED_01.mmd
```

---

## 📊 Статистика

### Распределение по категориям

| Категория | Количество | Процент | Статус |
|-----------|------------|---------|--------|
| Architecture | 24 | 66.7% | ✅ Извлечено из документации |
| User Scenarios | 4 | 11.1% | 🆕 Создано |
| Integration | 4 | 11.1% | ✅ Извлечено из документации |
| Flows | 3 | 8.3% | 🆕 Создано |
| Dependencies | 1 | 2.8% | 🆕 Создано |
| Business Processes | 1 | 2.8% | ✅ Извлечено из документации |
| **ВСЕГО** | **36** | **100%** | |

### Типы диаграмм

- **Flowchart/Graph** (~23): Блок-схемы и графы
- **Sequence** (~6): Диаграммы последовательности
- **State** (~2): Диаграммы состояний
- **Entity Relationship** (~3): ER-диаграммы
- **Mixed** (~2): Смешанные типы

---

## 🎯 Основные диаграммы

### Для разработчиков

1. **architecture/platform-architecture.mmd**
   - Основная архитектурная диаграмма
   - 4 слоя, 23 сервиса, 20 портов

2. **architecture/ARCHITECTURE_VISUALIZATIONS_01.mmd**
   - High-Level System Overview
   - Полная схема с User Layer, Intelligent Core, Platform Services, Infrastructure

3. **dependencies/SERVICE_DEPENDENCIES_DETAILED.mmd**
   - Детальный граф зависимостей
   - 11 Platform Services + 6 Intelligent Core модулей + 4 Infrastructure компонента

4. **flows/DATA_FLOW_COMPLETE.mmd**
   - Полный поток данных от пользователя до ответа
   - Включает AI анализ (RAG + LLM)

5. **flows/EVENTBUS_MESSAGE_FLOW.mmd**
   - Детальный поток сообщений EventBus
   - Redis Streams + RabbitMQ, ACK/NACK, retry механизм

### Для UI/UX дизайнеров

1. **user-scenarios/BCM_USER_JOURNEY.mmd**
   - Полный пользовательский путь
   - BIA → Risk → Plan → Exercise

2. **user-scenarios/BIA_DETAILED_WORKFLOW.mmd**
   - Детальный 6-шаговый workflow BIA
   - С AI анализом и валидацией

3. **user-scenarios/RISK_ASSESSMENT_FLOW.mmd**
   - Процесс оценки рисков
   - 3 источника, матрица 5×5, AI митигация

4. **doc-project/TZ_USER_INTERFACE.md**
   - Техническое задание UI/UX (1744 строки)
   - 10 разделов пользователя + 10 разделов админа

### Для администраторов

1. **user-scenarios/ADMIN_SERVICE_MONITORING.mmd**
   - Административная панель мониторинга
   - 23 сервиса + инфраструктура

2. **architecture/ARCHITECTURE_VISUALIZATIONS_19.mmd**
   - Complete Infrastructure Stack
   - PostgreSQL, Redis, RabbitMQ, Qdrant, Prometheus, Grafana

3. **architecture/ARCHITECTURE_VISUALIZATIONS_20.mmd**
   - Infrastructure Ports Map
   - Карта всех портов инфраструктуры

---

## 🛠️ Инструменты для работы с диаграммами

### Просмотр

- **Online**: [Mermaid Live Editor](https://mermaid.live)
- **VS Code**: Расширение "Markdown Preview Mermaid Support"
- **IntelliJ/PyCharm**: Плагин "Mermaid"

### Экспорт

```bash
# Установка CLI
npm install -g @mermaid-js/mermaid-cli

# PNG
mmdc -i diagram.mmd -o diagram.png

# SVG
mmdc -i diagram.mmd -o diagram.svg
```

---

## 📚 Источники

### Извлечено из документации

- **ARCHITECTURE_VISUALIZATIONS.md** (23 диаграммы)
  - doc-project/architecture/ARCHITECTURE_VISUALIZATIONS.md
  - 1960 строк, 10 разделов архитектурных визуализаций

- **Документация проекта** (4 диаграммы)
  - SPRINT_1_ASSEMBLY_PLAN.md
  - DOC_GENERATORS_UPDATED.md
  - DOCUMENTATION_UPDATE_PLAN.md
  - PHASE1_SYSTEM_BCM_COMPLETE.md

- **Platform Architecture** (1 диаграмма)
  - docs/platform-architecture.mmd

### Созданные диаграммы

- **User Scenarios** (4 диаграммы)
  - BCM User Journey
  - BIA Detailed Workflow
  - Admin Service Monitoring
  - Risk Assessment Flow

- **Dependencies** (1 диаграмма)
  - Service Dependencies Detailed

- **Flows** (3 диаграммы)
  - EventBus Message Flow
  - Data Flow Complete
  - AI Orchestration Flow

---

## ✅ Результаты

### Что сделано

1. ✅ Извлечено 28 существующих диаграмм из документации
2. ✅ Создано 8 новых профессиональных диаграмм
3. ✅ Организовано в 6 категорий по функциональности
4. ✅ Создана полная документация (README.md)
5. ✅ Все диаграммы в формате Mermaid (.mmd)

### Покрытие

- **Архитектура**: ✅ 100% (24 диаграммы)
- **Пользовательские сценарии**: ✅ 100% (4 основных потока)
- **Зависимости**: ✅ 100% (детальный граф)
- **Потоки данных**: ✅ 100% (3 ключевых потока)
- **Интеграция**: ✅ 100% (4 диаграммы)
- **Бизнес-процессы**: ✅ 100% (1 диаграмма)

---

## 📖 Связанные документы

- [README.md](./README.md) - Полная документация по всем диаграммам
- [TZ_USER_INTERFACE.md](../TZ_USER_INTERFACE.md) - Техническое задание UI/UX
- [ARCHITECTURE_VISUALIZATIONS.md](../architecture/ARCHITECTURE_VISUALIZATIONS.md) - Исходный документ
- [PROJECT_INDEX.md](../../PROJECT_INDEX.md) - Главный индекс проекта
- [INDEX.md](../INDEX.md) - Индекс проектной документации

---

## 🎓 Как использовать эту коллекцию

### 1. Для изучения платформы

Последовательность:
1. **Начните с**: `architecture/platform-architecture.mmd`
2. **Затем**: `architecture/ARCHITECTURE_VISUALIZATIONS_01.mmd` (High-Level Overview)
3. **Изучите**: `dependencies/SERVICE_DEPENDENCIES_DETAILED.mmd`
4. **Понимание потоков**: `flows/DATA_FLOW_COMPLETE.mmd`

### 2. Для разработки UI/UX

Последовательность:
1. **Сценарии**: `user-scenarios/BCM_USER_JOURNEY.mmd`
2. **Детали**: `user-scenarios/BIA_DETAILED_WORKFLOW.mmd`
3. **ТЗ**: `../TZ_USER_INTERFACE.md`
4. **Риски**: `user-scenarios/RISK_ASSESSMENT_FLOW.mmd`

### 3. Для backend разработки

Последовательность:
1. **Зависимости**: `dependencies/SERVICE_DEPENDENCIES_DETAILED.mmd`
2. **EventBus**: `flows/EVENTBUS_MESSAGE_FLOW.mmd`
3. **AI**: `flows/AI_ORCHESTRATION_FLOW.mmd`
4. **Архитектура**: Все файлы в `architecture/`

### 4. Для DevOps/администрирования

Последовательность:
1. **Мониторинг**: `user-scenarios/ADMIN_SERVICE_MONITORING.mmd`
2. **Инфраструктура**: `architecture/ARCHITECTURE_VISUALIZATIONS_19.mmd`
3. **Порты**: `architecture/ARCHITECTURE_VISUALIZATIONS_20.mmd`
4. **Deployment**: `architecture/ARCHITECTURE_VISUALIZATIONS_17-18.mmd`

---

**Версия**: 1.0.0
**Дата**: 2025-10-09
**Статус**: ✅ Готово к использованию
