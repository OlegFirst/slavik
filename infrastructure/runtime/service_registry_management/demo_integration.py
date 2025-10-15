#!/usr/bin/env python3
"""
Integration Demo: Service Registry Management + Service Discovery
==================================================================

This script demonstrates the full integration flow:
1. Register a service via Service Registry Management
2. Verify catalog entry was created
3. Verify service was registered in Service Discovery
4. Show unified view from catalog_integration.py

Prerequisites:
- Service Registry Management running on port 8200
- Service Discovery running on port 8500

Usage:
    python demo_integration.py
"""

import asyncio
import httpx
import json
from pathlib import Path
from datetime import datetime

# Configuration
SERVICE_REGISTRY_URL = "http://localhost:8200"
SERVICE_DISCOVERY_URL = "http://localhost:8500"
CATALOGS_DIR = Path("/Users/MD/AI-Platform-ISO/catalogs/platform-services")

# ANSI colors for output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_header(text: str):
    """Print colored header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(70)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}\n")


def print_success(text: str):
    """Print success message"""
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")


def print_info(text: str):
    """Print info message"""
    print(f"{Colors.OKCYAN}ℹ️  {text}{Colors.ENDC}")


def print_error(text: str):
    """Print error message"""
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")


def print_json(data: dict, title: str = None):
    """Print formatted JSON"""
    if title:
        print(f"\n{Colors.OKBLUE}{Colors.BOLD}{title}:{Colors.ENDC}")
    print(json.dumps(data, indent=2, ensure_ascii=False))


async def check_service_health(service_name: str, url: str) -> bool:
    """Check if a service is healthy"""
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            response = await client.get(f"{url}/health")
            if response.status_code == 200:
                print_success(f"{service_name} is healthy")
                return True
            else:
                print_error(f"{service_name} returned status {response.status_code}")
                return False
    except Exception as e:
        print_error(f"{service_name} is not accessible: {e}")
        return False


async def register_test_service() -> dict:
    """Register a test service via Service Registry Management"""
    print_header("STEP 1: Register Test Service")

    service_data = {
        "service_name": "demo_analytics_service",
        "service_type": "platform",
        "description": "Demo analytics service for integration testing",
        "component": "platform_services",
        "port": None,  # Auto-assign
        "create_template": True,
        "purpose": [
            "Demonstrate Service Registry Management",
            "Show integration with Service Discovery",
            "Validate end-to-end workflow"
        ],
        "capabilities": [
            "Real-time analytics",
            "Data aggregation",
            "Report generation"
        ],
        "dependencies": [
            "postgresql",
            "redis"
        ]
    }

    print_info("Sending registration request...")
    print_json(service_data, "Registration Payload")

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{SERVICE_REGISTRY_URL}/api/v1/services/register",
                json=service_data
            )

            if response.status_code == 200:
                result = response.json()
                print_success("Service registered successfully!")
                print_json(result, "Registration Response")
                return result
            else:
                print_error(f"Registration failed with status {response.status_code}")
                print(response.text)
                return None
    except Exception as e:
        print_error(f"Registration request failed: {e}")
        return None


async def verify_catalog_entry(service_name: str) -> bool:
    """Verify catalog YAML was created"""
    print_header("STEP 2: Verify Catalog Entry")

    catalog_file = CATALOGS_DIR / f"{service_name}.yaml"

    if catalog_file.exists():
        print_success(f"Catalog entry created: {catalog_file}")

        # Read and display excerpt
        with open(catalog_file, 'r') as f:
            lines = f.readlines()[:30]  # First 30 lines
            print(f"\n{Colors.OKBLUE}Catalog Entry Excerpt:{Colors.ENDC}")
            print("".join(lines))
            print("...")

        return True
    else:
        print_error(f"Catalog entry not found: {catalog_file}")
        return False


async def verify_service_discovery(service_name: str, port: int) -> bool:
    """Verify service was registered in Service Discovery"""
    print_header("STEP 3: Verify Service Discovery Registration")

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            # Get all services from Service Discovery
            response = await client.get(f"{SERVICE_DISCOVERY_URL}/v2/catalog/services")

            if response.status_code == 200:
                services = response.json()
                print_success(f"Service Discovery returned {len(services)} services")

                # Find our service
                service_found = False
                for service in services:
                    if service.get("name") == service_name:
                        service_found = True
                        print_success(f"Service '{service_name}' found in Service Discovery!")
                        print_json(service, "Service Details")
                        break

                if not service_found:
                    print_error(f"Service '{service_name}' not found in Service Discovery")
                    print_info("Available services:")
                    for service in services[:5]:
                        print(f"  - {service.get('name')} (port: {service.get('port')})")

                return service_found
            else:
                print_error(f"Service Discovery returned status {response.status_code}")
                return False
    except Exception as e:
        print_error(f"Could not query Service Discovery: {e}")
        return False


async def verify_template_generation(service_name: str, template_location: str) -> bool:
    """Verify service template was generated"""
    print_header("STEP 4: Verify Template Generation")

    template_path = Path(template_location)

    if not template_path.exists():
        print_error(f"Template directory not found: {template_path}")
        return False

    print_success(f"Template directory created: {template_path}")

    # Check for expected files
    expected_files = ["main.py", "requirements.txt", "README.md"]
    all_found = True

    for filename in expected_files:
        file_path = template_path / filename
        if file_path.exists():
            size = file_path.stat().st_size
            print_success(f"  {filename} ({size} bytes)")
        else:
            print_error(f"  {filename} - NOT FOUND")
            all_found = False

    # Show excerpt from main.py
    main_py = template_path / "main.py"
    if main_py.exists():
        with open(main_py, 'r') as f:
            lines = f.readlines()[:25]
            print(f"\n{Colors.OKBLUE}Generated main.py Excerpt:{Colors.ENDC}")
            print("".join(lines))
            print("...")

    return all_found


async def get_port_usage_stats() -> dict:
    """Get port usage statistics"""
    print_header("STEP 5: Port Usage Statistics")

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{SERVICE_REGISTRY_URL}/api/v1/ports/usage")

            if response.status_code == 200:
                stats = response.json()
                print_success("Port usage statistics retrieved")

                # Show summary for platform_services
                if "platform_services" in stats:
                    ps_stats = stats["platform_services"]
                    print(f"\n{Colors.OKBLUE}Platform Services Port Usage:{Colors.ENDC}")
                    print(f"  Range: {ps_stats['range_start']}-{ps_stats['range_end']}")
                    print(f"  Total Ports: {ps_stats['total_ports']}")
                    print(f"  Used: {ps_stats['used_ports']} ({ps_stats['usage_percent']:.1f}%)")
                    print(f"  Available: {ps_stats['available_ports']}")
                    print(f"  Used Ports: {ps_stats['used_port_list']}")

                return stats
            else:
                print_error(f"Failed to get port usage: {response.status_code}")
                return None
    except Exception as e:
        print_error(f"Could not get port usage stats: {e}")
        return None


async def get_service_stats() -> dict:
    """Get overall service statistics"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{SERVICE_REGISTRY_URL}/api/v1/services/stats")

            if response.status_code == 200:
                stats = response.json()
                print_success("Service statistics retrieved")
                print(f"\n{Colors.OKBLUE}Overall Statistics:{Colors.ENDC}")
                print(f"  Total Services: {stats['total_services']}")
                print(f"  Total Capacity: {stats['total_capacity']}")
                print(f"  Total Used: {stats['total_used']}")
                print(f"  Total Available: {stats['total_available']}")
                print(f"  Usage: {stats['usage_percent']:.2f}%")

                return stats
            else:
                print_error(f"Failed to get service stats: {response.status_code}")
                return None
    except Exception as e:
        print_error(f"Could not get service stats: {e}")
        return None


async def cleanup_test_service(service_name: str, template_location: str):
    """Cleanup test service (optional)"""
    print_header("CLEANUP (Optional)")

    print_info("To cleanup the test service:")
    catalog_file = CATALOGS_DIR / f"{service_name}.yaml"
    print(f"  1. Delete catalog: rm {catalog_file}")
    print(f"  2. Delete template: rm -rf {template_location}")
    print(f"  3. Service Discovery will auto-cleanup on restart")
    print()
    print_info("Or keep it as a reference example!")


async def main():
    """Main demo flow"""
    print_header("Service Registry Management + Service Discovery Integration Demo")
    print(f"{Colors.OKCYAN}This demo shows the complete integration workflow{Colors.ENDC}")
    print(f"{Colors.OKCYAN}Timestamp: {datetime.now().isoformat()}{Colors.ENDC}")

    # Check prerequisites
    print_header("Prerequisites Check")
    registry_ok = await check_service_health("Service Registry Management", SERVICE_REGISTRY_URL)
    discovery_ok = await check_service_health("Service Discovery", SERVICE_DISCOVERY_URL)

    if not registry_ok or not discovery_ok:
        print_error("\n⚠️  Prerequisites not met. Please start required services:")
        if not registry_ok:
            print("  cd /Users/MD/AI-Platform-ISO/infrastructure/runtime/service_registry_management")
            print("  python main.py")
        if not discovery_ok:
            print("  cd /Users/MD/AI-Platform-ISO/infrastructure/runtime/service_discovery")
            print("  python main.py")
        return

    # Run integration demo
    registration_result = await register_test_service()

    if not registration_result:
        print_error("\n⚠️  Service registration failed. Demo cannot continue.")
        return

    service_name = registration_result.get("service_name")
    port = registration_result.get("port")
    template_location = registration_result.get("template_location")

    # Verify each step
    await asyncio.sleep(1)  # Give systems time to sync

    catalog_ok = await verify_catalog_entry(service_name)
    discovery_ok = await verify_service_discovery(service_name, port)
    template_ok = await verify_template_generation(service_name, template_location)

    # Get statistics
    await get_port_usage_stats()
    await get_service_stats()

    # Summary
    print_header("Integration Demo Summary")

    results = {
        "Service Registration": registration_result is not None,
        "Catalog Entry Created": catalog_ok,
        "Service Discovery Registration": discovery_ok,
        "Template Generation": template_ok
    }

    all_passed = all(results.values())

    for step, passed in results.items():
        if passed:
            print_success(f"{step}")
        else:
            print_error(f"{step}")

    if all_passed:
        print(f"\n{Colors.OKGREEN}{Colors.BOLD}🎉 ALL INTEGRATION STEPS PASSED! 🎉{Colors.ENDC}")
        print(f"\n{Colors.OKCYAN}The Service Registry Management is fully integrated with:{Colors.ENDC}")
        print(f"  ✅ Catalog system (/catalogs/platform-services/)")
        print(f"  ✅ Service Discovery (port 8500)")
        print(f"  ✅ Template generation system")
        print(f"\n{Colors.OKCYAN}Next steps:{Colors.ENDC}")
        print(f"  1. Start the generated service: cd {template_location} && python main.py")
        print(f"  2. Check health: curl http://localhost:{port}/health")
        print(f"  3. View metrics: curl http://localhost:{port}/metrics")
    else:
        print(f"\n{Colors.WARNING}⚠️  Some integration steps failed. Check logs above.{Colors.ENDC}")

    # Cleanup info
    await cleanup_test_service(service_name, template_location)

    print(f"\n{Colors.HEADER}Demo completed at {datetime.now().isoformat()}{Colors.ENDC}\n")


if __name__ == "__main__":
    asyncio.run(main())
