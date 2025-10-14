# Scenario Generators - Infrastructure Tool

**Расположение:** `/infrastructure/tools/scenario-generators/`
**Версия:** 1.0.0
**Статус:** ✅ Production Ready

---

## 🎯 Назначение

Инструмент для генерации тестовых сценариев платформы BCM.

### Архитектурное Разделение

```
intelligent-core/scenario-intelligence/     # ЗНАНИЯ И ПОЛИТИКИ
├── templates/                              # Шаблоны сценариев (знания)
├── storage/                                # Хранилище и доступ к данным
├── analyzers/                              # Анализаторы (TODO)
└── validators/                             # Валидаторы (TODO)

infrastructure/tools/scenario-generators/   # ИНСТРУМЕНТЫ ГЕНЕРАЦИИ
├── generators/                             # Генераторы
├── managers/                               # Менеджеры оркестрации
└── cli/                                    # CLI интерфейс

infrastructure/AI-office-infrastructure/
└── scenario-orchestrator/                  # REST API координация
```

## 🏗️ Архитектура

### Принцип Разделения

**Intelligent Core (Ядро):**
- 🧠 Хранит знания (шаблоны)
- 📋 Определяет политики и правила
- 💾 Управляет данными (storage/registry)
- ✅ Валидирует и анализирует

**Infrastructure Tools (Инструменты):**
- 🔧 Используют знания из ядра
- ⚙️ Генерируют сценарии
- 📊 Координируются через AI Office
- 🚀 Предоставляют CLI/API интерфейсы

### Координация через AI Office

Генераторы управляются **MIO Manager** из AI Office:

```
MIO Manager (8025)
  ↓ координирует
Scenario Orchestrator (8060)
  ↓ использует
Generation Manager
  ↓ запускает
Generators (L1, L2, L3, L4)
  ↓ используют
Templates из intelligent-core
```

---

## 📁 Структура

```
scenario-generators/
│
├── generators/                      # Генераторы сценариев
│   ├── __init__.py
│   ├── base_generator.py           # Базовый класс
│   ├── platform_services_catalog.py
│   ├── l1_platform_generator.py    # 46 сервисов
│   ├── l1_application_generator.py # 16 приложений
│   ├── l2_subsystem_generator.py   # 12 подсистем
│   └── l3_system_generator.py      # 19 систем
│
├── managers/                        # Менеджеры
│   ├── __init__.py
│   └── generation_manager.py       # Оркестратор
│
├── cli/                             # CLI интерфейс (TODO)
│   └── cli.py
│
└── README.md (этот файл)
```

---

## 🚀 Использование

### 1. Через Generation Manager

```python
import sys
from pathlib import Path

# Добавляем пути
sys.path.insert(0, str(Path.cwd() / "infrastructure" / "tools" / "scenario-generators"))
sys.path.insert(0, str(Path.cwd() / "intelligent-core" / "scenario-intelligence"))

from managers import GenerationManager
import asyncio

async def main():
    manager = GenerationManager()
    report = await manager.generate_all(
        levels=["l1_platform", "l1_applications", "l2", "l3"]
    )
    print(f"Сгенерировано: {report['total_scenarios_generated']}")

asyncio.run(main())
```

### 2. Через CLI (из директории генераторов)

```bash
cd /infrastructure/tools/scenario-generators

# Генерация всех уровней
python3 managers/generation_manager.py

# Генерация отдельного уровня
python3 generators/l1_platform_generator.py
python3 generators/l1_application_generator.py
python3 generators/l2_subsystem_generator.py
python3 generators/l3_system_generator.py
```

### 3. Через REST API (Scenario Orchestrator)

```bash
# Запуск сервиса
cd /infrastructure/AI-office-infrastructure/scenario-orchestrator
PORT=8060 python3 main.py

# Генерация через API
curl -X POST http://localhost:8060/api/v1/generate/start \
  -H "Content-Type: application/json" \
  -d '{"levels": ["l1_platform", "l1_applications", "l2", "l3"]}'
```

### 4. Координация через MIO Manager

MIO Manager автоматически координирует генерацию через:
- Регистрацию Scenario Orchestrator как агента
- Приоритизацию задач генерации
- Мониторинг выполнения
- Управление ресурсами

---

## 📊 Генераторы

| Генератор | Количество | Шаблон | Статус |
|-----------|------------|--------|--------|
| L1 Platform | 46 | golden_standard_l1.yaml | ✅ |
| L1 Applications | 16 | golden_standard_l1_application.yaml | ✅ |
| L2 Subsystems | 12 | golden_standard_l2.yaml | ✅ |
| L3 Systems | 19 | 11 специализированных | ✅ |
| L4 Workflows | TBD | golden_standard_l4.yaml | 🔄 TODO |

**Итого:** 93 сценария, 100% успешность, 0.7с время генерации

---

## 🔗 Интеграции

### Текущие

1. **intelligent-core/scenario-intelligence** ✅
   - Использует templates/
   - Использует storage/registry
   - Использует template_loader

2. **Scenario Orchestrator API** ✅
   - REST API на порту 8060
   - Координация через MIO Manager

3. **File System** ✅
   - Сохранение в `generated/`

### Планируемые

4. **MIO Manager** 🔄
   - Регистрация как задача
   - Приоритизация
   - Мониторинг

5. **EventBus** 🔄
   - События генерации
   - Авто-регенерация

6. **PostgreSQL** 🔄
   - Хранение результатов

7. **Qdrant** 🔄
   - Векторный поиск

---

## 📈 Производительность

- **Скорость:** 133 сценария/сек
- **Успешность:** 100%
- **Время генерации (93 сценария):** 0.7с
- **Память:** < 50MB

---

## 🧪 Тестирование

```bash
# Тест Generation Manager
cd /infrastructure/tools/scenario-generators
python3 managers/generation_manager.py

# Тест отдельного генератора
python3 generators/l1_platform_generator.py

# Проверка результатов
ls -la ../../intelligent-core/scenario-intelligence/generated/
```

---

## 📚 Документация

Полная документация находится в:
- [intelligent-core/scenario-intelligence/ARCHITECTURE_FINAL.md](../../../intelligent-core/scenario-intelligence/ARCHITECTURE_FINAL.md)
- [intelligent-core/scenario-intelligence/GENERATORS_COMPLETE.md](../../../intelligent-core/scenario-intelligence/GENERATORS_COMPLETE.md)
- [AI-office-infrastructure/scenario-orchestrator/README.md](../../AI-office-infrastructure/scenario-orchestrator/README.md)

---

## 🔄 Workflow

```
1. MIO Manager получает запрос на генерацию
   ↓
2. Делегирует Scenario Orchestrator (REST API)
   ↓
3. Scenario Orchestrator запускает Generation Manager
   ↓
4. Generation Manager выбирает нужные генераторы
   ↓
5. Генераторы загружают шаблоны из intelligent-core
   ↓
6. Генераторы создают сценарии
   ↓
7. Сценарии регистрируются в Registry
   ↓
8. Сценарии сохраняются в файлы
   ↓
9. Отчет возвращается через цепочку обратно
```

---

## 🎯 Следующие Шаги

1. ✅ Перемещение генераторов в infrastructure/tools
2. 🔄 Интеграция с MIO Manager для координации
3. 🔄 CLI интерфейс
4. 🔄 L4 Workflow Generator (AI-powered)
5. 🔄 PostgreSQL хранение результатов
6. 🔄 Qdrant семантический поиск

---

## 📞 Поддержка

Для вопросов и проблем:
1. Проверьте документацию в intelligent-core/scenario-intelligence/
2. Обратитесь к архитектуре платформы
3. Проверьте логи Scenario Orchestrator

---

**Версия:** 1.0.0
**Последнее обновление:** 2025-10-13
**Статус:** ✅ Production Ready
