"""
Example Usage of Policy Engine
==============================

This script demonstrates how to use the Policy Engine.

Run with:
    python example_usage.py
"""

from pathlib import Path
from policy_engine import PolicyEngine


def main():
    print("Policy Engine Example")
    print("=" * 60)

    # Load policies
    policy_file = Path(__file__).parent / "policies.yaml"
    engine = PolicyEngine(policy_file)

    # Get database policy
    db_policy = engine.get_recovery_policy("database")
    print(f"\nDatabase Recovery Policy:")
    print(f"  Priority: {db_policy.priority}")
    print(f"  RTO: {db_policy.rto_seconds}s")
    print(f"  Strategy: {db_policy.recovery_strategy.value}")

    # Get thresholds
    cpu_critical = engine.get_threshold("cpu", "critical")
    print(f"\nCPU Critical Threshold: {cpu_critical}%")

    # Check compliance
    compliance = engine.check_compliance("scale_up")
    print(f"\nScale Up Compliance:")
    print(f"  Requires Approval: {compliance['requires_approval']}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
