# 🎨 AI Platform ISO - Unified Web UI

**Центральный веб-интерфейс для управления и мониторинга всей AI Platform**

---

## 🚀 Что это?

Unified Web UI - это **единая точка входа** для управления всей AI Platform ISO через браузер.

### Интегрирует:

1. **Tools Management** - управление всеми 26 инструментами анализа
2. **Grafana Dashboards** - визуализация метрик
3. **Prometheus Metrics** - real-time мониторинг
4. **Service Discovery** - статус всех сервисов
5. **Platform Overview** - общая картина платформы

---

## 📦 Установка

### 1. Установить зависимости:

```bash
cd /Users/MD/AI-Platform-ISO/infrastructure/web-ui
pip install -r requirements.txt
```

### 2. Создать статические директории:

```bash
mkdir -p static templates
```

---

## 🎯 Запуск

### Вариант 1: Uvicorn (для разработки)

```bash
cd /Users/MD/AI-Platform-ISO/infrastructure/web-ui
python3 -m uvicorn main:app --host 0.0.0.0 --port 8888 --reload
```

### Вариант 2: Python напрямую

```bash
cd /Users/MD/AI-Platform-ISO/infrastructure/web-ui
python3 main.py
```

### Открыть в браузере:

```
http://localhost:8888
```

---

## 📊 Страницы

### 1. Dashboard (/)

**URL:** `http://localhost:8888/`

**Что показывает:**
- Общее количество сервисов
- Количество healthy/unhealthy сервисов
- Uptime платформы
- Статус каждого сервиса (карточки)
- Quick actions (быстрые ссылки)

**Группы сервисов:**
- **AI Office Infrastructure:** Analytics Specialist, MIO Manager, AI Orchestrator
- **Intelligent Core:** Workflow Intelligence, Community Intelligence, Collective, Predictive, AI Foundation
- **Observability:** Prometheus, Grafana, Alert Manager

**Автообновление:** Каждые 30 секунд

---

### 2. Tools (/tools)

**URL:** `http://localhost:8888/tools`

**Что можно делать:**
- Просмотр всех 7 инструментов Analytics Specialist
- Запуск инструментов вручную (кнопка "Run Now")
- Видеть статус каждого инструмента
- Видеть уровень компетенции (Junior/Middle/Senior)

**Доступные инструменты:**
1. Metrics Discovery (Junior)
2. Module Scanner (Junior)
3. AST Analyzer (Junior)
4. Dependency Mapper (Middle)
5. API Mapper (Middle)
6. Dependency Validator (Middle)
7. Security Scanner (Senior)

**Запуск инструмента:**
1. Нажать "Run Now"
2. Дождаться выполнения
3. Посмотреть результаты в модальном окне

---

### 3. Monitoring (/monitoring)

**URL:** `http://localhost:8888/monitoring`

**Вкладки:**

#### Overview
- Ключевые метрики платформы (CPU, Memory, Requests, Errors)
- Quick links к Grafana и Prometheus
- Placeholder для будущих real-time графиков

#### Grafana
- Embedded Grafana dashboard
- Показывает Workflow Intelligence dashboard
- Кнопка "Open in full Grafana"

#### Prometheus
- Embedded Prometheus metrics explorer
- Можно писать PromQL запросы
- Кнопка "Open in full Prometheus"

#### Alerts
- Список активных алертов
- Embedded Alert Manager
- Статус всех правил алертинга

---

## 🔌 API Endpoints

### Services Status

**GET** `/api/services/status`

Получить статус всех сервисов платформы.

**Response:**
```json
{
  "timestamp": "2025-10-08T10:30:00Z",
  "services": {
    "analytics_specialist": {
      "status": "healthy",
      "url": "http://localhost:8051",
      "response_time_ms": 15.3
    },
    ...
  },
  "total": 12,
  "healthy": 10,
  "unhealthy": 2
}
```

---

### Tools List

**GET** `/api/tools/list`

Получить список всех инструментов.

**Response:**
```json
{
  "tools": {
    "ast_analyzer": {
      "available": true,
      "description": "Analyzes Python code structure",
      "competency_required": "junior"
    },
    ...
  },
  "competency_level": "middle",
  "total": 7
}
```

---

### Execute Tool

**POST** `/api/tools/{tool_name}/execute`

Запустить конкретный инструмент.

**Example:**
```bash
curl -X POST http://localhost:8888/api/tools/ast_analyzer/execute
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

---

### Prometheus Query

**GET** `/api/prometheus/query?query={promql}`

Выполнить PromQL запрос к Prometheus.

**Example:**
```bash
curl "http://localhost:8888/api/prometheus/query?query=up"
```

---

### Grafana Dashboards

**GET** `/api/grafana/dashboards`

Получить список Grafana dashboards.

**Response:**
```json
{
  "dashboards": [
    {
      "uid": "workflow-intelligence",
      "title": "Workflow Intelligence",
      "url": "http://localhost:3000/d/workflow-intelligence"
    },
    ...
  ]
}
```

---

## 🏗️ Архитектура

```
infrastructure/web-ui/
├── main.py                 # FastAPI application
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── static/                # Static assets (CSS, JS, images)
│   └── (empty for now)
└── templates/             # HTML templates
    ├── dashboard.html     # Main dashboard
    ├── tools.html         # Tools management
    └── monitoring.html    # Monitoring page
```

### Как работает:

1. **FastAPI backend** (main.py):
   - Проксирует запросы к Analytics Specialist
   - Проксирует запросы к Prometheus/Grafana
   - Проверяет health всех сервисов
   - Отдает HTML страницы

2. **HTML templates**:
   - Pure HTML + CSS + Vanilla JavaScript
   - Нет фреймворков (React/Vue)
   - Responsive дизайн
   - Auto-refresh каждые 30 секунд

3. **Интеграции**:
   - Analytics Specialist → `/api/tools/*`
   - Prometheus → `/api/prometheus/*`
   - Grafana → embedded iframes
   - All services → `/api/services/status`

---

## 🎨 Дизайн

### Цветовая схема:

- **Primary:** #1e3c72 (синий)
- **Secondary:** #667eea (фиолетовый)
- **Success:** #48bb78 (зеленый)
- **Warning:** #ed8936 (оранжевый)
- **Danger:** #e53e3e (красный)

### Градиенты:

- Dashboard: `linear-gradient(135deg, #1e3c72 0%, #2a5298 100%)`
- Tools: `linear-gradient(135deg, #667eea 0%, #764ba2 100%)`
- Monitoring: Dark theme `#1a202c`

---

## 🔧 Настройка

### Изменить порты сервисов:

Отредактировать `main.py`:

```python
SERVICES = {
    "analytics_specialist": "http://localhost:8051",  # Изменить порт
    "prometheus": "http://localhost:9090",
    ...
}
```

### Добавить новый сервис:

1. Добавить в `SERVICES` dict
2. Обновить `templates/dashboard.html`
3. Добавить в `serviceGroups`

---

## 📱 Responsive

UI адаптируется под:
- 📱 Mobile (iPhone, Android)
- 📱 Tablet (iPad)
- 💻 Desktop
- 🖥️ Large screens (4K)

---

## 🚀 Production

### С Docker:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8888

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8888"]
```

```bash
docker build -t ai-platform-ui .
docker run -p 8888:8888 ai-platform-ui
```

### С systemd:

```ini
[Unit]
Description=AI Platform Web UI
After=network.target

[Service]
Type=simple
User=ai-platform
WorkingDirectory=/opt/ai-platform/web-ui
ExecStart=/usr/bin/python3 -m uvicorn main:app --host 0.0.0.0 --port 8888
Restart=always

[Install]
WantedBy=multi-user.target
```

### С nginx:

```nginx
server {
    listen 80;
    server_name platform.ai-iso.local;

    location / {
        proxy_pass http://localhost:8888;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # WebSocket support (если понадобится)
    location /ws {
        proxy_pass http://localhost:8888;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

---

## 🔒 Безопасность

### Текущая версия (MVP):

⚠️ **НЕТ авторизации** - любой может зайти
⚠️ **CORS открыт** - accept all origins

### Production версия должна иметь:

✅ **JWT авторизация**
✅ **RBAC** (role-based access control)
✅ **Rate limiting**
✅ **HTTPS обязательно**
✅ **CORS только для разрешенных доменов**
✅ **Audit log**

---

## 🎯 Roadmap

### v1.0 (сейчас):
- ✅ Dashboard с статусом сервисов
- ✅ Tools management
- ✅ Embedded Grafana/Prometheus
- ✅ Auto-refresh

### v1.1 (следующая версия):
- [ ] Real-time WebSocket updates
- [ ] Custom Prometheus charts
- [ ] Tool scheduling interface
- [ ] Execution history

### v1.2:
- [ ] User authentication
- [ ] Role-based access
- [ ] Notification center
- [ ] Mobile app

### v2.0:
- [ ] AI-powered insights
- [ ] Predictive analytics
- [ ] Automated remediation
- [ ] Multi-tenant support

---

## 🐛 Troubleshooting

### Проблема: "Failed to load services status"

**Причина:** Сервисы не запущены

**Решение:**
```bash
# Проверить какие сервисы работают
curl http://localhost:8051/health  # Analytics Specialist
curl http://localhost:9090/-/healthy  # Prometheus
curl http://localhost:3000/api/health  # Grafana
```

### Проблема: "CORS error"

**Причина:** Браузер блокирует запросы

**Решение:** Добавить домен в CORS

```python
# main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://yourdomain.com"],  # Вместо ["*"]
)
```

### Проблема: Embedded iframe не загружается

**Причина:** Grafana/Prometheus блокирует embedding

**Решение:** Включить embedding в конфигах

**Grafana** (`grafana.ini`):
```ini
[security]
allow_embedding = true
```

**Prometheus:** Уже разрешает по умолчанию

---

## 📞 Поддержка

- GitHub Issues: https://github.com/your-org/ai-platform-iso/issues
- Documentation: https://docs.ai-platform-iso.com

---

## 🎉 Итог

**Unified Web UI теперь - единая точка входа для всей платформы!**

✅ Dashboard с реальными данными
✅ Tools management
✅ Integrated Grafana/Prometheus
✅ Auto-refresh каждые 30 секунд
✅ Responsive дизайн
✅ Production-ready architecture

**Запускай и управляй всей платформой из браузера!** 🚀
