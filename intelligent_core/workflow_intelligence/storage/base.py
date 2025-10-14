"""
Base Storage Adapter Protocol
"""

from typing import Protocol, Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime


class StorageAdapter(Protocol):
    """Protocol for storage adapters"""

    async def save_workflow_context(
        self,
        workflow_id: str,
        module: str,
        context: Dict[str, Any],
        tenant_id: str
    ) -> None:
        """Save workflow context"""
        ...

    async def get_workflow_context(
        self,
        workflow_id: str,
        tenant_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get workflow context"""
        ...

    async def save_case(
        self,
        case_id: str,
        module: str,
        case_data: Dict[str, Any],
        tenant_id: str
    ) -> None:
        """Save completed workflow case"""
        ...

    async def find_similar_cases(
        self,
        module: str,
        org_context: Dict[str, Any],
        current_stage: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Find similar cases using vector similarity"""
        ...

    async def get_benchmarks(
        self,
        module: str,
        industry: Optional[str] = None,
        org_size: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get benchmarks for module"""
        ...

    async def save_prediction(
        self,
        workflow_id: str,
        prediction: Dict[str, Any],
        tenant_id: str
    ) -> None:
        """Save ML prediction"""
        ...

    async def close(self) -> None:
        """Close connection"""
        ...
