# -*- coding: utf-8 -*-
"""
BCM Authentication REST API Adapter
Provides REST API endpoints for Vue frontend authentication
Converts REST requests to Odoo session management
"""

from odoo import http
from odoo.http import request
import json
import logging
from werkzeug.exceptions import BadRequest

_logger = logging.getLogger(__name__)


class BCMAuthController(http.Controller):
    """
    Authentication controller that provides REST API endpoints
    for Vue frontend integration with Odoo backend
    """

    def _build_response(self, success=True, data=None, message="", status_code=200):
        """Build unified response format"""
        response_data = {
            "success": success,
            "data": data or {},
            "message": message
        }

        response = request.make_response(
            json.dumps(response_data),
            headers=[
                ('Content-Type', 'application/json'),
                ('Access-Control-Allow-Origin', '*'),
                ('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS'),
                ('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With'),
                ('Access-Control-Allow-Credentials', 'true')
            ]
        )
        response.status_code = status_code
        return response

    def _get_user_data(self, user):
        """Extract user data for API response"""
        if not user:
            return None

        return {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'login': user.login,
            'company_id': user.company_id.id,
            'company_name': user.company_id.name,
            'groups': [group.name for group in user.groups_id],
            'is_admin': user.has_group('base.group_system'),
            'avatar_url': f'/web/image?model=res.users&id={user.id}&field=image_128',
            'lang': user.lang,
            'tz': user.tz or 'UTC'
        }

    @http.route('/api/auth/login', type='json', auth='none', methods=['POST'], cors='*', csrf=False)
    def api_login(self, email=None, password=None, **kwargs):
        """
        REST API Login endpoint
        Accepts: {"email": "user@example.com", "password": "password"}
        Returns: {"success": true, "data": {...user_data...}, "message": "Login successful"}
        """
        try:
            # Validate input parameters
            if not email or not password:
                _logger.warning("Login attempt with missing credentials")
                return self._build_response(
                    success=False,
                    message="Email and password are required",
                    status_code=400
                )

            # Authenticate user using Odoo's authentication system
            db = request.session.db or request.env.cr.dbname

            try:
                # Try to authenticate
                uid = request.session.authenticate(db, email, password)

                if not uid:
                    _logger.warning(f"Failed login attempt for email: {email}")
                    return self._build_response(
                        success=False,
                        message="Invalid email or password",
                        status_code=401
                    )

                # Get user data
                user = request.env['res.users'].sudo().browse(uid)
                user_data = self._get_user_data(user)

                _logger.info(f"Successful login for user: {email}")

                return self._build_response(
                    success=True,
                    data={
                        'user': user_data,
                        'session_id': request.session.sid,
                        'db': db
                    },
                    message="Login successful"
                )

            except Exception as auth_error:
                _logger.error(f"Authentication error for {email}: {auth_error}")
                return self._build_response(
                    success=False,
                    message="Authentication failed",
                    status_code=401
                )

        except Exception as e:
            _logger.error(f"Login API error: {e}")
            return self._build_response(
                success=False,
                message="Internal server error",
                status_code=500
            )

    @http.route('/api/auth/me', type='json', auth='user', methods=['GET'], cors='*', csrf=False)
    def api_current_user(self, **kwargs):
        """
        Get current authenticated user data
        Returns: {"success": true, "data": {...user_data...}, "message": "User data retrieved"}
        """
        try:
            if not request.env.user or request.env.user._is_public():
                return self._build_response(
                    success=False,
                    message="Not authenticated",
                    status_code=401
                )

            user_data = self._get_user_data(request.env.user)

            return self._build_response(
                success=True,
                data={'user': user_data},
                message="User data retrieved successfully"
            )

        except Exception as e:
            _logger.error(f"Current user API error: {e}")
            return self._build_response(
                success=False,
                message="Failed to retrieve user data",
                status_code=500
            )

    @http.route('/api/auth/logout', type='json', auth='user', methods=['POST'], cors='*', csrf=False)
    def api_logout(self, **kwargs):
        """
        Logout current user and destroy session
        Returns: {"success": true, "data": {}, "message": "Logout successful"}
        """
        try:
            user_email = request.env.user.email if request.env.user else "unknown"

            # Destroy the session
            request.session.logout(keep_db=False)

            _logger.info(f"User logged out: {user_email}")

            return self._build_response(
                success=True,
                data={},
                message="Logout successful"
            )

        except Exception as e:
            _logger.error(f"Logout API error: {e}")
            return self._build_response(
                success=False,
                message="Logout failed",
                status_code=500
            )

    @http.route('/api/auth/refresh', type='json', auth='user', methods=['POST'], cors='*', csrf=False)
    def api_refresh_session(self, **kwargs):
        """
        Refresh current session and return updated user data
        Returns: {"success": true, "data": {...user_data...}, "message": "Session refreshed"}
        """
        try:
            if not request.env.user or request.env.user._is_public():
                return self._build_response(
                    success=False,
                    message="Not authenticated",
                    status_code=401
                )

            # Update session timestamp
            request.session.update({})

            user_data = self._get_user_data(request.env.user)

            return self._build_response(
                success=True,
                data={
                    'user': user_data,
                    'session_id': request.session.sid
                },
                message="Session refreshed successfully"
            )

        except Exception as e:
            _logger.error(f"Session refresh API error: {e}")
            return self._build_response(
                success=False,
                message="Failed to refresh session",
                status_code=500
            )

    @http.route('/api/auth/check', type='json', auth='none', methods=['GET', 'POST'], cors='*', csrf=False)
    def api_check_auth(self, **kwargs):
        """
        Check authentication status without requiring authentication
        Returns: {"success": true, "data": {"authenticated": true/false}, "message": "..."}
        """
        try:
            authenticated = bool(
                request.env.user and
                not request.env.user._is_public() and
                request.session.uid
            )

            response_data = {
                'authenticated': authenticated,
                'session_id': request.session.sid if authenticated else None
            }

            if authenticated:
                response_data['user'] = self._get_user_data(request.env.user)

            return self._build_response(
                success=True,
                data=response_data,
                message="Authentication status checked"
            )

        except Exception as e:
            _logger.error(f"Auth check API error: {e}")
            return self._build_response(
                success=False,
                data={'authenticated': False},
                message="Failed to check authentication status"
            )

    @http.route('/api/auth/status', type='http', auth='none', methods=['OPTIONS'], cors='*', csrf=False)
    def api_options_handler(self, **kwargs):
        """Handle CORS preflight requests"""
        return request.make_response(
            '',
            headers=[
                ('Access-Control-Allow-Origin', '*'),
                ('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS'),
                ('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With'),
                ('Access-Control-Allow-Credentials', 'true'),
                ('Access-Control-Max-Age', '3600')
            ]
        )