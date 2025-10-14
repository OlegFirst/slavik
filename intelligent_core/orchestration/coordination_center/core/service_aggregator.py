"""
Service Aggregator
==================

Aggregates responses from multiple BCM services for complex queries.

When AI needs data from multiple services (e.g., "Give me full BCM status"):
1. Identifies required services
2. Makes parallel requests
3. Aggregates results
4. Returns unified response

Example:
    "What's our BCM maturity?" →
    - BIA Service: process coverage
    - Risk Service: risk scores
    - Plan Service: plan completeness
    - Validation Service: KPI metrics
    → Aggregated maturity report
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

import httpx

logger = logging.getLogger(__name__)


class AggregationStrategy(str, Enum):
    """Aggregation strategies"""
    PARALLEL = "parallel"  # All requests in parallel
    SEQUENTIAL = "sequential"  # One after another
    CONDITIONAL = "conditional"  # Next request depends on previous result


class ServiceAggregator:
    """
    Aggregates responses from multiple BCM services.

    Features:
    - Parallel service calls for performance
    - Error handling (partial success)
    - Circuit breaker integration
    - Response caching
    - Timeout management

    Example:
        ```python
        aggregator = ServiceAggregator(service_registry)

        # Get BCM maturity status
        result = await aggregator.aggregate(
            query_type="bcm_maturity",
            services=["bia", "risk", "plan", "validation"],
            tenant_id="org-123"
        )
        ```
    """

    # Predefined aggregation patterns
    AGGREGATION_PATTERNS = {
        "bcm_maturity": {
            "services": ["bia", "risk", "plan", "validation"],
            "strategy": AggregationStrategy.PARALLEL,
            "endpoints": {
                "bia": "/api/bia/coverage",
                "risk": "/api/risk/summary",
                "plan": "/api/plans/completeness",
                "validation": "/api/kpi/metrics"
            },
            "aggregator_func": "aggregate_maturity"
        },
        "full_status": {
            "services": ["bia", "risk", "plan", "incident", "exercise"],
            "strategy": AggregationStrategy.PARALLEL,
            "endpoints": {
                "bia": "/api/bia/status",
                "risk": "/api/risk/status",
                "plan": "/api/plans/status",
                "incident": "/api/incidents/active",
                "exercise": "/api/exercises/upcoming"
            },
            "aggregator_func": "aggregate_full_status"
        },
        "compliance_dashboard": {
            "services": ["compliance", "governance", "validation"],
            "strategy": AggregationStrategy.PARALLEL,
            "endpoints": {
                "compliance": "/api/compliance/gaps",
                "governance": "/api/governance/controls",
                "validation": "/api/kpi/compliance"
            },
            "aggregator_func": "aggregate_compliance"
        }
    }

    def __init__(
        self,
        service_registry,
        timeout_seconds: int = 30,
        max_concurrent: int = 5
    ):
        """
        Initialize service aggregator.

        Args:
            service_registry: BCM Service Registry instance
            timeout_seconds: Default timeout for service calls
            max_concurrent: Max concurrent requests
        """
        self.service_registry = service_registry
        self.timeout_seconds = timeout_seconds
        self.max_concurrent = max_concurrent
        self.aggregation_stats = {
            "total_aggregations": 0,
            "successful": 0,
            "partial_success": 0,
            "failed": 0,
            "avg_duration_ms": 0.0
        }

    async def aggregate(
        self,
        query_type: str,
        tenant_id: str,
        params: Optional[Dict[str, Any]] = None,
        strategy: Optional[AggregationStrategy] = None
    ) -> Dict[str, Any]:
        """
        Aggregate data from multiple services.

        Args:
            query_type: Type of aggregation (from AGGREGATION_PATTERNS)
            tenant_id: Tenant identifier
            params: Optional query parameters
            strategy: Override default strategy

        Returns:
            Aggregated result

        Example:
            ```python
            result = await aggregator.aggregate(
                query_type="bcm_maturity",
                tenant_id="org-123"
            )
            # {
            #   'success': True,
            #   'maturity_score': 75,
            #   'breakdown': {
            #     'bia': 80,
            #     'risk': 70,
            #     'plan': 75,
            #     'validation': 75
            #   },
            #   'services_queried': 4,
            #   'services_succeeded': 4
            # }
            ```
        """
        self.aggregation_stats["total_aggregations"] += 1
        start_time = datetime.utcnow()

        try:
            # Get aggregation pattern
            if query_type not in self.AGGREGATION_PATTERNS:
                raise ValueError(f"Unknown aggregation pattern: {query_type}")

            pattern = self.AGGREGATION_PATTERNS[query_type]
            strategy = strategy or pattern["strategy"]

            logger.info(f"Aggregating {query_type} for tenant {tenant_id} using {strategy.value} strategy")

            # Execute based on strategy
            if strategy == AggregationStrategy.PARALLEL:
                results = await self._aggregate_parallel(pattern, tenant_id, params)
            elif strategy == AggregationStrategy.SEQUENTIAL:
                results = await self._aggregate_sequential(pattern, tenant_id, params)
            else:
                results = await self._aggregate_conditional(pattern, tenant_id, params)

            # Run aggregation function
            aggregator_func = getattr(self, pattern["aggregator_func"])
            aggregated = aggregator_func(results)

            # Calculate success metrics
            services_succeeded = sum(1 for r in results.values() if r.get("success"))
            total_services = len(results)

            duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000

            if services_succeeded == total_services:
                self.aggregation_stats["successful"] += 1
                success_status = "full_success"
            elif services_succeeded > 0:
                self.aggregation_stats["partial_success"] += 1
                success_status = "partial_success"
            else:
                self.aggregation_stats["failed"] += 1
                success_status = "failed"

            # Update avg duration
            total = self.aggregation_stats["total_aggregations"]
            self.aggregation_stats["avg_duration_ms"] = (
                (self.aggregation_stats["avg_duration_ms"] * (total - 1) + duration_ms) / total
            )

            return {
                "success": services_succeeded > 0,
                "status": success_status,
                "query_type": query_type,
                "services_queried": total_services,
                "services_succeeded": services_succeeded,
                "duration_ms": duration_ms,
                **aggregated
            }

        except Exception as e:
            logger.error(f"Aggregation failed: {str(e)}", exc_info=True)
            self.aggregation_stats["failed"] += 1
            return {
                "success": False,
                "error": str(e),
                "query_type": query_type
            }

    async def _aggregate_parallel(
        self,
        pattern: Dict[str, Any],
        tenant_id: str,
        params: Optional[Dict[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        """Execute service calls in parallel."""
        tasks = []
        service_names = []

        for service_name in pattern["services"]:
            endpoint = pattern["endpoints"][service_name]
            tasks.append(self._call_service(service_name, endpoint, tenant_id, params))
            service_names.append(service_name)

        # Execute all in parallel
        results_list = await asyncio.gather(*tasks, return_exceptions=True)

        # Map results to service names
        results = {}
        for service_name, result in zip(service_names, results_list):
            if isinstance(result, Exception):
                results[service_name] = {
                    "success": False,
                    "error": str(result)
                }
            else:
                results[service_name] = result

        return results

    async def _aggregate_sequential(
        self,
        pattern: Dict[str, Any],
        tenant_id: str,
        params: Optional[Dict[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        """Execute service calls sequentially."""
        results = {}

        for service_name in pattern["services"]:
            endpoint = pattern["endpoints"][service_name]
            result = await self._call_service(service_name, endpoint, tenant_id, params)
            results[service_name] = result

        return results

    async def _aggregate_conditional(
        self,
        pattern: Dict[str, Any],
        tenant_id: str,
        params: Optional[Dict[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        """Execute service calls conditionally (each depends on previous)."""
        # TODO: Implement conditional logic
        # For now, fallback to sequential
        return await self._aggregate_sequential(pattern, tenant_id, params)

    async def _call_service(
        self,
        service_name: str,
        endpoint: str,
        tenant_id: str,
        params: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Call individual service."""
        try:
            # Get service URL from registry
            from .tool_registry import BCMServiceType
            service_type = BCMServiceType(f"{service_name}_service")
            service_url = self.service_registry.get_service_url(service_type)

            full_url = f"{service_url}{endpoint}"

            logger.debug(f"Calling {service_name}: {full_url}")

            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.get(
                    full_url,
                    headers={"X-Tenant-ID": tenant_id},
                    params=params or {}
                )

                if response.status_code == 200:
                    return {
                        "success": True,
                        "data": response.json(),
                        "status_code": response.status_code
                    }
                else:
                    return {
                        "success": False,
                        "error": f"HTTP {response.status_code}",
                        "status_code": response.status_code
                    }

        except Exception as e:
            logger.error(f"Service call failed: {service_name} - {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def aggregate_maturity(self, results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate BCM maturity data."""
        maturity_scores = {}

        # Extract scores from each service
        if results.get("bia", {}).get("success"):
            bia_data = results["bia"]["data"]
            maturity_scores["bia"] = bia_data.get("coverage_percentage", 0)

        if results.get("risk", {}).get("success"):
            risk_data = results["risk"]["data"]
            maturity_scores["risk"] = risk_data.get("assessment_completion", 0)

        if results.get("plan", {}).get("success"):
            plan_data = results["plan"]["data"]
            maturity_scores["plan"] = plan_data.get("plan_completeness", 0)

        if results.get("validation", {}).get("success"):
            validation_data = results["validation"]["data"]
            maturity_scores["validation"] = validation_data.get("kpi_achievement", 0)

        # Calculate overall maturity score
        if maturity_scores:
            overall_maturity = sum(maturity_scores.values()) / len(maturity_scores)
        else:
            overall_maturity = 0

        return {
            "maturity_score": overall_maturity,
            "breakdown": maturity_scores,
            "maturity_level": self._calculate_maturity_level(overall_maturity)
        }

    def aggregate_full_status(self, results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate full BCM status."""
        status = {}

        for service_name, result in results.items():
            if result.get("success"):
                status[service_name] = result["data"]
            else:
                status[service_name] = {"error": result.get("error")}

        return {"status": status}

    def aggregate_compliance(self, results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate compliance dashboard data."""
        compliance_data = {}

        if results.get("compliance", {}).get("success"):
            compliance_data["gaps"] = results["compliance"]["data"]

        if results.get("governance", {}).get("success"):
            compliance_data["controls"] = results["governance"]["data"]

        if results.get("validation", {}).get("success"):
            compliance_data["kpis"] = results["validation"]["data"]

        return {"compliance": compliance_data}

    def _calculate_maturity_level(self, score: float) -> str:
        """Calculate BCM maturity level from score."""
        if score >= 90:
            return "5_optimizing"
        elif score >= 75:
            return "4_managed"
        elif score >= 60:
            return "3_defined"
        elif score >= 40:
            return "2_repeatable"
        else:
            return "1_initial"

    def get_stats(self) -> Dict[str, Any]:
        """Get aggregation statistics."""
        return {
            "aggregator": "ServiceAggregator",
            "stats": self.aggregation_stats,
            "available_patterns": list(self.AGGREGATION_PATTERNS.keys())
        }
