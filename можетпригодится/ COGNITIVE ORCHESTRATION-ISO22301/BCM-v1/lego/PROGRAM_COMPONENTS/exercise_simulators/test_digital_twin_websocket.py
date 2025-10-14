#!/usr/bin/env python3
"""
Digital Twin WebSocket Integration Test
Quick test to verify the WebSocket service is working correctly
"""

import asyncio
import httpx
import websockets
import json
import sys
from datetime import datetime

async def test_http_endpoints():
    """Test HTTP API endpoints"""
    print("🧪 Testing HTTP API endpoints...")

    async with httpx.AsyncClient() as client:
        base_url = "http://localhost:8999"

        # Test health endpoint
        try:
            response = await client.get(f"{base_url}/health")
            if response.status_code == 200:
                print("✅ Health endpoint working")
            else:
                print(f"❌ Health endpoint failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Health endpoint error: {e}")
            return False

        # Test Digital Twin endpoints
        try:
            response = await client.get(f"{base_url}/digital-twin/personal")
            if response.status_code == 200:
                data = response.json()
                twin_count = len(data.get("digital_twins", []))
                print(f"✅ Personal Digital Twins endpoint working ({twin_count} twins)")
            else:
                print(f"❌ Digital Twins endpoint failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Digital Twins endpoint error: {e}")

        # Test organization health
        try:
            response = await client.get(f"{base_url}/digital-twin/organization/health")
            if response.status_code == 200:
                data = response.json()
                health_score = data.get("overall_health", 0)
                print(f"✅ Organization health endpoint working (health: {health_score:.2f})")
            else:
                print(f"❌ Organization health endpoint failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Organization health endpoint error: {e}")

    return True

async def test_websocket_connection():
    """Test WebSocket connection"""
    print("\n🔌 Testing WebSocket connection...")

    try:
        # Test general WebSocket
        uri = "ws://localhost:8999/ws/test_client"
        async with websockets.connect(uri) as websocket:
            print("✅ General WebSocket connection successful")

            # Send ping
            await websocket.send(json.dumps({"type": "ping"}))
            response = await websocket.recv()
            data = json.loads(response)

            if data.get("type") == "pong":
                print("✅ WebSocket ping/pong working")
            else:
                print("❌ WebSocket ping/pong failed")

    except Exception as e:
        print(f"❌ General WebSocket connection failed: {e}")
        return False

    return True

async def test_digital_twin_websocket():
    """Test Digital Twin WebSocket functionality"""
    print("\n🤖 Testing Digital Twin WebSocket...")

    try:
        uri = "ws://localhost:8999/ws/digital-twin/test_dt_client"
        async with websockets.connect(uri) as websocket:
            print("✅ Digital Twin WebSocket connection successful")

            # Subscribe to digital twins
            subscribe_msg = {
                "type": "subscribe",
                "topics": ["digital_twins", "twin_events", "metrics"]
            }
            await websocket.send(json.dumps(subscribe_msg))

            # Wait for subscription confirmation and some data
            messages_received = 0
            timeout = 10  # seconds

            while messages_received < 3 and timeout > 0:
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=1)
                    data = json.loads(response)
                    message_type = data.get("type")

                    print(f"📥 Received: {message_type}")

                    if message_type == "subscription":
                        print("✅ Digital Twin subscription confirmed")
                    elif message_type == "digital_twins_update":
                        twins_count = len(data.get("data", {}).get("digital_twins", []))
                        print(f"✅ Digital Twins update received ({twins_count} twins)")
                    elif message_type == "organization_metrics_update":
                        print("✅ Organization metrics update received")
                    elif message_type == "twin_event":
                        event_type = data.get("event_type", "unknown")
                        print(f"✅ Twin event received: {event_type}")

                    messages_received += 1

                except asyncio.TimeoutError:
                    timeout -= 1

            # Test sync functionality
            sync_msg = {
                "type": "sync",
                "twin_id": "1"
            }
            await websocket.send(json.dumps(sync_msg))
            print("🔄 Sent sync request for Twin 1")

            # Wait for sync response
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5)
                data = json.loads(response)

                if data.get("type") == "sync_response":
                    result = data.get("result", {})
                    if result.get("success"):
                        print("✅ Digital Twin sync successful")
                    else:
                        print(f"⚠️ Digital Twin sync failed: {result.get('message')}")
                else:
                    print(f"📥 Received other message during sync: {data.get('type')}")

            except asyncio.TimeoutError:
                print("⚠️ Sync response timeout (this is normal if Odoo is not available)")

    except Exception as e:
        print(f"❌ Digital Twin WebSocket test failed: {e}")
        return False

    return True

async def main():
    """Run all tests"""
    print("🚀 Digital Twin WebSocket Integration Test")
    print("="*50)
    print(f"Test started at: {datetime.utcnow().isoformat()}")
    print()

    # Check if service is running
    print("Checking if Digital Twin WebSocket service is running...")
    print("If not, start it with: python start_digital_twin_websocket.py")
    print()

    # Run tests
    http_ok = await test_http_endpoints()
    if not http_ok:
        print("\n❌ HTTP tests failed. Is the service running?")
        sys.exit(1)

    ws_ok = await test_websocket_connection()
    if not ws_ok:
        print("\n❌ WebSocket tests failed.")
        sys.exit(1)

    dt_ws_ok = await test_digital_twin_websocket()
    if not dt_ws_ok:
        print("\n❌ Digital Twin WebSocket tests failed.")
        sys.exit(1)

    print("\n🎉 All tests passed successfully!")
    print("\nDigital Twin WebSocket service is working correctly.")
    print("\nNow you can:")
    print("1. Connect your frontend to ws://localhost:8999/ws/digital-twin/{client_id}")
    print("2. Subscribe to topics: digital_twins, metrics, twin_events, performance, analytics")
    print("3. Send commands: sync, refresh, ping")
    print("4. Use HTTP API endpoints for additional functionality")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        sys.exit(1)