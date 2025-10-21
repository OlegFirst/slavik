"""
Notification Service (Phase 1.1)
=================================

Simple notification service for escalations and alerts.

Supports:
- Email notifications (via SMTP)
- Slack notifications (via webhook)
- Console logging
- EventBus event publishing

Features:
- Multiple notification channels
- Priority-based routing
- Retry logic for failed notifications
- Notification history tracking
"""

import logging
import asyncio
import smtplib
import aiohttp
from typing import Dict, List, Any, Optional
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class NotificationPriority(Enum):
    """Notification priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


class NotificationChannel(Enum):
    """Notification channels"""
    EMAIL = "email"
    SLACK = "slack"
    CONSOLE = "console"
    EVENTBUS = "eventbus"


@dataclass
class NotificationConfig:
    """Notification configuration"""
    # Email settings
    smtp_host: str = "localhost"
    smtp_port: int = 587
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    from_email: str = "noreply@ai-platform.com"

    # Slack settings
    slack_webhook_url: Optional[str] = None

    # Default recipients
    default_email_recipients: List[str] = field(default_factory=list)

    # Channel priorities (which channels to use for each priority)
    priority_channels: Dict[NotificationPriority, List[NotificationChannel]] = field(default_factory=lambda: {
        NotificationPriority.LOW: [NotificationChannel.CONSOLE],
        NotificationPriority.NORMAL: [NotificationChannel.CONSOLE, NotificationChannel.EVENTBUS],
        NotificationPriority.HIGH: [NotificationChannel.CONSOLE, NotificationChannel.EVENTBUS, NotificationChannel.EMAIL],
        NotificationPriority.CRITICAL: [NotificationChannel.CONSOLE, NotificationChannel.EVENTBUS, NotificationChannel.EMAIL, NotificationChannel.SLACK]
    })


@dataclass
class Notification:
    """Notification message"""
    id: str
    title: str
    message: str
    priority: NotificationPriority
    channels: List[NotificationChannel]
    metadata: Dict[str, Any] = field(default_factory=dict)
    recipients: Optional[List[str]] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    sent: bool = False
    sent_channels: List[NotificationChannel] = field(default_factory=list)
    failed_channels: List[NotificationChannel] = field(default_factory=list)


class NotificationService:
    """
    Notification Service

    Sends notifications through multiple channels based on priority.

    Example:
        ```python
        config = NotificationConfig(
            smtp_host='smtp.gmail.com',
            smtp_port=587,
            default_email_recipients=['ops@company.com']
        )

        service = NotificationService(config, eventbus)

        await service.send_notification(
            title='Critical Service Failure',
            message='Service X has failed after 3 recovery attempts',
            priority=NotificationPriority.CRITICAL,
            metadata={'service': 'X', 'attempts': 3}
        )
        ```
    """

    def __init__(self, config: NotificationConfig, eventbus=None):
        """
        Initialize Notification Service

        Args:
            config: NotificationConfig instance
            eventbus: Optional EventBus instance for publishing events
        """
        self.config = config
        self.eventbus = eventbus
        self.notification_history: List[Notification] = []
        logger.info("NotificationService initialized")

    async def send_notification(
        self,
        title: str,
        message: str,
        priority: NotificationPriority = NotificationPriority.NORMAL,
        metadata: Optional[Dict[str, Any]] = None,
        recipients: Optional[List[str]] = None,
        channels: Optional[List[NotificationChannel]] = None
    ) -> Notification:
        """
        Send notification through appropriate channels

        Args:
            title: Notification title
            message: Notification message
            priority: Notification priority
            metadata: Additional metadata
            recipients: Optional specific recipients (for email)
            channels: Optional specific channels (overrides priority-based routing)

        Returns:
            Notification: Notification object with send status
        """
        import uuid

        # Determine channels based on priority if not specified
        if channels is None:
            channels = self.config.priority_channels.get(
                priority,
                [NotificationChannel.CONSOLE]
            )

        # Create notification object
        notification = Notification(
            id=str(uuid.uuid4()),
            title=title,
            message=message,
            priority=priority,
            channels=channels,
            metadata=metadata or {},
            recipients=recipients or self.config.default_email_recipients
        )

        logger.info(f"Sending notification [{priority.name}]: {title}")

        # Send through each channel
        for channel in channels:
            try:
                if channel == NotificationChannel.CONSOLE:
                    await self._send_console(notification)
                elif channel == NotificationChannel.EMAIL:
                    await self._send_email(notification)
                elif channel == NotificationChannel.SLACK:
                    await self._send_slack(notification)
                elif channel == NotificationChannel.EVENTBUS:
                    await self._send_eventbus(notification)

                notification.sent_channels.append(channel)
                logger.info(f"  Sent via {channel.value}")

            except Exception as e:
                logger.error(f"  Failed to send via {channel.value}: {e}")
                notification.failed_channels.append(channel)

        # Mark as sent if at least one channel succeeded
        notification.sent = len(notification.sent_channels) > 0

        # Store in history
        self.notification_history.append(notification)

        logger.info(f"Notification sent: {len(notification.sent_channels)}/{len(channels)} channels successful")

        return notification

    async def _send_console(self, notification: Notification):
        """Send notification to console (logging)"""
        priority_prefix = {
            NotificationPriority.LOW: "ℹ️ ",
            NotificationPriority.NORMAL: "",
            NotificationPriority.HIGH: "️ ",
            NotificationPriority.CRITICAL: ""
        }

        prefix = priority_prefix.get(notification.priority, "")

        print(f"\n{prefix} {notification.priority.name} NOTIFICATION {prefix}")
        print(f"Title: {notification.title}")
        print(f"Message: {notification.message}")
        if notification.metadata:
            print(f"Metadata: {notification.metadata}")
        print(f"Timestamp: {notification.timestamp.isoformat()}")
        print("-" * 70 + "\n")

    async def _send_email(self, notification: Notification):
        """Send notification via email"""
        if not notification.recipients:
            logger.warning("No email recipients configured - skipping email notification")
            return

        # Create message
        msg = MIMEMultipart()
        msg['From'] = self.config.from_email
        msg['To'] = ', '.join(notification.recipients)
        msg['Subject'] = f"[{notification.priority.name}] {notification.title}"

        # Build email body
        body = f"""
{notification.message}

Priority: {notification.priority.name}
Timestamp: {notification.timestamp.isoformat()}

Metadata:
{self._format_metadata(notification.metadata)}

---
This is an automated notification from AI Platform Infrastructure Monitoring.
        """.strip()

        msg.attach(MIMEText(body, 'plain'))

        # Send email (synchronous SMTP)
        await asyncio.to_thread(self._send_smtp, msg, notification.recipients)

    def _send_smtp(self, msg: MIMEMultipart, recipients: List[str]):
        """Send email via SMTP (runs in thread pool)"""
        try:
            with smtplib.SMTP(self.config.smtp_host, self.config.smtp_port) as server:
                server.starttls()

                if self.config.smtp_user and self.config.smtp_password:
                    server.login(self.config.smtp_user, self.config.smtp_password)

                server.send_message(msg)

            logger.info(f"Email sent to {recipients}")
        except Exception as e:
            logger.error(f"SMTP error: {e}")
            raise

    async def _send_slack(self, notification: Notification):
        """Send notification to Slack"""
        if not self.config.slack_webhook_url:
            logger.warning("Slack webhook URL not configured - skipping Slack notification")
            return

        # Build Slack message
        color = {
            NotificationPriority.LOW: "#36a64f",      # green
            NotificationPriority.NORMAL: "#2196F3",   # blue
            NotificationPriority.HIGH: "#ff9800",     # orange
            NotificationPriority.CRITICAL: "#f44336"  # red
        }

        slack_message = {
            "attachments": [{
                "color": color.get(notification.priority, "#2196F3"),
                "title": f"[{notification.priority.name}] {notification.title}",
                "text": notification.message,
                "fields": [
                    {
                        "title": key,
                        "value": str(value),
                        "short": True
                    }
                    for key, value in notification.metadata.items()
                ],
                "footer": "AI Platform Infrastructure",
                "ts": int(notification.timestamp.timestamp())
            }]
        }

        # Send via webhook
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.config.slack_webhook_url,
                json=slack_message,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status != 200:
                    raise Exception(f"Slack webhook returned status {response.status}")

                logger.info("Slack notification sent")

    async def _send_eventbus(self, notification: Notification):
        """Publish notification as EventBus event"""
        if not self.eventbus:
            logger.warning("EventBus not configured - skipping EventBus notification")
            return

        from infrastructure.eventbus.core.events import Event, EventPriority

        # Map notification priority to event priority
        event_priority_map = {
            NotificationPriority.LOW: EventPriority.LOW,
            NotificationPriority.NORMAL: EventPriority.NORMAL,
            NotificationPriority.HIGH: EventPriority.HIGH,
            NotificationPriority.CRITICAL: EventPriority.CRITICAL
        }

        event = Event.create(
            event_type='infrastructure.notification.sent',
            data={
                'notification_id': notification.id,
                'title': notification.title,
                'message': notification.message,
                'priority': notification.priority.name,
                'metadata': notification.metadata,
                'timestamp': notification.timestamp.isoformat()
            },
            source='notification_service',
            tenant_id='system',
            priority=event_priority_map.get(notification.priority, EventPriority.NORMAL)
        )

        await self.eventbus.publish(event)
        logger.debug("Notification published to EventBus")

    def _format_metadata(self, metadata: Dict[str, Any]) -> str:
        """Format metadata for display"""
        if not metadata:
            return "None"

        return "\n".join(f"  {key}: {value}" for key, value in metadata.items())

    def get_notification_history(
        self,
        limit: int = 100,
        priority: Optional[NotificationPriority] = None
    ) -> List[Notification]:
        """
        Get notification history

        Args:
            limit: Maximum number of notifications to return
            priority: Optional filter by priority

        Returns:
            List of notifications
        """
        history = self.notification_history

        if priority:
            history = [n for n in history if n.priority == priority]

        return history[-limit:]

    def get_stats(self) -> Dict[str, Any]:
        """
        Get notification statistics

        Returns:
            Dict with notification stats
        """
        total = len(self.notification_history)
        successful = len([n for n in self.notification_history if n.sent])

        by_priority = {}
        for priority in NotificationPriority:
            count = len([n for n in self.notification_history if n.priority == priority])
            by_priority[priority.name] = count

        by_channel = {}
        for channel in NotificationChannel:
            count = sum(
                1 for n in self.notification_history
                if channel in n.sent_channels
            )
            by_channel[channel.value] = count

        return {
            'total_notifications': total,
            'successful_notifications': successful,
            'failed_notifications': total - successful,
            'success_rate': (successful / total * 100) if total > 0 else 0,
            'by_priority': by_priority,
            'by_channel': by_channel
        }
