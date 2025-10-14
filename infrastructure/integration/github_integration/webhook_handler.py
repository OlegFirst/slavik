"""
GitHub Webhook Handler
======================

Processes all GitHub webhook events and publishes to EventBus.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from models import (
    WebhookEvent,
    PRWebhookPayload,
    IssueWebhookPayload,
    PushWebhookPayload,
    WebhookProcessingResult
)
from infrastructure.eventbus.core.events import Event, EventPriority
from infrastructure.eventbus.factory import create_eventbus_from_env
from config import config

logger = logging.getLogger(__name__)


class WebhookHandler:
    """
    Processes GitHub webhooks and publishes platform events.

    Handles all major GitHub event types and translates them to platform events.
    """

    def __init__(self):
        self.eventbus = create_eventbus_from_env()

    async def process_webhook(
        self,
        event_type: str,
        payload: Dict[str, Any],
        delivery_id: str
    ) -> WebhookProcessingResult:
        """
        Process GitHub webhook and publish to EventBus.

        Args:
            event_type: GitHub event type (X-GitHub-Event header)
            payload: Webhook payload
            delivery_id: GitHub delivery ID

        Returns:
            WebhookProcessingResult
        """
        try:
            # Route to specific handler
            handler_map = {
                "pull_request": self._handle_pull_request,
                "issues": self._handle_issue,
                "push": self._handle_push,
                "release": self._handle_release,
                "deployment": self._handle_deployment,
                "check_run": self._handle_check_run,
                "workflow_run": self._handle_workflow_run
            }

            handler = handler_map.get(event_type)
            if handler:
                await handler(payload, delivery_id)
                event_published = True
            else:
                logger.warning(f"No handler for event type: {event_type}")
                event_published = False

            return WebhookProcessingResult(
                delivery_id=delivery_id,
                event_type=event_type,
                success=True,
                event_published=event_published
            )

        except Exception as e:
            logger.error(f"Webhook processing failed: {e}")
            return WebhookProcessingResult(
                delivery_id=delivery_id,
                event_type=event_type,
                success=False,
                error_message=str(e)
            )

    async def _handle_pull_request(self, payload: Dict[str, Any], delivery_id: str):
        """Handle pull_request event"""
        action = payload.get("action")
        pr = payload.get("pull_request", {})
        repo = payload.get("repository", {})

        event = Event.create(
            event_type=f"github.pull_request.{action}",
            data={
                "pr_number": pr.get("number"),
                "title": pr.get("title"),
                "state": pr.get("state"),
                "author": pr.get("user", {}).get("login"),
                "repository": repo.get("full_name"),
                "url": pr.get("html_url"),
                "delivery_id": delivery_id
            },
            source=config.SERVICE_NAME,
            tenant_id=self._extract_tenant_id(payload),
            priority=EventPriority.NORMAL
        )

        await self.eventbus.publish(event)
        logger.info(f"Published PR event: {action} - #{pr.get('number')}")

    async def _handle_issue(self, payload: Dict[str, Any], delivery_id: str):
        """Handle issues event"""
        action = payload.get("action")
        issue = payload.get("issue", {})
        repo = payload.get("repository", {})

        event = Event.create(
            event_type=f"github.issue.{action}",
            data={
                "issue_number": issue.get("number"),
                "title": issue.get("title"),
                "state": issue.get("state"),
                "author": issue.get("user", {}).get("login"),
                "repository": repo.get("full_name"),
                "labels": [label.get("name") for label in issue.get("labels", [])],
                "url": issue.get("html_url"),
                "delivery_id": delivery_id
            },
            source=config.SERVICE_NAME,
            tenant_id=self._extract_tenant_id(payload),
            priority=EventPriority.NORMAL
        )

        await self.eventbus.publish(event)
        logger.info(f"Published issue event: {action} - #{issue.get('number')}")

    async def _handle_push(self, payload: Dict[str, Any], delivery_id: str):
        """Handle push event"""
        ref = payload.get("ref")
        repo = payload.get("repository", {})
        commits = payload.get("commits", [])

        event = Event.create(
            event_type="github.push",
            data={
                "ref": ref,
                "branch": ref.replace("refs/heads/", ""),
                "repository": repo.get("full_name"),
                "commits_count": len(commits),
                "commits": commits,
                "pusher": payload.get("pusher", {}).get("name"),
                "delivery_id": delivery_id
            },
            source=config.SERVICE_NAME,
            tenant_id=self._extract_tenant_id(payload),
            priority=EventPriority.NORMAL
        )

        await self.eventbus.publish(event)
        logger.info(f"Published push event: {ref} - {len(commits)} commits")

    async def _handle_release(self, payload: Dict[str, Any], delivery_id: str):
        """Handle release event"""
        action = payload.get("action")
        release = payload.get("release", {})

        event = Event.create(
            event_type=f"github.release.{action}",
            data={
                "tag_name": release.get("tag_name"),
                "name": release.get("name"),
                "prerelease": release.get("prerelease"),
                "draft": release.get("draft"),
                "url": release.get("html_url"),
                "delivery_id": delivery_id
            },
            source=config.SERVICE_NAME,
            tenant_id=self._extract_tenant_id(payload),
            priority=EventPriority.HIGH
        )

        await self.eventbus.publish(event)

    async def _handle_deployment(self, payload: Dict[str, Any], delivery_id: str):
        """Handle deployment event"""
        deployment = payload.get("deployment", {})

        event = Event.create(
            event_type="github.deployment.created",
            data={
                "environment": deployment.get("environment"),
                "ref": deployment.get("ref"),
                "sha": deployment.get("sha"),
                "task": deployment.get("task"),
                "delivery_id": delivery_id
            },
            source=config.SERVICE_NAME,
            tenant_id=self._extract_tenant_id(payload),
            priority=EventPriority.HIGH
        )

        await self.eventbus.publish(event)

    async def _handle_check_run(self, payload: Dict[str, Any], delivery_id: str):
        """Handle check_run event"""
        action = payload.get("action")
        check_run = payload.get("check_run", {})

        event = Event.create(
            event_type=f"github.check_run.{action}",
            data={
                "name": check_run.get("name"),
                "conclusion": check_run.get("conclusion"),
                "status": check_run.get("status"),
                "delivery_id": delivery_id
            },
            source=config.SERVICE_NAME,
            tenant_id=self._extract_tenant_id(payload),
            priority=EventPriority.NORMAL
        )

        await self.eventbus.publish(event)

    async def _handle_workflow_run(self, payload: Dict[str, Any], delivery_id: str):
        """Handle workflow_run event"""
        action = payload.get("action")
        workflow_run = payload.get("workflow_run", {})

        event = Event.create(
            event_type=f"github.workflow_run.{action}",
            data={
                "name": workflow_run.get("name"),
                "conclusion": workflow_run.get("conclusion"),
                "status": workflow_run.get("status"),
                "run_number": workflow_run.get("run_number"),
                "delivery_id": delivery_id
            },
            source=config.SERVICE_NAME,
            tenant_id=self._extract_tenant_id(payload),
            priority=EventPriority.NORMAL
        )

        await self.eventbus.publish(event)

    def _extract_tenant_id(self, payload: Dict[str, Any]) -> str:
        """Extract tenant ID from payload (installation ID or default)"""
        installation = payload.get("installation", {})
        installation_id = installation.get("id")

        if installation_id:
            return f"github_installation_{installation_id}"

        return config.DEFAULT_TENANT_ID
