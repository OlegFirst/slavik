"""
AI Foundation Integration Client

REAL integration with AI Foundation service for:
- RAG-based scenario search and retrieval
- LLM-powered specification generation
- ML prediction of simulation outcomes
- Knowledge retrieval from Knowledge Center
"""

import logging
from typing import Dict, List, Optional, Any
import httpx

from models.pydantic_models import TaskSpecification, Scenario, EngineType
from config.settings import Settings

logger = logging.getLogger(__name__)


class AIFoundationClient:
    """
    AI Foundation integration client

    Provides:
    - RAG search for similar scenarios and templates
    - LLM generation of task specifications
    - ML prediction of simulation outcomes
    - Knowledge retrieval and semantic search
    """

    def __init__(self, settings: Settings):
        """
        Initialize AI Foundation client

        Args:
            settings: Application settings
        """
        self.settings = settings
        self.base_url = settings.ai_foundation_url
        self.enabled = settings.ai_foundation_enabled
        self.timeout = 60.0  # Longer timeout for LLM operations

        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout
        )

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

    # ========================================================================
    # RAG: RETRIEVAL AUGMENTED GENERATION
    # ========================================================================

    async def rag_search_scenarios(
        self,
        query: str,
        context: Optional[Dict] = None,
        limit: int = 10,
        min_similarity: float = 0.7
    ) -> List[Dict]:
        """
        RAG-based search for similar scenarios

        Uses vector embeddings and semantic search to find:
        - Similar past simulations
        - Relevant templates from catalog
        - Community-contributed scenarios
        - Knowledge base articles

        Args:
            query: Search query (natural language)
            context: Additional context for search refinement
            limit: Maximum results
            min_similarity: Minimum similarity score (0-1)

        Returns:
            List of similar scenarios with relevance scores
        """
        if not self.enabled:
            logger.debug("AI Foundation disabled, skipping RAG search")
            return []

        try:
            response = await self.client.post(
                "/api/v1/rag/search",
                json={
                    "query": query,
                    "context": context or {},
                    "collections": ["scenarios", "templates", "simulations", "knowledge"],
                    "limit": limit,
                    "min_similarity": min_similarity,
                    "include_metadata": True
                }
            )
            response.raise_for_status()
            result = response.json()

            scenarios = result.get("results", [])
            logger.info(f"RAG search found {len(scenarios)} similar scenarios")
            return scenarios

        except httpx.HTTPError as e:
            logger.error(f"RAG search failed: {e}")
            return []

    async def rag_retrieve_context(
        self,
        specification: TaskSpecification,
        context_types: Optional[List[str]] = None
    ) -> Dict[str, List[Dict]]:
        """
        Retrieve relevant context for specification

        Gathers contextual information from multiple sources:
        - Similar past simulations
        - Relevant templates
        - Domain knowledge
        - Best practices

        Args:
            specification: Task specification
            context_types: Types of context to retrieve (defaults to all)

        Returns:
            Categorized context data
        """
        if not self.enabled:
            return {}

        if context_types is None:
            context_types = ["simulations", "templates", "knowledge", "best_practices"]

        try:
            response = await self.client.post(
                "/api/v1/rag/retrieve-context",
                json={
                    "specification": specification.model_dump(),
                    "context_types": context_types
                }
            )
            response.raise_for_status()
            result = response.json()

            context_data = result.get("context", {})
            logger.info(f"Retrieved context: {len(context_data)} types")
            return context_data

        except httpx.HTTPError as e:
            logger.warning(f"Context retrieval failed: {e}")
            return {}

    # ========================================================================
    # LLM: SPECIFICATION GENERATION
    # ========================================================================

    async def generate_specification(
        self,
        user_input: str,
        organization_context: Optional[Dict] = None,
        constraints: Optional[Dict] = None,
        reference_data: Optional[Dict] = None
    ) -> Optional[TaskSpecification]:
        """
        Generate task specification from natural language input

        Uses LLM to transform user input into structured specification:
        - Extracts goals and objectives
        - Identifies constraints
        - Suggests success criteria
        - Recommends engine and parameters

        This is UNIVERSAL solution that works with:
        - /catalogs data for internal platform testing
        - Digital Twin data (when available)
        - User profile data
        - Uploaded documents

        Args:
            user_input: Natural language description
            organization_context: Organization data (from Digital Twin, profile, or catalogs)
            constraints: Additional constraints
            reference_data: Reference documents/metrics

        Returns:
            Generated TaskSpecification or None
        """
        if not self.enabled:
            logger.debug("AI Foundation disabled, skipping generation")
            return None

        try:
            # Prepare generation request
            generation_request = {
                "user_input": user_input,
                "organization_context": organization_context or {},
                "constraints": constraints or {},
                "reference_data": reference_data or {},

                # Include catalog data for context
                "catalog_context": {
                    "available_templates": True,
                    "available_engines": [e.value for e in EngineType],
                    "modeling_approaches": [
                        "discrete_event",
                        "process_based",
                        "monte_carlo",
                        "what_if",
                        "workflow_based"
                    ]
                },

                "generation_params": {
                    "model": "gpt-4",  # or Claude, depending on config
                    "temperature": 0.7,
                    "max_tokens": 2000,
                    "include_reasoning": True
                }
            }

            response = await self.client.post(
                "/api/v1/llm/generate-specification",
                json=generation_request,
                timeout=90.0  # Longer timeout for generation
            )
            response.raise_for_status()
            result = response.json()

            # Parse generated specification
            spec_data = result.get("specification")
            reasoning = result.get("reasoning", "")

            if spec_data:
                logger.info(f"Specification generated: {spec_data.get('goal', '')[:50]}...")
                logger.debug(f"LLM reasoning: {reasoning}")

                # Convert to TaskSpecification
                specification = TaskSpecification(**spec_data)
                return specification
            else:
                logger.warning("LLM generation returned empty specification")
                return None

        except httpx.HTTPError as e:
            logger.error(f"Specification generation failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to parse generated specification: {e}")
            return None

    async def enhance_specification(
        self,
        specification: TaskSpecification,
        enhancement_type: str = "auto"
    ) -> Optional[TaskSpecification]:
        """
        Enhance existing specification with AI suggestions

        Enhancement types:
        - auto: Automatic improvements
        - objectives: Add/refine objectives
        - constraints: Add realistic constraints
        - success_criteria: Generate comprehensive criteria
        - context: Enrich context with domain knowledge

        Args:
            specification: Existing specification
            enhancement_type: Type of enhancement

        Returns:
            Enhanced specification or None
        """
        if not self.enabled:
            return specification

        try:
            response = await self.client.post(
                "/api/v1/llm/enhance-specification",
                json={
                    "specification": specification.model_dump(),
                    "enhancement_type": enhancement_type
                }
            )
            response.raise_for_status()
            result = response.json()

            enhanced_data = result.get("specification")
            if enhanced_data:
                return TaskSpecification(**enhanced_data)

            return specification

        except httpx.HTTPError as e:
            logger.warning(f"Specification enhancement failed: {e}")
            return specification

    # ========================================================================
    # ML: PREDICTIVE ANALYTICS
    # ========================================================================

    async def predict_simulation_outcome(
        self,
        specification: TaskSpecification,
        scenario: Scenario,
        engine: EngineType
    ) -> Dict[str, Any]:
        """
        Predict simulation outcome using ML models

        Uses historical data to predict:
        - Expected success rate
        - Likely duration
        - Resource requirements
        - Potential challenges
        - Confidence intervals

        Args:
            specification: Task specification
            scenario: Scenario to simulate
            engine: Engine to use

        Returns:
            Prediction dictionary with confidence scores
        """
        if not self.enabled:
            return {
                "prediction": "unavailable",
                "confidence": 0.0
            }

        try:
            response = await self.client.post(
                "/api/v1/ml/predict-outcome",
                json={
                    "specification": specification.model_dump(),
                    "scenario": scenario.model_dump(),
                    "engine": engine.value
                }
            )
            response.raise_for_status()
            result = response.json()

            prediction = result.get("prediction", {})
            logger.info(f"Outcome prediction: success_rate={prediction.get('expected_success_rate')}, confidence={prediction.get('confidence')}")
            return prediction

        except httpx.HTTPError as e:
            logger.warning(f"Outcome prediction failed: {e}")
            return {
                "prediction": "unavailable",
                "confidence": 0.0,
                "error": str(e)
            }

    async def recommend_engine(
        self,
        specification: TaskSpecification,
        available_engines: Optional[List[EngineType]] = None
    ) -> Dict[str, Any]:
        """
        ML-based engine recommendation

        Analyzes specification and recommends best engine based on:
        - Task type and complexity
        - Historical performance
        - Resource availability
        - Time constraints

        Args:
            specification: Task specification
            available_engines: Available engines (defaults to all)

        Returns:
            Recommendation with reasoning and alternatives
        """
        if not self.enabled:
            return {
                "recommended_engine": "simpy",
                "confidence": 0.5,
                "reasoning": "Default recommendation (AI Foundation disabled)"
            }

        if available_engines is None:
            available_engines = list(EngineType)

        try:
            response = await self.client.post(
                "/api/v1/ml/recommend-engine",
                json={
                    "specification": specification.model_dump(),
                    "available_engines": [e.value for e in available_engines]
                }
            )
            response.raise_for_status()
            result = response.json()

            recommendation = result.get("recommendation", {})
            logger.info(f"Engine recommendation: {recommendation.get('recommended_engine')} (confidence: {recommendation.get('confidence')})")
            return recommendation

        except httpx.HTTPError as e:
            logger.warning(f"Engine recommendation failed: {e}")
            return {
                "recommended_engine": "simpy",
                "confidence": 0.5,
                "reasoning": f"Default recommendation (error: {e})"
            }

    async def estimate_resources(
        self,
        specification: TaskSpecification,
        scenario: Scenario
    ) -> Dict[str, Any]:
        """
        Estimate required resources for simulation

        Predicts:
        - Computation time
        - Memory requirements
        - Participant requirements
        - Data storage needs

        Args:
            specification: Task specification
            scenario: Scenario

        Returns:
            Resource estimates
        """
        if not self.enabled:
            return {
                "computation_time_seconds": 300,
                "memory_mb": 512,
                "confidence": 0.0
            }

        try:
            response = await self.client.post(
                "/api/v1/ml/estimate-resources",
                json={
                    "specification": specification.model_dump(),
                    "scenario": scenario.model_dump()
                }
            )
            response.raise_for_status()
            return response.json()

        except httpx.HTTPError as e:
            logger.warning(f"Resource estimation failed: {e}")
            return {
                "computation_time_seconds": 300,
                "memory_mb": 512,
                "confidence": 0.0,
                "error": str(e)
            }

    # ========================================================================
    # KNOWLEDGE RETRIEVAL
    # ========================================================================

    async def retrieve_domain_knowledge(
        self,
        domain: str,
        query: Optional[str] = None,
        limit: int = 5
    ) -> List[Dict]:
        """
        Retrieve domain-specific knowledge

        Retrieves relevant knowledge from:
        - ISO 22301 standards
        - BCM best practices
        - Industry-specific guidelines
        - Organizational knowledge base

        Args:
            domain: Domain area (e.g., "cyber_security", "disaster_recovery")
            query: Optional specific query
            limit: Maximum results

        Returns:
            List of knowledge articles
        """
        if not self.enabled:
            return []

        try:
            response = await self.client.post(
                "/api/v1/knowledge/retrieve",
                json={
                    "domain": domain,
                    "query": query,
                    "limit": limit
                }
            )
            response.raise_for_status()
            result = response.json()

            knowledge = result.get("knowledge", [])
            logger.info(f"Retrieved {len(knowledge)} knowledge articles for domain: {domain}")
            return knowledge

        except httpx.HTTPError as e:
            logger.warning(f"Knowledge retrieval failed: {e}")
            return []

    # ========================================================================
    # EMBEDDINGS & VECTOR OPERATIONS
    # ========================================================================

    async def generate_embedding(
        self,
        text: str,
        model: str = "text-embedding-ada-002"
    ) -> Optional[List[float]]:
        """
        Generate embedding vector for text

        Args:
            text: Text to embed
            model: Embedding model to use

        Returns:
            Embedding vector or None
        """
        if not self.enabled:
            return None

        try:
            response = await self.client.post(
                "/api/v1/embeddings/generate",
                json={
                    "text": text,
                    "model": model
                }
            )
            response.raise_for_status()
            result = response.json()

            embedding = result.get("embedding")
            return embedding

        except httpx.HTTPError as e:
            logger.warning(f"Embedding generation failed: {e}")
            return None

    async def find_similar_by_embedding(
        self,
        embedding: List[float],
        collection: str,
        limit: int = 10
    ) -> List[Dict]:
        """
        Find similar items using embedding vector

        Args:
            embedding: Query embedding vector
            collection: Collection to search
            limit: Maximum results

        Returns:
            List of similar items with scores
        """
        if not self.enabled:
            return []

        try:
            response = await self.client.post(
                "/api/v1/embeddings/search",
                json={
                    "embedding": embedding,
                    "collection": collection,
                    "limit": limit
                }
            )
            response.raise_for_status()
            result = response.json()

            return result.get("results", [])

        except httpx.HTTPError as e:
            logger.warning(f"Similarity search failed: {e}")
            return []

    # ========================================================================
    # HEALTH CHECK
    # ========================================================================

    async def health_check(self) -> Dict:
        """
        Check AI Foundation health

        Returns:
            Health status dictionary
        """
        if not self.enabled:
            return {
                "status": "disabled",
                "connected": False
            }

        try:
            response = await self.client.get("/health", timeout=5.0)
            response.raise_for_status()

            health_data = response.json()

            return {
                "status": "healthy",
                "connected": True,
                "services": {
                    "rag": health_data.get("rag_service", "unknown"),
                    "llm": health_data.get("llm_service", "unknown"),
                    "ml": health_data.get("ml_service", "unknown"),
                    "embeddings": health_data.get("embeddings_service", "unknown")
                },
                "response": health_data
            }

        except httpx.HTTPError as e:
            return {
                "status": "unhealthy",
                "connected": False,
                "error": str(e)
            }
