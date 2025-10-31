# -*- coding: utf-8 -*-
"""
BCM Compliance API Controllers
=============================

REST API endpoints for frontend Compliance Dashboard integration
"""

import json
import logging
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
                'error': 'Access denied',
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

    @http.route('/api/bcm/compliance/roadmap', type='json', auth='user', methods=['POST'], cors='*')
    def get_compliance_roadmap(self, **kwargs):
        """Get implementation roadmap"""
        try:
            dashboard_model = request.env['bcm.compliance.dashboard']
            roadmap_data = dashboard_model.get_compliance_roadmap()
            
            return {
                'success': True,
                'data': roadmap_data,
                'message': 'Compliance roadmap retrieved successfully'
            }
            
        except Exception as e:
            _logger.error(f'Error fetching compliance roadmap: {str(e)}')
            return {
                'success': False,
                'error': 'server_error',
                'message': f'Server error: {str(e)}'
            }

    @http.route('/api/bcm/compliance/requirements', type='json', auth='user', methods=['POST'], cors='*')
    def get_iso_requirements(self, **kwargs):
        """Get detailed ISO 22301 requirements"""
        try:
            domain = []
            
            # Filter by category if provided
            category = kwargs.get('category')
            if category:
                domain.append(('clause_category', '=', category))
            
            # Filter by compliance status if provided
            status = kwargs.get('status')
            if status:
                domain.append(('compliance_status', '=', status))
            
            requirements = request.env['bcm.iso22301.framework'].search(domain)
            
            data = []
            for req in requirements:
                data.append({
                    'id': req.id,
                    'clause_number': req.clause_number,
                    'clause_title': req.clause_title,
                    'clause_category': req.clause_category,
                    'compliance_status': req.compliance_status,
                    'compliance_percentage': req.compliance_percentage,
                    'risk_level': req.risk_level,
                    'responsible_user': req.responsible_user_id.name if req.responsible_user_id else None,
                    'target_completion_date': req.target_completion_date.isoformat() if req.target_completion_date else None,
                    'ai_compliance_score': req.ai_compliance_score,
                    'related_modules': [{'name': m.name, 'technical_name': m.technical_name} for m in req.related_bcm_modules]
                })
            
            return {
                'success': True,
                'data': data,
                'total': len(data),
                'message': 'ISO requirements retrieved successfully'
            }
            
        except Exception as e:
            _logger.error(f'Error fetching ISO requirements: {str(e)}')
            return {
                'success': False,
                'error': 'server_error',
                'message': f'Server error: {str(e)}'
            }

    @http.route('/api/bcm/compliance/gaps', type='json', auth='user', methods=['POST'], cors='*')
    def get_compliance_gaps(self, **kwargs):
        """Get critical compliance gaps"""
        try:
            # Get critical and high-risk gaps
            critical_gaps = request.env['bcm.iso22301.framework'].search([
                ('risk_level', 'in', ['critical', 'high']),
                ('compliance_status', 'in', ['not_started', 'non_compliant'])
            ])
            
            gaps_data = []
            for gap in critical_gaps:
                gaps_data.append({
                    'id': gap.id,
                    'clause_number': gap.clause_number,
                    'clause_title': gap.clause_title,
                    'risk_level': gap.risk_level,
                    'category': gap.clause_category,
                    'description': gap.clause_description,
                    'identified_gaps': gap.identified_gaps,
                    'gap_action_plan': gap.gap_action_plan,
                    'gap_priority': gap.gap_priority,
                    'responsible_user': gap.responsible_user_id.name if gap.responsible_user_id else None
                })
            
            return {
                'success': True,
                'data': gaps_data,
                'total': len(gaps_data),
                'message': 'Compliance gaps retrieved successfully'
            }
            
        except Exception as e:
            _logger.error(f'Error fetching compliance gaps: {str(e)}')
            return {
                'success': False,
                'error': 'server_error',
                'message': f'Server error: {str(e)}'
            }

    @http.route('/api/bcm/compliance/ai-assessment', type='json', auth='user', methods=['POST'], cors='*')
    def trigger_ai_assessment(self, **kwargs):
        """Trigger AI assessment for specific requirement or all"""
        try:
            requirement_id = kwargs.get('requirement_id')
            
            if requirement_id:
                # Assess specific requirement
                requirement = request.env['bcm.iso22301.framework'].browse(requirement_id)
                if not requirement.exists():
                    return {
                        'success': False,
                        'error': 'not_found',
                        'message': 'ISO requirement not found'
                    }
                
                requirement.action_ai_compliance_assessment()
                
                return {
                    'success': True,
                    'data': {
                        'clause_number': requirement.clause_number,
                        'ai_compliance_score': requirement.ai_compliance_score,
                        'compliance_status': requirement.compliance_status
                    },
                    'message': f'AI assessment completed for clause {requirement.clause_number}'
                }
            else:
                # Trigger full assessment
                dashboard_model = request.env['bcm.compliance.dashboard']
                result = dashboard_model.trigger_full_ai_assessment()
                
                return {
                    'success': True,
                    'data': result,
                    'message': 'Full AI assessment triggered successfully'
                }
                
        except Exception as e:
            _logger.error(f'Error triggering AI assessment: {str(e)}')
            return {
                'success': False,
                'error': 'server_error',
                'message': f'Server error: {str(e)}'
            }

    @http.route('/api/bcm/compliance/module-health', type='json', auth='user', methods=['POST'], cors='*')
    def get_module_health(self, **kwargs):
        """Get health status of BCM modules"""
        try:
            modules = request.env['bcm.module.mapping'].search([])
            
            health_data = []
            for module in modules:
                health_data.append({
                    'id': module.id,
                    'name': module.name,
                    'technical_name': module.technical_name,
                    'development_status': module.development_status,
                    'health_status': module.health_status,
                    'compliance_contribution': module.compliance_contribution,
                    'last_health_check': module.last_health_check.isoformat() if module.last_health_check else None,
                    'supported_clauses_count': len(module.iso_clauses)
                })
            
            # Calculate health summary
            total_modules = len(modules)
            healthy = len(modules.filtered(lambda m: m.health_status == 'healthy'))
            warning = len(modules.filtered(lambda m: m.health_status == 'warning'))
            critical = len(modules.filtered(lambda m: m.health_status == 'critical'))
            offline = len(modules.filtered(lambda m: m.health_status == 'offline'))
            
            return {
                'success': True,
                'data': {
                    'modules': health_data,
                    'summary': {
                        'total': total_modules,
                        'healthy': healthy,
                        'warning': warning,
                        'critical': critical,
                        'offline': offline,
                        'health_percentage': round((healthy / total_modules * 100), 1) if total_modules else 0
                    }
                },
                'message': 'Module health data retrieved successfully'
            }
            
        except Exception as e:
            _logger.error(f'Error fetching module health: {str(e)}')
            return {
                'success': False,
                'error': 'server_error',
                'message': f'Server error: {str(e)}'
            }

    @http.route('/api/bcm/compliance/open-module', type='http', auth='user', methods=['GET'], cors='*')
    def open_module_in_odoo(self, module_name, **kwargs):
        """Redirect to specific module in Odoo"""
        try:
            # Find the module
            module = request.env['bcm.module.mapping'].search([
                ('technical_name', '=', module_name)
            ], limit=1)
            
            if not module:
                return request.redirect('/web#action=&model=&view_type=&menu_id=')
            
            # Construct Odoo URL based on module type
            base_url = request.httprequest.host_url
            if module_name == 'bcm_governance':
                url = f"{base_url}web#action=bcm_governance.action_governance_brain&model=bcm.governance.brain&view_type=kanban&menu_id="
            elif module_name == 'bcm_risk_management':
                url = f"{base_url}web#action=bcm_risk_management.action_risk_register&model=bcm.risk&view_type=tree&menu_id="
            elif module_name == 'bcm_bia':
                url = f"{base_url}web#action=bcm_bia.action_bia_results&model=bcm.bia.result&view_type=tree&menu_id="
            else:
                # Generic module view
                url = f"{base_url}web#model={module_name}&view_type=form"
            
            return request.redirect(url)
            
        except Exception as e:
            _logger.error(f'Error opening module {module_name}: {str(e)}')
            return request.redirect('/web#action=&model=&view_type=&menu_id=')

    @http.route('/api/bcm/compliance/health-check', type='json', auth='user', methods=['POST'], cors='*')
    def run_health_check(self, **kwargs):
        """Run health check on all BCM modules"""
        try:
            modules = request.env['bcm.module.mapping'].search([])
            
            health_results = []
            for module in modules:
                # Simple health check logic
                # In production, this would ping actual services
                
                health_score = 100
                issues = []
                
                # Check development status
                if module.development_status == 'planning':
                    health_score -= 50
                    issues.append('Module in planning phase')
                elif module.development_status == 'development':
                    health_score -= 20
                    issues.append('Module in development')
                elif module.development_status == 'deprecated':
                    health_score -= 70
                    issues.append('Module deprecated')
                
                # Check compliance contribution
                if module.compliance_contribution < 50:
                    health_score -= 30
                    issues.append('Low compliance contribution')
                
                # Update health status
                if health_score >= 80:
                    new_status = 'healthy'
                elif health_score >= 60:
                    new_status = 'warning'
                elif health_score >= 30:
                    new_status = 'critical'
                else:
                    new_status = 