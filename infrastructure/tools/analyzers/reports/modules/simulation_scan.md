# Module Scan Report: simulation

**Дата сканирования:** 2025-10-06 21:11
**Путь:** `platform-services/simulation`

---

## 📊 Метрики

| Метрика | Значение |
|---------|----------|
| **LOC** | 44465 |
| **Python файлов** | 160 |
| **Классов** | 382 |
| **Функций** | 81 |
| **API Endpoints** | 233 |
| **Зависимостей** | 138 |

---

## 🔗 Зависимости (138)


### abc
- `abc`

### advanced_scenario_generator
- `advanced_scenario_generator`

### ai_scenario_generator
- `ai_scenario_generator`

### aiofiles
- `aiofiles`

### aiohttp
- `aiohttp`

### alembic
- `alembic`

### api
- `api`

### api.app
- `api.app`

### api.auth
- `api.auth`

### api.auth.dependencies
- `api.auth.dependencies`

### api.auth.jwt
- `api.auth.jwt`

### api.auth.password
- `api.auth.password`

### api.routers.auth
- `api.routers.auth`

### app
- `app`

### app.api.v1.endpoints.scenarios
- `app.api.v1.endpoints.scenarios`

### app.core.ai_engine
- `app.core.ai_engine`

### app.core.database
- `app.core.database`

### app.core.security
- `app.core.security`

### app.models
- `app.models`

### app.schemas.scenario
- `app.schemas.scenario`

### argparse
- `argparse`

### asyncio
- `asyncio`

### base
- `base`

### base64
- `base64`

### base_engine
- `base_engine`

### bridge
- `bridge`

### bridges.bia_engine.client
- `bridges.bia_engine.client`

### bridges.odoo
- `bridges.odoo`

### bridges.scenario_ai.client
- `bridges.scenario_ai.client`

### ciw
- `ciw`

### client
- `client`

### collector
- `collector`

### collectors.base
- `collectors.base`

### collectors.builtin.generic_rest_collector
- `collectors.builtin.generic_rest_collector`

### collectors.builtin.hubspot_collector
- `collectors.builtin.hubspot_collector`

### collectors.builtin.odoo_collector
- `collectors.builtin.odoo_collector`

### collectors.builtin.salesforce_collector
- `collectors.builtin.salesforce_collector`

### config
- `config`

### conflict_resolver
- `conflict_resolver`

### contextlib
- `contextlib`

### core.ai.advanced_scenario_generator
- `core.ai.advanced_scenario_generator`

### core.engine.monte_carlo_engine
- `core.engine.monte_carlo_engine`

### core.engine.prediction_engine
- `core.engine.prediction_engine`

### core.engine.queue_theory_engine
- `core.engine.queue_theory_engine`

### core.engine.simulation_engine
- `core.engine.simulation_engine`

### core.models.base
- `core.models.base`

### csv
- `csv`

### csv_collector
- `csv_collector`

### database
- `database/postgresql`

### database.base
- `database.base`

### database_collector
- `database_collector`

### dataclasses
- `dataclasses`

### datetime
- `datetime`

### dependencies
- `dependencies`

### difflib
- `difflib`

### dotenv
- `dotenv`

### engines.monte_carlo_engine
- `engines.monte_carlo_engine`

### engines.scenario_engine
- `engines.scenario_engine`

### engines.what_if_engine
- `engines.what_if_engine`

### enricher
- `enricher`

### entity_resolver
- `entity_resolver`

### enum
- `enum`

### fastapi
- `fastapi`

### fastapi.middleware.cors
- `fastapi.middleware.cors`

### fastapi.responses
- `fastapi.responses`

### fastapi.security
- `fastapi.security`

### generic_rest_collector
- `generic_rest_collector`

### hashlib
- `hashlib`

### hmac
- `hmac`

### httpx
- `httpx`

### hubspot
- `hubspot`

### hubspot.crm.companies
- `hubspot.crm.companies`

### hubspot.crm.contacts
- `hubspot.crm.contacts`

### hubspot_collector
- `hubspot_collector`

### impact_passport_engine
- `impact_passport_engine`

### io
- `io`

### jaamsim_client
- `jaamsim_client`

### jose
- `jose`

### json
- `json`

### jwt
- `jwt`

### logging
- `logging`

### logging.config
- `logging.config`

### main
- `main`

### manager
- `manager`

### math
- `math`

### metrics_engine
- `metrics_engine`

### mock_data
- `mock_data`

### models
- `models`

### models.simulation_model
- `models.simulation_model`

### nics_client
- `nics_client`

### normalizer
- `normalizer`

### numpy
- `numpy`

### odoo
- `odoo`

### odoo.exceptions
- `odoo.exceptions`

### odoo_collector
- `odoo_collector`

### os
- `os`

### pandas
- `pandas`

### passlib.context
- `passlib.context`

### password
- `password`

### pathlib
- `pathlib`

### postgres_storage
- `postgres_storage`

### prediction_engine
- `prediction_engine`

### pydantic
- `pydantic`

### pydantic_settings
- `pydantic_settings`

### pytest
- `pytest`

### random
- `random`

### re
- `re`

### requests
- `requests`

### routers
- `routers`

### runtime
- `runtime/eventbus`

### salesforce_collector
- `salesforce_collector`

### scenario
- `scenario`

### scenarios
- `scenarios`

### services.processor
- `services.processor`

### services.thehive_client
- `services.thehive_client`

### shutil
- `shutil`

### simple_salesforce
- `simple_salesforce`

### simulation_engine
- `simulation_engine`

### statistics
- `statistics`

### storage
- `storage`

### storage.models
- `storage.models`

### storage.postgres_storage
- `storage.postgres_storage`

### structlog
- `structlog`

### subprocess
- `subprocess`

### sync
- `sync`

### sys
- `sys`

### thehive_client
- `thehive_client`

### toc_engine
- `toc_engine`

### twin_engine
- `twin_engine`

### typing
- `typing`

### unittest.mock
- `unittest.mock`

### urllib.parse
- `urllib.parse`

### uuid
- `uuid`

### uvicorn
- `uvicorn`

### websockets
- `websockets`

### xml.etree.ElementTree
- `xml.etree.ElementTree`

### xmlrpc.client
- `xmlrpc.client`

### zipfile
- `zipfile`

---

## 🌐 API Endpoints (233)

- **GET** `/health` (файл: `main.py`)
- **GET** `/` (файл: `main.py`)
- **GET** `/health` (файл: `bridge_service.py`)
- **POST** `/api/v1/incident/create-case` (файл: `bridge_service.py`)
- **POST** `/api/v1/exercise/create-case` (файл: `bridge_service.py`)
- **PUT** `/api/v1/case/{case_id}` (файл: `bridge_service.py`)
- **GET** `/api/v1/case/{case_id}` (файл: `bridge_service.py`)
- **GET** `/api/v1/cases` (файл: `bridge_service.py`)
- **POST** `/api/v1/case/{case_id}/sync` (файл: `bridge_service.py`)
- **GET** `/api/v1/metrics` (файл: `bridge_service.py`)

---

## 💻 Классы (382)

- **BCMIncidentUnified** (47 методов) - `bcm_incident_unified.py`
- **TheHiveClient** (14 методов) - `thehive_client.py`
- **BCMIncidentMigration** (14 методов) - `migration_script.py`
- **ToCEngine** (13 методов) - `toc_engine.py`
- **BCMTheHiveIntegration** (12 методов) - `thehive_client.py`
- **QueueTheoryEngine** (12 методов) - `queue_theory_engine.py`
- **ConflictResolver** (12 методов) - `conflict_resolver.py`
- **Config** (11 методов) - `config.py`
- **CollectorManager** (10 методов) - `manager.py`
- **TestJWTTokens** (10 методов) - `test_auth_jwt.py`

---

## 📂 Структура

**Всего файлов:** 415
**Директорий:** 118
