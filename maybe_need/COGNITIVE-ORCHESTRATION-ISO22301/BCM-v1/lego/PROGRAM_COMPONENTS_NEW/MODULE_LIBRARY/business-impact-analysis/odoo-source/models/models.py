# -*- coding: utf-8 -*-

import json
import logging
from datetime import datetime

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

class BCMIndustryType(models.Model):
    """Отраслевые типы для BIA анализа"""
    _name = 'bcm.industry.type'
    _description = 'BCM Industry Types'
    _rec_name = 'name'
    _order = 'sequence, name'
    
    sequence = fields.Integer('Sequence', default=10)
    name = fields.Char('Industry Name', required=True)
    code = fields.Char('Industry Code', required=True)
    revenue_loss_multiplier = fields.Float('Revenue Loss Multiplier', default=1.0)
    reputation_impact = fields.Float('Reputation Impact Factor', default=1.0)
    regulatory_penalty = fields.Float('Regulatory Penalty Factor', default=0.5)
    base_rto_hours = fields.Integer('Base RTO Hours', default=24)
    base_rpo_minutes = fields.Integer('Base RPO Minutes', default=240)
    description = fields.Text('Description')
    active = fields.Boolean(default=True)
    
    # Multi-tenancy field
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True, index=True,
        default=lambda self: self.env.company,
        help='Company/tenant isolation'
    )

class BCMBusinessProcess(models.Model):
    """Бизнес-процессы для BIA анализа с AI интеграцией"""
    _name = 'bcm.business.process'
    _description = 'BCM Business Process for BIA Analysis'
    _rec_name = 'name'
    _order = 'criticality desc, name'
    
    name = fields.Char('Process Name', required=True)
    description = fields.Text('Process Description')
    
    # Основные параметры процесса
    industry_id = fields.Many2one('bcm.industry.type', 'Industry Type', required=True)
    criticality = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ], string='Criticality Level', required=True, default='medium')
    
    # Финансовые параметры
    annual_revenue_impact = fields.Float('Annual Revenue Impact ($)', required=True, default=0.0)
    peak_concurrent_users = fields.Integer('Peak Concurrent Users', default=0)
    staff_count = fields.Integer('Staff Count', required=True, default=1)
    
    # Зависимости и требования
    dependency_ids = fields.Many2many(
        'bcm.business.process', 
        'bcm_process_dependency_rel',
        'process_id', 'dependency_id',
        string='Process Dependencies'
    )
    geographical_scope = fields.Selection([
        ('local', 'Local'),
        ('regional', 'Regional'), 
        ('national', 'National'),
        ('global', 'Global'),
    ], string='Geographical Scope', default='local')
    
    compliance_requirement_ids = fields.Many2many(
        'bcm.compliance.requirement',
        string='Compliance Requirements'
    )
    
    technology_stack_ids = fields.Many2many(
        'bcm.technology.stack',
        string='Technology Stack'
    )
    
    # AI-оптимизированные параметры (результаты BIA Engine)
    optimized_rto_hours = fields.Float('Optimized RTO (Hours)', readonly=True)
    optimized_rpo_minutes = fields.Float('Optimized RPO (Minutes)', readonly=True) 
    mtpd_hours = fields.Float('MTPD (Hours)', readonly=True)
    confidence_score = fields.Float('AI Confidence Score', readonly=True)
    
    # Финансовые расчеты от AI
    total_financial_impact_24h = fields.Float('24h Financial Impact ($)', readonly=True)
    hourly_impact_rate = fields.Float('Hourly Impact Rate ($)', readonly=True)
    annual_risk_exposure = fields.Float('Annual Risk Exposure ($)', readonly=True)
    
    # Каскадные риски
    cascade_risk_score = fields.Float('Cascade Risk Score', readonly=True)
    dependency_depth = fields.Integer('Dependency Depth', readonly=True)
    impact_breadth = fields.Integer('Impact Breadth', readonly=True)
    
    # Метаданные AI анализа
    last_ai_analysis = fields.Datetime('Last AI Analysis', readonly=True)
    ai_recommendations = fields.Text('AI Recommendations', readonly=True)
    analysis_confidence = fields.Selection([
        ('low', 'Low Confidence'),
        ('medium', 'Medium Confidence'),
        ('high', 'High Confidence'),
    ], string='Analysis Confidence', readonly=True)
    
    active = fields.Boolean(default=True)
    
    # Multi-tenancy field
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True, index=True,
        default=lambda self: self.env.company,
        help='Company/tenant isolation'
    )
    
    def action_compute_bia(self):
        """Кнопка Compute BIA - запуск анализа через внешний BIA Engine"""
        self.ensure_one()
        
        try:
            import requests
            
            # Получить URL BIA Engine из настроек
            BcmConfig = self.env.get('bcm.config')
            if not BcmConfig:
                # Fallback to AI integration service
                return self.action_run_ai_analysis()
            
            config = BcmConfig.sudo().search([], limit=1)
            if not config or not config.bia_engine_base_url:
                raise UserError(_('BIA Engine URL is not configured. Please configure it in BCM Settings.'))
            
            # Подготавливаем данные процесса для BIA Engine
            process_data = {
                'process_id': self.id,
                'name': self.name,
                'description': self.description or '',
                'industry': self.industry_id.code if self.industry_id else 'other',
                'criticality': self.criticality,
                'annual_revenue_impact': self.annual_revenue_impact,
                'peak_concurrent_users': self.peak_concurrent_users,
                'dependencies': [dep.id for dep in self.dependency_ids],
                'geographical_scope': self.geographical_scope,
                'compliance_requirements': [req.code for req in self.compliance_requirement_ids],
                'technology_stack': [tech.name for tech in self.technology_stack_ids],
                'staff_count': self.staff_count,
            }
            
            # Вызов BIA Engine API
            url = f"{config.bia_engine_base_url}/compute"
            response = requests.post(
                url,
                json=process_data,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Сохраняем результаты
                self.write({
                    'optimized_rto_hours': result.get('rto', 0),
                    'optimized_rpo_minutes': result.get('rpo', 0),
                    'mtpd_hours': result.get('mtpd', 0),
                    'confidence_score': result.get('confidence', 0),
                    'total_financial_impact_24h': result.get('financial_impact_24h', 0),
                    'hourly_impact_rate': result.get('hourly_impact', 0),
                    'last_ai_analysis': fields.Datetime.now(),
                    'ai_recommendations': result.get('recommendations', ''),
                    'analysis_confidence': 'high' if result.get('confidence', 0) > 0.8 else 'medium'
                })
                
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('BIA Computed Successfully'),
                        'message': _('RTO: %s hours, RPO: %s minutes, MTPD: %s hours') % (
                            result.get('rto', 0),
                            result.get('rpo', 0),
                            result.get('mtpd', 0)
                        ),
                        'type': 'success',
                        'sticky': False,
                    }
                }
            else:
                raise UserError(_('BIA Engine returned error: %s') % response.text)
                
        except requests.exceptions.RequestException as e:
            _logger.error(f"BIA Engine request failed: {e}")
            raise UserError(_('Failed to connect to BIA Engine: %s') % str(e))
        except Exception as e:
            _logger.error(f"BIA computation failed: {e}")
            raise UserError(_('BIA computation failed: %s') % str(e))
    
    def action_run_ai_analysis(self):
        """Fallback метод для AI анализа через встроенный сервис"""
        self.ensure_one()
        
        ai_service = self.env['bcm.ai.integration']
        
        try:
            # Подготавливаем данные процесса для BIA Engine
            process_data = {
                'id': self.id,
                'name': self.name,
                'description': self.description or '',
                'industry': self.industry_id.code if self.industry_id else 'other',
                'criticality': self.criticality,
                'annual_revenue_impact': self.annual_revenue_impact,
                'peak_concurrent_users': self.peak_concurrent_users,
                'dependencies': [dep.id for dep in self.dependency_ids],
                'geographical_scope': self.geographical_scope,
                'compliance_requirements': [req.code for req in self.compliance_requirement_ids],
                'technology_stack': [tech.name for tech in self.technology_stack_ids],
                'staff_count': self.staff_count,
            }
            
            # Вызываем BIA Engine для оптимизации
            optimization_result = ai_service.bia_optimize_single_process(
                process_data, 
                risk_tolerance=0.05
            )
            
            # Обновляем данные процесса результатами AI
            if optimization_result.get('status') == 'success':
                opt_data = optimization_result['optimization']
                financial_data = optimization_result['financial_impact']
                
                self.write({
                    'optimized_rto_hours': opt_data['optimized_rto_hours'],
                    'optimized_rpo_minutes': opt_data['optimized_rpo_minutes'],
                    'mtpd_hours': opt_data['mtpd_hours'],
                    'confidence_score': opt_data['confidence_score'],
                    'total_financial_impact_24h': financial_data['total_financial_impact'],
                    'hourly_impact_rate': financial_data['hourly_impact_rate'],
                    'annual_risk_exposure': financial_data.get('annual_risk_exposure', 0),
                    'last_ai_analysis': fields.Datetime.now(),
                    'ai_recommendations': '\n'.join([
                        f"• Целевое RTO: {opt_data['optimized_rto_hours']} часов",
                        f"• Целевое RPO: {opt_data['optimized_rpo_minutes']} минут",
                        f"• Ожидаемые затраты на улучшения: ${opt_data['estimated_improvement_cost']:,.2f}",
                        f"• Потенциальные финансовые потери: ${financial_data['total_financial_impact']:,.2f}/инцидент"
                    ]),
                    'analysis_confidence': 'high' if opt_data['confidence_score'] > 0.8 else 'medium' if opt_data['confidence_score'] > 0.6 else 'low',
                })
                
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('🧠 AI Analysis Complete!'),
                        'message': _('BIA Engine optimized RTO to %s hours, RPO to %s minutes. Financial impact: $%s/24h') % (
                            opt_data['optimized_rto_hours'],
                            opt_data['optimized_rpo_minutes'], 
                            f"{financial_data['total_financial_impact']:,.2f}"
                        ),
                        'type': 'success',
                        'sticky': True,
                    }
                }
            
        except Exception as e:
            _logger.error(f"BIA AI Analysis failed for process {self.name}: {e}")
            raise UserError(_('AI Analysis failed: %s') % str(e))

class BCMBIAAnalysis(models.Model):
    """Комплексный BIA анализ для группы процессов"""
    _name = 'bcm.bia.analysis'
    _description = 'BCM Business Impact Analysis'
    _rec_name = 'name'
    _order = 'create_date desc'
    
    name = fields.Char('Analysis Name', required=True)
    description = fields.Text('Analysis Description')
    
    # Параметры анализа
    process_ids = fields.Many2many('bcm.business.process', string='Business Processes', required=True)
    analysis_period_days = fields.Integer('Analysis Period (Days)', default=365, required=True)
    risk_tolerance = fields.Float('Risk Tolerance', default=0.05, required=True)
    budget_constraint = fields.Float('Budget Constraint ($)', default=0.0)
    
    # Результаты анализа
    total_processes_analyzed = fields.Integer('Total Processes', readonly=True)
    critical_processes_count = fields.Integer('Critical Processes', readonly=True) 
    total_annual_risk_exposure = fields.Float('Total Annual Risk Exposure ($)', readonly=True)
    average_rto_hours = fields.Float('Average RTO (Hours)', readonly=True)
    
    # Статус анализа
    state = fields.Selection([
        ('draft', 'Draft'),
        ('analyzing', 'AI Analyzing...'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ], string='Status', default='draft', readonly=True)
    
    analysis_results = fields.Text('Detailed Analysis Results', readonly=True)
    dependency_recommendations = fields.Text('Dependency Recommendations', readonly=True)
    critical_path_processes = fields.Text('Critical Path Processes', readonly=True)
    
    # Метаданные
    analysis_date = fields.Datetime('Analysis Date', readonly=True)
    methodology = fields.Char('AI Methodology', readonly=True)
    
    # Multi-tenancy field
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True, index=True,
        default=lambda self: self.env.company,
        help='Company/tenant isolation'
    )
    
    def action_run_comprehensive_analysis(self):
        """Запуск комплексного BIA анализа через AI"""
        self.ensure_one()
        
        if not self.process_ids:
            raise UserError(_('Please select at least one business process for analysis.'))
        
        self.state = 'analyzing'
        
        ai_service = self.env['bcm.ai.integration']
        
        try:
            # Подготавливаем данные всех процессов
            processes_data = []
            for process in self.process_ids:
                process_data = {
                    'id': process.id,
                    'name': process.name,
                    'description': process.description or '',
                    'industry': process.industry_id.code if process.industry_id else 'other',
                    'criticality': process.criticality,
                    'annual_revenue_impact': process.annual_revenue_impact,
                    'peak_concurrent_users': process.peak_concurrent_users,
                    'dependencies': [dep.id for dep in process.dependency_ids],
                    'geographical_scope': process.geographical_scope,
                    'compliance_requirements': [req.code for req in process.compliance_requirement_ids],
                    'technology_stack': [tech.name for tech in process.technology_stack_ids],
                    'staff_count': process.staff_count,
                }
                processes_data.append(process_data)
            
            # Вызываем BIA Engine для комплексного анализа
            analysis_result = ai_service.bia_compute_comprehensive_analysis(
                processes_data,
                self.analysis_period_days,
                self.risk_tolerance
            )
            
            if analysis_result.get('status') == 'success':
                summary = analysis_result['summary']
                detailed_results = analysis_result['detailed_results']
                
                # Обновляем результаты анализа
                self.write({
                    'total_processes_analyzed': summary['total_processes_analyzed'],
                    'critical_processes_count': summary['critical_processes'],
                    'total_annual_risk_exposure': summary['total_annual_risk_exposure'],
                    'average_rto_hours': summary['average_rto_hours'],
                    'analysis_results': json.dumps(detailed_results, indent=2),
                    'dependency_recommendations': '\n'.join(
                        summary['dependency_analysis']['recommendations']
                    ),
                    'critical_path_processes': ', '.join(
                        map(str, summary['dependency_analysis']['critical_path_processes'])
                    ),
                    'analysis_date': fields.Datetime.now(),
                    'methodology': summary['analysis_metadata']['methodology'],
                    'state': 'completed',
                })
                
                # Обновляем отдельные процессы результатами
                for result in detailed_results:
                    process = self.process_ids.filtered(lambda p: p.id == result['process_id'])
                    if process:
                        opt_data = result['optimization']
                        financial_data = result['financial_impact']
                        dependency_data = result.get('dependency_metrics', {})
                        
                        process.write({
                            'optimized_rto_hours': opt_data['optimized_rto_hours'],
                            'optimized_rpo_minutes': opt_data['optimized_rpo_minutes'],
                            'mtpd_hours': opt_data['mtpd_hours'],
                            'confidence_score': opt_data['confidence_score'],
                            'total_financial_impact_24h': financial_data['24_hour_downtime']['total_financial_impact'],
                            'hourly_impact_rate': financial_data['optimized_rto_downtime']['hourly_impact_rate'],
                            'annual_risk_exposure': financial_data['annual_risk_exposure'],
                            'cascade_risk_score': dependency_data.get('cascade_risk_score', 0),
                            'dependency_depth': dependency_data.get('dependency_depth', 0),
                            'impact_breadth': dependency_data.get('impact_breadth', 0),
                            'last_ai_analysis': fields.Datetime.now(),
                            'ai_recommendations': '\n'.join(result.get('recommendations', [])),
                        })
                
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Comprehensive BIA Analysis Complete!'),
                        'message': _('Analyzed %d processes. Total annual risk: $%s. Average RTO: %s hours.') % (
                            summary['total_processes_analyzed'],
                            f"{summary['total_annual_risk_exposure']:,.2f}",
                            summary['average_rto_hours']
                        ),
                        'type': 'success',
                        'sticky': True,
                    }
                }
            else:
                self.state = 'failed'
                raise UserError(_('BIA Analysis failed'))
                
        except Exception as e:
            self.state = 'failed'
            _logger.error(f"Comprehensive BIA Analysis failed: {e}")
            raise UserError(_('Comprehensive BIA Analysis failed: %s') % str(e))

# Дополнительные справочники
class BCMComplianceRequirement(models.Model):
    _name = 'bcm.compliance.requirement'
    _description = 'BCM Compliance Requirements'
    
    name = fields.Char('Requirement Name', required=True)
    code = fields.Char('Requirement Code', required=True)
    description = fields.Text('Description')
    active = fields.Boolean(default=True)
    
    # Multi-tenancy field
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True, index=True,
        default=lambda self: self.env.company,
        help='Company/tenant isolation'
    )

class BCMTechnologyStack(models.Model):
    _name = 'bcm.technology.stack'
    _description = 'BCM Technology Stack'
    
    name = fields.Char('Technology Name', required=True)
    category = fields.Char('Technology Category')
    description = fields.Text('Description')
    active = fields.Boolean(default=True)
    
    # Multi-tenancy field
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True, index=True,
        default=lambda self: self.env.company,
        help='Company/tenant isolation'
    )
