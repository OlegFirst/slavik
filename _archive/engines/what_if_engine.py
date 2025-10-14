"""
What-If Analysis Engine

Analyzes "what if X happens" scenarios
"""

import sys
from pathlib import Path
from typing import Dict, Any
import httpx

sys.path.insert(0, str(Path(__file__).parent))
from base_engine import BaseSimulationEngine


class WhatIfEngine(BaseSimulationEngine):
    """
    What-If Analysis Engine

    Analyzes impact of hypothetical events on Digital Twin state
    """

    def validate_parameters(self) -> bool:
        """Validate parameters"""
        required = ['twin_id', 'event']

        for param in required:
            if param not in self.parameters:
                raise ValueError(f"Missing required parameter: {param}")

        return True

    async def run(self) -> Dict[str, Any]:
        """
        Run what-if analysis

        Parameters:
            - twin_id: Digital Twin organization ID
            - event: Event description (e.g., "system_failure", "resource_loss")
            - event_data: Event-specific data

        Returns:
            Impact analysis results
        """
        self.validate_parameters()

        twin_id = self.parameters['twin_id']
        event = self.parameters['event']
        event_data = self.parameters.get('event_data', {})

        self.log_progress("Starting what-if analysis", 0)

        # Get current Digital Twin state
        current_state = await self._get_twin_state(twin_id)

        self.log_progress("Retrieved current state", 20)

        # Apply hypothetical event
        modified_state = await self._apply_event(current_state, event, event_data)

        self.log_progress("Applied hypothetical event", 40)

        # Analyze impact
        impact_analysis = await self._analyze_impact(
            current_state,
            modified_state,
            event,
            event_data
        )

        self.log_progress("Completed impact analysis", 80)

        # Generate recommendations
        recommendations = await self._generate_recommendations(impact_analysis)

        self.log_progress("Generated recommendations", 100)

        return {
            "simulation_id": self.simulation_id,
            "event": event,
            "event_data": event_data,
            "current_state": current_state,
            "modified_state": modified_state,
            "impact_analysis": impact_analysis,
            "recommendations": recommendations,
            "confidence": 0.85
        }

    async def _get_twin_state(self, twin_id: int) -> Dict[str, Any]:
        """Get Digital Twin current state"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"http://localhost:8030/api/twin/organizations/{twin_id}/state"
                )

                if response.status_code == 200:
                    return response.json()['state']
                else:
                    self.logger.warning(f"Failed to get twin state: {response.status_code}")
                    return {}

        except Exception as e:
            self.logger.error(f"Error getting twin state: {e}")
            return {}

    async def _apply_event(
        self,
        current_state: Dict[str, Any],
        event: str,
        event_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply hypothetical event to state"""

        modified_state = current_state.copy()

        # Event-specific modifications
        if event == "system_failure":
            system_id = event_data.get('system_id')
            if system_id and 'critical_systems' in modified_state:
                if system_id in modified_state['critical_systems']:
                    modified_state['critical_systems'][system_id]['status'] = 'failed'
                    modified_state['critical_systems'][system_id]['health'] = 0.0

        elif event == "resource_loss":
            resource_type = event_data.get('resource_type')
            reduction = event_data.get('reduction_percent', 0.5)

            if resource_type == "staff":
                current_capacity = modified_state.get('operational_status', 1.0)
                modified_state['operational_status'] = current_capacity * (1 - reduction)

        elif event == "supplier_disruption":
            supplier_id = event_data.get('supplier_id')
            # Mark supplier as unavailable
            if 'suppliers' not in modified_state:
                modified_state['suppliers'] = {}
            modified_state['suppliers'][supplier_id] = {'status': 'disrupted'}

        return modified_state

    async def _analyze_impact(
        self,
        current_state: Dict[str, Any],
        modified_state: Dict[str, Any],
        event: str,
        event_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze impact of event"""

        impact = {
            "severity": "medium",
            "affected_areas": [],
            "metrics": {}
        }

        # Calculate operational impact
        current_ops = current_state.get('operational_status', 1.0)
        modified_ops = modified_state.get('operational_status', 1.0)
        ops_impact = current_ops - modified_ops

        impact['metrics']['operational_impact'] = {
            "current": current_ops,
            "modified": modified_ops,
            "delta": ops_impact,
            "delta_percent": (ops_impact / current_ops * 100) if current_ops > 0 else 0
        }

        # Determine severity
        if ops_impact > 0.5:
            impact['severity'] = "critical"
        elif ops_impact > 0.25:
            impact['severity'] = "high"
        elif ops_impact > 0.1:
            impact['severity'] = "medium"
        else:
            impact['severity'] = "low"

        # Identify affected areas
        if event == "system_failure":
            impact['affected_areas'].append("IT Infrastructure")
            impact['affected_areas'].append("Business Operations")

        elif event == "resource_loss":
            impact['affected_areas'].append("Human Resources")
            impact['affected_areas'].append("Service Delivery")

        elif event == "supplier_disruption":
            impact['affected_areas'].append("Supply Chain")
            impact['affected_areas'].append("Production")

        return impact

    async def _generate_recommendations(self, impact_analysis: Dict[str, Any]) -> list:
        """Generate recommendations based on impact"""

        recommendations = []

        severity = impact_analysis['severity']
        ops_impact = impact_analysis['metrics'].get('operational_impact', {})

        if severity in ["critical", "high"]:
            recommendations.append({
                "priority": "high",
                "action": "Activate Business Continuity Plan immediately",
                "rationale": f"Operational impact: {ops_impact.get('delta_percent', 0):.1f}%"
            })

            recommendations.append({
                "priority": "high",
                "action": "Notify stakeholders and activate crisis management team",
                "rationale": "Critical impact requires immediate escalation"
            })

        if "IT Infrastructure" in impact_analysis.get('affected_areas', []):
            recommendations.append({
                "priority": "medium",
                "action": "Initiate IT disaster recovery procedures",
                "rationale": "IT systems affected - follow DR plan"
            })

        if "Supply Chain" in impact_analysis.get('affected_areas', []):
            recommendations.append({
                "priority": "medium",
                "action": "Activate alternative suppliers",
                "rationale": "Supply chain disruption detected"
            })

        # Always add a general recommendation
        recommendations.append({
            "priority": "low",
            "action": "Document incident and update BCP based on lessons learned",
            "rationale": "Continuous improvement of BCM processes"
        })

        return recommendations
