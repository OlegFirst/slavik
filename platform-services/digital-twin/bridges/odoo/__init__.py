"""
Odoo Bridge

Real-time bidirectional sync with Odoo ERP
"""

from .bridge import OdooBridge
from .sync import OdooSyncManager

__all__ = ["OdooBridge", "OdooSyncManager"]
