# Каталоги Платформы - Быстрый старт

**Дата обновления**: 2025-10-12
**Статус**: ✅ ГОТОВО К ГЕНЕРАЦИИ СЦЕНАРИЕВ

---

## 🎯 Что это?

Централизованное хранилище всех каталогов платформы:
- **Сервисы** (46) - все микросервисы
- **Подсистемы** (11) - технические группы для деплоя
- **Функциональные системы** (19) - бизнес-возможности платформы

---

## 📁 Структура каталогов

```
catalogs/
├── services/
│   └── SERVICE_CATALOG_DETAILED.yaml       # 46 сервисов
│
├── subsystems/
│   └── SUBSYSTEMS_CATALOG.yaml             # 11 подсистем
│
├── systems/
│   └── SYSTEMS_CATALOG.yaml                # 19 функциональных систем
│
├── workflows/                               # Воркфлоу (будут созданы)
│
├── scenarios/                               # Сценарии (будут созданы)
│
├── FUNCTIONAL_SYSTEMS_ANALYSIS.md          # Детальный анализ (60KB)
├── FUNCTIONAL_SYSTEMS_QUICK_REF.md         # Быстрая справка
├── ARCHITECTURE_DIAGRAM.md                 # Диаграммы архитектуры
├── CATALOG_REBUILD_COMPLETE.md             # Отчёт о работе
├── QUICK_REFERENCE.md                      # Краткая справка (EN)
└── README_RU.md                            # Этот файл
```

---

## 🏗️ Три уровня архитектуры

```
46 Сервисов (L1)
    ↓ группируются для деплоя
11 Подсистем (L2 - технические)
    ↓ группируются по назначению
19 Функциональных систем (L3 - бизнес)
```

### Пример:
- **Сервис** (L1): `auth-service`, `vault`, `api-gateway`
- **Подсистема** (L2): `Security` (содержит auth, vault, secrets)
- **Функциональная система** (L3): `🔒 Система безопасности` (защита платформы)

---

## 🚀 19 Функциональных систем

Это **ЧТО ДЕЛАЕТ** система, а не какие технологии использует!

### 🏛️ Фундамент (7 систем)

1. **🚀 Система запуска и оркестрации**
   - Управляет жизненным циклом, координирует запуск
   - Сервисы: service-discovery, mio-manager, ai-orchestration

2. **🛡️ Система отказоустойчивости**
   - Обеспечивает непрерывность работы, самовосстановление
   - Сервисы: event-intelligence, system-bcm-service

3. **🔒 Система безопасности**
   - Аутентификация, авторизация, секреты, аудит
   - Сервисы: auth-service, vault

4. **📊 Система мониторинга**
   - Метрики, дашборды, алерты, наблюдаемость
   - Сервисы: prometheus, grafana, mio-manager

5. **🔍 Система аналитики**
   - Анализ данных, инсайты, обнаружение паттернов
   - Сервисы: analytics-specialist, community-intelligence

6. **💾 Система хранения данных**
   - Реляционные БД, кэш, векторный поиск
   - Сервисы: postgresql, redis, qdrant

7. **🌐 API и коммуникации**
   - HTTP API, WebSocket, очереди сообщений
   - Сервисы: api-gateway, websocket, eventbus

### 🤖 AI Интеллект (6 систем)

8. **📚 Система обучения и знаний**
   - Управление знаниями, обучение персонала, RAG
   - Сервисы: learning-service, ai-foundation

9. **🔮 Система предсказаний**
   - Прогнозирование рисков, ML, аналитика
   - Сервисы: predictive, analytics-specialist

10. **🤖 AI Оркестрация**
    - Координация AI агентов, распределение задач
    - Сервисы: ai-orchestration, agent-router

11. **👥 Коллективный AI**
    - Обмен знаниями, peer-review, сообщество
    - Сервисы: community-intelligence, collective

12. **🧬 Система эволюции**
    - Самообучение, адаптация, автоулучшение
    - Сервисы: event-intelligence, ai-orchestration

13. **🧠 AI Foundation Infrastructure**
    - RAG, embeddings, интеграция LLM
    - Сервисы: ai-foundation, qdrant, expertise-center

### 📋 Бизнес и операции (6 систем)

14. **📋 BCM Business Logic**
    - BIA, Риски, Планы, Управление, Комплаенс
    - Сервисы: bia, risk, plans, governance, compliance

15. **⚙️ Workflow Management**
    - Управление процессами, BPMN, Temporal
    - Сервисы: workflow-intelligence, workflow-engine

16. **📡 Event-Driven Architecture**
    - Асинхронная обработка событий, pub/sub
    - Сервисы: eventbus, event-intelligence

17. **🔧 DevOps & Infrastructure**
    - Автоматизация деплоя, CI/CD
    - Сервисы: devops-agent, project-agent

18. **✅ Testing & Validation**
    - Тестирование, валидация, аудит, CAPA
    - Сервисы: validation-service, tests

19. **🖥️ User Interface Layer**
    - Интерфейсы для пользователей и админов
    - Сервисы: admin-panel, platform-ui (reserved)

---

## 📊 11 Подсистем (технические)

Для деплоя и управления:

1. **💾 Database Infrastructure** (4 сервиса)
2. **⚡ Runtime Services** (3 сервиса)
3. **🚪 Gateway Layer** (1 сервис)
4. **📊 Observability** (2 сервиса)
5. **📡 EventBus Core** (1 сервис)
6. **🔒 Security** (3 сервиса)
7. **🤖 AI Office** (7 сервисов)
8. **📚 Shared Libraries** (2 сервиса)
9. **📋 Platform Services** (11 сервисов)
10. **🧠 Intelligent Core** (12 сервисов)
11. **🖥️ Interface Layer** (3 сервиса)

---

## 🔑 Ключевые сервисы (обязательны)

| Порт | Сервис | Назначение |
|------|--------|-----------|
| 5432 | PostgreSQL | База данных |
| 6379 | Redis | Кэш и сессии |
| 8003 | EventBus | События |
| 8000 | API Gateway | Внешний API |
| 8001 | Auth Service | Аутентификация |
| 8002 | MIO Manager | Координация |
| 8010 | Workflow Intelligence | Процессы |
| 8040 | AI Orchestration | AI мозг |
| 8500 | Service Discovery | Регистрация |

---

## 🚀 Последовательность запуска

```
1. Фундамент
   ├─ PostgreSQL, Redis, Qdrant
   └─ Shared Libraries

2. Инфраструктура
   ├─ Security (Auth, Vault)
   ├─ EventBus
   ├─ Service Discovery
   └─ Prometheus, Grafana

3. Gateway
   └─ API Gateway

4. Платформа
   └─ BIA, Risk, Plans и т.д.

5. Интеллект
   ├─ AI Foundation
   ├─ AI Orchestration
   └─ AI Office

6. Интерфейс
   └─ Admin Panel, Platform UI
```

---

## 🔗 Паттерны интеграции

1. **Все → DB Managers → PostgreSQL/Redis/Qdrant**
   - Универсальный доступ к данным

2. **Сервисы ↔ EventBus → Асинхронные коммуникации**
   - Event-driven choreography

3. **Внешние → Gateway → Service Discovery → Сервисы**
   - Роутинг с обнаружением сервисов

4. **Сервисы → Prometheus → Grafana**
   - Сбор метрик и визуализация

5. **AI задачи → Agent Router → AI Orchestration → Специалисты**
   - Координация AI агентов

6. **BCM → Workflow Intelligence → Temporal → Выполнение**
   - Оркестрация воркфлоу

7. **UI ↔ WebSocket ↔ EventBus → Обновления в реальном времени**
   - Живые апдейты интерфейса

8. **AI → RAG → Qdrant → Контекст для запросов**
   - Retrieval-Augmented Generation

---

## 📈 Статистика

- **Всего сервисов**: 46 (30 активных, 4 устаревших)
- **Подсистем**: 11 (9 production, 1 reserved)
- **Функциональных систем**: 19 (17 production)
- **Критичных систем**: 7
- **Критичных подсистем**: 8

---

## 🎯 Что дальше?

Теперь готовы к генерации:

1. **L1 Сценарии** (46) - по одному на каждый сервис
2. **L2 Сценарии** (11) - по одному на каждую подсистему
3. **L3 Сценарии** (19) - по одному на функциональную систему
4. **L4 Воркфлоу** - пользовательские E2E процессы

---

## 📚 Документация

### Основные файлы:
- `CATALOG_REBUILD_COMPLETE.md` - Полный отчёт о работе
- `FUNCTIONAL_SYSTEMS_ANALYSIS.md` - Детальный анализ (60KB)
- `ARCHITECTURE_DIAGRAM.md` - Диаграммы архитектуры
- `QUICK_REFERENCE.md` - Краткая справка (EN)

### Каталоги:
- `services/SERVICE_CATALOG_DETAILED.yaml` - Источник истины (46 сервисов)
- `subsystems/SUBSYSTEMS_CATALOG.yaml` - 11 технических подсистем
- `systems/SYSTEMS_CATALOG.yaml` - 19 функциональных систем

---

## 💡 Ключевая идея

**ФУНКЦИОНАЛЬНЫЙ подход** (не технический):
- ❌ НЕ: "Инфраструктурная система" (БД + Gateway + Security)
- ✅ ДА: "Система безопасности", "Система хранения", "Система API"

Каждая функциональная система имеет **чёткое назначение**, понятное бизнесу.

---

## 🔍 Быстрый поиск

```bash
# Найти сервис
grep -r "service_name" catalogs/services/

# Найти подсистему
grep -r "subsystem_id" catalogs/subsystems/

# Найти функциональную систему
grep -r "system_id" catalogs/systems/
```

---

## ✅ Статус

**АРХИТЕКТУРА КАТАЛОГОВ ЗАВЕРШЕНА** ✅

Платформа теперь имеет:
- ✅ 46 сервисов документированы
- ✅ 11 технических подсистем определены
- ✅ 19 функциональных систем спроектированы
- ✅ Готово к генерации сценариев L1-L4

Подход: **ФУНКЦИОНАЛЬНЫЙ** (что делает) не **ТЕХНИЧЕСКИЙ** (что использует).

---

**Последнее обновление**: 2025-10-12
**Готовность**: 100% ✅
