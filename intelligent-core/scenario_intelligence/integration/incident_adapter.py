"""
BCM Incident Adapter
Интеграция с Odoo BCM Incident модулем для создания L4 сценариев на основе реальных инцидентов
"""

import httpx
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import hashlib

logger = logging.getLogger(__name__)

# Configuration
ODOO_URL = "http://odoo:8069"
ODOO_API_KEY = None  # Set from env or config


class IncidentScenarioAdapter:
    """
    Adapter для конвертации реальных инцидентов → L4 training scenarios
    Anonymizes и generalizes incidents для создания учебных сценариев
    """

    def __init__(self, odoo_url: str = ODOO_URL, api_key: Optional[str] = None):
        self.odoo_url = odoo_url
        self.api_key = api_key

    async def create_scenario_from_incident(
        self,
        incident_id: str,
        anonymize: bool = True,
        generalize: bool = True
    ) -> Dict[str, Any]:
        """
        Create L4 scenario from real incident

        Args:
            incident_id: Odoo incident ID
            anonymize: Remove sensitive information
            generalize: Make scenario generic/reusable

        Returns:
            L4 scenario dict
        """
        try:
            logger.info(f"Creating scenario from incident: {incident_id}")

            # Get incident from Odoo
            incident = await self._get_odoo_incident(incident_id)

            if not incident:
                raise Exception(f"Incident not found: {incident_id}")

            # Anonymize if requested
            if anonymize:
                incident = self._anonymize_incident(incident)

            # Generalize if requested
            if generalize:
                incident = self._generalize_incident(incident)

            # Convert to L4 scenario
            l4_scenario = self._convert_incident_to_l4_scenario(incident)

            return l4_scenario

        except Exception as e:
            logger.error(f"Failed to create scenario from incident: {e}")
            raise

    async def _get_odoo_incident(self, incident_id: str) -> Optional[Dict[str, Any]]:
        """Get incident from Odoo API"""
        try:
            headers = {}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.odoo_url}/api/v1/bcm_incident/{incident_id}",
                    headers=headers
                )

                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"Failed to get incident: {response.status_code}")
                    return None

        except Exception as e:
            logger.error(f"Error getting incident from Odoo: {e}")
            return None

    def _anonymize_incident(self, incident: Dict[str, Any]) -> Dict[str, Any]:
        """
        Anonymize incident data

        Removes:
        - User names
        - Company names
        - Specific locations
        - IP addresses
        - Internal system names
        """
        anonymized = incident.copy()

        # Anonymize title
        anonymized["title"] = self._anonymize_text(incident.get("title", ""))

        # Anonymize description
        anonymized["description"] = self._anonymize_text(incident.get("description", ""))

        # Remove specific identifiers
        anonymized.pop("reported_by", None)
        anonymized.pop("assigned_to", None)
        anonymized.pop("company_id", None)

        # Hash incident number
        if "incident_number" in anonymized:
            original_number = anonymized["incident_number"]
            anonymized["incident_number"] = self._hash_identifier(original_number)

        return anonymized

    def _anonymize_text(self, text: str) -> str:
        """Anonymize text by replacing specific details"""
        # Simple anonymization - replace common patterns
        replacements = {
            r"\b[A-Z][a-z]+ [A-Z][a-z]+\b": "Person Name",  # Names
            r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b": "IP Address",  # IPs
            r"\b[A-Z][A-Z0-9-]+\b": "System Name",  # System names
            r"http[s]?://[^\s]+": "URL",  # URLs
        }

        import re
        anonymized = text
        for pattern, replacement in replacements.items():
            anonymized = re.sub(pattern, replacement, anonymized)

        return anonymized

    def _hash_identifier(self, identifier: str) -> str:
        """Hash identifier for anonymization"""
        return hashlib.sha256(identifier.encode()).hexdigest()[:16]

    def _generalize_incident(self, incident: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generalize incident to make it reusable

        Converts specific details to generic patterns
        """
        generalized = incident.copy()

        # Generalize timing to relative times
        if "detected_at" in generalized:
            generalized["detection_time_description"] = "T+0 (Initial detection)"

        if "reported_at" in generalized:
            generalized["reporting_time_description"] = "T+15min (Report to management)"

        if "resolved_at" in generalized:
            detected = generalized.get("detected_at")
            resolved = generalized.get("resolved_at")
            if detected and resolved:
                # Calculate duration
                # For generalization, use relative time
                generalized["resolution_time_description"] = "T+4h (Incident resolved)"

        return generalized

    def _convert_incident_to_l4_scenario(self, incident: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert incident to L4 scenario format

        Args:
            incident: Incident dict

        Returns:
            L4 scenario dict
        """
        incident_type = incident.get("incident_type", "operational")
        severity = incident.get("severity", "medium")
        status = incident.get("status", "resolved")

        # Map incident_type to pillar
        pillar_mapping = {
            "cyber": "security",
            "operational": "operational_excellence",
            "natural": "reliability",
            "supply_chain": "reliability",
            "health_safety": "operational_excellence",
            "financial": "cost_optimization",
            "reputational": "operational_excellence"
        }
        pillar = pillar_mapping.get(incident_type, "operational_excellence")

        # Map severity to complexity
        complexity_mapping = {
            "low": "LOW",
            "medium": "MEDIUM",
            "high": "HIGH",
            "critical": "CRITICAL"
        }
        complexity = complexity_mapping.get(severity, "MEDIUM")

        # Create scenario ID
        scenario_id = f"l4-user-incident-{incident_type}-{incident.get('incident_number', 'unknown')}"

        # Build L4 scenario
        l4_scenario = {
            "meta": {
                "id": scenario_id,
                "version": "1.0.0",
                "level": 4,
                "type": "user_workflow",
                "subtype": "incident_response",
                "pillar": pillar,
                "module": "incident-management",
                "subsystem": "platform-services",
                "tags": [
                    "incident-response",
                    incident_type,
                    f"severity-{severity}",
                    "real-world-based"
                ],
                "created_at": datetime.now().isoformat(),
                "source": "odoo-bcm-incident",
                "based_on_real_incident": True
            },
            "description": {
                "title": f"{incident_type.replace('_', ' ').title()} Incident Response",
                "summary": incident.get("description", f"Response to {incident_type} incident")[:200],
                "business_value": f"Train team to respond to {incident_type} incidents based on real-world experience",
                "user_experience": {
                    "role": "Incident Manager / Response Team",
                    "estimated_time": self._estimate_duration(incident),
                    "complexity": complexity,
                    "required_skills": [
                        "Incident management",
                        f"{incident_type.replace('_', ' ').title()} expertise",
                        "Crisis communication",
                        "Decision making under pressure"
                    ]
                },
                "success_criteria": [
                    "Incident detected within SLA",
                    "Response team mobilized quickly",
                    "Impact contained and minimized",
                    "Recovery procedures executed",
                    "Post-incident review completed"
                ],
                "incident_classification": {
                    "type": incident_type,
                    "severity": severity,
                    "original_status": status
                }
            },
            "behavior": {
                "feature": "Incident Response Workflow",
                "scenario": f"Respond to {incident_type.replace('_', ' ')} incident",
                "given": [
                    f"{incident_type.replace('_', ' ').title()} incident detected",
                    f"Severity level: {severity}",
                    "Response team is available",
                    "BCM procedures are in place"
                ],
                "when": [
                    "Incident is detected by monitoring system",
                    "Incident is assessed and classified",
                    "Response team is activated",
                    "Response procedures are executed",
                    "Recovery is initiated"
                ],
                "then": [
                    "Incident is contained",
                    "Impact is minimized",
                    "Services are restored",
                    "Stakeholders are informed",
                    "Lessons learned are captured"
                ]
            },
            "execution": {
                "steps": self._extract_phases_from_incident(incident),
                "rollback_on_failure": False,
                "continue_on_step_failure": True
            },
            "integration": {
                "calls": [
                    {
                        "scenario": "L3-ai-platform-integration/ai-assisted-bia",
                        "when": "step:assess_impact",
                        "params": {"analysis_type": "incident_impact"}
                    },
                    {
                        "scenario": "L2-platform-services/bcm-subsystem-health",
                        "when": "step:initiate_response",
                        "params": {}
                    },
                    {
                        "scenario": "L1-plans-service/functional/create-bcm-plan",
                        "when": "step:recovery_planning",
                        "params": {"plan_type": "recovery"}
                    }
                ],
                "events": {
                    "subscribes": [
                        "system.alert.triggered",
                        "monitoring.threshold.exceeded",
                        "service.degraded"
                    ],
                    "publishes": [
                        {
                            "event": "incident.detected",
                            "when": "step:detect_incident",
                            "data": {
                                "incident_type": incident_type,
                                "severity": severity
                            }
                        },
                        {
                            "event": "incident.resolved",
                            "when": "step:complete_recovery",
                            "data": {
                                "incident_type": incident_type,
                                "resolution_time": "calculated"
                            }
                        }
                    ]
                }
            },
            "observability": {
                "metrics": [
                    "incident_detection_time_seconds",
                    "response_team_mobilization_time_seconds",
                    "incident_resolution_time_seconds",
                    "stakeholder_notification_count",
                    "recovery_success_rate"
                ],
                "traces": {
                    "trace_id_prefix": f"incident-{incident_type}",
                    "sampling_rate": 1.0
                },
                "logging": {
                    "level": "INFO",
                    "structured": True,
                    "include_incident_details": True
                }
            },
            "sla": {
                "detection_time_max_seconds": self._get_detection_sla(severity),
                "response_time_max_seconds": self._get_response_sla(severity),
                "resolution_time_max_hours": self._get_resolution_sla(severity),
                "success_rate": 0.95
            },
            "compliance": {
                "standards": ["ISO 22301:2019"],
                "requirements": [
                    {
                        "clause": "ISO 22301:8.4",
                        "description": "Incident response",
                        "validation": "Incident handled according to BCM procedures"
                    }
                ],
                "evidence": {
                    "generate": True,
                    "artifacts": [
                        "incident_report",
                        "response_timeline",
                        "communication_log",
                        "recovery_actions",
                        "post_incident_review"
                    ]
                }
            },
            "real_incident_metadata": {
                "original_incident_id": incident.get("incident_number", "unknown"),
                "original_severity": severity,
                "original_type": incident_type,
                "anonymized": True,
                "generalized": True,
                "created_from_real_incident_at": datetime.now().isoformat()
            }
        }

        return l4_scenario

    def _extract_phases_from_incident(self, incident: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract execution phases from incident workflow"""
        severity = incident.get("severity", "medium")

        phases = [
            {
                "name": "Detect Incident",
                "action": "detect_incident",
                "params": {
                    "monitoring_enabled": True,
                    "alert_threshold": "configured"
                },
                "timeout": 300,
                "required": True
            },
            {
                "name": "Assess and Classify",
                "action": "assess_and_classify_incident",
                "params": {
                    "classification_criteria": "standard",
                    "severity_assessment": True
                },
                "timeout": 600,
                "required": True
            },
            {
                "name": "Notify Stakeholders",
                "action": "notify_stakeholders",
                "params": {
                    "stakeholder_groups": ["management", "response_team", "affected_users"],
                    "notification_method": "multi_channel"
                },
                "timeout": 300,
                "required": True
            },
            {
                "name": "Activate Response Team",
                "action": "activate_response_team",
                "params": {
                    "team_size": "based_on_severity",
                    "escalation_level": self._get_escalation_level(severity)
                },
                "timeout": 900,
                "required": True
            },
            {
                "name": "Contain Incident",
                "action": "contain_incident",
                "params": {
                    "containment_strategy": "minimize_impact",
                    "isolate_affected_systems": True
                },
                "timeout": 1800,
                "required": True
            },
            {
                "name": "Execute Recovery",
                "action": "execute_recovery_procedures",
                "params": {
                    "recovery_plan": "bcm_approved",
                    "validation_required": True
                },
                "timeout": 3600,
                "required": True
            },
            {
                "name": "Verify Recovery",
                "action": "verify_system_recovery",
                "params": {
                    "verification_tests": "comprehensive",
                    "sign_off_required": True
                },
                "timeout": 1800,
                "required": True
            },
            {
                "name": "Document Incident",
                "action": "document_incident",
                "params": {
                    "report_template": "iso_22301",
                    "include_timeline": True,
                    "include_lessons_learned": True
                },
                "timeout": 1800,
                "required": True
            },
            {
                "name": "Conduct Post-Incident Review",
                "action": "conduct_post_incident_review",
                "params": {
                    "review_participants": ["response_team", "management"],
                    "improvement_recommendations": True
                },
                "timeout": 3600,
                "required": False
            }
        ]

        return phases

    def _estimate_duration(self, incident: Dict[str, Any]) -> str:
        """Estimate scenario duration based on incident data"""
        severity = incident.get("severity", "medium")

        duration_mapping = {
            "low": "2h",
            "medium": "4h",
            "high": "8h",
            "critical": "24h"
        }

        return duration_mapping.get(severity, "4h")

    def _get_detection_sla(self, severity: str) -> int:
        """Get detection SLA in seconds"""
        sla_mapping = {
            "critical": 60,      # 1 min
            "high": 300,         # 5 min
            "medium": 900,       # 15 min
            "low": 3600          # 1 hour
        }
        return sla_mapping.get(severity, 900)

    def _get_response_sla(self, severity: str) -> int:
        """Get response SLA in seconds"""
        sla_mapping = {
            "critical": 300,     # 5 min
            "high": 900,         # 15 min
            "medium": 1800,      # 30 min
            "low": 7200          # 2 hours
        }
        return sla_mapping.get(severity, 1800)

    def _get_resolution_sla(self, severity: str) -> int:
        """Get resolution SLA in hours"""
        sla_mapping = {
            "critical": 4,
            "high": 8,
            "medium": 24,
            "low": 72
        }
        return sla_mapping.get(severity, 24)

    def _get_escalation_level(self, severity: str) -> str:
        """Get escalation level"""
        mapping = {
            "critical": "executive",
            "high": "senior_management",
            "medium": "department_head",
            "low": "team_lead"
        }
        return mapping.get(severity, "team_lead")

    async def get_incident_patterns(
        self,
        incident_type: Optional[str] = None,
        severity: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get incident patterns for pattern detection

        Args:
            incident_type: Filter by type
            severity: Filter by severity
            limit: Max results

        Returns:
            List of incident patterns
        """
        try:
            params = {"limit": limit}
            if incident_type:
                params["type"] = incident_type
            if severity:
                params["severity"] = severity

            headers = {}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.odoo_url}/api/v1/bcm_incident/patterns",
                    params=params,
                    headers=headers
                )

                if response.status_code == 200:
                    return response.json().get("patterns", [])
                else:
                    logger.warning(f"Failed to get patterns: {response.status_code}")
                    return []

        except Exception as e:
            logger.error(f"Error getting incident patterns: {e}")
            return []


# Global instance
_incident_adapter: Optional[IncidentScenarioAdapter] = None


def get_incident_adapter() -> IncidentScenarioAdapter:
    """Get or create global incident adapter"""
    global _incident_adapter

    if _incident_adapter is None:
        _incident_adapter = IncidentScenarioAdapter()

    return _incident_adapter
