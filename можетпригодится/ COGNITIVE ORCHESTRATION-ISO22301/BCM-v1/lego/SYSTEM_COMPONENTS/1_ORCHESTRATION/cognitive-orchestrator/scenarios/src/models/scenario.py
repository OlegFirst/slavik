from datetime import datetime
from pydantic import BaseModel, Field
from typing import Any, Dict


class Scenario(BaseModel):
    """Simplified scenario model for AI orchestrator."""
    id: str
    company_id: str
    title: str
    description: str
    scenario_type: str
    risk_level: str
    data: Dict[str, Any]
    created_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
