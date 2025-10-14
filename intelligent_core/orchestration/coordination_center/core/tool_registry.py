"""Tool Registry - каталог всех доступных инструментов."""
import json
from typing import Dict, List, Optional
from pathlib import Path
from models.schemas import ToolDefinition, ToolCategory, ToolParameter


class ToolRegistry:
    """Registry of all available tools for AI to use."""

    def __init__(self):
        self.tools: Dict[str, ToolDefinition] = {}
        self._load_default_tools()

    def _load_default_tools(self):
        """Load default tool definitions."""

        # BCM Tools (from PLATFORM Gateway)
        bcm_tools = [
            ToolDefinition(
                tool_id="bia_tool",
                name="Business Impact Analysis Tool",
                description="Create and manage BIA processes, dependencies, and impact assessments",
                category=ToolCategory.BCM,
                base_url="http://localhost:8000/api/bia",
                version="v1",
                supported_actions=["create", "read", "update", "list", "analyze"],
                endpoints={
                    "create": "/processes",
                    "read": "/processes/{id}",
                    "update": "/processes/{id}",
                    "list": "/processes",
                    "analyze": "/processes/{id}/analyze"
                },
                parameters={
                    "create": [
                        ToolParameter(name="name", type="string", required=True, description="Process name"),
                        ToolParameter(name="description", type="string", required=False),
                        ToolParameter(name="criticality", type="string", required=True, enum=["low", "medium", "high", "critical"]),
                        ToolParameter(name="rto_hours", type="integer", required=False),
                        ToolParameter(name="rpo_hours", type="integer", required=False),
                    ],
                    "read": [
                        ToolParameter(name="id", type="integer", required=True, description="Process ID")
                    ],
                    "update": [
                        ToolParameter(name="id", type="integer", required=True),
                        ToolParameter(name="name", type="string", required=False),
                        ToolParameter(name="criticality", type="string", required=False),
                    ]
                },
                requires_auth=True,
                rate_limit=100
            ),

            ToolDefinition(
                tool_id="risk_tool",
                name="Risk Assessment Tool",
                description="Identify, assess, and manage risks",
                category=ToolCategory.BCM,
                base_url="http://localhost:8000/api/risk",
                version="v1",
                supported_actions=["create", "read", "update", "list", "assess", "fair_analysis"],
                endpoints={
                    "create": "/risks",
                    "read": "/risks/{id}",
                    "update": "/risks/{id}",
                    "list": "/risks",
                    "assess": "/risks/{id}/assess",
                    "fair_analysis": "/risks/{id}/fair-analysis"
                },
                parameters={
                    "create": [
                        ToolParameter(name="name", type="string", required=True),
                        ToolParameter(name="description", type="string", required=False),
                        ToolParameter(name="category", type="string", required=True),
                        ToolParameter(name="likelihood", type="integer", required=False),
                        ToolParameter(name="impact", type="integer", required=False),
                    ]
                },
                requires_auth=True,
                rate_limit=100
            ),

            ToolDefinition(
                tool_id="planning_tool",
                name="Planning Tool",
                description="Create and manage BC/DR plans",
                category=ToolCategory.BCM,
                base_url="http://localhost:8000/api/planning",
                version="v1",
                supported_actions=["create", "read", "update", "list", "activate"],
                endpoints={
                    "create": "/plans",
                    "read": "/plans/{id}",
                    "update": "/plans/{id}",
                    "list": "/plans",
                    "activate": "/plans/{id}/activate"
                },
                requires_auth=True,
                rate_limit=100
            ),

            ToolDefinition(
                tool_id="response_tool",
                name="Incident Response Tool",
                description="Manage incidents and crisis response",
                category=ToolCategory.BCM,
                base_url="http://localhost:8000/api/response",
                version="v1",
                supported_actions=["create", "read", "update", "list", "escalate", "resolve"],
                endpoints={
                    "create": "/incidents",
                    "read": "/incidents/{id}",
                    "update": "/incidents/{id}",
                    "list": "/incidents",
                    "escalate": "/incidents/{id}/escalate",
                    "resolve": "/incidents/{id}/resolve"
                },
                requires_auth=True,
                rate_limit=100
            ),
        ]

        # Intelligence Tools
        intelligence_tools = [
            ToolDefinition(
                tool_id="digital_twin",
                name="Digital Twin",
                description="Model and simulate organizational state",
                category=ToolCategory.INTELLIGENCE,
                base_url="http://localhost:8030",
                version="v1",
                supported_actions=["create_org", "get_org", "create_dependency", "impact_analysis", "snapshot"],
                endpoints={
                    "create_org": "/api/twin/organizations",
                    "get_org": "/api/twin/organizations/{id}",
                    "create_dependency": "/api/twin/organizations/{id}/dependencies",
                    "impact_analysis": "/api/twin/organizations/{id}/impact-analysis",
                    "snapshot": "/api/twin/organizations/{id}/snapshot"
                },
                requires_auth=True,
                rate_limit=50
            ),

            ToolDefinition(
                tool_id="simulation",
                name="Simulation Engine",
                description="Run what-if, Monte Carlo, and scenario simulations",
                category=ToolCategory.INTELLIGENCE,
                base_url="http://localhost:8031",
                version="v1",
                supported_actions=["create_simulation", "run_simulation", "get_results"],
                endpoints={
                    "create_simulation": "/api/simulation/simulations",
                    "run_simulation": "/api/simulation/simulations/{id}/run",
                    "get_results": "/api/simulation/simulations/{id}/results"
                },
                parameters={
                    "create_simulation": [
                        ToolParameter(name="name", type="string", required=True),
                        ToolParameter(name="simulation_type", type="string", required=True, enum=["what_if", "monte_carlo", "scenario"]),
                        ToolParameter(name="parameters", type="object", required=True),
                    ]
                },
                requires_auth=True,
                rate_limit=20
            ),

            # 10 AI Organs (Individual tools)
            ToolDefinition(
                tool_id="governance_brain",
                name="🧠 Governance Brain",
                description="Strategic intelligence and policy guidance",
                category=ToolCategory.INTELLIGENCE,
                base_url="http://localhost:8032",
                version="v1",
                supported_actions=["analyze_governance"],
                endpoints={"analyze_governance": "/api/ai/organs/governance-brain"},
                parameters={
                    "analyze_governance": [
                        ToolParameter(name="organization_state", type="object", required=True),
                        ToolParameter(name="policies", type="array", required=False),
                        ToolParameter(name="strategic_objectives", type="array", required=False),
                    ]
                },
                requires_auth=True,
                rate_limit=30
            ),

            ToolDefinition(
                tool_id="emergency_response",
                name="🚨 Emergency Response",
                description="Crisis management and incident response",
                category=ToolCategory.INTELLIGENCE,
                base_url="http://localhost:8032",
                version="v1",
                supported_actions=["analyze_emergency"],
                endpoints={"analyze_emergency": "/api/ai/organs/emergency-response"},
                requires_auth=True,
                rate_limit=30
            ),

            ToolDefinition(
                tool_id="impact_oracle",
                name="🔮 Impact Oracle",
                description="Predictive business impact analysis",
                category=ToolCategory.INTELLIGENCE,
                base_url="http://localhost:8032",
                version="v1",
                supported_actions=["predict_impact"],
                endpoints={"predict_impact": "/api/ai/organs/impact-oracle"},
                requires_auth=True,
                rate_limit=30
            ),

            ToolDefinition(
                tool_id="scenario_creator",
                name="📝 Scenario Creator",
                description="AI-powered BCM scenario generation",
                category=ToolCategory.INTELLIGENCE,
                base_url="http://localhost:8032",
                version="v1",
                supported_actions=["create_scenario"],
                endpoints={"create_scenario": "/api/ai/organs/scenario-creator"},
                requires_auth=True,
                rate_limit=20
            ),

            ToolDefinition(
                tool_id="risk_advisor",
                name="⚡ Risk Advisor",
                description="Risk analysis and mitigation strategies",
                category=ToolCategory.INTELLIGENCE,
                base_url="http://localhost:8032",
                version="v1",
                supported_actions=["analyze_risk"],
                endpoints={"analyze_risk": "/api/ai/organs/risk-advisor"},
                requires_auth=True,
                rate_limit=30
            ),

            ToolDefinition(
                tool_id="compliance_guardian",
                name="🛡️ Compliance Guardian",
                description="Standards compliance monitoring",
                category=ToolCategory.INTELLIGENCE,
                base_url="http://localhost:8032",
                version="v1",
                supported_actions=["check_compliance"],
                endpoints={"check_compliance": "/api/ai/organs/compliance-guardian"},
                requires_auth=True,
                rate_limit=30
            ),

            ToolDefinition(
                tool_id="performance_analyst",
                name="📊 Performance Analyst",
                description="BCM KPI intelligence and analysis",
                category=ToolCategory.INTELLIGENCE,
                base_url="http://localhost:8032",
                version="v1",
                supported_actions=["analyze_performance"],
                endpoints={"analyze_performance": "/api/ai/organs/performance-analyst"},
                requires_auth=True,
                rate_limit=30
            ),

            ToolDefinition(
                tool_id="learning_coach",
                name="🎓 Learning Coach",
                description="Training optimization and learning insights",
                category=ToolCategory.INTELLIGENCE,
                base_url="http://localhost:8032",
                version="v1",
                supported_actions=["analyze_learning"],
                endpoints={"analyze_learning": "/api/ai/organs/learning-coach"},
                requires_auth=True,
                rate_limit=30
            ),

            ToolDefinition(
                tool_id="plan_generator",
                name="📋 Plan Generator",
                description="BCP/DRP plan creation and optimization",
                category=ToolCategory.INTELLIGENCE,
                base_url="http://localhost:8032",
                version="v1",
                supported_actions=["generate_plan"],
                endpoints={"generate_plan": "/api/ai/organs/plan-generator"},
                requires_auth=True,
                rate_limit=20
            ),

            ToolDefinition(
                tool_id="lifecycle_monitor",
                name="💓 Lifecycle Monitor",
                description="BCM program lifecycle health monitoring",
                category=ToolCategory.INTELLIGENCE,
                base_url="http://localhost:8032",
                version="v1",
                supported_actions=["monitor_lifecycle"],
                endpoints={"monitor_lifecycle": "/api/ai/organs/lifecycle-monitor"},
                requires_auth=True,
                rate_limit=30
            ),

            # Project Intelligence (Standalone Service)
            ToolDefinition(
                tool_id="project_intelligence",
                name="🎯 Project Intelligence",
                description="AI-powered project management and health monitoring",
                category=ToolCategory.INTELLIGENCE,
                base_url="http://localhost:8025",
                version="v1",
                supported_actions=["analyze_project", "suggest_assignee", "get_health"],
                endpoints={
                    "analyze_project": "/api/v1/projects/{project_id}/analyze",
                    "suggest_assignee": "/api/v1/projects/{project_id}/tasks/{task_id}/suggest-assignee",
                    "get_health": "/api/v1/projects/{project_id}/health"
                },
                requires_auth=True,
                rate_limit=50
            ),
        ]

        # AI Colleagues (7 RAG-powered conversational assistants)
        colleagues_tools = [
            ToolDefinition(
                tool_id="compliance_copilot",
                name="👔 Compliance Copilot",
                description="ISO 22301 compliance expert with conversational interface",
                category=ToolCategory.AI_COLLEAGUE,
                base_url="http://localhost:8032",
                version="v1",
                supported_actions=["assist_compliance", "assess_gap", "generate_report", "get_clause_guidance"],
                endpoints={
                    "assist_compliance": "/api/ai/colleagues/compliance-copilot",
                    "assess_gap": "/api/ai/colleagues/compliance-copilot/gap-analysis",
                    "generate_report": "/api/ai/colleagues/compliance-copilot/report",
                    "get_clause_guidance": "/api/ai/colleagues/compliance-copilot/clause/{clause}"
                },
                parameters={
                    "assist_compliance": [
                        ToolParameter(name="user_message", type="string", required=True),
                        ToolParameter(name="context", type="string", required=False, enum=["COMPLIANCE", "GOVERNANCE", "RISK", "BIA", "PLANNING", "RESPONSE", "DOCUMENTS"]),
                        ToolParameter(name="tenant_id", type="string", required=False),
                    ]
                },
                requires_auth=True,
                rate_limit=30
            ),

            ToolDefinition(
                tool_id="project_manager_colleague",
                name="🎯 Project Manager AI",
                description="BCM project management expert with RAG-powered advice",
                category=ToolCategory.AI_COLLEAGUE,
                base_url="http://localhost:8032",
                version="v1",
                supported_actions=["assist_project", "analyze_health", "suggest_assignment", "predict_completion", "recovery_strategy"],
                endpoints={
                    "assist_project": "/api/ai/colleagues/project-manager",
                    "analyze_health": "/api/ai/colleagues/project-manager/health",
                    "suggest_assignment": "/api/ai/colleagues/project-manager/assignment",
                    "predict_completion": "/api/ai/colleagues/project-manager/prediction",
                    "recovery_strategy": "/api/ai/colleagues/project-manager/recovery"
                },
                parameters={
                    "assist_project": [
                        ToolParameter(name="user_message", type="string", required=True),
                        ToolParameter(name="context", type="string", required=False, enum=["OVERVIEW", "GOVERNANCE", "RISK", "PLANNING", "EXERCISES", "TRAINING", "RESPONSE"]),
                        ToolParameter(name="tenant_id", type="string", required=False),
                    ]
                },
                requires_auth=True,
                rate_limit=30
            ),

            ToolDefinition(
                tool_id="risk_analyst_colleague",
                name="⚡ Risk Analyst AI",
                description="FAIR methodology expert for risk quantification",
                category=ToolCategory.AI_COLLEAGUE,
                base_url="http://localhost:8032",
                version="v1",
                supported_actions=["assist_risk", "assess_risk", "prioritize_risks", "suggest_treatments"],
                endpoints={
                    "assist_risk": "/api/ai/colleagues/risk-analyst",
                    "assess_risk": "/api/ai/colleagues/risk-analyst/assess",
                    "prioritize_risks": "/api/ai/colleagues/risk-analyst/prioritize",
                    "suggest_treatments": "/api/ai/colleagues/risk-analyst/treatments"
                },
                parameters={
                    "assist_risk": [
                        ToolParameter(name="user_message", type="string", required=True),
                        ToolParameter(name="context", type="string", required=False, enum=["RISK", "BIA", "COMPLIANCE", "GOVERNANCE", "PLANNING"]),
                        ToolParameter(name="tenant_id", type="string", required=False),
                    ]
                },
                requires_auth=True,
                rate_limit=30
            ),

            ToolDefinition(
                tool_id="bia_specialist_colleague",
                name="🔍 BIA Specialist AI",
                description="Business Impact Analysis expert",
                category=ToolCategory.AI_COLLEAGUE,
                base_url="http://localhost:8032",
                version="v1",
                supported_actions=["assist_bia", "analyze_process", "calculate_impact", "recommend_rto_rpo"],
                endpoints={
                    "assist_bia": "/api/ai/colleagues/bia-specialist",
                    "analyze_process": "/api/ai/colleagues/bia-specialist/analyze",
                    "calculate_impact": "/api/ai/colleagues/bia-specialist/impact",
                    "recommend_rto_rpo": "/api/ai/colleagues/bia-specialist/rto-rpo"
                },
                parameters={
                    "assist_bia": [
                        ToolParameter(name="user_message", type="string", required=True),
                        ToolParameter(name="context", type="string", required=False, enum=["BIA", "RISK", "PLANNING", "COMPLIANCE"]),
                        ToolParameter(name="tenant_id", type="string", required=False),
                    ]
                },
                requires_auth=True,
                rate_limit=30
            ),

            ToolDefinition(
                tool_id="plan_generator_colleague",
                name="📋 Plan Generator AI",
                description="BCP/DRP plan creation expert with conversational interface",
                category=ToolCategory.AI_COLLEAGUE,
                base_url="http://localhost:8032",
                version="v1",
                supported_actions=["assist_planning", "generate_bcp", "generate_drp", "optimize_plan"],
                endpoints={
                    "assist_planning": "/api/ai/colleagues/plan-generator",
                    "generate_bcp": "/api/ai/colleagues/plan-generator/bcp",
                    "generate_drp": "/api/ai/colleagues/plan-generator/drp",
                    "optimize_plan": "/api/ai/colleagues/plan-generator/optimize"
                },
                parameters={
                    "assist_planning": [
                        ToolParameter(name="user_message", type="string", required=True),
                        ToolParameter(name="context", type="string", required=False, enum=["PLANNING", "BIA", "RISK", "RESPONSE"]),
                        ToolParameter(name="tenant_id", type="string", required=False),
                    ]
                },
                requires_auth=True,
                rate_limit=20
            ),

            ToolDefinition(
                tool_id="incident_advisor_colleague",
                name="🚨 Incident Advisor AI",
                description="Incident response and crisis management expert",
                category=ToolCategory.AI_COLLEAGUE,
                base_url="http://localhost:8032",
                version="v1",
                supported_actions=["assist_incident", "assess_severity", "recommend_actions", "escalation_guide"],
                endpoints={
                    "assist_incident": "/api/ai/colleagues/incident-advisor",
                    "assess_severity": "/api/ai/colleagues/incident-advisor/severity",
                    "recommend_actions": "/api/ai/colleagues/incident-advisor/actions",
                    "escalation_guide": "/api/ai/colleagues/incident-advisor/escalation"
                },
                parameters={
                    "assist_incident": [
                        ToolParameter(name="user_message", type="string", required=True),
                        ToolParameter(name="context", type="string", required=False, enum=["RESPONSE", "PLANNING", "RISK", "BIA"]),
                        ToolParameter(name="tenant_id", type="string", required=False),
                    ]
                },
                requires_auth=True,
                rate_limit=30
            ),

            ToolDefinition(
                tool_id="exercise_designer_colleague",
                name="🎭 Exercise Designer AI",
                description="BCM exercise and training scenario expert",
                category=ToolCategory.AI_COLLEAGUE,
                base_url="http://localhost:8032",
                version="v1",
                supported_actions=["assist_exercise", "design_scenario", "create_tabletop", "evaluate_results"],
                endpoints={
                    "assist_exercise": "/api/ai/colleagues/exercise-designer",
                    "design_scenario": "/api/ai/colleagues/exercise-designer/scenario",
                    "create_tabletop": "/api/ai/colleagues/exercise-designer/tabletop",
                    "evaluate_results": "/api/ai/colleagues/exercise-designer/evaluate"
                },
                parameters={
                    "assist_exercise": [
                        ToolParameter(name="user_message", type="string", required=True),
                        ToolParameter(name="context", type="string", required=False, enum=["EXERCISES", "TRAINING", "PLANNING", "RISK"]),
                        ToolParameter(name="tenant_id", type="string", required=False),
                    ]
                },
                requires_auth=True,
                rate_limit=20
            ),
        ]

        # Platform Services (3 new services)
        platform_tools = [
            ToolDefinition(
                tool_id="ai_orchestration",
                name="🎯 AI Orchestration",
                description="Unified orchestration system (8 orchestrators in 1)",
                category=ToolCategory.PLATFORM,
                base_url="http://localhost:8002",
                version="v1",
                supported_actions=["orchestrate_platform", "orchestrate_ai", "generate_scenario", "deploy_service", "health_check"],
                endpoints={
                    "orchestrate_platform": "/api/v1/platform/orchestrate",
                    "orchestrate_ai": "/api/v1/ai/orchestrate",
                    "generate_scenario": "/api/v1/scenario/generate",
                    "deploy_service": "/api/v1/deploy",
                    "health_check": "/health"
                },
                requires_auth=True,
                rate_limit=50
            ),

            ToolDefinition(
                tool_id="eventbus",
                name="📡 EventBus",
                description="Event pub/sub, history, WebSocket streaming",
                category=ToolCategory.PLATFORM,
                base_url="http://localhost:8001",
                version="v1",
                supported_actions=["publish_event", "subscribe", "get_history", "stream_events"],
                endpoints={
                    "publish_event": "/events",
                    "subscribe": "/subscribe",
                    "get_history": "/events/history",
                    "stream_events": "/events/stream"
                },
                requires_auth=True,
                rate_limit=100
            ),

            ToolDefinition(
                tool_id="bpmn_workflow",
                name="🔄 BPMN Workflow",
                description="BPMN process engine for complex workflows",
                category=ToolCategory.PLATFORM,
                base_url="http://localhost:8003",
                version="v1",
                supported_actions=["start_process", "get_process", "update_process", "complete_task", "list_processes"],
                endpoints={
                    "start_process": "/processes",
                    "get_process": "/processes/{id}",
                    "update_process": "/processes/{id}",
                    "complete_task": "/processes/{id}/tasks/{task_id}/complete",
                    "list_processes": "/processes"
                },
                requires_auth=True,
                rate_limit=50
            ),

            ToolDefinition(
                tool_id="notification_service",
                name="📧 Notification Service",
                description="Multi-channel notifications (Email, SMS, Push, Webhooks)",
                category=ToolCategory.PLATFORM,
                base_url="http://localhost:8035",
                version="v1",
                supported_actions=["send_email", "send_sms", "send_push", "send_webhook", "get_history"],
                endpoints={
                    "send_email": "/email/send",
                    "send_sms": "/sms/send",
                    "send_push": "/push/send",
                    "send_webhook": "/webhook/send",
                    "get_history": "/notifications/history"
                },
                parameters={
                    "send_email": [
                        ToolParameter(name="to", type="array", required=True, description="Email recipients"),
                        ToolParameter(name="subject", type="string", required=True),
                        ToolParameter(name="body", type="string", required=True),
                        ToolParameter(name="html_body", type="string", required=False),
                    ],
                    "send_sms": [
                        ToolParameter(name="to", type="array", required=True, description="Phone numbers"),
                        ToolParameter(name="message", type="string", required=True),
                    ],
                    "send_push": [
                        ToolParameter(name="user_ids", type="array", required=True),
                        ToolParameter(name="title", type="string", required=True),
                        ToolParameter(name="message", type="string", required=True),
                    ],
                    "send_webhook": [
                        ToolParameter(name="url", type="string", required=True),
                        ToolParameter(name="payload", type="object", required=True),
                    ]
                },
                requires_auth=True,
                rate_limit=100
            ),
            # 🔍 Process Mining Service
            ToolDefinition(
                tool_id="process_mining_service",
                name="🔍 Process Mining Service",
                description="Advanced process analytics - discover patterns, detect deviations, analyze performance",
                category=ToolCategory.PLATFORM,
                base_url="http://localhost:8040",
                version="v1",
                supported_actions=["log_execution", "log_event", "analyze_performance", "discover_patterns", "detect_deviations", "comprehensive_analysis", "get_summary"],
                endpoints={
                    "log_execution": "/api/v1/process-mining/log-execution",
                    "log_event": "/api/v1/process-mining/log-event",
                    "analyze_performance": "/api/v1/process-mining/analyze-performance/{process_id}",
                    "discover_patterns": "/api/v1/process-mining/discover-patterns/{process_id}",
                    "detect_deviations": "/api/v1/process-mining/detect-deviations/{process_id}",
                    "comprehensive_analysis": "/api/v1/process-mining/comprehensive-analysis",
                    "get_summary": "/api/v1/process-mining/processes/{process_id}/summary"
                },
                parameters={
                    "log_execution": [
                        ToolParameter(name="process_id", type="string", required=True, description="Process identifier"),
                        ToolParameter(name="execution_id", type="string", required=True, description="Unique execution ID"),
                        ToolParameter(name="start_time", type="string", required=True, description="ISO datetime"),
                        ToolParameter(name="end_time", type="string", required=False, description="ISO datetime"),
                        ToolParameter(name="status", type="string", required=True, enum=["running", "completed", "failed", "cancelled"]),
                        ToolParameter(name="executed_by", type="string", required=False),
                        ToolParameter(name="metadata", type="object", required=False),
                    ],
                    "log_event": [
                        ToolParameter(name="execution_id", type="string", required=True),
                        ToolParameter(name="event_type", type="string", required=True, enum=["start", "end", "checkpoint", "error", "decision"]),
                        ToolParameter(name="step_name", type="string", required=True),
                        ToolParameter(name="timestamp", type="string", required=True, description="ISO datetime"),
                        ToolParameter(name="duration_minutes", type="number", required=False),
                        ToolParameter(name="actor", type="string", required=False),
                        ToolParameter(name="data", type="object", required=False),
                    ],
                    "analyze_performance": [
                        ToolParameter(name="process_id", type="string", required=True),
                        ToolParameter(name="days_back", type="integer", required=False, description="Default: 30"),
                    ],
                    "discover_patterns": [
                        ToolParameter(name="process_id", type="string", required=True),
                        ToolParameter(name="days_back", type="integer", required=False, description="Default: 30"),
                    ],
                    "detect_deviations": [
                        ToolParameter(name="process_id", type="string", required=True),
                        ToolParameter(name="days_back", type="integer", required=False, description="Default: 30"),
                    ],
                    "comprehensive_analysis": [
                        ToolParameter(name="process_id", type="string", required=True),
                        ToolParameter(name="date_from", type="string", required=False, description="ISO datetime"),
                        ToolParameter(name="date_to", type="string", required=False, description="ISO datetime"),
                        ToolParameter(name="include_performance", type="boolean", required=False, description="Default: true"),
                        ToolParameter(name="include_patterns", type="boolean", required=False, description="Default: true"),
                        ToolParameter(name="include_deviations", type="boolean", required=False, description="Default: true"),
                    ],
                    "get_summary": [
                        ToolParameter(name="process_id", type="string", required=True),
                    ]
                },
                requires_auth=True,
                rate_limit=100
            ),
            # 🔍 Monitoring Service
            ToolDefinition(
                tool_id="monitoring_service",
                name="🔍 Monitoring Service",
                description="Centralized monitoring, logging, and alerting - health checks, metrics, real-time dashboard",
                category=ToolCategory.PLATFORM,
                base_url="http://localhost:8045",
                version="v1",
                supported_actions=["get_status", "get_services", "get_logs", "get_metrics", "get_alerts", "ingest_log", "ingest_metrics", "acknowledge_alert", "resolve_alert"],
                endpoints={
                    "get_status": "/status",
                    "get_services": "/services",
                    "get_logs": "/logs",
                    "get_metrics": "/metrics/{service}",
                    "get_alerts": "/alerts",
                    "ingest_log": "/logs",
                    "ingest_metrics": "/metrics",
                    "acknowledge_alert": "/alerts/{alert_id}/acknowledge",
                    "resolve_alert": "/alerts/{alert_id}/resolve"
                },
                parameters={
                    "get_logs": [
                        ToolParameter(name="service", type="string", required=False, description="Filter by service"),
                        ToolParameter(name="level", type="string", required=False, enum=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]),
                        ToolParameter(name="limit", type="integer", required=False, description="Default: 100"),
                    ],
                    "get_metrics": [
                        ToolParameter(name="service", type="string", required=True, description="Service name"),
                        ToolParameter(name="hours", type="integer", required=False, description="Default: 1"),
                    ],
                    "get_alerts": [
                        ToolParameter(name="status", type="string", required=False, enum=["active", "acknowledged", "resolved"]),
                    ],
                    "ingest_log": [
                        ToolParameter(name="service", type="string", required=True),
                        ToolParameter(name="level", type="string", required=True, enum=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]),
                        ToolParameter(name="message", type="string", required=True),
                        ToolParameter(name="context", type="object", required=False),
                        ToolParameter(name="trace_id", type="string", required=False),
                    ],
                    "ingest_metrics": [
                        ToolParameter(name="service", type="string", required=True),
                        ToolParameter(name="status", type="string", required=True, enum=["healthy", "degraded", "unhealthy"]),
                        ToolParameter(name="response_time_ms", type="number", required=True),
                        ToolParameter(name="cpu_usage", type="number", required=False),
                        ToolParameter(name="memory_usage", type="number", required=False),
                        ToolParameter(name="active_connections", type="integer", required=False),
                    ],
                    "acknowledge_alert": [
                        ToolParameter(name="alert_id", type="string", required=True),
                    ],
                    "resolve_alert": [
                        ToolParameter(name="alert_id", type="string", required=True),
                    ]
                },
                requires_auth=True,
                rate_limit=100
            ),
            # 🚀 Realtime WebSocket Service
            ToolDefinition(
                tool_id="realtime_websocket",
                name="🚀 Realtime WebSocket Service",
                description="Real-time WebSocket communications - chat, notifications, live updates, collaborative features",
                category=ToolCategory.PLATFORM,
                base_url="http://localhost:8050",
                version="v1",
                supported_actions=["broadcast_notification", "get_channel_users", "get_channel_messages", "get_stats"],
                endpoints={
                    "broadcast_notification": "/api/v1/notifications/broadcast",
                    "get_channel_users": "/api/v1/channels/{channel_id}/users",
                    "get_channel_messages": "/api/v1/channels/{channel_id}/messages",
                    "get_stats": "/api/v1/stats"
                },
                parameters={
                    "broadcast_notification": [
                        ToolParameter(name="notification_type", type="string", required=True),
                        ToolParameter(name="channel_id", type="string", required=True),
                        ToolParameter(name="recipients", type="array", required=False, description="Empty = broadcast to all"),
                        ToolParameter(name="content", type="object", required=True),
                        ToolParameter(name="priority", type="string", required=False, enum=["normal", "high"]),
                    ],
                    "get_channel_users": [
                        ToolParameter(name="channel_id", type="string", required=True),
                    ],
                    "get_channel_messages": [
                        ToolParameter(name="channel_id", type="string", required=True),
                        ToolParameter(name="limit", type="integer", required=False, description="Default: 50, Max: 1000"),
                        ToolParameter(name="before", type="string", required=False, description="ISO datetime"),
                    ],
                },
                requires_auth=True,
                rate_limit=100
            ),
        ]

        # Register all tools
        for tool in bcm_tools + intelligence_tools + colleagues_tools + platform_tools:
            self.register_tool(tool)

    def register_tool(self, tool: ToolDefinition):
        """Register a new tool."""
        self.tools[tool.tool_id] = tool

    def get_tool(self, tool_id: str) -> Optional[ToolDefinition]:
        """Get tool definition by ID."""
        return self.tools.get(tool_id)

    def list_tools(self, category: Optional[ToolCategory] = None) -> List[ToolDefinition]:
        """List all tools, optionally filtered by category."""
        tools = list(self.tools.values())
        if category:
            tools = [t for t in tools if t.category == category]
        return tools

    def find_tool_for_action(self, action: str, entity: Optional[str] = None) -> Optional[ToolDefinition]:
        """Find appropriate tool for an action."""
        # Simple heuristic: match entity name to tool_id
        if entity:
            # Try exact match first
            if f"{entity}_tool" in self.tools:
                return self.tools[f"{entity}_tool"]

            # Try partial match
            for tool_id, tool in self.tools.items():
                if entity.lower() in tool_id.lower():
                    if action in tool.supported_actions:
                        return tool

        # Fallback: find first tool that supports the action
        for tool in self.tools.values():
            if action in tool.supported_actions:
                return tool

        return None

    def validate_action(self, tool_id: str, action: str, params: Dict) -> tuple[bool, Optional[str]]:
        """Validate if action is supported and params are correct."""
        tool = self.get_tool(tool_id)
        if not tool:
            return False, f"Tool {tool_id} not found"

        if action not in tool.supported_actions:
            return False, f"Action {action} not supported by {tool_id}"

        # Validate parameters
        if action in tool.parameters:
            required_params = [p.name for p in tool.parameters[action] if p.required]
            missing = set(required_params) - set(params.keys())
            if missing:
                return False, f"Missing required parameters: {missing}"

        return True, None


# Global registry instance
tool_registry = ToolRegistry()
