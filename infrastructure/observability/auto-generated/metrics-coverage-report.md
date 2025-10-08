# 📊 Metrics Coverage Report
**Generated:** 2025-10-07 22:00:47
**Total Modules with Metrics:** 10

---

## INTELLIGENT-CORE

- **Modules:** 5
- **Total Metrics:** 123
- **With Endpoint:** 5/5

### Modules:

✅ **ai-foundation-learning-knowledge** - 27 metrics :8031
   - Path: `intelligent-core/ai-foundation/learning-knowledge/monitoring`
   - Metrics: standards_loads_total, standards_load_duration, standards_cache_hits, standards_cache_misses, cases_collected_total ... (+22 more)

✅ **ai-foundation-llm** - 20 metrics :8031
   - Path: `intelligent-core/ai-foundation/llm`
   - Metrics: llm_requests_total, llm_request_duration_seconds, llm_errors_total, llm_tokens_used_total, llm_tokens_per_request ... (+15 more)

✅ **ai-foundation-rag** - 20 metrics :8031
   - Path: `intelligent-core/ai-foundation/rag`
   - Metrics: rag_search_duration_seconds, rag_search_results_count, rag_search_relevance_score, rag_searches_total, embedding_generation_duration_seconds ... (+15 more)

✅ **expertise-center-monitoring** - 27 metrics :8031
   - Path: `intelligent-core/expertise-center/monitoring`
   - Metrics: analyzer_calls_total, analyzer_duration_seconds, analyzer_errors_total, analyzer_recommendations_total, analyzer_http_calls_total ... (+22 more)

✅ **workflow_intelligence-monitoring** - 29 metrics :8031
   - Path: `intelligent-core/workflow_intelligence/monitoring`
   - Metrics: workflow_actions_total, workflow_action_duration, db_query_duration, db_queries_total, cache_hits_total ... (+24 more)

## INFRASTRUCTURE

- **Modules:** 5
- **Total Metrics:** 60
- **With Endpoint:** 0/5

### Modules:

⚠️ **AI-office-infrastructure-agent-router** - 18 metrics 
   - Path: `infrastructure/AI-office-infrastructure/agent-router`
   - Metrics: requests_total, requests_duration, agent_health, agent_response_time, agent_last_health_check ... (+13 more)

⚠️ **api** - 11 metrics 
   - Path: `platform-services/plans_service/api`
   - Metrics: http_requests_total, http_request_duration_seconds, http_request_errors_total, plans_created_total, plans_approved_total ... (+6 more)

⚠️ **api** - 10 metrics 
   - Path: `platform-services/planning_service/api`
   - Metrics: http_requests_total, http_request_duration_seconds, http_request_errors_total, strategies_created_total, strategies_approved_total ... (+5 more)

⚠️ **deployment-deployment-service** - 12 metrics 
   - Path: `infrastructure/deployment/deployment-service`
   - Metrics: deployment_info, deployments_total, deployment_duration_seconds, services_deployed_total, service_health_status ... (+7 more)

⚠️ **integration-github-integration** - 9 metrics 
   - Path: `infrastructure/integration/github-integration`
   - Metrics: github_info, webhooks_received_total, webhooks_processed_total, webhook_processing_duration, github_api_requests_total ... (+4 more)


---

## Metrics by Type

- **Counter:** 91
- **Histogram:** 45
- **Gauge:** 40
- **Info:** 7

---

## 🎯 Recommendations

### Modules Without Metrics Endpoint:

- **integration-github-integration** - Add metrics endpoint to expose 9 metrics
- **AI-office-infrastructure-agent-router** - Add metrics endpoint to expose 18 metrics
- **deployment-deployment-service** - Add metrics endpoint to expose 12 metrics
- **api** - Add metrics endpoint to expose 11 metrics
- **api** - Add metrics endpoint to expose 10 metrics
