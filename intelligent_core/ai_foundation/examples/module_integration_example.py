"""
Module Integration Example
==========================

This example shows how a module (like workflow_intelligence) would:
1. Create its own ML/RAG/Learning subsystems
2. Register them with the coordinator
3. Use the federated architecture

This demonstrates the INTENDED USE of ai_foundation's federated architecture.
"""

from typing import Dict, Any, List
import pandas as pd
from datetime import datetime

# Import base classes to extend
from intelligent_core.ai_foundation.ml import BaseMLSubsystem
from intelligent_core.ai_foundation.rag import BaseRAGSubsystem
from intelligent_core.ai_foundation.learning import BaseLearningSubsystem
from intelligent_core.ai_foundation.protocols import MLDataStandard, RAGDataStandard, LearningDataStandard
from intelligent_core.ai_foundation.coordinator import get_global_coordinator


# ============================================================================
# EXAMPLE 1: workflow_intelligence creates its own ML subsystem
# ============================================================================

class WorkflowMLSubsystem(BaseMLSubsystem):
    """
    ML subsystem specialized for workflow predictions.

    This extends BaseMLSubsystem with workflow-specific logic:
    - Predicts workflow duration
    - Predicts workflow bottlenecks
    - Predicts workflow success probability
    """

    def __init__(self):
        super().__init__()
        self.name = "workflow_ml"
        self.domain = "workflow"

        # Workflow-specific models
        self.duration_model = None  # Would load trained model
        self.bottleneck_model = None
        self.success_model = None

    def predict(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Workflow-specific predictions.

        Handles:
        - duration: Predict how long workflow will take
        - bottleneck: Predict where bottlenecks will occur
        - success: Predict probability of successful completion
        """
        prediction_type = features.get('workflow_prediction_type', 'duration')

        if prediction_type == 'duration':
            # Domain-specific logic for duration prediction
            workflow_type = features.get('workflow_type', 'generic')
            complexity = features.get('complexity', 1.0)

            # Simulate prediction (real implementation would use trained model)
            if workflow_type == 'bia':
                base_duration = 120  # minutes
            elif workflow_type == 'risk_assessment':
                base_duration = 90
            else:
                base_duration = 60

            predicted_duration = base_duration * complexity

            return MLDataStandard.format_prediction(
                subsystem_name=self.name,
                domain=self.domain,
                prediction={'duration_minutes': predicted_duration},
                confidence=0.87,
                model_used='workflow_duration_v2',
                explanation={
                    'workflow_type': workflow_type,
                    'complexity_factor': complexity,
                    'base_duration': base_duration
                }
            )

        elif prediction_type == 'bottleneck':
            # Predict workflow bottlenecks
            steps = features.get('steps', [])
            predicted_bottleneck = steps[len(steps) // 2] if steps else 'approval_stage'

            return MLDataStandard.format_prediction(
                subsystem_name=self.name,
                domain=self.domain,
                prediction={'bottleneck_step': predicted_bottleneck},
                confidence=0.75,
                model_used='workflow_bottleneck_detector',
                explanation={'step_count': len(steps)}
            )

        else:
            # Fall back to base implementation
            return super().predict(features)


# ============================================================================
# EXAMPLE 2: workflow_intelligence creates its own RAG subsystem
# ============================================================================

class WorkflowRAGSubsystem(BaseRAGSubsystem):
    """
    RAG subsystem specialized for workflow knowledge.

    This extends BaseRAGSubsystem with workflow-specific logic:
    - Retrieves workflow templates
    - Retrieves workflow best practices
    - Retrieves historical workflow data
    """

    def __init__(self):
        super().__init__(collection_name="workflow_knowledge")
        self.name = "workflow_rag"
        self.domain = "workflow"

    def retrieve(self, query: str, config: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Workflow-specific retrieval.

        Enhances base retrieval with workflow-specific logic:
        - Filters by workflow type
        - Prioritizes recent workflows
        - Includes workflow metrics
        """
        config = config or {}

        # Add workflow-specific filters
        workflow_type = config.get('workflow_type')
        if workflow_type:
            config['filters'] = config.get('filters', {})
            config['filters']['workflow_type'] = workflow_type

        # Call base retrieval
        result = super().retrieve(query, config)

        # Enhance results with workflow-specific metadata
        for doc in result['results']:
            # Add workflow-specific enrichment
            doc['metadata']['domain'] = 'workflow'
            doc['metadata']['retrieved_at'] = datetime.utcnow().isoformat() + 'Z'

        return result

    def get_workflow_templates(self, workflow_type: str) -> List[Dict[str, Any]]:
        """Workflow-specific method to get templates."""
        return self.search_by_filters({
            'type': 'template',
            'workflow_type': workflow_type
        })


# ============================================================================
# EXAMPLE 3: workflow_intelligence creates its own Learning subsystem
# ============================================================================

class WorkflowLearningSubsystem(BaseLearningSubsystem):
    """
    Learning subsystem specialized for workflow patterns.

    This extends BaseLearningSubsystem with workflow-specific logic:
    - Learns workflow optimization patterns
    - Learns bottleneck patterns
    - Learns success/failure patterns
    """

    def __init__(self):
        super().__init__(storage_path="/tmp/workflow_patterns.json")
        self.name = "workflow_learning"
        self.domain = "workflow"

    def learn_from_data(
        self,
        data: List[Dict[str, Any]],
        config: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Learn workflow-specific patterns.

        Analyzes:
        - Workflow completion times
        - Workflow success rates
        - Workflow bottlenecks
        - Workflow optimizations
        """
        config = config or {}

        # Pre-process workflow data
        workflow_data = self._preprocess_workflow_data(data)

        # Call base learning
        result = super().learn_from_data(workflow_data, config)

        # Add workflow-specific pattern detection
        workflow_patterns = self._detect_workflow_specific_patterns(workflow_data)

        # Merge with base patterns
        result['patterns'].extend(workflow_patterns)
        result['patterns_found'] += len(workflow_patterns)

        return result

    def _preprocess_workflow_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Preprocess workflow data for learning."""
        processed = []
        for item in data:
            processed.append({
                'workflow_type': item.get('type', 'unknown'),
                'duration': item.get('duration_minutes', 0),
                'success': item.get('status') == 'completed',
                'bottleneck_detected': item.get('bottleneck') is not None,
                'user_count': len(item.get('participants', []))
            })
        return processed

    def _detect_workflow_specific_patterns(
        self,
        data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Detect workflow-specific patterns."""
        patterns = []

        # Pattern: High user count correlates with longer duration
        high_user_workflows = [d for d in data if d.get('user_count', 0) > 5]
        if high_user_workflows:
            avg_duration = sum(d.get('duration', 0) for d in high_user_workflows) / len(high_user_workflows)

            patterns.append(
                LearningDataStandard.format_pattern(
                    pattern_id=f"workflow_pattern_{len(patterns)}",
                    description=f"Workflows with >5 users take avg {avg_duration:.0f} minutes",
                    confidence=0.82,
                    frequency=len(high_user_workflows),
                    conditions={'user_count_gt': 5},
                    actions={'allocate_extra_time': True, 'expected_duration': avg_duration}
                )
            )

        return patterns


# ============================================================================
# EXAMPLE 4: Module registers its subsystems with coordinator
# ============================================================================

def initialize_workflow_intelligence_ai():
    """
    Initialize all AI subsystems for workflow_intelligence module.

    This would be called when workflow_intelligence module starts.
    """
    # Get global coordinator
    coordinator = get_global_coordinator()

    # Create workflow-specific subsystems
    workflow_ml = WorkflowMLSubsystem()
    workflow_rag = WorkflowRAGSubsystem()
    workflow_learning = WorkflowLearningSubsystem()

    # Register with coordinator
    workflow_ml.register_with_coordinator(coordinator)
    workflow_rag.register_with_coordinator(coordinator)
    workflow_learning.register_with_coordinator(coordinator)

    print(f"✅ Workflow Intelligence AI subsystems registered")
    print(f"  - ML: {workflow_ml.name}")
    print(f"  - RAG: {workflow_rag.name}")
    print(f"  - Learning: {workflow_learning.name}")

    return {
        'ml': workflow_ml,
        'rag': workflow_rag,
        'learning': workflow_learning
    }


# ============================================================================
# EXAMPLE 5: Using the federated architecture
# ============================================================================

def example_federated_prediction():
    """
    Example: Make a prediction using ALL registered ML subsystems.

    The coordinator will:
    1. Query ALL ML subsystems (base_ml, workflow_ml, expertise_ml, etc.)
    2. Aggregate their predictions
    3. Return weighted result
    """
    coordinator = get_global_coordinator()

    # Features for prediction
    features = {
        'workflow_prediction_type': 'duration',
        'workflow_type': 'bia',
        'complexity': 1.5,
        'user_count': 7
    }

    # Coordinator queries ALL subsystems and aggregates
    aggregated_result = coordinator.coordinate_ml_prediction(
        features=features,
        aggregation='weighted_average'
    )

    print("\n=== Federated ML Prediction ===")
    print(f"Prediction: {aggregated_result['prediction']}")
    print(f"Confidence: {aggregated_result['confidence']:.2f}")
    print(f"Contributing subsystems: {len(aggregated_result['subsystems'])}")
    for subsystem_result in aggregated_result['subsystems']:
        print(f"  - {subsystem_result['subsystem']}: {subsystem_result['confidence']:.2f}")


def example_federated_retrieval():
    """
    Example: Retrieve knowledge from ALL registered RAG subsystems.

    The coordinator will:
    1. Query ALL RAG subsystems (base_rag, workflow_rag, expertise_rag, etc.)
    2. Merge and rank results
    3. Return best matches across all knowledge bases
    """
    coordinator = get_global_coordinator()

    query = "How to optimize workflow approval process?"

    # Coordinator queries ALL RAG subsystems
    aggregated_result = coordinator.coordinate_rag_retrieval(
        query=query,
        config={'top_k': 5}
    )

    print("\n=== Federated RAG Retrieval ===")
    print(f"Query: {query}")
    print(f"Total results: {aggregated_result['total_results']}")
    print(f"Contributing subsystems: {len(aggregated_result['subsystems'])}")

    for result in aggregated_result['results'][:3]:
        print(f"\n[Score: {result['score']:.2f}] {result['content'][:100]}...")
        print(f"  Source: {result['source']}")


def example_federated_learning():
    """
    Example: Learn patterns from data using ALL learning subsystems.

    The coordinator will:
    1. Distribute data to ALL learning subsystems
    2. Each learns domain-specific patterns
    3. Aggregate patterns from all subsystems
    """
    coordinator = get_global_coordinator()

    # Sample workflow data
    workflow_data = [
        {'type': 'bia', 'duration_minutes': 125, 'status': 'completed', 'participants': ['u1', 'u2', 'u3']},
        {'type': 'bia', 'duration_minutes': 180, 'status': 'completed', 'participants': ['u1', 'u2', 'u3', 'u4', 'u5', 'u6']},
        {'type': 'risk', 'duration_minutes': 95, 'status': 'completed', 'participants': ['u1', 'u2']},
        {'type': 'bia', 'duration_minutes': 145, 'status': 'failed', 'participants': ['u1']},
    ]

    # Coordinator distributes to ALL learning subsystems
    aggregated_result = coordinator.coordinate_learning(
        data=workflow_data,
        config={'mode': 'unsupervised', 'min_pattern_confidence': 0.7}
    )

    print("\n=== Federated Learning ===")
    print(f"Total patterns found: {aggregated_result['total_patterns']}")
    print(f"Contributing subsystems: {len(aggregated_result['subsystems'])}")

    for pattern in aggregated_result['patterns'][:3]:
        print(f"\n[Confidence: {pattern['confidence']:.2f}] {pattern['description']}")
        print(f"  Frequency: {pattern['frequency']}")


# ============================================================================
# MAIN EXAMPLE
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("AI Foundation - Module Integration Example")
    print("=" * 80)

    # Step 1: Initialize workflow_intelligence AI subsystems
    print("\n1. Initializing workflow_intelligence AI subsystems...")
    subsystems = initialize_workflow_intelligence_ai()

    # Step 2: Demonstrate federated ML prediction
    print("\n2. Demonstrating federated ML prediction...")
    example_federated_prediction()

    # Step 3: Demonstrate federated RAG retrieval
    print("\n3. Demonstrating federated RAG retrieval...")
    example_federated_retrieval()

    # Step 4: Demonstrate federated learning
    print("\n4. Demonstrating federated learning...")
    example_federated_learning()

    print("\n" + "=" * 80)
    print("✅ Module integration example complete!")
    print("=" * 80)
    print("\nKey Takeaways:")
    print("1. Each module creates its own specialized subsystems")
    print("2. Subsystems register with the global coordinator")
    print("3. Coordinator federates requests across all subsystems")
    print("4. Results are aggregated intelligently")
    print("5. This enables distributed, specialized AI across the platform")
