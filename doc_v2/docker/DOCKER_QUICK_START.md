# 🐳 Docker Quick Start - Быстрый старт

**Дата:** 2025-10-11
**Статус:** ✅ ДВА РЕЖИМА ГОТОВЫ

---

## 🎯 Выберите режим

У вас есть **ДВА варианта** запуска платформы:

| Режим | Когда использовать | Контейнеры | Команда |
|-------|-------------------|------------|---------|
| **Development** | Локальная разработка, отладка | 22 простых | `docker-compose -f docker-compose.dev.yml up -d` |
| **Production** | Railway, Cloud, Production | 12 оптимизированных | `docker-compose -f docker-compose.production.yml up -d` |

---

## 🚀 Development Режим (Рекомендуется для начала)

### Характеристики
- ✅ **22 отдельных контейнера** - один сервис = один контейнер
- ✅ **Простая отладка** - легко посмотреть логи
- ✅ **Быстрый restart** - перезапуск одного сервиса за секунды
- ✅ **Изолированные логи** - каждый сервис отдельно
- ✅ **5-слойная архитектура**

### Быстрый старт

```bash
# 1. Проверить требования
./scripts/check-prerequisites.sh

# 2. Запустить все сервисы
./scripts/startup-full-stack.sh

# Или вручную
docker-compose -f docker-compose.dev.yml up -d

# 3. Проверить здоровье
./scripts/health-check-all.sh

# 4. Посмотреть логи
docker-compose -f docker-compose.dev.yml logs -f workflow-engine

# 5. Перезапустить сервис
docker-compose -f docker-compose.dev.yml restart ai-orchestration

# 6. Остановить
./scripts/stop-full-stack.sh
```

### Точки доступа

```
Service Discovery:    http://localhost:8500
Message Queue:        http://localhost:8061
Realtime WebSocket:   http://localhost:8053
Workflow Engine:      http://localhost:8036
AI Orchestration:     http://localhost:8031
Community Intel:      http://localhost:8035
System BCM:           http://localhost:8052
Prometheus:           http://localhost:9090
Grafana:              http://localhost:3000 (admin/admin)
```

### Требования
- **CPU:** 8-10 ядер
- **RAM:** 6-8 GB
- **Хранилище:** 25 GB
- **Стоимость (Cloud):** ~$440/месяц

---

## 🏭 Production Режим (Для Railway)

### Характеристики
- ✅ **12 мультипроцессных контейнеров** - группировка по функциям
- ✅ **Supervisor** - управление процессами внутри контейнеров
- ✅ **Оптимизация ресурсов** - меньше overhead
- ✅ **Railway-ready** - готово к деплою
- ✅ **Меньше стоимость** - ~$280 вместо $440

### Быстрый старт

```bash
# 1. Настроить окружение
cp .env.production.example .env.production
nano .env.production  # Добавить ваши секреты

# 2. Собрать все контейнеры (30-45 мин)
./docker-build-all.sh

# 3. Запустить
docker-compose -f docker-compose.production.yml up -d

# 4. Проверить здоровье
./docker-test-health.sh

# 5. Посмотреть логи группы
docker-compose -f docker-compose.production.yml logs -f platform-services

# 6. Войти в контейнер
docker exec -it bcm-platform-services /bin/bash

# 7. Проверить supervisor
docker exec bcm-platform-services supervisorctl status

# 8. Перезапустить сервис внутри контейнера
docker exec bcm-platform-services supervisorctl restart bia-service

# 9. Остановить
docker-compose -f docker-compose.production.yml down
```

### Контейнеры (12 групп)

```
1. Redis              (6379)          - Кэш
2. EventBus           (8001)          - Сообщения
3. Gateway            (8000)          - API вход
4. Platform Services  (8011-8027)     - 9 бизнес-сервисов
5. Intelligent Core   (8002,8028+)    - 7 AI/ML сервисов
6. AI Office          (8055-8060)     - 6 внутренних агентов
7. Monitoring         (9090,8050,8054) - Prometheus + 2 бэкенда
8. Security           (8081,8084)     - Auth + Secrets
9. Runtime            (8053,8061,8500) - WebSocket, Queue, Discovery
10. DB Services       (8051)          - DB Intelligence
11. Interfaces        (3000-3002)     - 3 фронтенд приложения
12. Integrations      (8087-8089)     - GitHub, MCP, Partisia
```

### Точки доступа

```
API Gateway:     http://localhost:8000
Admin Panel:     http://localhost:3000
User Portal:     http://localhost:3001
Control Center:  http://localhost:3002
Prometheus:      http://localhost:9090
```

### Требования
- **CPU:** 14.5 ядер
- **RAM:** 12.5 GB
- **Хранилище:** 48 GB
- **Стоимость (Railway):** ~$280/месяц

---

## 📊 Сравнение режимов

| Характеристика | Development | Production |
|----------------|-------------|------------|
| **Контейнеры** | 22 простых | 12 с Supervisor |
| **Отладка** | ⭐⭐⭐⭐⭐ Легко | ⭐⭐⭐ Средне |
| **Перезапуск сервиса** | 2-5 сек | 10-20 сек |
| **Логи** | Изолированные | Общие (по группам) |
| **CPU** | 8-10 ядер | 14.5 ядер |
| **RAM** | 6-8 GB | 12.5 GB |
| **Стоимость** | $440/мес | $280/мес |
| **Использование** | Локально | Railway/Cloud |

---

## 🔧 Обновлённые порты (Фикс конфликтов)

### ❌ СТАРЫЕ ПОРТЫ (конфликты):
```
workflow-engine:        8030 ⚔️ community_intelligence: 8030
realtime-websocket:     8050 ⚔️ system-bcm-service:     8050
service-discovery:      8086 ⚔️ runtime services
```

### ✅ НОВЫЕ ПОРТЫ (исправлено):
```
# Intelligent Core
workflow-engine:        8036 ✅ (было 8030)
community-intelligence: 8035 ✅ (было 8030)
system-bcm-service:     8052 ✅ (было 8050)

# Runtime
realtime-websocket:     8053 ✅ (было 8082)
message-queue:          8061 ✅ (было 8085)
service-discovery:      8500 ✅ (было 8086)

# Monitoring
monitoring-backend:     8050 ✅ (оставлен)
service-catalog:        8054 ✅ (было 8052)
```

---

## 🎯 Рекомендации

### Для разработчиков
```bash
# Используйте Development режим
cd /Users/MD/AI-Platform-ISO
./scripts/startup-full-stack.sh
```

**Почему?**
- Быстрый restart одного сервиса
- Легко посмотреть логи
- Простая отладка
- Изолированные контейнеры

### Для DevOps
```bash
# Используйте Production режим
cd /Users/MD/AI-Platform-ISO
./docker-build-all.sh
docker-compose -f docker-compose.production.yml up -d
```

**Почему?**
- Оптимизация ресурсов
- Меньше стоимость
- Railway-готово
- Production patterns (Supervisor)

### Для тестирования
```bash
# 1. Начните с Development
docker-compose -f docker-compose.dev.yml up -d
./scripts/health-check-all.sh

# 2. После проверки → Production
docker-compose -f docker-compose.dev.yml down
./docker-build-all.sh
docker-compose -f docker-compose.production.yml up -d
./docker-test-health.sh
```

---

## 📚 Документация

### Основные документы
- **[DOCKER_UNIFIED_STRATEGY.md](DOCKER_UNIFIED_STRATEGY.md)** - Объединённая стратегия
- **[DOCKER_INDEX.md](DOCKER_INDEX.md)** - Полная навигация
- **[DOCKER_README.md](DOCKER_README.md)** - Подробный справочник

### Development документы
- **[DOCKER_CLEANUP_COMPLETE.md](DOCKER_CLEANUP_COMPLETE.md)** - Dev setup (Claude 2)
- **[SCRIPTS_CLEANUP_REPORT.md](SCRIPTS_CLEANUP_REPORT.md)** - Анализ скриптов
- **[docker-compose.dev.yml](docker-compose.dev.yml)** - Dev оркестрация

### Production документы
- **[DOCKER_STRATEGY.md](DOCKER_STRATEGY.md)** - Production архитектура
- **[DOCKER_IMPLEMENTATION_COMPLETE.md](DOCKER_IMPLEMENTATION_COMPLETE.md)** - Production setup
- **[DOCKER_DEPLOYMENT_READY.md](DOCKER_DEPLOYMENT_READY.md)** - Готовность к деплою
- **[docker-compose.production.yml](docker-compose.production.yml)** - Production оркестрация

---

## 🐛 Troubleshooting

### Development

```bash
# Сервис не запускается
docker-compose -f docker-compose.dev.yml logs workflow-engine

# Перезапустить сервис
docker-compose -f docker-compose.dev.yml restart workflow-engine

# Войти в контейнер
docker exec -it ai-platform-workflow-engine /bin/bash

# Проверить порты
lsof -i :8036
```

### Production

```bash
# Проверить все сервисы в группе
docker exec bcm-intelligent-core supervisorctl status

# Логи конкретного сервиса
docker exec bcm-intelligent-core tail -f /var/log/supervisor/workflow-engine.err.log

# Перезапустить сервис в группе
docker exec bcm-intelligent-core supervisorctl restart workflow-engine

# Войти в контейнер
docker exec -it bcm-intelligent-core /bin/bash
```

---

## ✅ Чеклист

### Development режим
- [ ] Установлен Docker & docker-compose
- [ ] Проверены требования (`./scripts/check-prerequisites.sh`)
- [ ] Создан `.env` файл
- [ ] Запущены сервисы (`./scripts/startup-full-stack.sh`)
- [ ] Проверено здоровье (`./scripts/health-check-all.sh`)
- [ ] Доступны все точки входа

### Production режим
- [ ] Скопирован `.env.production.example` → `.env.production`
- [ ] Заполнены секреты в `.env.production`
- [ ] Собраны образы (`./docker-build-all.sh`)
- [ ] Запущена платформа
- [ ] Проверено здоровье (`./docker-test-health.sh`)
- [ ] Доступны все интерфейсы

---

## 🚀 Следующие шаги

### После запуска Development
1. Проверить все сервисы
2. Отладить проблемные сервисы
3. Протестировать интеграции
4. Перейти на Production

### После запуска Production
1. Проверить все health checks
2. Настроить мониторинг (Prometheus/Grafana)
3. Настроить логирование
4. Подготовить к Railway deployment

---

## 📞 Поддержка

### Документация
- Начните с [DOCKER_INDEX.md](DOCKER_INDEX.md)
- Для dev: [DOCKER_CLEANUP_COMPLETE.md](DOCKER_CLEANUP_COMPLETE.md)
- Для prod: [DOCKER_IMPLEMENTATION_COMPLETE.md](DOCKER_IMPLEMENTATION_COMPLETE.md)

### Скрипты
- **Development:** `./scripts/startup-full-stack.sh`
- **Production:** `./docker-build-all.sh`
- **Health Check Dev:** `./scripts/health-check-all.sh`
- **Health Check Prod:** `./docker-test-health.sh`

---

**Создано:** DevOps Agent (8058) + Platform Agent (unified)
**Дата:** 2025-10-11
**Статус:** ✅ ОБА РЕЖИМА ГОТОВЫ

---

## 🎉 Готово!

Выберите режим и запускайте:

```bash
# Development (рекомендуется для начала)
./scripts/startup-full-stack.sh

# Production (для Railway)
./docker-build-all.sh
docker-compose -f docker-compose.production.yml up -d
```

**Успехов! 🚀**
