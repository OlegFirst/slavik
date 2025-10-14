# 🚀 Полный список сервисов BCM Platform (60+ компонентов)

## 🗄️ **БАЗЫ ДАННЫХ И ХРАНИЛИЩА (4 сервиса)**
1. **postgres** - Основная PostgreSQL база (порт 5432)
2. **redis** - Кэширование и очереди (порт 6379)
3. **rabbitmq** - Сообщения между сервисами (порты 5672, 15672)
4. **model_cache** - Кэш для AI моделей

## 🔐 **БЕЗОПАСНОСТЬ И АУТЕНТИФИКАЦИЯ (1 сервис)**
5. **keycloak** - SSO и управление ролями (порт 8080)

## 💼 **ОСНОВНЫЕ BCM СЕРВИСЫ (3 сервиса)**
6. **odoo** - Основная Odoo 18.0 ERP система (порт 8069)
7. **ai_orchestrator** - AI оркестратор (порт 8000)
8. **ai_control_center** - Центр управления AI (порт 8200)

## 🧠 **AI И ИНТЕЛЛЕКТ (15 сервисов)**
9. **bia_engine** - ML Business Impact Analysis (порт 8082)
10. **document_processor** - AI Document Intelligence (порт 8083)
11. **compliance_checker** - ISO 22301 автоматизация (порт 8084)
12. **pdca_assistant** - PDCA AI помощник (порт 8010)
13. **unified_ai_service** - Единый AI сервис (порт 8090)
14. **scenario_orchestrator** - Orchestrator сценариев (порт 8085)
15. **model_runner** - Локальная LLM (порт 8088)
16. **github_app** - GitHub App и Copilot (порт 8011)
17. **ai-consultant** - AI консультант для BCM анализа
18. **ai_workflow_optimizer** - Оптимизация AI workflows
19. **process_mining_service** - Process mining и анализ
20. **document_management** - Управление документооборотом
21. **knowledge-base** - База знаний с AI поиском
22. **bcm_content_training_bridge** - Мост для обучающего контента
23. **template_library** - Библиотека шаблонов

## 🌐 **API И ШЛЮЗЫ (4 сервиса)**
24. **unified_database_gateway** - Централизованный доступ к БД (порт 8888)
25. **unified_api_gateway** - Централизованный API роутер (порт 8777)
26. **crm_bridge** - Мост Odoo CRM (порт 8778)
27. **module_validator_api** - BCM Module Validation (порт 5001)

## 📋 **BACKEND АДАПТЕРЫ (8 сервисов)**
28. **bpmn_service** - BPMN Workflow сервис (порт 8005)
29. **lms_adapter** - LMS адаптер (порт 8006)
30. **thehive_adapter** - TheHive адаптер (порт 8007)
31. **grafana_adapter** - Grafana адаптер (порт 8008)
32. **eventbus** - Шина событий (порт 8001)
33. **document-processor** (adapter) - Обработка документов
34. **simulation** (adapter) - Симуляционный адаптер
35. **deployer** - Deployment сервис (порт 8009)

## 🖥️ **FRONTEND ПРИЛОЖЕНИЯ (7 сервисов)**
36. **admin_panel** - Основная админ панель React (порт 3001)
37. **admin_panel3** - Дополнительная админ панель
38. **unified-bcm-platform** - Объединенная BCM платформа Next.js (порт 3002)
39. **bcm-marketplace** - Маркетплейс BCM решений
40. **web_portal_enhanced** - Улучшенный веб-портал Vue.js (порт 3000)
41. **web_portal** - Базовый веб-портал Vue.js
42. **digital-twin-platform** - Платформа цифровых двойников (Node.js)

## 📧 **КОММУНИКАЦИИ (2 сервиса)**
43. **notification_service** - Сервис уведомлений (порт 8002)
44. **mailhog** - Email тестирование (порты 1025, 8025)

## 📊 **МОНИТОРИНГ (4 сервиса)**
45. **monitoring_service** - Централизованный мониторинг (порт 8779)
46. **grafana** - Мониторинг дашборды (порт 3003)
47. **prometheus** - Метрики (порт 9090) *из monitoring compose*
48. **realtime_websocket** - Real-time WebSocket коммуникации

## 🔧 **ИНФРАСТРУКТУРА (2 сервиса)**
49. **traefik** - Reverse proxy (порты 80, 443, 8888)
50. **nginx** - Веб-сервер и балансировщик нагрузки

## 🎯 **СИМУЛЯТОРЫ И УПРАЖНЕНИЯ (4 сервиса)**
51. **exercise_simulators** - Симуляторы упражнений (порт 8094)
52. **jaamsim** - Discrete Event Simulation (порт 5900)
53. **simulation_adapter** - Координация симуляций (порт 8012)
54. **bcm_mcp_server** - MCP сервер для BCM (порт 8087)

## 🔗 **ИНТЕГРАЦИИ (10 сервисов)**
55. **thehive** - Интеграция с TheHive для инцидентов
56. **lms** - Интеграция с системами обучения
57. **moodle** - Интеграция с Moodle LMS
58. **mcp-server** - Model Context Protocol сервер
59. **opengrc_oscal** - Интеграция с OpenGRC OSCAL
60. **governance** - Система управления и соответствия
61. **gateway** - Шлюз для внешних интеграций
62. **simulation** - Интеграция симуляций
63. **exercise_simulators** - Симуляторы упражнений
64. **nginx** - Конфигурация веб-шлюза

## 🏢 **ODOO BCM МОДУЛИ (28 модулей)**
65. **bcm_base** - Базовые функции BCM (фундамент всех модулей)
66. **bcm_core** - Фундаментальный модуль BCM с контекстом организации
67. **bcm_context** - Контекст организации
68. **bcm_risk_management** - Управление рисками и оценка угроз
69. **bcm_bia** - Business Impact Analysis
70. **bcm_plans** - Планы обеспечения непрерывности
71. **bcm_incident** - Управление инцидентами (базовый)
72. **bcm_incident_management** - Расширенное управление инцидентами
73. **bcm_exercise** - Учения и тренировки
74. **bcm_audit** - Аудит и соответствие ISO 22301
75. **bcm_training** - Модуль обучения и повышения квалификации
76. **bcm_governance** - Управление и корпоративное соответствие
77. **bcm_kpi** - Ключевые показатели эффективности BCM
78. **bcm_reporting** - Отчетность и аналитика
79. **bcm_templates** - Библиотека шаблонов документов
80. **bcm_community** - Сообщество пользователей BCM
81. **bcm_portal** - Портал пользователей
82. **bcm_admin_website** - Административный веб-сайт
83. **bcm_clients** - Управление клиентами BCM
84. **bcm_digital_twin_core** - Ядро цифрового двойника организации
85. **bcm_corporate_twin** - Корпоративный цифровой двойник
86. **bcm_digital_copy_manager** - Менеджер цифровых копий
87. **bcm_ai_control** - Центр управления цифровым организмом AI
88. **bcm_ai_consultant** - AI консультант для BCM
89. **bcm_ai_twin_orchestrator** - Оркестратор AI двойников
90. **bcm_intelligent_base** - Интеллектуальная база знаний
91. **bcm_scenario_hub** - Центр сценариев и упражнений
92. **bcm_config** - Конфигурация системы (устаревший)

---

## 📝 **ДОПОЛНИТЕЛЬНАЯ ИНФОРМАЦИЯ**

### 🎯 **Активные порты:**
- **Frontend**: 3000, 3001, 3003
- **Backend**: 8000-8094, 8200, 8777-8779, 8888-8889
- **Infrastructure**: 80, 443, 1025, 5432, 5672, 6379, 8025, 8080, 9090
- **Development**: 5001, 5900, 8069, 15672

### 🔄 **Основные связи:**
- Все сервисы подключены к **postgres**, **redis**, **rabbitmq**
- **AI сервисы** координируются через **ai_orchestrator**
- **API Gateway** объединяет все backend сервисы
- **EventBus** обеспечивает межсервисное взаимодействие

### 📈 **Статистика:**
- **92+ компонентов** всего
- **20+ сервисных портов** для внешнего доступа
- **15 AI/ML** сервисов
- **8 адаптеров** для интеграции
- **28 Odoo BCM модулей**
- **10 интеграционных** решений
- **7 frontend** приложений
- **4 сервиса** мониторинга

### ⚠️ **Выявленные проблемы:**
- **Дублирование сервисов**: ~30% функционала дублируется
- **Разрозненная структура**: Сервисы распределены по 6 директориям
- **Несогласованность технологий**: Python/Node.js/Go без единого стандарта
- **Отсутствие Service Mesh**: Нет единого управления коммуникациями
- **Фрагментация frontend**: 7 отдельных UI приложений

---

## 🚀 **Быстрый запуск**

### Запуск всех сервисов:
```bash
docker-compose up -d
```

### Запуск основных сервисов:
```bash
docker-compose -f docker-compose.yml up -d postgres redis rabbitmq odoo
```

### Запуск с мониторингом:
```bash
docker-compose -f docker-compose.yml -f monitoring/docker-compose.monitoring.yml up -d
```

### Проверка статуса:
```bash
docker-compose ps
```

---

## 📍 **Основные URL для доступа:**

| Сервис | URL | Описание |
|--------|-----|----------|
| Odoo | http://localhost:8069 | Основная BCM платформа |
| Admin Panel | http://localhost:3001 | Административная панель |
| Web Portal | http://localhost:3000 | Веб-портал |
| Unified BCM Dashboard | http://localhost:3002 | Объединенная BCM платформа (Next.js) |
| Grafana | http://localhost:3003 | Мониторинг дашборды |
| Keycloak | http://localhost:8080 | SSO управление |
| MailHog | http://localhost:8025 | Email UI |
| RabbitMQ | http://localhost:15672 | RabbitMQ Management |
| AI Control | http://localhost:8200 | AI Control Center |
| Traefik | http://localhost:8888 | Traefik Dashboard |
| BCM Marketplace | http://localhost:3004 | Маркетплейс BCM решений |

---

## 🛠️ **Управление сервисами**

### Остановка всех сервисов:
```bash
docker-compose down
```

### Перезапуск сервиса:
```bash
docker-compose restart <service-name>
```

### Просмотр логов:
```bash
docker-compose logs -f <service-name>
```

### Очистка данных:
```bash
docker-compose down -v
```

---

## 🔄 **План унификации и оптимизации**

Разработан детальный план консолидации и унификации всех сервисов:

📄 **[Полная архитектура и план унификации →](./ARCHITECTURE_FULL_SERVICES.md)**

### Ключевые цели унификации:
- ✅ Сокращение количества компонентов с 92+ до ~45 (-50%)
- ✅ Устранение дублирования функционала
- ✅ Стандартизация технологического стека
- ✅ Создание единого API Gateway
- ✅ Консолидация frontend приложений (с 7 до 3)
- ✅ Оптимизация использования ресурсов (-35% RAM/CPU)
- ✅ Упрощение управления и поддержки

### Этапы миграции:
1. **Q1 2025**: Подготовка и аудит
2. **Q2 2025**: Унификация core services
3. **Q3 2025**: Консолидация AI сервисов
4. **Q4 2025**: Frontend и production deployment

---

*Последнее обновление: 2025-01-29*