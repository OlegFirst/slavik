#!/usr/bin/env python3
"""
Notification Service Client
Интеграция MIO Manager с Notification Service для системных alerts
"""

import httpx
from typing import Dict, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class NotificationClient:
    """
    Клиент для отправки уведомлений через Notification Service

    Типы уведомлений:
    - CRITICAL security issues
    - HIGH priority incidents
    - Service down alerts
    - Workflow status updates
    - Task delegation notifications
    """

    def __init__(self, notification_service_url: str = "http://localhost:8003"):
        self.base_url = notification_service_url
        self.client = httpx.AsyncClient(timeout=30.0)

    # ========================================================================
    # SECURITY ALERTS
    # ========================================================================

    async def send_security_alert(
        self,
        severity: str,
        issue_count: int,
        high_issues: List[Dict],
        workflow_id: Optional[str] = None,
        recipients: Optional[List[str]] = None
    ) -> Dict:
        """
        Отправить security alert

        Args:
            severity: critical | high | medium
            issue_count: Количество HIGH security issues
            high_issues: Список проблем
            workflow_id: ID workflow для отслеживания
            recipients: Email/User IDs для уведомления

        Returns:
            {
                'notification_id': '...',
                'status': 'sent',
                'channels': ['email', 'slack', 'webhook']
            }
        """
        try:
            # Определить каналы по severity
            channels = self._get_channels_by_severity(severity)

            # Построить сообщение
            message = self._build_security_message(severity, issue_count, high_issues)

            # Отправить через Notification Service
            response = await self.client.post(
                f"{self.base_url}/api/notifications/send",
                json={
                    "type": "security_alert",
                    "severity": severity,
                    "title": f" Security Alert: {issue_count} {severity.upper()} issues detected",
                    "message": message,
                    "channels": channels,
                    "recipients": recipients or self._get_default_security_recipients(),
                    "metadata": {
                        "workflow_id": workflow_id,
                        "issue_count": issue_count,
                        "source": "mio_manager",
                        "timestamp": datetime.utcnow().isoformat()
                    },
                    "priority": self._map_severity_to_priority(severity),
                    "actions": [
                        {
                            "label": "View Details",
                            "url": f"/workflows/{workflow_id}" if workflow_id else "/security"
                        },
                        {
                            "label": "Acknowledge",
                            "action": "acknowledge",
                            "workflow_id": workflow_id
                        }
                    ]
                }
            )
            response.raise_for_status()
            result = response.json()

            logger.info(
                f" Security alert sent: {severity} | "
                f"notification_id={result.get('notification_id')}"
            )
            return result

        except Exception as e:
            logger.error(f" Failed to send security alert: {e}")
            return {
                "notification_id": None,
                "status": "failed",
                "error": str(e)
            }

    # ========================================================================
    # SERVICE DOWN ALERTS
    # ========================================================================

    async def send_service_down_alert(
        self,
        service_name: str,
        health_check_result: Dict,
        workflow_id: Optional[str] = None
    ) -> Dict:
        """
        Отправить service down alert

        CRITICAL priority - немедленная доставка
        """
        try:
            message = f"""
 **SERVICE DOWN ALERT**

**Service:** {service_name}
**Status:** DOWN
**Detected:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}

**Health Check Result:**
```
{health_check_result}
```

**Workflow ID:** {workflow_id or 'N/A'}

**Automated Actions:**
- Root cause analysis initiated
- Restart attempt in progress
- Circuit breaker enabled

**Next Steps:**
1. Check service logs
2. Verify dependencies
3. Manual intervention may be required
"""

            response = await self.client.post(
                f"{self.base_url}/api/notifications/send",
                json={
                    "type": "service_down",
                    "severity": "critical",
                    "title": f" CRITICAL: {service_name} is DOWN",
                    "message": message,
                    "channels": ["email", "slack", "webhook", "sms"],  # Все каналы
                    "recipients": self._get_default_incident_recipients(),
                    "metadata": {
                        "service_name": service_name,
                        "workflow_id": workflow_id,
                        "source": "mio_manager",
                        "alert_type": "service_down"
                    },
                    "priority": "critical",
                    "require_acknowledgement": True,
                    "actions": [
                        {
                            "label": "View Workflow",
                            "url": f"/workflows/{workflow_id}"
                        },
                        {
                            "label": "View Service Logs",
                            "url": f"/services/{service_name}/logs"
                        },
                        {
                            "label": "Acknowledge",
                            "action": "acknowledge"
                        }
                    ]
                }
            )
            response.raise_for_status()
            result = response.json()

            logger.warning(f" Service down alert sent for {service_name}")
            return result

        except Exception as e:
            logger.error(f" Failed to send service down alert: {e}")
            return {"status": "failed", "error": str(e)}

    # ========================================================================
    # WORKFLOW NOTIFICATIONS
    # ========================================================================

    async def send_workflow_update(
        self,
        workflow_id: str,
        workflow_type: str,
        current_state: str,
        previous_state: Optional[str] = None,
        action_data: Optional[Dict] = None
    ) -> Dict:
        """
        Отправить обновление по workflow

        Для информирования о progress
        """
        try:
            message = f"""
 **Workflow Update**

**Workflow ID:** {workflow_id}
**Type:** {workflow_type}
**State:** {previous_state or '?'} → {current_state}

{self._format_action_data(action_data) if action_data else ''}
"""

            response = await self.client.post(
                f"{self.base_url}/api/notifications/send",
                json={
                    "type": "workflow_update",
                    "severity": "info",
                    "title": f"Workflow {workflow_type}: {current_state}",
                    "message": message,
                    "channels": ["webhook"],  # Только webhook для workflow updates
                    "metadata": {
                        "workflow_id": workflow_id,
                        "workflow_type": workflow_type,
                        "current_state": current_state,
                        "previous_state": previous_state
                    },
                    "priority": "low"
                }
            )
            response.raise_for_status()
            return response.json()

        except Exception as e:
            logger.error(f" Failed to send workflow update: {e}")
            return {"status": "failed", "error": str(e)}

    # ========================================================================
    # TASK DELEGATION NOTIFICATIONS
    # ========================================================================

    async def send_task_delegation_notification(
        self,
        task_id: str,
        task_type: str,
        priority: str,
        assigned_to: Optional[str] = None,
        ai_recommendations: Optional[List[Dict]] = None
    ) -> Dict:
        """
        Уведомление о делегировании задачи

        Для информирования AI Orchestrator или команды
        """
        try:
            message = f"""
 **New Task Delegated**

**Task ID:** {task_id}
**Type:** {task_type}
**Priority:** {priority.upper()}
**Assigned To:** {assigned_to or 'AI Orchestrator'}

{self._format_ai_recommendations(ai_recommendations) if ai_recommendations else ''}
"""

            channels = ["webhook", "slack"] if priority in ["high", "critical"] else ["webhook"]

            response = await self.client.post(
                f"{self.base_url}/api/notifications/send",
                json={
                    "type": "task_delegation",
                    "severity": "info",
                    "title": f"Task Delegated: {task_type}",
                    "message": message,
                    "channels": channels,
                    "metadata": {
                        "task_id": task_id,
                        "task_type": task_type,
                        "priority": priority,
                        "assigned_to": assigned_to
                    },
                    "priority": priority,
                    "actions": [
                        {
                            "label": "View Task",
                            "url": f"/tasks/{task_id}"
                        },
                        {
                            "label": "Accept",
                            "action": "accept_task",
                            "task_id": task_id
                        }
                    ]
                }
            )
            response.raise_for_status()
            return response.json()

        except Exception as e:
            logger.error(f" Failed to send task delegation notification: {e}")
            return {"status": "failed", "error": str(e)}

    # ========================================================================
    # ISSUE RESOLUTION NOTIFICATIONS
    # ========================================================================

    async def send_issue_resolved_notification(
        self,
        issue_id: str,
        issue_type: str,
        severity: str,
        resolution_notes: Optional[str] = None,
        resolved_by_action_id: Optional[str] = None
    ) -> Dict:
        """
        Уведомление об успешном исправлении проблемы

        Positive feedback для команды
        """
        try:
            message = f"""
 **Issue Resolved**

**Issue ID:** {issue_id}
**Type:** {issue_type}
**Severity:** {severity}
**Resolved By:** {resolved_by_action_id or 'Automated'}

{resolution_notes or 'Automated resolution successful'}
"""

            response = await self.client.post(
                f"{self.base_url}/api/notifications/send",
                json={
                    "type": "issue_resolved",
                    "severity": "success",
                    "title": f" Issue Resolved: {issue_type}",
                    "message": message,
                    "channels": ["slack", "webhook"],
                    "metadata": {
                        "issue_id": issue_id,
                        "issue_type": issue_type,
                        "severity": severity,
                        "resolved_by_action_id": resolved_by_action_id
                    },
                    "priority": "low"
                }
            )
            response.raise_for_status()
            return response.json()

        except Exception as e:
            logger.error(f" Failed to send issue resolved notification: {e}")
            return {"status": "failed", "error": str(e)}

    # ========================================================================
    # METRICS & HEALTH
    # ========================================================================

    async def send_daily_summary(
        self,
        summary_data: Dict
    ) -> Dict:
        """
        Ежедневная сводка по MIO Manager

        Отправляется в конце дня
        """
        try:
            message = f"""
 **Daily MIO Manager Summary**

**Date:** {datetime.utcnow().strftime('%Y-%m-%d')}

**Service Coverage:** {summary_data.get('service_coverage', 0)}%
**Security Scans:** {summary_data.get('security_scans', 0)}
**High Issues Found:** {summary_data.get('high_issues', 0)}
**Issues Resolved:** {summary_data.get('issues_resolved', 0)}
**Actions Executed:** {summary_data.get('actions_executed', 0)}
**Tasks Delegated:** {summary_data.get('tasks_delegated', 0)}

**Success Rate:** {summary_data.get('success_rate', 0)}%
"""

            response = await self.client.post(
                f"{self.base_url}/api/notifications/send",
                json={
                    "type": "daily_summary",
                    "severity": "info",
                    "title": " MIO Manager Daily Summary",
                    "message": message,
                    "channels": ["email", "slack"],
                    "recipients": self._get_default_summary_recipients(),
                    "metadata": summary_data,
                    "priority": "low"
                }
            )
            response.raise_for_status()
            return response.json()

        except Exception as e:
            logger.error(f" Failed to send daily summary: {e}")
            return {"status": "failed", "error": str(e)}

    # ========================================================================
    # HELPERS
    # ========================================================================

    def _get_channels_by_severity(self, severity: str) -> List[str]:
        """Определить каналы доставки по severity"""
        if severity == "critical":
            return ["email", "slack", "webhook", "sms"]
        elif severity == "high":
            return ["email", "slack", "webhook"]
        elif severity == "medium":
            return ["slack", "webhook"]
        else:
            return ["webhook"]

    def _map_severity_to_priority(self, severity: str) -> str:
        """Map severity to notification priority"""
        mapping = {
            "critical": "critical",
            "high": "high",
            "medium": "medium",
            "low": "low"
        }
        return mapping.get(severity, "medium")

    def _build_security_message(
        self,
        severity: str,
        issue_count: int,
        high_issues: List[Dict]
    ) -> str:
        """Построить сообщение security alert"""
        message = f"""
 **Security Alert - {severity.upper()}**

**Issues Found:** {issue_count} HIGH severity vulnerabilities

**Top Issues:**
"""
        for i, issue in enumerate(high_issues[:5], 1):
            message += f"""
{i}. **{issue.get('issue_text', 'Unknown')}**
   - File: `{issue.get('filename', 'N/A')}`
   - Line: {issue.get('line_number', 'N/A')}
"""

        message += f"""

**Automated Actions:**
- Workflow created for tracking
- AI recommendations generated
- Task delegated to Orchestrator

**Required Actions:**
- Review security scan results
- Apply recommended fixes
- Verify after resolution
"""
        return message

    def _format_action_data(self, action_data: Dict) -> str:
        """Format action data для сообщения"""
        if not action_data:
            return ""

        formatted = "\n**Action Data:**\n"
        for key, value in action_data.items():
            formatted += f"- {key}: {value}\n"
        return formatted

    def _format_ai_recommendations(self, recommendations: List[Dict]) -> str:
        """Format AI recommendations"""
        if not recommendations:
            return ""

        formatted = "\n**AI Recommendations:**\n"
        for i, rec in enumerate(recommendations[:3], 1):
            formatted += f"{i}. {rec.get('recommendation', 'N/A')}\n"
        return formatted

    def _get_default_security_recipients(self) -> List[str]:
        """Default recipients для security alerts"""
        # TODO: Load from config
        return ["security-team@company.com", "devops@company.com"]

    def _get_default_incident_recipients(self) -> List[str]:
        """Default recipients для incidents"""
        # TODO: Load from config
        return ["incident-team@company.com", "on-call@company.com"]

    def _get_default_summary_recipients(self) -> List[str]:
        """Default recipients для daily summary"""
        # TODO: Load from config
        return ["team@company.com"]

    async def close(self):
        """Закрыть HTTP клиент"""
        await self.client.aclose()
