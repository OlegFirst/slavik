# Business Logic Map

## Statistics

- **database_query**: 1096 occurrences
- **http_call**: 1084 occurrences
- **eventbus_publish**: 570 occurrences
- **eventbus_subscribe**: 161 occurrences
- **temporal_workflow**: 134 occurrences
- **analyzer_call**: 94 occurrences
- **service_registry**: 53 occurrences
- **coordination_intent**: 7 occurrences

## Patterns by Module

### infrastructure/eventbus

#### eventbus_publish (10 files)

**infrastructure/eventbus/__init__.py**
- Found 2 matches

**infrastructure/eventbus/core/interface.py**
- Found 4 matches

**infrastructure/eventbus/backends/memory.py**
- Found 4 matches

**infrastructure/eventbus/backends/redis_streams.py**
- Found 4 matches

**infrastructure/eventbus/tests/test_memory_backend.py**
- Found 16 matches

**infrastructure/eventbus/examples/basic_usage.py**
- Found 2 matches

**infrastructure/eventbus/examples/redis_example.py**
- Found 2 matches

**infrastructure/eventbus/examples/subscriber_example.py**
- Found 10 matches

**infrastructure/eventbus/examples/fastapi_integration.py**
- Found 16 matches

**infrastructure/eventbus/events/test_eventbus_connection.py**
- Found 3 matches

#### eventbus_subscribe (11 files)

**infrastructure/eventbus/__init__.py**
- Found 2 matches

**infrastructure/eventbus/core/interface.py**
- Found 4 matches

**infrastructure/eventbus/backends/memory.py**
- Found 4 matches

**infrastructure/eventbus/backends/redis_streams.py**
- Found 1 matches

**infrastructure/eventbus/tests/test_memory_backend.py**
- Found 8 matches

**infrastructure/eventbus/examples/basic_usage.py**
- Found 1 matches

**infrastructure/eventbus/examples/redis_example.py**
- Found 1 matches

**infrastructure/eventbus/examples/subscriber_example.py**
- Found 9 matches

**infrastructure/eventbus/examples/fastapi_integration.py**
- Found 5 matches

**infrastructure/eventbus/subscribers/__init__.py**
- Found 1 matches

### intelligent-core/expertise-center

#### analyzer_call (2 files)

**intelligent-core/expertise-center/core/chief_executive.py**
- Found 2 matches

**intelligent-core/expertise-center/service/api/analyzers.py**
- Found 1 matches

#### database_query (1 files)

**intelligent-core/expertise-center/core/organism_coordinator.py**
- Found 1 matches

#### eventbus_subscribe (2 files)

**intelligent-core/expertise-center/service/standalone_main.py**
- Found 1 matches

**intelligent-core/expertise-center/service/main.py**
- Found 2 matches

#### http_call (17 files)

**intelligent-core/expertise-center/domains/bcm/analyzers/lifecycle_analyzer.py**
- Found 9 matches

**intelligent-core/expertise-center/domains/bcm/analyzers/impact_analyzer.py**
- Found 6 matches

**intelligent-core/expertise-center/domains/bcm/analyzers/performance_analyzer.py**
- Found 9 matches

**intelligent-core/expertise-center/domains/bcm/analyzers/plan_analyzer.py**
- Found 9 matches

**intelligent-core/expertise-center/domains/bcm/analyzers/scenario_analyzer.py**
- Found 6 matches

**intelligent-core/expertise-center/domains/bcm/analyzers/emergency_analyzer.py**
- Found 6 matches

**intelligent-core/expertise-center/domains/bcm/analyzers/risk_analyzer.py**
- Found 3 matches

**intelligent-core/expertise-center/domains/bcm/analyzers/compliance_analyzer.py**
- Found 6 matches

**intelligent-core/expertise-center/domains/bcm/analyzers/learning_analyzer.py**
- Found 6 matches

**intelligent-core/expertise-center/domains/bcm/tactical_assistants/community_specialist.py**
- Found 6 matches

### intelligent-core/orchestration

#### analyzer_call (2 files)

**intelligent-core/orchestration/bcm-services-orchestrator/bcm_orchestrator.py**
- Found 6 matches

**intelligent-core/orchestration/bcm-services-orchestrator/analyzer_coordinator.py**
- Found 50 matches

#### coordination_intent (2 files)

**intelligent-core/orchestration/coordination-center/core/tool_registry.py**
- Found 2 matches

**intelligent-core/orchestration/coordination-center/core/command_interpreter.py**
- Found 2 matches

#### database_query (4 files)

**intelligent-core/orchestration/ai-orchestration/orchestrator.py**
- Found 1 matches

**intelligent-core/orchestration/ai-orchestration/memory/short_term_memory.py**
- Found 9 matches

**intelligent-core/orchestration/ai-orchestration/decision_center/__init__.py**
- Found 1 matches

**intelligent-core/orchestration/ai-orchestration/decision_center/strategy_selector.py**
- Found 1 matches

#### eventbus_publish (14 files)

**intelligent-core/orchestration/bcm-services-orchestrator/bcm_orchestrator.py**
- Found 3 matches

**intelligent-core/orchestration/bcm-services-orchestrator/analyzer_coordinator.py**
- Found 3 matches

**intelligent-core/orchestration/ai-orchestration/orchestrator.py**
- Found 3 matches

**intelligent-core/orchestration/ai-orchestration/main.py**
- Found 6 matches

**intelligent-core/orchestration/ai-orchestration/core/base_orchestrator.py**
- Found 3 matches

**intelligent-core/orchestration/ai-orchestration/core/event_coordinator.py**
- Found 2 matches

**intelligent-core/orchestration/ai-orchestration/decision_center/delegation_manager.py**
- Found 6 matches

**intelligent-core/orchestration/ai-orchestration/platform_orch/platform_orchestrator.py**
- Found 4 matches

**intelligent-core/orchestration/ai-orchestration/scenario/scenario_orchestrator.py**
- Found 1 matches

**intelligent-core/orchestration/ai-orchestration/ai/ai_orchestrator.py**
- Found 10 matches

#### eventbus_subscribe (6 files)

**intelligent-core/orchestration/bcm-services-orchestrator/bcm_orchestrator.py**
- Found 3 matches

**intelligent-core/orchestration/ai-orchestration/orchestrator.py**
- Found 6 matches

**intelligent-core/orchestration/ai-orchestration/core/base_orchestrator.py**
- Found 1 matches

**intelligent-core/orchestration/ai-orchestration/decision_center/delegation_manager.py**
- Found 2 matches

**intelligent-core/orchestration/task_queue/eventbus_bridge.py**
- Found 1 matches

**intelligent-core/orchestration/coordination-center/main.py**
- Found 5 matches

#### http_call (21 files)

**intelligent-core/orchestration/pdca_assistant.py**
- Found 1 matches

**intelligent-core/orchestration/ai-orchestration/core/health_monitor.py**
- Found 1 matches

**intelligent-core/orchestration/ai-orchestration/tentacles/knowledge_orchestrator.py**
- Found 9 matches

**intelligent-core/orchestration/ai-orchestration/tentacles/ai_office_connector.py**
- Found 1 matches

**intelligent-core/orchestration/ai-orchestration/muscles/agent_router.py**
- Found 6 matches

**intelligent-core/orchestration/ai-orchestration/muscles/model_selector.py**
- Found 3 matches

**intelligent-core/orchestration/ai-orchestration/muscles/llm_clients/anthropic_client.py**
- Found 6 matches

**intelligent-core/orchestration/ai-orchestration/muscles/ai_organs/compliance_guardian.py**
- Found 6 matches

**intelligent-core/orchestration/ai-orchestration/muscles/ai_organs/risk_advisor.py**
- Found 3 matches

**intelligent-core/orchestration/ai-orchestration/muscles/ai_organs/plan_generator.py**
- Found 9 matches

#### service_registry (3 files)

**intelligent-core/orchestration/bcm-services-orchestrator/bcm_orchestrator.py**
- Found 15 matches

**intelligent-core/orchestration/bcm-services-orchestrator/service_registry.py**
- Found 15 matches

**intelligent-core/orchestration/coordination-center/core/service_aggregator.py**
- Found 2 matches

#### temporal_workflow (2 files)

**intelligent-core/orchestration/bcm-services-orchestrator/bcm_orchestrator.py**
- Found 2 matches

**intelligent-core/orchestration/ai-orchestration/decision_center/delegation_manager.py**
- Found 2 matches

### intelligent-core/workflow_intelligence

#### analyzer_call (2 files)

**intelligent-core/workflow_intelligence/temporal_workflows/risk_workflow.py**
- Found 12 matches

**intelligent-core/workflow_intelligence/temporal_workflows/bia_workflow.py**
- Found 15 matches

#### database_query (21 files)

**intelligent-core/workflow_intelligence/tests/conftest.py**
- Found 1 matches

**intelligent-core/workflow_intelligence/tests/test_rls.py**
- Found 4 matches

**intelligent-core/workflow_intelligence/tests/test_postgres_adapter.py**
- Found 4 matches

**intelligent-core/workflow_intelligence/tests/test_integration_security.py**
- Found 1 matches

**intelligent-core/workflow_intelligence/tests/test_sql_injection.py**
- Found 12 matches

**intelligent-core/workflow_intelligence/storage/rls_context.py**
- Found 19 matches

**intelligent-core/workflow_intelligence/storage/postgres_adapter.py**
- Found 18 matches

**intelligent-core/workflow_intelligence/audit/storage.py**
- Found 2 matches

**intelligent-core/workflow_intelligence/case_library/repository.py**
- Found 1 matches

**intelligent-core/workflow_intelligence/venv/lib/python3.11/site-packages/typing_extensions.py**
- Found 2 matches

#### eventbus_publish (6 files)

**intelligent-core/workflow_intelligence/core/workflow_engine.py**
- Found 12 matches

**intelligent-core/workflow_intelligence/integration/eventbus_publisher.py**
- Found 15 matches

**intelligent-core/workflow_intelligence/integration/bia_adapter.py**
- Found 3 matches

**intelligent-core/workflow_intelligence/tests/test_workflow_engine.py**
- Found 3 matches

**intelligent-core/workflow_intelligence/workflows/temporal/bia_workflow.py**
- Found 1 matches

**intelligent-core/workflow_intelligence/monitoring/metrics.py**
- Found 3 matches

#### eventbus_subscribe (3 files)

**intelligent-core/workflow_intelligence/main.py**
- Found 1 matches

**intelligent-core/workflow_intelligence/tests/test_workflow_engine.py**
- Found 10 matches

**intelligent-core/workflow_intelligence/case_library/collector.py**
- Found 6 matches

#### http_call (9 files)

**intelligent-core/workflow_intelligence/temporal_workflows/risk_workflow.py**
- Found 9 matches

**intelligent-core/workflow_intelligence/temporal_workflows/bia_workflow.py**
- Found 9 matches

**intelligent-core/workflow_intelligence/integration/legacy_anthropic_client.py**
- Found 3 matches

**intelligent-core/workflow_intelligence/tests/api_tests/test_analysis.py**
- Found 46 matches

**intelligent-core/workflow_intelligence/tests/api_tests/test_health.py**
- Found 15 matches

**intelligent-core/workflow_intelligence/tests/api_tests/test_cases.py**
- Found 42 matches

**intelligent-core/workflow_intelligence/venv/lib/python3.11/site-packages/nexusrpc/handler/_decorators.py**
- Found 3 matches

**intelligent-core/workflow_intelligence/venv/lib/python3.11/site-packages/opentelemetry/metrics/_internal/__init__.py**
- Found 1 matches

**intelligent-core/workflow_intelligence/venv/lib/python3.11/site-packages/pip/_vendor/requests/__init__.py**
- Found 2 matches

#### service_registry (2 files)

**intelligent-core/workflow_intelligence/temporal_workflows/risk_workflow.py**
- Found 9 matches

**intelligent-core/workflow_intelligence/temporal_workflows/bia_workflow.py**
- Found 9 matches

#### temporal_workflow (20 files)

**intelligent-core/workflow_intelligence/temporal_workflows/risk_workflow.py**
- Found 11 matches

**intelligent-core/workflow_intelligence/temporal_workflows/bia_workflow.py**
- Found 13 matches

**intelligent-core/workflow_intelligence/temporal_workflows/devops_workflow.py**
- Found 22 matches

**intelligent-core/workflow_intelligence/workflows/temporal/bia_workflow.py**
- Found 23 matches

**intelligent-core/workflow_intelligence/temporal-sample/activities.py**
- Found 3 matches

**intelligent-core/workflow_intelligence/temporal-sample/workflows.py**
- Found 4 matches

**intelligent-core/workflow_intelligence/venv/lib/python3.11/site-packages/temporalio/client.py**
- Found 16 matches

**intelligent-core/workflow_intelligence/venv/lib/python3.11/site-packages/temporalio/activity.py**
- Found 1 matches

**intelligent-core/workflow_intelligence/venv/lib/python3.11/site-packages/temporalio/workflow.py**
- Found 3 matches

**intelligent-core/workflow_intelligence/venv/lib/python3.11/site-packages/temporalio/contrib/opentelemetry.py**
- Found 2 matches

### platform-services

#### analyzer_call (2 files)

**platform-services/simulation/digital-twin/api/routers/bia.py**
- Found 1 matches

**platform-services/bcm-coordination-service/main.py**
- Found 7 matches

#### coordination_intent (3 files)

**platform-services/мониторинг/compliance-monitoring/main.py**
- Found 1 matches

**platform-services/simulation/digital-twin/venv/lib/python3.9/site-packages/numpy/f2py/tests/test_parameter.py**
- Found 1 matches

**platform-services/simulation/digital-twin/venv/lib/python3.9/site-packages/numpy/f2py/tests/test_regression.py**
- Found 1 matches

#### database_query (167 files)

**platform-services/validation-service/tasks/kpi_collector.py**
- Found 2 matches

**platform-services/validation-service/tasks/kpi_alerting.py**
- Found 11 matches

**platform-services/governance-service/repositories/resource_repository.py**
- Found 10 matches

**platform-services/governance-service/repositories/objective_repository.py**
- Found 9 matches

**platform-services/governance-service/repositories/role_repository.py**
- Found 7 matches

**platform-services/governance-service/repositories/policy_repository.py**
- Found 9 matches

**platform-services/governance-service/repositories/competence_repository.py**
- Found 9 matches

**platform-services/plans_service/repositories/plan_repository.py**
- Found 20 matches

**platform-services/plans_service/api/health.py**
- Found 2 matches

**platform-services/мониторинг/process-analytics/main.py**
- Found 10 matches

#### eventbus_publish (35 files)

**platform-services/validation-service/events/publishers.py**
- Found 5 matches

**platform-services/compliance-service/workflows/evidence_workflow.py**
- Found 3 matches

**platform-services/compliance-service/workflows/audit_workflow.py**
- Found 3 matches

**platform-services/compliance-service/workflows/base_workflow.py**
- Found 3 matches

**platform-services/compliance-service/api/improvements.py**
- Found 4 matches

**platform-services/compliance-service/services/core/gap_analyzer.py**
- Found 3 matches

**platform-services/compliance-service/services/core/assessment_engine.py**
- Found 6 matches

**platform-services/governance-service/api/routes.py**
- Found 36 matches

**platform-services/governance-service/events/publishers.py**
- Found 18 matches

**platform-services/plans_service/services/plan_service.py**
- Found 5 matches

#### eventbus_subscribe (27 files)

**platform-services/governance-service/events/subscribers.py**
- Found 8 matches

**platform-services/мониторинг/compliance-monitoring/main.py**
- Found 2 matches

**platform-services/integration-tests/test_eventbus_integration.py**
- Found 1 matches

**platform-services/simulation/simulation/main.py**
- Found 2 matches

**platform-services/simulation/simulation/thehive/bridge_service.py**
- Found 1 matches

**platform-services/simulation/simulation/thehive/thehive/app.py**
- Found 6 matches

**platform-services/simulation/simulation/simulation2/app.py**
- Found 5 matches

**platform-services/simulation/simulation/api/execution_router.py**
- Found 3 matches

**platform-services/simulation/simulation/api/simulation_router.py**
- Found 2 matches

**platform-services/simulation/digital-twin/venv/lib/python3.9/site-packages/redis/client.py**
- Found 1 matches

#### http_call (91 files)

**platform-services/validation-service/main.py**
- Found 9 matches

**platform-services/validation-service/tasks/kpi_collector.py**
- Found 7 matches

**platform-services/validation-service/events/publishers.py**
- Found 3 matches

**platform-services/plans_service/main.py**
- Found 9 matches

**platform-services/plans_service/test_eventbus_integration.py**
- Found 22 matches

**platform-services/plans_service/api/health.py**
- Found 6 matches

**platform-services/plans_service/services/plan_service.py**
- Found 4 matches

**platform-services/мониторинг/compliance-monitoring/main.py**
- Found 3 matches

**platform-services/мониторинг/compliance-monitoring/integrations/automation_toolkit.py**
- Found 6 matches

**platform-services/мониторинг/compliance-monitoring/integrations/notifications.py**
- Found 15 matches

#### service_registry (1 files)

**platform-services/simulation/digital-twin/venv/lib/python3.9/site-packages/ciw/simulation.py**
- Found 2 matches

### shared

#### database_query (4 files)

**shared/database/connection.py**
- Found 1 matches

**shared/database/pagination.py**
- Found 5 matches

**shared/database/query_profiler.py**
- Found 2 matches

**shared/database/bulk_operations.py**
- Found 2 matches

#### eventbus_publish (6 files)

**shared/eventbus/domain_publishers.py**
- Found 78 matches

**shared/eventbus/client.py**
- Found 8 matches

**shared/eventbus/__init__.py**
- Found 1 matches

**shared/eventbus/publisher.py**
- Found 11 matches

**shared/auth/permissions.py**
- Found 2 matches

**shared/orchestration-patterns/base_orchestrator.py**
- Found 3 matches

#### eventbus_subscribe (6 files)

**shared/database/connection.py**
- Found 3 matches

**shared/eventbus/client.py**
- Found 6 matches

**shared/eventbus/subscriber.py**
- Found 2 matches

**shared/cache/redis_cache.py**
- Found 2 matches

**shared/auth/jwt.py**
- Found 1 matches

**shared/orchestration-patterns/base_orchestrator.py**
- Found 1 matches

#### http_call (5 files)

**shared/service_client/health.py**
- Found 3 matches

**shared/service_client/client.py**
- Found 7 matches

**shared/integrations/knowledge_client.py**
- Found 1 matches

**shared/integrations/rag_connector.py**
- Found 1 matches

**shared/integrations/ml_platform_client.py**
- Found 1 matches

#### service_registry (1 files)

**shared/service_client/registry.py**
- Found 1 matches

