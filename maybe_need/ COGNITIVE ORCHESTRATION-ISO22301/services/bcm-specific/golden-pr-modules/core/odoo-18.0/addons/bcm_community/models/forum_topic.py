# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class BCMForumTopic(models.Model):
    """Forum topics integrated with external Community Service"""
    _name = 'bcm.forum.topic'
    _description = 'BCM Forum Topic'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'last_activity desc, create_date desc'
    _rec_name = 'name'

    name = fields.Char('Topic Title', required=True, tracking=True)

    # External service integration
    external_id = fields.Char('External Topic ID', help='ID in Community Forum Service')
    forum_url = fields.Char('Forum URL', help='Direct link to topic in forum')
    is_synced = fields.Boolean('Synchronized', default=False)

    # Topic categorization
    category = fields.Selection([
        ('general', 'General Discussion'),
        ('bcm_policy', 'BCM Policy & Standards'),
        ('risk_management', 'Risk Management'),
        ('incident_response', 'Incident Response'),
        ('bia', 'Business Impact Analysis'),
        ('recovery_planning', 'Recovery Planning'),
        ('exercises', 'Exercises & Testing'),
        ('technology', 'Technology & Tools'),
        ('scenario_discussion', 'Scenario Discussion'),
        ('knowledge_base', 'Knowledge Base'),
    ], string='Category', required=True, default='general')

    # Content and metadata
    description = fields.Html('Description')
    tags = fields.Char('Tags', help='Comma-separated tags')

    # Relationships
    scenario_id = fields.Many2one(
        'bcm.scenario',
        string='Related Scenario',
        help='Scenario this topic discusses'
    )

    user_id = fields.Many2one(
        'res.users',
        string='Created By',
        default=lambda self: self.env.user,
        required=True
    )

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        required=True
    )

    # Activity tracking
    post_count = fields.Integer('Post Count', default=0)
    view_count = fields.Integer('View Count', default=0)
    last_activity = fields.Datetime('Last Activity', default=fields.Datetime.now)
    last_post_user_id = fields.Many2one('res.users', string='Last Post By')

    # Status
    is_locked = fields.Boolean('Locked', default=False)
    is_pinned = fields.Boolean('Pinned', default=False)
    is_solved = fields.Boolean('Solved', default=False)

    # Reputation and engagement
    upvotes = fields.Integer('Upvotes', default=0)
    downvotes = fields.Integer('Downvotes', default=0)
    score = fields.Integer('Score', compute='_compute_score', store=True)

    @api.depends('upvotes', 'downvotes')
    def _compute_score(self):
        """Compute topic score based on votes"""
        for topic in self:
            topic.score = topic.upvotes - topic.downvotes

    def action_view_in_forum(self):
        """Open topic in external forum service"""
        if not self.forum_url:
            raise ValidationError(_('No forum URL available for this topic'))

        return {
            'type': 'ir.actions.act_url',
            'url': self.forum_url,
            'target': 'new',
        }

    def action_sync_with_forum(self):
        """Sync topic data with external forum service"""
        integration = self.env['bcm.forum.integration'].search([
            ('is_active', '=', True)
        ], limit=1)

        if not integration:
            raise ValidationError(_('No active forum integration found'))

        # This would sync data from external service
        # Implementation depends on the specific API
        try:
            import requests

            response = requests.get(
                f'{integration.service_url}/api/topics/{self.external_id}',
                headers=integration._get_forum_api_headers(),
                timeout=10
            )

            if response.status_code == 200:
                topic_data = response.json()

                self.write({
                    'post_count': topic_data.get('post_count', self.post_count),
                    'view_count': topic_data.get('view_count', self.view_count),
                    'upvotes': topic_data.get('upvotes', self.upvotes),
                    'downvotes': topic_data.get('downvotes', self.downvotes),
                    'is_locked': topic_data.get('is_locked', self.is_locked),
                    'is_solved': topic_data.get('is_solved', self.is_solved),
                    'last_activity': topic_data.get('updated_at', self.last_activity),
                })

                self.message_post(
                    body=_('Topic synchronized with forum service'),
                    subject=_('Forum Sync')
                )

                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Sync Successful'),
                        'message': _('Topic data updated from forum service'),
                        'type': 'success',
                    }
                }

        except Exception as e:
            _logger.error(f'Failed to sync topic {self.id}: {str(e)}')
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Sync Error'),
                    'message': str(e),
                    'type': 'danger',
                }
            }

    @api.model
    def create_from_scenario(self, scenario_id, auto_create_forum_topic=True):
        """Create forum topic from scenario"""
        scenario = self.env['bcm.scenario'].browse(scenario_id)
        if not scenario.exists():
            return False

        topic = self.create({
            'name': f'Discussion: {scenario.title}',
            'category': 'scenario_discussion',
            'description': f"""
                <h3>Scenario Discussion: {scenario.title}</h3>
                <p><strong>Category:</strong> {scenario.category}</p>
                <p><strong>Level:</strong> {scenario.level}</p>
                <p><strong>Author:</strong> {scenario.create_uid.name}</p>

                <h4>Description</h4>
                <p>{scenario.meta_description or 'No description provided'}</p>

                <h4>Discussion</h4>
                <p>Please share your thoughts, experiences, and improvements for this scenario.</p>
            """,
            'scenario_id': scenario.id,
            'tags': f"{scenario.category},{scenario.level},scenario",
        })

        # Auto-create in external forum service
        if auto_create_forum_topic:
            integration = self.env['bcm.forum.integration']
            forum_topic_id = integration.create_forum_topic_from_scenario(scenario.id, topic.name)

            if forum_topic_id:
                topic.write({
                    'external_id': str(forum_topic_id),
                    'is_synced': True,
                    'forum_url': f"{integration.search([('is_active', '=', True)], limit=1).service_url}/topics/{forum_topic_id}"
                })

        return topic

    def action_create_knowledge_article(self):
        """Convert topic discussion to knowledge base article"""
        if self.category != 'scenario_discussion':
            raise ValidationError(_('Only scenario discussions can be converted to knowledge articles'))

        integration = self.env['bcm.forum.integration']

        article_title = f"Best Practices: {self.scenario_id.title if self.scenario_id else self.name}"
        article_content = f"""
# {article_title}

Based on community discussion: [{self.name}]({self.forum_url})

## Scenario Overview
{self.description}

## Community Insights
*This section will be populated with key insights from the forum discussion*

## Best Practices
*Key recommendations from the community discussion*

## Related Resources
- Original Scenario: {self.scenario_id.title if self.scenario_id else 'N/A'}
- Forum Discussion: {self.forum_url or 'Not available'}

---
*This knowledge base article was created from community discussion and should be regularly updated based on new insights.*
        """

        article_id = integration.create_knowledge_base_article(
            title=article_title,
            content=article_content,
            category='bcm_best_practices'
        )

        if article_id:
            self.message_post(
                body=f'Knowledge base article created: {article_title}',
                subject='Knowledge Article Created'
            )

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Knowledge Article Created'),
                    'message': f'Article "{article_title}" has been created in the knowledge base',
                    'type': 'success',
                }
            }
        else:
            raise ValidationError(_('Failed to create knowledge base article'))