# BCM Portal - Клиентский портал самообслуживания

## Обзор модуля

**Назначение**: Веб-портал самообслуживания для клиентов с AI-ассистентом, предоставляющий доступ к BCM сервисам, отчетам и аналитике.

**Расположение**: `core/odoo-18.0/addons/bcm_portal/`

## Ключевые компоненты

### PortalClient (bcm.portal.client)
**Файл**: `models/portal_client.py:18`

**Основные поля**:
- `client_id` (Many2one) - Связь с основным клиентом
- `portal_access_level` (Selection) - Уровень доступа (basic, premium, enterprise)
- `dashboard_config` (Text) - JSON конфигурация дашборда
- `ai_assistant_enabled` (Boolean) - Включение AI-ассистента
- `custom_branding` (Binary) - Кастомный брендинг
- `sso_enabled` (Boolean) - Single Sign-On
- `api_access_enabled` (Boolean) - Доступ к API

### PortalDashboard (bcm.portal.dashboard)
**Файл**: `models/portal_dashboard.py:25`

**Виджеты дашборда**:
- BCM метрики и KPI
- Статус планов непрерывности
- Активные инциденты
- Результаты тестирований
- Compliance статус
- Финансовые метрики BCM

### AIAssistant (bcm.portal.ai_assistant)
**Файл**: `models/ai_assistant.py:30`

**Возможности**:
- Ответы на вопросы по BCM
- Рекомендации по улучшению
- Анализ трендов и паттернов
- Помощь в планировании
- Интерпретация отчетов

### Контроллеры

#### PortalController
**Файл**: `controllers/portal_controller.py:15`

**Эндпоинты**:
```python
@http.route('/portal/dashboard', type='http', auth='portal')
def portal_dashboard(self)

@http.route('/portal/ai-chat', type='json', auth='portal')  
def ai_assistant_chat(self, message)

@http.route('/portal/reports', type='http', auth='portal')
def portal_reports(self, report_type)
```

## Функциональность портала

### Self-Service возможности:
- Просмотр BCM статуса в реальном времени
- Генерация отчетов по требованию
- Планирование и инициация тестирований
- Управление пользователями и правами
- Настройка уведомлений и алертов

### AI-ассистент функции:
- Чат-бот для BCM вопросов
- Анализ данных и трендов
- Рекомендации по оптимизации
- Проактивные предупреждения
- Помощь в принятии решений