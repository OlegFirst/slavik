# -*- coding: utf-8 -*-

from odoo import http, _
from odoo.http import request
import json
import logging

_logger = logging.getLogger(__name__)

class BcmAiAssistant(http.Controller):
    
    def _get_user_client(self):
        """Получить клиента для текущего пользователя"""
        if not request.env.user.has_group('base.group_portal'):
            return None
            
        contact = request.env['bcm.client.contact'].search([
            ('user_id', '=', request.env.user.id)
        ], limit=1)
        
        return contact.client_id if contact else None
    
    @http.route('/portal/bcm/ai/chat', type='http', auth='user', methods=['POST'], csrf=False)
    def ai_chat(self, **kwargs):
        """AI чат для консультаций"""
        try:
            client = self._get_user_client()
            if not client:
                return self._json_response({'error': 'Access denied'}, status=403)
            
            # Получение сообщения пользователя
            data = json.loads(request.httprequest.data.decode('utf-8'))
            user_message = data.get('message', '').strip()
            
            if not user_message:
                return self._json_response({'error': 'Message is required'}, status=400)
            
            # Получить контекст клиента для ИИ
            context = self._prepare_client_context(client)
            
            # Вызов AI Orchestrator
            ai_response = self._call_ai_orchestrator('/chat/bcm-assistant', {
                'message': user_message,
                'client_id': client.id,
                'company_id': client.company_id.id,
                'context': context,
                'user': request.env.user.name
            })
            
            # Сохранить диалог
            self._save_chat_history(client, user_message, ai_response.get('response', ''))
            
            return self._json_response({
                'success': True,
                'response': ai_response.get('response', 'Sorry, I could not process your request.'),
                'suggestions': ai_response.get('suggestions', []),
                'references': ai_response.get('references', [])
            })
            
        except Exception as e:
            _logger.error(f"Error in AI chat: {e}")
            return self._json_response({'error': str(e)}, status=500)
    
    @http.route('/portal/bcm/ai/recommendations', type='http', auth='user', methods=['GET'])
    def get_recommendations(self, **kwargs):
        """Получить рекомендации от ИИ"""
        try:
            client = self._get_user_client()
            if not client:
                return self._json_response({'error': 'Access denied'}, status=403)
            
            # Тип рекомендаций
            rec_type = kwargs.get('type', 'general')
            
            # Получить контекст клиента
            context = self._prepare_client_context(client)
            
            # Вызов AI Orchestrator для рекомендаций
            ai_response = self._call_ai_orchestrator('/recommendations', {
                'type': rec_type,
                'client_id': client.id,
                'company_id': client.company_id.id,
                'context': context
            })
            
            return self._json_response({
                'success': True,
                'recommendations': ai_response.get('recommendations', []),
                'priority_actions': ai_response.get('priority_actions', []),
                'insights': ai_response.get('insights', {})
            })
            
        except Exception as e:
            _logger.error(f"Error getting recommendations: {e}")
            return self._json_response({'error': str(e)}, status=500)
    
    def _prepare_client_context(self, client):
        """Подготовить контекст клиента для ИИ"""
        try:
            # Собрать ключевую информацию о клиенте
            context = {
                'client_name': client.name,
                'sector': client.sector,
                'region': client.region,
                'onboarding_stage': client.onboarding_stage,
                'data_residency': client.data_residency,
            }
            
            # Добавить данные из vault
            vault_records = request.env['bcm.client.vault'].search([
                ('client_id', '=', client.id),
                ('indexed', '=', True),
                ('active', '=', True)
            ], limit=10)
            
            context['vault_context'] = []
            for vault in vault_records:
                context['vault_context'].append({
                    'type': vault.context_type,
                    'name': vault.name,
                    'description': vault.description[:200] if vault.description else '',
                    'sensitivity': vault.sensitivity_level,
                    'tags': vault.tags
                })
            
            # Добавить текущие метрики
            context['current_metrics'] = {
                'bia_coverage': client.bia_coverage,
                'plans_freshness': client.plans_freshness,
                'open_findings': client.open_findings,
            }
            
            return context
            
        except Exception as e:
            _logger.error(f"Error preparing client context: {e}")
            return {}
    
    def _call_ai_orchestrator(self, endpoint, data):
        """Вызов AI Orchestrator API"""
        try:
            # TODO: Реализация HTTP запроса к AI Orchestrator
            # В production это будет requests.post() к микросервису
            
            # Мок ответы для демо
            mock_responses = {
                '/chat/bcm-assistant': {
                    'response': f"Based on your question about {data.get('message', '')[:50]}... "
                              f"and your current BCM status (sector: {data.get('context', {}).get('sector', 'unknown')}), "
                              f"I recommend focusing on strengthening your business continuity plans. "
                              f"Your current BIA coverage is at {data.get('context', {}).get('current_metrics', {}).get('bia_coverage', 0)}%. "
                              f"Would you like me to help you identify priority areas for improvement?",
                    'suggestions': [
                        'Review current BIA coverage',
                        'Update business continuity plans', 
                        'Schedule recovery testing',
                        'Conduct risk assessment'
                    ],
                    'references': [
                        {'title': 'ISO 22301 Standard', 'url': '#'},
                        {'title': 'BCM Best Practices', 'url': '#'}
                    ]
                },
                '/recommendations': {
                    'recommendations': [
                        {
                            'title': 'Improve BIA Coverage',
                            'description': 'Increase business impact analysis coverage from current level to 90%+',
                            'priority': 'high',
                            'effort': 'medium',
                            'timeline': '2-4 weeks'
                        },
                        {
                            'title': 'Update Recovery Plans', 
                            'description': 'Review and update business continuity plans that are over 12 months old',
                            'priority': 'medium',
                            'effort': 'high',
                            'timeline': '4-8 weeks'
                        },
                        {
                            'title': 'Schedule Tabletop Exercise',
                            'description': 'Conduct tabletop exercise to test current response procedures',
                            'priority': 'medium',
                            'effort': 'low',
                            'timeline': '1-2 weeks'
                        }
                    ],
                    'priority_actions': [
                        'Complete BIA for critical processes',
                        'Address high-priority findings',
                        'Update emergency contacts'
                    ],
                    'insights': {
                        'maturity_score': 75,
                        'improvement_areas': ['Documentation', 'Testing', 'Training'],
                        'strengths': ['Risk Identification', 'Management Support']
                    }
                }
            }
            
            return mock_responses.get(endpoint, {'error': 'Unknown endpoint'})
            
        except Exception as e:
            _logger.error(f"AI Orchestrator call failed: {e}")
            return {'error': str(e)}
    
    def _save_chat_history(self, client, user_message, ai_response):
        """Сохранить историю чата"""
        try:
            request.env['bcm.chat.history'].create({
                'client_id': client.id,
                'user_id': request.env.user.id,
                'user_message': user_message,
                'ai_response': ai_response,
                'session_id': request.session.get('session_id', ''),
                'company_id': client.company_id.id,
            })
        except Exception as e:
            _logger.warning(f"Failed to save chat history: {e}")
    
    def _json_response(self, data, status=200):
        """Создать JSON ответ"""
        response = json.dumps(data, ensure_ascii=False)
        return request.make_response(
            response,
            status=status,
            headers={'Content-Type': 'application/json; charset=utf-8'}
        )
