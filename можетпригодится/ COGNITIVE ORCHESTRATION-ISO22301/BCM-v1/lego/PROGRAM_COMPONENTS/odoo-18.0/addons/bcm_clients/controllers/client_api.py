# -*- coding: utf-8 -*-

from odoo import http, _
from odoo.http import request
from odoo.exceptions import ValidationError, AccessError
import json
import logging

_logger = logging.getLogger(__name__)

class BcmClientApiController(http.Controller):
    
    @http.route('/api/clients/<int:client_id>/reindex', type='http', auth='user', methods=['POST'], csrf=False)
    def reindex_client(self, client_id, **kwargs):
        """API endpoint для переиндексации контекста клиента"""
        try:
            client = request.env['bcm.client'].browse(client_id)
            
            if not client.exists():
                return request.make_response(
                    json.dumps({'error': 'Client not found'}),
                    status=404,
                    headers={'Content-Type': 'application/json'}
                )
            
            # Проверка прав доступа
            client.check_access_rights('write')
            client.check_access_rule('write')
            
            # Переиндексация
            client.action_reindex_context()
            
            return request.make_response(
                json.dumps({
                    'success': True,
                    'message': 'Client context reindexed successfully',
                    'client_id': client_id
                }),
                headers={'Content-Type': 'application/json'}
            )
            
        except AccessError:
            return request.make_response(
                json.dumps({'error': 'Access denied'}),
                status=403,
                headers={'Content-Type': 'application/json'}
            )
        except Exception as e:
            _logger.error(f"Error reindexing client {client_id}: {e}")
            return request.make_response(
                json.dumps({'error': str(e)}),
                status=500,
                headers={'Content-Type': 'application/json'}
            )

    @http.route('/api/clients/<int:client_id>/metrics', type='http', auth='user', methods=['GET'])
    def get_client_metrics(self, client_id, **kwargs):
        """API endpoint для получения метрик клиента"""
        try:
            client = request.env['bcm.client'].browse(client_id)
            
            if not client.exists():
                return request.make_response(
                    json.dumps({'error': 'Client not found'}),
                    status=404,
                    headers={'Content-Type': 'application/json'}
                )
            
            # Проверка прав доступа
            client.check_access_rights('read')
            client.check_access_rule('read')
            
            # Сбор метрик
            metrics = {
                'client_id': client.id,
                'name': client.name,
                'onboarding_stage': client.onboarding_stage,
                'status': client.status,
                'bia_coverage': client.bia_coverage,
                'plans_freshness': client.plans_freshness,
                'open_findings': client.open_findings,
                'contact_count': client.contact_count,
                'vault_count': client.vault_count,
                'sector': client.sector,
                'region': client.region
            }
            
            return request.make_response(
                json.dumps(metrics),
                headers={'Content-Type': 'application/json'}
            )
            
        except AccessError:
            return request.make_response(
                json.dumps({'error': 'Access denied'}),
                status=403,
                headers={'Content-Type': 'application/json'}
            )
        except Exception as e:
            _logger.error(f"Error getting metrics for client {client_id}: {e}")
            return request.make_response(
                json.dumps({'error': str(e)}),
                status=500,
                headers={'Content-Type': 'application/json'}
            )

    @http.route('/api/clients/<int:client_id>/vault/search', type='http', auth='user', methods=['POST'], csrf=False)
    def search_client_vault(self, client_id, **kwargs):
        """API endpoint для поиска в контексте клиента"""
        try:
            client = request.env['bcm.client'].browse(client_id)
            
            if not client.exists():
                return request.make_response(
                    json.dumps({'error': 'Client not found'}),
                    status=404,
                    headers={'Content-Type': 'application/json'}
                )
            
            # Получение параметров поиска
            data = json.loads(request.httprequest.data.decode('utf-8'))
            query = data.get('query', '')
            context_type = data.get('context_type')
            limit = data.get('limit', 10)
            
            if not query:
                return request.make_response(
                    json.dumps({'error': 'Query parameter is required'}),
                    status=400,
                    headers={'Content-Type': 'application/json'}
                )
            
            # Поиск в vault
            domain = [('client_id', '=', client_id), ('active', '=', True)]
            if context_type:
                domain.append(('context_type', '=', context_type))
            
            # Текстовый поиск
            domain.extend([
                '|', '|',
                ('name', 'ilike', query),
                ('description', 'ilike', query),
                ('tags', 'ilike', query)
            ])
            
            vault_records = request.env['bcm.client.vault'].search(domain, limit=limit)
            
            # Формирование результатов
            results = []
            for record in vault_records:
                results.append({
                    'id': record.id,
                    'name': record.name,
                    'description': record.description,
                    'context_type': record.context_type,
                    'sensitivity_level': record.sensitivity_level,
                    'tags': record.tags,
                    'indexed': record.indexed,
                    'updated_at': record.updated_at.isoformat() if record.updated_at else None
                })
            
            return request.make_response(
                json.dumps({
                    'query': query,
                    'total': len(results),
                    'results': results
                }),
                headers={'Content-Type': 'application/json'}
            )
            
        except AccessError:
            return request.make_response(
                json.dumps({'error': 'Access denied'}),
                status=403,
                headers={'Content-Type': 'application/json'}
            )
        except Exception as e:
            _logger.error(f"Error searching vault for client {client_id}: {e}")
            return request.make_response(
                json.dumps({'error': str(e)}),
                status=500,
                headers={'Content-Type': 'application/json'}
            )

    @http.route('/api/clients/webhook', type='http', auth='none', methods=['POST'], csrf=False)
    def client_webhook(self, **kwargs):
        """Webhook endpoint для получения событий от внешних систем"""
        try:
            # Проверка API ключа
            api_key = request.httprequest.headers.get('Authorization', '').replace('Bearer ', '')
            if not api_key:
                return request.make_response(
                    json.dumps({'error': 'API key required'}),
                    status=401,
                    headers={'Content-Type': 'application/json'}
                )
            
            # Поиск и проверка API ключа
            appkey = request.env['bcm.client.appkey'].sudo().search([
                ('token_hash', '=', request.env['bcm.client.appkey']._hash_token(api_key)),
                ('revoked', '=', False),
                ('valid_until', '>', fields.Datetime.now())
            ], limit=1)
            
            if not appkey:
                return request.make_response(
                    json.dumps({'error': 'Invalid or expired API key'}),
                    status=401,
                    headers={'Content-Type': 'application/json'}
                )
            
            # Записать использование ключа
            client_ip = request.httprequest.environ.get('REMOTE_ADDR')
            appkey.record_usage(client_ip)
            
            # Проверка rate limit
            if not appkey.check_rate_limit():
                return request.make_response(
                    json.dumps({'error': 'Rate limit exceeded'}),
                    status=429,
                    headers={'Content-Type': 'application/json'}
                )
            
            # Обработка webhook данных
            data = json.loads(request.httprequest.data.decode('utf-8'))
            event_type = data.get('event_type')
            client_id = data.get('client_id', appkey.client_id.id)
            payload = data.get('payload', {})
            
            _logger.info(f"Webhook received: {event_type} for client {client_id}")
            
            # TODO: Обработка различных типов событий
            # - external_data_updated
            # - integration_sync
            # - context_changed
            
            return request.make_response(
                json.dumps({
                    'success': True,
                    'event_type': event_type,
                    'processed_at': fields.Datetime.now().isoformat()
                }),
                headers={'Content-Type': 'application/json'}
            )
            
        except Exception as e:
            _logger.error(f"Webhook error: {e}")
            return request.make_response(
                json.dumps({'error': str(e)}),
                status=500,
                headers={'Content-Type': 'application/json'}
            )
