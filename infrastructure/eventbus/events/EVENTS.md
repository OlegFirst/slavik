# BCM Platform Event Catalog
**Generated:** Automatically scanned from codebase
**Total Events:** 126
**Files Scanned:** 10220

---

## AI Events

### `ai.tool.executed`

**Publishers (1):**
- `tools/base_tool.py`

**Subscribers:** ⚠️ None found


### `ai.tool.failed`

**Publishers (1):**
- `tools/base_tool.py`

**Subscribers:** ⚠️ None found


## BCM Events

### `bcm.bia.completed`

**Publishers (1):**
- `services/bia_service.py`

**Subscribers:** ⚠️ None found


### `bcm.bia.critical_process_identified`

**Publishers (1):**
- `services/bia_service.py`

**Subscribers:** ⚠️ None found


### `bcm.bia.started`

**Publishers (1):**
- `services/bia_service.py`

**Subscribers:** ⚠️ None found


### `bcm.compliance.improvement_created`

**Publishers (1):**
- `api/improvements.py`

**Subscribers:** ⚠️ None found


### `bcm.compliance.improvement_verified`

**Publishers (1):**
- `api/improvements.py`

**Subscribers:** ⚠️ None found


### `bcm.exercise.completed`

**Publishers (1):**
- `simulation/sim_adapter.py`

**Subscribers:** ⚠️ None found


### `bcm.exercise.created`

**Publishers (1):**
- `simulation/sim_adapter.py`

**Subscribers:** ⚠️ None found


### `bcm.exercise.inject_delivered`

**Publishers (1):**
- `simulation/sim_adapter.py`

**Subscribers:** ⚠️ None found


### `bcm.exercise.response_submitted`

**Publishers (1):**
- `simulation/sim_adapter.py`

**Subscribers:** ⚠️ None found


### `bcm.exercise.scenario_created`

**Publishers (1):**
- `simulation/sim_adapter.py`

**Subscribers:** ⚠️ None found


### `bcm.exercise.scheduled`

**Publishers (1):**
- `simulation/sim_adapter.py`

**Subscribers:** ⚠️ None found


### `bcm.exercise.started`

**Publishers (1):**
- `simulation/sim_adapter.py`

**Subscribers:** ⚠️ None found


### `bcm.incident.alert_created`

**Publishers (1):**
- `thehive/thehive_adapter.py`

**Subscribers:** ⚠️ None found


### `bcm.incident.case_created`

**Publishers (1):**
- `thehive/thehive_adapter.py`

**Subscribers:** ⚠️ None found


### `bcm.incident.case_updated`

**Publishers (1):**
- `thehive/thehive_adapter.py`

**Subscribers:** ⚠️ None found


### `bcm.incident.task_created`

**Publishers (1):**
- `thehive/thehive_adapter.py`

**Subscribers:** ⚠️ None found


## BEST Events

### `best.practice.retrieved`

**Publishers (1):**
- `tools/case_library_tool.py`

**Subscribers:** ⚠️ None found


## BIA Events

### `bia.analysis.completed`

**Publishers (1):**
- `tools/bia_tools.py`

**Subscribers:** ⚠️ None found


### `bia.process.created`

**Publishers (1):**
- `integration-tests/test_eventbus_integration.py`

**Subscribers:** ⚠️ None found


## BPMN Events

### `bpmn.instance.completed`

**Publishers (2):**
- `bpmn/engine.py`
- `bpmn/engine_persistent.py`

**Subscribers:** ⚠️ None found


### `bpmn.instance.started`

**Publishers (2):**
- `bpmn/engine.py`
- `bpmn/engine_persistent.py`

**Subscribers:** ⚠️ None found


### `bpmn.instance.terminated`

**Publishers (2):**
- `bpmn/engine.py`
- `bpmn/engine_persistent.py`

**Subscribers:** ⚠️ None found


### `bpmn.process.deployed`

**Publishers (2):**
- `bpmn/engine.py`
- `bpmn/engine_persistent.py`

**Subscribers:** ⚠️ None found


### `bpmn.task.completed`

**Publishers (2):**
- `bpmn/engine.py`
- `bpmn/engine_persistent.py`

**Subscribers:** ⚠️ None found


### `bpmn.task.created`

**Publishers (2):**
- `bpmn/engine.py`
- `bpmn/engine_persistent.py`

**Subscribers:** ⚠️ None found


## CASE Events

### `case.approved`

**Publishers (1):**
- `services/peer_review_service.py`

**Subscribers:** ⚠️ None found


### `case.rejected`

**Publishers (1):**
- `services/peer_review_service.py`

**Subscribers:** ⚠️ None found


### `case.review.assigned`

**Publishers (1):**
- `services/peer_review_service.py`

**Subscribers:** ⚠️ None found


### `case.search.completed`

**Publishers (1):**
- `tools/case_library_tool.py`

**Subscribers:** ⚠️ None found


## COMPLIANCE Events

### `compliance.check.completed`

**Publishers (1):**
- `tools/compliance_tools.py`

**Subscribers:** ⚠️ None found


## CONTRIBUTION Events

### `contribution.auto_submitted`

**Publishers (1):**
- `services/workflow_completion_handler.py`

**Subscribers:** ⚠️ None found


### `contribution.offer_sent`

**Publishers (2):**
- `services/workflow_completion_handler.py`
- `services/workflow_integration_service.py`

**Subscribers:** ⚠️ None found


### `contribution.processing_failed`

**Publishers (1):**
- `services/workflow_completion_handler.py`

**Subscribers:** ⚠️ None found


### `contribution.submission_failed`

**Publishers (1):**
- `services/workflow_integration_service.py`

**Subscribers:** ⚠️ None found


### `contribution.submitted`

**Publishers (1):**
- `services/workflow_completion_handler.py`

**Subscribers:** ⚠️ None found


## DEPENDENCY Events

### `dependency.mapping.completed`

**Publishers (1):**
- `tools/bia_tools.py`

**Subscribers:** ⚠️ None found


## DOCUMENT Events

### `document.*`

**Publishers:** ⚠️ None found

**Subscribers (1):**
- `eventbus/subscriber.py`


### `document.approved`

**Publishers:** ⚠️ None found

**Subscribers (1):**
- `events/subscribers.py`


## EVIDENCE Events

### `evidence.validation.completed`

**Publishers (1):**
- `tools/compliance_tools.py`

**Subscribers:** ⚠️ None found


## EXERCISE Events

### `exercise.*`

**Publishers:** ⚠️ None found

**Subscribers (1):**
- `eventbus/client.py`


### `exercise.completed`

**Publishers:** ⚠️ None found

**Subscribers (1):**
- `events/subscribers.py`


### `exercise.created`

**Publishers (1):**
- `eventbus/client.py`

**Subscribers (2):**
- `eventbus/client.py`
- `eventbus/subscriber.py`


### `exercise.gap_identified`

**Publishers:** ⚠️ None found

**Subscribers (1):**
- `events/subscribers.py`


## GAP Events

### `gap.analysis.completed`

**Publishers (1):**
- `tools/compliance_tools.py`

**Subscribers:** ⚠️ None found


## GOVERNANCE Events

### `governance.competence.gap_identified`

**Publishers (1):**
- `events/publishers.py`

**Subscribers:** ⚠️ None found


### `governance.competence.recorded`

**Publishers (2):**
- `api/routes.py`
- `events/publishers.py`

**Subscribers (1):**
- `events/subscribers.py`


### `governance.objective.completed`

**Publishers (1):**
- `events/publishers.py`

**Subscribers:** ⚠️ None found


### `governance.objective.created`

**Publishers (2):**
- `api/routes.py`
- `events/publishers.py`

**Subscribers:** ⚠️ None found


### `governance.objective.updated`

**Publishers (2):**
- `api/routes.py`
- `events/publishers.py`

**Subscribers:** ⚠️ None found


### `governance.organization.created`

**Publishers:** ⚠️ None found

**Subscribers (1):**
- `events/subscribers.py`


### `governance.person.added`

**Publishers:** ⚠️ None found

**Subscribers (1):**
- `events/subscribers.py`


### `governance.policy.approved`

**Publishers (2):**
- `api/routes.py`
- `events/publishers.py`

**Subscribers:** ⚠️ None found


### `governance.policy.created`

**Publishers (2):**
- `api/routes.py`
- `events/publishers.py`

**Subscribers (1):**
- `events/subscribers.py`


### `governance.policy.deleted`

**Publishers (2):**
- `api/routes.py`
- `events/publishers.py`

**Subscribers:** ⚠️ None found


### `governance.policy.published`

**Publishers (2):**
- `api/routes.py`
- `events/publishers.py`

**Subscribers (1):**
- `events/subscribers.py`


### `governance.policy.updated`

**Publishers (2):**
- `api/routes.py`
- `events/publishers.py`

**Subscribers:** ⚠️ None found


### `governance.resource.allocated`

**Publishers (2):**
- `api/routes.py`
- `events/publishers.py`

**Subscribers (1):**
- `events/subscribers.py`


### `governance.resource.created`

**Publishers (2):**
- `api/routes.py`
- `events/publishers.py`

**Subscribers:** ⚠️ None found


### `governance.role.assigned`

**Publishers (2):**
- `api/routes.py`
- `events/publishers.py`

**Subscribers (2):**
- `events/subscribers.py`
- `events/subscribers.py`


### `governance.role.created`

**Publishers (2):**
- `api/routes.py`
- `events/publishers.py`

**Subscribers:** ⚠️ None found


### `governance.role.removed`

**Publishers:** ⚠️ None found

**Subscribers (1):**
- `events/subscribers.py`


## IMPACT Events

### `impact.calculation.completed`

**Publishers (1):**
- `tools/bia_tools.py`

**Subscribers:** ⚠️ None found


## INCIDENT Events

### `incident.declared`

**Publishers:** ⚠️ None found

**Subscribers (1):**
- `events/subscribers.py`


### `incident.resolved`

**Publishers:** ⚠️ None found

**Subscribers (1):**
- `events/subscribers.py`


## LEARNING Events

### `learning.certification.issued`

**Publishers (2):**
- `api/routes.py`
- `events/publishers.py`

**Subscribers (3):**
- `events/subscribers.py`
- `events/subscribers.py`
- `events/subscribers.py`


### `learning.enrollment.completed`

**Publishers (1):**
- `events/publishers.py`

**Subscribers:** ⚠️ None found


### `learning.enrollment.created`

**Publishers (1):**
- `api/routes.py`

**Subscribers:** ⚠️ None found


### `learning.enrollment.submitted`

**Publishers (1):**
- `api/routes.py`

**Subscribers:** ⚠️ None found


### `learning.program.created`

**Publishers (2):**
- `api/routes.py`
- `events/publishers.py`

**Subscribers:** ⚠️ None found


### `learning.program.published`

**Publishers (1):**
- `api/routes.py`

**Subscribers (1):**
- `events/subscribers.py`


### `learning.training.completed`

**Publishers (1):**
- `api/routes.py`

**Subscribers (3):**
- `events/subscribers.py`
- `events/subscribers.py`
- `events/subscribers.py`


### `learning.training.started`

**Publishers (1):**
- `api/routes.py`

**Subscribers:** ⚠️ None found


## MARKETPLACE Events

### `marketplace.project.assigned`

**Publishers (2):**
- `services/project_service.py`
- `services/proposal_service.py`

**Subscribers:** ⚠️ None found


### `marketplace.project.completed`

**Publishers (1):**
- `services/project_service.py`

**Subscribers:** ⚠️ None found


### `marketplace.project.created`

**Publishers (1):**
- `services/project_service.py`

**Subscribers:** ⚠️ None found


### `marketplace.project.published`

**Publishers (1):**
- `services/project_service.py`

**Subscribers:** ⚠️ None found


### `marketplace.proposal.accepted`

**Publishers (1):**
- `services/proposal_service.py`

**Subscribers:** ⚠️ None found


### `marketplace.proposal.rejected`

**Publishers (1):**
- `services/proposal_service.py`

**Subscribers:** ⚠️ None found


### `marketplace.proposal.submitted`

**Publishers (1):**
- `services/proposal_service.py`

**Subscribers:** ⚠️ None found


### `marketplace.review.created`

**Publishers (1):**
- `services/review_service.py`

**Subscribers:** ⚠️ None found


### `marketplace.review.responded`

**Publishers (1):**
- `services/review_service.py`

**Subscribers:** ⚠️ None found


### `marketplace.specialist.profile_updated`

**Publishers (1):**
- `services/specialist_service.py`

**Subscribers:** ⚠️ None found


### `marketplace.specialist.registered`

**Publishers (1):**
- `services/specialist_service.py`

**Subscribers:** ⚠️ None found


### `marketplace.specialist.verified`

**Publishers (1):**
- `services/specialist_service.py`

**Subscribers:** ⚠️ None found


## MATURITY Events

### `maturity.assessment.completed`

**Publishers (1):**
- `tools/strategic_tools.py`

**Subscribers:** ⚠️ None found


## OTHER Events

### `#`

**Publishers:** ⚠️ None found

**Subscribers (1):**
- `eventbus/client.py`


### `dependency_added`

**Publishers:** ⚠️ None found

**Subscribers (1):**
- `integration/bia_adapter.py`


### `impact_assessed`

**Publishers:** ⚠️ None found

**Subscribers (1):**
- `integration/bia_adapter.py`


### `milestone_reached`

**Publishers:** ⚠️ None found

**Subscribers (1):**
- `integration/bia_adapter.py`


### `process_added`

**Publishers:** ⚠️ None found

**Subscribers (2):**
- `integration/bia_adapter.py`
- `workflows/bia_workflow.py`


### `rto_set`

**Publishers:** ⚠️ None found

**Subscribers (1):**
- `integration/bia_adapter.py`


### `stage_completed`

**Publishers:** ⚠️ None found

**Subscribers (2):**
- `integration/bia_adapter.py`
- `workflows/bia_workflow.py`


### `state_changed`

**Publishers:** ⚠️ None found

**Subscribers (1):**
- `integration/bia_adapter.py`


## PROACTIVE Events

### `proactive.daily_digest`

**Publishers (1):**
- `services/proactive_recommendations.py`

**Subscribers:** ⚠️ None found


## REPUTATION Events

### `reputation.level_up`

**Publishers (1):**
- `services/reputation_engine.py`

**Subscribers:** ⚠️ None found


### `reputation.points_awarded`

**Publishers (1):**
- `services/reputation_engine.py`

**Subscribers:** ⚠️ None found


## RESOURCE Events

### `resource.planning.completed`

**Publishers (1):**
- `tools/strategic_tools.py`

**Subscribers:** ⚠️ None found


## RESPONSE Events

### `response.compliance.violation`

**Publishers (1):**
- `events/publishers.py`

**Subscribers:** ⚠️ None found


### `response.incident.closed`

**Publishers (1):**
- `events/publishers.py`

**Subscribers:** ⚠️ None found


### `response.incident.created`

**Publishers (1):**
- `events/publishers.py`

**Subscribers:** ⚠️ None found


### `response.incident.escalated`

**Publishers (1):**
- `events/publishers.py`

**Subscribers:** ⚠️ None found


### `response.incident.resolved`

**Publishers (1):**
- `events/publishers.py`

**Subscribers:** ⚠️ None found


### `response.incident.status_changed`

**Publishers (1):**
- `events/publishers.py`

**Subscribers:** ⚠️ None found


### `response.incident.updated`

**Publishers (1):**
- `events/publishers.py`

**Subscribers:** ⚠️ None found


### `response.metrics.updated`

**Publishers (1):**
- `events/publishers.py`

**Subscribers:** ⚠️ None found


### `response.stakeholder.notification`

**Publishers (1):**
- `events/publishers.py`

**Subscribers:** ⚠️ None found


## REVIEW Events

### `review.submitted`

**Publishers (1):**
- `services/peer_review_service.py`

**Subscribers:** ⚠️ None found


## RISK Events

### `risk.identified`

**Publishers:** ⚠️ None found

**Subscribers (1):**
- `events/subscribers.py`


## SPECIALIST Events

### `specialist.demand_forecast`

**Publishers (1):**
- `services/demand_forecaster.py`

**Subscribers:** ⚠️ None found


## SYSTEM Events

### `system.*`

**Publishers:** ⚠️ None found

**Subscribers (1):**
- `ai-orchestration/orchestrator.py`


## TEST Events

### `test.*`

**Publishers:** ⚠️ None found

**Subscribers (1):**
- `tests/test_workflow_engine.py`


### `test.workflow.completed`

**Publishers:** ⚠️ None found

**Subscribers (1):**
- `tests/test_workflow_engine.py`


### `test.workflow.started`

**Publishers:** ⚠️ None found

**Subscribers (1):**
- `tests/test_workflow_engine.py`


## THEHIVE Events

### `thehive.alert.created`

**Publishers (1):**
- `thehive_adapter/main.py`

**Subscribers:** ⚠️ None found


### `thehive.alert.promoted`

**Publishers (1):**
- `thehive_adapter/main.py`

**Subscribers:** ⚠️ None found


### `thehive.bcm.incident.created`

**Publishers (1):**
- `thehive_adapter/main.py`

**Subscribers:** ⚠️ None found


### `thehive.case.created`

**Publishers (1):**
- `thehive_adapter/main.py`

**Subscribers:** ⚠️ None found


### `thehive.case.updated`

**Publishers (1):**
- `thehive_adapter/main.py`

**Subscribers:** ⚠️ None found


### `thehive.task.created`

**Publishers (1):**
- `thehive_adapter/main.py`

**Subscribers:** ⚠️ None found


## TIMELINE Events

### `timeline.prediction.completed`

**Publishers (1):**
- `tools/strategic_tools.py`

**Subscribers:** ⚠️ None found


## TRAINING Events

### `training.assessment_failed`

**Publishers (2):**
- `programs/training_service.py`
- `services/training_service.py`

**Subscribers:** ⚠️ None found


### `training.auto_completed`

**Publishers (2):**
- `programs/training_service.py`
- `services/training_service.py`

**Subscribers:** ⚠️ None found


### `training.certified`

**Publishers (2):**
- `programs/training_service.py`
- `services/training_service.py`

**Subscribers:** ⚠️ None found


## WORKFLOW Events

### `workflow.*`

**Publishers:** ⚠️ None found

**Subscribers (1):**
- `ai-orchestration/orchestrator.py`

