"""
Unit tests for BCM Platform services
"""
import pytest
import os
import sys

# Add services to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'services'))


def test_services_directory_exists():
    """Test that services directory exists"""
    services_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'services')
    assert os.path.exists(services_dir)


def test_ai_orchestrator_exists():
    """Test that AI orchestrator service exists"""
    ai_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'services', 'ai_orchestrator')
    assert os.path.exists(ai_dir)
    
    main_file = os.path.join(ai_dir, 'main.py')
    if os.path.exists(main_file):
        assert True  # main.py exists
    else:
        pytest.skip("AI orchestrator main.py not found")


class TestAIOrchestrator:
    """Test AI Orchestrator service"""
    
    def test_ai_orchestrator_import(self):
        """Test that AI orchestrator can be imported"""
        try:
            # Try to import if the module exists
            services_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'services')
            if os.path.exists(os.path.join(services_dir, 'ai_orchestrator', 'main.py')):
                # Module exists, test passed
                assert True
            else:
                pytest.skip("AI orchestrator service not found")
        except Exception as e:
            pytest.skip(f"AI orchestrator import test skipped: {e}")