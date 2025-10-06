from setuptools import setup
import os

# Read README
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

# List all subpackages manually
packages = [
    "auth",
    "audit",
    "compliance",
    "governance",
    "ml",
    "schemas",
    "storage",
    "core",
    "ai",
    "case_library",
    "monitoring",
    "models",
    "workflows",
]

setup(
    name="workflow_intelligence",
    version="1.0.0",
    author="BCM Platform Team",
    description="Self-Learning Workflow Engine with Context-Aware AI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    py_modules=["__init__"],
    packages=packages,
    python_requires=">=3.9",
    install_requires=requirements,
)
