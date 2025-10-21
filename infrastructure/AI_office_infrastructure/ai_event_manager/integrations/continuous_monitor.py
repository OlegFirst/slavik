"""
Continuous Monitor for AI Event Manager

Автоматический мониторинг с:
- Continuous scanning
- Auto-fix gaps
- Alert на критические проблемы
"""

import logging
import asyncio
from typing import Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class ContinuousMonitor:
    """
    Continuous monitoring service

    Features:
    - Periodic infrastructure scanning
    - Automatic gap detection
    - Critical alert triggering
    - Auto-fix coordination
    """

    def __init__(self, integration_manager, interval_seconds: int = 300):
        """
        Initialize continuous monitor

        Args:
            integration_manager: IntegrationManager instance
            interval_seconds: Scan interval in seconds (default: 5 minutes)
        """
        self.integration_manager = integration_manager
        self.interval_seconds = interval_seconds
        self.running = False
        self.monitor_task = None

        # Statistics
        self.scans_completed = 0
        self.gaps_detected = 0
        self.critical_gaps = 0
        self.auto_fixes_triggered = 0
        self.alerts_sent = 0

    async def start(self):
        """Start continuous monitoring"""
        if self.running:
            logger.warning("Continuous monitor already running")
            return

        self.running = True
        self.monitor_task = asyncio.create_task(self._monitor_loop())
        logger.info(f"Continuous monitor started (interval: {self.interval_seconds}s)")

    async def stop(self):
        """Stop continuous monitoring"""
        if not self.running:
            return

        self.running = False

        if self.monitor_task:
            self.monitor_task.cancel()
            try:
                await self.monitor_task
            except asyncio.CancelledError:
                pass

        logger.info("Continuous monitor stopped")

    async def _monitor_loop(self):
        """Main monitoring loop"""
        logger.info("Monitoring loop started")

        while self.running:
            try:
                await self._run_scan_cycle()

                # Wait for next cycle
                await asyncio.sleep(self.interval_seconds)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitor loop: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error

    async def _run_scan_cycle(self):
        """Run single scan cycle"""
        logger.info("=== Starting Scan Cycle ===")
        cycle_start = datetime.utcnow()

        try:
            # Step 1: Scan infrastructure with DevOps Agent
            scan_results = await self._scan_infrastructure()

            # Step 2: Analyze with Event Intelligence
            analysis_results = await self._analyze_results(scan_results)

            # Step 3: Process findings
            await self._process_findings(analysis_results)

            # Step 4: Report to MIO Manager
            await self._report_cycle_results({
                "scan_results": scan_results,
                "analysis_results": analysis_results,
                "cycle_timestamp": cycle_start.isoformat()
            })

            self.scans_completed += 1
            logger.info(f"=== Scan Cycle Complete (#{self.scans_completed}) ===")

        except Exception as e:
            logger.error(f"Scan cycle failed: {e}")

    async def _scan_infrastructure(self) -> Optional[Dict]:
        """Scan infrastructure using DevOps Agent"""
        logger.info("Step 1: Infrastructure scanning...")

        if not self.integration_manager.devops_agent:
            logger.warning("DevOps Agent not available")
            return None

        try:
            scan_results = await self.integration_manager.scan_infrastructure("events")

            if scan_results:
                logger.info(f"Scan complete: {scan_results.get('total_issues', 0)} issues found")

            return scan_results

        except Exception as e:
            logger.error(f"Infrastructure scan failed: {e}")
            return None

    async def _analyze_results(self, scan_results: Optional[Dict]) -> Optional[Dict]:
        """Analyze scan results with Event Intelligence"""
        if not scan_results:
            return None

        logger.info("Step 2: AI analysis...")

        if not self.integration_manager.event_intelligence:
            logger.warning("Event Intelligence not available")
            return None

        try:
            analysis = await self.integration_manager.analyze_with_ai({
                "scan_results": scan_results,
                "context": "continuous_monitoring"
            })

            if analysis:
                logger.info(f"Analysis complete: {len(analysis.get('findings', []))} findings")

            return analysis

        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            return None

    async def _process_findings(self, analysis_results: Optional[Dict]):
        """Process analysis findings"""
        if not analysis_results:
            return

        logger.info("Step 3: Processing findings...")

        findings = analysis_results.get('findings', [])
        gaps = analysis_results.get('gaps', [])

        # Count critical gaps
        critical_gaps = [g for g in gaps if g.get('severity') == 'critical']
        self.critical_gaps += len(critical_gaps)
        self.gaps_detected += len(gaps)

        # Publish critical gaps to EventBus
        if critical_gaps and self.integration_manager.eventbus:
            for gap in critical_gaps:
                await self.integration_manager.eventbus.publish_gap_detected(gap)
                logger.warning(f" Critical gap detected: {gap.get('event_name')}")

            self.alerts_sent += len(critical_gaps)

        # Create GitHub issues for high-priority gaps
        high_priority_gaps = [g for g in gaps if g.get('priority') in ['high', 'critical']]

        if high_priority_gaps and self.integration_manager.github:
            for gap in high_priority_gaps[:3]:  # Limit to 3 per cycle
                await self.integration_manager.create_github_issue(
                    title=f"Event Gap: {gap.get('event_name')}",
                    body=gap.get('description', 'Auto-detected event gap'),
                    labels=['event-gap', gap.get('severity', 'medium'), 'auto-detected']
                )

        # Trigger auto-fix for safe fixes
        safe_fixes = [
            f for f in findings
            if f.get('auto_fix_safe', False) and f.get('severity') != 'critical'
        ]

        if safe_fixes:
            logger.info(f"Triggering auto-fix for {len(safe_fixes)} safe fixes")
            self.auto_fixes_triggered += len(safe_fixes)

            # Request auto-fix through MIO Manager
            if self.integration_manager.mio_manager:
                await self.integration_manager.mio_manager.request_task({
                    "type": "auto_fix",
                    "fixes": safe_fixes
                })

    async def _report_cycle_results(self, results: Dict):
        """Report cycle results to MIO Manager"""
        logger.info("Step 4: Reporting to MIO Manager...")

        if not self.integration_manager.mio_manager:
            return

        try:
            await self.integration_manager.report_to_mio({
                "source": "continuous_monitor",
                "type": "scan_cycle_complete",
                "results": results,
                "statistics": self.get_stats()
            })

        except Exception as e:
            logger.error(f"Failed to report to MIO Manager: {e}")

    def get_stats(self) -> Dict:
        """Get monitoring statistics"""
        return {
            "scans_completed": self.scans_completed,
            "gaps_detected": self.gaps_detected,
            "critical_gaps": self.critical_gaps,
            "auto_fixes_triggered": self.auto_fixes_triggered,
            "alerts_sent": self.alerts_sent,
            "running": self.running,
            "interval_seconds": self.interval_seconds
        }

    async def trigger_immediate_scan(self) -> Dict:
        """Trigger immediate scan (outside regular schedule)"""
        logger.info("Triggering immediate scan...")

        await self._run_scan_cycle()

        return {
            "status": "completed",
            "timestamp": datetime.utcnow().isoformat(),
            "stats": self.get_stats()
        }
