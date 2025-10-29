# 🚀 Vercel Deployment Instructions

## Current Setup
- Root Directory: **пустой** (весь репо)
- Build Command: автоматически из `vercel.json`
- Output Directory: автоматически из `vercel.json`

## vercel.json Configuration
Создан в корне проекта:
```json
{
  "buildCommand": "cd frontend/web_portal && npm ci && npm run build",
  "outputDirectory": "frontend/web_portal/dist",
  "installCommand": "cd frontend/web_portal && npm ci",
  "rewrites": [
    { "source": "/(.*)", "destination": "/" }
  ]
}
```

## Environment Variables для Vercel
```
VITE_EVENTBUS_URL=/api/events
VITE_ORCHESTRATOR_URL=/api
VITE_ODOO_URL=/odoo
VITE_DOCPROC_URL=/api/docproc
```

## Настройки в Vercel Dashboard
1. **Framework Preset**: Other
2. **Root Directory**: (оставить пустым)
3. **Build Command**: (будет взято из vercel.json)
4. **Output Directory**: (будет взято из vercel.json)
5. **Install Command**: (будет взято из vercel.json)

## После деплоя
Frontend будет работать, но API вызовы будут идти на относительные пути.
Для полной функциональности нужно:
1. Развернуть backend сервисы
2. Настроить правильные API URLs в environment variables
