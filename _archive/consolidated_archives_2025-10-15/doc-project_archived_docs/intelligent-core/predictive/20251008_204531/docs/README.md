# Predictive Journey Service - Документация

## 📚 Оглавление

### Основная Документация

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Архитектура системы
  - Компоненты и их взаимодействие
  - Алгоритм предсказаний
  - Схема данных

- **[MAGIC_COMPLETE.md](MAGIC_COMPLETE.md)** - "Магические" функции
  - 90-day journey prediction
  - Certification timeline
  - Proactive recommendations
  - Expert demand forecasting

- **[INTEGRATION_COMPLETE.md](INTEGRATION_COMPLETE.md)** - Интеграция
  - Case Library integration
  - Notification Service
  - Daily digest scheduler

### ⚠️ Критичная Документация

- **[ANALYSIS_AND_IMPROVEMENTS.md](ANALYSIS_AND_IMPROVEMENTS.md)** - ОБЯЗАТЕЛЬНО К ПРОЧТЕНИЮ!
  - 🔴 Критичные проблемы (database session management, missing seed data)
  - 🟡 Важные улучшения (caching, error handling, config)
  - 🟢 Будущие улучшения (ML enhancement, accuracy tracking)
  - ✅ Quick wins (можно сделать сегодня)

## 🚀 Быстрый Старт

1. Прочитай [ANALYSIS_AND_IMPROVEMENTS.md](ANALYSIS_AND_IMPROVEMENTS.md) - там критичные баги!
2. Изучи [ARCHITECTURE.md](ARCHITECTURE.md) для понимания системы
3. Смотри [MAGIC_COMPLETE.md](MAGIC_COMPLETE.md) для примеров использования

## ⚠️ Важно

**Перед запуском в production:**
- Исправь database session management (P0)
- Добавь seed data generator (P0)
- Реализуй caching (P1)
- Добавь error handling (P1)

См. полный список в [ANALYSIS_AND_IMPROVEMENTS.md](ANALYSIS_AND_IMPROVEMENTS.md)
