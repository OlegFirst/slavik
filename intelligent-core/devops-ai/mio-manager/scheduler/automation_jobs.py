#!/usr/bin/env python3
"""
Automation Jobs Scheduler
Автоматическое выполнение задач по расписанию
"""

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
import logging

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


def start_scheduler(toolkit_manager, orchestrator_client, gateway_manager):
    """Start all automation jobs"""

    # ============================================================================
    # JOB 1: Service Discovery (каждые 5 минут)
    # ============================================================================
    @scheduler.scheduled_job(IntervalTrigger(minutes=5))
    async def auto_discover_services():
        """Auto-discovery новых сервисов"""
        try:
            logger.info("🔍 Running auto-discovery...")
            result = await toolkit_manager.discover_services()

            # Если есть unmonitored сервисы - регистрируем в Gateway
            if result['coverage']['percentage'] < 100:
                for service in result['services']:
                    if not (service['has_health'] and service['has_metrics']):
                        logger.warning(f"⚠️  Service {service['name']} not fully monitored")

                        # Register in Gateway
                        await gateway_manager.register_service({
                            'name': service['name'],
                            'endpoints': service['endpoints']
                        })

            logger.info(f"✅ Discovery complete: {result['coverage']['percentage']:.1f}% coverage")

        except Exception as e:
            logger.error(f"❌ Auto-discovery failed: {e}")

    # ============================================================================
    # JOB 2: Security Scan (каждый час)
    # ============================================================================
    @scheduler.scheduled_job(IntervalTrigger(hours=1))
    async def hourly_security_scan():
        """Hourly security scan"""
        try:
            logger.info("🔒 Running security scan...")
            result = await toolkit_manager.run_security_scan()

            # Если найдены HIGH severity issues - создать задачу
            if result['high_severity'] > 0:
                logger.warning(f"⚠️  Found {result['high_severity']} HIGH security issues")

                task = await toolkit_manager.create_improvement_task(
                    issue_type='security',
                    details={
                        'severity': 'high',
                        'count': result['high_severity'],
                        'issues': result['high_issues']
                    }
                )

                # Delegate to Orchestrator
                await orchestrator_client.delegate_task(task)
                logger.info(f"✅ Security task created: {task['task_id']}")

            else:
                logger.info("✅ No high-severity issues found")

        except Exception as e:
            logger.error(f"❌ Security scan failed: {e}")

    # ============================================================================
    # JOB 3: Dependency Analysis (каждые 15 минут)
    # ============================================================================
    @scheduler.scheduled_job(IntervalTrigger(minutes=15))
    async def dependency_analysis():
        """Analyze service dependencies"""
        try:
            logger.info("🔗 Analyzing dependencies...")
            result = await toolkit_manager.analyze_dependencies()

            # Если найдены циклические зависимости - создать задачу
            if result.get('circular_dependencies'):
                logger.warning(f"⚠️  Found {len(result['circular_dependencies'])} circular dependencies")

                task = await toolkit_manager.create_improvement_task(
                    issue_type='circular_dependency',
                    details={
                        'cycles': result['circular_dependencies']
                    }
                )

                await orchestrator_client.delegate_task(task)

            logger.info(f"✅ Dependency analysis complete: {result['graph_nodes']} nodes")

        except Exception as e:
            logger.error(f"❌ Dependency analysis failed: {e}")

    # ============================================================================
    # JOB 4: Code Complexity Analysis (ежедневно в 2:00)
    # ============================================================================
    @scheduler.scheduled_job(CronTrigger(hour=2, minute=0))
    async def daily_complexity_analysis():
        """Daily code complexity analysis"""
        try:
            logger.info("📊 Running daily complexity analysis...")

            services = ['validation', 'documents', 'governance', 'incident']

            for service in services:
                result = await toolkit_manager.analyze_code_complexity(service)

                # Если max complexity > 20 - создать задачу на рефакторинг
                if result['max_complexity'] > 20:
                    logger.warning(
                        f"⚠️  {service}: max complexity {result['max_complexity']} "
                        f"(avg: {result['avg_complexity']:.1f})"
                    )

                    task = await toolkit_manager.create_improvement_task(
                        issue_type='high_complexity',
                        details={
                            'service': service,
                            'max_complexity': result['max_complexity'],
                            'functions': result['high_complexity_functions']
                        }
                    )

                    await orchestrator_client.delegate_task(task)

            logger.info("✅ Complexity analysis complete")

        except Exception as e:
            logger.error(f"❌ Complexity analysis failed: {e}")

    # ============================================================================
    # JOB 5: Synthetic Test Generation (еженедельно в воскресенье 3:00)
    # ============================================================================
    @scheduler.scheduled_job(CronTrigger(day_of_week='sun', hour=3, minute=0))
    async def weekly_test_generation():
        """Weekly synthetic test generation"""
        try:
            logger.info("🧪 Generating weekly synthetic tests...")
            result = await toolkit_manager.generate_synthetic_tests()

            logger.info(f"✅ Generated {result['total_tests']} synthetic tests")

        except Exception as e:
            logger.error(f"❌ Test generation failed: {e}")

    # ============================================================================
    # JOB 6: Health Check All Services (каждые 2 минуты)
    # ============================================================================
    @scheduler.scheduled_job(IntervalTrigger(minutes=2))
    async def health_check_services():
        """Health check all services through Gateway"""
        try:
            # Get discovered services
            if toolkit_manager.last_discovery:
                services = toolkit_manager.last_discovery['services']

                for service in services:
                    health = await gateway_manager.get_service_health(service['name'])

                    if health['status'] != 'healthy':
                        logger.warning(f"⚠️  Service {service['name']} is {health['status']}")

                        # Create restart task
                        task = {
                            'type': 'service_restart',
                            'service': service['name'],
                            'reason': f"Health check failed: {health['status']}"
                        }

                        await orchestrator_client.request_service_restart(service['name'])

        except Exception as e:
            logger.error(f"❌ Health check failed: {e}")

    # Start scheduler
    scheduler.start()
    logger.info("✅ Automation scheduler started with 6 jobs")


def stop_scheduler():
    """Stop scheduler"""
    scheduler.shutdown()
    logger.info("✅ Automation scheduler stopped")
