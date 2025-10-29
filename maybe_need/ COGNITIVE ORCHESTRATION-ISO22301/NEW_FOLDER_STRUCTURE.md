# 🏗️ НОВАЯ СТРУКТУРА ПАПОК ПО СЛОЯМ

## Текущая структура (путает):
```
platform-framework/
├── api-gateway/
├── auth-service/
├── event-bus/
├── orchestrator/
├── monitoring/
└── ...
```

## Предлагаемая структура (понятная по слоям):

```
COGNITIVE-ORCHESTRATION-ISO22301/
│
├── 1_NUCLEUS/                 # 🧠 ЯДРО (мозг и нервы)
│   ├── orchestrator/          # Единый мозг
│   ├── event-bus/             # Нервная система
│   ├── service-registry/      # Память о сервисах
│   ├── workflow-engine/       # Исполнение процессов
│   ├── bcm-integration-hub/   # Координатор модулей
│   └── infrastructure/        # PostgreSQL, Redis, RabbitMQ configs
│
├── 2_PROTECTION/              # 🛡️ ЗАЩИТА (череп и кожа)
│   ├── api-gateway/          # Главные ворота
│   ├── auth-service/         # Страж у ворот
│   ├── config-service/       # Хранитель настроек
│   ├── rate-limiter/         # Защита от DDoS
│   ├── monitoring/           # Наблюдатель (Prometheus, Grafana)
│   └── notifications/        # Коммуникатор
│
├── 3_SERVICES/                # 📦 СЕРВИСЫ (органы системы)
│   ├── document-processor/   # Обработка документов
│   ├── risk-management/      # Управление рисками
│   ├── incident-management/  # Управление инцидентами
│   ├── audit-service/        # Аудит
│   ├── training-service/     # Обучение
│   ├── bia-service/         # Анализ влияния на бизнес
│   └── recovery-planning/    # Планирование восстановления
│
├── 4_INTEGRATIONS/           # 🔌 ИНТЕГРАЦИИ (внешние связи)
│   ├── odoo-modules/        # BCM модули Odoo
│   ├── thehive/            # TheHive интеграция
│   ├── moodle/             # Moodle интеграция
│   ├── external-apis/      # Внешние API
│   └── iot-sensors/        # IoT датчики
│
├── 5_AI_CORE/               # 🤖 AI КОМПОНЕНТЫ
│   ├── models/             # AI модели
│   ├── agents/             # AI агенты
│   ├── prompts/            # Библиотека промптов
│   └── training/           # Обучение моделей
│
├── docker-compose/          # 🐳 Docker конфигурации
│   ├── nucleus.yml         # Ядро
│   ├── protection.yml      # Защита
│   ├── services.yml        # Сервисы
│   └── integrations.yml    # Интеграции
│
├── scripts/                # 📜 Скрипты запуска
│   ├── start-nucleus.sh
│   ├── start-protection.sh
│   ├── start-services.sh
│   └── start-platform.sh   # Запуск всего
│
└── config/                 # ⚙️ Конфигурации
    ├── development/
    ├── staging/
    └── production/
```

## Команды для перестройки:

```bash
# Создаем новую структуру
mkdir -p 1_NUCLEUS 2_PROTECTION 3_SERVICES 4_INTEGRATIONS 5_AI_CORE

# Переносим компоненты ядра
mv platform-framework/orchestrator 1_NUCLEUS/
mv platform-framework/event-bus 1_NUCLEUS/
mv platform-framework/service-registry 1_NUCLEUS/
mv platform-framework/services/bpmn_service 1_NUCLEUS/workflow-engine

# Переносим защитный слой
mv platform-framework/api-gateway 2_PROTECTION/
mv platform-framework/auth-service 2_PROTECTION/
mv platform-framework/config-service 2_PROTECTION/
mv platform-framework/monitoring 2_PROTECTION/
mv platform-framework/notification-service 2_PROTECTION/notifications

# Переносим сервисы
mv platform-framework/document-processor 3_SERVICES/
# ... и так далее

# Docker конфигурации
mkdir docker-compose
mv docker-compose-*.yml docker-compose/
```

## Преимущества новой структуры:

1. **Понятная иерархия** - сразу видно что к какому слою относится
2. **Числовой порядок** - понятна последовательность запуска
3. **Изоляция слоев** - легко работать с отдельным слоем
4. **Модульность** - можно запускать только нужные слои
5. **Масштабируемость** - легко добавлять новые компоненты в слой