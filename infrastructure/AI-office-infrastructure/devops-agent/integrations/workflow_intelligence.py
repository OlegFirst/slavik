#!/usr/bin/env python3
"""
Workflow Intelligence Integration

Integration between DevOps Agent and Workflow Intelligence (мозг)
"""

import httpx
import logging
from typing import Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class WorkflowIntelligenceClient:
    """Client for Workflow Intelligence (мозг)"""

    def __init__(self, base_url: str = "http://localhost:8050"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
        self.agent_id = "devops-agent"

    async def report_infrastructure_analysis(self, analysis: Dict) -> Dict:
        """
        Report infrastructure analysis to мозг

        Args:
            analysis: Infrastructure analysis results

        Returns:
            Brain's response with decisions
        """
        logger.info(f"📡 Sending infrastructure analysis to мозг...")

        try:
            response = await self.client.post(
                f"{self.base_url}/workflow/process",
                json={
                    "agent_id": self.agent_id,
                    "agent_type": "devops",
                    "timestamp": datetime.utcnow().isoformat(),
                    "action": "infrastructure_analysis",
                    "data": analysis
                }
            )

            response.raise_for_status()
            result = response.json()

            logger.info(f"✅ Brain response received: {result.get('status')}")
            return result

        except Exception as e:
            logger.error(f"❌ Failed to report to мозг: {e}")
            return {"status": "error", "error": str(e)}

    async def request_decision(self, context: Dict) -> Dict:
        """
        Request decision from мозг

        Args:
            context: Decision context (deployment, fix, etc.)

        Returns:
            Brain's decision
        """
        logger.info(f"🧠 Requesting decision from мозг...")

        try:
            response = await self.client.post(
                f"{self.base_url}/workflow/decide",
                json={
                    "agent_id": self.agent_id,
                    "context": context
                }
            )

            response.raise_for_status()
            decision = response.json()

            logger.info(f"✅ Decision received: {decision.get('action')}")
            return decision

        except Exception as e:
            logger.error(f"❌ Failed to get decision: {e}")
            return {"action": "none", "error": str(e)}

    async def report_fix_applied(self, fix_details: Dict) -> Dict:
        """
        Report that a fix was applied

        Args:
            fix_details: Details of the applied fix

        Returns:
            Acknowledgment
        """
        logger.info(f"🛠️  Reporting fix to мозг...")

        try:
            response = await self.client.post(
                f"{self.base_url}/workflow/fix-applied",
                json={
                    "agent_id": self.agent_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    "fix": fix_details
                }
            )

            response.raise_for_status()
            return response.json()

        except Exception as e:
            logger.error(f"❌ Failed to report fix: {e}")
            return {"status": "error", "error": str(e)}

    async def get_agent_context(self) -> Optional[Dict]:
        """
        Get current context from мозг for DevOps Agent

        Returns:
            Agent context with priorities, focus areas
        """
        try:
            response = await self.client.get(
                f"{self.base_url}/agents/{self.agent_id}/context"
            )

            response.raise_for_status()
            context = response.json()

            logger.info(f"✅ Agent context: {context.get('focus_area')}")
            return context

        except Exception as e:
            logger.warning(f"Could not get agent context: {e}")
            return None

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()
