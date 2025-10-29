# -*- coding: utf-8 -*-
"""
BCM Governance Extension - ISO 22301 Compliance Engine
======================================================

Расширение существующего bcm_governance модуля для полной поддержки ISO 22301:2019
с интеграцией в frontend Compliance Dashboard
"""

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import json
import logging

_logger = logging.getLogger(__name__)

class ISO22301ComplianceFramework(models.Model):
    """ISO 22301:2019 Compliance Framework - Core engine"""
    _name = 'bcm.iso22301.framework'
    _description = 'ISO 22301:2019 Compliance Framework'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'clause_number'

    # ISO 22301 Structure
    clause_number = fields.Char('Clause Number', required=True, index=True)
    clause_title = fields.Char('Clause Title', required=True, tracking=True)
    clause_description = fields.Html('Clause Description')
    clause_category = fields.Selection([
        ('context', '4. Context of the Organization'),
        ('leadership', '5. Leadership'),
        ('planning', '6. Planning'),
        ('support', '7. Support'),
        ('operation', '8. Operation'),
        ('evaluation', '9. Performance Evaluation'),
        ('improvement', '10. Improvement')
    ], string='ISO Category', required=True, index=True)

    # Compliance Assessment
    compliance_status = fields.Selection([
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('implemented', 'Implemented'),
        ('verified', 'Verified'),
        ('non_compliant', 'Non-Compliant')
    ], string='Compliance Status', default='not_started', tracking=True)

    compliance_percentage = fields.Float('Compliance %', compute='_compute_compliance_percentage', store=True)
    risk_level = fields.Selection([
        ('low', 'Low Risk'),
        ('medium', 'Medium Risk'),
        ('high', 'High Risk'),
        ('critical', 'Critical Risk')
    ], string='Risk Level', default='medium', tracking=True)

    # AI Assessment
    ai_compliance_score = fields.Float('AI Compliance Score', readonly=True)
    ai_assessment_notes = fields.Html('AI Assessment Notes', readonly=True)
    ai_recommendations = fields.Html('AI Recommendations', readonly=True)
    ai_last_assessment = fields.Datetime('Last AI Assessment', readonly=True)

    # Implementation Tracking
    implementation_plan = fields.Html('Implementation Plan')
    responsible_user_id = fields.Many2one('res.users', string='Responsible Person')
    target_completion_date = fields.Date('Target Completion Date')
    actual_completion_date = fields.Date('Actual Completion Date')

    # Evidence Management
    evidence_documents = fields.Many2many('ir.attachment', string='Evidence Documents')
    evidence_notes = fields.Text('Evidence Notes')

    # Related BCM Modules
    related_bcm_modules = fields.Many2many(
        'bcm.module.mapping', 
        string='Related BCM Modules',
        help='BCM modules that support this ISO requirement'
    )

    # Gap Analysis
    identified_gaps = fields.Html('Identified Gaps')
    gap_action_plan = fields.Html('Gap Action Plan')
    gap_priority = fields.Selection([
        ('low', 'Low Priority'),
        ('medium', 'Medium Priority'),
        ('high', 'High Priority'),
        ('urgent', 'Urgent')
    ], string='Gap Priority', default='medium')

    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    active = fields.Boolean(default=True)

    @api.depends('compliance_status', 'ai_compliance_score')
    def _compute_compliance_percentage(self):
        """Calculate compliance percentage based on status and AI score"""
        for record in self:
            status_scores = {
                'not_started': 0,
                'in_progress': 30,
                'implemented': 80,
                'verified': 95,
                'non_compliant': 10
            }
            
            base_score = status_scores.get(record.compliance_status, 0)
            ai_factor = (record.ai_compliance_score or 0) / 100
            
            # Weighted calculation: 70% status, 30% AI assessment
            record.compliance_percentage = (base_score * 0.7) + (ai_factor * 100 * 0.3)

    def action_ai_compliance_assessment(self):
        """AI-powered compliance assessment using existing Governance Brain"""
        self.ensure_one()

        # Use existing AI Governance Brain for assessment
        governance_brain = self.env['bcm.governance.brain'].create({
            'name': f'ISO 22301 Assessment: {self.clause_number} {self.clause_title}',
            'description': f"""
            Assess compliance with ISO 22301:2019 requirement:
            
            Clause: {self.clause_number}
            Title: {self.clause_title}
            Description: {self.clause_description}
            
            Current Status: {self.compliance_status}
            Risk Level: {self.risk_level}
            
            Related BCM Modules: {', '.join([m.name for m in self.related_bcm_modules])}
            """,
            'governance_domain': 'iso_22301',
            'priority': 'high' if self.risk_level in ['high', 'critical'] else 'medium'
        })

        # Trigger AI analysis
        governance_brain.action_anthropic_analysis()

        # Extract compliance-specific insights
        ai_insights = self._extract_compliance_insights(governance_brain.ai_analysis)

        self.write({
            'ai_compliance_score': ai_insights.get('score', 0),
            'ai_assessment_notes': ai_insights.get('assessment', ''),
            'ai_recommendations': ai_insights.get('recommendations', ''),
            'ai_last_assessment': fields.Datetime.now(),
            'identified_gaps': ai_insights.get('gaps', ''),
            'gap_action_plan': ai_insights.get('action_plan', '')
        })

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('AI Compliance Assessment Complete'),
                'message': f'ISO 22301 clause {self.clause_number} assessed with {self.ai_compliance_score}% compliance',
                'type': 'success',
            }
        }

    def _extract_compliance_insights(self, ai_analysis):
        """Extract structured compliance insights from AI analysis"""
        if not ai_analysis:
            return {}

        # Parse AI analysis for specific compliance elements
        analysis_text = ai_analysis.lower()
        
        # Score extraction logic
        score = 50  # Default
        if 'fully compliant' in analysis_text or '100%' in analysis_text:
            score = 95
        elif 'largely compliant' in analysis_text or 'mostly' in analysis_text:
            score = 80
        elif 'partially compliant' in analysis_text:
            score = 60
        elif 'minimal compliance' in analysis_text:
            score = 30
        elif 'non-compliant' in analysis_text:
            score = 10

        return {
            'score': score,
            'assessment': ai_analysis,
            'recommendations': self._extract_recommendations(ai_analysis),
            'gaps': self._extract_gaps(ai_analysis),
            'action_plan': self._extract_action_plan(ai_analysis)
        }

class BCMModuleMapping(models.Model):
    """Mapping between BCM Modules and ISO 22301 Requirements"""
    _name = 'bcm.module.mapping'
    _description = 'BCM Module to ISO Mapping'

    name = fields.Char('Module Name', required=True)
    technical_name = fields.Char('Technical Name', required=True, 
                                help='Technical name like bcm_risk_management')
    module_description = fields.Text('Module Description')
    
    # Development Status
    development_status = fields.Selection([
        ('planning', 'Planning'),
        ('development', 'In Development'),
        ('active', 'Active'),
        ('maintenance', 'Maintenance'),
        ('deprecated', 'Deprecated')
    ], string='Development Status', default='planning')

    # Compliance Contribution
    iso_clauses = fields.Many2many('bcm.iso22301.framework', string='Supported ISO Clauses')
    compliance_contribution = fields.Float('Compliance Contribution %', 
                                         help='How much this module contributes to overall compliance')

    # Module Health
    health_status = fields.Selection([
        ('healthy', 'Healthy'),
        ('warning', 'Warning'),
        ('critical', 'Critical'),
        ('offline', 'Offline')
    ], string='Health Status', default='healthy', compute='_compute_health_status', store=True)

    last_health_check = fields.Datetime('Last Health Check')
    health_metrics = fields.Text('Health Metrics JSON')

    @api.depends('development_status', 'compliance_contribution')
    def _compute_health_status(self):
        """Compute module health based on various factors"""
        for record in self:
            if record.development_status == 'active' and record.compliance_contribution >= 80:
                record.health_status = 'healthy'
            elif record.development_status == 'development' or record.compliance_contribution >= 50:
                record.health_status = 'warning' 
            elif record.development_status == 'deprecated' or record.compliance_contribution < 30:
                record.health_status = 'critical'
            else:
                record.health_status = 'offline'

class ComplianceDashboardAPI(models.Model):
    """API Model for Frontend Compliance Dashboard"""
    _name = 'bcm.compliance.dashboard'
    _description = 'Compliance Dashboard API'

    @api.model
    def get_compliance_overview(self):
        """Get compliance overview for frontend dashboard"""
        
        # Get all ISO requirements
        iso_requirements = self.env['bcm.iso22301.framework'].search([])
        
        # Calculate overall metrics
        total_requirements = len(iso_requirements)
        implemented = len(iso_requirements.filtered(lambda r: r.compliance_status == 'implemented'))
        verified = len(iso_requirements.filtered(lambda r: r.compliance_status == 'verified'))
        
        overall_compliance = sum(iso_requirements.mapped('compliance_percentage')) / total_requirements if total_requirements else 0
        
        # Critical gaps
        critical_gaps = iso_requirements.filtered(lambda r: r.risk_level == 'critical' and r.compliance_status in ['not_started', 'non_compliant'])
        
        # Module health
        bcm_modules = self.env['bcm.module.mapping'].search([])
        healthy_modules = len(bcm_modules.filtered(lambda m: m.health_status == 'healthy'))
        warning_modules = len(bcm_modules.filtered(lambda m: m.health_status == 'warning'))
        critical_modules = len(bcm_modules.filtered(lambda m: m.health_status == 'critical'))

        return {
            'overall_compliance': round(overall_compliance, 1),
            'total_requirements': total_requirements,
            'implemented_requirements': implemented + verified,
            'critical_gaps': len(critical_gaps),
            'total_modules': len(bcm_modules),
            'healthy_modules': healthy_modules,
            'warning_modules': warning_modules,
            'critical_modules': critical_modules,
            'critical_gaps_list': [{
                'id': gap.id,
                'clause': gap.clause_number,
                'title': gap.clause_title,
                'risk_level': gap.risk_level,
                'category': gap.clause_category
            } for gap in critical_gaps[:5]]  # Top 5 critical gaps
        }

    @api.model
    def get_module_compliance_matrix(self):
        """Get module compliance matrix for dashboard"""
        
        bcm_modules = self.env['bcm.module.mapping'].search([])
        
        module_data = []
        for module in bcm_modules:
            # Calculate module compliance score based on related ISO clauses
            related_clauses = module.iso_clauses
            avg_compliance = sum(related_clauses.mapped('compliance_percentage')) / len(related_clauses) if related_clauses else 0
            
            module_data.append({
                'name': module.name,
                'technical_name': module.technical_name,
                'compliance_score': round(avg_compliance, 1),
                'health_status': module.health_status,
                'development_status': module.development_status,
                'supported_clauses': len(related_clauses),
                'contribution': module.compliance_contribution
            })

        return module_data

    @api.model
    def get_compliance_roadmap(self):
        """Get implementation roadmap for dashboard"""
        
        iso_requirements = self.env['bcm.iso22301.framework'].search([])
        
        # Group by categories for roadmap phases
        roadmap_phases = []
        
        for category_key, category_name in [
            ('leadership', '5. Leadership'), 
            ('planning', '6. Planning'),
            ('operation', '8. Operation'),
            ('evaluation', '9. Performance Evaluation')
        ]:
            category_requirements = iso_requirements.filtered(lambda r: r.clause_category == category_key)
            
            if category_requirements:
                avg_compliance = sum(category_requirements.mapped('compliance_percentage')) / len(category_requirements)
                
                roadmap_phases.append({
                    'phase': category_name,
                    'requirements_count': len(category_requirements),
                    'compliance_percentage': round(avg_compliance, 1),
                    'status': 'completed' if avg_compliance >= 80 else 'in_progress' if avg_compliance >= 30 else 'planning'
                })

        return roadmap_phases

    @api.model
    def trigger_full_ai_assessment(self):
        """Trigger AI assessment for all ISO requirements"""
        
        iso_requirements = self.env['bcm.iso22301.framework'].search([
            ('compliance_status', 'in', ['not_started', 'in_progress'])
        ])

        results = []
        for req in iso_requirements[:10]:  # Limit to 10 for performance
            try:
                req.action_ai_compliance_assessment()
                results.append({
                    'clause': req.clause_number,
                    'status': 'success',
                    'score': req.ai_compliance_score
                })
            except Exception as e:
                results.append({
                    'clause': req.clause_number,
                    'status': 'error',
                    'error': str(e)
                })

        return {
            'total_assessed': len(results),
            'successful': len([r for r in results if r['status'] == 'success']),
            'errors': len([r for r in results if r['status'] == 'error']),
            'results': results
        }
