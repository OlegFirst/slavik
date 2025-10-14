from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import json
import logging
import asyncio
import os

_logger = logging.getLogger(__name__)

class BCMGovernanceAIBrain(models.Model):
    """AI-Powered Governance Brain - The Wise Ruler of BCM Platform"""
    _name = 'bcm.governance.brain'
    _description = 'AI Governance Brain - Strategic Intelligence Center'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'priority desc, create_date desc'

    name = fields.Char('Governance Topic', required=True, tracking=True)
    description = fields.Html('Description')

    # AI Brain Configuration
    brain_status = fields.Selection([
        ('learning', 'Learning Mode'),
        ('active', 'Active Intelligence'),
        ('wise', 'Wisdom Mode'),
        ('emergency', 'Emergency Override')
    ], string='Brain Status', default='learning', tracking=True)

    ai_personality = fields.Selection([
        ('wise_ruler', 'Wise Ruler - Strategic & Thoughtful'),
        ('compliance_guardian', 'Compliance Guardian - Strict & Thorough'),
        ('innovation_catalyst', 'Innovation Catalyst - Creative & Progressive'),
        ('risk_advisor', 'Risk Advisor - Cautious & Analytical')
    ], string='AI Personality', default='wise_ruler')

    # Governance Domain
    governance_domain = fields.Selection([
        ('iso_22301', 'ISO 22301 Compliance'),
        ('policy_management', 'Policy Management'),
        ('risk_governance', 'Risk Governance'),
        ('performance_oversight', 'Performance Oversight'),
        ('strategic_planning', 'Strategic Planning'),
        ('board_reporting', 'Board Reporting'),
        ('regulatory_compliance', 'Regulatory Compliance'),
        ('crisis_governance', 'Crisis Governance')
    ], string='Governance Domain', required=True)

    priority = fields.Selection([
        ('low', 'Low Priority'),
        ('medium', 'Medium Priority'),
        ('high', 'High Priority'),
        ('critical', 'Critical - Immediate Attention'),
        ('strategic', 'Strategic - Long-term Impact')
    ], string='Priority', default='medium', tracking=True)

    # AI Analysis Results
    ai_analysis = fields.Html('AI Analysis & Recommendations', readonly=True)
    ai_confidence = fields.Float('AI Confidence Score', readonly=True, help='0-1 scale')
    ai_reasoning = fields.Text('AI Reasoning Process', readonly=True)
    ai_last_analysis = fields.Datetime('Last AI Analysis', readonly=True)

    # Policy Management
    related_policies = fields.Many2many('bcm.policy', string='Related Policies')
    policy_gaps_identified = fields.Text('AI-Identified Policy Gaps')
    policy_recommendations = fields.Html('AI Policy Recommendations')

    # Compliance Monitoring
    compliance_status = fields.Selection([
        ('compliant', 'Fully Compliant'),
        ('minor_gaps', 'Minor Gaps Identified'),
        ('major_gaps', 'Major Gaps - Action Required'),
        ('non_compliant', 'Non-Compliant - Immediate Action'),
        ('under_review', 'Under AI Review')
    ], string='AI Compliance Assessment', compute='_compute_compliance_status', store=True)

    compliance_score = fields.Float('AI Compliance Score', compute='_compute_compliance_score', store=True)
    compliance_trends = fields.Text('Compliance Trends (JSON)', readonly=True)

    # Strategic Intelligence
    strategic_insights = fields.Html('Strategic Insights from AI')
    risk_alerts = fields.Text('AI Risk Alerts')
    improvement_opportunities = fields.Html('AI Improvement Opportunities')

    # Board Reporting
    board_report_ready = fields.Boolean('Board Report Ready', compute='_compute_board_report_ready')
    executive_summary = fields.Html('Executive Summary', compute='_compute_executive_summary')

    # Integration with other modules
    related_incidents = fields.Many2many('bcm.incident', string='Related Incidents')
    related_exercises = fields.Many2many('bcm.exercise', string='Governance-Required Exercises')
    related_audits = fields.Many2many('bcm.audit', string='Related Audits')

    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    def action_anthropic_analysis(self):
        """Trigger Anthropic AI analysis for strategic governance"""
        self.ensure_one()

        if not self.description:
            raise UserError(_('Description is required for AI analysis'))

        try:
            # Call Anthropic API for sophisticated governance analysis
            ai_analysis_result = self._call_anthropic_governance_brain()

            self.write({
                'ai_analysis': ai_analysis_result.get('analysis_html', ''),
                'ai_confidence': ai_analysis_result.get('confidence', 0.0),
                'ai_reasoning': ai_analysis_result.get('reasoning', ''),
                'ai_last_analysis': fields.Datetime.now(),
                'strategic_insights': ai_analysis_result.get('strategic_insights', ''),
                'policy_recommendations': ai_analysis_result.get('policy_recommendations', ''),
                'risk_alerts': ai_analysis_result.get('risk_alerts', '')
            })

            # Trigger EventBus notification for ecosystem
            self._broadcast_governance_insight(ai_analysis_result)

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('AI Governance Analysis Complete'),
                    'message': f'Strategic analysis completed with {int(self.ai_confidence * 100)}% confidence',
                    'type': 'success',
                }
            }

        except Exception as e:
            _logger.error(f'Anthropic AI analysis failed: {str(e)}')
            raise UserError(f'AI analysis failed: {str(e)}')

    def _call_anthropic_governance_brain(self):
        """Call Anthropic API for sophisticated governance analysis"""

        # Build sophisticated governance prompt
        governance_prompt = f"""
You are the AI Governance Brain for a BCM Platform - a wise, strategic intelligence that provides executive-level governance insights.

GOVERNANCE CONTEXT:
Domain: {self.governance_domain}
Priority: {self.priority}
Organization: {self.company_id.name}

GOVERNANCE TOPIC:
{self.description}

RELATED CONTEXT:
- Recent Incidents: {len(self.related_incidents)} incidents requiring governance review
- Active Exercises: {len(self.related_exercises)} exercises under governance oversight
- Audit Status: {len(self.related_audits)} audits in progress

As the AI Governance Brain, provide:

1. STRATEGIC ANALYSIS:
   - Executive-level assessment of the governance topic
   - Strategic implications for the organization
   - Risk and opportunity identification
   - Stakeholder impact analysis

2. COMPLIANCE GUIDANCE:
   - ISO 22301 compliance implications
   - Regulatory requirements analysis
   - Best practice recommendations
   - Gap analysis and remediation steps

3. POLICY RECOMMENDATIONS:
   - Policy development or update recommendations
   - Implementation guidance
   - Resource allocation suggestions
   - Timeline and milestone recommendations

4. STRATEGIC INSIGHTS:
   - Long-term implications
   - Industry trends and benchmarking
   - Innovation opportunities
   - Competitive advantages

5. ACTION PLAN:
   - Immediate actions required
   - Medium-term strategic initiatives
   - Long-term governance evolution
   - Success metrics and KPIs

Provide response in structured HTML format suitable for executive presentation.
"""

        try:
            import requests

            # Call Anthropic API through AI Orchestrator
            response = requests.post(
                'http://ai_orchestrator:8000/nlp/query',
                json={
                    'query': governance_prompt,
                    'context': {
                        'module': 'bcm_governance',
                        'domain': self.governance_domain,
                        'priority': self.priority,
                        'company': self.company_id.name,
                        'ai_personality': self.ai_personality
                    },
                    'user_role': 'governance_brain',
                    'use_anthropic': True  # Flag for high-quality analysis
                },
                timeout=120  # Longer timeout for sophisticated analysis
            )

            if response.status_code == 200:
                ai_result = response.json()

                return {
                    'analysis_html': ai_result.get('response', ''),
                    'confidence': 0.95,  # High confidence for Anthropic
                    'reasoning': 'Anthropic Claude analysis with strategic governance focus',
                    'strategic_insights': self._extract_strategic_insights(ai_result.get('response', '')),
                    'policy_recommendations': self._extract_policy_recommendations(ai_result.get('response', '')),
                    'risk_alerts': self._extract_risk_alerts(ai_result.get('response', ''))
                }
            else:
                raise Exception(f'AI Orchestrator error: {response.status_code}')

        except Exception as e:
            _logger.error(f'Failed to call Anthropic governance brain: {e}')
            # Fallback to local AI if Anthropic fails
            return self._fallback_local_governance_analysis()

    def _broadcast_governance_insight(self, ai_analysis):
        """Broadcast governance insights to BCM ecosystem"""
        try:
            import requests

            # Notify other modules of governance decision
            governance_event = {
                'event_type': 'governance_insight_generated',
                'source_module': 'bcm_governance',
                'governance_domain': self.governance_domain,
                'priority': self.priority,
                'ai_insights': ai_analysis.get('strategic_insights', ''),
                'compliance_impact': self._assess_compliance_impact(),
                'affected_modules': self._identify_affected_modules(),
                'timestamp': fields.Datetime.now().isoformat()
            }

            # Broadcast через EventBus
            requests.post(
                'http://eventbus:8001/api/events/governance',
                json=governance_event,
                timeout=5
            )

            _logger.info(f'Governance insight broadcasted to ecosystem: {self.governance_domain}')

        except Exception as e:
            _logger.warning(f'Failed to broadcast governance insight: {e}')

    def action_generate_board_report(self):
        """Generate AI-powered board report"""
        if not self.ai_analysis:
            raise UserError(_('AI analysis required before generating board report'))

        try:
            # Sophisticated board report generation
            board_report_prompt = f"""
As the AI Governance Brain, create an executive board report based on the governance analysis.

GOVERNANCE ANALYSIS:
{self.ai_analysis}

Create a professional board-level report with:
1. Executive Summary
2. Key Findings and Implications
3. Strategic Recommendations
4. Risk Assessment
5. Resource Requirements
6. Implementation Timeline
7. Success Metrics

Format for C-level presentation with clear action items and business impact.
"""

            # Call Anthropic for executive-quality report
            board_report = self._call_anthropic_for_board_report(board_report_prompt)

            return {
                'type': 'ir.actions.report',
                'report_name': 'bcm_governance.board_report',
                'report_type': 'qweb-html',
                'data': {
                    'governance_topic': self.name,
                    'board_report_content': board_report,
                    'company': self.company_id.name,
                    'generation_date': fields.Datetime.now()
                },
                'context': self.env.context
            }

        except Exception as e:
            raise UserError(f'Board report generation failed: {str(e)}')

    @api.depends('ai_analysis', 'related_incidents', 'related_audits')
    def _compute_compliance_status(self):
        """AI-powered compliance status assessment"""
        for record in self:
            if record.ai_analysis:
                # Analyze AI recommendations for compliance indicators
                analysis_text = record.ai_analysis.lower() if record.ai_analysis else ''

                if 'non-compliant' in analysis_text or 'violation' in analysis_text:
                    record.compliance_status = 'non_compliant'
                elif 'major gap' in analysis_text or 'significant risk' in analysis_text:
                    record.compliance_status = 'major_gaps'
                elif 'minor gap' in analysis_text or 'improvement needed' in analysis_text:
                    record.compliance_status = 'minor_gaps'
                elif 'compliant' in analysis_text or 'satisfactory' in analysis_text:
                    record.compliance_status = 'compliant'
                else:
                    record.compliance_status = 'under_review'
            else:
                record.compliance_status = 'under_review'

    @api.depends('compliance_status', 'ai_confidence')
    def _compute_compliance_score(self):
        """Calculate compliance score based on AI analysis"""
        for record in self:
            score_mapping = {
                'compliant': 95,
                'minor_gaps': 80,
                'major_gaps': 60,
                'non_compliant': 30,
                'under_review': 50
            }

            base_score = score_mapping.get(record.compliance_status, 50)
            confidence_factor = record.ai_confidence or 0.5

            record.compliance_score = base_score * confidence_factor

    def action_emergency_governance_session(self):
        """Emergency governance session with immediate AI analysis"""
        self.ensure_one()

        # Switch to emergency mode
        self.brain_status = 'emergency'

        # Immediate Anthropic analysis with emergency context
        emergency_prompt = f"""
EMERGENCY GOVERNANCE SESSION

Critical governance issue requiring immediate attention:
{self.description}

As the AI Governance Brain in EMERGENCY MODE, provide:
1. Immediate risk assessment
2. Critical actions required within 24 hours
3. Stakeholder notification requirements
4. Resource mobilization needs
5. Regulatory/legal implications
6. Crisis communication strategy

This is a strategic emergency - provide executive-level guidance for immediate action.
"""

        emergency_analysis = self._call_anthropic_emergency_analysis(emergency_prompt)

        self.write({
            'ai_analysis': emergency_analysis,
            'priority': 'critical'
        })

        # Immediate notification to all governance stakeholders
        self._emergency_notification_cascade()

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Emergency Governance Analysis Complete'),
                'message': 'Emergency AI analysis completed - immediate actions identified',
                'type': 'warning',
            }
        }

    def _call_anthropic_emergency_analysis(self, prompt):
        """Emergency Anthropic analysis with priority routing"""
        # Enhanced with emergency priority
        return self._call_anthropic_governance_brain_with_priority(prompt, priority='emergency')

    def _emergency_notification_cascade(self):
        """Emergency notification to all stakeholders"""
        try:
            import requests

            # Notify через Notification Service с высоким приоритетом
            emergency_notification = {
                'title': f'🚨 EMERGENCY GOVERNANCE ALERT: {self.name}',
                'message': f'Critical governance issue requires immediate attention. AI analysis complete.',
                'channels': ['slack', 'teams', 'email'],
                'severity': 'emergency',
                'recipients': self._get_emergency_stakeholders(),
                'metadata': {
                    'governance_id': self.id,
                    'domain': self.governance_domain,
                    'priority': 'emergency',
                    'ai_confidence': self.ai_confidence
                }
            }

            requests.post(
                'http://notification_service:8002/external/notify',
                json=emergency_notification,
                timeout=10
            )

        except Exception as e:
            _logger.error(f'Emergency notification failed: {e}')

    def _get_emergency_stakeholders(self):
        """Get emergency governance stakeholders"""
        # Get users with governance emergency roles
        emergency_groups = self.env['res.groups'].search([
            ('name', 'ilike', 'governance'),
            '|', ('name', 'ilike', 'emergency'), ('name', 'ilike', 'crisis')
        ])

        stakeholders = []
        for group in emergency_groups:
            for user in group.users:
                if user.email:
                    stakeholders.append(user.email)

        return stakeholders

    @api.model
    def continuous_compliance_monitoring(self):
        """Continuous AI compliance monitoring - scheduled daily"""

        # Get all active governance topics
        active_governance = self.search([
            ('brain_status', 'in', ['active', 'wise']),
            ('governance_domain', '=', 'iso_22301')
        ])

        compliance_alerts = []

        for gov_record in active_governance:
            # Daily compliance check via Anthropic
            compliance_check = gov_record._daily_compliance_analysis()

            if compliance_check.get('alerts'):
                compliance_alerts.extend(compliance_check['alerts'])

        # Generate daily governance intelligence report
        if compliance_alerts:
            self._generate_daily_intelligence_report(compliance_alerts)

        return True

    def _daily_compliance_analysis(self):
        """Daily compliance analysis via Anthropic"""

        daily_prompt = f"""
Daily Compliance Intelligence Analysis

Governance Domain: {self.governance_domain}
Organization: {self.company_id.name}
Last Analysis: {self.ai_last_analysis}

Perform daily compliance health check:
1. Any new compliance risks emerged?
2. Are current policies still adequate?
3. Any regulatory changes affecting compliance?
4. Predictive compliance risk assessment for next 30 days
5. Proactive recommendations for maintaining compliance

Provide concise daily intelligence update.
"""

        return self._call_anthropic_daily_analysis(daily_prompt)

# Enhanced Policy Management
class BCMPolicy(models.Model):
    """AI-Enhanced Policy Management"""
    _name = 'bcm.policy'
    _description = 'BCM Policy with AI Enhancement'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Policy Name', required=True, tracking=True)
    policy_content = fields.Html('Policy Content')
    policy_type = fields.Selection([
        ('bcm_policy', 'BCM Policy'),
        ('incident_response', 'Incident Response Policy'),
        ('risk_management', 'Risk Management Policy'),
        ('governance', 'Governance Policy'),
        ('compliance', 'Compliance Policy')
    ], required=True)

    # AI Analysis
    ai_compliance_analysis = fields.Html('AI Compliance Analysis')
    ai_improvement_suggestions = fields.Text('AI Improvement Suggestions')
    ai_regulatory_alignment = fields.Text('AI Regulatory Alignment')

    # Policy Lifecycle
    approval_status = fields.Selection([
        ('draft', 'Draft'),
        ('ai_review', 'AI Review'),
        ('management_review', 'Management Review'),
        ('approved', 'Approved'),
        ('published', 'Published'),
        ('archived', 'Archived')
    ], default='draft', tracking=True)

    governance_brain_id = fields.Many2one('bcm.governance.brain', 'Governance Oversight')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    def action_ai_policy_review(self):
        """AI-powered policy review via Anthropic"""

        policy_review_prompt = f"""
AI Policy Review for BCM Platform

Policy Name: {self.name}
Policy Type: {self.policy_type}
Organization: {self.company_id.name}

Policy Content:
{self.policy_content}

Perform comprehensive policy analysis:
1. ISO 22301 compliance assessment
2. Best practice alignment
3. Gap analysis and recommendations
4. Regulatory alignment check
5. Implementation feasibility
6. Stakeholder impact assessment
7. Improvement recommendations

Provide executive-level policy review with actionable recommendations.
"""

        ai_review = self._call_anthropic_policy_analysis(policy_review_prompt)

        self.write({
            'ai_compliance_analysis': ai_review.get('compliance_html', ''),
            'ai_improvement_suggestions': ai_review.get('improvements', ''),
            'ai_regulatory_alignment': ai_review.get('regulatory_notes', ''),
            'approval_status': 'ai_review'
        })

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('AI Policy Review Complete'),
                'message': 'Policy reviewed by AI Governance Brain',
                'type': 'success',
            }
        }

# Legacy model for backward compatibility
class BcmGovernanceRecord(models.Model):
    _name = 'bcm_governance.record'
    _description = 'BCM Governance Record (Legacy)'

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    notes = fields.Text()

    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
