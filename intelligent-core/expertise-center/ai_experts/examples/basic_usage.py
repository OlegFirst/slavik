"""
Basic Usage Examples for AI Experts

Demonstrates how to use the AI Experts module.
"""

import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def example_bcm_advisor():
    """Example: Using BCM Advisor"""
    from ai_experts.specialists.bcm_advisor import BCMAdvisor

    print("\n=== BCM Advisor Example ===\n")

    # Initialize BCM Advisor
    advisor = BCMAdvisor()

    # Prepare context
    context = {
        'industry': 'healthcare',
        'size': 'medium',
        'module': 'BIA',
        'current_stage': 'identify_processes',
        'progress': 30
    }

    # Get advice
    advice = await advisor.advise(
        query="How should I identify critical processes for a healthcare organization?",
        context=context
    )

    print("BCM Advisor Response:")
    print(advice)
    print()


async def example_compliance_auditor():
    """Example: Using Compliance Auditor"""
    from ai_experts.specialists.compliance_auditor import ComplianceAuditor

    print("\n=== Compliance Auditor Example ===\n")

    # Initialize Compliance Auditor
    auditor = ComplianceAuditor()

    # Prepare context
    context = {
        'industry': 'finance',
        'size': 'large',
        'module': 'BIA',
        'current_stage': 'documentation'
    }

    # Check compliance
    advice = await auditor.advise(
        query="What evidence do I need for ISO 22301 clause 8.2.2?",
        context=context
    )

    print("Compliance Auditor Response:")
    print(advice)
    print()


async def example_strategic_planner():
    """Example: Using Strategic Planner"""
    from ai_experts.specialists.strategic_planner import StrategicPlanner

    print("\n=== Strategic Planner Example ===\n")

    # Initialize Strategic Planner
    planner = StrategicPlanner()

    # Prepare context
    context = {
        'industry': 'technology',
        'size': 'small',
        'module': 'full-iso22301',
        'maturity': 2
    }

    # Get strategic plan
    advice = await planner.advise(
        query="How long will it take to achieve ISO 22301 certification?",
        context=context
    )

    print("Strategic Planner Response:")
    print(advice)
    print()


async def example_case_search():
    """Example: Searching case library"""
    from ai_experts.tools.case_library_tool import CaseSearchTool

    print("\n=== Case Search Example ===\n")

    # Initialize case search tool
    tool = CaseSearchTool()

    # Search for relevant cases
    results = await tool.execute(
        query="healthcare BIA implementation",
        industry="healthcare",
        module="BIA",
        max_results=3
    )

    print(f"Found {results['total_results']} relevant cases:")
    for i, case in enumerate(results['cases'], 1):
        print(f"\n{i}. {case['title']}")
        print(f"   Industry: {case['industry']}, Size: {case['org_size']}")
        print(f"   Summary: {case['summary'][:100]}...")

    print(f"\nKey Insights:")
    for insight in results['key_insights']:
        print(f"  - {insight}")
    print()


async def example_workflow_prediction():
    """Example: Workflow prediction"""
    from ai_experts.ml.predictive_models import WorkflowPredictor

    print("\n=== Workflow Prediction Example ===\n")

    # Initialize predictor
    predictor = WorkflowPredictor()

    # Prepare data
    org_context = {
        'size': 'medium',
        'maturity': 3,
        'industry': 'healthcare'
    }

    current_progress = {
        'current_stage_index': 2,
        'total_stages': 6,
        'complexity_score': 4,
        'ai_usage_count': 5,
        'challenges': []
    }

    # Predict journey
    prediction = await predictor.predict_journey(
        org_context=org_context,
        current_state='strategy',
        current_progress=current_progress
    )

    print("Workflow Prediction:")
    print(f"  Current Stage Duration: {prediction['current_stage_prediction']['estimated_duration_hours']} hours")
    print(f"  Stuck Probability: {prediction['stuck_probability']['probability']} ({prediction['stuck_probability']['risk_level']} risk)")
    print(f"  Expert Help Needed: {prediction['expert_help_needed']}")
    print(f"  Total Completion Estimate: {prediction['total_completion_estimate']['estimated_days']} days")

    print(f"\nRecommendations:")
    for rec in prediction['recommendations']:
        print(f"  - {rec}")
    print()


async def example_rag_pipeline():
    """Example: RAG Pipeline"""
    from ai_experts.rag.pipeline import RAGPipeline

    print("\n=== RAG Pipeline Example ===\n")

    # Initialize RAG pipeline
    pipeline = RAGPipeline()

    # Ingest documents
    documents = [
        {
            'text': 'ISO 22301:2019 Clause 8.2.2 requires organizations to conduct Business Impact Analysis to identify critical activities and their dependencies.',
            'metadata': {'source': 'iso_standard', 'clause': '8.2.2'}
        },
        {
            'text': 'Critical processes should be identified through stakeholder workshops and process mapping exercises.',
            'metadata': {'source': 'best_practice', 'topic': 'bia'}
        }
    ]

    await pipeline.ingest_documents(documents, source_type='iso_standard')

    # Retrieve relevant knowledge
    results = await pipeline.retrieve(
        query="How to identify critical processes?",
        context={'module': 'BIA'},
        top_k=2
    )

    print("RAG Retrieval Results:")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. Source: {result['source']}")
        print(f"   Score: {result['score']:.3f}")
        print(f"   Content: {result['content'][:100]}...")
    print()


async def main():
    """Run all examples"""
    print("=" * 60)
    print("AI Experts Module - Usage Examples")
    print("=" * 60)

    await example_bcm_advisor()
    await example_compliance_auditor()
    await example_strategic_planner()
    await example_case_search()
    await example_workflow_prediction()
    await example_rag_pipeline()

    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
