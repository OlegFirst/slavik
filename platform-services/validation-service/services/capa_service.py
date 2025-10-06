"""
CAPA Service
Business logic for Corrective and Preventive Actions management
"""

from typing import List, Optional, Dict
from datetime import datetime
from repositories.repository import ValidationRepository
from workflows.capa_workflow import can_verify_capa
from models.database import CAPA as CAPADB
from models.domain import CAPAStatus


class CAPAService:
    """CAPA business logic service"""

    def __init__(self, repository: ValidationRepository):
        self.repo = repository

    async def create_capa(self, capa_data: Dict) -> CAPADB:
        """Create new CAPA"""
        # Set initial status
        capa_data["status"] = CAPAStatus.OPEN

        return await self.repo.create_capa(capa_data)

    async def list_capas(
        self,
        tenant_id: str,
        status: Optional[str] = None,
        source: Optional[str] = None,
        priority: Optional[str] = None
    ) -> List[CAPADB]:
        """List CAPAs with filters"""
        return await self.repo.list_capas(tenant_id, status, source, priority)

    async def get_capa(self, capa_id: int) -> CAPADB:
        """Get CAPA by ID"""
        capa = await self.repo.get_capa(capa_id)
        if not capa:
            raise ValueError("CAPA not found")
        return capa

    async def update_capa(self, capa_id: int, updates: Dict) -> CAPADB:
        """Update CAPA"""
        capa = await self.repo.update_capa(capa_id, updates)
        if not capa:
            raise ValueError("CAPA not found")
        return capa

    async def verify_capa(self, capa_id: int) -> CAPADB:
        """Verify CAPA effectiveness with workflow validation"""
        capa = await self.repo.get_capa(capa_id)
        if not capa:
            raise ValueError("CAPA not found")

        # Validate workflow transition
        can_verify, error = can_verify_capa(capa)
        if not can_verify:
            raise ValueError(error)

        # Update CAPA status
        updates = {
            "status": CAPAStatus.VERIFIED,
            "verification_date": datetime.utcnow()
        }

        return await self.repo.update_capa(capa_id, updates)
