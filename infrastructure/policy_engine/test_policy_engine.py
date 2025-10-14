"""
Test Policy Engine
==================

Simple tests to verify policy engine functionality.

Run with:
    pytest test_policy_engine.py -v
"""

import pytest
from pathlib import Path
from .policy_engine import PolicyEngine, PolicyLoadError
from .policy_validator import validate_policy_file
from .policy_models import RecoveryStrategy


@pytest.fixture
def policy_file():
    """Get path to policies.yaml"""
    return Path(__file__).parent / "policies.yaml"


@pytest.fixture
def engine(policy_file):
    """Create policy engine instance"""
    return PolicyEngine(policy_file)


class TestPolicyValidation:
    """Test policy validation"""

    def test_validate_policies_yaml(self, policy_file):
        """Test that policies.yaml is valid"""
        is_valid, errors, warnings = validate_policy_file(policy_file)

        # Print warnings for visibility
        for warning in warnings:
            print(f"Warning: {warning}")

        # Should be valid
        assert is_valid, f"Policy validation failed: {errors}"

    def test_policy_structure(self, policy_file):
        """Test that policy file has correct structure"""
        engine = PolicyEngine(policy_file)

        metadata = engine.get_policy_metadata()
        assert metadata["loaded"] is True
        assert "version" in metadata
        assert "approved_by" in metadata


class TestRecoveryPolicies:
    """Test recovery policy queries"""

    def test_get_database_policy(self, engine):
        """Test getting database recovery policy"""
        policy = engine.get_recovery_policy("database")

        assert policy.priority == 1
        assert policy.rto_seconds == 120
        assert policy.rpo_seconds == 300
        assert policy.recovery_strategy == RecoveryStrategy.CIRCUIT_BREAKER
        assert "ops" in policy.notify_teams
        assert "dba" in policy.notify_teams

    def test_get_eventbus_policy(self, engine):
        """Test getting eventbus recovery policy"""
        policy = engine.get_recovery_policy("eventbus")

        assert policy.priority == 1
        assert policy.rto_seconds == 60
        assert policy.rpo_seconds == 0  # No data loss acceptable
        assert policy.escalate_immediately is True
        assert policy.recovery_strategy == RecoveryStrategy.RESTART

    def test_get_default_policy(self, engine):
        """Test getting default recovery policy for unknown service"""
        policy = engine.get_recovery_policy("unknown_service")

        # Should return default policy
        assert policy.priority == 3  # Medium
        assert policy.recovery_strategy == RecoveryStrategy.RESTART

    def test_service_priority(self, engine):
        """Test service priority retrieval"""
        # Critical services
        assert engine.get_service_priority("database") == 1
        assert engine.get_service_priority("eventbus") == 1
        assert engine.get_service_priority("monitoring") == 1

        # High priority services
        assert engine.get_service_priority("api_gateway") == 2
        assert engine.get_service_priority("mio_manager") == 2

        # Medium priority services
        assert engine.get_service_priority("rag_pipeline") == 3
        assert engine.get_service_priority("expertise_center") == 3


class TestOptimizationPolicies:
    """Test optimization policy queries"""

    def test_cpu_thresholds(self, engine):
        """Test CPU threshold retrieval"""
        assert engine.get_threshold("cpu", "normal") == 70
        assert engine.get_threshold("cpu", "high") == 80
        assert engine.get_threshold("cpu", "critical") == 90

    def test_memory_thresholds(self, engine):
        """Test memory threshold retrieval"""
        assert engine.get_threshold("memory", "normal") == 75
        assert engine.get_threshold("memory", "high") == 85
        assert engine.get_threshold("memory", "critical") == 95

    def test_disk_thresholds(self, engine):
        """Test disk threshold retrieval"""
        assert engine.get_threshold("disk", "normal") == 70
        assert engine.get_threshold("disk", "high") == 80
        assert engine.get_threshold("disk", "critical") == 90

    def test_threshold_progression(self, engine):
        """Test that thresholds are in ascending order"""
        for resource in ["cpu", "memory", "disk"]:
            normal = engine.get_threshold(resource, "normal")
            high = engine.get_threshold(resource, "high")
            critical = engine.get_threshold(resource, "critical")

            assert normal < high < critical


class TestCompliancePolicies:
    """Test compliance and action approval"""

    def test_scale_up_requires_approval(self, engine):
        """Test that scale_up requires approval"""
        compliance = engine.check_compliance("scale_up")

        assert compliance["requires_approval"] is True
        assert compliance["manual_only"] is True
        assert compliance["auto_execute"] is False

    def test_restart_auto_execute(self, engine):
        """Test that restart can auto-execute"""
        compliance = engine.check_compliance("restart")

        assert compliance["auto_execute"] is True
        assert compliance["requires_approval"] is False
        assert compliance["manual_only"] is False

    def test_optimize_auto_execute(self, engine):
        """Test that optimize can auto-execute"""
        compliance = engine.check_compliance("optimize")

        assert compliance["auto_execute"] is True
        assert compliance["requires_approval"] is False

    def test_audit_settings(self, engine):
        """Test audit configuration"""
        assert engine.should_audit("decision") is True
        assert engine.should_audit("action") is True
        assert engine.requires_justification() is True


class TestMonitoringPolicies:
    """Test monitoring policy queries"""

    def test_monitoring_intervals(self, engine):
        """Test monitoring interval calculation"""
        # Critical services (priority 1) - 30 seconds
        assert engine.get_monitoring_interval(1) == 30

        # High priority services (priority 2-3) - 60 seconds
        assert engine.get_monitoring_interval(2) == 60
        assert engine.get_monitoring_interval(3) == 60

        # Low priority services (priority 4-5) - 120 seconds
        assert engine.get_monitoring_interval(4) == 120
        assert engine.get_monitoring_interval(5) == 120


class TestNotificationPolicies:
    """Test notification and escalation policies"""

    def test_escalation_levels(self, engine):
        """Test escalation level configuration"""
        levels = engine.get_escalation_levels()

        assert len(levels) == 4

        # Level 1: Immediate
        assert levels[0].level == 1
        assert levels[0].delay_seconds == 0
        assert "ops_team" in levels[0].notify

        # Level 2: 5 minutes
        assert levels[1].level == 2
        assert levels[1].delay_seconds == 300
        assert "on_call" in levels[1].notify

        # Level 3: 15 minutes
        assert levels[2].level == 3
        assert levels[2].delay_seconds == 900
        assert "management" in levels[2].notify

    def test_notification_channels(self, engine):
        """Test notification channel configuration"""
        channels = engine.get_notification_channels()

        # Email should be enabled
        assert channels.email.enabled is True
        assert len(channels.email.recipients) > 0


class TestActionValidation:
    """Test comprehensive action validation"""

    def test_validate_allowed_action(self, engine):
        """Test validation of allowed action"""
        context = {
            "attempts": 1,
            "metrics": {
                "cpu": 70,
                "memory": 75
            }
        }

        result = engine.validate_action_context(
            action="restart",
            service_name="api_gateway",
            context=context
        )

        assert result["allowed"] is True
        assert len(result["violations"]) == 0

    def test_validate_max_attempts_exceeded(self, engine):
        """Test validation when max attempts exceeded"""
        context = {
            "attempts": 5,
            "metrics": {
                "cpu": 70
            }
        }

        result = engine.validate_action_context(
            action="restart",
            service_name="database",
            context=context
        )

        assert result["allowed"] is False
        assert len(result["violations"]) > 0
        assert "Maximum auto-recovery attempts" in result["violations"][0]

    def test_validate_critical_metrics(self, engine):
        """Test validation with critical metrics"""
        context = {
            "attempts": 1,
            "metrics": {
                "cpu": 95,  # Critical level
                "memory": 90
            }
        }

        result = engine.validate_action_context(
            action="optimize",
            service_name="api_gateway",
            context=context
        )

        # Should be allowed but have recommendations
        assert result["allowed"] is True
        assert len(result["recommendations"]) > 0
        assert "critical level" in result["recommendations"][0]


class TestHotReload:
    """Test hot reload functionality"""

    def test_reload_policies(self, engine):
        """Test that policies can be reloaded"""
        # Get initial metadata
        metadata_before = engine.get_policy_metadata()

        # Reload
        success = engine.reload_policies()

        # Should succeed
        assert success is True

        # Should have loaded timestamp
        metadata_after = engine.get_policy_metadata()
        assert metadata_after["loaded"] is True


class TestErrorHandling:
    """Test error handling"""

    def test_load_nonexistent_file(self):
        """Test loading nonexistent policy file"""
        with pytest.raises(PolicyLoadError):
            engine = PolicyEngine(Path("/nonexistent/policies.yaml"))

    def test_ensure_loaded_check(self):
        """Test that operations fail without loaded policies"""
        engine = PolicyEngine()

        with pytest.raises(PolicyLoadError):
            engine.get_recovery_policy("database")


if __name__ == "__main__":
    # Run with: python -m pytest test_policy_engine.py -v
    pytest.main([__file__, "-v"])
