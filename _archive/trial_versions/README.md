# Trial Versions Archive

**Дата архивации**: 2025-10-06
**Причина**: Подготовка к V7 Architecture migration

---

## Что здесь

Пробные/экспериментальные версии модулей, созданные в процессе проектирования архитектуры:

### 1. expertise-center_trial/
- **Создано**: 2025-10-05
- **Файлов**: 19 Python files
- **Статус**: Experimental/proof of concept
- **Причина архивации**: Заменяется финальной версией expertise-center в рамках V7

**Что было:**
- core/ - Plugin manager prototype
- shared/ - Shared infrastructure prototype
- domains/ - Domain plugins prototype

---

### 2. bcm_offices_trial/
- **Создано**: 2025-10-05
- **Файлов**: 7 Python files
- **Статус**: Experimental BCM module structure
- **Причина архивации**: Заменяется expertise-center/domains/bcm/ в V7

**Что было:**
- risk/ - Risk office module prototype

---

### 3. ai_platform_trial/
- **Создано**: 2025-10-05
- **Файлов**: 12 Python files
- **Статус**: Platform architecture prototype
- **Причина архивации**: Концепция распределена между ai-foundation и expertise-center в V7

**Что было:**
- chief/ - Chief executive prototype
- experts/ - Experts prototype
- managers/ - Managers prototype
- organs/ - Organs prototype
- shared/ - Shared components prototype
- tools/ - Tools prototype

---

## Финальная архитектура (V7)

Эти пробные версии заменяются на:

```
intelligent-core/
├─ ai-foundation/           # AI Infrastructure (RAG, ML, Learning, LLM)
├─ expertise-center/        # Domain Plugin Manager
│  └─ domains/bcm/
│     ├─ specialists/       # Strategic AI
│     ├─ colleagues/        # Tactical AI
│     └─ analyzers/         # Heavy AI (was "organs")
└─ workflow_intelligence/   # THE BRAIN (workflow engine)
```

---

## Можно ли удалить?

**НЕТ, не сейчас!**

Сохраняем как reference на случай если:
- Нужно вспомнить какие идеи были
- Нужно восстановить какой-то код
- Нужно сравнить подходы

**Когда можно удалить:**
- Через 3-6 месяцев после успешного запуска V7
- Когда уверены что ничего не понадобится

---

**Создано**: Automated during V7 migration preparation
