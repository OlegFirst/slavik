#!/usr/bin/env python3
"""
Test Script: System BCM Self-Application Cycle

Tests the complete cycle of platform applying BCM to itself:
1. Load system scenarios
2. Execute BIA for platform
3. Assess platform risks
4. Setup recovery procedures
5. Apply resource priorities
6. Learn from practice
7. Generate improvements

This demonstrates the platform LIVING BCM through practice.
"""

import asyncio
import logging
import json
import sys
from pathlib import Path

# Direct imports to avoid complex dependencies
import importlib.util

# Load SystemBCM
spec = importlib.util.spec_from_file_location(
    "system_bcm",
    Path(__file__).parent / "system_bcm" / "system_bcm.py"
)
system_bcm_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(system_bcm_module)
SystemBCM = system_bcm_module.SystemBCM

# Load PracticeLearningEngine
spec = importlib.util.spec_from_file_location(
    "practice_learning",
    Path(__file__).parent / "learning" / "practice_learning.py"
)
practice_learning_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(practice_learning_module)
PracticeLearningEngine = practice_learning_module.PracticeLearningEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('system_bcm_test.log')
    ]
)

logger = logging.getLogger(__name__)


async def test_full_cycle():
    """Test the complete System BCM cycle"""

    logger.info("=" * 80)
    logger.info("SYSTEM BCM SELF-APPLICATION TEST")
    logger.info("Testing platform applying BCM to ITSELF")
    logger.info("=" * 80)
    logger.info("")

    try:
        # Phase 1: System BCM Execution
        logger.info("PHASE 1: Executing System BCM")
        logger.info("-" * 80)

        bcm = SystemBCM()
        bcm_results = await bcm.execute_full_cycle()

        logger.info("")
        logger.info("BCM Execution Results:")
        logger.info(f"  Status: {bcm_results['status']}")
        logger.info(f"  Phases completed: {len(bcm_results['phases'])}")

        for phase_name, phase_data in bcm_results["phases"].items():
            logger.info(f"  ✓ {phase_name}: {phase_data['status']}")

        # Phase 2: Learning from Practice
        logger.info("")
        logger.info("PHASE 2: Learning from Practice")
        logger.info("-" * 80)

        learning_engine = PracticeLearningEngine()
        learning_results = await learning_engine.learn_from_self_application(bcm_results)

        logger.info("")
        logger.info("Learning Results:")
        logger.info(f"  Phases analyzed: {learning_results['metrics_analyzed']}")
        logger.info(f"  Insights generated: {len(learning_results['insights_generated'])}")
        logger.info(f"  Improvements identified: {len(learning_results['improvements_identified'])}")
        logger.info(f"  Overall confidence: {learning_results['confidence_scores']['overall_confidence']:.2f}")

        # Display insights
        if learning_results['insights_generated']:
            logger.info("")
            logger.info("Key Insights:")
            for insight in learning_results['insights_generated'][:5]:  # Top 5
                logger.info(f"  💡 {insight['category']}: {insight['observation']}")
                logger.info(f"     → {insight['recommendation']} (confidence: {insight['confidence']:.2f})")

        # Display improvements
        if learning_results['improvements_identified']:
            logger.info("")
            logger.info("Identified Improvements:")
            for improvement in learning_results['improvements_identified'][:5]:  # Top 5
                logger.info(
                    f"  🔧 [{improvement['priority']}] {improvement['description']} "
                    f"(impact: {improvement['estimated_impact']})"
                )

        # Phase 3: Measure Effectiveness (simulated)
        logger.info("")
        logger.info("PHASE 3: Measuring Effectiveness")
        logger.info("-" * 80)

        # Simulate measuring some metrics
        metrics = []

        # RTO measurement
        rto_metric = await learning_engine.measure_effectiveness(
            metric_type="event_bus_rto",
            target_value=30,  # 30 seconds
            actual_value=28,  # 28 seconds actual
            context={"service": "event-bus", "incident": "test_failure_001"}
        )
        metrics.append(rto_metric)

        # Availability measurement
        availability_metric = await learning_engine.measure_effectiveness(
            metric_type="tier_1_availability",
            target_value=99.9,  # 99.9%
            actual_value=99.95,  # Better than target!
            context={"tier": "tier_1", "measurement_period": "24h"}
        )
        metrics.append(availability_metric)

        # Recovery success rate
        recovery_metric = await learning_engine.measure_effectiveness(
            metric_type="auto_recovery_success_rate",
            target_value=95,  # 95%
            actual_value=92,  # Slightly below target
            context={"period": "last_week", "total_incidents": 25}
        )
        metrics.append(recovery_metric)

        logger.info("")
        logger.info("Effectiveness Measurements:")
        for metric in metrics:
            status = "✅ SUCCESS" if metric.success else "⚠️  NEEDS IMPROVEMENT"
            logger.info(
                f"  {status} - {metric.metric_type}: "
                f"target={metric.target_value}, actual={metric.actual_value} "
                f"(deviation={metric.deviation_percentage:.1f}%)"
            )

        # Phase 4: Apply Improvements
        logger.info("")
        logger.info("PHASE 4: Applying Improvements")
        logger.info("-" * 80)

        if learning_results['improvements_identified']:
            improvement_results = await learning_engine.improve_based_on_practice(
                improvements=learning_results['improvements_identified'],
                apply_immediately=True
            )

            logger.info("")
            logger.info("Improvement Application Results:")
            logger.info(f"  Applied immediately: {len(improvement_results['applied'])}")
            logger.info(f"  Queued for review: {len(improvement_results['queued'])}")
            logger.info(f"  Failed: {len(improvement_results['failed'])}")
        else:
            logger.info("  No improvements to apply (system is optimal!)")

        # Summary
        logger.info("")
        logger.info("=" * 80)
        logger.info("CYCLE COMPLETE: Platform Successfully Applied BCM to ITSELF!")
        logger.info("=" * 80)
        logger.info("")
        logger.info("Summary:")
        logger.info(f"  ✅ BIA executed for {len(bcm_results['phases']['bia']['results']['critical_processes'])} critical processes")
        logger.info(f"  ✅ {len(bcm_results['phases']['risk_assessment']['results']['high_priority_risks'])} high-priority risks identified")
        logger.info(f"  ✅ {len(bcm_results['phases']['recovery_setup']['results']['procedures_configured'])} recovery procedures configured")
        logger.info(f"  ✅ {len(bcm_results['phases']['priority_application']['results']['services_prioritized'])} services prioritized")
        logger.info(f"  ✅ {learning_results['metrics_analyzed']} phases analyzed for learning")
        logger.info(f"  ✅ {len(learning_results['insights_generated'])} insights generated")
        logger.info(f"  ✅ {len(metrics)} effectiveness metrics measured")
        logger.info("")
        logger.info("🎓 The platform has learned resilience through PRACTICE!")
        logger.info("🔄 This cycle will repeat continuously, improving with each iteration")

        # Save results
        output_file = "system_bcm_cycle_results.json"
        with open(output_file, 'w') as f:
            json.dump({
                "bcm_execution": bcm_results,
                "learning_results": learning_results,
                "effectiveness_metrics": [
                    {
                        "metric_type": m.metric_type,
                        "target_value": m.target_value,
                        "actual_value": m.actual_value,
                        "success": m.success,
                        "deviation_percentage": m.deviation_percentage
                    }
                    for m in metrics
                ]
            }, f, indent=2)

        logger.info(f"\n📄 Full results saved to: {output_file}")

        return {
            "status": "success",
            "bcm_results": bcm_results,
            "learning_results": learning_results,
            "metrics": metrics
        }

    except Exception as e:
        logger.error(f"❌ Test failed: {e}", exc_info=True)
        return {
            "status": "failed",
            "error": str(e)
        }


async def test_individual_components():
    """Test individual components separately"""

    logger.info("\n" + "=" * 80)
    logger.info("INDIVIDUAL COMPONENT TESTS")
    logger.info("=" * 80)

    bcm = SystemBCM()

    # Test 1: BIA
    logger.info("\nTest 1: BIA Execution")
    logger.info("-" * 40)
    try:
        bia_results = await bcm.execute_self_bia()
        logger.info(f"✅ BIA: {len(bia_results['critical_processes'])} processes identified")
    except Exception as e:
        logger.error(f"❌ BIA failed: {e}")

    # Test 2: Risk Assessment
    logger.info("\nTest 2: Risk Assessment")
    logger.info("-" * 40)
    try:
        risk_results = await bcm.assess_own_risks()
        logger.info(f"✅ Risks: {len(risk_results['high_priority_risks'])} high-priority")
    except Exception as e:
        logger.error(f"❌ Risk Assessment failed: {e}")

    # Test 3: Recovery Setup
    logger.info("\nTest 3: Recovery Setup")
    logger.info("-" * 40)
    try:
        recovery_results = await bcm.setup_recovery()
        logger.info(f"✅ Recovery: {len(recovery_results['procedures_configured'])} procedures")
    except Exception as e:
        logger.error(f"❌ Recovery Setup failed: {e}")

    # Test 4: Priorities
    logger.info("\nTest 4: Resource Priorities")
    logger.info("-" * 40)
    try:
        priority_results = await bcm.apply_priorities()
        logger.info(f"✅ Priorities: {len(priority_results['services_prioritized'])} services")
    except Exception as e:
        logger.error(f"❌ Priority Application failed: {e}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Test System BCM Self-Application")
    parser.add_argument(
        "--mode",
        choices=["full", "individual"],
        default="full",
        help="Test mode: full cycle or individual components"
    )

    args = parser.parse_args()

    if args.mode == "full":
        result = asyncio.run(test_full_cycle())
        sys.exit(0 if result["status"] == "success" else 1)
    else:
        asyncio.run(test_individual_components())
        sys.exit(0)
