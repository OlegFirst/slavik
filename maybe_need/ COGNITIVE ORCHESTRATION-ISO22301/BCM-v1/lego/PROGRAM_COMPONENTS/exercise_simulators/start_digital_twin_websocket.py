#!/usr/bin/env python3
"""
Digital Twin WebSocket Service Startup Script
Combines API Gateway with WebSocket for real-time Digital Twin updates

Usage:
    python start_digital_twin_websocket.py

Features:
    - Combined API Gateway + WebSocket service
    - Auto-start Digital Twin data streams
    - Health monitoring and connection management
    - Graceful shutdown handling
    - Real-time Personal Digital Twin updates
    - Organization health metrics streaming
"""

import asyncio
import logging
import signal
import sys
import os
from datetime import datetime
import uvicorn
from contextlib import asynccontextmanager

# Add current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from simple_gateway import app
from websocket_manager import (
    connection_manager,
    live_data_manager,
    digital_twin_manager
)

# Enhanced logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/Users/MD/ISO-22301/api/digital_twin_websocket.log')
    ]
)
logger = logging.getLogger(__name__)

class DigitalTwinWebSocketService:
    """
    Digital Twin WebSocket Service Manager
    Handles startup, monitoring, and graceful shutdown
    """

    def __init__(self, host: str = "0.0.0.0", port: int = 8999):
        self.host = host
        self.port = port
        self.server = None
        self.monitoring_task = None
        self.startup_complete = False

    async def start_data_streams(self):
        """Start all Digital Twin data streams"""
        logger.info("🔄 Starting Digital Twin data streams...")

        try:
            # Start Personal Digital Twin stream (every 10 seconds)
            await digital_twin_manager.start_personal_twins_stream(interval=10)
            logger.info("✅ Personal Digital Twins stream started (10s interval)")

            # Start Organization metrics stream (every 30 seconds)
            await digital_twin_manager.start_organization_metrics_stream(interval=30)
            logger.info("✅ Organization metrics stream started (30s interval)")

            # Start general system streams
            await live_data_manager.start_metrics_stream(interval=5)
            logger.info("✅ System metrics stream started (5s interval)")

            await live_data_manager.start_service_health_stream(interval=15)
            logger.info("✅ Service health stream started (15s interval)")

            self.startup_complete = True
            logger.info("🚀 All Digital Twin data streams are active!")

        except Exception as e:
            logger.error(f"❌ Failed to start data streams: {e}")
            raise

    async def monitor_health(self):
        """Monitor service health and connections"""
        while True:
            try:
                await asyncio.sleep(60)  # Check every minute

                # Log connection statistics
                active_connections = len(connection_manager.active_connections)
                total_subscriptions = sum(len(subs) for subs in connection_manager.subscriptions.values())

                logger.info(
                    f"📊 Health Check: {active_connections} active connections, "
                    f"{total_subscriptions} total subscriptions"
                )

                # Check if streams are still running
                dt_streams = len(digital_twin_manager.update_tasks)
                general_streams = len(live_data_manager.update_tasks)

                if dt_streams == 0 and self.startup_complete:
                    logger.warning("⚠️ Digital Twin streams stopped unexpectedly, restarting...")
                    await self.start_data_streams()

                logger.info(f"🔄 Streams active: {dt_streams} Digital Twin, {general_streams} general")

            except Exception as e:
                logger.error(f"❌ Health monitoring error: {e}")
                await asyncio.sleep(60)

    async def graceful_shutdown(self):
        """Perform graceful shutdown"""
        logger.info("🛑 Starting graceful shutdown...")

        try:
            # Stop monitoring
            if self.monitoring_task:
                self.monitoring_task.cancel()
                try:
                    await self.monitoring_task
                except asyncio.CancelledError:
                    pass

            # Stop all data streams
            digital_twin_manager.stop_all_streams()
            live_data_manager.stop_all_streams()
            logger.info("✅ All data streams stopped")

            # Cleanup Digital Twin manager
            await digital_twin_manager.cleanup()
            logger.info("✅ Digital Twin manager cleaned up")

            # Disconnect all WebSocket clients
            if connection_manager.active_connections:
                await connection_manager.broadcast_all({
                    "type": "server_shutdown",
                    "message": "Server is shutting down gracefully",
                    "timestamp": datetime.utcnow().isoformat()
                })
                logger.info(f"✅ Notified {len(connection_manager.active_connections)} clients of shutdown")

            logger.info("👋 Digital Twin WebSocket Service shutdown complete")

        except Exception as e:
            logger.error(f"❌ Error during shutdown: {e}")

    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            logger.info(f"📡 Received signal {signum}")
            asyncio.create_task(self.graceful_shutdown())
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

    async def start_service(self):
        """Start the Digital Twin WebSocket service"""
        try:
            logger.info("🚀 Starting Digital Twin WebSocket Service")
            logger.info(f"📍 Service will be available at:")
            logger.info(f"   - HTTP API: http://{self.host}:{self.port}")
            logger.info(f"   - General WebSocket: ws://{self.host}:{self.port}/ws/{{client_id}}")
            logger.info(f"   - Digital Twin WebSocket: ws://{self.host}:{self.port}/ws/digital-twin/{{client_id}}")

            # Setup signal handlers
            self.setup_signal_handlers()

            # Start data streams
            await self.start_data_streams()

            # Start health monitoring
            self.monitoring_task = asyncio.create_task(self.monitor_health())

            # Start the server
            config = uvicorn.Config(
                app=app,
                host=self.host,
                port=self.port,
                log_level="info",
                access_log=True
            )

            server = uvicorn.Server(config)
            logger.info("✅ Digital Twin WebSocket Service started successfully!")

            await server.serve()

        except Exception as e:
            logger.error(f"❌ Failed to start service: {e}")
            await self.graceful_shutdown()
            raise


def print_service_info():
    """Print service information and usage examples"""
    print("\n" + "="*60)
    print("🎯 DIGITAL TWIN WEBSOCKET SERVICE")
    print("="*60)
    print(f"📅 Started: {datetime.utcnow().isoformat()}")
    print(f"🌐 Host: 0.0.0.0:8999")
    print()
    print("📡 AVAILABLE ENDPOINTS:")
    print("   HTTP API:")
    print("     GET  /health")
    print("     GET  /digital-twin/personal")
    print("     GET  /digital-twin/personal/{twin_id}")
    print("     POST /digital-twin/personal/{twin_id}/sync")
    print("     GET  /digital-twin/organization/metrics")
    print("     GET  /digital-twin/organization/health")
    print()
    print("   WebSocket:")
    print("     ws://localhost:8999/ws/{client_id}")
    print("     ws://localhost:8999/ws/digital-twin/{client_id}")
    print()
    print("🔄 DATA STREAMS:")
    print("   - Personal Digital Twins: Updates every 10 seconds")
    print("   - Organization Metrics: Updates every 30 seconds")
    print("   - System Health: Updates every 15 seconds")
    print("   - Performance Metrics: Updates every 5 seconds")
    print()
    print("📋 WEBSOCKET TOPICS:")
    print("   - 'digital_twins': Personal Digital Twin updates")
    print("   - 'metrics': Organization health metrics")
    print("   - 'twin_events': Digital Twin events (sync, create, update)")
    print("   - 'health': Service health monitoring")
    print("   - 'notifications': System notifications")
    print("   - 'alerts': Critical alerts")
    print()
    print("🎮 WEBSOCKET COMMANDS:")
    print("   - subscribe: {'type': 'subscribe', 'topics': ['digital_twins', 'metrics']}")
    print("   - sync: {'type': 'sync', 'twin_id': '1'}")
    print("   - refresh: {'type': 'refresh'}")
    print("   - ping: {'type': 'ping'}")
    print()
    print("🛑 To stop: Ctrl+C")
    print("="*60)


async def main():
    """Main application entry point"""
    try:
        # Print service information
        print_service_info()

        # Create and start service
        service = DigitalTwinWebSocketService(host="0.0.0.0", port=8999)
        await service.start_service()

    except KeyboardInterrupt:
        logger.info("🛑 Service interrupted by user")
    except Exception as e:
        logger.error(f"❌ Service failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Digital Twin WebSocket Service stopped")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)