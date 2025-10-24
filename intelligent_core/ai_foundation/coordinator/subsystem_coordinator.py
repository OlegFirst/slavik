"""
SubsystemCoordinator - Central Coordination for Federated Subsystems
=====================================================================

Coordinates all ML, RAG, and Learning subsystems across the platform.

Philosophy:
-----------
The coordinator is NOT a single point of control. It's a coordination hub
that polls distributed subsystems and aggregates their results.

Like a nervous system:
- Brain (coordinator) coordinates
- Nerves (subsystems) are everywhere, each with their own function
- Brain doesn't replace nerves, it synthesizes their signals

Architecture:
-------------
1. Registration: Subsystems register themselves with coordinator
2. Discovery: Coordinator tracks all available subsystems
3. Routing: Coordinator routes requests to appropriate subsystems
4. Aggregation: Coordinator combines results from multiple subsystems
5. Monitoring: Coordinator monitors health of all subsystems
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
from collections import defaultdict

from ..protocols import IMLSubsystem, IRAGSubsystem, ILearningSubsystem


logger = logging.getLogger(__name__)


class SubsystemCoordinator:
    """
    Coordinates all federated subsystems across the platform.

    This is the central hub that:
    - Registers subsystems from different modules
    - Routes queries to appropriate subsystems
    - Aggregates results from multiple subsystems
    - Monitors subsystem health
    - Provides unified API for the platform
    """

    def __init__(self):
        """Initialize coordinator with empty registries."""
        # Subsystem registries by type
        self.ml_subsystems: Dict[str, IMLSubsystem] = {}
        self.rag_subsystems: Dict[str, IRAGSubsystem] = {}
        self.learning_subsystems: Dict[str, ILearningSubsystem] = {}

        # Metadata caches
        self._ml_metadata: Dict[str, Dict[str, Any]] = {}
        self._rag_metadata: Dict[str, Dict[str, Any]] = {}
        self._learning_metadata: Dict[str, Dict[str, Any]] = {}

        # Health tracking
        self._health_cache: Dict[str, Dict[str, Any]] = {}
        self._last_health_check: Optional[datetime] = None

        logger.info("SubsystemCoordinator initialized")

    # ===========================
    # Registration Methods
    # ===========================

    def register_ml(self, name: str, subsystem: IMLSubsystem) -> bool:
        """
        Register ML subsystem.

        Args:
            name: Unique subsystem name (e.g., 'workflow_ml', 'expert_ml')
            subsystem: IMLSubsystem implementation

        Returns:
            bool: True if registration successful
        """
        if name in self.ml_subsystems:
            logger.warning(f"ML subsystem '{name}' already registered, overwriting")

        self.ml_subsystems[name] = subsystem
        self._ml_metadata[name] = subsystem.get_metadata()

        logger.info(f"ML subsystem registered: {name} (domain: {self._ml_metadata[name].get('domain')})")
        return True

    def register_rag(self, name: str, subsystem: IRAGSubsystem) -> bool:
        """
        Register RAG subsystem.

        Args:
            name: Unique subsystem name (e.g., 'workflow_rag', 'expert_rag')
            subsystem: IRAGSubsystem implementation

        Returns:
            bool: True if registration successful
        """
        if name in self.rag_subsystems:
            logger.warning(f"RAG subsystem '{name}' already registered, overwriting")

        self.rag_subsystems[name] = subsystem
        self._rag_metadata[name] = subsystem.get_metadata()

        logger.info(f"RAG subsystem registered: {name} (domain: {self._rag_metadata[name].get('domain')})")
        return True

    def register_learning(self, name: str, subsystem: ILearningSubsystem) -> bool:
        """
        Register Learning subsystem.

        Args:
            name: Unique subsystem name (e.g., 'workflow_learning', 'expert_learning')
            subsystem: ILearningSubsystem implementation

        Returns:
            bool: True if registration successful
        """
        if name in self.learning_subsystems:
            logger.warning(f"Learning subsystem '{name}' already registered, overwriting")

        self.learning_subsystems[name] = subsystem
        self._learning_metadata[name] = subsystem.get_metadata()

        logger.info(f"Learning subsystem registered: {name} (domain: {self._learning_metadata[name].get('domain')})")
        return True

    # ===========================
    # Discovery Methods
    # ===========================

    def list_ml_subsystems(self) -> List[Dict[str, Any]]:
        """Return list of all registered ML subsystems with metadata."""
        return [
            {
                'name': name,
                **metadata
            }
            for name, metadata in self._ml_metadata.items()
        ]

    def list_rag_subsystems(self) -> List[Dict[str, Any]]:
        """Return list of all registered RAG subsystems with metadata."""
        return [
            {
                'name': name,
                **metadata
            }
            for name, metadata in self._rag_metadata.items()
        ]

    def list_learning_subsystems(self) -> List[Dict[str, Any]]:
        """Return list of all registered Learning subsystems with metadata."""
        return [
            {
                'name': name,
                **metadata
            }
            for name, metadata in self._learning_metadata.items()
        ]

    def get_subsystem_by_domain(self, subsystem_type: str, domain: str) -> List[str]:
        """
        Find subsystems by domain.

        Args:
            subsystem_type: 'ml', 'rag', or 'learning'
            domain: Domain name (e.g., 'workflow', 'expertise', 'orchestration')

        Returns:
            List[str]: Names of subsystems in that domain
        """
        if subsystem_type == 'ml':
            return [
                name for name, meta in self._ml_metadata.items()
                if meta.get('domain') == domain
            ]
        elif subsystem_type == 'rag':
            return [
                name for name, meta in self._rag_metadata.items()
                if meta.get('domain') == domain
            ]
        elif subsystem_type == 'learning':
            return [
                name for name, meta in self._learning_metadata.items()
                if meta.get('domain') == domain
            ]
        return []

    # ===========================
    # ML Coordination Methods
    # ===========================

    def coordinate_ml_prediction(
        self,
        features: Dict[str, Any],
        subsystems: Optional[List[str]] = None,
        aggregation: str = 'weighted_average'
    ) -> Dict[str, Any]:
        """
        Coordinate ML prediction across multiple subsystems.

        Args:
            features: Input features for prediction
            subsystems: Optional list of subsystem names to query (None = all)
            aggregation: How to aggregate results ('weighted_average', 'voting', 'ensemble')

        Returns:
            dict: Aggregated prediction result
                - predictions: List[dict] - Predictions from each subsystem
                - aggregated: Any - Aggregated prediction
                - confidence: float - Aggregated confidence
                - subsystems_used: List[str]
                - timestamp: str
        """
        target_subsystems = subsystems or list(self.ml_subsystems.keys())

        predictions = []
        for name in target_subsystems:
            if name not in self.ml_subsystems:
                logger.warning(f"ML subsystem '{name}' not found, skipping")
                continue

            try:
                subsystem = self.ml_subsystems[name]
                result = subsystem.predict(features)
                predictions.append(result)
            except Exception as e:
                logger.error(f"Error in ML subsystem '{name}': {e}")
                continue

        # Aggregate results
        aggregated = self._aggregate_ml_predictions(predictions, aggregation)

        return {
            'predictions': predictions,
            'aggregated': aggregated,
            'confidence': aggregated.get('confidence', 0.0),
            'subsystems_used': [p['subsystem'] for p in predictions],
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }

    def _aggregate_ml_predictions(self, predictions: List[Dict[str, Any]], method: str) -> Dict[str, Any]:
        """
        Aggregate predictions from multiple subsystems.

        Args:
            predictions: List of prediction results
            method: Aggregation method

        Returns:
            dict: Aggregated prediction
        """
        if not predictions:
            return {'prediction': None, 'confidence': 0.0}

        if method == 'weighted_average':
            # Weight by confidence
            total_confidence = sum(p['confidence'] for p in predictions)
            if total_confidence == 0:
                return predictions[0]  # Return first if all have 0 confidence

            # For numeric predictions, average weighted by confidence
            # For categorical, use voting weighted by confidence
            # This is simplified - real implementation would be more sophisticated
            highest_confidence = max(predictions, key=lambda p: p['confidence'])
            return {
                'prediction': highest_confidence['prediction'],
                'confidence': sum(p['confidence'] for p in predictions) / len(predictions),
                'method': 'weighted_average',
                'contributor_count': len(predictions)
            }

        elif method == 'voting':
            # Simple majority voting
            votes = defaultdict(float)
            for pred in predictions:
                pred_str = str(pred['prediction'])
                votes[pred_str] += pred['confidence']

            winner = max(votes.items(), key=lambda x: x[1])
            return {
                'prediction': winner[0],
                'confidence': winner[1] / len(predictions),
                'method': 'voting',
                'contributor_count': len(predictions)
            }

        else:  # ensemble
            return {
                'prediction': [p['prediction'] for p in predictions],
                'confidence': sum(p['confidence'] for p in predictions) / len(predictions),
                'method': 'ensemble',
                'contributor_count': len(predictions)
            }

    # ===========================
    # RAG Coordination Methods
    # ===========================

    def coordinate_rag_retrieval(
        self,
        query: str,
        subsystems: Optional[List[str]] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Coordinate RAG retrieval across multiple subsystems.

        Args:
            query: Search query
            subsystems: Optional list of subsystem names to query (None = all)
            config: Optional retrieval configuration

        Returns:
            dict: Aggregated retrieval results
                - results: List[dict] - All retrieved documents (merged & deduplicated)
                - results_by_subsystem: Dict[str, List[dict]] - Results grouped by subsystem
                - total_results: int
                - subsystems_used: List[str]
                - timestamp: str
        """
        target_subsystems = subsystems or list(self.rag_subsystems.keys())

        results_by_subsystem = {}
        all_results = []

        for name in target_subsystems:
            if name not in self.rag_subsystems:
                logger.warning(f"RAG subsystem '{name}' not found, skipping")
                continue

            try:
                subsystem = self.rag_subsystems[name]
                result = subsystem.retrieve(query, config)
                results_by_subsystem[name] = result['results']
                all_results.extend(result['results'])
            except Exception as e:
                logger.error(f"Error in RAG subsystem '{name}': {e}")
                continue

        # Deduplicate and rerank
        deduplicated = self._deduplicate_rag_results(all_results)
        reranked = self._rerank_rag_results(deduplicated, query)

        return {
            'results': reranked,
            'results_by_subsystem': results_by_subsystem,
            'total_results': len(reranked),
            'subsystems_used': list(results_by_subsystem.keys()),
            'query': query,
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }

    def _deduplicate_rag_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Deduplicate results based on document ID or content similarity.

        Args:
            results: List of documents from multiple subsystems

        Returns:
            List[dict]: Deduplicated results
        """
        seen_ids = set()
        deduplicated = []

        for result in results:
            doc_id = result.get('id')
            if doc_id not in seen_ids:
                seen_ids.add(doc_id)
                deduplicated.append(result)

        return deduplicated

    def _rerank_rag_results(self, results: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
        """
        Rerank results from multiple subsystems.

        Args:
            results: Deduplicated results
            query: Original query

        Returns:
            List[dict]: Reranked results (sorted by score)
        """
        # Simple reranking by score
        # Real implementation would use cross-encoder or similar
        return sorted(results, key=lambda r: r.get('score', 0.0), reverse=True)

    # ===========================
    # Learning Coordination Methods
    # ===========================

    def coordinate_learning(
        self,
        data: List[Dict[str, Any]],
        subsystems: Optional[List[str]] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Coordinate learning across multiple subsystems.

        Args:
            data: Training data
            subsystems: Optional list of subsystem names (None = all)
            config: Optional learning configuration

        Returns:
            dict: Aggregated learning results
                - results_by_subsystem: Dict[str, dict] - Learning results per subsystem
                - total_patterns: int - Total patterns discovered across all subsystems
                - total_rules: int - Total rules generated
                - subsystems_used: List[str]
                - timestamp: str
        """
        target_subsystems = subsystems or list(self.learning_subsystems.keys())

        results_by_subsystem = {}
        total_patterns = 0
        total_rules = 0

        for name in target_subsystems:
            if name not in self.learning_subsystems:
                logger.warning(f"Learning subsystem '{name}' not found, skipping")
                continue

            try:
                subsystem = self.learning_subsystems[name]
                result = subsystem.learn_from_data(data, config)
                results_by_subsystem[name] = result
                total_patterns += result.get('patterns_found', 0)
                total_rules += result.get('rules_generated', 0)
            except Exception as e:
                logger.error(f"Error in Learning subsystem '{name}': {e}")
                continue

        return {
            'results_by_subsystem': results_by_subsystem,
            'total_patterns': total_patterns,
            'total_rules': total_rules,
            'subsystems_used': list(results_by_subsystem.keys()),
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }

    # ===========================
    # Health Monitoring
    # ===========================

    def check_all_health(self) -> Dict[str, Any]:
        """
        Check health of all registered subsystems.

        Returns:
            dict: Health status for all subsystems
                - ml: Dict[str, dict] - ML subsystem health
                - rag: Dict[str, dict] - RAG subsystem health
                - learning: Dict[str, dict] - Learning subsystem health
                - overall_healthy: bool
                - unhealthy_subsystems: List[str]
                - timestamp: str
        """
        ml_health = {}
        rag_health = {}
        learning_health = {}
        unhealthy = []

        # Check ML subsystems
        for name, subsystem in self.ml_subsystems.items():
            try:
                health = subsystem.get_health_status()
                ml_health[name] = health
                if not health.get('healthy', False):
                    unhealthy.append(f"ml:{name}")
            except Exception as e:
                logger.error(f"Error checking ML subsystem '{name}' health: {e}")
                ml_health[name] = {'healthy': False, 'status': 'error', 'error': str(e)}
                unhealthy.append(f"ml:{name}")

        # Check RAG subsystems
        for name, subsystem in self.rag_subsystems.items():
            try:
                health = subsystem.get_health_status()
                rag_health[name] = health
                if not health.get('healthy', False):
                    unhealthy.append(f"rag:{name}")
            except Exception as e:
                logger.error(f"Error checking RAG subsystem '{name}' health: {e}")
                rag_health[name] = {'healthy': False, 'status': 'error', 'error': str(e)}
                unhealthy.append(f"rag:{name}")

        # Check Learning subsystems
        for name, subsystem in self.learning_subsystems.items():
            try:
                health = subsystem.get_health_status()
                learning_health[name] = health
                if not health.get('healthy', False):
                    unhealthy.append(f"learning:{name}")
            except Exception as e:
                logger.error(f"Error checking Learning subsystem '{name}' health: {e}")
                learning_health[name] = {'healthy': False, 'status': 'error', 'error': str(e)}
                unhealthy.append(f"learning:{name}")

        self._last_health_check = datetime.utcnow()

        return {
            'ml': ml_health,
            'rag': rag_health,
            'learning': learning_health,
            'overall_healthy': len(unhealthy) == 0,
            'unhealthy_subsystems': unhealthy,
            'timestamp': self._last_health_check.isoformat() + 'Z'
        }

    def get_coordinator_status(self) -> Dict[str, Any]:
        """
        Get status of coordinator itself.

        Returns:
            dict: Coordinator status
                - ml_subsystem_count: int
                - rag_subsystem_count: int
                - learning_subsystem_count: int
                - total_subsystems: int
                - last_health_check: Optional[str]
                - timestamp: str
        """
        return {
            'ml_subsystem_count': len(self.ml_subsystems),
            'rag_subsystem_count': len(self.rag_subsystems),
            'learning_subsystem_count': len(self.learning_subsystems),
            'total_subsystems': (
                len(self.ml_subsystems) +
                len(self.rag_subsystems) +
                len(self.learning_subsystems)
            ),
            'last_health_check': (
                self._last_health_check.isoformat() + 'Z'
                if self._last_health_check else None
            ),
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }


# ===========================
# Global Coordinator Instance
# ===========================

# Singleton instance for the entire platform
_global_coordinator = None


def get_global_coordinator() -> SubsystemCoordinator:
    """
    Get or create global coordinator instance.

    This is the central coordinator used across the entire platform.
    All subsystems should register with this instance.

    Returns:
        SubsystemCoordinator: Global coordinator instance
    """
    global _global_coordinator
    if _global_coordinator is None:
        _global_coordinator = SubsystemCoordinator()
        logger.info("Global SubsystemCoordinator created")
    return _global_coordinator
