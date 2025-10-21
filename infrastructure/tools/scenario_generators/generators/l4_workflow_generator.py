"""
L4 Workflow Generator

Generates AI-powered user workflow scenarios.
Uses LLM to create realistic user journeys combining L1-L3 scenarios.
Uses golden_standard_l4.yaml template.
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import sys
from datetime import datetime

# Add intelligent-core to path for templates/storage
intelligent_core_path = Path(__file__).parent.parent.parent.parent.parent / "intelligent-core" / "scenario-intelligence"
sys.path.insert(0, str(intelligent_core_path))

# Add AI Foundation for LLM Router
ai_foundation_path = Path(__file__).parent.parent.parent.parent.parent / "intelligent-core" / "ai-foundation"
sys.path.insert(0, str(ai_foundation_path))

from generators.base_generator import BaseGenerator

# Import metrics
try:
    from monitoring import GenerationMetricsContext, record_scenario_generated
except ImportError:
    # Fallback if metrics not available
    class GenerationMetricsContext:
        def __init__(self, *args, **kwargs):
            pass
        def __enter__(self):
            return self
        def __exit__(self, *args):
            return False
    def record_scenario_generated(*args, **kwargs):
        pass

logger = logging.getLogger(__name__)


class L4WorkflowGenerator(BaseGenerator):
    """
    Generator for L4 Workflow scenarios (AI-powered).

    Creates test scenarios for complete user workflows:
    - BCM specialist workflows (BIA creation, risk assessment, etc.)
    - Admin workflows (organization setup, user management, etc.)
    - Consultant workflows (compliance review, audit, etc.)
    - Executive workflows (dashboard review, reporting, etc.)
    - Incident manager workflows (incident response, recovery, etc.)

    Uses LLM to generate realistic user journeys with timing, actions, and validation.
    """

    def __init__(
        self,
        template_loader,
        registry,
        output_dir: str = "generated/l4",
        llm_router=None
    ):
        """
        Initialize L4 Workflow Generator.

        Args:
            template_loader: TemplateLoader instance
            registry: ScenarioRegistry instance
            output_dir: Output directory for generated scenarios
            llm_router: LLMRouter instance (creates new if None)
        """
        super().__init__(
            template_loader=template_loader,
            registry=registry,
            output_dir=output_dir,
            level=4
        )

        # Initialize LLM Router
        self.llm_router = llm_router
        if self.llm_router is None:
            try:
                from llm.llm_router import LLMRouter
                self.llm_router = LLMRouter()
                logger.info("LLMRouter initialized for L4 generation")
            except Exception as e:
                logger.warning(f"LLMRouter initialization failed: {e}. L4 will use fallback generation.")
                self.llm_router = None

    async def generate_one(self, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Generate scenario for one workflow (override to add LLM enhancement).

        Args:
            item: Workflow definition

        Returns:
            Generated scenario or None if failed
        """
        # Track metrics for L4 generation
        with GenerationMetricsContext(level='l4', generator='l4_workflow'):
            try:
                # Build base context
                context = self._build_context(item)

                # Enhance with LLM if available
                if self.llm_router:
                    try:
                        enhanced_context = await self._generate_journey_with_llm(item, context)
                        context.update(enhanced_context)
                        logger.info(f" LLM-enhanced context for workflow: {item['name']}")
                    except Exception as e:
                        logger.warning(f"LLM enhancement failed for {item['name']}: {e}. Using fallback.")

                # Get template name
                template_name = self._get_template_name(item)

                # Generate scenario from template
                scenario = self.loader.create_scenario_from_template(
                    template_name,
                    context,
                    validate=True
                )

                # Add metadata
                self._enrich_scenario(scenario, item)

                # Record successful generation
                scenario_id = scenario.get('meta', {}).get('id', 'unknown')
                record_scenario_generated('l4', 'l4_workflow', 'manual', count=1)
                logger.info(f" Metrics recorded for L4 scenario: {scenario_id}")

                return scenario

            except Exception as e:
                logger.error(f"Failed to generate scenario for {item.get('name', 'unknown')}: {e}", exc_info=True)
                self.stats["failed"] += 1
                return None

    def _get_catalog(self) -> List[Dict[str, Any]]:
        """
        Get catalog of user workflows.

        Returns:
            List of 15 workflow definitions
        """
        return [
            # === BCM Specialist Workflows ===
            {
                "name": "bcm-specialist-creates-bia",
                "description": "BCM specialist creates comprehensive Business Impact Analysis document",
                "persona": "BCM Manager",
                "role": "bcm_manager",
                "goal": "Create a comprehensive BIA document identifying critical business functions",
                "complexity": "high",
                "category": "daily_operations",
                "criticality": "critical",
                "frequency": "weekly",
                "required_scenarios": ["bia-module", "document-generation", "approval-workflow"],
                "involved_systems": ["system-bcm-service", "bia-service", "workflow-intelligence", "document-service"],
                "duration_estimate": "45-60 minutes",
                "business_outcome": "Complete BIA document with identified critical functions and recovery priorities",
                "user_goals": [
                    "Identify critical business functions",
                    "Assess business impact of disruptions",
                    "Define recovery time objectives (RTO)",
                    "Generate professional BIA report"
                ],
                "pain_points": [
                    "Complex data collection process",
                    "Multiple stakeholder inputs required",
                    "Need to validate compliance requirements"
                ],
                "success_criteria": [
                    "All critical functions identified",
                    "RTO/RPO defined for each function",
                    "Document meets ISO 22301 requirements",
                    "Stakeholders notified for review"
                ]
            },
            {
                "name": "bcm-specialist-performs-risk-assessment",
                "description": "BCM consultant conducts comprehensive organizational risk assessment",
                "persona": "Risk Assessment Consultant",
                "role": "bcm_consultant",
                "goal": "Identify and evaluate organizational risks with mitigation strategies",
                "complexity": "high",
                "category": "daily_operations",
                "criticality": "critical",
                "frequency": "monthly",
                "required_scenarios": ["risk-module", "analytics-service", "reporting"],
                "involved_systems": ["risk-service", "predictive-service", "analytics-specialist", "document-service"],
                "duration_estimate": "60-90 minutes",
                "business_outcome": "Complete risk register with mitigation strategies and priority matrix",
                "user_goals": [
                    "Identify potential risks",
                    "Evaluate risk likelihood and impact",
                    "Develop mitigation strategies",
                    "Create risk matrix visualization"
                ],
                "pain_points": [
                    "Need to integrate multiple data sources",
                    "Complex risk scoring methodology",
                    "Stakeholder consensus required"
                ],
                "success_criteria": [
                    "All risks categorized and scored",
                    "Mitigation strategies defined",
                    "Risk matrix generated",
                    "Executive summary created"
                ]
            },
            {
                "name": "bcm-specialist-develops-recovery-strategy",
                "description": "BCM professional develops business continuity recovery strategy",
                "persona": "Continuity Planner",
                "role": "bcm_planner",
                "goal": "Create actionable recovery strategy for critical business functions",
                "complexity": "high",
                "category": "daily_operations",
                "criticality": "critical",
                "frequency": "monthly",
                "required_scenarios": ["strategy-module", "workflow-engine", "approval-workflow"],
                "involved_systems": ["strategy-service", "workflow-intelligence", "system-bcm-service"],
                "duration_estimate": "90-120 minutes",
                "business_outcome": "Approved recovery strategy with defined procedures and resources",
                "user_goals": [
                    "Define recovery strategies for critical functions",
                    "Identify required resources",
                    "Create recovery procedures",
                    "Establish recovery timelines"
                ],
                "pain_points": [
                    "Balancing cost vs. recovery speed",
                    "Resource availability constraints",
                    "Multiple approval levels"
                ],
                "success_criteria": [
                    "Strategy aligns with RTO/RPO",
                    "Resources identified and allocated",
                    "Procedures documented",
                    "Management approval obtained"
                ]
            },

            # === Admin Workflows ===
            {
                "name": "admin-configures-new-organization",
                "description": "Platform admin sets up new organization with complete configuration",
                "persona": "Platform Administrator",
                "role": "platform_admin",
                "goal": "Onboard new organization with proper configuration and access controls",
                "complexity": "medium",
                "category": "onboarding",
                "criticality": "high",
                "frequency": "weekly",
                "required_scenarios": ["admin-panel", "auth-service", "database-gateway", "tenant-management"],
                "involved_systems": ["api-gateway", "auth-service", "postgresql", "secrets-manager"],
                "duration_estimate": "30-45 minutes",
                "business_outcome": "Fully configured organization ready for user onboarding",
                "user_goals": [
                    "Create new organization tenant",
                    "Configure access controls",
                    "Set up initial users",
                    "Verify isolation and security"
                ],
                "pain_points": [
                    "Multiple configuration steps",
                    "Need to ensure proper isolation",
                    "Security settings validation"
                ],
                "success_criteria": [
                    "Organization created and isolated",
                    "Admin user configured",
                    "Security policies applied",
                    "Welcome email sent"
                ]
            },
            {
                "name": "admin-manages-user-access",
                "description": "Admin manages user roles, permissions, and access controls",
                "persona": "Security Administrator",
                "role": "security_admin",
                "goal": "Manage user access ensuring principle of least privilege",
                "complexity": "medium",
                "category": "daily_operations",
                "criticality": "high",
                "frequency": "daily",
                "required_scenarios": ["auth-service", "rbac-engine", "audit-logging"],
                "involved_systems": ["auth-service", "api-gateway", "audit-service"],
                "duration_estimate": "15-30 minutes",
                "business_outcome": "Users have appropriate access with full audit trail",
                "user_goals": [
                    "Add/remove users",
                    "Assign appropriate roles",
                    "Review access permissions",
                    "Verify audit logging"
                ],
                "pain_points": [
                    "Understanding complex permission matrix",
                    "Ensuring no privilege escalation",
                    "Compliance requirements"
                ],
                "success_criteria": [
                    "User access properly configured",
                    "Least privilege enforced",
                    "Changes logged in audit trail",
                    "Email notifications sent"
                ]
            },
            {
                "name": "admin-monitors-system-health",
                "description": "Admin monitors platform health and responds to alerts",
                "persona": "Platform Operations Admin",
                "role": "ops_admin",
                "goal": "Ensure platform health and respond to incidents proactively",
                "complexity": "medium",
                "category": "daily_operations",
                "criticality": "critical",
                "frequency": "daily",
                "required_scenarios": ["observability", "prometheus", "grafana", "alertmanager"],
                "involved_systems": ["prometheus", "grafana", "balancer-service", "eventbus"],
                "duration_estimate": "20-30 minutes",
                "business_outcome": "Platform health verified and any issues addressed",
                "user_goals": [
                    "Review system dashboards",
                    "Check service health metrics",
                    "Investigate any alerts",
                    "Verify auto-recovery systems"
                ],
                "pain_points": [
                    "Information overload from metrics",
                    "False positive alerts",
                    "Need to correlate multiple dashboards"
                ],
                "success_criteria": [
                    "All services healthy",
                    "Alerts investigated",
                    "Issues documented",
                    "Team notified if needed"
                ]
            },

            # === End User Workflows ===
            {
                "name": "user-reports-incident",
                "description": "End user reports business continuity incident",
                "persona": "Department Manager",
                "role": "end_user",
                "goal": "Report and track resolution of business continuity incident",
                "complexity": "low",
                "category": "incident_response",
                "criticality": "critical",
                "frequency": "ad-hoc",
                "required_scenarios": ["incident-module", "notification-service", "workflow-engine"],
                "involved_systems": ["response-service", "workflow-intelligence", "notification-service"],
                "duration_estimate": "10-15 minutes",
                "business_outcome": "Incident reported and response workflow initiated",
                "user_goals": [
                    "Report incident quickly",
                    "Provide necessary details",
                    "Track incident status",
                    "Receive updates"
                ],
                "pain_points": [
                    "Stress during incident",
                    "Need for clear guidance",
                    "Uncertainty about what to report"
                ],
                "success_criteria": [
                    "Incident submitted successfully",
                    "Response team notified",
                    "Tracking ID received",
                    "Initial acknowledgment received"
                ]
            },
            {
                "name": "user-completes-training",
                "description": "Employee completes BCM awareness training",
                "persona": "New Employee",
                "role": "employee",
                "goal": "Complete required BCM training and certification",
                "complexity": "low",
                "category": "training",
                "criticality": "medium",
                "frequency": "quarterly",
                "required_scenarios": ["learning-system", "gamification", "certification"],
                "involved_systems": ["learning-system", "knowledge-base", "document-service"],
                "duration_estimate": "30-45 minutes",
                "business_outcome": "Employee trained and certified in BCM basics",
                "user_goals": [
                    "Learn BCM fundamentals",
                    "Pass knowledge check",
                    "Obtain certification",
                    "Download certificate"
                ],
                "pain_points": [
                    "Time constraints",
                    "Complex terminology",
                    "Need for engaging content"
                ],
                "success_criteria": [
                    "Training completed",
                    "Assessment passed",
                    "Certificate issued",
                    "Compliance record updated"
                ]
            },
            {
                "name": "user-reviews-continuity-plan",
                "description": "Department head reviews and approves continuity plan",
                "persona": "Department Head",
                "role": "department_manager",
                "goal": "Review and approve departmental continuity plan",
                "complexity": "medium",
                "category": "compliance_management",
                "criticality": "high",
                "frequency": "quarterly",
                "required_scenarios": ["document-service", "approval-workflow", "notification-service"],
                "involved_systems": ["document-service", "workflow-intelligence", "notification-service"],
                "duration_estimate": "45-60 minutes",
                "business_outcome": "Continuity plan reviewed and formally approved",
                "user_goals": [
                    "Review plan comprehensively",
                    "Provide feedback if needed",
                    "Approve or request changes",
                    "Ensure team awareness"
                ],
                "pain_points": [
                    "Large document to review",
                    "Need to understand technical details",
                    "Coordination with multiple teams"
                ],
                "success_criteria": [
                    "Plan reviewed thoroughly",
                    "Feedback provided",
                    "Approval decision made",
                    "Team notified"
                ]
            },

            # === Consultant Workflows ===
            {
                "name": "consultant-performs-compliance-audit",
                "description": "External consultant audits BCM compliance against ISO 22301",
                "persona": "BCM Compliance Auditor",
                "role": "auditor",
                "goal": "Assess organization's BCM compliance and provide audit report",
                "complexity": "high",
                "category": "compliance_management",
                "criticality": "high",
                "frequency": "annual",
                "required_scenarios": ["audit-service", "compliance-tracking", "reporting", "document-service"],
                "involved_systems": ["audit-service", "compliance-tracking", "analytics-specialist", "document-service"],
                "duration_estimate": "180-240 minutes",
                "business_outcome": "Comprehensive audit report with compliance gaps and recommendations",
                "user_goals": [
                    "Review all BCM documentation",
                    "Assess compliance status",
                    "Identify gaps",
                    "Generate audit report"
                ],
                "pain_points": [
                    "Large volume of documents",
                    "Complex compliance requirements",
                    "Need to verify evidence"
                ],
                "success_criteria": [
                    "All requirements reviewed",
                    "Gaps identified",
                    "Recommendations provided",
                    "Report delivered"
                ]
            },
            {
                "name": "consultant-delivers-tabletop-exercise",
                "description": "Consultant facilitates tabletop exercise for BCM plan validation",
                "persona": "BCM Exercise Facilitator",
                "role": "consultant",
                "goal": "Conduct effective tabletop exercise and capture learnings",
                "complexity": "high",
                "category": "simulation_exercises",
                "criticality": "high",
                "frequency": "semi-annual",
                "required_scenarios": ["simulation-service", "validation-service", "learning-system"],
                "involved_systems": ["simulation-service", "validation-service", "learning-system", "document-service"],
                "duration_estimate": "120-180 minutes",
                "business_outcome": "Exercise completed with identified improvements and lessons learned",
                "user_goals": [
                    "Set up realistic scenario",
                    "Facilitate team discussion",
                    "Capture observations",
                    "Generate improvement plan"
                ],
                "pain_points": [
                    "Keeping exercise realistic",
                    "Engaging all participants",
                    "Capturing learnings effectively"
                ],
                "success_criteria": [
                    "Exercise completed",
                    "All participants engaged",
                    "Gaps identified",
                    "Action plan created"
                ]
            },

            # === Executive Workflows ===
            {
                "name": "executive-reviews-bcm-dashboard",
                "description": "Executive reviews BCM program status and key metrics",
                "persona": "Chief Risk Officer",
                "role": "executive",
                "goal": "Understand BCM program health and make strategic decisions",
                "complexity": "low",
                "category": "business_continuity_planning",
                "criticality": "high",
                "frequency": "monthly",
                "required_scenarios": ["executive-dashboard", "analytics-specialist", "reporting"],
                "involved_systems": ["analytics-specialist", "grafana", "system-bcm-service"],
                "duration_estimate": "15-20 minutes",
                "business_outcome": "Executive informed of BCM status and strategic decisions made",
                "user_goals": [
                    "View high-level BCM metrics",
                    "Identify trends and issues",
                    "Review compliance status",
                    "Make strategic decisions"
                ],
                "pain_points": [
                    "Need for executive-level summaries",
                    "Too much technical detail",
                    "Limited time available"
                ],
                "success_criteria": [
                    "Dashboard reviewed",
                    "Key metrics understood",
                    "Issues identified",
                    "Decisions made"
                ]
            },
            {
                "name": "executive-approves-bcm-budget",
                "description": "CFO reviews and approves BCM program budget",
                "persona": "Chief Financial Officer",
                "role": "cfo",
                "goal": "Review BCM budget proposal and make approval decision",
                "complexity": "medium",
                "category": "business_continuity_planning",
                "criticality": "high",
                "frequency": "annual",
                "required_scenarios": ["approval-workflow", "analytics-specialist", "document-service"],
                "involved_systems": ["workflow-intelligence", "analytics-specialist", "document-service"],
                "duration_estimate": "30-45 minutes",
                "business_outcome": "BCM budget approved with funding allocated",
                "user_goals": [
                    "Review budget proposal",
                    "Assess ROI and business value",
                    "Compare to previous years",
                    "Make approval decision"
                ],
                "pain_points": [
                    "Need to justify costs",
                    "Competing budget priorities",
                    "Understanding technical requirements"
                ],
                "success_criteria": [
                    "Budget reviewed",
                    "Questions answered",
                    "Approval decision made",
                    "Funding allocated"
                ]
            },

            # === Multi-User Collaborative Workflows ===
            {
                "name": "team-collaborates-on-bcm-plan",
                "description": "Cross-functional team collaborates on comprehensive BCM plan",
                "persona": "BCM Team Lead",
                "role": "team_lead",
                "goal": "Coordinate team to create comprehensive BCM plan collaboratively",
                "complexity": "high",
                "category": "business_continuity_planning",
                "criticality": "critical",
                "frequency": "quarterly",
                "required_scenarios": ["collaboration", "document-service", "workflow-engine", "notification-service"],
                "involved_systems": ["document-service", "workflow-intelligence", "notification-service", "realtime-websocket"],
                "duration_estimate": "300-360 minutes (distributed)",
                "business_outcome": "Complete BCM plan created through team collaboration",
                "user_goals": [
                    "Coordinate team contributions",
                    "Track progress",
                    "Review and consolidate inputs",
                    "Finalize plan"
                ],
                "pain_points": [
                    "Coordinating multiple contributors",
                    "Version control",
                    "Conflicting inputs",
                    "Meeting deadlines"
                ],
                "success_criteria": [
                    "All sections completed",
                    "Team inputs consolidated",
                    "Quality reviewed",
                    "Plan approved"
                ]
            },

            # === Integration Workflows ===
            {
                "name": "integration-workflow-bcm-to-grc",
                "description": "Automated workflow integrating BCM with GRC platform",
                "persona": "Integration Specialist",
                "role": "integration_admin",
                "goal": "Set up automated data flow between BCM and GRC platforms",
                "complexity": "high",
                "category": "daily_operations",
                "criticality": "medium",
                "frequency": "one-time",
                "required_scenarios": ["integration-layer", "mcp-server", "api-gateway", "workflow-engine"],
                "involved_systems": ["mcp-server", "api-gateway", "workflow-intelligence", "eventbus"],
                "duration_estimate": "120-180 minutes",
                "business_outcome": "Automated integration between BCM and GRC platforms",
                "user_goals": [
                    "Configure API connections",
                    "Map data fields",
                    "Test data flow",
                    "Verify automation"
                ],
                "pain_points": [
                    "Complex API documentation",
                    "Data mapping challenges",
                    "Authentication setup",
                    "Error handling"
                ],
                "success_criteria": [
                    "Connection established",
                    "Data mapping complete",
                    "Tests passing",
                    "Automation working"
                ]
            }
        ]

    def _build_context(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build template context from workflow definition.

        This is the key method that uses LLM to generate workflow steps.

        Args:
            workflow: Workflow definition

        Returns:
            Context for template placeholder replacement
        """
        # Start with basic workflow metadata
        context = {
            "workflow_name": workflow["name"],
            "workflow_description": workflow["description"],
            "workflow_category": workflow["category"],
            "user_role": workflow["role"],
            "user_goal": workflow["goal"],
            "persona_name": workflow["persona"],
            "role": workflow["role"],
            "measurable_business_outcome": workflow["business_outcome"],
            "business_benefit": workflow["business_outcome"],
            "usage_frequency": workflow["frequency"],
            "business_criticality": workflow["criticality"],
            "estimated_duration": workflow["duration_estimate"],
            "timestamp": datetime.utcnow().isoformat(),

            # User context
            "goal_1": workflow["user_goals"][0] if len(workflow["user_goals"]) > 0 else "Complete workflow",
            "goal_2": workflow["user_goals"][1] if len(workflow["user_goals"]) > 1 else "Achieve business outcome",
            "pain_1": workflow["pain_points"][0] if len(workflow["pain_points"]) > 0 else "Complex process",
            "pain_2": workflow["pain_points"][1] if len(workflow["pain_points"]) > 1 else "Time consuming",
            "criteria_1": workflow["success_criteria"][0] if len(workflow["success_criteria"]) > 0 else "Task completed",
            "criteria_2": workflow["success_criteria"][1] if len(workflow["success_criteria"]) > 1 else "Quality validated",

            # Systems
            "system_1": workflow["involved_systems"][0] if len(workflow["involved_systems"]) > 0 else "system-bcm-service",
            "system_2": workflow["involved_systems"][1] if len(workflow["involved_systems"]) > 1 else "workflow-intelligence",

            # Placeholders for LLM-generated content (will be filled if LLM available)
            "step_title": "User performs action",
            "what_user_does": "User interacts with the system",
            "expected_system_behavior": "System responds appropriately",
            "step_outcome": "Step completed successfully",
            "expected_duration": "5 minutes",
            "step_title_2": "User continues workflow",
            "what_user_does_2": "User proceeds to next step",
            "expected_system_behavior_2": "System updates state",
            "step_outcome_2": "Progress saved",
            "expected_duration_2": "5 minutes",
            "step_title_3": "User completes workflow",
            "what_user_does_3": "User submits final step",
            "expected_system_behavior_3": "System finalizes workflow",
            "step_outcome_3": "Workflow completed",

            # Additional placeholders
            "application_name": "BCM Workspace",
            "entry_url": "/workflows/start",
            "landing_page": "/dashboard",
            "element_type": "button",
            "input_value": "sample_input",
            "measurable_result": workflow["business_outcome"],
            "data_artifacts": "workflow_data.json",
            "notification_list": "user, manager",
            "nav_1": "Dashboard",
            "nav_2": "Workflows",
            "business_metric_1": "workflow_completion_rate",
            "target_value": "95%",
            "business_metric_2": "user_satisfaction",
            "target_value_2": "4.5/5.0",
            "path_description": "Alternative navigation path",
            "step_sequence": "nav -> form -> submit",
            "path_description_b": "Quick path for experienced users",
            "step_sequence_b": "shortcut -> submit",
            "variation_1": "mobile_workflow",
            "variation_2": "desktop_workflow",
            "optional_step_1": "help_section",
            "invalid_data": "test@invalid",
            "invalid_input": "empty_field",
            "special_char_string": "<script>alert('test')</script>",
            "min_data": "minimum_required_fields",
            "max_data": "all_optional_fields",
            "target_time": "60 minutes",
            "target": "45 minutes",
            "p50_target": "30 seconds",
            "p95_target": "60 seconds",
            "unit": "count",
            "unit_2": "percentage",
            "stakeholder_roles": "manager, auditor",
            "threshold": "90 seconds",
            "business_objective": workflow["goal"],
            "systems_list": ", ".join(workflow["involved_systems"]),
            "compliance_list": "ISO 22301",
            "subsystem_1": "authentication",
            "subsystem_2": "authorization",
            "service_1": workflow["involved_systems"][0] if workflow["involved_systems"] else "api-gateway",
            "service_2": workflow["involved_systems"][1] if len(workflow["involved_systems"]) > 1 else "auth-service",
            "app_1": "bcm-workspace",
            "app_2": "admin-control-center",
            "retention_policy": "7 years",
            "approval_policy": "dual_approval",
            "access_policy": "rbac",
            "regulation_1": "ISO 22301",
            "regulation_2": "GDPR",
            "process_name": "upstream_process",
            "process_name_2": "downstream_process",
            "upstream_system": "erp_system",
            "data_type": "business_function_data",
            "data_type_2": "recovery_strategy_data",
            "notification_type": "email",
            "business_outcome_1": "plans_created",
            "business_outcome_2": "compliance_rate"
        }

        # Note: LLM enhancement would be called here if we had an async version of _build_context
        # For now, we use fallback generation. The LLM integration can be enabled
        # by refactoring BaseGenerator to support async _build_context method.

        return context

    async def _generate_journey_with_llm(
        self,
        workflow: Dict[str, Any],
        base_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Use LLM to generate realistic user journey steps.

        Args:
            workflow: Workflow definition
            base_context: Base context with metadata

        Returns:
            Enhanced context with LLM-generated journey details
        """
        # Fetch related L1-L3 scenarios
        related_scenarios = await self._fetch_related_scenarios(workflow)

        # Build prompt for LLM
        system_prompt = """You are a UX and workflow design expert specializing in Business Continuity Management platforms.
Generate realistic, detailed user journey steps that are practical and actionable."""

        user_prompt = f"""Generate a realistic user workflow for a Business Continuity Management platform.

**Workflow Context:**
- User Persona: {workflow['persona']}
- User Role: {workflow['role']}
- Goal: {workflow['goal']}
- Complexity: {workflow['complexity']}
- Duration: {workflow['duration_estimate']}
- Business Outcome: {workflow['business_outcome']}

**User Goals:**
{json.dumps(workflow['user_goals'], indent=2)}

**User Pain Points:**
{json.dumps(workflow['pain_points'], indent=2)}

**Success Criteria:**
{json.dumps(workflow['success_criteria'], indent=2)}

**Involved Systems:**
{json.dumps(workflow['involved_systems'], indent=2)}

**Available Related Scenarios:**
{json.dumps(related_scenarios[:5], indent=2)}

Generate a step-by-step user journey with 3 main steps. For each step provide:
1. Step title (brief, action-oriented)
2. What the user does (specific action)
3. Expected system behavior (what system does in response)
4. Step outcome (what's achieved)
5. Duration estimate (realistic timing)

Respond in JSON format:
{{
  "step_1": {{
    "title": "...",
    "user_action": "...",
    "system_response": "...",
    "outcome": "...",
    "duration": "..."
  }},
  "step_2": {{
    "title": "...",
    "user_action": "...",
    "system_response": "...",
    "outcome": "...",
    "duration": "..."
  }},
  "step_3": {{
    "title": "...",
    "user_action": "...",
    "system_response": "...",
    "outcome": "...",
    "duration": "..."
  }}
}}

Keep it realistic, practical, and aligned with the user's experience level and goals."""

        try:
            # Query LLM
            response = await self.llm_router.query(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                task_type="content_generation",
                temperature=0.7,
                max_tokens=1500
            )

            # Parse JSON response
            # Try to extract JSON from response (LLM might wrap in markdown)
            response_text = response.strip()
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()

            journey_data = json.loads(response_text)

            # Map to context keys
            enhanced_context = {}

            if "step_1" in journey_data:
                step1 = journey_data["step_1"]
                enhanced_context.update({
                    "step_title": step1.get("title", "User performs action"),
                    "what_user_does": step1.get("user_action", "User interacts with system"),
                    "expected_system_behavior": step1.get("system_response", "System responds"),
                    "step_outcome": step1.get("outcome", "Step completed"),
                    "expected_duration": step1.get("duration", "5 minutes")
                })

            if "step_2" in journey_data:
                step2 = journey_data["step_2"]
                enhanced_context.update({
                    "step_title_2": step2.get("title", "User continues workflow"),
                    "what_user_does_2": step2.get("user_action", "User proceeds"),
                    "expected_system_behavior_2": step2.get("system_response", "System updates"),
                    "step_outcome_2": step2.get("outcome", "Progress saved"),
                    "expected_duration_2": step2.get("duration", "5 minutes")
                })

            if "step_3" in journey_data:
                step3 = journey_data["step_3"]
                enhanced_context.update({
                    "step_title_3": step3.get("title", "User completes workflow"),
                    "what_user_does_3": step3.get("user_action", "User submits"),
                    "expected_system_behavior_3": step3.get("system_response", "System finalizes"),
                    "step_outcome_3": step3.get("outcome", "Workflow completed")
                })

            return enhanced_context

        except Exception as e:
            logger.warning(f"LLM journey generation failed: {e}")
            return {}

    async def _fetch_related_scenarios(self, workflow: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Fetch L1-L3 scenarios that are relevant for this workflow.

        Args:
            workflow: Workflow definition

        Returns:
            List of related scenario summaries
        """
        related = []

        try:
            # Get scenarios from registry based on required scenarios and involved systems
            required = workflow.get("required_scenarios", [])
            systems = workflow.get("involved_systems", [])

            # Use find_scenarios method which exists in the registry
            # Search for L1 scenarios
            l1_scenarios = await self.registry.find_scenarios(level=1)
            for scenario in l1_scenarios[:5]:  # Get first 5 L1 scenarios
                meta = scenario.get("meta", {})
                related.append({
                    "id": meta.get("id"),
                    "level": 1,
                    "type": "service",
                    "name": meta.get("service_name", meta.get("id", "unknown")),
                    "description": scenario.get("description", {}).get("summary", "")
                })

            # Search for L2 scenarios
            l2_scenarios = await self.registry.find_scenarios(level=2)
            for scenario in l2_scenarios[:3]:  # Get first 3 L2 scenarios
                meta = scenario.get("meta", {})
                related.append({
                    "id": meta.get("id"),
                    "level": 2,
                    "type": "subsystem",
                    "name": meta.get("subsystem", meta.get("id", "unknown")),
                    "description": scenario.get("description", {}).get("summary", "")
                })

            # Search for L3 scenarios
            l3_scenarios = await self.registry.find_scenarios(level=3)
            for scenario in l3_scenarios[:2]:  # Get first 2 L3 scenarios
                meta = scenario.get("meta", {})
                related.append({
                    "id": meta.get("id"),
                    "level": 3,
                    "type": "system",
                    "name": meta.get("system", meta.get("id", "unknown")),
                    "description": scenario.get("description", {}).get("summary", "")
                })

        except Exception as e:
            logger.warning(f"Failed to fetch related scenarios: {e}")

        return related

    def _get_template_name(self, workflow: Dict[str, Any]) -> str:
        """
        Get template name for workflow.

        Args:
            workflow: Workflow definition

        Returns:
            Template filename (always golden_standard_l4.yaml)
        """
        return "golden_standard_l4.yaml"


async def main():
    """Run L4 Workflow Generator standalone."""
    from template_loader import TemplateLoader
    from storage.registry import ScenarioRegistry

    print("="*70)
    print("L4 WORKFLOW GENERATOR (AI-POWERED)")
    print("="*70)

    # Initialize components
    loader = TemplateLoader(templates_dir="templates")
    registry = ScenarioRegistry()

    # Create generator
    generator = L4WorkflowGenerator(
        template_loader=loader,
        registry=registry,
        output_dir="generated/l4"
    )

    # Generate all scenarios
    scenario_ids = await generator.generate_all()

    # Print results
    stats = generator.get_statistics()
    print(f"\n Generated {stats['generated']}/{stats['total']} workflow scenarios")
    print(f" Saved to: generated/l4/")
    print(f" Scenario IDs: {len(scenario_ids)}")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    asyncio.run(main())
