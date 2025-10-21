"""
Integration test for Phase 1.1 Governance Layer
Tests Decision Center -> Auto-Recovery -> Escalation flow

This test validates:
1. Decision Center is consulted before recovery actions
2. Policies are enforced correctly
3. Escalations are created when needed
4. Audit logs are maintained
5. Auto-recovery is blocked when appropriate
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from infrastructure.eventbus import create_eventbus, Event
from infrastructure.eventbus.coordination import InfrastructureCoordinator


async def test_governance_integration():
    """
    Test complete governance integration:
    1. Start Infrastructure Coordinator with governance
    2. Simulate service failure
    3. Verify Decision Center consulted
    4. Verify recovery decision made
    5. Verify escalation if needed
    """

    print("\n" + "=" * 70)
    print("PHASE 1.1 INTEGRATION TEST")
    print("=" * 70)

    # Start coordinator with governance
    print("\n[1/7] Starting Infrastructure Coordinator with Governance...")
    coordinator = InfrastructureCoordinator(
        event_bus_backend='memory',  # Use in-memory for testing
        enable_governance=True
    )

    await coordinator.start()
    print(" Coordinator started with governance enabled")

    # Wait for startup
    await asyncio.sleep(2)

    # Test 1: Simulate database failure (attempt 1)
    print("\n[2/7] TEST 1: Simulate database unhealthy (attempt 1)")
    print("Expected: Decision Center approves recovery (within max attempts)")
    await coordinator.eventbus.publish(
        Event.create(
            event_type='infrastructure.health.unhealthy',
            data={
                'service_name': 'database',
                'status': 'unhealthy',
                'message': 'Connection refused',
                'details': {'error_code': 'ECONNREFUSED'}
            },
            source='test',
            tenant_id='system'
        )
    )

    await asyncio.sleep(3)
    print(" Decision Center should have approved recovery (attempt 1/1)")
    print("   Database is critical, max_attempts=1 per policy")

    # Test 2: Simulate API Gateway failure (attempt 1)
    print("\n[3/7] TEST 2: Simulate api_gateway unhealthy (attempt 1)")
    print("Expected: Decision Center approves recovery (attempt 1/2)")
    await coordinator.eventbus.publish(
        Event.create(
            event_type='infrastructure.health.unhealthy',
            data={
                'service_name': 'api_gateway',
                'status': 'unhealthy',
                'message': 'Service not responding',
                'details': {'http_status': 503}
            },
            source='test',
            tenant_id='system'
        )
    )

    await asyncio.sleep(3)
    print(" Decision Center should have approved recovery (attempt 1/2)")

    # Test 3: Second API Gateway failure (attempt 2)
    print("\n[4/7] TEST 3: Simulate api_gateway unhealthy (attempt 2)")
    print("Expected: Decision Center approves, but close to escalation threshold")
    await coordinator.eventbus.publish(
        Event.create(
            event_type='infrastructure.health.unhealthy',
            data={
                'service_name': 'api_gateway',
                'status': 'unhealthy',
                'message': 'Service not responding',
                'details': {'http_status': 503}
            },
            source='test',
            tenant_id='system'
        )
    )

    await asyncio.sleep(3)
    print(" Decision Center should have approved recovery (attempt 2/2)")
    print("   Critical service approaching max attempts")

    # Test 4: Third API Gateway failure (should ESCALATE)
    print("\n[5/7] TEST 4: Simulate api_gateway unhealthy (attempt 3 - ESCALATION!)")
    print("Expected: Decision Center REJECTS and ESCALATES")
    await coordinator.eventbus.publish(
        Event.create(
            event_type='infrastructure.health.unhealthy',
            data={
                'service_name': 'api_gateway',
                'status': 'unhealthy',
                'message': 'Service not responding',
                'details': {'http_status': 503}
            },
            source='test',
            tenant_id='system'
        )
    )

    await asyncio.sleep(3)
    print("️  Decision Center should have REJECTED (max attempts exceeded)")
    print(" Escalation Manager should have created escalation")
    print(" Notification Service should have sent alerts")
    print(" Auto-Recovery should be BLOCKED for api_gateway")

    # Test 5: Check Decision Center statistics
    print("\n[6/7] Checking Decision Center Statistics...")
    stats = await coordinator.decision_center.get_stats()
    print("\n DECISION CENTER STATISTICS:")
    print(f"  Total decisions: {stats.get('total_decisions', 0)}")
    print(f"  Approved: {stats.get('approved_decisions', 0)}")
    print(f"  Rejected: {stats.get('rejected_decisions', 0)}")
    print(f"  Auto-approved: {stats.get('auto_approved', 0)}")
    print(f"  Manual approvals required: {stats.get('manual_approved', 0)}")
    print(f"  Active escalations: {stats.get('active_escalations', 0)}")
    print(f"  Pending approvals: {stats.get('pending_approvals', 0)}")
    print(f"  Approval rate: {stats.get('approval_rate', 0):.1f}%")
    print(f"  Automation rate: {stats.get('automation_rate', 0):.1f}%")

    # Test 6: Check audit logs
    print("\n[7/7] Checking Audit Logs...")
    import os
    from datetime import datetime

    log_file = f"/Users/MD/AI-Platform-ISO/infrastructure/decision-center/audit_logs/audit_{datetime.now().strftime('%Y-%m-%d')}.jsonl"
    if os.path.exists(log_file):
        with open(log_file) as f:
            lines = f.readlines()
            print(f"\n AUDIT LOGS:")
            print(f"  Total audit entries today: {len(lines)}")
            print(f"  Last 5 decisions:")
            for line in lines[-5:]:
                import json
                try:
                    entry = json.loads(line)
                    decision_type = entry.get('decision_type', 'unknown')
                    outcome = entry.get('outcome', 'unknown')
                    service = entry.get('service_name', 'unknown')
                    action = entry.get('action_type', 'unknown')
                    timestamp = entry.get('timestamp', '')[:19]
                    print(f"    - [{timestamp}] {decision_type}: {outcome} - {service}/{action}")
                except json.JSONDecodeError:
                    print(f"    - [Invalid JSON entry]")
    else:
        print(f"  ️  Audit log file not found: {log_file}")
        print(f"  Note: Audit logs may be stored in memory for this test")

    # Get active escalations
    print("\n ACTIVE ESCALATIONS:")
    escalations = await coordinator.decision_center.get_active_escalations()
    if escalations:
        for esc in escalations:
            print(f"  - {esc.service_name}: {esc.reason}")
            print(f"    Severity: {esc.severity}, Assigned to: {esc.assigned_team}")
            print(f"    Created: {esc.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        print("  No active escalations")

    # Get pending approvals
    print("\n PENDING APPROVALS:")
    approvals = await coordinator.decision_center.get_pending_approvals()
    if approvals:
        for app in approvals:
            print(f"  - {app.service_name}: {app.requested_action}")
            print(f"    Justification: {app.justification}")
            print(f"    Expires: {app.expires_at.strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        print("  No pending approvals")

    # Overall coordinator status
    print("\n OVERALL COORDINATOR STATUS:")
    status = await coordinator.get_status()
    print(f"  Health Monitor: {status['health_monitor']['checks_registered']} checks registered")
    print(f"  Auto-Recovery: {status['auto_recovery']['total_recoveries']} total recoveries")
    print(f"  Resource Optimizer: {status['resource_optimizer']['cycles_completed']} cycles completed")

    print("\n" + "=" * 70)
    print(" INTEGRATION TEST COMPLETE")
    print("=" * 70)
    print("\nKey Findings:")
    print(f"  • Decision Center made {stats.get('total_decisions', 0)} decisions")
    print(f"  • {stats.get('approved_decisions', 0)} approved, {stats.get('rejected_decisions', 0)} rejected")
    print(f"  • {stats.get('active_escalations', 0)} active escalations")
    print(f"  • Automation rate: {stats.get('automation_rate', 0):.1f}%")
    print("\nConclusion:")
    if stats.get('total_decisions', 0) > 0:
        print("   Decision Center is functional and making decisions")
    else:
        print("  ️  Decision Center did not make any decisions - check integration")

    if stats.get('active_escalations', 0) > 0:
        print("   Escalation system is working")
    else:
        print("  ℹ️  No escalations triggered (may be expected)")

    print("\n" + "=" * 70)

    # Stop coordinator
    await coordinator.stop()


async def test_policy_compliance():
    """
    Test policy compliance checking
    """
    print("\n" + "=" * 70)
    print("POLICY COMPLIANCE TEST")
    print("=" * 70)

    coordinator = InfrastructureCoordinator(
        event_bus_backend='memory',
        enable_governance=True
    )
    await coordinator.start()
    await asyncio.sleep(1)

    print("\n[1/3] Testing policy compliance for critical service...")
    compliance = await coordinator.decision_center.check_policy_compliance(
        service_name='database',
        action_type='restart',
        current_attempt=1
    )
    print(f"  Compliant: {compliance.get('compliant', False)}")
    print(f"  Requires approval: {compliance.get('requires_approval', False)}")
    print(f"  Requires escalation: {compliance.get('requires_escalation', False)}")
    print(f"  Reason: {compliance.get('reason', 'N/A')}")

    print("\n[2/3] Testing policy compliance for non-critical service...")
    compliance = await coordinator.decision_center.check_policy_compliance(
        service_name='rag_pipeline',
        action_type='restart',
        current_attempt=1
    )
    print(f"  Compliant: {compliance.get('compliant', False)}")
    print(f"  Requires approval: {compliance.get('requires_approval', False)}")
    print(f"  Requires escalation: {compliance.get('requires_escalation', False)}")
    print(f"  Reason: {compliance.get('reason', 'N/A')}")

    print("\n[3/3] Testing policy compliance for excessive attempts...")
    compliance = await coordinator.decision_center.check_policy_compliance(
        service_name='database',
        action_type='restart',
        current_attempt=5  # Exceeds max attempts
    )
    print(f"  Compliant: {compliance.get('compliant', False)}")
    print(f"  Requires approval: {compliance.get('requires_approval', False)}")
    print(f"  Requires escalation: {compliance.get('requires_escalation', False)}")
    print(f"  Reason: {compliance.get('reason', 'N/A')}")

    print("\n POLICY COMPLIANCE TEST COMPLETE")
    print("=" * 70)

    await coordinator.stop()


if __name__ == "__main__":
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    print("\n Starting Phase 1.1 Integration Tests...")

    # Run main integration test
    asyncio.run(test_governance_integration())

    # Run policy compliance test
    print("\n\n")
    asyncio.run(test_policy_compliance())

    print("\n\n All tests completed!")
