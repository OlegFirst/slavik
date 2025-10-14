"""
Scenario Orchestrator Adapter
Интеграция с существующим Scenario Orchestrator для AI-генерации L4 сценариев
"""

import httpx
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import yaml

logger = logging.getLogger(__name__)

# Configuration
SCENARIO_ORCHESTRATOR_URL = "http://scenario-orchestrator:8085"


class ScenarioOrchestratorAdapter:
    """
    Adapter для интеграции с Scenario Orchestrator
    Конвертирует AI-generated exercise scenarios → L4 YAML формат
    """

    def __init__(self, orchestrator_url: str = SCENARIO_ORCHESTRATOR_URL):
        self.orchestrator_url = orchestrator_url

    async def generate_l4_scenario(
        self,
        category: str,
        complexity: int = 3,
        duration_hours: int = 4,
        participants: int = 10,
        affected_systems: Optional[List[str]] = None,
        custom_objectives: Optional[List[str]] = None,
        organization_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate L4 User Scenario using AI через Scenario Orchestrator

        Args:
            category: epidemic|blackout|cyber|supply|natural|terrorism
            complexity: 1-5 scale
            duration_hours: Exercise duration
            participants: Number of participants
            affected_systems: List of affected systems
            custom_objectives: Custom exercise objectives
            organization_context: Organization context

        Returns:
            L4 scenario in YAML format (as dict)
        """
        try:
            logger.info(f"Generating L4 scenario: {category} (complexity: {complexity})")

            # Call Scenario Orchestrator
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.orchestrator_url}/scenarios/generate",
                    json={
                        "category": category,
                        "complexity": complexity,
                        "duration_hours": duration_hours,
                        "participants": participants,
                        "affected_systems": affected_systems or [],
                        "custom_objectives": custom_objectives or [],
                        "organization_context": organization_context
                    }
                )

                if response.status_code != 200:
                    raise Exception(f"Scenario Orchestrator error: {response.status_code}")

                orchestrator_result = response.json()

            # Convert to L4 YAML format
            l4_scenario = self._convert_to_l4_yaml(
                orchestrator_result,
                category,
                complexity,
                duration_hours,
                participants
            )

            return l4_scenario

        except Exception as e:
            logger.error(f"Failed to generate L4 scenario: {e}")
            raise

    def _convert_to_l4_yaml(
        self,
        orchestrator_result: Dict[str, Any],
        category: str,
        complexity: int,
        duration_hours: int,
        participants: int
    ) -> Dict[str, Any]:
        """
        Convert Scenario Orchestrator JSON → L4 YAML format

        Args:
            orchestrator_result: Result from Scenario Orchestrator
            category: Exercise category
            complexity: Complexity level
            duration_hours: Duration
            participants: Participant count

        Returns:
            L4 scenario dict (YAML-compatible)
        """
        scenario_id = orchestrator_result.get("scenario_id", "unknown")
        title = orchestrator_result.get("title", f"{category.title()} BCM Exercise")

        # Map category to pillar
        pillar_mapping = {
            "cyber": "security",
            "supply": "reliability",
            "blackout": "operational_excellence",
            "epidemic": "operational_excellence",
            "natural": "reliability",
            "terrorism": "security"
        }
        pillar = pillar_mapping.get(category, "operational_excellence")

        # Build L4 scenario
        l4_scenario = {
            "meta": {
                "id": f"l4-user-exercise-{category}-{scenario_id}",
                "version": "1.0.0",
                "level": 4,
                "type": "user_workflow",
                "subtype": "bcm_exercise",
                "pillar": pillar,
                "module": "bcm-training",
                "subsystem": "platform-services",
                "tags": ["bcm-exercise", category, "ai-generated", f"complexity-{complexity}"],
                "created_at": datetime.now().isoformat(),
                "source": "scenario-orchestrator",
                "ai_generated": True
            },
            "description": {
                "title": title,
                "summary": f"AI-generated {category} BCM exercise scenario for training {participants} participants",
                "business_value": f"Train BCM team to respond to {category} incidents through realistic simulation",
                "user_experience": {
                    "role": "BCM Coordinator / Exercise Facilitator",
                    "estimated_time": f"{duration_hours}h",
                    "complexity": "MEDIUM" if complexity <= 2 else "HIGH" if complexity <= 4 else "CRITICAL",
                    "required_skills": ["BCM knowledge", "Incident management", "Team coordination"],
                    "participants_count": participants
                },
                "success_criteria": [
                    "All participants complete assigned roles",
                    "Incident detection within SLA",
                    "Effective communication maintained",
                    "Recovery procedures executed correctly",
                    "Post-exercise debrief completed"
                ]
            },
            "behavior": {
                "feature": "BCM Exercise Execution",
                "scenario": title,
                "given": [
                    f"BCM exercise scenario: {category}",
                    f"{participants} participants are briefed",
                    "Exercise objectives are defined",
                    "Exercise environment is prepared"
                ],
                "when": [
                    "Exercise facilitator initiates scenario",
                    "Injects are delivered according to timeline",
                    "Participants execute response procedures",
                    "Observers monitor and evaluate performance"
                ],
                "then": [
                    "All exercise objectives are achieved",
                    "Response procedures are validated",
                    "Lessons learned are captured",
                    "Improvement recommendations are generated",
                    "Exercise report is created"
                ]
            },
            "execution": {
                "steps": [
                    {
                        "name": "Prepare Exercise Environment",
                        "action": "setup_exercise_environment",
                        "params": {
                            "category": category,
                            "complexity": complexity,
                            "duration_hours": duration_hours
                        },
                        "timeout": 1800,  # 30 min
                        "required": True
                    },
                    {
                        "name": "Brief Participants",
                        "action": "brief_participants",
                        "params": {
                            "participants_count": participants,
                            "briefing_duration_minutes": 30
                        },
                        "timeout": 1800,
                        "required": True
                    },
                    {
                        "name": "Initialize Exercise",
                        "action": "initialize_exercise",
                        "params": {
                            "scenario_id": scenario_id,
                            "start_time": "now"
                        },
                        "timeout": 300,
                        "required": True
                    },
                    {
                        "name": "Execute Exercise Phases",
                        "action": "execute_exercise_phases",
                        "params": {
                            "duration_hours": duration_hours,
                            "inject_timeline": "auto"  # From AI-generated scenario
                        },
                        "timeout": duration_hours * 3600 + 1800,  # Exercise + 30min buffer
                        "required": True
                    },
                    {
                        "name": "Collect Feedback",
                        "action": "collect_participant_feedback",
                        "params": {
                            "participants_count": participants,
                            "feedback_method": "digital_form"
                        },
                        "timeout": 1800,
                        "required": True
                    },
                    {
                        "name": "Conduct Debrief",
                        "action": "conduct_debrief_session",
                        "params": {
                            "debrief_duration_minutes": 60,
                            "facilitator": "bcm_coordinator"
                        },
                        "timeout": 3600,
                        "required": True
                    },
                    {
                        "name": "Analyze Results",
                        "action": "analyze_exercise_results",
                        "params": {
                            "scenario_id": scenario_id,
                            "generate_report": True
                        },
                        "timeout": 1800,
                        "required": True
                    },
                    {
                        "name": "Send to Learning System",
                        "action": "send_results_to_learning",
                        "params": {
                            "scenario_id": scenario_id,
                            "learning_endpoint": f"{self.orchestrator_url}/learning/exercise-result"
                        },
                        "timeout": 300,
                        "required": False
                    }
                ],
                "rollback_on_failure": False,
                "continue_on_step_failure": True
            },
            "integration": {
                "calls": [
                    # Call L3 inter-system scenarios
                    {
                        "scenario": "L3-ai-platform-integration/ai-assisted-bia",
                        "when": "step:analyze_exercise_results",
                        "params": {"analysis_depth": "deep"}
                    },
                    {
                        "scenario": "L2-platform-services/bcm-subsystem-health",
                        "when": "before:initialize_exercise",
                        "params": {}
                    }
                ],
                "events": {
                    "subscribes": [
                        "exercise.inject.delivered",
                        "participant.action.completed",
                        "system.alert.triggered"
                    ],
                    "publishes": [
                        {
                            "event": "exercise.started",
                            "when": "step:initialize_exercise",
                            "data": {
                                "scenario_id": scenario_id,
                                "category": category,
                                "participants_count": participants
                            }
                        },
                        {
                            "event": "exercise.completed",
                            "when": "step:send_results_to_learning",
                            "data": {
                                "scenario_id": scenario_id,
                                "duration_actual": "calculated",
                                "success_rate": "calculated"
                            }
                        },
                        {
                            "event": "lesson.learned",
                            "when": "step:conduct_debrief_session",
                            "data": {
                                "lessons": "extracted_from_feedback"
                            }
                        }
                    ]
                }
            },
            "observability": {
                "metrics": [
                    "exercise_duration_seconds",
                    "participant_completion_rate",
                    "exercise_success_score",
                    "feedback_effectiveness_rating",
                    "lessons_learned_count"
                ],
                "traces": {
                    "trace_id_prefix": f"exercise-{category}",
                    "sampling_rate": 1.0  # Always trace exercises
                },
                "logging": {
                    "level": "INFO",
                    "structured": True,
                    "include_participant_actions": True
                }
            },
            "chaos": {
                "experiments": [
                    {
                        "name": "Communication System Failure",
                        "hypothesis": "Team can maintain coordination using backup communication",
                        "inject": {
                            "type": "network_failure",
                            "target": "primary_communication_system",
                            "duration": 900  # 15 min
                        },
                        "abort_conditions": ["critical_safety_issue", "complete_coordination_breakdown"],
                        "progressive_rollout": True,
                        "rollout_percentage": 50
                    },
                    {
                        "name": "Key Decision Maker Unavailable",
                        "hypothesis": "Backup decision maker can assume responsibilities",
                        "inject": {
                            "type": "participant_unavailable",
                            "role": "incident_commander",
                            "duration": 1800  # 30 min
                        },
                        "abort_conditions": ["no_backup_available"],
                        "progressive_rollout": False
                    }
                ]
            },
            "compliance": {
                "standards": ["ISO 22301:2019", "NFPA 1600"],
                "requirements": [
                    {
                        "clause": "ISO 22301:8.5",
                        "description": "Exercising and testing",
                        "validation": "Exercise completed and documented"
                    }
                ],
                "evidence": {
                    "generate": True,
                    "artifacts": [
                        "exercise_plan",
                        "participant_roster",
                        "inject_timeline",
                        "participant_feedback",
                        "debrief_report",
                        "lessons_learned",
                        "improvement_recommendations"
                    ]
                }
            },
            "sla": {
                "success_rate": 0.85,  # 85% of exercises successful
                "availability": 0.99,
                "max_latency_ms": 5000,
                "constraints": {
                    "max_exercise_duration_hours": duration_hours + 2,  # 2h buffer
                    "min_participant_completion_rate": 0.8
                }
            },
            "ai_generation_metadata": {
                "generated_by": "scenario-orchestrator",
                "orchestrator_scenario_id": scenario_id,
                "ai_model": "existing_ai_orchestrator",
                "complexity_level": complexity,
                "category": category,
                "generated_at": orchestrator_result.get("created_at", datetime.now().isoformat()),
                "jaamsim_enabled": orchestrator_result.get("jaamsim_config") is not None
            }
        }

        return l4_scenario

    async def get_exercise_learning_insights(self, scenario_id: str) -> Dict[str, Any]:
        """
        Get learning insights from Scenario Orchestrator

        Args:
            scenario_id: Scenario ID

        Returns:
            Learning insights dict
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.orchestrator_url}/learning/scenario/{scenario_id}/insights"
                )

                if response.status_code == 200:
                    return response.json()
                else:
                    logger.warning(f"Failed to get insights: {response.status_code}")
                    return {"insights": {}}

        except Exception as e:
            logger.error(f"Error getting learning insights: {e}")
            return {"insights": {}}

    async def send_exercise_result(
        self,
        exercise_id: str,
        scenario_id: str,
        template_id: str,
        exercise_type: str,
        duration_actual_hours: float,
        participants_count: int,
        success_metrics: Dict[str, Any],
        participant_feedback: List[Dict[str, Any]],
        lessons_learned: List[str],
        effectiveness_score: float
    ) -> bool:
        """
        Send exercise result back to Scenario Orchestrator for learning

        Args:
            exercise_id: Exercise ID
            scenario_id: Scenario ID
            template_id: Template ID
            exercise_type: Exercise type
            duration_actual_hours: Actual duration
            participants_count: Participant count
            success_metrics: Success metrics
            participant_feedback: Feedback list
            lessons_learned: Lessons learned
            effectiveness_score: Effectiveness score (0-10)

        Returns:
            Success status
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.orchestrator_url}/learning/exercise-result",
                    json={
                        "exercise_id": exercise_id,
                        "scenario_id": scenario_id,
                        "template_id": template_id,
                        "exercise_type": exercise_type,
                        "duration_actual_hours": duration_actual_hours,
                        "participants_count": participants_count,
                        "success_metrics": success_metrics,
                        "participant_feedback": participant_feedback,
                        "lessons_learned": lessons_learned,
                        "effectiveness_score": effectiveness_score
                    }
                )

                if response.status_code == 200:
                    logger.info(f"Exercise result sent successfully: {exercise_id}")
                    return True
                else:
                    logger.error(f"Failed to send exercise result: {response.status_code}")
                    return False

        except Exception as e:
            logger.error(f"Error sending exercise result: {e}")
            return False

    async def health_check(self) -> bool:
        """Check if Scenario Orchestrator is healthy"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.orchestrator_url}/health")
                return response.status_code == 200
        except Exception:
            return False


# Global instance
_orchestrator_adapter: Optional[ScenarioOrchestratorAdapter] = None


def get_orchestrator_adapter() -> ScenarioOrchestratorAdapter:
    """Get or create global Orchestrator adapter"""
    global _orchestrator_adapter

    if _orchestrator_adapter is None:
        _orchestrator_adapter = ScenarioOrchestratorAdapter()

    return _orchestrator_adapter
