"""Integration layer for Predictive Service"""

from .dependencies import (
    get_dependencies,
    cleanup_dependencies,
    get_supabase_client,
    get_predictive_repository,
    get_case_library,
    get_notification_client,
    NotificationClient,
    Dependencies
)

__all__ = [
    "get_dependencies",
    "cleanup_dependencies",
    "get_supabase_client",
    "get_predictive_repository",
    "get_case_library",
    "get_notification_client",
    "NotificationClient",
    "Dependencies"
]
