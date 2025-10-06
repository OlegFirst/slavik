"""
GitHub Integration Data Models
==============================

Pydantic models for GitHub webhooks, API responses, and database entities.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum
from pydantic import BaseModel, Field
from uuid import uuid4


class GitHubEventType(str, Enum):
    """GitHub event types we handle"""
    PUSH = "push"
    PULL_REQUEST = "pull_request"
    PULL_REQUEST_REVIEW = "pull_request_review"
    ISSUES = "issues"
    ISSUE_COMMENT = "issue_comment"
    RELEASE = "release"
    DEPLOYMENT = "deployment"
    DEPLOYMENT_STATUS = "deployment_status"
    STATUS = "status"
    CHECK_RUN = "check_run"
    CHECK_SUITE = "check_suite"
    WORKFLOW_RUN = "workflow_run"


class WebhookEvent(BaseModel):
    """Base webhook event model"""
    event_type: str
    delivery_id: str
    signature: str
    payload: Dict[str, Any]
    received_at: datetime = Field(default_factory=datetime.utcnow)


class PRWebhookPayload(BaseModel):
    """Pull Request webhook payload"""
    action: str  # opened, closed, reopened, synchronized, etc.
    number: int
    pull_request: Dict[str, Any]
    repository: Dict[str, Any]
    sender: Dict[str, Any]
    installation: Optional[Dict[str, Any]] = None


class IssueWebhookPayload(BaseModel):
    """Issue webhook payload"""
    action: str
    issue: Dict[str, Any]
    repository: Dict[str, Any]
    sender: Dict[str, Any]
    installation: Optional[Dict[str, Any]] = None


class PushWebhookPayload(BaseModel):
    """Push webhook payload"""
    ref: str
    before: str
    after: str
    commits: List[Dict[str, Any]]
    repository: Dict[str, Any]
    sender: Dict[str, Any]
    installation: Optional[Dict[str, Any]] = None


# Database Models
class GitHubInstallation(BaseModel):
    """GitHub App installation"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    installation_id: int
    account_type: str  # "User" or "Organization"
    account_login: str
    tenant_id: str
    installed_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class GitHubPullRequest(BaseModel):
    """Pull Request record"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    pr_number: int
    repository_full_name: str
    title: str
    state: str  # open, closed, merged
    author: str
    created_at: datetime
    updated_at: datetime
    merged_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    installation_id: int
    tenant_id: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class GitHubIssue(BaseModel):
    """Issue record"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    issue_number: int
    repository_full_name: str
    title: str
    state: str  # open, closed
    author: str
    created_at: datetime
    updated_at: datetime
    closed_at: Optional[datetime] = None
    installation_id: int
    tenant_id: str
    labels: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class WebhookProcessingResult(BaseModel):
    """Result of webhook processing"""
    delivery_id: str
    event_type: str
    success: bool
    processed_at: datetime = Field(default_factory=datetime.utcnow)
    error_message: Optional[str] = None
    event_published: bool = False


class InstallationToken(BaseModel):
    """GitHub App installation token"""
    token: str
    expires_at: datetime
    installation_id: int
    permissions: Dict[str, str] = Field(default_factory=dict)


class GitHubAPIRequest(BaseModel):
    """GitHub API request tracking"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    method: str
    endpoint: str
    status_code: int
    duration_ms: float
    rate_limit_remaining: Optional[int] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    error: Optional[str] = None
