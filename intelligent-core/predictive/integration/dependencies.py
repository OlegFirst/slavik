"""
Predictive Service - Dependency Integration

Integrates all external services:
- Case Library (workflow_intelligence)
- Notification Service
- Database Repository
"""

import os
import sys
from pathlib import Path
import httpx
from supabase import create_client, Client

# Add parent directories to path
intelligent_core_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(intelligent_core_path))

from workflow_intelligence.case_library.repository import CaseRepository
from predictive.database.repository import PredictiveRepository


# =====================================================
# DATABASE SETUP
# =====================================================

def get_supabase_client() -> Client:
    """Get Supabase client for database operations"""
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

    if not supabase_url or not supabase_key:
        raise Exception("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set")

    return create_client(supabase_url, supabase_key)


def get_predictive_repository() -> PredictiveRepository:
    """Get Predictive Service database repository"""
    supabase = get_supabase_client()
    return PredictiveRepository(supabase_client=supabase)


# =====================================================
# CASE LIBRARY INTEGRATION
# =====================================================

async def get_case_library() -> CaseRepository:
    """
    Get Case Library repository for accessing historical journeys

    Returns:
        CaseRepository instance with database connection
    """
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    from sqlalchemy.orm import sessionmaker

    # Get database URL from environment
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        # Construct from Supabase credentials
        supabase_url = os.getenv("SUPABASE_URL")
        if not supabase_url:
            raise Exception("DATABASE_URL or SUPABASE_URL must be set")

        # Extract connection string from Supabase URL
        # Format: https://xxxxx.supabase.co -> postgres://postgres:password@db.xxxxx.supabase.co:5432/postgres
        project_ref = supabase_url.split("//")[1].split(".")[0]
        db_password = os.getenv("SUPABASE_DB_PASSWORD", os.getenv("SUPABASE_SERVICE_ROLE_KEY"))

        db_url = f"postgresql+asyncpg://postgres:{db_password}@db.{project_ref}.supabase.co:5432/postgres"

    # Create async engine
    engine = create_async_engine(db_url, echo=False)

    # Create session factory
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    # Create session
    async with async_session() as session:
        # Initialize Case Repository
        case_repository = CaseRepository(db_session=session)
        return case_repository


# =====================================================
# NOTIFICATION SERVICE INTEGRATION
# =====================================================

class NotificationClient:
    """Client for Notification Service API"""

    def __init__(self, base_url: str = None):
        self.base_url = base_url or os.getenv(
            "NOTIFICATION_SERVICE_URL",
            "http://localhost:8035"
        )
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=30.0)

    async def send_email(
        self,
        to: list[str],
        subject: str,
        body: str,
        html_body: str = None
    ) -> dict:
        """
        Send email notification

        Args:
            to: List of email addresses
            subject: Email subject
            body: Plain text body
            html_body: HTML body (optional)

        Returns:
            Response from notification service
        """
        try:
            response = await self.client.post(
                "/email/send",
                json={
                    "to": to,
                    "subject": subject,
                    "body": body,
                    "html_body": html_body
                }
            )

            response.raise_for_status()
            return response.json()

        except httpx.HTTPError as e:
            print(f"Error sending email notification: {e}")
            return {"status": "error", "message": str(e)}

    async def send_proactive_digest(
        self,
        user_email: str,
        recommendations: list[dict]
    ) -> dict:
        """
        Send daily proactive recommendations digest

        Args:
            user_email: User's email address
            recommendations: List of recommendations

        Returns:
            Response from notification service
        """
        # Build HTML email
        html_body = self._build_digest_html(recommendations)

        subject = f"📅 Your BCM Journey Update - {len(recommendations)} recommendations"

        body = f"""
You have {len(recommendations)} proactive recommendations for your BCM journey:

""" + "\n".join([
            f"{i+1}. {rec['title']} (Priority: {rec['priority']})"
            for i, rec in enumerate(recommendations)
        ])

        return await self.send_email(
            to=[user_email],
            subject=subject,
            body=body,
            html_body=html_body
        )

    def _build_digest_html(self, recommendations: list[dict]) -> str:
        """Build HTML email for recommendations digest"""

        priority_colors = {
            'critical': '#dc2626',
            'high': '#ea580c',
            'medium': '#ca8a04',
            'low': '#65a30d'
        }

        recs_html = ""
        for rec in recommendations:
            color = priority_colors.get(rec['priority'], '#6b7280')

            actions_html = ""
            if rec.get('actions'):
                actions_html = "<ul>" + "".join([
                    f"<li>{action}</li>"
                    for action in rec['actions']
                ]) + "</ul>"

            recs_html += f"""
            <div style="border-left: 4px solid {color}; padding-left: 16px; margin-bottom: 24px;">
                <h3 style="margin: 0 0 8px 0; color: {color};">
                    {rec['title']}
                </h3>
                <p style="color: #6b7280; margin: 0 0 8px 0;">
                    Priority: <strong>{rec['priority'].upper()}</strong>
                    {f" | {rec['days_until']} days until {rec['milestone']}" if rec.get('days_until') else ""}
                </p>
                <p style="margin: 0 0 12px 0;">
                    {rec['message']}
                </p>
                {f"<h4>Recommended Actions:</h4>{actions_html}" if actions_html else ""}
            </div>
            """

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #1f2937;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        h1 {{
            color: #111827;
            border-bottom: 3px solid #3b82f6;
            padding-bottom: 12px;
        }}
        .footer {{
            margin-top: 32px;
            padding-top: 16px;
            border-top: 1px solid #e5e7eb;
            color: #6b7280;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <h1>📅 Your BCM Journey Update</h1>
    <p>Here are {len(recommendations)} proactive recommendations to keep your BCM journey on track:</p>

    {recs_html}

    <div class="footer">
        <p>
            🔮 These recommendations are AI-powered predictions based on similar organizations' successful journeys.
        </p>
        <p>
            <a href="#">View in Dashboard</a> | <a href="#">Update Preferences</a>
        </p>
    </div>
</body>
</html>
        """

        return html

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


def get_notification_client() -> NotificationClient:
    """Get Notification Service client"""
    return NotificationClient()


# =====================================================
# DEPENDENCY CONTAINER
# =====================================================

class Dependencies:
    """Container for all service dependencies"""

    def __init__(self):
        self.supabase = None
        self.predictive_repo = None
        self.case_library = None
        self.notification_client = None

    async def initialize(self):
        """Initialize all dependencies"""
        # Database
        self.supabase = get_supabase_client()
        self.predictive_repo = get_predictive_repository()

        # Case Library
        self.case_library = await get_case_library()

        # Notification Service
        self.notification_client = get_notification_client()

        return self

    async def cleanup(self):
        """Cleanup connections"""
        if self.notification_client:
            await self.notification_client.close()


# Global dependencies instance
_dependencies: Dependencies = None


async def get_dependencies() -> Dependencies:
    """Get or create dependencies instance"""
    global _dependencies

    if _dependencies is None:
        _dependencies = Dependencies()
        await _dependencies.initialize()

    return _dependencies


async def cleanup_dependencies():
    """Cleanup global dependencies"""
    global _dependencies

    if _dependencies:
        await _dependencies.cleanup()
        _dependencies = None
