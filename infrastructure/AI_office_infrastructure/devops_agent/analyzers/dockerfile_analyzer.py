#!/usr/bin/env python3
"""
Dockerfile Analyzer & Generator

Analyzes services and generates optimized Dockerfiles
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class ServiceMetadata:
    """Service metadata for Dockerfile generation"""
    name: str
    path: str
    language: str  # 'python', 'node', 'go', etc.
    framework: Optional[str] = None  # 'fastapi', 'flask', 'express', etc.
    port: Optional[int] = None
    dependencies_file: Optional[str] = None
    has_dockerfile: bool = False


class DockerfileAnalyzer:
    """Analyzes services and generates Dockerfiles"""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.services: List[ServiceMetadata] = []
        self.services_count = 0

    def find_services(self) -> List[ServiceMetadata]:
        """Find all services in the project"""
        logger.info(" Scanning for services...")

        # Scan common service directories
        service_dirs = [
            self.project_root / "intelligent-core",
            self.project_root / "infrastructure",
            self.project_root / "platform-services"
        ]

        for base_dir in service_dirs:
            if not base_dir.exists():
                continue

            # Find Python services (with main.py or __main__.py)
            for main_file in base_dir.rglob("main.py"):
                if "venv" in str(main_file) or "node_modules" in str(main_file):
                    continue

                service_metadata = self._analyze_service(main_file.parent)
                if service_metadata:
                    self.services.append(service_metadata)
                    self.services_count += 1

        logger.info(f" Found {len(self.services)} services")
        return self.services

    def _analyze_service(self, service_path: Path) -> Optional[ServiceMetadata]:
        """Analyze a single service"""

        # Detect language
        if (service_path / "requirements.txt").exists():
            language = "python"
            deps_file = "requirements.txt"
        elif (service_path / "package.json").exists():
            language = "node"
            deps_file = "package.json"
        elif (service_path / "go.mod").exists():
            language = "go"
            deps_file = "go.mod"
        else:
            return None

        # Detect framework
        framework = self._detect_framework(service_path, language)

        # Detect port
        port = self._detect_port(service_path)

        # Check for existing Dockerfile
        has_dockerfile = (service_path / "Dockerfile").exists()

        return ServiceMetadata(
            name=service_path.name,
            path=str(service_path.relative_to(self.project_root)),
            language=language,
            framework=framework,
            port=port,
            dependencies_file=deps_file,
            has_dockerfile=has_dockerfile
        )

    def _detect_framework(self, service_path: Path, language: str) -> Optional[str]:
        """Detect framework used"""
        if language == "python":
            main_file = service_path / "main.py"
            if main_file.exists():
                content = main_file.read_text()
                if "FastAPI" in content or "from fastapi" in content:
                    return "fastapi"
                elif "Flask" in content or "from flask" in content:
                    return "flask"

        elif language == "node":
            package_json = service_path / "package.json"
            if package_json.exists():
                try:
                    data = json.loads(package_json.read_text())
                    deps = data.get("dependencies", {})
                    if "express" in deps:
                        return "express"
                    elif "next" in deps:
                        return "nextjs"
                except:
                    pass

        return None

    def _detect_port(self, service_path: Path) -> Optional[int]:
        """Detect service port"""
        main_file = service_path / "main.py"
        if main_file.exists():
            content = main_file.read_text()
            # Look for port = XXXX or uvicorn.run(..., port=XXXX)
            import re
            port_match = re.search(r'port["\s]*[:=]["\s]*(\d+)', content)
            if port_match:
                return int(port_match.group(1))

        return None

    def find_missing_dockerfiles(self) -> List[ServiceMetadata]:
        """Find services without Dockerfiles"""
        self.find_services()
        missing = [s for s in self.services if not s.has_dockerfile]
        logger.info(f"️  {len(missing)} services without Dockerfiles")
        return missing

    def analyze_existing(self) -> List[Dict]:
        """Analyze existing Dockerfiles for issues"""
        issues = []

        for service in self.services:
            if not service.has_dockerfile:
                continue

            dockerfile_path = self.project_root / service.path / "Dockerfile"
            content = dockerfile_path.read_text()

            # Check for common issues
            if "COPY . ." in content and ".dockerignore" not in os.listdir(dockerfile_path.parent):
                issues.append({
                    "service": service.name,
                    "issue": "missing_.dockerignore",
                    "severity": "warning",
                    "recommendation": "Add .dockerignore to exclude unnecessary files"
                })

            if "pip install" in content and "--no-cache-dir" not in content:
                issues.append({
                    "service": service.name,
                    "issue": "missing_no_cache_dir",
                    "severity": "info",
                    "recommendation": "Use 'pip install --no-cache-dir' to reduce image size"
                })

        return issues

    def generate_dockerfile(self, service: ServiceMetadata) -> str:
        """Generate optimized Dockerfile for service"""

        if service.language == "python":
            return self._generate_python_dockerfile(service)
        elif service.language == "node":
            return self._generate_node_dockerfile(service)
        elif service.language == "go":
            return self._generate_go_dockerfile(service)

        return ""

    def _generate_python_dockerfile(self, service: ServiceMetadata) -> str:
        """Generate Python Dockerfile"""
        port = service.port or 8000

        return f"""# Auto-generated by DevOps Agent
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY {service.dependencies_file} .
RUN pip install --no-cache-dir -r {service.dependencies_file}

# Copy application
COPY . .

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \\
    CMD python -c "import requests; requests.get('http://localhost:{port}/health')"

# Expose port
EXPOSE {port}

# Run application
{"CMD" if service.framework == "fastapi" else "ENTRYPOINT"} ["python", "main.py"]
"""

    def _generate_node_dockerfile(self, service: ServiceMetadata) -> str:
        """Generate Node.js Dockerfile"""
        port = service.port or 3000

        return f"""# Auto-generated by DevOps Agent
FROM node:18-alpine

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci --only=production

# Copy application
COPY . .

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \\
    CMD wget --no-verbose --tries=1 --spider http://localhost:{port}/health || exit 1

# Expose port
EXPOSE {port}

# Run application
CMD ["npm", "start"]
"""

    def _generate_go_dockerfile(self, service: ServiceMetadata) -> str:
        """Generate Go Dockerfile (multi-stage)"""
        port = service.port or 8080

        return f"""# Auto-generated by DevOps Agent
# Build stage
FROM golang:1.21-alpine AS builder

WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download

COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o main .

# Runtime stage
FROM alpine:latest

RUN apk --no-cache add ca-certificates
WORKDIR /root/

COPY --from=builder /app/main .

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \\
    CMD wget --no-verbose --tries=1 --spider http://localhost:{port}/health || exit 1

EXPOSE {port}

CMD ["./main"]
"""
