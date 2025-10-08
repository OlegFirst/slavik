"""
Events Module for AI Foundation Learning & Knowledge System

Reactive event-driven learning system that subscribes to platform events
and triggers ML model updates, pattern detection, and knowledge base enrichment.
"""

from .subscribers import setup_event_subscribers

__all__ = ["setup_event_subscribers"]
