# 🧹 Safe Cleanup для AI-Platform-ISO

Безопасный инструмент для очистки репозитория с сохранением русского языка и Unicode.

## 🎯 Что делает

### ✅ Безопасно СОХРАНЯЕТ:
- ✅ Русский язык (кириллица)
- ✅ Unicode символы и эмодзи
- ✅ Упоминания AI tools (Claude, ChatGPT, etc)
- ✅ Архивы (`_archive/`)
- ✅ Документация (`docs/`, `DOC/`, `catalogs/`)
- ✅ Имена файлов (БЕЗ транслитерации)

### 🧹 Безопасно ОЧИЩАЕТ:
- 🧹 Временные файлы (`.bak`, `.tmp`, `.DS_Store`, `*~`, etc)
- 🧹 Валидирует JSON/YAML (без изменений)
- 🧹 Prettier только для staged файлов
- 🧹 Shellcheck для bash скриптов
- 🧹 Находит большие файлы (>10MB)
- 🧹 Находит пустые директории

### ❌ НЕ делает:
- ❌ НЕ транслитерирует имена файлов
- ❌ НЕ удаляет Unicode контент
- ❌ НЕ удаляет упоминания AI
- ❌ НЕ переформатирует весь код
- ❌ НЕ трогает архивы

---

## 📦 Установка

```bash
# Скрипт уже готов к использованию:
chmod +x scripts/safe-cleanup.sh

# Опционально: установить зависимости для полного функционала
# - jq (для JSON валидации)
brew install jq

# - shellcheck (для bash скриптов)
brew install shellcheck

# - prettier (для форматирования, если нет)
npm install -g prettier
```

---

## 🚀 Использование

### 1. Dry-Run (только отчет, БЕЗ изменений)

```bash
./scripts/safe-cleanup.sh

# Вывод:
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#    🧹 Safe Cleanup для AI-Platform-ISO
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Mode: dry-run
#
# ✅ Found 5 temporary files
# ✅ All 234 JSON files valid
# ✅ All 87 YAML files valid
# ...
#
# 📊 Report saved: .cleanup-report/cleanup-report-20251021_123456.md
```

### 2. Применить изменения

```bash
./scripts/safe-cleanup.sh --apply

# Что произойдет:
# 1. Удалятся временные файлы (.bak, .tmp, .DS_Store)
# 2. Prettier отформатирует staged файлы
# 3. Создастся детальный отчет
```

### 3. Только валидация (БЕЗ очистки)

```bash
./scripts/safe-cleanup.sh --validate

# Проверяет:
# - JSON валидность
# - YAML валидность
# - Shellcheck для bash
```

### 4. Verbose mode (детальный вывод)

```bash
./scripts/safe-cleanup.sh -v

# Покажет каждый найденный файл:
# Found: ./platform_services/bia_service/models.py.bak
# Found: ./.DS_Store
# ✅ ./package.json (JSON valid)
# ...
```

---

## 📊 Отчет

После каждого запуска создается детальный отчет:

```
.cleanup-report/
└── cleanup-report-20251021_123456.md
```

**Содержимое отчета:**
```markdown
# Safe Cleanup Report

## Summary

### 1. Temporary Files
- **Found:** 5
- **Deleted:** 5

#### Files:
- `./platform_services/bia_service/models.py.bak`
- `./.DS_Store`
- ...

### 2. JSON Validation
- **Valid:** 234
- **Invalid:** 0

### 3. YAML Validation
- **Valid:** 87
- **Invalid:** 0

### 4. Shellcheck
- **Passed:** 23
- **Warnings:** 2

### 5. Prettier
- **Formatted:** 12 staged files

### 6. Large Files (>10MB)
- **Found:** 3

#### Files:
- `./platform_services/monitoring/prometheus/data/01K7.../chunks/000001` (15MB)
...

### 7. Empty Directories
- **Found:** 0

---

## Final Summary

| Category | Count |
|----------|-------|
| Temporary files deleted | 5 |
| JSON valid | 234 |
| YAML valid | 87 |
...
```

---

## 🔧 Конфигурация

### Временные файлы (удаляются):
```bash
*.bak       # Backup files
*.tmp       # Temporary files
*.temp      # Temporary files
.DS_Store   # macOS metadata
Thumbs.db   # Windows thumbnails
*.swp       # Vim swap files
*.swo       # Vim swap files
*~          # Backup files
*.orig      # Git merge originals
*.rej       # Git merge rejects
```

### Исключаемые директории (НЕ трогаем):
```bash
.git/
node_modules/
_archive/       # Наши архивы
dist/
build/
.next/
coverage/
__pycache__/
.venv/
venv/
```

---

## 💡 Примеры использования

### Перед коммитом

```bash
# 1. Сделай изменения
git add .

# 2. Запусти cleanup
./scripts/safe-cleanup.sh --apply

# 3. Проверь отчет
cat .cleanup-report/cleanup-report-*.md

# 4. Коммит
git commit -m "feat: новая фича"
```

### Периодическая очистка

```bash
# Раз в неделю - полная очистка
./scripts/safe-cleanup.sh --apply

# Проверь найденные большие файлы
grep "Large Files" .cleanup-report/cleanup-report-*.md -A 20
```

### CI/CD интеграция

```yaml
# .github/workflows/cleanup-check.yml
name: Cleanup Check
on: [pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install dependencies
        run: |
          brew install jq shellcheck
          npm install -g prettier

      - name: Run safe cleanup validation
        run: ./scripts/safe-cleanup.sh --validate

      - name: Upload report
        uses: actions/upload-artifact@v4
        with:
          name: cleanup-report
          path: .cleanup-report/
```

---

## 🆚 Отличия от Repo Cleaner Pack

| Функция | Repo Cleaner Pack | Safe Cleanup |
|---------|-------------------|--------------|
| **Русский язык** | ❌ Транслитерация | ✅ Сохраняет |
| **Unicode** | ❌ Удаляет | ✅ Сохраняет |
| **Эмодзи** | ❌ Удаляет | ✅ Сохраняет |
| **AI упоминания** | ❌ Удаляет | ✅ Сохраняет |
| **Имена файлов** | ❌ Меняет | ✅ Сохраняет |
| **Temp files** | ✅ Удаляет | ✅ Удаляет |
| **Валидация** | ✅ Есть | ✅ Есть |
| **Prettier** | ⚠️ Весь код | ✅ Только staged |
| **Сложность** | ⚠️ Docker + scripts | ✅ Один bash |
| **Отчеты** | ✅ CSV + MD | ✅ Markdown |

---

## 🔒 Безопасность

### Git Safety

```bash
# Скрипт НЕ требует:
- ❌ Stash изменений
- ❌ Создание веток
- ❌ Автоматические коммиты

# Работает с любым состоянием git:
- ✅ Dirty index - OK
- ✅ Uncommitted changes - OK
- ✅ Detached HEAD - OK
```

### Rollback

```bash
# Если что-то пошло не так:

# 1. Временные файлы удалены случайно?
# Проверь отчет - там список всех удаленных файлов
cat .cleanup-report/cleanup-report-*.md

# 2. Prettier испортил файл?
git checkout -- <file>

# 3. Полный откат
git reset --hard HEAD
```

---

## 📝 FAQ

### Q: Удалит ли скрипт русские имена файлов?
**A:** НЕТ! Скрипт НЕ трогает имена файлов. Только удаляет временные (.bak, .tmp).

### Q: Удалит ли упоминания Claude в документации?
**A:** НЕТ! Скрипт сохраняет весь контент как есть. Только валидация.

### Q: Безопасно ли запускать на production?
**A:** ДА! По умолчанию режим `dry-run` (только отчет). С `--apply` тоже безопасно - удаляются только временные файлы.

### Q: Что если JSON/YAML невалидны?
**A:** Скрипт покажет ошибку и НЕ применит изменения (exit 1). Нужно сначала исправить.

### Q: Можно ли кастомизировать?
**A:** ДА! Отредактируй переменные в начале скрипта:
```bash
TEMP_PATTERNS=(...)  # Какие файлы удалять
EXCLUDE_DIRS=(...)   # Какие директории пропускать
```

### Q: Чем отличается от `git clean -fdx`?
**A:** `git clean -fdx` удаляет ВСЕ untracked файлы. `safe-cleanup.sh` удаляет ТОЛЬКО временные (.bak, .tmp), сохраняя остальное.

---

## 🎯 Roadmap

### Планируется добавить:

- [ ] Поиск дубликатов файлов
- [ ] Проверка на оставшиеся секреты (git-secrets integration)
- [ ] SQL валидация
- [ ] Python code formatting (black/ruff)
- [ ] TypeScript validation
- [ ] Автоматическое добавление в `.gitignore`
- [ ] Интерактивный режим (выбор что удалять)
- [ ] Dry-run diff preview

---

## 📚 Ссылки

- **Документация проекта:** `/docs/`
- **Vault Setup:** `/VAULT_SETUP_COMPLETE.md`
- **ENV Consolidation:** `/ENV_CONSOLIDATION_REPORT.md`

---

## 🤝 Поддержка

Нашел баг или есть идея? Создай issue:
```bash
# Приложи к issue:
cat .cleanup-report/cleanup-report-*.md
```

---

**Автор:** Claude Code
**Дата:** 2025-10-21
**Версия:** 1.0.0
**Статус:** ✅ Production Ready
