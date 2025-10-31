# 🏢 MSP Server - Managed Service Provider
## Централизованное управление Universal Orchestration Platform

**MSP Server** - это корпоративный сервер управления для Universal Orchestration Platform с интеграцией **официального SDK Anthropic Claude**.

---

## 🚀 Возможности

### ✅ **Управление Пользователями и Проектами**
- Регистрация и аутентификация пользователей
- Управление проектами и доступом
- Role-based access control (admin, user, viewer)
- API key management

### ✅ **Оркестрация Задач**
- Централизованная обработка задач
- Load balancing между orchestrator instances
- Мониторинг статуса задач
- Background processing

### ✅ **AI Сервисы (Anthropic Claude)**
- 🧠 **AI анализ проектов** - структурный анализ с помощью Claude
- 💡 **AI рекомендации** - предложения по улучшению
- 📚 **AI объяснения архитектуры** - понятные описания
- 🔍 **AI оценка качества кода** - детальная оценка

### ✅ **Мониторинг и Аналитика**
- Real-time dashboard
- Системная статистика
- Analytics и reporting
- Health monitoring

### ✅ **Инспектор MSP**
- Автоматическая диагностика
- Проверка всех компонентов
- Генерация отчетов
- Performance мониторинг

---

## 📋 Установка и Настройка

### **1. Установка зависимостей:**
```bash
cd msp_server
pip install -r requirements.txt
```

### **2. Настройка Anthropic API:**
```bash
# Установите ваш API key
export ANTHROPIC_API_KEY="your-anthropic-api-key-here"

# Или создайте .env файл
echo "ANTHROPIC_API_KEY=your-api-key" > .env
```

### **3. Запуск MSP Server:**
```bash
# Запуск на порту 8080
python msp_main.py

# Или с uvicorn
uvicorn msp_main:app --host 0.0.0.0 --port 8080 --reload
```

### **4. Проверка с помощью Inspector:**
```bash
# Полная инспекция
python msp_inspector.py

# С сохранением отчета
python msp_inspector.py --save-report

# Другой URL
python msp_inspector.py --url http://your-server:8080
```

---

## 🌐 Web Dashboard

Перейдите на **http://localhost:8080** для доступа к MSP Dashboard:

### **📊 Основные метрики:**
- Активные пользователи
- Количество проектов
- Выполненные задачи
- Активные orchestrator instances

### **🖥️ Управление Instance'ами:**
- Статус всех orchestrator'ов
- Мониторинг загрузки
- Health checks
- Version tracking

### **👥 Управление пользователями:**
- Список пользователей
- Роли и права доступа
- История активности
- Статистика использования

---

## 📡 API Endpoints

### **🔐 Аутентификация:**
```bash
# Регистрация пользователя
POST /api/users/register
{
  "username": "user",
  "email": "user@example.com",
  "role": "user"
}

# Ответ включает API key для дальнейшей аутентификации
```

### **📊 Проекты:**
```bash
# Создание проекта
POST /api/projects/create
Headers: Authorization: Bearer YOUR_API_KEY
{
  "name": "My Project",
  "description": "Project description"
}
```

### **🤖 AI Сервисы (Anthropic):**
```bash
# AI анализ проекта
POST /api/ai/analyze-project
Headers: Authorization: Bearer YOUR_API_KEY
{
  "project_data": {
    "files": [...],
    "structure": {...}
  }
}

# AI рекомендации
POST /api/ai/recommendations
Headers: Authorization: Bearer YOUR_API_KEY
{
  "analysis_data": {...}
}

# AI объяснение архитектуры
POST /api/ai/explain-architecture
Headers: Authorization: Bearer YOUR_API_KEY
{
  "architecture_data": {...}
}

# AI оценка качества кода
POST /api/ai/assess-quality
Headers: Authorization: Bearer YOUR_API_KEY
{
  "code_data": {...}
}
```

### **⚙️ Задачи:**
```bash
# Отправка задачи
POST /api/tasks/submit
Headers: Authorization: Bearer YOUR_API_KEY
{
  "user_id": "user-id",
  "project_id": "project-id",
  "task_type": "analyze",
  "input_data": {...}
}

# Статус задачи
GET /api/tasks/{task_id}/status
Headers: Authorization: Bearer YOUR_API_KEY
```

### **📈 Мониторинг:**
```bash
# Системная статистика
GET /api/stats

# Список instances
GET /api/instances

# Health check
GET /health
```

---

## 🔧 Конфигурация

### **Environment Variables:**
```bash
ANTHROPIC_API_KEY=your-anthropic-api-key  # Обязательно для AI функций
MSP_PORT=8080                             # Порт сервера (по умолчанию 8080)
MSP_HOST=0.0.0.0                         # Host binding
LOG_LEVEL=INFO                            # Уровень логирования
```

### **Demo Data:**
При первом запуске автоматически создаются demo пользователи:
- **Admin**: `username: admin`, проверьте логи для API key
- **Demo User**: `username: demo`, проверьте логи для API key

---

## 🔍 MSP Inspector

Автоматический инспектор для проверки состояния MSP Server:

### **Основные проверки:**
- ✅ **Connectivity** - доступность сервера
- ✅ **Health Status** - состояние сервисов
- ✅ **Anthropic Service** - работа AI сервиса
- ✅ **API Endpoints** - функциональность API
- ✅ **Orchestrator Instances** - состояние orchestrator'ов
- ✅ **Users & Projects** - данные пользователей
- ✅ **Performance** - время ответа
- ✅ **Security** - базовые проверки безопасности

### **Использование:**
```bash
# Быстрая проверка
python msp_inspector.py

# Полная проверка с отчетом
python msp_inspector.py --save-report --output my_report.json

# Проверка production сервера
python msp_inspector.py --url https://your-msp-server.com
```

### **Коды выхода:**
- `0` - Все проверки пройдены
- `1` - Некритические проблемы
- `2` - Критические проблемы

---

## 🏗️ Архитектура

```
┌─────────────────────────────────────────────────────────────┐
│                    MSP Dashboard                            │
│              (Web Interface: :8080)                        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   MSP Server Core                           │
├─────────────────────────────────────────────────────────────┤
│  • User Management      • Project Management               │
│  • Task Orchestration   • Analytics & Monitoring           │
│  • API Gateway          • Security & Auth                  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                 Anthropic AI Service                        │
├─────────────────────────────────────────────────────────────┤
│  • Project Analysis     • Code Quality Assessment          │
│  • Recommendations     • Architecture Explanations        │
│  • Claude SDK           • Structured Responses             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              Orchestrator Instances                         │
├─────────────────────────────────────────────────────────────┤
│  • Load Balancing       • Health Monitoring                │
│  • Task Distribution    • Result Collection                │
│  • Instance Registry    • Performance Tracking             │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Мониторинг

### **Real-time Metrics:**
- Active users и sessions
- Task processing rates
- Orchestrator instance health
- AI service usage statistics
- API response times

### **Alerting:**
- Critical instance failures
- API key issues
- Performance degradation
- Security events

### **Reporting:**
- Daily/weekly usage reports
- Performance analytics
- User activity summaries
- Cost tracking (AI API usage)

---

## 🔐 Безопасность

### **Аутентификация:**
- API key based authentication
- Role-based access control
- User session management
- Token expiration

### **Авторизация:**
- Project-level permissions
- Admin/user/viewer roles
- Resource access control
- Audit logging

### **Best Practices:**
- HTTPS recommended для production
- API rate limiting
- Input validation
- Error handling без exposure sensitive data

---

## 🚀 Production Deployment

### **Docker Deployment:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8080
CMD ["python", "msp_main.py"]
```

### **Environment Setup:**
```bash
# Production environment
export ANTHROPIC_API_KEY="prod-api-key"
export MSP_PORT=8080
export LOG_LEVEL=INFO

# For HTTPS
export MSP_SSL_CERT="/path/to/cert.pem"
export MSP_SSL_KEY="/path/to/key.pem"
```

### **Load Balancing:**
- Multiple MSP server instances
- Nginx reverse proxy
- Health check endpoints
- Session persistence

---

## 🎯 Использование

### **Типичный рабочий процесс:**

1. **Регистрация пользователя:**
   ```bash
   curl -X POST http://localhost:8080/api/users/register \
     -H "Content-Type: application/json" \
     -d '{"username":"developer","email":"dev@company.com","role":"user"}'
   ```

2. **Создание проекта:**
   ```bash
   curl -X POST http://localhost:8080/api/projects/create \
     -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{"name":"My App","description":"Production application"}'
   ```

3. **AI анализ проекта:**
   ```bash
   curl -X POST http://localhost:8080/api/ai/analyze-project \
     -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{"project_data":{"files":[...],"structure":{...}}}'
   ```

4. **Отправка задачи на обработку:**
   ```bash
   curl -X POST http://localhost:8080/api/tasks/submit \
     -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{"project_id":"proj-id","task_type":"analyze","input_data":{...}}'
   ```

5. **Мониторинг статуса:**
   ```bash
   curl http://localhost:8080/api/tasks/task-id/status \
     -H "Authorization: Bearer YOUR_API_KEY"
   ```

---

## 🔧 Troubleshooting

### **Частые проблемы:**

**Anthropic API не работает:**
```bash
# Проверьте API key
echo $ANTHROPIC_API_KEY

# Проверьте health
curl http://localhost:8080/health
```

**Orchestrator instances не подключены:**
```bash
# Зарегистрируйте instance
curl -X POST http://localhost:8080/api/instances/register \
  -H "Content-Type: application/json" \
  -d '{"instance_id":"main","url":"http://localhost:9000","version":"1.0.0"}'
```

**Inspector показывает ошибки:**
```bash
# Запустите детальную проверку
python msp_inspector.py --save-report
# Проверьте сгенерированный отчет
```

---

## 🎉 Заключение

MSP Server предоставляет корпоративный уровень управления для Universal Orchestration Platform с:

- ✅ **Централизованным управлением** пользователями и проектами
- ✅ **AI-powered анализом** через официальный Anthropic SDK
- ✅ **Автоматическим мониторингом** и диагностикой
- ✅ **Enterprise-ready** архитектурой и безопасностью
- ✅ **Комплексным инспектором** для проверки состояния

**Готов к использованию в production с полной поддержкой AI функций!** 🚀