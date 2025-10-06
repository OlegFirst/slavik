"""
BIA Report Service - Reporting & Analytics

BIA summary reports, critical processes, and dependency mapping.
Extracted from original endpoints without loss of functionality.
"""

import logging
import numpy as np
from typing import Dict, Any, List

from ..models.domain import BIASummaryReport
from ..models.enums import ProcessStatus
from ..repositories.bia_repository import BIARepository

logger = logging.getLogger(__name__)


class ReportService:
    """Report Service for BIA analytics"""

    def __init__(self, repository: BIARepository):
        self.repo = repository

    async def get_summary_report(self, tenant_id: str) -> BIASummaryReport:
        """
        Get BIA summary report for tenant.

        Original logic from GET /api/bia/reports/summary preserved.
        """
        processes = await self.repo.list(tenant_id)

        if not processes:
            return BIASummaryReport(
                tenant_id=tenant_id,
                total_processes=0,
                critical_processes=0,
                average_rto_hours=0,
                total_potential_loss_24h=0,
                top_critical_processes=[],
                bia_completion_rate=0
            )

        # Critical processes (original logic)
        critical_processes = [
            p for p in processes
            if p.criticality_score and p.criticality_score >= 4
        ]

        # Completed processes (original logic)
        completed_processes = [
            p for p in processes
            if p.status == ProcessStatus.COMPLETED
        ]

        # Average RTO (original logic)
        avg_rto = np.mean([p.rto_hours for p in processes]) if processes else 0

        # Total potential loss 24h (original logic)
        total_loss_24h = sum([
            p.financial_impact.get("24_hours", 0) if p.financial_impact else 0
            for p in processes
        ])

        # Top critical processes (original logic)
        top_critical = sorted(
            critical_processes,
            key=lambda p: (p.criticality_score or 0, -(p.rto_hours or 999)),
            reverse=True
        )[:10]

        return BIASummaryReport(
            tenant_id=tenant_id,
            total_processes=len(processes),
            critical_processes=len(critical_processes),
            average_rto_hours=float(avg_rto),
            total_potential_loss_24h=total_loss_24h,
            top_critical_processes=[
                {
                    "id": p.id,
                    "name": p.name,
                    "criticality": p.criticality_score,
                    "rto_hours": p.rto_hours,
                    "financial_impact_24h": p.financial_impact.get("24_hours", 0) if p.financial_impact else 0
                }
                for p in top_critical
            ],
            bia_completion_rate=len(completed_processes) / len(processes) if processes else 0
        )

    async def get_critical_processes_report(
        self,
        tenant_id: str
    ) -> Dict[str, Any]:
        """
        Get critical processes report grouped by tier.

        Original logic from GET /api/bia/reports/critical-processes preserved.
        """
        # Get all processes
        all_processes = await self.repo.list(tenant_id)

        # Filter critical (original logic)
        processes = [
            p for p in all_processes
            if p.criticality_score and p.criticality_score >= 4
        ]

        # Group by criticality (original logic)
        by_criticality = {
            5: [p for p in processes if p.criticality_score == 5],
            4: [p for p in processes if p.criticality_score == 4]
        }

        return {
            "tenant_id": tenant_id,
            "total_critical_processes": len(processes),
            "tier_1_critical": len(by_criticality[5]),
            "tier_2_high": len(by_criticality[4]),
            "processes": [
                {
                    "id": p.id,
                    "name": p.name,
                    "criticality": p.criticality_score,
                    "rto_hours": p.rto_hours,
                    "rpo_hours": p.rpo_hours,
                    "mtpd_hours": p.mtpd_hours,
                    "who_tier": p.who_tier,
                    "patient_safety_impact": p.patient_safety_impact
                }
                for p in sorted(
                    processes,
                    key=lambda x: (x.criticality_score or 0),
                    reverse=True
                )
            ]
        }

    async def get_dependencies_report(
        self,
        tenant_id: str
    ) -> Dict[str, Any]:
        """
        Get dependencies mapping report with graph.

        Original logic from GET /api/bia/reports/dependencies preserved.
        """
        processes = await self.repo.list(tenant_id)

        # Build dependency graph (original logic)
        dependency_graph = {
            "nodes": [],
            "edges": []
        }

        for process in processes:
            dependency_graph["nodes"].append({
                "id": process.id,
                "name": process.name,
                "criticality": process.criticality_score,
                "type": "process"
            })

            for dep in process.dependencies:
                dependency_graph["edges"].append({
                    "source": process.id,
                    "target": dep.id if dep.id else dep.name,
                    "type": dep.type,
                    "criticality": dep.criticality
                })

        return {
            "tenant_id": tenant_id,
            "total_processes": len(processes),
            "total_dependencies": sum(len(p.dependencies) for p in processes),
            "dependency_graph": dependency_graph
        }
