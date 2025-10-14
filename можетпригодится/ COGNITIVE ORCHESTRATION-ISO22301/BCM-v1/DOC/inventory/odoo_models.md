# Odoo BCM Models Inventory

## Models Overview

### Multi-tenancy Status
✅ = Has company_id field with index
❌ = Missing company_id
🔗 = Has company_id via relation

## Core Foundation Models

### bcm_core
| Model | company_id | Key Fields | Relationships |
|-------|------------|------------|---------------|
| `bcm.base` (Abstract) | ✅ | active, iso_clause, compliance_level, risk_level, last_review_date, next_review_date | Base for all BCM models |
| `bcm.tag` | ❌ | name, color | Many2many with various models |

### bcm_config  
| Model | company_id | Key Fields | Purpose |
|-------|------------|------------|---------|
| `bcm.config` | ✅ | eventbus_url, orchestrator_url, bia_engine_url, document_processor_url | Service configuration |
| `bcm.webhook.mixin` (Abstract) | Via mixin | - | Webhook sending functionality |
| `bcm.company.mixin` (Abstract) | ✅ | company_id | Multi-tenancy mixin |

## Client Management Models

### bcm_clients
| Model | company_id | Key Fields | Smart Buttons |
|-------|------------|------------|---------------|
| `bcm.client` | ✅ | name, sector, region, onboarding_stage, dpa_signed, data_residency, status | Contacts, Vault, API Keys, Processes, BIA, Plans, Incidents |
| `bcm.client.contact` | 🔗 | client_id, user_id, role, active | - |
| `bcm.client.appkey` | 🔗 | client_id, api_key, permissions, valid_until, rate_limit | - |
| `bcm.client.vault` | 🔗 | client_id, context_type, name, data, metadata | - |
| `bcm.scope` | ❌ | name, description | - |

## Business Impact Analysis

### bcm_bia
| Model | company_id | Key Fields | Actions |
|-------|------------|------------|---------|
| `bcm.industry.type` | ✅ | name, code, revenue_loss_multiplier, base_rto_hours, base_rpo_minutes | - |
| `bcm.business.process` | ✅ | name, criticality, annual_revenue_impact, optimized_rto_hours, optimized_rpo_minutes, mtpd_hours | `action_compute_bia()`, `action_run_ai_analysis()` |
| `bcm.bia.analysis` | ✅ | name, process_ids, risk_tolerance, budget_constraint, state | `action_run_comprehensive_analysis()` |
| `bcm.compliance.requirement` | ✅ | name, code, description | - |
| `bcm.technology.stack` | ✅ | name, category, description | - |

## Plans & Procedures

### bcm_plans
| Model | company_id | Key Fields | Actions |
|-------|------------|------------|---------|
| `bcm.plan` | ✅ | name, plan_type, priority, status, version, process_ids, plan_owner_id | `action_activate()`, `action_deactivate()`, `action_generate_draft()` |
| `bcm.plan.procedure` | 🔗 | plan_id, sequence, name, responsible_user_id, estimated_duration, is_critical | - |
| `bcm.plan.resource` | 🔗 | plan_id, resource_type, name, quantity | - |
| `bcm.plan.execution` | 🔗 | plan_id, execution_date, status, duration | - |

## Incident Management

### bcm_incident
| Model | company_id | Key Fields | Actions |
|-------|------------|------------|---------|
| `bcm_incident.record` | ✅ | name, active, notes | - |
| `bcm.incident` (via mixin) | ✅ | Via bcm.company.mixin | `action_ai_draft_response()` |

## Portal & Chat

### bcm_portal
| Model | company_id | Key Fields | Purpose |
|-------|------------|------------|---------|
| `bcm.chat.history` | ✅ | user_id, message, response, context, model_used | AI chat history |
| `bcm.portal.dashboard` | ✅ | name, user_id, widgets | User dashboards |

## KPI & Analytics

### bcm_kpi
| Model | company_id | Key Fields | Actions |
|-------|------------|------------|---------|
| `bcm.kpi.category` | ✅ | name, sequence, description, color | - |
| `bcm.kpi` | ✅ | name, category_id, measurement_unit, calculation_method, target_value, critical_threshold | `action_calculate_kpis()` |
| `bcm.kpi.measurement` | 🔗 | kpi_id, measurement_date, value, verified | `action_verify()` |
| `bcm.kpi.dashboard` | ✅ | name, dashboard_type, kpi_ids, refresh_interval | - |
| `bcm.kpi.report` | ✅ | name, report_type, period_from, period_to, kpi_ids | `action_generate_report()`, `action_send_report()` |

## Scenario Management

### bcm_scenario_hub
| Model | company_id | Key Fields | Actions |
|-------|------------|------------|---------|
| `bcm.scenario` | ✅ | name, description, domain_id, impact_level, likelihood | `action_submit_for_review()`, `action_approve()`, `action_reject()`, `action_fork()`, `action_apply_to_client()` |
| `bcm.scenario.rating` | Referenced | - | - |
| `bcm.scenario.review` | Referenced | - | - |
| `bcm.domain` | Referenced | - | - |

## Action Buttons Catalog

### BIA Actions
| Action | Module | Description | External Call |
|--------|--------|-------------|---------------|
| `action_compute_bia()` | bcm.business.process | Compute BIA via external engine | POST to BIA_ENGINE_URL/compute |
| `action_run_ai_analysis()` | bcm.business.process | Fallback AI analysis | Internal calculation |
| `action_run_comprehensive_analysis()` | bcm.bia.analysis | Multi-process BIA | Batch processing |

### Plan Actions
| Action | Module | Description | External Call |
|--------|--------|-------------|---------------|
| `action_generate_draft()` | bcm.plan | Generate AI plan steps | POST to ORCHESTRATOR_URL/recommendations |
| `action_activate()` | bcm.plan | Activate plan | Internal |
| `action_deactivate()` | bcm.plan | Deactivate plan | Internal |

### Incident Actions
| Action | Module | Description | External Call |
|--------|--------|-------------|---------------|
| `action_ai_draft_response()` | bcm.incident | Generate response checklist | POST to ORCHESTRATOR_URL/recommendations |

### Client Actions
| Action | Module | Description | External Call |
|--------|--------|-------------|---------------|
| `action_archive_client()` | bcm.client | Archive client | Publishes event |
| `action_reindex_context()` | bcm.client | Reindex in AI system | POST to ORCHESTRATOR_URL/reindex |
| `action_view_*` | bcm.client | Navigation actions | Internal |
| `action_revoke()` | bcm.client.appkey | Revoke API key | Internal |
| `action_regenerate()` | bcm.client.appkey | New API token | Internal |

### KPI Actions
| Action | Module | Description | External Call |
|--------|--------|-------------|---------------|
| `action_calculate_kpis()` | bcm.kpi | Calculate metrics | Publishes bcm.kpi.calculated |
| `action_verify()` | bcm.kpi.measurement | Verify measurement | Internal |
| `action_generate_report()` | bcm.kpi.report | Generate report | Internal |
| `action_send_report()` | bcm.kpi.report | Email report | SMTP |

## Webhook Configurations

### Webhook Mixin Methods
```python
class BCMWebhookMixin:
    def send_event_to_eventbus(event_type, data)
    def call_orchestrator(endpoint, data)
```

### Events Published
| Event | Triggered By | Payload |
|-------|--------------|---------|
| `bcm.bia.completed` | BIA calculation complete | bia_id, rto, rpo, mtpd |
| `bcm.plan.draft_generated` | Plan draft created | plan_id, steps |
| `bcm.incident.response_generated` | Response created | incident_id, checklist |
| `bcm.kpi.calculated` | KPI calculation | metrics dict |
| `client.created` | New client | client_id, name |
| `client.updated` | Client modified | client_id, changes |
| `client.archived` | Client archived | client_id |

## Portal Controllers

### Main Portal (`bcm_portal.portal_main`)
| Route | Method | Auth | Description |
|-------|--------|------|-------------|
| `/my/bcm` | GET | user | Main dashboard |
| `/my/bcm/bia` | GET | user | BIA portal |
| `/my/bcm/plans` | GET | user | Plans page |
| `/my/bcm/incidents` | GET | user | Incidents |
| `/my/bcm/exercises` | GET | user | Exercises |
| `/my/bcm/audit` | GET | user | Audit findings |
| `/my/bcm/training` | GET | user | Training |

### Portal Actions (`bcm_portal.portal_actions`)
| Route | Method | Auth | Description |
|-------|--------|------|-------------|
| `/portal/bcm/upload-evidence` | POST | user | Upload evidence |
| `/portal/bcm/request-audit` | POST | user | Request audit |
| `/portal/bcm/schedule-exercise` | POST | user | Schedule exercise |

### AI Assistant (`bcm_portal.ai_assistant`)
| Route | Method | Auth | Description |
|-------|--------|------|-------------|
| `/portal/bcm/ai/chat` | POST | user | AI chat |
| `/portal/bcm/ai/recommendations` | GET | user | Get recommendations |

### KPI API (`bcm_kpi.kpi_api`)
| Route | Method | Auth | Description |
|-------|--------|------|-------------|
| `/bcm/kpi` | GET/POST | public* | Get current KPIs |
| `/bcm/kpi/calculate` | POST | user | Trigger calculation |

*Note: KPI endpoint configured for public access for dashboard integration

## Computed KPI Metrics

### Core Metrics
1. **BIA Coverage** = `covered_processes / total_processes * 100`
2. **Plans Up-to-date** = `current_plans / total_plans * 100` (updated < 6 months)
3. **CAPA On-time** = `ontime_capa / total_capa * 100`

### Additional Metrics
4. **Incident Response Time** = Average hours from creation to response
5. **Exercise Completion** = `completed_exercises / total_exercises * 100`
6. **Training Completion** = `completed_training / total_training * 100`

## Security & Access Control

### Groups
- `bcm_core.group_bcm_portal` - Portal users
- `bcm_core.group_bcm_internal` - Internal BCM users
- `bcm_core.group_bcm_manager` - BCM managers

### Record Rules
- Portal users: `[('company_id', '=', user.company_id.id)]`
- Internal users: `[(1, '=', 1)]` (all companies)
- Regular users: `[('company_id', 'in', company_ids)]`
