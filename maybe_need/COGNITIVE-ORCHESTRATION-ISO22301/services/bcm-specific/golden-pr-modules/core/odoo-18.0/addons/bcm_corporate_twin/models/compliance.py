# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime, timedelta

class CorporateCompliance(models.Model):
    """Compliance tracking for corporate digital twin"""
    _name = 'bcm.corporate.compliance'
    _description = 'Corporate Compliance Tracking'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char('Compliance Item', required=True)
    corporate_twin_id = fields.Many2one('bcm.corporate.twin', 'Corporate Twin', required=True)
    active = fields.Boolean('Active', default=True)

    # Compliance Type
    compliance_type = fields.Selection([
        ('regulatory', 'Regulatory'),
        ('industry', 'Industry Standard'),
        ('internal', 'Internal Policy'),
        ('contractual', 'Contractual'),
        ('voluntary', 'Voluntary')
    ], string='Compliance Type', default='regulatory')

    # Standards and Regulations
    standard = fields.Selection([
        ('iso22301', 'ISO 22301 - BCM'),
        ('iso27001', 'ISO 27001 - Information Security'),
        ('iso31000', 'ISO 31000 - Risk Management'),
        ('sox', 'SOX - Sarbanes-Oxley'),
        ('gdpr', 'GDPR - Data Protection'),
        ('hipaa', 'HIPAA - Healthcare'),
        ('pci_dss', 'PCI DSS - Payment Card'),
        ('basel', 'Basel III - Banking'),
        ('custom', 'Custom Standard')
    ], string='Standard/Regulation')

    custom_standard = fields.Char('Custom Standard Name')

    # Compliance Status
    compliance_status = fields.Selection([
        ('compliant', 'Compliant'),
        ('partial', 'Partially Compliant'),
        ('non_compliant', 'Non-Compliant'),
        ('in_progress', 'In Progress'),
        ('not_applicable', 'Not Applicable')
    ], string='Compliance Status', default='in_progress')

    compliance_percentage = fields.Float('Compliance %', default=0.0)

    # Dates
    assessment_date = fields.Date('Last Assessment Date')
    due_date = fields.Date('Next Assessment Due')
    certification_date = fields.Date('Certification Date')
    expiry_date = fields.Date('Certification Expiry')

    # Requirements
    total_requirements = fields.Integer('Total Requirements')
    met_requirements = fields.Integer('Met Requirements')
    pending_requirements = fields.Integer('Pending Requirements', compute='_compute_pending')

    # Risk and Impact
    non_compliance_risk = fields.Selection([
        ('low', 'Low Risk'),
        ('medium', 'Medium Risk'),
        ('high', 'High Risk'),
        ('critical', 'Critical Risk')
    ], string='Non-Compliance Risk', default='medium')

    financial_penalty = fields.Monetary('Potential Financial Penalty', currency_field='currency_id')
    reputation_impact = fields.Selection([
        ('minimal', 'Minimal'),
        ('low', 'Low'),
        ('moderate', 'Moderate'),
        ('high', 'High'),
        ('severe', 'Severe')
    ], string='Reputation Impact')

    # Audit Trail
    last_audit_id = fields.Many2one('bcm.audit', 'Last Audit')
    audit_findings = fields.Text('Audit Findings')
    corrective_actions = fields.Text('Corrective Actions')

    # Documentation
    evidence_documents = fields.Integer('Evidence Documents')
    policy_documents = fields.Integer('Policy Documents')
    documentation_complete = fields.Boolean('Documentation Complete')

    # Compliance Score
    compliance_score = fields.Float('Compliance Score', compute='_compute_compliance_score')

    # Currency
    currency_id = fields.Many2one('res.currency', 'Currency',
                                  default=lambda self: self.env.company.currency_id)
    company_id = fields.Many2one('res.company', 'Company',
                                 default=lambda self: self.env.company)

    @api.depends('total_requirements', 'met_requirements')
    def _compute_pending(self):
        for record in self:
            record.pending_requirements = record.total_requirements - record.met_requirements

    @api.depends('compliance_status', 'compliance_percentage', 'documentation_complete')
    def _compute_compliance_score(self):
        for record in self:
            score = 0.0

            # Status factor (40%)
            status_scores = {
                'compliant': 40,
                'partial': 25,
                'in_progress': 15,
                'non_compliant': 0,
                'not_applicable': 40
            }
            score += status_scores.get(record.compliance_status, 0)

            # Percentage factor (40%)
            score += (record.compliance_percentage / 100) * 40

            # Documentation factor (20%)
            if record.documentation_complete:
                score += 20
            elif record.evidence_documents > 0:
                score += 10

            record.compliance_score = min(score, 100)

    def action_perform_assessment(self):
        """Perform compliance assessment"""
        self.ensure_one()

        # Calculate compliance percentage
        if self.total_requirements > 0:
            self.compliance_percentage = (self.met_requirements / self.total_requirements) * 100

            # Update status based on percentage
            if self.compliance_percentage >= 100:
                self.compliance_status = 'compliant'
            elif self.compliance_percentage >= 70:
                self.compliance_status = 'partial'
            elif self.compliance_percentage > 0:
                self.compliance_status = 'in_progress'
            else:
                self.compliance_status = 'non_compliant'

        self.assessment_date = fields.Date.today()

        # Set next due date (6 months)
        self.due_date = fields.Date.today() + timedelta(days=180)

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Assessment Complete',
                'message': f'Compliance assessment completed: {self.compliance_percentage:.1f}% compliant',
                'type': 'success',
            }
        }

    def action_generate_compliance_report(self):
        """Generate compliance report"""
        self.ensure_one()

        report_text = f"""
        Compliance Report for {self.name}
        =====================================
        Standard: {self.standard}
        Type: {self.compliance_type}
        Status: {self.compliance_status}

        Compliance Metrics:
        - Overall Compliance: {self.compliance_percentage:.1f}%
        - Requirements Met: {self.met_requirements}/{self.total_requirements}
        - Pending Items: {self.pending_requirements}

        Risk Assessment:
        - Non-Compliance Risk: {self.non_compliance_risk}
        - Potential Financial Impact: {self.financial_penalty:,.2f} {self.currency_id.symbol}
        - Reputation Impact: {self.reputation_impact}

        Documentation:
        - Evidence Documents: {self.evidence_documents}
        - Policy Documents: {self.policy_documents}
        - Documentation Complete: {"Yes" if self.documentation_complete else "No"}

        Compliance Score: {self.compliance_score:.1f}/100

        Next Assessment Due: {self.due_date}
        """

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Report Generated',
                'message': 'Compliance report has been generated',
                'type': 'info',
                'sticky': True,
            }
        }

    def action_create_corrective_action(self):
        """Create corrective action plan"""
        self.ensure_one()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Corrective Action',
                'message': 'Creating corrective action plan',
                'type': 'warning',
            }
        }