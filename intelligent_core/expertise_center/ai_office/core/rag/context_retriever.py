"""
Context Retriever

Fetches relevant data from BCM modules via HTTP to provide context for RAG.
Supports async requests with timeout and error handling.
"""

import logging
from typing import Dict, List, Optional, Any
from enum import Enum
import httpx
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class RetrievedContext(BaseModel):
    """Context retrieved from BCM modules"""
    module: str
    data: List[Dict[str, Any]]
    score: float  # Relevance score
    source_url: str


class ContextRetriever:
    """
    Retrieves relevant context from BCM modules.

    Performs parallel HTTP requests to BCM services to gather
    context for answering user queries.
    """

    def __init__(
        self,
        module_urls: Dict[str, str],
        timeout: int = 10,
        max_items_per_module: int = 5
    ):
        """
        Initialize context retriever.

        Args:
            module_urls: Dict of module_name -> base_url
            timeout: Request timeout in seconds
            max_items_per_module: Max items to retrieve per module
        """
        self.module_urls = module_urls
        self.timeout = timeout
        self.max_items_per_module = max_items_per_module

    async def retrieve(
        self,
        query: str,
        target_modules: List[str],
        intent: Dict[str, Any],
        tenant_id: str = "demo",
        entities: Optional[Dict[str, Any]] = None
    ) -> List[RetrievedContext]:
        """
        Retrieve relevant context from BCM modules.

        Args:
            query: User's query
            target_modules: List of module names to query
            intent: Intent analysis result
            tenant_id: Tenant identifier
            entities: Extracted entities (IDs, etc.)

        Returns:
            List of RetrievedContext from each module
        """
        contexts = []

        # Build requests for each target module
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            tasks = []

            for module_name in target_modules:
                if module_name not in self.module_urls:
                    logger.warning(f"Unknown module: {module_name}")
                    continue

                # Build module-specific request
                request_task = self._fetch_from_module(
                    client=client,
                    module_name=module_name,
                    query=query,
                    intent=intent,
                    tenant_id=tenant_id,
                    entities=entities
                )
                tasks.append(request_task)

            # Execute all requests in parallel
            if tasks:
                results = await asyncio.gather(*tasks, return_exceptions=True)

                # Process results
                for result in results:
                    if isinstance(result, RetrievedContext):
                        contexts.append(result)
                    elif isinstance(result, Exception):
                        logger.error(f"Context retrieval error: {str(result)}")

        # Sort by relevance score
        contexts.sort(key=lambda x: x.score, reverse=True)

        return contexts

    async def _fetch_from_module(
        self,
        client: httpx.AsyncClient,
        module_name: str,
        query: str,
        intent: Dict[str, Any],
        tenant_id: str,
        entities: Optional[Dict[str, Any]]
    ) -> Optional[RetrievedContext]:
        """
        Fetch data from a specific BCM module.

        Args:
            client: httpx client
            module_name: Name of BCM module
            query: User query
            intent: Intent analysis
            tenant_id: Tenant ID
            entities: Extracted entities

        Returns:
            RetrievedContext or None
        """
        base_url = self.module_urls[module_name]

        try:
            # Determine endpoint based on module and intent
            endpoint, params = self._build_request(module_name, intent, entities, tenant_id)

            if not endpoint:
                return None

            # Make request
            response = await client.get(
                f"{base_url}{endpoint}",
                params=params,
                headers={"X-Tenant-ID": tenant_id}
            )

            if response.status_code == 200:
                data = response.json()

                # Extract items (handle different response formats)
                items = self._extract_items(data, module_name)

                # Limit items
                items = items[:self.max_items_per_module]

                # Calculate relevance score
                score = self._calculate_score(items, query, intent)

                return RetrievedContext(
                    module=module_name,
                    data=items,
                    score=score,
                    source_url=f"{base_url}{endpoint}"
                )
            else:
                logger.warning(f"Module {module_name} returned {response.status_code}")
                return None

        except httpx.TimeoutException:
            logger.error(f"Timeout fetching from {module_name}")
            return None
        except Exception as e:
            logger.error(f"Error fetching from {module_name}: {str(e)}", exc_info=True)
            return None

    def _build_request(
        self,
        module_name: str,
        intent: Dict[str, Any],
        entities: Optional[Dict[str, Any]],
        tenant_id: str
    ) -> tuple[Optional[str], Dict[str, Any]]:
        """
        Build module-specific API request.

        Returns:
            (endpoint, params) or (None, {})
        """
        intent_type = intent.get('intent_type', 'unknown')
        params = {"tenant_id": tenant_id}

        # Risk module
        if module_name == "risk":
            if entities and 'risk_id' in entities:
                return f"/api/risks/{entities['risk_id']}", {}
            else:
                # Get top risks
                params['limit'] = self.max_items_per_module
                params['sort'] = 'priority_desc'
                return "/api/risks", params

        # BIA module
        elif module_name == "bia":
            if 'analyze' in intent_type:
                params['limit'] = self.max_items_per_module
                return "/api/bia/critical-processes", params
            else:
                return "/api/bia/summary", params

        # Plans module
        elif module_name == "plans":
            if entities and 'plan_id' in entities:
                return f"/api/plans/{entities['plan_id']}", {}
            else:
                params['limit'] = self.max_items_per_module
                params['status'] = 'active'
                return "/api/plans", params

        # Compliance module
        elif module_name == "compliance":
            if 'assessment' in intent_type or 'compliance' in intent_type:
                return "/api/compliance/gaps", params
            else:
                return "/api/compliance/status", params

        # Response module
        elif module_name == "response":
            if entities and 'incident_id' in entities:
                return f"/api/incidents/{entities['incident_id']}", {}
            else:
                params['limit'] = self.max_items_per_module
                params['status'] = 'open'
                return "/api/incidents", params

        # Validation module
        elif module_name == "validation":
            params['limit'] = self.max_items_per_module
            return "/api/exercises/recent", params

        # Learning module
        elif module_name == "learning":
            params['limit'] = self.max_items_per_module
            return "/api/training/upcoming", params

        # Documents module
        elif module_name == "documents":
            params['limit'] = self.max_items_per_module
            return "/api/documents/recent", params

        # Governance module
        elif module_name == "governance":
            return "/api/governance/framework", params

        # Planning module
        elif module_name == "planning":
            return "/api/planning/current-cycle", params

        # Unknown module
        else:
            logger.warning(f"No retrieval strategy for module: {module_name}")
            return None, {}

    def _extract_items(self, response_data: Any, module_name: str) -> List[Dict[str, Any]]:
        """
        Extract items from module response.

        Handles different response formats:
        - Direct list: [...]
        - Wrapped: {"items": [...]}
        - Wrapped with pagination: {"data": [...], "total": N}
        """
        if isinstance(response_data, list):
            return response_data

        if isinstance(response_data, dict):
            # Try common keys
            for key in ['items', 'data', 'results', module_name]:
                if key in response_data and isinstance(response_data[key], list):
                    return response_data[key]

            # Single item response
            if 'id' in response_data:
                return [response_data]

        return []

    def _calculate_score(
        self,
        items: List[Dict[str, Any]],
        query: str,
        intent: Dict[str, Any]
    ) -> float:
        """
        Calculate relevance score for retrieved context.

        Scoring factors:
        - Number of items retrieved
        - Keyword matches
        - Intent alignment
        """
        if not items:
            return 0.0

        score = 0.5  # Base score

        # More items = higher score (up to +0.2)
        score += min(len(items) / 10, 0.2)

        # Keyword matching (simple approach)
        query_lower = query.lower()
        keywords = query_lower.split()

        for item in items:
            item_text = str(item).lower()
            matches = sum(1 for kw in keywords if kw in item_text)
            score += (matches / len(keywords)) * 0.1

        # Cap at 1.0
        return min(score, 1.0)


# Import asyncio for gather
import asyncio
