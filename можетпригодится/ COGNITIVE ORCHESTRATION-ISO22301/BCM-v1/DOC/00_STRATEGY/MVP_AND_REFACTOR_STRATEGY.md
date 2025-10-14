# 🎯 Двухтрековая стратегия: MVP + Рефакторинг

**Дата**: 2025-09-28
**Статус**: ✅ Утверждено
**Подход**: Параллельная разработка

---

## 📋 Общая стратегия

```
┌─────────────────────────────────────────────────────────┐
│  Track 1: MVP в текущей ветке (unified-complete...)     │
│  Цель: Запустить работающую версию ASAP                 │
│  Приоритет: 🔴 ВЫСОКИЙ                                   │
│  Срок: 2-3 недели                                        │
└─────────────────────────────────────────────────────────┘
                            ↓
                    Копируем проверенный код
                            ↓
┌─────────────────────────────────────────────────────────┐
│  Track 2: Новая архитектура (feature/clean-architecture)│
│  Цель: Чистая структура с проверенным кодом             │
│  Приоритет: 🟡 СРЕДНИЙ                                   │
│  Срок: Параллельно, без дедлайна                        │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 TRACK 1: MVP (ГЛАВНЫЙ ФОКУС)

### Текущее состояние

**Сервисы в docker-compose.yml**: 27 сервисов

**Инфраструктура**:
- ✅ postgres
- ✅ redis
- ✅ rabbitmq
- ✅ keycloak
- ✅ traefik

**Core**:
- ✅ odoo (образ maxde4/seh-foundation-iso-22301:v1.1)

**Backend сервисы** (19):
1. ai_orchestrator
2. bia_engine
3. notification_service
4. document_processor
5. compliance_checker
6. bpmn_service
7. lms_adapter
8. thehive_adapter
9. grafana_adapter
10. eventbus
11. deployer
12. github_app
13. pdca_assistant
14. module_validator_api
15. unified_ai_service
16. scenario_orchestrator
17. model_runner
18. bcm_mcp_server
19. simulation_adapter

**Frontend** (2):
1. web_portal
2. admin_panel

**Мониторинг**:
1. grafana
2. exercise_simulators
3. jaamsim
4. mailhog

---

### Цели MVP (Minimum Viable Product)

**Что должно работать**:

1. ✅ **Odoo BCM модули**
   - Вход в систему
   - Просмотр BCM меню
   - Создание BIA записи
   - Создание инцидента
   - Просмотр рисков

2. ✅ **Web Portal** (основной UI)
   - Дашборд
   - Навигация по модулям
   - Интеграция с Odoo

3. ✅ **Admin Panel**
   - Управление пользователями
   - Настройки

4. ✅ **AI Orchestrator**
   - Claude API интеграция
   - Базовые AI функции

5. ✅ **BIA Engine**
   - Расчёт business impact
   - Приоритизация ресурсов

6. ⚠️ **Notification Service**
   - Email уведомления
   - (SMS опционально)

**Что НЕ обязательно для MVP**:
- ❌ TheHive интеграция (можно позже)
- ❌ Moodle/LMS интеграция (можно позже)
- ❌ Digital Twin симуляции (можно позже)
- ❌ GitHub App (можно позже)
- ❌ Полный мониторинг (базовый достаточно)

---

### План запуска MVP (2-3 недели)

#### Неделя 1: Диагностика и критические фиксы

**День 1-2: Аудит текущего состояния**

```bash
# 1. Проверить какие сервисы реально работают
docker-compose up -d
docker-compose ps

# 2. Проверить логи каждого сервиса
docker-compose logs odoo | tail -50
docker-compose logs ai_orchestrator | tail -50
docker-compose logs bia_engine | tail -50

# 3. Проверить health endpoints
curl http://localhost:8069/web/health  # Odoo
curl http://localhost:8001/health      # AI Orchestrator (?)
curl http://localhost:8002/health      # BIA Engine (?)
```

**День 3-4: Исправить критические проблемы**

Из предыдущего анализа:
1. 🔴 Hardcoded credentials в ai_orchestrator → переменные окружения
2. 🔴 Missing authentication в unified_api_gateway → добавить
3. 🔴 In-memory storage → заменить на Redis/Postgres

**День 5: Smoke tests**
- Войти в Odoo
- Создать BIA запись
- Создать инцидент
- Вызвать AI функцию
- Проверить уведомления

---

#### Неделя 2: Интеграция и функциональность

**День 1-2: Odoo ↔ Backend интеграция**
- Проверить EventBus работает
- Проверить AI Orchestrator получает события
- Проверить BIA Engine вызывается из Odoo

**День 3-4: Frontend интеграция**
- Запустить web_portal
- Проверить подключение к Odoo API
- Проверить дашборды отображаются

**День 5: E2E тест основного flow**
```
User → Web Portal → Odoo → EventBus → AI Orchestrator → Response
```

---

#### Неделя 3: Стабилизация и документация

**День 1-3: Bug fixing**
- Исправить найденные баги
- Улучшить error handling
- Добавить логирование

**День 4-5: Документация MVP**
- Инструкция по запуску
- Описание основных функций
- Known issues и workarounds

---

### Критические действия для MVP

| Задача | Приоритет | Усилия | Блокер? |
|--------|-----------|--------|---------|
| Исправить hardcoded credentials | 🔴 Critical | 2 часа | Да (security) |
| Добавить authentication | 🔴 Critical | 1 день | Да (security) |
| Запустить Odoo с BCM модулями | 🔴 Critical | 1 день | Да (core функция) |
| Запустить web_portal | 🔴 Critical | 1 день | Да (UI) |
| Интеграция AI Orchestrator | 🟡 High | 2 дня | Нет |
| Интеграция BIA Engine | 🟡 High | 2 дня | Нет |
| Email notifications | 🟠 Medium | 1 день | Нет |
| Мониторинг (базовый) | 🟢 Low | 1 день | Нет |

---

### MVP Success Criteria

**Must Have** (обязательно):
- [ ] Odoo запущен и доступен
- [ ] Можно войти в систему
- [ ] Видны BCM модули в меню
- [ ] Можно создать BIA запись
- [ ] Можно создать инцидент
- [ ] Web portal показывает дашборд
- [ ] AI Orchestrator отвечает на запросы

**Should Have** (желательно):
- [ ] BIA Engine считает impact
- [ ] Email уведомления работают
- [ ] EventBus передаёт события
- [ ] Admin panel работает

**Could Have** (опционально):
- [ ] TheHive интеграция
- [ ] Moodle интеграция
- [ ] Digital Twin симуляции
- [ ] Полный мониторинг

---

## 🏗️ TRACK 2: Новая архитектура (параллельно)

### Создание новой ветки

```bash
# 1. Создать новую ветку от текущей
git checkout unified-complete-iso22301-20250920
git checkout -b feature/clean-architecture

# 2. Создать новую структуру директорий
mkdir -p apps/{frontend,core}
mkdir -p services/{ai,bcm,platform,infrastructure,integration}
mkdir -p adapters
mkdir -p integrations/{clients,configs}
mkdir -p infrastructure/{docker-configs,monitoring,deploy-scripts}
mkdir -p tools/{scripts,sandbox,tests}

# 3. Добавить README в каждую
# (описание структуры)

# 4. Commit начальной структуры
git add .
git commit -m "feat: Initialize clean architecture structure"
git push origin feature/clean-architecture
```

---

### Процесс миграции (постепенно)

**Подход**: После того как сервис заработал в Track 1 → копируем в Track 2

**Пример workflow**:

```bash
# 1. В Track 1: Фиксим ai_orchestrator
# (исправили hardcoded credentials, протестировали)

# 2. Переключаемся на Track 2
git checkout feature/clean-architecture

# 3. Копируем ПРОВЕРЕННЫЙ код с исправлениями
git checkout unified-complete-iso22301-20250920 -- services/ai_orchestrator

# 4. Перемещаем в новую структуру
mv services/ai_orchestrator services/ai/orchestrator

# 5. Обновляем пути в конфигах
# (docker-compose, imports, etc)

# 6. Commit
git add .
git commit -m "feat(ai): Migrate ai_orchestrator to new structure"

# 7. Вернуться на Track 1 для следующего сервиса
git checkout unified-complete-iso22301-20250920
```

---

### Порядок миграции сервисов

**Фаза 1: Core сервисы** (первыми)
1. Odoo (apps/core/odoo-18.0)
2. API Gateway (services/platform/api-gateway)
3. EventBus (services/platform/event-bus)

**Фаза 2: AI сервисы**
1. ai_orchestrator → services/ai/orchestrator
2. unified_ai_service → services/ai/unified
3. pdca_assistant → services/ai/pdca-assistant

**Фаза 3: BCM сервисы**
1. bia_engine → services/bcm/bia-engine
2. compliance_checker → services/bcm/compliance-checker
3. scenario_orchestrator → services/bcm/scenario-orchestrator

**Фаза 4: Infrastructure**
1. document_processor → services/infrastructure/document-processor
2. notification_service → services/infrastructure/notification-service

**Фаза 5: Integrations**
1. thehive_adapter → adapters/thehive
2. lms_adapter → services/integration/lms-adapter

**Фаза 6: Frontend**
1. web_portal → apps/frontend/unified-platform
2. admin_panel → apps/frontend/admin-panel

---

### Track 2 Success Criteria

**Milestone 1**: Структура создана
- [ ] Все директории созданы
- [ ] README в каждой директории
- [ ] .gitkeep файлы

**Milestone 2**: Core мигрирован
- [ ] Odoo в apps/core/
- [ ] Запускается через docker-compose

**Milestone 3**: 5+ сервисов мигрировано
- [ ] AI Orchestrator
- [ ] BIA Engine
- [ ] API Gateway
- [ ] EventBus
- [ ] Notification Service

**Milestone 4**: Frontend мигрирован
- [ ] Web Portal в apps/frontend/
- [ ] Работает с новыми путями

**Milestone 5**: Полная миграция
- [ ] Все сервисы перенесены
- [ ] Docker-compose обновлён
- [ ] Все тесты проходят
- [ ] Документация обновлена

---

## 🔄 Синхронизация между треками

### Правила работы

1. **Track 1 (MVP) - главный**
   - Все фиксы и новые фичи делаем здесь
   - Тестируем здесь
   - Это production-ready ветка

2. **Track 2 (Refactor) - копирует проверенное**
   - Копируем только РАБОЧИЙ код из Track 1
   - Не создаём новую функциональность здесь
   - Фокус на структуре, не на фичах

3. **Merge strategy**
   - Track 1 → Track 2 (cherry-pick проверенных коммитов)
   - Track 2 → Track 1 (ТОЛЬКО когда Track 2 полностью готов)

---

### Git workflow

```bash
# Ежедневно: Обновить Track 1
git checkout unified-complete-iso22301-20250920
git pull origin unified-complete-iso22301-20250920

# Еженедельно: Синхронизировать Track 2
git checkout feature/clean-architecture
git rebase unified-complete-iso22301-20250920

# При конфликтах: Приоритет Track 1
git checkout --theirs <file>

# Когда сервис готов: Копировать в Track 2
git checkout feature/clean-architecture
git checkout unified-complete-iso22301-20250920 -- services/some_service
mv services/some_service services/category/some-service
git add .
git commit -m "feat: Migrate some_service to new structure"
```

---

## 📊 Метрики прогресса

### Track 1 (MVP)

| Метрика | Текущее | Цель | Статус |
|---------|---------|------|--------|
| Сервисы запущены | ?/27 | 10/27 | ⏳ TODO |
| Критические баги исправлены | 0/5 | 5/5 | ⏳ TODO |
| Smoke tests проходят | 0/5 | 5/5 | ⏳ TODO |
| Odoo модули работают | ?/29 | 15/29 | ⏳ TODO |
| Frontend работает | 0/2 | 2/2 | ⏳ TODO |

### Track 2 (Refactor)

| Метрика | Текущее | Цель |
|---------|---------|------|
| Структура создана | 0% | 100% |
| Сервисы мигрировано | 0/27 | 27/27 |
| Docker-compose обновлён | 0% | 100% |
| Tests проходят | 0% | 100% |
| Документация обновлена | 0% | 100% |

---

## ⚡ Быстрый старт

### Сегодня (Track 1):

```bash
# 1. Проверить текущее состояние
cd /Users/MD/ISO-22301
git status
docker-compose ps

# 2. Запустить все сервисы
docker-compose up -d

# 3. Проверить логи
docker-compose logs --tail=50

# 4. Проверить какие сервисы работают
curl http://localhost:8069/web/health
# ... проверить все endpoints

# 5. Создать TODO для критических фиксов
```

### На этой неделе (Track 2):

```bash
# 1. Создать новую ветку
git checkout -b feature/clean-architecture

# 2. Создать структуру директорий
# (как показано выше)

# 3. Commit начальной структуры
git add .
git commit -m "feat: Initialize clean architecture"
git push origin feature/clean-architecture

# 4. Вернуться на Track 1
git checkout unified-complete-iso22301-20250920
```

---

## 🎯 Финальный результат

### Через 2-3 недели:

**Track 1**:
- ✅ Работающий MVP
- ✅ Odoo + 10 ключевых сервисов
- ✅ Web Portal работает
- ✅ Можно показать клиенту
- ✅ Можно деплоить

**Track 2**:
- ✅ Чистая структура создана
- ✅ 5-10 сервисов мигрировано
- ⏳ Остальные постепенно переносим

### Через 1-2 месяца:

**Track 1**:
- Развиваем функциональность
- Добавляем новые фичи
- Production use

**Track 2**:
- Полная миграция завершена
- Готов к merge в main
- Становится новым production

---

## 🤝 Вердикт

Ваш подход **идеален**:

✅ Прагматичный (MVP быстро)
✅ Безопасный (новая ветка отдельно)
✅ Гибкий (можем переключаться)
✅ Профессиональный (лучшие практики)

**Следующий шаг**: Начать с Track 1 - запуск MVP.

---

**Автор**: Claude Sonnet 4
**Дата**: 2025-09-28