#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Data Collection Orchestrator Usage Examples

This file contains examples of how to use the BCM Digital Twin Data Collection Orchestrator
for real-time data collection from 70+ BCM platform services.

Author: BCM Platform Team
License: LGPL-3
"""

# Example 1: Creating and Configuring an Orchestrator
def create_orchestrator_example(env):
    """
    Example: Create a new data collection orchestrator
    """
    orchestrator = env['bcm.data.collection.orchestrator'].create({
        'name': 'Production BCM Data Collector',
        'enable_real_time': True,
        'enable_parallel_collection': True,
        'max_concurrent_collections': 15,
        'rate_limit_requests_per_second': 20.0,
        'collection_timeout': 30,
        'max_retry_attempts': 3
    })

    print(f"✅ Created orchestrator: {orchestrator.name} (ID: {orchestrator.orchestrator_id})")
    return orchestrator


# Example 2: Registering Services Programmatically
def register_services_example(orchestrator):
    """
    Example: Register multiple services with the orchestrator
    """
    services = [
        {
            'name': 'bcm_incident',
            'config': {
                'url': '/web/dataset/call_kw/bcm.incident/search_read',
                'auth_type': 'session',
                'priority': 1,
                'data_types': ['incidents', 'responses', 'timelines'],
                'collection_method': 'realtime'
            }
        },
        {
            'name': 'ai_consultant',
            'config': {
                'url': 'http://localhost:8001/api/v1/consultant/status',
                'auth_type': 'bearer',
                'priority': 1,
                'data_types': ['recommendations', 'analysis', 'insights'],
                'collection_method': 'websocket'
            }
        },
        {
            'name': 'keycloak',
            'config': {
                'url': 'http://localhost:8080/auth/admin/realms/bcm/users',
                'auth_type': 'oauth2',
                'priority': 3,
                'data_types': ['users', 'sessions', 'permissions'],
                'collection_method': 'api'
            }
        }
    ]

    for service in services:
        success = orchestrator.register_service_endpoint(
            service['name'],
            service['config']
        )
        if success:
            print(f"✅ Registered service: {service['name']}")
        else:
            print(f"❌ Failed to register service: {service['name']}")


# Example 3: Starting Real-time Collection
def start_collection_example(orchestrator):
    """
    Example: Start real-time data collection
    """
    try:
        orchestrator.start_real_time_collection()
        print(f"🚀 Started real-time collection for orchestrator: {orchestrator.name}")
        print(f"   Status: {orchestrator.collection_status}")
        print(f"   Active collections: {len(orchestrator.active_collections or {})}")

    except Exception as e:
        print(f"❌ Failed to start collection: {str(e)}")


# Example 4: Manual Data Collection from Specific Service
def manual_collection_example(orchestrator):
    """
    Example: Manually collect data from a specific service
    """
    service_name = 'bcm_incident'

    try:
        data = orchestrator.collect_from_service(service_name)
        if data:
            print(f"✅ Collected data from {service_name}:")
            print(f"   Timestamp: {data.get('timestamp')}")
            print(f"   Data points: {len(data.get('data', []))}")
            print(f"   Response time: {data.get('metadata', {}).get('response_time', 'N/A')}s")

            # Process and update digital twins
            processed_data = orchestrator.process_collected_data(data, service_name)
            if processed_data:
                orchestrator.update_digital_twins(processed_data)
                print(f"   ✅ Updated digital twins with processed data")
        else:
            print(f"❌ No data collected from {service_name}")

    except Exception as e:
        print(f"❌ Manual collection failed: {str(e)}")


# Example 5: Health Check All Services
def health_check_example(orchestrator):
    """
    Example: Perform health check on all configured services
    """
    try:
        health_results = orchestrator.health_check_all_services()

        print("🏥 Service Health Check Results:")
        for category, services in health_results.items():
            print(f"\n  📂 {category.upper()}:")
            for service_name, result in services.items():
                status = result.get('status', 'unknown')
                if status == 'healthy':
                    response_time = result.get('response_time', 0)
                    print(f"    ✅ {service_name}: Healthy ({response_time:.2f}s)")
                elif status == 'unhealthy':
                    code = result.get('response_code', 'N/A')
                    print(f"    ⚠️  {service_name}: Unhealthy (HTTP {code})")
                else:
                    error = result.get('error', 'Unknown error')
                    print(f"    ❌ {service_name}: Error ({error})")

    except Exception as e:
        print(f"❌ Health check failed: {str(e)}")


# Example 6: Performance Monitoring
def performance_monitoring_example(orchestrator):
    """
    Example: Monitor performance metrics
    """
    metrics = orchestrator.performance_metrics or {}

    print("📊 Performance Metrics:")
    print(f"  Total Collections: {metrics.get('total_collections', 0)}")
    print(f"  Successful: {metrics.get('successful_collections', 0)}")
    print(f"  Failed: {metrics.get('failed_collections', 0)}")
    print(f"  Average Response Time: {metrics.get('average_collection_time', 0):.2f}s")
    print(f"  Data Volume Processed: {metrics.get('data_volume_processed', 0)} bytes")

    # Service-specific response times
    response_times = metrics.get('services_response_times', {})
    if response_times:
        print("\n  🎯 Service Response Times:")
        for service, times in response_times.items():
            avg_time = sum(times) / len(times) if times else 0
            print(f"    {service}: {avg_time:.2f}s (last {len(times)} collections)")

    # Error rates
    error_rates = metrics.get('error_rates', {})
    if error_rates:
        print("\n  ⚠️  Error Rates:")
        for service, errors in error_rates.items():
            print(f"    {service}: {errors} errors")


# Example 7: Using the Setup Wizard Programmatically
def setup_wizard_example(env, orchestrator):
    """
    Example: Use the collection setup wizard programmatically
    """
    wizard = env['bcm.collection.setup.wizard'].create({
        'orchestrator_id': orchestrator.id,
        'setup_type': 'quick_start',
        'enable_bcm_modules': True,
        'enable_ai_services': True,
        'enable_integrations': True,
        'enable_adapters': False,
        'collection_frequency': 'medium',
        'max_concurrent': 10,
        'rate_limit': 15.0,
        'auto_discover_services': True,
        'validate_config': True,
        'test_connections': True
    })

    # Run discovery
    wizard.action_discover_services()
    print("🔍 Service discovery completed")

    # Validate configuration
    wizard.action_validate_configuration()
    print("✅ Configuration validated")

    # Apply configuration
    result = wizard.action_apply_configuration()
    print("🚀 Configuration applied successfully")

    return wizard


# Example 8: Service Registration Wizard
def service_registration_example(env, orchestrator):
    """
    Example: Register a new service using the wizard
    """
    wizard = env['bcm.service.registration.wizard'].create({
        'orchestrator_id': orchestrator.id,
        'service_name': 'custom_monitoring_service',
        'service_url': 'http://localhost:9001/api/metrics',
        'service_category': 'integrations',
        'auth_type': 'api_key',
        'api_key': 'your-api-key-here',
        'priority': 2,
        'collection_method': 'api',
        'data_types': 'system_metrics, performance_data, alerts',
        'test_connection': True
    })

    # Test connection
    wizard.action_test_connection()
    print(f"🔌 Connection test result: {wizard.connection_test_result[:100]}...")

    # Register service
    result = wizard.action_register_service()
    print("✅ Service registered successfully")

    return wizard


# Example 9: Real-world Usage Scenario
def complete_scenario_example(env):
    """
    Example: Complete real-world usage scenario
    """
    print("🌟 BCM Digital Twin Data Collection - Complete Scenario")
    print("=" * 60)

    # Step 1: Create orchestrator
    print("\n1️⃣  Creating orchestrator...")
    orchestrator = create_orchestrator_example(env)

    # Step 2: Setup with wizard
    print("\n2️⃣  Setting up with wizard...")
    setup_wizard = setup_wizard_example(env, orchestrator)

    # Step 3: Register additional custom service
    print("\n3️⃣  Registering custom service...")
    reg_wizard = service_registration_example(env, orchestrator)

    # Step 4: Health check
    print("\n4️⃣  Performing health check...")
    health_check_example(orchestrator)

    # Step 5: Start collection
    print("\n5️⃣  Starting real-time collection...")
    start_collection_example(orchestrator)

    # Step 6: Manual collection test
    print("\n6️⃣  Testing manual collection...")
    manual_collection_example(orchestrator)

    # Step 7: Monitor performance
    print("\n7️⃣  Monitoring performance...")
    performance_monitoring_example(orchestrator)

    print("\n🎉 Complete scenario finished!")
    print(f"   Orchestrator ID: {orchestrator.orchestrator_id}")
    print(f"   Status: {orchestrator.collection_status}")
    print(f"   Services configured: {len(orchestrator.service_endpoints or {})}")


# Example 10: Configuration Templates
def get_configuration_templates():
    """
    Example: Pre-built configuration templates for different scenarios
    """
    templates = {
        'production_high_volume': {
            'max_concurrent_collections': 20,
            'rate_limit_requests_per_second': 50.0,
            'collection_timeout': 15,
            'collection_frequency': 'high',
            'enable_all_categories': True
        },

        'development_testing': {
            'max_concurrent_collections': 5,
            'rate_limit_requests_per_second': 5.0,
            'collection_timeout': 60,
            'collection_frequency': 'low',
            'enable_basic_only': True
        },

        'critical_systems_only': {
            'max_concurrent_collections': 15,
            'rate_limit_requests_per_second': 30.0,
            'collection_timeout': 10,
            'collection_frequency': 'realtime',
            'critical_services_only': True
        }
    }

    return templates


if __name__ == '__main__':
    print("""
BCM Digital Twin Data Collection Orchestrator Examples
======================================================

This script contains comprehensive examples for using the automated data collection
system for real-time Digital Twin updates from 70+ BCM platform services.

Key Features Demonstrated:
• Service registration and management
• Real-time data collection orchestration
• WebSocket and API-based collection methods
• Parallel processing and performance optimization
• Error handling and automatic recovery
• Health monitoring and analytics
• Configuration wizards and automation

To use these examples in your Odoo environment:

1. Access the Odoo shell: ./odoo-bin shell -d your_database
2. Import and run examples:

   from addons.bcm_digital_twin_core.examples.data_collection_usage_example import *
   complete_scenario_example(env)

3. Or run individual examples:

   orchestrator = create_orchestrator_example(env)
   start_collection_example(orchestrator)
   health_check_example(orchestrator)

For production deployment, ensure:
• Proper authentication credentials are configured
• Network access to all service endpoints
• Sufficient system resources for parallel collection
• Monitoring and alerting for collection failures
""")