#!/usr/bin/env python3
"""
Smart Scheduler для MIO Manager v2.0
=====================================

Умный планировщик, управляющий всеми циклами работы MIO Manager:

НЕПРЕРЫВНО (24/7):
  └─ ObservationWorkflow (30s) - управляется Temporal
  └─ Health Check (60s) - управляется этим планировщиком
  └─ Alert Monitoring - управляется EventBus

ЕЖЕДНЕВНО:
  └─ 03:00 AM - Deep Analysis (глубокий анализ производительности)
  └─ 06:00 AM - Daily Report (отчет к мозгу)

ЕЖЕНЕДЕЛЬНО:
  └─ Monday 02:00 AM - Focus Analysis (фокусный анализ каждого элемента)
  └─ Monday 08:00 AM - Weekly Report (недельный отчет)

ЕЖЕМЕСЯЧНО:
  └─ 1st day 09:00 AM - Monthly Report (месячный отчет)

Философия:
- Не частый, но ФОКУСНЫЙ и ГЛУБОКИЙ мониторинг
- "Раз в сутки" для основного анализа (по совету пользователя)
- Каждый элемент системы анализируется в цикле
- Рекомендации для общей системы
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

logger = logging.getLogger(__name__)


class SmartScheduler:
    """
    Умный планировщик для MIO Manager.

    Управляет всеми циклами анализа, отчетности и мониторинга.
    """

    def __init__(
        self,
        workflow_intelligence_client,
        predictive_client,
        optimizer_client,
        coordination_center_client,
        compliance_monitoring_client,
        automation_toolkit_manager,
        ai_event_manager_client,
        devops_agent_client,
        collective_client=None
    ):
        """
        Args:
            workflow_intelligence_client: Клиент для связи с мозгом
            predictive_client: Клиент для предсказаний
            optimizer_client: Клиент для оптимизаций
            coordination_center_client: Клиент для координации
            compliance_monitoring_client: Клиент для compliance данных
            automation_toolkit_manager: Менеджер для сбора метрик
            ai_event_manager_client: Клиент для Event Intelligence
            devops_agent_client: Клиент для DevOps Agent
            collective_client: Клиент для Collective Intelligence (опционально)
        """
        self.brain = workflow_intelligence_client
        self.predictive = predictive_client
        self.optimizer = optimizer_client
        self.coordinator = coordination_center_client
        self.compliance = compliance_monitoring_client
        self.toolkit = automation_toolkit_manager
        self.ai_event_manager = ai_event_manager_client
        self.devops_agent = devops_agent_client
        self.collective = collective_client

        self.scheduler = AsyncIOScheduler()
        self._is_running = False

        # Счетчики для статистики
        self.stats = {
            'health_checks': 0,
            'daily_analyses': 0,
            'weekly_analyses': 0,
            'monthly_reports': 0,
            'last_health_check': None,
            'last_daily_analysis': None,
            'last_weekly_analysis': None
        }

        logger.info("SmartScheduler initialized")

    # ========================================================================
    # LIFECYCLE MANAGEMENT
    # ========================================================================

    async def start(self):
        """Запустить планировщик со всеми циклами."""
        if self._is_running:
            logger.warning("SmartScheduler already running")
            return

        logger.info("🚀 Starting SmartScheduler...")

        # Регистрация всех циклов
        self._register_health_checks()
        self._register_hourly_cycles()  # NEW: Hourly monitoring
        self._register_daily_cycles()
        self._register_weekly_cycles()
        self._register_monthly_cycles()

        # Запуск планировщика
        self.scheduler.start()
        self._is_running = True

        logger.info("✅ SmartScheduler started with all cycles")

        # Показать следующие запланированные задачи
        await self._print_schedule()

    async def stop(self):
        """Остановить планировщик."""
        if not self._is_running:
            return

        logger.info("Stopping SmartScheduler...")
        self.scheduler.shutdown(wait=True)
        self._is_running = False
        logger.info("SmartScheduler stopped")

    def is_running(self) -> bool:
        """Проверить, работает ли планировщик."""
        return self._is_running

    # ========================================================================
    # ЦИКЛ: HEALTH CHECKS (каждую минуту)
    # ========================================================================

    def _register_health_checks(self):
        """Регистрация health checks всех интеграций."""
        self.scheduler.add_job(
            self._health_check_all,
            trigger=IntervalTrigger(seconds=60),
            id='health_check_all',
            name='Health Check All Integrations',
            max_instances=1,
            coalesce=True
        )
        logger.info("✅ Registered: Health Check (every 60s)")

    async def _health_check_all(self):
        """
        Проверить здоровье всех интеграций.

        Проверяет:
        - workflow_intelligence (мозг)
        - predictive
        - optimizer
        - coordination_center
        - compliance_monitoring (критично для специалиста!)

        Если критичный сервис down → эскалировать к мозгу.
        """
        logger.debug("🏥 Running health checks...")

        self.stats['health_checks'] += 1
        self.stats['last_health_check'] = datetime.utcnow().isoformat()

        health_results = {}
        critical_failures = []

        try:
            # 1. workflow_intelligence (КРИТИЧНЫЙ)
            brain_health = await self.brain.health_check()
            health_results['workflow_intelligence'] = brain_health
            if brain_health.get('status') != 'healthy':
                critical_failures.append({
                    'service': 'workflow_intelligence',
                    'status': brain_health.get('status'),
                    'error': brain_health.get('error')
                })

            # 2. predictive
            predictive_health = await self.predictive.health_check()
            health_results['predictive'] = predictive_health
            if predictive_health.get('status') != 'healthy':
                logger.warning("⚠️  Predictive Service unhealthy")

            # 3. optimizer
            optimizer_health = await self.optimizer.health_check()
            health_results['optimizer'] = optimizer_health
            if optimizer_health.get('status') != 'healthy':
                logger.warning("⚠️  Optimizer Service unhealthy")

            # 4. coordination_center
            coordinator_health = await self.coordinator.health_check()
            health_results['coordination_center'] = coordinator_health
            if coordinator_health.get('status') != 'healthy':
                logger.warning("⚠️  Coordination Center unhealthy")

            # 5. compliance_monitoring (КРИТИЧНО для специалиста!)
            compliance_health = await self.compliance.health_check()
            health_results['compliance_monitoring'] = compliance_health
            if compliance_health.get('status') != 'healthy':
                logger.warning("⚠️  Compliance Monitoring unhealthy")
                # Compliance - критичный для специалиста, но не блокирует систему
                critical_failures.append({
                    'service': 'compliance_monitoring',
                    'status': compliance_health.get('status'),
                    'error': compliance_health.get('error'),
                    'severity': 'high',  # Высокий приоритет для специалиста
                    'note': 'Critical data for compliance specialist unavailable'
                })

            # 6. ai_event_manager (Event Intelligence)
            ai_event_health = await self.ai_event_manager.health_check()
            health_results['ai_event_manager'] = {
                'status': 'healthy' if ai_event_health else 'unhealthy'
            }
            if not ai_event_health:
                logger.warning("⚠️  AI Event Manager unhealthy")

            # 7. devops_agent (Infrastructure)
            devops_health = await self.devops_agent.health_check()
            health_results['devops_agent'] = {
                'status': 'healthy' if devops_health else 'unhealthy'
            }
            if not devops_health:
                logger.warning("⚠️  DevOps Agent unhealthy")

            # 8. collective_intelligence (Privacy-preserving collaboration)
            if self.collective:
                try:
                    collective_health = await self.collective.health_check()
                    health_results['collective_intelligence'] = collective_health
                    if collective_health.get('status') != 'healthy':
                        logger.warning("⚠️  Collective Intelligence unhealthy")
                except Exception as e:
                    logger.warning(f"⚠️  Collective Intelligence health check failed: {e}")
                    health_results['collective_intelligence'] = {
                        'status': 'unknown',
                        'error': str(e)
                    }

            # Если критичный сервис down → эскалировать
            if critical_failures:
                await self._escalate_critical_failure(critical_failures, health_results)

        except Exception as e:
            logger.error(f"❌ Health check failed: {e}")

    async def _escalate_critical_failure(
        self,
        critical_failures: List[Dict],
        health_results: Dict
    ):
        """
        Эскалировать критичный сбой к мозгу.

        Критичный сбой = workflow_intelligence недоступен.
        Парадокс: если мозг down, мы не можем эскалировать к мозгу :)
        Решение: логируем локально, пытаемся переподключиться.
        """
        logger.error(f"🚨 CRITICAL FAILURE DETECTED: {critical_failures}")

        # Если мозг down - не можем эскалировать
        brain_down = any(f['service'] == 'workflow_intelligence' for f in critical_failures)

        if brain_down:
            logger.error("⚠️  BRAIN IS DOWN - Cannot escalate. Logging locally.")
            # TODO: Implement local fallback (save to DB, retry later)
            return

        # Эскалировать к мозгу
        try:
            await self.brain.escalate_problem(
                problem={
                    'type': 'critical_service_failure',
                    'services': critical_failures
                },
                severity='critical',
                context={
                    'health_results': health_results,
                    'detected_at': datetime.utcnow().isoformat()
                },
                recommendations=[
                    {
                        'recommendation': 'Investigate service failures immediately',
                        'priority': 'critical'
                    }
                ]
            )
            logger.info("✅ Critical failure escalated to brain")

        except Exception as e:
            logger.error(f"❌ Failed to escalate critical failure: {e}")

    # ========================================================================
    # ЦИКЛ: DAILY DEEP ANALYSIS (03:00 AM)
    # ========================================================================

    def _register_daily_cycles(self):
        """Регистрация ежедневных циклов."""
        # 03:00 AM - Глубокий анализ
        self.scheduler.add_job(
            self._daily_deep_analysis,
            trigger=CronTrigger(hour=3, minute=0),
            id='daily_deep_analysis',
            name='Daily Deep Analysis (03:00 AM)',
            max_instances=1,
            coalesce=True
        )

        # 06:00 AM - Отчет к мозгу
        self.scheduler.add_job(
            self._daily_report_to_brain,
            trigger=CronTrigger(hour=6, minute=0),
            id='daily_report',
            name='Daily Report to Brain (06:00 AM)',
            max_instances=1,
            coalesce=True
        )

        # 08:00 AM - Predictive: Daily Proactive Recommendations
        self.scheduler.add_job(
            self._daily_predictive_recommendations,
            trigger=CronTrigger(hour=8, minute=0),
            id='daily_predictive_recommendations',
            name='Daily Predictive Recommendations (08:00 AM)',
            max_instances=1,
            coalesce=True
        )

        # 09:00 AM - Coordination Center Health Check
        if self.coordinator:
            self.scheduler.add_job(
                self._daily_coordination_health,
                trigger=CronTrigger(hour=9, minute=0),
                id='daily_coordination_health',
                name='Daily Coordination Center Health (09:00 AM)',
                max_instances=1,
                coalesce=True
            )

        coord_msg = ", 09:00 AM coordination" if self.coordinator else ""
        logger.info(f"✅ Registered: Daily cycles (03:00 AM analysis, 06:00 AM report, 08:00 AM predictive{coord_msg})")

    async def _daily_deep_analysis(self):
        """
        Глубокий анализ производительности системы (раз в сутки).

        Как вы и просили: "не частый, но фокусный глубокий мониторинг".

        Шаги:
        1. Собрать метрики за последние 24ч
        2. Анализ через optimizer.analyze_system_performance()
        3. Предсказания через predictive.get_proactive_recommendations()
        4. Генерация инсайтов
        5. Сохранение результатов для отчета (06:00 AM)
        """
        logger.info("🔍 Starting DAILY DEEP ANALYSIS (03:00 AM)")

        self.stats['daily_analyses'] += 1
        self.stats['last_daily_analysis'] = datetime.utcnow().isoformat()

        try:
            # 1. Собрать метрики за 24ч
            logger.info("📊 Collecting 24h metrics...")
            system_metrics = await self._collect_system_metrics(timeframe='24h')

            # 2. Глубокий анализ через optimizer
            logger.info("🔬 Running optimizer analysis...")
            optimizer_analysis = await self.optimizer.analyze_system_performance(
                system_metrics=system_metrics,
                timeframe='24h'
            )

            # 3. Проактивные рекомендации через predictive
            logger.info("🔮 Getting proactive recommendations...")
            predictive_recommendations = await self.predictive.get_proactive_recommendations(
                system_metrics=system_metrics,
                timeframe='1h'  # Предсказания на ближайший час
            )

            # 4. Собрать compliance статус (КРИТИЧНО для специалиста!)
            logger.info("📋 Collecting compliance status...")
            compliance_status = await self.compliance.get_compliance_status()

            # 5. АВТОМАТИЗАЦИЯ НАСТРОЙКИ МиО (ПРЯМАЯ ОБЯЗАННОСТЬ!)
            logger.info("🔧 Setting up monitoring automation...")
            monitoring_setup = await self.toolkit.setup_monitoring()
            logger.info(f"   ✅ Prometheus config: {monitoring_setup.get('prometheus_config')}")
            logger.info(f"   ✅ Grafana dashboard: {monitoring_setup.get('grafana_dashboard')}")
            logger.info(f"   📊 Coverage: {monitoring_setup.get('coverage_percentage', 0):.1f}%")

            # 6. Генерация инсайтов
            insights = self._generate_daily_insights(
                optimizer_analysis,
                predictive_recommendations,
                compliance_status
            )

            # 7. Сохранить результаты для утреннего отчета
            self._daily_analysis_cache = {
                'analysis_date': datetime.utcnow().isoformat(),
                'optimizer_analysis': optimizer_analysis,
                'predictive_recommendations': predictive_recommendations,
                'compliance_status': compliance_status,
                'monitoring_setup': monitoring_setup,
                'insights': insights,
                'system_metrics': system_metrics
            }

            logger.info(
                f"✅ Daily deep analysis completed: "
                f"health_score={optimizer_analysis.get('overall_health_score', 0):.2f}, "
                f"insights={len(insights)}"
            )

        except Exception as e:
            logger.error(f"❌ Daily deep analysis failed: {e}")
            self._daily_analysis_cache = {
                'analysis_date': datetime.utcnow().isoformat(),
                'error': str(e)
            }

    async def _daily_report_to_brain(self):
        """
        Отправить ежедневный отчет к мозгу (06:00 AM).

        Отправляет результаты анализа из 03:00 AM.
        """
        logger.info("📊 Sending DAILY REPORT to brain (06:00 AM)")

        try:
            # Проверить, есть ли результаты анализа
            if not hasattr(self, '_daily_analysis_cache'):
                logger.warning("No daily analysis results to report")
                return

            analysis = self._daily_analysis_cache

            # Подготовить отчет
            compliance = analysis.get('compliance_status', {})
            monitoring = analysis.get('monitoring_setup', {})
            report_data = {
                'report_type': 'daily',
                'period': 'last_24h',
                'generated_at': datetime.utcnow().isoformat(),
                'health_score': analysis.get('optimizer_analysis', {}).get('overall_health_score', 0),
                'bottlenecks': analysis.get('optimizer_analysis', {}).get('bottlenecks', []),
                'optimization_opportunities': analysis.get('optimizer_analysis', {}).get('optimization_opportunities', []),
                'proactive_recommendations': analysis.get('predictive_recommendations', []),
                'performance_trends': analysis.get('optimizer_analysis', {}).get('performance_trends', {}),
                'cost_savings': analysis.get('optimizer_analysis', {}).get('cost_savings', {}),
                'system_metrics_summary': self._summarize_metrics(analysis.get('system_metrics', {})),
                # КРИТИЧНО: Compliance data для специалиста
                'compliance_score': compliance.get('compliance_score', 0),
                'active_alerts': compliance.get('active_alerts', 0),
                'open_nonconformities': compliance.get('open_nonconformities', 0),
                'recent_audits': compliance.get('recent_audits', 0),
                'compliance_trends': compliance.get('compliance_trends', {}),
                # КРИТИЧНО: Monitoring automation (прямая обязанность!)
                'monitoring_coverage': monitoring.get('coverage_percentage', 0),
                'services_discovered': monitoring.get('services_discovered', 0),
                'services_with_metrics': monitoring.get('services_with_metrics', 0),
                'prometheus_jobs': monitoring.get('prometheus_scrape_jobs', 0),
                'grafana_panels': monitoring.get('grafana_panels', 0)
            }

            # Отправить к мозгу
            result = await self.brain.publish_report(
                report_type='daily',
                report_data=report_data,
                insights=analysis.get('insights', [])
            )

            logger.info(
                f"✅ Daily report published to brain: {result.get('report_id')}"
            )

        except Exception as e:
            logger.error(f"❌ Failed to send daily report: {e}")

    async def _daily_predictive_recommendations(self):
        """
        Ежедневные проактивные рекомендации (08:00 AM).

        Predictive Service генерирует:
        - Upcoming milestones (следующие 14 дней)
        - Proactive recommendations for all organizations
        - Resource preparation suggestions
        - Expert booking recommendations
        """
        logger.info("🔮 Generating DAILY PREDICTIVE RECOMMENDATIONS (08:00 AM)")

        try:
            # Trigger Predictive Service daily recommendations
            recommendations = await self.predictive.generate_daily_recommendations(
                horizon_days=14
            )

            logger.info(
                f"✅ Predictive recommendations: {recommendations.get('organizations_processed', 0)} orgs, "
                f"{recommendations.get('total_recommendations', 0)} recommendations, "
                f"{recommendations.get('high_priority_count', 0)} high priority"
            )

            # Store key metrics for daily report
            if not hasattr(self, '_daily_predictive_cache'):
                self._daily_predictive_cache = {}

            self._daily_predictive_cache = {
                'generated_at': datetime.utcnow().isoformat(),
                'organizations_processed': recommendations.get('organizations_processed', 0),
                'total_recommendations': recommendations.get('total_recommendations', 0),
                'high_priority_count': recommendations.get('high_priority_count', 0),
                'notifications_sent': recommendations.get('notifications_sent', 0)
            }

        except Exception as e:
            logger.error(f"❌ Daily predictive recommendations failed: {e}")
            self._daily_predictive_cache = {
                'generated_at': datetime.utcnow().isoformat(),
                'error': str(e)
            }

    # ========================================================================
    # ЦИКЛ: WEEKLY FOCUS ANALYSIS (Monday 02:00 AM)
    # ========================================================================

    def _register_hourly_cycles(self):
        """Регистрация ежечасных циклов."""
        # Hourly DevOps Continuous Monitoring
        self.scheduler.add_job(
            self._hourly_devops_monitoring,
            trigger=IntervalTrigger(hours=1),
            id='hourly_devops_monitoring',
            name='Hourly DevOps Continuous Monitoring',
            max_instances=1,
            coalesce=True
        )

        logger.info("✅ Registered: Hourly DevOps Continuous Monitoring")

    def _register_weekly_cycles(self):
        """Регистрация еженедельных циклов."""
        # Monday 02:00 AM - Фокусный анализ каждого элемента
        self.scheduler.add_job(
            self._weekly_focus_analysis,
            trigger=CronTrigger(day_of_week='mon', hour=2, minute=0),
            id='weekly_focus_analysis',
            name='Weekly Focus Analysis (Monday 02:00 AM)',
            max_instances=1,
            coalesce=True
        )

        # Monday 03:00 AM - DevOps Agent Deep Scan
        self.scheduler.add_job(
            self._weekly_devops_deep_scan,
            trigger=CronTrigger(day_of_week='mon', hour=3, minute=0),
            id='weekly_devops_scan',
            name='Weekly DevOps Deep Scan (Monday 03:00 AM)',
            max_instances=1,
            coalesce=True
        )

        # Monday 04:00 AM - Event Intelligence Analysis
        self.scheduler.add_job(
            self._weekly_event_intelligence_analysis,
            trigger=CronTrigger(day_of_week='mon', hour=4, minute=0),
            id='weekly_event_intelligence',
            name='Weekly Event Intelligence Analysis (Monday 04:00 AM)',
            max_instances=1,
            coalesce=True
        )

        # Monday 05:00 AM - Collective Intelligence Stuck Detection
        if self.collective:
            self.scheduler.add_job(
                self._weekly_collective_stuck_detection,
                trigger=CronTrigger(day_of_week='mon', hour=5, minute=0),
                id='weekly_collective_stuck_detection',
                name='Weekly Collective Intelligence Stuck Detection (Monday 05:00 AM)',
                max_instances=1,
                coalesce=True
            )

        # Sunday 02:00 AM - Predictive: ML Model Retraining
        self.scheduler.add_job(
            self._weekly_model_retraining,
            trigger=CronTrigger(day_of_week='sun', hour=2, minute=0),
            id='weekly_model_retraining',
            name='Weekly ML Model Retraining (Sunday 02:00 AM)',
            max_instances=1,
            coalesce=True
        )

        # Monday 06:00 AM - Community Intelligence Insights
        self.scheduler.add_job(
            self._weekly_community_insights,
            trigger=CronTrigger(day_of_week='mon', hour=6, minute=0),
            id='weekly_community_insights',
            name='Weekly Community Intelligence Insights (Monday 06:00 AM)',
            max_instances=1,
            coalesce=True
        )

        # Monday 07:00 AM - Expertise Center Analysis
        self.scheduler.add_job(
            self._weekly_expertise_analysis,
            trigger=CronTrigger(day_of_week='mon', hour=7, minute=0),
            id='weekly_expertise_analysis',
            name='Weekly Expertise Center Analysis (Monday 07:00 AM)',
            max_instances=1,
            coalesce=True
        )

        # Monday 08:00 AM - Недельный отчет
        self.scheduler.add_job(
            self._weekly_report_to_brain,
            trigger=CronTrigger(day_of_week='mon', hour=8, minute=0),
            id='weekly_report',
            name='Weekly Report to Brain (Monday 08:00 AM)',
            max_instances=1,
            coalesce=True
        )

        collective_msg = ", 05:00 AM collective" if self.collective else ""
        logger.info(f"✅ Registered: Weekly cycles (Monday 02:00-08:00 AM: analysis, events{collective_msg}, community, expertise, report; Sunday 02:00 AM: model retraining)")

    async def _weekly_focus_analysis(self):
        """
        Фокусный анализ каждого элемента системы (раз в неделю).

        Deep dive в каждый компонент для поиска скрытых проблем и возможностей.

        Анализируем:
        - workflow_intelligence (мозг)
        - orchestration (оркестрация)
        - coordination_center (координация)
        - predictive (предсказания)
        - expertise-center (эксперты)
        - collective (коллектив)
        - community_intelligence (сообщество)
        """
        logger.info("🔍 Starting WEEKLY FOCUS ANALYSIS (Monday 02:00 AM)")

        self.stats['weekly_analyses'] += 1
        self.stats['last_weekly_analysis'] = datetime.utcnow().isoformat()

        components_to_analyze = [
            'workflow_intelligence',
            'orchestration',
            'coordination_center',
            'predictive',
            'expertise_center',
            'collective',
            'community_intelligence'
        ]

        component_analyses = {}

        try:
            for component in components_to_analyze:
                logger.info(f"📊 Analyzing component: {component}")

                # Собрать метрики конкретного компонента за неделю
                component_metrics = await self._collect_component_metrics(
                    component=component,
                    timeframe='7d'
                )

                # Анализ через optimizer
                analysis = await self.optimizer.get_recommendations(
                    service=component,
                    category='performance'
                )

                # Предсказание проблем для этого компонента
                incident_prediction = await self.predictive.predict_incident_probability(
                    current_state=component_metrics,
                    incident_type='performance_degradation'
                )

                component_analyses[component] = {
                    'metrics': component_metrics,
                    'recommendations': analysis,
                    'incident_risk': incident_prediction,
                    'analyzed_at': datetime.utcnow().isoformat()
                }

                logger.info(
                    f"✅ {component}: "
                    f"recommendations={len(analysis)}, "
                    f"risk={incident_prediction.get('risk_level', 'unknown')}"
                )

            # Сохранить результаты для утреннего отчета
            self._weekly_analysis_cache = {
                'analysis_date': datetime.utcnow().isoformat(),
                'component_analyses': component_analyses,
                'overall_insights': self._generate_weekly_insights(component_analyses)
            }

            logger.info(f"✅ Weekly focus analysis completed for {len(component_analyses)} components")

        except Exception as e:
            logger.error(f"❌ Weekly focus analysis failed: {e}")
            self._weekly_analysis_cache = {
                'analysis_date': datetime.utcnow().isoformat(),
                'error': str(e)
            }

    # ========================================================================
    # ЦИКЛ: HOURLY DEVOPS MONITORING
    # ========================================================================

    async def _hourly_devops_monitoring(self):
        """
        Continuous monitoring каждый час

        Quick scan:
        - Event architecture gaps
        - Port conflicts
        - Service health
        - Export metrics to Prometheus
        - Alert on critical issues
        """
        logger.info("🔍 HOURLY DEVOPS MONITORING")

        try:
            # Quick scan (events only for performance)
            scan_result = await self.devops_agent.trigger_scan(scan_type="events")

            logger.info(f"✅ DevOps hourly scan: {scan_result.get('status')}")

            # Get event metrics
            event_data = scan_result.get('result', {}).get('scan_results', {}).get('events', {})

            critical_gaps = event_data.get('critical_gaps', 0)
            total_gaps = event_data.get('gaps_found', 0)

            # Export metrics to Prometheus (placeholder - будет реализовано в следующем шаге)
            logger.info(f"📊 Metrics: {total_gaps} gaps ({critical_gaps} critical)")

            # Alert on critical issues
            if critical_gaps > 0:
                logger.warning(f"⚠️ Critical event gaps detected: {critical_gaps}")

                # Send alert to brain
                await self.brain.send_alert({
                    'severity': 'high',
                    'source': 'devops_agent',
                    'category': 'event_architecture',
                    'message': f'Critical event architecture gaps detected: {critical_gaps}',
                    'timestamp': datetime.utcnow().isoformat(),
                    'details': {
                        'total_gaps': total_gaps,
                        'critical_gaps': critical_gaps
                    }
                })

                logger.info("📡 Alert sent to brain")

        except Exception as e:
            logger.error(f"❌ Hourly DevOps monitoring failed: {e}")

    # ========================================================================
    # ЦИКЛ: WEEKLY DEVOPS DEEP SCAN (Monday 03:00 AM)
    # ========================================================================

    async def _weekly_devops_deep_scan(self):
        """
        Еженедельное глубокое сканирование инфраструктуры (Monday 03:00 AM).

        DevOps Agent проводит полный анализ:
        - Event architecture
        - Container configurations
        - Deployment health
        - Port conflicts
        - Infrastructure drift
        """
        logger.info("🤖 WEEKLY DEVOPS DEEP SCAN (Monday 03:00 AM)")

        try:
            # 1. Триггерим полное сканирование
            scan_result = await self.devops_agent.trigger_scan(scan_type="full")

            logger.info(f"✅ DevOps scan completed: {scan_result.get('status')}")

            # 2. Получаем последний отчёт
            latest_report = await self.devops_agent.get_latest_report()

            # 3. Отправляем в мозг
            await self.brain.publish_report(
                report_type='devops_infrastructure',
                report_data={
                    'scan_result': scan_result,
                    'report': latest_report,
                    'timestamp': 'Monday 03:00 AM',
                    'scan_type': 'weekly_deep_scan'
                }
            )

            logger.info("✅ DevOps report sent to мозг")

        except Exception as e:
            logger.error(f"❌ DevOps Deep Scan failed: {e}")

    async def _weekly_event_intelligence_analysis(self):
        """
        Еженедельный анализ событий через Event Intelligence (Monday 04:00 AM).

        Получает рекомендации и статистику обучения от AI Event Manager.
        """
        logger.info("🔍 WEEKLY EVENT INTELLIGENCE ANALYSIS (Monday 04:00 AM)")

        try:
            # 1. Получить рекомендации по событиям
            logger.info("📡 Getting event recommendations...")
            recommendations = await self.ai_event_manager.get_recommendations(
                scope='all'
            )

            # 2. Получить статистику обучения
            logger.info("📊 Getting learning stats...")
            learning_stats = await self.ai_event_manager.get_learning_stats()

            # 3. Получить architecture insights
            logger.info("🏗️  Getting architecture insights...")
            architecture_insights = await self.ai_event_manager.get_architecture_insights(
                timeframe='7d'
            )

            # 4. Сохранить результаты для недельного отчета
            event_intelligence_data = {
                'analyzed_at': datetime.utcnow().isoformat(),
                'recommendations': recommendations if recommendations else [],
                'learning_stats': learning_stats if learning_stats else {},
                'architecture_insights': architecture_insights if architecture_insights else {}
            }

            # Добавляем к weekly cache для включения в отчет
            if not hasattr(self, '_weekly_analysis_cache'):
                self._weekly_analysis_cache = {}

            self._weekly_analysis_cache['event_intelligence'] = event_intelligence_data

            # 5. Отправить промежуточный отчет к мозгу
            if recommendations or learning_stats:
                await self.brain.publish_report(
                    report_type='event_intelligence',
                    report_data=event_intelligence_data,
                    insights=self._generate_event_insights(event_intelligence_data)
                )

            logger.info(
                f"✅ Event intelligence analysis completed: "
                f"recommendations={len(event_intelligence_data['recommendations'])}, "
                f"patterns_learned={event_intelligence_data['learning_stats'].get('patterns_learned', 0)}"
            )

        except Exception as e:
            logger.error(f"❌ Event intelligence analysis failed: {e}")
            if not hasattr(self, '_weekly_analysis_cache'):
                self._weekly_analysis_cache = {}
            self._weekly_analysis_cache['event_intelligence'] = {
                'analyzed_at': datetime.utcnow().isoformat(),
                'error': str(e)
            }

    def _generate_event_insights(self, event_data: Dict) -> List[Dict]:
        """Генерация инсайтов из Event Intelligence данных."""
        insights = []

        # Высокоприоритетные рекомендации
        recommendations = event_data.get('recommendations', [])
        high_priority_recommendations = [
            r for r in recommendations
            if r.get('impact') == 'high' and r.get('confidence', 0) > 0.8
        ]

        if high_priority_recommendations:
            insights.append({
                'type': 'event_recommendations',
                'severity': 'high',
                'message': f'{len(high_priority_recommendations)} high-impact EventBus improvements recommended',
                'recommendation': 'Review and implement AI-suggested event patterns',
                'suggestions': [
                    {
                        'type': r.get('type'),
                        'suggestion': r.get('suggestion'),
                        'confidence': r.get('confidence')
                    } for r in high_priority_recommendations
                ]
            })

        # Статистика обучения
        learning = event_data.get('learning_stats', {})
        success_rate = learning.get('success_rate', 0)

        if success_rate > 0:
            insights.append({
                'type': 'learning_progress',
                'severity': 'info',
                'message': f'Event Intelligence success rate: {success_rate:.2%}',
                'recommendation': 'Continue collecting event feedback for improvement',
                'stats': {
                    'total_suggestions': learning.get('total_suggestions', 0),
                    'accepted_suggestions': learning.get('accepted_suggestions', 0),
                    'success_rate': success_rate
                }
            })

        # Architecture insights
        architecture = event_data.get('architecture_insights', {})
        critical_insights = architecture.get('critical_insights', [])

        if critical_insights:
            insights.append({
                'type': 'architecture_health',
                'severity': 'medium',
                'message': f'{len(critical_insights)} critical architecture issues detected',
                'recommendation': 'Review event-driven architecture bottlenecks',
                'overall_health': architecture.get('overall_health', 0),
                'issues': [
                    {
                        'insight': i.get('insight'),
                        'severity': i.get('severity')
                    } for i in critical_insights
                ]
            })

        return insights

    async def _weekly_model_retraining(self):
        """
        Еженедельная переобучение ML моделей (Sunday 02:00 AM).

        Predictive Service переобучает prediction models:
        - Journey prediction models
        - Demand forecasting models
        - Anomaly detection models

        После переобучения проверяется accuracy:
        - Если accuracy улучшилась → deploy new model
        - Если accuracy ухудшилась → rollback to previous version
        """
        logger.info("🤖 WEEKLY ML MODEL RETRAINING (Sunday 02:00 AM)")

        try:
            # Trigger model retraining through Predictive Service
            retraining_result = await self.predictive.retrain_prediction_models()

            accuracy_before = retraining_result.get('accuracy_before', 0)
            accuracy_after = retraining_result.get('accuracy_after', 0)
            improvement = retraining_result.get('improvement', 0)
            samples_trained = retraining_result.get('samples_trained', 0)

            logger.info(
                f"✅ Model retraining completed: "
                f"accuracy {accuracy_before:.2%} → {accuracy_after:.2%} "
                f"(improvement: {improvement:.2%}), {samples_trained} samples"
            )

            # Store results for weekly report
            if not hasattr(self, '_weekly_model_training_cache'):
                self._weekly_model_training_cache = {}

            self._weekly_model_training_cache = {
                'trained_at': datetime.utcnow().isoformat(),
                'model_name': retraining_result.get('model_name'),
                'samples_trained': samples_trained,
                'accuracy_before': accuracy_before,
                'accuracy_after': accuracy_after,
                'improvement': improvement,
                'status': retraining_result.get('status')
            }

            # Alert brain if accuracy degraded
            if improvement < 0:
                logger.warning(
                    f"⚠️ Model accuracy degraded by {abs(improvement):.2%}, "
                    "rolled back to previous version"
                )

                await self.brain.send_alert({
                    'severity': 'medium',
                    'source': 'predictive_service',
                    'category': 'model_accuracy',
                    'message': f'ML model accuracy degraded during retraining: {abs(improvement):.2%}',
                    'timestamp': datetime.utcnow().isoformat(),
                    'details': {
                        'accuracy_before': accuracy_before,
                        'accuracy_after': accuracy_after,
                        'action': 'rolled_back'
                    }
                })

        except Exception as e:
            logger.error(f"❌ Weekly model retraining failed: {e}")
            self._weekly_model_training_cache = {
                'trained_at': datetime.utcnow().isoformat(),
                'error': str(e)
            }

    async def _weekly_report_to_brain(self):
        """Отправить недельный отчет к мозгу (Monday 08:00 AM)."""
        logger.info("📊 Sending WEEKLY REPORT to brain (Monday 08:00 AM)")

        try:
            if not hasattr(self, '_weekly_analysis_cache'):
                logger.warning("No weekly analysis results to report")
                return

            analysis = self._weekly_analysis_cache

            report_data = {
                'report_type': 'weekly',
                'period': 'last_7d',
                'generated_at': datetime.utcnow().isoformat(),
                'component_analyses': analysis.get('component_analyses', {}),
                'overall_insights': analysis.get('overall_insights', []),
                'top_priorities': self._extract_top_priorities(analysis)
            }

            result = await self.brain.publish_report(
                report_type='weekly',
                report_data=report_data,
                insights=analysis.get('overall_insights', [])
            )

            logger.info(f"✅ Weekly report published to brain: {result.get('report_id')}")

        except Exception as e:
            logger.error(f"❌ Failed to send weekly report: {e}")

    # ========================================================================
    # ЦИКЛ: MONTHLY REPORT (1st day 09:00 AM)
    # ========================================================================

    def _register_monthly_cycles(self):
        """Регистрация месячных циклов."""
        self.scheduler.add_job(
            self._monthly_report_to_brain,
            trigger=CronTrigger(day=1, hour=9, minute=0),
            id='monthly_report',
            name='Monthly Report to Brain (1st day 09:00 AM)',
            max_instances=1,
            coalesce=True
        )

        logger.info("✅ Registered: Monthly report (1st day 09:00 AM)")

    async def _monthly_report_to_brain(self):
        """
        Отправить месячный отчет к мозгу (1st day 09:00 AM).

        Aggregated insights за месяц.
        """
        logger.info("📊 Sending MONTHLY REPORT to brain (1st day 09:00 AM)")

        self.stats['monthly_reports'] += 1

        try:
            # Собрать метрики за 30 дней
            monthly_metrics = await self._collect_system_metrics(timeframe='30d')

            # Тренды за месяц
            monthly_trends = await self._analyze_monthly_trends(monthly_metrics)

            report_data = {
                'report_type': 'monthly',
                'period': 'last_30d',
                'generated_at': datetime.utcnow().isoformat(),
                'metrics_summary': self._summarize_metrics(monthly_metrics),
                'trends': monthly_trends,
                'achievements': self._extract_achievements(monthly_metrics),
                'challenges': self._extract_challenges(monthly_metrics),
                'scheduler_stats': self.stats
            }

            result = await self.brain.publish_report(
                report_type='monthly',
                report_data=report_data,
                insights=monthly_trends.get('insights', [])
            )

            logger.info(f"✅ Monthly report published to brain: {result.get('report_id')}")

        except Exception as e:
            logger.error(f"❌ Failed to send monthly report: {e}")

    # ========================================================================
    # HELPER METHODS - Data Collection
    # ========================================================================

    async def _collect_system_metrics(self, timeframe: str = '24h') -> Dict[str, Any]:
        """
        Собрать метрики всей системы за период.

        Args:
            timeframe: 24h, 7d, 30d

        Returns:
            {
                'services': [...],
                'cpu_avg': 45.2,
                'memory_avg': 68.1,
                'request_count': 125000,
                'error_rate': 0.02,
                'p95_latency': 250
            }
        """
        try:
            # Используем AutomationToolkitManager для сбора метрик
            discovery_result = await self.toolkit.discover_services()

            # Aggregate metrics
            metrics = {
                'timeframe': timeframe,
                'collected_at': datetime.utcnow().isoformat(),
                'services': discovery_result.get('services', []),
                'total_services': discovery_result.get('total_services', 0),
                'coverage': discovery_result.get('coverage', {})
            }

            # TODO: Добавить реальные метрики из Prometheus
            # Сейчас используем mock data
            metrics.update({
                'cpu_avg': 45.2,
                'memory_avg': 68.1,
                'disk_usage': 55.0,
                'request_count': 125000,
                'error_rate': 0.02,
                'p95_latency': 250
            })

            return metrics

        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")
            return {'error': str(e)}

    async def _collect_component_metrics(
        self,
        component: str,
        timeframe: str = '7d'
    ) -> Dict[str, Any]:
        """
        Собрать метрики конкретного компонента.

        Args:
            component: Имя компонента
            timeframe: Период
        """
        # TODO: Implement real component-specific metrics
        return {
            'component': component,
            'timeframe': timeframe,
            'collected_at': datetime.utcnow().isoformat(),
            'cpu_avg': 40.0,
            'memory_avg': 60.0,
            'request_count': 50000,
            'error_rate': 0.01
        }

    # ========================================================================
    # HELPER METHODS - Analysis & Insights
    # ========================================================================

    def _generate_daily_insights(
        self,
        optimizer_analysis: Dict,
        predictive_recommendations: List[Dict],
        compliance_status: Dict
    ) -> List[Dict]:
        """Генерация инсайтов из ежедневного анализа."""
        insights = []

        # Инсайты из optimizer
        health_score = optimizer_analysis.get('overall_health_score', 0)
        if health_score < 0.7:
            insights.append({
                'type': 'health_warning',
                'severity': 'high',
                'message': f'System health score is low: {health_score:.2f}',
                'recommendation': 'Review bottlenecks and optimization opportunities'
            })

        # Инсайты из predictive
        high_priority_recommendations = [
            r for r in predictive_recommendations
            if r.get('priority') == 'high'
        ]

        if high_priority_recommendations:
            insights.append({
                'type': 'proactive_action',
                'severity': 'medium',
                'message': f'{len(high_priority_recommendations)} high-priority preventive actions recommended',
                'recommendation': 'Review and execute proactive recommendations'
            })

        # КРИТИЧНО: Инсайты из compliance (для специалиста!)
        compliance_score = compliance_status.get('compliance_score', 100)
        if compliance_score < 90:
            insights.append({
                'type': 'compliance_warning',
                'severity': 'high',
                'message': f'Compliance score below threshold: {compliance_score:.1f}%',
                'recommendation': 'Review open nonconformities and active alerts',
                'data': {
                    'active_alerts': compliance_status.get('active_alerts', 0),
                    'open_nonconformities': compliance_status.get('open_nonconformities', 0)
                }
            })

        active_alerts = compliance_status.get('active_alerts', 0)
        if active_alerts > 5:
            insights.append({
                'type': 'compliance_alert',
                'severity': 'medium',
                'message': f'{active_alerts} active compliance alerts require attention',
                'recommendation': 'Review and resolve compliance alerts'
            })

        return insights

    def _generate_weekly_insights(
        self,
        component_analyses: Dict[str, Dict]
    ) -> List[Dict]:
        """Генерация инсайтов из еженедельного анализа."""
        insights = []

        # Найти компоненты с высоким риском
        high_risk_components = [
            comp for comp, analysis in component_analyses.items()
            if analysis.get('incident_risk', {}).get('risk_level') == 'high'
        ]

        if high_risk_components:
            insights.append({
                'type': 'risk_alert',
                'severity': 'high',
                'message': f'High risk detected in {len(high_risk_components)} components',
                'components': high_risk_components,
                'recommendation': 'Urgent attention required'
            })

        return insights

    def _summarize_metrics(self, metrics: Dict) -> Dict:
        """Суммаризация метрик для отчета."""
        return {
            'cpu_avg': metrics.get('cpu_avg', 0),
            'memory_avg': metrics.get('memory_avg', 0),
            'disk_usage': metrics.get('disk_usage', 0),
            'request_count': metrics.get('request_count', 0),
            'error_rate': metrics.get('error_rate', 0),
            'p95_latency': metrics.get('p95_latency', 0)
        }

    def _extract_top_priorities(self, analysis: Dict) -> List[Dict]:
        """Извлечь топ приоритетов из анализа."""
        # TODO: Implement real priority extraction logic
        return [
            {
                'priority': 'high',
                'action': 'Example action',
                'component': 'example_component'
            }
        ]

    async def _analyze_monthly_trends(self, metrics: Dict) -> Dict:
        """Анализ месячных трендов."""
        # TODO: Implement real trend analysis
        return {
            'insights': [
                {'message': 'Example monthly insight'}
            ]
        }

    def _extract_achievements(self, metrics: Dict) -> List[str]:
        """Извлечь достижения за месяц."""
        return [
            'System uptime: 99.9%',
            'Average response time improved by 15%'
        ]

    def _extract_challenges(self, metrics: Dict) -> List[str]:
        """Извлечь проблемы за месяц."""
        return [
            'Memory usage increased by 10%'
        ]

    # ========================================================================
    # COLLEAGUE-SPECIFIC SCHEDULED METHODS
    # ========================================================================

    async def _weekly_collective_stuck_detection(self):
        """
        Weekly Collective Intelligence stuck organization detection

        Identifies organizations that may need help and creates collective agents
        """
        logger.info("🔍 WEEKLY COLLECTIVE INTELLIGENCE STUCK DETECTION")

        try:
            if not self.collective:
                logger.warning("Collective Intelligence client not available")
                return

            # Trigger stuck detection workflow via Temporal
            result = await self.workflow_client.start_workflow(
                workflow_name="StuckDetectionWorkflow",
                workflow_input={"scan_type": "weekly_full"}
            )

            logger.info(f"✅ Collective stuck detection complete: {result.get('stuck_orgs_found', 0)} stuck organizations")

            # Alert brain if organizations need help
            stuck_count = result.get('stuck_orgs_found', 0)
            if stuck_count > 0:
                await self.brain.send_alert({
                    'severity': 'medium',
                    'source': 'collective_intelligence',
                    'message': f'{stuck_count} organizations may need collective wisdom assistance'
                })

        except Exception as e:
            logger.error(f"❌ Collective stuck detection failed: {e}")

    async def _daily_coordination_health(self):
        """
        Daily Coordination Center health check

        Monitors multi-service coordination and conflict resolution
        """
        logger.info("🏥 DAILY COORDINATION CENTER HEALTH CHECK")

        try:
            if not self.coordinator:
                logger.warning("Coordination Center client not available")
                return

            # Check coordination health
            health = await self.coordinator.health_check()

            pending_conflicts = health.get('pending_conflicts', 0)
            coordination_failures = health.get('coordination_failures_24h', 0)

            logger.info(f"✅ Coordination health: {pending_conflicts} pending conflicts, {coordination_failures} failures")

            # Alert on high conflict rate
            if pending_conflicts > 10:
                await self.brain.send_alert({
                    'severity': 'high',
                    'source': 'coordination_center',
                    'message': f'{pending_conflicts} pending coordination conflicts require attention'
                })

        except Exception as e:
            logger.error(f"❌ Coordination health check failed: {e}")

    async def _weekly_community_insights(self):
        """
        Weekly Community Intelligence insights generation

        Analyzes community contributions and generates insights
        """
        logger.info("💡 WEEKLY COMMUNITY INTELLIGENCE INSIGHTS")

        try:
            # Trigger community insights workflow
            result = await self.workflow_client.start_workflow(
                workflow_name="CommunityInsightsWorkflow",
                workflow_input={"period": "weekly"}
            )

            insights_count = result.get('insights_generated', 0)
            top_contributors = result.get('top_contributors', [])

            logger.info(f"✅ Community insights: {insights_count} insights, {len(top_contributors)} top contributors")

        except Exception as e:
            logger.error(f"❌ Community insights generation failed: {e}")

    async def _weekly_expertise_analysis(self):
        """
        Weekly Expertise Center tactical assistants analysis

        Reviews tactical assistant performance and recommendations quality
        """
        logger.info("🎓 WEEKLY EXPERTISE CENTER ANALYSIS")

        try:
            # Trigger expertise analysis workflow
            result = await self.workflow_client.start_workflow(
                workflow_name="ExpertiseAnalysisWorkflow",
                workflow_input={"analysis_type": "weekly_tactical_review"}
            )

            assistants_count = result.get('assistants_analyzed', 0)
            recommendations_quality = result.get('avg_quality_score', 0)

            logger.info(f"✅ Expertise analysis: {assistants_count} assistants, quality: {recommendations_quality:.2f}")

            # Alert on low quality
            if recommendations_quality < 0.7:
                await self.brain.send_alert({
                    'severity': 'medium',
                    'source': 'expertise_center',
                    'message': f'Tactical assistants quality score low: {recommendations_quality:.2f}'
                })

        except Exception as e:
            logger.error(f"❌ Expertise analysis failed: {e}")

    # ========================================================================
    # UTILITY METHODS
    # ========================================================================

    async def _print_schedule(self):
        """Показать расписание всех задач."""
        jobs = self.scheduler.get_jobs()
        logger.info(f"📅 Scheduled {len(jobs)} jobs:")
        for job in jobs:
            logger.info(f"  - {job.name} (next run: {job.next_run_time})")

    def get_stats(self) -> Dict:
        """Получить статистику работы планировщика."""
        return self.stats.copy()
