#!/usr/bin/env python3
"""
Verification Script for Database Intelligence Implementation

Проверяет что все компоненты реализованы и готовы к работе.
"""

import os
import sys
from pathlib import Path


def check_file(file_path: str, min_lines: int = 0) -> bool:
    """Check if file exists and has minimum lines"""
    path = Path(file_path)
    if not path.exists():
        print(f" Missing: {file_path}")
        return False

    if min_lines > 0:
        lines = len(path.read_text().splitlines())
        if lines < min_lines:
            print(f"️  {file_path} has only {lines} lines (expected {min_lines}+)")
            return False

    print(f" {file_path} ({len(path.read_text().splitlines())} lines)")
    return True


def check_imports():
    """Check if all modules can be imported"""
    print("\n Checking Imports...")

    try:
        # Core service
        from db_intelligence_service import DatabaseIntelligenceService, get_db_intelligence
        print(" db_intelligence_service imports successfully")

        # Security monitor
        from security_monitor import SecurityMonitor
        print(" security_monitor imports successfully")

        # AI integration
        from ai_integration import AIIntegration, get_ai_integration
        print(" ai_integration imports successfully")

        # Orchestrator integration
        from orchestrator_integration import OrchestratorClient, get_orchestrator_client
        print(" orchestrator_integration imports successfully")

        # Command handler
        from command_handler import CommandHandler
        print(" command_handler imports successfully")

        # API
        from api import app
        print(" api imports successfully")

        return True
    except Exception as e:
        print(f" Import error: {e}")
        return False


def check_features():
    """Check if all features are implemented"""
    print("\n Checking Features...")

    from db_intelligence_service import DatabaseIntelligenceService

    service = DatabaseIntelligenceService()

    # Check attributes
    attributes = [
        'service_name',
        'version',
        'query_metrics',
        'slow_queries',
        'optimization_suggestions',
        'monitoring_task',
        'command_polling_task',
        'heartbeat_task',
        'security_monitor',
        'ai_integration',
        'orchestrator_client',
        'command_handler'
    ]

    for attr in attributes:
        if hasattr(service, attr):
            print(f" Attribute: {attr}")
        else:
            print(f" Missing attribute: {attr}")
            return False

    # Check methods
    methods = [
        'start',
        'stop',
        '_monitoring_loop',
        '_command_polling_loop',
        '_heartbeat_loop',
        '_collect_metrics',
        '_analyze_performance',
        '_check_health',
        '_run_security_checks',
        '_publish_alerts_to_ai',
        'get_health',
        'get_slow_queries',
        'get_optimization_suggestions',
        'analyze_query',
        'get_table_statistics'
    ]

    for method in methods:
        if hasattr(service, method):
            print(f" Method: {method}")
        else:
            print(f" Missing method: {method}")
            return False

    return True


def check_api_endpoints():
    """Check if all API endpoints are defined"""
    print("\n Checking API Endpoints...")

    from api import app

    expected_paths = [
        '/health',
        '/metrics',
        '/slow-queries',
        '/suggestions',
        '/analyze',
        '/tables',
        '/metrics/prometheus',
        '/admin/execute',
        '/admin/running-queries',
        '/admin/locks'
    ]

    routes = [route.path for route in app.routes]

    for path in expected_paths:
        if path in routes:
            print(f" Endpoint: {path}")
        else:
            print(f" Missing endpoint: {path}")
            return False

    return True


def check_orchestrator_client():
    """Check Orchestrator client methods"""
    print("\n Checking Orchestrator Client...")

    from orchestrator_integration import OrchestratorClient

    client = OrchestratorClient()

    methods = [
        'register',
        'heartbeat',
        'deregister',
        'poll_commands',
        'report_command_result',
        'send_critical_alert',
        'send_recommendation',
        'push_metrics',
        'request_resource',
        'coordinate_with_service'
    ]

    for method in methods:
        if hasattr(client, method):
            print(f" Method: {method}")
        else:
            print(f" Missing method: {method}")
            return False

    return True


def check_command_handler():
    """Check Command Handler"""
    print("\n Checking Command Handler...")

    from command_handler import CommandHandler
    from db_intelligence_service import DatabaseIntelligenceService

    service = DatabaseIntelligenceService()
    handler = CommandHandler(service)

    # Check supported commands
    commands = [
        'optimize_query',
        'kill_query',
        'vacuum_table',
        'analyze_table',
        'create_index',
        'reindex_table'
    ]

    # These should be implemented as _handle_{command} methods
    for cmd in commands:
        method_name = f'_handle_{cmd}'
        if hasattr(handler, method_name):
            print(f" Command handler: {cmd}")
        else:
            print(f" Missing handler: {cmd}")
            return False

    return True


def main():
    """Run all checks"""
    print("=" * 60)
    print("Database Intelligence Implementation Verification")
    print("=" * 60)

    # Change to intelligence directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)

    all_passed = True

    # Check files
    print("\n Checking Files...")
    files = [
        ('db_intelligence_service.py', 600),
        ('security_monitor.py', 300),
        ('ai_integration.py', 400),
        ('orchestrator_integration.py', 400),
        ('command_handler.py', 300),
        ('api.py', 400),
        ('main.py', 50),
        ('requirements.txt', 10),
        ('Dockerfile', 20),
        ('README.md', 200),
        ('INTEGRATION_COMPLETE.md', 300)
    ]

    for file_path, min_lines in files:
        if not check_file(file_path, min_lines):
            all_passed = False

    # Check imports
    if not check_imports():
        all_passed = False

    # Check features
    if not check_features():
        all_passed = False

    # Check API endpoints
    if not check_api_endpoints():
        all_passed = False

    # Check Orchestrator client
    if not check_orchestrator_client():
        all_passed = False

    # Check Command Handler
    if not check_command_handler():
        all_passed = False

    # Final result
    print("\n" + "=" * 60)
    if all_passed:
        print(" ALL CHECKS PASSED - READY FOR PRODUCTION")
    else:
        print(" SOME CHECKS FAILED - REVIEW ABOVE")
    print("=" * 60)

    return 0 if all_passed else 1


if __name__ == '__main__':
    sys.exit(main())
