# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import json


class BCMHealthController(http.Controller):
    
    @http.route('/web/health', type='json', auth='none', methods=['GET'], cors='*')
    def health_check(self, **kwargs):
        """Health check endpoint for Odoo"""
        try:
            # Basic health check - check if database is accessible
            request.env.cr.execute("SELECT 1")
            
            return {
                'status': 'ok',
                'service': 'odoo',
                'timestamp': request.env['ir.http']._get_current_timestamp(),
                'database': request.env.cr.dbname,
                'version': '18.0'
            }
        except Exception as e:
            return {
                'status': 'error',
                'service': 'odoo',
                'error': str(e),
                'timestamp': request.env['ir.http']._get_current_timestamp()
            }
    
    @http.route('/web/health', type='http', auth='none', methods=['GET'], cors='*')  
    def health_check_http(self, **kwargs):
        """HTTP health check endpoint for Odoo"""
        try:
            # Basic health check - check if database is accessible
            request.env.cr.execute("SELECT 1")
            
            data = {
                'status': 'ok',
                'service': 'odoo',
                'timestamp': request.env['ir.http']._get_current_timestamp(),
                'database': request.env.cr.dbname,
                'version': '18.0'
            }
            
            return request.make_json_response(data)
        except Exception as e:
            data = {
                'status': 'error',
                'service': 'odoo',
                'error': str(e),
                'timestamp': request.env['ir.http']._get_current_timestamp()
            }
            
            return request.make_json_response(data, status=500)