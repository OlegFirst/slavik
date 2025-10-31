"""TheHive API client service"""

import aiohttp
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class TheHiveClient:
    """Client for TheHive API integration"""
    
    def __init__(self, config):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        self.base_url = config.THEHIVE_URL
        self.api_key = config.THEHIVE_API_KEY
        
    async def connect(self):
        """Initialize HTTP session"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "User-Agent": "BCM-Platform/1.0"
            }
            
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(
                headers=headers,
                timeout=timeout
            )
            
            # Test connection
            await self.is_healthy()
            logger.info("Connected to TheHive API")
            
        except Exception as e:
            logger.error(f"Failed to connect to TheHive: {str(e)}")
            raise
    
    async def disconnect(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()
            logger.info("Disconnected from TheHive API")
    
    async def is_healthy(self) -> bool:
        """Check TheHive API health"""
        try:
            async with self.session.get(f"{self.base_url}/api/status") as response:
                return response.status == 200
        except Exception as e:
            logger.error(f"TheHive health check failed: {str(e)}")
            return False
    
    async def create_case(
        self, 
        title: str, 
        description: str, 
        severity: int, 
        tags: List[str],
        tenant_id: str,
        incident_id: str
    ) -> Optional[Dict[str, Any]]:
        """Create new case in TheHive"""
        try:
            # Add tenant and incident tags
            all_tags = tags + [f"tenant:{tenant_id}", f"bcm_incident:{incident_id}"]
            
            case_data = {
                "title": title,
                "description": description,
                "severity": severity,
                "tags": all_tags,
                "tlp": 2,  # TLP:AMBER
                "pap": 2,  # PAP:AMBER
                "source": "BCM Platform",
                "customFields": {
                    "bcm_tenant_id": {"string": tenant_id},
                    "bcm_incident_id": {"string": incident_id},
                    "bcm_created_at": {"date": int(datetime.utcnow().timestamp() * 1000)}
                }
            }
            
            async with self.session.post(f"{self.base_url}/api/case", json=case_data) as response:
                if response.status == 201:
                    case = await response.json()
                    logger.info(f"Created TheHive case {case['id']} for incident {incident_id}")
                    return case
                else:
                    error_text = await response.text()
                    logger.error(f"Failed to create case: {response.status} - {error_text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error creating case: {str(e)}")
            return None
    
    async def get_case(self, case_id: str) -> Optional[Dict[str, Any]]:
        """Get case details by ID"""
        try:
            async with self.session.get(f"{self.base_url}/api/case/{case_id}") as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 404:
                    return None
                else:
                    error_text = await response.text()
                    logger.error(f"Failed to get case: {response.status} - {error_text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error getting case: {str(e)}")
            return None
    
    async def update_case(self, case_id: str, updates: Dict[str, Any]) -> bool:
        """Update case in TheHive"""
        try:
            async with self.session.patch(f"{self.base_url}/api/case/{case_id}", json=updates) as response:
                if response.status == 204:
                    logger.info(f"Updated TheHive case {case_id}")
                    return True
                else:
                    error_text = await response.text()
                    logger.error(f"Failed to update case: {response.status} - {error_text}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error updating case: {str(e)}")
            return False
    
    async def close_case(self, case_id: str, resolution: str = "Resolved") -> bool:
        """Close case in TheHive"""
        try:
            update_data = {
                "status": "Resolved",
                "resolutionStatus": resolution,
                "endDate": int(datetime.utcnow().timestamp() * 1000)
            }
            
            return await self.update_case(case_id, update_data)
            
        except Exception as e:
            logger.error(f"Error closing case: {str(e)}")
            return False
    
    async def add_observable(
        self,
        case_id: str,
        data_type: str,
        data: str,
        message: str = "",
        tags: List[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Add observable to case"""
        try:
            observable_data = {
                "dataType": data_type,
                "data": data,
                "message": message,
                "tags": tags or [],
                "tlp": 2,  # TLP:AMBER
                "pap": 2,  # PAP:AMBER
                "ioc": False,
                "sighted": False
            }
            
            async with self.session.post(
                f"{self.base_url}/api/case/{case_id}/artifact", 
                json=observable_data
            ) as response:
                if response.status == 201:
                    observable = await response.json()
                    logger.info(f"Added observable {observable['id']} to case {case_id}")
                    return observable
                else:
                    error_text = await response.text()
                    logger.error(f"Failed to add observable: {response.status} - {error_text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error adding observable: {str(e)}")
            return None
    
    async def create_task(
        self,
        case_id: str,
        title: str,
        description: str = "",
        assignee: str = None
    ) -> Optional[Dict[str, Any]]:
        """Create task in case"""
        try:
            task_data = {
                "title": title,
                "description": description,
                "status": "Waiting",
                "flag": False
            }
            
            if assignee:
                task_data["assignee"] = assignee
            
            async with self.session.post(
                f"{self.base_url}/api/case/{case_id}/task",
                json=task_data
            ) as response:
                if response.status == 201:
                    task = await response.json()
                    logger.info(f"Created task {task['id']} in case {case_id}")
                    return task
                else:
                    error_text = await response.text()
                    logger.error(f"Failed to create task: {response.status} - {error_text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error creating task: {str(e)}")
            return None
    
    async def search_cases(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search cases by query"""
        try:
            async with self.session.post(f"{self.base_url}/api/case/_search", json=query) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    logger.error(f"Failed to search cases: {response.status} - {error_text}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error searching cases: {str(e)}")
            return []
    
    async def get_case_statistics(self, tenant_id: str) -> Dict[str, Any]:
        """Get case statistics for tenant"""
        try:
            # Search for cases with tenant tag
            query = {
                "query": {"_field": "tags", "_value": f"tenant:{tenant_id}"},
                "range": "all"
            }
            
            cases = await self.search_cases(query)
            
            # Calculate statistics
            total_cases = len(cases)
            open_cases = len([c for c in cases if c.get("status") != "Resolved"])
            critical_cases = len([c for c in cases if c.get("severity", 1) >= 3])
            
            severity_distribution = {}
            status_distribution = {}
            
            for case in cases:
                severity = case.get("severity", 1)
                status = case.get("status", "Open")
                
                severity_distribution[severity] = severity_distribution.get(severity, 0) + 1
                status_distribution[status] = status_distribution.get(status, 0) + 1
            
            return {
                "total_cases": total_cases,
                "open_cases": open_cases,
                "critical_cases": critical_cases,
                "severity_distribution": severity_distribution,
                "status_distribution": status_distribution,
                "tenant_id": tenant_id
            }
            
        except Exception as e:
            logger.error(f"Error getting statistics: {str(e)}")
            return {
                "total_cases": 0,
                "open_cases": 0,
                "critical_cases": 0,
                "severity_distribution": {},
                "status_distribution": {},
                "tenant_id": tenant_id,
                "error": str(e)
            }
    
    async def get_case_tasks(self, case_id: str) -> List[Dict[str, Any]]:
        """Get tasks for a case"""
        try:
            async with self.session.get(f"{self.base_url}/api/case/{case_id}/task") as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"Failed to get case tasks: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error getting case tasks: {str(e)}")
            return []
    
    async def get_case_observables(self, case_id: str) -> List[Dict[str, Any]]:
        """Get observables for a case"""
        try:
            async with self.session.get(f"{self.base_url}/api/case/{case_id}/artifact") as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"Failed to get case observables: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error getting case observables: {str(e)}")
            return []
    
    def _map_bcm_severity_to_hive(self, bcm_severity: str) -> int:
        """Map BCM severity to TheHive severity scale (1-4)"""
        severity_mapping = {
            "low": 1,
            "medium": 2,
            "high": 3,
            "critical": 4
        }
        return severity_mapping.get(bcm_severity.lower(), 2)
    
    def _extract_tenant_from_tags(self, tags: List[str]) -> Optional[str]:
        """Extract tenant ID from case tags"""
        for tag in tags:
            if tag.startswith("tenant:"):
                return tag.split(":", 1)[1]
        return None
    
    def _extract_incident_from_tags(self, tags: List[str]) -> Optional[str]:
        """Extract BCM incident ID from case tags"""
        for tag in tags:
            if tag.startswith("bcm_incident:"):
                return tag.split(":", 1)[1]
        return None
