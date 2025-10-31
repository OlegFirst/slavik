# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessError
import requests
import json
import logging

_logger = logging.getLogger(__name__)

class BCMForumIntegration(models.Model):
    """Integration bridge with Community Forum Service"""
    _name = 'bcm.forum.integration'
    _description = 'BCM Forum Service Integration'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Integration Name', required=True, default='Community Forum Service')

    # Service configuration
    service_url = fields.Char(
        'Forum Service URL',
        default='http://localhost:3000',  # Default community service port
        help='URL of the external Community Forum Service'
    )

    api_key = fields.Char('API Key', help='Authentication key for forum service')
    is_active = fields.Boolean('Active', default=True)

    # Synchronization settings
    sync_users = fields.Boolean('Sync Users', default=True)
    sync_topics = fields.Boolean('Sync Topics', default=True)
    sync_posts = fields.Boolean('Sync Posts', default=True)

    # Status fields
    last_sync = fields.Datetime('Last Synchronization')
    sync_status = fields.Selection([
        ('idle', 'Idle'),
        ('syncing', 'Synchronizing'),
        ('error', 'Error'),
        ('success', 'Success')
    ], default='idle', string='Sync Status')

    error_message = fields.Text('Last Error Message')

    def _get_forum_api_headers(self):
        """Get headers for forum service API calls"""
        headers = {'Content-Type': 'application/json'}
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'
        return headers

    @api.model
    def create_forum_topic_from_scenario(self, scenario_id, topic_title=None):
        """Create forum topic when new scenario is published"""
        scenario = self.env['bcm.scenario'].browse(scenario_id)
        if not scenario.exists():
            return False

        integration = self.search([('is_active', '=', True)], limit=1)
        if not integration:
            _logger.warning('No active forum integration found')
            return False

        topic_data = {
            'title': topic_title or f'Discussion: {scenario.title}',
            'category': 'scenario_discussion',
            'content': f"""
# Scenario Discussion: {scenario.title}

**Category**: {scenario.category}
**Level**: {scenario.level}
**Author**: {scenario.create_uid.name}

## Description
{scenario.meta_description or 'No description provided'}

## Discussion
Please share your thoughts, experiences, and improvements for this scenario.

---
*This topic was automatically created from BCM Scenario Hub*
            """.strip(),
            'tags': [scenario.category, scenario.level, 'scenario'],
            'metadata': {
                'source': 'bcm_scenario_hub',
                'scenario_id': scenario.id,
                'scenario_uuid': scenario.uuid if hasattr(scenario, 'uuid') else None
            }
        }

        try:
            response = requests.post(
                f'{integration.service_url}/api/topics',
                json=topic_data,
                headers=integration._get_forum_api_headers(),
                timeout=10
            )

            if response.status_code == 201:
                forum_topic_data = response.json()

                # Create local record for tracking
                self.env['bcm.forum.topic'].create({
                    'name': topic_data['title'],
                    'external_id': forum_topic_data.get('id'),
                    'category': 'scenario_discussion',
                    'scenario_id': scenario.id,
                    'forum_url': f"{integration.service_url}/topics/{forum_topic_data.get('id')}",
                    'is_synced': True
                })

                # Add chatter message
                scenario.message_post(
                    body=f"Forum discussion topic created: <a href='{integration.service_url}/topics/{forum_topic_data.get('id')}' target='_blank'>{topic_data['title']}</a>",
                    subject='Forum Discussion Created'
                )

                return forum_topic_data.get('id')

        except Exception as e:
            _logger.error(f'Failed to create forum topic: {str(e)}')
            integration.error_message = str(e)
            integration.sync_status = 'error'

        return False

    @api.model
    def sync_user_to_forum(self, user_id):
        """Sync Odoo user to forum service"""
        user = self.env['res.users'].browse(user_id)
        if not user.exists():
            return False

        integration = self.search([('is_active', '=', True), ('sync_users', '=', True)], limit=1)
        if not integration:
            return False

        user_data = {
            'username': user.login,
            'email': user.email,
            'name': user.name,
            'company': user.company_id.name if user.company_id else None,
            'is_bcm_professional': user.has_group('bcm_core.group_bcm_user'),
            'is_bcm_expert': user.has_group('bcm_core.group_bcm_manager'),
            'avatar_url': f'/web/image/res.users/{user.id}/image_128',
            'metadata': {
                'odoo_user_id': user.id,
                'company_id': user.company_id.id if user.company_id else None,
                'sync_timestamp': fields.Datetime.now().isoformat()
            }
        }

        try:
            response = requests.post(
                f'{integration.service_url}/api/users/sync',
                json=user_data,
                headers=integration._get_forum_api_headers(),
                timeout=10
            )

            return response.status_code in [200, 201]

        except Exception as e:
            _logger.error(f'Failed to sync user to forum: {str(e)}')
            return False

    def action_test_connection(self):
        """Test connection to forum service"""
        try:
            response = requests.get(
                f'{self.service_url}/api/health',
                headers=self._get_forum_api_headers(),
                timeout=5
            )

            if response.status_code == 200:
                self.sync_status = 'success'
                self.error_message = False
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Connection Test'),
                        'message': _('Successfully connected to Forum Service'),
                        'type': 'success',
                    }
                }
            else:
                raise Exception(f'HTTP {response.status_code}: {response.text}')

        except Exception as e:
            self.sync_status = 'error'
            self.error_message = str(e)
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Connection Error'),
                    'message': str(e),
                    'type': 'danger',
                }
            }

    def action_sync_all(self):
        """Synchronize all data with forum service"""
        self.sync_status = 'syncing'

        try:
            # Sync users
            if self.sync_users:
                users = self.env['res.users'].search([('active', '=', True)])
                for user in users:
                    self.sync_user_to_forum(user.id)

            # Sync scenario discussions
            if self.sync_topics:
                scenarios = self.env['bcm.scenario'].search([
                    ('is_published', '=', True),
                    ('scenario_discussion_topic', '=', False)
                ])
                for scenario in scenarios:
                    self.create_forum_topic_from_scenario(scenario.id)

            self.last_sync = fields.Datetime.now()
            self.sync_status = 'success'
            self.error_message = False

        except Exception as e:
            _logger.error(f'Sync failed: {str(e)}')
            self.sync_status = 'error'
            self.error_message = str(e)

    @api.model
    def create_knowledge_base_article(self, title, content, category='general'):
        """Create knowledge base article in forum service"""
        integration = self.search([('is_active', '=', True)], limit=1)
        if not integration:
            return False

        article_data = {
            'title': title,
            'content': content,
            'category': category,
            'type': 'knowledge_base',
            'author_id': self.env.user.id,
            'metadata': {
                'source': 'bcm_odoo',
                'created_from': 'knowledge_base',
                'author_company': self.env.user.company_id.name
            }
        }

        try:
            response = requests.post(
                f'{integration.service_url}/api/knowledge-base',
                json=article_data,
                headers=integration._get_forum_api_headers(),
                timeout=10
            )

            if response.status_code == 201:
                return response.json().get('id')

        except Exception as e:
            _logger.error(f'Failed to create knowledge base article: {str(e)}')

        return False