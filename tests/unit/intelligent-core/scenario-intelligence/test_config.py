"""
Unit tests for Scenario Intelligence Configuration

Tests:
- Config loading
- Validation
- Environment variables
"""

import pytest
import sys
import os
from pathlib import Path

# Add to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "intelligent-core/scenario-intelligence"))


def test_config_import():
    """Test that config can be imported"""
    from config import get_config, Config
    assert get_config is not None
    assert Config is not None


def test_config_loading():
    """Test configuration loading"""
    from config import get_config

    config = get_config()
    assert config is not None
    assert config.service is not None
    assert config.database is not None


def test_config_validation():
    """Test configuration validation"""
    from config import get_config

    config = get_config()
    warnings = config.validate()

    # Should return a list (may have warnings but should not fail)
    assert isinstance(warnings, list)


def test_storage_config():
    """Test storage configuration"""
    from config import get_config

    config = get_config()
    assert config.storage is not None
    assert hasattr(config.storage, 'use_memory')
    assert hasattr(config.storage, 'use_postgres')
    assert hasattr(config.storage, 'use_qdrant')


def test_feature_flags():
    """Test feature flags"""
    from config import get_config

    config = get_config()
    assert config.features is not None
    assert hasattr(config.features, 'l4_generation')
    assert hasattr(config.features, 'semantic_search')
    assert hasattr(config.features, 'auto_regeneration')
    assert hasattr(config.features, 'execution_engine')


def test_monitoring_config():
    """Test monitoring configuration"""
    from config import get_config

    config = get_config()
    assert config.monitoring is not None
    assert hasattr(config.monitoring, 'mio_manager_host')
    assert hasattr(config.monitoring, 'metrics_port')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
