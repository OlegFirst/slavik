============================================================
📊 DEPENDENCY RECONCILIATION REPORT
============================================================

🆕 MISSING SERVICES (17):
  • runtime_realtime-websocket
  • simulation
  • security_auth
  • ai-foundation
  • database_vector-db
  • runtime_eventbus
  • gateway_unified_database_gateway
  • integration_github-integration
  • архив_event-bus
  • observability_mio-manager
  • gateway_api-gateway
  • gateway_agent-router
  • database_postgresql
  • архив_eventbus

📌 MISSING DEPENDENCIES (36 services):
  • predictive: ai_foundation/workflow_intelligence, ai_services/predictive
  • можетпригодится: database/postgresql, runtime/eventbus
  • _archive: ai_foundation/workflow_intelligence, runtime/eventbus, ai_foundation/workflow_engine, ai_services/predictive, database/postgresql
  • expertise-center: shared/base, ai_foundation/expertise_center
  • gateway_api-gateway: runtime/eventbus
  • gateway_agent-router: runtime/eventbus
  • documents_service: ai_foundation/workflow_intelligence, shared/database, shared/auth
  • planning_service: shared/utils, shared/cache, ai_foundation/workflow_intelligence
  • risk_service: ai_foundation/workflow_intelligence
  • runtime_realtime-websocket: database/postgresql, runtime/eventbus
  ... and 26 more

⚠️  OBSOLETE DEPENDENCIES (10 services):
  • documents_service: ai_services/living_docs
  • orchestration: external/external/temporal-cloud
  • learning_system: database/postgresql
  • recovery_service: database/postgresql
  • incident_service: database/postgresql, runtime/eventbus

✅ CHANGES APPLIED:
  • Added 14 services
  • Updated dependencies for 33 services

============================================================