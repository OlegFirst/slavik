# СРОЧНО: Исправление Vercel интеграции

## Проблема
@superman32432432 пытается деплоить в твою команду "Max's projects" на Vercel, но не является участником команды.

## Решение

### Вариант 1: Отключить @superman32432432 от GitHub (РЕКОМЕНДУЕТСЯ)

1. Зайди на GitHub: https://github.com/SEH-foundation/ISO-22301/settings
2. Слева выбери "Integrations" или "Installed GitHub Apps"
3. Найди Vercel интеграцию для @superman32432432
4. Нажми "Configure" → "Revoke" или "Uninstall"

### Вариант 2: Через Vercel Dashboard

1. Зайди в Vercel под своим аккаунтом: https://vercel.com/maxdemchenko-6220
2. Перейди в настройки проекта
3. Раздел "Git" → отключи неправильную интеграцию
4. Переподключи к правильному GitHub аккаунту

### После отключения @superman32432432:

1. Зайди в Vercel: https://vercel.com/maxdemchenko-6220  
2. Импортируй проект заново:
   - Нажми "New Project"
   - Выбери репозиторий SEH-foundation/ISO-22301
   - Root Directory: `frontend/web_portal`
   - Framework: Vue.js
   - Build Command: `npm run build`

## Важно
- НЕ добавляй @superman32432432 в свою команду
- НЕ делай репозиторий публичным (если не хочешь)
- Проблема именно в том, что чужой аккаунт пытается деплоить в твою команду