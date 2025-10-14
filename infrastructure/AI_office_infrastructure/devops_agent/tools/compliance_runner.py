"""
Compliance Runner - Unified interface for all compliance checks

Integrates 6 priority compliance checks:
1. Port conflicts
2. Metrics integration
3. Database connections
4. KPI registration
5. EventBus events
6. Orchestrator control
"""

import sys
from pathlib import Path
from typing import Dict, List
from datetime import datetime

# Add compliance-checks to path
sys.path.insert(0, str(Path(__file__).parent / "compliance-checks"))


class ComplianceRunner:
    """
    Unified compliance checker for platform infrastructure

    Previously: /infrastructure/tools/project-manager/
    Now: Part of DevOps Agent toolkit
    """

    def __init__(self):
        self.checks_passed = 0
        self.checks_failed = 0
        self.checks_warnings = 0

    async def run_all_checks(self) -> Dict:
        """
        Run all 6 priority compliance checks

        Returns:
            {
                "timestamp": "...",
                "overall_status": "OK|WARNING|CRITICAL",
                "checks": {
                    "priority_1_ports": {...},
                    "priority_2_metrics": {...},
                    "priority_3_database": {...},
                    "priority_4_kpi": {...},
                    "priority_5_eventbus": {...},
                    "priority_6_orchestrator": {...}
                },
                "summary": {
                    "passed": 5,
                    "failed": 1,
                    "warnings": 0,
                    "total": 6
                }
            }
        """
        results = {
            "timestamp": datetime.utcnow().isoformat(),
            "checks": {},
            "summary": {}
        }

        # Priority 1: Port Conflicts
        results["checks"]["priority_1_ports"] = await self._check_ports()

        # Priority 2: Metrics Integration
        results["checks"]["priority_2_metrics"] = await self._check_metrics()

        # Priority 3: Database Connections
        results["checks"]["priority_3_database"] = await self._check_database()

        # Priority 4: KPI Registration
        results["checks"]["priority_4_kpi"] = await self._check_kpi()

        # Priority 5: EventBus Events
        results["checks"]["priority_5_eventbus"] = await self._check_eventbus()

        # Priority 6: Orchestrator Control
        results["checks"]["priority_6_orchestrator"] = await self._check_orchestrator()

        # Calculate summary
        results["summary"] = self._calculate_summary(results["checks"])
        results["overall_status"] = self._determine_overall_status(results["summary"])

        return results

    async def _check_ports(self) -> Dict:
        """Priority 1: Port conflicts check"""
        try:
            from priority_1_port_conflicts import check_port_conflicts
            result = check_port_conflicts()
            return self._normalize_result(result, "ports")
        except Exception as e:
            return {"status": "ERROR", "error": str(e), "priority": 1}

    async def _check_metrics(self) -> Dict:
        """Priority 2: Metrics integration check"""
        try:
            from priority_2_metrics_integration import check_metrics_integration
            result = check_metrics_integration()
            return self._normalize_result(result, "metrics")
        except Exception as e:
            return {"status": "ERROR", "error": str(e), "priority": 2}

    async def _check_database(self) -> Dict:
        """Priority 3: Database connections check"""
        try:
            from priority_3_database_connections import check_database_connections
            result = check_database_connections()
            return self._normalize_result(result, "database")
        except Exception as e:
            return {"status": "ERROR", "error": str(e), "priority": 3}

    async def _check_kpi(self) -> Dict:
        """Priority 4: KPI registration check"""
        try:
            from priority_4_kpi_registration import check_kpi_registration
            result = check_kpi_registration()
            return self._normalize_result(result, "kpi")
        except Exception as e:
            return {"status": "ERROR", "error": str(e), "priority": 4}

    async def _check_eventbus(self) -> Dict:
        """Priority 5: EventBus events check"""
        try:
            from priority_5_eventbus_events import check_eventbus_events
            result = check_eventbus_events()
            return self._normalize_result(result, "eventbus")
        except Exception as e:
            return {"status": "ERROR", "error": str(e), "priority": 5}

    async def _check_orchestrator(self) -> Dict:
        """Priority 6: Orchestrator control check"""
        try:
            from priority_6_orchestrator_control import check_orchestrator_control
            result = check_orchestrator_control()
            return self._normalize_result(result, "orchestrator")
        except Exception as e:
            return {"status": "ERROR", "error": str(e), "priority": 6}

    def _normalize_result(self, result: Dict, check_name: str) -> Dict:
        """Normalize check result to standard format"""
        if isinstance(result, dict):
            # Add check name if not present
            if "check" not in result:
                result["check"] = check_name
            return result
        else:
            # Convert boolean to dict
            return {
                "check": check_name,
                "status": "OK" if result else "FAILED"
            }

    def _calculate_summary(self, checks: Dict) -> Dict:
        """Calculate summary statistics"""
        passed = 0
        failed = 0
        warnings = 0
        errors = 0

        for check_result in checks.values():
            status = check_result.get("status", "UNKNOWN")

            if status in ["OK", "PASSED"]:
                passed += 1
            elif status in ["FAILED", "CRITICAL"]:
                failed += 1
            elif status == "WARNING":
                warnings += 1
            elif status == "ERROR":
                errors += 1

        total = len(checks)

        return {
            "passed": passed,
            "failed": failed,
            "warnings": warnings,
            "errors": errors,
            "total": total,
            "pass_rate": round((passed / total * 100), 2) if total > 0 else 0
        }

    def _determine_overall_status(self, summary: Dict) -> str:
        """Determine overall status from summary"""
        if summary["failed"] > 0 or summary["errors"] > 0:
            return "CRITICAL"
        elif summary["warnings"] > 0:
            return "WARNING"
        else:
            return "OK"

    def export_state_for_mio_manager(self) -> Dict:
        """
        Export state in format compatible with MIO Manager

        Previously used by:
        /infrastructure/AI-office-infrastructure/mio-manager/monitoring/infrastructure_state.py
        """
        import asyncio

        # Run checks synchronously for compatibility
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        results = loop.run_until_complete(self.run_all_checks())
        loop.close()

        return {
            "timestamp": results["timestamp"],
            "overall_status": results["overall_status"],
            "compliance_checks": results["checks"],
            "summary": results["summary"],
            "source": "devops-agent-compliance-toolkit"
        }
