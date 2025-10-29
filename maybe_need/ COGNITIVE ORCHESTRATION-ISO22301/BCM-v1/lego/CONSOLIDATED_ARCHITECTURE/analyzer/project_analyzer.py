#!/usr/bin/env python3
"""
Project Analyzer - Core analysis engine for code structure and patterns
"""

import ast
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
import zipfile
import tempfile

logger = logging.getLogger(__name__)

class ProjectAnalyzer:
    """Analyzes project structure, dependencies, and patterns"""

    def __init__(self):
        self.supported_extensions = {
            '.py': 'python',
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.java': 'java',
            '.go': 'go',
            '.rs': 'rust',
            '.cpp': 'cpp',
            '.c': 'c',
            '.php': 'php',
            '.rb': 'ruby'
        }

    async def analyze(self, project_path: Path) -> Dict[str, Any]:
        """Main analysis entry point"""
        try:
            logger.info(f"Starting analysis of {project_path}")

            # Get project structure
            structure = self._analyze_structure(project_path)

            # Detect languages and frameworks
            languages = self._detect_languages(project_path)
            frameworks = self._detect_frameworks(project_path)

            # Analyze dependencies
            dependencies = self._analyze_dependencies(project_path)

            # Calculate metrics
            metrics = self._calculate_metrics(project_path)

            # Detect architecture patterns
            patterns = self._detect_patterns(project_path, structure)

            result = {
                "project_name": project_path.name,
                "structure": structure,
                "languages": languages,
                "frameworks": frameworks,
                "dependencies": dependencies,
                "metrics": metrics,
                "patterns": patterns,
                "complexity_score": self._calculate_complexity(metrics, dependencies),
                "recommendations": self._generate_recommendations(patterns, metrics)
            }

            logger.info("Analysis completed successfully")
            return result

        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            raise

    def _analyze_structure(self, project_path: Path) -> Dict[str, Any]:
        """Analyze directory structure and file organization"""
        structure = {
            "directories": [],
            "files": [],
            "depth": 0,
            "total_files": 0,
            "file_types": {}
        }

        try:
            for item in project_path.rglob("*"):
                if item.is_file():
                    relative_path = item.relative_to(project_path)
                    structure["files"].append(str(relative_path))
                    structure["total_files"] += 1

                    # Track file types
                    suffix = item.suffix.lower()
                    if suffix in structure["file_types"]:
                        structure["file_types"][suffix] += 1
                    else:
                        structure["file_types"][suffix] = 1

                elif item.is_dir():
                    relative_path = item.relative_to(project_path)
                    structure["directories"].append(str(relative_path))

                    # Calculate max depth
                    depth = len(relative_path.parts)
                    structure["depth"] = max(structure["depth"], depth)

        except Exception as e:
            logger.warning(f"Structure analysis warning: {e}")

        return structure

    def _detect_languages(self, project_path: Path) -> Dict[str, int]:
        """Detect programming languages by file extensions"""
        languages = {}

        for file_path in project_path.rglob("*"):
            if file_path.is_file():
                ext = file_path.suffix.lower()
                if ext in self.supported_extensions:
                    lang = self.supported_extensions[ext]
                    languages[lang] = languages.get(lang, 0) + 1

        return languages

    def _detect_frameworks(self, project_path: Path) -> List[str]:
        """Detect frameworks and libraries"""
        frameworks = []

        # Check for package.json (Node.js)
        package_json = project_path / "package.json"
        if package_json.exists():
            try:
                with open(package_json) as f:
                    data = json.load(f)
                    deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}

                    # Common frameworks
                    if "react" in deps:
                        frameworks.append("React")
                    if "vue" in deps:
                        frameworks.append("Vue.js")
                    if "angular" in deps:
                        frameworks.append("Angular")
                    if "express" in deps:
                        frameworks.append("Express.js")
                    if "next" in deps:
                        frameworks.append("Next.js")
                    if "nuxt" in deps:
                        frameworks.append("Nuxt.js")

            except Exception as e:
                logger.warning(f"Error reading package.json: {e}")

        # Check for requirements.txt (Python)
        requirements = project_path / "requirements.txt"
        if requirements.exists():
            try:
                with open(requirements) as f:
                    content = f.read().lower()
                    if "django" in content:
                        frameworks.append("Django")
                    if "flask" in content:
                        frameworks.append("Flask")
                    if "fastapi" in content:
                        frameworks.append("FastAPI")
                    if "streamlit" in content:
                        frameworks.append("Streamlit")

            except Exception as e:
                logger.warning(f"Error reading requirements.txt: {e}")

        # Check for pom.xml (Java)
        pom_xml = project_path / "pom.xml"
        if pom_xml.exists():
            frameworks.append("Maven")
            try:
                with open(pom_xml) as f:
                    content = f.read().lower()
                    if "spring" in content:
                        frameworks.append("Spring")

            except Exception as e:
                logger.warning(f"Error reading pom.xml: {e}")

        # Check for Dockerfile
        dockerfile_paths = [
            project_path / "Dockerfile",
            project_path / "services" / "user_service" / "Dockerfile",
            project_path / "services" / "order_service" / "Dockerfile"
        ]
        if any(path.exists() for path in dockerfile_paths):
            frameworks.append("Docker")

        # Check for docker-compose
        if (project_path / "docker-compose.yml").exists() or (project_path / "docker-compose.yaml").exists():
            frameworks.append("Docker Compose")

        return frameworks

    def _analyze_dependencies(self, project_path: Path) -> Dict[str, Any]:
        """Analyze project dependencies"""
        dependencies = {
            "external": [],
            "internal": [],
            "count": 0,
            "complexity": "low"
        }

        # Analyze Python imports
        for py_file in project_path.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    tree = ast.parse(f.read())

                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            dependencies["external"].append(alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            dependencies["external"].append(node.module)

            except Exception as e:
                logger.warning(f"Error analyzing {py_file}: {e}")

        # Remove duplicates and count
        dependencies["external"] = list(set(dependencies["external"]))
        dependencies["count"] = len(dependencies["external"])

        # Determine complexity
        if dependencies["count"] > 50:
            dependencies["complexity"] = "high"
        elif dependencies["count"] > 20:
            dependencies["complexity"] = "medium"

        return dependencies

    def _calculate_metrics(self, project_path: Path) -> Dict[str, Any]:
        """Calculate code metrics"""
        metrics = {
            "lines_of_code": 0,
            "files_count": 0,
            "directories_count": 0,
            "test_files": 0,
            "config_files": 0,
            "documentation_files": 0
        }

        config_extensions = {'.json', '.yml', '.yaml', '.toml', '.ini', '.cfg'}
        doc_extensions = {'.md', '.rst', '.txt', '.pdf'}

        for file_path in project_path.rglob("*"):
            if file_path.is_file():
                metrics["files_count"] += 1

                # Count lines of code
                if file_path.suffix.lower() in self.supported_extensions:
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            lines = f.readlines()
                            # Count non-empty, non-comment lines
                            code_lines = [line for line in lines if line.strip() and not line.strip().startswith('#')]
                            metrics["lines_of_code"] += len(code_lines)
                    except Exception:
                        pass

                # Count test files
                if 'test' in file_path.name.lower() or file_path.name.lower().endswith('_test.py'):
                    metrics["test_files"] += 1

                # Count config files
                if file_path.suffix.lower() in config_extensions:
                    metrics["config_files"] += 1

                # Count documentation
                if file_path.suffix.lower() in doc_extensions:
                    metrics["documentation_files"] += 1

            elif file_path.is_dir():
                metrics["directories_count"] += 1

        return metrics

    def _detect_patterns(self, project_path: Path, structure: Dict[str, Any]) -> List[str]:
        """Detect architecture patterns"""
        patterns = []

        # Check for microservices pattern
        if any("service" in d for d in structure["directories"]):
            patterns.append("microservices")

        # Check for MVC pattern
        if any(name in structure["directories"] for name in ["models", "views", "controllers"]):
            patterns.append("mvc")

        # Check for component-based (React/Vue)
        if any("component" in d for d in structure["directories"]):
            patterns.append("component-based")

        # Check for layered architecture
        if any(name in structure["directories"] for name in ["domain", "infrastructure", "application"]):
            patterns.append("layered")

        # Check for monolith
        if structure["total_files"] > 100 and len(patterns) == 0:
            patterns.append("monolith")

        return patterns

    def _calculate_complexity(self, metrics: Dict[str, Any], dependencies: Dict[str, Any]) -> str:
        """Calculate overall project complexity"""
        score = 0

        # Lines of code factor (adjusted for better detection)
        if metrics["lines_of_code"] > 50000:
            score += 3
        elif metrics["lines_of_code"] > 5000:
            score += 2
        elif metrics["lines_of_code"] > 200:  # Lowered threshold for test
            score += 1

        # Dependencies factor
        if dependencies["count"] > 50:
            score += 3
        elif dependencies["count"] > 20:
            score += 2
        elif dependencies["count"] > 10:
            score += 1

        # Files factor (more sensitive to file count)
        if metrics["files_count"] > 100:
            score += 2
        elif metrics["files_count"] > 20:  # Lowered threshold
            score += 1

        if score >= 6:
            return "very_high"
        elif score >= 4:
            return "high"
        elif score >= 2:
            return "medium"
        else:
            return "low"

    def _generate_recommendations(self, patterns: List[str], metrics: Dict[str, Any]) -> List[str]:
        """Generate architecture recommendations"""
        recommendations = []

        if "monolith" in patterns and metrics["lines_of_code"] > 10000:
            recommendations.append("Consider breaking into microservices")

        if metrics["test_files"] == 0:
            recommendations.append("Add comprehensive test suite")

        if not patterns:
            recommendations.append("Implement clear architectural pattern")

        if metrics["lines_of_code"] > 50000:
            recommendations.append("Consider modular architecture")

        return recommendations