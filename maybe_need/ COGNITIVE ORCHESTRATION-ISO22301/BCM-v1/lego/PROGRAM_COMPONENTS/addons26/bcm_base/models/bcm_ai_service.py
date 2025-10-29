# -*- coding: utf-8 -*-

import json
import requests
import logging
from datetime import datetime, timedelta

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

class BCMServiceConfig(models.Model):
    """Конфигурация AI сервисов BCM"""
    _name = 'bcm.service.config'
    _description = 'BCM AI Services Configuration'
    
    name = fields.Char('Service Name', required=True)
    service_type = fields.Selection([
        ('ai_orchestrator', 'AI Orchestrator'),
        ('bia_engine', 'BIA Engine'),
        ('document_processor', 'Document Processor'),
        ('compliance_checker', 'Compliance Checker'),
    ], string='Service Type', required=True)
    
    base_url = fields.Char('Base URL', required=True, default='http://localhost')
    port = fields.Integer('Port', required=True, default=8000)
    api_key = fields.Char('API Key', groups="base.group_system")
    timeout = fields.Integer('Timeout (seconds)', default=30)
    
    active = fields.Boolean('Active', default=True)
    last_health_check = fields.Datetime('Last Health Check')
    health_status = fields.Selection([
        ('healthy', 'Healthy'),
        ('unhealthy', 'Unhealthy'), 
        ('unknown', 'Unknown'),
    ], string='Health Status', default='unknown')
    
    @api.model
    def create_default_configs(self):
        """Создает дефолтные конфигурации сервисов"""
        default_configs = [
            {
                'name': 'AI Orchestrator',
                'service_type': 'ai_orchestrator',
                'base_url': 'http://localhost',
                'port': 8000,
            },
            {
                'name': 'BIA Engine',
                'service_type': 'bia_engine', 
                'base_url': 'http://localhost',
                'port': 8082,
            },
            {
                'name': 'Document Processor',
                'service_type': 'document_processor',
                'base_url': 'http://localhost',
                'port': 8083,
            },
            {
                'name': 'Compliance Checker',
                'service_type': 'compliance_checker',
                'base_url': 'http://localhost',
                'port': 8084,
            },
        ]
        
        for config in default_configs:
            existing = self.search([('service_type', '=', config['service_type'])])
            if not existing:
                self.create(config)
    
    @property 
    def service_url(self):
        """Получает полный URL сервиса"""
        return f"{self.base_url}:{self.port}"
    
    def check_health(self):
        """Проверяет здоровье сервиса"""
        try:
            response = requests.get(
                f"{self.service_url}/health",
                timeout=self.timeout
            )
            if response.status_code == 200:
                self.health_status = 'healthy'
                self.last_health_check = datetime.now()
                return True
            else:
                self.health_status = 'unhealthy'
                return False
                
        except Exception as e:
            _logger.error(f"Health check failed for {self.name}: {e}")
            self.health_status = 'unhealthy'
            return False

class BCMAIService(models.Model):
    """Интеграционный сервис для работы с AI микросервисами"""
    _name = 'bcm.ai.service'
    _description = 'BCM AI Integration Service'
    
    @api.model
    def check_services_health(self):
        """Проверяет здоровье всех активных сервисов"""
        configs = self.env['bcm.service.config'].search([('active', '=', True)])
        results = {}
        
        for config in configs:
            results[config.service_type] = config.check_health()
        
        return results
    
    @api.model
    def get_service_config(self, service_type):
        """Получает конфигурацию сервиса по типу"""
        config = self.env['bcm.service.config'].search([
            ('service_type', '=', service_type),
            ('active', '=', True)
        ], limit=1)
        
        if not config:
            raise UserError(_('Service configuration for %s not found or inactive') % service_type)
        
        return config
    
    def _make_api_request(self, service_type, endpoint, method='GET', data=None, files=None):
        """Выполняет API запрос к микросервису"""
        config = self.get_service_config(service_type)
        
        url = f"{config.service_url}{endpoint}"
        headers = {}
        
        if config.api_key:
            headers['Authorization'] = f'Bearer {config.api_key}'
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=config.timeout)
            elif method == 'POST':
                if files:
                    # Для загрузки файлов не устанавливаем Content-Type
                    response = requests.post(url, headers=headers, data=data, files=files, timeout=config.timeout)
                else:
                    headers['Content-Type'] = 'application/json'
                    json_data = json.dumps(data) if data else None
                    response = requests.post(url, headers=headers, data=json_data, timeout=config.timeout)
            elif method == 'PUT':
                headers['Content-Type'] = 'application/json'
                json_data = json.dumps(data) if data else None
                response = requests.put(url, headers=headers, data=json_data, timeout=config.timeout)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=config.timeout)
            
            response.raise_for_status()
            return response.json()
            
        except requests.RequestException as e:
            _logger.error(f"API request failed: {e}")
            raise UserError(_('Failed to communicate with %s service: %s') % (service_type, str(e)))
    
    # AI Orchestrator методы
    def analyze_process_risk(self, process_data):
        """Анализ рисков процесса через AI Orchestrator"""
        return self._make_api_request(
            'ai_orchestrator',
            '/analyze/process-risk',
            method='POST',
            data=process_data
        )
    
    def classify_incident(self, incident_data):
        """Классификация инцидента через AI Orchestrator"""
        return self._make_api_request(
            'ai_orchestrator', 
            '/analyze/incident',
            method='POST',
            data=incident_data
        )
    
    def process_nlp_query(self, query_data):
        """Обработка NLP запроса через AI Orchestrator"""
        return self._make_api_request(
            'ai_orchestrator',
            '/nlp/query',
            method='POST',
            data=query_data
        )
    
    # BIA Engine методы
    def compute_bia_analysis(self, bia_request_data):
        """Комплексный BIA анализ через BIA Engine"""
        return self._make_api_request(
            'bia_engine',
            '/compute',
            method='POST',
            data=bia_request_data
        )
    
    def optimize_single_process(self, process_data, risk_tolerance=0.05):
        """Оптимизация отдельного процесса через BIA Engine"""
        return self._make_api_request(
            'bia_engine',
            f'/optimize/single-process?risk_tolerance={risk_tolerance}',
            method='POST', 
            data=process_data
        )
    
    # Document Processor методы
    def upload_document(self, file_data, document_type_hint=None):
        """Загрузка и обработка документа через Document Processor"""
        files = {'file': file_data}
        form_data = {}
        
        if document_type_hint:
            form_data['document_type_hint'] = document_type_hint
        
        return self._make_api_request(
            'document_processor',
            '/upload',
            method='POST',
            data=form_data,
            files=files
        )
    
    def search_documents(self, query, document_type=None, compliance_level=None):
        """Поиск документов через Document Processor"""
        params = {'query': query}
        if document_type:
            params['document_type'] = document_type
        if compliance_level:
            params['compliance_level'] = compliance_level
        
        # Формируем query string
        query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        
        return self._make_api_request(
            'document_processor',
            f'/search?{query_string}',
            method='GET'
        )
    
    # Compliance Checker методы  
    def conduct_compliance_assessment(self, standard='iso_22301', assessor='system', scope='Full assessment'):
        """Проведение оценки соответствия через Compliance Checker"""
        params = {
            'standard': standard,
            'assessor': assessor,
            'scope': scope
        }
        query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        
        return self._make_api_request(
            'compliance_checker',
            f'/assess?{query_string}',
            method='POST'
        )
    
    def submit_compliance_evidence(self, evidence_data):
        """Предоставление доказательств соответствия"""
        return self._make_api_request(
            'compliance_checker',
            '/evidence',
            method='POST',
            data=evidence_data
        )
    
    def get_compliance_analytics(self, days=30):
        """Получение аналитики соответствия"""
        return self._make_api_request(
            'compliance_checker',
            f'/analytics/compliance-trends?days={days}',
            method='GET'
        )
