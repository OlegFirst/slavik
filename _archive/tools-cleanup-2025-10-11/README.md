# Архив: Tools Cleanup 2025-10-11

**Дата архивации**: 2025-10-11
**Причина**: Устранение дубликатов и пустых структур

---

## Что архивировано

### 1. `auto-generated/`
**Причина**: Дубликат `/infrastructure/tools/docker-generated/`
**Содержимое**:
- `docker-compose.auto.yml` (18KB)
- `docker-compose.improved.yml` (33KB)
- `service-catalog.json` (40KB)
- `prometheus.auto.yml`
- `gateway-routes.auto.json`

**Заметка**: Все эти файлы продублированы в `/infrastructure/tools/docker-generated/` с более свежими датами.

---

### 2. `deployment/`
**Причина**: Пустая структура (0 файлов Python, 0 строк кода)
**Содержимое**:
- `README.md` (generic template)
- `generated/` (пустая папка)

**Заметка**:
- Для Docker используется `/infrastructure/tools/docker-management/`
- Для generated конфигов используется `/infrastructure/tools/docker-generated/`

---

## Можно ли восстановить?

✅ **Да!** Все файлы сохранены в этой папке.

Если нужно восстановить:
```bash
# Восстановить auto-generated
cp -r /Users/MD/AI-Platform-ISO/_archive/tools-cleanup-2025-10-11/auto-generated \
      /Users/MD/AI-Platform-ISO/infrastructure/tools/

# Восстановить deployment
cp -r /Users/MD/AI-Platform-ISO/_archive/tools-cleanup-2025-10-11/deployment \
      /Users/MD/AI-Platform-ISO/infrastructure/
```

---

## Рекомендации

**Через 30 дней** (2025-11-10):
- Если не потребовалось восстановление → удалить этот архив

**Если нужны generated configs**:
- Использовать `/infrastructure/tools/docker-generated/` вместо `auto-generated/`

---

**Архивировано**: 2025-10-11
**Безопасно удалить после**: 2025-11-10
