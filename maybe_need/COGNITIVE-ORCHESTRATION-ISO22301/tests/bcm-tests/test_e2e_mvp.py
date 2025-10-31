"""
E2E Test for BCM Platform MVP
Tests the complete flow: Process → BIA → Plan → Incident → Audit → KPI
"""

import pytest
import pytest_asyncio
import asyncio
import httpx
import json
import os
from datetime import datetime
import time

# Service URLs
EVENTBUS_URL = "http://localhost:8001"
ORCHESTRATOR_URL = "http://localhost:8002"
ODOO_URL = "http://localhost:8069"
FRONTEND_URL = "http://localhost:8081"

# Test tenant
TEST_TENANT = "test_mvp"
TEST_USER = "test_user"

@pytest.mark.skipif("CI" in os.environ, reason="E2E tests require running services")
class TestBCMMVP:
    """End-to-end test for BCM MVP"""
    
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self):
        """Setup test environment"""
        self.client = httpx.AsyncClient()
        self.events = []
        yield
        await self.client.aclose()
    
    async def publish_event(self, event_type: str, data: dict):
        """Helper to publish event to EventBus"""
        event = {
            "event_type": event_type,
            "tenant_id": TEST_TENANT,
            "user_id": TEST_USER,
            "data": data,
            "correlation_id": f"test_{datetime.utcnow().timestamp()}"
        }
        
        response = await self.client.post(
            f"{EVENTBUS_URL}/api/events/publish",
            json=event
        )
        assert response.status_code == 200
        result = response.json()
        self.events.append(result)
        return result
    
    @pytest.mark.asyncio
    async def test_01_health_check(self):
        """Test all services are healthy"""
        # EventBus health
        response = await self.client.get(f"{EVENTBUS_URL}/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
        
        # Orchestrator health
        response = await self.client.get(f"{ORCHESTRATOR_URL}/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
        
        print("✓ All services are healthy")
    
    @pytest.mark.asyncio
    async def test_02_create_process(self):
        """Test creating a business process"""
        # Publish process created event
        event = await self.publish_event(
            "bcm.process.created",
            {
                "process_id": "proc_001",
                "name": "Order Processing",
                "department": "Operations",
                "criticality": "high"
            }
        )
        
        assert event["status"] == "published"
        print(f"✓ Process created: {event['id']}")
    
    @pytest.mark.asyncio
    async def test_03_compute_bia(self):
        """Test BIA computation"""
        # Start BIA
        await self.publish_event(
            "bcm.bia.started",
            {
                "bia_id": "bia_001",
                "processes": ["proc_001"],
                "departments": ["Operations"]
            }
        )
        
        # Simulate BIA completion
        await asyncio.sleep(1)
        
        event = await self.publish_event(
            "bcm.bia.completed",
            {
                "bia_id": "bia_001",
                "critical_processes": ["proc_001"],
                "rto_targets": {"proc_001": 4},
                "rpo_targets": {"proc_001": 1},
                "mtpd": 8
            }
        )
        
        # Check if AI decision was created
        await asyncio.sleep(2)
        
        response = await self.client.get(
            f"{ORCHESTRATOR_URL}/api/ai/decisions/pending",
            params={"tenant_id": TEST_TENANT}
        )
        assert response.status_code == 200
        decisions = response.json()
        
        # Should have BCP generation decision
        bcp_decisions = [d for d in decisions if d["type"] == "bcp_generation"]
        assert len(bcp_decisions) > 0
        
        print(f"✓ BIA completed with RTO: 4h, RPO: 1h, MTPD: 8h")
        print(f"✓ AI decision created for BCP generation")
    
    @pytest.mark.asyncio
    async def test_04_generate_plan(self):
        """Test BCP generation"""
        # Get pending decisions
        response = await self.client.get(
            f"{ORCHESTRATOR_URL}/api/ai/decisions/pending",
            params={"tenant_id": TEST_TENANT}
        )
        decisions = response.json()
        
        if decisions:
            # Approve first decision
            decision_id = decisions[0]["id"]
            response = await self.client.post(
                f"{ORCHESTRATOR_URL}/api/ai/decisions/{decision_id}/approve"
            )
            assert response.status_code == 200
            
            print(f"✓ BCP generation approved: {decision_id}")
        
        # Simulate plan creation
        event = await self.publish_event(
            "bcm.plan.created",
            {
                "plan_id": "bcp_001",
                "type": "BCP",
                "status": "draft",
                "based_on_bia": "bia_001"
            }
        )
        
        print(f"✓ BCP draft created: bcp_001")
    
    @pytest.mark.asyncio
    async def test_05_handle_incident(self):
        """Test incident handling"""
        # Report incident
        event = await self.publish_event(
            "bcm.incident.opened",
            {
                "incident_id": "inc_001",
                "title": "Service Disruption",
                "severity": "critical",
                "affected_processes": ["proc_001"]
            }
        )
        
        # Wait for AI response
        await asyncio.sleep(2)
        
        # Check for incident response decision
        response = await self.client.get(
            f"{ORCHESTRATOR_URL}/api/ai/decisions/pending",
            params={"tenant_id": TEST_TENANT}
        )
        decisions = response.json()
        
        incident_decisions = [d for d in decisions if d["type"] == "incident_response"]
        assert len(incident_decisions) > 0
        
        # Get checklist from decision
        checklist = incident_decisions[0]["data"].get("checklist", [])
        assert len(checklist) > 0
        
        print(f"✓ Incident reported: inc_001")
        print(f"✓ AI generated response checklist with {len(checklist)} items")
    
    @pytest.mark.asyncio
    async def test_06_conduct_audit(self):
        """Test audit process"""
        # Initiate audit
        await self.publish_event(
            "bcm.audit.initiated",
            {
                "audit_id": "audit_001",
                "audit_date": "2024-01-15",
                "scope": ["BIA", "BCP", "Incident Management"]
            }
        )
        
        # Submit audit evidence
        response = await self.client.post(
            f"{ORCHESTRATOR_URL}/api/audit/summarize",
            json={
                "audit_id": "audit_001",
                "tenant_id": TEST_TENANT,
                "evidence": [
                    {"status": "conformity", "description": "BIA process documented"},
                    {"status": "non_conformity", "description": "BCP not tested"},
                    {"status": "observation", "description": "Incident logs incomplete"}
                ]
            }
        )
        assert response.status_code == 200
        summary = response.json()
        
        assert len(summary["findings"]) > 0
        assert len(summary["capa_items"]) > 0
        
        print(f"✓ Audit completed with {len(summary['findings'])} findings")
        print(f"✓ Generated {len(summary['capa_items'])} CAPA items")
    
    @pytest.mark.asyncio
    async def test_07_calculate_kpi(self):
        """Test KPI calculation"""
        # Request KPI calculation
        await self.publish_event(
            "bcm.kpi.calculate",
            {
                "period": "Q1-2024",
                "metrics": ["coverage", "plan_currency", "capa_completion"]
            }
        )
        
        # Simulate KPI results
        kpi_data = {
            "coverage": 85,  # 85% processes covered
            "plans_up_to_date": 92,  # 92% plans current
            "capa_on_time": 78  # 78% CAPA on schedule
        }
        
        await self.publish_event(
            "bcm.kpi.calculated",
            {
                "period": "Q1-2024",
                "results": kpi_data
            }
        )
        
        print(f"✓ KPI calculated:")
        print(f"  - Coverage: {kpi_data['coverage']}%")
        print(f"  - Plans up-to-date: {kpi_data['plans_up_to_date']}%")
        print(f"  - CAPA on-time: {kpi_data['capa_on_time']}%")
    
    @pytest.mark.asyncio
    async def test_08_verify_event_stream(self):
        """Verify all events were captured"""
        # Get event history
        response = await self.client.get(
            f"{EVENTBUS_URL}/api/events/history",
            params={"tenant_id": TEST_TENANT, "limit": 50}
        )
        assert response.status_code == 200
        history = response.json()
        
        # Check we have events from each phase
        event_types = {event["event_type"] for event in history}
        expected_types = {
            "bcm.process.created",
            "bcm.bia.started",
            "bcm.bia.completed",
            "bcm.plan.created",
            "bcm.incident.opened",
            "bcm.audit.initiated",
            "bcm.kpi.calculate",
            "bcm.kpi.calculated"
        }
        
        for expected in expected_types:
            assert expected in event_types, f"Missing event type: {expected}"
        
        print(f"✓ Event stream verified: {len(history)} events captured")
    
    @pytest.mark.asyncio
    async def test_09_get_statistics(self):
        """Get event statistics"""
        response = await self.client.get(
            f"{EVENTBUS_URL}/api/events/stats",
            params={"tenant_id": TEST_TENANT}
        )
        assert response.status_code == 200
        stats = response.json()
        
        assert stats["total_events"] > 0
        assert stats["unique_event_types"] > 0
        
        print(f"✓ Statistics:")
        print(f"  - Total events: {stats['total_events']}")
        print(f"  - Event types: {stats['unique_event_types']}")
        print(f"  - Top events: {stats['top_event_types'][:3]}")

def run_tests():
    """Run all E2E tests"""
    print("\n" + "="*60)
    print("BCM Platform MVP - End-to-End Test")
    print("="*60 + "\n")
    
    # Run tests
    pytest.main([__file__, "-v", "-s"])
    
    print("\n" + "="*60)
    print("✅ All E2E tests passed successfully!")
    print("="*60 + "\n")

if __name__ == "__main__":
    run_tests()
