#!/usr/bin/env python3
"""
AI Workflow Optimizer Client
Integrates with existing AI Workflow Optimizer service for enhanced code generation
"""

import asyncio
import httpx
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class WorkflowOptimizerClient:
    """Client for AI Workflow Optimizer service integration"""

    def __init__(self, optimizer_url: str = "http://localhost:8080"):
        """Initialize workflow optimizer client"""
        self.optimizer_url = optimizer_url
        self.client = httpx.AsyncClient(timeout=30.0)

    async def optimize_architecture_workflow(self, architecture: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optimize architecture using ML-powered workflow insights

        Args:
            architecture: Architecture analysis data

        Returns:
            Optimized architecture with workflow recommendations
        """
        try:
            # Transform architecture data to workflow format
            workflow_data = self._transform_to_workflow_data(architecture)

            # Get optimization recommendations
            optimization_result = await self._call_optimizer_api(workflow_data)

            # Enhance architecture with optimization insights
            enhanced_architecture = self._enhance_architecture_with_insights(
                architecture, optimization_result
            )

            return enhanced_architecture

        except Exception as e:
            logger.warning(f"Workflow optimization failed, using original architecture: {e}")
            return architecture

    def _transform_to_workflow_data(self, architecture: Dict[str, Any]) -> Dict[str, Any]:
        """Transform architecture data to workflow optimizer format"""

        pattern = architecture.get("pattern", "monolith")
        components = architecture.get("components", [])
        languages = architecture.get("languages", ["python"])
        frameworks = architecture.get("frameworks", [])

        # Calculate complexity based on architecture
        complexity = self._calculate_architecture_complexity(architecture)

        # Estimate workflow parameters
        workflow_data = {
            "process_name": f"deploy_{pattern}_architecture",
            "department": "IT",
            "category": "deployment",
            "complexity": complexity,
            "resource_count": len(components) if components else 1,
            "stakeholder_count": min(5 + len(components), 15),
            "step_count": self._estimate_deployment_steps(architecture),
            "technologies": languages + frameworks,
            "architecture_pattern": pattern
        }

        return workflow_data

    def _calculate_architecture_complexity(self, architecture: Dict[str, Any]) -> int:
        """Calculate architecture complexity (1-3)"""

        pattern = architecture.get("pattern", "monolith")
        components = len(architecture.get("components", []))
        languages = len(architecture.get("languages", []))
        frameworks = len(architecture.get("frameworks", []))

        # Base complexity by pattern
        base_complexity = {
            "monolith": 1,
            "serverless": 2,
            "microservices": 3,
            "hybrid": 3
        }.get(pattern, 2)

        # Adjust based on complexity factors
        if components > 5:
            base_complexity = min(3, base_complexity + 1)
        if languages > 2 or frameworks > 3:
            base_complexity = min(3, base_complexity + 1)

        return base_complexity

    def _estimate_deployment_steps(self, architecture: Dict[str, Any]) -> int:
        """Estimate number of deployment steps"""

        pattern = architecture.get("pattern", "monolith")
        components = len(architecture.get("components", []))

        base_steps = {
            "monolith": 6,      # Build, test, package, deploy, verify, monitor
            "serverless": 8,    # Package, deploy functions, configure triggers, test
            "microservices": 10, # Build services, deploy gateway, configure networking
            "hybrid": 12        # Complex multi-stage deployment
        }.get(pattern, 8)

        # Add steps for multiple components
        return base_steps + max(0, components - 1) * 2

    async def _call_optimizer_api(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Call the AI Workflow Optimizer API"""

        try:
            # First, check if optimizer service is available
            health_response = await self.client.get(f"{self.optimizer_url}/health")
            if health_response.status_code != 200:
                raise Exception("Optimizer service not available")

            # Get performance prediction
            performance_response = await self.client.post(
                f"{self.optimizer_url}/api/v1/optimize/performance",
                json=workflow_data
            )

            if performance_response.status_code == 200:
                performance_data = performance_response.json()
            else:
                performance_data = {}

            # Get resource optimization
            try:
                resource_response = await self.client.post(
                    f"{self.optimizer_url}/api/v1/optimize/resources",
                    json={
                        "process_id": "arch_deployment",
                        "current_allocation": {
                            "cpu_cores": workflow_data.get("resource_count", 2),
                            "memory_gb": workflow_data.get("resource_count", 2) * 2,
                            "storage_gb": 50
                        }
                    }
                )

                if resource_response.status_code == 200:
                    resource_data = resource_response.json()
                else:
                    resource_data = {}

            except Exception:
                resource_data = {}

            return {
                "performance_prediction": performance_data,
                "resource_optimization": resource_data,
                "optimization_timestamp": asyncio.get_event_loop().time()
            }

        except Exception as e:
            logger.warning(f"Failed to call optimizer API: {e}")
            # Return mock optimization data as fallback
            return self._generate_mock_optimization(workflow_data)

    def _generate_mock_optimization(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate mock optimization data when service is unavailable"""

        complexity = workflow_data.get("complexity", 2)
        resource_count = workflow_data.get("resource_count", 2)

        return {
            "performance_prediction": {
                "predicted_execution_time": complexity * 15 + resource_count * 5,
                "confidence_score": 0.85,
                "recommendations": [
                    "Consider parallel deployment for faster execution",
                    "Implement health checks for reliability",
                    "Use container orchestration for scalability"
                ]
            },
            "resource_optimization": {
                "optimized_allocation": {
                    "cpu_cores": max(2, resource_count),
                    "memory_gb": max(4, resource_count * 2),
                    "storage_gb": max(20, resource_count * 10)
                },
                "cost_savings": 15.5,
                "recommendations": [
                    "Use auto-scaling for cost optimization",
                    "Implement resource monitoring",
                    "Consider spot instances for non-critical workloads"
                ]
            },
            "mock_data": True
        }

    def _enhance_architecture_with_insights(self,
                                          architecture: Dict[str, Any],
                                          optimization: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance architecture with optimization insights"""

        enhanced = architecture.copy()

        # Add optimization metadata
        enhanced["workflow_optimization"] = {
            "performance_insights": optimization.get("performance_prediction", {}),
            "resource_insights": optimization.get("resource_optimization", {}),
            "optimized": True,
            "optimization_timestamp": optimization.get("optimization_timestamp")
        }

        # Enhance deployment strategy based on predictions
        performance = optimization.get("performance_prediction", {})
        if performance:
            predicted_time = performance.get("predicted_execution_time", 30)

            if predicted_time > 60:  # Long deployment
                enhanced["deployment_strategy"] = "parallel_staged"
                enhanced["deployment_recommendations"] = [
                    "Use parallel deployment stages",
                    "Implement progressive rollout",
                    "Add automated rollback capabilities"
                ]
            else:
                enhanced["deployment_strategy"] = "standard"
                enhanced["deployment_recommendations"] = [
                    "Standard deployment process",
                    "Monitor deployment metrics",
                    "Implement health checks"
                ]

        # Add resource optimization
        resource_insights = optimization.get("resource_optimization", {})
        if resource_insights:
            optimized_allocation = resource_insights.get("optimized_allocation", {})
            enhanced["resource_recommendations"] = {
                "cpu_cores": optimized_allocation.get("cpu_cores", 2),
                "memory_gb": optimized_allocation.get("memory_gb", 4),
                "storage_gb": optimized_allocation.get("storage_gb", 20),
                "cost_optimization": resource_insights.get("recommendations", [])
            }

        return enhanced

    async def get_workflow_insights(self, architecture: Dict[str, Any]) -> Dict[str, Any]:
        """Get workflow insights for architecture explanation"""

        try:
            optimization = await self._call_optimizer_api(
                self._transform_to_workflow_data(architecture)
            )

            insights = {
                "deployment_complexity": self._calculate_architecture_complexity(architecture),
                "estimated_deployment_time": optimization.get(
                    "performance_prediction", {}
                ).get("predicted_execution_time", 30),
                "resource_requirements": optimization.get(
                    "resource_optimization", {}
                ).get("optimized_allocation", {}),
                "workflow_recommendations": []
            }

            # Add specific recommendations
            performance = optimization.get("performance_prediction", {})
            if performance:
                insights["workflow_recommendations"].extend(
                    performance.get("recommendations", [])
                )

            resource_opt = optimization.get("resource_optimization", {})
            if resource_opt:
                insights["workflow_recommendations"].extend(
                    resource_opt.get("recommendations", [])
                )

            return insights

        except Exception as e:
            logger.warning(f"Failed to get workflow insights: {e}")
            return {
                "deployment_complexity": 2,
                "estimated_deployment_time": 30,
                "resource_requirements": {"cpu_cores": 2, "memory_gb": 4},
                "workflow_recommendations": [
                    "Monitor deployment process",
                    "Implement automated testing",
                    "Use infrastructure as code"
                ]
            }

    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()