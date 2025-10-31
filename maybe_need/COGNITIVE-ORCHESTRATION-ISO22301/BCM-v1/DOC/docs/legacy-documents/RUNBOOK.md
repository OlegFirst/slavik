# Runbook

## SSE
```
curl -N -H "Accept: text/event-stream" "https://<host>/api/events/stream?tenant=demo"
```

## Odoo
```
curl -s "https://<host>/api/odoo/health" | jq
```

## KPI
```
curl -s "https://<host>/api/kpi/overview" | jq 'type,length?'
```
