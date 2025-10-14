# -*- coding: utf-8 -*-

from odoo import http, fields
from odoo.http import request
import json
import logging

_logger = logging.getLogger(__name__)

class BCMScenarioAPI(http.Controller):
    """REST API for BCM Scenarios"""

    @http.route('/api/v1/bcm_scenario', type='json', auth='public', methods=['POST'], csrf=False)
    def create_scenario(self, **kwargs):
        """Create new BCM scenario via API"""
        try:
            # Get JSON data from request
            data = request.get_json_data() or kwargs

            # Validate required fields
            if not data.get('title'):
                return {'error': 'Title is required', 'code': 400}

            # Create scenario record
            scenario_vals = {
                'title': data.get('title'),
                'category': data.get('category', 'other'),
                'level': data.get('level', 'tabletop'),
                'content_md': data.get('content_md', ''),
                'meta_description': data.get('meta_description', ''),
                'meta_duration': data.get('meta_duration', 4),
                'meta_participants': data.get('meta_participants', 10),
                'status': 'draft',  # Start as draft
                'is_published': False,
            }

            # Add AI generation metadata if present
            if data.get('is_ai_generated'):
                scenario_vals.update({
                    'meta_ai_generated': True,
                    'meta_ai_params': json.dumps(data.get('ai_generation_params', {}))
                })

            # Create the scenario
            scenario = request.env['bcm.scenario'].sudo().create(scenario_vals)

            _logger.info(f"Created scenario via API: {scenario.id} - {scenario.title}")

            return {
                'status': 'success',
                'id': scenario.id,
                'title': scenario.title,
                'category': scenario.category,
                'created_at': scenario.create_date.isoformat() if scenario.create_date else None
            }

        except Exception as e:
            _logger.error(f"Error creating scenario via API: {str(e)}")
            return {'error': str(e), 'code': 500}

    @http.route('/api/v1/bcm_scenario', type='json', auth='public', methods=['GET'], csrf=False)
    def get_scenarios(self, **kwargs):
        """Get BCM scenarios via API"""
        try:
            # Build domain for search
            domain = []

            # Add filters
            if kwargs.get('published_only'):
                domain.append(('is_published', '=', True))

            if kwargs.get('category'):
                domain.append(('category', '=', kwargs.get('category')))

            if kwargs.get('ai_generated'):
                domain.append(('meta_ai_generated', '=', True))

            # Get scenarios
            scenarios = request.env['bcm.scenario'].sudo().search(domain, limit=kwargs.get('limit', 50))

            scenario_data = []
            for scenario in scenarios:
                scenario_data.append({
                    'id': scenario.id,
                    'title': scenario.title,
                    'category': scenario.category,
                    'level': scenario.level,
                    'description': scenario.meta_description or '',
                    'duration': scenario.meta_duration,
                    'participants': scenario.meta_participants,
                    'status': scenario.status,
                    'is_published': scenario.is_published,
                    'is_ai_generated': getattr(scenario, 'meta_ai_generated', False),
                    'created_at': scenario.create_date.isoformat() if scenario.create_date else None,
                    'author': scenario.create_uid.name if scenario.create_uid else 'Unknown'
                })

            return {
                'status': 'success',
                'scenarios': scenario_data,
                'total': len(scenario_data)
            }

        except Exception as e:
            _logger.error(f"Error getting scenarios via API: {str(e)}")
            return {'error': str(e), 'code': 500}

    @http.route('/api/v1/bcm_scenario/<int:scenario_id>', type='json', auth='public', methods=['GET'], csrf=False)
    def get_scenario(self, scenario_id, **kwargs):
        """Get specific BCM scenario via API"""
        try:
            scenario = request.env['bcm.scenario'].sudo().browse(scenario_id)

            if not scenario.exists():
                return {'error': 'Scenario not found', 'code': 404}

            return {
                'status': 'success',
                'scenario': {
                    'id': scenario.id,
                    'title': scenario.title,
                    'category': scenario.category,
                    'level': scenario.level,
                    'content_md': scenario.content_md or '',
                    'description': scenario.meta_description or '',
                    'duration': scenario.meta_duration,
                    'participants': scenario.meta_participants,
                    'status': scenario.status,
                    'is_published': scenario.is_published,
                    'is_ai_generated': getattr(scenario, 'meta_ai_generated', False),
                    'created_at': scenario.create_date.isoformat() if scenario.create_date else None,
                    'updated_at': scenario.write_date.isoformat() if scenario.write_date else None,
                    'author': scenario.create_uid.name if scenario.create_uid else 'Unknown',
                    'company': scenario.company_id.name if scenario.company_id else None
                }
            }

        except Exception as e:
            _logger.error(f"Error getting scenario {scenario_id} via API: {str(e)}")
            return {'error': str(e), 'code': 500}

    @http.route('/web/health', type='http', auth='none', methods=['GET'], csrf=False)
    def health_check(self):
        """Health check endpoint"""
        return request.make_response(
            json.dumps({"status": "pass", "service": "odoo_bcm_platform"}),
            headers=[('Content-Type', 'application/json')]
        )