"""
JWT Token Handler
Production-grade JWT validation and claims extraction
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
import jwt
from jwt.exceptions import (
    ExpiredSignatureError,
    InvalidTokenError,
    DecodeError,
    InvalidSignatureError,
)

from config import settings

logger = logging.getLogger(__name__)


class JWTError(Exception):
    """Base exception for JWT errors"""
    pass


class TokenExpiredError(JWTError):
    """Token has expired"""
    pass


class TokenInvalidError(JWTError):
    """Token is invalid"""
    pass


class TokenMissingClaimsError(JWTError):
    """Required claims missing from token"""
    pass


class JWTHandler:
    """
    Production-grade JWT handler with comprehensive validation

    Features:
    - JWT token validation with RS256/HS256 support
    - Claims extraction and validation
    - Token expiration checking
    - Detailed error handling with specific exceptions
    - Thread-safe operations
    """

    def __init__(self):
        """Initialize JWT handler with configuration"""
        self.secret = settings.jwt_secret
        self.algorithm = settings.jwt_algorithm
        self.expiration_hours = settings.jwt_expiration_hours

        # Validate configuration
        if not self.secret:
            logger.error("JWT secret is not configured")
            raise ValueError("JWT_SECRET must be configured")

        logger.info(
            f"JWT Handler initialized with algorithm: {self.algorithm}, "
            f"expiration: {self.expiration_hours}h"
        )

    def validate_token(self, token: str) -> Dict[str, Any]:
        """
        Validate JWT token and extract claims

        Args:
            token: JWT token string (without Bearer prefix)

        Returns:
            Dict containing token claims

        Raises:
            TokenExpiredError: Token has expired
            TokenInvalidError: Token is malformed or invalid
            TokenMissingClaimsError: Required claims are missing
        """
        if not token:
            logger.warning("Empty token provided for validation")
            raise TokenInvalidError("Token cannot be empty")

        try:
            # Decode and validate token
            payload = jwt.decode(
                token,
                self.secret,
                algorithms=[self.algorithm],
                options={
                    "verify_signature": True,
                    "verify_exp": True,
                    "require": ["exp", "sub"],  # Required claims
                }
            )

            # Log successful validation (without sensitive data)
            user_id = payload.get("sub")
            logger.debug(f"Token validated successfully for user: {user_id}")

            return payload

        except ExpiredSignatureError as e:
            logger.warning(f"Token expired: {str(e)}")
            raise TokenExpiredError("Token has expired") from e

        except InvalidSignatureError as e:
            logger.error(f"Invalid token signature: {str(e)}")
            raise TokenInvalidError("Invalid token signature") from e

        except DecodeError as e:
            logger.error(f"Token decode error: {str(e)}")
            raise TokenInvalidError("Token is malformed") from e

        except InvalidTokenError as e:
            logger.error(f"Invalid token: {str(e)}")
            raise TokenInvalidError(f"Invalid token: {str(e)}") from e

        except Exception as e:
            logger.exception(f"Unexpected error validating token: {str(e)}")
            raise TokenInvalidError(f"Token validation failed: {str(e)}") from e

    def extract_claims(self, token: str) -> Dict[str, Any]:
        """
        Extract user claims from validated token

        Args:
            token: JWT token string

        Returns:
            Dict containing:
                - user_id: User identifier (from 'sub' claim)
                - tenant_id: Tenant/organization identifier
                - roles: List of user roles
                - email: User email address
                - exp: Token expiration timestamp
                - iat: Token issued at timestamp

        Raises:
            TokenExpiredError: Token has expired
            TokenInvalidError: Token is invalid
            TokenMissingClaimsError: Required claims missing
        """
        payload = self.validate_token(token)

        # Extract standard claims
        user_id = payload.get("sub")
        if not user_id:
            raise TokenMissingClaimsError("Token missing 'sub' claim (user_id)")

        # Extract optional but important claims
        tenant_id = payload.get("tenant_id") or payload.get("org_id")
        roles = payload.get("roles", [])
        email = payload.get("email")
        exp = payload.get("exp")
        iat = payload.get("iat")

        # Build claims dictionary
        claims = {
            "user_id": user_id,
            "tenant_id": tenant_id,
            "roles": roles if isinstance(roles, list) else [roles] if roles else [],
            "email": email,
            "exp": exp,
            "iat": iat,
            "raw_payload": payload,  # Include full payload for extensibility
        }

        logger.debug(f"Extracted claims for user {user_id}: {list(claims.keys())}")

        return claims

    def check_expiration(self, token: str) -> bool:
        """
        Check if token is expired without full validation

        Args:
            token: JWT token string

        Returns:
            True if token is expired, False otherwise
        """
        try:
            payload = jwt.decode(
                token,
                options={"verify_signature": False},  # Skip signature check for quick expiry check
                algorithms=[self.algorithm]
            )

            exp = payload.get("exp")
            if not exp:
                logger.warning("Token missing expiration claim")
                return True

            # Check if expired
            is_expired = datetime.utcnow().timestamp() >= exp

            if is_expired:
                logger.debug("Token is expired")

            return is_expired

        except Exception as e:
            logger.error(f"Error checking token expiration: {str(e)}")
            return True  # Treat errors as expired for safety

    def generate_token(
        self,
        user_id: str,
        tenant_id: Optional[str] = None,
        roles: Optional[list] = None,
        email: Optional[str] = None,
        extra_claims: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Generate a new JWT token (for testing or token refresh)

        Args:
            user_id: User identifier
            tenant_id: Tenant/organization identifier
            roles: List of user roles
            email: User email
            extra_claims: Additional claims to include

        Returns:
            Encoded JWT token string
        """
        now = datetime.utcnow()
        exp = now + timedelta(hours=self.expiration_hours)

        payload = {
            "sub": user_id,
            "iat": int(now.timestamp()),
            "exp": int(exp.timestamp()),
        }

        # Add optional claims
        if tenant_id:
            payload["tenant_id"] = tenant_id

        if roles:
            payload["roles"] = roles

        if email:
            payload["email"] = email

        # Add extra claims
        if extra_claims:
            payload.update(extra_claims)

        # Encode token
        token = jwt.encode(payload, self.secret, algorithm=self.algorithm)

        logger.info(f"Generated token for user {user_id}, expires at {exp.isoformat()}")

        return token

    def decode_without_verification(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Decode token without signature verification (for debugging/inspection)

        WARNING: Do not use for authentication! This is for debugging only.

        Args:
            token: JWT token string

        Returns:
            Decoded payload or None if decode fails
        """
        try:
            payload = jwt.decode(
                token,
                options={"verify_signature": False},
                algorithms=[self.algorithm]
            )
            return payload
        except Exception as e:
            logger.error(f"Error decoding token: {str(e)}")
            return None

    def is_token_revoked(self, token: str, redis_client) -> bool:
        """
        Check if token has been revoked (blacklisted)

        This requires Redis integration for the blacklist.
        Tokens can be added to blacklist on logout or security events.

        Args:
            token: JWT token string
            redis_client: Redis client instance

        Returns:
            True if token is revoked, False otherwise
        """
        try:
            # Extract token ID (jti claim) or use token hash
            payload = self.decode_without_verification(token)
            if not payload:
                return True  # Treat decode failures as revoked

            token_id = payload.get("jti", None)

            # If no jti, create hash of token as identifier
            if not token_id:
                import hashlib
                token_id = hashlib.sha256(token.encode()).hexdigest()

            # Check Redis blacklist
            key = f"token:blacklist:{token_id}"
            is_blacklisted = redis_client.exists(key)

            if is_blacklisted:
                logger.warning(f"Token {token_id[:8]}... is blacklisted")

            return bool(is_blacklisted)

        except Exception as e:
            logger.error(f"Error checking token revocation: {str(e)}")
            return False  # Don't block on errors


# Global JWT handler instance
jwt_handler = JWTHandler()


def get_jwt_handler() -> JWTHandler:
    """Get global JWT handler instance"""
    return jwt_handler
