# Пошаговая инструкция по установке и запуску MVP Platform

## Шаг 1: Настройка Supabase

1. **Создайте проект на Supabase**
   - Перейдите на https://supabase.com
   - Нажмите "New Project"
   - Выберите организацию и регион
   - Укажите имя проекта и пароль для БД
   - Дождитесь создания (2-3 минуты)

2. **Получите credentials**
   - Откройте Settings → API
   - Скопируйте:
     * `Project URL` (это SUPABASE_URL)
     * `anon public` key (это SUPABASE_ANON_KEY)
     * `service_role` key (это SUPABASE_SERVICE_ROLE_KEY)

3. **Примените database schema**
   - Откройте SQL Editor в Supabase
   - Создайте новый запрос
   - Скопируйте содержимое `database/schema.sql`
   - Выполните (Run)
   - Убедитесь что нет ошибок

4. **Настройте Authentication**
   - Authentication → Providers
   - Убедитесь что Email включен
   - Site URL: http://localhost:3000
   - Redirect URLs: http://localhost:3000/*

## Шаг 2: Получение Anthropic API Key

1. Перейдите на https://console.anthropic.com
2. Зарегистрируйтесь или войдите
3. Settings → API Keys
4. Create Key
5. Скопируйте ключ (сохраните, он показывается один раз)

## Шаг 3: Backend Setup

1. **Перейдите в директорию backend**
   ```bash
   cd /Users/MD/AI-Platform-ISO/mvp-platform/backend
   ```

2. **Создайте .env файл**
   ```bash
   cp .env.example .env
   ```

3. **Заполните .env** (откройте в редакторе)
   ```env
   ENVIRONMENT=development

   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_ANON_KEY=your-anon-key-here
   SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here

   DATABASE_URL=postgresql://postgres:your-db-password@db.your-project.supabase.co:5432/postgres

   JWT_SECRET=your-secret-key-here
   JWT_ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   REFRESH_TOKEN_EXPIRE_DAYS=7

   API_HOST=0.0.0.0
   API_PORT=8000
   CORS_ORIGINS=http://localhost:3000

   ANTHROPIC_API_KEY=your-anthropic-key-here
   CLAUDE_MODEL=claude-3-5-sonnet-20241022

   LOG_LEVEL=INFO
   ```

4. **Сгенерируйте JWT_SECRET**
   ```bash
   openssl rand -hex 32
   ```
   Скопируйте результат в JWT_SECRET

5. **Установите зависимости**
   ```bash
   pip3 install -r requirements.txt
   ```

   Если pip3 не найден:
   ```bash
   python3 -m pip install -r requirements.txt
   ```

6. **Запустите backend**
   ```bash
   python3 main.py
   ```

   Вы должны увидеть:
   ```
   INFO:     Started server process
   INFO:     Uvicorn running on http://0.0.0.0:8000
   ```

7. **Проверьте API**
   - Откройте http://localhost:8000
   - Должно показать: `{"message": "AI Platform ISO 22301 - MVP", ...}`
   - Откройте http://localhost:8000/docs
   - Должен открыться Swagger UI с API документацией

## Шаг 4: Frontend Setup

1. **Откройте новый терминал**

2. **Перейдите в директорию frontend**
   ```bash
   cd /Users/MD/AI-Platform-ISO/mvp-platform/frontend
   ```

3. **Создайте .env.local**
   ```bash
   cp .env.local.example .env.local
   ```

4. **Заполните .env.local**
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

5. **Установите зависимости**
   ```bash
   npm install
   ```

   Это займёт 2-3 минуты

6. **Запустите frontend**
   ```bash
   npm run dev
   ```

   Вы должны увидеть:
   ```
   ready - started server on 0.0.0.0:3000, url: http://localhost:3000
   ```

7. **Откройте приложение**
   - Перейдите на http://localhost:3000
   - Должна открыться страница приложения

## Шаг 5: Первый запуск

1. **Регистрация**
   - Нажмите "Register"
   - Заполните форму:
     * Email: test@example.com
     * Password: password123
     * Full Name: Test User
     * Organization Name: Test Organization
   - Нажмите "Create account"
   - Вы будете автоматически залогинены и перенаправлены на Dashboard

2. **Проверка Dashboard**
   - Должен отобразиться ваш email вверху
   - Должна быть секция "Organization" с данными вашей организации
   - Кнопка "Create New BIA"

3. **Создание BIA**
   - Нажмите "Create New BIA"
   - Укажите имя: "Test BIA"
   - Выберите метод: Questionnaire
   - Нажмите Create

4. **Тестирование AI**
   - В организации попробуйте "Generate Processes (AI)"
   - AI должен предложить процессы для вашей индустрии
   - Или попробуйте "Calculate RTO (AI)" для процесса

## Troubleshooting

### Backend ошибки

**ModuleNotFoundError: No module named 'fastapi'**
```bash
cd backend
pip3 install -r requirements.txt
```

**Port 8000 already in use**
```bash
# Найти процесс на порту 8000
lsof -ti:8000
# Убить процесс
kill -9 <PID>
```

**Supabase connection error**
- Проверьте SUPABASE_URL и ключи
- Убедитесь что schema применён
- Проверьте интернет соединение

### Frontend ошибки

**Error: Cannot find module 'next'**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**API connection error**
- Убедитесь что backend запущен на 8000
- Проверьте NEXT_PUBLIC_API_URL в .env.local
- Проверьте CORS в backend

**Port 3000 already in use**
```bash
# Убить процесс на порту 3000
lsof -ti:3000 | xargs kill -9
```

### Database ошибки

**RLS policy violation**
- Убедитесь что вы используете правильный токен
- Logout/Login снова
- Проверьте что RLS policies применены из schema.sql

**Table does not exist**
- Убедитесь что schema.sql был выполнен полностью
- Проверьте SQL Editor в Supabase на ошибки

## Альтернативный запуск: Docker Compose

Если у вас установлен Docker:

1. **Перейдите в корень проекта**
   ```bash
   cd /Users/MD/AI-Platform-ISO/mvp-platform
   ```

2. **Создайте .env в корне**
   ```bash
   # Скопируйте все переменные из backend/.env
   ```

3. **Запустите**
   ```bash
   docker-compose up --build
   ```

4. **Готово!**
   - Frontend: http://localhost:3000
   - Backend: http://localhost:8000

## Проверка работоспособности

Чеклист после установки:

- [ ] Backend запущен на http://localhost:8000
- [ ] Frontend запущен на http://localhost:3000
- [ ] API docs доступна на http://localhost:8000/docs
- [ ] Можно зарегистрироваться
- [ ] Можно войти
- [ ] Dashboard показывает данные
- [ ] Можно создать организацию
- [ ] Можно создать BIA
- [ ] AI генерация процессов работает

Если все пункты выполнены - установка успешна!

## Следующие шаги

1. Изучите API documentation: http://localhost:8000/docs
2. Создайте свою организацию с реальными данными
3. Добавьте процессы
4. Создайте BIA анализ
5. Попробуйте AI функции

Удачи! 🚀
