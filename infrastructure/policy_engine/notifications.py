"""
Governance Notification System

Sends notifications for approvals, escalations, and decisions via:
- Email (SMTP)
- Slack
- PagerDuty (for critical escalations)

Author: Security hardening initiative
Date: 2025-10-19
"""

import logging
import os
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum
import json

logger = logging.getLogger(__name__)

# Lazy import vault_client
def _get_vault_client():
    """Lazy import of vault client"""
    try:
        from infrastructure.security.vault_client import get_vault_client
        return get_vault_client()
    except Exception as e:
        logger.warning(f"Vault client not available: {e}")
        return None


class NotificationType(str, Enum):
    """Notification channel types"""
    EMAIL = "email"
    SLACK = "slack"
    PAGERDUTY = "pagerduty"
    WEBHOOK = "webhook"


class NotificationPriority(str, Enum):
    """Notification priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class NotificationService:
    """
    Service for sending governance notifications

    Supports:
    - Email via SMTP
    - Slack via webhook
    - PagerDuty for critical escalations
    - Generic webhooks

    Configuration via environment variables:
    - SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD
    - SLACK_WEBHOOK_URL
    - PAGERDUTY_API_KEY
    """

    def __init__(
        self,
        db_session_factory=None,
        smtp_config: Optional[Dict[str, Any]] = None,
        slack_webhook: Optional[str] = None,
        pagerduty_key: Optional[str] = None
    ):
        """
        Initialize notification service

        Args:
            db_session_factory: Database session factory for tracking notifications
            smtp_config: SMTP configuration dict (host, port, user, password)
            slack_webhook: Slack webhook URL
            pagerduty_key: PagerDuty API key
        """
        self.db_session_factory = db_session_factory

        # Try to get vault client
        vault = _get_vault_client()

        # SMTP configuration (try Vault first, fallback to env)
        if smtp_config:
            self.smtp_config = smtp_config
        else:
            smtp_password = None
            if vault:
                try:
                    smtp_password = vault.get_secret_with_fallback('smtp_password', 'SMTP_PASSWORD', None)
                except Exception as e:
                    logger.debug(f"Could not get smtp_password from Vault: {e}")
                    smtp_password = os.getenv('SMTP_PASSWORD')
            else:
                smtp_password = os.getenv('SMTP_PASSWORD')

            self.smtp_config = {
                'host': os.getenv('SMTP_HOST', 'localhost'),
                'port': int(os.getenv('SMTP_PORT', '587')),
                'user': os.getenv('SMTP_USER'),
                'password': smtp_password,
                'from_email': os.getenv('SMTP_FROM_EMAIL', 'noreply@ai-platform-iso.org')
            }

        # Slack configuration (try Vault first)
        if slack_webhook:
            self.slack_webhook = slack_webhook
        elif vault:
            try:
                self.slack_webhook = vault.get_secret_with_fallback('slack_webhook_url', 'SLACK_WEBHOOK_URL', None)
            except Exception as e:
                logger.debug(f"Could not get slack_webhook_url from Vault: {e}")
                self.slack_webhook = os.getenv('SLACK_WEBHOOK_URL')
        else:
            self.slack_webhook = os.getenv('SLACK_WEBHOOK_URL')

        # PagerDuty configuration (try Vault first)
        if pagerduty_key:
            self.pagerduty_key = pagerduty_key
        elif vault:
            try:
                self.pagerduty_key = vault.get_secret_with_fallback('pagerduty_api_key', 'PAGERDUTY_API_KEY', None)
            except Exception as e:
                logger.debug(f"Could not get pagerduty_api_key from Vault: {e}")
                self.pagerduty_key = os.getenv('PAGERDUTY_API_KEY')
        else:
            self.pagerduty_key = os.getenv('PAGERDUTY_API_KEY')

        # Notification statistics
        self.stats = {
            'total_sent': 0,
            'email_sent': 0,
            'slack_sent': 0,
            'pagerduty_sent': 0,
            'failed': 0
        }

    def send_approval_request(
        self,
        approval_id: str,
        service_id: str,
        action_type: str,
        action_details: Dict[str, Any],
        priority: str = "medium",
        recipients: Optional[List[str]] = None
    ) -> bool:
        """
        Send approval request notification

        Args:
            approval_id: Unique approval ID
            service_id: Service requesting approval
            action_type: Type of action (e.g., "auto_recovery", "optimization")
            action_details: Details of the action
            priority: Priority level
            recipients: List of recipient emails (defaults to APPROVAL_RECIPIENTS env var)

        Returns:
            True if notification sent successfully
        """
        recipients = recipients or os.getenv('APPROVAL_RECIPIENTS', '').split(',')
        if not recipients:
            logger.warning(f"No approval recipients configured for {approval_id}")
            return False

        subject = f"[{priority.upper()}] Approval Required: {service_id} - {action_type}"
        message = self._format_approval_message(approval_id, service_id, action_type, action_details, priority)

        # Send via email
        success = self._send_email(recipients, subject, message, approval_id)

        # Also send to Slack if priority is high or critical
        if priority in ['high', 'critical'] and self.slack_webhook:
            slack_message = f"🔔 *Approval Required*\n{message}"
            self._send_slack(slack_message, approval_id)

        return success

    def send_escalation_notification(
        self,
        escalation_id: str,
        service_id: str,
        severity: str,
        issue_type: str,
        description: str,
        context: Optional[Dict[str, Any]] = None,
        recipients: Optional[List[str]] = None
    ) -> bool:
        """
        Send escalation notification

        Args:
            escalation_id: Unique escalation ID
            service_id: Service with issue
            severity: Severity level (low, medium, high, critical)
            issue_type: Type of issue
            description: Issue description
            context: Additional context
            recipients: List of recipient emails (defaults to ESCALATION_RECIPIENTS env var)

        Returns:
            True if notification sent successfully
        """
        recipients = recipients or os.getenv('ESCALATION_RECIPIENTS', '').split(',')
        if not recipients:
            logger.warning(f"No escalation recipients configured for {escalation_id}")
            return False

        subject = f"[{severity.upper()}] Escalation: {service_id} - {issue_type}"
        message = self._format_escalation_message(escalation_id, service_id, severity, issue_type, description, context)

        # Send via email
        success = self._send_email(recipients, subject, message, escalation_id)

        # Send to Slack if severity is high or critical
        if severity in ['high', 'critical'] and self.slack_webhook:
            slack_message = f"⚠️ *Escalation - {severity.upper()}*\n{message}"
            self._send_slack(slack_message, escalation_id)

        # Page on-call if critical
        if severity == 'critical' and self.pagerduty_key:
            self._send_pagerduty(subject, description, escalation_id)

        return success

    def send_decision_notification(
        self,
        decision_id: str,
        decision_type: str,
        outcome: str,
        service_id: str,
        action_type: str,
        reason: Optional[str] = None,
        recipients: Optional[List[str]] = None
    ) -> bool:
        """
        Send decision outcome notification

        Args:
            decision_id: Unique decision ID
            decision_type: Type of decision
            outcome: Decision outcome (approved, rejected, escalated)
            service_id: Service affected
            action_type: Type of action
            reason: Reason for decision
            recipients: List of recipient emails

        Returns:
            True if notification sent successfully
        """
        if not recipients:
            # Only notify on rejections and escalations
            if outcome not in ['rejected', 'escalated']:
                return True

            recipients = os.getenv('DECISION_RECIPIENTS', '').split(',')

        if not recipients:
            return True  # No recipients configured, skip silently

        subject = f"Decision {outcome.upper()}: {service_id} - {action_type}"
        message = self._format_decision_message(decision_id, decision_type, outcome, service_id, action_type, reason)

        return self._send_email(recipients, subject, message, decision_id)

    # ============================================
    # INTERNAL METHODS
    # ============================================

    def _send_email(self, recipients: List[str], subject: str, message: str, notification_id: str) -> bool:
        """Send email via SMTP"""
        try:
            # This is a placeholder - in production, use smtplib or service like SendGrid
            logger.info(f"[EMAIL] To: {recipients}, Subject: {subject}")
            logger.debug(f"[EMAIL] Message: {message}")

            # Track in database
            if self.db_session_factory:
                self._track_notification(notification_id, NotificationType.EMAIL, recipients[0], subject, message, 'sent')

            self.stats['email_sent'] += 1
            self.stats['total_sent'] += 1
            return True

        except Exception as e:
            logger.error(f"Failed to send email for {notification_id}: {e}")
            if self.db_session_factory:
                self._track_notification(notification_id, NotificationType.EMAIL, recipients[0], subject, message, 'failed', str(e))
            self.stats['failed'] += 1
            return False

    def _send_slack(self, message: str, notification_id: str) -> bool:
        """Send message to Slack webhook"""
        try:
            # This is a placeholder - in production, use requests to POST to webhook
            logger.info(f"[SLACK] Message: {message[:100]}...")

            # Track in database
            if self.db_session_factory:
                self._track_notification(notification_id, NotificationType.SLACK, 'slack-channel', 'Slack Alert', message, 'sent')

            self.stats['slack_sent'] += 1
            self.stats['total_sent'] += 1
            return True

        except Exception as e:
            logger.error(f"Failed to send Slack message for {notification_id}: {e}")
            if self.db_session_factory:
                self._track_notification(notification_id, NotificationType.SLACK, 'slack-channel', 'Slack Alert', message, 'failed', str(e))
            self.stats['failed'] += 1
            return False

    def _send_pagerduty(self, subject: str, description: str, notification_id: str) -> bool:
        """Send PagerDuty alert"""
        try:
            # This is a placeholder - in production, use PagerDuty Events API
            logger.info(f"[PAGERDUTY] Alert: {subject}")

            # Track in database
            if self.db_session_factory:
                self._track_notification(notification_id, NotificationType.PAGERDUTY, 'on-call', subject, description, 'sent')

            self.stats['pagerduty_sent'] += 1
            self.stats['total_sent'] += 1
            return True

        except Exception as e:
            logger.error(f"Failed to send PagerDuty alert for {notification_id}: {e}")
            if self.db_session_factory:
                self._track_notification(notification_id, NotificationType.PAGERDUTY, 'on-call', subject, description, 'failed', str(e))
            self.stats['failed'] += 1
            return False

    def _track_notification(
        self,
        notification_id: str,
        notification_type: NotificationType,
        recipient: str,
        subject: str,
        message: str,
        status: str,
        failed_reason: Optional[str] = None
    ):
        """Track notification in database"""
        # Placeholder - in production, insert into governance.notifications table
        pass

    # ============================================
    # MESSAGE FORMATTERS
    # ============================================

    def _format_approval_message(self, approval_id: str, service_id: str, action_type: str, action_details: Dict, priority: str) -> str:
        """Format approval request message"""
        return f"""
Approval Request: {approval_id}

Service: {service_id}
Action: {action_type}
Priority: {priority.upper()}

Action Details:
{json.dumps(action_details, indent=2)}

Please review and approve/reject this action via the Decision Center dashboard.
        """.strip()

    def _format_escalation_message(self, escalation_id: str, service_id: str, severity: str, issue_type: str, description: str, context: Optional[Dict]) -> str:
        """Format escalation message"""
        ctx = f"\nContext:\n{json.dumps(context, indent=2)}" if context else ""
        return f"""
Escalation: {escalation_id}

Service: {service_id}
Issue Type: {issue_type}
Severity: {severity.upper()}

Description:
{description}
{ctx}

Immediate attention required. Please review and resolve via the Decision Center dashboard.
        """.strip()

    def _format_decision_message(self, decision_id: str, decision_type: str, outcome: str, service_id: str, action_type: str, reason: Optional[str]) -> str:
        """Format decision notification message"""
        reason_text = f"\nReason: {reason}" if reason else ""
        return f"""
Decision: {decision_id}

Service: {service_id}
Action: {action_type}
Decision Type: {decision_type}
Outcome: {outcome.upper()}
{reason_text}

Timestamp: {datetime.utcnow().isoformat()}
        """.strip()


# Global singleton
_notification_service: Optional[NotificationService] = None


def get_notification_service(
    db_session_factory=None,
    smtp_config: Optional[Dict[str, Any]] = None,
    slack_webhook: Optional[str] = None,
    pagerduty_key: Optional[str] = None
) -> NotificationService:
    """
    Get global notification service instance (singleton)

    Args:
        db_session_factory: Database session factory
        smtp_config: SMTP configuration
        slack_webhook: Slack webhook URL
        pagerduty_key: PagerDuty API key

    Returns:
        NotificationService instance
    """
    global _notification_service

    if _notification_service is None:
        _notification_service = NotificationService(
            db_session_factory=db_session_factory,
            smtp_config=smtp_config,
            slack_webhook=slack_webhook,
            pagerduty_key=pagerduty_key
        )

    return _notification_service
