# 📊 АНАЛИЗ ТЕКУЩЕЙ СТРУКТУРЫ ПОСЛЕ МИГРАЦИИ

## 🔴 ПРОБЛЕМЫ И ДУБЛИ:

### 1. **Множественные папки integrations:**
```
./integrations/                        # Почти пустая (только подпапки)
./platform-framework/integrations/     # Реальные интеграции
./platform-framework/document-processor/integrations/  # Интеграции документов
```

### 2. **Дублирование services:**
```
./services/                           # Общие сервисы (ai, cognitive, domain, utility)
./platform-framework/services/        # Системные сервисы
./ai-core/services/                   # AI сервисы
./collected-services/                 # Собранные сервисы (не разобраны)
```

### 3. **Несколько мониторингов:**
```
./platform-framework/monitoring/      # Основной мониторинг
./platform-framework/monitoring-bcm/  # BCM мониторинг
./infrastructure/monitoring/          # Инфраструктурный мониторинг
```

### 4. **Разбросанные базы данных:**
```
./infrastructure/database/
./infrastructure/databases/
```

### 5. **Непонятные пустые структуры:**
```
./core/                              # Пустые подпапки
./platforms/                         # Пустые подпапки
./interfaces/                        # Пустые подпапки
```

## ✅ ХОРОШО ОРГАНИЗОВАНО:

### 1. **platform-framework/** - системные компоненты
- event-bus
- service-registry
- config-service
- orchestrator (собран из всех частей)
- document-processor (собран)
- auth-service
- notification-service

### 2. **services/bcm-specific/** - BCM компоненты
- golden-pr-modules (новая сборка Odoo)
- compliance
- odoo (420MB)
- digital-twin-module
- simulators-module
- frontend

### 3. **ai-core/** - AI компоненты
- services/ai-consultant
- services/ai-pdca
- services/ai_control_center
- prototypes

## 📝 ЧТО НУЖНО СДЕЛАТЬ:

### Этап 1: Объединение дублей
1. Объединить все integrations в одну папку
2. Объединить все services по категориям
3. Объединить monitoring в один модуль
4. Объединить database/databases

### Этап 2: Удаление пустых
1. Проверить и удалить пустые папки в core/
2. Проверить и удалить пустые папки в platforms/
3. Проверить и удалить пустые папки в interfaces/

### Этап 3: Реорганизация
1. Разобрать collected-services
2. Структурировать services по типам:
   - system-services (из platform-framework)
   - ai-services (из ai-core)
   - bcm-services (из bcm-specific)
   - utility-services

### Этап 4: Финализация
1. Создать единую карту зависимостей
2. Настроить docker-compose
3. Создать документацию по запуску

## 📊 СТАТИСТИКА:

- **Общее количество директорий**: ~70
- **Пустых директорий**: ~20
- **Дублированных структур**: 5-6
- **Требует реорганизации**: ~30%

## 🎯 ЦЕЛЕВАЯ СТРУКТУРА:

```
COGNITIVE-ORCHESTRATION-ISO22301/
├── platform-framework/     # Ядро системы
│   ├── core/              # Event Bus, Service Registry, Config
│   ├── orchestrator/      # Единый оркестратор
│   ├── api-gateway/       # API шлюз
│   └── services/          # Системные сервисы
│
├── services/              # Все сервисы
│   ├── system/           # Системные (auth, notification)
│   ├── ai/               # AI сервисы
│   ├── bcm/              # BCM-специфичные
│   └── utility/          # Вспомогательные
│
├── integrations/          # Все интеграции
│   ├── external/         # TheHive, OpenGRC
│   ├── internal/         # Moodle, Gateway
│   └── protocols/        # WebSocket, gRPC
│
├── infrastructure/        # Инфраструктура
│   ├── docker/           # Docker конфигурации
│   ├── kubernetes/       # K8s манифесты
│   ├── monitoring/       # Prometheus, Grafana
│   └── databases/        # PostgreSQL, MongoDB
│
├── tests/                # Все тесты
├── docs/                 # Вся документация
└── BCM-v1/              # Архив и референсы
```