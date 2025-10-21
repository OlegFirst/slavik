from setuptools import setup, find_packages
import os

# Read README
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

# Use find_packages to automatically discover all packages
# Exclude test directories and examples
packages = find_packages(
    exclude=[
        "tests",
        "tests.*",
        "test_processes",
        "test_processes.*",
        "examples",
        "examples.*",
        "docs",
        "docs.*",
        "temporal_sample",  # Sample code, not production
        "temporal_sample.*"
    ]
)

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
