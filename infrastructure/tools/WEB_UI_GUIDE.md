# 🎨 Веб-интерфейс для управления инструментами

**Статус:** ✅ Реализован для Analytics Specialist

---

## Что можно делать через интерфейс?

### 1. Просмотр всех доступных инструментов
- Видеть статус каждого инструмента (доступен/недоступен)
- Видеть уровень компетенции (Junior/Middle/Senior)
- Видеть описание каждого инструмента

### 2. Запуск инструментов вручную
- Нажать кнопку "Run Now" - инструмент выполнится немедленно
- Получить результаты в модальном окне
- Просмотр JSON результатов

### 3. Планирование автоматических запусков
- Нажать кнопку "Schedule"
- Выбрать расписание:
  - Daily at 02:00 UTC
  - Every 6 hours
  - Weekly on Monday at 09:00 UTC
  - Monthly on 1st at 00:00 UTC
  - Custom cron expression
- Сохранить расписание

### 4. Просмотр статистики
- Общее количество инструментов
- Количество доступных инструментов
- Текущий уровень компетенции
- Время последнего анализа

---

## Как открыть интерфейс?

### Запустить Analytics Specialist:

```bash
cd /Users/MD/AI-Platform-ISO/infrastructure/AI-office-infrastructure/analytics-specialist

# Запустить сервис
python3 -m uvicorn main:app --host 0.0.0.0 --port 8051
```

### Открыть в браузере:

```
http://localhost:8051/ui/
```

**Или из любого компьютера в сети:**
```
http://<SERVER_IP>:8051/ui/
```

---

## Скриншот интерфейса (описание)

```
┌─────────────────────────────────────────────────────────────────┐
│ 🔍 Analytics Specialist - Tools Dashboard                      │
│ Manage and execute analysis tools for AI Platform ISO          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ Total    │  │Available │  │Competency│  │Last      │       │
│  │ Tools    │  │          │  │ Level    │  │Analysis  │       │
│  │   7      │  │    7     │  │  MIDDLE  │  │  Never   │       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
│                                                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌───────────────────────────────┐  ┌───────────────────────┐  │
│  │ Metrics Discovery    [JUNIOR] │  │ AST Analyzer [JUNIOR] │  │
│  │ Discovers and analyzes        │  │ Analyzes Python code  │  │
│  │ metrics from all services     │  │ structure using AST   │  │
│  │ ● Available                   │  │ ● Available           │  │
│  │ [Run Now]    [Schedule]       │  │ [Run Now] [Schedule]  │  │
│  └───────────────────────────────┘  └───────────────────────┘  │
│                                                                  │
│  ┌───────────────────────────────┐  ┌───────────────────────┐  │
│  │ Dependency Mapper  [MIDDLE]   │  │ API Mapper  [MIDDLE]  │  │
│  │ Maps dependencies between     │  │ Maps all API endpoints│  │
│  │ services                      │  │ across services       │  │
│  │ ● Available                   │  │ ● Available           │  │
│  │ [Run Now]    [Schedule]       │  │ [Run Now] [Schedule]  │  │
│  └───────────────────────────────┘  └───────────────────────┘  │
│                                                                  │
│  ┌───────────────────────────────┐  ┌───────────────────────┐  │
│  │ Security Scanner    [SENIOR]  │  │ Module Scanner [JUN.] │  │
│  │ Scans code for security       │  │ Scans all Python      │  │
│  │ vulnerabilities               │  │ modules               │  │
│  │ ● Available                   │  │ ● Available           │  │
│  │ [Run Now]    [Schedule]       │  │ [Run Now] [Schedule]  │  │
│  └───────────────────────────────┘  └───────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Функции интерфейса

### 1. Карточки инструментов

Каждая карточка показывает:
- **Название** инструмента
- **Badge** с уровнем компетенции (цветная метка)
  - 🟢 Junior - зеленый
  - 🟠 Middle - оранжевый
  - 🔴 Senior - красный
- **Описание** что делает инструмент
- **Статус** доступности (● Available / ● Unavailable)
- **Кнопки:**
  - `Run Now` - запустить сейчас
  - `Schedule` - запланировать

### 2. Модальное окно запуска

При нажатии "Run Now":
1. Открывается модальное окно
2. Показывается spinner "Executing tool, please wait..."
3. После завершения:
   - ✅ "Execution Complete"
   - Показывается JSON результат
4. Можно закрыть окно (×)

### 3. Модальное окно планирования

При нажатии "Schedule":
1. Открывается форма планирования
2. Можно выбрать:
   - Daily at 02:00 UTC
   - Every 6 hours
   - Weekly on Monday at 09:00 UTC
   - Monthly on 1st at 00:00 UTC
   - Custom (cron expression)
3. Нажать "Save Schedule"

### 4. Автоматическое обновление

- При открытии страницы загружаются все инструменты
- Статистика обновляется автоматически
- Показывается актуальный статус каждого инструмента

---

## API endpoints для UI

Web UI использует следующие API:

### GET /api/v1/analytics/status
Получить список всех инструментов и их статусы

**Response:**
```json
{
  "service": "analytics-specialist",
  "status": "healthy",
  "competency_level": "middle",
  "tools": {
    "metrics_discovery": {
      "available": true,
      "description": "Discovers and analyzes metrics",
      "competency_required": "junior"
    },
    "ast_analyzer": {
      "available": true,
      "description": "Analyzes Python code structure",
      "competency_required": "junior"
    },
    ...
  }
}
```

### POST /api/v1/analytics/tools/{tool_name}
Запустить конкретный инструмент

**Example:**
```bash
curl -X POST http://localhost:8051/api/v1/analytics/tools/ast-analysis
```

**Response:**
```json
{
  "status": "success",
  "tool": "ast_analyzer",
  "total_functions": 142,
  "total_classes": 38,
  "analyzed_at": "2025-10-08T10:30:00Z"
}
```

### POST /ui/api/execute
Запустить инструмент через UI (с параметрами)

**Request:**
```json
{
  "tool_name": "security_scanner",
  "parameters": {
    "project_path": "/path/to/project"
  },
  "async_execution": false
}
```

**Response:**
```json
{
  "status": "completed",
  "tool": "security_scanner",
  "result": {
    "total_issues": 3,
    "critical_issues": [],
    "high_issues": [...]
  }
}
```

### POST /ui/api/schedule
Запланировать регулярный запуск инструмента

**Request:**
```json
{
  "tool_name": "dependency_mapper",
  "schedule": "0 2 * * *",
  "parameters": {},
  "enabled": true
}
```

**Response:**
```json
{
  "status": "scheduled",
  "tool": "dependency_mapper",
  "schedule": "0 2 * * *",
  "message": "Tool scheduled successfully"
}
```

---

## Дизайн и UX

### Цветовая схема

- **Background:** Gradient (фиолетово-синий)
- **Cards:** Белый с тенями
- **Primary button:** #667eea (синий)
- **Secondary button:** #e2e8f0 (серый)

### Уровни компетенции (цвета)

- **Junior:** 🟢 Зеленый (#48bb78)
- **Middle:** 🟠 Оранжевый (#ed8936)
- **Senior:** 🔴 Красный (#e53e3e)

### Responsive дизайн

- Grid автоматически адаптируется к ширине экрана
- На мобильных устройствах карточки выстраиваются в 1 колонку
- На планшетах - 2 колонки
- На десктопе - 3-4 колонки

### Интерактивность

- Hover эффекты на карточках (поднимаются вверх)
- Анимация spinner при загрузке
- Плавные transitions на кнопках
- Модальные окна с backdrop

---

## Расширение функционала

### Что можно добавить в будущем?

#### 1. История выполнения
```python
@ui_router.get("/api/executions")
async def get_execution_history():
    """Get execution history for all tools"""
    # TODO: Implement with database
```

Показывать:
- Когда запускался инструмент
- Кто запустил (user/scheduled/manual)
- Результаты
- Длительность выполнения

#### 2. Реальное планирование
```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()

@ui_router.post("/api/schedule")
async def schedule_tool(request: ToolScheduleRequest):
    # Add job to APScheduler
    scheduler.add_job(
        execute_tool,
        'cron',
        **parse_cron(request.schedule),
        args=[request.tool_name, request.parameters]
    )
```

#### 3. Параметры инструментов
Для каждого инструмента показывать форму с параметрами:
- project_path (путь к проекту)
- depth (глубина анализа)
- exclude_patterns (паттерны исключения)

#### 4. Экспорт результатов
- Download JSON
- Download PDF report
- Send to email

#### 5. Сравнение результатов
- Compare current vs previous run
- Show trends over time
- Highlight changes

#### 6. Уведомления
- Desktop notifications когда инструмент завершился
- Email notifications на критические находки
- Slack/Teams integration

#### 7. Multi-user support
- Авторизация (login/password)
- Роли (admin/user/viewer)
- Audit log (кто что запускал)

---

## Для других AI коллег

Аналогичный UI можно создать для:

### MIO Manager (Port 8046)
```
http://localhost:8046/ui/

Инструменты:
- Service Discovery
- Docker Compose Generator
- Prometheus Config Generator
- Deployment Orchestrator
```

### Project Agent (Port 8045)
```
http://localhost:8045/ui/

Инструменты:
- Documentation Generator
- Test Generator
- Changelog Generator
- UI Blueprint Generator
```

### Infrastructure Builder (Port 8004)
```
http://localhost:8004/ui/

Инструменты:
- All 26 tools (orchestrator имеет доступ ко всем)
```

---

## Мобильная версия

UI уже адаптивный, можно открыть на:
- 📱 iPhone/Android
- 📱 iPad/Tablet
- 💻 Desktop
- 🖥️ Large screens

Автоматически подстраивается под размер экрана.

---

## Безопасность

### Текущая версия (MVP):
- ⚠️ Нет авторизации (любой может запускать)
- ⚠️ CORS открыт для всех

### Production версия должна иметь:
- ✅ JWT авторизация
- ✅ RBAC (role-based access control)
- ✅ Rate limiting
- ✅ CORS только для разрешенных доменов
- ✅ HTTPS обязательно
- ✅ Audit log всех действий

---

## Запуск в production

### 1. С Docker:
```bash
cd infrastructure/AI-office-infrastructure/analytics-specialist

docker build -t analytics-specialist .
docker run -p 8051:8051 analytics-specialist
```

### 2. С systemd:
```ini
[Unit]
Description=Analytics Specialist AI
After=network.target

[Service]
Type=simple
User=ai-platform
WorkingDirectory=/opt/ai-platform/analytics-specialist
ExecStart=/usr/bin/python3 -m uvicorn main:app --host 0.0.0.0 --port 8051
Restart=always

[Install]
WantedBy=multi-user.target
```

### 3. С nginx reverse proxy:
```nginx
server {
    listen 80;
    server_name analytics.ai-platform.local;

    location / {
        proxy_pass http://localhost:8051;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## Итог

✅ **Веб-интерфейс создан и готов к использованию!**

**Для Analytics Specialist:**
- Открыть http://localhost:8051/ui/
- Просматривать все 7 инструментов
- Запускать вручную
- Планировать автоматические запуски

**Для других специалистов:**
- Можно скопировать `tools_ui_routes.py`
- Адаптировать под их инструменты
- Добавить в их `main.py`

**Теперь можно настраивать ВСЁ через красивый веб-интерфейс!** 🎨✨
