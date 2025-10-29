# -*- coding: utf-8 -*-

from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.exceptions import AccessError
import logging

_logger = logging.getLogger(__name__)

class BcmPortal(CustomerPortal):
    
    def _prepare_home_portal_values(self, counters):
        """Добавить BCM данные в портал"""
        values = super()._prepare_home_portal_values(counters)
        
        if request.env.user.has_group('base.group_portal'):
            try:
                # Получить клиента текущего пользователя
                client = self._get_user_client()
                if client:
                    # Подсчеты для портала
                    if 'bcm_processes' in counters:
                        values['bcm_process_count'] = request.env['bcm.process'].search_count([
                            ('company_id', '=', client.company_id.id)
                        ])
                    
                    if 'bcm_plans' in counters:
                        values['bcm_plan_count'] = request.env['bcm.plan'].search_count([
                            ('company_id', '=', client.company_id.id)
                        ])
                    
                    if 'bcm_incidents' in counters:
                        values['bcm_incident_count'] = request.env['bcm.incident'].search_count([
                            ('company_id', '=', client.company_id.id),
                            ('status', 'not in', ['closed', 'resolved'])
                        ])
                    
                    if 'bcm_exercises' in counters:
                        values['bcm_exercise_count'] = request.env['bcm.exercise'].search_count([
                            ('company_id', '=', client.company_id.id)
                        ])
                    
                    if 'bcm_findings' in counters:
                        values['bcm_finding_count'] = request.env['bcm.finding'].search_count([
                            ('company_id', '=', client.company_id.id),
                            ('status', 'not in', ['closed'])
                        ])
                        
            except Exception as e:
                _logger.warning(f"Error preparing BCM portal values: {e}")
                
        return values
    
    def _get_user_client(self):
        """Получить клиента для текущего пользователя"""
        if not request.env.user.has_group('base.group_portal'):
            return None
            
        # Найти контакт клиента для текущего пользователя
        contact = request.env['bcm.client.contact'].search([
            ('user_id', '=', request.env.user.id)
        ], limit=1)
        
        return contact.client_id if contact else None
    
    @http.route('/my/bcm', type='http', auth='user', website=True)
    def portal_bcm_dashboard(self, **kwargs):
        """Главная страница BCM портала"""
        client = self._get_user_client()
        
        if not client:
            return request.render('bcm_portal.no_client_access', {
                'page_name': 'BCM Portal',
                'error_message': _('You do not have access to any BCM client data.')
            })
        
        # Сбор данных для дашборда
        dashboard_data = self._prepare_dashboard_data(client)
        
        values = {
            'page_name': 'bcm_dashboard',
            'client': client,
            'dashboard_data': dashboard_data,
        }
        
        return request.render('bcm_portal.bcm_dashboard', values)
    
    def _prepare_dashboard_data(self, client):
        """Подготовка данных для дашборда"""
        try:
            # BIA Coverage
            total_processes = request.env['bcm.process'].search_count([
                ('company_id', '=', client.company_id.id)
            ])
            analyzed_processes = request.env['bcm.bia.result'].search_count([
                ('company_id', '=', client.company_id.id)
            ])
            bia_coverage = (analyzed_processes / total_processes * 100) if total_processes > 0 else 0
            
            # Plans Freshness
            plans = request.env['bcm.plan'].search([
                ('company_id', '=', client.company_id.id),
                ('status', '=', 'active')
            ])
            avg_plan_age = 0
            if plans:
                from datetime import datetime
                ages = [(datetime.now().date() - plan.last_updated.date()).days 
                       for plan in plans if plan.last_updated]
                avg_plan_age = sum(ages) / len(ages) if ages else 0
            
            # Open Findings
            open_findings = request.env['bcm.finding'].search_count([
                ('company_id', '=', client.company_id.id),
                ('status', 'not in', ['closed', 'resolved'])
            ])
            
            # Recent Incidents
            recent_incidents = request.env['bcm.incident'].search([
                ('company_id', '=', client.company_id.id)
            ], limit=5, order='create_date desc')
            
            # Upcoming Exercises
            upcoming_exercises = request.env['bcm.exercise'].search([
                ('company_id', '=', client.company_id.id),
                ('status', 'in', ['planned', 'scheduled']),
                ('scheduled_date', '>', request.env.cr.now())
            ], limit=5, order='scheduled_date asc')
            
            # Training Status
            training_completion = request.env['bcm.training.status'].search_count([
                ('company_id', '=', client.company_id.id),
                ('status', '=', 'completed')
            ])
            
            total_training = request.env['bcm.training.status'].search_count([
                ('company_id', '=', client.company_id.id)
            ])
            
            training_percentage = (training_completion / total_training * 100) if total_training > 0 else 0
            
            return {
                'bia_coverage': round(bia_coverage, 1),
                'avg_plan_age': round(avg_plan_age),
                'open_findings': open_findings,
                'recent_incidents': recent_incidents,
                'upcoming_exercises': upcoming_exercises,
                'training_percentage': round(training_percentage, 1),
                'total_processes': total_processes,
                'analyzed_processes': analyzed_processes,
                'active_plans': len(plans),
            }
            
        except Exception as e:
            _logger.error(f"Error preparing dashboard data: {e}")
            return {}
    
    @http.route('/my/bcm/bia', type='http', auth='user', website=True)
    def portal_bcm_bia(self, **kwargs):
        """Страница BIA в портале"""
        client = self._get_user_client()
        if not client:
            return self._redirect_no_access()
        
        # Получить BIA данные
        bia_surveys = request.env['bcm.bia.survey'].search([
            ('company_id', '=', client.company_id.id)
        ])
        
        bia_results = request.env['bcm.bia.result'].search([
            ('company_id', '=', client.company_id.id)
        ])
        
        values = {
            'page_name': 'bia',
            'client': client,
            'bia_surveys': bia_surveys,
            'bia_results': bia_results,
        }
        
        return request.render('bcm_portal.bcm_bia_portal', values)
    
    @http.route('/my/bcm/plans', type='http', auth='user', website=True)
    def portal_bcm_plans(self, **kwargs):
        """Страница планов в портале"""
        client = self._get_user_client()
        if not client:
            return self._redirect_no_access()
        
        # Получить планы
        plans = request.env['bcm.plan'].search([
            ('company_id', '=', client.company_id.id)
        ])
        
        values = {
            'page_name': 'plans',
            'client': client,
            'plans': plans,
        }
        
        return request.render('bcm_portal.bcm_plans_portal', values)
    
    @http.route('/my/bcm/incidents', type='http', auth='user', website=True)
    def portal_bcm_incidents(self, **kwargs):
        """Страница инцидентов в портале"""
        client = self._get_user_client()
        if not client:
            return self._redirect_no_access()
        
        # Получить инциденты
        incidents = request.env['bcm.incident'].search([
            ('company_id', '=', client.company_id.id)
        ])
        
        values = {
            'page_name': 'incidents', 
            'client': client,
            'incidents': incidents,
        }
        
        return request.render('bcm_portal.bcm_incidents_portal', values)
    
    @http.route('/my/bcm/exercises', type='http', auth='user', website=True)
    def portal_bcm_exercises(self, **kwargs):
        """Страница учений в портале"""
        client = self._get_user_client()
        if not client:
            return self._redirect_no_access()
        
        # Получить учения
        exercises = request.env['bcm.exercise'].search([
            ('company_id', '=', client.company_id.id)
        ])
        
        values = {
            'page_name': 'exercises',
            'client': client,
            'exercises': exercises,
        }
        
        return request.render('bcm_portal.bcm_exercises_portal', values)
    
    @http.route('/my/bcm/audit', type='http', auth='user', website=True)
    def portal_bcm_audit(self, **kwargs):
        """Страница аудитов в портале"""
        client = self._get_user_client()
        if not client:
            return self._redirect_no_access()
        
        # Получить аудиты и findings
        audits = request.env['bcm.audit'].search([
            ('company_id', '=', client.company_id.id)
        ])
        
        findings = request.env['bcm.finding'].search([
            ('company_id', '=', client.company_id.id)
        ])
        
        values = {
            'page_name': 'audit',
            'client': client,
            'audits': audits,
            'findings': findings,
        }
        
        return request.render('bcm_portal.bcm_audit_portal', values)
    
    @http.route('/my/bcm/training', type='http', auth='user', website=True)
    def portal_bcm_training(self, **kwargs):
        """Страница обучения в портале"""
        client = self._get_user_client()
        if not client:
            return self._redirect_no_access()
        
        # Получить обучение
        trainings = request.env['bcm.training'].search([
            ('company_id', '=', client.company_id.id)
        ])
        
        training_status = request.env['bcm.training.status'].search([
            ('company_id', '=', client.company_id.id),
            ('user_id', '=', request.env.user.id)
        ])
        
        values = {
            'page_name': 'training',
            'client': client,
            'trainings': trainings,
            'training_status': training_status,
        }
        
        return request.render('bcm_portal.bcm_training_portal', values)
    
    def _redirect_no_access(self):
        """Перенаправление при отсутствии доступа"""
        return request.render('bcm_portal.no_client_access', {
            'error_message': _('Access denied: You do not have permission to view this BCM data.')
        })
