"""
Platform Integration Examples

Демонстрирует как использовать shared platform components
в Learning System
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add paths
shared_path = Path(__file__).parent.parent.parent.parent / "shared"
sys.path.insert(0, str(shared_path))

from integrations.rag_connector import RAGConnector, RAGQueryBuilder
from integrations.ml_platform_client import MLPlatformClient, FeatureBuilder
from integrations.knowledge_client import KnowledgeClient, KnowledgeType, KnowledgeArticleBuilder


# ============================================================================
# Example 1: RAG Semantic Search
# ============================================================================

async def example_rag_semantic_search():
    """
    Example: Поиск learning resources с помощью RAG
    """
    print("\n" + "="*70)
    print("EXAMPLE 1: RAG Semantic Search")
    print("="*70)

    rag = RAGConnector()

    try:
        # Simple search
        print("\n1. Simple search:")
        results = await rag.search_knowledge(
            query="cyber incident escalation procedures",
            limit=5
        )
        print(f"Found {len(results)} results")
        for r in results[:2]:
            print(f"  - {r.get('metadata', {}).get('title', 'Untitled')}: score={r.get('score', 0):.2f}")

        # Advanced search with context and filters
        print("\n2. Advanced search with context:")
        query_builder = RAGQueryBuilder()
        query_builder.with_query("how to improve communication during incidents")
        query_builder.with_context(
            user_id="user123",
            domain="BCM",
            competency_level="intermediate"
        )
        query_builder.filter_by_type("procedure", "guideline", "best_practice")
        query_builder.filter_by_tags("communication", "incident")

        results = await rag.search_knowledge(
            query=query_builder.query,
            context=query_builder.context,
            filters=query_builder.filters,
            limit=5
        )
        print(f"Found {len(results)} filtered results")

        # Get related knowledge
        if results:
            print("\n3. Get related knowledge:")
            first_id = results[0].get('id')
            related = await rag.get_related_knowledge(first_id, limit=3)
            print(f"Found {len(related)} related items")

    finally:
        await rag.close()

    print("\n✓ RAG semantic search example complete\n")


# ============================================================================
# Example 2: ML Platform Predictions
# ============================================================================

async def example_ml_predictions():
    """
    Example: Предсказания с помощью ML Platform
    """
    print("\n" + "="*70)
    print("EXAMPLE 2: ML Platform Predictions")
    print("="*70)

    ml_client = MLPlatformClient()

    try:
        # Exercise success prediction
        print("\n1. Predict exercise success:")
        features = FeatureBuilder()
        features.add_categorical('scenario_type', 'cyber_incident')
        features.add_numeric('team_size', 12)
        features.add_numeric('avg_competency', 0.75)
        features.add_numeric('days_since_last_exercise', 45)
        features.add_list_aggregates('historical_scores', [78, 82, 85])

        prediction = await ml_client.predict(
            model_name='exercise_success_predictor',
            features=features.build(),
            context={'user_id': 'user123'},
            return_explanation=True
        )

        print(f"Predicted score: {prediction.get('prediction', 0):.1f}")
        print(f"Confidence: {prediction.get('confidence', 0):.2f}")
        print(f"Model version: {prediction.get('model_version', 'unknown')}")

        prediction_id = prediction.get('prediction_id')

        # Submit feedback (simulate)
        print("\n2. Submit feedback (after exercise):")
        actual_score = 82.0
        success = await ml_client.submit_feedback(
            prediction_id=prediction_id,
            actual_outcome=actual_score,
            metadata={
                'exercise_id': 'ex_123',
                'duration_minutes': 120,
                'participant_count': 12
            }
        )
        print(f"Feedback submitted: {success}")
        print(f"Actual score: {actual_score} (predicted: {prediction.get('prediction', 0):.1f})")
        print(f"Error: {abs(actual_score - prediction.get('prediction', 0)):.1f} points")

        # Get model info
        print("\n3. Get model information:")
        model_info = await ml_client.get_model_info('exercise_success_predictor')
        if model_info:
            print(f"Model: {model_info.get('name', 'unknown')}")
            print(f"Version: {model_info.get('version', 'unknown')}")
        else:
            print("Model info not available (service not running)")

        # List available models
        print("\n4. List available models:")
        models = await ml_client.list_available_models(domain='bcm')
        print(f"Found {len(models)} BCM models")
        for model in models[:3]:
            print(f"  - {model.get('name', 'unknown')}: {model.get('description', '')}")

    finally:
        await ml_client.close()

    print("\n✓ ML Platform predictions example complete\n")


# ============================================================================
# Example 3: Knowledge Base Operations
# ============================================================================

async def example_knowledge_base():
    """
    Example: Работа с Knowledge Base
    """
    print("\n" + "="*70)
    print("EXAMPLE 3: Knowledge Base Operations")
    print("="*70)

    kb_client = KnowledgeClient()

    try:
        # Create article
        print("\n1. Create knowledge article:")
        article_builder = KnowledgeArticleBuilder()
        article_builder.with_title("Communication Best Practices for Cyber Incidents")
        article_builder.with_content("""
## Overview

Effective communication is critical during cyber incidents.

## Key Principles

1. **Clarity**: Use clear, unambiguous language
2. **Timeliness**: Communicate updates promptly
3. **Consistency**: Ensure all stakeholders receive same information

## Procedures

1. Initial notification within 15 minutes
2. Status updates every 30 minutes
3. Escalation to senior management for critical issues
        """)
        article_builder.with_category("best_practices")
        article_builder.with_type(KnowledgeType.BEST_PRACTICE)
        article_builder.add_tag("communication", "cyber", "incident")
        article_builder.with_iso_reference("ISO 22301:2019 8.4")
        article_builder.with_severity("medium")

        article_data = article_builder.build()
        article_id = await kb_client.create_article(**article_data)

        if article_id:
            print(f"Created article: {article_id}")
        else:
            print("Article creation failed (service not running)")

        # Search knowledge
        print("\n2. Search knowledge base:")
        results = await kb_client.search(
            query="communication cyber incident",
            filters={'category': 'best_practices'},
            limit=5
        )
        print(f"Found {len(results)} articles")
        for r in results[:2]:
            print(f"  - {r.get('title', 'Untitled')}")

        # List by category
        print("\n3. List by category:")
        procedures = await kb_client.list_by_category('procedures', limit=10)
        print(f"Found {len(procedures)} procedures")

        # List by tags
        print("\n4. List by tags:")
        tagged = await kb_client.list_by_tags(['cyber', 'incident'], match_all=True, limit=10)
        print(f"Found {len(tagged)} articles with both tags")

    finally:
        await kb_client.close()

    print("\n✓ Knowledge Base operations example complete\n")


# ============================================================================
# Example 4: Integrated Knowledge Connector
# ============================================================================

async def example_integrated_knowledge():
    """
    Example: Integrated Knowledge Connector (Learning System specific)
    """
    print("\n" + "="*70)
    print("EXAMPLE 4: Integrated Knowledge Connector")
    print("="*70)

    # Import integrated connector
    engines_path = Path(__file__).parent.parent / "engines"
    sys.path.insert(0, str(engines_path))

    from knowledge_base_connector_integrated import IntegratedKnowledgeConnector

    kb_connector = IntegratedKnowledgeConnector()

    try:
        # Search resources for competency gap
        print("\n1. Search resources for competency gap:")
        resources = await kb_connector.search_resources_for_gap(
            gap_keyword="escalation",
            user_id="user123",
            competency_level="intermediate"
        )
        print(f"Found {len(resources)} resources for 'escalation' gap")

        # Create learning path
        print("\n2. Create learning path from resources:")
        learning_path = await kb_connector.create_learning_path_from_resources(
            user_id="user123",
            competency_gap="escalation",
            resources=resources
        )
        print(f"Created learning path with {len(learning_path.get('path', []))} resources")
        print(f"Estimated hours: {learning_path.get('estimated_hours', 0)}")

        # Auto-create knowledge from pattern
        print("\n3. Auto-create knowledge from pattern:")
        pattern = {
            'pattern_name': 'Communication Delays in Cyber Incidents',
            'description': 'Recurring delays in escalation communication during cyber incidents',
            'occurrence_count': 8,  # ≥5 threshold
            'confidence': 0.85,
            'severity': 'high',
            'pattern_type': 'failure',
            'pattern_category': 'exercise',
            'affected_areas': ['scenario:cyber_incident', 'role:incident_manager'],
            'recommended_actions': [
                'Implement automated escalation notifications',
                'Provide communication protocol training',
                'Add communication checkpoints to runbooks'
            ],
            'evidence_data': {
                'avg_delay_minutes': 12,
                'exercises_affected': 8
            }
        }

        article_id = await kb_connector.auto_create_knowledge_from_pattern(
            pattern=pattern,
            threshold_occurrences=5
        )

        if article_id:
            print(f"Auto-created knowledge article: {article_id}")
        else:
            print("Pattern below threshold or service not available")

    finally:
        await kb_connector.close()

    print("\n✓ Integrated Knowledge Connector example complete\n")


# ============================================================================
# Example 5: Integrated ML Predictor
# ============================================================================

async def example_integrated_ml():
    """
    Example: Integrated ML Predictor (Learning System specific)
    """
    print("\n" + "="*70)
    print("EXAMPLE 5: Integrated ML Predictor")
    print("="*70)

    # Import integrated predictor
    engines_path = Path(__file__).parent.parent / "engines"
    sys.path.insert(0, str(engines_path))

    from ml_predictor_integrated import IntegratedMLPredictor

    ml_predictor = IntegratedMLPredictor()

    try:
        # Predict exercise success
        print("\n1. Predict exercise success:")
        team_composition = {
            'size': 12,
            'avg_competency': 0.75,
            'competency_variance': 0.1
        }

        historical_performance = [
            {'overall_score': 78, 'conducted_at': datetime.utcnow() - timedelta(days=90)},
            {'overall_score': 82, 'conducted_at': datetime.utcnow() - timedelta(days=60)},
            {'overall_score': 85, 'conducted_at': datetime.utcnow() - timedelta(days=30)}
        ]

        prediction = await ml_predictor.predict_exercise_success(
            scenario_type='cyber_incident',
            team_composition=team_composition,
            historical_performance=historical_performance,
            context={'user_id': 'user123'}
        )

        print(f"Predicted score: {prediction.get('predicted_score', 0):.1f}")
        print(f"Success probability: {prediction.get('success_probability', 0):.0%}")
        print(f"Risk level: {prediction.get('risk_level', 'unknown')}")
        print(f"Recommendations:")
        for rec in prediction.get('recommendations', []):
            print(f"  - {rec}")

        # Predict difficulty
        print("\n2. Predict scenario difficulty:")
        scenario_definition = {
            'type': 'cyber_incident',
            'complexity': 75,
            'objectives': ['Detect', 'Contain', 'Eradicate', 'Recover', 'Lessons']
        }

        target_audience = {
            'avg_competency': 0.65,
            'avg_experience_months': 18
        }

        difficulty = await ml_predictor.predict_difficulty_score(
            scenario_definition=scenario_definition,
            target_audience=target_audience
        )

        print(f"Difficulty score: {difficulty.get('difficulty_score', 0):.1f}/100")
        print(f"Difficulty level: {difficulty.get('difficulty_level', 'unknown')}")
        print(f"Recommended prep hours: {difficulty.get('recommended_preparation_hours', 0)}")

        # Get model performance
        print("\n3. Get model performance:")
        performance = await ml_predictor.get_model_performance()
        print(f"Performance data available for {len(performance)} model types")

        # Get feature importance
        print("\n4. Get feature importance:")
        importance = await ml_predictor.get_feature_importance('exercise_success')
        if importance:
            print("Top features:")
            sorted_features = sorted(importance.items(), key=lambda x: x[1], reverse=True)
            for feature, score in sorted_features[:5]:
                print(f"  - {feature}: {score:.2f}")
        else:
            print("Feature importance not available (service not running)")

    finally:
        await ml_predictor.close()

    print("\n✓ Integrated ML Predictor example complete\n")


# ============================================================================
# Example 6: Unified Workflow
# ============================================================================

async def example_unified_workflow():
    """
    Example: Unified workflow combining multiple services
    """
    print("\n" + "="*70)
    print("EXAMPLE 6: Unified Workflow")
    print("="*70)

    # Import integrated components
    engines_path = Path(__file__).parent.parent / "engines"
    sys.path.insert(0, str(engines_path))

    from ml_predictor_integrated import IntegratedMLPredictor
    from knowledge_base_connector_integrated import IntegratedKnowledgeConnector

    ml_predictor = IntegratedMLPredictor()
    kb_connector = IntegratedKnowledgeConnector()

    try:
        print("\n🎯 Scenario: Planning new exercise")
        print("-" * 70)

        # Step 1: Predict success
        print("\n📊 Step 1: Predict exercise success")
        team_composition = {
            'size': 12,
            'avg_competency': 0.55,  # Low competency
            'competency_variance': 0.15
        }

        historical_performance = [
            {'overall_score': 65, 'conducted_at': datetime.utcnow() - timedelta(days=60)},
            {'overall_score': 68, 'conducted_at': datetime.utcnow() - timedelta(days=30)}
        ]

        prediction = await ml_predictor.predict_exercise_success(
            scenario_type='cyber_incident',
            team_composition=team_composition,
            historical_performance=historical_performance
        )

        print(f"  Predicted score: {prediction.get('predicted_score', 0):.1f}/100")
        print(f"  Risk level: {prediction.get('risk_level', 'unknown').upper()}")

        # Step 2: If risk is medium/high, search for training resources
        if prediction.get('risk_level') in ['medium', 'high']:
            print("\n📚 Step 2: Search for training resources (risk is medium/high)")

            resources = await kb_connector.search_resources_for_gap(
                gap_keyword='cyber_incident',
                competency_level='intermediate'
            )

            print(f"  Found {len(resources)} resources")

            # Step 3: Create learning path
            print("\n🎓 Step 3: Create learning path")
            learning_path = await kb_connector.create_learning_path_from_resources(
                user_id="user123",
                competency_gap="cyber_incident",
                resources=resources
            )

            print(f"  Learning path created:")
            print(f"    - {len(learning_path.get('path', []))} resources")
            print(f"    - Estimated hours: {learning_path.get('estimated_hours', 0)}")
            print(f"  Resources:")
            for item in learning_path.get('path', [])[:3]:
                print(f"    {item.get('order')}. {item.get('title')} ({item.get('duration_hours')}h)")

        print("\n✅ Workflow complete: Exercise planned with preparation resources")

    finally:
        await ml_predictor.close()
        await kb_connector.close()

    print("\n✓ Unified workflow example complete\n")


# ============================================================================
# Run All Examples
# ============================================================================

async def main():
    """Run all examples"""
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*20 + "PLATFORM INTEGRATION EXAMPLES" + " "*20 + "║")
    print("╚" + "="*68 + "╝")

    try:
        await example_rag_semantic_search()
        await example_ml_predictions()
        await example_knowledge_base()
        await example_integrated_knowledge()
        await example_integrated_ml()
        await example_unified_workflow()

        print("\n" + "="*70)
        print("✅ ALL EXAMPLES COMPLETED SUCCESSFULLY")
        print("="*70)
        print("\nNote: Some examples may show 'service not running' messages.")
        print("This is expected when RAG/ML Platform/KB services are not started.")
        print("Examples will use fallback modes in that case.\n")

    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
