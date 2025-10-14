# 🚑 СРОЧНО: Восстановление контекста - Переименование директорий

**Дата:** 2025-10-15
**Статус:** ⚠️ Claude завис, терминал не реагирует
**Задача:** Переименование директорий с дефисами в snake_case

## 🎯 ЧТО БЫЛО СДЕЛАНО (до зависания)

### ✅ Выполнено успешно:

1. **Переименованы ВСЕ директории** с дефисами в snake_case:
   ```bash
   intelligent-core → intelligent_core
   platform-services → platform_services
   ```

2. **Переименованы вложенные директории** (~30 директорий):
   - ai-foundation → ai_foundation
   - bia-service → bia_service
   - policy-engine → policy_engine
   - И все остальные...

3. **Git commit создан:**
   ```
   "fix: Rename ALL directories to snake_case (Complete Phase 2)"
   ```

4. **Переименованы 4 Python файла:**
   - generate-complete-platform-map.py → generate_complete_platform_map.py
   - generate-module-docs.py → generate_module_docs.py
   - generate-service-docs.py → generate_service_docs.py
   - И ещё один...

### ⚠️ ЧТО ОСТАЛОСЬ СДЕЛАТЬ:

1. **КРИТИЧНО: Исправить импорты!**

   Claude сказал: "Все сломанные импорты закомментированы (#) - они не активны!"

   **НО ЭТО ПОДОЗРИТЕЛЬНО!** Нужно проверить:
   - Возможно не все импорты найдены
   - Возможно есть активные импорты с дефисами
   - Нужно искать паттерны: `from intelligent_core.ai-foundation` (смешанные!)

2. **Запустить Test 1.1** для проверки:
   ```bash
   python -m pytest tests/ -v
   ```

3. **Создать второй commit** с исправлениями импортов

## 🔍 КАК НАЙТИ ВСЕ СЛОМАННЫЕ ИМПОРТЫ

### Паттерны для поиска:

```bash
# 1. Старый формат с дефисами (полностью)
grep -r "from intelligent-core" --include="*.py" . 2>/dev/null

# 2. Смешанный формат (ОПАСНО! Может быть пропущен)
grep -r "from intelligent_core\..*-" --include="*.py" . 2>/dev/null
grep -r "from platform_services\..*-" --include="*.py" . 2>/dev/null
grep -r "from infrastructure\..*-" --include="*.py" . 2>/dev/null

# 3. Import statements с дефисами
grep -r "import .*-.*" --include="*.py" . 2>/dev/null

# 4. Относительные импорты
grep -r "from \\..*-" --include="*.py" . 2>/dev/null
```

### Автоматическое исправление:

```bash
# Скрипт для массового исправления импортов
cat > /tmp/fix_all_imports.py << 'SCRIPT'
#!/usr/bin/env python3
import os
import re
from pathlib import Path

def fix_imports_in_file(filepath):
    """Исправляет импорты в одном файле"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        original = content

        # 1. Заменяем директории первого уровня
        content = re.sub(r'from intelligent-core', 'from intelligent_core', content)
        content = re.sub(r'from platform-services', 'from platform_services', content)
        content = re.sub(r'import intelligent-core', 'import intelligent_core', content)
        content = re.sub(r'import platform-services', 'import platform_services', content)

        # 2. Заменяем все дефисы в путях импортов
        # from intelligent_core.ai-foundation → from intelligent_core.ai_foundation
        content = re.sub(
            r'(from|import)\s+([\w_]+(?:\.[\w_-]+)*)',
            lambda m: m.group(1) + ' ' + m.group(2).replace('-', '_'),
            content
        )

        # 3. Сохраняем если были изменения
        if content != original:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False

    except Exception as e:
        print(f"❌ Ошибка в {filepath}: {e}")
        return False

def main():
    """Обрабатываем все Python файлы"""
    base_dirs = [
        'intelligent_core',
        'platform_services',
        'infrastructure',
        'tests'
    ]

    fixed_count = 0

    for base_dir in base_dirs:
        if not os.path.exists(base_dir):
            continue

        for py_file in Path(base_dir).rglob('*.py'):
            if fix_imports_in_file(py_file):
                print(f"✅ Исправлен: {py_file}")
                fixed_count += 1

    print(f"\n🎉 Исправлено файлов: {fixed_count}")

if __name__ == '__main__':
    main()
SCRIPT

chmod +x /tmp/fix_all_imports.py
python3 /tmp/fix_all_imports.py
```

## 🔧 ДЕЙСТВИЯ ДЛЯ ВОССТАНОВЛЕНИЯ

### Шаг 1: Проверить статус терминала

```bash
# Если терминал завис, попробуй:
# 1. Ctrl+C несколько раз
# 2. Ctrl+Z (приостановка)
# 3. Закрыть терминал и открыть новый
```

### Шаг 2: Проверить статус git

```bash
cd /Users/MD/AI-Platform-ISO
git status
git log --oneline -5
```

**Ожидаемый результат:**
- Должен быть commit "fix: Rename ALL directories to snake_case"
- Могут быть uncommitted changes (4 переименованных .py файла)

### Шаг 3: Завершить переименование файлов

```bash
cd /Users/MD/AI-Platform-ISO

# Если файлы ещё не переименованы:
cd infrastructure/tools
git mv generate-complete-platform-map.py generate_complete_platform_map.py
git mv generate-module-docs.py generate_module_docs.py
git mv generate-service-docs.py generate_service_docs.py
cd ../..

git add -A
git commit -m "fix: Rename Python files with hyphens to snake_case"
```

### Шаг 4: КРИТИЧНО - Исправить импорты

```bash
# Запустить скрипт исправления импортов (см. выше)
python3 /tmp/fix_all_imports.py

# Проверить что исправилось
git diff

# Commit
git add -A
git commit -m "fix: Update all imports after directory rename to snake_case"
```

### Шаг 5: Проверить что всё работает

```bash
# Проверка базовых импортов
python3 -c "from intelligent_core.ai_foundation import llm; print('✅ Import OK')"

# Запуск тестов
python3 -m pytest tests/ -v --tb=short

# Проверка что нет сломанных импортов
python3 -m py_compile intelligent_core/**/*.py 2>&1 | grep -i error
```

## 🚨 ВАЖНЫЕ ЗАМЕТКИ

### Что проверил предыдущий Claude:

1. ✅ Нашёл закомментированные импорты - они не проблема
2. ✅ Нашёл 4 .py файла с дефисами - начал переименовывать
3. ⚠️ Сказал "Все сломанные импорты закомментированы" - **ПОДОЗРИТЕЛЬНО!**

### Что может быть пропущено:

1. **Смешанные импорты:**
   ```python
   from intelligent_core.ai-foundation import something  # Дефис в середине!
   ```

2. **Относительные импорты:**
   ```python
   from .ai-foundation import something
   ```

3. **Динамические импорты:**
   ```python
   __import__('intelligent-core.ai-foundation')
   ```

4. **Импорты в строках:**
   ```python
   module = importlib.import_module('intelligent-core.something')
   ```

### Где искать проблемы:

1. **intelligent_core/** - все подмодули
2. **platform_services/** - все сервисы
3. **infrastructure/** - tools, policy-engine и т.д.
4. **tests/** - тестовые файлы
5. **scripts/** - скрипты запуска

## 📊 СТАТИСТИКА ДО/ПОСЛЕ

### До переименования:
- `intelligent-core/` с множеством `module-name/`
- `platform-services/` с множеством `service-name/`
- ~30+ директорий с дефисами
- 4 Python файла с дефисами

### После переименования:
- `intelligent_core/` с `module_name/`
- `platform_services/` с `service_name/`
- ВСЕ директории в snake_case ✅
- ВСЕ Python файлы в snake_case ✅
- Импорты: **НУЖНО ПРОВЕРИТЬ И ИСПРАВИТЬ!** ⚠️

## 🎯 ИТОГОВЫЙ ЧЕКЛИСТ

Для нового Claude или для восстановления:

- [ ] Терминал восстановлен
- [ ] Git status проверен
- [ ] Завершить переименование 4 .py файлов (если не закончено)
- [ ] Запустить скрипт исправления импортов
- [ ] Проверить результаты git diff
- [ ] Commit исправлений импортов
- [ ] Запустить тесты
- [ ] Проверить что нет ошибок импорта
- [ ] Создать финальный отчёт

## 💾 BACKUP ИНФОРМАЦИЯ

**Последний известный commit:**
```
"fix: Rename ALL directories to snake_case (Complete Phase 2)"
```

**Рабочая директория:**
```
/Users/MD/AI-Platform-ISO
```

**Ветка:** (вероятно `main` или `fix/rename-directories`)

**Файлы для проверки:**
- `intelligent_core/` (существует?)
- `platform_services/` (существует?)
- `infrastructure/tools/generate_complete_platform_map.py` (переименован?)

---

**Создано:** 2025-10-15
**Для восстановления работы Claude по переименованию директорий и исправлению импортов**
**Приоритет:** 🔴 ВЫСОКИЙ - импорты сломаны, нужно исправить!
