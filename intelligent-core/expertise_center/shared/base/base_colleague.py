"""
Base Colleague - Tactical Assistant AI

Colleagues = Tactical level assistants (7)
- Specific task execution
- Quick answers
- Workflow support
"""

from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod


class BaseColleague(ABC):
    """
    Base class for Tactical AI Colleagues

    Used for:
    - BIA Specialist
    - Risk Analyst
    - Project Manager
    - Incident Advisor
    - Plan Generator
    - Compliance Copilot
    - Exercise Designer
    """

    def __init__(
        self,
        colleague_id: str,
        name: str,
        specialty: str,
        domain: str = "bcm"
    ):
        self.colleague_id = colleague_id
        self.name = name
        self.specialty = specialty
        self.domain = domain

    @abstractmethod
    async def assist(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Provide tactical assistance

        Args:
            task: Task description
            context: Task context

        Returns:
            Assistance result
        """
        pass

    @abstractmethod
    async def validate(
        self,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate task data

        Args:
            data: Data to validate

        Returns:
            Validation result
        """
        pass

    async def get_capabilities(self) -> List[str]:
        """Get colleague capabilities"""
        return []

    def __repr__(self):
        return f"<{self.__class__.__name__} id={self.colleague_id} specialty={self.specialty}>"
