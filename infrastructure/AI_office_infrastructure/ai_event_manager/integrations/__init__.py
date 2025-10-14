"""
AI Event Manager - Complete Integration Layer

Максимальная интеграция со всеми компонентами платформы:
- EventBus (event-driven architecture)
- Event Intelligence (AI analysis)
- DevOps Agent (infrastructure scanning)
- GitHub Integration (code repository)
- MIO Manager (platform coordination)

Architecture:
    AI Event Manager (this service)
         |
         |-- EventBus: Publish/Subscribe events
         |-- Event Intelligence: AI-powered analysis
         |-- DevOps Agent: Infrastructure analysis
         |-- GitHub Integration: Code repository
         |-- MIO Manager: Platform coordination
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# Import all integration clients
from .eventbus_integration import EventBusIntegration
from .event_intelligence_integration import EventIntelligenceIntegration
from .devops_agent_integration import DevOpsAgentIntegration
from .github_integration_client import GitHubIntegrationClient
from .mio_manager_integration import MioManagerIntegration
from .continuous_monitor import ContinuousMonitor
from monitoring.infrastructure_state import InfrastructureStateMonitor

__all__ = [
    'EventBusIntegration',
    'EventIntelligenceIntegration',
    'DevOpsAgentIntegration',
    'GitHubIntegrationClient',
    'MioManagerIntegration',
    'ContinuousMonitor',
    'InfrastructureStateMonitor',
    'IntegrationManager'
]


class IntegrationManager:
    """
    Central integration manager for AI Event Manager

    Manages all integrations and provides unified interface
    """

    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize integration manager

        Args:
            config: Configuration dictionary with integration settings
        """
        self.config = config or self._default_config()

        # Integration instances
        self.eventbus: Optional[EventBusIntegration] = None
        self.event_intelligence: Optional[EventIntelligenceIntegration] = None
        self.devops_agent: Optional[DevOpsAgentIntegration] = None
        self.github: Optional[GitHubIntegrationClient] = None
        self.mio_manager: Optional[MioManagerIntegration] = None
        self.monitor: Optional[ContinuousMonitor] = None
        self.infrastructure_monitor: Optional[InfrastructureStateMonitor] = None

        # Statistics
        self.stats = {
            "initialized_at": datetime.utcnow().isoformat(),
            "integrations_active": 0,
            "events_published": 0,
            "events_received": 0,
            "ai_analyses": 0,
            "infrastructure_scans": 0,
            "github_operations": 0,
            "coordination_requests": 0
        }

        logger.info("Integration Manager initialized")

    async def initialize_all(self):
        """Initialize all integrations"""
        logger.info("Initializing all integrations...")

        # 1. EventBus (critical - for event-driven architecture)
        try:
            self.eventbus = EventBusIntegration(
                backend=self.config.get('eventbus_backend', 'memory'),
                redis_url=self.config.get('redis_url', 'redis://localhost:6379')
            )
            await self.eventbus.initialize()
            self.stats["integrations_active"] += 1
            logger.info("✅ EventBus integration initialized")
        except Exception as e:
            logger.error(f"❌ EventBus initialization failed: {e}")

        # 2. Event Intelligence (AI analysis)
        try:
            self.event_intelligence = EventIntelligenceIntegration(
                base_url=self.config.get('event_intelligence_url', 'http://localhost:8039')
            )
            await self.event_intelligence.initialize()
            self.stats["integrations_active"] += 1
            logger.info("✅ Event Intelligence integration initialized")
        except Exception as e:
            logger.error(f"❌ Event Intelligence initialization failed: {e}")

        # 3. DevOps Agent (infrastructure scanning)
        try:
            self.devops_agent = DevOpsAgentIntegration(
                base_url=self.config.get('devops_agent_url', 'http://localhost:8050'),
                project_root=self.config.get('project_root', '/Users/MD/AI-Platform-ISO')
            )
            await self.devops_agent.initialize()
            self.stats["integrations_active"] += 1
            logger.info("✅ DevOps Agent integration initialized")
        except Exception as e:
            logger.error(f"❌ DevOps Agent initialization failed: {e}")

        # 4. GitHub Integration (code repository)
        try:
            self.github = GitHubIntegrationClient(
                base_url=self.config.get('github_integration_url', 'http://localhost:8051')
            )
            await self.github.initialize()
            self.stats["integrations_active"] += 1
            logger.info("✅ GitHub Integration initialized")
        except Exception as e:
            logger.error(f"❌ GitHub Integration initialization failed: {e}")

        # 5. MIO Manager (platform coordination)
        try:
            self.mio_manager = MioManagerIntegration(
                base_url=self.config.get('mio_manager_url', 'http://localhost:8046')
            )
            await self.mio_manager.initialize()
            self.stats["integrations_active"] += 1
            logger.info("✅ MIO Manager integration initialized")
        except Exception as e:
            logger.error(f"❌ MIO Manager initialization failed: {e}")

        # 6. Continuous Monitor (automated monitoring)
        try:
            self.monitor = ContinuousMonitor(
                integration_manager=self,
                interval_seconds=self.config.get('monitor_interval', 300)  # 5 minutes
            )
            await self.monitor.start()
            self.stats["integrations_active"] += 1
            logger.info("✅ Continuous Monitor started")
        except Exception as e:
            logger.error(f"❌ Continuous Monitor initialization failed: {e}")

        # 7. Infrastructure State Monitor (NEW! - unified monitoring)
        try:
            if self.eventbus:
                self.infrastructure_monitor = InfrastructureStateMonitor(
                    eventbus=self.eventbus,
                    config={
                        'monitor_interval': self.config.get('infrastructure_monitor_interval', 60),
                        'project_manager_enabled': True,
                        'mio_manager_enabled': True,
                        'service_discovery_enabled': True,
                        'prometheus_enabled': True
                    }
                )
                # Start continuous monitoring in background
                import asyncio
                self.infrastructure_monitor.monitoring_task = asyncio.create_task(
                    self.infrastructure_monitor.start_continuous_monitoring()
                )
                self.stats["integrations_active"] += 1
                logger.info("✅ Infrastructure State Monitor started")
            else:
                logger.warning("⚠️ EventBus not available, skipping Infrastructure State Monitor")
        except Exception as e:
            logger.error(f"❌ Infrastructure State Monitor initialization failed: {e}")

        logger.info(f"✅ Integration Manager ready: {self.stats['integrations_active']}/7 integrations active")

    async def publish_event(self, event_name: str, data: Dict, priority: str = "normal") -> bool:
        """
        Publish event to EventBus

        Args:
            event_name: Event name (e.g., 'event.gap.detected')
            data: Event data
            priority: Event priority (low, normal, high, critical)

        Returns:
            Success status
        """
        if not self.eventbus:
            logger.warning("EventBus not initialized, cannot publish event")
            return False

        try:
            await self.eventbus.publish(event_name, data, priority)
            self.stats["events_published"] += 1
            return True
        except Exception as e:
            logger.error(f"Failed to publish event: {e}")
            return False

    async def analyze_with_ai(self, event_data: Dict) -> Optional[Dict]:
        """
        Analyze event with Event Intelligence AI

        Args:
            event_data: Event data to analyze

        Returns:
            AI analysis results or None
        """
        if not self.event_intelligence:
            logger.warning("Event Intelligence not initialized")
            return None

        try:
            analysis = await self.event_intelligence.analyze_event(event_data)
            self.stats["ai_analyses"] += 1
            return analysis
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            return None

    async def scan_infrastructure(self, scan_type: str = "events") -> Optional[Dict]:
        """
        Request infrastructure scan from DevOps Agent

        Args:
            scan_type: Type of scan (events, containers, deployments, full)

        Returns:
            Scan results or None
        """
        if not self.devops_agent:
            logger.warning("DevOps Agent not initialized")
            return None

        try:
            results = await self.devops_agent.request_scan(scan_type)
            self.stats["infrastructure_scans"] += 1
            return results
        except Exception as e:
            logger.error(f"Infrastructure scan failed: {e}")
            return None

    async def create_github_issue(self, title: str, body: str, labels: List[str] = None) -> Optional[str]:
        """
        Create GitHub issue for event gap

        Args:
            title: Issue title
            body: Issue description
            labels: Issue labels

        Returns:
            Issue URL or None
        """
        if not self.github:
            logger.warning("GitHub Integration not initialized")
            return None

        try:
            issue_url = await self.github.create_issue(title, body, labels or [])
            self.stats["github_operations"] += 1
            return issue_url
        except Exception as e:
            logger.error(f"GitHub issue creation failed: {e}")
            return None

    async def report_to_mio(self, report: Dict) -> bool:
        """
        Report findings to MIO Manager

        Args:
            report: Report data

        Returns:
            Success status
        """
        if not self.mio_manager:
            logger.warning("MIO Manager not initialized")
            return False

        try:
            await self.mio_manager.report_insights(report)
            self.stats["coordination_requests"] += 1
            return True
        except Exception as e:
            logger.error(f"MIO Manager report failed: {e}")
            return False

    async def run_full_analysis_cycle(self) -> Dict:
        """
        Run complete analysis cycle with all integrations

        Returns:
            Complete analysis results
        """
        logger.info("Running full analysis cycle...")

        results = {
            "timestamp": datetime.utcnow().isoformat(),
            "cycle_type": "full_analysis",
            "steps_completed": []
        }

        # Step 1: Scan infrastructure with DevOps Agent
        if self.devops_agent:
            logger.info("Step 1: Infrastructure scanning...")
            scan_results = await self.scan_infrastructure("events")
            results["infrastructure_scan"] = scan_results
            results["steps_completed"].append("infrastructure_scan")

        # Step 2: Analyze with Event Intelligence
        if self.event_intelligence and scan_results:
            logger.info("Step 2: AI analysis...")
            ai_analysis = await self.analyze_with_ai({
                "scan_results": scan_results,
                "context": "automated_analysis"
            })
            results["ai_analysis"] = ai_analysis
            results["steps_completed"].append("ai_analysis")

        # Step 3: Publish critical findings to EventBus
        if self.eventbus and ai_analysis:
            logger.info("Step 3: Publishing critical findings...")
            critical_findings = [
                f for f in ai_analysis.get("findings", [])
                if f.get("severity") == "critical"
            ]

            for finding in critical_findings:
                await self.publish_event(
                    "event.gap.critical_detected",
                    finding,
                    priority="critical"
                )

            results["critical_findings_published"] = len(critical_findings)
            results["steps_completed"].append("eventbus_publish")

        # Step 4: Create GitHub issues for high-priority gaps
        if self.github and ai_analysis:
            logger.info("Step 4: Creating GitHub issues...")
            high_priority_gaps = [
                g for g in ai_analysis.get("gaps", [])
                if g.get("priority") in ["high", "critical"]
            ]

            github_issues = []
            for gap in high_priority_gaps[:5]:  # Limit to 5
                issue_url = await self.create_github_issue(
                    title=f"Event Gap: {gap.get('event_name')}",
                    body=gap.get("description", ""),
                    labels=["event-gap", gap.get("priority", "medium")]
                )
                if issue_url:
                    github_issues.append(issue_url)

            results["github_issues_created"] = github_issues
            results["steps_completed"].append("github_issues")

        # Step 5: Report to MIO Manager
        if self.mio_manager:
            logger.info("Step 5: Reporting to MIO Manager...")
            await self.report_to_mio({
                "source": "ai-event-manager",
                "type": "full_analysis_cycle",
                "results": results,
                "recommendations": ai_analysis.get("recommendations", []) if ai_analysis else []
            })
            results["steps_completed"].append("mio_report")

        logger.info(f"✅ Full analysis cycle completed: {len(results['steps_completed'])} steps")

        return results

    def get_integration_status(self) -> Dict:
        """Get status of all integrations"""
        return {
            "integrations": {
                "eventbus": "active" if self.eventbus else "inactive",
                "event_intelligence": "active" if self.event_intelligence else "inactive",
                "devops_agent": "active" if self.devops_agent else "inactive",
                "github": "active" if self.github else "inactive",
                "mio_manager": "active" if self.mio_manager else "inactive",
                "monitor": "active" if self.monitor else "inactive",
                "infrastructure_monitor": "active" if self.infrastructure_monitor else "inactive"
            },
            "statistics": self.stats,
            "health": "healthy" if self.stats["integrations_active"] >= 5 else "degraded"
        }

    async def close(self):
        """Close all integrations"""
        logger.info("Closing all integrations...")

        if self.monitor:
            await self.monitor.stop()

        if self.infrastructure_monitor:
            self.infrastructure_monitor.stop_monitoring()

        if self.eventbus:
            await self.eventbus.close()

        if self.event_intelligence:
            await self.event_intelligence.close()

        if self.devops_agent:
            await self.devops_agent.close()

        if self.github:
            await self.github.close()

        if self.mio_manager:
            await self.mio_manager.close()

        logger.info("✅ All integrations closed")

    def _default_config(self) -> Dict:
        """Default configuration"""
        return {
            'eventbus_backend': 'memory',
            'redis_url': 'redis://localhost:6379',
            'event_intelligence_url': 'http://localhost:8039',
            'devops_agent_url': 'http://localhost:8050',
            'github_integration_url': 'http://localhost:8051',
            'mio_manager_url': 'http://localhost:8046',
            'project_root': '/Users/MD/AI-Platform-ISO',
            'monitor_interval': 300  # 5 minutes
        }
