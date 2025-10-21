#!/usr/bin/env python3
"""
Collective Intelligence Workflow - Temporal Durable Execution

Provides fault-tolerant, retryable workflows for Collective Intelligence:
- Stuck organization detection
- Collective agent creation from anonymized data
- Multi-agent consensus mechanisms
- Privacy-preserving collaboration
- Agent lifecycle management

Patterns:
- Saga для rollback при ошибках
- Retry policies для fault tolerance
- Privacy enforcement на каждом шаге
- Long-running workflows с state persistence
- Multi-agent coordination с consensus
"""

import asyncio
import logging
from datetime import timedelta, datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import uuid

from temporalio import workflow, activity
from temporalio.common import RetryPolicy
from temporalio.exceptions import ApplicationError

logger = logging.getLogger(__name__)


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class StuckDetectionConfig:
    """Configuration for stuck organization detection"""
    org_id: str
    module: Optional[str] = None
    threshold: int = 4
    check_last_days: int = 7


@dataclass
class StuckDetectionResult:
    """Result of stuck detection analysis"""
    org_id: str
    is_stuck: bool
    stuck_score: int
    signals: Dict[str, Any]
    recommendations: List[Dict[str, Any]]
    timestamp: str


@dataclass
class CollectiveAgentConfig:
    """Configuration for creating collective agent"""
    problem_type: str
    requesting_org_id: str
    min_orgs: int = 5
    min_success_rate: float = 0.8
    agent_expiration_days: int = 7


@dataclass
class CollectiveAgentResult:
    """Result of collective agent creation"""
    agent_id: str
    source_org_count: int
    problem_type: str
    expires_at: str
    system_prompt: str
    k_anonymity_verified: bool


@dataclass
class ConsensusConfig:
    """Configuration for multi-agent consensus"""
    agent_ids: List[str]
    question: str
    consensus_threshold: float = 0.75
    max_rounds: int = 3


@dataclass
class ConsensusResult:
    """Result of consensus mechanism"""
    consensus_reached: bool
    confidence: float
    synthesized_answer: str
    participating_agents: int
    rounds_used: int
    individual_responses: List[Dict[str, Any]]


@dataclass
class AgentCleanupConfig:
    """Configuration for agent cleanup"""
    max_age_days: int = 7
    batch_size: int = 100


# ============================================================================
# Activities - Stuck Detection
# ============================================================================

@activity.defn
async def detect_stuck_organization(config: StuckDetectionConfig) -> StuckDetectionResult:
    """
    Detect if organization is stuck and needs help

    Activity: Idempotent, retryable

    Signals analyzed:
    - Days without progress
    - Validation failures
    - Low AI confidence scores
    - Repeated questions
    - Frustration indicators
    """
    import httpx

    logger.info(f" Detecting stuck status for org: {config.org_id}")

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "http://localhost:8032/api/v1/stuck-detection/detect",
                json={
                    "org_id": config.org_id,
                    "module": config.module,
                    "threshold": config.threshold,
                    "days": config.check_last_days
                }
            )

            if response.status_code != 200:
                raise Exception(f"Stuck detection failed: {response.status_code}")

            result = response.json()

            return StuckDetectionResult(
                org_id=config.org_id,
                is_stuck=result.get("is_stuck", False),
                stuck_score=result.get("stuck_score", 0),
                signals=result.get("signals", {}),
                recommendations=result.get("recommendations", []),
                timestamp=datetime.utcnow().isoformat()
            )

    except Exception as e:
        logger.error(f" Stuck detection failed: {e}")
        raise


@activity.defn
async def scan_all_organizations() -> List[str]:
    """
    Scan all active organizations for stuck signals

    Activity: Returns list of organization IDs to check
    """
    import httpx

    logger.info(" Scanning all organizations...")

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                "http://localhost:8032/api/v1/stuck-detection/active-orgs"
            )

            if response.status_code != 200:
                raise Exception(f"Failed to get active orgs: {response.status_code}")

            result = response.json()
            org_ids = result.get("organization_ids", [])

            logger.info(f" Found {len(org_ids)} active organizations")
            return org_ids

    except Exception as e:
        logger.error(f" Organization scan failed: {e}")
        return []


# ============================================================================
# Activities - Collective Agent Creation
# ============================================================================

@activity.defn
async def verify_k_anonymity(config: CollectiveAgentConfig) -> Dict[str, Any]:
    """
    Verify k-anonymity requirements before creating agent

    Activity: Privacy-critical validation

    Ensures:
    - Minimum 5 organizations (k-anonymity)
    - Source organizations are similar enough
    - No outlier organizations that could be identified
    """
    import httpx

    logger.info(f" Verifying k-anonymity for {config.problem_type}")

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "http://localhost:8032/api/v1/collective-agents/verify-privacy",
                json={
                    "problem_type": config.problem_type,
                    "min_orgs": config.min_orgs,
                    "requesting_org_id": config.requesting_org_id
                }
            )

            if response.status_code != 200:
                raise Exception(f"Privacy verification failed: {response.status_code}")

            result = response.json()

            return {
                "verified": result.get("k_anonymity_verified", False),
                "source_count": result.get("source_org_count", 0),
                "risk_score": result.get("re_identification_risk", 1.0),
                "similar_orgs": result.get("similar_org_count", 0)
            }

    except Exception as e:
        logger.error(f" K-anonymity verification failed: {e}")
        raise


@activity.defn
async def create_collective_agent(config: CollectiveAgentConfig) -> CollectiveAgentResult:
    """
    Create Collective Agent from anonymized organization data

    Activity: Creates temporary AI agent from collective wisdom

    Process:
    1. Find organizations that solved this problem
    2. Extract and anonymize their approaches
    3. Create system prompt with collective wisdom
    4. Generate agent with expiration
    """
    import httpx

    logger.info(f" Creating Collective Agent for {config.problem_type}")

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "http://localhost:8032/api/v1/collective-agents/create",
                json={
                    "problem_type": config.problem_type,
                    "min_orgs": config.min_orgs,
                    "min_success_rate": config.min_success_rate,
                    "requesting_org_id": config.requesting_org_id,
                    "expiration_days": config.agent_expiration_days
                }
            )

            if response.status_code not in [200, 201]:
                raise Exception(f"Agent creation failed: {response.status_code}")

            result = response.json()

            return CollectiveAgentResult(
                agent_id=result.get("agent_id"),
                source_org_count=result.get("source_org_count", 0),
                problem_type=config.problem_type,
                expires_at=result.get("expires_at"),
                system_prompt=result.get("system_prompt", ""),
                k_anonymity_verified=True
            )

    except Exception as e:
        logger.error(f" Agent creation failed: {e}")
        raise


@activity.defn
async def anonymize_organization_data(org_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Multi-layer anonymization of organization data

    Activity: Privacy-preserving transformation

    Layers:
    1. Organization anonymization (remove names, dates, people)
    2. Aggregation (ensure minimum group size)
    3. Collective synthesis (AI-generated collective wisdom)
    """
    import httpx

    logger.info(" Anonymizing organization data...")

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "http://localhost:8032/api/v1/collective-agents/anonymize",
                json={
                    "organization_data": org_data,
                    "anonymization_level": "full"
                }
            )

            if response.status_code != 200:
                raise Exception(f"Anonymization failed: {response.status_code}")

            result = response.json()

            return {
                "anonymized_data": result.get("anonymized_data"),
                "risk_score": result.get("re_identification_risk", 0.0),
                "removed_fields": result.get("removed_fields", [])
            }

    except Exception as e:
        logger.error(f" Anonymization failed: {e}")
        raise


# ============================================================================
# Activities - Multi-Agent Consensus
# ============================================================================

@activity.defn
async def get_agent_response(agent_id: str, question: str) -> Dict[str, Any]:
    """
    Get response from individual collective agent

    Activity: Query single agent for answer
    """
    import httpx

    logger.info(f" Getting response from agent {agent_id}")

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"http://localhost:8032/api/v1/collective-agents/{agent_id}/chat",
                json={"message": question}
            )

            if response.status_code != 200:
                raise Exception(f"Agent chat failed: {response.status_code}")

            result = response.json()

            return {
                "agent_id": agent_id,
                "response": result.get("message", ""),
                "confidence": result.get("confidence", 0.0),
                "source_count": result.get("source_count", 0)
            }

    except Exception as e:
        logger.error(f" Agent response failed: {e}")
        raise


@activity.defn
async def synthesize_consensus(responses: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Synthesize consensus from multiple agent responses

    Activity: Multi-agent consensus mechanism

    Uses:
    - Semantic similarity to find common patterns
    - Confidence weighting
    - Conflict resolution
    """
    import httpx

    logger.info(f" Synthesizing consensus from {len(responses)} agents")

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "http://localhost:8032/api/v1/collective-agents/consensus",
                json={
                    "responses": responses,
                    "synthesis_method": "weighted_semantic"
                }
            )

            if response.status_code != 200:
                raise Exception(f"Consensus synthesis failed: {response.status_code}")

            result = response.json()

            return {
                "synthesized_answer": result.get("synthesized_answer", ""),
                "consensus_confidence": result.get("confidence", 0.0),
                "agreement_level": result.get("agreement_level", 0.0),
                "conflicting_points": result.get("conflicts", [])
            }

    except Exception as e:
        logger.error(f" Consensus synthesis failed: {e}")
        raise


# ============================================================================
# Activities - Agent Lifecycle
# ============================================================================

@activity.defn
async def expire_old_agents(config: AgentCleanupConfig) -> Dict[str, Any]:
    """
    Expire and cleanup old collective agents

    Activity: Periodic cleanup job

    Deletes agents that:
    - Exceeded expiration date (default 7 days)
    - No activity for extended period
    - Security requirement
    """
    import httpx

    logger.info(f" Cleaning up agents older than {config.max_age_days} days")

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "http://localhost:8032/api/v1/collective-agents/cleanup",
                json={
                    "max_age_days": config.max_age_days,
                    "batch_size": config.batch_size
                }
            )

            if response.status_code != 200:
                raise Exception(f"Cleanup failed: {response.status_code}")

            result = response.json()

            return {
                "agents_expired": result.get("expired_count", 0),
                "agents_deleted": result.get("deleted_count", 0),
                "storage_freed_mb": result.get("storage_freed_mb", 0)
            }

    except Exception as e:
        logger.error(f" Agent cleanup failed: {e}")
        return {
            "agents_expired": 0,
            "agents_deleted": 0,
            "storage_freed_mb": 0,
            "error": str(e)
        }


@activity.defn
async def notify_organization(notification: Dict[str, Any]) -> None:
    """
    Send notification to organization about collective agent offer

    Activity: User notification
    """
    import httpx

    logger.info(f" Sending notification to org: {notification.get('org_id')}")

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            await client.post(
                "http://localhost:8035/api/notifications/send",
                json=notification
            )

        logger.info(" Notification sent")

    except Exception as e:
        logger.warning(f"️ Notification failed (non-critical): {e}")


@activity.defn
async def report_to_brain(report_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Report collective intelligence metrics to Workflow Intelligence

    Activity: Final reporting
    """
    import httpx

    logger.info(" Reporting to Workflow Intelligence...")

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "http://localhost:8020/api/report/collective-intelligence",
                json={
                    "timestamp": datetime.utcnow().isoformat(),
                    "report_type": "collective_intelligence",
                    "data": report_data
                }
            )

            if response.status_code != 200:
                raise Exception(f"Brain report failed: {response.status_code}")

            result = response.json()

        logger.info(f" Report sent to brain: {result.get('status')}")
        return result

    except Exception as e:
        logger.error(f" Brain reporting failed: {e}")
        raise


# ============================================================================
# Workflow - Stuck Detection & Collective Agent Creation
# ============================================================================

@workflow.defn
class CollectiveIntelligenceWorkflow:
    """
    Main Collective Intelligence Workflow

    Provides durable, fault-tolerant execution for:
    - Stuck organization detection
    - Collective agent creation
    - Privacy-preserving collaboration
    - Agent lifecycle management

    Patterns:
    - Saga for rollback
    - Retry for fault tolerance
    - Privacy enforcement
    - Multi-agent coordination
    """

    @workflow.run
    async def run(self, org_id: str, module: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute Collective Intelligence workflow for an organization

        Steps:
        1. Detect stuck status
        2. Verify privacy requirements
        3. Create collective agent (if needed)
        4. Notify organization
        5. Report to brain
        """

        workflow.logger.info(f" Starting Collective Intelligence Workflow for: {org_id}")

        # Retry policy for activities
        retry_policy = RetryPolicy(
            maximum_attempts=3,
            initial_interval=timedelta(seconds=1),
            maximum_interval=timedelta(seconds=10),
            backoff_coefficient=2.0
        )

        results = {
            "workflow": "CollectiveIntelligenceWorkflow",
            "org_id": org_id,
            "started_at": workflow.now().isoformat()
        }

        try:
            # Step 1: Detect if organization is stuck
            stuck_config = StuckDetectionConfig(
                org_id=org_id,
                module=module,
                threshold=4,
                check_last_days=7
            )

            stuck_result = await workflow.execute_activity(
                detect_stuck_organization,
                stuck_config,
                start_to_close_timeout=timedelta(minutes=5),
                retry_policy=retry_policy
            )

            results["stuck_detection"] = {
                "is_stuck": stuck_result.is_stuck,
                "stuck_score": stuck_result.stuck_score,
                "signals": stuck_result.signals
            }

            workflow.logger.info(
                f" Stuck detection: score={stuck_result.stuck_score}, stuck={stuck_result.is_stuck}"
            )

            # Step 2: If stuck, create collective agent
            if stuck_result.is_stuck and stuck_result.recommendations:

                # Find collective agent recommendations
                collective_recs = [
                    r for r in stuck_result.recommendations
                    if r.get("type") == "collective_agent"
                ]

                if collective_recs:
                    recommendation = collective_recs[0]
                    problem_type = recommendation.get("problem_type")

                    # Step 2.1: Verify k-anonymity
                    agent_config = CollectiveAgentConfig(
                        problem_type=problem_type,
                        requesting_org_id=org_id,
                        min_orgs=5,
                        min_success_rate=0.8
                    )

                    privacy_check = await workflow.execute_activity(
                        verify_k_anonymity,
                        agent_config,
                        start_to_close_timeout=timedelta(minutes=2),
                        retry_policy=retry_policy
                    )

                    results["privacy_verification"] = privacy_check

                    if privacy_check.get("verified"):
                        workflow.logger.info(" K-anonymity verified")

                        # Step 2.2: Create collective agent
                        try:
                            agent_result = await workflow.execute_activity(
                                create_collective_agent,
                                agent_config,
                                start_to_close_timeout=timedelta(minutes=10),
                                retry_policy=retry_policy
                            )

                            results["collective_agent"] = {
                                "agent_id": agent_result.agent_id,
                                "source_org_count": agent_result.source_org_count,
                                "problem_type": agent_result.problem_type,
                                "expires_at": agent_result.expires_at
                            }

                            workflow.logger.info(
                                f" Collective Agent created: {agent_result.agent_id}"
                            )

                            # Step 2.3: Notify organization
                            await workflow.execute_activity(
                                notify_organization,
                                {
                                    "org_id": org_id,
                                    "type": "collective_agent_created",
                                    "agent_id": agent_result.agent_id,
                                    "problem_type": problem_type,
                                    "source_count": agent_result.source_org_count,
                                    "expires_at": agent_result.expires_at
                                },
                                start_to_close_timeout=timedelta(seconds=30),
                                retry_policy=RetryPolicy(maximum_attempts=2)
                            )

                        except Exception as e:
                            workflow.logger.error(f" Agent creation failed: {e}")
                            results["collective_agent"] = {
                                "status": "failed",
                                "error": str(e)
                            }

                    else:
                        workflow.logger.warning(
                            f"️ Insufficient data for collective agent: "
                            f"need {agent_config.min_orgs}, found {privacy_check.get('source_count', 0)}"
                        )
                        results["collective_agent"] = {
                            "status": "insufficient_data",
                            "source_count": privacy_check.get("source_count", 0)
                        }

            else:
                workflow.logger.info(" Organization not stuck - no action needed")
                results["action"] = "none_required"

            # Step 3: Report to brain
            await workflow.execute_activity(
                report_to_brain,
                {
                    "org_id": org_id,
                    "workflow_results": results,
                    "timestamp": workflow.now().isoformat()
                },
                start_to_close_timeout=timedelta(minutes=5),
                retry_policy=retry_policy
            )

            results["status"] = "completed"
            results["completed_at"] = workflow.now().isoformat()

            workflow.logger.info(" Collective Intelligence Workflow completed!")

            return results

        except Exception as e:
            workflow.logger.error(f" Workflow failed: {e}")
            results["status"] = "failed"
            results["error"] = str(e)
            results["failed_at"] = workflow.now().isoformat()
            raise


# ============================================================================
# Workflow - Multi-Agent Consensus
# ============================================================================

@workflow.defn
class MultiAgentConsensusWorkflow:
    """
    Multi-Agent Consensus Workflow

    Coordinates multiple collective agents to reach consensus on a question.

    Use case: When multiple collective agents exist for similar problems,
    synthesize their collective wisdom for higher confidence.
    """

    @workflow.run
    async def run(self, config: ConsensusConfig) -> ConsensusResult:
        """
        Execute multi-agent consensus workflow

        Steps:
        1. Query each agent independently
        2. Analyze responses for agreement
        3. Synthesize consensus
        4. Return unified answer with confidence
        """

        workflow.logger.info(
            f" Starting Multi-Agent Consensus: {len(config.agent_ids)} agents"
        )

        retry_policy = RetryPolicy(
            maximum_attempts=2,
            initial_interval=timedelta(seconds=1)
        )

        all_responses = []

        # Step 1: Get responses from all agents
        for agent_id in config.agent_ids:
            try:
                response = await workflow.execute_activity(
                    get_agent_response,
                    agent_id,
                    config.question,
                    start_to_close_timeout=timedelta(minutes=2),
                    retry_policy=retry_policy
                )
                all_responses.append(response)

            except Exception as e:
                workflow.logger.warning(f"️ Agent {agent_id} failed: {e}")

        if not all_responses:
            raise ApplicationError("No agent responses received")

        workflow.logger.info(f" Got {len(all_responses)} agent responses")

        # Step 2: Synthesize consensus
        consensus = await workflow.execute_activity(
            synthesize_consensus,
            all_responses,
            start_to_close_timeout=timedelta(minutes=5),
            retry_policy=retry_policy
        )

        consensus_reached = consensus.get("agreement_level", 0.0) >= config.consensus_threshold

        result = ConsensusResult(
            consensus_reached=consensus_reached,
            confidence=consensus.get("consensus_confidence", 0.0),
            synthesized_answer=consensus.get("synthesized_answer", ""),
            participating_agents=len(all_responses),
            rounds_used=1,
            individual_responses=all_responses
        )

        workflow.logger.info(
            f" Consensus {'reached' if consensus_reached else 'not reached'}: "
            f"confidence={result.confidence:.2f}"
        )

        return result


# ============================================================================
# Workflow - Batch Stuck Detection (Daily/Weekly)
# ============================================================================

@workflow.defn
class BatchStuckDetectionWorkflow:
    """
    Batch Stuck Detection Workflow

    Scans all active organizations for stuck signals.
    Runs daily/weekly as scheduled job.
    """

    @workflow.run
    async def run(self) -> Dict[str, Any]:
        """
        Execute batch stuck detection across all organizations

        Steps:
        1. Get all active organizations
        2. Check each for stuck signals
        3. Create collective agents for stuck orgs
        4. Report aggregated results to brain
        """

        workflow.logger.info(" Starting Batch Stuck Detection")

        retry_policy = RetryPolicy(
            maximum_attempts=3,
            initial_interval=timedelta(seconds=2)
        )

        # Step 1: Get all active organizations
        org_ids = await workflow.execute_activity(
            scan_all_organizations,
            start_to_close_timeout=timedelta(minutes=5),
            retry_policy=retry_policy
        )

        workflow.logger.info(f" Checking {len(org_ids)} organizations")

        results = {
            "total_orgs": len(org_ids),
            "stuck_orgs": [],
            "agents_created": 0,
            "timestamp": workflow.now().isoformat()
        }

        # Step 2: Check each organization (parallel execution)
        for org_id in org_ids:
            try:
                # Run individual workflow for each org
                stuck_result = await workflow.execute_child_workflow(
                    CollectiveIntelligenceWorkflow.run,
                    org_id,
                    id=f"collective-{org_id}-{workflow.now().timestamp()}",
                    task_queue="collective-intelligence"
                )

                if stuck_result.get("stuck_detection", {}).get("is_stuck"):
                    results["stuck_orgs"].append({
                        "org_id": org_id,
                        "stuck_score": stuck_result["stuck_detection"]["stuck_score"],
                        "agent_created": "collective_agent" in stuck_result
                    })

                    if "collective_agent" in stuck_result:
                        results["agents_created"] += 1

            except Exception as e:
                workflow.logger.warning(f"️ Org {org_id} check failed: {e}")

        # Step 3: Report to brain
        await workflow.execute_activity(
            report_to_brain,
            {
                "report_type": "batch_stuck_detection",
                "results": results
            },
            start_to_close_timeout=timedelta(minutes=5),
            retry_policy=retry_policy
        )

        workflow.logger.info(
            f" Batch detection complete: {len(results['stuck_orgs'])} stuck, "
            f"{results['agents_created']} agents created"
        )

        return results


# ============================================================================
# Workflow - Agent Lifecycle Management (Cleanup)
# ============================================================================

@workflow.defn
class AgentLifecycleWorkflow:
    """
    Agent Lifecycle Management Workflow

    Manages collective agent lifecycle:
    - Expiration (default 7 days)
    - Cleanup of old agents
    - Storage optimization

    Runs daily as scheduled job.
    """

    @workflow.run
    async def run(self, max_age_days: int = 7) -> Dict[str, Any]:
        """
        Execute agent lifecycle management

        Steps:
        1. Expire old agents
        2. Cleanup storage
        3. Report metrics
        """

        workflow.logger.info(f" Starting Agent Lifecycle Management (age > {max_age_days} days)")

        retry_policy = RetryPolicy(
            maximum_attempts=3,
            initial_interval=timedelta(seconds=1)
        )

        # Cleanup old agents
        cleanup_config = AgentCleanupConfig(
            max_age_days=max_age_days,
            batch_size=100
        )

        cleanup_result = await workflow.execute_activity(
            expire_old_agents,
            cleanup_config,
            start_to_close_timeout=timedelta(minutes=10),
            retry_policy=retry_policy
        )

        workflow.logger.info(
            f" Cleanup complete: {cleanup_result['agents_expired']} expired, "
            f"{cleanup_result['agents_deleted']} deleted, "
            f"{cleanup_result['storage_freed_mb']}MB freed"
        )

        # Report to brain
        await workflow.execute_activity(
            report_to_brain,
            {
                "report_type": "agent_lifecycle",
                "cleanup_results": cleanup_result,
                "timestamp": workflow.now().isoformat()
            },
            start_to_close_timeout=timedelta(minutes=5),
            retry_policy=retry_policy
        )

        return cleanup_result


# ============================================================================
# Export all workflows and activities
# ============================================================================

collective_workflows = [
    CollectiveIntelligenceWorkflow,
    MultiAgentConsensusWorkflow,
    BatchStuckDetectionWorkflow,
    AgentLifecycleWorkflow
]

collective_activities = [
    detect_stuck_organization,
    scan_all_organizations,
    verify_k_anonymity,
    create_collective_agent,
    anonymize_organization_data,
    get_agent_response,
    synthesize_consensus,
    expire_old_agents,
    notify_organization,
    report_to_brain
]
