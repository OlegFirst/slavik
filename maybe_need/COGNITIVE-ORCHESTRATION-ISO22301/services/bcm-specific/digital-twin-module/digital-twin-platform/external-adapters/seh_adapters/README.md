
# SEH Adapters — SimPy / Mesa / EpiNow2 (Minimal)

## Быстрый старт
```bash
docker compose build
docker compose up -d
```

## Эндпоинты
- SimPy:   POST http://localhost:7001/run
- Mesa:    POST http://localhost:7002/run
- EpiNow2: POST http://localhost:7003/run

## Примеры запросов
### SimPy (очередь/capacity)
```bash
curl -s http://localhost:7001/run -H "Content-Type: application/json" -d '{
  "experiment":"simpy_queue",
  "params":{
    "arrival_rate":12,
    "service_time":{"dist":"lognormal","mu":"10m","sigma":0.5},
    "capacity_agents":[6,8,10],
    "targets":{"sla_target":0.95,"wait_p50_min":"15m"}
  },
  "monte_carlo_runs": 50
}'
```

### Mesa (ABM-политики)
```bash
curl -s http://localhost:7002/run -H "Content-Type: application/json" -d '{
  "experiment":"mesa_abm",
  "params":{"steps":200,"population_size":2000,"policies":{"sms":1.5,"vouchers":1.1}},
  "monte_carlo_runs": 100
}'
```

### EpiNow2 (Rt демо)
```bash
curl -s http://localhost:7003/run -H "Content-Type: application/json" -d '{
  "experiment":"epi_nowcasting_rt",
  "params":{"cases_ts":"supabase://bucket/path.csv","generation_time":"dist_ref","reporting_delay":"dist_ref"}
}'
```

## Интеграция с нашим воркером
Маршрутизация по `experiment`:
- `simpy_queue` → http://seh-simpy:7001/run
- `mesa_abm`    → http://seh-mesa:7002/run
- `epi_nowcasting_rt` → http://seh-epinow2:7003/run

Ответы уже соответствуют нашему стандарту: `run_id/experiment/best/frontier/explain`.

> Примечание: В EpiNow2 сейчас заглушка на Rt. Подключите реальные ряды случаев и параметры генерационного времени — замените демо-часть на вызов `epinow()`.
