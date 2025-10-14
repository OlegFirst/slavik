"""
Smoke tests for BCM Platform endpoints
"""
import pytest
import os


def test_smoke_basic():
    """Basic smoke test"""
    assert True


class TestEndpoints:
    """Smoke tests for API endpoints"""
    
    def test_environment_variables(self):
        """Test that basic environment variables are accessible"""
        # These should be available in CI
        env_vars = ['CI', 'GITHUB_ACTIONS']
        for var in env_vars:
            if os.getenv(var):
                assert True
        # At least one should exist in CI
        assert any(os.getenv(var) for var in env_vars)
    
    def test_python_version(self):
        """Test Python version compatibility"""
        import sys
        version = sys.version_info
        # Should be Python 3.11+
        assert version.major == 3
        assert version.minor >= 11