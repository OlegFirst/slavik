# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import requests
import json
import logging
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)

class DigitalTwinBridge(models.TransientModel):
    _name = 'bcm.digital.twin.bridge'
    _description = 'Digital Twin API Bridge'

    # Configuration
    service_url = fields.Char(
        string='Digital Twin Service URL',
        default='http://localhost:3000',
        help="Base URL for the Digital Twin Node.js service"
    )

    timeout = fields.Integer(
        string='Request Timeout',
        default=30,
        help="HTTP request timeout in seconds"
    )

    retry_count = fields.Integer(
        string='Retry Count',
        default=3,
        help="Number of retry attempts for failed requests"
    )

    @api.model
    def get_service_config(self):
        """Get service configuration from system parameters"""
        params = self.env['ir.config_parameter'].sudo()

        return {
            'service_url': params.get_param(
                'digital_twin.service_url',
                'http://localhost:3000'
            ),
            'timeout': int(params.get_param(
                'digital_twin.timeout',
                '30'
            )),
            'retry_count': int(params.get_param(
                'digital_twin.retry_count',
                '3'
            )),
            'api_key': params.get_param(
                'digital_twin.api_key',
                ''
            )
        }

    def _make_request(self, method, endpoint, data=None, params=None):
        """Make HTTP request to Digital Twin service with retry logic"""
        config = self.get_service_config()
        url = f"{config['service_url']}{endpoint}"

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        # Add API key if configured
        if config.get('api_key'):
            headers['Authorization'] = f"Bearer {config['api_key']}"

        # Prepare request data
        request_data = {
            'method': method.upper(),
            'url': url,
            'headers': headers,
            'timeout': config['timeout']
        }

        if data:
            request_data['json'] = data
        if params:
            request_data['params'] = params

        # Retry logic
        last_exception = None
        for attempt in range(config['retry_count']):
            try:
                _logger.info(f"Digital Twin API call attempt {attempt + 1}: {method} {url}")

                response = requests.request(**request_data)
                response.raise_for_status()

                result = response.json() if response.content else {}

                _logger.info(f"Digital Twin API call successful: {response.status_code}")
                return result

            except requests.exceptions.ConnectionError as e:
                last_exception = e
                _logger.warning(f"Connection error on attempt {attempt + 1}: {str(e)}")
                if attempt < config['retry_count'] - 1:
                    continue

            except requests.exceptions.Timeout as e:
                last_exception = e
                _logger.warning(f"Timeout error on attempt {attempt + 1}: {str(e)}")
                if attempt < config['retry_count'] - 1:
                    continue

            except requests.exceptions.HTTPError as e:
                last_exception = e
                _logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
                break  # Don't retry on HTTP errors

            except Exception as e:
                last_exception = e
                _logger.error(f"Unexpected error on attempt {attempt + 1}: {str(e)}")
                break

        # All attempts failed
        error_msg = f"Digital Twin service request failed after {config['retry_count']} attempts"
        if last_exception:
            error_msg += f": {str(last_exception)}"

        _logger.error(error_msg)
        raise UserError(_(error_msg))

    def create_digital_twin(self, organization_data):
        """Create Digital Twin for organization"""
        endpoint = '/api/digital-twins'

        # Transform data for Digital Twin service
        twin_data = {
            'organizationData': {
                'organizationId': organization_data['organization_id'],
                'name': organization_data['name'],
                'description': organization_data.get('description', ''),
                'domain': organization_data['domain_type'],
                'industry': organization_data.get('industry_sector', ''),
                'bcmIntegration': organization_data.get('bcm_data', {})
            },
            'configuration': organization_data.get('config', {})
        }

        try:
            result = self._make_request('POST', endpoint, twin_data)

            # Process successful response
            return {
                'twin_id': result.get('twinId'),
                'config': result.get('configuration', {}),
                'status': result.get('status', 'created'),
                'message': result.get('message', 'Digital Twin created successfully')
            }

        except Exception as e:
            _logger.error(f"Failed to create Digital Twin: {str(e)}")
            raise

    def sync_organization_data(self, organization_id):
        """Sync organization data with Digital Twin service"""
        organization = self.env['bcm.digital.twin.organization'].browse(organization_id)

        if not organization.exists():
            raise UserError(_("Organization not found"))

        # Prepare data for sync
        sync_data = organization._prepare_twin_data()

        endpoint = f'/api/digital-twins/{organization_id}/sync'

        try:
            result = self._make_request('PUT', endpoint, sync_data)

            # Update organization with sync results
            if result.get('updated_config'):
                organization.twin_config = json.dumps(result['updated_config'])

            if result.get('health_score'):
                organization.twin_health_score = result['health_score']

            organization.message_post(
                body=_("Data synchronized with Digital Twin service"),
                message_type='notification'
            )

            return result

        except Exception as e:
            _logger.error(f"Failed to sync organization data: {str(e)}")
            raise

    def execute_simulation(self, simulation_record):
        """Execute simulation through Digital Twin service"""
        endpoint = '/api/simulations'

        # Prepare simulation data
        sim_data = {
            'organizationId': simulation_record.organization_id.id,
            'scenarioType': simulation_record.scenario_type,
            'parameters': json.loads(simulation_record.parameters or '{}'),
            'bcmContext': self._get_bcm_context_for_simulation(simulation_record)
        }

        try:
            result = self._make_request('POST', endpoint, sim_data)

            # Process simulation results
            processed_results = self._process_simulation_results(result)

            # Update simulation record
            simulation_record.write({
                'results': json.dumps(processed_results),
                'state': 'completed',
                'completion_date': fields.Datetime.now()
            })

            return processed_results

        except Exception as e:
            # Mark simulation as failed
            simulation_record.write({
                'state': 'failed',
                'error_message': str(e)
            })
            _logger.error(f"Simulation execution failed: {str(e)}")
            raise

    def get_organization_metrics(self, organization_id):
        """Get real-time metrics for organization"""
        endpoint = f'/api/digital-twins/{organization_id}/metrics'

        try:
            result = self._make_request('GET', endpoint)
            return result.get('metrics', {})

        except Exception as e:
            _logger.error(f"Failed to get organization metrics: {str(e)}")
            return {}

    def get_predictions(self, organization_id, prediction_type=None):
        """Get AI predictions for organization"""
        endpoint = f'/api/digital-twins/{organization_id}/predictions'

        params = {}
        if prediction_type:
            params['type'] = prediction_type

        try:
            result = self._make_request('GET', endpoint, params=params)
            return result.get('predictions', [])

        except Exception as e:
            _logger.error(f"Failed to get predictions: {str(e)}")
            return []

    def test_connection(self):
        """Test connection to Digital Twin service"""
        endpoint = '/api/health'

        try:
            result = self._make_request('GET', endpoint)

            return {
                'success': True,
                'status': result.get('status', 'unknown'),
                'version': result.get('version', 'unknown'),
                'uptime': result.get('uptime', 0),
                'message': 'Connection successful'
            }

        except Exception as e:
            return {
                'success': False,
                'message': str(e)
            }

    def _get_bcm_context_for_simulation(self, simulation_record):
        """Get BCM context data for simulation"""
        context_data = {}

        # Get organization BCM data
        org = simulation_record.organization_id
        if org.bcm_client_id:
            context_data['client'] = {
                'name': org.bcm_client_id.name,
                'type': getattr(org.bcm_client_id, 'client_type', ''),
                'industry': getattr(org.bcm_client_id, 'industry', ''),
            }

        if org.bcm_context_id:
            context_data['context'] = {
                'business_functions': getattr(org.bcm_context_id, 'business_functions', {}),
                'stakeholders': getattr(org.bcm_context_id, 'stakeholders', {}),
                'dependencies': getattr(org.bcm_context_id, 'dependencies', {}),
            }

        # Get related BCM records
        if simulation_record.related_incident:
            context_data['incident'] = {
                'type': simulation_record.related_incident.incident_type,
                'severity': simulation_record.related_incident.severity,
                'impact': simulation_record.related_incident.impact,
            }

        if simulation_record.related_bia:
            context_data['bia'] = {
                'critical_functions': getattr(simulation_record.related_bia, 'critical_functions', []),
                'recovery_objectives': getattr(simulation_record.related_bia, 'recovery_objectives', {}),
            }

        return context_data

    def _process_simulation_results(self, raw_results):
        """Process and structure simulation results"""
        processed = {
            'simulation_id': raw_results.get('simulationId'),
            'status': raw_results.get('status', 'completed'),
            'execution_time': raw_results.get('executionTime', 0),
            'timestamp': datetime.now().isoformat(),
            'results': {}
        }

        # Process different result types
        if 'financial' in raw_results:
            processed['results']['financial'] = {
                'projected_savings': raw_results['financial'].get('savings', 0),
                'cost_impact': raw_results['financial'].get('cost_impact', 0),
                'roi_estimate': raw_results['financial'].get('roi', 0)
            }

        if 'operational' in raw_results:
            processed['results']['operational'] = {
                'efficiency_gain': raw_results['operational'].get('efficiency', 0),
                'process_improvements': raw_results['operational'].get('improvements', []),
                'resource_optimization': raw_results['operational'].get('resources', {})
            }

        if 'risk' in raw_results:
            processed['results']['risk'] = {
                'risk_reduction': raw_results['risk'].get('reduction', 0),
                'new_risks': raw_results['risk'].get('new_risks', []),
                'mitigation_strategies': raw_results['risk'].get('mitigations', [])
            }

        if 'predictions' in raw_results:
            processed['results']['predictions'] = raw_results['predictions']

        # Add recommendations
        if 'recommendations' in raw_results:
            processed['recommendations'] = raw_results['recommendations']

        return processed

    @api.model
    def setup_service_parameters(self, service_url, api_key=None, timeout=30):
        """Setup Digital Twin service parameters"""
        params = self.env['ir.config_parameter'].sudo()

        params.set_param('digital_twin.service_url', service_url)
        params.set_param('digital_twin.timeout', str(timeout))

        if api_key:
            params.set_param('digital_twin.api_key', api_key)

        # Test connection
        test_result = self.test_connection()

        if not test_result['success']:
            raise UserError(_(
                "Failed to connect to Digital Twin service: %s"
            ) % test_result['message'])

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _("Success"),
                'message': _("Digital Twin service configured successfully"),
                'type': 'success'
            }
        }