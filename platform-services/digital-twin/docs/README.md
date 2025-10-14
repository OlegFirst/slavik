# 🎯 Digital Twin Universal Service

**Production-ready BCM Digital Twin API with integrated Queue Theory, Advanced AI, and comprehensive simulation engines.**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue.svg)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-7-red.svg)](https://redis.io/)
[![Tests](https://img.shields.io/badge/Tests-150+-success.svg)](tests/)

---

## 🚀 Quick Start (5 минут)

```bash
# 1. Клонируем/переходим в папку
cd /Users/MD/ISO-22301/sandbox/services-v2/digital-twin

# 2. Копируем .env
cp .env.example .env

# 3. Запускаем все сервисы
docker-compose up -d

# 4. Применяем миграции
docker-compose exec api python -m alembic upgrade head

# 5. Открываем Swagger UI
open http://localhost:8000/docs
```

**Готово!** API работает 🎉

---

## 📦 Что внутри

### 🎯 Основные фичи:
- ✅ **Multi-tenant Architecture** - Полная изоляция данных между клиентами
- ✅ **JWT Authentication** - Безопасная авторизация
- ✅ **PostgreSQL + Redis** - Надежное хранение + быстрый кеш
- ✅ **13 API Routers** - Полный REST API
- ✅ **150+ Tests** - Комплексное покрытие тестами

### 🔬 Движки симуляции (8 engines):

1. **Queue Theory Engine** ⭐⭐⭐⭐⭐
   - M/M/c queue simulation
   - Erlang C formula
   - Mathematical BIA analysis

2. **Advanced AI Generator** ⭐⭐⭐⭐⭐
   - LLM-powered scenarios
   - Learning loop
   - Context-aware

3. **Monte Carlo Engine**
4. **Simulation Engine**
5. **Prediction Engine**
6. **Metrics Engine**
7. **TOC Engine**
8. **Impact Passport Engine**

---

## 📚 API Endpoints

### Organizations
- `POST /api/v1/organizations/` - Создать
- `GET /api/v1/organizations/{id}` - Получить
- `GET /api/v1/organizations/{id}/insights` - AI Insights ⭐ NEW

### BIA & Scenarios
- `POST /api/v1/bia/queue-theory` - Queue Theory BIA ⭐ NEW
- `POST /api/v1/scenarios/ai-generate-advanced` - Advanced AI ⭐ NEW
- `POST /api/v1/scenarios/learn-from-exercise` - Learning Loop ⭐ NEW

**Полный список:** http://localhost:8000/docs

---

## 📖 Документация

- [DEPLOYMENT.md](DEPLOYMENT.md) - Руководство по деплою
- [TESTS_COMPLETE.md](TESTS_COMPLETE.md) - Информация о тестах
- [QUEUE_THEORY_INTEGRATION.md](QUEUE_THEORY_INTEGRATION.md) - Queue Theory
- [ADVANCED_AI_INTEGRATION.md](ADVANCED_AI_INTEGRATION.md) - Advanced AI
- [FRONTEND_INTEGRATION_COMPLETE.md](FRONTEND_INTEGRATION_COMPLETE.md) - Frontend

---

## 🧪 Тестирование

```bash
# Все тесты
pytest

# Юнит-тесты (без БД)
pytest tests/unit/ -v

# С coverage
pytest --cov=. --cov-report=html
```

**150+ тестов** покрывают все компоненты

---

## 🎊 Status

**✅ PRODUCTION READY**

- 91+ Python files
- 8 simulation engines
- 13 API routers
- 150+ tests
- Full Docker support

**Ready to deploy!** 🚀

---

**Built with ❤️ for BCM professionals**
