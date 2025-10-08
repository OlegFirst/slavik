"""
Module Scanner Tool
===================

Wrapper for infrastructure/tools/analyzers/module_scanner.py

Scans and catalogs all Python modules in the platform.
"""

import sys
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

from ..config import settings

logger = logging.getLogger(__name__)

# Add tools/analyzers to Python path
analyzers_path = Path(settings.TOOLS_ANALYZERS_PATH)
if str(analyzers_path) not in sys.path:
    sys.path.insert(0, str(analyzers_path))

try:
    from module_scanner import ModuleScanner as OriginalModuleScanner
    TOOL_AVAILABLE = True
    logger.info("✅ module_scanner tool loaded successfully")
except ImportError as e:
    TOOL_AVAILABLE = False
    logger.warning(f"❌ module_scanner tool not available: {e}")
    OriginalModuleScanner = None


class ModuleScannerTool:
    """
    Wrapper for Module Scanner tool

    Scans all Python modules and packages.

    Competency required: JUNIOR

    Example:
        ```python
        tool = ModuleScannerTool()
        modules = await tool.scan_all_modules()
        print(f"Total modules: {modules['total_modules']}")
        ```
    """

    def __init__(self):
        """Initialize Module Scanner tool"""
        self.available = TOOL_AVAILABLE
        self.name = "module_scanner"
        self.description = "Scans all Python modules in the platform"
        self.competency_required = "junior"

        if self.available:
            try:
                self.tool = OriginalModuleScanner()
                logger.info("ModuleScannerTool initialized")
            except Exception as e:
                logger.error(f"Failed to initialize ModuleScanner: {e}")
                self.available = False
                self.tool = None
        else:
            self.tool = None

    async def scan_all_modules(self, project_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Scan all modules in the platform

        Args:
            project_path: Path to project

        Returns:
            Complete module catalog
        """
        if not self.available:
            logger.warning("module_scanner tool not available")
            return {
                "total_modules": 0,
                "modules": [],
                "error": "Tool not available"
            }

        try:
            if not project_path:
                project_path = settings.PROJECT_ROOT

            modules = self.tool.scan_modules(project_path)

            return {
                "total_modules": len(modules),
                "modules": modules,
                "analyzed_at": self.tool._get_timestamp()
            }

        except Exception as e:
            logger.error(f"Module scanning failed: {e}")
            return {"error": str(e)}
