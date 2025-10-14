"""
API Mapper Tool
===============

Wrapper for infrastructure/tools/analyzers/api_mapper.py

Maps all API endpoints across services.
"""

import sys
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

from config import settings

logger = logging.getLogger(__name__)

# Add tools/analyzers to Python path
analyzers_path = Path(settings.TOOLS_ANALYZERS_PATH)
if str(analyzers_path) not in sys.path:
    sys.path.insert(0, str(analyzers_path))

try:
    from api_mapper import APIMapper as OriginalAPIMapper
    TOOL_AVAILABLE = True
    logger.info("✅ api_mapper tool loaded successfully")
except ImportError as e:
    TOOL_AVAILABLE = False
    logger.warning(f"❌ api_mapper tool not available: {e}")
    OriginalAPIMapper = None


class APIMapperTool:
    """
    Wrapper for API Mapper tool

    Maps all REST API endpoints across the platform.

    Competency required: MIDDLE

    Example:
        ```python
        tool = APIMapperTool()
        api_map = await tool.map_all_apis()
        print(f"Total endpoints: {api_map['total_endpoints']}")
        ```
    """

    def __init__(self):
        """Initialize API Mapper tool"""
        self.available = TOOL_AVAILABLE
        self.name = "api_mapper"
        self.description = "Maps all API endpoints across services"
        self.competency_required = "middle"

        if self.available:
            try:
                self.tool = OriginalAPIMapper()
                logger.info("APIMapperTool initialized")
            except Exception as e:
                logger.error(f"Failed to initialize APIMapper: {e}")
                self.available = False
                self.tool = None
        else:
            self.tool = None

    async def map_all_apis(self) -> Dict[str, Any]:
        """
        Map all API endpoints in the platform

        Returns:
            Complete API map

        Example:
            ```python
            api_map = await tool.map_all_apis()

            for service, endpoints in api_map['services'].items():
                print(f"{service}: {len(endpoints)} endpoints")
            ```
        """
        if not self.available:
            logger.warning("api_mapper tool not available")
            return {
                "total_services": 0,
                "total_endpoints": 0,
                "services": {},
                "error": "Tool not available"
            }

        try:
            api_map = self.tool.map_all_apis()

            total_endpoints = sum(
                len(endpoints)
                for endpoints in api_map.get("services", {}).values()
            )

            return {
                "total_services": len(api_map.get("services", {})),
                "total_endpoints": total_endpoints,
                "services": api_map.get("services", {}),
                "analyzed_at": api_map.get("analyzed_at")
            }

        except Exception as e:
            logger.error(f"API mapping failed: {e}")
            return {"error": str(e)}

    async def get_service_endpoints(self, service_name: str) -> List[Dict[str, Any]]:
        """
        Get endpoints for specific service

        Args:
            service_name: Name of service

        Returns:
            List of endpoints
        """
        if not self.available:
            return []

        try:
            api_map = await self.map_all_apis()
            return api_map.get("services", {}).get(service_name, [])

        except Exception as e:
            logger.error(f"Failed to get endpoints for {service_name}: {e}")
            return []
