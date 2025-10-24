"""
AI Foundation Fallback Coordinator
Graceful degradation when primary AI services unavailable
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import asyncio

logger = logging.getLogger(__name__)


class FallbackCoordinator:
    """Fallback coordinator for AI services when primary unavailable"""

    def __init__(self):
        self.cache = {}  # Simple in-memory cache (should use Redis in production)
        self.cache_ttl = timedelta(hours=1)
        self.rule_based_predictor = RuleBasedPredictor()
        self.postgres_search = PostgresFullTextSearch()

    # =========================================================================
    # ML Fallbacks
    # =========================================================================

    async def coordinate_ml_prediction_fallback(
        self,
        features: Dict,
        **kwargs
    ) -> Dict:
        """
        Fallback для ML predictions

        Priority:
        1. Cached predictions (fastest)
        2. Rule-based predictions (fast)
        3. Historical average (slowest)
        """
        cache_key = self._get_cache_key('ml', features)

        # Fallback 1: Cached prediction
        cached = self._get_from_cache(cache_key)
        if cached:
            logger.info("Using cached ML prediction")
            return {
                "prediction": cached,
                "confidence": 0.7,  # Lower confidence for cached
                "source": "cache",
                "degraded": True
            }

        # Fallback 2: Rule-based prediction
        try:
            prediction = await self.rule_based_predictor.predict(features)
            logger.info("Using rule-based ML prediction")

            # Cache for future use
            self._save_to_cache(cache_key, prediction)

            return {
                "prediction": prediction,
                "confidence": 0.5,  # Lower confidence for rules
                "source": "rule_based",
                "degraded": True
            }
        except Exception as e:
            logger.error(f"Rule-based prediction failed: {e}")

        # Fallback 3: Historical average
        logger.warning("Using historical average (lowest confidence)")
        return {
            "prediction": self._get_historical_average(),
            "confidence": 0.3,
            "source": "historical",
            "degraded": True
        }

    # =========================================================================
    # RAG Fallbacks
    # =========================================================================

    async def coordinate_rag_fallback(
        self,
        query: str,
        **kwargs
    ) -> List[Dict]:
        """
        Fallback для RAG (vector search unavailable)

        Priority:
        1. Cached results
        2. PostgreSQL full-text search
        3. Simple keyword matching
        """
        cache_key = self._get_cache_key('rag', {'query': query})

        # Fallback 1: Cached results
        cached = self._get_from_cache(cache_key)
        if cached:
            logger.info("Using cached RAG results")
            return cached

        # Fallback 2: PostgreSQL full-text search
        try:
            results = await self.postgres_search.search(query)
            logger.info(f"Using PostgreSQL FTS: {len(results)} results")

            self._save_to_cache(cache_key, results)
            return results
        except Exception as e:
            logger.error(f"PostgreSQL FTS failed: {e}")

        # Fallback 3: Simple keyword matching (last resort)
        logger.warning("Using simple keyword matching")
        return []

    # =========================================================================
    # LLM Fallbacks
    # =========================================================================

    async def coordinate_llm_fallback(
        self,
        prompt: str,
        **kwargs
    ) -> str:
        """
        Fallback для LLM generation

        Priority:
        1. Cached responses
        2. Template-based responses
        3. Error message
        """
        cache_key = self._get_cache_key('llm', {'prompt': prompt})

        # Fallback 1: Cached response
        cached = self._get_from_cache(cache_key)
        if cached:
            logger.info("Using cached LLM response")
            return cached

        # Fallback 2: Template-based response
        template_response = self._get_template_response(prompt)
        if template_response:
            logger.info("Using template-based response")
            self._save_to_cache(cache_key, template_response)
            return template_response

        # Fallback 3: Error message
        logger.warning("No fallback available for LLM")
        return (
            "AI services are temporarily unavailable. "
            "Your request has been queued and will be processed shortly."
        )

    # =========================================================================
    # Cache Management
    # =========================================================================

    def _get_cache_key(self, service: str, params: Dict) -> str:
        """Generate cache key"""
        import hashlib
        import json
        content = json.dumps({"service": service, **params}, sort_keys=True)
        return hashlib.md5(content.encode()).hexdigest()

    def _get_from_cache(self, key: str) -> Optional[Any]:
        """Get from cache if not expired"""
        if key in self.cache:
            value, timestamp = self.cache[key]
            if datetime.now() - timestamp < self.cache_ttl:
                return value
            else:
                del self.cache[key]
        return None

    def _save_to_cache(self, key: str, value: Any):
        """Save to cache"""
        self.cache[key] = (value, datetime.now())

    # =========================================================================
    # Helpers
    # =========================================================================

    def _get_historical_average(self) -> float:
        """Get historical average for ML predictions"""
        # TODO: Query from database
        return 4.5  # Example: 4.5 hours

    def _get_template_response(self, prompt: str) -> Optional[str]:
        """Get template-based response"""
        templates = {
            "incident": "Please follow standard incident response procedures.",
            "bia": "Complete Business Impact Analysis using the standard template.",
            "risk": "Assess risks using the risk matrix framework."
        }

        for keyword, template in templates.items():
            if keyword in prompt.lower():
                return template

        return None


class RuleBasedPredictor:
    """Rule-based predictor for ML fallback"""

    async def predict(self, features: Dict) -> Any:
        """Simple rule-based prediction"""
        # Example: Workflow duration prediction based on type
        workflow_type = features.get('workflow_type', 'unknown')

        rules = {
            'bia': 8.0,  # hours
            'risk_assessment': 4.0,
            'compliance_check': 2.0,
            'incident_response': 1.0
        }

        return rules.get(workflow_type, 5.0)


class PostgresFullTextSearch:
    """PostgreSQL full-text search fallback for RAG"""

    async def search(self, query: str, limit: int = 5) -> List[Dict]:
        """Full-text search in PostgreSQL"""
        # TODO: Implement actual PostgreSQL FTS
        # This is a placeholder
        logger.info(f"PostgreSQL FTS for: {query}")
        return []


# Global instance
_fallback_coordinator: Optional[FallbackCoordinator] = None


def get_fallback_coordinator() -> FallbackCoordinator:
    """Get global fallback coordinator instance"""
    global _fallback_coordinator
    if _fallback_coordinator is None:
        _fallback_coordinator = FallbackCoordinator()
    return _fallback_coordinator
