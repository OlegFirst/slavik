"""
BCM Modules Health Tracking API
Monitors health and compliance contribution of all BCM platform services
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging
import aiohttp

from compliance.database.connection import get_db
from compliance.models.schemas import (
    ModuleHealthResponse,
    ModuleHealthSummary,
    ModuleRegistration
)
from compliance.config.settings import settings

logger = logging.getLogger(__name__)
router = APIRouter()


# Platform services registry
PLATFORM_SERVICES = {
    # BCM Core Services
    "bcm_risk_management": {
        "name": "Risk Management",
        "port": 8003,
        "health_endpoint": "/health",
        "iso_clauses": ["6.1", "8.2.3"],
        "bci_practice": "PP3",
        "compliance_contribution": 25.0,
        "description": "FAIR + Monte Carlo risk analysis"
    },
    "bcm_bia": {
        "name": "Business Impact Analysis",
        "port": 8004,
        "health_endpoint": "/health",
        "iso_clauses": ["8.2.2"],
        "bci_practice": "PP3",
        "compliance_contribution": 20.0,
        "description": "BIA engine with dependency mapping"
    },
    "bcm_plans": {
        "name": "BC Plans Management",
        "port": 8005,
        "health_endpoint": "/health",
        "iso_clauses": ["8.4"],
        "bci_practice": "PP5",
        "compliance_contribution": 15.0,
        "description": "BC plans and procedures"
    },
    "bcm_exercise": {
        "name": "Exercise & Testing",
        "port": 8006,
        "health_endpoint": "/health",
        "iso_clauses": ["8.5"],
        "bci_practice": "PP6",
        "compliance_contribution": 15.0,
        "description": "Exercise planning and execution"
    },
    "bcm_incident": {
        "name": "Incident Management",
        "port": 8007,
        "health_endpoint": "/health",
        "iso_clauses": ["8.4.2", "8.4.3"],
        "bci_practice": "PP5",
        "compliance_contribution": 10.0,
        "description": "Incident response structure"
    },
    "digital_twin": {
        "name": "Digital Twin",
        "port": 8008,
        "health_endpoint": "/health",
        "iso_clauses": ["8.5"],
        "bci_practice": "PP6",
        "compliance_contribution": 15.0,
        "description": "Virtual environment simulation"
    },
    "bcm_governance": {
        "name": "Governance",
        "port": 8009,
        "health_endpoint": "/health",
        "iso_clauses": ["4.1", "4.2", "4.3", "5.1", "5.2", "5.3"],
        "bci_practice": "PP1",
        "compliance_contribution": 20.0,
        "description": "BCMS governance framework"
    },
    "bcm_training": {
        "name": "Training & Awareness",
        "port": 8010,
        "health_endpoint": "/health",
        "iso_clauses": ["7.2", "7.3"],
        "bci_practice": "PP2",
        "compliance_contribution": 8.0,
        "description": "Competency and awareness management"
    },
    "document_processor": {
        "name": "Document Management",
        "port": 8011,
        "health_endpoint": "/health",
        "iso_clauses": ["7.5"],
        "bci_practice": "PP2",
        "compliance_contribution": 10.0,
        "description": "Document control and version management"
    },
    "bcm_reporting": {
        "name": "Reporting & Analytics",
        "port": 8012,
        "health_endpoint": "/health",
        "iso_clauses": ["9.1"],
        "bci_practice": "PP6",
        "compliance_contribution": 8.0,
        "description": "Performance metrics and reporting"
    },
    "scenario_hub": {
        "name": "Scenario Hub",
        "port": 8013,
        "health_endpoint": "/health",
        "iso_clauses": ["8.5"],
        "bci_practice": "PP6",
        "compliance_contribution": 12.0,
        "description": "AI scenario generation"
    },
    "compliance": {
        "name": "Compliance & Audit",
        "port": 8014,
        "health_endpoint": "/health",
        "iso_clauses": ["9.2", "9.3", "10.1", "10.2"],
        "bci_practice": "PP6",
        "compliance_contribution": 25.0,
        "description": "ISO 22301 compliance management"
    },

    # PLATFORM Services
    "api_gateway": {
        "name": "API Gateway",
        "port": 8000,
        "health_endpoint": "/health",
        "iso_clauses": [],
        "bci_practice": None,
        "compliance_contribution": 0.0,
        "description": "Unified API gateway"
    },
    "eventbus": {
        "name": "EventBus",
        "port": 8001,
        "health_endpoint": "/health",
        "iso_clauses": [],
        "bci_practice": None,
        "compliance_contribution": 0.0,
        "description": "Event-driven messaging"
    },
    "ai_orchestration": {
        "name": "AI Orchestration",
        "port": 8002,
        "health_endpoint": "/health",
        "iso_clauses": [],
        "bci_practice": None,
        "compliance_contribution": 0.0,
        "description": "AI model orchestration"
    }
}


async def check_service_health(service_name: str, service_config: Dict) -> Dict[str, Any]:
    """Check health of a single service"""

    health_url = f"http://localhost:{service_config['port']}{service_config['health_endpoint']}"

    try:
        timeout = aiohttp.ClientTimeout(total=3)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(health_url) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "service": service_name,
                        "status": "healthy",
                        "response_time_ms": None,  # Could measure
                        "details": data
                    }
                else:
                    return {
                        "service": service_name,
                        "status": "unhealthy",
                        "error": f"HTTP {response.status}"
                    }
    except aiohttp.ClientConnectorError:
        return {
            "service": service_name,
            "status": "offline",
            "error": "Connection refused"
        }
    except asyncio.TimeoutError:
        return {
            "service": service_name,
            "status": "timeout",
            "error": "Health check timeout"
        }
    except Exception as e:
        return {
            "service": service_name,
            "status": "error",
            "error": str(e)
        }


@router.get("/health", response_model=ModuleHealthSummary)
async def get_modules_health(
    db: AsyncSession = Depends(get_db)
) -> ModuleHealthSummary:
    """
    Get health status of all BCM platform modules

    Returns real-time health checks for:
    - BCM services (compliance, risk, bia, etc.)
    - PLATFORM services (gateway, eventbus, ai)
    - Compliance contribution %
    - ISO clause coverage

    Args:
        db: Database session

    Returns:
        Complete module health summary
    """
    try:
        import asyncio

        # Check all services concurrently
        health_checks = [
            check_service_health(name, config)
            for name, config in PLATFORM_SERVICES.items()
        ]

        health_results = await asyncio.gather(*health_checks, return_exceptions=True)

        # Process results
        modules = []
        total_contribution = 0.0
        healthy_count = 0
        warning_count = 0
        critical_count = 0
        offline_count = 0

        for i, result in enumerate(health_results):
            if isinstance(result, Exception):
                logger.error(f"Health check exception: {result}")
                continue

            service_name = result["service"]
            service_config = PLATFORM_SERVICES[service_name]

            # Determine health status
            status = result.get("status", "unknown")

            if status == "healthy":
                health_status = "healthy"
                healthy_count += 1
            elif status in ["unhealthy", "timeout"]:
                health_status = "warning"
                warning_count += 1
            elif status == "offline":
                health_status = "offline"
                offline_count += 1
            else:
                health_status = "critical"
                critical_count += 1

            # Add to contribution only if BCM service
            contribution = service_config.get("compliance_contribution", 0.0)
            if contribution > 0:
                total_contribution += contribution

            modules.append({
                "name": service_config["name"],
                "technical_name": service_name,
                "port": service_config["port"],
                "health_status": health_status,
                "development_status": "active" if status == "healthy" else "maintenance",
                "compliance_contribution": contribution,
                "iso_clauses": service_config.get("iso_clauses", []),
                "bci_practice": service_config.get("bci_practice"),
                "description": service_config.get("description", ""),
                "last_check": datetime.utcnow().isoformat(),
                "error": result.get("error")
            })

        # Calculate summary
        total_modules = len(modules)
        health_percentage = (healthy_count / total_modules * 100) if total_modules > 0 else 0

        return ModuleHealthSummary(
            total_modules=total_modules,
            healthy=healthy_count,
            warning=warning_count,
            critical=critical_count,
            offline=offline_count,
            health_percentage=round(health_percentage, 1),
            total_compliance_contribution=round(total_contribution, 1),
            modules=modules,
            timestamp=datetime.utcnow().isoformat()
        )

    except Exception as e:
        logger.error(f"Failed to get modules health: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get modules health: {str(e)}"
        )


@router.get("/health/{service_name}", response_model=ModuleHealthResponse)
async def get_service_health(
    service_name: str,
    db: AsyncSession = Depends(get_db)
) -> ModuleHealthResponse:
    """
    Get detailed health status of specific service

    Args:
        service_name: Technical service name (e.g., 'bcm_risk_management')
        db: Database session

    Returns:
        Detailed service health information
    """
    try:
        if service_name not in PLATFORM_SERVICES:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Service '{service_name}' not found in registry"
            )

        service_config = PLATFORM_SERVICES[service_name]

        # Check service health
        health_result = await check_service_health(service_name, service_config)

        # Determine status
        check_status = health_result.get("status", "unknown")

        if check_status == "healthy":
            health_status = "healthy"
        elif check_status in ["unhealthy", "timeout"]:
            health_status = "warning"
        elif check_status == "offline":
            health_status = "offline"
        else:
            health_status = "critical"

        return ModuleHealthResponse(
            name=service_config["name"],
            technical_name=service_name,
            port=service_config["port"],
            health_status=health_status,
            development_status="active" if check_status == "healthy" else "maintenance",
            compliance_contribution=service_config.get("compliance_contribution", 0.0),
            iso_clauses=service_config.get("iso_clauses", []),
            bci_practice=service_config.get("bci_practice"),
            description=service_config.get("description", ""),
            last_check=datetime.utcnow().isoformat(),
            error=health_result.get("error"),
            details=health_result.get("details")
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get service health: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get service health: {str(e)}"
        )


@router.get("/registry", response_model=List[Dict])
async def get_services_registry() -> List[Dict]:
    """
    Get complete BCM services registry

    Returns list of all registered services with metadata

    Returns:
        List of service definitions
    """
    return [
        {
            "name": config["name"],
            "technical_name": name,
            "port": config["port"],
            "iso_clauses": config.get("iso_clauses", []),
            "bci_practice": config.get("bci_practice"),
            "compliance_contribution": config.get("compliance_contribution", 0.0),
            "description": config.get("description", "")
        }
        for name, config in PLATFORM_SERVICES.items()
    ]


@router.post("/registry", status_code=status.HTTP_201_CREATED)
async def register_service(
    service: ModuleRegistration,
    db: AsyncSession = Depends(get_db)
) -> Dict:
    """
    Register new BCM service

    Allows dynamic service registration for platform expansion

    Args:
        service: Service registration data
        db: Database session

    Returns:
        Registration confirmation
    """
    try:
        # Add to registry (in production, store in database)
        PLATFORM_SERVICES[service.technical_name] = {
            "name": service.name,
            "port": service.port,
            "health_endpoint": service.health_endpoint or "/health",
            "iso_clauses": service.iso_clauses or [],
            "bci_practice": service.bci_practice,
            "compliance_contribution": service.compliance_contribution or 0.0,
            "description": service.description or ""
        }

        logger.info(f"Service registered: {service.technical_name} on port {service.port}")

        return {
            "success": True,
            "message": f"Service '{service.name}' registered successfully",
            "technical_name": service.technical_name
        }

    except Exception as e:
        logger.error(f"Failed to register service: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to register service: {str(e)}"
        )
