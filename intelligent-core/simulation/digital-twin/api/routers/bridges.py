"""
Bridge Endpoints

API endpoints for external system bridges (Odoo, Salesforce)
"""

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel

from bridges.odoo import OdooBridge, OdooSyncManager

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================
# REQUEST/RESPONSE MODELS
# ============================================

class SyncRequest(BaseModel):
    """Sync request"""
    full_sync: bool = False


class PushRequest(BaseModel):
    """Push to external system request"""
    twin_id: str
    force: bool = False


# ============================================
# DEPENDENCIES
# ============================================

def get_storage(request: Request):
    """Get storage dependency"""
    return request.app.state.app_state.storage


def get_cache(request: Request):
    """Get cache dependency"""
    return request.app.state.app_state.cache


# ============================================
# ODOO BRIDGE ENDPOINTS
# ============================================

@router.post("/odoo/sync")
async def sync_from_odoo(
    sync_request: SyncRequest,
    storage = Depends(get_storage),
    cache = Depends(get_cache)
):
    """
    Sync organizations from Odoo to Digital Twin
    
    Pulls data from Odoo and updates Digital Twin
    """
    try:
        # TODO: Get Odoo config from environment or database
        odoo_config = {
            'url': 'http://localhost:8069',
            'database': 'odoo',
            'username': 'admin',
            'password': 'admin'
        }
        
        # Create bridge and sync manager
        async with OdooBridge(odoo_config) as bridge:
            sync_manager = OdooSyncManager(bridge, storage, cache)
            
            # Perform sync
            result = await sync_manager.sync_from_odoo(
                full_sync=sync_request.full_sync
            )
            
            return result
            
    except Exception as e:
        logger.error(f"Sync from Odoo failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/odoo/push")
async def push_to_odoo(
    push_request: PushRequest,
    storage = Depends(get_storage),
    cache = Depends(get_cache)
):
    """
    Push organization from Digital Twin to Odoo
    
    Syncs Digital Twin data to Odoo ERP
    """
    try:
        # TODO: Get Odoo config
        odoo_config = {
            'url': 'http://localhost:8069',
            'database': 'odoo',
            'username': 'admin',
            'password': 'admin'
        }
        
        async with OdooBridge(odoo_config) as bridge:
            sync_manager = OdooSyncManager(bridge, storage, cache)
            
            # Push to Odoo
            result = await sync_manager.sync_to_odoo(
                twin_id=push_request.twin_id,
                force=push_request.force
            )
            
            return result
            
    except Exception as e:
        logger.error(f"Push to Odoo failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/odoo/status")
async def get_odoo_status():
    """
    Get Odoo bridge status
    
    Returns connection and sync status
    """
    try:
        # TODO: Get Odoo config
        odoo_config = {
            'url': 'http://localhost:8069',
            'database': 'odoo',
            'username': 'admin',
            'password': 'admin'
        }
        
        async with OdooBridge(odoo_config) as bridge:
            stats = bridge.get_statistics()
            
            return {
                'bridge': 'odoo',
                'status': 'connected' if stats['connected'] else 'disconnected',
                'statistics': stats
            }
            
    except Exception as e:
        logger.error(f"Failed to get Odoo status: {e}")
        return {
            'bridge': 'odoo',
            'status': 'error',
            'error': str(e)
        }


@router.get("/odoo/organization/{odoo_id}")
async def pull_odoo_organization(odoo_id: int):
    """
    Pull single organization from Odoo
    
    Retrieves organization data from Odoo by ID
    """
    try:
        odoo_config = {
            'url': 'http://localhost:8069',
            'database': 'odoo',
            'username': 'admin',
            'password': 'admin'
        }
        
        async with OdooBridge(odoo_config) as bridge:
            org_data = await bridge.pull_organization(odoo_id)
            
            if not org_data:
                raise HTTPException(
                    status_code=404,
                    detail=f"Organization {odoo_id} not found in Odoo"
                )
            
            return org_data
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to pull organization from Odoo: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# SALESFORCE BRIDGE ENDPOINTS (TODO)
# ============================================

@router.get("/salesforce/status")
async def get_salesforce_status():
    """Get Salesforce bridge status (TODO)"""
    return {
        'bridge': 'salesforce',
        'status': 'not_implemented',
        'message': 'Salesforce bridge coming soon'
    }
