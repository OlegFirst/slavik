# 🚀 Как Запустить Sprint 1

**Для**: MD
**Цель**: Запустить 5 Claude разработчиков параллельно

---

## 📋 Подготовка

### 1. Открой 5 терминалов Claude Code

Каждый в директории: `/Users/MD/AI-Platform-ISO`

### 2. Присвой роли

- **Терминал 1**: Claude #1 (Координатор + ai-foundation)
- **Терминал 2**: Claude #2 (workflow_intelligence)
- **Терминал 3**: Claude #3 (Infrastructure + Temporal)
- **Терминал 4**: Claude #4 (expertise-center)
- **Терминал 5**: Claude #5 (Community + Integration)

---

## 🎬 Команды для Запуска

### Терминал 1 (Координатор):

```
Я Claude #1 - Координатор + ai-foundation.

Читай план: /Users/MD/AI-Platform-ISO/doc-project/SPRINT_1_ASSEMBLY_PLAN.md

Моя секция: "Claude #1 (Координатор + ai-foundation)"

Начинай работу:
1. Подключить Qdrant к ai-foundation
2. Настроить RAG с реальными embeddings
3. Настроить LLM routing
4. Координировать остальных через doc-project/SPRINT_STATUS.md

Статус обновляй каждый час в: doc-project/SPRINT_STATUS.md

Поехали!
```

---

### Терминал 2 (workflow_intelligence):

```
Я Claude #2 - Workflow Engine Specialist.

Читай план: /Users/MD/AI-Platform-ISO/doc-project/SPRINT_1_ASSEMBLY_PLAN.md

Моя секция: "Claude #2 (workflow_intelligence)"

Моя задача:
1. КРИТИЧНО: Переписать storage/postgres_adapter.py на SQLAlchemy
2. Интегрировать ai-foundation (RAG, ML, LLM)
3. Интегрировать shared (database, cache, eventbus)
4. Убрать все моки
5. Integration tests

Жду готовности ai-foundation от Claude #1.

Статус обновляю в: doc-project/SPRINT_STATUS.md

Готов!
```

---

### Терминал 3 (Infrastructure):

```
Я Claude #3 - Infrastructure & Orchestration Specialist.

Читай план: /Users/MD/AI-Platform-ISO/doc-project/SPRINT_1_ASSEMBLY_PLAN.md

Моя секция: "Claude #3 (Infrastructure + Temporal)"

Моя задача:
1. Завершить настройку Temporal.io (https://cloud.temporal.io)
2. RabbitMQ eventbus
3. Qdrant collections
4. Prometheus + Grafana

Начинаю с Temporal!

Статус в: doc-project/SPRINT_STATUS.md

Погнали!
```

---

### Терминал 4 (expertise-center):

```
Я Claude #4 - Domain Expertise Specialist.

Читай:
1. План: /Users/MD/AI-Platform-ISO/doc-project/SPRINT_1_ASSEMBLY_PLAN.md
2. ТЗ: /Users/MD/AI-Platform-ISO/doc-project/PARALLEL_TASK_SPECIFICATION.md

Моя секция: "Claude #4 (expertise-center)"

Моя задача:
1. Реорганизовать expertise-center (core/, shared/, domains/bcm/)
2. Разобрать ai_experts и ai-office
3. Создать 3 specialists, 7 colleagues, 10 analyzers
4. Интегрировать с ai-foundation + shared
5. БЕЗ заглушек!

Жду ai-foundation от Claude #1.

Статус в: doc-project/SPRINT_STATUS.md

Начинаю!
```

---

### Терминал 5 (Community + Integration):

```
Я Claude #5 - Community AI & Integration Specialist.

Читай план: /Users/MD/AI-Platform-ISO/doc-project/SPRINT_1_ASSEMBLY_PLAN.md

Моя секция: "Claude #5 (Community Intelligence + Integration)"

Моя задача:
1. Интегрировать community_intelligence с ai-foundation + shared
2. Интегрировать collective, predictive, learning-system, living-docs
3. Убрать дубликаты с ai-foundation
4. Integration tests для всех модулей

Жду ai-foundation от Claude #1.

Статус в: doc-project/SPRINT_STATUS.md

К работе готов!
```

---

## 📊 Мониторинг Прогресса

### Каждые 30 минут проверяй:

```bash
cat /Users/MD/AI-Platform-ISO/doc-project/SPRINT_STATUS.md
```

Смотри секции каждого Claude - они будут обновлять статус.

### Если блокеры:

Все Claude пишут блокеры в `SPRINT_STATUS.md` секцию "🚧 Current Blockers"

---

## 🔄 Синхронизация

### Каждый час все Claude обновляют:

```markdown
## Claude #X (имя)
**Status**: ACTIVE / BLOCKED / COMPLETED
**Current Task**: что делаю сейчас
**Progress**: [x] done [ ] todo
**Blockers**: если есть
```

---

## ✅ Критерии Успеха

### После 6-8 часов работы должно быть:

- [ ] ai-foundation подключен к Qdrant + настроен RAG/LLM
- [ ] workflow_intelligence на SQLAlchemy + интегрирован
- [ ] expertise-center реорганизован + интегрирован
- [ ] Temporal.io работает
- [ ] Нет моков, нет заглушек
- [ ] Integration tests написаны

---

## 🆘 Если Проблемы

1. Остановить всех Claude
2. Обсудить проблему
3. Обновить план
4. Перезапустить

---

## 📝 После Спринта

### Каждый Claude делает коммит:

```bash
git add .
git commit -m "feat(module): sprint 1 integration

- Detailed changes
- Integrations completed

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"
```

### Координатор (Claude #1) создаёт:

`doc-project/SPRINT_1_RETROSPECTIVE.md` - итоги спринта

---

## 🎯 Поехали!

**Запускай всех 5 Claude по очереди** командами выше.

Они начнут работать параллельно и синхронизироваться через `SPRINT_STATUS.md`.

**Удачи!** 🚀
