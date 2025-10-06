"""
Odoo Sync Manager

Manages automated sync between Odoo and Digital Twin
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime

from storage import PostgreSQLStorage, RedisCache
from .bridge import OdooBridge

logger = logging.getLogger(__name__)


class OdooSyncManager:
    """
    Odoo Sync Manager
    
    Orchestrates bidirectional sync between Odoo and Digital Twin
    """
    
    def __init__(
        self,
        odoo_bridge: OdooBridge,
        storage: PostgreSQLStorage,
        cache: RedisCache,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize Sync Manager
        
        Args:
            odoo_bridge: Odoo bridge instance
            storage: PostgreSQL storage
            cache: Redis cache
            config: Sync configuration
        """
        self.bridge = odoo_bridge
        self.storage = storage
        self.cache = cache
        self.config = config or {}
        
        # Sync settings
        self.sync_interval = self.config.get('sync_interval', 300)  # 5 minutes
        self.batch_size = self.config.get('batch_size', 100)
        self.auto_sync = self.config.get('auto_sync', False)
        
        # Sync state
        self.is_syncing = False
        self.last_sync = None
        
        # Statistics
        self.stats = {
            'total_syncs': 0,
            'successful_syncs': 0,
            'failed_syncs': 0,
            'organizations_synced': 0,
            'conflicts_resolved': 0
        }
        
        logger.info("Odoo Sync Manager initialized")
    
    # ============================================
    # FULL SYNC (Odoo -> Digital Twin)
    # ============================================
    
    async def sync_from_odoo(
        self,
        full_sync: bool = False
    ) -> Dict[str, Any]:
        """
        Sync organizations from Odoo to Digital Twin
        
        Args:
            full_sync: If True, sync all; if False, sync only changed
            
        Returns:
            Sync result summary
        """
        if self.is_syncing:
            logger.warning("Sync already in progress")
            return {'status': 'error', 'message': 'Sync already in progress'}
        
        self.is_syncing = True
        sync_start = datetime.utcnow()
        
        try:
            logger.info(f"Starting sync from Odoo (full_sync={full_sync})")
            
            # Pull organizations from Odoo
            odoo_orgs = await self.bridge.pull_organizations(
                domain=[['is_company', '=', True]],
                limit=self.batch_size if not full_sync else 1000
            )
            
            synced_count = 0
            created_count = 0
            updated_count = 0
            errors = []
            
            for odoo_org in odoo_orgs:
                try:
                    # Check if organization exists in Digital Twin
                    existing = await self._find_existing_organization(odoo_org)
                    
                    if existing:
                        # Update existing
                        await self.storage.update_organization(
                            existing.id,
                            odoo_org
                        )
                        updated_count += 1
                        
                        # Invalidate cache
                        await self.cache.invalidate_organization(existing.id)
                    else:
                        # Create new
                        org_data = self._prepare_organization_data(odoo_org)
                        await self.storage.create_organization(org_data)
                        created_count += 1
                    
                    synced_count += 1
                    
                except Exception as e:
                    logger.error(f"Failed to sync organization: {e}")
                    errors.append(str(e))
            
            # Update stats
            self.stats['total_syncs'] += 1
            self.stats['successful_syncs'] += 1
            self.stats['organizations_synced'] += synced_count
            
            # Update last sync time
            self.last_sync = sync_start
            
            duration = (datetime.utcnow() - sync_start).total_seconds()
            
            result = {
                'status': 'success',
                'synced': synced_count,
                'created': created_count,
                'updated': updated_count,
                'errors': len(errors),
                'error_details': errors[:10] if errors else [],
                'duration_seconds': duration,
                'started_at': sync_start.isoformat(),
                'completed_at': datetime.utcnow().isoformat()
            }
            
            logger.info(
                f"Sync from Odoo completed: {synced_count} synced "
                f"({created_count} created, {updated_count} updated) "
                f"in {duration:.2f}s"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Sync from Odoo failed: {e}", exc_info=True)
            self.stats['failed_syncs'] += 1
            
            return {
                'status': 'error',
                'message': str(e),
                'started_at': sync_start.isoformat(),
                'completed_at': datetime.utcnow().isoformat()
            }
            
        finally:
            self.is_syncing = False
    
    # ============================================
    # PUSH TO ODOO (Digital Twin -> Odoo)
    # ============================================
    
    async def sync_to_odoo(
        self,
        twin_id: str,
        force: bool = False
    ) -> Dict[str, Any]:
        """
        Sync organization from Digital Twin to Odoo
        
        Args:
            twin_id: Digital Twin ID
            force: If True, push even if unchanged
            
        Returns:
            Sync result
        """
        try:
            # Get organization from Digital Twin
            org = await self.storage.get_organization(twin_id=twin_id)
            
            if not org:
                return {
                    'status': 'error',
                    'message': f'Organization not found: {twin_id}'
                }
            
            # Check if already synced with Odoo
            odoo_id = await self._get_odoo_id(twin_id)
            
            # Convert organization to dict
            org_data = {
                'name': org.name,
                'email': org.email_domain,
                'phone': org.contacts.get('phone') if org.contacts else None,
                'website': org.website,
                'employee_count': org.employee_count,
                'annual_revenue': org.annual_revenue,
                'industry': org.industry
            }
            
            # Push to Odoo
            result_id = await self.bridge.push_organization(org_data, odoo_id)
            
            if result_id:
                # Save Odoo ID mapping
                await self._save_odoo_id(twin_id, result_id)
                
                return {
                    'status': 'success',
                    'twin_id': twin_id,
                    'odoo_id': result_id,
                    'action': 'updated' if odoo_id else 'created'
                }
            else:
                return {
                    'status': 'error',
                    'message': 'Failed to push to Odoo'
                }
                
        except Exception as e:
            logger.error(f"Failed to sync to Odoo: {e}", exc_info=True)
            return {
                'status': 'error',
                'message': str(e)
            }
    
    # ============================================
    # AUTO SYNC
    # ============================================
    
    async def start_auto_sync(self) -> None:
        """
        Start automatic sync loop
        
        Runs continuous sync in background
        """
        if not self.auto_sync:
            logger.warning("Auto sync is disabled in config")
            return
        
        logger.info(f"Starting auto sync (interval: {self.sync_interval}s)")
        
        while self.auto_sync:
            try:
                # Wait for interval
                await asyncio.sleep(self.sync_interval)
                
                # Perform sync
                result = await self.sync_from_odoo(full_sync=False)
                
                logger.info(f"Auto sync completed: {result.get('synced', 0)} organizations")
                
            except Exception as e:
                logger.error(f"Auto sync error: {e}", exc_info=True)
    
    def stop_auto_sync(self) -> None:
        """Stop automatic sync"""
        self.auto_sync = False
        logger.info("Auto sync stopped")
    
    # ============================================
    # HELPERS
    # ============================================
    
    async def _find_existing_organization(
        self,
        odoo_org: Dict[str, Any]
    ) -> Optional[Any]:
        """
        Find existing organization in Digital Twin
        
        Args:
            odoo_org: Odoo organization data
            
        Returns:
            Existing organization model or None
        """
        # Try to find by source ID
        odoo_id = odoo_org.get('_source_id')
        
        if odoo_id:
            # Search for organization with this Odoo ID
            # TODO: Implement source_id search in storage
            pass
        
        # Try to find by name
        name = odoo_org.get('name')
        if name:
            orgs = await self.storage.list_organizations(
                filters={'name_contains': name},
                limit=1
            )
            if orgs:
                return orgs[0]
        
        return None
    
    def _prepare_organization_data(
        self,
        odoo_org: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Prepare organization data for creation
        
        Args:
            odoo_org: Odoo organization data
            
        Returns:
            Prepared organization data
        """
        import uuid
        
        # Generate IDs
        org_id = f"org-{uuid.uuid4().hex[:12]}"
        twin_id = f"twin-{uuid.uuid4().hex[:12]}"
        
        return {
            'id': org_id,
            'twin_id': twin_id,
            'name': odoo_org.get('name', 'Unknown'),
            'org_type': 'business',
            'email_domain': odoo_org.get('email'),
            'website': odoo_org.get('website'),
            'employee_count': odoo_org.get('employee_count'),
            'annual_revenue': odoo_org.get('annual_revenue'),
            'industry': odoo_org.get('industry'),
            'headquarters': {
                'street': odoo_org.get('street'),
                'city': odoo_org.get('city'),
                'zip': odoo_org.get('zip'),
                'country': odoo_org.get('country')
            },
            'source_ids': {
                'odoo': odoo_org.get('_source_id')
            }
        }
    
    async def _get_odoo_id(self, twin_id: str) -> Optional[int]:
        """Get Odoo ID for twin"""
        # Try cache first
        cached = await self.cache.get_hash_field('odoo_mapping', twin_id)
        if cached:
            return int(cached)
        
        # Get from database
        org = await self.storage.get_organization(twin_id=twin_id)
        if org and org.source_ids:
            odoo_id = org.source_ids.get('odoo')
            if odoo_id:
                # Cache it
                await self.cache.set_hash_field('odoo_mapping', twin_id, odoo_id)
                return int(odoo_id)
        
        return None
    
    async def _save_odoo_id(self, twin_id: str, odoo_id: int) -> None:
        """Save Odoo ID mapping"""
        # Save to cache
        await self.cache.set_hash_field('odoo_mapping', twin_id, odoo_id)
        
        # Update organization
        org = await self.storage.get_organization(twin_id=twin_id)
        if org:
            source_ids = org.source_ids or {}
            source_ids['odoo'] = odoo_id
            await self.storage.update_organization(org.id, {'source_ids': source_ids})
    
    # ============================================
    # STATUS & STATISTICS
    # ============================================
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get sync statistics
        
        Returns:
            Statistics dictionary
        """
        return {
            **self.stats,
            'is_syncing': self.is_syncing,
            'last_sync': self.last_sync.isoformat() if self.last_sync else None,
            'auto_sync_enabled': self.auto_sync,
            'sync_interval': self.sync_interval
        }
