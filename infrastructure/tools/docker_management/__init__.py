"""
Docker Management Module

Docker API wrapper for container lifecycle management:
start, stop, restart, logs, status, scaling.

Extracted from: intelligent-core/orchestrator_обьединенный/core/docker_manager.py
Date: 2025-10-04
"""

from .docker_manager import DockerManager, ContainerStatus

__all__ = ['DockerManager', 'ContainerStatus']
