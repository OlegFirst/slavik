# 🌐 Web/UI Documentation

Техническая документация веб-интерфейса и UI спецификации.

## 📚 Содержание

| Файл | Описание | Строк |
|------|----------|-------|
| [UI_TECHNICAL_SPECIFICATION.md](UI_TECHNICAL_SPECIFICATION.md) | Полная техническая спецификация UI | ~1,150 |
| [UI_Core_TZ.md](UI_Core_TZ.md) | Техническое задание core UI | ~1,470 |
| [PHASE_5_INTERFACE_SPECIFICATIONS.md](PHASE_5_INTERFACE_SPECIFICATIONS.md) | Спецификации интерфейса Phase 5 | ~1,380 |
| [FRONTEND_REQUIREMENTS.md](FRONTEND_REQUIREMENTS.md) | Требования к frontend | ~840 |
| [BCM-UX-Modules-Technical-Documentation.md](BCM-UX-Modules-Technical-Documentation.md) | UX модули техническая документация | ~870 |

## 🎯 Категории документации

### 1. Технические спецификации
**Файлы**:
- [UI_TECHNICAL_SPECIFICATION.md](UI_TECHNICAL_SPECIFICATION.md) - Полная UI спецификация
- [UI_Core_TZ.md](UI_Core_TZ.md) - ТЗ на core компоненты

**Содержит**:
- Структура компонентов
- Технические требования
- Архитектура UI
- Стандарты кодирования

### 2. Interface Requirements
**Файлы**:
- [FRONTEND_REQUIREMENTS.md](FRONTEND_REQUIREMENTS.md) - Общие требования
- [PHASE_5_INTERFACE_SPECIFICATIONS.md](PHASE_5_INTERFACE_SPECIFICATIONS.md) - Phase 5 спецификации

**Содержит**:
- Функциональные требования
- UI/UX требования
- Performance требования
- Accessibility требования

### 3. UX Documentation
**Файл**: [BCM-UX-Modules-Technical-Documentation.md](BCM-UX-Modules-Technical-Documentation.md)

**Содержит**:
- UX flows для каждого модуля
- User interactions
- Navigation patterns
- UI состояния

## 🎯 Для разных ролей

### Frontend Developer
1. [UI_TECHNICAL_SPECIFICATION.md](UI_TECHNICAL_SPECIFICATION.md) - технические детали
2. [UI_Core_TZ.md](UI_Core_TZ.md) - ТЗ на компоненты
3. См. также [Frontend Documentation](../frontend/) для Vue.js специфики

### UI/UX Designer
1. [BCM-UX-Modules-Technical-Documentation.md](BCM-UX-Modules-Technical-Documentation.md) - UX flows
2. [FRONTEND_REQUIREMENTS.md](FRONTEND_REQUIREMENTS.md) - требования к дизайну
3. См. также [Frontend UI/UX Guide](../frontend/clean/03_UI_UX_GUIDE.md)

### Project Manager
1. [PHASE_5_INTERFACE_SPECIFICATIONS.md](PHASE_5_INTERFACE_SPECIFICATIONS.md) - спецификации по фазам
2. [FRONTEND_REQUIREMENTS.md](FRONTEND_REQUIREMENTS.md) - общие требования

### QA Engineer
1. [UI_TECHNICAL_SPECIFICATION.md](UI_TECHNICAL_SPECIFICATION.md) - что тестировать
2. [FRONTEND_REQUIREMENTS.md](FRONTEND_REQUIREMENTS.md) - требования для тестов

## 🔄 Связь с другой документацией

### Frontend Documentation
Эта папка содержит **низкоуровневые UI спецификации и ТЗ**.

Для **высокоуровневой frontend документации** см.:
- [Frontend Documentation](../frontend/) - Vue.js архитектура
- [Frontend Clean](../frontend/clean/) - структурированная документация

### Отличия:
| web/ | frontend/ |
|------|-----------|
| Технические спецификации UI | Vue.js архитектура |
| ТЗ и requirements | Практические гайды |
| Low-level детали | High-level концепции |
| Для всех UI платформ | Специфично для Vue.js |

## 📊 Фазы разработки

Документация организована по фазам:
- **Phase 1-4**: Legacy (см. в файлах references)
- **Phase 5**: [PHASE_5_INTERFACE_SPECIFICATIONS.md](PHASE_5_INTERFACE_SPECIFICATIONS.md)

## 🔗 Связанная документация

- [Frontend Documentation](../frontend/) - Vue.js реализация
- [Frontend UI/UX Guide](../frontend/clean/03_UI_UX_GUIDE.md) - Design System
- [Business Logic](../business_logic/) - UI flows

---

**Последнее обновление**: 2025-09-28