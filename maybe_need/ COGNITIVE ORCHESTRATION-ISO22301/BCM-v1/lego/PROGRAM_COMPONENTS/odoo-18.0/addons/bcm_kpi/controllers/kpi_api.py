# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import json

class BCMKPIController(http.Controller):
    
    @http.route('/bcm/kpi', type='json', auth='user', methods=['GET', 'POST'], cors='*')
    def get_kpis(self, **kwargs):
        """Get current KPIs for the company"""
        try:
            kpi_calculator = request.env['bcm.kpi.calculator']
            kpis = kpi_calculator.get_current_kpis()
            return {
                'status': 'success',
                'data': kpis
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }
    
    @http.route('/bcm/kpi/calculate', type='json', auth='user', methods=['POST'], cors='*')
    def calculate_kpis(self, period=None, **kwargs):
        """Trigger KPI calculation"""
        try:
            kpi_calculator = request.env['bcm.kpi.calculator']
            
            # Find or create KPI record
            domain = [('company_id', '=', request.env.company.id)]
            if period:
                domain.append(('name', '=', period))
            
            kpi = kpi_calculator.search(domain, limit=1, order='create_date desc')
            if not kpi:
                kpi = kpi_calculator.create({'name': period or 'Current'})
            
            # Calculate KPIs
            kpi.action_calculate_kpis()
            
            return {
                'status': 'success',
                'data': {
                    'bia_coverage': kpi.bia_coverage,
                    'plans_up_to_date': kpi.plans_up_to_date,
                    'capa_on_time': kpi.capa_on_time,
                    'incident_response_time': kpi.incident_response_time,
                    'exercise_completion': kpi.exercise_completion,
                    'training_completion': kpi.training_completion,
                    'period': kpi.name
                }
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }
