"""
Event Intelligence Integration

Connects to intelligent-core/event_intelligence service for AI-powered analysis
"""

import logging
import httpx
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class EventIntelligenceIntegration:
    """
    Integration with Event Intelligence service

    Provides:
    - AI-powered event analysis
    - Pattern detection
    - Predictive recommendations
    """

    def __init__(self, base_url: str = 'http://localhost:8039'):
        """
        Initialize Event Intelligence integration

        Args:
            base_url: Event Intelligence service base URL
        """
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
        self.available = False

    async def initialize(self):
        """Check if Event Intelligence service is available"""
        try:
            response = await self.client.get(f"{self.base_url}/health")
            if response.status_code == 200:
                self.available = True
                logger.info(" Event Intelligence service available")
            else:
                logger.warning(f"Event Intelligence service returned {response.status_code}")
        except Exception as e:
            logger.warning(f"Event Intelligence service not available: {e}")
            self.available = False

    async def analyze_event(self, event_data: Dict) -> Optional[Dict]:
        """
        Analyze event with AI

        Args:
            event_data: Event data to analyze

        Returns:
            AI analysis results or None
        """
        if not self.available:
            logger.warning("Event Intelligence service not available")
            return None

        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/event-intelligence/analyze",
                json=event_data,
                timeout=60.0
            )

            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Analysis failed: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"Failed to analyze event: {e}")
            return None

    async def get_recommendations(self, context: Dict) -> Optional[Dict]:
        """
        Get AI recommendations

        Args:
            context: Analysis context

        Returns:
            Recommendations or None
        """
        if not self.available:
            return None

        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/event-intelligence/recommendations",
                json=context
            )

            if response.status_code == 200:
                return response.json()
            else:
                return None

        except Exception as e:
            logger.error(f"Failed to get recommendations: {e}")
            return None

    async def predict_future_gaps(self, current_state: Dict) -> Optional[Dict]:
        """
        Predict future event gaps

        Args:
            current_state: Current system state

        Returns:
            Predictions or None
        """
        if not self.available:
            return None

        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/event-intelligence/predict",
                json=current_state
            )

            if response.status_code == 200:
                return response.json()
            else:
                return None

        except Exception as e:
            logger.error(f"Failed to predict gaps: {e}")
            return None

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()
