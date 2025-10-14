"""
External Integrations - Wrappers for external services

Provides unified interfaces for:
- GitHub API
- Anthropic Claude API
- Supabase
- Other external services
"""

from .github_client import GitHubTokenManager

__all__ = [
    'GitHubTokenManager',
]