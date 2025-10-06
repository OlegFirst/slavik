"""
User Service - Real Database Authentication
Replaces mock authentication with Supabase users table
"""

from typing import Optional, Dict, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from passlib.hash import bcrypt
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class User:
    """User model for authentication"""

    def __init__(
        self,
        user_id: str,
        username: str,
        email: str,
        password_hash: str,
        roles: List[str],
        tenant_id: str,
        is_active: bool = True,
        is_verified: bool = False,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        department: Optional[str] = None,
        job_title: Optional[str] = None,
    ):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.roles = roles
        self.tenant_id = tenant_id
        self.is_active = is_active
        self.is_verified = is_verified
        self.first_name = first_name
        self.last_name = last_name
        self.department = department
        self.job_title = job_title


class UserService:
    """
    User authentication service

    Handles:
    - User login with password verification
    - Password hashing
    - User lookup
    - Failed login tracking
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def authenticate_user(
        self,
        username: str,
        password: str,
        tenant_id: str = "tenant_001",
    ) -> Optional[User]:
        """
        Authenticate user with username/password

        Returns:
            User object if authentication successful, None otherwise
        """
        # Get user from database
        user = await self._get_user_by_username(username, tenant_id)

        if not user:
            logger.warning(f"Authentication failed: user '{username}' not found")
            return None

        # Check if account is active
        if not user.is_active:
            logger.warning(f"Authentication failed: user '{username}' is inactive")
            return None

        # Verify password
        if not self._verify_password(password, user.password_hash):
            logger.warning(f"Authentication failed: invalid password for '{username}'")
            await self._record_failed_login(user.user_id)
            return None

        # Record successful login
        await self._record_successful_login(user.user_id)

        logger.info(f"User '{username}' authenticated successfully")
        return user

    async def _get_user_by_username(
        self,
        username: str,
        tenant_id: str
    ) -> Optional[User]:
        """Get user from database by username"""
        try:
            # Direct SQL query (since we don't have SQLAlchemy model yet)
            query = """
                SELECT
                    user_id,
                    username,
                    email,
                    password_hash,
                    roles,
                    tenant_id,
                    is_active,
                    is_verified,
                    first_name,
                    last_name,
                    department,
                    job_title
                FROM auth.users
                WHERE username = :username
                  AND tenant_id = :tenant_id
                  AND deleted_at IS NULL
                  AND is_active = TRUE
            """

            result = await self.db.execute(
                select([query]).params(username=username, tenant_id=tenant_id)
            )
            row = result.first()

            if not row:
                return None

            # Parse roles from JSONB
            roles = row.roles if isinstance(row.roles, list) else []

            return User(
                user_id=row.user_id,
                username=row.username,
                email=row.email,
                password_hash=row.password_hash,
                roles=roles,
                tenant_id=row.tenant_id,
                is_active=row.is_active,
                is_verified=row.is_verified,
                first_name=row.first_name,
                last_name=row.last_name,
                department=row.department,
                job_title=row.job_title,
            )

        except Exception as e:
            logger.error(f"Error getting user by username: {e}")
            return None

    def _verify_password(self, plain_password: str, password_hash: str) -> bool:
        """Verify password using bcrypt"""
        try:
            return bcrypt.verify(plain_password, password_hash)
        except Exception as e:
            logger.error(f"Error verifying password: {e}")
            return False

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt"""
        return bcrypt.hash(password)

    async def _record_successful_login(self, user_id: str):
        """Record successful login"""
        try:
            query = """
                UPDATE auth.users
                SET
                    last_login_at = :now,
                    failed_login_attempts = 0
                WHERE user_id = :user_id
            """
            await self.db.execute(
                update([query]).params(
                    now=datetime.utcnow(),
                    user_id=user_id
                )
            )
            await self.db.commit()
        except Exception as e:
            logger.error(f"Error recording successful login: {e}")

    async def _record_failed_login(self, user_id: str):
        """Record failed login attempt"""
        try:
            query = """
                UPDATE auth.users
                SET
                    failed_login_attempts = failed_login_attempts + 1,
                    locked_until = CASE
                        WHEN failed_login_attempts + 1 >= 5
                        THEN :lock_until
                        ELSE NULL
                    END
                WHERE user_id = :user_id
            """
            from datetime import timedelta
            lock_until = datetime.utcnow() + timedelta(minutes=15)

            await self.db.execute(
                update([query]).params(
                    lock_until=lock_until,
                    user_id=user_id
                )
            )
            await self.db.commit()
        except Exception as e:
            logger.error(f"Error recording failed login: {e}")

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by user_id"""
        try:
            query = """
                SELECT
                    user_id,
                    username,
                    email,
                    password_hash,
                    roles,
                    tenant_id,
                    is_active,
                    is_verified,
                    first_name,
                    last_name,
                    department,
                    job_title
                FROM auth.users
                WHERE user_id = :user_id
                  AND deleted_at IS NULL
            """

            result = await self.db.execute(
                select([query]).params(user_id=user_id)
            )
            row = result.first()

            if not row:
                return None

            roles = row.roles if isinstance(row.roles, list) else []

            return User(
                user_id=row.user_id,
                username=row.username,
                email=row.email,
                password_hash=row.password_hash,
                roles=roles,
                tenant_id=row.tenant_id,
                is_active=row.is_active,
                is_verified=row.is_verified,
                first_name=row.first_name,
                last_name=row.last_name,
                department=row.department,
                job_title=row.job_title,
            )

        except Exception as e:
            logger.error(f"Error getting user by ID: {e}")
            return None


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_user_dict(user: User) -> Dict:
    """Convert User object to dictionary for JWT payload"""
    return {
        "user_id": user.user_id,
        "username": user.username,
        "email": user.email,
        "tenant_id": user.tenant_id,
        "roles": user.roles,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "department": user.department,
        "job_title": user.job_title,
    }
