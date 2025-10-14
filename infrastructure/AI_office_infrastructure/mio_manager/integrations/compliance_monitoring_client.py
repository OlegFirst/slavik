#!/usr/bin/env python3
"""
Compliance Monitoring Client
============================

Интеграция MIO Manager с Compliance Monitoring Service.

Compliance Monitoring отвечает за:
- ISO 22301 compliance tracking
- Alerts & Nonconformities
- Audits management
- Business metrics (RTO/RPO/MTPD)
- Service registry

MIO Manager использует для:
- Публикация compliance alerts
- Tracking nonconformities
- Service registration
- Compliance reporting
"""

import httpx
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ComplianceMonitoringClient:
    """
    Клиент для взаимодействия с Compliance Monitoring Service.

    Compliance Monitoring Service предоставляет:
    - Compliance alerts management
    - Nonconformities tracking (ISO 10.1)
    - Audits management (ISO 9.2)
    - Business metrics (RTO/RPO/MTPD)
    - Service registry
    """

    def __init__(self, base_url: str = "http://localhost:8779"):
        """
        Args:
            base_url: URL Compliance Monitoring Service
        """
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
        logger.info(f"ComplianceMonitoringClient initialized: {base_url}")

    # ========================================================================
    # COMPLIANCE ALERTS
    # ========================================================================

    async def create_alert(
        self,
        alert_type: str,
        severity: str,
        title: str,
        message: str,
        service_name: Optional[str] = None,
        iso_clause: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Создать compliance alert.

        Args:
            alert_type: security, availability, performance, compliance
            severity: low, medium, high, critical
            title: Alert title
            message: Alert message
            service_name: Service name (optional)
            iso_clause: ISO 22301 clause reference (optional)
            metadata: Additional metadata

        Returns:
            {
                'alert_id': 'ALERT-20251008-001',
                'status': 'active'
            }
        """
        try:
            response = await self.client.post(
                f"{self.base_url}/alerts",
                json={
                    'alert_type': alert_type,
                    'severity': severity,
                    'title': title,
                    'message': message,
                    'service_name': service_name,
                    'iso_clause': iso_clause,
                    'metadata': metadata or {}
                }
            )
            response.raise_for_status()
            result = response.json()

            logger.info(f"✅ Alert created: {result.get('alert_id')}")
            return result

        except Exception as e:
            logger.error(f"Failed to create alert: {e}")
            return {'error': str(e)}

    async def get_active_alerts(
        self,
        severity: Optional[str] = None,
        service_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Получить активные alerts.

        Args:
            severity: Filter by severity
            service_name: Filter by service

        Returns:
            List of active alerts
        """
        try:
            params = {}
            if severity:
                params['severity'] = severity
            if service_name:
                params['service'] = service_name

            response = await self.client.get(
                f"{self.base_url}/alerts",
                params=params
            )
            response.raise_for_status()
            alerts = response.json()

            logger.info(f"Retrieved {len(alerts)} active alerts")
            return alerts

        except Exception as e:
            logger.error(f"Failed to get alerts: {e}")
            return []

    async def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge alert."""
        try:
            response = await self.client.patch(
                f"{self.base_url}/alerts/{alert_id}",
                json={'status': 'acknowledged'}
            )
            response.raise_for_status()
            logger.info(f"✅ Alert acknowledged: {alert_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to acknowledge alert: {e}")
            return False

    async def resolve_alert(self, alert_id: str) -> bool:
        """Resolve alert."""
        try:
            response = await self.client.patch(
                f"{self.base_url}/alerts/{alert_id}",
                json={'status': 'resolved'}
            )
            response.raise_for_status()
            logger.info(f"✅ Alert resolved: {alert_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to resolve alert: {e}")
            return False

    # ========================================================================
    # NONCONFORMITIES (ISO 10.1)
    # ========================================================================

    async def create_nonconformity(
        self,
        title: str,
        description: str,
        severity: str,
        iso_clause: str,
        service_name: Optional[str] = None,
        responsible_person: Optional[str] = None,
        target_resolution_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Создать nonconformity (несоответствие ISO).

        Args:
            title: NC title
            description: NC description
            severity: minor, major, critical
            iso_clause: ISO 22301 clause (e.g., "8.3")
            service_name: Service name
            responsible_person: Who is responsible
            target_resolution_date: Target date (ISO format)

        Returns:
            {
                'nc_id': 'NC-20251008-001',
                'status': 'open'
            }
        """
        try:
            response = await self.client.post(
                f"{self.base_url}/nonconformities",
                json={
                    'title': title,
                    'description': description,
                    'severity': severity,
                    'iso_clause': iso_clause,
                    'service_name': service_name,
                    'responsible_person': responsible_person,
                    'target_resolution_date': target_resolution_date
                }
            )
            response.raise_for_status()
            result = response.json()

            logger.info(f"✅ Nonconformity created: {result.get('nc_id')}")
            return result

        except Exception as e:
            logger.error(f"Failed to create nonconformity: {e}")
            return {'error': str(e)}

    async def get_open_nonconformities(self) -> List[Dict[str, Any]]:
        """Получить открытые nonconformities."""
        try:
            response = await self.client.get(f"{self.base_url}/nonconformities")
            response.raise_for_status()
            ncs = response.json()

            logger.info(f"Retrieved {len(ncs)} open nonconformities")
            return ncs

        except Exception as e:
            logger.error(f"Failed to get nonconformities: {e}")
            return []

    # ========================================================================
    # AUDITS (ISO 9.2)
    # ========================================================================

    async def create_audit(
        self,
        audit_type: str,
        title: str,
        description: str,
        iso_clauses: List[str],
        auditor_name: Optional[str] = None,
        audit_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Создать audit.

        Args:
            audit_type: internal, external, surveillance, certification
            title: Audit title
            description: Audit description
            iso_clauses: List of ISO clauses to audit
            auditor_name: Auditor name
            audit_date: Audit date (ISO format)

        Returns:
            {
                'audit_id': 'AUDIT-20251008-001',
                'status': 'planned'
            }
        """
        try:
            response = await self.client.post(
                f"{self.base_url}/audits",
                json={
                    'audit_type': audit_type,
                    'title': title,
                    'description': description,
                    'iso_clauses': iso_clauses,
                    'auditor_name': auditor_name,
                    'audit_date': audit_date
                }
            )
            response.raise_for_status()
            result = response.json()

            logger.info(f"✅ Audit created: {result.get('audit_id')}")
            return result

        except Exception as e:
            logger.error(f"Failed to create audit: {e}")
            return {'error': str(e)}

    async def get_audits(
        self,
        audit_type: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Получить audits."""
        try:
            params = {}
            if audit_type:
                params['type'] = audit_type
            if status:
                params['status'] = status

            response = await self.client.get(
                f"{self.base_url}/audits",
                params=params
            )
            response.raise_for_status()
            audits = response.json()

            logger.info(f"Retrieved {len(audits)} audits")
            return audits

        except Exception as e:
            logger.error(f"Failed to get audits: {e}")
            return []

    # ========================================================================
    # SERVICE STATUS
    # ========================================================================

    async def get_services_status(self) -> Dict[str, Any]:
        """
        Получить статус всех мониторируемых сервисов.

        Returns:
            {
                'total_services': 11,
                'services': [
                    {
                        'name': 'workflow_intelligence',
                        'status': 'up',
                        'health_url': 'http://localhost:8050/health'
                    }
                ]
            }
        """
        try:
            response = await self.client.get(f"{self.base_url}/services/status")
            response.raise_for_status()
            status = response.json()

            logger.info(f"Retrieved status for {status.get('total_services', 0)} services")
            return status

        except Exception as e:
            logger.error(f"Failed to get services status: {e}")
            return {'error': str(e)}

    async def get_compliance_status(self) -> Dict[str, Any]:
        """
        Получить compliance статус платформы.

        Returns:
            {
                'compliance_score': 95.5,
                'active_alerts': 3,
                'open_nonconformities': 2,
                'pending_audits': 1
            }
        """
        try:
            response = await self.client.get(f"{self.base_url}/services/compliance")
            response.raise_for_status()
            compliance = response.json()

            logger.info(f"Compliance score: {compliance.get('compliance_score', 0)}")
            return compliance

        except Exception as e:
            logger.error(f"Failed to get compliance status: {e}")
            return {'error': str(e)}

    # ========================================================================
    # HEALTH CHECK
    # ========================================================================

    async def health_check(self) -> Dict[str, Any]:
        """
        Проверить доступность Compliance Monitoring Service.

        Returns:
            {
                'status': 'healthy',
                'service': 'compliance-monitoring',
                'version': '1.0.0'
            }
        """
        try:
            response = await self.client.get(
                f"{self.base_url}/health",
                timeout=5.0
            )
            response.raise_for_status()
            return response.json()

        except Exception as e:
            logger.error(f"Compliance Monitoring health check failed: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e)
            }

    async def close(self):
        """Закрыть HTTP клиент."""
        await self.client.aclose()


# Convenience instance
_compliance_client: Optional[ComplianceMonitoringClient] = None


def get_compliance_client(base_url: str = "http://localhost:8779") -> ComplianceMonitoringClient:
    """
    Получить singleton instance ComplianceMonitoringClient.

    Usage:
        client = get_compliance_client()
        result = await client.create_alert('security', 'high', 'Security breach', 'Unauthorized access')
    """
    global _compliance_client

    if _compliance_client is None:
        _compliance_client = ComplianceMonitoringClient(base_url)

    return _compliance_client
