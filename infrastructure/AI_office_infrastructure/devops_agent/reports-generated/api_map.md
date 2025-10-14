# Complete API Map

## Statistics

**Total APIs: 1554**

- **http_apis**: 1391
- **temporal_activities**: 106
- **temporal_workflows**: 34
- **eventbus_handlers**: 19
- **grpc_services**: 4

## HTTP APIs

| Method | Path | Module | File | Function |
|--------|------|--------|------|----------|
| GET | `/` | infrastructure | infrastructure/eventbus/examples/fastapi_integration.py:165 | `root()` |
| GET | `/` | infrastructure | infrastructure/integration/github-integration/main.py:13 | `root()` |
| GET | `/` | infrastructure | infrastructure/runtime/realtime-websocket/main.py:682 | `get_websocket_test_page()` |
| GET | `/` | infrastructure | infrastructure/observability/notification-service/main.py:556 | `root()` |
| GET | `/` | infrastructure | infrastructure/AI-office-infrastructure/db-intelligence/api.py:73 | `root()` |
| GET | `/` | infrastructure | infrastructure/AI-office-infrastructure/ai-event-manager/main.py:184 | `root()` |
| GET | `/` | infrastructure | infrastructure/AI-office-infrastructure/devops-agent/api/main.py:65 | `root()` |
| GET | `/` | infrastructure | infrastructure/AI-office-infrastructure/analytics-specialist/main.py:239 | `root()` |
| GET | `/` | infrastructure | infrastructure/AI-office-infrastructure/agent-router/metrics_server.py:48 | `root()` |
| POST | `/admin/execute` | infrastructure | infrastructure/AI-office-infrastructure/db-intelligence/api.py:354 | `execute_admin_command()` |
| GET | `/admin/locks` | infrastructure | infrastructure/AI-office-infrastructure/db-intelligence/api.py:507 | `get_database_locks()` |
| GET | `/admin/running-queries` | infrastructure | infrastructure/AI-office-infrastructure/db-intelligence/api.py:451 | `get_running_queries()` |
| POST | `/analyze` | infrastructure | infrastructure/AI-office-infrastructure/db-intelligence/api.py:203 | `analyze_query()` |
| POST | `/analyze/complexity` | infrastructure | infrastructure/AI-office-infrastructure/mio-manager/api/routes.py:89 | `analyze_complexity()` |
| POST | `/analyze/dependencies` | infrastructure | infrastructure/AI-office-infrastructure/mio-manager/api/routes.py:71 | `analyze_dependencies()` |
| POST | `/analyze/event` | infrastructure | infrastructure/AI-office-infrastructure/ai-event-manager/main.py:225 | `analyze_event()` |
| GET | `/api/health` | infrastructure | infrastructure/AI-office-infrastructure/project-agent/test-project/src/app.py:37 | `health_check()` |
| GET' | `/api/incidents` | infrastructure | infrastructure/AI-office-infrastructure/project-agent/test-project/src/app.py:14 | `incidents()` |
| POST | `/api/risk/assess` | infrastructure | infrastructure/AI-office-infrastructure/project-agent/test-project/src/app.py:25 | `assess_risk()` |
| POST | `/api/v1/build-and-deploy` | infrastructure | infrastructure/AI-office-infrastructure/orchestrator/unified_orchestrator.py:693 | `build_and_deploy()` |
| GET | `/api/v1/channels/{channel_id}/messages` | infrastructure | infrastructure/runtime/realtime-websocket/main.py:612 | `get_channel_messages()` |
| GET | `/api/v1/channels/{channel_id}/users` | infrastructure | infrastructure/runtime/realtime-websocket/main.py:602 | `get_channel_users()` |
| POST | `/api/v1/deploy` | infrastructure | infrastructure/AI-office-infrastructure/orchestrator/unified_orchestrator.py:683 | `deploy_infrastructure()` |
| POST | `/api/v1/discover` | infrastructure | infrastructure/AI-office-infrastructure/orchestrator/unified_orchestrator.py:662 | `discover_services()` |
| POST | `/api/v1/events/add-publisher` | infrastructure | infrastructure/AI-office-infrastructure/orchestrator/unified_orchestrator.py:759 | `add_publisher()` |
| POST | `/api/v1/events/add-subscriber` | infrastructure | infrastructure/AI-office-infrastructure/orchestrator/unified_orchestrator.py:783 | `add_subscriber()` |
| POST | `/api/v1/events/create-pr` | infrastructure | infrastructure/AI-office-infrastructure/orchestrator/unified_orchestrator.py:805 | `create_event_pr()` |
| POST | `/api/v1/events/fix-gap` | infrastructure | infrastructure/AI-office-infrastructure/orchestrator/unified_orchestrator.py:739 | `fix_event_gap()` |
| POST | `/api/v1/events/fix-gaps` | infrastructure | infrastructure/AI-office-infrastructure/orchestrator/unified_orchestrator.py:751 | `fix_multiple_gaps()` |
| POST | `/api/v1/events/rollback` | infrastructure | infrastructure/AI-office-infrastructure/orchestrator/unified_orchestrator.py:819 | `rollback_event_changes()` |
| POST | `/api/v1/gateway/ai/analyze` | infrastructure | infrastructure/gateway/api-gateway/main.py:290 | `ai_analyze_gateway()` |
| POST | `/api/v1/gateway/ai/optimize` | infrastructure | infrastructure/gateway/api-gateway/main.py:321 | `ai_optimize_gateway()` |
| GET | `/api/v1/gateway/services` | infrastructure | infrastructure/gateway/api-gateway/main.py:355 | `list_services()` |
| POST | `/api/v1/generate` | infrastructure | infrastructure/AI-office-infrastructure/orchestrator/unified_orchestrator.py:673 | `generate_configs()` |
| GET | `/api/v1/metrics/current` | infrastructure | infrastructure/AI-office-infrastructure/orchestrator/unified_orchestrator.py:835 | `get_current_metrics()` |
| POST | `/api/v1/monitoring/start` | infrastructure | infrastructure/AI-office-infrastructure/orchestrator/unified_orchestrator.py:969 | `start_monitoring()` |
| POST | `/api/v1/monitoring/stop` | infrastructure | infrastructure/AI-office-infrastructure/orchestrator/unified_orchestrator.py:983 | `stop_monitoring()` |
| POST | `/api/v1/notifications/broadcast` | infrastructure | infrastructure/runtime/realtime-websocket/main.py:551 | `broadcast_notification()` |
| POST | `/api/v1/queue/add` | infrastructure | infrastructure/AI-office-infrastructure/orchestrator/unified_orchestrator.py:875 | `add_task_with_priority()` |
| GET | `/api/v1/queue/next` | infrastructure | infrastructure/AI-office-infrastructure/orchestrator/unified_orchestrator.py:940 | `get_next_task_endpoint()` |
| GET | `/api/v1/queue/stats` | infrastructure | infrastructure/AI-office-infrastructure/orchestrator/unified_orchestrator.py:862 | `get_queue_stats()` |
| GET | `/api/v1/stats` | infrastructure | infrastructure/runtime/realtime-websocket/main.py:656 | `get_realtime_stats()` |
| GET | `/api/v1/status` | infrastructure | infrastructure/AI-office-infrastructure/orchestrator/unified_orchestrator.py:656 | `get_status()` |
| POST | `/api/v1/tasks/execute` | infrastructure | infrastructure/AI-office-infrastructure/orchestrator/unified_orchestrator.py:724 | `execute_task()` |
| POST | `/auth/login` | infrastructure | infrastructure/security/auth/main.py:110 | `login()` |
| POST | `/auth/logout` | infrastructure | infrastructure/security/auth/main.py:202 | `logout()` |
| GET | `/auth/me` | infrastructure | infrastructure/security/auth/main.py:197 | `get_me()` |
| POST | `/auth/odoo` | infrastructure | infrastructure/gateway/_deprecated_unified_database_gateway/main.py:590 | `authenticate_odoo()` |
| GET | `/auth/odoo/session/{session_id}` | infrastructure | infrastructure/gateway/_deprecated_unified_database_gateway/main.py:642 | `get_odoo_session()` |
| DELETE | `/auth/odoo/session/{session_id}` | infrastructure | infrastructure/gateway/_deprecated_unified_database_gateway/main.py:651 | `logout_odoo_session()` |
| POST | `/auth/signup` | infrastructure | infrastructure/security/auth/main.py:153 | `signup()` |
| POST | `/auth/token-exchange` | infrastructure | infrastructure/integration/github-integration/main.py:30 | `token_exchange()` |
| POST | `/claude/analyze-changes` | infrastructure | infrastructure/integration/github-integration/main.py:41 | `proxy_analyze_changes()` |
| POST | `/claude/analyze-deployment` | infrastructure | infrastructure/integration/github-integration/main.py:75 | `proxy_analyze_deployment()` |
| POST | `/claude/generate-config` | infrastructure | infrastructure/integration/github-integration/main.py:53 | `proxy_generate_config()` |
| GET | `/config` | infrastructure | infrastructure/AI-office-infrastructure/db-intelligence/api.py:249 | `get_configuration()` |
| PUT | `/config` | infrastructure | infrastructure/AI-office-infrastructure/db-intelligence/api.py:267 | `update_configuration()` |
| GET | `/dashboard/summary` | infrastructure | infrastructure/AI-office-infrastructure/ai-event-manager/main.py:423 | `get_dashboard_summary()` |
| GET | `/data` | infrastructure | infrastructure/database/__init__.py:16 | `get_data()` |
| GET | `/deployment/history` | infrastructure | infrastructure/integration/github-integration/main.py:65 | `proxy_deployment_history()` |
| POST | `/deployment/orchestrate` | infrastructure | infrastructure/integration/github-integration/main.py:87 | `proxy_orchestrate()` |
| POST | `/discover` | infrastructure | infrastructure/AI-office-infrastructure/mio-manager/api/routes.py:55 | `discover_services()` |
| POST | `/email/send` | infrastructure | infrastructure/observability/notification-service/main.py:312 | `send_email()` |
| POST | `/events/analyze` | infrastructure | infrastructure/AI-office-infrastructure/mio-manager/api/routes.py:288 | `analyze_event()` |
| GET | `/events/architecture/insights` | infrastructure | infrastructure/AI-office-infrastructure/mio-manager/api/routes.py:336 | `get_architecture_insights()` |
| POST | `/events/feedback` | infrastructure | infrastructure/AI-office-infrastructure/mio-manager/api/routes.py:375 | `record_event_feedback()` |
| GET | `/events/learning/stats` | infrastructure | infrastructure/AI-office-infrastructure/mio-manager/api/routes.py:357 | `get_event_learning_stats()` |
| GET | `/events/recommendations` | infrastructure | infrastructure/AI-office-infrastructure/mio-manager/api/routes.py:315 | `get_event_recommendations()` |
| POST | `/feedback` | infrastructure | infrastructure/AI-office-infrastructure/ai-event-manager/main.py:323 | `record_feedback()` |
| POST | `/files/` | infrastructure | infrastructure/AI-office-infrastructure/ai-event-manager/venv/lib/python3.9/site-packages/fastapi/datastructures.py:53 | `create_file()` |
| GET | `/gateway/health/{service_name}` | infrastructure | infrastructure/AI-office-infrastructure/mio-manager/api/routes.py:254 | `get_service_health()` |
| POST | `/gateway/register` | infrastructure | infrastructure/AI-office-infrastructure/mio-manager/api/routes.py:239 | `register_service_in_gateway()` |
| POST | `/github/webhook` | infrastructure | infrastructure/integration/github-integration/main.py:22 | `github_webhook()` |
| GET | `/health` | infrastructure | infrastructure/security/auth/auth_service.py:492 | `health_check()` |
| GET | `/health` | infrastructure | infrastructure/security/auth/main.py:100 | `health()` |
| GET | `/health` | infrastructure | infrastructure/runtime/realtime-websocket/main.py:452 | `health_check()` |
| GET | `/health` | infrastructure | infrastructure/observability/notification-service/main.py:293 | `health_check()` |
| GET | `/health` | infrastructure | infrastructure/AI-office-infrastructure/db-intelligence/api.py:91 | `health_check()` |
| GET | `/health` | infrastructure | infrastructure/AI-office-infrastructure/ai-event-manager/main.py:209 | `health()` |
| GET | `/health` | infrastructure | infrastructure/AI-office-infrastructure/devops-agent/api/main.py:76 | `health()` |
| GET | `/health` | infrastructure | infrastructure/AI-office-infrastructure/agent-router/metrics_server.py:38 | `health()` |
| GET | `/health` | infrastructure | infrastructure/AI-office-infrastructure/mio-manager/main.py:290 | `health_check()` |
| GET | `/health` | infrastructure | infrastructure/AI-office-infrastructure/orchestrator/unified_orchestrator.py:646 | `health()` |
| GET | `/health` | infrastructure | infrastructure/gateway/api-gateway/main.py:247 | `health_check()` |
| GET | `/health` | infrastructure | infrastructure/gateway/_deprecated_unified_database_gateway/main.py:176 | `health_check()` |
| GET | `/health/databases` | infrastructure | infrastructure/gateway/_deprecated_unified_database_gateway/main.py:186 | `check_all_databases()` |
| POST | `/integrations/analyze/full` | infrastructure | infrastructure/AI-office-infrastructure/ai-event-manager/main.py:494 | `run_full_analysis()` |
| POST | `/integrations/eventbus/publish` | infrastructure | infrastructure/AI-office-infrastructure/ai-event-manager/main.py:511 | `publish_to_eventbus()` |
| POST | `/integrations/github/issue` | infrastructure | infrastructure/AI-office-infrastructure/ai-event-manager/main.py:528 | `create_github_issue_endpoint()` |
| POST | `/integrations/scan/trigger` | infrastructure | infrastructure/AI-office-infrastructure/ai-event-manager/main.py:477 | `trigger_immediate_scan()` |
| GET | `/integrations/status` | infrastructure | infrastructure/AI-office-infrastructure/ai-event-manager/main.py:468 | `integration_status()` |
| GET | `/items/` | infrastructure | infrastructure/AI-office-infrastructure/ai-event-manager/venv/lib/python3.9/site-packages/fastapi/applications.py:239 | `unknown()` |
| POST | `/items/` | infrastructure | infrastructure/AI-office-infrastructure/ai-event-manager/venv/lib/python3.9/site-packages/fastapi/applications.py:2610 | `create_item()` |
| PATCH | `/items/` | infrastructure | infrastructure/AI-office-infrastructure/ai-event-manager/venv/lib/python3.9/site-packages/fastapi/applications.py:4107 | `update_item()` |
| GET | `/items/` | infrastructure | infrastructure/AI-office-infrastructure/ai-event-manager/venv/lib/python3.9/site-packages/fastapi/routing.py:1632 | `read_items()` |
| POST | `/items/` | infrastructure | infrastructure/AI-office-infrastructure/ai-event-manager/venv/lib/python3.9/site-packages/fastapi/routing.py:2396 | `create_item()` |
| PATCH | `/items/` | infrastructure | infrastructure/AI-office-infrastructure/ai-event-manager/venv/lib/python3.9/site-packages/fastapi/routing.py:3914 | `update_item()` |
| GET | `/items/` | infrastructure | infrastructure/AI-office-infrastructure/ai-event-manager/venv/lib/python3.9/site-packages/fastapi/param_functions.py:2272 | `read_items()` |
| GET | `/items/` | infrastructure | infrastructure/AI-office-infrastructure/ai-event-manager/venv/lib/python3.9/site-packages/fastapi/security/api_key.py:41 | `read_items()` |
| PUT | `/items/{item_id}` | infrastructure | infrastructure/AI-office-infrastructure/ai-event-manager/venv/lib/python3.9/site-packages/fastapi/applications.py:2232 | `replace_item()` |
| DELETE | `/items/{item_id}` | infrastructure | infrastructure/AI-office-infrastructure/ai-event-manager/venv/lib/python3.9/site-packages/fastapi/applications.py:2983 | `delete_item()` |
| PUT | `/items/{item_id}` | infrastructure | infrastructure/AI-office-infrastructure/ai-event-manager/venv/lib/python3.9/site-packages/fastapi/routing.py:2014 | `replace_item()` |
| DELETE | `/items/{item_id}` | infrastructure | infrastructure/AI-office-infrastructure/ai-event-manager/venv/lib/python3.9/site-packages/fastapi/routing.py:2773 | `delete_item()` |
| GET | `/items/{item_id}` | infrastructure | infrastructure/AI-office-infrastructure/ai-event-manager/venv/lib/python3.9/site-packages/fastapi/exceptions.py:29 | `read_item()` |
| GET | `/items/{item_id}` | infrastructure | infrastructure/AI-office-infrastructure/ai-event-manager/venv/lib/python3.9/site-packages/fastapi/param_functions.py:299 | `read_items()` |
| GET | `/learning/report` | infrastructure | infrastructure/AI-office-infrastructure/ai-event-manager/main.py:406 | `get_learning_report()` |
| GET | `/learning/stats` | infrastructure | infrastructure/AI-office-infrastructure/ai-event-manager/main.py:388 | `get_learning_stats()` |
| POST | `/login` | infrastructure | infrastructure/security/auth/auth_service.py:369 | `login()` |
| POST | `/login` | infrastructure | infrastructure/AI-office-infrastructure/ai-event-manager/venv/lib/python3.9/site-packages/fastapi/security/oauth2.py:41 | `login()` |
| POST | `/logout` | infrastructure | infrastructure/security/auth/auth_service.py:476 | `logout()` |
| GET | `/me` | infrastructure | infrastructure/security/auth/auth_service.py:486 | `get_current_user_info()` |
| GET | `/metrics` | infrastructure | infrastructure/tools/analyzers/metrics_discovery.py:210 | `_extract_port()` |
| GET | `/metrics` | infrastructure | infrastructure/observability/add_metrics_to_services.py:72 | `metrics()` |
| GET | `/metrics` | infrastructure | infrastructure/observability/notification-service/main.py:551 | `metrics()` |
| GET | `/metrics` | infrastructure | infrastructure/AI-office-infrastructure/db-intelligence/api.py:111 | `get_metrics()` |
| GET | `/metrics` | infrastructure | infrastructure/AI-office-infrastructure/analytics-specialist/main.py:276 | `metrics()` |
| GET | `/metrics` | infrastructure | infrastructure/gateway/_deprecated_unified_database_gateway/main.py:660 | `get_metrics()` |
| GET | `/metrics/prometheus` | infrastructure | infrastructure/AI-office-infrastructure/db-intelligence/api.py:300 | `prometheus_metrics()` |
| GET | `/metrics\` | infrastructure | infrastructure/observability/add_metrics_to_services.py:105 | `analyze_imports()` |
| GET | `/monitor/stats` | infrastructure | infrastructure/AI-office-infrastructure/ai-event-manager/main.py:550 | `get_monitor_stats()` |
| POST | `/monitoring/grafana/dashboard` | infrastructure | infrastructure/AI-office-infrastructure/mio-manager/api/routes.py:179 | `generate_grafana_dashboard()` |
| POST | `/monitoring/prometheus/config` | infrastructure | infrastructure/AI-office-infrastructure/mio-manager/api/routes.py:157 | `generate_prometheus_config()` |
| POST | `/monitoring/setup` | infrastructure | infrastructure/AI-office-infrastructure/mio-manager/api/routes.py:136 | `setup_monitoring()` |
| GET | `/notifications/history` | infrastructure | infrastructure/observability/notification-service/main.py:479 | `get_notification_history()` |
| GET | `/notifications/stats` | infrastructure | infrastructure/observability/notification-service/main.py:531 | `get_notification_stats()` |
| POST | `/path` | infrastructure | infrastructure/tools/analyzers/api_mapper.py:98 | `unknown()` |
| GET | `/predictions/future` | infrastructure | infrastructure/AI-office-infrastructure/ai-event-manager/main.py:347 | `predict_future()` |
| POST | `/push/send` | infrastructure | infrastructure/observability/notification-service/main.py:425 | `send_push()` |
| POST | `/query` | infrastructure | infrastructure/gateway/_deprecated_unified_database_gateway/main.py:327 | `execute_query()` |
| GET | `/query-metrics` | infrastructure | infrastructure/AI-office-infrastructure/db-intelligence/api.py:131 | `get_query_metrics()` |
| GET | `/recommendations` | infrastructure | infrastructure/AI-office-infrastructure/ai-event-manager/main.py:255 | `get_recommendations()` |
| GET | `/reports/history` | infrastructure | infrastructure/AI-office-infrastructure/devops-agent/api/main.py:121 | `get_report_history()` |
| GET | `/reports/latest` | infrastructure | infrastructure/AI-office-infrastructure/devops-agent/api/main.py:107 | `get_latest_report()` |
| POST | `/scan` | infrastructure | infrastructure/AI-office-infrastructure/devops-agent/api/main.py:90 | `trigger_scan()` |
| POST | `/security/scan` | infrastructure | infrastructure/AI-office-infrastructure/mio-manager/api/routes.py:106 | `security_scan()` |
| POST | `/send-notification/{email}` | infrastructure | infrastructure/AI-office-infrastructure/ai-event-manager/venv/lib/python3.9/site-packages/fastapi/background.py:31 | `send_notification()` |
| POST | `/signup` | infrastructure | infrastructure/security/auth/auth_service.py:249 | `signup()` |
| GET | `/slow-queries` | infrastructure | infrastructure/AI-office-infrastructure/db-intelligence/api.py:153 | `get_slow_queries()` |
| POST | `/sms/send` | infrastructure | infrastructure/observability/notification-service/main.py:398 | `send_sms()` |
| GET | `/stats` | infrastructure | infrastructure/eventbus/examples/fastapi_integration.py:268 | `get_stats()` |
| GET | `/status` | infrastructure | infrastructure/AI-office-infrastructure/devops-agent/api/main.py:135 | `get_status()` |
| GET | `/status` | infrastructure | infrastructure/AI-office-infrastructure/mio-manager/api/routes.py:269 | `get_mio_status()` |
| GET | `/suggestions` | infrastructure | infrastructure/AI-office-infrastructure/db-intelligence/api.py:178 | `get_optimization_suggestions()` |
| GET | `/tables` | infrastructure | infrastructure/AI-office-infrastructure/db-intelligence/api.py:225 | `get_table_statistics()` |
| POST | `/tasks/delegate` | infrastructure | infrastructure/AI-office-infrastructure/mio-manager/api/routes.py:201 | `delegate_task()` |
| GET | `/tasks/{task_id}` | infrastructure | infrastructure/AI-office-infrastructure/mio-manager/api/routes.py:224 | `get_task_status()` |
| POST | `/tests/generate` | infrastructure | infrastructure/AI-office-infrastructure/mio-manager/api/routes.py:121 | `generate_tests()` |
| POST | `/uploadfile/` | infrastructure | infrastructure/AI-office-infrastructure/ai-event-manager/venv/lib/python3.9/site-packages/fastapi/datastructures.py:58 | `create_upload_file()` |
| GET | `/users/` | infrastructure | infrastructure/AI-office-infrastructure/ai-event-manager/venv/lib/python3.9/site-packages/fastapi/applications.py:238 | `unknown()` |
| GET | `/users/` | infrastructure | infrastructure/AI-office-infrastructure/ai-event-manager/venv/lib/python3.9/site-packages/fastapi/routing.py:540 | `read_users()` |
| GET | `/users/me` | infrastructure | infrastructure/AI-office-infrastructure/ai-event-manager/venv/lib/python3.9/site-packages/fastapi/security/http.py:124 | `read_current_user()` |
| GET | `/users/me/items/` | infrastructure | infrastructure/AI-office-infrastructure/ai-event-manager/venv/lib/python3.9/site-packages/fastapi/param_functions.py:2353 | `read_own_items()` |
| POST | `/webhook/send` | infrastructure | infrastructure/observability/notification-service/main.py:453 | `send_webhook()` |
| POST | `/workflows` | infrastructure | infrastructure/eventbus/examples/fastapi_integration.py:86 | `create_workflow()` |
| POST | `/workflows/{workflow_id}/complete` | infrastructure | infrastructure/eventbus/examples/fastapi_integration.py:223 | `complete_workflow()` |
| POST | `[^)]*?` | infrastructure | infrastructure/tools/analyzers/api_mapper.py:106 | `unknown()` |
| POST | `[^)]*?` | infrastructure | infrastructure/tools/analyzers/module_scanner.py:216 | `unknown()` |
| POST | `, response_model=ContributionResponse, status_code=status.HTTP_201_CREATED)
async def create_contribution(
    request: ContributionCreate,
    current_user: dict = Depends(get_current_user),
    service: ContributionService = Depends(get_contribution_service)
):
    ` | intelligent-core | intelligent-core/community_intelligence/api/contributions.py:109 | `unknown()` |
| POST | `, response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def submit_review(
    request: ReviewSubmit,
    current_user: dict = Depends(get_current_user),
    service: PeerReviewService = Depends(get_peer_review_service),
    db: AsyncSession = Depends(get_db)
):
    ` | intelligent-core | intelligent-core/community_intelligence/api/reviews.py:91 | `unknown()` |
| GET | `/` | intelligent-core | intelligent-core/main.py:86 | `root()` |
| GET | `/` | intelligent-core | intelligent-core/workflow-engine/main.py:75 | `root()` |
| GET | `/` | intelligent-core | intelligent-core/predictive/main.py:196 | `root()` |
| GET | `/` | intelligent-core | intelligent-core/expertise-center/service/standalone_main.py:199 | `root()` |
| GET | `/` | intelligent-core | intelligent-core/expertise-center/service/main.py:123 | `root()` |
| GET | `/` | intelligent-core | intelligent-core/collective/main.py:241 | `root()` |
| GET | `/` | intelligent-core | intelligent-core/workflow_intelligence/main.py:310 | `root()` |
| GET | `/` | intelligent-core | intelligent-core/event_intelligence/main.py:129 | `root()` |
| GET | `/` | intelligent-core | intelligent-core/ai-foundation/main.py:75 | `root()` |
| GET | `/` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/main.py:249 | `root()` |
| GET | `/` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/learning/recommendation_router.py:45 | `get_recommendations()` |
| GET | `/` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/learning/pattern_router.py:176 | `list_patterns()` |
| GET | `/` | intelligent-core | intelligent-core/community_intelligence/main.py:146 | `root()` |
| GET | `/` | intelligent-core | intelligent-core/orchestration/coordination-center/main.py:119 | `root()` |
| GET | `/...` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/shared/database.py:59 | `endpoint()` |
| POST | `/accept-help` | intelligent-core | intelligent-core/collective/api/stuck_detection.py:123 | `accept_collective_help()` |
| POST | `/achievements/check` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/learning/gamification_router.py:276 | `check_achievements()` |
| GET | `/active` | intelligent-core | intelligent-core/collective/api/collective_agents.py:266 | `get_active_agents()` |
| POST | `/admin/clear-cache` | intelligent-core | intelligent-core/orchestration/ai-orchestration/tentacles/knowledge_orchestrator.py:403 | `clear_all_caches()` |
| GET | `/admin/stats` | intelligent-core | intelligent-core/orchestration/ai-orchestration/tentacles/knowledge_orchestrator.py:417 | `get_admin_stats()` |
| POST | `/admin/sync-benchmarks` | intelligent-core | intelligent-core/orchestration/ai-orchestration/tentacles/knowledge_orchestrator.py:387 | `trigger_benchmark_sync()` |
| GET | `/agents` | intelligent-core | intelligent-core/orchestration/ai-orchestration/api/monitoring_routes.py:217 | `get_agent_performance()` |
| GET | `/agents/utilization` | intelligent-core | intelligent-core/orchestration/ai-orchestration/api/monitoring_routes.py:266 | `get_agent_utilization()` |
| GET | `/alerts/active` | intelligent-core | intelligent-core/orchestration/ai-orchestration/api/monitoring_routes.py:540 | `get_active_alerts()` |
| GET | `/alerts/history` | intelligent-core | intelligent-core/orchestration/ai-orchestration/api/monitoring_routes.py:574 | `get_alert_history()` |
| GET | `/analytics/benchmarks` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/learning/analytics_router.py:301 | `get_benchmarks()` |
| GET | `/analytics/comparative` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/learning/analytics_router.py:259 | `get_comparative_analytics()` |
| GET | `/analytics/cross-service-learning` | intelligent-core | intelligent-core/orchestration/ai-orchestration/tentacles/knowledge_orchestrator.py:256 | `get_cross_service_learning_stats()` |
| POST | `/analytics/drill-down` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/learning/analytics_router.py:185 | `drill_down_analytics()` |
| GET | `/analytics/export` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/learning/analytics_router.py:343 | `export_analytics()` |
| GET | `/analytics/performance-matrix` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/learning/analytics_router.py:221 | `get_performance_matrix()` |
| GET | `/analytics/platform` | intelligent-core | intelligent-core/orchestration/ai-orchestration/tentacles/knowledge_orchestrator.py:218 | `get_platform_analytics()` |
| GET | `/analytics/predictions` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/learning/analytics_router.py:409 | `get_predictive_analytics()` |
| GET | `/analytics/real-time` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/learning/analytics_router.py:374 | `get_real_time_metrics()` |
| POST | `/analyze` | intelligent-core | intelligent-core/workflow_intelligence/main.py:249 | `analyze_workflow()` |
| POST | `/analyze` | intelligent-core | intelligent-core/event_intelligence/api.py:109 | `analyze_event()` |
| POST | `/analyze` | intelligent-core | intelligent-core/event_intelligence/api/routes.py:218 | `analyze_event()` |
| POST | `/analyze/bulk` | intelligent-core | intelligent-core/event_intelligence/api/routes.py:316 | `analyze_bulk_events()` |
| POST | `/analyze/domain` | intelligent-core | intelligent-core/event_intelligence/api.py:156 | `analyze_domain()` |
| POST | `/analyze/domain` | intelligent-core | intelligent-core/event_intelligence/api/routes.py:274 | `analyze_domain()` |
| POST | `/analyze/impact` | intelligent-core | intelligent-core/METRICS_INTEGRATION_EXAMPLE.py:82 | `analyze_impact()` |
| POST | `/annotations` | intelligent-core | intelligent-core/community_intelligence/api/routes.py:324 | `add_annotation()` |
| POST | `/annotations/{annotation_id}/vote` | intelligent-core | intelligent-core/community_intelligence/api/routes.py:391 | `vote_annotation()` |
| GET | `/api/actions` | intelligent-core | intelligent-core/orchestration/pdca_assistant.py:534 | `get_actions()` |
| POST | `/api/actions/{action_id}/execute` | intelligent-core | intelligent-core/orchestration/pdca_assistant.py:540 | `execute_action()` |
| GET | `/api/compliance/check` | intelligent-core | intelligent-core/workflow_intelligence/examples/service_integration_template.py:290 | `compliance_check()` |
| GET | `/api/cross-learning/virtuous-cycle/metrics` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/main.py:723 | `get_virtuous_cycle_metrics()` |
| POST | `/api/cross-learning/virtuous-cycle/pattern` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/main.py:689 | `process_pattern_for_cycle()` |
| POST | `/api/cross-learning/virtuous-cycle/workflow` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/main.py:654 | `process_workflow_for_cycle()` |
| POST | `/api/message` | intelligent-core | intelligent-core/orchestration/pdca_assistant.py:524 | `process_message()` |
| POST | `/api/phase/update` | intelligent-core | intelligent-core/orchestration/pdca_assistant.py:546 | `update_phase()` |
| GET | `/api/reactive-learning/statistics` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/main.py:806 | `get_reactive_learning_statistics()` |
| GET | `/api/reactive-learning/subscribers` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/main.py:837 | `list_active_subscribers()` |
| GET | `/api/search` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/main.py:760 | `unified_search()` |
| POST | `/api/v1/ai/agent/process` | intelligent-core | intelligent-core/orchestration/ai-orchestration/main.py:573 | `process_with_ai_agent()` |
| GET | `/api/v1/ai/agents/analytics` | intelligent-core | intelligent-core/orchestration/ai-orchestration/main.py:622 | `get_ai_agent_analytics()` |
| GET | `/api/v1/ai/agents/health` | intelligent-core | intelligent-core/orchestration/ai-orchestration/main.py:607 | `check_ai_agents_health()` |
| POST | `/api/v1/ai/analyze/incident` | intelligent-core | intelligent-core/orchestration/ai-orchestration/main.py:495 | `classify_incident_ai()` |
| POST | `/api/v1/ai/analyze/process-risk` | intelligent-core | intelligent-core/orchestration/ai-orchestration/main.py:482 | `analyze_process_risk()` |
| GET | `/api/v1/ai/analyze/{process_id}` | intelligent-core | intelligent-core/ai_workflow_optimizer/main.py:1000 | `ai_analyze_workflow()` |
| GET | `/api/v1/ai/decisions` | intelligent-core | intelligent-core/orchestration/ai-orchestration/main.py:303 | `list_decisions()` |
| POST | `/api/v1/ai/decisions/{decision_id}/approve` | intelligent-core | intelligent-core/orchestration/ai-orchestration/main.py:324 | `approve_decision()` |
| POST | `/api/v1/ai/decisions/{decision_id}/reject` | intelligent-core | intelligent-core/orchestration/ai-orchestration/main.py:336 | `reject_decision()` |
| POST | `/api/v1/ai/learn` | intelligent-core | intelligent-core/ai_workflow_optimizer/main.py:1104 | `learn_from_execution()` |
| POST | `/api/v1/ai/nlp/query` | intelligent-core | intelligent-core/orchestration/ai-orchestration/main.py:508 | `process_nlp_query()` |
| POST | `/api/v1/ai/recommendations` | intelligent-core | intelligent-core/ai_workflow_optimizer/main.py:1056 | `get_ai_recommendations()` |
| GET | `/api/v1/ai/rules` | intelligent-core | intelligent-core/orchestration/ai-orchestration/main.py:260 | `list_ai_rules()` |
| POST | `/api/v1/ai/rules/{rule_name}/disable` | intelligent-core | intelligent-core/orchestration/ai-orchestration/main.py:290 | `disable_rule()` |
| POST | `/api/v1/ai/rules/{rule_name}/enable` | intelligent-core | intelligent-core/orchestration/ai-orchestration/main.py:277 | `enable_rule()` |
| GET | `/api/v1/ai/status` | intelligent-core | intelligent-core/orchestration/ai-orchestration/main.py:254 | `get_ai_status()` |
| GET | `/api/v1/analyze/bottlenecks/{process_id}` | intelligent-core | intelligent-core/ai_workflow_optimizer/main.py:885 | `analyze_bottlenecks()` |
| POST | `/api/v1/auth/refresh-token` | intelligent-core | intelligent-core/orchestration/ai-orchestration/main.py:655 | `refresh_user_token()` |
| POST | `/api/v1/auth/token-exchange` | intelligent-core | intelligent-core/orchestration/ai-orchestration/main.py:639 | `exchange_github_token()` |
| POST | `/api/v1/bcm/audit/start` | intelligent-core | intelligent-core/orchestration/ai-orchestration/main.py:466 | `start_audit()` |
| POST | `/api/v1/bcm/bia/start` | intelligent-core | intelligent-core/orchestration/ai-orchestration/main.py:442 | `start_bia()` |
| POST | `/api/v1/bcm/incident/report` | intelligent-core | intelligent-core/orchestration/ai-orchestration/main.py:454 | `report_incident()` |
| POST | `/api/v1/chat` | intelligent-core | intelligent-core/main.py:383 | `ai_chat()` |
| POST | `/api/v1/claude/analyze-changes` | intelligent-core | intelligent-core/orchestration/ai-orchestration/main.py:523 | `claude_analyze_changes()` |
| POST | `/api/v1/claude/create-pr` | intelligent-core | intelligent-core/orchestration/ai-orchestration/main.py:554 | `claude_create_pr()` |
| POST | `/api/v1/claude/generate-config` | intelligent-core | intelligent-core/orchestration/ai-orchestration/main.py:540 | `claude_generate_config()` |
| POST | `/api/v1/decisions/make` | intelligent-core | intelligent-core/main.py:146 | `make_decision()` |
| GET | `/api/v1/deployment/history` | intelligent-core | intelligent-core/orchestration/ai-orchestration/main.py:692 | `get_deployment_history()` |
| POST | `/api/v1/deployment/orchestrate` | intelligent-core | intelligent-core/orchestration/ai-orchestration/main.py:675 | `orchestrate_deployment()` |
| GET | `/api/v1/detect/anomalies/{process_id}` | intelligent-core | intelligent-core/ai_workflow_optimizer/main.py:941 | `detect_process_anomalies()` |
| GET | `/api/v1/digital-twin/model/{org_id}` | intelligent-core | intelligent-core/main.py:207 | `get_organization_model()` |
| POST | `/api/v1/digital-twin/simulate` | intelligent-core | intelligent-core/main.py:175 | `simulate_disruption()` |
| POST | `/api/v1/events/publish` | intelligent-core | intelligent-core/orchestration/ai-orchestration/main.py:416 | `publish_event()` |
| GET | `/api/v1/knowledge/bcm/{topic}` | intelligent-core | intelligent-core/main.py:234 | `get_bcm_knowledge()` |
| GET | `/api/v1/knowledge/history/{org_id}/incidents` | intelligent-core | intelligent-core/main.py:259 | `get_incident_history()` |
| POST | `/api/v1/models/retrain` | intelligent-core | intelligent-core/ai_workflow_optimizer/main.py:965 | `retrain_models()` |
| GET | `/api/v1/models/status` | intelligent-core | intelligent-core/ai_workflow_optimizer/main.py:976 | `get_model_status()` |
| POST | `/api/v1/optimization/recommend-strategy` | intelligent-core | intelligent-core/main.py:283 | `recommend_strategy()` |
| POST | `/api/v1/optimize/performance` | intelligent-core | intelligent-core/ai_workflow_optimizer/main.py:836 | `optimize_process_performance()` |
| GET | `/api/v1/optimize/resources/{process_id}` | intelligent-core | intelligent-core/ai_workflow_optimizer/main.py:913 | `optimize_process_resources()` |
| GET | `/api/v1/patterns/incidents/{org_id}` | intelligent-core | intelligent-core/main.py:411 | `find_incident_patterns()` |
| GET | `/api/v1/platform/health` | intelligent-core | intelligent-core/ai_workflow_optimizer/main.py:1151 | `platform_health()` |
| GET | `/api/v1/platform/services` | intelligent-core | intelligent-core/orchestration/ai-orchestration/main.py:242 | `list_services()` |
| POST | `/api/v1/platform/services/{service}/restart` | intelligent-core | intelligent-core/orchestration/ai-orchestration/main.py:218 | `restart_service()` |
| POST | `/api/v1/platform/services/{service}/start` | intelligent-core | intelligent-core/orchestration/ai-orchestration/main.py:194 | `start_service()` |
| GET | `/api/v1/platform/services/{service}/status` | intelligent-core | intelligent-core/orchestration/ai-orchestration/main.py:230 | `get_service_status()` |
| POST | `/api/v1/platform/services/{service}/stop` | intelligent-core | intelligent-core/orchestration/ai-orchestration/main.py:206 | `stop_service()` |
| GET | `/api/v1/platform/status` | intelligent-core | intelligent-core/orchestration/ai-orchestration/main.py:188 | `get_platform_status()` |
| POST | `/api/v1/predictions/financial-impact` | intelligent-core | intelligent-core/main.py:318 | `predict_financial_impact()` |
| GET | `/api/v1/predictions/rto-achievement` | intelligent-core | intelligent-core/main.py:347 | `predict_rto_achievement()` |
| POST | `/api/v1/scenario/generate` | intelligent-core | intelligent-core/orchestration/ai-orchestration/main.py:358 | `generate_scenario()` |
| GET | `/api/v1/scenario/learning/stats` | intelligent-core | intelligent-core/orchestration/ai-orchestration/main.py:404 | `get_learning_stats()` |
| GET | `/api/v1/scenario/status` | intelligent-core | intelligent-core/orchestration/ai-orchestration/main.py:352 | `get_scenario_status()` |
| GET | `/api/v1/scenario/{scenario_id}` | intelligent-core | intelligent-core/orchestration/ai-orchestration/main.py:380 | `get_scenario()` |
| GET | `/api/v1/scenario/{scenario_id}/learning` | intelligent-core | intelligent-core/orchestration/ai-orchestration/main.py:392 | `get_scenario_learning()` |
| POST | `/api/v1/system/orchestrator/{orchestrator}/restart` | intelligent-core | intelligent-core/orchestration/ai-orchestration/main.py:175 | `restart_orchestrator()` |
| POST | `/api/v1/system/restart` | intelligent-core | intelligent-core/orchestration/ai-orchestration/main.py:166 | `restart_system()` |
| GET | `/api/v1/system/status` | intelligent-core | intelligent-core/orchestration/ai-orchestration/main.py:160 | `get_system_status()` |
| POST | `/api/v1/workflows/start` | intelligent-core | intelligent-core/orchestration/ai-orchestration/main.py:430 | `start_workflow()` |
| GET | `/audit` | intelligent-core | intelligent-core/orchestration/coordination-center/api/routes.py:477 | `get_audit_logs()` |
| POST | `/badges/check` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/learning/gamification_router.py:103 | `check_badges_earned()` |
| GET | `/badges/definitions` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/learning/gamification_router.py:133 | `get_badge_definitions()` |
| GET | `/benchmarks/all` | intelligent-core | intelligent-core/orchestration/ai-orchestration/tentacles/knowledge_orchestrator.py:86 | `get_all_benchmarks()` |
| POST | `/bia/analyze` | intelligent-core | intelligent-core/expertise-center/service/api/tactical.py:159 | `analyze_business_impact()` |
| GET | `/cases` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/main.py:459 | `list_cases()` |
| POST | `/cases/add` | intelligent-core | intelligent-core/workflow_intelligence/main.py:169 | `add_case()` |
| POST | `/cases/bulk` | intelligent-core | intelligent-core/workflow_intelligence/main.py:236 | `bulk_operations()` |
| POST | `/cases/search` | intelligent-core | intelligent-core/workflow_intelligence/main.py:225 | `search_cases()` |
| POST | `/cases/search` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/main.py:534 | `search_cases()` |
| GET | `/cases/search` | intelligent-core | intelligent-core/orchestration/ai-orchestration/tentacles/knowledge_orchestrator.py:151 | `search_cases_across_services()` |
| GET | `/cases/{case_id}` | intelligent-core | intelligent-core/workflow_intelligence/main.py:209 | `get_case()` |
| GET | `/cases/{case_id}` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/main.py:499 | `get_case()` |
| GET | `/certification/{org_id}` | intelligent-core | intelligent-core/predictive/api/predictions.py:175 | `get_certification_prediction()` |
| GET | `/check` | intelligent-core | intelligent-core/collective/api/stuck_detection.py:70 | `check_if_stuck()` |
| GET | `/clauses/search` | intelligent-core | intelligent-core/community_intelligence/api/routes.py:509 | `search_clauses()` |
| POST | `/community/engage` | intelligent-core | intelligent-core/expertise-center/service/api/tactical.py:507 | `engage_community()` |
| GET | `/competencies/summary` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/learning/competency_router.py:221 | `get_competency_summary()` |
| POST | `/compliance/analyze` | intelligent-core | intelligent-core/expertise-center/service/api/analyzers.py:147 | `analyze_compliance()` |
| POST | `/compliance/check` | intelligent-core | intelligent-core/expertise-center/service/api/tactical.py:221 | `check_compliance()` |
| POST | `/contributions` | intelligent-core | intelligent-core/community_intelligence/api/routes.py:113 | `submit_case()` |
| GET | `/contributions/pending-reviews` | intelligent-core | intelligent-core/community_intelligence/api/routes.py:188 | `get_pending_reviews()` |
| GET | `/contributions/{contribution_id}` | intelligent-core | intelligent-core/community_intelligence/api/routes.py:154 | `get_contribution()` |
| POST | `/contributions/{contribution_id}/review` | intelligent-core | intelligent-core/community_intelligence/api/routes.py:211 | `submit_review()` |
| POST | `/coverage/analyze` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/learning/process_gap_router.py:52 | `analyze_process_coverage()` |
| POST | `/coverage/save` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/learning/process_gap_router.py:180 | `save_process_coverage()` |
| GET | `/coverage/summary` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/learning/process_gap_router.py:163 | `get_coverage_summary()` |
| POST | `/create` | intelligent-core | intelligent-core/collective/api/collective_agents.py:113 | `create_collective_agent()` |
| GET | `/dashboard` | intelligent-core | intelligent-core/orchestration/ai-orchestration/api/monitoring_routes.py:647 | `get_dashboard_data()` |
| GET | `/dashboard/executive` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/learning/analytics_router.py:40 | `get_executive_dashboard()` |
| GET | `/dashboard/learning-trends` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/learning/analytics_router.py:120 | `get_learning_trends()` |
| POST | `/decay/calculate` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/learning/competency_router.py:199 | `calculate_skills_decay()` |
| POST | `/detect` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/learning/pattern_router.py:67 | `detect_patterns()` |
| POST | `/detect/anomalies` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/learning/ml_router.py:169 | `detect_anomalies()` |
| POST | `/difficulty/adjust` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/learning/ml_router.py:110 | `adjust_scenario_difficulty()` |
| GET | `/discovery/graph` | intelligent-core | intelligent-core/event_intelligence/main.py:236 | `get_event_graph()` |
| GET | `/discovery/patterns` | intelligent-core | intelligent-core/event_intelligence/main.py:178 | `get_patterns()` |
| GET | `/discovery/predict/{event_type}` | intelligent-core | intelligent-core/event_intelligence/main.py:194 | `predict_next_event()` |
| GET | `/discovery/services` | intelligent-core | intelligent-core/event_intelligence/main.py:165 | `get_services()` |
| GET | `/discovery/stats` | intelligent-core | intelligent-core/event_intelligence/main.py:219 | `get_discovery_stats()` |
| POST | `/documents/create` | intelligent-core | intelligent-core/expertise-center/service/api/tactical.py:380 | `create_document()` |
| POST | `/effectiveness/record` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/learning/knowledge_router.py:181 | `record_resource_effectiveness()` |
| GET | `/effectiveness/report` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/learning/knowledge_router.py:214 | `get_effectiveness_report()` |
| GET | `/effectiveness/{gap_keyword}/best-resources` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/learning/knowledge_router.py:230 | `get_best_resources_for_gap()` |
| POST | `/emergency/analyze` | intelligent-core | intelligent-core/expertise-center/service/api/analyzers.py:336 | `analyze_emergency()` |
| POST | `/execute` | intelligent-core | intelligent-core/orchestration/coordination-center/api/routes.py:32 | `execute_intent()` |
| GET | `/executions` | intelligent-core | intelligent-core/orchestration/coordination-center/api/routes.py:274 | `list_executions()` |
| GET | `/executions/{execution_id}` | intelligent-core | intelligent-core/orchestration/coordination-center/api/routes.py:260 | `get_execution()` |
| POST | `/executions/{execution_id}/approve` | intelligent-core | intelligent-core/orchestration/coordination-center/api/routes.py:289 | `approve_execution()` |
| POST | `/executions/{execution_id}/rollback` | intelligent-core | intelligent-core/orchestration/coordination-center/api/routes.py:371 | `rollback_execution()` |
| POST | `/exercise/design` | intelligent-core | intelligent-core/expertise-center/service/api/tactical.py:316 | `design_exercise()` |
| GET | `/expert-demand` | intelligent-core | intelligent-core/predictive/api/predictions.py:273 | `get_expert_demand_forecast()` |
| GET | `/experts` | intelligent-core | intelligent-core/expertise-center/service/api/routes.py:216 | `list_experts()` |
| GET | `/experts/{expert_id}` | intelligent-core | intelligent-core/expertise-center/service/api/routes.py:234 | `get_expert_info()` |
| POST | `/from-workflow/{workflow_id}` | intelligent-core | intelligent-core/community_intelligence/api/contributions.py:308 | `create_contribution_from_workflow()` |
| GET | `/gap-mappings` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/learning/knowledge_router.py:256 | `list_gap_mappings()` |
| POST | `/gap-mappings/create` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/learning/knowledge_router.py:271 | `create_gap_mapping()` |
| GET | `/gaps/critical` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/learning/process_gap_router.py:144 | `get_critical_gaps()` |
| POST | `/gaps/map-to-knowledge` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/learning/knowledge_router.py:56 | `map_gaps_to_knowledge()` |
| POST | `/governance/analyze` | intelligent-core | intelligent-core/expertise-center/service/api/analyzers.py:212 | `analyze_governance()` |
| POST | `/governance/analyze` | intelligent-core | intelligent-core/expertise-center/service/api/tactical.py:412 | `analyze_governance()` |
| GET | `/guidance/{clause_id}` | intelligent-core | intelligent-core/community_intelligence/api/routes.py:355 | `get_synthesized_guidance()` |
| GET | `/health` | intelligent-core | intelligent-core/METRICS_INTEGRATION_EXAMPLE.py:43 | `health()` |
| GET | `/health` | intelligent-core | intelligent-core/main.py:101 | `health_check()` |
| GET | `/health` | intelligent-core | intelligent-core/workflow-engine/main.py:67 | `health_check()` |
| GET | `/health` | intelligent-core | intelligent-core/workflow-engine/workflow/api/main.py:253 | `health_check()` |
| GET | `/health` | intelligent-core | intelligent-core/predictive/main.py:175 | `health_check()` |
| GET | `/health` | intelligent-core | intelligent-core/expertise-center/service/standalone_main.py:86 | `health_check()` |
| GET | `/health` | intelligent-core | intelligent-core/expertise-center/service/main.py:136 | `health()` |
| GET | `/health` | intelligent-core | intelligent-core/expertise-center/service/api/routes.py:60 | `health_check()` |
| GET | `/health` | intelligent-core | intelligent-core/collective/main.py:218 | `health_check()` |
| GET | `/health` | intelligent-core | intelligent-core/ai_workflow_optimizer/main.py:822 | `health_check()` |
| GET | `/health` | intelligent-core | intelligent-core/workflow_intelligence/main.py:124 | `health_check()` |
| GET | `/health` | intelligent-core | intelligent-core/event_intelligence/api.py:94 | `health_check()` |
| GET | `/health` | intelligent-core | intelligent-core/event_intelligence/main.py:112 | `health_check()` |
| GET | `/health` | intelligent-core | intelligent-core/event_intelligence/api/routes.py:163 | `health_check()` |
| GET | `/health` | intelligent-core | intelligent-core/ai-foundation/main.py:67 | `health_check()` |
| GET | `/health` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/main.py:194 | `health_check()` |
| GET | `/health` | intelligent-core | intelligent-core/community_intelligence/main.py:112 | `health_check()` |
| GET | `/health` | intelligent-core | intelligent-core/community_intelligence/api/routes.py:593 | `health_check()` |
| GET | `/health` | intelligent-core | intelligent-core/orchestration/pdca_assistant.py:520 | `health()` |
| GET | `/health` | intelligent-core | intelligent-core/orchestration/ai-orchestration/main.py:128 | `health_check()` |
| GET | `/health` | intelligent-core | intelligent-core/orchestration/ai-orchestration/tentacles/knowledge_orchestrator.py:283 | `check_all_services_health()` |
| GET | `/health` | intelligent-core | intelligent-core/orchestration/ai-orchestration/api/monitoring_routes.py:423 | `health_check()` |
| GET | `/health` | intelligent-core | intelligent-core/orchestration/coordination-center/main.py:130 | `health_standard()` |
| GET | `/health` | intelligent-core | intelligent-core/orchestration/coordination-center/api/routes.py:495 | `health_check()` |
| GET | `/health/live` | intelligent-core | intelligent-core/orchestration/ai-orchestration/api/monitoring_routes.py:462 | `liveness_probe()` |
| GET | `/health/ready` | intelligent-core | intelligent-core/orchestration/ai-orchestration/api/monitoring_routes.py:475 | `readiness_probe()` |
| POST | `/impact/analyze` | intelligent-core | intelligent-core/expertise-center/service/api/analyzers.py:367 | `analyze_impact()` |
| POST | `/incident/advise` | intelligent-core | intelligent-core/expertise-center/service/api/tactical.py:252 | `advise_on_incident()` |
| GET | `/info` | intelligent-core | intelligent-core/expertise-center/service/standalone_main.py:102 | `get_info()` |
| GET | `/info` | intelligent-core | intelligent-core/expertise-center/service/api/routes.py:70 | `get_info()` |
| GET | `/info` | intelligent-core | intelligent-core/workflow_intelligence/main.py:140 | `get_info()` |
| GET | `/insights/similar-orgs/{org_id}` | intelligent-core | intelligent-core/community_intelligence/api/routes.py:443 | `get_similar_org_insights()` |
| GET | `/instances` | intelligent-core | intelligent-core/workflow-engine/workflow/api/main.py:549 | `list_instances()` |
| DELETE | `/instances/{instance_id}` | intelligent-core | intelligent-core/workflow-engine/workflow/api/main.py:573 | `terminate_instance()` |
| GET | `/instances/{instance_id}/visual-state` | intelligent-core | intelligent-core/workflow-engine/workflow/api/main.py:349 | `get_visual_state()` |
| GET | `/iso-mapping` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/learning/process_gap_router.py:209 | `get_iso_22301_mapping()` |
| GET | `/journey/{org_id}` | intelligent-core | intelligent-core/predictive/api/predictions.py:71 | `get_journey_prediction()` |
| POST | `/kb/auto-create-from-pattern` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/learning/platform_integration_router.py:381 | `auto_create_knowledge_from_pattern()` |
| POST | `/kb/auto-create-from-patterns` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/learning/self_learning_router.py:173 | `auto_create_knowledge()` |
| POST | `/kb/create-learning-path` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/learning/platform_integration_router.py:343 | `create_learning_path()` |
| POST | `/kb/create-learning-path` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/learning/self_learning_router.py:153 | `create_learning_path_from_kb()` |
| GET | `/kb/search` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/learning/self_learning_router.py:126 | `search_knowledge_base()` |
| POST | `/kb/sync-external` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/learning/platform_integration_router.py:418 | `sync_external_knowledge()` |
| POST | `/kb/sync-external` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/learning/self_learning_router.py:201 | `sync_external_knowledge()` |
| POST | `/knowledge/export` | intelligent-core | intelligent-core/event_intelligence/api/routes.py:642 | `export_knowledge()` |
| GET | `/knowledge/patterns/{event_name}` | intelligent-core | intelligent-core/event_intelligence/api.py:307 | `get_relevant_patterns()` |
| GET | `/knowledge/patterns/{event_name}` | intelligent-core | intelligent-core/event_intelligence/api/routes.py:591 | `get_relevant_patterns()` |
| GET | `/knowledge/similar/{event_name}` | intelligent-core | intelligent-core/event_intelligence/api.py:288 | `get_similar_events()` |
| GET | `/knowledge/similar/{event_name}` | intelligent-core | intelligent-core/event_intelligence/api/routes.py:565 | `get_similar_events()` |
| GET | `/knowledge/stats` | intelligent-core | intelligent-core/event_intelligence/api.py:326 | `get_knowledge_stats()` |
| GET | `/knowledge/stats` | intelligent-core | intelligent-core/event_intelligence/api/routes.py:617 | `get_knowledge_stats()` |
| GET | `/leaderboard/global` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/learning/gamification_router.py:194 | `get_global_leaderboard()` |
| GET | `/leaderboard/global` | intelligent-core | intelligent-core/community_intelligence/api/reputation.py:148 | `get_global_leaderboard()` |
| GET | `/leaderboard/monthly` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/learning/gamification_router.py:213 | `get_monthly_leaderboard()` |
| GET | `/leaderboard/scenario/{scenario_type}` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/learning/gamification_router.py:236 | `get_scenario_leaderboard()` |
| GET | `/leaderboard/{module}` | intelligent-core | intelligent-core/community_intelligence/api/reputation.py:172 | `get_module_leaderboard()` |
| POST | `/learning-paths/generate` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/learning/knowledge_router.py:81 | `generate_learning_path()` |
| POST | `/learning-paths/save` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/learning/knowledge_router.py:106 | `save_learning_path()` |
| POST | `/learning-paths/{path_id}/progress` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/learning/knowledge_router.py:151 | `update_learning_progress()` |
| GET | `/learning-paths/{user_id}` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/learning/knowledge_router.py:132 | `get_user_learning_paths()` |
| POST | `/learning/analyze` | intelligent-core | intelligent-core/expertise-center/service/api/analyzers.py:274 | `analyze_learning()` |
| POST | `/learning/design` | intelligent-core | intelligent-core/expertise-center/service/api/tactical.py:444 | `design_learning()` |
| POST | `/learning/feedback` | intelligent-core | intelligent-core/event_intelligence/api.py:203 | `record_feedback()` |
| POST | `/learning/feedback` | intelligent-core | intelligent-core/event_intelligence/api/routes.py:399 | `record_feedback()` |
| GET | `/learning/report` | intelligent-core | intelligent-core/event_intelligence/api.py:246 | `get_learning_report()` |
| GET | `/learning/report` | intelligent-core | intelligent-core/event_intelligence/api/routes.py:464 | `get_learning_report()` |
| GET | `/learning/stats` | intelligent-core | intelligent-core/event_intelligence/api.py:231 | `get_learning_stats()` |
| GET | `/learning/stats` | intelligent-core | intelligent-core/event_intelligence/api/routes.py:437 | `get_learning_stats()` |
| POST | `/learning/suggest` | intelligent-core | intelligent-core/event_intelligence/api.py:175 | `record_suggestion()` |
| POST | `/learning/suggest` | intelligent-core | intelligent-core/event_intelligence/api/routes.py:361 | `record_suggestion()` |
| GET | `/levels` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/learning/gamification_router.py:186 | `get_level_definitions()` |
| POST | `/lifecycle/analyze` | intelligent-core | intelligent-core/expertise-center/service/api/analyzers.py:243 | `analyze_lifecycle()` |
| GET | `/llm` | intelligent-core | intelligent-core/orchestration/ai-orchestration/api/monitoring_routes.py:332 | `get_llm_performance()` |
| GET | `/llm/cost` | intelligent-core | intelligent-core/orchestration/ai-orchestration/api/monitoring_routes.py:373 | `get_llm_cost_breakdown()` |
| GET | `/marketplace/demand-forecast` | intelligent-core | intelligent-core/community_intelligence/api/routes.py:481 | `get_demand_forecast()` |
| POST | `/matrix/generate` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/learning/process_gap_router.py:80 | `generate_coverage_matrix()` |
| GET | `/metrics` | intelligent-core | intelligent-core/METRICS_INTEGRATION_EXAMPLE.py:17 | `metrics()` |
| GET | `/metrics` | intelligent-core | intelligent-core/main.py:117 | `metrics()` |
| GET | `/metrics` | intelligent-core | intelligent-core/workflow-engine/main.py:71 | `metrics()` |
| GET | `/metrics` | intelligent-core | intelligent-core/workflow-engine/workflow/api/main.py:267 | `metrics()` |
| GET | `/metrics` | intelligent-core | intelligent-core/predictive/main.py:186 | `metrics()` |
| GET | `/metrics` | intelligent-core | intelligent-core/expertise-center/service/standalone_main.py:96 | `metrics()` |
| GET | `/metrics` | intelligent-core | intelligent-core/expertise-center/service/main.py:146 | `metrics()` |
| GET | `/metrics` | intelligent-core | intelligent-core/collective/main.py:232 | `metrics()` |
| GET | `/metrics` | intelligent-core | intelligent-core/ai_workflow_optimizer/main.py:827 | `metrics()` |
| GET | `/metrics` | intelligent-core | intelligent-core/workflow_intelligence/main.py:134 | `metrics()` |
| GET | `/metrics` | intelligent-core | intelligent-core/event_intelligence/main.py:123 | `metrics()` |
| GET | `/metrics` | intelligent-core | intelligent-core/event_intelligence/api/routes.py:667 | `get_metrics()` |
| GET | `/metrics` | intelligent-core | intelligent-core/ai-foundation/main.py:71 | `metrics()` |
| GET | `/metrics` | intelligent-core | intelligent-core/community_intelligence/main.py:122 | `metrics()` |
| GET | `/metrics` | intelligent-core | intelligent-core/orchestration/ai-orchestration/main.py:134 | `metrics()` |
| GET | `/metrics` | intelligent-core | intelligent-core/orchestration/ai-orchestration/api/monitoring_routes.py:68 | `prometheus_metrics()` |
| GET | `/ml/feature-importance` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/learning/platform_integration_router.py:318 | `get_feature_importance()` |
| GET | `/ml/model-info` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/learning/ml_router.py:275 | `get_ml_model_info()` |
| GET | `/ml/performance` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/learning/platform_integration_router.py:296 | `get_ml_performance()` |
| POST | `/ml/predict-success` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/learning/platform_integration_router.py:199 | `predict_exercise_success()` |
| POST | `/ml/submit-feedback` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/learning/platform_integration_router.py:257 | `submit_prediction_feedback()` |
| GET | `/my` | intelligent-core | intelligent-core/community_intelligence/api/reviews.py:181 | `get_my_reviews()` |
| GET | `/my` | intelligent-core | intelligent-core/community_intelligence/api/contributions.py:155 | `get_my_contributions()` |
| POST | `/needs/collect` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/learning/self_learning_router.py:71 | `collect_learning_needs()` |
| GET | `/needs/training-plan` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/learning/self_learning_router.py:106 | `get_training_plan()` |
| GET | `/next-exercise` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/learning/recommendation_router.py:185 | `recommend_next_exercise()` |
| GET | `/optimal-challenge` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/learning/ml_router.py:195 | `get_optimal_challenge_zone()` |
| GET | `/pending` | intelligent-core | intelligent-core/community_intelligence/api/reviews.py:139 | `get_pending_reviews()` |
| GET | `/performance` | intelligent-core | intelligent-core/orchestration/ai-orchestration/api/monitoring_routes.py:126 | `get_performance_statistics()` |
| POST | `/performance/analyze` | intelligent-core | intelligent-core/expertise-center/service/api/analyzers.py:305 | `analyze_performance()` |
| GET | `/performance/golden-metrics` | intelligent-core | intelligent-core/orchestration/ai-orchestration/api/monitoring_routes.py:168 | `get_golden_metrics()` |
| POST | `/plan/analyze` | intelligent-core | intelligent-core/expertise-center/service/api/analyzers.py:398 | `analyze_plan()` |
| POST | `/plan/generate` | intelligent-core | intelligent-core/expertise-center/service/api/tactical.py:284 | `generate_plan()` |
| POST | `/points/award` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/learning/gamification_router.py:157 | `award_points()` |
| POST | `/predict/gaps` | intelligent-core | intelligent-core/event_intelligence/api.py:261 | `predict_gaps()` |
| POST | `/predict/gaps` | intelligent-core | intelligent-core/event_intelligence/api/routes.py:488 | `predict_gaps()` |
| GET | `/predict/recommendations/{event_name}` | intelligent-core | intelligent-core/event_intelligence/api/routes.py:531 | `get_event_recommendations()` |
| POST | `/predict/success` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/learning/ml_router.py:74 | `predict_exercise_success()` |
| POST | `/preview-anonymization` | intelligent-core | intelligent-core/community_intelligence/api/contributions.py:278 | `preview_anonymization()` |
| POST | `/priorities/generate` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/learning/process_gap_router.py:236 | `generate_improvement_priorities()` |
| POST | `/processes` | intelligent-core | intelligent-core/workflow-engine/workflow/api/main.py:280 | `start_process()` |
| GET | `/processes` | intelligent-core | intelligent-core/workflow-engine/workflow/api/main.py:525 | `list_processes()` |
| GET | `/processes` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/learning/process_gap_router.py:103 | `list_bcm_processes()` |
| GET | `/processes/{process_id}` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/learning/process_gap_router.py:127 | `get_process_details()` |
| POST | `/profile/calculate` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/learning/gamification_router.py:56 | `calculate_gamification_profile()` |
| GET | `/profile/{user_id}` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/learning/gamification_router.py:84 | `get_gamification_profile()` |
| POST | `/project/manage` | intelligent-core | intelligent-core/expertise-center/service/api/tactical.py:348 | `manage_project()` |
| POST | `/query` | intelligent-core | intelligent-core/expertise-center/service/standalone_main.py:138 | `query_expert()` |
| POST | `/query` | intelligent-core | intelligent-core/expertise-center/service/api/routes.py:262 | `query_expert()` |
| POST | `/rag/add-knowledge` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/learning/platform_integration_router.py:153 | `contribute_knowledge_to_rag()` |
| POST | `/rag/search` | intelligent-core | intelligent-core/METRICS_INTEGRATION_EXAMPLE.py:56 | `rag_search()` |
| POST | `/rag/search` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/learning/platform_integration_router.py:114 | `search_unified_knowledge()` |
| POST | `/recommend` | intelligent-core | intelligent-core/workflow_intelligence/main.py:283 | `get_recommendations()` |
| POST | `/recommend/learning-path` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/learning/ml_router.py:133 | `recommend_learning_path()` |
| GET | `/recommendations/{org_id}` | intelligent-core | intelligent-core/predictive/api/predictions.py:233 | `get_recommendations()` |
| GET | `/reputation/leaderboard` | intelligent-core | intelligent-core/community_intelligence/api/routes.py:277 | `get_leaderboard()` |
| GET | `/reputation/{user_id}` | intelligent-core | intelligent-core/community_intelligence/api/routes.py:250 | `get_reputation()` |
| GET | `/resources` | intelligent-core | intelligent-core/orchestration/ai-orchestration/api/monitoring_routes.py:503 | `get_resource_metrics()` |
| GET | `/resources/recommend` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/learning/knowledge_router.py:299 | `recommend_resources()` |
| POST | `/results` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/learning/learning_router.py:96 | `create_exercise_result()` |
| GET | `/results` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/learning/learning_router.py:144 | `list_exercise_results()` |
| POST | `/risk/analyze` | intelligent-core | intelligent-core/expertise-center/service/api/analyzers.py:181 | `analyze_risk()` |
| POST | `/risk/assess` | intelligent-core | intelligent-core/expertise-center/service/api/tactical.py:190 | `assess_risk()` |
| GET | `/roles` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/learning/competency_router.py:191 | `list_available_roles()` |
| POST | `/roles/gaps` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/learning/competency_router.py:150 | `analyze_role_gaps()` |
| GET | `/roles/{role_name}/requirements` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/learning/competency_router.py:174 | `get_role_requirements()` |
| GET | `/scenario-complexity` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/learning/ml_router.py:212 | `get_scenario_complexity()` |
| POST | `/scenario/analyze` | intelligent-core | intelligent-core/expertise-center/service/api/analyzers.py:429 | `analyze_scenario()` |
| GET | `/scenarios` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/learning/learning_router.py:265 | `list_scenario_types()` |
| GET | `/scenarios/{scenario_type}` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/learning/learning_router.py:178 | `get_scenario_learning()` |
| GET | `/search` | intelligent-core | intelligent-core/community_intelligence/api/cases.py:51 | `search_cases()` |
| GET | `/self-learn/accuracy-report` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/learning/self_learning_router.py:315 | `get_accuracy_report()` |
| GET | `/self-learn/effectiveness` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/learning/self_learning_router.py:296 | `analyze_learning_effectiveness()` |
| GET | `/self-learn/export-training-data` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/learning/self_learning_router.py:381 | `export_training_data()` |
| GET | `/self-learn/feature-importance` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/learning/self_learning_router.py:361 | `get_feature_importance()` |
| GET | `/self-learn/predictions` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/learning/self_learning_router.py:334 | `get_predictions()` |
| POST | `/self-learn/record-outcome` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/learning/self_learning_router.py:265 | `record_outcome()` |
| POST | `/self-learn/record-prediction` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/learning/self_learning_router.py:231 | `record_prediction()` |
| POST | `/self-learn/trigger-retrain` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/learning/self_learning_router.py:397 | `trigger_model_retrain()` |
| GET | `/similar-organizations/{org_id}` | intelligent-core | intelligent-core/predictive/api/predictions.py:356 | `get_similar_organizations()` |
| GET | `/similar/for-workflow` | intelligent-core | intelligent-core/community_intelligence/api/cases.py:155 | `find_similar_cases()` |
| POST | `/simulate/performance` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/learning/ml_router.py:222 | `simulate_performance()` |
| GET | `/sla` | intelligent-core | intelligent-core/orchestration/ai-orchestration/api/monitoring_routes.py:612 | `get_sla_metrics()` |
| GET | `/standards` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/main.py:296 | `list_standards()` |
| GET | `/standards/{standard_id:path}` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/main.py:331 | `get_standard()` |
| GET | `/standards/{standard_id:path}/metadata` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/main.py:399 | `get_standard_metadata()` |
| GET | `/stats` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/learning/learning_router.py:273 | `get_learning_stats()` |
| GET | `/stats/community` | intelligent-core | intelligent-core/community_intelligence/api/routes.py:528 | `get_community_stats()` |
| GET | `/stats/eventbus` | intelligent-core | intelligent-core/predictive/api/predictions.py:390 | `get_eventbus_stats()` |
| GET | `/stats/impact` | intelligent-core | intelligent-core/community_intelligence/api/routes.py:573 | `get_impact_stats()` |
| GET | `/stats/overview` | intelligent-core | intelligent-core/community_intelligence/api/cases.py:207 | `get_case_library_stats()` |
| GET | `/stats/summary` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/learning/gamification_router.py:302 | `get_gamification_stats()` |
| GET | `/status` | intelligent-core | intelligent-core/event_intelligence/api/routes.py:189 | `get_status()` |
| GET | `/status` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/learning/platform_integration_router.py:507 | `platform_integration_status()` |
| GET | `/status` | intelligent-core | intelligent-core/orchestration/ai-orchestration/tentacles/knowledge_orchestrator.py:346 | `get_platform_status()` |
| GET | `/streaks/{user_id}` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/learning/gamification_router.py:257 | `get_user_streaks()` |
| POST | `/tasks/{task_id}/assign` | intelligent-core | intelligent-core/workflow-engine/workflow/api/main.py:461 | `assign_task()` |
| POST | `/tasks/{task_id}/complete` | intelligent-core | intelligent-core/workflow-engine/workflow/api/main.py:392 | `complete_task()` |
| POST | `/teams/analyze` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/learning/competency_router.py:122 | `analyze_team_competency()` |
| POST | `/timeline/predict` | intelligent-core | intelligent-core/community_intelligence/api/routes.py:421 | `predict_timeline()` |
| GET | `/timeline/{org_id}/next-steps` | intelligent-core | intelligent-core/community_intelligence/api/routes.py:455 | `get_next_steps()` |
| GET | `/tools` | intelligent-core | intelligent-core/orchestration/coordination-center/api/routes.py:452 | `list_tools()` |
| GET | `/tools/{tool_id}` | intelligent-core | intelligent-core/orchestration/coordination-center/api/routes.py:463 | `get_tool()` |
| GET | `/training` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/learning/recommendation_router.py:135 | `get_training_recommendations()` |
| GET | `/transactions/{user_id}` | intelligent-core | intelligent-core/community_intelligence/api/reputation.py:199 | `get_transactions()` |
| POST | `/unified/predict-and-recommend` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/learning/platform_integration_router.py:451 | `unified_prediction_workflow()` |
| GET | `/users/{user_email}/tasks` | intelligent-core | intelligent-core/workflow-engine/workflow/api/main.py:492 | `get_user_tasks()` |
| POST | `/users/{user_id}/competency` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/learning/competency_router.py:73 | `calculate_user_competency()` |
| GET | `/users/{user_id}/competency` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/learning/competency_router.py:104 | `get_user_competency()` |
| POST | `/validation/validate` | intelligent-core | intelligent-core/expertise-center/service/api/tactical.py:476 | `validate_bcm()` |
| POST | `/workflow/full-cycle` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/learning/self_learning_router.py:423 | `run_full_learning_cycle()` |
| GET | `/{agent_id}` | intelligent-core | intelligent-core/collective/api/collective_agents.py:223 | `get_agent_details()` |
| POST | `/{agent_id}/chat` | intelligent-core | intelligent-core/collective/api/collective_agents.py:164 | `chat_with_agent()` |
| GET | `/{agent_id}/history` | intelligent-core | intelligent-core/collective/api/collective_agents.py:294 | `get_chat_history()` |
| GET | `/{case_id}` | intelligent-core | intelligent-core/community_intelligence/api/cases.py:109 | `get_case()` |
| GET | `/{contribution_id}` | intelligent-core | intelligent-core/community_intelligence/api/contributions.py:188 | `get_contribution()` |
| DELETE | `/{contribution_id}` | intelligent-core | intelligent-core/community_intelligence/api/contributions.py:241 | `withdraw_contribution()` |
| GET | `/{pattern_id}` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/learning/pattern_router.py:220 | `get_pattern()` |
| DELETE | `/{pattern_id}` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/learning/pattern_router.py:269 | `deactivate_pattern()` |
| POST | `/{pattern_id}/acknowledge` | intelligent-core | intelligent-core/ai-foundation/learning-knowledge/api/learning/pattern_router.py:248 | `acknowledge_pattern()` |
| GET | `/{review_id}` | intelligent-core | intelligent-core/community_intelligence/api/reviews.py:213 | `get_review()` |
| GET | `/{user_id}` | intelligent-core | intelligent-core/community_intelligence/api/reputation.py:90 | `get_reputation()` |
| GET | `/{user_id}/expertise/{module}` | intelligent-core | intelligent-core/community_intelligence/api/reputation.py:122 | `get_expertise_level()` |
| GET | `, response_model=List[OrganizationResponse])
async def list_organizations(
    industry: Optional[str] = None,
    organization_size: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    ` | platform-services | platform-services/community-service/portal/api/organizations.py:136 | `unknown()` |
| GET | `, response_model=List[ProjectResponse])
async def search_projects(
    # Search filters
    service_type: Optional[str] = Query(None, description=` | platform-services | platform-services/community-service/marketplace/api/projects.py:64 | `unknown()` |
| GET | `, response_model=List[ProposalResponse])
async def get_my_proposals(
    status: Optional[str] = Query(None, description=` | platform-services | platform-services/community-service/marketplace/api/proposals.py:86 | `unknown()` |
| GET | `, response_model=List[ReviewResponse])
async def list_reviews(
    # Filters
    specialist_id: Optional[int] = Query(None, description=` | platform-services | platform-services/community-service/marketplace/api/reviews.py:75 | `unknown()` |
| GET | `, response_model=List[SpecialistResponse])
async def search_specialists(
    # Search filters
    skills: Optional[str] = Query(None, description=` | platform-services | platform-services/community-service/marketplace/api/specialists.py:68 | `unknown()` |
| POST | `, response_model=ProjectResponse, status_code=201)
async def create_project(
    project_data: ProjectCreate,
    current_user: dict = Depends(require_client),
    db: AsyncSession = Depends(get_db_with_context)
):
    ` | platform-services | platform-services/community-service/marketplace/api/projects.py:34 | `unknown()` |
| POST | `, response_model=ProposalResponse, status_code=201)
async def submit_proposal(
    proposal_data: ProposalCreate,
    current_user: dict = Depends(require_verified_specialist),
    db: AsyncSession = Depends(get_db_with_context)
):
    ` | platform-services | platform-services/community-service/marketplace/api/proposals.py:32 | `unknown()` |
| POST | `, response_model=ReviewResponse, status_code=201)
async def create_review(
    review_data: ReviewCreate,
    current_user: dict = Depends(require_client),
    db: AsyncSession = Depends(get_db_with_context)
):
    ` | platform-services | platform-services/community-service/marketplace/api/reviews.py:33 | `unknown()` |
| GET | `, response_model=ScenarioListResponse)
async def get_scenarios(
    scenario_type: Optional[str] = Query(None, description=` | platform-services | platform-services/community-service/portal/api/scenarios.py:30 | `unknown()` |
| POST | `, response_model=SpecialistResponse, status_code=201)
async def create_specialist_profile(
    specialist_data: SpecialistCreate,
    current_user: dict = Depends(require_specialist),
    db: AsyncSession = Depends(get_db_with_context)
):
    ` | platform-services | platform-services/community-service/marketplace/api/specialists.py:40 | `unknown()` |
| GET | `/` | platform-services | platform-services/compliance-service/api/gaps.py:49 | `list_gaps()` |
| POST | `/` | platform-services | platform-services/compliance-service/api/assessments.py:69 | `create_assessment()` |
| GET | `/` | platform-services | platform-services/compliance-service/api/assessments.py:115 | `list_assessments()` |
| POST | `/` | platform-services | platform-services/compliance-service/api/evidence.py:58 | `create_evidence()` |
| GET | `/` | platform-services | platform-services/compliance-service/api/evidence.py:116 | `list_evidence()` |
| POST | `/` | platform-services | platform-services/compliance-service/api/management_review.py:58 | `create_management_review()` |
| GET | `/` | platform-services | platform-services/compliance-service/api/management_review.py:112 | `list_management_reviews()` |
| GET | `/` | platform-services | platform-services/governance-service/main.py:235 | `root()` |
| GET | `/` | platform-services | platform-services/plans_service/main.py:461 | `root()` |
| GET | `/` | platform-services | platform-services/planning_service/main.py:447 | `root()` |
| POST | `/` | platform-services | platform-services/planning_service/api/routes.py:27 | `create_strategy()` |
| GET | `/` | platform-services | platform-services/planning_service/api/routes.py:54 | `list_strategies()` |
| GET | `/` | platform-services | platform-services/living-docs/main.py:239 | `root()` |
| GET | `/` | platform-services | platform-services/risk-service/main.py:210 | `root()` |
| GET | `/` | platform-services | platform-services/simulation/simulation/main.py:81 | `root()` |
| GET | `/` | platform-services | platform-services/simulation/simulation/simulation2/simple_app.py:40 | `root()` |
| GET | `/` | platform-services | platform-services/simulation/simulation/simulation/bia_engine/app.py:453 | `root()` |
| GET | `/` | platform-services | platform-services/simulation/simulation/simulation/bia_engine_O/app.py:453 | `root()` |
| GET | `/` | platform-services | platform-services/simulation/simulation/simulation/scenario_orchestrator/main.py:549 | `root()` |
| GET | `/` | platform-services | platform-services/simulation/scenarios/scenario_orchestrator/main.py:549 | `root()` |
| GET | `/` | platform-services | platform-services/simulation/digital-twin/api/app.py:237 | `root()` |
| POST | `/` | platform-services | platform-services/simulation/digital-twin/api/routers/bia.py:89 | `create_bia_analysis()` |
| GET | `/` | platform-services | platform-services/simulation/digital-twin/api/routers/bia.py:146 | `list_bia_analyses()` |
| POST | `/` | platform-services | platform-services/simulation/digital-twin/api/routers/scenarios.py:102 | `create_scenario_template()` |
| GET | `/` | platform-services | platform-services/simulation/digital-twin/api/routers/scenarios.py:132 | `list_scenario_templates()` |
| POST | `/` | platform-services | platform-services/simulation/digital-twin/api/routers/predictions.py:81 | `create_prediction()` |
| GET | `/` | platform-services | platform-services/simulation/digital-twin/api/routers/predictions.py:273 | `list_predictions()` |
| POST | `/` | platform-services | platform-services/simulation/digital-twin/api/routers/simulations.py:100 | `create_simulation()` |
| GET | `/` | platform-services | platform-services/simulation/digital-twin/api/routers/simulations.py:257 | `list_simulations()` |
| POST | `/` | platform-services | platform-services/simulation/digital-twin/api/routers/organizations.py:119 | `create_organization()` |
| GET | `/` | platform-services | platform-services/simulation/digital-twin/api/routers/organizations.py:369 | `list_organizations()` |
| POST | `/` | platform-services | platform-services/simulation/digital-twin/api/routers/exercises.py:104 | `create_exercise()` |
| GET | `/` | platform-services | platform-services/simulation/digital-twin/api/routers/exercises.py:154 | `list_exercises()` |
| GET | `/` | platform-services | platform-services/community-service/portal/main.py:134 | `root()` |
| GET | `/` | platform-services | platform-services/community-service/marketplace/main.py:140 | `root()` |
| GET | `/` | platform-services | platform-services/response-service/main.py:313 | `root()` |
| GET | `/` | platform-services | platform-services/learning-service/main.py:240 | `root()` |
| GET | `/` | platform-services | platform-services/documents-service/main.py:339 | `root()` |
| PUT | `/actions/{action_id}` | platform-services | platform-services/response-service/api/routes.py:357 | `update_response_action()` |
| GET | `/activations` | platform-services | platform-services/plans_service/api/routes.py:306 | `list_activations()` |
| POST | `/ai-generate` | platform-services | platform-services/simulation/digital-twin/api/routers/scenarios.py:273 | `generate_scenario_with_ai()` |
| POST | `/ai-generate` | platform-services | platform-services/community-service/portal/api/knowledge.py:464 | `generate_article_from_exercise()` |
| POST | `/ai-generate-advanced` | platform-services | platform-services/simulation/digital-twin/api/routers/scenarios.py:470 | `generate_scenario_advanced_ai()` |
| POST | `/ai-scenarios/generate/{twin_id}` | platform-services | platform-services/simulation/digital-twin/api/routers/integrations.py:276 | `generate_ai_scenario()` |
| GET | `/analytics` | platform-services | platform-services/compliance-service/api/dashboard.py:404 | `get_compliance_analytics()` |
| GET | `/analytics/compliance` | platform-services | platform-services/documents-service/api/routes.py:578 | `get_compliance_analytics()` |
| GET | `/analytics/patterns` | platform-services | platform-services/validation-service/api/workflow_ai.py:250 | `analyze_patterns()` |
| GET | `/analytics/patterns` | platform-services | platform-services/risk-service/api/workflow_ai.py:232 | `analyze_patterns()` |
| GET | `/analytics/patterns` | platform-services | platform-services/response-service/api/workflow_ai.py:233 | `analyze_patterns()` |
| GET | `/analytics/performance` | platform-services | platform-services/validation-service/api/workflow_ai.py:293 | `get_performance_metrics()` |
| GET | `/analytics/performance` | platform-services | platform-services/risk-service/api/workflow_ai.py:272 | `get_performance_metrics()` |
| GET | `/analytics/performance` | platform-services | platform-services/response-service/api/workflow_ai.py:273 | `get_performance_metrics()` |
| POST | `/analyze` | platform-services | platform-services/simulation/simulation/simulation/scenario_orchestrator/app/api/v1/endpoints/scenarios.py:117 | `analyze_scenario()` |
| POST | `/analyze` | platform-services | platform-services/simulation/simulation/simulation/scenario_orchestrator/src/api/v1/endpoints/scenarios.py:117 | `analyze_scenario()` |
| POST | `/analyze` | platform-services | platform-services/simulation/scenarios/scenario_orchestrator/app/api/v1/endpoints/scenarios.py:117 | `analyze_scenario()` |
| POST | `/analyze` | platform-services | platform-services/simulation/scenarios/scenario_orchestrator/src/api/v1/endpoints/scenarios.py:117 | `analyze_scenario()` |
| POST | `/api/alerts` | platform-services | platform-services/simulation/simulation/thehive/thehive_adapter.py:506 | `create_alert()` |
| POST | `/api/alerts/{alert_id}/promote` | platform-services | platform-services/simulation/simulation/thehive/thehive_adapter.py:531 | `promote_alert()` |
| POST | `/api/batch/simulations` | platform-services | platform-services/simulation/simulation/simulation2/app.py:309 | `run_batch_simulations()` |
| POST | `/api/bia/processes/{process_id}/suggest-rto` | platform-services | platform-services/governance-service/services/ai_domain_integration.py:291 | `suggest_rto_with_domain()` |
| POST | `/api/cases` | platform-services | platform-services/simulation/simulation/thehive/thehive_adapter.py:512 | `create_case()` |
| GET | `/api/cases` | platform-services | platform-services/simulation/simulation/thehive/thehive_adapter.py:518 | `get_cases()` |
| POST | `/api/cases/create` | platform-services | platform-services/simulation/simulation/thehive/thehive/app.py:98 | `create_case_manual()` |
| GET | `/api/cases/search` | platform-services | platform-services/simulation/simulation/thehive/thehive/app.py:231 | `search_cases()` |
| GET | `/api/cases/{case_id}` | platform-services | platform-services/simulation/simulation/thehive/thehive/app.py:136 | `get_case_details()` |
| POST | `/api/cases/{case_id}/observables` | platform-services | platform-services/simulation/simulation/thehive/thehive/app.py:186 | `add_observable()` |
| POST | `/api/cases/{case_id}/tasks` | platform-services | platform-services/simulation/simulation/thehive/thehive/app.py:209 | `create_task()` |
| PUT | `/api/cases/{case_id}/update` | platform-services | platform-services/simulation/simulation/thehive/thehive/app.py:158 | `update_case()` |
| GET | `/api/compliance/check` | platform-services | platform-services/validation-service/main.py:279 | `compliance_check()` |
| GET | `/api/compliance/check` | platform-services | platform-services/compliance-service/main.py:538 | `compliance_check()` |
| GET | `/api/compliance/check` | platform-services | platform-services/governance-service/main.py:191 | `compliance_check()` |
| GET | `/api/compliance/check` | platform-services | platform-services/plans_service/main.py:425 | `compliance_check()` |
| GET | `/api/compliance/check` | platform-services | platform-services/planning_service/main.py:415 | `compliance_check()` |
| GET | `/api/compliance/check` | platform-services | platform-services/risk-service/main.py:177 | `compliance_check()` |
| GET | `/api/compliance/check` | platform-services | platform-services/response-service/main.py:331 | `compliance_check()` |
| GET | `/api/compliance/check` | platform-services | platform-services/learning-service/main.py:197 | `compliance_check()` |
| GET | `/api/compliance/check` | platform-services | platform-services/bia-service/main.py:423 | `compliance_check()` |
| GET | `/api/compliance/check` | platform-services | platform-services/documents-service/main.py:289 | `compliance_check()` |
| POST | `/api/events/webhook` | platform-services | platform-services/validation-service/main.py:314 | `event_webhook()` |
| GET | `/api/example` | platform-services | platform-services/shared/USAGE_EXAMPLE.py:151 | `example_endpoint()` |
| POST | `/api/exercises` | platform-services | platform-services/simulation/simulation/simulation/simulation/sim_adapter.py:547 | `create_exercise()` |
| GET | `/api/exercises` | platform-services | platform-services/simulation/simulation/simulation/simulation/sim_adapter.py:553 | `get_exercises()` |
| POST | `/api/exercises/{exercise_id}/complete` | platform-services | platform-services/simulation/simulation/simulation/simulation/sim_adapter.py:565 | `complete_exercise()` |
| GET | `/api/exercises/{exercise_id}/simulations` | platform-services | platform-services/simulation/simulation/simulation2/app.py:247 | `get_exercise_simulations()` |
| POST | `/api/exercises/{exercise_id}/start` | platform-services | platform-services/simulation/simulation/simulation/simulation/sim_adapter.py:559 | `start_exercise()` |
| GET | `/api/governance/policies` | platform-services | platform-services/learning-service/_archived/database.20251002/connection.py:36 | `list_policies()` |
| GET | `/api/learning/programs` | platform-services | platform-services/learning-service/database/connection.py:75 | `list_programs()` |
| GET | `/api/metrics` | platform-services | platform-services/simulation/simulation/thehive/thehive_adapter.py:525 | `get_metrics()` |
| GET | `/api/metrics` | platform-services | platform-services/simulation/simulation/simulation/simulation/sim_adapter.py:571 | `get_metrics()` |
| GET | `/api/metrics/{tenant_id}` | platform-services | platform-services/simulation/simulation/simulation2/app.py:263 | `get_simulation_metrics()` |
| GET | `/api/reports/{simulation_id}` | platform-services | platform-services/simulation/simulation/simulation2/app.py:328 | `generate_simulation_report()` |
| GET | `/api/scenarios` | platform-services | platform-services/simulation/simulation/simulation2/app.py:202 | `list_scenarios()` |
| GET | `/api/scenarios` | platform-services | platform-services/simulation/simulation/simulation/simulation/sim_adapter.py:541 | `get_scenarios()` |
| POST | `/api/scenarios/custom` | platform-services | platform-services/simulation/simulation/simulation2/app.py:275 | `create_custom_scenario()` |
| POST | `/api/scenarios/validate` | platform-services | platform-services/simulation/simulation/simulation2/app.py:230 | `validate_scenario()` |
| GET | `/api/scenarios/{scenario_name}` | platform-services | platform-services/simulation/simulation/simulation2/app.py:213 | `get_scenario_details()` |
| POST | `/api/simulations/start` | platform-services | platform-services/simulation/simulation/simulation2/app.py:103 | `start_simulation()` |
| GET | `/api/simulations/{simulation_id}/results` | platform-services | platform-services/simulation/simulation/simulation2/app.py:157 | `get_simulation_results()` |
| GET | `/api/simulations/{simulation_id}/status` | platform-services | platform-services/simulation/simulation/simulation2/app.py:140 | `get_simulation_status()` |
| POST | `/api/simulations/{simulation_id}/stop` | platform-services | platform-services/simulation/simulation/simulation2/app.py:174 | `stop_simulation()` |
| GET | `/api/statistics/{tenant_id}` | platform-services | platform-services/simulation/simulation/thehive/thehive/app.py:294 | `get_statistics()` |
| GET | `/api/templates` | platform-services | platform-services/simulation/simulation/simulation2/app.py:294 | `get_scenario_templates()` |
| POST | `/api/thehive/configs` | platform-services | platform-services/simulation/simulation/thehive/thehive_adapter/main.py:459 | `add_thehive_config()` |
| GET | `/api/thehive/configs` | platform-services | platform-services/simulation/simulation/thehive/thehive_adapter/main.py:464 | `get_thehive_configs()` |
| GET | `/api/thehive/mock/alerts` | platform-services | platform-services/simulation/simulation/thehive/thehive_adapter/main.py:635 | `get_mock_alert_data()` |
| GET | `/api/thehive/mock/cases` | platform-services | platform-services/simulation/simulation/thehive/thehive_adapter/main.py:630 | `get_mock_case_data()` |
| GET | `/api/thehive/mock/configs` | platform-services | platform-services/simulation/simulation/thehive/thehive_adapter/main.py:625 | `get_mock_thehive_config_data()` |
| GET | `/api/thehive/mock/metrics` | platform-services | platform-services/simulation/simulation/thehive/thehive_adapter/main.py:655 | `get_mock_metrics_data()` |
| GET | `/api/thehive/mock/observables` | platform-services | platform-services/simulation/simulation/thehive/thehive_adapter/main.py:640 | `get_mock_observable_data()` |
| POST | `/api/thehive/mock/setup-demo-config` | platform-services | platform-services/simulation/simulation/thehive/thehive_adapter/main.py:660 | `setup_demo_thehive_config()` |
| GET | `/api/thehive/mock/tasks` | platform-services | platform-services/simulation/simulation/thehive/thehive_adapter/main.py:645 | `get_mock_task_data()` |
| GET | `/api/thehive/mock/templates` | platform-services | platform-services/simulation/simulation/thehive/thehive_adapter/main.py:650 | `get_mock_template_data()` |
| POST | `/api/thehive/{config_id}/alerts` | platform-services | platform-services/simulation/simulation/thehive/thehive_adapter/main.py:516 | `create_alert()` |
| GET | `/api/thehive/{config_id}/alerts` | platform-services | platform-services/simulation/simulation/thehive/thehive_adapter/main.py:532 | `get_alerts()` |
| POST | `/api/thehive/{config_id}/alerts/{alert_id}/promote` | platform-services | platform-services/simulation/simulation/thehive/thehive_adapter/main.py:538 | `promote_alert_to_case()` |
| POST | `/api/thehive/{config_id}/bcm/incident` | platform-services | platform-services/simulation/simulation/thehive/thehive_adapter/main.py:572 | `create_bcm_incident()` |
| POST | `/api/thehive/{config_id}/cases` | platform-services | platform-services/simulation/simulation/thehive/thehive_adapter/main.py:473 | `create_case()` |
| GET | `/api/thehive/{config_id}/cases` | platform-services | platform-services/simulation/simulation/thehive/thehive_adapter/main.py:489 | `get_cases()` |
| GET | `/api/thehive/{config_id}/cases/{case_id}` | platform-services | platform-services/simulation/simulation/thehive/thehive_adapter/main.py:495 | `get_case()` |
| PATCH | `/api/thehive/{config_id}/cases/{case_id}` | platform-services | platform-services/simulation/simulation/thehive/thehive_adapter/main.py:501 | `update_case()` |
| POST | `/api/thehive/{config_id}/cases/{case_id}/tasks` | platform-services | platform-services/simulation/simulation/thehive/thehive_adapter/main.py:554 | `add_task_to_case()` |
| POST | `/api/v1/analyze` | platform-services | platform-services/bcm-coordination-service/main.py:249 | `analyze()` |
| POST | `/api/v1/analyze/batch` | platform-services | platform-services/bcm-coordination-service/main.py:293 | `batch_analyze()` |
| POST | `/api/v1/analyze/compliance` | platform-services | platform-services/bcm-coordination-service/main.py:338 | `analyze_compliance()` |
| POST | `/api/v1/analyze/impact` | platform-services | platform-services/bcm-coordination-service/main.py:376 | `analyze_impact()` |
| POST | `/api/v1/analyze/iso_clause` | platform-services | platform-services/bcm-coordination-service/main.py:395 | `analyze_by_iso_clause()` |
| POST | `/api/v1/analyze/risk` | platform-services | platform-services/bcm-coordination-service/main.py:357 | `analyze_risk()` |
| GET | `/api/v1/analyzers` | platform-services | platform-services/bcm-coordination-service/main.py:154 | `get_available_analyzers()` |
| PUT | `/api/v1/case/{case_id}` | platform-services | platform-services/simulation/simulation/thehive/bridge_service.py:207 | `update_case()` |
| GET | `/api/v1/case/{case_id}` | platform-services | platform-services/simulation/simulation/thehive/bridge_service.py:246 | `get_case()` |
| POST | `/api/v1/case/{case_id}/sync` | platform-services | platform-services/simulation/simulation/thehive/bridge_service.py:300 | `sync_case_to_bcm()` |
| GET | `/api/v1/cases` | platform-services | platform-services/simulation/simulation/thehive/bridge_service.py:263 | `list_cases()` |
| POST | `/api/v1/exercise/create-case` | platform-services | platform-services/simulation/simulation/thehive/bridge_service.py:175 | `create_case_from_exercise()` |
| GET | `/api/v1/exercises` | platform-services | platform-services/simulation/simulation/simulation/exercise_simulators/bridge_service.py:469 | `list_exercises()` |
| POST | `/api/v1/exercises/create` | platform-services | platform-services/simulation/simulation/simulation/exercise_simulators/bridge_service.py:195 | `create_exercise()` |
| POST | `/api/v1/exercises/{exercise_id}/complete` | platform-services | platform-services/simulation/simulation/simulation/exercise_simulators/bridge_service.py:409 | `complete_exercise()` |
| POST | `/api/v1/exercises/{exercise_id}/inject` | platform-services | platform-services/simulation/simulation/simulation/exercise_simulators/bridge_service.py:313 | `inject_event()` |
| POST | `/api/v1/exercises/{exercise_id}/start` | platform-services | platform-services/simulation/simulation/simulation/exercise_simulators/bridge_service.py:251 | `start_exercise()` |
| GET | `/api/v1/exercises/{exercise_id}/status` | platform-services | platform-services/simulation/simulation/simulation/exercise_simulators/bridge_service.py:364 | `get_exercise_status()` |
| POST | `/api/v1/incident/create-case` | platform-services | platform-services/simulation/simulation/thehive/bridge_service.py:143 | `create_case_from_incident()` |
| GET | `/api/v1/metrics` | platform-services | platform-services/simulation/simulation/thehive/bridge_service.py:331 | `get_metrics()` |
| GET | `/api/v1/metrics` | platform-services | platform-services/simulation/simulation/simulation/exercise_simulators/bridge_service.py:524 | `get_metrics()` |
| POST | `/api/v1/process-mining/analyze-performance/{process_id}` | platform-services | platform-services/мониторинг/process-analytics/main.py:926 | `analyze_performance()` |
| POST | `/api/v1/process-mining/comprehensive-analysis` | platform-services | platform-services/мониторинг/process-analytics/main.py:959 | `comprehensive_analysis()` |
| POST | `/api/v1/process-mining/detect-deviations/{process_id}` | platform-services | platform-services/мониторинг/process-analytics/main.py:948 | `detect_deviations()` |
| POST | `/api/v1/process-mining/discover-patterns/{process_id}` | platform-services | platform-services/мониторинг/process-analytics/main.py:937 | `discover_patterns()` |
| GET | `/api/v1/process-mining/health` | platform-services | platform-services/мониторинг/process-analytics/main.py:1015 | `health_check()` |
| POST | `/api/v1/process-mining/log-event` | platform-services | platform-services/мониторинг/process-analytics/main.py:890 | `log_process_event()` |
| POST | `/api/v1/process-mining/log-execution` | platform-services | platform-services/мониторинг/process-analytics/main.py:856 | `log_process_execution()` |
| GET | `/api/v1/process-mining/processes/{process_id}/summary` | platform-services | platform-services/мониторинг/process-analytics/main.py:1025 | `get_process_summary()` |
| GET | `/api/v1/scenarios/status` | platform-services | platform-services/simulation/simulation/simulation/scenario_orchestrator/main.py:564 | `scenarios_status()` |
| GET | `/api/v1/scenarios/status` | platform-services | platform-services/simulation/scenarios/scenario_orchestrator/main.py:564 | `scenarios_status()` |
| GET | `/api/v1/stats` | platform-services | platform-services/bcm-coordination-service/main.py:230 | `get_stats()` |
| POST | `/api/webhooks/thehive` | platform-services | platform-services/simulation/simulation/thehive/thehive/app.py:274 | `thehive_webhook()` |
| POST | `/approvals/{approval_id}/respond` | platform-services | platform-services/documents-service/api/routes.py:387 | `respond_to_approval_endpoint()` |
| POST | `/approve` | platform-services | platform-services/planning_service/api/bulk_operations.py:203 | `bulk_approve_strategies()` |
| POST | `/articles` | platform-services | platform-services/community-service/portal/api/knowledge.py:38 | `create_article()` |
| GET | `/articles` | platform-services | platform-services/community-service/portal/api/knowledge.py:67 | `get_articles()` |
| GET | `/articles/{article_id}` | platform-services | platform-services/community-service/portal/api/knowledge.py:152 | `get_article()` |
| PATCH | `/articles/{article_id}` | platform-services | platform-services/community-service/portal/api/knowledge.py:213 | `update_article()` |
| POST | `/articles/{article_id}/bookmark` | platform-services | platform-services/community-service/portal/api/knowledge.py:311 | `bookmark_article()` |
| DELETE | `/articles/{article_id}/bookmark` | platform-services | platform-services/community-service/portal/api/knowledge.py:335 | `remove_bookmark()` |
| POST | `/articles/{article_id}/discuss` | platform-services | platform-services/community-service/portal/api/knowledge.py:551 | `create_article_discussion()` |
| GET | `/articles/{article_id}/discussion` | platform-services | platform-services/community-service/portal/api/knowledge.py:618 | `get_article_discussion()` |
| POST | `/articles/{article_id}/verify` | platform-services | platform-services/community-service/portal/api/knowledge.py:511 | `verify_article()` |
| POST | `/articles/{article_id}/vote` | platform-services | platform-services/community-service/portal/api/knowledge.py:256 | `vote_article()` |
| DELETE | `/articles/{article_id}/vote` | platform-services | platform-services/community-service/portal/api/knowledge.py:289 | `remove_vote()` |
| POST | `/assessments` | platform-services | platform-services/risk-service/api/routes.py:49 | `create_risk()` |
| GET | `/assessments` | platform-services | platform-services/risk-service/api/routes.py:68 | `list_risks()` |
| GET | `/assessments/{risk_id}` | platform-services | platform-services/risk-service/api/routes.py:101 | `get_risk()` |
| PUT | `/assessments/{risk_id}` | platform-services | platform-services/risk-service/api/routes.py:119 | `update_risk()` |
| DELETE | `/assessments/{risk_id}` | platform-services | platform-services/risk-service/api/routes.py:138 | `delete_risk()` |
| POST | `/assessments/{risk_id}/fair-analysis` | platform-services | platform-services/risk-service/api/routes.py:159 | `perform_fair_analysis()` |
| GET | `/assessments/{risk_id}/fair-analysis` | platform-services | platform-services/risk-service/api/routes.py:180 | `get_fair_analysis()` |
| GET | `/assessments/{risk_id}/matrix-position` | platform-services | platform-services/risk-service/api/routes.py:324 | `get_risk_matrix_position()` |
| POST | `/assessments/{risk_id}/monte-carlo` | platform-services | platform-services/risk-service/api/routes.py:198 | `run_monte_carlo_simulation()` |
| GET | `/assessments/{risk_id}/monte-carlo` | platform-services | platform-services/risk-service/api/routes.py:219 | `get_monte_carlo_results()` |
| POST | `/assessments/{risk_id}/treatment-plans` | platform-services | platform-services/risk-service/api/routes.py:241 | `create_treatment_plan()` |
| GET | `/assessments/{risk_id}/treatment-plans` | platform-services | platform-services/risk-service/api/routes.py:263 | `list_treatment_plans()` |
| POST | `/audits` | platform-services | platform-services/validation-service/api/routes.py:515 | `create_audit()` |
| GET | `/audits` | platform-services | platform-services/validation-service/api/routes.py:530 | `list_audits()` |
| GET | `/audits` | platform-services | platform-services/compliance-service/api/audit.py:232 | `list_audits()` |
| GET | `/audits/findings-analysis` | platform-services | platform-services/validation-service/api/workflow_ai.py:384 | `analyze_audit_findings()` |
| GET | `/audits/{audit_id}` | platform-services | platform-services/validation-service/api/routes.py:549 | `get_audit()` |
| PATCH | `/audits/{audit_id}/close` | platform-services | platform-services/validation-service/api/routes.py:596 | `close_audit()` |
| POST | `/audits/{audit_id}/findings` | platform-services | platform-services/validation-service/api/routes.py:567 | `add_finding()` |
| GET | `/audits/{audit_id}/report` | platform-services | platform-services/validation-service/api/routes.py:582 | `get_audit_report()` |
| POST | `/auth/token` | platform-services | platform-services/governance-service/main.py:255 | `login()` |
| POST | `/auth/token` | platform-services | platform-services/learning-service/main.py:262 | `login()` |
| POST | `/automation/auto-register-services` | platform-services | platform-services/мониторинг/compliance-monitoring/main.py:845 | `automation_auto_register()` |
| GET | `/automation/code-complexity/{service_name}` | platform-services | platform-services/мониторинг/compliance-monitoring/main.py:893 | `automation_code_complexity()` |
| GET | `/automation/dependencies/{service_name}` | platform-services | platform-services/мониторинг/compliance-monitoring/main.py:857 | `automation_get_dependencies()` |
| POST | `/automation/discover-services` | platform-services | platform-services/мониторинг/compliance-monitoring/main.py:833 | `automation_discover_services()` |
| GET | `/automation/metrics` | platform-services | platform-services/мониторинг/compliance-monitoring/main.py:905 | `automation_prometheus_metrics()` |
| POST | `/automation/root-cause/{failed_service}` | platform-services | platform-services/мониторинг/compliance-monitoring/main.py:869 | `automation_find_root_cause()` |
| POST | `/automation/security-scan` | platform-services | platform-services/мониторинг/compliance-monitoring/main.py:881 | `automation_security_scan()` |
| GET | `/badges` | platform-services | platform-services/community-service/portal/api/forum.py:694 | `get_badges()` |
| POST | `/batch-ai-scan` | platform-services | platform-services/compliance-service/api/assessments.py:429 | `batch_ai_assessment()` |
| GET | `/bci/practices` | platform-services | platform-services/compliance-service/api/knowledge_base.py:180 | `get_bci_practices()` |
| GET | `/benchmarks` | platform-services | platform-services/compliance-service/api/workflow_ai.py:73 | `get_benchmarks()` |
| GET | `/benchmarks` | platform-services | platform-services/governance-service/api/workflow_ai.py:73 | `get_benchmarks()` |
| GET | `/benchmarks` | platform-services | platform-services/plans_service/api/workflow_ai.py:73 | `get_benchmarks()` |
| GET | `/benchmarks` | platform-services | platform-services/planning_service/api/workflow_ai.py:163 | `get_planning_benchmarks()` |
| GET | `/benchmarks` | platform-services | platform-services/learning-service/api/workflow_ai.py:73 | `get_benchmarks()` |
| GET | `/benchmarks` | platform-services | platform-services/bia-service/api/workflow_ai.py:73 | `get_benchmarks()` |
| GET | `/benchmarks` | platform-services | platform-services/documents-service/api/workflow_ai.py:73 | `get_benchmarks()` |
| GET | `/benchmarks/{metric_name}` | platform-services | platform-services/governance-service/services/domain_intelligence_service.py:273 | `get_industry_benchmark()` |
| GET | `/best-practices` | platform-services | platform-services/compliance-service/api/library.py:302 | `get_best_practices()` |
| POST | `/bia/analyze/{twin_id}` | platform-services | platform-services/simulation/digital-twin/api/routers/integrations.py:101 | `analyze_with_bia_engine()` |
| GET | `/bia/status/{twin_id}` | platform-services | platform-services/simulation/digital-twin/api/routers/integrations.py:220 | `get_bia_analysis_status()` |
| GET | `/bookmarks` | platform-services | platform-services/community-service/portal/api/knowledge.py:353 | `get_my_bookmarks()` |
| POST | `/capa` | platform-services | platform-services/validation-service/api/routes.py:612 | `create_capa()` |
| GET | `/capa` | platform-services | platform-services/validation-service/api/routes.py:645 | `list_capa()` |
| GET | `/capa/effectiveness` | platform-services | platform-services/validation-service/api/workflow_ai.py:427 | `analyze_capa_effectiveness()` |
| GET | `/capa/{capa_id}` | platform-services | platform-services/validation-service/api/routes.py:668 | `get_capa()` |
| PATCH | `/capa/{capa_id}` | platform-services | platform-services/validation-service/api/routes.py:684 | `update_capa()` |
| POST | `/capa/{capa_id}/verify` | platform-services | platform-services/validation-service/api/routes.py:705 | `verify_capa()` |
| GET | `/case-studies` | platform-services | platform-services/compliance-service/api/library.py:378 | `get_case_studies()` |
| GET | `/cases/search` | platform-services | platform-services/validation-service/api/workflow_ai.py:129 | `search_cases()` |
| GET | `/cases/search` | platform-services | platform-services/risk-service/api/workflow_ai.py:119 | `search_cases()` |
| GET | `/cases/search` | platform-services | platform-services/response-service/api/workflow_ai.py:119 | `search_cases()` |
| GET | `/cases/{case_id}/similar` | platform-services | platform-services/validation-service/api/workflow_ai.py:186 | `find_similar_cases()` |
| GET | `/cases/{case_id}/similar` | platform-services | platform-services/risk-service/api/workflow_ai.py:169 | `find_similar_cases()` |
| GET | `/cases/{case_id}/similar` | platform-services | platform-services/response-service/api/workflow_ai.py:169 | `find_similar_cases()` |
| GET | `/cases/{case_id}/timeline` | platform-services | platform-services/validation-service/api/workflow_ai.py:214 | `get_case_timeline()` |
| GET | `/cases/{case_id}/timeline` | platform-services | platform-services/risk-service/api/workflow_ai.py:197 | `get_case_timeline()` |
| GET | `/cases/{case_id}/timeline` | platform-services | platform-services/response-service/api/workflow_ai.py:197 | `get_case_timeline()` |
| GET | `/categories` | platform-services | platform-services/community-service/portal/api/forum.py:37 | `get_categories()` |
| GET | `/categories/available` | platform-services | platform-services/simulation/digital-twin/api/routers/scenarios.py:407 | `get_available_categories()` |
| GET | `/certifications/expiring` | platform-services | platform-services/learning-service/api/analytics.py:613 | `get_expiring_certifications()` |
| POST | `/communication-plans` | platform-services | platform-services/governance-service/api/routes.py:1050 | `create_communication_plan()` |
| GET | `/communication-plans` | platform-services | platform-services/governance-service/api/routes.py:1082 | `list_communication_plans()` |
| POST | `/competence` | platform-services | platform-services/governance-service/api/routes.py:809 | `create_competence_record()` |
| GET | `/competence` | platform-services | platform-services/governance-service/api/routes.py:869 | `list_competence()` |
| GET | `/compliance/alerts` | platform-services | platform-services/мониторинг/compliance-monitoring/main.py:595 | `get_compliance_alerts()` |
| POST | `/compliance/alerts` | platform-services | platform-services/мониторинг/compliance-monitoring/main.py:617 | `create_compliance_alert()` |
| PUT | `/compliance/alerts/{alert_id}/acknowledge` | platform-services | platform-services/мониторинг/compliance-monitoring/main.py:623 | `acknowledge_compliance_alert()` |
| PUT | `/compliance/alerts/{alert_id}/resolve` | platform-services | platform-services/мониторинг/compliance-monitoring/main.py:633 | `resolve_compliance_alert()` |
| GET | `/compliance/audit-requirements` | platform-services | platform-services/мониторинг/compliance-monitoring/main.py:707 | `get_audit_requirements()` |
| POST | `/compliance/audit-requirements` | platform-services | platform-services/мониторинг/compliance-monitoring/main.py:725 | `create_audit_requirement()` |
| GET | `/compliance/iso-clauses` | platform-services | platform-services/мониторинг/compliance-monitoring/main.py:567 | `get_iso_clause_coverage()` |
| POST | `/compliance/metrics` | platform-services | platform-services/мониторинг/compliance-monitoring/main.py:734 | `ingest_compliance_metrics()` |
| GET | `/compliance/metrics/{service}` | platform-services | platform-services/мониторинг/compliance-monitoring/main.py:740 | `get_service_compliance_metrics()` |
| GET | `/compliance/nonconformities` | platform-services | platform-services/мониторинг/compliance-monitoring/main.py:649 | `get_nonconformities()` |
| POST | `/compliance/nonconformities` | platform-services | platform-services/мониторинг/compliance-monitoring/main.py:671 | `create_nonconformity()` |
| PUT | `/compliance/nonconformities/{nonconformity_id}` | platform-services | platform-services/мониторинг/compliance-monitoring/main.py:677 | `update_nonconformity()` |
| GET | `/compliance/services` | platform-services | platform-services/мониторинг/compliance-monitoring/main.py:587 | `get_compliance_services()` |
| GET | `/compliance/status` | platform-services | platform-services/мониторинг/compliance-monitoring/main.py:510 | `get_compliance_status()` |
| POST | `/compute` | platform-services | platform-services/simulation/simulation/simulation/bia_engine/app.py:361 | `compute_comprehensive_bia()` |
| POST | `/compute` | platform-services | platform-services/simulation/simulation/simulation/bia_engine_O/app.py:361 | `compute_comprehensive_bia()` |
| POST | `/contact-lists` | platform-services | platform-services/plans_service/api/routes.py:270 | `create_contact_list()` |
| GET | `/contact-lists` | platform-services | platform-services/plans_service/api/routes.py:280 | `list_contact_lists()` |
| POST | `/context-analysis` | platform-services | platform-services/governance-service/api/routes.py:1330 | `create_context_analysis()` |
| GET | `/context-analysis` | platform-services | platform-services/governance-service/api/routes.py:1369 | `list_context_analyses()` |
| GET | `/context-analysis/{analysis_id}` | platform-services | platform-services/governance-service/api/routes.py:1395 | `get_context_analysis()` |
| POST | `/corrective-actions/bulk` | platform-services | platform-services/compliance-service/api/bulk_operations.py:284 | `bulk_create_corrective_actions()` |
| POST | `/cost-benefit` | platform-services | platform-services/planning_service/api/bulk_operations.py:117 | `bulk_calculate_cost_benefit()` |
| POST | `/critical-incidents` | platform-services | platform-services/response-service/auth/dependencies.py:172 | `create_critical_incident()` |
| POST | `/critical-risks` | platform-services | platform-services/risk-service/auth/dependencies.py:172 | `create_critical_risk()` |
| POST | `/csv` | platform-services | platform-services/simulation/digital-twin/api/routers/import_data.py:146 | `import_csv()` |
| GET | `/dashboard` | platform-services | platform-services/мониторинг/compliance-monitoring/main.py:1060 | `get_compliance_dashboard()` |
| GET | `/dashboard` | platform-services | platform-services/response-service/api/routes.py:669 | `get_incident_dashboard()` |
| GET | `/dashboard/{twin_id}` | platform-services | platform-services/simulation/digital-twin/api/routers/metrics.py:472 | `get_metrics_dashboard()` |
| GET | `/departments/metrics` | platform-services | platform-services/learning-service/api/analytics.py:352 | `get_department_metrics()` |
| DELETE | `/deregister-service/{service_name}` | platform-services | platform-services/мониторинг/compliance-monitoring/main.py:803 | `deregister_service()` |
| POST | `/disruptions` | platform-services | platform-services/bia-service/supply_chain_api.py:382 | `record_supplier_disruption()` |
| POST | `/documents` | platform-services | platform-services/documents-service/api/routes.py:70 | `create_document()` |
| GET | `/documents` | platform-services | platform-services/documents-service/api/routes.py:150 | `list_documents()` |
| POST | `/documents/compare` | platform-services | platform-services/documents-service/api/routes.py:295 | `compare_documents_endpoint()` |
| GET | `/documents/{document_id}` | platform-services | platform-services/documents-service/api/routes.py:112 | `get_document()` |
| PATCH | `/documents/{document_id}` | platform-services | platform-services/documents-service/api/routes.py:181 | `update_document()` |
| DELETE | `/documents/{document_id}` | platform-services | platform-services/documents-service/api/routes.py:196 | `delete_document()` |
| GET | `/documents/{document_id}/access-log` | platform-services | platform-services/documents-service/api/routes.py:510 | `get_document_access_log_endpoint()` |
| POST | `/documents/{document_id}/approvals` | platform-services | platform-services/documents-service/api/routes.py:363 | `request_approval_endpoint()` |
| GET | `/documents/{document_id}/approvals` | platform-services | platform-services/documents-service/api/routes.py:410 | `get_document_approvals_endpoint()` |
| GET | `/documents/{document_id}/download` | platform-services | platform-services/documents-service/api/routes.py:126 | `download_document()` |
| GET | `/documents/{document_id}/retention` | platform-services | platform-services/documents-service/api/routes.py:463 | `get_document_retention_status_endpoint()` |
| POST | `/documents/{document_id}/share` | platform-services | platform-services/documents-service/api/routes.py:320 | `share_document_endpoint()` |
| GET | `/documents/{document_id}/shares` | platform-services | platform-services/documents-service/api/routes.py:346 | `get_document_shares_endpoint()` |
| POST | `/documents/{document_id}/upload` | platform-services | platform-services/documents-service/api/routes.py:80 | `upload_document_file()` |
| POST | `/documents/{document_id}/version` | platform-services | platform-services/documents-service/api/routes.py:259 | `create_new_version()` |
| GET | `/documents/{document_id}/versions` | platform-services | platform-services/documents-service/api/routes.py:278 | `get_document_versions_endpoint()` |
| GET | `/documents/{document_id}/workflow/status` | platform-services | platform-services/documents-service/api/routes.py:240 | `get_workflow_status_endpoint()` |
| POST | `/documents/{document_id}/workflow/{action}` | platform-services | platform-services/documents-service/api/routes.py:215 | `execute_workflow_action_endpoint()` |
| GET | `/endpoint` | platform-services | platform-services/community-service/shared/database/connection.py:89 | `endpoint()` |
| GET | `/engines` | platform-services | platform-services/simulation/simulation/api/simulation_router.py:152 | `list_engines()` |
| GET | `/engines` | platform-services | platform-services/community-service/portal/api/simulation_router.py:152 | `list_engines()` |
| POST | `/enrollments` | platform-services | platform-services/learning-service/api/routes.py:165 | `create_enrollment()` |
| GET | `/enrollments/{enrollment_id}` | platform-services | platform-services/learning-service/api/routes.py:199 | `get_enrollment()` |
| POST | `/enrollments/{enrollment_id}/approve` | platform-services | platform-services/learning-service/api/routes.py:239 | `approve_enrollment()` |
| POST | `/enrollments/{enrollment_id}/assess` | platform-services | platform-services/learning-service/api/routes.py:331 | `submit_assessment()` |
| POST | `/enrollments/{enrollment_id}/certify` | platform-services | platform-services/learning-service/api/routes.py:362 | `issue_certification()` |
| POST | `/enrollments/{enrollment_id}/complete` | platform-services | platform-services/learning-service/api/routes.py:296 | `complete_training()` |
| PATCH | `/enrollments/{enrollment_id}/progress` | platform-services | platform-services/learning-service/api/routes.py:280 | `update_progress()` |
| POST | `/enrollments/{enrollment_id}/start` | platform-services | platform-services/learning-service/api/routes.py:255 | `start_training()` |
| POST | `/enrollments/{enrollment_id}/submit` | platform-services | platform-services/learning-service/api/routes.py:214 | `submit_enrollment()` |
| POST | `/evidence/bulk` | platform-services | platform-services/compliance-service/api/bulk_operations.py:203 | `bulk_upload_evidence()` |
| POST | `/examples/generate` | platform-services | platform-services/living-docs/api/documentation.py:99 | `generate_example()` |
| POST | `/exercises` | platform-services | platform-services/validation-service/api/routes.py:107 | `create_exercise()` |
| GET | `/exercises` | platform-services | platform-services/validation-service/api/routes.py:138 | `list_exercises()` |
| GET | `/exercises/effectiveness` | platform-services | platform-services/validation-service/api/workflow_ai.py:341 | `analyze_exercise_effectiveness()` |
| POST | `/exercises/schedule` | platform-services | platform-services/plans_service/api/bulk_operations.py:235 | `bulk_schedule_exercises()` |
| GET | `/exercises/{exercise_id}` | platform-services | platform-services/validation-service/api/routes.py:156 | `get_exercise()` |
| POST | `/exercises/{exercise_id}/complete` | platform-services | platform-services/validation-service/api/routes.py:190 | `complete_exercise()` |
| POST | `/exercises/{exercise_id}/observations` | platform-services | platform-services/validation-service/api/routes.py:209 | `add_observation()` |
| GET | `/exercises/{exercise_id}/report` | platform-services | platform-services/validation-service/api/routes.py:236 | `get_exercise_report()` |
| POST | `/exercises/{exercise_id}/start` | platform-services | platform-services/validation-service/api/routes.py:171 | `start_exercise()` |
| GET | `/featured/popular` | platform-services | platform-services/community-service/portal/api/scenarios.py:206 | `get_popular_scenarios()` |
| POST | `/feedback` | platform-services | platform-services/living-docs/api/documentation.py:168 | `submit_feedback()` |
| POST | `/files/` | platform-services | platform-services/simulation/digital-twin/venv/lib/python3.9/site-packages/fastapi/datastructures.py:53 | `create_file()` |
| GET | `/gamification/metrics` | platform-services | platform-services/learning-service/api/analytics.py:673 | `get_gamification_metrics()` |
| GET | `/gaps` | platform-services | platform-services/living-docs/api/documentation.py:330 | `get_knowledge_gaps()` |
| POST | `/generate` | platform-services | platform-services/simulation/simulation/simulation/scenario_orchestrator/app/api/v1/endpoints/scenarios.py:50 | `generate_scenario()` |
| POST | `/generate` | platform-services | platform-services/simulation/simulation/simulation/scenario_orchestrator/src/api/v1/endpoints/scenarios.py:50 | `generate_scenario()` |
| POST | `/generate` | platform-services | platform-services/simulation/scenarios/scenario_orchestrator/app/api/v1/endpoints/scenarios.py:50 | `generate_scenario()` |
| POST | `/generate` | platform-services | platform-services/simulation/scenarios/scenario_orchestrator/src/api/v1/endpoints/scenarios.py:50 | `generate_scenario()` |
| GET | `/guides` | platform-services | platform-services/compliance-service/api/library.py:20 | `list_implementation_guides()` |
| GET | `/guides/{guide_id}` | platform-services | platform-services/compliance-service/api/library.py:97 | `get_guide_detail()` |
| GET | `/health` | platform-services | platform-services/validation-service/main.py:301 | `health_check()` |
| GET | `/health` | platform-services | platform-services/validation-service/api/workflow_ai.py:470 | `workflow_health_check()` |
| GET | `/health` | platform-services | platform-services/compliance-service/main.py:560 | `health_check()` |
| GET | `/health` | platform-services | platform-services/compliance-service/api/health.py:17 | `health_check()` |
| GET | `/health` | platform-services | platform-services/compliance-service/api/modules.py:211 | `get_modules_health()` |
| GET | `/health` | platform-services | platform-services/governance-service/main.py:212 | `health_check()` |
| GET | `/health` | platform-services | platform-services/plans_service/main.py:447 | `health_check()` |
| GET | `/health` | platform-services | platform-services/plans_service/api/health.py:105 | `health_check()` |
| GET | `/health` | platform-services | platform-services/мониторинг/compliance-monitoring/main.py:497 | `health_check()` |
| GET | `/health` | platform-services | platform-services/planning_service/main.py:401 | `health_check()` |
| GET | `/health` | platform-services | platform-services/planning_service/api/health.py:106 | `health_check()` |
| GET | `/health` | platform-services | platform-services/living-docs/main.py:271 | `health_check()` |
| GET | `/health` | platform-services | platform-services/risk-service/main.py:199 | `health_check()` |
| GET | `/health` | platform-services | platform-services/risk-service/api/workflow_ai.py:316 | `workflow_health_check()` |
| GET | `/health` | platform-services | platform-services/simulation/simulation/main.py:71 | `health_check()` |
| GET | `/health` | platform-services | platform-services/simulation/simulation/thehive/bridge_service.py:130 | `health_check()` |
| GET | `/health` | platform-services | platform-services/simulation/simulation/thehive/thehive_adapter.py:502 | `health()` |
| GET | `/health` | platform-services | platform-services/simulation/simulation/thehive/thehive/app.py:80 | `health_check()` |
| GET | `/health` | platform-services | platform-services/simulation/simulation/thehive/thehive_adapter/main.py:454 | `health_check()` |
| GET | `/health` | platform-services | platform-services/simulation/simulation/simulation2/simple_app.py:29 | `health_check()` |
| GET | `/health` | platform-services | platform-services/simulation/simulation/simulation2/app.py:83 | `health_check()` |
| GET | `/health` | platform-services | platform-services/simulation/simulation/simulation/bia_engine/app.py:346 | `health()` |
| GET | `/health` | platform-services | platform-services/simulation/simulation/simulation/bia_engine_O/app.py:346 | `health()` |
| GET | `/health` | platform-services | platform-services/simulation/simulation/simulation/exercise_simulators/bridge_service.py:180 | `health_check()` |
| GET | `/health` | platform-services | platform-services/simulation/simulation/simulation/simulation/sim_adapter.py:537 | `health()` |
| GET | `/health` | platform-services | platform-services/simulation/simulation/simulation/scenario_orchestrator/main.py:537 | `health_check()` |
| GET | `/health` | platform-services | platform-services/simulation/scenarios/scenario_orchestrator/main.py:537 | `health_check()` |
| POST | `/health` | platform-services | platform-services/simulation/digital-twin/api/routers/metrics.py:215 | `create_health_score()` |
| GET | `/health` | platform-services | platform-services/simulation/digital-twin/api/routers/health.py:42 | `health_check()` |
| GET | `/health` | platform-services | platform-services/simulation/digital-twin/api/routers/integrations.py:408 | `check_integrations_health()` |
| GET | `/health` | platform-services | platform-services/shared/USAGE_EXAMPLE.py:60 | `health_check()` |
| GET | `/health` | platform-services | platform-services/community-service/portal/main.py:124 | `health_check()` |
| GET | `/health` | platform-services | platform-services/community-service/marketplace/main.py:130 | `health_check()` |
| GET | `/health` | platform-services | platform-services/response-service/main.py:352 | `health_check()` |
| GET | `/health` | platform-services | platform-services/response-service/api/workflow_ai.py:359 | `workflow_health_check()` |
| GET | `/health` | platform-services | platform-services/response-service/api/routes.py:735 | `health_check()` |
| GET | `/health` | platform-services | platform-services/learning-service/main.py:218 | `health_check()` |
| GET | `/health` | platform-services | platform-services/bia-service/main.py:390 | `health_check()` |
| GET | `/health` | platform-services | platform-services/documents-service/main.py:311 | `health_check()` |
| GET | `/health` | platform-services | platform-services/bcm-coordination-service/main.py:142 | `health_check()` |
| GET | `/health/database` | platform-services | platform-services/shared/USAGE_EXAMPLE.py:99 | `database_health()` |
| GET | `/health/detailed` | platform-services | platform-services/plans_service/api/health.py:119 | `detailed_health_check()` |
| GET | `/health/detailed` | platform-services | platform-services/planning_service/api/health.py:120 | `detailed_health_check()` |
| GET | `/health/info` | platform-services | platform-services/compliance-service/api/health.py:63 | `service_info()` |
| GET | `/health/live` | platform-services | platform-services/plans_service/api/health.py:186 | `liveness_check()` |
| GET | `/health/live` | platform-services | platform-services/planning_service/api/health.py:187 | `liveness_check()` |
| GET | `/health/ready` | platform-services | platform-services/compliance-service/api/health.py:33 | `readiness_check()` |
| GET | `/health/ready` | platform-services | platform-services/plans_service/api/health.py:160 | `readiness_check()` |
| GET | `/health/ready` | platform-services | platform-services/planning_service/api/health.py:161 | `readiness_check()` |
| GET | `/health/simple` | platform-services | platform-services/shared/USAGE_EXAMPLE.py:86 | `simple_health()` |
| GET | `/health/{service_name}` | platform-services | platform-services/compliance-service/api/modules.py:316 | `get_service_health()` |
| GET | `/health/{twin_id}` | platform-services | platform-services/simulation/digital-twin/api/routers/metrics.py:257 | `get_health_scores()` |
| GET | `/health/{twin_id}/latest` | platform-services | platform-services/simulation/digital-twin/api/routers/metrics.py:307 | `get_latest_health_score()` |
| GET | `/hub/catalog` | platform-services | platform-services/simulation/simulation/simulation/scenario_orchestrator/app/api/v1/endpoints/scenarios.py:332 | `get_scenario_catalog()` |
| GET | `/hub/catalog` | platform-services | platform-services/simulation/simulation/simulation/scenario_orchestrator/src/api/v1/endpoints/scenarios.py:332 | `get_scenario_catalog()` |
| GET | `/hub/catalog` | platform-services | platform-services/simulation/scenarios/scenario_orchestrator/app/api/v1/endpoints/scenarios.py:332 | `get_scenario_catalog()` |
| GET | `/hub/catalog` | platform-services | platform-services/simulation/scenarios/scenario_orchestrator/src/api/v1/endpoints/scenarios.py:332 | `get_scenario_catalog()` |
| POST | `/hub/submit` | platform-services | platform-services/simulation/simulation/simulation/scenario_orchestrator/app/api/v1/endpoints/scenarios.py:391 | `submit_scenario_to_hub()` |
| POST | `/hub/submit` | platform-services | platform-services/simulation/simulation/simulation/scenario_orchestrator/src/api/v1/endpoints/scenarios.py:391 | `submit_scenario_to_hub()` |
| POST | `/hub/submit` | platform-services | platform-services/simulation/scenarios/scenario_orchestrator/app/api/v1/endpoints/scenarios.py:391 | `submit_scenario_to_hub()` |
| POST | `/hub/submit` | platform-services | platform-services/simulation/scenarios/scenario_orchestrator/src/api/v1/endpoints/scenarios.py:391 | `submit_scenario_to_hub()` |
| POST | `/improvements` | platform-services | platform-services/compliance-service/api/improvements.py:40 | `create_improvement_initiative()` |
| GET | `/improvements` | platform-services | platform-services/compliance-service/api/improvements.py:105 | `list_improvement_initiatives()` |
| GET | `/improvements` | platform-services | platform-services/living-docs/api/documentation.py:391 | `get_improvement_queue()` |
| GET | `/improvements/dashboard` | platform-services | platform-services/compliance-service/api/improvements.py:291 | `get_improvements_dashboard()` |
| GET | `/improvements/roi-analysis` | platform-services | platform-services/compliance-service/api/improvements.py:333 | `analyze_improvements_roi()` |
| GET | `/improvements/{initiative_id}` | platform-services | platform-services/compliance-service/api/improvements.py:137 | `get_improvement_initiative()` |
| PATCH | `/improvements/{initiative_id}` | platform-services | platform-services/compliance-service/api/improvements.py:161 | `update_improvement_initiative()` |
| PATCH | `/improvements/{initiative_id}/progress` | platform-services | platform-services/compliance-service/api/improvements.py:195 | `update_initiative_progress()` |
| POST | `/improvements/{initiative_id}/verify` | platform-services | platform-services/compliance-service/api/improvements.py:236 | `verify_improvement()` |
| GET | `/incidents` | platform-services | platform-services/response-service/auth/dependencies.py:53 | `list_incidents()` |
| POST | `/incidents` | platform-services | platform-services/response-service/api/routes.py:64 | `create_incident()` |
| GET | `/incidents` | platform-services | platform-services/response-service/api/routes.py:99 | `list_incidents()` |
| GET | `/incidents/{incident_id}` | platform-services | platform-services/response-service/api/routes.py:139 | `get_incident()` |
| PUT | `/incidents/{incident_id}` | platform-services | platform-services/response-service/api/routes.py:163 | `update_incident()` |
| POST | `/incidents/{incident_id}/actions` | platform-services | platform-services/response-service/api/routes.py:314 | `add_response_action()` |
| GET | `/incidents/{incident_id}/actions` | platform-services | platform-services/response-service/api/routes.py:342 | `list_incident_actions()` |
| POST | `/incidents/{incident_id}/communications` | platform-services | platform-services/response-service/api/routes.py:496 | `log_communication()` |
| GET | `/incidents/{incident_id}/communications` | platform-services | platform-services/response-service/api/routes.py:526 | `list_incident_communications()` |
| POST | `/incidents/{incident_id}/escalate` | platform-services | platform-services/response-service/api/routes.py:275 | `escalate_incident()` |
| POST | `/incidents/{incident_id}/metrics` | platform-services | platform-services/response-service/api/routes.py:564 | `add_recovery_metrics()` |
| GET | `/incidents/{incident_id}/metrics` | platform-services | platform-services/response-service/api/routes.py:617 | `get_incident_metrics()` |
| GET | `/incidents/{incident_id}/report` | platform-services | platform-services/response-service/api/routes.py:636 | `generate_incident_report()` |
| POST | `/incidents/{incident_id}/resolve` | platform-services | platform-services/response-service/api/routes.py:238 | `resolve_incident()` |
| PATCH | `/incidents/{incident_id}/status` | platform-services | platform-services/response-service/api/routes.py:201 | `change_incident_status()` |
| POST | `/incidents/{incident_id}/team` | platform-services | platform-services/response-service/api/routes.py:389 | `assign_response_team()` |
| GET | `/incidents/{incident_id}/team` | platform-services | platform-services/response-service/api/routes.py:424 | `get_incident_team()` |
| GET | `/incidents/{incident_id}/timeline` | platform-services | platform-services/response-service/api/routes.py:545 | `get_incident_timeline()` |
| GET | `/industries` | platform-services | platform-services/governance-service/services/domain_intelligence_service.py:444 | `list_available_industries()` |
| GET | `/insights` | platform-services | platform-services/validation-service/api/workflow_ai.py:49 | `get_workflow_insights()` |
| GET | `/insights` | platform-services | platform-services/risk-service/api/workflow_ai.py:44 | `get_workflow_insights()` |
| GET | `/insights` | platform-services | platform-services/response-service/api/workflow_ai.py:44 | `get_workflow_insights()` |
| GET | `/iso-coverage` | platform-services | platform-services/documents-service/api/routes.py:497 | `get_iso_coverage()` |
| GET | `/iso22301/clauses` | platform-services | platform-services/compliance-service/api/knowledge_base.py:67 | `get_iso22301_clauses()` |
| GET | `/iso22301/{clause}` | platform-services | platform-services/compliance-service/api/knowledge_base.py:134 | `get_iso22301_clause_detail()` |
| GET | `/items` | platform-services | platform-services/compliance-service/database/connection.py:43 | `get_items()` |
| GET | `/items/` | platform-services | platform-services/simulation/digital-twin/venv/lib/python3.9/site-packages/fastapi/applications.py:239 | `unknown()` |
| POST | `/items/` | platform-services | platform-services/simulation/digital-twin/venv/lib/python3.9/site-packages/fastapi/applications.py:2610 | `create_item()` |
| PATCH | `/items/` | platform-services | platform-services/simulation/digital-twin/venv/lib/python3.9/site-packages/fastapi/applications.py:4107 | `update_item()` |
| GET | `/items/` | platform-services | platform-services/simulation/digital-twin/venv/lib/python3.9/site-packages/fastapi/routing.py:1632 | `read_items()` |
| POST | `/items/` | platform-services | platform-services/simulation/digital-twin/venv/lib/python3.9/site-packages/fastapi/routing.py:2396 | `create_item()` |
| PATCH | `/items/` | platform-services | platform-services/simulation/digital-twin/venv/lib/python3.9/site-packages/fastapi/routing.py:3914 | `update_item()` |
| GET | `/items/` | platform-services | platform-services/simulation/digital-twin/venv/lib/python3.9/site-packages/fastapi/param_functions.py:2272 | `read_items()` |
| GET | `/items/` | platform-services | platform-services/simulation/digital-twin/venv/lib/python3.9/site-packages/fastapi/security/api_key.py:41 | `read_items()` |
| PUT | `/items/{item_id}` | platform-services | platform-services/simulation/digital-twin/venv/lib/python3.9/site-packages/fastapi/applications.py:2232 | `replace_item()` |
| DELETE | `/items/{item_id}` | platform-services | platform-services/simulation/digital-twin/venv/lib/python3.9/site-packages/fastapi/applications.py:2983 | `delete_item()` |
| PUT | `/items/{item_id}` | platform-services | platform-services/simulation/digital-twin/venv/lib/python3.9/site-packages/fastapi/routing.py:2014 | `replace_item()` |
| DELETE | `/items/{item_id}` | platform-services | platform-services/simulation/digital-twin/venv/lib/python3.9/site-packages/fastapi/routing.py:2773 | `delete_item()` |
| GET | `/items/{item_id}` | platform-services | platform-services/simulation/digital-twin/venv/lib/python3.9/site-packages/fastapi/exceptions.py:29 | `read_item()` |
| GET | `/items/{item_id}` | platform-services | platform-services/simulation/digital-twin/venv/lib/python3.9/site-packages/fastapi/param_functions.py:299 | `read_items()` |
| GET | `/journey/{goal}` | platform-services | platform-services/living-docs/api/documentation.py:260 | `get_personalized_journey()` |
| POST | `/json` | platform-services | platform-services/simulation/digital-twin/api/routers/import_data.py:251 | `import_json()` |
| GET | `/knowledge` | platform-services | platform-services/governance-service/services/domain_intelligence_service.py:166 | `get_domain_knowledge()` |
| GET | `/kpi/alerts` | platform-services | platform-services/validation-service/api/routes.py:470 | `get_active_kpi_alerts()` |
| POST | `/kpi/alerts/{alert_id}/acknowledge` | platform-services | platform-services/validation-service/api/routes.py:486 | `acknowledge_alert()` |
| POST | `/kpi/collect-now` | platform-services | platform-services/validation-service/api/routes.py:455 | `trigger_kpi_collection()` |
| POST | `/kpis` | platform-services | platform-services/validation-service/api/routes.py:303 | `create_kpi()` |
| GET | `/kpis` | platform-services | platform-services/validation-service/api/routes.py:339 | `list_kpis()` |
| GET | `/kpis/dashboard` | platform-services | platform-services/validation-service/api/routes.py:440 | `get_kpi_dashboard()` |
| GET | `/kpis/{kpi_id}` | platform-services | platform-services/validation-service/api/routes.py:356 | `get_kpi()` |
| PATCH | `/kpis/{kpi_id}` | platform-services | platform-services/validation-service/api/routes.py:373 | `update_kpi()` |
| POST | `/kpis/{kpi_id}/measure` | platform-services | platform-services/validation-service/api/routes.py:393 | `record_measurement()` |
| GET | `/kpis/{kpi_id}/trend` | platform-services | platform-services/validation-service/api/routes.py:422 | `get_kpi_trend()` |
| GET | `/leaderboard` | platform-services | platform-services/community-service/portal/api/forum.py:661 | `get_leaderboard()` |
| GET | `/leaderboard` | platform-services | platform-services/learning-service/api/routes.py:462 | `get_leaderboard()` |
| POST | `/learn-from-exercise` | platform-services | platform-services/simulation/digital-twin/api/routers/scenarios.py:579 | `submit_learning_feedback()` |
| GET | `/learners/{person_id}/profile` | platform-services | platform-services/learning-service/api/analytics.py:450 | `get_learner_profile()` |
| GET | `/learning/dashboard` | platform-services | platform-services/simulation/simulation/simulation/scenario_orchestrator/main.py:487 | `get_learning_dashboard()` |
| GET | `/learning/dashboard` | platform-services | platform-services/simulation/scenarios/scenario_orchestrator/main.py:487 | `get_learning_dashboard()` |
| POST | `/learning/exercise-result` | platform-services | platform-services/simulation/simulation/simulation/scenario_orchestrator/main.py:281 | `collect_exercise_result()` |
| POST | `/learning/exercise-result` | platform-services | platform-services/simulation/scenarios/scenario_orchestrator/main.py:281 | `collect_exercise_result()` |
| GET | `/learning/scenario/{scenario_id}/insights` | platform-services | platform-services/simulation/simulation/simulation/scenario_orchestrator/main.py:353 | `get_scenario_learning_insights()` |
| GET | `/learning/scenario/{scenario_id}/insights` | platform-services | platform-services/simulation/scenarios/scenario_orchestrator/main.py:353 | `get_scenario_learning_insights()` |
| GET | `/library` | platform-services | platform-services/simulation/simulation/api/scenario_library_router.py:62 | `list_scenario_library()` |
| GET | `/library` | platform-services | platform-services/community-service/portal/api/scenario_library_router.py:62 | `list_scenario_library()` |
| GET | `/library/complexity-levels` | platform-services | platform-services/simulation/simulation/api/scenario_library_router.py:133 | `list_complexity_levels()` |
| GET | `/library/complexity-levels` | platform-services | platform-services/community-service/portal/api/scenario_library_router.py:133 | `list_complexity_levels()` |
| GET | `/library/stats` | platform-services | platform-services/simulation/simulation/api/scenario_library_router.py:141 | `library_stats()` |
| GET | `/library/stats` | platform-services | platform-services/community-service/portal/api/scenario_library_router.py:141 | `library_stats()` |
| GET | `/library/threat-types` | platform-services | platform-services/simulation/simulation/api/scenario_library_router.py:125 | `list_threat_types()` |
| GET | `/library/threat-types` | platform-services | platform-services/community-service/portal/api/scenario_library_router.py:125 | `list_threat_types()` |
| GET | `/library/{scenario_id}` | platform-services | platform-services/simulation/simulation/api/scenario_library_router.py:91 | `get_scenario_details()` |
| GET | `/library/{scenario_id}` | platform-services | platform-services/community-service/portal/api/scenario_library_router.py:91 | `get_scenario_details()` |
| GET | `/live` | platform-services | platform-services/response-service/main.py:433 | `liveness_check()` |
| GET | `/liveness` | platform-services | platform-services/simulation/digital-twin/api/routers/health.py:194 | `liveness_check()` |
| POST | `/login` | platform-services | platform-services/simulation/digital-twin/api/routers/auth.py:167 | `login()` |
| POST | `/login` | platform-services | platform-services/simulation/digital-twin/venv/lib/python3.9/site-packages/fastapi/security/oauth2.py:41 | `login()` |
| POST | `/logout` | platform-services | platform-services/simulation/digital-twin/api/routers/auth.py:319 | `logout()` |
| POST | `/management-reviews` | platform-services | platform-services/validation-service/api/routes.py:727 | `create_management_review()` |
| GET | `/management-reviews` | platform-services | platform-services/validation-service/api/routes.py:759 | `list_management_reviews()` |
| GET | `/management-reviews/{review_id}/prepare` | platform-services | platform-services/validation-service/api/routes.py:782 | `prepare_management_review()` |
| GET | `/mapping` | platform-services | platform-services/compliance-service/api/knowledge_base.py:321 | `get_iso_bci_platform_mapping()` |
| GET | `/me` | platform-services | platform-services/simulation/digital-twin/api/routers/auth.py:280 | `get_current_user_info()` |
| GET | `/me` | platform-services | platform-services/community-service/portal/api/organizations.py:83 | `get_my_organization()` |
| GET | `/me` | platform-services | platform-services/community-service/marketplace/api/specialists.py:135 | `get_my_specialist_profile()` |
| GET | `/metrics` | platform-services | platform-services/plans_service/api/metrics.py:121 | `metrics()` |
| GET | `/metrics` | platform-services | platform-services/planning_service/api/metrics.py:114 | `metrics()` |
| GET | `/metrics` | platform-services | platform-services/response-service/main.py:444 | `metrics()` |
| GET | `/metrics` | platform-services | platform-services/response-service/api/routes.py:703 | `get_organization_metrics()` |
| GET | `/metrics` | platform-services | platform-services/learning-service/api/analytics.py:142 | `get_training_metrics()` |
| GET | `/metrics/cache` | platform-services | platform-services/bia-service/main.py:454 | `cache_metrics()` |
| PUT | `/metrics/{metrics_id}` | platform-services | platform-services/response-service/api/routes.py:589 | `update_recovery_metrics()` |
| POST | `/moderation/flags/{flag_id}/resolve` | platform-services | platform-services/community-service/portal/api/forum.py:533 | `resolve_flag()` |
| GET | `/moderation/queue` | platform-services | platform-services/community-service/portal/api/forum.py:517 | `get_moderation_queue()` |
| POST | `/monte-carlo` | platform-services | platform-services/simulation/digital-twin/api/routers/predictions.py:488 | `run_monte_carlo_prediction()` |
| GET | `/my` | platform-services | platform-services/community-service/marketplace/api/projects.py:129 | `get_my_projects()` |
| GET | `/my/written` | platform-services | platform-services/community-service/marketplace/api/reviews.py:409 | `get_my_written_reviews()` |
| POST | `/nonconformities/bulk` | platform-services | platform-services/compliance-service/api/bulk_operations.py:103 | `bulk_import_nonconformities()` |
| POST | `/nonconformities/{nc_id}/rca/complete` | platform-services | platform-services/compliance-service/api/nonconformities.py:99 | `complete_rca_process()` |
| POST | `/nonconformities/{nc_id}/rca/start` | platform-services | platform-services/compliance-service/api/nonconformities.py:41 | `start_rca_process()` |
| POST | `/objectives` | platform-services | platform-services/governance-service/api/routes.py:900 | `create_objective()` |
| GET | `/objectives` | platform-services | platform-services/governance-service/api/routes.py:951 | `list_objectives()` |
| GET | `/objectives/{objective_id}` | platform-services | platform-services/governance-service/api/routes.py:975 | `get_objective()` |
| PATCH | `/objectives/{objective_id}` | platform-services | platform-services/governance-service/api/routes.py:997 | `update_objective()` |
| GET | `/odoo/organization/{odoo_id}` | platform-services | platform-services/simulation/digital-twin/api/routers/bridges.py:159 | `pull_odoo_organization()` |
| POST | `/odoo/push` | platform-services | platform-services/simulation/digital-twin/api/routers/bridges.py:89 | `push_to_odoo()` |
| GET | `/odoo/status` | platform-services | platform-services/simulation/digital-twin/api/routers/bridges.py:125 | `get_odoo_status()` |
| POST | `/odoo/sync` | platform-services | platform-services/simulation/digital-twin/api/routers/bridges.py:53 | `sync_from_odoo()` |
| POST | `/optimize` | platform-services | platform-services/simulation/simulation/simulation/scenario_orchestrator/app/api/v1/endpoints/scenarios.py:166 | `optimize_scenario()` |
| POST | `/optimize` | platform-services | platform-services/simulation/simulation/simulation/scenario_orchestrator/src/api/v1/endpoints/scenarios.py:166 | `optimize_scenario()` |
| POST | `/optimize` | platform-services | platform-services/simulation/scenarios/scenario_orchestrator/app/api/v1/endpoints/scenarios.py:166 | `optimize_scenario()` |
| POST | `/optimize` | platform-services | platform-services/simulation/scenarios/scenario_orchestrator/src/api/v1/endpoints/scenarios.py:166 | `optimize_scenario()` |
| POST | `/optimize/single-process` | platform-services | platform-services/simulation/simulation/simulation/bia_engine/app.py:432 | `optimize_single_process()` |
| POST | `/optimize/single-process` | platform-services | platform-services/simulation/simulation/simulation/bia_engine_O/app.py:432 | `optimize_single_process()` |
| GET | `/organization/{org_id}/summary` | platform-services | platform-services/simulation/digital-twin/api/routers/predictions.py:416 | `get_organization_predictions_summary()` |
| GET | `/organizational-types` | platform-services | platform-services/governance-service/services/domain_intelligence_service.py:533 | `get_organizational_types()` |
| GET | `/overview` | platform-services | platform-services/compliance-service/api/dashboard.py:48 | `get_compliance_overview()` |
| GET | `/persons/{person_id}/achievements` | platform-services | platform-services/learning-service/api/routes.py:425 | `get_user_achievements()` |
| GET | `/persons/{person_id}/enrollments` | platform-services | platform-services/learning-service/api/routes.py:403 | `list_person_enrollments()` |
| GET | `/persons/{person_id}/points` | platform-services | platform-services/learning-service/api/routes.py:440 | `get_user_points()` |
| GET | `/persons/{person_id}/rank` | platform-services | platform-services/learning-service/api/routes.py:483 | `get_user_rank()` |
| GET | `/ping` | platform-services | platform-services/simulation/digital-twin/api/routers/health.py:146 | `ping()` |
| POST | `/plans` | platform-services | platform-services/plans_service/api/bulk_operations.py:65 | `bulk_create_plans()` |
| POST | `/plans` | platform-services | platform-services/plans_service/api/routes.py:30 | `create_plan()` |
| GET | `/plans` | platform-services | platform-services/plans_service/api/routes.py:40 | `list_plans()` |
| GET | `/plans/{plan_id}` | platform-services | platform-services/plans_service/api/routes.py:63 | `get_plan()` |
| PUT | `/plans/{plan_id}` | platform-services | platform-services/plans_service/api/routes.py:79 | `update_plan()` |
| DELETE | `/plans/{plan_id}` | platform-services | platform-services/plans_service/api/routes.py:96 | `delete_plan()` |
| POST | `/plans/{plan_id}/activate` | platform-services | platform-services/plans_service/api/routes.py:148 | `activate_plan()` |
| POST | `/plans/{plan_id}/activate-real` | platform-services | platform-services/plans_service/api/routes.py:292 | `activate_for_incident()` |
| POST | `/plans/{plan_id}/approve` | platform-services | platform-services/plans_service/api/routes.py:128 | `approve_plan()` |
| GET | `/plans/{plan_id}/documents` | platform-services | platform-services/documents-service/api/routes.py:482 | `get_documents_for_plan()` |
| POST | `/plans/{plan_id}/procedures` | platform-services | platform-services/plans_service/api/routes.py:187 | `add_procedure()` |
| GET | `/plans/{plan_id}/procedures` | platform-services | platform-services/plans_service/api/routes.py:201 | `list_procedures()` |
| PUT | `/plans/{plan_id}/procedures/{procedure_id}` | platform-services | platform-services/plans_service/api/routes.py:211 | `update_procedure()` |
| DELETE | `/plans/{plan_id}/procedures/{procedure_id}` | platform-services | platform-services/plans_service/api/routes.py:229 | `delete_procedure()` |
| POST | `/plans/{plan_id}/resources` | platform-services | platform-services/plans_service/api/routes.py:244 | `add_resource()` |
| GET | `/plans/{plan_id}/resources` | platform-services | platform-services/plans_service/api/routes.py:258 | `list_resources()` |
| POST | `/plans/{plan_id}/reviews` | platform-services | platform-services/plans_service/api/routes.py:318 | `create_review()` |
| GET | `/plans/{plan_id}/reviews` | platform-services | platform-services/plans_service/api/routes.py:332 | `list_reviews()` |
| POST | `/plans/{plan_id}/submit-review` | platform-services | platform-services/plans_service/api/routes.py:110 | `submit_for_review()` |
| GET | `/plans/{plan_id}/workflow` | platform-services | platform-services/plans_service/api/routes.py:166 | `get_workflow_status()` |
| GET | `/playbooks/recommend` | platform-services | platform-services/response-service/api/workflow_ai.py:317 | `recommend_playbooks()` |
| POST | `/policies` | platform-services | platform-services/governance-service/api/routes.py:230 | `create_policy()` |
| GET | `/policies` | platform-services | platform-services/governance-service/api/routes.py:283 | `list_policies()` |
| GET | `/policies/{policy_id}` | platform-services | platform-services/governance-service/api/routes.py:310 | `get_policy()` |
| PATCH | `/policies/{policy_id}` | platform-services | platform-services/governance-service/api/routes.py:330 | `update_policy()` |
| DELETE | `/policies/{policy_id}` | platform-services | platform-services/governance-service/api/routes.py:374 | `delete_policy()` |
| POST | `/policies/{policy_id}/approve` | platform-services | platform-services/governance-service/api/routes.py:412 | `approve_policy()` |
| POST | `/policies/{policy_id}/publish` | platform-services | platform-services/governance-service/api/routes.py:451 | `publish_policy()` |
| PATCH | `/posts/{post_id}` | platform-services | platform-services/community-service/portal/api/forum.py:294 | `update_post()` |
| POST | `/posts/{post_id}/flag` | platform-services | platform-services/community-service/portal/api/forum.py:497 | `flag_post()` |
| POST | `/posts/{post_id}/mark-solution` | platform-services | platform-services/community-service/portal/api/forum.py:425 | `mark_solution()` |
| POST | `/posts/{post_id}/vote` | platform-services | platform-services/community-service/portal/api/forum.py:378 | `vote_post()` |
| POST | `/predictions` | platform-services | platform-services/simulation/digital-twin/api/routers/metrics.py:360 | `create_prediction()` |
| GET | `/predictions/twin/{twin_id}` | platform-services | platform-services/simulation/digital-twin/api/routers/metrics.py:447 | `get_predictions()` |
| GET | `/predictions/{pred_id}` | platform-services | platform-services/simulation/digital-twin/api/routers/metrics.py:394 | `get_prediction()` |
| POST | `/procedures/validate` | platform-services | platform-services/plans_service/api/bulk_operations.py:127 | `bulk_validate_procedures()` |
| GET | `/processes` | platform-services | platform-services/bia-service/database/connection.py:63 | `list_processes()` |
| POST | `/processes` | platform-services | platform-services/bia-service/api/routes.py:89 | `unknown()` |
| GET | `/processes` | platform-services | platform-services/bia-service/api/routes.py:155 | `list_bia_processes()` |
| POST | `/processes/bulk` | platform-services | platform-services/bia-service/api/routes.py:393 | `bulk_create_processes()` |
| PATCH | `/processes/bulk` | platform-services | platform-services/bia-service/api/routes.py:437 | `bulk_update_processes()` |
| DELETE | `/processes/bulk` | platform-services | platform-services/bia-service/api/routes.py:487 | `bulk_delete_processes()` |
| POST | `/processes/bulk/validate` | platform-services | platform-services/bia-service/api/routes.py:527 | `bulk_validate_processes()` |
| GET | `/processes/{process_id}` | platform-services | platform-services/bia-service/api/routes.py:176 | `get_bia_process()` |
| PUT | `/processes/{process_id}` | platform-services | platform-services/bia-service/api/routes.py:196 | `update_bia_process()` |
| DELETE | `/processes/{process_id}` | platform-services | platform-services/bia-service/api/routes.py:217 | `delete_bia_process()` |
| GET | `/processes/{process_id}` | platform-services | platform-services/bia-service/api/history.py:15 | `get_process_history()` |
| POST | `/processes/{process_id}/complete` | platform-services | platform-services/bia-service/api/routes.py:237 | `complete_bia_process()` |
| POST | `/processes/{process_id}/discover-dependencies` | platform-services | platform-services/bia-service/api/routes.py:314 | `discover_dependencies()` |
| GET | `/processes/{process_id}/fields/{field_name}` | platform-services | platform-services/bia-service/api/history.py:48 | `get_field_history()` |
| GET | `/processes/{process_id}/snapshot/{version}` | platform-services | platform-services/bia-service/api/history.py:78 | `get_process_snapshot()` |
| POST | `/processes/{process_id}/suggest-rto` | platform-services | platform-services/bia-service/api/routes.py:257 | `suggest_rt()` |
| POST | `/programs` | platform-services | platform-services/compliance-service/api/audit.py:59 | `create_audit_program()` |
| GET | `/programs` | platform-services | platform-services/compliance-service/api/audit.py:113 | `list_audit_programs()` |
| POST | `/programs` | platform-services | platform-services/learning-service/api/routes.py:30 | `create_program()` |
| GET | `/programs` | platform-services | platform-services/learning-service/api/routes.py:141 | `list_programs()` |
| GET | `/programs/performance` | platform-services | platform-services/learning-service/api/analytics.py:271 | `get_program_performance()` |
| GET | `/programs/{program_id}` | platform-services | platform-services/learning-service/api/routes.py:60 | `get_program()` |
| PATCH | `/programs/{program_id}` | platform-services | platform-services/learning-service/api/routes.py:84 | `update_program()` |
| POST | `/programs/{program_id}/archive` | platform-services | platform-services/learning-service/api/routes.py:129 | `archive_program()` |
| POST | `/programs/{program_id}/audits` | platform-services | platform-services/compliance-service/api/audit.py:159 | `schedule_audit()` |
| POST | `/programs/{program_id}/publish` | platform-services | platform-services/learning-service/api/routes.py:100 | `publish_program()` |
| GET | `/public-incidents` | platform-services | platform-services/response-service/auth/dependencies.py:119 | `list_public_incidents()` |
| GET | `/public-risks` | platform-services | platform-services/risk-service/auth/dependencies.py:119 | `list_public_risks()` |
| POST | `/queue-theory` | platform-services | platform-services/simulation/digital-twin/api/routers/bia.py:470 | `run_queue_theory_bia()` |
| POST | `/rca/bulk-validate` | platform-services | platform-services/compliance-service/api/bulk_operations.py:366 | `bulk_validate_rca_templates()` |
| GET | `/rca/methods` | platform-services | platform-services/compliance-service/api/nonconformities.py:246 | `get_rca_methods()` |
| GET | `/rca/templates/{method}` | platform-services | platform-services/compliance-service/api/nonconformities.py:152 | `get_rca_template()` |
| GET | `/readiness` | platform-services | platform-services/simulation/digital-twin/api/routers/health.py:159 | `readiness_check()` |
| GET | `/ready` | platform-services | platform-services/response-service/main.py:407 | `readiness_check()` |
| POST | `/recommend` | platform-services | platform-services/simulation/simulation/simulation/scenario_orchestrator/app/api/v1/endpoints/scenarios.py:221 | `recommend_scenarios()` |
| POST | `/recommend` | platform-services | platform-services/simulation/simulation/simulation/scenario_orchestrator/src/api/v1/endpoints/scenarios.py:221 | `recommend_scenarios()` |
| POST | `/recommend` | platform-services | platform-services/simulation/scenarios/scenario_orchestrator/app/api/v1/endpoints/scenarios.py:221 | `recommend_scenarios()` |
| POST | `/recommend` | platform-services | platform-services/simulation/scenarios/scenario_orchestrator/src/api/v1/endpoints/scenarios.py:221 | `recommend_scenarios()` |
| GET | `/recommendations` | platform-services | platform-services/validation-service/api/workflow_ai.py:95 | `get_recommendations()` |
| GET | `/recommendations` | platform-services | platform-services/governance-service/services/domain_intelligence_service.py:338 | `get_tenant_recommendations()` |
| GET | `/recommendations` | platform-services | platform-services/risk-service/api/workflow_ai.py:87 | `get_recommendations()` |
| GET | `/recommendations` | platform-services | platform-services/response-service/api/workflow_ai.py:87 | `get_recommendations()` |
| POST | `/refresh` | platform-services | platform-services/simulation/digital-twin/api/routers/auth.py:226 | `refresh_access_token()` |
| POST | `/register` | platform-services | platform-services/simulation/digital-twin/api/routers/auth.py:92 | `register()` |
| POST | `/register-service` | platform-services | platform-services/мониторинг/compliance-monitoring/main.py:760 | `register_service()` |
| GET | `/registry` | platform-services | platform-services/compliance-service/api/modules.py:380 | `get_services_registry()` |
| POST | `/registry` | platform-services | platform-services/compliance-service/api/modules.py:404 | `register_service()` |
| GET | `/reports` | platform-services | platform-services/risk-service/api/routes.py:301 | `generate_risk_report()` |
| GET | `/reports/compliance-status` | platform-services | platform-services/validation-service/api/routes.py:1024 | `get_compliance_status()` |
| GET | `/reports/critical-processes` | platform-services | platform-services/bia-service/api/routes.py:353 | `get_critical_processes_report()` |
| GET | `/reports/dependencies` | platform-services | platform-services/bia-service/api/routes.py:372 | `get_dependencies_report()` |
| GET | `/reports/performance-summary` | platform-services | platform-services/validation-service/api/routes.py:956 | `get_performance_summary()` |
| GET | `/reports/summary` | platform-services | platform-services/bia-service/api/routes.py:334 | `get_summary_report()` |
| GET | `/reputation/{user_id}` | platform-services | platform-services/community-service/portal/api/forum.py:564 | `get_user_reputation()` |
| GET | `/requirements-matrix` | platform-services | platform-services/compliance-service/api/dashboard.py:168 | `get_requirements_matrix()` |
| GET | `/research` | platform-services | platform-services/compliance-service/api/library.py:149 | `get_consultant_research()` |
| GET | `/research/{source}` | platform-services | platform-services/compliance-service/api/library.py:237 | `get_research_by_source()` |
| POST | `/resources` | platform-services | platform-services/governance-service/api/routes.py:660 | `create_resource()` |
| GET | `/resources` | platform-services | platform-services/governance-service/api/routes.py:712 | `list_resources()` |
| GET | `/resources/{resource_id}` | platform-services | platform-services/governance-service/api/routes.py:739 | `get_resource()` |
| PATCH | `/resources/{resource_id}` | platform-services | platform-services/governance-service/api/routes.py:759 | `update_resource()` |
| POST | `/retention-policies` | platform-services | platform-services/documents-service/api/routes.py:429 | `create_retention_policy_endpoint()` |
| GET | `/retention-policies` | platform-services | platform-services/documents-service/api/routes.py:446 | `list_retention_policies_endpoint()` |
| GET | `/risk-heat-map` | platform-services | platform-services/risk-service/api/routes.py:358 | `get_risk_heat_map()` |
| GET | `/risk-trends` | platform-services | platform-services/risk-service/api/routes.py:374 | `get_risk_trends()` |
| GET | `/risks` | platform-services | platform-services/risk-service/auth/dependencies.py:53 | `list_risks()` |
| GET | `/roadmap` | platform-services | platform-services/compliance-service/api/dashboard.py:289 | `get_compliance_roadmap()` |
| POST | `/roles` | platform-services | platform-services/governance-service/api/routes.py:487 | `create_role()` |
| GET | `/roles` | platform-services | platform-services/governance-service/api/routes.py:536 | `list_roles()` |
| GET | `/roles/{role_id}` | platform-services | platform-services/governance-service/api/routes.py:563 | `get_role()` |
| PATCH | `/roles/{role_id}` | platform-services | platform-services/governance-service/api/routes.py:583 | `update_role()` |
| POST | `/roles/{role_id}/assign` | platform-services | platform-services/governance-service/api/routes.py:614 | `assign_role()` |
| GET | `/salesforce/status` | platform-services | platform-services/simulation/digital-twin/api/routers/bridges.py:196 | `get_salesforce_status()` |
| POST | `/scenarios` | platform-services | platform-services/validation-service/api/routes.py:253 | `create_scenario()` |
| GET | `/scenarios` | platform-services | platform-services/validation-service/api/routes.py:283 | `list_scenarios()` |
| POST | `/scenarios` | platform-services | platform-services/simulation/simulation/api/scenario_router.py:49 | `create_scenario()` |
| GET | `/scenarios` | platform-services | platform-services/simulation/simulation/api/scenario_router.py:76 | `list_scenarios()` |
| GET | `/scenarios/available` | platform-services | platform-services/simulation/simulation/simulation/scenario_orchestrator/main.py:233 | `get_available_scenarios()` |
| GET | `/scenarios/available` | platform-services | platform-services/simulation/scenarios/scenario_orchestrator/main.py:233 | `get_available_scenarios()` |
| POST | `/scenarios/generate` | platform-services | platform-services/simulation/simulation/simulation/scenario_orchestrator/main.py:52 | `generate_ai_scenario()` |
| POST | `/scenarios/generate` | platform-services | platform-services/simulation/scenarios/scenario_orchestrator/main.py:52 | `generate_ai_scenario()` |
| GET | `/scenarios/{scenario_id}` | platform-services | platform-services/simulation/simulation/api/scenario_router.py:99 | `get_scenario()` |
| DELETE | `/scenarios/{scenario_id}` | platform-services | platform-services/simulation/simulation/api/scenario_router.py:127 | `delete_scenario()` |
| GET | `/search` | platform-services | platform-services/compliance-service/api/knowledge_base.py:416 | `search_knowledge_base()` |
| GET | `/search` | platform-services | platform-services/living-docs/api/documentation.py:198 | `smart_search()` |
| GET | `/search` | platform-services | platform-services/community-service/portal/api/knowledge.py:397 | `search_articles()` |
| GET | `/search` | platform-services | platform-services/documents-service/api/routes.py:537 | `search_documents()` |
| POST | `/send-notification/{email}` | platform-services | platform-services/simulation/digital-twin/venv/lib/python3.9/site-packages/fastapi/background.py:31 | `send_notification()` |
| POST | `/series` | platform-services | platform-services/simulation/digital-twin/api/routers/metrics.py:124 | `create_metric_series()` |
| GET | `/series/{twin_id}` | platform-services | platform-services/simulation/digital-twin/api/routers/metrics.py:162 | `get_metrics()` |
| GET | `/severity/{severity}` | platform-services | platform-services/compliance-service/api/gaps.py:520 | `get_gaps_by_severity()` |
| POST | `/simulate` | platform-services | platform-services/simulation/simulation/simulation2/simple_app.py:49 | `simulate_basic()` |
| POST | `/simulations` | platform-services | platform-services/simulation/simulation/api/simulation_router.py:49 | `create_simulation()` |
| GET | `/simulations` | platform-services | platform-services/simulation/simulation/api/simulation_router.py:80 | `list_simulations()` |
| POST | `/simulations` | platform-services | platform-services/community-service/portal/api/simulation_router.py:42 | `create_simulation()` |
| GET | `/simulations` | platform-services | platform-services/community-service/portal/api/simulation_router.py:73 | `list_simulations()` |
| GET | `/simulations/{sim_id}` | platform-services | platform-services/simulation/simulation/api/simulation_router.py:107 | `get_simulation()` |
| DELETE | `/simulations/{sim_id}` | platform-services | platform-services/simulation/simulation/api/simulation_router.py:122 | `delete_simulation()` |
| GET | `/simulations/{sim_id}` | platform-services | platform-services/community-service/portal/api/simulation_router.py:103 | `get_simulation()` |
| DELETE | `/simulations/{sim_id}` | platform-services | platform-services/community-service/portal/api/simulation_router.py:120 | `delete_simulation()` |
| GET | `/simulations/{sim_id}/results` | platform-services | platform-services/simulation/simulation/api/execution_router.py:142 | `get_simulation_results()` |
| GET | `/simulations/{sim_id}/results` | platform-services | platform-services/community-service/portal/api/execution_router.py:139 | `get_simulation_results()` |
| POST | `/simulations/{sim_id}/run` | platform-services | platform-services/simulation/simulation/api/execution_router.py:96 | `run_simulation()` |
| POST | `/simulations/{sim_id}/run` | platform-services | platform-services/community-service/portal/api/execution_router.py:89 | `run_simulation()` |
| GET | `/simulations/{sim_id}/status` | platform-services | platform-services/simulation/simulation/api/execution_router.py:122 | `get_simulation_status()` |
| GET | `/simulations/{sim_id}/status` | platform-services | platform-services/community-service/portal/api/execution_router.py:117 | `get_simulation_status()` |
| POST | `/simulations/{sim_id}/stop` | platform-services | platform-services/simulation/simulation/api/execution_router.py:179 | `stop_simulation()` |
| POST | `/simulations/{sim_id}/stop` | platform-services | platform-services/community-service/portal/api/execution_router.py:180 | `stop_simulation()` |
| GET | `/single-points-of-failure` | platform-services | platform-services/bia-service/supply_chain_api.py:311 | `identify_single_points_of_failure()` |
| GET | `/specialists/{specialist_id}/reviews` | platform-services | platform-services/community-service/marketplace/api/reviews.py:267 | `get_specialist_reviews()` |
| GET | `/specialists/{specialist_id}/stats` | platform-services | platform-services/community-service/marketplace/api/reviews.py:296 | `get_specialist_review_stats()` |
| POST | `/stakeholders` | platform-services | platform-services/governance-service/api/routes.py:1151 | `create_stakeholder()` |
| GET | `/stakeholders` | platform-services | platform-services/governance-service/api/routes.py:1197 | `list_stakeholders()` |
| GET | `/stakeholders/{stakeholder_id}` | platform-services | platform-services/governance-service/api/routes.py:1227 | `get_stakeholder()` |
| PATCH | `/stakeholders/{stakeholder_id}` | platform-services | platform-services/governance-service/api/routes.py:1256 | `update_stakeholder()` |
| GET | `/standards` | platform-services | platform-services/compliance-service/api/knowledge_base.py:23 | `list_standards()` |
| GET | `/statistics` | platform-services | platform-services/simulation/digital-twin/api/routers/health.py:114 | `get_statistics()` |
| GET | `/stats` | platform-services | platform-services/living-docs/main.py:286 | `get_stats()` |
| GET | `/stats` | platform-services | platform-services/community-service/portal/api/forum.py:719 | `get_forum_stats()` |
| GET | `/stats/my` | platform-services | platform-services/community-service/marketplace/api/proposals.py:447 | `get_my_proposal_stats()` |
| GET | `/stats/overview` | platform-services | platform-services/community-service/marketplace/api/projects.py:515 | `get_projects_stats()` |
| GET | `/status` | platform-services | platform-services/validation-service/api/routes.py:1062 | `get_service_status()` |
| GET | `/status` | platform-services | platform-services/simulation/digital-twin/api/routers/health.py:90 | `get_status()` |
| POST | `/strategies` | platform-services | platform-services/planning_service/api/bulk_operations.py:51 | `bulk_create_strategies()` |
| GET | `/strategies/{strategy_id}/ai-advice` | platform-services | platform-services/planning_service/api/workflow_ai.py:33 | `get_ai_advice()` |
| POST | `/strategies/{strategy_id}/complete-case` | platform-services | platform-services/planning_service/api/workflow_ai.py:111 | `complete_and_create_case()` |
| GET | `/summary` | platform-services | platform-services/bia-service/supply_chain_api.py:543 | `get_supply_chain_summary()` |
| POST | `/suppliers` | platform-services | platform-services/bia-service/supply_chain_api.py:44 | `create_supplier()` |
| GET | `/suppliers` | platform-services | platform-services/bia-service/supply_chain_api.py:82 | `list_suppliers()` |
| GET | `/suppliers/{supplier_id}` | platform-services | platform-services/bia-service/supply_chain_api.py:134 | `get_supplier()` |
| PATCH | `/suppliers/{supplier_id}` | platform-services | platform-services/bia-service/supply_chain_api.py:156 | `update_supplier()` |
| GET | `/suppliers/{supplier_id}/risk-profile` | platform-services | platform-services/bia-service/supply_chain_api.py:188 | `get_supplier_risk_profile()` |
| POST | `/teams` | platform-services | platform-services/response-service/api/routes.py:439 | `create_response_team()` |
| GET | `/teams` | platform-services | platform-services/response-service/api/routes.py:472 | `list_response_teams()` |
| GET | `/template/csv` | platform-services | platform-services/simulation/digital-twin/api/routers/import_data.py:333 | `get_csv_template()` |
| GET | `/template/json` | platform-services | platform-services/simulation/digital-twin/api/routers/import_data.py:359 | `get_json_template()` |
| GET | `/templates` | platform-services | platform-services/compliance-service/api/templates.py:30 | `list_templates()` |
| POST | `/templates` | platform-services | platform-services/compliance-service/api/templates.py:124 | `create_template()` |
| GET | `/templates` | platform-services | platform-services/governance-service/services/domain_intelligence_service.py:219 | `get_domain_templates()` |
| GET | `/templates/bpmn/{workflow_type}` | platform-services | platform-services/compliance-service/api/templates.py:330 | `get_bpmn_workflow()` |
| GET | `/templates/category/{category}` | platform-services | platform-services/compliance-service/api/templates.py:264 | `get_templates_by_category()` |
| POST | `/templates/generate` | platform-services | platform-services/compliance-service/api/templates.py:296 | `generate_template_with_ai()` |
| GET | `/templates/iso-clause/{clause}` | platform-services | platform-services/compliance-service/api/templates.py:283 | `get_templates_by_iso_clause()` |
| GET | `/templates/{template_id}` | platform-services | platform-services/compliance-service/api/templates.py:149 | `get_template()` |
| PUT | `/templates/{template_id}` | platform-services | platform-services/compliance-service/api/templates.py:201 | `update_template()` |
| DELETE | `/templates/{template_id}` | platform-services | platform-services/compliance-service/api/templates.py:248 | `delete_template()` |
| POST | `/templates/{template_id}/render` | platform-services | platform-services/compliance-service/api/templates.py:218 | `render_template()` |
| GET | `/templates/{template_id}/usage-stats` | platform-services | platform-services/compliance-service/api/templates.py:402 | `get_template_usage_stats()` |
| POST | `/templates/{template_id}/verify` | platform-services | platform-services/compliance-service/api/templates.py:374 | `verify_template_integrity()` |
| GET | `/tenant` | platform-services | platform-services/governance-service/services/domain_intelligence_service.py:124 | `get_tenant_domain()` |
| PATCH | `/tenant/classify` | platform-services | platform-services/governance-service/services/domain_intelligence_service.py:30 | `classify_tenant_domain()` |
| POST | `/test/simulate` | platform-services | platform-services/simulation/simulation/simulation/scenario_orchestrator/app/api/v1/endpoints/scenarios.py:270 | `simulate_scenario_test()` |
| POST | `/test/simulate` | platform-services | platform-services/simulation/simulation/simulation/scenario_orchestrator/src/api/v1/endpoints/scenarios.py:270 | `simulate_scenario_test()` |
| POST | `/test/simulate` | platform-services | platform-services/simulation/scenarios/scenario_orchestrator/app/api/v1/endpoints/scenarios.py:270 | `simulate_scenario_test()` |
| POST | `/test/simulate` | platform-services | platform-services/simulation/scenarios/scenario_orchestrator/src/api/v1/endpoints/scenarios.py:270 | `simulate_scenario_test()` |
| POST | `/topics` | platform-services | platform-services/community-service/portal/api/forum.py:56 | `create_topic()` |
| GET | `/topics` | platform-services | platform-services/community-service/portal/api/forum.py:91 | `get_topics()` |
| GET | `/topics/{topic_id}` | platform-services | platform-services/community-service/portal/api/forum.py:132 | `get_topic()` |
| PATCH | `/topics/{topic_id}` | platform-services | platform-services/community-service/portal/api/forum.py:173 | `update_topic()` |
| POST | `/topics/{topic_id}/flag` | platform-services | platform-services/community-service/portal/api/forum.py:473 | `flag_topic()` |
| POST | `/topics/{topic_id}/posts` | platform-services | platform-services/community-service/portal/api/forum.py:211 | `create_post()` |
| GET | `/topics/{topic_id}/posts` | platform-services | platform-services/community-service/portal/api/forum.py:254 | `get_topic_posts()` |
| POST | `/topics/{topic_id}/vote` | platform-services | platform-services/community-service/portal/api/forum.py:332 | `vote_topic()` |
| PUT | `/treatment-plans/{plan_id}` | platform-services | platform-services/risk-service/api/routes.py:278 | `update_treatment_plan()` |
| GET | `/twin/{twin_id}` | platform-services | platform-services/simulation/digital-twin/api/routers/organizations.py:218 | `get_organization_by_twin_id()` |
| GET | `/twin/{twin_id}/latest` | platform-services | platform-services/simulation/digital-twin/api/routers/simulations.py:295 | `get_latest_simulation()` |
| GET | `/twin/{twin_id}/summary` | platform-services | platform-services/simulation/digital-twin/api/routers/simulations.py:447 | `get_simulation_summary()` |
| GET | `/types/available` | platform-services | platform-services/simulation/digital-twin/api/routers/bia.py:407 | `get_available_bia_types()` |
| GET | `/types/available` | platform-services | platform-services/simulation/digital-twin/api/routers/scenarios.py:334 | `get_available_scenario_types()` |
| GET | `/types/available` | platform-services | platform-services/simulation/digital-twin/api/routers/predictions.py:372 | `get_available_prediction_types()` |
| POST | `/uploadfile/` | platform-services | platform-services/simulation/digital-twin/venv/lib/python3.9/site-packages/fastapi/datastructures.py:58 | `create_upload_file()` |
| GET | `/users/` | platform-services | platform-services/simulation/digital-twin/venv/lib/python3.9/site-packages/fastapi/applications.py:238 | `unknown()` |
| GET | `/users/` | platform-services | platform-services/simulation/digital-twin/venv/lib/python3.9/site-packages/fastapi/routing.py:540 | `read_users()` |
| GET | `/users/me` | platform-services | platform-services/simulation/digital-twin/venv/lib/python3.9/site-packages/fastapi/security/http.py:124 | `read_current_user()` |
| GET | `/users/me/items/` | platform-services | platform-services/simulation/digital-twin/venv/lib/python3.9/site-packages/fastapi/param_functions.py:2353 | `read_own_items()` |
| GET | `/users/{user_id}/badges` | platform-services | platform-services/community-service/portal/api/forum.py:708 | `get_user_badges()` |
| GET | `/users/{user_id}/profile` | platform-services | platform-services/community-service/portal/api/forum.py:575 | `get_user_profile()` |
| POST | `/what-if-analysis` | platform-services | platform-services/bia-service/supply_chain_api.py:425 | `perform_what_if_analysis()` |
| GET | `/who/framework` | platform-services | platform-services/compliance-service/api/knowledge_base.py:262 | `get_who_framework()` |
| GET | `/{assessment_id}` | platform-services | platform-services/compliance-service/api/assessments.py:155 | `get_assessment()` |
| DELETE | `/{assessment_id}` | platform-services | platform-services/compliance-service/api/assessments.py:379 | `delete_assessment()` |
| GET | `/{assessment_id}/results` | platform-services | platform-services/compliance-service/api/assessments.py:298 | `get_assessment_results()` |
| POST | `/{assessment_id}/run` | platform-services | platform-services/compliance-service/api/assessments.py:193 | `run_assessment()` |
| GET | `/{audit_id}/checklist` | platform-services | platform-services/compliance-service/api/audit.py:269 | `get_audit_checklist()` |
| POST | `/{audit_id}/complete` | platform-services | platform-services/compliance-service/api/audit.py:512 | `complete_audit()` |
| POST | `/{audit_id}/findings` | platform-services | platform-services/compliance-service/api/audit.py:353 | `create_audit_finding()` |
| GET | `/{audit_id}/findings` | platform-services | platform-services/compliance-service/api/audit.py:425 | `list_audit_findings()` |
| GET | `/{audit_id}/report` | platform-services | platform-services/compliance-service/api/audit.py:551 | `generate_audit_report()` |
| POST | `/{audit_id}/start` | platform-services | platform-services/compliance-service/api/audit.py:473 | `start_audit()` |
| GET | `/{bia_id}` | platform-services | platform-services/simulation/digital-twin/api/routers/bia.py:182 | `get_bia_analysis()` |
| DELETE | `/{bia_id}` | platform-services | platform-services/simulation/digital-twin/api/routers/bia.py:211 | `delete_bia_analysis()` |
| POST | `/{bia_id}/execute` | platform-services | platform-services/simulation/digital-twin/api/routers/bia.py:245 | `execute_bia_analysis()` |
| GET | `/{evidence_id}` | platform-services | platform-services/compliance-service/api/evidence.py:165 | `get_evidence()` |
| PATCH | `/{evidence_id}` | platform-services | platform-services/compliance-service/api/evidence.py:210 | `update_evidence()` |
| DELETE | `/{evidence_id}` | platform-services | platform-services/compliance-service/api/evidence.py:376 | `delete_evidence()` |
| GET | `/{evidence_id}/history` | platform-services | platform-services/compliance-service/api/evidence.py:440 | `get_evidence_history()` |
| POST | `/{evidence_id}/transition` | platform-services | platform-services/compliance-service/api/evidence.py:264 | `transition_evidence()` |
| GET | `/{exercise_id}` | platform-services | platform-services/simulation/digital-twin/api/routers/exercises.py:190 | `get_exercise()` |
| PUT | `/{exercise_id}` | platform-services | platform-services/simulation/digital-twin/api/routers/exercises.py:219 | `update_exercise()` |
| DELETE | `/{exercise_id}` | platform-services | platform-services/simulation/digital-twin/api/routers/exercises.py:260 | `delete_exercise()` |
| POST | `/{exercise_id}/complete` | platform-services | platform-services/simulation/digital-twin/api/routers/exercises.py:340 | `complete_exercise()` |
| POST | `/{exercise_id}/execute` | platform-services | platform-services/simulation/digital-twin/api/routers/exercises.py:403 | `execute_exercise_simulation()` |
| POST | `/{exercise_id}/start` | platform-services | platform-services/simulation/digital-twin/api/routers/exercises.py:294 | `start_exercise()` |
| GET | `/{gap_id}` | platform-services | platform-services/compliance-service/api/gaps.py:98 | `get_gap()` |
| PATCH | `/{gap_id}` | platform-services | platform-services/compliance-service/api/gaps.py:136 | `update_gap()` |
| POST | `/{gap_id}/effectiveness-review` | platform-services | platform-services/compliance-service/api/gaps.py:717 | `create_effectiveness_review()` |
| GET | `/{gap_id}/effectiveness-reviews` | platform-services | platform-services/compliance-service/api/gaps.py:817 | `get_effectiveness_reviews()` |
| POST | `/{gap_id}/rca` | platform-services | platform-services/compliance-service/api/gaps.py:573 | `create_root_cause_analysis()` |
| GET | `/{gap_id}/rca` | platform-services | platform-services/compliance-service/api/gaps.py:658 | `get_root_cause_analyses()` |
| POST | `/{gap_id}/reopen` | platform-services | platform-services/compliance-service/api/gaps.py:454 | `reopen_gap()` |
| POST | `/{gap_id}/resolve` | platform-services | platform-services/compliance-service/api/gaps.py:319 | `resolve_gap()` |
| POST | `/{gap_id}/start-remediation` | platform-services | platform-services/compliance-service/api/gaps.py:183 | `start_remediation()` |
| POST | `/{gap_id}/update-progress` | platform-services | platform-services/compliance-service/api/gaps.py:251 | `update_remediation_progress()` |
| POST | `/{gap_id}/verify` | platform-services | platform-services/compliance-service/api/gaps.py:385 | `verify_gap_resolution()` |
| GET | `/{item_id}/ai-advice` | platform-services | platform-services/compliance-service/api/workflow_ai.py:28 | `get_ai_advice()` |
| GET | `/{item_id}/ai-advice` | platform-services | platform-services/governance-service/api/workflow_ai.py:28 | `get_ai_advice()` |
| GET | `/{item_id}/ai-advice` | platform-services | platform-services/plans_service/api/workflow_ai.py:28 | `get_ai_advice()` |
| GET | `/{item_id}/ai-advice` | platform-services | platform-services/learning-service/api/workflow_ai.py:28 | `get_ai_advice()` |
| GET | `/{item_id}/ai-advice` | platform-services | platform-services/bia-service/api/workflow_ai.py:28 | `get_ai_advice()` |
| GET | `/{item_id}/ai-advice` | platform-services | platform-services/documents-service/api/workflow_ai.py:28 | `get_ai_advice()` |
| GET | `/{org_id}` | platform-services | platform-services/simulation/digital-twin/api/routers/organizations.py:151 | `get_organization()` |
| PUT | `/{org_id}` | platform-services | platform-services/simulation/digital-twin/api/routers/organizations.py:277 | `update_organization()` |
| DELETE | `/{org_id}` | platform-services | platform-services/simulation/digital-twin/api/routers/organizations.py:323 | `delete_organization()` |
| GET | `/{org_id}` | platform-services | platform-services/community-service/portal/api/organizations.py:113 | `get_organization()` |
| GET | `/{org_id}/data-sources` | platform-services | platform-services/simulation/digital-twin/api/routers/organizations.py:420 | `get_organization_data_sources()` |
| GET | `/{org_id}/insights` | platform-services | platform-services/simulation/digital-twin/api/routers/organizations.py:463 | `get_ai_insights()` |
| GET | `/{page_id}` | platform-services | platform-services/living-docs/api/documentation.py:43 | `get_documentation()` |
| GET | `/{prediction_id}` | platform-services | platform-services/simulation/digital-twin/api/routers/predictions.py:309 | `get_prediction()` |
| DELETE | `/{prediction_id}` | platform-services | platform-services/simulation/digital-twin/api/routers/predictions.py:338 | `delete_prediction()` |
| GET | `/{project_id}` | platform-services | platform-services/community-service/marketplace/api/projects.py:151 | `get_project()` |
| PUT | `/{project_id}` | platform-services | platform-services/community-service/marketplace/api/projects.py:178 | `update_project()` |
| DELETE | `/{project_id}` | platform-services | platform-services/community-service/marketplace/api/projects.py:359 | `delete_project()` |
| POST | `/{project_id}/cancel` | platform-services | platform-services/community-service/marketplace/api/projects.py:313 | `cancel_project()` |
| POST | `/{project_id}/complete` | platform-services | platform-services/community-service/marketplace/api/projects.py:267 | `complete_project()` |
| GET | `/{project_id}/matching-specialists` | platform-services | platform-services/community-service/marketplace/api/projects.py:552 | `find_matching_specialists_for_project()` |
| GET | `/{project_id}/proposals` | platform-services | platform-services/community-service/marketplace/api/projects.py:416 | `get_project_proposals()` |
| POST | `/{project_id}/publish` | platform-services | platform-services/community-service/marketplace/api/projects.py:223 | `publish_project()` |
| GET | `/{project_id}/scenarios` | platform-services | platform-services/community-service/marketplace/api/projects.py:466 | `get_project_scenarios()` |
| POST | `/{project_id}/set-competency-requirements` | platform-services | platform-services/community-service/marketplace/api/projects.py:674 | `set_project_competency_requirements()` |
| GET | `/{proposal_id}` | platform-services | platform-services/community-service/marketplace/api/proposals.py:129 | `get_proposal()` |
| PUT | `/{proposal_id}` | platform-services | platform-services/community-service/marketplace/api/proposals.py:181 | `update_proposal()` |
| DELETE | `/{proposal_id}` | platform-services | platform-services/community-service/marketplace/api/proposals.py:227 | `delete_proposal()` |
| POST | `/{proposal_id}/accept` | platform-services | platform-services/community-service/marketplace/api/proposals.py:280 | `accept_proposal()` |
| POST | `/{proposal_id}/reject` | platform-services | platform-services/community-service/marketplace/api/proposals.py:339 | `reject_proposal()` |
| POST | `/{proposal_id}/withdraw` | platform-services | platform-services/community-service/marketplace/api/proposals.py:391 | `withdraw_proposal()` |
| GET | `/{review_id}` | platform-services | platform-services/compliance-service/api/management_review.py:158 | `get_management_review()` |
| GET | `/{review_id}` | platform-services | platform-services/community-service/marketplace/api/reviews.py:155 | `get_review()` |
| POST | `/{review_id}/complete` | platform-services | platform-services/compliance-service/api/management_review.py:493 | `complete_review()` |
| POST | `/{review_id}/decisions` | platform-services | platform-services/compliance-service/api/management_review.py:418 | `record_decisions()` |
| POST | `/{review_id}/hide` | platform-services | platform-services/community-service/marketplace/api/reviews.py:337 | `hide_review()` |
| GET | `/{review_id}/inputs` | platform-services | platform-services/compliance-service/api/management_review.py:203 | `get_review_inputs()` |
| GET | `/{review_id}/report` | platform-services | platform-services/compliance-service/api/management_review.py:573 | `generate_review_report()` |
| POST | `/{review_id}/respond` | platform-services | platform-services/community-service/marketplace/api/reviews.py:210 | `respond_to_review()` |
| POST | `/{review_id}/start` | platform-services | platform-services/compliance-service/api/management_review.py:356 | `start_review()` |
| POST | `/{review_id}/verify` | platform-services | platform-services/community-service/marketplace/api/reviews.py:374 | `verify_review()` |
| GET | `/{scenario_id}` | platform-services | platform-services/simulation/digital-twin/api/routers/scenarios.py:168 | `get_scenario_template()` |
| PUT | `/{scenario_id}` | platform-services | platform-services/simulation/digital-twin/api/routers/scenarios.py:198 | `update_scenario_template()` |
| DELETE | `/{scenario_id}` | platform-services | platform-services/simulation/digital-twin/api/routers/scenarios.py:239 | `delete_scenario_template()` |
| GET | `/{scenario_id}` | platform-services | platform-services/community-service/portal/api/scenarios.py:70 | `get_scenario()` |
| POST | `/{scenario_id}/deploy` | platform-services | platform-services/community-service/portal/api/scenarios.py:97 | `deploy_scenario()` |
| POST | `/{scenario_id}/reviews` | platform-services | platform-services/community-service/portal/api/scenarios.py:154 | `create_review()` |
| GET | `/{scenario_id}/reviews` | platform-services | platform-services/community-service/portal/api/scenarios.py:184 | `get_scenario_reviews()` |
| GET | `/{sim_id}` | platform-services | platform-services/simulation/digital-twin/api/routers/simulations.py:142 | `get_simulation()` |
| PUT | `/{sim_id}` | platform-services | platform-services/simulation/digital-twin/api/routers/simulations.py:210 | `update_simulation()` |
| POST | `/{sim_id}/execute` | platform-services | platform-services/simulation/digital-twin/api/routers/simulations.py:327 | `execute_simulation()` |
| GET | `/{specialist_id}` | platform-services | platform-services/community-service/marketplace/api/specialists.py:160 | `get_specialist()` |
| PUT | `/{specialist_id}` | platform-services | platform-services/community-service/marketplace/api/specialists.py:198 | `update_specialist()` |
| DELETE | `/{specialist_id}` | platform-services | platform-services/community-service/marketplace/api/specialists.py:231 | `deactivate_specialist()` |
| POST | `/{specialist_id}/certifications` | platform-services | platform-services/community-service/marketplace/api/specialists.py:298 | `add_certification()` |
| DELETE | `/{specialist_id}/certifications/{cert_id}` | platform-services | platform-services/community-service/marketplace/api/specialists.py:329 | `delete_certification()` |
| GET | `/{specialist_id}/community-reputation` | platform-services | platform-services/community-service/marketplace/api/specialists.py:461 | `get_specialist_community_reputation()` |
| GET | `/{specialist_id}/knowledge-articles` | platform-services | platform-services/community-service/marketplace/api/specialists.py:420 | `get_specialist_knowledge()` |
| POST | `/{specialist_id}/portfolio` | platform-services | platform-services/community-service/marketplace/api/specialists.py:359 | `add_portfolio_item()` |
| DELETE | `/{specialist_id}/portfolio/{portfolio_id}` | platform-services | platform-services/community-service/marketplace/api/specialists.py:390 | `delete_portfolio_item()` |
| POST | `/{specialist_id}/sync-competencies` | platform-services | platform-services/community-service/marketplace/api/specialists.py:571 | `sync_specialist_competencies()` |
| POST | `/{specialist_id}/verify` | platform-services | platform-services/community-service/marketplace/api/specialists.py:262 | `verify_specialist()` |
| POST | `/{specialist_id}/verify-via-governance` | platform-services | platform-services/community-service/marketplace/api/specialists.py:505 | `verify_specialist_via_governance()` |
| GET | `/{strategy_id}` | platform-services | platform-services/planning_service/api/routes.py:83 | `get_strategy()` |
| PUT | `/{strategy_id}` | platform-services | platform-services/planning_service/api/routes.py:110 | `update_strategy()` |
| DELETE | `/{strategy_id}` | platform-services | platform-services/planning_service/api/routes.py:145 | `delete_strategy()` |
| POST | `/{strategy_id}/approve` | platform-services | platform-services/planning_service/api/routes.py:233 | `approve_strategy()` |
| POST | `/{strategy_id}/cost-benefit` | platform-services | platform-services/planning_service/api/routes.py:171 | `calculate_cost_benefit()` |
| POST | `/{strategy_id}/submit-review` | platform-services | platform-services/planning_service/api/routes.py:202 | `submit_for_review()` |
| GET | `/{twin_id}/health-trend` | platform-services | platform-services/simulation/digital-twin/api/routers/visualize.py:231 | `get_health_trend()` |
| GET | `/{twin_id}/organization-graph` | platform-services | platform-services/simulation/digital-twin/api/routers/visualize.py:37 | `get_organization_graph()` |
| GET | `/{twin_id}/risk-heatmap` | platform-services | platform-services/simulation/digital-twin/api/routers/visualize.py:146 | `get_risk_heatmap()` |
| GET | `/{twin_id}/simulation-flow` | platform-services | platform-services/simulation/digital-twin/api/routers/visualize.py:87 | `get_simulation_flow()` |
| GET | `/{twin_id}/simulation-impact` | platform-services | platform-services/simulation/digital-twin/api/routers/visualize.py:309 | `get_simulation_impact_chart()` |
| GET | `/documents/{id}` | shared | shared/auth/permissions.py:375 | `get_document()` |
| POST | `/documents/{id}/publish` | shared | shared/auth/permissions.py:421 | `publish_document()` |
| POST | `/enrollments/{id}/approve` | shared | shared/auth/dependencies.py:143 | `approve_enrollment()` |
| POST | `/exercises` | shared | shared/auth/permissions.py:330 | `create_exercise()` |
| GET | `/exercises` | shared | shared/models/common.py:131 | `list_exercises()` |
| GET | `/health` | shared | shared/models/common.py:94 | `health_check()` |
| GET | `/items` | shared | shared/database/connection.py:44 | `get_items()` |
| GET | `/metrics` | shared | shared/monitoring/prometheus_metrics.py:192 | `metrics()` |
| GET | `/profile` | shared | shared/auth/dependencies.py:49 | `get_profile()` |
| GET | `/profile` | shared | shared/auth/jwt.py:235 | `get_profile()` |
| POST | `/programs` | shared | shared/auth/dependencies.py:84 | `create_program()` |
| DELETE | `/programs/{id}` | shared | shared/auth/dependencies.py:123 | `delete_program()` |
| GET | `/public-data` | shared | shared/auth/jwt.py:266 | `get_data()` |
| GET | `/users` | shared | shared/database/connection.py:201 | `list_users()` |

## Temporal Workflows

| Workflow | Module | File |
|----------|--------|------|
| `AccuracyMonitoringWorkflow` | intelligent-core | intelligent-core/workflow_intelligence/temporal_workflows/predictive_workflow.py:908 |
| `AgentHealthMonitoringWorkflow` | infrastructure | infrastructure/AI-office-infrastructure/agent-router/temporal_workflows.py:213 |
| `AgentLifecycleWorkflow` | intelligent-core | intelligent-core/workflow_intelligence/temporal_workflows/collective_workflow.py:894 |
| `BIAWorkflow` | intelligent-core | intelligent-core/workflow_intelligence/temporal_workflows/bia_workflow.py:399 |
| `BIAWorkflow` | intelligent-core | intelligent-core/workflow_intelligence/workflows/temporal/bia_workflow.py:192 |
| `BatchStuckDetectionWorkflow` | intelligent-core | intelligent-core/workflow_intelligence/temporal_workflows/collective_workflow.py:803 |
| `CaseContributionWorkflow` | intelligent-core | intelligent-core/workflow_intelligence/temporal_workflows/community_workflow.py:266 |
| `CircuitBreakerRecoveryWorkflow` | infrastructure | infrastructure/AI-office-infrastructure/agent-router/temporal_workflows.py:289 |
| `CollectiveIntelligenceWorkflow` | intelligent-core | intelligent-core/workflow_intelligence/temporal_workflows/collective_workflow.py:525 |
| `CommunityInsightsWorkflow` | intelligent-core | intelligent-core/workflow_intelligence/temporal_workflows/community_workflow.py:189 |
| `ContinuousMonitoringWorkflow` | intelligent-core | intelligent-core/workflow_intelligence/temporal_workflows/devops_workflow.py:522 |
| `ControlWorkflow` | infrastructure | infrastructure/AI-office-infrastructure/mio-manager/temporal_workflows/control_workflow.py:164 |
| `CoordinationWorkflow` | intelligent-core | intelligent-core/workflow_intelligence/temporal_workflows/coordination_workflow.py:475 |
| `CrossServiceWorkflow` | intelligent-core | intelligent-core/workflow_intelligence/temporal_workflows/coordination_workflow.py:605 |
| `DailyRecommendationsWorkflow` | intelligent-core | intelligent-core/workflow_intelligence/temporal_workflows/predictive_workflow.py:827 |
| `DevOpsAgentWorkflow` | infrastructure | infrastructure/AI-office-infrastructure/devops-agent/workflows/devops_workflow.py:66 |
| `DevOpsInfrastructureWorkflow` | intelligent-core | intelligent-core/workflow_intelligence/temporal_workflows/devops_workflow.py:358 |
| `DevOpsWeeklyDeepScan` | infrastructure | infrastructure/AI-office-infrastructure/devops-agent/workflows/devops_workflow.py:154 |
| `DockerfileGenerationWorkflow` | intelligent-core | intelligent-core/workflow_intelligence/temporal_workflows/devops_workflow.py:584 |
| `EventAnalysisWorkflow` | intelligent-core | intelligent-core/workflow_intelligence/temporal_workflows/event_intelligence_workflow.py:38 |
| `ExpertiseWorkflow` | intelligent-core | intelligent-core/workflow_intelligence/temporal_workflows/expertise_workflow.py:339 |
| `GapPredictionWorkflow` | intelligent-core | intelligent-core/workflow_intelligence/temporal_workflows/event_intelligence_workflow.py:259 |
| `MetricsExportWorkflow` | infrastructure | infrastructure/AI-office-infrastructure/agent-router/temporal_workflows.py:442 |
| `ModelRetrainingWorkflow` | intelligent-core | intelligent-core/workflow_intelligence/temporal_workflows/predictive_workflow.py:733 |
| `MoneyTransfer` | intelligent-core | intelligent-core/workflow_intelligence/temporal-sample/workflows.py:13 |
| `MultiAgentConsensusWorkflow` | intelligent-core | intelligent-core/workflow_intelligence/temporal_workflows/collective_workflow.py:718 |
| `ObservationWorkflow` | infrastructure | infrastructure/AI-office-infrastructure/mio-manager/temporal_workflows/observation_workflow.py:144 |
| `ParallelTaskWorkflow` | intelligent-core | intelligent-core/workflow_intelligence/temporal_workflows/coordination_workflow.py:775 |
| `PatternLearningWorkflow` | intelligent-core | intelligent-core/workflow_intelligence/temporal_workflows/event_intelligence_workflow.py:154 |
| `PredictiveAnalysisWorkflow` | intelligent-core | intelligent-core/workflow_intelligence/temporal_workflows/predictive_workflow.py:579 |
| `ReactionWorkflow` | infrastructure | infrastructure/AI-office-infrastructure/mio-manager/temporal_workflows/reaction_workflow.py:239 |
| `ReportingWorkflow` | infrastructure | infrastructure/AI-office-infrastructure/mio-manager/temporal_workflows/reporting_workflow.py:170 |
| `RiskAssessmentWorkflow` | intelligent-core | intelligent-core/workflow_intelligence/temporal_workflows/risk_workflow.py:299 |
| `ServiceDiscoverySyncWorkflow` | infrastructure | infrastructure/AI-office-infrastructure/agent-router/temporal_workflows.py:380 |

## Temporal Activities

| Activity | Module | File |
|----------|--------|------|
| `ai_analysis()` | infrastructure | infrastructure/AI-office-infrastructure/devops-agent/workflows/devops_workflow.py:30 |
| `analyze_contributions()` | intelligent-core | intelligent-core/workflow_intelligence/temporal_workflows/community_workflow.py:65 |
| `analyze_dependencies()` | intelligent-core | intelligent-core/workflow_intelligence/workflows/temporal/bia_workflow.py:78 |
| `analyze_event_activity()` | intelligent-core | intelligent-core/workflow_intelligence/temporal_workflows/event_intelligence_workflow.py:374 |
| `analyze_patterns_activity()` | intelligent-core | intelligent-core/workflow_intelligence/temporal_workflows/event_intelligence_workflow.py:469 |
| `analyze_with_ai()` | intelligent-core | intelligent-core/workflow_intelligence/temporal_workflows/devops_workflow.py:121 |
| `anonymize_organization_data()` | intelligent-core | intelligent-core/workflow_intelligence/temporal_workflows/collective_workflow.py:287 |
| `apply_fixes()` | intelligent-core | intelligent-core/workflow_intelligence/temporal_workflows/devops_workflow.py:199 |
| `apply_fixes()` | infrastructure | infrastructure/AI-office-infrastructure/devops-agent/workflows/devops_workflow.py:42 |
| `approval_request()` | intelligent-core | intelligent-core/workflow_intelligence/temporal_workflows/coordination_workflow.py:381 |
| `assess_impact()` | intelligent-core | intelligent-core/workflow_intelligence/workflows/temporal/bia_workflow.py:105 |
| `bia_activity_analyze_dependencies()` | intelligent-core | intelligent-core/workflow_intelligence/temporal_workflows/bia_workflow.py:98 |
| `bia_activity_assess_impact()` | intelligent-core | intelligent-core/workflow_intelligence/temporal_workflows/bia_workflow.py:151 |
| `bia_activity_determine_rto_rpo()` | intelligent-core | intelligent-core/workflow_intelligence/temporal_workflows/bia_workflow.py:197 |
| `bia_activity_generate_report()` | intelligent-core | intelligent-core/workflow_intelligence/temporal_workflows/bia_workflow.py:345 |
| `bia_activity_identify_processes()` | intelligent-core | intelligent-core/workflow_intelligence/temporal_workflows/bia_workflow.py:47 |
| `bia_activity_review_results()` | intelligent-core | intelligent-core/workflow_intelligence/temporal_workflows/bia_workflow.py:270 |
| `check_agent_health()` | infrastructure | infrastructure/AI-office-infrastructure/agent-router/temporal_workflows.py:64 |
| `check_all_agents()` | infrastructure | infrastructure/AI-office-infrastructure/agent-router/temporal_workflows.py:26 |
| `check_task_status()` | infrastructure | infrastructure/AI-office-infrastructure/mio-manager/temporal_workflows/control_workflow.py:45 |
| `classify_problem_activity()` | infrastructure | infrastructure/AI-office-infrastructure/mio-manager/temporal_workflows/reaction_workflow.py:48 |
| `collect_feedback_activity()` | intelligent-core | intelligent-core/workflow_intelligence/temporal_workflows/event_intelligence_workflow.py:451 |
| `collect_platform_metrics()` | infrastructure | infrastructure/AI-office-infrastructure/mio-manager/temporal_workflows/reporting_workflow.py:46 |
| `conflict_resolution()` | intelligent-core | intelligent-core/workflow_intelligence/temporal_workflows/coordination_workflow.py:313 |
| `create_collective_agent()` | intelligent-core | intelligent-core/workflow_intelligence/temporal_workflows/collective_workflow.py:238 |
| `deposit()` | intelligent-core | intelligent-core/workflow_intelligence/temporal-sample/activities.py:30 |
| `detect_prediction_anomalies()` | intelligent-core | intelligent-core/workflow_intelligence/temporal_workflows/predictive_workflow.py:389 |
| `detect_problems_from_observation()` | infrastructure | infrastructure/AI-office-infrastructure/mio-manager/temporal_workflows/observation_workflow.py:69 |
| `detect_sharing_patterns()` | intelligent-core | intelligent-core/workflow_intelligence/temporal_workflows/community_workflow.py:97 |
| `detect_stuck_organization()` | intelligent-core | intelligent-core/workflow_intelligence/temporal_workflows/collective_workflow.py:110 |
| `determine_rto_rpo()` | intelligent-core | intelligent-core/workflow_intelligence/workflows/temporal/bia_workflow.py:124 |
| `escalate_to_brain_activity()` | infrastructure | infrastructure/AI-office-infrastructure/mio-manager/temporal_workflows/reaction_workflow.py:169 |
| `execute_instant_action()` | infrastructure | infrastructure/AI-office-infrastructure/mio-manager/temporal_workflows/reaction_workflow.py:78 |
| `execute_quick_action()` | infrastructure | infrastructure/AI-office-infrastructure/mio-manager/temporal_workflows/reaction_workflow.py:125 |
| `expertise_activity_analyze_with_analyzer()` | intelligent-core | intelligent-core/workflow_intelligence/temporal_workflows/expertise_workflow.py:100 |
| `expertise_activity_collaborate_experts()` | intelligent-core | intelligent-core/workflow_intelligence/temporal_workflows/expertise_workflow.py:148 |
| `expertise_activity_generate_recommendations()` | intelligent-core | intelligent-core/workflow_intelligence/temporal_workflows/expertise_workflow.py:274 |
| `expertise_activity_route_to_expert()` | intelligent-core | intelligent-core/workflow_intelligence/temporal_workflows/expertise_workflow.py:45 |
| `expertise_activity_validate_with_knowledge()` | intelligent-core | intelligent-core/workflow_intelligence/temporal_workflows/expertise_workflow.py:218 |
| `expire_old_agents()` | intelligent-core | intelligent-core/workflow_intelligence/temporal_workflows/collective_workflow.py:415 |
| `export_metrics()` | infrastructure | infrastructure/AI-office-infrastructure/agent-router/temporal_workflows.py:157 |
| `export_metrics_to_prometheus()` | intelligent-core | intelligent-core/workflow_intelligence/temporal_workflows/predictive_workflow.py:555 |
| `export_prometheus_metrics()` | intelligent-core | intelligent-core/workflow_intelligence/temporal_workflows/devops_workflow.py:339 |
| `forecast_expert_demand()` | intelligent-core | intelligent-core/workflow_intelligence/temporal_workflows/predictive_workflow.py:197 |
| `generate_daily_recommendations()` | intelligent-core | intelligent-core/workflow_intelligence/temporal_workflows/predictive_workflow.py:280 |
| `generate_dockerfiles()` | intelligent-core | intelligent-core/workflow_intelligence/temporal_workflows/devops_workflow.py:265 |
| `generate_gap_recommendations_activity()` | intelligent-core | intelligent-core/workflow_intelligence/temporal_workflows/event_intelligence_workflow.py:591 |
| `generate_insights()` | intelligent-core | intelligent-core/workflow_intelligence/temporal_workflows/community_workflow.py:113 |
| `generate_learning_report_activity()` | intelligent-core | intelligent-core/workflow_intelligence/temporal_workflows/event_intelligence_workflow.py:520 |
| `generate_recommendations_activity()` | intelligent-core | intelligent-core/workflow_intelligence/temporal_workflows/event_intelligence_workflow.py:426 |
| `generate_report()` | infrastructure | infrastructure/AI-office-infrastructure/mio-manager/temporal_workflows/reporting_workflow.py:86 |
| `get_agent_response()` | intelligent-core | intelligent-core/workflow_intelligence/temporal_workflows/collective_workflow.py:333 |
| `handle_task_completion()` | infrastructure | infrastructure/AI-office-infrastructure/mio-manager/temporal_workflows/control_workflow.py:100 |
| `handle_task_failure()` | infrastructure | infrastructure/AI-office-infrastructure/mio-manager/temporal_workflows/control_workflow.py:131 |
| `identify_processes()` | intelligent-core | intelligent-core/workflow_intelligence/workflows/temporal/bia_workflow.py:50 |
| `identify_top_contributors()` | intelligent-core | intelligent-core/workflow_intelligence/temporal_workflows/community_workflow.py:82 |
| `initialize_bia()` | intelligent-core | intelligent-core/workflow_intelligence/workflows/temporal/bia_workflow.py:30 |
| `intent_execution()` | intelligent-core | intelligent-core/workflow_intelligence/temporal_workflows/coordination_workflow.py:98 |
| `notify_organization()` | intelligent-core | intelligent-core/workflow_intelligence/temporal_workflows/collective_workflow.py:462 |
| `notify_stakeholders()` | infrastructure | infrastructure/AI-office-infrastructure/mio-manager/temporal_workflows/reporting_workflow.py:145 |
| `observe_all_layers()` | infrastructure | infrastructure/AI-office-infrastructure/mio-manager/temporal_workflows/observation_workflow.py:43 |
| `predict_gaps_activity()` | intelligent-core | intelligent-core/workflow_intelligence/temporal_workflows/event_intelligence_workflow.py:557 |
| `predict_organization_journey()` | intelligent-core | intelligent-core/workflow_intelligence/temporal_workflows/predictive_workflow.py:98 |
| `publish_event()` | intelligent-core | intelligent-core/workflow_intelligence/workflows/temporal/bia_workflow.py:175 |
| `publish_prediction_events()` | intelligent-core | intelligent-core/workflow_intelligence/temporal_workflows/predictive_workflow.py:518 |
| `publish_problems_to_eventbus()` | infrastructure | infrastructure/AI-office-infrastructure/mio-manager/temporal_workflows/observation_workflow.py:107 |
| `publish_report_to_brain()` | infrastructure | infrastructure/AI-office-infrastructure/mio-manager/temporal_workflows/reporting_workflow.py:125 |
| `publish_to_case_library()` | intelligent-core | intelligent-core/workflow_intelligence/workflows/temporal/bia_workflow.py:161 |
| `refund()` | intelligent-core | intelligent-core/workflow_intelligence/temporal-sample/activities.py:55 |
| `report_progress_to_brain()` | infrastructure | infrastructure/AI-office-infrastructure/mio-manager/temporal_workflows/control_workflow.py:80 |
| `report_to_brain()` | intelligent-core | intelligent-core/workflow_intelligence/temporal_workflows/collective_workflow.py:486 |
| `report_to_brain()` | intelligent-core | intelligent-core/workflow_intelligence/temporal_workflows/devops_workflow.py:307 |
| `report_to_brain()` | infrastructure | infrastructure/AI-office-infrastructure/devops-agent/workflows/devops_workflow.py:54 |
| `request_brain_approval()` | intelligent-core | intelligent-core/workflow_intelligence/temporal_workflows/devops_workflow.py:161 |
| `reset_circuit_breaker()` | infrastructure | infrastructure/AI-office-infrastructure/agent-router/temporal_workflows.py:89 |
| `retrain_prediction_models()` | intelligent-core | intelligent-core/workflow_intelligence/temporal_workflows/predictive_workflow.py:349 |
| `risk_activity_assess_vulnerabilities()` | intelligent-core | intelligent-core/workflow_intelligence/temporal_workflows/risk_workflow.py:81 |
| `risk_activity_calculate_fair()` | intelligent-core | intelligent-core/workflow_intelligence/temporal_workflows/risk_workflow.py:138 |
| `risk_activity_generate_report()` | intelligent-core | intelligent-core/workflow_intelligence/temporal_workflows/risk_workflow.py:249 |
| `risk_activity_identify_threats()` | intelligent-core | intelligent-core/workflow_intelligence/temporal_workflows/risk_workflow.py:39 |
| `risk_activity_recommend_treatments()` | intelligent-core | intelligent-core/workflow_intelligence/temporal_workflows/risk_workflow.py:202 |
| `rollback_execution()` | intelligent-core | intelligent-core/workflow_intelligence/temporal_workflows/coordination_workflow.py:416 |
| `rollback_fixes()` | intelligent-core | intelligent-core/workflow_intelligence/temporal_workflows/devops_workflow.py:232 |
| `scan_all_organizations()` | intelligent-core | intelligent-core/workflow_intelligence/temporal_workflows/collective_workflow.py:159 |
| `scan_current_architecture_activity()` | intelligent-core | intelligent-core/workflow_intelligence/temporal_workflows/event_intelligence_workflow.py:533 |
| `scan_events_activity()` | intelligent-core | intelligent-core/workflow_intelligence/temporal_workflows/event_intelligence_workflow.py:359 |
| `scan_infrastructure()` | intelligent-core | intelligent-core/workflow_intelligence/temporal_workflows/devops_workflow.py:88 |
| `scan_infrastructure()` | infrastructure | infrastructure/AI-office-infrastructure/devops-agent/workflows/devops_workflow.py:16 |
| `send_alert()` | infrastructure | infrastructure/AI-office-infrastructure/agent-router/temporal_workflows.py:187 |
| `send_notification_activity()` | intelligent-core | intelligent-core/workflow_intelligence/temporal_workflows/event_intelligence_workflow.py:608 |
| `service_coordination()` | intelligent-core | intelligent-core/workflow_intelligence/temporal_workflows/coordination_workflow.py:220 |
| `status_aggregation()` | intelligent-core | intelligent-core/workflow_intelligence/temporal_workflows/coordination_workflow.py:266 |
| `store_contribution()` | intelligent-core | intelligent-core/workflow_intelligence/temporal_workflows/community_workflow.py:171 |
| `store_knowledge_activity()` | intelligent-core | intelligent-core/workflow_intelligence/temporal_workflows/event_intelligence_workflow.py:403 |
| `store_predictions_to_database()` | intelligent-core | intelligent-core/workflow_intelligence/temporal_workflows/predictive_workflow.py:488 |
| `sync_with_service_registry()` | infrastructure | infrastructure/AI-office-infrastructure/agent-router/temporal_workflows.py:115 |
| `synthesize_consensus()` | intelligent-core | intelligent-core/workflow_intelligence/temporal_workflows/collective_workflow.py:368 |
| `task_distribution()` | intelligent-core | intelligent-core/workflow_intelligence/temporal_workflows/coordination_workflow.py:178 |
| `update_ml_models_activity()` | intelligent-core | intelligent-core/workflow_intelligence/temporal_workflows/event_intelligence_workflow.py:491 |
| `validate_and_complete()` | intelligent-core | intelligent-core/workflow_intelligence/workflows/temporal/bia_workflow.py:142 |
| `validate_case_quality()` | intelligent-core | intelligent-core/workflow_intelligence/temporal_workflows/community_workflow.py:153 |
| `validate_prediction_accuracy()` | intelligent-core | intelligent-core/workflow_intelligence/temporal_workflows/predictive_workflow.py:432 |
| `validate_predictions_activity()` | intelligent-core | intelligent-core/workflow_intelligence/temporal_workflows/event_intelligence_workflow.py:578 |
| `verify_k_anonymity()` | intelligent-core | intelligent-core/workflow_intelligence/temporal_workflows/collective_workflow.py:194 |
| `wait_for_brain_directive_activity()` | infrastructure | infrastructure/AI-office-infrastructure/mio-manager/temporal_workflows/reaction_workflow.py:205 |
| `withdraw()` | intelligent-core | intelligent-core/workflow_intelligence/temporal-sample/activities.py:14 |

## EventBus Handlers

| Event Type | Handler | Module | File |
|------------|---------|--------|------|
| `dependency_added` | `_get_workflow()` | intelligent-core | intelligent-core/workflow_intelligence/integration/bia_adapter.py:188 |
| `document.*` | `handle_all_document_events()` | shared | shared/eventbus/subscriber.py:58 |
| `event.type` | `unknown()` | infrastructure | infrastructure/tools/doc-generators/event_catalog_generator.py:138 |
| `event.type` | `generate_markdown_report()` | infrastructure | infrastructure/tools/doc-generators/event_catalog_generator.py:144 |
| `exercise.created` | `handle_exercise_created()` | shared | shared/eventbus/subscriber.py:23 |
| `exercise.created` | `handle_exercise_created()` | shared | shared/eventbus/subscriber.py:53 |
| `impact_assessed` | `_get_workflow()` | intelligent-core | intelligent-core/workflow_intelligence/integration/bia_adapter.py:189 |
| `milestone_reached` | `_get_workflow()` | intelligent-core | intelligent-core/workflow_intelligence/integration/bia_adapter.py:192 |
| `process_added` | `_get_workflow()` | intelligent-core | intelligent-core/workflow_intelligence/integration/bia_adapter.py:187 |
| `process_added` | `_validate_processes()` | intelligent-core | intelligent-core/workflow_intelligence/workflows/bia_workflow.py:160 |
| `rto_set` | `_get_workflow()` | intelligent-core | intelligent-core/workflow_intelligence/integration/bia_adapter.py:190 |
| `stage_completed` | `_get_workflow()` | intelligent-core | intelligent-core/workflow_intelligence/integration/bia_adapter.py:191 |
| `stage_completed` | `_validate_processes()` | intelligent-core | intelligent-core/workflow_intelligence/workflows/bia_workflow.py:163 |
| `state_changed` | `_get_workflow()` | intelligent-core | intelligent-core/workflow_intelligence/integration/bia_adapter.py:186 |
| `test.*` | `unknown()` | intelligent-core | intelligent-core/workflow_intelligence/tests/test_workflow_engine.py:286 |
| `test.*` | `unknown()` | intelligent-core | intelligent-core/workflow_intelligence/tests/test_workflow_engine.py:427 |
| `test.*` | `unknown()` | intelligent-core | intelligent-core/workflow_intelligence/tests/test_workflow_engine.py:524 |
| `test.workflow.completed` | `unknown()` | intelligent-core | intelligent-core/workflow_intelligence/tests/test_workflow_engine.py:311 |
| `test.workflow.started` | `test_event_publishing_on_action()` | intelligent-core | intelligent-core/workflow_intelligence/tests/test_workflow_engine.py:265 |
