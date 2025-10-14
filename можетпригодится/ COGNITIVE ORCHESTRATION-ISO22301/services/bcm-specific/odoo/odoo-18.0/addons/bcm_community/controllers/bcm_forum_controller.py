# -*- coding: utf-8 -*-

from odoo import http, fields, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.addons.website_forum.controllers.main import WebsiteForum
import json

class BCMForumController(WebsiteForum):
    """BCM Community Forum Controller extending Odoo's website_forum"""

    @http.route('/bcm/community', type='http', auth='public', website=True)
    def bcm_community_home(self, **kwargs):
        """BCM Community homepage with scenario discussions"""

        # Get forum data
        Forum = request.env['forum.forum']
        forums = Forum.search([])

        # Get recent scenarios with discussions
        scenarios_with_discussions = request.env['bcm.scenario'].search([
            ('is_published', '=', True),
            ('forum_topic_id', '!=', False)
        ], limit=10, order='create_date desc')

        # Get community stats
        community_stats = self._get_community_stats()

        values = {
            'forums': forums,
            'recent_scenarios': scenarios_with_discussions,
            'community_stats': community_stats,
            'page_name': 'bcm_community_home',
        }

        return request.render('bcm_community.community_homepage', values)

    @http.route('/bcm/community/scenario/<int:scenario_id>/discuss', type='http', auth='public', website=True)
    def scenario_discussion(self, scenario_id, **kwargs):
        """Scenario-specific discussion page"""

        scenario = request.env['bcm.scenario'].browse(scenario_id)
        if not scenario.exists() or not scenario.is_published:
            return request.not_found()

        # Get or create forum topic for scenario
        if not scenario.forum_topic_id:
            # Auto-create forum topic
            forum_topic = request.env['bcm.forum.topic'].sudo().create_from_scenario(scenario_id)
            scenario.sudo().forum_topic_id = forum_topic

        # Get forum posts for this scenario
        forum_posts = []
        if scenario.forum_topic_id and scenario.forum_topic_id.external_id:
            # Get posts from forum system
            pass

        values = {
            'scenario': scenario,
            'forum_topic': scenario.forum_topic_id,
            'forum_posts': forum_posts,
            'page_name': 'scenario_discussion',
        }

        return request.render('bcm_community.scenario_discussion', values)

    @http.route('/bcm/community/api/scenarios/<int:scenario_id>/create-discussion',
                type='json', auth='user', methods=['POST'])
    def create_scenario_discussion(self, scenario_id, **kwargs):
        """API endpoint to create forum discussion for scenario"""

        scenario = request.env['bcm.scenario'].browse(scenario_id)
        if not scenario.exists():
            return {'error': 'Scenario not found'}

        if scenario.forum_topic_id:
            return {'error': 'Discussion already exists', 'topic_id': scenario.forum_topic_id.id}

        # Create forum topic
        forum_topic = request.env['bcm.forum.topic'].create_from_scenario(scenario_id)

        if forum_topic:
            scenario.forum_topic_id = forum_topic
            return {
                'success': True,
                'topic_id': forum_topic.id,
                'forum_url': f'/bcm/community/scenario/{scenario_id}/discuss'
            }

        return {'error': 'Failed to create discussion'}

    @http.route('/bcm/community/api/stats', type='json', auth='public')
    def get_community_stats(self, **kwargs):
        """Get community statistics via API"""
        return self._get_community_stats()

    def _get_community_stats(self):
        """Get community statistics"""

        # Scenario stats
        total_scenarios = request.env['bcm.scenario'].search_count([('is_published', '=', True)])
        ai_scenarios = request.env['bcm.scenario'].search_count([
            ('is_published', '=', True),
            ('meta_ai_generated', '=', True)
        ])

        # Forum stats
        total_topics = request.env['bcm.forum.topic'].search_count([])
        scenario_discussions = request.env['bcm.forum.topic'].search_count([
            ('category', '=', 'scenario_discussion')
        ])

        # User stats
        active_users = request.env['res.users'].search_count([('active', '=', True)])

        return {
            'total_scenarios': total_scenarios,
            'ai_scenarios': ai_scenarios,
            'scenario_discussions': scenario_discussions,
            'total_topics': total_topics,
            'active_users': active_users,
            'last_updated': fields.Datetime.now().isoformat()
        }

class BCMPortalController(CustomerPortal):
    """BCM Portal integration for external users"""

    @http.route('/my/bcm', type='http', auth='user', website=True)
    def portal_my_bcm(self, **kwargs):
        """BCM portal homepage for users"""

        # Get user's scenarios and discussions
        user_scenarios = request.env['bcm.scenario'].search([
            ('create_uid', '=', request.env.user.id),
            ('is_published', '=', True)
        ])

        user_topics = request.env['bcm.forum.topic'].search([
            ('user_id', '=', request.env.user.id)
        ])

        values = {
            'user_scenarios': user_scenarios,
            'user_topics': user_topics,
            'page_name': 'my_bcm',
        }

        return request.render('bcm_community.portal_my_bcm', values)

    @http.route('/my/bcm/scenarios', type='http', auth='user', website=True)
    def portal_my_scenarios(self, **kwargs):
        """User's scenarios management"""

        scenarios = request.env['bcm.scenario'].search([
            ('create_uid', '=', request.env.user.id)
        ])

        values = {
            'scenarios': scenarios,
            'page_name': 'my_scenarios',
        }

        return request.render('bcm_community.portal_my_scenarios', values)