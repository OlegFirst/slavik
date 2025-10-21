"""
Basic BIA Workflow Example

Demonstrates complete workflow from start to completion using
Workflow Intelligence Engine with Governance.
"""

import asyncio
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

async def run_bia_workflow():
    """Complete BIA workflow example"""

    print("=" * 70)
    print("WORKFLOW INTELLIGENCE ENGINE - BIA Example")
    print("=" * 70)

    # Import after path setup
    try:
        from workflow_intelligence.workflows.bia_workflow import BIAWorkflowEngine
        from workflow_intelligence.governance.rules_engine import RulesEngine
        from workflow_intelligence.governance.bia_rules import BIARules
        from workflow_intelligence.governance.creative_zones import CreativeZonesManager, BIACreativeZones
        from workflow_intelligence.governance.checkpoint_manager import CheckpointManager, BIACheckpoints
    except ImportError as e:
        print(f" Import error: {e}")
        print("\n Make sure you're running from project root:")
        print("   python intelligent-core/workflow_intelligence/examples/basic_bia_workflow.py")
        return

    # 1. Initialize BIA Workflow
    print("\n1️⃣  Initializing BIA Workflow...")
    bia = BIAWorkflowEngine(organization_id='org_healthcare_123')
    print(f"   Current stage: {bia.current_stage.value}")

    # 2. Initialize Governance
    print("\n2️⃣  Setting up Governance System...")

    # Rules Engine
    rules = RulesEngine()
    rules.register_rules(BIARules.get_all_rules())
    print(f"   Registered {len(rules.rules)} rules")

    # Creative Zones
    zones = CreativeZonesManager()
    zones.register_zones(BIACreativeZones.get_all_zones())
    print(f"   Registered {len(zones.zones)} creative zones")

    # Checkpoints
    checkpoints = CheckpointManager(rules, zones)
    checkpoints.register_checkpoints(BIACheckpoints.get_all_checkpoints())
    print(f"   Registered {len(checkpoints.checkpoints)} checkpoints")

    # 3. STAGE 1: Identify Processes
    print("\n3️⃣  STAGE 1: Identify Processes")

    processes = [
        {
            'name': 'Patient Records System (EMR)',
            'description': 'Electronic Medical Records system',
            'criticality': 'critical',
            'owner': 'Dr. Smith, Chief Medical Officer'
        },
        {
            'name': 'Patient Admission System',
            'description': 'Patient intake and admission workflow',
            'criticality': 'high',
            'owner': 'Jane Doe, Operations Manager'
        },
        {
            'name': 'Billing System',
            'description': 'Patient billing and insurance claims',
            'criticality': 'medium',
            'owner': 'Finance Department'
        }
    ]

    for process in processes:
        await bia.add_process(process)
        print(f"    Added: {process['name']}")

    # Validate stage
    print("\n   Validating stage...")
    violations = await rules.validate(bia.get_context(), stage='identify_processes')
    if violations:
        print(f"   ️  {len(violations)} violations:")
        for v in violations:
            print(f"      - {v.message} ({v.severity.value})")
    else:
        print("    No violations")

    # Try to advance
    if bia.can_advance_to('analyze_dependencies'):
        await bia.transition_to('analyze_dependencies')
        print(f"\n   → Advanced to: {bia.current_stage.value}")
    else:
        print("    Cannot advance yet")

    # 4. STAGE 2: Analyze Dependencies
    print("\n4️⃣  STAGE 2: Analyze Dependencies")

    dependencies = [
        {
            'from_process': 'Patient Records System (EMR)',
            'to_process': 'External Lab System',
            'dependency_type': 'external',
            'criticality': 'high',
            'description': 'Lab results integration'
        },
        {
            'from_process': 'Patient Records System (EMR)',
            'to_process': 'Backup Power System',
            'dependency_type': 'infrastructure',
            'criticality': 'critical',
            'description': 'Requires continuous power'
        },
        {
            'from_process': 'Billing System',
            'to_process': 'Patient Records System (EMR)',
            'dependency_type': 'internal',
            'criticality': 'high',
            'description': 'Requires patient data for billing'
        }
    ]

    for dep in dependencies:
        await bia.add_dependency(dep)
        print(f"    Dependency: {dep['from_process']} → {dep['to_process']}")

    # Check checkpoint
    print("\n   Checkpoint: Dependencies Mapped")
    checkpoint_result = await checkpoints.validate_checkpoint(
        'dependencies_mapped',
        bia.get_context(),
        'analyze_dependencies'
    )

    if checkpoint_result.passed:
        print("    Checkpoint passed")
    else:
        print(f"   ️  Checkpoint failed: {len(checkpoint_result.violations)} violations")
        if checkpoint_result.requires_escalation:
            print("   ️  ESCALATION REQUIRED")

    # Advance
    if bia.can_advance_to('assess_impact'):
        await bia.transition_to('assess_impact')
        print(f"\n   → Advanced to: {bia.current_stage.value}")

    # 5. STAGE 3: Assess Impact
    print("\n5️⃣  STAGE 3: Assess Impact")

    impacts = [
        {
            'process_name': 'Patient Records System (EMR)',
            'financial_impact': {
                'hourly_loss': 50000,
                'description': 'Cannot admit patients, surgeries delayed'
            },
            'operational_impact': {
                'severity': 'critical',
                'description': 'Complete halt of patient care documentation'
            },
            'reputational_impact': {
                'severity': 'high',
                'description': 'Patient safety concerns, regulatory issues'
            }
        },
        {
            'process_name': 'Billing System',
            'financial_impact': {
                'hourly_loss': 10000,
                'description': 'Revenue collection delayed'
            },
            'operational_impact': {
                'severity': 'medium',
                'description': 'Manual billing required'
            },
            'reputational_impact': {
                'severity': 'low',
                'description': 'Minimal patient-facing impact'
            }
        }
    ]

    for impact in impacts:
        await bia.assess_impact(impact)
        print(f"    Impact assessed: {impact['process_name']}")

    # Creative Zone check
    zone = zones.get_zone('impact_analysis')
    if zone:
        print(f"\n   Creative Zone: {zone.name}")
        print(f"   Creativity Level: {zone.creativity_level.value}")
        print(f"   AI can: {', '.join(zone.allowed_approaches[:2])}")

    # Advance
    if bia.can_advance_to('determine_rto'):
        await bia.transition_to('determine_rto')
        print(f"\n   → Advanced to: {bia.current_stage.value}")

    # 6. STAGE 4: Determine RTO
    print("\n6️⃣  STAGE 4: Determine RTO/RPO")

    rtos = [
        {
            'process_name': 'Patient Records System (EMR)',
            'rto_hours': 2,
            'rpo_hours': 0.5,
            'rationale': 'Critical for patient care, must restore within 2h. Data loss max 30min acceptable.'
        },
        {
            'process_name': 'Billing System',
            'rto_hours': 24,
            'rpo_hours': 4,
            'rationale': 'Can operate manually for 24h. 4h data loss acceptable for billing.'
        }
    ]

    for rto in rtos:
        await bia.set_recovery_objective(rto)
        print(f"    RTO set: {rto['process_name']} - {rto['rto_hours']}h")

    # Validate RTO checkpoint
    print("\n   Checkpoint: RTO Determination Valid")
    checkpoint_result = await checkpoints.validate_checkpoint(
        'rto_determination_valid',
        bia.get_context(),
        'determine_rto'
    )

    if checkpoint_result.passed:
        print("    Checkpoint passed")
    else:
        print(f"   ️  Violations: {len(checkpoint_result.violations)}")

    # Advance
    if bia.can_advance_to('review_results'):
        await bia.transition_to('review_results')
        print(f"\n   → Advanced to: {bia.current_stage.value}")

    # 7. STAGE 5: Review & Complete
    print("\n7️⃣  STAGE 5: Review Results")

    # Final checkpoint
    print("\n   Final Checkpoint Validation...")
    checkpoint_result = await checkpoints.validate_checkpoint(
        'final_bia_validation',
        bia.get_context(),
        'review_results'
    )

    if checkpoint_result.passed:
        print("    All validations passed!")

        if bia.can_advance_to('completed'):
            await bia.transition_to('completed')
            print(f"\n    BIA COMPLETED!")
            print(f"   Final stage: {bia.current_stage.value}")
    else:
        print(f"   ️  Final validation failed: {len(checkpoint_result.violations)} issues")
        for v in checkpoint_result.violations:
            print(f"      - {v.message}")

    # 8. Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    context = bia.get_context()
    print(f"Processes identified: {len(context.get('processes', []))}")
    print(f"Dependencies mapped: {len(context.get('dependencies', []))}")
    print(f"Impacts assessed: {len(context.get('impacts', []))}")
    print(f"RTOs determined: {len(context.get('recovery_objectives', []))}")
    print(f"\nFinal stage: {bia.current_stage.value}")

    print("\n" + "=" * 70)
    print(" Example completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(run_bia_workflow())
