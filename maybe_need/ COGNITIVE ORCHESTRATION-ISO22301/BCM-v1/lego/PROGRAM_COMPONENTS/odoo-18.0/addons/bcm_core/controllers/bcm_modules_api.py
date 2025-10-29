# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import json
import logging
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)


class BCMModulesAPIController(http.Controller):
    """REST API адаптеры для всех BCM модулей в Odoo"""

    def _get_base_response_format(self, data=None, total=None, success=True, message=None):
        """Базовый формат ответа для всех API эндпоинтов"""
        response = {
            "success": success,
            "data": data or [],
            "total": total if total is not None else (len(data) if data else 0)
        }
        if message:
            response["message"] = message
        return response

    def _handle_api_error(self, error, context="API Error"):
        """Обработка ошибок API с логированием"""
        error_msg = str(error)
        _logger.error(f"{context}: {error_msg}")
        return self._get_base_response_format(
            success=False,
            message=f"{context}: {error_msg}"
        )

    # ========================= BCM MODULES API =========================

    @http.route('/api/bcm/modules', type='json', auth='user', methods=['GET'], cors='*')
    def get_bcm_modules(self, **kwargs):
        """Получить список всех установленных BCM модулей

        Query params:
        - state: фильтр по состоянию модуля (installed, to upgrade, etc.)
        - limit: лимит записей (по умолчанию 50)
        - offset: смещение для пагинации
        """
        try:
            domain = [('name', 'like', 'bcm_%')]

            # Фильтрация по состоянию
            state = kwargs.get('state', 'installed')
            if state:
                domain.append(('state', '=', state))

            # Пагинация
            limit = int(kwargs.get('limit', 50))
            offset = int(kwargs.get('offset', 0))

            modules = request.env['ir.module.module'].search(domain, limit=limit, offset=offset)
            total = request.env['ir.module.module'].search_count(domain)

            module_data = []
            for module in modules:
                module_info = {
                    'id': module.id,
                    'name': module.name,
                    'display_name': module.display_name or module.name,
                    'shortdesc': module.shortdesc,
                    'description': module.description,
                    'state': module.state,
                    'category': module.category_id.name if module.category_id else 'Other',
                    'version': module.latest_version,
                    'author': module.author,
                    'website': module.website,
                    'summary': module.summary,
                    'installed_version': module.installed_version,
                    'auto_install': module.auto_install,
                    'application': module.application,
                }
                module_data.append(module_info)

            return self._get_base_response_format(data=module_data, total=total)

        except Exception as e:
            return self._handle_api_error(e, "Failed to fetch BCM modules")

    # ========================= CLIENTS API =========================

    @http.route('/api/clients', type='json', auth='user', methods=['GET'], cors='*')
    def get_clients(self, **kwargs):
        """Получить список BCM клиентов

        Query params:
        - sector: фильтр по сектору
        - status: фильтр по статусу
        - region: фильтр по региону
        - search: поиск по названию
        - limit: лимит записей
        - offset: смещение для пагинации
        """
        try:
            domain = [('company_id', '=', request.env.company.id)]

            # Фильтры
            if kwargs.get('sector'):
                domain.append(('sector', '=', kwargs['sector']))
            if kwargs.get('status'):
                domain.append(('status', '=', kwargs['status']))
            if kwargs.get('region'):
                domain.append(('region', 'ilike', kwargs['region']))
            if kwargs.get('search'):
                domain.append(('name', 'ilike', kwargs['search']))

            # Пагинация
            limit = int(kwargs.get('limit', 50))
            offset = int(kwargs.get('offset', 0))

            clients = request.env['bcm.client'].search(domain, limit=limit, offset=offset)
            total = request.env['bcm.client'].search_count(domain)

            client_data = []
            for client in clients:
                client_info = {
                    'id': client.id,
                    'name': client.name,
                    'sector': client.sector,
                    'region': client.region,
                    'status': client.status,
                    'onboarding_stage': client.onboarding_stage,
                    'dpa_signed': client.dpa_signed,
                    'data_residency': client.data_residency,
                    'contact_count': client.contact_count,
                    'vault_count': client.vault_count,
                    'appkey_count': client.appkey_count,
                    'process_count': client.process_count,
                    'bia_count': client.bia_count,
                    'plan_count': client.plan_count,
                    'incident_count': client.incident_count,
                    'bia_coverage': client.bia_coverage,
                    'plans_freshness': client.plans_freshness,
                    'open_findings': client.open_findings,
                    'create_date': client.create_date.isoformat() if client.create_date else None,
                    'write_date': client.write_date.isoformat() if client.write_date else None,
                }
                client_data.append(client_info)

            return self._get_base_response_format(data=client_data, total=total)

        except Exception as e:
            return self._handle_api_error(e, "Failed to fetch clients")

    @http.route('/api/clients/<int:client_id>', type='json', auth='user', methods=['GET'], cors='*')
    def get_client_details(self, client_id, **kwargs):
        """Получить детальную информацию о конкретном клиенте"""
        try:
            client = request.env['bcm.client'].browse(client_id)
            if not client.exists():
                return self._get_base_response_format(
                    success=False,
                    message=f"Client with ID {client_id} not found"
                )

            # Проверка доступа (только для своей компании)
            if client.company_id != request.env.company:
                return self._get_base_response_format(
                    success=False,
                    message="Access denied to this client"
                )

            client_details = {
                'id': client.id,
                'name': client.name,
                'sector': client.sector,
                'region': client.region,
                'status': client.status,
                'onboarding_stage': client.onboarding_stage,
                'dpa_signed': client.dpa_signed,
                'data_residency': client.data_residency,
                'notes': client.notes,
                'contacts': [{
                    'id': contact.id,
                    'name': contact.name,
                    'email': contact.email,
                    'phone': contact.phone,
                    'role': contact.role,
                } for contact in client.contact_ids],
                'vault_items': [{
                    'id': vault.id,
                    'name': vault.name,
                    'document_type': vault.document_type,
                    'status': vault.status,
                } for vault in client.vault_ids],
                'api_keys': [{
                    'id': key.id,
                    'name': key.name,
                    'status': key.status,
                    'last_used': key.last_used.isoformat() if key.last_used else None,
                } for key in client.appkey_ids],
                'metrics': {
                    'contact_count': client.contact_count,
                    'vault_count': client.vault_count,
                    'appkey_count': client.appkey_count,
                    'process_count': client.process_count,
                    'bia_count': client.bia_count,
                    'plan_count': client.plan_count,
                    'incident_count': client.incident_count,
                    'bia_coverage': client.bia_coverage,
                    'plans_freshness': client.plans_freshness,
                    'open_findings': client.open_findings,
                },
                'create_date': client.create_date.isoformat() if client.create_date else None,
                'write_date': client.write_date.isoformat() if client.write_date else None,
            }

            return self._get_base_response_format(data=client_details)

        except Exception as e:
            return self._handle_api_error(e, f"Failed to fetch client {client_id}")

    # ========================= SCENARIOS API =========================

    @http.route('/api/scenarios', type='json', auth='user', methods=['GET'], cors='*')
    def get_scenarios(self, **kwargs):
        """Получить список BCM сценариев

        Query params:
        - category: фильтр по категории
        - level: фильтр по уровню (tabletop, full)
        - status: фильтр по статусу
        - visibility: фильтр по видимости
        - author_id: фильтр по автору
        - search: поиск по названию и контенту
        - tags: фильтр по тегам (comma-separated)
        - rating_min: минимальный рейтинг
        - limit: лимит записей
        - offset: смещение для пагинации
        """
        try:
            # Базовая фильтрация по видимости и правам доступа
            domain = []
            user = request.env.user

            # Фильтр видимости
            visibility_domain = [
                '|', '|',
                ('visibility', '=', 'public'),
                '&', ('visibility', '=', 'client_only'),
                     ('author_user_id.company_id', '=', user.company_id.id),
                ('author_user_id', '=', user.id)
            ]
            domain.extend(visibility_domain)

            # Дополнительные фильтры
            if kwargs.get('category'):
                domain.append(('category', '=', kwargs['category']))
            if kwargs.get('level'):
                domain.append(('level', '=', kwargs['level']))
            if kwargs.get('status'):
                domain.append(('status', '=', kwargs['status']))
            else:
                # По умолчанию показываем только опубликованные
                domain.append(('status', '=', 'published'))
            if kwargs.get('visibility'):
                domain.append(('visibility', '=', kwargs['visibility']))
            if kwargs.get('author_id'):
                domain.append(('author_user_id', '=', int(kwargs['author_id'])))
            if kwargs.get('search'):
                search_term = kwargs['search']
                domain.append('|')
                domain.append(('title', 'ilike', search_term))
                domain.append(('content_md', 'ilike', search_term))
            if kwargs.get('rating_min'):
                domain.append(('avg_rating', '>=', float(kwargs['rating_min'])))

            # Фильтр по тегам
            if kwargs.get('tags'):
                tag_names = [tag.strip() for tag in kwargs['tags'].split(',')]
                tag_ids = request.env['bcm.tag'].search([('name', 'in', tag_names)]).ids
                if tag_ids:
                    domain.append(('tags', 'in', tag_ids))

            # Пагинация
            limit = int(kwargs.get('limit', 50))
            offset = int(kwargs.get('offset', 0))

            scenarios = request.env['bcm.scenario'].search(domain, limit=limit, offset=offset)
            total = request.env['bcm.scenario'].search_count(domain)

            scenario_data = []
            for scenario in scenarios:
                scenario_info = {
                    'id': scenario.id,
                    'title': scenario.title,
                    'category': scenario.category,
                    'level': scenario.level,
                    'status': scenario.status,
                    'visibility': scenario.visibility,
                    'license': scenario.license,
                    'version': scenario.version,
                    'author': {
                        'id': scenario.author_user_id.id,
                        'name': scenario.author_user_id.name,
                        'organization': scenario.author_org,
                    },
                    'tags': [{'id': tag.id, 'name': tag.name} for tag in scenario.tags],
                    'domains': [{'id': domain.id, 'name': domain.name} for domain in scenario.domains],
                    'avg_rating': scenario.avg_rating,
                    'rating_count': scenario.rating_count,
                    'application_count': scenario.application_count,
                    'exercise_count': scenario.exercise_count,
                    'meta_ai_generated': scenario.meta_ai_generated,
                    'create_date': scenario.create_date.isoformat() if scenario.create_date else None,
                    'write_date': scenario.write_date.isoformat() if scenario.write_date else None,
                    'forum_topic_id': scenario.forum_topic_id.id if scenario.forum_topic_id else None,
                }
                scenario_data.append(scenario_info)

            return self._get_base_response_format(data=scenario_data, total=total)

        except Exception as e:
            return self._handle_api_error(e, "Failed to fetch scenarios")

    @http.route('/api/scenarios/<int:scenario_id>', type='json', auth='user', methods=['GET'], cors='*')
    def get_scenario_details(self, scenario_id, **kwargs):
        """Получить детальную информацию о конкретном сценарии"""
        try:
            scenario = request.env['bcm.scenario'].browse(scenario_id)
            if not scenario.exists():
                return self._get_base_response_format(
                    success=False,
                    message=f"Scenario with ID {scenario_id} not found"
                )

            # Проверка доступа
            user = request.env.user
            has_access = (
                scenario.visibility == 'public' or
                (scenario.visibility == 'client_only' and
                 scenario.author_user_id.company_id == user.company_id) or
                scenario.author_user_id == user
            )

            if not has_access:
                return self._get_base_response_format(
                    success=False,
                    message="Access denied to this scenario"
                )

            scenario_details = {
                'id': scenario.id,
                'title': scenario.title,
                'category': scenario.category,
                'level': scenario.level,
                'status': scenario.status,
                'visibility': scenario.visibility,
                'license': scenario.license,
                'custom_license_text': scenario.custom_license_text,
                'version': scenario.version,
                'content_md': scenario.content_md,
                'inputs_schema': scenario.get_inputs_schema_dict(),
                'expected_metrics': scenario.get_expected_metrics_dict(),
                'author': {
                    'id': scenario.author_user_id.id,
                    'name': scenario.author_user_id.name,
                    'organization': scenario.author_org,
                },
                'parent_id': scenario.parent_id.id if scenario.parent_id else None,
                'tags': [{'id': tag.id, 'name': tag.name} for tag in scenario.tags],
                'domains': [{'id': domain.id, 'name': domain.name} for domain in scenario.domains],
                'avg_rating': scenario.avg_rating,
                'rating_count': scenario.rating_count,
                'application_count': scenario.application_count,
                'exercise_count': scenario.exercise_count,
                'available_templates': [
                    {'id': tpl.id, 'name': tpl.name, 'template_type': tpl.template_type}
                    for tpl in scenario.available_templates
                ],
                'reviews': [{
                    'id': review.id,
                    'reviewer_name': review.reviewer_id.name,
                    'decision': review.decision,
                    'notes': review.notes,
                    'create_date': review.create_date.isoformat() if review.create_date else None,
                } for review in scenario.review_ids],
                'meta_ai_generated': scenario.meta_ai_generated,
                'meta_ai_params': scenario.meta_ai_params,
                'rejection_reason': scenario.rejection_reason,
                'permissions': {
                    'can_edit': scenario.can_edit,
                    'can_review': scenario.can_review,
                    'is_author': scenario.is_author,
                },
                'forum_topic_id': scenario.forum_topic_id.id if scenario.forum_topic_id else None,
                'create_date': scenario.create_date.isoformat() if scenario.create_date else None,
                'write_date': scenario.write_date.isoformat() if scenario.write_date else None,
            }

            return self._get_base_response_format(data=scenario_details)

        except Exception as e:
            return self._handle_api_error(e, f"Failed to fetch scenario {scenario_id}")

    # ========================= DASHBOARD API =========================

    @http.route('/api/dashboard/<string:dashboard_type>', type='json', auth='user', methods=['GET'], cors='*')
    def get_dashboard_data(self, dashboard_type, **kwargs):
        """Получить данные для различных типов дашбордов

        Поддерживаемые типы:
        - overview: общий обзор BCM
        - incidents: дашборд инцидентов
        - risk: дашборд рисков
        - plans: дашборд планов
        - kpi: дашборд KPI
        - clients: дашборд клиентов
        """
        try:
            company_id = request.env.company.id

            if dashboard_type == 'overview':
                data = self._get_overview_dashboard_data(company_id)
            elif dashboard_type == 'incidents':
                data = self._get_incidents_dashboard_data(company_id)
            elif dashboard_type == 'risk':
                data = self._get_risk_dashboard_data(company_id)
            elif dashboard_type == 'plans':
                data = self._get_plans_dashboard_data(company_id)
            elif dashboard_type == 'kpi':
                data = self._get_kpi_dashboard_data(company_id)
            elif dashboard_type == 'clients':
                data = self._get_clients_dashboard_data(company_id)
            else:
                return self._get_base_response_format(
                    success=False,
                    message=f"Unknown dashboard type: {dashboard_type}"
                )

            return self._get_base_response_format(data=data)

        except Exception as e:
            return self._handle_api_error(e, f"Failed to fetch {dashboard_type} dashboard data")

    def _get_overview_dashboard_data(self, company_id):
        """Данные для общего дашборда"""
        # Базовые счетчики
        client_count = request.env['bcm.client'].search_count([('company_id', '=', company_id)])

        incident_env = request.env.get('bcm.incident')
        incident_count = incident_env.search_count([('company_id', '=', company_id)]) if incident_env else 0
        active_incidents = incident_env.search_count([
            ('company_id', '=', company_id),
            ('status', 'in', ['draft', 'in_progress'])
        ]) if incident_env else 0

        plan_env = request.env.get('bcm.plan')
        plan_count = plan_env.search_count([('company_id', '=', company_id)]) if plan_env else 0

        scenario_count = request.env['bcm.scenario'].search_count([
            ('author_user_id.company_id', '=', company_id)
        ])

        return {
            'summary': {
                'total_clients': client_count,
                'total_incidents': incident_count,
                'active_incidents': active_incidents,
                'total_plans': plan_count,
                'total_scenarios': scenario_count,
            },
            'recent_activity': self._get_recent_activity(company_id),
            'alerts': self._get_dashboard_alerts(company_id),
        }

    def _get_incidents_dashboard_data(self, company_id):
        """Данные для дашборда инцидентов"""
        incident_env = request.env.get('bcm.incident')
        if not incident_env:
            return {'incidents_by_severity': {}, 'incidents_by_status': {}, 'recent_incidents': []}

        domain = [('company_id', '=', company_id)]
        incidents = incident_env.search(domain)

        # Группировка по серьезности
        severity_counts = {}
        for incident in incidents:
            severity = incident.severity or 'unknown'
            severity_counts[severity] = severity_counts.get(severity, 0) + 1

        # Группировка по статусу
        status_counts = {}
        for incident in incidents:
            status = incident.status or 'unknown'
            status_counts[status] = status_counts.get(status, 0) + 1

        # Последние инциденты
        recent_incidents = []
        for incident in incidents[:10]:  # Последние 10
            recent_incidents.append({
                'id': incident.id,
                'name': incident.name,
                'severity': incident.severity,
                'status': incident.status,
                'create_date': incident.create_date.isoformat() if incident.create_date else None,
            })

        return {
            'incidents_by_severity': severity_counts,
            'incidents_by_status': status_counts,
            'recent_incidents': recent_incidents,
        }

    def _get_risk_dashboard_data(self, company_id):
        """Данные для дашборда рисков"""
        risk_env = request.env.get('bcm.risk')
        if not risk_env:
            return {'risk_matrix': {}, 'top_risks': [], 'risk_trends': []}

        domain = [('company_id', '=', company_id)]
        risks = risk_env.search(domain)

        # Матрица рисков (impact vs probability)
        risk_matrix = {}
        for risk in risks:
            impact = getattr(risk, 'impact', 'unknown')
            probability = getattr(risk, 'probability', 'unknown')
            key = f"{impact}_{probability}"
            risk_matrix[key] = risk_matrix.get(key, 0) + 1

        # Топ рисков
        top_risks = []
        for risk in risks[:10]:
            top_risks.append({
                'id': risk.id,
                'name': risk.name if hasattr(risk, 'name') else str(risk),
                'risk_level': getattr(risk, 'risk_level', 'unknown'),
                'impact': getattr(risk, 'impact', 'unknown'),
                'probability': getattr(risk, 'probability', 'unknown'),
            })

        return {
            'risk_matrix': risk_matrix,
            'top_risks': top_risks,
            'risk_trends': [],  # TODO: Implement trend analysis
        }

    def _get_plans_dashboard_data(self, company_id):
        """Данные для дашборда планов"""
        plan_env = request.env.get('bcm.plan')
        if not plan_env:
            return {'plans_by_type': {}, 'plans_by_status': {}, 'outdated_plans': []}

        domain = [('company_id', '=', company_id)]
        plans = plan_env.search(domain)

        # Группировка по типу
        type_counts = {}
        for plan in plans:
            plan_type = getattr(plan, 'plan_type', 'unknown')
            type_counts[plan_type] = type_counts.get(plan_type, 0) + 1

        # Группировка по статусу
        status_counts = {}
        for plan in plans:
            status = getattr(plan, 'status', 'unknown')
            status_counts[status] = status_counts.get(status, 0) + 1

        # Устаревшие планы (более 1 года)
        outdated_threshold = datetime.now() - timedelta(days=365)
        outdated_plans = []
        for plan in plans:
            if plan.write_date and plan.write_date < outdated_threshold:
                outdated_plans.append({
                    'id': plan.id,
                    'name': getattr(plan, 'name', str(plan)),
                    'plan_type': getattr(plan, 'plan_type', 'unknown'),
                    'last_updated': plan.write_date.isoformat(),
                })

        return {
            'plans_by_type': type_counts,
            'plans_by_status': status_counts,
            'outdated_plans': outdated_plans[:10],  # Топ 10 устаревших
        }

    def _get_kpi_dashboard_data(self, company_id):
        """Данные для дашборда KPI"""
        kpi_env = request.env.get('bcm.kpi')
        if not kpi_env:
            return {'kpi_summary': {}, 'kpi_trends': []}

        domain = [('company_id', '=', company_id)]
        kpis = kpi_env.search(domain)

        kpi_summary = {}
        for kpi in kpis:
            kpi_summary[getattr(kpi, 'name', str(kpi))] = {
                'current_value': getattr(kpi, 'current_value', 0),
                'target_value': getattr(kpi, 'target_value', 0),
                'trend': getattr(kpi, 'trend', 'stable'),
            }

        return {
            'kpi_summary': kpi_summary,
            'kpi_trends': [],  # TODO: Implement KPI trends
        }

    def _get_clients_dashboard_data(self, company_id):
        """Данные для дашборда клиентов"""
        clients = request.env['bcm.client'].search([('company_id', '=', company_id)])

        # Группировка по секторам
        sector_counts = {}
        for client in clients:
            sector = client.sector or 'unknown'
            sector_counts[sector] = sector_counts.get(sector, 0) + 1

        # Группировка по статусам
        status_counts = {}
        for client in clients:
            status = client.status or 'unknown'
            status_counts[status] = status_counts.get(status, 0) + 1

        # Группировка по этапам внедрения
        onboarding_counts = {}
        for client in clients:
            stage = client.onboarding_stage or 'unknown'
            onboarding_counts[stage] = onboarding_counts.get(stage, 0) + 1

        return {
            'clients_by_sector': sector_counts,
            'clients_by_status': status_counts,
            'clients_by_onboarding_stage': onboarding_counts,
            'total_clients': len(clients),
        }

    def _get_recent_activity(self, company_id):
        """Получить последнюю активность"""
        activities = []

        # Последние инциденты
        incident_env = request.env.get('bcm.incident')
        if incident_env:
            recent_incidents = incident_env.search([
                ('company_id', '=', company_id)
            ], limit=5, order='create_date desc')

            for incident in recent_incidents:
                activities.append({
                    'type': 'incident',
                    'title': f"New incident: {incident.name}",
                    'date': incident.create_date.isoformat() if incident.create_date else None,
                    'severity': getattr(incident, 'severity', 'unknown'),
                })

        # Последние планы
        plan_env = request.env.get('bcm.plan')
        if plan_env:
            recent_plans = plan_env.search([
                ('company_id', '=', company_id)
            ], limit=5, order='create_date desc')

            for plan in recent_plans:
                activities.append({
                    'type': 'plan',
                    'title': f"Plan updated: {getattr(plan, 'name', str(plan))}",
                    'date': plan.write_date.isoformat() if plan.write_date else None,
                })

        # Сортировка по дате
        activities.sort(key=lambda x: x['date'] or '', reverse=True)
        return activities[:10]

    def _get_dashboard_alerts(self, company_id):
        """Получить alerts для дашборда"""
        alerts = []

        # Alert для активных инцидентов
        incident_env = request.env.get('bcm.incident')
        if incident_env:
            active_incidents = incident_env.search_count([
                ('company_id', '=', company_id),
                ('status', 'in', ['draft', 'in_progress'])
            ])

            if active_incidents > 0:
                alerts.append({
                    'type': 'warning',
                    'title': f"{active_incidents} active incident(s)",
                    'message': "There are active incidents requiring attention",
                })

        # Alert для устаревших планов
        plan_env = request.env.get('bcm.plan')
        if plan_env:
            outdated_threshold = datetime.now() - timedelta(days=365)
            outdated_plans = plan_env.search_count([
                ('company_id', '=', company_id),
                ('write_date', '<', outdated_threshold)
            ])

            if outdated_plans > 0:
                alerts.append({
                    'type': 'info',
                    'title': f"{outdated_plans} outdated plan(s)",
                    'message': "Some business continuity plans need review",
                })

        return alerts

    # ========================= NOTIFICATIONS API =========================

    @http.route('/api/notifications', type='json', auth='user', methods=['GET'], cors='*')
    def get_notifications(self, **kwargs):
        """Получить уведомления для текущего пользователя

        Query params:
        - unread_only: показать только непрочитанные (true/false)
        - limit: лимит записей
        - offset: смещение для пагинации
        """
        try:
            user = request.env.user

            # Ищем сообщения и активности пользователя
            domain = [
                '|',
                ('author_id', '=', user.partner_id.id),
                ('partner_ids', 'in', [user.partner_id.id])
            ]

            # Фильтр по непрочитанным
            if kwargs.get('unread_only') == 'true':
                # TODO: Добавить фильтр по непрочитанным сообщениям
                pass

            # Пагинация
            limit = int(kwargs.get('limit', 50))
            offset = int(kwargs.get('offset', 0))

            # Получаем сообщения
            messages = request.env['mail.message'].search(
                domain,
                limit=limit,
                offset=offset,
                order='create_date desc'
            )
            total = request.env['mail.message'].search_count(domain)

            notification_data = []
            for message in messages:
                notification_data.append({
                    'id': message.id,
                    'subject': message.subject or 'No subject',
                    'body': message.body,
                    'message_type': message.message_type,
                    'subtype': message.subtype_id.name if message.subtype_id else None,
                    'author': {
                        'id': message.author_id.id,
                        'name': message.author_id.name,
                    } if message.author_id else None,
                    'model': message.model,
                    'res_id': message.res_id,
                    'create_date': message.create_date.isoformat() if message.create_date else None,
                    'is_read': False,  # TODO: Implement read status
                })

            return self._get_base_response_format(data=notification_data, total=total)

        except Exception as e:
            return self._handle_api_error(e, "Failed to fetch notifications")

    # ========================= KPI API =========================

    @http.route('/api/kpi', type='json', auth='user', methods=['GET'], cors='*')
    def get_kpi_data(self, **kwargs):
        """Получить KPI данные

        Query params:
        - category: фильтр по категории KPI
        - period: период для расчета (day, week, month, year)
        - from_date: начальная дата
        - to_date: конечная дата
        """
        try:
            company_id = request.env.company.id

            # Базовые KPI из различных модулей
            kpi_data = {
                'incidents': self._get_incident_kpis(company_id, kwargs),
                'plans': self._get_plan_kpis(company_id, kwargs),
                'risks': self._get_risk_kpis(company_id, kwargs),
                'clients': self._get_client_kpis(company_id, kwargs),
                'scenarios': self._get_scenario_kpis(company_id, kwargs),
            }

            # Если есть модуль bcm_kpi, получаем дополнительные KPI
            kpi_env = request.env.get('bcm.kpi')
            if kpi_env:
                custom_kpis = kpi_env.search([('company_id', '=', company_id)])
                kpi_data['custom'] = [{
                    'id': kpi.id,
                    'name': getattr(kpi, 'name', str(kpi)),
                    'value': getattr(kpi, 'current_value', 0),
                    'target': getattr(kpi, 'target_value', 0),
                    'unit': getattr(kpi, 'unit', ''),
                    'trend': getattr(kpi, 'trend', 'stable'),
                } for kpi in custom_kpis]

            return self._get_base_response_format(data=kpi_data)

        except Exception as e:
            return self._handle_api_error(e, "Failed to fetch KPI data")

    def _get_incident_kpis(self, company_id, filters):
        """KPI для инцидентов"""
        incident_env = request.env.get('bcm.incident')
        if not incident_env:
            return {}

        domain = [('company_id', '=', company_id)]
        incidents = incident_env.search(domain)

        return {
            'total_incidents': len(incidents),
            'active_incidents': len([i for i in incidents if getattr(i, 'status', '') in ['draft', 'in_progress']]),
            'resolved_incidents': len([i for i in incidents if getattr(i, 'status', '') == 'resolved']),
            'high_severity_incidents': len([i for i in incidents if getattr(i, 'severity', '') == 'high']),
        }

    def _get_plan_kpis(self, company_id, filters):
        """KPI для планов"""
        plan_env = request.env.get('bcm.plan')
        if not plan_env:
            return {}

        domain = [('company_id', '=', company_id)]
        plans = plan_env.search(domain)

        outdated_threshold = datetime.now() - timedelta(days=365)
        outdated_plans = [p for p in plans if p.write_date and p.write_date < outdated_threshold]

        return {
            'total_plans': len(plans),
            'active_plans': len([p for p in plans if getattr(p, 'status', '') == 'active']),
            'outdated_plans': len(outdated_plans),
            'plan_coverage': 75.0,  # TODO: Calculate actual coverage
        }

    def _get_risk_kpis(self, company_id, filters):
        """KPI для рисков"""
        risk_env = request.env.get('bcm.risk')
        if not risk_env:
            return {}

        domain = [('company_id', '=', company_id)]
        risks = risk_env.search(domain)

        return {
            'total_risks': len(risks),
            'high_risks': len([r for r in risks if getattr(r, 'risk_level', '') == 'high']),
            'mitigated_risks': len([r for r in risks if getattr(r, 'status', '') == 'mitigated']),
            'risk_coverage': 60.0,  # TODO: Calculate actual coverage
        }

    def _get_client_kpis(self, company_id, filters):
        """KPI для клиентов"""
        clients = request.env['bcm.client'].search([('company_id', '=', company_id)])

        return {
            'total_clients': len(clients),
            'active_clients': len([c for c in clients if c.status == 'active']),
            'onboarding_clients': len([c for c in clients if c.status == 'onboarding']),
            'avg_bia_coverage': sum(c.bia_coverage for c in clients) / len(clients) if clients else 0,
        }

    def _get_scenario_kpis(self, company_id, filters):
        """KPI для сценариев"""
        scenarios = request.env['bcm.scenario'].search([
            ('author_user_id.company_id', '=', company_id)
        ])

        return {
            'total_scenarios': len(scenarios),
            'published_scenarios': len([s for s in scenarios if s.status == 'published']),
            'avg_rating': sum(s.avg_rating for s in scenarios) / len(scenarios) if scenarios else 0,
            'total_applications': sum(s.application_count for s in scenarios),
        }

    # ========================= UTILITY ENDPOINTS =========================

    @http.route('/api/bcm/health', type='json', auth='user', methods=['GET'], cors='*')
    def health_check(self, **kwargs):
        """Health check для BCM API"""
        try:
            # Проверяем доступность основных моделей
            models_status = {}

            key_models = [
                'bcm.client', 'bcm.scenario', 'bcm.incident',
                'bcm.plan', 'bcm.risk', 'bcm.kpi'
            ]

            for model_name in key_models:
                try:
                    model = request.env.get(model_name)
                    if model:
                        count = model.search_count([])
                        models_status[model_name] = {'available': True, 'count': count}
                    else:
                        models_status[model_name] = {'available': False, 'count': 0}
                except Exception as e:
                    models_status[model_name] = {'available': False, 'error': str(e)}

            health_data = {
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'models': models_status,
                'user': {
                    'id': request.env.user.id,
                    'name': request.env.user.name,
                    'company': request.env.company.name,
                },
            }

            return self._get_base_response_format(data=health_data)

        except Exception as e:
            return self._handle_api_error(e, "Health check failed")

    @http.route('/api/bcm/stats', type='json', auth='user', methods=['GET'], cors='*')
    def get_bcm_stats(self, **kwargs):
        """Получить общую статистику BCM платформы"""
        try:
            company_id = request.env.company.id

            stats = {
                'modules': {
                    'installed_count': request.env['ir.module.module'].search_count([
                        ('name', 'like', 'bcm_%'),
                        ('state', '=', 'installed')
                    ]),
                    'available_count': request.env['ir.module.module'].search_count([
                        ('name', 'like', 'bcm_%')
                    ]),
                },
                'data': {
                    'clients': request.env['bcm.client'].search_count([('company_id', '=', company_id)]),
                    'scenarios': request.env['bcm.scenario'].search_count([
                        ('author_user_id.company_id', '=', company_id)
                    ]),
                },
                'activity': {
                    'last_login': request.env.user.login_date.isoformat() if request.env.user.login_date else None,
                    'total_users': request.env['res.users'].search_count([
                        ('company_id', '=', company_id)
                    ]),
                },
            }

            # Добавляем статистику для дополнительных моделей если они доступны
            optional_models = {
                'incidents': 'bcm.incident',
                'plans': 'bcm.plan',
                'risks': 'bcm.risk',
                'kpis': 'bcm.kpi',
            }

            for key, model_name in optional_models.items():
                model = request.env.get(model_name)
                if model:
                    stats['data'][key] = model.search_count([('company_id', '=', company_id)])
                else:
                    stats['data'][key] = 0

            return self._get_base_response_format(data=stats)

        except Exception as e:
            return self._handle_api_error(e, "Failed to fetch BCM stats")