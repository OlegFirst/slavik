# Инструкция по переименованию HTML файлов

## Проблема
Python не может читать имена файлов с дефисами `-`, нужны подчеркивания `_`

## Что нужно сделать

### Шаг 1: Переименовать файлы (15 файлов)

Откройте Terminal и выполните:

```bash
cd /Users/MD/AI-Platform-ISO/docs
bash RENAME_FILES_SCRIPT.sh
```

Это переименует все файлы:
- `business-flow.html` → `business_flow.html`
- `bcm-philosophy.html` → `bcm_philosophy.html`
- `decision-center.html` → `decision_center.html`
- `mio-manager.html` → `mio_manager.html`
- `platform-overview.html` → `platform_overview.html`
- `workflow-intelligence.html` → `workflow_intelligence.html`
- `ai-foundation.html` → `ai_foundation.html`
- `eventbus-choreography.html` → `eventbus_choreography.html`
- `collective-intelligence.html` → `collective_intelligence.html`
- `expertise-center.html` → `expertise_center.html`
- `predictive-intelligence.html` → `predictive_intelligence.html`
- `governance-layer.html` → `governance_layer.html`
- `ace-service.html` → `ace_service.html`
- `service-catalog-visual.html` → `service_catalog_visual.html`
- `platform-services-overview.html` → `platform_services_overview.html`

### Шаг 2: Обновить ссылки во всех HTML файлах

```bash
cd /Users/MD/AI-Platform-ISO/docs
bash UPDATE_LINKS_SCRIPT.sh
```

Это обновит все `href="..."` ссылки во ВСЕХ HTML файлах (включая index.html, navigation, footer).

### Шаг 3: Проверить результат

Откройте `index.html` в браузере:

```bash
open /Users/MD/AI-Platform-ISO/docs/index.html
```

Проверьте:
- ✅ Все ссылки в навигации работают
- ✅ Все карточки в разделе "Deep-Dive Documentation" работают
- ✅ Все ссылки в футере работают
- ✅ Нет ошибок 404

### Шаг 4: Удалить backup файлы (если все OK)

```bash
cd /Users/MD/AI-Platform-ISO/docs
rm *.html.backup
```

---

## Альтернатива: Ручное переименование через Finder

Если терминал не работает, можно переименовать вручную:

1. Откройте Finder
2. Перейдите в `/Users/MD/AI-Platform-ISO/docs/`
3. Для каждого файла:
   - Правый клик → "Rename"
   - Замените `-` на `_`
   - Нажмите Enter

Потом выполните только Шаг 2 (UPDATE_LINKS_SCRIPT.sh)

---

## Проверка (если что-то пошло не так)

### Найти файлы с дефисами:
```bash
cd /Users/MD/AI-Platform-ISO/docs
ls -1 | grep "-"
```

### Найти ссылки с дефисами:
```bash
cd /Users/MD/AI-Platform-ISO/docs
grep -r 'href=".*-.*\.html"' *.html | grep -v backup
```

---

## Что дальше?

После успешного переименования и обновления ссылок:

1. ✅ Все файлы переименованы
2. ✅ Все ссылки обновлены
3. ✅ Проверено в браузере
4. ✅ Backup файлы удалены

**Готово!** Теперь Python может правильно читать все файлы.

---

## Файлы, созданные Claude Code:

- ✅ `RENAME_FILES_SCRIPT.sh` - скрипт переименования файлов
- ✅ `UPDATE_LINKS_SCRIPT.sh` - скрипт обновления ссылок
- ✅ `FILE_RENAME_CHECKLIST.md` - полный чеклист на английском
- ✅ `ИНСТРУКЦИЯ_ПЕРЕИМЕНОВАНИЕ.md` - эта инструкция на русском

**Дата создания**: 2025-10-15
**Автор**: Claude Code (AI Assistant)
