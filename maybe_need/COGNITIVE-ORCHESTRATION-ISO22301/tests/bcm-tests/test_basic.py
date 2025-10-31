"""
Basic tests for BCM Platform
"""
import pytest


def test_basic_python():
    """Test that basic Python functionality works"""
    assert 1 + 1 == 2


def test_imports():
    """Test that required modules can be imported"""
    try:
        import fastapi
        import pika
        import structlog
        assert True
    except ImportError as e:
        pytest.fail(f"Failed to import required module: {e}")


class TestBCMPlatform:
    """Test suite for BCM Platform"""
    
    def test_platform_basic(self):
        """Basic platform test"""
        assert True
        
    def test_environment_setup(self):
        """Test environment is properly set up"""
        import os
        # Check if we're in CI
        if os.getenv('CI'):
            assert os.getenv('CI') == 'true'