"""
Test EventBus Integration for Plans Service
Usage: python3 test_eventbus_integration.py
"""

import asyncio
import httpx
import json
from datetime import datetime


async def test_plan_created_event():
    """Test plans.plan.created event"""
    print("\n" + "="*60)
    print("TEST 1: Create Plan -> plans.plan.created event")
    print("="*60)

    async with httpx.AsyncClient() as client:
        # Create a plan
        plan_data = {
            "tenant_id": "test-tenant",
            "plan_code": "BC-TEST-001",
            "plan_name": "Test Business Continuity Plan",
            "plan_type": "business_continuity",
            "priority": "high",
            "objective": "Test objective",
            "scope": "Test scope",
            "rto_hours": 4,
            "rpo_hours": 1,
            "mtpd_hours": 24,
            "plan_owner_user_id": "user-test-owner",
            "team_leader_user_id": "user-test-leader"
        }

        try:
            response = await client.post(
                "http://localhost:8023/api/plans/plans",
                json=plan_data,
                timeout=10.0
            )
            print(f"\nAPI Response: {response.status_code}")
            if response.status_code == 200:
                plan = response.json()
                print(f"Created Plan ID: {plan.get('plan_id')}")
                print(f"Plan Code: {plan.get('plan_code')}")
                print(f"Status: {plan.get('status')}")

                # Check EventBus for the event
                await asyncio.sleep(1)  # Give EventBus time to receive
                event_response = await client.get(
                    "http://localhost:8001/topics/plans.plan.created",
                    timeout=5.0
                )
                if event_response.status_code == 200:
                    events = event_response.json()
                    print(f"\n✓ EventBus received {len(events.get('events', []))} event(s)")
                    if events.get('events'):
                        latest_event = events['events'][-1]
                        print(f"  Event data: {json.dumps(latest_event.get('data'), indent=2)}")
                else:
                    print(f"⨯ Failed to check EventBus: {event_response.status_code}")

                return plan.get('plan_id')
            else:
                print(f"⨯ Failed to create plan: {response.text}")
                return None
        except Exception as e:
            print(f"⨯ Error: {e}")
            return None


async def test_plan_approved_event(plan_id: int):
    """Test plans.plan.approved event"""
    print("\n" + "="*60)
    print("TEST 2: Approve Plan -> plans.plan.approved event")
    print("="*60)

    async with httpx.AsyncClient() as client:
        try:
            # First, submit for review
            submit_response = await client.post(
                f"http://localhost:8023/api/plans/plans/{plan_id}/submit",
                json={"user_id": "user-reviewer"},
                timeout=10.0
            )
            print(f"\nSubmit for Review: {submit_response.status_code}")

            # Then approve
            approve_data = {
                "approved_by": "user-admin",
                "approval_notes": "Test approval - all requirements met"
            }
            response = await client.post(
                f"http://localhost:8023/api/plans/plans/{plan_id}/approve",
                json=approve_data,
                timeout=10.0
            )
            print(f"Approve Plan: {response.status_code}")

            if response.status_code == 200:
                plan = response.json()
                print(f"Plan Status: {plan.get('status')}")
                print(f"Approved By: {plan.get('approved_by_user_id')}")

                # Check EventBus for the event
                await asyncio.sleep(1)
                event_response = await client.get(
                    "http://localhost:8001/topics/plans.plan.approved",
                    timeout=5.0
                )
                if event_response.status_code == 200:
                    events = event_response.json()
                    print(f"\n✓ EventBus received {len(events.get('events', []))} event(s)")
                    if events.get('events'):
                        latest_event = events['events'][-1]
                        print(f"  Event data: {json.dumps(latest_event.get('data'), indent=2)}")
                else:
                    print(f"⨯ Failed to check EventBus: {event_response.status_code}")
            else:
                print(f"⨯ Failed to approve plan: {response.text}")
        except Exception as e:
            print(f"⨯ Error: {e}")


async def test_plan_activated_event(plan_id: int):
    """Test plans.plan.activated event"""
    print("\n" + "="*60)
    print("TEST 3: Activate Plan -> plans.plan.activated event")
    print("="*60)

    async with httpx.AsyncClient() as client:
        try:
            # First, add a contact list (required for activation)
            contact_list_data = {
                "tenant_id": "test-tenant",
                "plan_id": plan_id,
                "list_name": "Emergency Contacts",
                "list_type": "internal",
                "contacts": [
                    {
                        "name": "John Doe",
                        "role": "BC Coordinator",
                        "phone": "+1-555-0001",
                        "email": "john.doe@example.com"
                    }
                ]
            }
            contact_response = await client.post(
                "http://localhost:8023/api/plans/contact-lists",
                json=contact_list_data,
                timeout=10.0
            )
            print(f"\nAdd Contact List: {contact_response.status_code}")

            # Activate the plan
            activate_data = {
                "activated_by": "user-admin"
            }
            response = await client.post(
                f"http://localhost:8023/api/plans/plans/{plan_id}/activate",
                json=activate_data,
                timeout=10.0
            )
            print(f"Activate Plan: {response.status_code}")

            if response.status_code == 200:
                plan = response.json()
                print(f"Plan Status: {plan.get('status')}")

                # Check EventBus for the event
                await asyncio.sleep(1)
                event_response = await client.get(
                    "http://localhost:8001/topics/plans.plan.activated",
                    timeout=5.0
                )
                if event_response.status_code == 200:
                    events = event_response.json()
                    print(f"\n✓ EventBus received {len(events.get('events', []))} event(s)")
                    if events.get('events'):
                        latest_event = events['events'][-1]
                        print(f"  Event data: {json.dumps(latest_event.get('data'), indent=2)}")
                else:
                    print(f"⨯ Failed to check EventBus: {event_response.status_code}")
            else:
                print(f"⨯ Failed to activate plan: {response.text}")
        except Exception as e:
            print(f"⨯ Error: {e}")


async def test_review_completed_event(plan_id: int):
    """Test plans.review.completed event"""
    print("\n" + "="*60)
    print("TEST 4: Create Review -> plans.review.completed event")
    print("="*60)

    async with httpx.AsyncClient() as client:
        try:
            review_data = {
                "tenant_id": "test-tenant",
                "review_type": "periodic",
                "is_current": True,
                "is_effective": True,
                "findings": [
                    "Plan is up to date with current procedures",
                    "All contact information verified"
                ],
                "recommendations": [
                    "Update RTO based on new SLA requirements",
                    "Add cloud backup procedures"
                ],
                "action_items": [
                    {
                        "description": "Update RTO to 2 hours",
                        "assigned_to": "user-test-owner",
                        "due_date": "2025-11-01"
                    }
                ]
            }

            response = await client.post(
                f"http://localhost:8023/api/plans/plans/{plan_id}/reviews",
                json=review_data,
                timeout=10.0
            )
            print(f"\nAPI Response: {response.status_code}")

            if response.status_code == 200:
                review = response.json()
                print(f"Review ID: {review.get('review_id')}")
                print(f"Review Type: {review.get('review_type')}")
                print(f"Is Effective: {review.get('is_effective')}")

                # Check EventBus for the event
                await asyncio.sleep(1)
                event_response = await client.get(
                    "http://localhost:8001/topics/plans.review.completed",
                    timeout=5.0
                )
                if event_response.status_code == 200:
                    events = event_response.json()
                    print(f"\n✓ EventBus received {len(events.get('events', []))} event(s)")
                    if events.get('events'):
                        latest_event = events['events'][-1]
                        print(f"  Event data: {json.dumps(latest_event.get('data'), indent=2)}")
                else:
                    print(f"⨯ Failed to check EventBus: {event_response.status_code}")
            else:
                print(f"⨯ Failed to create review: {response.text}")
        except Exception as e:
            print(f"⨯ Error: {e}")


async def check_services():
    """Check if required services are running"""
    print("\n" + "="*60)
    print("CHECKING SERVICES")
    print("="*60)

    async with httpx.AsyncClient() as client:
        # Check Plans Service
        try:
            response = await client.get("http://localhost:8023/health", timeout=5.0)
            if response.status_code == 200:
                print("✓ Plans Service is running on port 8023")
            else:
                print("⨯ Plans Service not responding properly")
                return False
        except Exception as e:
            print(f"⨯ Plans Service not available: {e}")
            return False

        # Check EventBus
        try:
            response = await client.get("http://localhost:8001/health", timeout=5.0)
            if response.status_code == 200:
                print("✓ EventBus is running on port 8001")
            else:
                print("⨯ EventBus not responding properly")
                return False
        except Exception as e:
            print(f"⨯ EventBus not available: {e}")
            return False

    return True


async def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("PLANS SERVICE - EVENTBUS INTEGRATION TEST")
    print("="*60)

    # Check if services are running
    if not await check_services():
        print("\n⨯ Required services are not running. Please start:")
        print("  1. EventBus: cd eventbus && uvicorn main:app --port 8001")
        print("  2. Plans Service: cd plans_service && uvicorn main:app --port 8023")
        return

    # Run tests
    plan_id = await test_plan_created_event()

    if plan_id:
        await test_plan_approved_event(plan_id)
        await test_plan_activated_event(plan_id)
        await test_review_completed_event(plan_id)

    print("\n" + "="*60)
    print("TESTS COMPLETED")
    print("="*60)
    print("\nTo view all events in EventBus:")
    print("  curl http://localhost:8001/topics/plans.plan.created")
    print("  curl http://localhost:8001/topics/plans.plan.approved")
    print("  curl http://localhost:8001/topics/plans.plan.activated")
    print("  curl http://localhost:8001/topics/plans.review.completed")
    print()


if __name__ == "__main__":
    asyncio.run(main())
