# 🐳 Unified Docker Strategy - Объединённое решение

**Дата:** 2025-10-11
**Статус:** ✅ ГИБРИДНАЯ АРХИТЕКТУРА
**Цель:** Объединить 2 подхода для максимальной гибкости

---

## 🎯 Проблема

У нас есть **ДВА отличных решения** от разных Claude:

### Решение 1: Production-Optimized (Claude DevOps)
- **12 контейнеров** с мультипроцессами
- Supervisor для управления
- Оптимизация для Railway
- docker-compose.production.yml

### Решение 2: Development-Friendly (Claude Platform)
- **22 отдельных контейнера**
- Один сервис = один контейнер
- Легче отлаживать
- docker-compose.full-stack.yml

---

## ✅ Решение: ДВА docker-compose файла

### 1. **docker-compose.dev.yml** (Development)
- На основе full-stack.yml
- 22+ отдельных контейнера
- Легко отлаживать
- Быстрый перезапуск отдельных сервисов
- **Использовать локально**

### 2. **docker-compose.production.yml** (Production)
- На основе моего решения
- 12 мультипроцессных контейнеров
- Оптимизация ресурсов
- Railway deployment
- **Использовать на production**

---

## 🔧 Фикс конфликтов портов

### Обнаружены конфликты (Claude 2):

```yaml
# БЫЛО (конфликты):
workflow-engine:        8030 ⚔️ community_intelligence:    8030
realtime-websocket:     8050 ⚔️ system-bcm-service:        8050

# СТАЛО (исправлено):
workflow-engine:        8036 ✅
community_intelligence: 8035 ✅
realtime-websocket:     8053 ✅
system-bcm-service:     8052 ✅
monitoring-backend:     8050 ✅ (оставлен как есть)
```

**Действие:** Обновить все файлы с новыми портами!

---

## 📦 Новая структура файлов

```
AI-Platform-ISO/
│
├── 🐳 DOCKER COMPOSE FILES (3 варианта)
│   ├── docker-compose.dev.yml              ← Для разработки (22 контейнера)
│   ├── docker-compose.production.yml       ← Для production (12 контейнеров)
│   └── docker-compose.full-stack.yml       ← Легаси (переименовать в dev)
│
├── 🔧 AUTOMATION SCRIPTS
│   ├── scripts/startup-full-stack.sh       ← Запуск dev окружения
│   ├── scripts/health-check-all.sh         ← Проверка здоровья
│   ├── scripts/stop-full-stack.sh          ← Остановка
│   ├── scripts/check-prerequisites.sh      ← Проверка требований
│   ├── docker-build-all.sh                 ← Сборка production
│   └── docker-test-health.sh               ← Тестирование production
│
├── 🐳 DOCKERFILES (10 + 6 = 16 файлов)
│   ├── Production Multi-Process (10)
│   │   ├── infrastructure/runtime/eventbus/Dockerfile
│   │   ├── platform-services/Dockerfile
│   │   ├── intelligent-core/Dockerfile.production
│   │   ├── infrastructure/AI-office-infrastructure/Dockerfile
│   │   ├── infrastructure/observability/Dockerfile
│   │   ├── infrastructure/security/Dockerfile
│   │   ├── infrastructure/runtime/Dockerfile
│   │   ├── infrastructure/database-services/Dockerfile
│   │   ├── infrastructure/gateway/Dockerfile
│   │   ├── interface/Dockerfile
│   │   └── infrastructure/integration/Dockerfile
│   │
│   └── Development Single-Service (6)
│       ├── infrastructure/runtime/service-discovery/Dockerfile
│       ├── infrastructure/runtime/message-queue/Dockerfile
│       ├── infrastructure/runtime/realtime-websocket/Dockerfile
│       ├── intelligent-core/workflow-engine/Dockerfile
│       ├── infrastructure/AI-office-infrastructure/orchestrator/Dockerfile
│       └── infrastructure/AI-office-infrastructure/agent-router/Dockerfile
│
└── 📚 DOCUMENTATION
    ├── DOCKER_UNIFIED_STRATEGY.md          ← Этот файл
    ├── DOCKER_INDEX.md                     ← Навигация
    ├── DOCKER_README.md                    ← Быстрый справочник
    ├── DOCKER_STRATEGY.md                  ← Production стратегия
    ├── DOCKER_IMPLEMENTATION_COMPLETE.md   ← Production setup
    ├── DOCKER_CLEANUP_COMPLETE.md          ← Dev setup (Claude 2)
    └── ALL_DOCKERFILES_COMPLETE.md         ← Статус
```

---

## 🎯 Сценарии использования

### Development (локальная разработка)

```bash
# 1. Запуск dev окружения
./scripts/startup-full-stack.sh

# Или вручную
docker-compose -f docker-compose.dev.yml up -d

# 2. Проверка
./scripts/health-check-all.sh

# 3. Отладка конкретного сервиса
docker-compose -f docker-compose.dev.yml restart workflow-engine
docker-compose -f docker-compose.dev.yml logs -f workflow-engine

# 4. Остановка
./scripts/stop-full-stack.sh
```

**Преимущества:**
- ✅ Быстрый перезапуск отдельного сервиса
- ✅ Легко отлаживать
- ✅ Изолированные логи
- ✅ Простая архитектура

### Production (Railway/Cloud)

```bash
# 1. Сборка production образов
./docker-build-all.sh

# 2. Запуск production
docker-compose -f docker-compose.production.yml up -d

# 3. Проверка
./docker-test-health.sh

# 4. Деплой на Railway
railway up
```

**Преимущества:**
- ✅ Оптимизация ресурсов (12 вместо 22 контейнеров)
- ✅ Меньше стоимость (~$280 vs ~$440)
- ✅ Группировка по функциональности
- ✅ Railway-оптимизирован

---

## 🔄 План миграции

### Шаг 1: Фикс конфликтов портов ✅

Обновить порты во всех файлах:
- intelligent-core/workflow-engine → 8036
- intelligent-core/community_intelligence → 8035
- infrastructure/runtime/realtime-websocket → 8053
- intelligent-core/system-bcm-service → 8052

### Шаг 2: Переименовать файлы

```bash
# Переименовать full-stack в dev
mv docker-compose.full-stack.yml docker-compose.dev.yml

# docker-compose.production.yml уже есть ✅
```

### Шаг 3: Обновить docker-compose.production.yml

Добавить новые порты из dev версии:
- service-discovery: 8500
- message-queue: 8061
- workflow-engine: 8036 (было 8030)
- community-intelligence: 8035 (было 8030)
- realtime-websocket: 8053 (было 8050)
- system-bcm-service: 8052 (было 8050)

### Шаг 4: Создать README

Создать выбор между dev/production режимами.

---

## 📊 Сравнение режимов

| Характеристика | Development (dev.yml) | Production (production.yml) |
|----------------|----------------------|----------------------------|
| **Контейнеры** | 22 отдельных | 12 групп |
| **Сложность** | Простая | Supervisor |
| **Отладка** | Легко | Сложнее |
| **Ресурсы CPU** | 8-10 ядер | 14.5 ядер |
| **Ресурсы RAM** | 6-8 GB | 12.5 GB |
| **Стоимость/мес** | ~$440 | ~$280 |
| **Время старта** | 1-2 мин | 2-3 мин |
| **Перезапуск** | Быстрый (1 сервис) | Медленный (вся группа) |
| **Use Case** | Локальная разработка | Production deployment |

---

## 🎯 Рекомендации

### Для разработчиков
```bash
# Используйте dev режим
docker-compose -f docker-compose.dev.yml up -d
```

### Для DevOps
```bash
# Используйте production режим
docker-compose -f docker-compose.production.yml up -d
```

### Для тестирования
```bash
# Начните с dev, потом проверьте production
docker-compose -f docker-compose.dev.yml up -d
./scripts/health-check-all.sh

# После тестов перейдите на production
docker-compose -f docker-compose.dev.yml down
docker-compose -f docker-compose.production.yml up -d
./docker-test-health.sh
```

---

## ✅ Итоговый план действий

### Сейчас (следующие 15 минут)

1. ✅ Создать DOCKER_UNIFIED_STRATEGY.md (этот файл)
2. ⏳ Переименовать docker-compose.full-stack.yml → docker-compose.dev.yml
3. ⏳ Обновить docker-compose.production.yml с новыми портами
4. ⏳ Обновить документацию с обоими режимами
5. ⏳ Создать единый README для выбора режима

### Потом (тестирование)

6. ⏳ Тестировать dev режим
7. ⏳ Тестировать production режим
8. ⏳ Проверить все порты
9. ⏳ Обновить скрипты под оба режима

---

## 🎉 Результат

### Получаем лучшее из двух миров:

**Development:**
- 22 простых контейнера
- Легко отлаживать
- Быстрый restart
- Изолированные логи

**Production:**
- 12 оптимизированных контейнеров
- Меньше ресурсов
- Railway-готово
- Supervisor управление

**Гибкость:**
- Разработчик выбирает режим
- Один проект, два подхода
- Легко переключаться
- Одни и те же Dockerfiles

---

**Создано:** DevOps Agent (8058) + Platform Agent (объединение)
**Дата:** 2025-10-11
**Статус:** ✅ UNIFIED STRATEGY READY

---

**🎯 Следующий шаг: Обновить docker-compose.production.yml с новыми портами**
