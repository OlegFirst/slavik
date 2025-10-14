# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging
import requests
import json

_logger = logging.getLogger(__name__)

class BCMKnowledgeArticle(models.Model):
    """Knowledge Base Articles for BCM Platform"""
    _name = 'bcm.knowledge.article'
    _description = 'BCM Knowledge Base Article'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'website.published.mixin']
    _order = 'sequence, create_date desc'

    name = fields.Char('Article Title', required=True, translate=True)
    content = fields.Html('Article Content', translate=True)
    summary = fields.Text('Summary', translate=True)

    # Categorization
    category = fields.Selection([
        ('best_practice', 'Best Practice'),
        ('lesson_learned', 'Lesson Learned'),
        ('procedure', 'Standard Procedure'),
        ('case_study', 'Case Study'),
        ('template_guide', 'Template Usage Guide'),
        ('troubleshooting', 'Troubleshooting Guide'),
        ('compliance', 'Compliance Guide')
    ], string='Category', required=True, default='best_practice')

    article_type = fields.Selection([
        ('manual', 'Manually Created'),
        ('ai_generated', 'AI Generated'),
        ('community_driven', 'Community Driven'),
        ('exercise_derived', 'Derived from Exercise')
    ], string='Article Type', default='manual')

    # Source tracking
    source_exercise_id = fields.Many2one(
        'bcm.exercise',
        string='Source Exercise',
        help='Exercise this article was derived from'
    )

    source_scenario_id = fields.Many2one(
        'bcm.scenario',
        string='Source Scenario',
        help='Scenario this article relates to'
    )

    source_forum_topic_id = fields.Many2one(
        'bcm.forum.topic',
        string='Source Forum Discussion',
        help='Forum discussion this article was created from'
    )

    # AI generation metadata
    ai_prompt = fields.Text('AI Generation Prompt', help='Prompt used for AI generation')
    ai_confidence = fields.Float('AI Confidence Score', help='AI confidence in generated content')

    # Content organization
    tags = fields.Many2many('bcm.knowledge.tag', string='Tags')
    iso_clauses = fields.Many2many('bcm.iso.clause', string='Related ISO 22301 Clauses')

    # Analytics
    view_count = fields.Integer('View Count', default=0)
    bookmark_count = fields.Integer('Bookmarks', default=0)
    usefulness_score = fields.Float('Usefulness Score', compute='_compute_usefulness_score', store=True)
    feedback_count = fields.Integer('Feedback Count', default=0)

    # Structure
    sequence = fields.Integer('Sequence', default=10)
    parent_article_id = fields.Many2one('bcm.knowledge.article', 'Parent Article')
    child_article_ids = fields.One2many('bcm.knowledge.article', 'parent_article_id', 'Sub-articles')

    # Relations
    related_scenarios = fields.Many2many('bcm.scenario', string='Related Scenarios')
    related_templates = fields.Many2many('bcm.template', string='Related Templates')

    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    @api.depends('view_count', 'bookmark_count', 'feedback_count')
    def _compute_usefulness_score(self):
        """Compute article usefulness score"""
        for article in self:
            # Weighted score: views (30%), bookmarks (50%), feedback (20%)
            if article.view_count > 0:
                score = (
                    (article.view_count * 0.3) +
                    (article.bookmark_count * 5 * 0.5) +  # Bookmarks worth 5x views
                    (article.feedback_count * 3 * 0.2)     # Feedback worth 3x views
                )
                article.usefulness_score = min(score / 10, 10.0)  # Normalize to 0-10
            else:
                article.usefulness_score = 0

    @api.model
    def create_from_exercise_results(self, exercise_id):
        """Auto-create knowledge article from exercise results"""
        exercise = self.env['bcm.exercise'].browse(exercise_id)
        if not exercise.exists():
            return False

        # Get exercise learning data from Scenario Orchestrator
        try:
            if exercise.scenario_id:
                response = requests.get(
                    f'http://scenario_orchestrator:8085/learning/scenario/{exercise.scenario_id.id}/insights',
                    timeout=10
                )

                if response.status_code == 200:
                    insights = response.json().get('insights', {})

                    # Generate AI-powered knowledge article
                    article_content = self._generate_article_content_with_ai(exercise, insights)

                    article_data = {
                        'name': f'Best Practices: {exercise.name}',
                        'category': 'lesson_learned',
                        'article_type': 'exercise_derived',
                        'content': article_content,
                        'source_exercise_id': exercise.id,
                        'source_scenario_id': exercise.scenario_id.id if exercise.scenario_id else None,
                        'summary': f'Key learnings and best practices from exercise "{exercise.name}"',
                        'is_published': False  # Start as draft for review
                    }

                    article = self.create(article_data)

                    # Link back to exercise
                    exercise.message_post(
                        body=f'Knowledge article created: <a href="/web#id={article.id}&model=bcm.knowledge.article">{article.name}</a>',
                        subject='Knowledge Article Generated'
                    )

                    return article

        except Exception as e:
            _logger.error(f'Failed to create knowledge article from exercise {exercise_id}: {e}')

        return False

    def _generate_article_content_with_ai(self, exercise, insights):
        """Generate knowledge article content using AI"""
        try:
            # Build AI prompt for knowledge article generation
            ai_prompt = f"""
Create a comprehensive knowledge base article based on the following BCM exercise results:

EXERCISE INFORMATION:
- Name: {exercise.name}
- Type: {exercise.exercise_type}
- Scenario: {exercise.scenario_id.title if exercise.scenario_id else 'N/A'}
- Participants: {len(exercise.participant_ids)}

LEARNING INSIGHTS:
- Total scenario uses: {insights.get('total_uses', 0)}
- Average effectiveness: {insights.get('avg_effectiveness', 0)}/10
- Successful elements: {', '.join(insights.get('successful_elements', [])[:3])}
- Common issues: {', '.join(insights.get('common_issues', [])[:3])}
- Improvement recommendations: {', '.join(insights.get('ai_recommendations', [])[:3])}

Please create a structured knowledge article with:
1. Executive Summary
2. Key Findings
3. Best Practices
4. Lessons Learned
5. Implementation Recommendations
6. Related Resources

Format as HTML для Odoo knowledge base.
"""

            # Query AI Orchestrator
            response = requests.post(
                'http://ai_orchestrator:8000/nlp/query',
                json={
                    'query': ai_prompt,
                    'context': {
                        'type': 'knowledge_article_generation',
                        'exercise_id': exercise.id,
                        'scenario_id': exercise.scenario_id.id if exercise.scenario_id else None
                    },
                    'user_role': 'knowledge_curator'
                },
                timeout=60
            )

            if response.status_code == 200:
                ai_result = response.json()
                ai_content = ai_result.get('response', '')

                # Format AI response as structured HTML
                formatted_content = f"""
<div class="knowledge-article">
    <div class="article-meta">
        <p><strong>Generated from Exercise:</strong> {exercise.name}</p>
        <p><strong>Exercise Type:</strong> {exercise.exercise_type}</p>
        <p><strong>Generated on:</strong> {fields.Datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
    </div>

    <div class="ai-generated-content">
        {ai_content}
    </div>

    <div class="source-data">
        <h4>Source Data</h4>
        <ul>
            <li><strong>Exercise Uses:</strong> {insights.get('total_uses', 0)} times</li>
            <li><strong>Effectiveness Score:</strong> {insights.get('avg_effectiveness', 0)}/10</li>
            <li><strong>Data Source:</strong> Scenario Orchestrator Learning System</li>
        </ul>
    </div>

    <div class="disclaimer">
        <p><em>This article was automatically generated from exercise results and AI analysis.
        Please review and validate before publication.</em></p>
    </div>
</div>
"""

                return formatted_content

        except Exception as e:
            _logger.error(f'AI article generation failed: {e}')

        # Fallback manual template
        return f"""
<div class="knowledge-article">
    <h2>Exercise Summary: {exercise.name}</h2>

    <h3>Exercise Details</h3>
    <ul>
        <li><strong>Type:</strong> {exercise.exercise_type}</li>
        <li><strong>Participants:</strong> {len(exercise.participant_ids)}</li>
        <li><strong>Template Used:</strong> {exercise.template_id.name if exercise.template_id else 'None'}</li>
    </ul>

    <h3>Key Learnings</h3>
    <p>This section will be populated with insights from exercise feedback and AI analysis.</p>

    <h3>Best Practices</h3>
    <p>Best practices identified during this exercise will be documented here.</p>

    <h3>Recommendations</h3>
    <p>Recommendations for future exercises based on this experience.</p>
</div>
"""

    def action_regenerate_with_ai(self):
        """Regenerate article content using AI"""
        if not self.source_exercise_id:
            raise ValidationError(_('Cannot regenerate - no source exercise found'))

        # Get latest insights
        exercise = self.source_exercise_id
        try:
            response = requests.get(
                f'http://scenario_orchestrator:8085/learning/scenario/{exercise.scenario_id.id}/insights',
                timeout=10
            )

            if response.status_code == 200:
                insights = response.json().get('insights', {})
                new_content = self._generate_article_content_with_ai(exercise, insights)

                self.write({
                    'content': new_content,
                    'ai_confidence': insights.get('avg_effectiveness', 0) / 10  # Convert to 0-1 scale
                })

                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Article Regenerated'),
                        'message': 'Article content updated with latest AI insights',
                        'type': 'success',
                    }
                }

        except Exception as e:
            raise UserError(f'Failed to regenerate article: {str(e)}')

class BCMKnowledgeTag(models.Model):
    """Tags for knowledge base articles"""
    _name = 'bcm.knowledge.tag'
    _description = 'Knowledge Tag'

    name = fields.Char('Tag Name', required=True)
    color = fields.Integer('Color Index')
    description = fields.Text('Tag Description')

    article_count = fields.Integer('Article Count', compute='_compute_article_count')

    @api.depends()
    def _compute_article_count(self):
        for tag in self:
            tag.article_count = self.env['bcm.knowledge.article'].search_count([
                ('tags', 'in', [tag.id])
            ])

class BCMISOClause(models.Model):
    """ISO 22301 Clauses for knowledge base organization"""
    _name = 'bcm.iso.clause'
    _description = 'ISO 22301 Clause'

    name = fields.Char('Clause Number', required=True)  # e.g., "4.1", "8.1"
    title = fields.Char('Clause Title', required=True)  # e.g., "Organization Context"
    description = fields.Text('Clause Description')

    article_count = fields.Integer('Related Articles', compute='_compute_article_count')

    @api.depends()
    def _compute_article_count(self):
        for clause in self:
            clause.article_count = self.env['bcm.knowledge.article'].search_count([
                ('iso_clauses', 'in', [clause.id])
            ])


class BCMKnowledgeBookmark(models.Model):
    """Knowledge Article Bookmark for tracking user bookmarks"""
    _name = 'bcm.knowledge.bookmark'
    _description = 'Knowledge Article Bookmark'

    article_id = fields.Many2one('bcm.knowledge.article', required=True, ondelete='cascade')
    user_id = fields.Many2one('res.users', required=True, ondelete='cascade')
    create_date = fields.Datetime(default=fields.Datetime.now)

    _sql_constraints = [
        ('unique_user_article', 'unique(user_id, article_id)', 'User can only bookmark an article once')
    ]


class BCMKnowledgeCategory(models.Model):
    """Knowledge Article Categories"""
    _name = 'bcm.knowledge.category'
    _description = 'Knowledge Article Category'

    name = fields.Char('Category Name', required=True)
    code = fields.Char('Category Code', required=True)
    description = fields.Text('Description')
    icon = fields.Char('Icon Class', default='fas fa-folder')
    color = fields.Char('Color', default='#007bff')
    sequence = fields.Integer('Sequence', default=10)

    article_count = fields.Integer('Article Count', compute='_compute_article_count')

    @api.depends()
    def _compute_article_count(self):
        for category in self:
            category.article_count = self.env['bcm.knowledge.article'].search_count([
                ('category', '=', category.code)
            ])


class BCMExpertVerification(models.Model):
    """Expert verification system for knowledge articles"""
    _name = 'bcm.expert.verification'
    _description = 'Expert Verification'

    article_id = fields.Many2one('bcm.knowledge.article', required=True, ondelete='cascade')
    expert_id = fields.Many2one('res.users', required=True, string='Expert')
    verification_status = fields.Selection([
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('needs_revision', 'Needs Revision')
    ], default='pending')

    verification_date = fields.Datetime('Verification Date')
    comments = fields.Text('Comments')
    confidence_score = fields.Float('Confidence Score', help='Expert confidence in article accuracy (0-10)')

    @api.model
    def create(self, vals):
        # Auto-set verification date when status changes
        if vals.get('verification_status') != 'pending':
            vals['verification_date'] = fields.Datetime.now()
        return super().create(vals)

    def write(self, vals):
        # Auto-set verification date when status changes
        if 'verification_status' in vals and vals['verification_status'] != 'pending':
            vals['verification_date'] = fields.Datetime.now()
        return super().write(vals)