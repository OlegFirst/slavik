"""
Comprehensive integration tests for BCM Platform backend services
Tests all adapter integrations with EventBus and mock data
"""

import asyncio
import httpx
import pytest
import json
from datetime import datetime
from typing import Dict, Any, List

# Service URLs
EVENTBUS_URL = "http://localhost:8001"
BPMN_SERVICE_URL = "http://localhost:8005"
LMS_ADAPTER_URL = "http://localhost:8006"
THEHIVE_ADAPTER_URL = "http://localhost:8007"
GRAFANA_ADAPTER_URL = "http://localhost:8008"

class IntegrationTester:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.test_tenant_id = "tenant_test_001"
        self.results = {
            "eventbus": {},
            "bpmn_service": {},
            "lms_adapter": {},
            "thehive_adapter": {},
            "grafana_adapter": {}
        }
    
    async def test_eventbus_health(self) -> Dict[str, Any]:
        """Test EventBus service health and functionality"""
        print("🔄 Testing EventBus service...")
        
        try:
            # Health check
            response = await self.client.get(f"{EVENTBUS_URL}/health")
            health_status = response.status_code == 200
            
            # Test event publishing
            test_event = {
                "event_type": "test.integration.started",
                "tenant_id": self.test_tenant_id,
                "data": {
                    "test_name": "Backend Integration Test",
                    "timestamp": datetime.utcnow().isoformat()
                },
                "user_id": "integration_tester"
            }
            
            response = await self.client.post(f"{EVENTBUS_URL}/api/events/publish", json=test_event)
            publish_status = response.status_code == 200
            
            # Test event history
            response = await self.client.get(
                f"{EVENTBUS_URL}/api/events/history",
                params={"tenant_id": self.test_tenant_id, "limit": 10}
            )
            history_status = response.status_code == 200
            
            # Test event validation
            response = await self.client.post(f"{EVENTBUS_URL}/api/events/validate", json=test_event)
            validation_status = response.status_code == 200
            
            # Test statistics
            response = await self.client.get(
                f"{EVENTBUS_URL}/api/events/stats",
                params={"tenant_id": self.test_tenant_id}
            )
            stats_status = response.status_code == 200
            
            result = {
                "health": health_status,
                "publish": publish_status,
                "history": history_status,
                "validation": validation_status,
                "stats": stats_status,
                "overall": all([health_status, publish_status, history_status, validation_status, stats_status])
            }
            
            self.results["eventbus"] = result
            print(f"✅ EventBus: {'PASS' if result['overall'] else 'FAIL'}")
            return result
            
        except Exception as e:
            print(f"❌ EventBus: FAIL - {str(e)}")
            result = {"error": str(e), "overall": False}
            self.results["eventbus"] = result
            return result
    
    async def test_bpmn_service(self) -> Dict[str, Any]:
        """Test BPMN Service functionality"""
        print("🔄 Testing BPMN Service...")
        
        try:
            # Health check
            response = await self.client.get(f"{BPMN_SERVICE_URL}/health")
            health_status = response.status_code == 200
            
            # Test mock data endpoints
            response = await self.client.get(f"{BPMN_SERVICE_URL}/api/bpmn/mock/processes")
            mock_processes_status = response.status_code == 200
            
            response = await self.client.get(f"{BPMN_SERVICE_URL}/api/bpmn/mock/instances")
            mock_instances_status = response.status_code == 200
            
            response = await self.client.get(f"{BPMN_SERVICE_URL}/api/bpmn/mock/tasks")
            mock_tasks_status = response.status_code == 200
            
            response = await self.client.get(f"{BPMN_SERVICE_URL}/api/bpmn/mock/templates")
            mock_templates_status = response.status_code == 200
            
            # Test demo process deployment
            response = await self.client.post(
                f"{BPMN_SERVICE_URL}/api/bpmn/mock/deploy-demo-process",
                params={"tenant_id": self.test_tenant_id}
            )
            deploy_demo_status = response.status_code == 200
            
            # Test process listing
            response = await self.client.get(
                f"{BPMN_SERVICE_URL}/api/bpmn/processes",
                params={"tenant_id": self.test_tenant_id}
            )
            list_processes_status = response.status_code == 200
            
            result = {
                "health": health_status,
                "mock_processes": mock_processes_status,
                "mock_instances": mock_instances_status,
                "mock_tasks": mock_tasks_status,
                "mock_templates": mock_templates_status,
                "deploy_demo": deploy_demo_status,
                "list_processes": list_processes_status,
                "overall": all([
                    health_status, mock_processes_status, mock_instances_status,
                    mock_tasks_status, mock_templates_status, deploy_demo_status,
                    list_processes_status
                ])
            }
            
            self.results["bpmn_service"] = result
            print(f"✅ BPMN Service: {'PASS' if result['overall'] else 'FAIL'}")
            return result
            
        except Exception as e:
            print(f"❌ BPMN Service: FAIL - {str(e)}")
            result = {"error": str(e), "overall": False}
            self.results["bpmn_service"] = result
            return result
    
    async def test_lms_adapter(self) -> Dict[str, Any]:
        """Test LMS Adapter functionality"""
        print("🔄 Testing LMS Adapter...")
        
        try:
            # Health check
            response = await self.client.get(f"{LMS_ADAPTER_URL}/health")
            health_status = response.status_code == 200
            
            # Test mock data endpoints
            response = await self.client.get(f"{LMS_ADAPTER_URL}/api/lms/mock/configs")
            mock_configs_status = response.status_code == 200
            
            response = await self.client.get(f"{LMS_ADAPTER_URL}/api/lms/mock/courses")
            mock_courses_status = response.status_code == 200
            
            response = await self.client.get(f"{LMS_ADAPTER_URL}/api/lms/mock/enrollments")
            mock_enrollments_status = response.status_code == 200
            
            response = await self.client.get(f"{LMS_ADAPTER_URL}/api/lms/mock/training-paths")
            training_paths_status = response.status_code == 200
            
            response = await self.client.get(f"{LMS_ADAPTER_URL}/api/lms/mock/competency-matrix")
            competency_matrix_status = response.status_code == 200
            
            response = await self.client.get(f"{LMS_ADAPTER_URL}/api/lms/mock/analytics")
            analytics_status = response.status_code == 200
            
            # Test demo configuration setup
            response = await self.client.post(
                f"{LMS_ADAPTER_URL}/api/lms/mock/setup-demo-config",
                params={"tenant_id": self.test_tenant_id, "lms_type": "moodle"}
            )
            setup_demo_status = response.status_code == 200
            
            result = {
                "health": health_status,
                "mock_configs": mock_configs_status,
                "mock_courses": mock_courses_status,
                "mock_enrollments": mock_enrollments_status,
                "training_paths": training_paths_status,
                "competency_matrix": competency_matrix_status,
                "analytics": analytics_status,
                "setup_demo": setup_demo_status,
                "overall": all([
                    health_status, mock_configs_status, mock_courses_status,
                    mock_enrollments_status, training_paths_status, competency_matrix_status,
                    analytics_status, setup_demo_status
                ])
            }
            
            self.results["lms_adapter"] = result
            print(f"✅ LMS Adapter: {'PASS' if result['overall'] else 'FAIL'}")
            return result
            
        except Exception as e:
            print(f"❌ LMS Adapter: FAIL - {str(e)}")
            result = {"error": str(e), "overall": False}
            self.results["lms_adapter"] = result
            return result
    
    async def test_thehive_adapter(self) -> Dict[str, Any]:
        """Test TheHive Adapter functionality"""
        print("🔄 Testing TheHive Adapter...")
        
        try:
            # Health check
            response = await self.client.get(f"{THEHIVE_ADAPTER_URL}/health")
            health_status = response.status_code == 200
            
            # Test mock data endpoints
            response = await self.client.get(f"{THEHIVE_ADAPTER_URL}/api/thehive/mock/configs")
            mock_configs_status = response.status_code == 200
            
            response = await self.client.get(f"{THEHIVE_ADAPTER_URL}/api/thehive/mock/cases")
            mock_cases_status = response.status_code == 200
            
            response = await self.client.get(f"{THEHIVE_ADAPTER_URL}/api/thehive/mock/alerts")
            mock_alerts_status = response.status_code == 200
            
            response = await self.client.get(f"{THEHIVE_ADAPTER_URL}/api/thehive/mock/observables")
            mock_observables_status = response.status_code == 200
            
            response = await self.client.get(f"{THEHIVE_ADAPTER_URL}/api/thehive/mock/tasks")
            mock_tasks_status = response.status_code == 200
            
            response = await self.client.get(f"{THEHIVE_ADAPTER_URL}/api/thehive/mock/templates")
            templates_status = response.status_code == 200
            
            response = await self.client.get(f"{THEHIVE_ADAPTER_URL}/api/thehive/mock/metrics")
            metrics_status = response.status_code == 200
            
            # Test demo configuration setup
            response = await self.client.post(
                f"{THEHIVE_ADAPTER_URL}/api/thehive/mock/setup-demo-config",
                params={"tenant_id": self.test_tenant_id}
            )
            setup_demo_status = response.status_code == 200
            
            result = {
                "health": health_status,
                "mock_configs": mock_configs_status,
                "mock_cases": mock_cases_status,
                "mock_alerts": mock_alerts_status,
                "mock_observables": mock_observables_status,
                "mock_tasks": mock_tasks_status,
                "templates": templates_status,
                "metrics": metrics_status,
                "setup_demo": setup_demo_status,
                "overall": all([
                    health_status, mock_configs_status, mock_cases_status,
                    mock_alerts_status, mock_observables_status, mock_tasks_status,
                    templates_status, metrics_status, setup_demo_status
                ])
            }
            
            self.results["thehive_adapter"] = result
            print(f"✅ TheHive Adapter: {'PASS' if result['overall'] else 'FAIL'}")
            return result
            
        except Exception as e:
            print(f"❌ TheHive Adapter: FAIL - {str(e)}")
            result = {"error": str(e), "overall": False}
            self.results["thehive_adapter"] = result
            return result
    
    async def test_grafana_adapter(self) -> Dict[str, Any]:
        """Test Grafana Adapter functionality"""
        print("🔄 Testing Grafana Adapter...")
        
        try:
            # Health check
            response = await self.client.get(f"{GRAFANA_ADAPTER_URL}/health")
            health_status = response.status_code == 200
            
            # Test mock data endpoints
            response = await self.client.get(f"{GRAFANA_ADAPTER_URL}/api/grafana/mock/configs")
            mock_configs_status = response.status_code == 200
            
            response = await self.client.get(f"{GRAFANA_ADAPTER_URL}/api/grafana/mock/dashboards")
            mock_dashboards_status = response.status_code == 200
            
            response = await self.client.get(f"{GRAFANA_ADAPTER_URL}/api/grafana/mock/datasources")
            mock_datasources_status = response.status_code == 200
            
            response = await self.client.get(f"{GRAFANA_ADAPTER_URL}/api/grafana/mock/kpis")
            kpis_status = response.status_code == 200
            
            response = await self.client.get(f"{GRAFANA_ADAPTER_URL}/api/grafana/mock/incident-metrics")
            incident_metrics_status = response.status_code == 200
            
            response = await self.client.get(f"{GRAFANA_ADAPTER_URL}/api/grafana/mock/training-metrics")
            training_metrics_status = response.status_code == 200
            
            response = await self.client.get(f"{GRAFANA_ADAPTER_URL}/api/grafana/mock/exercise-metrics")
            exercise_metrics_status = response.status_code == 200
            
            response = await self.client.get(f"{GRAFANA_ADAPTER_URL}/api/grafana/mock/panels")
            panels_status = response.status_code == 200
            
            response = await self.client.get(f"{GRAFANA_ADAPTER_URL}/api/grafana/mock/annotations")
            annotations_status = response.status_code == 200
            
            response = await self.client.get(f"{GRAFANA_ADAPTER_URL}/api/grafana/mock/alert-rules")
            alert_rules_status = response.status_code == 200
            
            # Test demo configuration setup
            response = await self.client.post(
                f"{GRAFANA_ADAPTER_URL}/api/grafana/mock/setup-demo-config",
                params={"tenant_id": self.test_tenant_id}
            )
            setup_demo_status = response.status_code == 200
            
            result = {
                "health": health_status,
                "mock_configs": mock_configs_status,
                "mock_dashboards": mock_dashboards_status,
                "mock_datasources": mock_datasources_status,
                "kpis": kpis_status,
                "incident_metrics": incident_metrics_status,
                "training_metrics": training_metrics_status,
                "exercise_metrics": exercise_metrics_status,
                "panels": panels_status,
                "annotations": annotations_status,
                "alert_rules": alert_rules_status,
                "setup_demo": setup_demo_status,
                "overall": all([
                    health_status, mock_configs_status, mock_dashboards_status,
                    mock_datasources_status, kpis_status, incident_metrics_status,
                    training_metrics_status, exercise_metrics_status, panels_status,
                    annotations_status, alert_rules_status, setup_demo_status
                ])
            }
            
            self.results["grafana_adapter"] = result
            print(f"✅ Grafana Adapter: {'PASS' if result['overall'] else 'FAIL'}")
            return result
            
        except Exception as e:
            print(f"❌ Grafana Adapter: FAIL - {str(e)}")
            result = {"error": str(e), "overall": False}
            self.results["grafana_adapter"] = result
            return result
    
    async def test_event_flow_integration(self) -> Dict[str, Any]:
        """Test end-to-end event flow between services"""
        print("🔄 Testing Event Flow Integration...")
        
        try:
            # Simulate BCM incident workflow
            workflow_events = []
            
            # 1. Create incident in TheHive (simulated)
            incident_event = {
                "event_type": "thehive.bcm.incident.created",
                "tenant_id": self.test_tenant_id,
                "data": {
                    "case_id": "case_test_001",
                    "title": "Integration Test Incident",
                    "severity": 3,
                    "incident_manager": "test@company.com"
                },
                "user_id": "integration_tester"
            }
            
            response = await self.client.post(f"{EVENTBUS_URL}/api/events/publish", json=incident_event)
            incident_created = response.status_code == 200
            workflow_events.append({"step": "incident_created", "success": incident_created})
            
            # 2. Start BPMN process (simulated)
            process_event = {
                "event_type": "bpmn.instance.started",
                "tenant_id": self.test_tenant_id,
                "data": {
                    "instance_id": "inst_test_001",
                    "process_id": "proc_001",
                    "triggered_by": "case_test_001"
                },
                "user_id": "system",
                "correlation_id": "workflow_001"
            }
            
            response = await self.client.post(f"{EVENTBUS_URL}/api/events/publish", json=process_event)
            process_started = response.status_code == 200
            workflow_events.append({"step": "process_started", "success": process_started})
            
            # 3. Trigger training assignment (simulated)
            training_event = {
                "event_type": "lms.training.assigned",
                "tenant_id": self.test_tenant_id,
                "data": {
                    "course_id": "course_001",
                    "user_email": "test@company.com",
                    "assignment_reason": "incident_response_training"
                },
                "user_id": "system",
                "correlation_id": "workflow_001"
            }
            
            response = await self.client.post(f"{EVENTBUS_URL}/api/events/publish", json=training_event)
            training_assigned = response.status_code == 200
            workflow_events.append({"step": "training_assigned", "success": training_assigned})
            
            # 4. Update KPI metrics (simulated)
            kpi_event = {
                "event_type": "grafana.kpi.updated",
                "tenant_id": self.test_tenant_id,
                "data": {
                    "metric": "incident_response_time",
                    "value": 4.2,
                    "period": "2024-Q1"
                },
                "user_id": "system",
                "correlation_id": "workflow_001"
            }
            
            response = await self.client.post(f"{EVENTBUS_URL}/api/events/publish", json=kpi_event)
            kpi_updated = response.status_code == 200
            workflow_events.append({"step": "kpi_updated", "success": kpi_updated})
            
            # 5. Verify event correlation
            response = await self.client.get(
                f"{EVENTBUS_URL}/api/events/history",
                params={
                    "tenant_id": self.test_tenant_id,
                    "correlation_id": "workflow_001",
                    "limit": 10
                }
            )
            correlation_check = response.status_code == 200
            workflow_events.append({"step": "correlation_check", "success": correlation_check})
            
            # Calculate overall workflow success
            workflow_success = all(event["success"] for event in workflow_events)
            
            result = {
                "workflow_events": workflow_events,
                "correlation_verified": correlation_check,
                "overall": workflow_success
            }
            
            print(f"✅ Event Flow Integration: {'PASS' if workflow_success else 'FAIL'}")
            return result
            
        except Exception as e:
            print(f"❌ Event Flow Integration: FAIL - {str(e)}")
            return {"error": str(e), "overall": False}
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all integration tests"""
        print("🚀 Starting BCM Platform Backend Integration Tests\n")
        
        # Run individual service tests
        await self.test_eventbus_health()
        await self.test_bpmn_service()
        await self.test_lms_adapter()
        await self.test_thehive_adapter()
        await self.test_grafana_adapter()
        
        # Run end-to-end integration test
        event_flow_result = await self.test_event_flow_integration()
        self.results["event_flow"] = event_flow_result
        
        # Calculate overall success
        service_results = [
            self.results["eventbus"]["overall"],
            self.results["bpmn_service"]["overall"],
            self.results["lms_adapter"]["overall"],
            self.results["thehive_adapter"]["overall"],
            self.results["grafana_adapter"]["overall"],
            event_flow_result["overall"]
        ]
        
        overall_success = all(service_results)
        success_count = sum(service_results)
        total_tests = len(service_results)
        
        print(f"\n📊 Integration Test Results:")
        print(f"   Tests Passed: {success_count}/{total_tests}")
        print(f"   Overall Status: {'✅ PASS' if overall_success else '❌ FAIL'}")
        
        self.results["summary"] = {
            "overall_success": overall_success,
            "tests_passed": success_count,
            "total_tests": total_tests,
            "success_rate": (success_count / total_tests) * 100
        }
        
        return self.results
    
    async def close(self):
        """Clean up resources"""
        await self.client.aclose()

async def main():
    """Main test runner"""
    tester = IntegrationTester()
    
    try:
        results = await tester.run_all_tests()
        
        # Save results to file
        with open("integration_test_results.json", "w") as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n💾 Results saved to integration_test_results.json")
        
        return results["summary"]["overall_success"]
        
    finally:
        await tester.close()

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)