# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class BCMPolicyWorkflow(models.Model):
    """Policy Management and Approval Workflows - Andreas Idea Implementation"""
    _name = 'bcm.policy.workflow'
    _description = 'BCM Policy Workflow Management'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Policy Name', required=True, tracking=True)
    policy_type = fields.Selection([
        ('bcm_policy', 'BCM Policy'),
        ('incident_response', 'Incident Response Policy'),
        ('risk_management', 'Risk Management Policy'),
        ('business_continuity', 'Business Continuity Policy'),
        ('crisis_management', 'Crisis Management Policy'),
        ('training_policy', 'Training Policy'),
        ('governance_policy', 'Governance Policy')
    ], string='Policy Type', required=True)

    # Policy Content
    policy_content = fields.Html('Policy Content')
    policy_summary = fields.Text('Executive Summary')

    # AI Enhancement (Andreas suggestion)
    ai_generated = fields.Boolean('AI Generated Policy')
    ai_templates_used = fields.Text('AI Templates Applied')
    ai_compliance_check = fields.Html('AI Compliance Analysis')

    # Approval Workflow (Andreas core idea)
    approval_status = fields.Selection([
        ('draft', 'Draft'),
        ('ai_review', 'AI Review'),
        ('stakeholder_review', 'Stakeholder Review'),
        ('legal_review', 'Legal Review'),
        ('management_approval', 'Management Approval'),
        ('board_approval', 'Board Approval'),
        ('approved', 'Approved'),
        ('published', 'Published'),
        ('archived', 'Archived')
    ], string='Approval Status', default='draft', tracking=True)

    # Workflow Participants
    policy_owner = fields.Many2one('res.users', 'Policy Owner', required=True)
    reviewers = fields.Many2many('res.users', 'policy_reviewers_rel', string='Reviewers')
    approvers = fields.Many2many('res.users', 'policy_approvers_rel', string='Approvers')

    # Approval Tracking
    approval_history = fields.One2many('bcm.policy.approval', 'policy_id', 'Approval History')
    current_approver = fields.Many2one('res.users', 'Current Approver')
    approval_deadline = fields.Datetime('Approval Deadline')

    # DMS Integration (Andreas suggestion)
    sharepoint_url = fields.Char('SharePoint URL')
    dms_document_id = fields.Char('DMS Document ID')
    version_history = fields.Text('Version History (JSON)')

    # Compliance Mapping
    iso_clauses = fields.Many2many('bcm.iso.clause', string='Related ISO 22301 Clauses')
    regulatory_requirements = fields.Text('Regulatory Requirements')

    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    def action_ai_policy_generation(self):
        """AI-powered policy generation (Andreas suggestion)"""
        try:
            ai_prompt = f"""
AI POLICY GENERATOR

POLICY REQUIREMENTS:
Policy Type: {self.policy_type}
Organization: {self.company_id.name}
ISO 22301 Compliance: Required

POLICY GENERATION REQUEST:
Generate comprehensive {self.policy_type} policy including:

1. POLICY STATEMENT:
   - Clear policy objectives
   - Scope and applicability
   - Authority and responsibility

2. PROCEDURES:
   - Step-by-step procedures
   - Role assignments
   - Decision criteria

3. COMPLIANCE ALIGNMENT:
   - ISO 22301 clause mapping
   - Regulatory requirements
   - Best practice alignment

4. IMPLEMENTATION:
   - Resource requirements
   - Training needs
   - Review schedules

Generate professional policy document ready for approval workflow.
"""

            # Call AI Orchestrator for policy generation
            import requests
            response = requests.post(
                'http://ai_orchestrator:8000/nlp/query',
                json={
                    'query': ai_prompt,
                    'context': {
                        'policy_type': self.policy_type,
                        'company': self.company_id.name
                    },
                    'user_role': 'policy_generator'
                },
                timeout=60
            )

            if response.status_code == 200:
                result = response.json()

                self.write({
                    'policy_content': result.get('response', ''),
                    'ai_generated': True,
                    'ai_templates_used': 'AI-generated policy template',
                    'approval_status': 'ai_review'
                })

                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('AI Policy Generated'),
                        'message': f'AI generated {self.policy_type} policy ready for review',
                        'type': 'success',
                    }
                }

        except Exception as e:
            raise UserError(f'AI policy generation failed: {str(e)}')

    def action_start_approval_workflow(self):
        """Start approval workflow (Andreas core feature)"""
        if not self.policy_content:
            raise UserError(_('Policy content required before starting approval'))

        # Create approval workflow
        workflow_steps = self._get_approval_workflow_steps()

        for step in workflow_steps:
            self.env['bcm.policy.approval'].create({
                'policy_id': self.id,
                'approval_step': step['step'],
                'approver_id': step['approver_id'],
                'status': 'pending',
                'deadline': step['deadline']
            })

        self.approval_status = 'stakeholder_review'
        self.current_approver = workflow_steps[0]['approver_id']

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Approval Workflow Started'),
                'message': 'Policy sent for stakeholder review',
                'type': 'success',
            }
        }

    def action_ai_compliance_check(self):
        """AI compliance validation (Andreas suggestion)"""
        try:
            compliance_prompt = f"""
AI COMPLIANCE CHECKER

POLICY COMPLIANCE ANALYSIS:
Policy Type: {self.policy_type}
Policy Content: {self.policy_content[:1000]}...

COMPLIANCE VALIDATION REQUIRED:

1. ISO 22301 ALIGNMENT:
   - Clause compliance verification
   - Gap identification
   - Best practice alignment

2. REGULATORY REQUIREMENTS:
   - Industry-specific requirements
   - Legal compliance
   - Risk mitigation adequacy

3. POLICY QUALITY:
   - Clarity and completeness
   - Implementation feasibility
   - Stakeholder consideration

Provide compliance assessment with specific recommendations.
"""

            import requests
            response = requests.post(
                'http://compliance_checker:8084/api/compliance/policy-check',
                json={
                    'policy_content': self.policy_content,
                    'policy_type': self.policy_type,
                    'compliance_framework': 'iso_22301'
                },
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                self.ai_compliance_check = result.get('compliance_html', 'Compliance check completed')

                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('AI Compliance Check Complete'),
                        'message': 'Policy compliance validated by AI',
                        'type': 'success',
                    }
                }

        except Exception as e:
            raise UserError(f'AI compliance check failed: {str(e)}')

    def _get_approval_workflow_steps(self):
        """Get approval workflow steps based on policy type"""
        base_workflow = [
            {'step': 'stakeholder_review', 'approver_id': self.policy_owner.id, 'deadline': fields.Datetime.now() + timedelta(days=3)},
            {'step': 'management_approval', 'approver_id': self.policy_owner.id, 'deadline': fields.Datetime.now() + timedelta(days=7)}
        ]

        if self.policy_type in ['governance_policy', 'crisis_management']:
            # Board approval required for critical policies
            base_workflow.append({
                'step': 'board_approval',
                'approver_id': self.policy_owner.id,
                'deadline': fields.Datetime.now() + timedelta(days=14)
            })

        return base_workflow

class BCMPolicyApproval(models.Model):
    """Policy Approval Tracking"""
    _name = 'bcm.policy.approval'
    _description = 'Policy Approval Step'

    policy_id = fields.Many2one('bcm.policy.workflow', 'Policy', required=True)
    approval_step = fields.Char('Approval Step', required=True)
    approver_id = fields.Many2one('res.users', 'Approver', required=True)

    status = fields.Selection([
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('delegated', 'Delegated')
    ], default='pending')

    approval_date = fields.Datetime('Approval Date')
    comments = fields.Text('Approval Comments')
    deadline = fields.Datetime('Deadline')

    def action_approve(self):
        """Approve policy step"""
        self.write({
            'status': 'approved',
            'approval_date': fields.Datetime.now()
        })

        # Move to next approval step
        self.policy_id._advance_approval_workflow()

    def action_reject(self):
        """Reject policy step"""
        self.write({
            'status': 'rejected',
            'approval_date': fields.Datetime.now()
        })

        # Reset policy to draft
        self.policy_id.approval_status = 'draft'