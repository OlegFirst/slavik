"""
ISO 22301 Compliance API - Notification Integration

Автоматические уведомления для:
- Критичные алерты
- Nonconformities
- Failed audits
- Metric breaches
"""

import os
import logging
import httpx
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class NotificationIntegration:
    """Integration with Notification Service"""

    def __init__(self, notification_service_url: str = None):
        self.base_url = notification_service_url or os.getenv(
            "NOTIFICATION_SERVICE_URL",
            "http://localhost:8035"
        )
        self.enabled = os.getenv("NOTIFICATIONS_ENABLED", "true").lower() == "true"

        if not self.enabled:
            logger.info("📢 Notifications disabled by configuration")

    async def send_alert_notification(
        self,
        alert_id: str,
        alert_type: str,
        severity: str,
        service_name: str,
        title: str,
        message: str
    ) -> bool:
        """Send notification for compliance alert"""

        if not self.enabled:
            return False

        try:
            # Determine notification channels based on severity
            channels = ["email"]

            if severity in ["high", "critical"]:
                channels.extend(["teams", "slack"])

            if severity == "critical":
                channels.append("sms")  # SMS for critical alerts only

            # Send webhook notification
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{self.base_url}/webhook/send",
                    json={
                        "url": f"{self.base_url}/internal/alert-webhook",
                        "method": "POST",
                        "payload": {
                            "alert_id": alert_id,
                            "alert_type": alert_type,
                            "severity": severity,
                            "service_name": service_name,
                            "title": title,
                            "message": message,
                            "timestamp": datetime.now().isoformat()
                        }
                    }
                )

                if response.status_code == 200:
                    logger.info(f"✅ Alert notification sent: {alert_id}")
                    return True
                else:
                    logger.error(f"❌ Failed to send alert notification: {response.text}")
                    return False

        except Exception as e:
            logger.error(f"❌ Error sending alert notification: {e}")
            return False


    async def send_nonconformity_notification(
        self,
        nc_id: str,
        title: str,
        severity: str,
        iso_clause: str,
        responsible_person: Optional[str] = None
    ) -> bool:
        """Send notification for new nonconformity"""

        if not self.enabled:
            return False

        try:
            recipients = []
            if responsible_person:
                recipients.append(responsible_person)

            # Add ISO compliance officers
            compliance_emails = os.getenv("COMPLIANCE_OFFICERS_EMAILS", "").split(",")
            recipients.extend([e.strip() for e in compliance_emails if e.strip()])

            if not recipients:
                logger.warning("No recipients configured for nonconformity notification")
                return False

            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{self.base_url}/email/send",
                    json={
                        "to": recipients,
                        "subject": f"🚨 New Nonconformity: {nc_id} - {title}",
                        "body": f"""
New ISO 22301 Nonconformity Detected

Nonconformity ID: {nc_id}
Title: {title}
Severity: {severity}
ISO Clause: {iso_clause}
Responsible Person: {responsible_person or 'Not assigned'}

Please review and take corrective action.

View details: http://localhost:8045/nonconformities/{nc_id}
                        """,
                        "html_body": f"""
<html>
<body>
<h2>🚨 New ISO 22301 Nonconformity Detected</h2>

<table>
<tr><td><strong>Nonconformity ID:</strong></td><td>{nc_id}</td></tr>
<tr><td><strong>Title:</strong></td><td>{title}</td></tr>
<tr><td><strong>Severity:</strong></td><td><span style="color: red;">{severity.upper()}</span></td></tr>
<tr><td><strong>ISO Clause:</strong></td><td>{iso_clause}</td></tr>
<tr><td><strong>Responsible Person:</strong></td><td>{responsible_person or 'Not assigned'}</td></tr>
</table>

<p>Please review and take corrective action immediately.</p>

<a href="http://localhost:8045/nonconformities/{nc_id}" style="padding: 10px 20px; background-color: #4CAF50; color: white; text-decoration: none; border-radius: 4px;">View Details</a>
</body>
</html>
                        """
                    }
                )

                if response.status_code == 200:
                    logger.info(f"✅ Nonconformity notification sent: {nc_id}")
                    return True
                else:
                    logger.error(f"❌ Failed to send NC notification: {response.text}")
                    return False

        except Exception as e:
            logger.error(f"❌ Error sending NC notification: {e}")
            return False


    async def send_audit_notification(
        self,
        audit_id: str,
        audit_type: str,
        title: str,
        status: str,
        findings_count: int
    ) -> bool:
        """Send notification for audit status update"""

        if not self.enabled:
            return False

        try:
            audit_emails = os.getenv("AUDIT_TEAM_EMAILS", "").split(",")
            recipients = [e.strip() for e in audit_emails if e.strip()]

            if not recipients:
                logger.warning("No recipients configured for audit notification")
                return False

            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{self.base_url}/email/send",
                    json={
                        "to": recipients,
                        "subject": f"📋 ISO 22301 Audit Update: {audit_id} - {status}",
                        "body": f"""
ISO 22301 Audit Status Update

Audit ID: {audit_id}
Type: {audit_type}
Title: {title}
Status: {status}
Findings: {findings_count}

View details: http://localhost:8045/audits/{audit_id}
                        """
                    }
                )

                if response.status_code == 200:
                    logger.info(f"✅ Audit notification sent: {audit_id}")
                    return True
                else:
                    logger.error(f"❌ Failed to send audit notification: {response.text}")
                    return False

        except Exception as e:
            logger.error(f"❌ Error sending audit notification: {e}")
            return False


    async def send_metric_breach_notification(
        self,
        service_name: str,
        metric_type: str,
        target_value: float,
        actual_value: float,
        unit: str
    ) -> bool:
        """Send notification for metric breach (RTO/RPO/MTPD)"""

        if not self.enabled:
            return False

        try:
            breach_percentage = ((actual_value - target_value) / target_value) * 100

            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{self.base_url}/webhook/send",
                    json={
                        "url": f"{self.base_url}/internal/metric-breach",
                        "method": "POST",
                        "payload": {
                            "service_name": service_name,
                            "metric_type": metric_type,
                            "target_value": target_value,
                            "actual_value": actual_value,
                            "unit": unit,
                            "breach_percentage": breach_percentage,
                            "severity": "critical" if breach_percentage > 50 else "high",
                            "timestamp": datetime.now().isoformat()
                        }
                    }
                )

                if response.status_code == 200:
                    logger.info(f"✅ Metric breach notification sent: {service_name}/{metric_type}")
                    return True
                else:
                    logger.error(f"❌ Failed to send metric breach notification: {response.text}")
                    return False

        except Exception as e:
            logger.error(f"❌ Error sending metric breach notification: {e}")
            return False


    async def send_service_health_notification(
        self,
        service_name: str,
        status: str,
        previous_status: str,
        last_health_check: datetime
    ) -> bool:
        """Send notification for service health change"""

        if not self.enabled:
            return False

        # Only notify on degradation or failure
        if status in ["up", "unknown"]:
            return False

        try:
            severity = "critical" if status == "down" else "high"

            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{self.base_url}/webhook/send",
                    json={
                        "url": f"{self.base_url}/internal/service-health",
                        "method": "POST",
                        "payload": {
                            "service_name": service_name,
                            "status": status,
                            "previous_status": previous_status,
                            "last_health_check": last_health_check.isoformat(),
                            "severity": severity,
                            "timestamp": datetime.now().isoformat()
                        }
                    }
                )

                if response.status_code == 200:
                    logger.info(f"✅ Service health notification sent: {service_name}")
                    return True
                else:
                    logger.error(f"❌ Failed to send service health notification: {response.text}")
                    return False

        except Exception as e:
            logger.error(f"❌ Error sending service health notification: {e}")
            return False


# Global instance
notification_integration = NotificationIntegration()
