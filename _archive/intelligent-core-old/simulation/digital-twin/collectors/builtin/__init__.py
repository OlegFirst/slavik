"""
Built-in Data Collectors
"""

from .odoo_collector import OdooCollector
from .salesforce_collector import SalesforceCollector
from .hubspot_collector import HubSpotCollector
from .generic_rest_collector import GenericRESTCollector
from .csv_collector import CSVCollector
from .database_collector import DatabaseCollector

__all__ = [
    "OdooCollector",
    "SalesforceCollector",
    "HubSpotCollector",
    "GenericRESTCollector",
    "CSVCollector",
    "DatabaseCollector",
]
