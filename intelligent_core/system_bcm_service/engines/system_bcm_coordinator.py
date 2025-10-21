"""
System BCM Coordinator - ПРАВИЛЬНАЯ версия
Использует СУЩЕСТВУЮЩИЕ компоненты платформы вместо дубликатов
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Add integrations
sys.path.insert(0, str(Path(__file__).parent.parent))

from integrations.learning_integration import LearningIntegration
from integrations.expertise_integration import ExpertiseIntegration
from integrations.collective_integration import CollectiveIntegration
from integrations.ai_integration import AIIntegration

# EventBus
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "infrastructure"))
from eventbus import create_eventbus, Event

# Service Recovery Handler (NEW!)
from engines.service_recovery_handler import ServiceRecoveryHandler

logger = logging.getLogger(__name__)


class SystemBCMCoordinator:
    """
    System BCM Coordinator - ИНТЕГРИРОВАННАЯ версия

    РОЛЬ: КООРДИНАТОР, не исполнитель

    ЧТО ДЕЛАЕТ САМ:
    - Собирает метрики платформы
    - Координирует фазы BCM цикла
    - Публикует события
    - Управляет workflow

    ЧТО ДЕЛЕГИРУЕТ (используя существующие компоненты):
    - Pattern detection → learning-knowledge
    - AI анализ → Expertise Center + LLM/RAG
    - Сохранение знаний → Collective Intelligence
    - Глубокий анализ → ai-foundation (RAG + LLM)

    РЕЗУЛЬТАТ: Интегрирован с ЯДРОМ платформы!
    """

    def __init__(self, resource_tracker=None, decision_center_url="http://localhost:8080"):
        """Инициализация координатора"""
        # EventBus
        self.eventbus = None

        # Интеграции с существующими компонентами
        self.learning = LearningIntegration()
        self.expertise = ExpertiseIntegration()
        self.collective = CollectiveIntegration()
        self.ai = AIIntegration()

        # ResourceTracker (NEW!)
        self.resource_tracker = resource_tracker

        # Service Recovery Handler with Decision Center (NEW!)
        self.recovery_handler = None
        self.decision_center_url = decision_center_url

        # State
        self.running = False
        self.current_cycle_id = None

        # Platform services to monitor
        self.platform_services = [
            {"name": "api-gateway", "port": 8000, "tier": "critical"},
            {"name": "workflow-intelligence", "port": 8001, "tier": "critical"},
            {"name": "rag-service", "port": 8002, "tier": "critical"},
            {"name": "expertise-center", "port": 8003, "tier": "important"},
            {"name": "collective", "port": 8004, "tier": "important"},
            {"name": "bia-service", "port": 8010, "tier": "important"},
            {"name": "risk-service", "port": 8011, "tier": "important"},
            {"name": "planning-service", "port": 8012, "tier": "important"},
            {"name": "compliance-service", "port": 8013, "tier": "important"},
            {"name": "documents-service", "port": 8014, "tier": "optional"},
            {"name": "learning-service", "port": 8015, "tier": "optional"},
            {"name": "community-service", "port": 8016, "tier": "optional"}
        ]

        logger.info(" System BCM Coordinator initialized (INTEGRATED version)")

    async def initialize(self):
        """Инициализация"""
        try:
            # Setup EventBus
            self.eventbus = create_eventbus('redis')
            logger.info(" EventBus connected")

            # Initialize Service Recovery Handler (NEW!)
            self.recovery_handler = ServiceRecoveryHandler(
                decision_center_url=self.decision_center_url,
                eventbus=self.eventbus
            )
            logger.info(" Service Recovery Handler initialized with Decision Center governance")

            # Subscribe to platform events
            await self._subscribe_to_events()

            self.running = True
            logger.info(" System BCM Coordinator ready")

        except Exception as e:
            logger.error(f" Initialization failed: {e}")
            self.eventbus = create_eventbus('memory')
            logger.warning("️  Using memory EventBus (fallback)")

    async def run_bcm_cycle(self) -> Dict[str, Any]:
        """
        Запустить BCM цикл

        КООРДИНИРУЕТ (не делает сам):
        1. Собирает метрики (единственное что делаем сами)
        2. Pattern detection через learning-knowledge
        3. Консультация с Expertise Center
        4. Поиск решений через RAG
        5. Анализ через LLM
        6. Сохранение в Collective

        РЕЗУЛЬТАТ: Полностью интегрированный цикл
        """
        self.current_cycle_id = f"cycle-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
        start_time = datetime.utcnow()

        logger.info(f" Starting BCM cycle: {self.current_cycle_id}")

        try:
            # Publish start event
            await self._publish_event("cycle.started", {
                "cycle_id": self.current_cycle_id,
                "started_at": start_time.isoformat()
            })

            # PHASE 1: BIA - Собрать метрики (делаем сами) + ResourceTracker
            logger.info(" Phase 1: BIA - Collecting platform metrics...")
            bia_results = await self._execute_bia_phase(self.resource_tracker)

            # PHASE 2: Risk Assessment - Консультация с Expertise Center
            logger.info("️  Phase 2: Risk Assessment - Consulting AI experts...")
            risk_results = await self.expertise.assess_platform_risks(bia_results)

            # PHASE 3: Pattern Detection - через learning-knowledge
            logger.info(" Phase 3: Pattern Detection - Using learning-knowledge...")
            # Собрать историю циклов для pattern detection
            cycle_history = await self._get_cycle_history()
            patterns = await self.learning.detect_patterns(cycle_history)

            # PHASE 4: AI Analysis - RAG + LLM + Expertise
            logger.info(" Phase 4: AI Analysis - RAG + LLM + Experts...")

            # 4.1: Поиск похожих решений через RAG
            issue_description = self._describe_current_state(bia_results, risk_results, patterns)
            similar_solutions = await self.ai.find_similar_solutions(
                issue_description,
                context=bia_results
            )

            # 4.2: Комплексная консультация с экспертами
            expert_analysis = await self.expertise.get_comprehensive_analysis({
                "bia_results": bia_results,
                "risk_results": risk_results,
                "detected_patterns": patterns
            })

            # 4.3: Глубокий анализ через LLM
            llm_analysis = await self.ai.analyze_with_llm(
                situation={
                    "bia_results": bia_results,
                    "risk_results": risk_results,
                    "patterns": patterns
                },
                similar_cases=similar_solutions,
                expert_insights=expert_analysis.get("strategic", {}).get("insights", [])
            )

            # PHASE 5: Generate Comprehensive Insights
            logger.info(" Phase 5: Generating insights...")
            comprehensive_insights = await self.ai.generate_comprehensive_insights(
                cycle_results=bia_results,
                patterns=patterns,
                expert_analysis=expert_analysis
            )

            # PHASE 6: Learning - Сохранить в Collective + Knowledge Base
            logger.info(" Phase 6: Sharing knowledge with community...")

            # 6.1: Сохранить паттерны в Collective Intelligence
            for pattern in patterns:
                await self.collective.share_pattern(
                    pattern,
                    effectiveness_score=pattern.get("confidence_score", 0.7)
                )

            # 6.2: Индексировать в Qdrant для RAG
            for pattern in patterns:
                await self.ai.index_pattern_in_qdrant(
                    pattern,
                    effectiveness=pattern.get("confidence_score")
                )

            # 6.3: Сохранить в knowledge base через learning integration
            await self.learning.save_to_knowledge_base(patterns)

            # 6.4: Practice learning from this cycle
            effectiveness_score = self._calculate_cycle_effectiveness(bia_results)
            learning_result = await self.learning.learn_from_practice(
                cycle_results={
                    "bia_results": bia_results,
                    "risk_results": risk_results,
                    "patterns": patterns,
                    "insights": comprehensive_insights,
                    "improvements_applied": comprehensive_insights.get("final_recommendations", [])[:3]
                },
                effectiveness_score=effectiveness_score
            )

            # Calculate cycle metrics
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()

            # Build final result
            cycle_result = {
                "cycle_id": self.current_cycle_id,
                "started_at": start_time.isoformat(),
                "completed_at": end_time.isoformat(),
                "duration_seconds": duration,
                "status": "completed",
                "phases": {
                    "bia": bia_results,
                    "risk_assessment": risk_results,
                    "pattern_detection": {
                        "patterns": patterns,
                        "count": len(patterns)
                    },
                    "ai_analysis": {
                        "similar_solutions": similar_solutions,
                        "expert_analysis": expert_analysis,
                        "llm_analysis": llm_analysis,
                        "comprehensive_insights": comprehensive_insights
                    },
                    "learning": learning_result
                },
                "integration_status": {
                    "learning_knowledge": " Used PatternDetector",
                    "expertise_center": f" Consulted {len(expert_analysis.get('consulted_specialists', []))} specialists",
                    "collective_intelligence": f" Shared {len(patterns)} patterns",
                    "rag_llm": f" Found {len(similar_solutions)} similar cases",
                    "knowledge_base": " Patterns indexed in Qdrant"
                },
                "metrics": {
                    "platform_health_score": bia_results.get("health_score", 0),
                    "critical_risks": risk_results.get("critical_count", 0),
                    "patterns_detected": len(patterns),
                    "insights_generated": len(comprehensive_insights.get("rag_findings", {}).get("proven_solutions", [])),
                    "knowledge_shared": len(patterns),
                    "effectiveness_score": effectiveness_score
                }
            }

            # Publish completion event
            await self._publish_event("cycle.completed", cycle_result)

            logger.info(f" BCM cycle completed in {duration:.2f}s - FULLY INTEGRATED!")
            logger.info(f"    Platform health: {bia_results.get('health_score', 0)}%")
            logger.info(f"    Patterns detected: {len(patterns)}")
            logger.info(f"    AI specialists consulted: {len(expert_analysis.get('consulted_specialists', []))}")
            logger.info(f"    Knowledge shared with community: {len(patterns)} patterns")
            logger.info(f"    Insights generated: {len(comprehensive_insights.get('final_recommendations', []))}")

            return cycle_result

        except Exception as e:
            logger.error(f" BCM cycle failed: {e}")
            await self._publish_event("cycle.failed", {
                "cycle_id": self.current_cycle_id,
                "error": str(e)
            })
            raise

    async def _execute_bia_phase(self, resource_tracker=None) -> Dict[str, Any]:
        """
        Выполнить BIA фазу - ЕДИНСТВЕННОЕ что делаем сами

        Собираем метрики платформы для анализа + ResourceTracker данные
        """
        # Собрать health статус всех сервисов
        services_health = []
        healthy_count = 0

        for service in self.platform_services:
            health = await self._check_service_health(service)
            services_health.append(health)
            if health["status"] == "healthy":
                healthy_count += 1

        # Рассчитать общий health score
        health_score = (healthy_count / len(self.platform_services)) * 100

        # Определить зависимости
        dependencies = self._analyze_dependencies()

        # Классифицировать сервисы по критичности
        critical_services = [s for s in self.platform_services if s["tier"] == "critical"]
        important_services = [s for s in self.platform_services if s["tier"] == "important"]
        optional_services = [s for s in self.platform_services if s["tier"] == "optional"]

        # RTO/RPO рекомендации
        rto_recommendations = {
            "critical": 60,  # 1 минута
            "important": 300,  # 5 минут
            "optional": 1800  # 30 минут
        }

        # ResourceTracker данные (NEW!)
        resource_monitoring = None
        if resource_tracker:
            available = resource_tracker.get_available_resources()
            resource_state = resource_tracker.detect_resource_state()
            cpu_deficit = resource_tracker.predict_deficit('cpu_percent', 90.0)
            mem_deficit = resource_tracker.predict_deficit('memory_percent', 90.0)

            resource_monitoring = {
                "state": resource_state,
                "available": available,
                "predictions": {
                    "cpu_deficit_seconds": cpu_deficit,
                    "memory_deficit_seconds": mem_deficit
                },
                "stats": resource_tracker.get_stats()
            }

            # Publish event if deficit detected
            if resource_state == "deficit":
                logger.warning(f"️  Resource deficit detected!")
                await self._publish_event("resources.contention", {
                    "type": "predicted_shortage",
                    "available": available,
                    "cpu_deficit_seconds": cpu_deficit,
                    "memory_deficit_seconds": mem_deficit
                })

        result = {
            "services": services_health,
            "health_score": round(health_score, 2),
            "healthy_count": healthy_count,
            "total_count": len(self.platform_services),
            "dependencies": dependencies,
            "classification": {
                "critical": [s["name"] for s in critical_services],
                "important": [s["name"] for s in important_services],
                "optional": [s["name"] for s in optional_services]
            },
            "rto_recommendations": rto_recommendations,
            "timestamp": datetime.utcnow().isoformat()
        }

        # Add resource monitoring if available
        if resource_monitoring:
            result["resource_monitoring"] = resource_monitoring

        # Add recovery statistics if available (NEW!)
        if self.recovery_handler:
            recovery_stats = self.recovery_handler.get_recovery_stats()
            result["recovery_statistics"] = recovery_stats

            logger.info(
                f"    Recovery stats: {recovery_stats['total_attempts']} attempts, "
                f"{recovery_stats['successful_recoveries']} successful "
                f"(success rate: {recovery_stats['success_rate']:.1%})"
            )

        return result

    async def _check_service_health(self, service: Dict[str, Any]) -> Dict[str, Any]:
        """Проверить здоровье сервиса"""
        import aiohttp

        try:
            async with aiohttp.ClientSession() as session:
                url = f"http://localhost:{service['port']}/health"
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=2)) as response:
                    if response.status == 200:
                        return {
                            "name": service["name"],
                            "status": "healthy",
                            "tier": service["tier"],
                            "response_time_ms": 0,
                            "port": service["port"]
                        }
        except:
            pass

        return {
            "name": service["name"],
            "status": "down",
            "tier": service["tier"],
            "port": service["port"]
        }

    def _analyze_dependencies(self) -> Dict[str, List[str]]:
        """Анализ зависимостей между сервисами"""
        return {
            "api-gateway": ["workflow-intelligence", "rag-service", "expertise-center"],
            "workflow-intelligence": ["bia-service", "risk-service", "planning-service"],
            "rag-service": ["qdrant", "embeddings"],
            "expertise-center": ["rag-service", "llm"],
            "collective": ["postgresql", "redis"],
            "bia-service": ["postgresql"],
            "risk-service": ["postgresql"],
            "planning-service": ["postgresql"],
            "compliance-service": ["postgresql"],
            "documents-service": ["postgresql", "storage"],
            "learning-service": ["postgresql", "qdrant"],
            "community-service": ["postgresql", "redis"]
        }

    async def _get_cycle_history(self) -> List[Dict[str, Any]]:
        """Получить историю предыдущих циклов"""
        # TODO: Получать из БД
        # Пока возвращаем пустой список
        return []

    def _describe_current_state(
        self,
        bia_results: Dict[str, Any],
        risk_results: Dict[str, Any],
        patterns: List[Dict[str, Any]]
    ) -> str:
        """Описать текущее состояние платформы для RAG поиска"""
        health_score = bia_results.get("health_score", 100)
        critical_risks = risk_results.get("critical_count", 0)

        description_parts = [
            f"Platform health: {health_score}%",
            f"Critical risks: {critical_risks}",
            f"Detected patterns: {len(patterns)}"
        ]

        if health_score < 90:
            unhealthy = len(bia_results.get("services", [])) - bia_results.get("healthy_count", 0)
            description_parts.append(f"{unhealthy} services degraded")

        for pattern in patterns:
            description_parts.append(f"Pattern: {pattern.get('type', 'unknown')}")

        return " | ".join(description_parts)

    def _calculate_cycle_effectiveness(self, bia_results: Dict[str, Any]) -> float:
        """Рассчитать эффективность цикла"""
        health_score = bia_results.get("health_score", 0)

        # Эффективность = здоровье платформы
        # Можно улучшить: сравнивать с предыдущим циклом
        return health_score

    async def _subscribe_to_events(self):
        """Подписаться на события платформы"""

        @self.eventbus.subscribe("platform.health.degraded")
        async def on_health_degraded(event: Event):
            logger.warning(f"️  Platform health degraded: {event.data}")
            # Можно запустить внеплановый цикл

        @self.eventbus.subscribe("platform.service.failed")
        async def on_service_failed(event: Event):
            logger.error(f" Service failed: {event.data}")

            # Trigger automatic recovery with Decision Center governance (NEW!)
            if self.recovery_handler:
                try:
                    service_name = event.data.get("service")
                    failure_type = event.data.get("failure_type", "health_check_failed")
                    metrics = event.data.get("metrics", {})
                    tier = event.data.get("tier", "standard")

                    logger.info(
                        f" Initiating recovery for {service_name} with Decision Center governance..."
                    )

                    recovery_result = await self.recovery_handler.handle_service_failure(
                        service_name=service_name,
                        failure_type=failure_type,
                        metrics=metrics,
                        tier=tier
                    )

                    logger.info(
                        f"Recovery result: {recovery_result.get('outcome')} - "
                        f"{recovery_result.get('justification')}"
                    )

                except Exception as e:
                    logger.error(f" Recovery handling failed: {e}", exc_info=True)

        logger.info(" Subscribed to platform events")

    async def _publish_event(self, event_type: str, data: Dict[str, Any]):
        """Опубликовать событие"""
        if not self.eventbus:
            return

        try:
            event = Event(
                type=f"platform.bcm.{event_type}",
                data=data,
                source="system-bcm-coordinator"
            )
            await self.eventbus.publish(event)
        except Exception as e:
            logger.error(f"Failed to publish event: {e}")

    async def start_scheduler(self, interval_hours: int = 24):
        """Запустить планировщик (каждые 24 часа)"""
        logger.info(f"⏰ Starting BCM cycle scheduler (every {interval_hours}h)")

        while self.running:
            try:
                await self.run_bcm_cycle()
            except Exception as e:
                logger.error(f" Scheduled cycle failed: {e}")

            # Ждать до следующего цикла
            await asyncio.sleep(interval_hours * 3600)

    async def shutdown(self):
        """Выключение"""
        logger.info(" Shutting down System BCM Coordinator...")
        self.running = False

        # Close recovery handler (NEW!)
        if self.recovery_handler:
            logger.info("Closing Service Recovery Handler...")
            await self.recovery_handler.close()


# Export
__all__ = ["SystemBCMCoordinator"]
