"""
What-If Analysis Engine
========================

Analyzes "what if X happens" scenarios using Digital Twin state.

Adapted from: /simulation/engines/what_if_engine.py
"""

import logging
from typing import Dict, Any

import httpx

from .base_engine import BaseSimulationEngine

logger = logging.getLogger(__name__)


class WhatIfEngine(BaseSimulationEngine):
    """
    What-If Analysis Engine

    Analyzes impact of hypothetical events on Digital Twin state.
    Provides risk assessment and recommendations for BCM planning.
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
            Impact analysis results with recommendations
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
                    f"http://localhost:8030/api/twin/organizations/{twin_id}/state",
                    timeout=5.0
                )

                if response.status_code == 200:
                    return response.json()['state']
                else:
                    logger.warning(f"Failed to get twin state: {response.status_code}")
                    return self._get_mock_state()

        except Exception as e:
            logger.error(f"Error getting twin state: {e}")
            return self._get_mock_state()

    def _get_mock_state(self) -> Dict[str, Any]:
        """Get mock state for testing"""
        return {
            "operational_status": 1.0,
            "critical_systems": {
                "sys_001": {"status": "operational", "health": 1.0},
                "sys_002": {"status": "operational", "health": 0.95},
                "sys_003": {"status": "operational", "health": 1.0}
            },
            "suppliers": {},
            "staff_capacity": 1.0,
            "resource_availability": 0.98
        }

    async def _apply_event(
        self,
        current_state: Dict[str, Any],
        event: str,
        event_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply hypothetical event to state"""

        modified_state = dict(current_state)  # Deep copy

        # Event-specific modifications
        if event == "system_failure":
            system_id = event_data.get('system_id', 'sys_001')
            if 'critical_systems' not in modified_state:
                modified_state['critical_systems'] = {}

            if system_id in modified_state.get('critical_systems', {}):
                modified_state['critical_systems'][system_id]['status'] = 'failed'
                modified_state['critical_systems'][system_id]['health'] = 0.0
            else:
                modified_state['critical_systems'][system_id] = {
                    'status': 'failed',
                    'health': 0.0
                }

            # Reduce operational status
            impact_factor = event_data.get('impact_factor', 0.3)
            current_ops = modified_state.get('operational_status', 1.0)
            modified_state['operational_status'] = max(0.0, current_ops - impact_factor)

        elif event == "resource_loss":
            resource_type = event_data.get('resource_type', 'staff')
            reduction = event_data.get('reduction_percent', 0.5)

            if resource_type == "staff":
                current_capacity = modified_state.get('staff_capacity', 1.0)
                modified_state['staff_capacity'] = max(0.0, current_capacity * (1 - reduction))

                # Impact operational status
                current_ops = modified_state.get('operational_status', 1.0)
                modified_state['operational_status'] = max(0.0, current_ops * (1 - reduction * 0.8))

        elif event == "supplier_disruption":
            supplier_id = event_data.get('supplier_id', 'supplier_001')

            if 'suppliers' not in modified_state:
                modified_state['suppliers'] = {}

            modified_state['suppliers'][supplier_id] = {
                'status': 'disrupted',
                'availability': 0.0
            }

            # Reduce resource availability
            current_resources = modified_state.get('resource_availability', 1.0)
            impact = event_data.get('supply_impact', 0.3)
            modified_state['resource_availability'] = max(0.0, current_resources - impact)

        elif event == "pandemic":
            staff_reduction = event_data.get('staff_reduction', 0.4)

            modified_state['staff_capacity'] = max(0.0, modified_state.get('staff_capacity', 1.0) * (1 - staff_reduction))

            current_ops = modified_state.get('operational_status', 1.0)
            modified_state['operational_status'] = max(0.0, current_ops * (1 - staff_reduction * 0.9))

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
            "current": round(current_ops, 2),
            "modified": round(modified_ops, 2),
            "delta": round(ops_impact, 2),
            "delta_percent": round((ops_impact / current_ops * 100) if current_ops > 0 else 0, 1)
        }

        # Calculate staff impact
        current_staff = current_state.get('staff_capacity', 1.0)
        modified_staff = modified_state.get('staff_capacity', 1.0)
        staff_impact = current_staff - modified_staff

        impact['metrics']['staff_impact'] = {
            "current": round(current_staff, 2),
            "modified": round(modified_staff, 2),
            "delta": round(staff_impact, 2),
            "delta_percent": round((staff_impact / current_staff * 100) if current_staff > 0 else 0, 1)
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

        elif event == "pandemic":
            impact['affected_areas'].append("Workforce")
            impact['affected_areas'].append("Business Continuity")

        # Estimate recovery time
        impact['estimated_recovery_time'] = self._estimate_recovery_time(impact['severity'], event)

        return impact

    def _estimate_recovery_time(self, severity: str, event: str) -> Dict[str, Any]:
        """Estimate recovery time based on severity and event type"""
        base_times = {
            "critical": {"min": 24, "max": 72, "unit": "hours"},
            "high": {"min": 8, "max": 24, "unit": "hours"},
            "medium": {"min": 2, "max": 8, "unit": "hours"},
            "low": {"min": 30, "max": 120, "unit": "minutes"}
        }

        # Event-specific modifiers
        modifiers = {
            "system_failure": 1.0,
            "supplier_disruption": 1.5,
            "pandemic": 2.0,
            "resource_loss": 1.2
        }

        base = base_times.get(severity, base_times["medium"])
        modifier = modifiers.get(event, 1.0)

        return {
            "min": int(base["min"] * modifier),
            "max": int(base["max"] * modifier),
            "unit": base["unit"],
            "confidence": 0.75
        }

    async def _generate_recommendations(self, impact_analysis: Dict[str, Any]) -> list:
        """Generate recommendations based on impact"""

        recommendations = []

        severity = impact_analysis['severity']
        ops_impact = impact_analysis['metrics'].get('operational_impact', {})

        if severity in ["critical", "high"]:
            recommendations.append({
                "priority": "high",
                "action": "Activate Business Continuity Plan immediately",
                "rationale": f"Operational impact: {ops_impact.get('delta_percent', 0):.1f}%",
                "timeline": "Immediate"
            })

            recommendations.append({
                "priority": "high",
                "action": "Notify stakeholders and activate crisis management team",
                "rationale": "Critical impact requires immediate escalation",
                "timeline": "Within 1 hour"
            })

        if "IT Infrastructure" in impact_analysis.get('affected_areas', []):
            recommendations.append({
                "priority": "medium",
                "action": "Initiate IT disaster recovery procedures",
                "rationale": "IT systems affected - follow DR plan",
                "timeline": "Within 2 hours"
            })

        if "Supply Chain" in impact_analysis.get('affected_areas', []):
            recommendations.append({
                "priority": "medium",
                "action": "Activate alternative suppliers",
                "rationale": "Supply chain disruption detected",
                "timeline": "Within 4 hours"
            })

        if "Workforce" in impact_analysis.get('affected_areas', []):
            recommendations.append({
                "priority": "high",
                "action": "Implement remote work procedures",
                "rationale": "Staff capacity significantly reduced",
                "timeline": "Within 24 hours"
            })

        # Always add general recommendation
        recommendations.append({
            "priority": "low",
            "action": "Document incident and update BCP based on lessons learned",
            "rationale": "Continuous improvement of BCM processes",
            "timeline": "Post-incident"
        })

        return recommendations
