# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import json
import logging

_logger = logging.getLogger(__name__)

class BCMComplianceGuardian(models.Model):
    """AI Compliance Guardian - Automated Compliance Intelligence"""
    _name = 'bcm.compliance.guardian'
    _description = 'AI Compliance Guardian - Automated Audit Intelligence'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Compliance Monitoring Topic', required=True)

    # Guardian Configuration
    guardian_mode = fields.Selection([
        ('vigilant', '👁️ Vigilant - Continuous Monitoring'),
        ('investigative', '🔍 Investigative - Deep Analysis'),
        ('preventive', '🛡️ Preventive - Risk Prevention'),
        ('corrective', '🔧 Corrective - Issue Resolution')
    ], string='Guardian Mode', default='vigilant')

    # Compliance Intelligence
    ai_compliance_status = fields.Html('AI Compliance Assessment', readonly=True)
    compliance_confidence = fields.Float('Assessment Confidence', readonly=True)
    gap_analysis = fields.Html('AI Gap Analysis', readonly=True)
    remediation_plan = fields.Html('AI Remediation Plan', readonly=True)

    # Automated Monitoring
    auto_monitoring = fields.Boolean('Automated Monitoring', default=True)
    monitoring_frequency = fields.Selection([
        ('hourly', 'Hourly Checks'),
        ('daily', 'Daily Monitoring'),
        ('weekly', 'Weekly Reviews'),
        ('monthly', 'Monthly Assessments')
    ], default='daily')

    # Compliance Memory
    compliance_patterns = fields.Text('Compliance Patterns Learned')
    audit_wisdom = fields.Text('Audit Wisdom Accumulated')
    remediation_effectiveness = fields.Text('Remediation Effectiveness Data')

    # Performance Metrics
    audits_automated = fields.Integer('Audits Automated', default=0)
    gaps_identified = fields.Integer('Gaps Identified', default=0)
    remediation_success_rate = fields.Float('Remediation Success Rate')

    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    def action_ai_compliance_scan(self):
        """AI-powered compliance scanning"""
        try:
            compliance_prompt = f"""
AI COMPLIANCE GUARDIAN SCAN

COMPLIANCE MONITORING REQUEST:
Topic: {self.name}
Guardian Mode: {self.guardian_mode}
Organization: {self.company_id.name}
Monitoring Level: {self.monitoring_frequency}

GUARDIAN SCAN REQUIRED:

1. ISO 22301 COMPLIANCE HEALTH:
   - Current compliance status assessment
   - Critical gaps identification
   - Risk exposure analysis
   - Compliance trend evaluation

2. AUTOMATED EVIDENCE REVIEW:
   - Documentation completeness
   - Process adherence verification
   - Record keeping assessment
   - Audit trail validation

3. PREVENTIVE ANALYSIS:
   - Emerging compliance risks
   - Potential gap prediction
   - Proactive remediation needs
   - Prevention opportunities

4. REMEDIATION INTELLIGENCE:
   - Gap remediation priorities
   - Resource allocation recommendations
   - Timeline optimization
   - Success probability assessment

5. COMPLIANCE FORECAST:
   - Future compliance outlook
   - Risk trend predictions
   - Regulatory change impacts
   - Continuous improvement opportunities

Provide AUTOMATED COMPLIANCE INTELLIGENCE with actionable recommendations.
"""

            # Call Compliance Checker service for automated analysis
            result = self._call_compliance_guardian_ai(compliance_prompt)

            if result:
                self.write({
                    'ai_compliance_status': result.get('compliance_html', ''),
                    'compliance_confidence': result.get('confidence', 0.0),
                    'gap_analysis': result.get('gap_analysis', ''),
                    'remediation_plan': result.get('remediation_plan', ''),
                    'audits_automated': self.audits_automated + 1
                })

                # Store compliance intelligence
                self._store_compliance_intelligence(result)

                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Compliance Scan Complete'),
                        'message': f'Automated compliance scan completed',
                        'type': 'success',
                    }
                }

        except Exception as e:
            raise UserError(f'Compliance scan failed: {str(e)}')

    def action_automated_audit_preparation(self):
        """Automated audit preparation via AI"""
        try:
            audit_prep_prompt = f"""
AI COMPLIANCE GUARDIAN - AUDIT PREPARATION

AUDIT PREPARATION REQUEST:
Organization: {self.company_id.name}
Compliance Status: Current assessment required
Guardian Mode: {self.guardian_mode}

AUDIT PREPARATION INTELLIGENCE:

1. AUDIT READINESS ASSESSMENT:
   - Documentation completeness check
   - Process maturity evaluation
   - Evidence availability verification
   - Gap remediation status

2. AUTOMATED EVIDENCE COLLECTION:
   - Critical evidence identification
   - Documentation gaps flagging
   - Record completeness verification
   - Audit trail preparation

3. RISK ASSESSMENT:
   - Audit risk areas identification
   - Potential findings prediction
   - Remediation priority ranking
   - Resource allocation needs

4. PREPARATION PLAN:
   - Pre-audit action items
   - Evidence organization strategy
   - Stakeholder preparation needs
   - Timeline optimization

Provide AUTOMATED AUDIT PREPARATION with comprehensive readiness assessment.
"""

            result = self._call_compliance_checker(audit_prep_prompt)

            if result:
                # Create automated audit preparation record
                audit_prep = self.env['bcm.audit.preparation'].create({
                    'name': f'Automated Audit Prep - {self.name}',
                    'ai_readiness_assessment': result.get('readiness_html', ''),
                    'evidence_checklist': result.get('evidence_list', ''),
                    'preparation_plan': result.get('preparation_plan', ''),
                    'guardian_id': self.id
                })

                return {
                    'type': 'ir.actions.act_window',
                    'name': _('Automated Audit Preparation'),
                    'res_model': 'bcm.audit.preparation',
                    'res_id': audit_prep.id,
                    'view_mode': 'form',
                    'target': 'new'
                }

        except Exception as e:
            raise UserError(f'Automated audit preparation failed: {str(e)}')

    def _call_compliance_guardian_ai(self, prompt):
        """Call Compliance Checker for automated analysis"""
        try:
            import requests

            response = requests.post(
                'http://compliance_checker:8084/api/compliance/analyze',
                json={
                    'analysis_request': prompt,
                    'organization': self.company_id.name,
                    'framework': 'iso_22301',
                    'guardian_mode': self.guardian_mode
                },
                timeout=45
            )

            return response.json() if response.status_code == 200 else None

        except Exception as e:
            _logger.error(f'Compliance Guardian AI call failed: {e}')
            return None