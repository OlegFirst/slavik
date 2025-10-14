"""
Expertise Center Workflow - Domain Expert Orchestration
=========================================================

Temporal workflow for coordinating domain experts and tactical assistants.

Orchestrates:
- 12 Tactical Assistants (BIA, Risk, Compliance, etc.)
- 10 Strategic Analyzers
- Multi-domain expert collaboration
- Knowledge base integration

Integrates with:
- Expertise Center Service (port 8035)
- AI Foundation (RAG/LLM)
- Knowledge Base
- EventBus (audit trail)
"""

import logging
from datetime import timedelta
from typing import Dict, Any, List, Optional
import httpx

from temporalio import workflow, activity
from temporalio.common import RetryPolicy

logger = logging.getLogger(__name__)

# Global configuration
_expertise_service_url: str = "http://localhost:8035"
_ai_foundation_url: str = "http://localhost:8040"


def inject_dependencies(expertise_service_url: str, ai_foundation_url: str):
    """Inject dependencies for activities (called by Temporal worker)."""
    global _expertise_service_url, _ai_foundation_url
    _expertise_service_url = expertise_service_url
    _ai_foundation_url = ai_foundation_url
    logger.info(f"Dependencies injected: expertise={expertise_service_url}, ai_foundation={ai_foundation_url}")


# ==================== Activity Definitions ====================

@activity.defn
async def expertise_activity_route_to_expert(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Route query to appropriate tactical assistant.

    Determines which expert should handle the query based on:
    - Query intent
    - Domain
    - Context
    """
    logger.info(f"Routing query to expert: {input_data.get('query')[:50]}...")

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{_expertise_service_url}/expertise/query",
                json={
                    'expert_type': input_data.get('expert_type', 'bia_specialist'),
                    'query': input_data['query'],
                    'context': input_data.get('context', {}),
                    'organization_id': input_data.get('organization_id')
                }
            )

            if response.status_code != 200:
                raise Exception(f"Expertise Center returned {response.status_code}: {response.text}")

            result = response.json()

        return {
            "stage": "route_to_expert",
            "expert": result['expert'],
            "response": result['response'],
            "confidence": result.get('confidence', 0.0),
            "sources": result.get('sources', []),
            "metadata": result.get('metadata', {}),
            "status": "completed"
        }

    except httpx.TimeoutException:
        logger.error("Expertise Center timeout")
        return {
            "stage": "route_to_expert",
            "status": "failed",
            "error": "Service timeout"
        }
    except Exception as e:
        logger.error(f"Expert routing failed: {str(e)}")
        return {
            "stage": "route_to_expert",
            "status": "failed",
            "error": str(e)
        }


@activity.defn
async def expertise_activity_analyze_with_analyzer(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run strategic analyzer (Compliance, Risk, Governance, etc.).

    Uses:
    - Expertise Center analyzers
    - AI Foundation for deep analysis
    """
    logger.info(f"Running analyzer: {input_data.get('analyzer_type')}")

    try:
        analyzer_type = input_data['analyzer_type']

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{_expertise_service_url}/expertise/analyzers/{analyzer_type}/analyze",
                json={
                    'data': input_data.get('data', {}),
                    'context': input_data.get('context', {}),
                    'organization_id': input_data.get('organization_id')
                }
            )

            if response.status_code != 200:
                raise Exception(f"Analyzer returned {response.status_code}: {response.text}")

            result = response.json()

        return {
            "stage": "analyze",
            "analyzer": analyzer_type,
            "insights": result.get('insights', []),
            "recommendations": result.get('recommendations', []),
            "confidence": result.get('confidence', 0.0),
            "metadata": result.get('metadata', {}),
            "status": "completed"
        }

    except Exception as e:
        logger.error(f"Analyzer failed: {str(e)}")
        return {
            "stage": "analyze",
            "status": "failed",
            "error": str(e)
        }


@activity.defn
async def expertise_activity_collaborate_experts(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Coordinate multiple experts for complex queries.

    Example: BIA Specialist + Risk Analyst + Compliance Copilot working together
    """
    logger.info(f"Coordinating {len(input_data.get('experts', []))} experts")

    try:
        experts = input_data.get('experts', [])
        query = input_data['query']
        context = input_data.get('context', {})

        # Collect responses from all experts
        expert_responses = []

        async with httpx.AsyncClient(timeout=30.0) as client:
            for expert_type in experts:
                try:
                    response = await client.post(
                        f"{_expertise_service_url}/expertise/query",
                        json={
                            'expert_type': expert_type,
                            'query': query,
                            'context': context,
                            'organization_id': input_data.get('organization_id')
                        }
                    )

                    if response.status_code == 200:
                        expert_data = response.json()
                        expert_responses.append({
                            'expert': expert_type,
                            'response': expert_data['response'],
                            'confidence': expert_data.get('confidence', 0.0)
                        })
                    else:
                        logger.warning(f"Expert {expert_type} failed: {response.status_code}")

                except Exception as e:
                    logger.warning(f"Expert {expert_type} error: {str(e)}")
                    continue

        # Synthesize responses (could use AI to combine)
        combined_response = "\n\n".join([
            f"**{er['expert']}** (confidence: {er['confidence']}):\n{er['response']}"
            for er in expert_responses
        ])

        avg_confidence = sum(er['confidence'] for er in expert_responses) / len(expert_responses) if expert_responses else 0.0

        return {
            "stage": "collaborate",
            "experts_consulted": len(expert_responses),
            "expert_responses": expert_responses,
            "combined_response": combined_response,
            "avg_confidence": avg_confidence,
            "status": "completed"
        }

    except Exception as e:
        logger.error(f"Expert collaboration failed: {str(e)}")
        return {
            "stage": "collaborate",
            "status": "failed",
            "error": str(e)
        }


@activity.defn
async def expertise_activity_validate_with_knowledge(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate expert response against knowledge base.

    Uses:
    - ISO standards
    - Best practices
    - Case library
    """
    logger.info("Validating response with knowledge base")

    try:
        response_to_validate = input_data.get('response', '')

        # Call AI Foundation for validation
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{_ai_foundation_url}/ai/rag/validate",
                json={
                    'text': response_to_validate,
                    'domain': input_data.get('domain', 'bcm'),
                    'standard': input_data.get('standard', 'iso22301')
                }
            )

            if response.status_code != 200:
                logger.warning(f"Validation service returned {response.status_code}")
                # Continue without validation
                return {
                    "stage": "validate",
                    "validation_score": 0.5,
                    "issues": [],
                    "status": "completed_without_validation"
                }

            result = response.json()

        return {
            "stage": "validate",
            "validation_score": result.get('score', 0.0),
            "issues": result.get('issues', []),
            "suggestions": result.get('suggestions', []),
            "status": "completed"
        }

    except Exception as e:
        logger.warning(f"Validation failed (non-critical): {str(e)}")
        return {
            "stage": "validate",
            "validation_score": 0.5,
            "issues": [],
            "status": "completed_without_validation"
        }


@activity.defn
async def expertise_activity_generate_recommendations(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate actionable recommendations based on expert analysis.

    Uses:
    - Expert responses
    - Analyzer insights
    - Best practices
    """
    logger.info("Generating recommendations")

    try:
        # Collect all insights and responses
        expert_response = input_data.get('expert_response', {})
        analyzer_insights = input_data.get('analyzer_insights', [])

        # Use AI Foundation to generate recommendations
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{_ai_foundation_url}/ai/llm/generate",
                json={
                    'prompt': f"""Based on the following expert analysis, generate 3-5 actionable recommendations:

Expert Response: {expert_response.get('response', '')}

Analyzer Insights: {analyzer_insights}

Generate specific, prioritized recommendations with implementation steps.""",
                    'max_tokens': 1000
                }
            )

            if response.status_code != 200:
                raise Exception(f"AI Foundation returned {response.status_code}")

            result = response.json()

        recommendations_text = result.get('text', '')

        # Parse recommendations (simple split, could be enhanced)
        recommendations = [
            r.strip() for r in recommendations_text.split('\n')
            if r.strip() and len(r.strip()) > 10
        ]

        return {
            "stage": "generate_recommendations",
            "recommendations": recommendations[:5],  # Top 5
            "full_text": recommendations_text,
            "status": "completed"
        }

    except Exception as e:
        logger.error(f"Recommendation generation failed: {str(e)}")
        return {
            "stage": "generate_recommendations",
            "recommendations": [],
            "status": "failed",
            "error": str(e)
        }


# ==================== Workflow Definition ====================

@workflow.defn
class ExpertiseWorkflow:
    """
    Expertise Center Workflow - Multi-Expert Orchestration.

    Workflows:
    1. Single Expert Query
    2. Multi-Expert Collaboration
    3. Expert + Analyzer
    4. Full Analysis with Recommendations

    Features:
    - Automatic expert routing
    - Multi-expert collaboration
    - Knowledge validation
    - Actionable recommendations
    """

    @workflow.run
    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Expertise workflow."""
        workflow.logger.info(f"Starting Expertise workflow: {input_data.get('workflow_type', 'single_expert')}")

        # Retry policy
        retry_policy = RetryPolicy(
            initial_interval=timedelta(seconds=1),
            maximum_interval=timedelta(seconds=30),
            maximum_attempts=3
        )

        results = {
            "workflow": "ExpertiseWorkflow",
            "workflow_type": input_data.get("workflow_type", "single_expert"),
            "organization_id": input_data.get("organization_id"),
            "started_at": workflow.now().isoformat(),
            "stages": []
        }

        try:
            workflow_type = input_data.get("workflow_type", "single_expert")

            if workflow_type == "single_expert":
                return await self._single_expert_workflow(input_data, retry_policy, results)

            elif workflow_type == "multi_expert":
                return await self._multi_expert_workflow(input_data, retry_policy, results)

            elif workflow_type == "expert_analyzer":
                return await self._expert_analyzer_workflow(input_data, retry_policy, results)

            elif workflow_type == "full_analysis":
                return await self._full_analysis_workflow(input_data, retry_policy, results)

            else:
                raise ValueError(f"Unknown workflow type: {workflow_type}")

        except Exception as e:
            workflow.logger.error(f"Expertise workflow failed: {str(e)}")
            results["status"] = "failed"
            results["error"] = str(e)
            results["failed_at"] = workflow.now().isoformat()
            raise

    async def _single_expert_workflow(
        self,
        input_data: Dict[str, Any],
        retry_policy: RetryPolicy,
        results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Single expert query workflow."""
        workflow.logger.info("Executing single expert workflow")

        # Route to expert
        stage1 = await workflow.execute_activity(
            expertise_activity_route_to_expert,
            input_data,
            start_to_close_timeout=timedelta(minutes=3),
            retry_policy=retry_policy
        )
        results["stages"].append(stage1)

        # Validate with knowledge
        stage2_input = {**input_data, "response": stage1.get("response")}
        stage2 = await workflow.execute_activity(
            expertise_activity_validate_with_knowledge,
            stage2_input,
            start_to_close_timeout=timedelta(minutes=2),
            retry_policy=retry_policy
        )
        results["stages"].append(stage2)

        results["status"] = "completed"
        results["completed_at"] = workflow.now().isoformat()
        results["expert_response"] = stage1.get("response")
        results["validation_score"] = stage2.get("validation_score")

        return results

    async def _multi_expert_workflow(
        self,
        input_data: Dict[str, Any],
        retry_policy: RetryPolicy,
        results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Multi-expert collaboration workflow."""
        workflow.logger.info("Executing multi-expert collaboration workflow")

        # Collaborate experts
        stage1 = await workflow.execute_activity(
            expertise_activity_collaborate_experts,
            input_data,
            start_to_close_timeout=timedelta(minutes=5),
            retry_policy=retry_policy
        )
        results["stages"].append(stage1)

        # Validate combined response
        stage2_input = {**input_data, "response": stage1.get("combined_response")}
        stage2 = await workflow.execute_activity(
            expertise_activity_validate_with_knowledge,
            stage2_input,
            start_to_close_timeout=timedelta(minutes=2),
            retry_policy=retry_policy
        )
        results["stages"].append(stage2)

        results["status"] = "completed"
        results["completed_at"] = workflow.now().isoformat()
        results["expert_responses"] = stage1.get("expert_responses")
        results["combined_response"] = stage1.get("combined_response")
        results["validation_score"] = stage2.get("validation_score")

        return results

    async def _expert_analyzer_workflow(
        self,
        input_data: Dict[str, Any],
        retry_policy: RetryPolicy,
        results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Expert + Analyzer workflow."""
        workflow.logger.info("Executing expert + analyzer workflow")

        # Route to expert
        stage1 = await workflow.execute_activity(
            expertise_activity_route_to_expert,
            input_data,
            start_to_close_timeout=timedelta(minutes=3),
            retry_policy=retry_policy
        )
        results["stages"].append(stage1)

        # Run analyzer
        stage2_input = {
            **input_data,
            "analyzer_type": input_data.get("analyzer_type", "compliance_analyzer"),
            "data": {"expert_response": stage1.get("response")}
        }
        stage2 = await workflow.execute_activity(
            expertise_activity_analyze_with_analyzer,
            stage2_input,
            start_to_close_timeout=timedelta(minutes=5),
            retry_policy=retry_policy
        )
        results["stages"].append(stage2)

        # Generate recommendations
        stage3_input = {
            **input_data,
            "expert_response": stage1,
            "analyzer_insights": stage2.get("insights", [])
        }
        stage3 = await workflow.execute_activity(
            expertise_activity_generate_recommendations,
            stage3_input,
            start_to_close_timeout=timedelta(minutes=3),
            retry_policy=retry_policy
        )
        results["stages"].append(stage3)

        results["status"] = "completed"
        results["completed_at"] = workflow.now().isoformat()
        results["expert_response"] = stage1.get("response")
        results["analyzer_insights"] = stage2.get("insights")
        results["recommendations"] = stage3.get("recommendations")

        return results

    async def _full_analysis_workflow(
        self,
        input_data: Dict[str, Any],
        retry_policy: RetryPolicy,
        results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Full analysis with multi-expert + analyzers + recommendations."""
        workflow.logger.info("Executing full analysis workflow")

        # Multi-expert collaboration
        stage1 = await workflow.execute_activity(
            expertise_activity_collaborate_experts,
            input_data,
            start_to_close_timeout=timedelta(minutes=5),
            retry_policy=retry_policy
        )
        results["stages"].append(stage1)

        # Run analyzers (multiple)
        analyzers = input_data.get("analyzers", ["compliance_analyzer", "risk_analyzer"])
        analyzer_results = []

        for analyzer_type in analyzers:
            stage_input = {
                **input_data,
                "analyzer_type": analyzer_type,
                "data": {"expert_responses": stage1.get("expert_responses")}
            }
            analyzer_result = await workflow.execute_activity(
                expertise_activity_analyze_with_analyzer,
                stage_input,
                start_to_close_timeout=timedelta(minutes=5),
                retry_policy=retry_policy
            )
            analyzer_results.append(analyzer_result)
            results["stages"].append(analyzer_result)

        # Generate recommendations
        stage3_input = {
            **input_data,
            "expert_response": stage1,
            "analyzer_insights": [
                insight
                for ar in analyzer_results
                for insight in ar.get("insights", [])
            ]
        }
        stage3 = await workflow.execute_activity(
            expertise_activity_generate_recommendations,
            stage3_input,
            start_to_close_timeout=timedelta(minutes=3),
            retry_policy=retry_policy
        )
        results["stages"].append(stage3)

        # Validate final output
        stage4_input = {
            **input_data,
            "response": stage3.get("full_text")
        }
        stage4 = await workflow.execute_activity(
            expertise_activity_validate_with_knowledge,
            stage4_input,
            start_to_close_timeout=timedelta(minutes=2),
            retry_policy=retry_policy
        )
        results["stages"].append(stage4)

        results["status"] = "completed"
        results["completed_at"] = workflow.now().isoformat()
        results["expert_responses"] = stage1.get("expert_responses")
        results["analyzer_results"] = [
            {"analyzer": ar["analyzer"], "insights": ar.get("insights", [])}
            for ar in analyzer_results
        ]
        results["recommendations"] = stage3.get("recommendations")
        results["validation_score"] = stage4.get("validation_score")

        return results


# Export activities for registration
expertise_activities = [
    expertise_activity_route_to_expert,
    expertise_activity_analyze_with_analyzer,
    expertise_activity_collaborate_experts,
    expertise_activity_validate_with_knowledge,
    expertise_activity_generate_recommendations
]
