"""
AST Analyzer Tool
=================

Wrapper for infrastructure/tools/analyzers/ast_analyzer.py

Analyzes Python code using Abstract Syntax Trees (AST).
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
    from ast_analyzer import ASTAnalyzer as OriginalASTAnalyzer
    TOOL_AVAILABLE = True
    logger.info("✅ ast_analyzer tool loaded successfully")
except ImportError as e:
    TOOL_AVAILABLE = False
    logger.warning(f"❌ ast_analyzer tool not available: {e}")
    OriginalASTAnalyzer = None


class ASTAnalyzerTool:
    """
    Wrapper for AST Analyzer tool

    Analyzes Python code structure, functions, classes, complexity.

    Competency required: JUNIOR

    Example:
        ```python
        tool = ASTAnalyzerTool()
        analysis = await tool.analyze_project()
        print(f"Total functions: {analysis['total_functions']}")
        ```
    """

    def __init__(self):
        """Initialize AST Analyzer tool"""
        self.available = TOOL_AVAILABLE
        self.name = "ast_analyzer"
        self.description = "Analyzes Python code structure using AST"
        self.competency_required = "junior"

        if self.available:
            try:
                self.tool = OriginalASTAnalyzer()
                logger.info("ASTAnalyzerTool initialized")
            except Exception as e:
                logger.error(f"Failed to initialize ASTAnalyzer: {e}")
                self.available = False
                self.tool = None
        else:
            self.tool = None

    async def analyze_project(self, project_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze entire project codebase

        Args:
            project_path: Path to project (defaults to PROJECT_ROOT)

        Returns:
            Complete AST analysis

        Example:
            ```python
            analysis = await tool.analyze_project()
            print(f"Functions: {analysis['total_functions']}")
            print(f"Classes: {analysis['total_classes']}")
            ```
        """
        if not self.available:
            logger.warning("ast_analyzer tool not available")
            return {
                "total_functions": 0,
                "total_classes": 0,
                "error": "Tool not available"
            }

        try:
            if not project_path:
                project_path = settings.PROJECT_ROOT

            results = self.tool.analyze_project(project_path)

            return {
                "total_functions": len(results.get("functions", [])),
                "total_classes": len(results.get("classes", [])),
                "total_imports": len(results.get("imports", [])),
                "functions": results.get("functions", []),
                "classes": results.get("classes", []),
                "imports": results.get("imports", []),
                "analyzed_at": results.get("analyzed_at")
            }

        except Exception as e:
            logger.error(f"AST analysis failed: {e}")
            return {"error": str(e)}

    async def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """
        Analyze single Python file

        Args:
            file_path: Path to Python file

        Returns:
            File AST analysis
        """
        if not self.available:
            return {"error": "Tool not available"}

        try:
            results = self.tool.analyze_file(file_path)
            return results

        except Exception as e:
            logger.error(f"File analysis failed: {e}")
            return {"error": str(e)}

    async def calculate_complexity_score(self) -> float:
        """
        Calculate overall code complexity score

        Returns:
            Complexity score 0-100 (lower is better)
        """
        if not self.available:
            return 0.0

        try:
            analysis = await self.analyze_project()

            # Simple heuristic: average function complexity
            functions = analysis.get("functions", [])
            if not functions:
                return 0.0

            total_complexity = sum(
                f.get("complexity", 1) for f in functions
            )
            avg_complexity = total_complexity / len(functions)

            # Normalize to 0-100 scale
            return min(100, avg_complexity * 10)

        except Exception as e:
            logger.error(f"Failed to calculate complexity: {e}")
            return 0.0
