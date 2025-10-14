# ИНСТРУКЦИЯ ПО ЗАПУСКУ

## Быстрый старт (2 команды)

Откройте **Terminal** и выполните:

```bash
cd /Users/MD/AI-Platform-ISO/docs

python3 rename_files.py

python3 update_links.py
```

**Готово!** Все файлы переименованы и все ссылки обновлены.

---

## Проверка результата

Откройте в браузере:

```bash
open /Users/MD/AI-Platform-ISO/docs/index.html
```

Проверьте что все ссылки работают:
- Навигация (верхнее меню)
- Раздел "Deep-Dive Documentation" (10 карточек)
- Футер (внизу страницы)

---

## Что делают скрипты?

### 1. `rename_files.py`
Переименовывает **15 файлов**:
- `ace-service.html` → `ace_service.html`
- `ai-foundation.html` → `ai_foundation.html`
- `bcm-philosophy.html` → `bcm_philosophy.html`
- И так далее...

### 2. `update_links.py`
Обновляет **все ссылки** во всех HTML файлах:
- `href="ace-service.html"` → `href="ace_service.html"`
- `href="ai-foundation.html"` → `href="ai_foundation.html"`
- И так далее во ВСЕХ файлах...

---

## Если возникли проблемы

### Проверить что файлы существуют:
```bash
cd /Users/MD/AI-Platform-ISO/docs
ls -la | grep "\.html$" | head -20
```

### Найти файлы с дефисами:
```bash
cd /Users/MD/AI-Platform-ISO/docs
ls -1 *.html | grep "-"
```

### Найти ссылки с дефисами:
```bash
cd /Users/MD/AI-Platform-ISO/docs
grep -r 'href=".*-.*\.html"' *.html | head -10
```

---

## Альтернатива: Bash скрипты

Если Python не работает, используйте bash:

```bash
cd /Users/MD/AI-Platform-ISO/docs
bash RENAME_FILES_SCRIPT.sh
bash UPDATE_LINKS_SCRIPT.sh
```

---

**Создано**: 2025-10-15
**Автор**: Claude Code (AI Assistant)
