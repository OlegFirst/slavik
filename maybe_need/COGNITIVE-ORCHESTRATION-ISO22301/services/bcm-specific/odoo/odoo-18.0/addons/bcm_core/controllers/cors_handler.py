# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import json
import logging

_logger = logging.getLogger(__name__)

class CORSController(http.Controller):
    """CORS handler for BCM API endpoints"""

    def _setup_cors_headers(self, origin=None):
        """Setup CORS headers for cross-origin requests"""
        headers = {
            'Access-Control-Allow-Origin': origin or 'http://localhost:5173',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With, X-Request-ID, X-Client-ID',
            'Access-Control-Allow-Credentials': 'true',
            'Access-Control-Max-Age': '86400'
        }
        return headers

    @http.route(['/web/health'], type='http', auth='none', methods=['GET', 'OPTIONS'], cors='*')
    def health_check_cors(self, **kwargs):
        """Health check with CORS support"""
        if request.httprequest.method == 'OPTIONS':
            # Handle preflight request
            response = request.make_response('', headers=self._setup_cors_headers())
            return response

        # Regular health check
        try:
            response_data = {'status': 'pass', 'service': 'odoo', 'timestamp': str(request.env.cr.now())}
            response = request.make_response(
                json.dumps(response_data),
                headers={
                    'Content-Type': 'application/json',
                    **self._setup_cors_headers()
                }
            )
            return response
        except Exception as e:
            _logger.error(f"Health check error: {e}")
            response = request.make_response(
                json.dumps({'status': 'fail', 'error': str(e)}),
                headers={
                    'Content-Type': 'application/json',
                    **self._setup_cors_headers()
                }
            )
            return response

    @http.route(['/api/<path:path>'], type='http', auth='none', methods=['OPTIONS'], cors='*')
    def api_options_handler(self, path=None, **kwargs):
        """Handle OPTIONS requests for all API endpoints"""
        return request.make_response('', headers=self._setup_cors_headers())

    @http.route(['/web/session/<path:path>'], type='http', auth='none', methods=['OPTIONS'], cors='*')
    def session_options_handler(self, path=None, **kwargs):
        """Handle OPTIONS requests for session endpoints"""
        return request.make_response('', headers=self._setup_cors_headers())