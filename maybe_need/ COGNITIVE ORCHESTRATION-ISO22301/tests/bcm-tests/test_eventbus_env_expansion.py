"""
Test for EventBus environment variable expansion functionality
"""
import os
import pytest
import sys
sys.path.insert(0, '/home/runner/work/ISO-22301/ISO-22301/backend/eventbus')

def test_env_var_expansion():
    """Test that environment variable expansion works correctly"""
    try:
        from main import expand_env_vars
    except ImportError:
        pytest.skip("expand_env_vars function not available - skipping expansion test")
    
    # Test the specific case from the bug report
    problematic_url = "postgresql://bcm:bcm_password@localhost:${PGPORT}/bcm_events"
    expected_url = "postgresql://bcm:bcm_password@localhost:5432/bcm_events"
    
    result = expand_env_vars(problematic_url)
    assert result == expected_url
    
    # Test full expansion
    full_expansion = "postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${PGHOST}:${PGPORT}/${POSTGRES_DB}"
    expected_full = "postgresql://bcm:bcm_password@localhost:5432/bcm_events"
    
    result_full = expand_env_vars(full_expansion)
    assert result_full == expected_full
    
    # Test normal URL (no expansion needed)
    normal_url = "postgresql://user:password@host:5432/database"
    result_normal = expand_env_vars(normal_url)
    assert result_normal == normal_url
    
    # Test with environment variable set
    os.environ['PGPORT'] = '5433'
    try:
        result_custom = expand_env_vars(problematic_url)
        expected_custom = "postgresql://bcm:bcm_password@localhost:5433/bcm_events"
        assert result_custom == expected_custom
    finally:
        # Clean up
        if 'PGPORT' in os.environ:
            del os.environ['PGPORT']

def test_postgres_url_construction():
    """Test that POSTGRES_URL is properly constructed with expansion"""
    # Set a problematic environment variable
    os.environ['POSTGRES_URL'] = "postgresql://bcm:bcm_password@localhost:${PGPORT}/bcm_events"
    
    try:
        # Import after setting the environment variable
        import importlib
        import main
        importlib.reload(main)
        
        # Should be expanded to valid URL
        if hasattr(main, 'POSTGRES_URL'):
            assert "${PGPORT}" not in main.POSTGRES_URL
        else:
            pytest.skip("POSTGRES_URL not available in main module")
        assert ":5432/" in main.POSTGRES_URL or ":5433/" in main.POSTGRES_URL  # Default or custom port
        
    finally:
        # Clean up
        if 'POSTGRES_URL' in os.environ:
            del os.environ['POSTGRES_URL']

if __name__ == "__main__":
    test_env_var_expansion()
    test_postgres_url_construction()
    print("All tests passed!")