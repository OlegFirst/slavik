# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta
import json
import logging

_logger = logging.getLogger(__name__)


class BCMProject(models.Model):
    _inherit = 'project.project'
    _description = 'BCM Enhanced Project'

    # ============== BCM SPECIFIC FIELDS ==============

    bcm_type = fields.Selection([
        ('recovery', 'Recovery Plan Implementation'),
        ('exercise', 'Exercise & Training'),
        ('audit', 'BCM Audit'),
        ('incident', 'Incident Response'),
        ('improvement', 'Continuous Improvement'),
        ('assessment', 'Risk & BIA Assessment'),
    ], string='BCM Project Type',
       help='Type of BCM project determines templates and automation')

    # Criticality and Priority
    criticality_level = fields.Selection([
        ('critical', 'Critical'),
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ], string='Criticality Level', default='medium')

    criticality_score = fields.Float(
        'Criticality Score (0-10)',
        compute='_compute_criticality_score',
        store=True,
        help='AI-calculated criticality based on business impact'
    )

    # Recovery Objectives (for recovery projects)
    recovery_time_objective = fields.Float('RTO (hours)',
        help='Recovery Time Objective - Maximum acceptable downtime')
    recovery_point_objective = fields.Float('RPO (hours)',
        help='Recovery Point Objective - Maximum acceptable data loss')
    maximum_tolerable_downtime = fields.Float('MTD (hours)',
        help='Maximum Tolerable Downtime before severe impact')

    # Health and Status
    health_status = fields.Selection([
        ('healthy', 'On Track'),
        ('warning', 'Needs Attention'),
        ('critical', 'Critical Issues'),
        ('blocked', 'Blocked'),
    ], string='Health Status',
       compute='_compute_health_status',
       store=True,
       help='Real-time project health indicator')

    health_score = fields.Integer(
        'Health Score (%)',
        compute='_compute_health_status',
        store=True
    )

    # AI Fields
    ai_insights = fields.Html('AI Insights', readonly=True)
    ai_recommendations = fields.Json('AI Recommendations')
    ai_risk_score = fields.Float('AI Risk Score', readonly=True)
    smart_deadline = fields.Datetime(
        'AI-Adjusted Deadline',
        compute='_compute_smart_deadline',
        help='Deadline adjusted based on team capacity and dependencies'
    )

    # BCM Specific Relations
    bcm_template_id = fields.Many2one(
        'bcm.project.template',
        string='BCM Template',
        help='Template used for project initialization'
    )

    # Integration fields for inter-module connectivity
    source_risk_id = fields.Char('Source Risk ID', help='ID of risk that triggered this project')
    source_incident_id = fields.Char('Source Incident ID', help='ID of incident that triggered this project')
    source_audit_finding_id = fields.Char('Source Audit Finding ID', help='ID of audit finding that triggered this project')
    source_module = fields.Char('Source Module', help='Module that created this project')
    workflow_id = fields.Char('Workflow ID', help='ID of workflow that created this project')

    # Virtual relations (will be real when other modules are installed)
    risk_ids = fields.One2many('bcm.risk', 'project_id', string='Associated Risks')
    incident_ids = fields.One2many('bcm.incident', 'project_id', string='Related Incidents')
    exercise_ids = fields.One2many('bcm.exercise', 'project_id', string='Exercises')

    # Automation flags
    auto_escalate = fields.Boolean('Auto Escalate', default=True,
        help='Automatically escalate issues based on rules')
    auto_assign = fields.Boolean('Auto Assign Tasks', default=True,
        help='Use AI to automatically assign tasks to best resources')
    auto_notify = fields.Boolean('Smart Notifications', default=True,
        help='Send intelligent notifications based on context')

    # Metrics
    tasks_overdue_count = fields.Integer(
        'Overdue Tasks',
        compute='_compute_task_metrics',
        store=True
    )
    tasks_at_risk_count = fields.Integer(
        'At Risk Tasks',
        compute='_compute_task_metrics',
        store=True
    )
    overall_progress = fields.Float(
        'Overall Progress (%)',
        compute='_compute_task_metrics',
        store=True
    )

    # ============== COMPUTED FIELDS ==============

    @api.depends('task_ids.stage_id', 'task_ids.date_deadline', 'task_ids.priority')
    def _compute_health_status(self):
        """Calculate real-time project health"""
        for project in self:
            if not project.task_ids:
                project.health_status = 'healthy'
                project.health_score = 100
                continue

            # Collect metrics
            total_tasks = len(project.task_ids)
            completed_tasks = len(project.task_ids.filtered(lambda t: t.stage_id.fold))
            overdue_tasks = len(project.task_ids.filtered(
                lambda t: t.date_deadline and
                         t.date_deadline < fields.Date.today() and
                         not t.stage_id.fold
            ))
            blocked_tasks = len(project.task_ids.filtered(
                lambda t: t.kanban_state == 'blocked'
            ))

            # Calculate health score
            score = 100
            score -= (overdue_tasks / total_tasks * 40) if total_tasks else 0
            score -= (blocked_tasks / total_tasks * 30) if total_tasks else 0

            # Add progress factor
            if total_tasks:
                progress_factor = (completed_tasks / total_tasks) * 20
                score = min(100, score + progress_factor)

            project.health_score = max(0, int(score))

            # Determine status
            if blocked_tasks > 0 and blocked_tasks >= total_tasks * 0.3:
                project.health_status = 'blocked'
            elif score < 40:
                project.health_status = 'critical'
            elif score < 70:
                project.health_status = 'warning'
            else:
                project.health_status = 'healthy'

    @api.depends('criticality_level', 'bcm_type', 'risk_ids')
    def _compute_criticality_score(self):
        """Calculate criticality score using AI if available"""
        for project in self:
            base_score = {
                'critical': 10,
                'high': 7.5,
                'medium': 5,
                'low': 2.5
            }.get(project.criticality_level, 5)

            # Adjust based on BCM type
            if project.bcm_type == 'incident':
                base_score *= 1.5
            elif project.bcm_type == 'recovery':
                base_score *= 1.3

            # Consider associated risks
            if project.risk_ids:
                max_risk = max(project.risk_ids.mapped('risk_score') or [0])
                base_score = (base_score + max_risk) / 2

            project.criticality_score = min(10, base_score)

    @api.depends('date_deadline', 'task_ids.date_deadline', 'health_status')
    def _compute_smart_deadline(self):
        """Calculate AI-adjusted deadline based on various factors"""
        for project in self:
            if not project.date_deadline:
                project.smart_deadline = False
                continue

            # Start with original deadline
            deadline = project.date_deadline

            # Adjust based on health
            if project.health_status == 'critical':
                # Need more time if critical
                deadline = deadline + timedelta(days=7)
            elif project.health_status == 'warning':
                deadline = deadline + timedelta(days=3)

            project.smart_deadline = deadline

    @api.depends('task_ids.stage_id', 'task_ids.date_deadline')
    def _compute_task_metrics(self):
        """Calculate task-based metrics"""
        for project in self:
            tasks = project.task_ids.filtered(lambda t: not t.stage_id.fold)

            project.tasks_overdue_count = len(tasks.filtered(
                lambda t: t.date_deadline and t.date_deadline < fields.Date.today()
            ))

            project.tasks_at_risk_count = len(tasks.filtered(
                lambda t: t.date_deadline and
                         fields.Date.today() <= t.date_deadline <= fields.Date.today() + timedelta(days=3)
            ))

            if project.task_ids:
                completed = len(project.task_ids.filtered(lambda t: t.stage_id.fold))
                project.overall_progress = (completed / len(project.task_ids)) * 100
            else:
                project.overall_progress = 0

    # ============== CRUD OVERRIDES ==============

    @api.model
    def create(self, vals):
        """Enhanced create with BCM automation"""
        # Set template if BCM type is specified
        if vals.get('bcm_type') and not vals.get('bcm_template_id'):
            template = self._find_best_template(vals['bcm_type'])
            if template:
                vals['bcm_template_id'] = template.id

        project = super().create(vals)

        # BCM specific initialization
        if project.bcm_type:
            project._initialize_bcm_project()

        return project

    def write(self, vals):
        """Enhanced write with change tracking"""
        # Track critical changes
        critical_fields = ['bcm_type', 'criticality_level', 'date_deadline']
        changed_critical = any(field in vals for field in critical_fields)

        result = super().write(vals)

        if changed_critical:
            self._on_critical_change()

        return result

    # ============== PRIVATE METHODS ==============

    def _initialize_bcm_project(self):
        """Initialize BCM project with intelligent setup"""
        self.ensure_one()

        try:
            # Create standard stages
            self._create_bcm_stages()

            # Generate initial tasks
            if self.auto_assign:
                self._generate_initial_tasks()

            # Set up automation rules
            self._setup_automation_rules()

            # Subscribe stakeholders
            self._auto_subscribe_stakeholders()

            # Create initial calendar events
            self._create_milestone_events()

            # Get AI insights if available
            self._get_initial_ai_insights()

            # Log successful initialization
            self.message_post(
                body=_("✅ BCM Project initialized successfully with %d tasks") % len(self.task_ids),
                message_type='notification'
            )

        except Exception as e:
            _logger.error(f"Failed to initialize BCM project {self.id}: {str(e)}")
            self.message_post(
                body=_("⚠️ Project initialization partially failed: %s") % str(e),
                message_type='notification'
            )

    def _create_bcm_stages(self):
        """Create standard BCM stages based on project type"""
        self.ensure_one()

        stage_templates = {
            'recovery': [
                ('init', 'Initiation', 'Κickoff and planning', 1, '0'),
                ('analysis', 'Impact Analysis', 'Analyze business impact', 2, '0'),
                ('design', 'Solution Design', 'Design recovery solution', 3, '0'),
                ('implement', 'Implementation', 'Implement solution', 4, '1'),
                ('test', 'Testing', 'Test recovery procedures', 5, '0'),
                ('deploy', 'Deployment', 'Deploy to production', 6, '0'),
                ('closure', 'Closure', 'Project closure', 7, '0', True),
            ],
            'exercise': [
                ('planning', 'Planning', 'Exercise planning', 1, '0'),
                ('scenario', 'Scenario Design', 'Create exercise scenario', 2, '0'),
                ('prepare', 'Preparation', 'Prepare resources', 3, '0'),
                ('execute', 'Execution', 'Run the exercise', 4, '1'),
                ('evaluate', 'Evaluation', 'Evaluate results', 5, '0'),
                ('report', 'Reporting', 'Create reports', 6, '0'),
                ('done', 'Completed', 'Exercise completed', 7, '0', True),
            ],
            'incident': [
                ('detected', 'Detection', 'Incident detected', 1, '2'),
                ('assessment', 'Assessment', 'Assess impact', 2, '2'),
                ('response', 'Response', 'Active response', 3, '1'),
                ('recovery', 'Recovery', 'Recovery actions', 4, '1'),
                ('review', 'Review', 'Post-incident review', 5, '0'),
                ('closed', 'Closed', 'Incident closed', 6, '0', True),
            ],
        }

        stages_data = stage_templates.get(self.bcm_type, [])
        if not stages_data:
            # Default stages
            stages_data = [
                ('new', 'New', 'New tasks', 1, '0'),
                ('progress', 'In Progress', 'Work in progress', 2, '1'),
                ('review', 'Review', 'Under review', 3, '0'),
                ('done', 'Done', 'Completed', 4, '0', True),
            ]

        for stage_data in stages_data:
            code, name, desc, seq, priority = stage_data[:5]
            fold = stage_data[5] if len(stage_data) > 5 else False

            self.env['project.task.type'].create({
                'name': name,
                'sequence': seq,
                'project_ids': [(4, self.id)],
                'description': desc,
                'fold': fold,
            })

    def _generate_initial_tasks(self):
        """Generate initial tasks using AI or templates"""
        self.ensure_one()

        # Try AI generation first
        if self._try_ai_task_generation():
            return

        # Fallback to template-based generation
        self._generate_template_tasks()

    def _try_ai_task_generation(self):
        """Try to generate tasks using AI service"""
        try:
            ai_connector = self.env['bcm.ai.connector'].sudo()
            if not ai_connector.is_configured():
                return False

            response = ai_connector.call_service('task_generator', {
                'project_type': self.bcm_type,
                'project_name': self.name,
                'criticality': self.criticality_level,
                'context': {
                    'company': self.company_id.name,
                    'team_size': len(self.user_id),
                    'deadline': str(self.date_deadline) if self.date_deadline else None,
                }
            })

            if response.get('success') and response.get('tasks'):
                self._create_tasks_from_ai_response(response['tasks'])
                return True

        except Exception as e:
            _logger.warning(f"AI task generation failed: {str(e)}")

        return False

    def _generate_template_tasks(self):
        """Generate tasks from templates"""
        self.ensure_one()

        # Task templates by project type
        task_templates = {
            'recovery': [
                ('Conduct Business Impact Analysis', 'analysis', 16, '1'),
                ('Identify Critical Processes', 'analysis', 8, '1'),
                ('Define Recovery Objectives', 'analysis', 4, '1'),
                ('Design Recovery Strategy', 'design', 24, '1'),
                ('Document Recovery Procedures', 'design', 16, '0'),
                ('Prepare Recovery Resources', 'implement', 8, '0'),
                ('Conduct Recovery Test', 'test', 8, '1'),
                ('Validate Recovery Time', 'test', 4, '1'),
                ('Deploy Recovery Plan', 'deploy', 8, '0'),
                ('Train Recovery Team', 'deploy', 16, '0'),
            ],
            'exercise': [
                ('Define Exercise Objectives', 'planning', 4, '1'),
                ('Select Exercise Type', 'planning', 2, '1'),
                ('Identify Participants', 'planning', 4, '0'),
                ('Develop Exercise Scenario', 'scenario', 16, '1'),
                ('Prepare Exercise Materials', 'prepare', 8, '0'),
                ('Book Resources and Venues', 'prepare', 4, '0'),
                ('Conduct Pre-Exercise Briefing', 'prepare', 2, '1'),
                ('Execute Exercise', 'execute', 8, '2'),
                ('Collect Participant Feedback', 'evaluate', 4, '0'),
                ('Create Exercise Report', 'report', 8, '1'),
            ],
        }

        tasks_data = task_templates.get(self.bcm_type, [])

        # Get stages
        stages = self.type_ids.sorted('sequence')
        stage_map = {stage.name.lower(): stage for stage in stages}

        for task_name, stage_key, hours, priority in tasks_data:
            # Find matching stage
            stage = None
            for key in stage_map:
                if stage_key.lower() in key:
                    stage = stage_map[key]
                    break

            if not stage and stages:
                stage = stages[0]

            # Calculate deadline
            if self.date_deadline:
                # Distribute tasks across project timeline
                task_deadline = self.date_deadline - timedelta(days=len(tasks_data) - tasks_data.index((task_name, stage_key, hours, priority)))
            else:
                task_deadline = fields.Date.today() + timedelta(days=7)

            # Create task
            self.env['project.task'].create({
                'name': task_name,
                'project_id': self.id,
                'stage_id': stage.id if stage else False,
                'planned_hours': hours,
                'priority': priority,
                'date_deadline': task_deadline,
                'description': f"<p>Auto-generated task for {self.bcm_type} project</p>",
                'user_ids': [(4, self._find_best_assignee_for_task(task_name).id)] if self.auto_assign else False,
            })

    def _find_best_assignee_for_task(self, task_name):
        """Find the best assignee for a task using smart logic"""
        self.ensure_one()

        # Get all BCM users
        bcm_users = self.env['res.users'].search([
            ('share', '=', False),  # Internal users only
            ('company_id', '=', self.company_id.id),
        ])

        if not bcm_users:
            return self.env.user

        # Simple workload balancing
        user_workload = {}
        for user in bcm_users:
            active_tasks = self.env['project.task'].search_count([
                ('user_ids', 'in', user.id),
                ('stage_id.fold', '=', False),
            ])
            user_workload[user.id] = active_tasks

        # Return user with least workload
        best_user_id = min(user_workload, key=user_workload.get)
        return self.env['res.users'].browse(best_user_id)

    # ============== ACTIONS ==============

    def action_generate_recovery_plan(self):
        """Generate a complete recovery plan"""
        self.ensure_one()

        if self.bcm_type != 'recovery':
            raise UserError(_("This action is only available for Recovery projects"))

        # Implementation would generate comprehensive recovery plan
        # This is a placeholder for the actual implementation

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Recovery Plan Generation'),
                'message': _('Recovery plan generation started. This may take a few moments.'),
                'type': 'info',
                'sticky': False,
            }
        }

    def action_run_health_check(self):
        """Run comprehensive health check"""
        self.ensure_one()

        # Force recompute
        self._compute_health_status()
        self._compute_task_metrics()

        # Get AI insights if available
        self._get_ai_health_insights()

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Health Check Complete'),
                'message': _('Project health: %s (%d%%)') % (self.health_status, self.health_score),
                'type': 'success' if self.health_status == 'healthy' else 'warning',
                'sticky': False,
            }
        }

    def action_escalate(self):
        """Manually escalate project issues"""
        self.ensure_one()

        # Create escalation
        self._escalate_project_issues('manual')

        # Publish escalation event to other modules
        self._publish_integration_event('project_escalated', {
            'project_id': self.id,
            'health_status': self.health_status,
            'criticality_level': self.criticality_level,
            'escalation_type': 'manual',
            'issues_count': self.tasks_overdue_count,
        })

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Escalation'),
                'message': _('Project issues have been escalated to management'),
                'type': 'warning',
                'sticky': False,
            }
        }

    # ============== AUTOMATION METHODS ==============

    @api.model
    def _cron_check_project_health(self):
        """Scheduled job to check all BCM project health"""
        projects = self.search([
            ('bcm_type', '!=', False),
            ('active', '=', True),
        ])

        for project in projects:
            old_health = project.health_status
            project._compute_health_status()

            # Check if health degraded
            if old_health in ['healthy', 'warning'] and project.health_status in ['critical', 'blocked']:
                project._escalate_project_issues('auto')

            # Check for overdue tasks
            if project.tasks_overdue_count > 3:
                project._notify_overdue_tasks()

    def _escalate_project_issues(self, escalation_type='auto'):
        """Escalate project issues to management"""
        self.ensure_one()

        # Prepare escalation data
        issues = []
        if self.health_status == 'critical':
            issues.append('Project health is critical')
        if self.health_status == 'blocked':
            issues.append('Project is blocked')
        if self.tasks_overdue_count > 0:
            issues.append(f'{self.tasks_overdue_count} tasks are overdue')

        # Create calendar event for crisis meeting
        if self.health_status in ['critical', 'blocked']:
            meeting = self.env['calendar.event'].create({
                'name': f'URGENT: {self.name} - Crisis Meeting',
                'start': fields.Datetime.now() + timedelta(hours=1),
                'stop': fields.Datetime.now() + timedelta(hours=2),
                'partner_ids': [(4, self.user_id.partner_id.id)],
                'description': f"""
                    <p><strong>Project Crisis Meeting</strong></p>
                    <p>Project: {self.name}</p>
                    <p>Type: {self.bcm_type}</p>
                    <p>Health Status: {self.health_status}</p>
                    <p>Issues:</p>
                    <ul>
                        {''.join(f'<li>{issue}</li>' for issue in issues)}
                    </ul>
                """,
            })

        # Send notification
        self.message_post(
            body=f"""
                <p><strong>⚠️ Project Escalation ({escalation_type})</strong></p>
                <ul>
                    {''.join(f'<li>{issue}</li>' for issue in issues)}
                </ul>
                <p>Immediate action required!</p>
            """,
            subject=f'ESCALATION: {self.name}',
            partner_ids=self.user_id.partner_id.ids,
            subtype_xmlid='mail.mt_comment',
            message_type='notification',
        )

    def _get_initial_ai_insights(self):
        """Get AI insights for the project"""
        self.ensure_one()

        try:
            ai_connector = self.env['bcm.ai.connector'].sudo()
            if ai_connector.is_configured():
                insights = ai_connector.get_project_insights(self)
                if insights:
                    self.ai_insights = insights.get('html_summary')
                    self.ai_recommendations = insights.get('recommendations')
                    self.ai_risk_score = insights.get('risk_score', 0)
        except Exception as e:
            _logger.warning(f"Could not get AI insights: {str(e)}")

    # ============== HELPER METHODS ==============

    def _find_best_template(self, bcm_type):
        """Find the best template for BCM type"""
        return self.env['bcm.project.template'].search([
            ('bcm_type', '=', bcm_type),
            ('active', '=', True),
        ], limit=1)

    def _auto_subscribe_stakeholders(self):
        """Auto-subscribe relevant stakeholders"""
        self.ensure_one()

        # Subscribe project manager
        if self.user_id:
            self.message_subscribe(partner_ids=self.user_id.partner_id.ids)

        # Subscribe BCM team based on type
        # This would be configured in real implementation
        pass

    def _create_milestone_events(self):
        """Create calendar events for major milestones"""
        self.ensure_one()

        if not self.date_deadline:
            return

        # Create deadline reminder
        self.env['calendar.event'].create({
            'name': f'{self.name} - Project Deadline',
            'start': self.date_deadline,
            'stop': self.date_deadline + timedelta(hours=1),
            'partner_ids': [(4, self.user_id.partner_id.id)],
            'alarm_ids': [(0, 0, {
                'name': '1 week before',
                'duration': 7,
                'interval': 'days',
                'alarm_type': 'notification',
            })],
        })

    # ============== INTEGRATION HOOKS - ПРЕВРАЩЕНИЕ В "ОРГАН" ==============

    @api.model
    def create(self, vals):
        """Override create to publish integration events"""
        project = super(BCMProject, self).create(vals)

        # Publish project creation event to other modules
        if project.bcm_type:
            project._publish_integration_event('project_created', {
                'project_id': project.id,
                'project_name': project.name,
                'bcm_type': project.bcm_type,
                'criticality_level': project.criticality_level,
                'source_module': vals.get('source_module', 'bcm_project_management'),
                'source_trigger': {
                    'risk_id': vals.get('source_risk_id'),
                    'incident_id': vals.get('source_incident_id'),
                    'audit_finding_id': vals.get('source_audit_finding_id'),
                }
            })

        return project

    def write(self, vals):
        """Override write to detect health changes and trigger integration events"""

        old_health_status = {p.id: p.health_status for p in self}
        old_criticality = {p.id: p.criticality_level for p in self}

        result = super(BCMProject, self).write(vals)

        # Check for health status changes
        for project in self:
            if project.bcm_type:
                # Health status changed
                if project.health_status != old_health_status.get(project.id):
                    project._on_health_status_changed(old_health_status.get(project.id))

                # Criticality level changed
                if project.criticality_level != old_criticality.get(project.id):
                    project._on_criticality_changed(old_criticality.get(project.id))

        return result

    def _on_health_status_changed(self, old_health_status):
        """Triggered when project health status changes"""
        self.ensure_one()

        # Publish health change event
        self._publish_integration_event('project_health_changed', {
            'project_id': self.id,
            'project_name': self.name,
            'old_health_status': old_health_status,
            'new_health_status': self.health_status,
            'health_score': self.health_score,
            'criticality_level': self.criticality_level,
        })

        # Auto-escalate if health becomes critical
        if self.auto_escalate and self.health_status == 'critical' and old_health_status != 'critical':
            self._escalate_project_issues('auto_health_critical')

        # Trigger integration with other systems
        if self.health_status == 'critical':
            self._trigger_critical_health_response()

    def _on_criticality_changed(self, old_criticality):
        """Triggered when project criticality changes"""
        self.ensure_one()

        self._publish_integration_event('project_criticality_changed', {
            'project_id': self.id,
            'old_criticality': old_criticality,
            'new_criticality': self.criticality_level,
            'auto_actions_needed': self.criticality_level in ['high', 'critical'],
        })

    def _trigger_critical_health_response(self):
        """Triggers coordinated response when project becomes critical"""
        self.ensure_one()

        # Check if we have integration hub
        if 'bcm.integration.hub' in self.env:
            integration_hub = self.env['bcm.integration.hub']

            # Trigger intelligent coordination across all BCM modules
            coordination_result = integration_hub.coordinate_intelligent_response(
                'critical_project_health',
                {
                    'project_id': self.id,
                    'project_name': self.name,
                    'bcm_type': self.bcm_type,
                    'health_score': self.health_score,
                    'overdue_tasks': self.tasks_overdue_count,
                    'team_capacity': len(self.member_ids),
                    'business_impact': self._assess_business_impact(),
                }
            )

            _logger.info(f"Coordinated critical response for project {self.id}: {coordination_result}")

    def _assess_business_impact(self):
        """Оценивает бизнес-воздействие критического проекта"""
        self.ensure_one()

        impact_factors = {
            'recovery': 'high',  # Recovery projects always have high business impact
            'incident': 'high',  # Incident response is critical
            'audit': 'medium',   # Audit compliance is important but not urgent
            'exercise': 'low',   # Exercises are planned activities
            'improvement': 'medium',  # Improvements are valuable but not urgent
            'assessment': 'medium',   # Assessments inform decisions
        }

        base_impact = impact_factors.get(self.bcm_type, 'medium')

        # Increase impact based on criticality
        if self.criticality_level == 'critical':
            return 'critical'
        elif self.criticality_level == 'high' and base_impact in ['medium', 'high']:
            return 'high'

        return base_impact

    def _publish_integration_event(self, event_type, event_data, priority='normal'):
        """Публикует событие интеграции для других модулей"""
        self.ensure_one()

        # Check if Event Bus is available
        if 'bcm.event.bus' in self.env:
            event_bus = self.env['bcm.event.bus']

            event_bus.publish_event(
                event_type,
                'bcm_project_management',
                event_data,
                priority=priority
            )

            _logger.info(f"Published integration event {event_type} for project {self.id}")

        # Fallback: process through AI Bridge if available
        elif 'bcm.ai.bridge' in self.env:
            bridge = self.env['bcm.ai.bridge'].get_instance()
            bridge.process_real_time_integration(
                'bcm_project_management',
                event_type,
                event_data
            )

    # ============== WORKFLOW INTEGRATION ==============

    def execute_workflow_step(self, workflow_id, step_action, step_data):
        """Выполняет шаг workflow для интеграции между модулями"""
        self.ensure_one()

        workflow_actions = {
            'activate_recovery_project': self._workflow_activate_recovery,
            'create_mitigation_project': self._workflow_create_mitigation,
            'escalate_to_incident': self._workflow_escalate_to_incident,
            'generate_audit_tasks': self._workflow_generate_audit_tasks,
        }

        action_handler = workflow_actions.get(step_action)
        if action_handler:
            return action_handler(workflow_id, step_data)

        _logger.warning(f"Unknown workflow action {step_action} for project {self.id}")
        return {'success': False, 'error': f'Unknown workflow action: {step_action}'}

    def _workflow_activate_recovery(self, workflow_id, step_data):
        """Workflow action: активация проекта восстановления"""
        self.ensure_one()

        # Update project to recovery type if not already
        if self.bcm_type != 'recovery':
            self.bcm_type = 'recovery'

        # Set recovery objectives from step data
        if 'rto' in step_data:
            self.recovery_time_objective = step_data['rto']
        if 'rpo' in step_data:
            self.recovery_point_objective = step_data['rpo']
        if 'mtd' in step_data:
            self.maximum_tolerable_downtime = step_data['mtd']

        # Auto-generate recovery tasks
        self._generate_recovery_tasks()

        return {
            'success': True,
            'result': f'Recovery project {self.id} activated',
            'output_data': {
                'recovery_project_id': self.id,
                'rto': self.recovery_time_objective,
                'rpo': self.recovery_point_objective,
            }
        }

    def _workflow_create_mitigation(self, workflow_id, step_data):
        """Workflow action: создание проекта митигации"""
        self.ensure_one()

        # Update project type to improvement for mitigation
        if self.bcm_type != 'improvement':
            self.bcm_type = 'improvement'

        # Create mitigation-specific tasks
        risk_level = step_data.get('risk_level', 'medium')
        self._generate_mitigation_tasks(risk_level)

        return {
            'success': True,
            'result': f'Mitigation project {self.id} configured',
            'output_data': {'mitigation_project_id': self.id}
        }

    def _generate_recovery_tasks(self):
        """Генерирует задачи восстановления"""
        self.ensure_one()

        recovery_tasks = [
            ('Assess system damage', 'assessment'),
            ('Activate backup systems', 'implementation'),
            ('Restore critical data', 'implementation'),
            ('Validate system integrity', 'testing'),
            ('Resume normal operations', 'implementation'),
            ('Post-recovery review', 'assessment'),
        ]

        for i, (task_name, task_type) in enumerate(recovery_tasks):
            self.env['project.task'].create({
                'name': task_name,
                'project_id': self.id,
                'bcm_task_type': task_type,
                'sequence': i + 1,
            })

    def _generate_mitigation_tasks(self, risk_level):
        """Генерирует задачи митигации риска"""
        self.ensure_one()

        base_tasks = [
            ('Analyze risk factors', 'assessment'),
            ('Develop mitigation strategy', 'implementation'),
            ('Implement risk controls', 'implementation'),
            ('Test mitigation measures', 'testing'),
            ('Document procedures', 'implementation'),
            ('Monitor effectiveness', 'assessment'),
        ]

        # Add extra tasks for high/critical risks
        if risk_level in ['high', 'critical']:
            base_tasks.extend([
                ('Executive briefing', 'assessment'),
                ('Stakeholder communication', 'implementation'),
                ('Contingency planning', 'implementation'),
            ])

        for i, (task_name, task_type) in enumerate(base_tasks):
            self.env['project.task'].create({
                'name': task_name,
                'project_id': self.id,
                'bcm_task_type': task_type,
                'sequence': i + 1,
            })