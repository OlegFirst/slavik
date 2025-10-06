"""API package for Compliance service"""

from .improvements import router as improvements_router
from .nonconformities import router as nonconformities_router

__all__ = ["improvements_router", "nonconformities_router"]
