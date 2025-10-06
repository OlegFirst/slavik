"""
BIA AI Service - AI Integration

AI-powered RTO suggestions and dependency discovery.
Extracted from original endpoints without loss of functionality.
"""

import logging
import httpx
from typing import Dict, Any, List

from ..models.domain import BIAProcess, AIRTOSuggestion, Dependency
from ..models.enums import CriticalityLevel
from ..repositories.bia_repository import BIARepository
from shared.exceptions import EntityNotFoundError, TenantMismatchError

logger = logging.getLogger(__name__)


class AIService:
    """AI Service for BIA intelligence"""

    def __init__(
        self,
        repository: BIARepository,
        orchestration_url: str = "http://localhost:8002"
    ):
        self.repo = repository
        self.orchestration_url = orchestration_url

    async def call_ai_orchestration(
        self,
        task: str,
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Call AI Orchestration service.

        Original logic from main.py preserved.
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.orchestration_url}/api/ai/route",
                    json={"task": task, "input": input_data},
                    timeout=30.0
                )
                if response.status_code == 200:
                    return response.json()
                return {}
        except Exception as e:
            logger.error(f"AI Orchestration call failed: {e}")
            return {}

    async def suggest_rto(
        self,
        process_id: int,
        tenant_id: str
    ) -> AIRTOSuggestion:
        """
        AI-powered RTO/RPO/MTPD suggestion.

        Original logic from POST /api/bia/processes/{id}/suggest-rto preserved.
        """
        process = await self.repo.get(process_id)
        if not process:
            raise EntityNotFoundError("BIAProcess", str(process_id))
        if process.tenant_id != tenant_id:
            raise TenantMismatchError(tenant_id, process.tenant_id)

        # Call AI Orchestration (original logic)
        ai_result = await self.call_ai_orchestration("bia_rto_suggestion", {
            "process_name": process.name,
            "description": process.description,
            "industry": process.industry,
            "criticality": process.criticality,
            "annual_revenue_impact": process.annual_revenue_impact,
            "geographical_scope": process.geographical_scope
        })

        if not ai_result:
            # Fallback: rule-based suggestion (original logic)
            base_rto = {
                CriticalityLevel.CRITICAL: 2,
                CriticalityLevel.HIGH: 8,
                CriticalityLevel.MODERATE: 24,
                CriticalityLevel.MINOR: 72,
                CriticalityLevel.LOW: 168
            }.get(process.criticality, 24)

            return AIRTOSuggestion(
                suggested_rto_hours=base_rto,
                suggested_rpo_hours=base_rto / 2,
                suggested_mtpd_hours=base_rto * 2,
                confidence=0.7,
                reasoning=f"Rule-based suggestion for {process.criticality} criticality",
                benchmarks={"p25": base_rto * 0.5, "p50": base_rto, "p75": base_rto * 1.5}
            )

        # Parse AI result and update process (original logic)
        suggested_rto = ai_result.get("suggested_rto_hours", process.rto_hours)
        process.ai_suggested_rto = suggested_rto
        process.ai_confidence = ai_result.get("confidence", 0.85)
        process.ai_recommendations = ai_result.get("reasoning", "")

        await self.repo.update(process_id, {
            "ai_suggested_rto": process.ai_suggested_rto,
            "ai_confidence": process.ai_confidence,
            "ai_recommendations": process.ai_recommendations
        })

        return AIRTOSuggestion(
            suggested_rto_hours=suggested_rto,
            suggested_rpo_hours=ai_result.get("suggested_rpo_hours", suggested_rto / 2),
            suggested_mtpd_hours=ai_result.get("suggested_mtpd_hours", suggested_rto * 2),
            confidence=ai_result.get("confidence", 0.85),
            reasoning=ai_result.get("reasoning", "AI-based analysis"),
            benchmarks=ai_result.get("benchmarks", {})
        )

    async def discover_dependencies(
        self,
        process_id: int,
        tenant_id: str
    ) -> Dict[str, Any]:
        """
        AI-powered dependency discovery.

        Original logic from POST /api/bia/processes/{id}/discover-dependencies preserved.
        """
        process = await self.repo.get(process_id)
        if not process:
            raise EntityNotFoundError("BIAProcess", str(process_id))
        if process.tenant_id != tenant_id:
            raise TenantMismatchError(tenant_id, process.tenant_id)

        # Call AI Orchestration (original logic)
        ai_result = await self.call_ai_orchestration("dependency_discovery", {
            "process_name": process.name,
            "description": process.description,
            "industry": process.industry
        })

        if ai_result and "dependencies" in ai_result:
            discovered_deps = [
                Dependency(**dep) for dep in ai_result["dependencies"]
            ]
            process.dependencies.extend(discovered_deps)

            await self.repo.update(process_id, {
                "dependencies": process.dependencies
            })

            return {
                "status": "success",
                "discovered_dependencies": discovered_deps,
                "total_dependencies": len(process.dependencies)
            }

        return {
            "status": "no_ai_result",
            "message": "AI service unavailable, no dependencies discovered"
        }
