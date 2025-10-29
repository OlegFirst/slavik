# -*- coding: utf-8 -*-

from odoo import http, _, fields
from odoo.http import request
from odoo.exceptions import ValidationError, AccessError
import json
import base64
import logging

_logger = logging.getLogger(__name__)

class BcmPortalActions(http.Controller):
    
    def _get_user_client(self):
        """Получить клиента для текущего пользователя"""
        if not request.env.user.has_group('base.group_portal'):
            return None
            
        contact = request.env['bcm.client.contact'].search([
            ('user_id', '=', request.env.user.id)
        ], limit=1)
        
        return contact.client_id if contact else None
    
    @http.route('/portal/bcm/upload-evidence', type='http', auth='user', methods=['POST'], csrf=False)
    def upload_evidence(self, **kwargs):
        """Загрузка evidence к findings или планам"""
        try:
            client = self._get_user_client()
            if not client:
                return self._json_response({'error': 'Access denied'}, status=403)
            
            # Получение параметров
            finding_id = kwargs.get('finding_id')
            plan_id = kwargs.get('plan_id') 
            description = kwargs.get('description', '')
            files = request.httprequest.files.getlist('files')
            
            if not files:
                return self._json_response({'error': 'No files provided'}, status=400)
            
            uploaded_files = []
            
            for file in files:
                if file.filename:
                    # Создать attachment
                    attachment = request.env['ir.attachment'].create({
                        'name': file.filename,
                        'datas': base64.b64encode(file.read()),
                        'res_model': 'bcm.finding' if finding_id else 'bcm.plan',
                        'res_id': int(finding_id) if finding_id else int(plan_id),
                        'description': description,
                        'company_id': client.company_id.id,
                    })
                    
                    uploaded_files.append({
                        'id': attachment.id,
                        'name': attachment.name,
                        'size': attachment.file_size
                    })
            
            # Отправить событие в Event Bus
            self._notify_event_bus('evidence.uploaded', {
                'client_id': client.id,
                'company_id': client.company_id.id,
                'finding_id': finding_id,
                'plan_id': plan_id,
                'files_count': len(uploaded_files)
            })
            
            return self._json_response({
                'success': True,
                'message': _('%d files uploaded successfully') % len(uploaded_files),
                'files': uploaded_files
            })
            
        except Exception as e:
            _logger.error(f"Error uploading evidence: {e}")
            return self._json_response({'error': str(e)}, status=500)
    
    @http.route('/portal/bcm/request-audit', type='http', auth='user', methods=['POST'], csrf=False)
    def request_audit(self, **kwargs):
        """Запрос внешнего аудита"""
        try:
            client = self._get_user_client()
            if not client:
                return self._json_response({'error': 'Access denied'}, status=403)
            
            # Получение параметров
            audit_type = kwargs.get('audit_type', 'internal')
            scope = kwargs.get('scope', '')
            description = kwargs.get('description', '')
            
            # Создать тикет для запроса аудита
            ticket = request.env['helpdesk.ticket'].create({
                'name': f'Audit Request - {client.name}',
                'description': f"Type: {audit_type}\nScope: {scope}\n\n{description}",
                'partner_id': request.env.user.partner_id.id,
                'company_id': client.company_id.id,
                'team_id': request.env.ref('bcm_portal.helpdesk_team_bcm').id,
            })
            
            return self._json_response({
                'success': True,
                'message': _('Audit request submitted successfully'),
                'ticket_id': ticket.id
            })
            
        except Exception as e:
            _logger.error(f"Error requesting audit: {e}")
            return self._json_response({'error': str(e)}, status=500)
    
    @http.route('/portal/bcm/schedule-exercise', type='http', auth='user', methods=['POST'], csrf=False)
    def schedule_exercise(self, **kwargs):
        """Создание учения (draft)"""
        try:
            client = self._get_user_client()
            if not client:
                return self._json_response({'error': 'Access denied'}, status=403)
            
            # Получение параметров
            exercise_name = kwargs.get('name', '')
            exercise_type = kwargs.get('exercise_type', 'tabletop')
            description = kwargs.get('description', '')
            
            if not exercise_name:
                return self._json_response({'error': 'Exercise name is required'}, status=400)
            
            # Создать черновик учения в BCM модуле
            exercise_vals = {
                'name': exercise_name,
                'description': description,
                'exercise_type': exercise_type,
                'status': 'draft',
                'company_id': client.company_id.id,
            }
            
            # Создать запись (будет обработана BCM командой)
            request.env['bcm.exercise'].create(exercise_vals)
            
            return self._json_response({
                'success': True,
                'message': _('Exercise scheduled successfully')
            })
            
        except Exception as e:
            _logger.error(f"Error scheduling exercise: {e}")
            return self._json_response({'error': str(e)}, status=500)
    
    def _notify_event_bus(self, event_type, payload):
        """Отправка уведомления в Event Bus"""
        try:
            import requests
            
            # Получить URL Event Bus из настроек
            BcmConfig = request.env.get('bcm.config')
            if BcmConfig:
                config = BcmConfig.sudo().search([], limit=1)
                if config and config.eventbus_base_url:
                    url = f"{config.eventbus_base_url}/api/events/publish"
                    
                    event_data = {
                        'event_type': event_type,
                        'payload': payload,
                        'timestamp': fields.Datetime.now().isoformat()
                    }
                    
                    response = requests.post(
                        url,
                        json=event_data,
                        headers={'Content-Type': 'application/json'},
                        timeout=5
                    )
                    
                    if response.status_code != 200:
                        _logger.warning(f"Event Bus notification failed: {response.text}")
                        
        except Exception as e:
            _logger.warning(f"Failed to notify Event Bus: {e}")
    
    def _json_response(self, data, status=200):
        """Создать JSON ответ"""
        response = json.dumps(data)
        return request.make_response(
            response,
            status=status,
            headers={'Content-Type': 'application/json'}
        )
