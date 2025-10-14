"""
Data Import Endpoints

API endpoints for importing organizations from CSV, JSON, Excel
"""

import logging
import io
import json
import uuid
from typing import List, Dict, Any, Optional

from fastapi import APIRouter, HTTPException, Depends, Request, UploadFile, File
from pydantic import BaseModel

from storage import PostgreSQLStorage, RedisCache
from core.models.base import OrganizationType
from api.auth.dependencies import get_current_active_user

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================
# REQUEST/RESPONSE MODELS
# ============================================

class BulkImportRequest(BaseModel):
    """Bulk import request"""
    organizations: List[Dict[str, Any]]
    validate_only: bool = False


class ImportResponse(BaseModel):
    """Import response"""
    status: str
    total: int
    imported: int
    failed: int
    errors: List[Dict[str, Any]] = []
    imported_ids: List[str] = []


# ============================================
# DEPENDENCIES
# ============================================

def get_storage(request: Request) -> PostgreSQLStorage:
    """Get storage dependency"""
    return request.app.state.app_state.storage


def get_cache(request: Request) -> RedisCache:
    """Get cache dependency"""
    return request.app.state.app_state.cache


# ============================================
# AUTO FIELD MAPPING
# ============================================

FIELD_MAPPING_VARIANTS = {
    'name': ['name', 'company_name', 'organization_name', 'org_name', 'company'],
    'email': ['email', 'contact_email', 'email_address', 'contact'],
    'phone': ['phone', 'telephone', 'phone_number', 'tel', 'mobile'],
    'website': ['website', 'url', 'web', 'site', 'homepage'],
    'industry': ['industry', 'sector', 'industry_type', 'business_type'],
    'employee_count': ['employees', 'employee_count', 'staff', 'team_size', 'headcount'],
    'annual_revenue': ['revenue', 'annual_revenue', 'turnover', 'sales'],
    'annual_budget': ['budget', 'annual_budget', 'operating_budget'],
    'city': ['city', 'location', 'town'],
    'country': ['country', 'nation', 'country_name'],
    'street': ['street', 'address', 'street_address', 'address_line_1'],
    'zip': ['zip', 'postal_code', 'postcode', 'zip_code'],
    'state': ['state', 'province', 'region'],
    'vat': ['vat', 'tax_id', 'vat_number', 'registration_number'],
    'description': ['description', 'about', 'summary', 'overview'],
}


def auto_detect_columns(headers: List[str]) -> Dict[str, str]:
    """
    Auto-detect column mapping from headers
    
    Args:
        headers: CSV column headers
        
    Returns:
        Mapping of standard_field -> csv_column
    """
    mapping = {}
    
    headers_lower = [h.lower().strip() for h in headers]
    
    for standard_field, variants in FIELD_MAPPING_VARIANTS.items():
        for variant in variants:
            if variant in headers_lower:
                idx = headers_lower.index(variant)
                mapping[standard_field] = headers[idx]
                break
    
    logger.info(f"Auto-detected mapping: {mapping}")
    
    return mapping


def normalize_row(row: Dict[str, Any], mapping: Dict[str, str]) -> Dict[str, Any]:
    """
    Normalize row data using mapping
    
    Args:
        row: Raw row data
        mapping: Field mapping
        
    Returns:
        Normalized organization data
    """
    normalized = {}
    
    for standard_field, csv_column in mapping.items():
        value = row.get(csv_column)
        
        if value is not None and str(value).strip():
            # Type conversions
            if standard_field in ['employee_count']:
                try:
                    normalized[standard_field] = int(float(str(value).replace(',', '')))
                except:
                    pass
            elif standard_field in ['annual_revenue', 'annual_budget']:
                try:
                    normalized[standard_field] = float(str(value).replace(',', '').replace('$', ''))
                except:
                    pass
            else:
                normalized[standard_field] = str(value).strip()
    
    return normalized


# ============================================
# IMPORT ENDPOINTS
# ============================================

@router.post("/csv", response_model=ImportResponse)
async def import_csv(
    file: UploadFile = File(...),
    storage: PostgreSQLStorage = Depends(get_storage),
    current_user = Depends(get_current_active_user)
):
    """
    Import organizations from CSV file
    
    Supports auto-detection of columns
    """
    try:
        # Read CSV
        contents = await file.read()
        
        # Try different encodings
        try:
            content_str = contents.decode('utf-8')
        except:
            content_str = contents.decode('latin-1')
        
        # Parse CSV
        import csv
        csv_file = io.StringIO(content_str)
        reader = csv.DictReader(csv_file)
        
        headers = reader.fieldnames
        
        # Auto-detect columns
        mapping = auto_detect_columns(headers)
        
        if not mapping.get('name'):
            raise HTTPException(
                status_code=400,
                detail="Could not detect 'name' column. Please include organization name."
            )
        
        # Process rows
        imported = []
        failed = []
        errors = []
        
        for idx, row in enumerate(reader):
            try:
                # Normalize
                org_data = normalize_row(row, mapping)
                
                if not org_data.get('name'):
                    raise ValueError("Missing organization name")
                
                # Generate IDs
                org_id = f"org-{uuid.uuid4().hex[:12]}"
                twin_id = f"twin-{uuid.uuid4().hex[:12]}"
                
                # Prepare for database
                db_data = {
                    'id': org_id,
                    'twin_id': twin_id,
                    'name': org_data['name'],
                    'org_type': OrganizationType.BUSINESS,  # Default
                    'industry': org_data.get('industry'),
                    'employee_count': org_data.get('employee_count'),
                    'annual_revenue': org_data.get('annual_revenue'),
                    'annual_budget': org_data.get('annual_budget'),
                    'website': org_data.get('website'),
                    'email_domain': org_data.get('email'),
                    'description': org_data.get('description'),
                    'headquarters': {
                        'street': org_data.get('street'),
                        'city': org_data.get('city'),
                        'state': org_data.get('state'),
                        'zip': org_data.get('zip'),
                        'country': org_data.get('country')
                    }
                }
                
                # Create in database
                org_model = await storage.create_organization(db_data)
                imported.append(org_model.id)
                
                logger.info(f"Imported organization: {org_data['name']} ({org_model.id})")
                
            except Exception as e:
                failed.append(idx)
                errors.append({
                    'row': idx + 2,  # +2 for header and 0-based index
                    'error': str(e),
                    'data': dict(row)
                })
                logger.error(f"Failed to import row {idx}: {e}")
        
        return ImportResponse(
            status='success' if not failed else 'partial',
            total=len(imported) + len(failed),
            imported=len(imported),
            failed=len(failed),
            errors=errors[:10],  # Limit error details
            imported_ids=imported
        )
        
    except Exception as e:
        logger.error(f"CSV import failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/json", response_model=ImportResponse)
async def import_json(
    data: BulkImportRequest,
    storage: PostgreSQLStorage = Depends(get_storage),
    current_user = Depends(get_current_active_user)
):
    """
    Import organizations from JSON array
    
    Supports bulk creation with validation
    """
    try:
        if data.validate_only:
            # Validation mode
            valid_count = 0
            invalid_count = 0
            errors = []
            
            for idx, org_data in enumerate(data.organizations):
                if not org_data.get('name'):
                    invalid_count += 1
                    errors.append({
                        'index': idx,
                        'error': 'Missing required field: name'
                    })
                else:
                    valid_count += 1
            
            return ImportResponse(
                status='validated',
                total=len(data.organizations),
                imported=valid_count,
                failed=invalid_count,
                errors=errors
            )
        
        # Import mode
        imported = []
        failed = []
        errors = []
        
        for idx, org_data in enumerate(data.organizations):
            try:
                # Generate IDs if not provided
                if 'id' not in org_data:
                    org_data['id'] = f"org-{uuid.uuid4().hex[:12]}"
                if 'twin_id' not in org_data:
                    org_data['twin_id'] = f"twin-{uuid.uuid4().hex[:12]}"
                
                # Set defaults
                if 'org_type' not in org_data:
                    org_data['org_type'] = OrganizationType.BUSINESS
                
                # Create in database
                org_model = await storage.create_organization(org_data)
                imported.append(org_model.id)
                
                logger.info(f"Imported organization: {org_data.get('name')} ({org_model.id})")
                
            except Exception as e:
                failed.append(idx)
                errors.append({
                    'index': idx,
                    'error': str(e),
                    'name': org_data.get('name', 'Unknown')
                })
                logger.error(f"Failed to import organization {idx}: {e}")
        
        return ImportResponse(
            status='success' if not failed else 'partial',
            total=len(data.organizations),
            imported=len(imported),
            failed=len(failed),
            errors=errors[:10],
            imported_ids=imported
        )
        
    except Exception as e:
        logger.error(f"JSON import failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/template/csv")
async def get_csv_template():
    """
    Get CSV import template
    
    Returns example CSV structure
    """
    template = """name,industry,employee_count,annual_revenue,city,country,website
Acme Corp,Technology,500,10000000,San Francisco,USA,https://acme.com
Example Ltd,Finance,150,5000000,London,UK,https://example.com
Demo Inc,Healthcare,300,7500000,New York,USA,https://demo.com"""
    
    return {
        'format': 'csv',
        'template': template,
        'fields': {
            'required': ['name'],
            'optional': [
                'industry', 'employee_count', 'annual_revenue', 'annual_budget',
                'city', 'country', 'street', 'zip', 'state',
                'website', 'email', 'phone', 'description'
            ]
        }
    }


@router.get("/template/json")
async def get_json_template():
    """
    Get JSON import template
    
    Returns example JSON structure
    """
    template = [
        {
            "name": "Acme Corp",
            "org_type": "business",
            "industry": "Technology",
            "employee_count": 500,
            "annual_revenue": 10000000.0,
            "annual_budget": 5000000.0,
            "headquarters": {
                "city": "San Francisco",
                "country": "USA"
            },
            "website": "https://acme.com",
            "email_domain": "acme.com"
        },
        {
            "name": "Example Ltd",
            "org_type": "business",
            "industry": "Finance",
            "employee_count": 150,
            "annual_revenue": 5000000.0
        }
    ]
    
    return {
        'format': 'json',
        'template': template,
        'schema': {
            'required': ['name'],
            'optional': [
                'org_type', 'industry', 'employee_count', 'annual_revenue',
                'annual_budget', 'headquarters', 'website', 'email_domain',
                'description', 'metadata'
            ]
        }
    }
