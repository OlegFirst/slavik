# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)

class BcmScenarioReview(models.Model):
    _name = 'bcm.scenario.review'
    _description = 'BCM Scenario Review (Moderation)'
    _order = 'created_at desc'
    _rec_name = 'scenario_id'
    
    # Основные поля согласно ТЗ
    scenario_id = fields.Many2one(
        'bcm.scenario',
        string='Scenario',
        required=True, index=True,
        ondelete='cascade'
    )
    
    reviewer_id = fields.Many2one(
        'res.users',
        string='Reviewer',
        required=True, index=True,
        default=lambda self: self.env.user
    )
    
    decision = fields.Selection([
        ('approve', 'Approve'),
        ('reject', 'Reject'),
        ('request_changes', 'Request Changes')
    ], string='Decision', required=True)
    
    notes = fields.Text(
        string='Review Notes',
        required=True, index=True,
        help='Detailed review notes and feedback'
    )
    
    created_at = fields.Datetime(
        string='Review Date',
        default=fields.Datetime.now,
        readonly=True
    )
    
    # Multi-tenancy
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        index=True,
        default=lambda self: self.env.company
    )
    
    # Дополнительные поля для детальной оценки
    content_quality = fields.Selection([
        ('1', 'Poor'),
        ('2', 'Fair'), 
        ('3', 'Good'),
        ('4', 'Very Good'),
        ('5', 'Excellent')
    ], string='Content Quality')
    
    technical_accuracy = fields.Selection([
        ('1', 'Poor'),
        ('2', 'Fair'),
        ('3', 'Good'), 
        ('4', 'Very Good'),
        ('5', 'Excellent')
    ], string='Technical Accuracy')
    
    compliance_iso22301 = fields.Selection([
        ('1', 'Not Compliant'),
        ('2', 'Partially Compliant'),
        ('3', 'Mostly Compliant'),
        ('4', 'Fully Compliant'),
        ('5', 'Exceeds Standards')
    ], string='ISO 22301 Compliance')
    
    # Проверки безопасности и лицензий
    has_pii_phi = fields.Boolean(
        string='Contains PII/PHI',
        help='Scenario contains Personal/Protected Health Information'
    )
    
    license_appropriate = fields.Boolean(
        string='License Appropriate',
        default=True,
        help='License terms are appropriate for content'
    )
    
    # Рекомендации по улучшению
    improvement_suggestions = fields.Text(
        string='Improvement Suggestions',
        help='Specific suggestions for improving the scenario'
    )
    
    # Связанные поля
    scenario_title = fields.Char(
        related='scenario_id.title',
        string='Scenario Title',
        readonly=True
    )
    
    scenario_author = fields.Char(
        related='scenario_id.author_org',
        string='Author Organization', 
        readonly=True
    )
    
    scenario_category = fields.Selection(
        related='scenario_id.category',
        string='Category',
        readonly=True
    )
    
    reviewer_name = fields.Char(
        related='reviewer_id.name',
        string='Reviewer Name',
        readonly=True
    )
    
    # Статус обработки
    is_processed = fields.Boolean(
        string='Review Processed',
        default=False,
        help='Whether this review has been processed and scenario status updated'
    )
    
    # Конфиденциальность рецензии
    internal_notes = fields.Text(
        string='Internal Notes',
        help='Internal notes not visible to scenario author'
    )
    
    @api.model
    def create(self, vals):
        """Создание рецензии с автоматической обработкой"""
        review = super().create(vals)
        
        # Автоматически обработать решение
        review._process_review_decision()
        
        return review
    
    def _process_review_decision(self):
        """Обработать решение рецензии"""
        self.ensure_one()
        
        if self.is_processed:
            return
        
        scenario = self.scenario_id
        
        if self.decision == 'approve':
            if scenario.status == 'pending_review':
                scenario.status = 'published'
                scenario.message_post(
                    body=_('Scenario approved by reviewer: %s') % self.reviewer_id.name,
                    message_type='notification'
                )
                
        elif self.decision == 'reject':
            if scenario.status == 'pending_review':
                scenario.write({
                    'status': 'rejected',
                    'rejection_reason': self.notes
                })
                scenario.message_post(
                    body=_('Scenario rejected by reviewer: %s') % self.reviewer_id.name,
                    message_type='notification'
                )
                
        elif self.decision == 'request_changes':
            if scenario.status == 'pending_review':
                scenario.status = 'draft'
                scenario.message_post(
                    body=_('Changes requested by reviewer: %s\n\nFeedback: %s') % 
                         (self.reviewer_id.name, self.notes),
                    message_type='notification'
                )
        
        self.is_processed = True
    
    def action_view_scenario(self):
        """Открыть сценарий для просмотра"""
        self.ensure_one()
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Scenario'),
            'res_model': 'bcm.scenario',
            'res_id': self.scenario_id.id,
            'view_mode': 'form',
            'target': 'current'
        }
    
    @api.model
    def get_review_statistics(self):
        """Получить статистику рецензирования"""
        stats = {}
        
        # Общее количество рецензий
        stats['total_reviews'] = self.search_count([])
        
        # По решениям
        for decision in ['approve', 'reject', 'request_changes']:
            stats[f'{decision}_count'] = self.search_count([('decision', '=', decision)])
        
        # По рецензентам (топ-5)
        reviews_by_reviewer = self.read_group(
            domain=[],
            fields=['reviewer_id'],
            groupby=['reviewer_id'],
            limit=5
        )
        
        stats['top_reviewers'] = [
            {
                'reviewer': group['reviewer_id'][1] if group['reviewer_id'] else 'Unknown',
                'count': group['reviewer_id_count']
            }
            for group in reviews_by_reviewer
        ]
        
        # Средние оценки
        all_reviews = self.search([
            ('content_quality', '!=', False),
            ('technical_accuracy', '!=', False)
        ])
        
        if all_reviews:
            stats['avg_content_quality'] = sum(int(r.content_quality) for r in all_reviews) / len(all_reviews)
            stats['avg_technical_accuracy'] = sum(int(r.technical_accuracy) for r in all_reviews) / len(all_reviews)
        else:
            stats['avg_content_quality'] = 0
            stats['avg_technical_accuracy'] = 0
        
        return stats
