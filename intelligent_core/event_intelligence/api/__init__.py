"""
Event Intelligence API Package

REST API endpoints for Event Intelligence service
"""

from .routes import router, initialize_event_intelligence

__all__ = ['router', 'initialize_event_intelligence']
