"""
API Request/Response Schemas
Additional schemas not in domain models
"""

from pydantic import BaseModel
from typing import Optional, Dict, Any


class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str
    service: str
    version: str
    port: int
    eventbus: str
    database: str


class ErrorResponse(BaseModel):
    """Error response"""
    detail: str
    error_code: Optional[str] = None
    additional_info: Optional[Dict[str, Any]] = None
