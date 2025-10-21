# -*- coding: utf-8 -*-
"""
External Integrations for BCM Notification Service
Teams, Slack, SMS, PagerDuty integrations
"""

import os
import asyncio
import httpx
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class NotificationRequest(BaseModel):
    title: str
    message: str
    severity: str = "info"  # info, warning, critical, emergency
    recipients: List[str] = []
    channels: List[str] = ["email"]  # email, teams, slack, sms, pagerduty
    metadata: Optional[Dict[str, Any]] = None

class ExternalNotificationService:
    """Service for external notifications (Teams, Slack, SMS, etc.)"""

    def __init__(self):
        # Teams
        self.teams_webhook = os.getenv("TEAMS_WEBHOOK_URL")
        self.teams_enabled = os.getenv("TEAMS_ENABLED", "false").lower() == "true"

        # Slack
        self.slack_webhook = os.getenv("SLACK_WEBHOOK_URL")
        self.slack_bot_token = os.getenv("SLACK_BOT_TOKEN")
        self.slack_enabled = os.getenv("SLACK_ENABLED", "false").lower() == "true"

        # SMS (Twilio)
        self.twilio_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.twilio_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.twilio_phone = os.getenv("TWILIO_PHONE_NUMBER")
        self.sms_enabled = os.getenv("SMS_ENABLED", "false").lower() == "true"

        # PagerDuty
        self.pagerduty_key = os.getenv("PAGERDUTY_INTEGRATION_KEY")
        self.pagerduty_enabled = os.getenv("PAGERDUTY_ENABLED", "false").lower() == "true"

    async def send_notification(self, request: NotificationRequest) -> Dict[str, Any]:
        """Send notification through requested channels"""

        results = {"status": "success", "channels": {}}

        for channel in request.channels:
            try:
                if channel == "teams" and self.teams_enabled:
                    result = await self._send_teams_notification(request)
                    results["channels"]["teams"] = result

                elif channel == "slack" and self.slack_enabled:
                    result = await self._send_slack_notification(request)
                    results["channels"]["slack"] = result

                elif channel == "sms" and self.sms_enabled:
                    result = await self._send_sms_notification(request)
                    results["channels"]["sms"] = result

                elif channel == "pagerduty" and self.pagerduty_enabled and request.severity in ["critical", "emergency"]:
                    result = await self._send_pagerduty_alert(request)
                    results["channels"]["pagerduty"] = result

                else:
                    results["channels"][channel] = {"status": "skipped", "reason": "disabled or not configured"}

            except Exception as e:
                logger.error(f"Failed to send {channel} notification: {e}")
                results["channels"][channel] = {"status": "error", "error": str(e)}

        return results

    async def _send_teams_notification(self, request: NotificationRequest) -> Dict[str, str]:
        """Send Microsoft Teams notification"""

        if not self.teams_webhook:
            return {"status": "error", "error": "Teams webhook not configured"}

        # Teams Adaptive Card format
        severity_colors = {
            "info": "Good",
            "warning": "Warning",
            "critical": "Attention",
            "emergency": "Attention"
        }

        card_data = {
            "@type": "MessageCard",
            "@context": "https://schema.org/extensions",
            "themeColor": severity_colors.get(request.severity, "Good"),
            "summary": request.title,
            "sections": [{
                "activityTitle": f" BCM Alert - {request.severity.upper()}",
                "activitySubtitle": request.title,
                "activityImage": "https://adaptivecards.io/content/cats/1.png",
                "text": request.message,
                "facts": [
                    {"name": "Severity", "value": request.severity},
                    {"name": "Time", "value": datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
                    {"name": "Source", "value": "BCM Platform"}
                ]
            }],
            "potentialAction": [{
                "@type": "OpenUri",
                "name": "View in BCM Platform",
                "targets": [{"os": "default", "uri": "http://localhost:8069"}]
            }]
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.teams_webhook,
                json=card_data,
                headers={"Content-Type": "application/json"}
            )

            if response.status_code == 200:
                return {"status": "sent", "response": response.text}
            else:
                return {"status": "error", "error": f"HTTP {response.status_code}: {response.text}"}

    async def _send_slack_notification(self, request: NotificationRequest) -> Dict[str, str]:
        """Send Slack notification"""

        if not self.slack_webhook:
            return {"status": "error", "error": "Slack webhook not configured"}

        # Slack Block Kit format
        severity_colors = {
            "info": "#36a64f",
            "warning": "#ff9500",
            "critical": "#ff0000",
            "emergency": "#8b0000"
        }

        severity_emojis = {
            "info": "ℹ️",
            "warning": "️",
            "critical": "",
            "emergency": "🆘"
        }

        slack_data = {
            "channel": os.getenv("SLACK_CHANNEL_ALERTS", "#bcm-alerts"),
            "username": "BCM Platform",
            "icon_emoji": ":warning:",
            "attachments": [{
                "color": severity_colors.get(request.severity, "#36a64f"),
                "blocks": [{
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"{severity_emojis.get(request.severity, '')} BCM Alert - {request.severity.upper()}"
                    }
                }, {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*{request.title}*\n{request.message}"
                    }
                }, {
                    "type": "section",
                    "fields": [
                        {"type": "mrkdwn", "text": f"*Severity:*\n{request.severity}"},
                        {"type": "mrkdwn", "text": f"*Time:*\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"}
                    ]
                }, {
                    "type": "actions",
                    "elements": [{
                        "type": "button",
                        "text": {"type": "plain_text", "text": "View in BCM Platform"},
                        "url": "http://localhost:8069",
                        "style": "primary"
                    }]
                }]
            }]
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.slack_webhook,
                json=slack_data,
                headers={"Content-Type": "application/json"}
            )

            if response.status_code == 200:
                return {"status": "sent", "response": "ok"}
            else:
                return {"status": "error", "error": f"HTTP {response.status_code}: {response.text}"}

    async def _send_sms_notification(self, request: NotificationRequest) -> Dict[str, str]:
        """Send SMS notification via Twilio"""

        if not all([self.twilio_sid, self.twilio_token, self.twilio_phone]):
            return {"status": "error", "error": "Twilio not configured"}

        # Simplified SMS message
        sms_text = f"BCM Alert ({request.severity.upper()}): {request.title}\n{request.message[:140]}..."

        twilio_data = {
            "From": self.twilio_phone,
            "Body": sms_text
        }

        sent_count = 0
        for recipient in request.recipients:
            if recipient.startswith('+') or recipient.startswith('1'):  # Phone numbers
                try:
                    twilio_data["To"] = recipient

                    async with httpx.AsyncClient() as client:
                        response = await client.post(
                            f"https://api.twilio.com/2010-04-01/Accounts/{self.twilio_sid}/Messages.json",
                            data=twilio_data,
                            auth=(self.twilio_sid, self.twilio_token)
                        )

                        if response.status_code == 201:
                            sent_count += 1

                except Exception as e:
                    logger.error(f"Failed to send SMS to {recipient}: {e}")

        return {"status": "sent", "recipients": sent_count}

    async def _send_pagerduty_alert(self, request: NotificationRequest) -> Dict[str, str]:
        """Send PagerDuty alert for critical/emergency incidents"""

        if not self.pagerduty_key:
            return {"status": "error", "error": "PagerDuty not configured"}

        event_data = {
            "routing_key": self.pagerduty_key,
            "event_action": "trigger",
            "payload": {
                "summary": request.title,
                "source": "BCM Platform",
                "severity": request.severity,
                "component": "BCM System",
                "group": "BCM Incidents",
                "class": "BCM Alert",
                "custom_details": {
                    "message": request.message,
                    "timestamp": datetime.now().isoformat(),
                    "metadata": request.metadata or {}
                }
            }
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://events.pagerduty.com/v2/enqueue",
                json=event_data,
                headers={"Content-Type": "application/json"}
            )

            if response.status_code == 202:
                result = response.json()
                return {"status": "sent", "dedup_key": result.get("dedup_key")}
            else:
                return {"status": "error", "error": f"HTTP {response.status_code}: {response.text}"}

# Global instance
external_notifications = ExternalNotificationService()

# BCM-specific notification helpers
async def send_exercise_notification(exercise_title: str, exercise_type: str, participants: List[str]):
    """Send exercise start notification"""

    request = NotificationRequest(
        title=f"BCM Exercise Started: {exercise_title}",
        message=f"Exercise '{exercise_title}' ({exercise_type}) has begun with {len(participants)} participants.",
        severity="info",
        channels=["teams", "slack"],
        recipients=participants,
        metadata={"exercise_type": exercise_type, "participant_count": len(participants)}
    )

    return await external_notifications.send_notification(request)

async def send_incident_alert(incident_title: str, severity: str, affected_systems: List[str]):
    """Send incident alert notification"""

    channels = ["teams", "slack", "email"]
    if severity in ["critical", "emergency"]:
        channels.extend(["sms", "pagerduty"])

    request = NotificationRequest(
        title=f"BCM Incident: {incident_title}",
        message=f"Incident affecting: {', '.join(affected_systems)}. Immediate attention required.",
        severity=severity,
        channels=channels,
        metadata={"affected_systems": affected_systems}
    )

    return await external_notifications.send_notification(request)

async def send_system_health_alert(system_name: str, status: str, details: str):
    """Send system health notification"""

    severity = "critical" if status == "down" else "warning"

    request = NotificationRequest(
        title=f"System Health Alert: {system_name}",
        message=f"System {system_name} is {status}. {details}",
        severity=severity,
        channels=["teams", "slack"],
        metadata={"system": system_name, "status": status}
    )

    return await external_notifications.send_notification(request)