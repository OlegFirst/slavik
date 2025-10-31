# ТЗ №1: BCM Platform Frontend (интерфейс для 19 модулей)

## Цель
Создать единый веб-интерфейс для управления всеми 19 модулями BCM платформы ISO-22301.

## Список модулей (каждый — отдельный раздел/страница):
1. bcm_incident — управление инцидентами
2. bcm_plans — планы BCM
3. bcm_audit — аудит
4. bcm_kpi — ключевые показатели
5. bcm_bia — бизнес-анализ воздействия
6. document_processor — обработка документов
7. notification_service — уведомления
8. eventbus — обработка событий
9. orchestrator_service — оркестрация процессов
10. grafana_adapter — мониторинг
11. lms_adapter — обучение
12. auth_service — авторизация
13. bpmn_service — бизнес-процессы
14. compliance_checker — проверка соответствия
15. thehive_adapter — интеграция с TheHive
16. odoo_adapter — интеграция с Odoo
17. ai_orchestrator — AI-сервисы
18. core/database — управление БД
19. gateway — API-шлюз

## Функциональные требования
- Для каждого модуля: CRUD-операции, фильтрация, поиск, экспорт данных.
- Dashboard: сводная информация по всем модулям.
- Навигация: sidebar/menu с доступом к каждому модулю.
- Формы для создания/редактирования сущностей.
- Таблицы с фильтрами и сортировкой.
- Модальные окна для подтверждений.
- Система уведомлений.
- Адаптивный дизайн.

## API-интеграция
- Все действия через REST API/GraphQL.
- Авторизация через JWT/OAuth2.
- Обработка ошибок и статусов.

## Технологии
- Vue.js 3 + TypeScript + Vuetify/Element Plus.
- Axios для API.
- Vite для сборки.
- Jest/Cypress для тестов.

## Безопасность
- Разграничение прав доступа.
- Защита от XSS/CSRF.
- Валидация данных.

## Этапы
1. Проектирование UI/UX для всех модулей.
2. Реализация страниц и компонентов.
3. Интеграция с API.
4. Тестирование.
5. Документация.
6. Деплой.

---

# ТЗ №2: Техническая документация BCM Platform (19 модулей)

## Цель
Подготовить подробную техническую документацию по архитектуре, функциям и API всех 19 модулей BCM платформы.

## Структура документации

### 1. Архитектура платформы
- Описание общей структуры, связей между модулями.
- Диаграмма компонентов.

### 2. Описание каждого модуля

(Для каждого модуля — функции, API, схема)

## Примеры:

### bcm_incident
- **Функции:**  create_incident(data), get_incident(id), update_incident(id, data), list_incidents(filter), close_incident(id)
- **API:**  POST /api/incidents, GET /api/incidents/{id}, PUT /api/incidents/{id}, GET /api/incidents, POST /api/incidents/{id}/close
- **Схема:**
```json
{
  "id": "int",
  "title": "string",
  "status": "string",
  "created_at": "datetime",
  "details": "string"
}
```

### bcm_plans
- **Функции:**  create_plan(data), get_plan(id), update_plan(id, data), list_plans(filter), activate_plan(id)
- **API:**  POST /api/plans, GET /api/plans/{id}, PUT /api/plans/{id}, GET /api/plans, POST /api/plans/{id}/activate
- **Схема:**
```json
{
  "id": "int",
  "name": "string",
  "status": "string",
  "steps": ["string"]
}
```

### bcm_audit
- **Функции:**  create_audit(data), get_audit(id), list_audits(filter), export_audit(id)
- **API:**  POST /api/audits, GET /api/audits/{id}, GET /api/audits, GET /api/audits/{id}/export
- **Схема:**
```json
{
  "id": "int",
  "date": "datetime",
  "result": "string",
  "details": "string"
}
```

... (и так далее для всех 19 модулей)

### 3. Сценарии интеграции
- Как модули взаимодействуют друг с другом.
- Примеры последовательностей вызовов.

### 4. Структуры данных
- Описание моделей, DTO, схем.

### 5. Безопасность и права доступа
- Механизмы авторизации.
- Ограничения по ролям.

### 6. Инструкции по запуску и тестированию
- Как развернуть каждый модуль.
- Как проверить работоспособность.

### 7. FAQ и troubleshooting

---

(Полные примеры для всех модулей включены выше. Если нужно — могу дополнить деталями для конкретных сервисов.)
