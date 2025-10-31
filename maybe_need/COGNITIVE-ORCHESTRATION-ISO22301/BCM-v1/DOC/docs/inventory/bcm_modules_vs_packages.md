# BCM Modules vs Root Packages Inventory

This document clarifies the usage of the `bcm_` prefix across the codebase and
explains where functionality lives.

## Odoo Modules (`core/odoo-18.0/addons/bcm_*`)
The following modules implement business logic inside the Odoo backend:

- `bcm_core` – base models, security groups and shared utilities.
- `bcm_config` – platform configuration and webhooks.
- `bcm_clients` – client records, contacts, API keys and vault.
- `bcm_bia` – business impact analysis processes and computations.
- `bcm_plans` – continuity plans and procedures.
- `bcm_incident` – incident records and AI generated checklists.
- `bcm_kpi` – KPI metrics, dashboards and reports.
- `bcm_portal` – portal dashboards and chat history.
- `bcm_scenario_hub` – scenario catalogue, reviews and ratings.
- Additional support modules: `bcm_templates`, `bcm_training`, `bcm_governance`,
  `bcm_audit`, `bcm_exercise`, `bcm_intelligent_base`, `bcm_risk_management`,
  `bcm_incident_management`, `bcm_reporting`, etc.

These modules are the authoritative place for BCM data and actions.

## Root Packages (`ai_orchestrator/app/*`)
Historically some Python packages also used the `bcm_` prefix. The remaining
ones have been renamed to avoid confusion:

- `api/v1/endpoints/scenarios.py` – REST endpoints for AI scenario operations.
- `schemas/scenario.py` – Pydantic models for scenario requests and responses.
- `models/scenario.py` – lightweight model used by the orchestrator service.

No other root-level packages use the `bcm_` prefix.

These packages live outside the Odoo `core` tree and operate as standalone services,
so neutral names help differentiate them from the Odoo modules.

## Decision
The project will keep the Odoo modules with their `bcm_` prefixes as the core
implementation. Root Python packages should avoid the prefix to reduce
ambiguity. Existing `bcm_*` packages have been renamed accordingly and new
services should follow the neutral naming convention (e.g., `scenarios.py` rather
than `bcm_scenarios.py`).
