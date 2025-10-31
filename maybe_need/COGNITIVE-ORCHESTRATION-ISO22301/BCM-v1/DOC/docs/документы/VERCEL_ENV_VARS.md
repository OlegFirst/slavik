# Vercel Environment Variables Configuration

## Remove these VITE_ variables:
- VITE_DISABLE_AUTH
- VITE_DOCPROC_URL  
- VITE_ODOO_URL
- VITE_ORCHESTRATOR_URL
- VITE_EVENTBUS_URL

## Add these VUE_APP_ variables instead:

```
VUE_APP_DISABLE_AUTH=true
VUE_APP_DEMO_MODE=true
VUE_APP_DOCPROC_URL=/api/docproc
VUE_APP_ODOO_URL=/odoo
VUE_APP_ORCHESTRATOR_URL=/api
VUE_APP_EVENTBUS_URL=/api/events
```

Or for demo mode (no backend):
```
VUE_APP_DISABLE_AUTH=true
VUE_APP_DEMO_MODE=true
VUE_APP_DOCPROC_URL=
VUE_APP_ODOO_URL=
VUE_APP_ORCHESTRATOR_URL=
VUE_APP_EVENTBUS_URL=
```
