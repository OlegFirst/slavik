#!/usr/bin/env python3
"""
Setup script for In-Project Orchestration Service
Allows installation as a package into user projects
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent.parent / "README.md"
long_description = readme_file.read_text(encoding='utf-8') if readme_file.exists() else ""

setup(
    name="universal-orchestrator",
    version="1.0.0",
    description="AI-Enhanced Universal Orchestration Platform - Embeddable Service",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="AI-Enhanced Development Team",
    author_email="dev@orchestrator.ai",
    url="https://github.com/orchestrator/universal-platform",
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=[
        "asyncio",
        "httpx>=0.24.0",
        "aiofiles>=0.8.0",
        "pydantic>=1.10.0",
        "typing-extensions>=4.0.0",
        "pathlib",
        "tempfile",
        "shutil"
    ],
    extras_require={
        "ai": [
            "anthropic>=0.3.0",
            "openai>=0.27.0"
        ],
        "visualization": [
            "mermaid-py>=0.1.0",
            "pillow>=9.0.0"
        ],
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.20.0",
            "black>=22.0.0",
            "flake8>=5.0.0"
        ]
    },
    entry_points={
        "console_scripts": [
            "orchestrator=orchestrator:main",
            "uop-analyze=orchestrator:analyze_project",
            "uop-generate=orchestrator:generate_architecture"
        ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
    keywords="ai, code-generation, architecture, orchestration, automation"
)