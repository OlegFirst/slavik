# -*- coding: utf-8 -*-
"""
BCM Compliance API Controllers
=============================

REST API endpoints for frontend Compliance Dashboard integration
"""

import json
import logging
from datetime import datetime
from odoo import http, _
from odoo.http import request
from odoo.exceptions import AccessError, UserError

_logger = logging.getLogger(__name__)

class BCMComplianceAPI(http.Controller):
    """API Controller for BCM Compliance Dashboard"""

    @http.route('/api/bcm/compliance/overview', type='json', auth='user', methods=['POST'], cors='*')
    def get_compliance_overview(self, **kwargs):
        """Get comprehensive compliance overview for dashboard"""
        try:
            dashboard_model = request.env['bcm.compliance.dashboard']
            overview_data = dashboard_model.get_compliance_overview()
            
            return {
                'success': True,
                'data': overview_data,
                'message': 'Compliance overview retrieved successfully'
            }
            
        except AccessError:
            return {
                'success': False,
                'error': 'access_denied',
                'message': 'Insufficient permissions to access compliance data'
            }
        except Exception as e:
            _logger.error(f'Error fetching compliance overview: {str(e)}')
            return {
                'success': False,
                'error': 'server_error',
                'message': f'Server error: {str(e)}'
            }

    @http.route('/api/bcm/compliance/modules', type='json', auth='user', methods=['POST'], cors='*')
    def get_module_compliance(self, **kwargs):
        """Get module compliance matrix"""
        try:
            dashboard_model = request.env['bcm.compliance.dashboard']
            module_data = dashboard_model.get_module_compliance_matrix()
            
            return {
                'success': True,
                'data': module_data,
                'message': 'Module compliance data retrieved successfully'
            }
            
        except Exception as e:
            _logger.error(f'Error fetching module compliance: {str(e)}')
            return {
                'success': False,
                'error': 'server_error',
                'message': f'Server error: {str(e)}'
            }

    @http.route('/api/bcm/module/<module_name>/open', type='http', auth='user', methods=['GET'])
    def open_module_in_odoo(self, module_name, **kwargs):
        """Redirect to specific module in Odoo"""
        try:
            base_url = request.httprequest.host_url
            
            # Module-specific URLs
            module_urls = {
                'bcm_governance': 'web#action=bcm_governance.action_governance_brain&model=bcm.governance.brain&view_type=kanban',
                'bcm_risk_management': 'web#model=bcm.risk&view_type=tree',
                'bcm_bia': 'web#model=bcm.bia.result&view_type=tree',
                'bcm_plans': 'web#model=bcm.plan&view_type=tree',
                'bcm_incident': 'web#model=bcm.incident&view_type=tree',
                'bcm_ai_control': 'web#model=bcm.ai.control&view_type=form',
                'bcm_community': 'web#model=bcm.community&view_type=kanban',
            }
            
            url = f"{base_url}{module_urls.get(module_name, f'web#model={module_name}&view_type=form')}"
            return request.redirect(url)
            
        except Exception as e:
            _logger.error(f'Error opening module {module_name}: {str(e)}')
            return request.redirect('/web')
