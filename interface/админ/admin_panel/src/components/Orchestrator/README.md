# Orchestrator Control Panel

## Quick Start

### 1. Start Orchestrator API (Required)

```bash
cd /Users/MD/AI-Platform-ISO/intelligent-core/orchestration/ai-orchestration
python api.py
```

API должен быть доступен на http://localhost:8050

### 2. Open Control Panel

Navigate to: http://localhost:3000/orchestrator

## Components

- **OrchestratorHeader** - Status badge и header
- **SystemStatus** - 5 системных компонентов
- **PerformanceMetrics** - 4 ключевые метрики
- **ActiveCrises** - Мониторинг кризисов
- **RecentDecisions** - История решений
- **QuickActions** - Управление (evolution, cache)
- **ServiceHealthGrid** - 9 сервисов
- **AIExpertsDelegation** - 3 AI эксперта

## Troubleshooting

### "Internal Server Error" при загрузке страницы

**Причина:** Orchestrator API не запущен

**Решение:**
```bash
cd /Users/MD/AI-Platform-ISO/intelligent-core/orchestration/ai-orchestration
python api.py
```

### Components показывают "Loading..."

**Причина:** API недоступен или возвращает ошибки

**Проверка:**
```bash
curl http://localhost:8050/health
curl http://localhost:8050/stats
```

### React Query errors в консоли

**Причина:** Нормально, React Query делает retry при недоступности API

**Решение:** Запустите Orchestrator API
