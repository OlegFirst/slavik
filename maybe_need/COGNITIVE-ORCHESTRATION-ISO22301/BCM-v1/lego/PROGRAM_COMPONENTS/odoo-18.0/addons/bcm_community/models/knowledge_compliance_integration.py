# -*- coding: utf-8 -*-
"""
BCM Community - ISO 22301 Knowledge Integration
=============================================

Интеграция knowledge базы с compliance данными из bcm_governance
"""

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class BCMKnowledgeArticle(models.Model):
    """Расширение Knowledge Article для интеграции с ISO 22301 compliance"""
    _inherit = 'bcm.knowledge.article'

    # ISO 22301 Compliance Integration
    iso_compliance_level = fields.Selection([
        ('gap_critical', 'Critical Gap (0-20%)'),
        ('gap_major', 'Major Gap (20-50%)'),
        ('gap_minor', 'Minor Gap (50-80%)'),
        ('compliant', 'Compliant (80%+)')
    ], string='ISO Compliance Level', compute='_compute_compliance_level', store=True)

    related_bcm_modules = fields.Many2many(
        'bcm.module.mapping',
        string='Related BCM Modules',
        help='BCM modules this knowledge article supports'
    )

    compliance_contribution = fields.Float(
        'Compliance Contribution %',
        help='How much this article contributes to overall compliance'
    )

    # Knowledge Types for ISO 22301
    knowledge_type = fields.Selection([
        ('policy_template', 'Policy Template'),
        ('procedure_guide', 'Procedure Guide'),
        ('assessment_method', 'Assessment Methodology'),
        ('training_material', 'Training Material'),
        ('audit_checklist', 'Audit Checklist'),
        ('gap_remedy', 'Gap Remediation Guide'),
        ('best_practice', 'Best Practice'),
        ('case_study', 'Implementation Case Study'),
        ('tool_template', 'Tool/Template'),
        ('regulation_guide', 'Regulatory Guidance')
    ], string='Knowledge Type', default='best_practice')

    # Auto-generation from gaps
    auto_generated_for_gap = fields.Char('Generated for Gap', help='ISO clause this article addresses')
    gap_severity = fields.Selection([
        ('low', 'Low Impact'),
        ('medium', 'Medium Impact'), 
        ('high', 'High Impact'),
        ('critical', 'Critical Impact')
    ], string='Gap Severity')

    @api.depends('iso_clauses', 'related_bcm_modules')
    def _compute_compliance_level(self):
        """Compute compliance level based on related ISO clauses and modules"""
        for article in self:
            if not article.iso_clauses:
                article.iso_compliance_level = False
                continue
                
            # Получаем данные соответствия из bcm_governance
            try:
                compliance_api = self.env['bcm.compliance.dashboard']
                module_data = compliance_api.get_module_compliance_matrix()
                
                # Находим средний compliance связанных модулей
                related_modules = article.related_bcm_modules.mapped('technical_name')
                relevant_modules = [m for m in module_data if m['technical_name'] in related_modules]
                
                if relevant_modules:
                    avg_compliance = sum(m['compliance_score'] for m in relevant_modules) / len(relevant_modules)
                    
                    if avg_compliance >= 80:
                        article.iso_compliance_level = 'compliant'
                    elif avg_compliance >= 50:
                        article.iso_compliance_level = 'gap_minor'
                    elif avg_compliance >= 20:
                        article.iso_compliance_level = 'gap_major'
                    else:
                        article.iso_compliance_level = 'gap_critical'
                else:
                    article.iso_compliance_level = 'gap_major'
                    
            except Exception as e:
                _logger.warning(f'Could not compute compliance level for article {article.id}: {e}')
                article.iso_compliance_level = False

    @api.model
    def auto_generate_gap_articles(self):
        """Автоматически создаём knowledge статьи для критических пробелов"""
        try:
            # Получаем данные о критических пробелах
            compliance_api = self.env['bcm.compliance.dashboard']
            overview = compliance_api.get_compliance_overview()
            
            critical_gaps = overview.get('critical_gaps_list', [])
            
            generated_articles = []
            
            for gap in critical_gaps:
                # Проверяем, есть ли уже статья для этого пробела
                existing = self.search([
                    ('auto_generated_for_gap', '=', gap['clause']),
                    ('knowledge_type', '=', 'gap_remedy')
                ])
                
                if existing:
                    continue
                
                # Генерируем статью для пробела
                article_data = {
                    'name': f"How to Address ISO 22301 Gap: {gap['title']} ({gap['clause']})",
                    'knowledge_type': 'gap_remedy',
                    'auto_generated_for_gap': gap['clause'],
                    'gap_severity': 'critical' if gap['compliance'] <= 15 else 'high',
                    'category': 'compliance',
                    'article_type': 'ai_generated',
                    'summary': f"Remediation guide for ISO 22301 clause {gap['clause']} - {gap['title']}",
                    'content': self._generate_gap_remedy_content(gap),
                    'is_published': False  # Draft for review
                }
                
                # Создаём связи с ISO clauses если они существуют
                iso_clause = self.env['bcm.iso.clause'].search([('name', '=', gap['clause'])], limit=1)
                if iso_clause:
                    article_data['iso_clauses'] = [(6, 0, [iso_clause.id])]
                
                article = self.create(article_data)
                generated_articles.append(article)
                
                _logger.info(f"Generated gap remedy article for {gap['clause']}: {article.name}")
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Gap Articles Generated'),
                    'message': f'Created {len(generated_articles)} knowledge articles for critical gaps',
                    'type': 'success',
                }
            }
            
        except Exception as e:
            _logger.error(f'Failed to auto-generate gap articles: {e}')
            raise UserError(f'Failed to generate gap articles: {str(e)}')

    def _generate_gap_remedy_content(self, gap):
        """Generate content for gap remediation article"""
        
        # Шаблон контента на основе типа пробела
        gap_templates = {
            '8.4': self._template_exercises_testing(),
            '8.2': self._template_bc_plans(),
            '5.1': self._template_leadership(),
            '7.2': self._template_training(),
            '9.2': self._template_internal_audit(),
            '10.2': self._template_improvement()
        }
        
        template = gap_templates.get(gap['clause'], self._template_generic_gap())
        
        return template.format(
            clause=gap['clause'],
            title=gap['title'],
            compliance=gap['compliance']
        )

    def _template_exercises_testing(self):
        return """
<div class="gap-remedy-article">
    <h2>🎯 Addressing Gap: Exercises & Testing ({clause})</h2>
    
    <div class="alert alert-danger">
        <strong>Current Status:</strong> {compliance}% compliance - Critical Gap
    </div>

    <h3>📋 What ISO 22301 Requires</h3>
    <p>ISO 22301 clause {clause} requires organizations to conduct regular exercises to validate business continuity plans and capabilities.</p>

    <h3>🚨 Why This Gap is Critical</h3>
    <ul>
        <li>Untested plans often fail during real incidents</li>
        <li>Teams lack practical experience with BC procedures</li>
        <li>Assumptions about recovery times prove incorrect</li>
        <li>Communication channels haven't been validated</li>
    </ul>

    <h3>✅ Remediation Steps</h3>
    <ol>
        <li><strong>Exercise Program Setup:</strong>
            <ul>
                <li>Develop annual exercise calendar</li>
                <li>Define exercise types (tabletop, walkthrough, full-scale)</li>
                <li>Assign exercise coordinators</li>
            </ul>
        </li>
        <li><strong>Start with Tabletop Exercises:</strong>
            <ul>
                <li>Use BCM Exercise module scenarios</li>
                <li>Involve key personnel</li>
                <li>Document lessons learned</li>
            </ul>
        </li>
        <li><strong>Progress to Functional Tests:</strong>
            <ul>
                <li>Test specific BC plan elements</li>
                <li>Validate recovery time objectives</li>
                <li>Test backup systems and processes</li>
            </ul>
        </li>
        <li><strong>Document and Improve:</strong>
            <ul>
                <li>Record exercise results in BCM Exercise module</li>
                <li>Update plans based on findings</li>
                <li>Share knowledge articles from exercises</li>
            </ul>
        </li>
    </ol>

    <h3>🛠 Using BCM Platform Tools</h3>
    <p><strong>BCM Exercise Module:</strong> Use the exercise scenarios and templates to conduct structured tests</p>
    <p><strong>BCM Scenario Hub:</strong> Access pre-built exercise scenarios for various threat types</p>
    <p><strong>BCM Training Module:</strong> Ensure participants are prepared for exercises</p>

    <h3>📊 Success Metrics</h3>
    <ul>
        <li>Conduct at least 2 exercises per year</li>
        <li>Test all critical business processes annually</li>
        <li>Achieve 80%+ participant satisfaction scores</li>
        <li>Complete action items within 30 days</li>
    </ul>

    <h3>📚 Related Resources</h3>
    <p>See also: Exercise Planning Templates, Scenario Library, Training Materials</p>
</div>
"""

    def _template_bc_plans(self):
        return """
<div class="gap-remedy-article">
    <h2>📋 Addressing Gap: Business Continuity Plans ({clause})</h2>
    
    <div class="alert alert-danger">
        <strong>Current Status:</strong> {compliance}% compliance - Critical Gap
    </div>

    <h3>📋 What ISO 22301 Requires</h3>
    <p>Clause {clause} requires documented business continuity strategies and solutions based on BIA results.</p>

    <h3>🚨 Impact of This Gap</h3>
    <ul>
        <li>No clear recovery procedures during incidents</li>
        <li>Inconsistent response across departments</li>
        <li>Extended downtime and revenue loss</li>
        <li>Regulatory compliance failures</li>
    </ul>

    <h3>✅ Step-by-Step Remediation</h3>
    <ol>
        <li><strong>Leverage BIA Results:</strong> Use existing BCM BIA module data to identify critical processes</li>
        <li><strong>Develop Recovery Strategies:</strong> Create specific recovery procedures for each critical process</li>
        <li><strong>Document Plans:</strong> Use BCM Plans module templates to create structured plans</li>
        <li><strong>Define Roles:</strong> Assign clear responsibilities and authorities</li>
        <li><strong>Resource Planning:</strong> Identify required resources for recovery</li>
        <li><strong>Communication Plans:</strong> Define internal/external communication procedures</li>
    </ol>

    <h3>🛠 BCM Platform Integration</h3>
    <p><strong>BCM BIA Module:</strong> Export BIA results to inform plan development</p>
    <p><strong>BCM Plans Module:</strong> Use plan templates and version control</p>
    <p><strong>BCM Templates:</strong> Access industry-standard plan formats</p>

    <p><em>Priority: Start with your top 3 critical processes identified in BIA</em></p>
</div>
"""

    def _template_generic_gap(self):
        return """
<div class="gap-remedy-article">
    <h2>Addressing ISO 22301 Gap: {title} ({clause})</h2>
    
    <div class="alert alert-warning">
        <strong>Current Compliance:</strong> {compliance}%
    </div>

    <h3>Gap Analysis</h3>
    <p>This article provides guidance for addressing gaps in ISO 22301 clause {clause} - {title}.</p>

    <h3>Recommended Actions</h3>
    <ol>
        <li>Review ISO 22301 requirements for this clause</li>
        <li>Assess current implementation status</li>
        <li>Develop improvement plan</li>
        <li>Implement changes</li>
        <li>Document evidence</li>
        <li>Monitor progress</li>
    </ol>

    <p><em>This article was auto-generated. Please review and enhance with specific guidance.</em></p>
</div>
"""

class BCMComplianceKnowledgeLink(models.Model):
    """Связь между compliance gaps и knowledge articles"""
    _name = 'bcm.compliance.knowledge.link'
    _description = 'Compliance Gap to Knowledge Article Link'

    iso_clause = fields.Char('ISO Clause', required=True)
    knowledge_article_id = fields.Many2one('bcm.knowledge.article', 'Knowledge Article', required=True)
    gap_severity = fields.Selection([
        ('critical', 'Critical'),
        ('major', 'Major'),
        ('minor', 'Minor')
    ], string='Gap Severity')
    
    effectiveness_score = fields.Float('Effectiveness Score', help='How effective this article is for addressing the gap')
    usage_count = fields.Integer('Usage Count', default=0)
    
    def action_mark_as_used(self):
        """Mark this knowledge article as used for gap remediation"""
        self.usage_count += 1
        self.knowledge_article_id.view_count += 1