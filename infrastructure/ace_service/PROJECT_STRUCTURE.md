# ACE - Структура Проекта

## ✅ Правильная Структура (После Очистки)

### Есть ТОЛЬКО ОДНА папка ACE:

```
/Users/MD/AI-Platform-ISO/
└── infrastructure/
    └── ace-service/          ← ЕДИНСТВЕННАЯ папка ACE
        ├── main.py           ← FastAPI сервис (900+ строк)
        ├── ace_client.py     ← Клиентская библиотека (500+ строк)
        ├── requirements.txt
        ├── Dockerfile
        ├── docker-compose.yml
        ├── setup_ace_in_supabase.sh
        ├── start_ace_service.sh
        ├── test_ace_integration.py
        ├── QUICKSTART.md
        ├── INTEGRATION_GUIDE.md
        └── README.md
```

## ❌ Удалено / Перемещено

### 1. Удалено: `/infrastructure/ace_service/` (дубликат)
- Была лишняя папка с подчеркиванием вместо дефиса
- Все файлы скопированы в правильную папку `ace-service/`
- Папка удалена

### 2. Архивировано: `/intelligent-core/ace-engine/` (старая POC версия)
- Это была старая POC версия 1.0 (in-memory, только для AI Orchestration)
- Перемещена в: `/Users/MD/AI-Platform-ISO/_archive/ace-engine-poc-v1/`
- Сохранена для истории, но больше не используется

## 📍 Централизованная Архитектура

ACE - это **централизованный микросервис** в infrastructure:

```
Все модули платформы
    ↓
    → используют ACEClient из infrastructure/ace-service/ace_client.py
    ↓
    → подключаются к ACE Service (REST API на порту 8050)
    ↓
    → ACE Service работает с Supabase PostgreSQL
```

## 🔌 Как Модули Используют ACE

Модули **НЕ содержат** код ACE, они только **импортируют клиент**:

```python
# В любом модуле (например, scenario-intelligence)
from infrastructure.ace_service.ace_client import ACEClient

class ВашМодуль:
    def __init__(self):
        self.ace = ACEClient(base_url="http://localhost:8050")
```

## 📊 Почему Только Одна Папка?

### Централизованный подход (Версия 2.0 - Production):
- ✅ Один сервис для всей платформы
- ✅ Единая база данных playbook'ов
- ✅ Централизованное обновление и мониторинг
- ✅ Легко масштабировать и обслуживать
- ✅ Все модули используют одинаковые playbook'и

### Распределенный подход (Версия 1.0 - POC, устарела):
- ❌ Каждый модуль имеет свой ACE engine
- ❌ Playbook'и не обмениваются между модулями
- ❌ Дублирование кода
- ❌ Сложно обновлять и мониторить

**Мы выбрали централизованный подход!**

## 🎯 Итого

| Локация | Статус | Назначение |
|---------|--------|------------|
| `/infrastructure/ace-service/` | ✅ **АКТИВНА** | Production централизованный сервис |
| `/infrastructure/ace_service/` | ❌ **УДАЛЕНА** | Дубликат (был с подчеркиванием) |
| `/intelligent-core/ace-engine/` | 📦 **АРХИВИРОВАНА** | Старая POC версия 1.0 |

---

**Очищено:** 15 октября 2025
**Правильная структура:** ✅ Установлена
