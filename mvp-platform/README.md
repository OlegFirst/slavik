# AI Platform ISO 22301 - MVP

Полностью работающая платформа для Business Continuity Management (BCM) с AI-интеграцией.

## Архитектура

- **Frontend:** Next.js 14 + TypeScript + Tailwind CSS
- **Backend:** Python FastAPI + Supabase
- **Database:** Supabase PostgreSQL (с Row Level Security)
- **AI:** Claude API (Anthropic)

## Возможности

### Реализованные функции (MVP):

✅ **Аутентификация**
- Регистрация пользователей
- Вход в систему
- JWT токены
- Protected routes

✅ **Организации**
- Создание организации
- Просмотр/редактирование информации
- Управление бизнес-процессами
- AI-генерация процессов для индустрии

✅ **BIA (Business Impact Analysis)**
- Создание BIA анализов
- Добавление процессов
- Определение критичности
- AI-расчёт RTO/RPO
- Управление зависимостями
- Генерация анкет
- Сбор ответов
- Результаты и рекомендации

✅ **AI Интеграция**
- Генерация процессов по индустрии
- Расчёт RTO/RPO
- Анализ анкет BIA

## Структура проекта

```
mvp-platform/
├── backend/                 # FastAPI Backend
│   ├── routers/            # API endpoints
│   │   ├── auth.py         # Аутентификация
│   │   ├── organizations.py # Организации
│   │   └── bia.py          # BIA модуль
│   ├── models.py           # Pydantic модели
│   ├── database.py         # Supabase клиент
│   ├── auth.py             # JWT utilities
│   ├── ai_service.py       # Claude AI сервис
│   ├── config.py           # Конфигурация
│   ├── main.py             # FastAPI приложение
│   └── requirements.txt    # Python зависимости
│
├── frontend/               # Next.js Frontend
│   ├── src/
│   │   ├── app/           # Next.js 14 App Router
│   │   │   ├── page.tsx   # Главная
│   │   │   ├── login/     # Страница входа
│   │   │   ├── register/  # Страница регистрации
│   │   │   └── dashboard/ # Dashboard
│   │   ├── lib/
│   │   │   └── api.ts     # API client
│   │   └── store/
│   │       └── auth.ts    # Zustand store
│   └── package.json
│
├── database/
│   └── schema.sql         # База данных schema
│
├── docker-compose.yml     # Docker конфигурация
└── README.md              # Эта документация
```

## Установка и запуск

### Предварительные требования

1. **Supabase проект**
   - Создайте проект на https://supabase.com
   - Получите `SUPABASE_URL` и ключи API

2. **Anthropic API Key**
   - Получите ключ на https://console.anthropic.com

3. **Docker & Docker Compose** (опционально)
   - Или Python 3.11+ и Node.js 18+

### Шаг 1: Настройка базы данных

1. Откройте Supabase SQL Editor
2. Выполните скрипт из `database/schema.sql`
3. Это создаст все таблицы, индексы, RLS policies и seed data

### Шаг 2: Backend setup

```bash
cd mvp-platform/backend

# Создайте .env файл
cp .env.example .env

# Отредактируйте .env и заполните:
# - SUPABASE_URL
# - SUPABASE_ANON_KEY
# - SUPABASE_SERVICE_ROLE_KEY
# - DATABASE_URL
# - JWT_SECRET (сгенерируйте: openssl rand -hex 32)
# - ANTHROPIC_API_KEY

# Установите зависимости
pip install -r requirements.txt

# Запустите backend
python main.py
```

Backend запустится на http://localhost:8000

API документация: http://localhost:8000/docs

### Шаг 3: Frontend setup

```bash
cd mvp-platform/frontend

# Создайте .env.local файл
cp .env.local.example .env.local

# Отредактируйте .env.local:
# NEXT_PUBLIC_API_URL=http://localhost:8000

# Установите зависимости
npm install

# Запустите frontend
npm run dev
```

Frontend запустится на http://localhost:3000

### Альтернатива: Docker Compose

```bash
cd mvp-platform

# Создайте .env файл с переменными
cp backend/.env.example .env

# Заполните .env

# Запустите
docker-compose up --build
```

## Использование

### 1. Регистрация

1. Откройте http://localhost:3000
2. Перейдите на "Register"
3. Заполните:
   - Email
   - Password (минимум 8 символов)
   - Full Name (опционально)
   - Organization Name (опционально)
4. Нажмите "Create account"

### 2. Вход

1. Используйте email и password
2. После входа вы попадёте в Dashboard

### 3. Создание организации

1. В Dashboard нажмите "Create Organization"
2. Заполните:
   - Name
   - Industry (Healthcare, Finance, etc.)
   - Size (количество сотрудников)
   - Country
   - Description
3. Сохраните

### 4. Создание BIA

1. В Dashboard нажмите "Create New BIA"
2. Укажите:
   - Name (например "Q1 2025 BIA")
   - Collection Method (Questionnaire/Document Upload/etc.)
3. BIA создан! Теперь добавьте процессы

### 5. Добавление процессов

**Вручную:**
1. Откройте BIA
2. "Add Process"
3. Заполните: Name, Description, Criticality

**С AI:**
1. Используйте "Generate Processes (AI)"
2. AI предложит типичные процессы для вашей индустрии
3. Выберите нужные

### 6. Расчёт RTO/RPO

1. Для каждого процесса нажмите "Calculate RTO (AI)"
2. AI рассчитает рекомендации на основе:
   - Индустрии
   - Критичности процесса
   - Лучших практик

### 7. Анкета BIA

1. Генерируйте анкету
2. Заполните ответы
3. AI проанализирует и создаст рекомендации

## API Endpoints

### Authentication
- `POST /api/auth/register` - Регистрация
- `POST /api/auth/login` - Вход
- `GET /api/auth/me` - Текущий пользователь

### Organizations
- `POST /api/organizations` - Создать организацию
- `GET /api/organizations/my` - Моя организация
- `GET /api/organizations/{id}` - Детали организации
- `PATCH /api/organizations/{id}` - Обновить
- `POST /api/organizations/{id}/processes` - Создать процесс
- `GET /api/organizations/{id}/processes` - Список процессов
- `POST /api/organizations/{id}/processes/generate-ai` - AI генерация

### BIA
- `POST /api/bia?org_id={id}` - Создать BIA
- `GET /api/bia?org_id={id}` - Список BIA
- `GET /api/bia/{id}` - Детали BIA
- `PATCH /api/bia/{id}` - Обновить BIA
- `POST /api/bia/{id}/processes` - Добавить процесс
- `GET /api/bia/{id}/processes` - Список процессов
- `PATCH /api/bia/{id}/processes/{pid}` - Обновить процесс
- `POST /api/bia/{id}/questionnaire/generate` - Генерация анкеты
- `POST /api/bia/{id}/questionnaire/answers` - Отправить ответы
- `POST /api/bia/{id}/ai/calculate-rto` - AI расчёт RTO

Полная документация: http://localhost:8000/docs

## Database Schema

### Основные таблицы:

- `user_profiles` - Профили пользователей
- `organizations` - Организации
- `organization_departments` - Отделы
- `organization_processes` - Бизнес-процессы
- `bia_analyses` - BIA анализы
- `bia_processes` - Процессы в BIA
- `bia_dependencies` - Зависимости процессов
- `bia_questions` - Вопросы анкеты
- `bia_answers` - Ответы на анкету
- `bia_findings` - Результаты и рекомендации
- `ai_prompts` - Шаблоны промптов для AI
- `ai_logs` - Логи использования AI
- `audit_log` - Аудит действий

Row Level Security (RLS) обеспечивает, что пользователи видят только свои данные.

## Технические особенности

### Backend
- **FastAPI** - современный асинхронный framework
- **Supabase** - managed PostgreSQL + Auth
- **SQLAlchemy** - не используется, прямые запросы через Supabase client
- **Claude API** - для AI функций
- **JWT** - для аутентификации
- **Pydantic** - валидация данных

### Frontend
- **Next.js 14** - App Router
- **TypeScript** - типизация
- **Tailwind CSS** - стилизация
- **Zustand** - state management (легче чем Redux)
- **Axios** - HTTP клиент
- **React Hook Form** - работа с формами
- **React Hot Toast** - уведомления

### Security
- JWT токены
- Password hashing (bcrypt)
- Row Level Security в БД
- CORS protection
- Environment variables для секретов

## Что можно добавить (V2)

**Модули:**
- Gap Analysis (анализ соответствия ISO 22301)
- Risk Assessment (оценка рисков)
- Plans Management (планы восстановления)
- Compliance Tracking (мониторинг compliance)

**Features:**
- Document upload + OCR + AI extraction
- ERP integration (Odoo, SAP)
- Reports generation (PDF/Excel)
- Monte Carlo simulation для финансового impact
- Dependency graph visualization
- Continuous monitoring & alerts
- Multi-user/roles (Auditor, Learner, Sponsor)
- Notifications (email, in-app)

**UI/UX:**
- BIA wizard (5-step process)
- Interactive dependency graph
- Charts & dashboards
- Dark mode
- Mobile responsive

## Troubleshooting

### Backend не запускается
- Проверьте .env файл
- Убедитесь что Supabase credentials правильные
- Проверьте что порт 8000 свободен

### Frontend не может подключиться к API
- Проверьте NEXT_PUBLIC_API_URL в .env.local
- Убедитесь что backend запущен
- Проверьте CORS settings в backend

### Ошибки авторизации
- Проверьте JWT_SECRET в backend .env
- Попробуйте logout/login снова
- Проверьте что Supabase Auth настроена

### AI не работает
- Проверьте ANTHROPIC_API_KEY
- Убедитесь что у вас есть кредиты на Anthropic
- Проверьте ai_logs в БД для деталей

## Поддержка

Для вопросов и багов создавайте issue в репозитории.

## Лицензия

MIT
