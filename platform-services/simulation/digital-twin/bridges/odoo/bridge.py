"""
Odoo Bridge

Bidirectional sync between Digital Twin and Odoo ERP
"""

import logging
import xmlrpc.client
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class OdooBridge:
    """
    Odoo Bridge
    
    Manages bidirectional data sync with Odoo ERP system
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Odoo Bridge
        
        Args:
            config: Odoo connection configuration
        """
        self.config = config
        
        # Connection details
        self.url = config.get('url', 'http://localhost:8069')
        self.db = config.get('database', 'odoo')
        self.username = config.get('username', 'admin')
        self.password = config.get('password', 'admin')
        
        # XML-RPC clients
        self.common = None
        self.models = None
        self.uid = None
        
        # Field mappings (Digital Twin -> Odoo)
        self.field_mappings = {
            'organization': {
                'name': 'name',
                'email': 'email',
                'phone': 'phone',
                'website': 'website',
                'street': 'street',
                'city': 'city',
                'zip': 'zip',
                'country': 'country_id',
                'state': 'state_id',
                'vat': 'vat',
                'employee_count': 'x_employee_count',  # Custom field
                'annual_revenue': 'x_annual_revenue',   # Custom field
                'industry': 'industry_id',
            }
        }
        
        # Statistics
        self.stats = {
            'syncs_performed': 0,
            'records_pushed': 0,
            'records_pulled': 0,
            'errors': 0
        }
        
        logger.info(f"Odoo Bridge initialized for {self.url}")
    
    async def connect(self) -> bool:
        """
        Connect to Odoo
        
        Returns:
            True if connected successfully
        """
        try:
            # Common endpoint
            self.common = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/common')
            
            # Authenticate
            self.uid = self.common.authenticate(
                self.db,
                self.username,
                self.password,
                {}
            )
            
            if not self.uid:
                logger.error("Odoo authentication failed")
                return False
            
            # Models endpoint
            self.models = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/object')
            
            # Test connection
            version = self.common.version()
            logger.info(f"Connected to Odoo {version['server_version']} - UID: {self.uid}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Odoo: {e}", exc_info=True)
            self.stats['errors'] += 1
            return False
    
    async def disconnect(self) -> None:
        """Disconnect from Odoo"""
        self.common = None
        self.models = None
        self.uid = None
        logger.info("Disconnected from Odoo")
    
    # ============================================
    # PULL FROM ODOO (Odoo -> Digital Twin)
    # ============================================
    
    async def pull_organization(self, odoo_id: int) -> Optional[Dict[str, Any]]:
        """
        Pull organization from Odoo
        
        Args:
            odoo_id: Odoo partner ID
            
        Returns:
            Organization data or None
        """
        if not self.uid:
            await self.connect()
        
        try:
            # Search for partner
            partner = self.models.execute_kw(
                self.db, self.uid, self.password,
                'res.partner', 'read',
                [[odoo_id]],
                {'fields': list(self.field_mappings['organization'].values())}
            )
            
            if not partner:
                logger.warning(f"Partner {odoo_id} not found in Odoo")
                return None
            
            partner_data = partner[0]
            
            # Map to Digital Twin format
            org_data = self._map_odoo_to_dt(partner_data)
            
            # Add metadata
            org_data['_source'] = 'odoo'
            org_data['_source_id'] = odoo_id
            org_data['_synced_at'] = datetime.utcnow().isoformat()
            
            self.stats['records_pulled'] += 1
            logger.info(f"Pulled organization from Odoo: {odoo_id}")
            
            return org_data
            
        except Exception as e:
            logger.error(f"Failed to pull organization from Odoo: {e}", exc_info=True)
            self.stats['errors'] += 1
            return None
    
    async def pull_organizations(
        self,
        domain: Optional[List] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Pull multiple organizations from Odoo
        
        Args:
            domain: Odoo search domain
            limit: Max records to pull
            
        Returns:
            List of organization data
        """
        if not self.uid:
            await self.connect()
        
        try:
            # Default domain: companies only
            if domain is None:
                domain = [['is_company', '=', True]]
            
            # Search for partners
            partner_ids = self.models.execute_kw(
                self.db, self.uid, self.password,
                'res.partner', 'search',
                [domain],
                {'limit': limit}
            )
            
            if not partner_ids:
                logger.info("No partners found in Odoo")
                return []
            
            # Read partners
            partners = self.models.execute_kw(
                self.db, self.uid, self.password,
                'res.partner', 'read',
                [partner_ids],
                {'fields': list(self.field_mappings['organization'].values())}
            )
            
            # Map to Digital Twin format
            organizations = []
            for partner in partners:
                org_data = self._map_odoo_to_dt(partner)
                org_data['_source'] = 'odoo'
                org_data['_source_id'] = partner['id']
                org_data['_synced_at'] = datetime.utcnow().isoformat()
                organizations.append(org_data)
            
            self.stats['records_pulled'] += len(organizations)
            logger.info(f"Pulled {len(organizations)} organizations from Odoo")
            
            return organizations
            
        except Exception as e:
            logger.error(f"Failed to pull organizations from Odoo: {e}", exc_info=True)
            self.stats['errors'] += 1
            return []
    
    # ============================================
    # PUSH TO ODOO (Digital Twin -> Odoo)
    # ============================================
    
    async def push_organization(
        self,
        org_data: Dict[str, Any],
        odoo_id: Optional[int] = None
    ) -> Optional[int]:
        """
        Push organization to Odoo
        
        Args:
            org_data: Digital Twin organization data
            odoo_id: Existing Odoo ID (for update) or None (for create)
            
        Returns:
            Odoo partner ID or None
        """
        if not self.uid:
            await self.connect()
        
        try:
            # Map to Odoo format
            odoo_data = self._map_dt_to_odoo(org_data)
            
            if odoo_id:
                # Update existing partner
                self.models.execute_kw(
                    self.db, self.uid, self.password,
                    'res.partner', 'write',
                    [[odoo_id], odoo_data]
                )
                logger.info(f"Updated organization in Odoo: {odoo_id}")
                return odoo_id
            else:
                # Create new partner
                new_id = self.models.execute_kw(
                    self.db, self.uid, self.password,
                    'res.partner', 'create',
                    [odoo_data]
                )
                logger.info(f"Created organization in Odoo: {new_id}")
                self.stats['records_pushed'] += 1
                return new_id
                
        except Exception as e:
            logger.error(f"Failed to push organization to Odoo: {e}", exc_info=True)
            self.stats['errors'] += 1
            return None
    
    # ============================================
    # FIELD MAPPING
    # ============================================
    
    def _map_odoo_to_dt(self, odoo_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Map Odoo data to Digital Twin format
        
        Args:
            odoo_data: Odoo partner data
            
        Returns:
            Digital Twin organization data
        """
        dt_data = {}
        
        # Reverse mapping
        reverse_mapping = {v: k for k, v in self.field_mappings['organization'].items()}
        
        for odoo_field, value in odoo_data.items():
            if odoo_field in reverse_mapping:
                dt_field = reverse_mapping[odoo_field]
                
                # Handle many2one fields (tuples)
                if isinstance(value, (list, tuple)) and len(value) == 2:
                    dt_data[dt_field] = value[1]  # Get name from (id, name)
                else:
                    dt_data[dt_field] = value
        
        return dt_data
    
    def _map_dt_to_odoo(self, dt_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Map Digital Twin data to Odoo format
        
        Args:
            dt_data: Digital Twin organization data
            
        Returns:
            Odoo partner data
        """
        odoo_data = {}
        
        for dt_field, value in dt_data.items():
            if dt_field in self.field_mappings['organization']:
                odoo_field = self.field_mappings['organization'][dt_field]
                
                # Skip None values
                if value is not None:
                    odoo_data[odoo_field] = value
        
        return odoo_data
    
    # ============================================
    # SYNC STATUS
    # ============================================
    
    async def get_sync_status(self, twin_id: str) -> Dict[str, Any]:
        """
        Get sync status for digital twin
        
        Args:
            twin_id: Digital Twin ID
            
        Returns:
            Sync status information
        """
        # TODO: Implement sync tracking in database
        return {
            'twin_id': twin_id,
            'last_sync': None,
            'sync_status': 'not_synced',
            'odoo_id': None
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get bridge statistics
        
        Returns:
            Statistics dictionary
        """
        return {
            **self.stats,
            'connected': self.uid is not None,
            'odoo_url': self.url,
            'odoo_db': self.db
        }
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.disconnect()
