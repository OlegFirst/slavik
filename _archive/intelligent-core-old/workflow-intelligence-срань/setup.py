"""
Workflow Intelligence Engine - Setup Configuration
"""

from setuptools import setup, find_packages

setup(
    name="workflow-intelligence",
    version="1.0.0",
    description="Self-Learning Workflow Engine with Context-Aware AI",
    author="BCM Platform Team",
    python_requires=">=3.9",
    packages=find_packages(exclude=["tests*", "examples*", "docs*"]),
    install_requires=[
        # Core
        "pydantic>=2.0.0",
        "python-dateutil>=2.8.0",

        # Database (PostgreSQL + Vector DB)
        "asyncpg>=0.28.0",
        "sqlalchemy>=2.0.0",
        "pgvector>=0.2.0",

        # ML & AI
        "scikit-learn>=1.3.0",
        "numpy>=1.24.0",
        "pandas>=2.0.0",
        "joblib>=1.3.0",

        # LLM Clients
        "anthropic>=0.18.0",
        "openai>=1.0.0",

        # Caching & Events
        "redis>=5.0.0",
        "aioredis>=2.0.0",

        # Utilities
        "pyyaml>=6.0.0",
        "python-dotenv>=1.0.0",
        "structlog>=23.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.1.0",
            "faker>=19.0.0",
            "black>=23.0.0",
            "ruff>=0.1.0",
            "mypy>=1.5.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "workflow-intelligence=workflow_intelligence.cli:main",
        ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
