"""
Test script for Platform Topology Mapper
Discovers all services in AI-Platform-ISO and creates digital mirrors
"""

import asyncio
import json
from core.system_clone.platform_topology import PlatformTopologyMapper
from core.system_clone.service_mirror import ServiceMirror
from core.system_clone.integration_graph import IntegrationGraph


async def test_topology_discovery():
    """Test platform topology discovery"""
    print("\n" + "="*70)
    print("🔍 AI-PLATFORM-ISO TOPOLOGY DISCOVERY")
    print("="*70 + "\n")

    # Create topology mapper
    async with PlatformTopologyMapper(timeout=3.0) as mapper:
        # Discover all services
        print("📡 Discovering services...")
        topology = await mapper.discover_all_services()

        print(f"\n✅ Discovery complete!")
        print(f"   Total services: {topology.total_services}")
        print(f"   Running: {topology.running_services}")
        print(f"   Stopped: {topology.total_services - topology.running_services}")

        # Show running services
        print("\n🟢 Running Services:")
        running = await mapper.get_running_services()
        for service in running:
            print(f"   ✓ {service.name:30} Port {service.port:5} ({service.response_time_ms:.0f}ms)")

        # Show stopped services
        print("\n🔴 Stopped Services:")
        for service in topology.services.values():
            if service.status.value != "running":
                print(f"   ✗ {service.name:30} Port {service.port:5}")

        # Get topology summary
        print("\n📊 Topology Summary:")
        summary = await mapper.get_topology_summary()
        print(f"   Health: {summary['health_percentage']:.1f}%")
        print(f"   Integrations: {summary['integration_count']}")

        print("\n📦 Services by Type:")
        for service_type, data in summary['services_by_type'].items():
            print(f"   {service_type:20} {data['running']}/{data['total']} running")

        # Export graph
        print("\n🌐 Exporting topology graph...")
        graph_data = await mapper.export_topology_graph()
        print(f"   Nodes: {graph_data['metadata']['total_nodes']}")
        print(f"   Edges: {graph_data['metadata']['total_edges']}")

        return topology, graph_data


async def test_service_mirror(service_name: str, base_url: str):
    """Test service mirror creation"""
    print(f"\n{'='*70}")
    print(f"🪞 CREATING MIRROR FOR: {service_name}")
    print(f"{'='*70}\n")

    async with ServiceMirror(service_name, base_url, timeout=5.0) as mirror:
        # Create mirror
        print(f"📸 Creating digital mirror...")
        mirror_data = await mirror.create_mirror()

        # Show summary
        summary = mirror.get_mirror_summary()
        print(f"\n✅ Mirror created!")
        print(f"   Status: {summary['status']}")
        print(f"   Version: {summary['version']}")
        print(f"   Uptime: {summary['uptime_seconds']}s" if summary['uptime_seconds'] else "   Uptime: N/A")
        print(f"   Endpoints: {summary['endpoints_count']}")
        print(f"   Integrations: {summary['integrations_count']}")
        print(f"   Data Models: {summary['data_models_count']}")

        if mirror_data.endpoints:
            print(f"\n📍 Discovered Endpoints:")
            for endpoint in mirror_data.endpoints[:10]:  # Show first 10
                print(f"   {endpoint.method:6} {endpoint.path:40} - {endpoint.description or 'N/A'}")

        return mirror_data


async def test_integration_graph(topology):
    """Test integration graph analysis"""
    print(f"\n{'='*70}")
    print("🔗 INTEGRATION GRAPH ANALYSIS")
    print(f"{'='*70}\n")

    # Build integration graph
    graph = IntegrationGraph()

    # Add services
    for service_name, service_info in topology.services.items():
        graph.add_service(
            service_name,
            is_running=(service_info.status.value == "running")
        )

    # Add integrations from topology
    for service_name, integrations in topology.integration_map.items():
        for target_service in integrations:
            graph.add_integration(service_name, target_service)

    # Calculate criticality
    print("🎯 Calculating service criticality...")
    graph.calculate_criticality_scores()

    # Show critical services
    print("\n⭐ Critical Services:")
    critical = graph.get_critical_services(threshold=0.3)
    for service_name in critical:
        node = graph.nodes[service_name]
        print(f"   {service_name:30} Criticality: {node.criticality_score:.2f}")

    # Integration health
    print("\n💚 Integration Health:")
    health = graph.get_integration_health()
    print(f"   Service Availability: {health['service_availability']:.1f}%")
    print(f"   Integration Health: {health['integration_health_percentage']:.1f}%")
    print(f"   Circular Dependencies: {'❌ YES' if health['has_circular_dependencies'] else '✅ NO'}")

    # Impact analysis for critical service
    if "simulation_service" in topology.services:
        print("\n💥 Impact Analysis: simulation_service failure")
        impact = graph.assess_impact_if_service_fails("simulation_service")
        print(f"   Total Affected: {impact['total_affected']}")
        print(f"   Direct Impact: {impact['direct_impact']['count']} services")
        print(f"   Indirect Impact: {impact['indirect_impact']['count']} services")
        print(f"   Is Critical: {'⚠️ YES' if impact['is_critical'] else 'NO'}")

    # Export graph
    print("\n📤 Exporting integration graph...")
    graph_export = graph.export_graph()
    print(f"   Total Nodes: {len(graph_export['nodes'])}")
    print(f"   Total Edges: {len(graph_export['edges'])}")

    return graph


async def main():
    """Main test function"""
    print("\n" + "🚀"*35)
    print("    AI-PLATFORM-ISO SYSTEM CLONE TEST")
    print("🚀"*35 + "\n")

    try:
        # 1. Topology Discovery
        topology, graph_data = await test_topology_discovery()

        # 2. Create mirror for simulation_service (if running)
        simulation_service = topology.services.get("simulation_service")
        if simulation_service and simulation_service.status.value == "running":
            await test_service_mirror(
                "simulation_service",
                f"http://localhost:{simulation_service.port}"
            )
        else:
            print("\n⚠️  simulation_service not running, skipping mirror creation")

        # 3. Integration Graph Analysis
        graph = await test_integration_graph(topology)

        print("\n" + "="*70)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY")
        print("="*70 + "\n")

        # Save results
        print("💾 Saving results...")

        results = {
            "topology": {
                "total_services": topology.total_services,
                "running_services": topology.running_services,
                "services": {
                    name: {
                        "port": info.port,
                        "status": info.status.value,
                        "type": info.service_type.value
                    }
                    for name, info in topology.services.items()
                }
            },
            "graph": graph_data
        }

        with open("platform_topology_results.json", "w") as f:
            json.dump(results, f, indent=2)

        print("✅ Results saved to platform_topology_results.json")

    except Exception as error:
        print(f"\n❌ ERROR: {error}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
