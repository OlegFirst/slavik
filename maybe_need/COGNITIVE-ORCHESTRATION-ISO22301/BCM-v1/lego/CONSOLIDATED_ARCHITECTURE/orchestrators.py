"""
Cognitive Orchestration Controller
Python wrapper for our JavaScript orchestrators with production integrations
"""

import asyncio
import json
import logging
import subprocess
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class JavaScriptOrchestratorWrapper:
    """Base wrapper for JavaScript orchestrators"""

    def __init__(self, orchestrator_name: str, orchestrator_path: str):
        self.name = orchestrator_name
        self.path = Path(orchestrator_path)
        self.process = None
        self.is_running = False

    async def start(self):
        """Start the JavaScript orchestrator process"""
        try:
            # Create a Node.js wrapper script for the orchestrator
            wrapper_script = f"""
const {self.name.title()}Orchestrator = require('./{self.path.name}');

class PythonBridge {{
    constructor() {{
        this.orchestrator = new {self.name.title()}Orchestrator();
        this.setupCommunication();
    }}

    async setupCommunication() {{
        await this.orchestrator.initialize();

        process.stdin.on('data', async (data) => {{
            try {{
                const request = JSON.parse(data.toString());
                const result = await this.orchestrator.handle(request.data, request.context || {{}});

                process.stdout.write(JSON.stringify({{
                    success: true,
                    requestId: request.id,
                    result: result
                }}) + '\\n');
            }} catch (error) {{
                process.stdout.write(JSON.stringify({{
                    success: false,
                    requestId: request.id,
                    error: error.message
                }}) + '\\n');
            }}
        }});

        // Send ready signal
        process.stdout.write(JSON.stringify({{ready: true}}) + '\\n');
    }}
}}

new PythonBridge();
"""

            # Write wrapper script
            wrapper_path = self.path.parent / f"{self.name}_wrapper.js"
            wrapper_path.write_text(wrapper_script)

            # Start Node.js process
            self.process = await asyncio.create_subprocess_exec(
                'node', str(wrapper_path),
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(self.path.parent)
            )

            # Wait for ready signal
            ready_line = await self.process.stdout.readline()
            ready_data = json.loads(ready_line.decode())

            if ready_data.get('ready'):
                self.is_running = True
                logger.info(f"✅ {self.name} orchestrator started")
            else:
                raise Exception(f"Failed to start {self.name} orchestrator")

        except Exception as error:
            logger.error(f"❌ Failed to start {self.name}: {error}")
            raise

    async def handle(self, request_data: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Send request to JavaScript orchestrator and get response"""
        if not self.is_running:
            raise Exception(f"{self.name} orchestrator is not running")

        try:
            request = {
                'id': f"{self.name}-{asyncio.get_event_loop().time()}",
                'data': request_data,
                'context': context or {}
            }

            # Send request
            request_json = json.dumps(request) + '\\n'
            self.process.stdin.write(request_json.encode())
            await self.process.stdin.drain()

            # Get response
            response_line = await self.process.stdout.readline()
            response_data = json.loads(response_line.decode())

            if response_data.get('success'):
                return response_data['result']
            else:
                raise Exception(response_data.get('error', 'Unknown error'))

        except Exception as error:
            logger.error(f"❌ {self.name} request failed: {error}")
            raise

    async def get_health_status(self) -> Dict[str, Any]:
        """Get orchestrator health status"""
        try:
            if not self.is_running:
                return {"status": "stopped", "error": "Not running"}

            result = await self.handle({"type": "health-check"})
            return result

        except Exception as error:
            return {"status": "error", "error": str(error)}

    async def stop(self):
        """Stop the orchestrator process"""
        if self.process:
            self.process.terminate()
            await self.process.wait()
            self.is_running = False
            logger.info(f"🛑 {self.name} orchestrator stopped")


class CognitiveOrchestrationController:
    """
    Main controller that wraps our JavaScript orchestrators
    with production integrations (Redis, PostgreSQL, Docker)
    """

    def __init__(self, integrations: Dict[str, Any] = None):
        self.integrations = integrations or {}
        self.orchestrators = {}
        self.metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "average_response_time": 0.0
        }

        # Initialize orchestrator wrappers
        orchestrator_base_path = Path(__file__).parent.parent / "ORCHESTRATORS"

        self.orchestrators = {
            'system': JavaScriptOrchestratorWrapper('system', orchestrator_base_path / 'system-orchestrator.js'),
            'bridge': JavaScriptOrchestratorWrapper('bridge', orchestrator_base_path / 'bridge-orchestrator.js'),
            'program': JavaScriptOrchestratorWrapper('program', orchestrator_base_path / 'program-orchestrator.js'),
            'client': JavaScriptOrchestratorWrapper('client', orchestrator_base_path / 'client-orchestrator.js'),
            'sandbox': JavaScriptOrchestratorWrapper('sandbox', orchestrator_base_path / 'sandbox-orchestrator.js')
        }

        # Add integrations to each orchestrator
        for orchestrator in self.orchestrators.values():
            orchestrator.integrations = self.integrations

    async def start(self):
        """Start all orchestrators"""
        logger.info("🚀 Starting Cognitive Orchestration Controller...")

        start_tasks = []
        for name, orchestrator in self.orchestrators.items():
            start_tasks.append(orchestrator.start())

        try:
            await asyncio.gather(*start_tasks)
            logger.info("✅ All orchestrators started successfully")

        except Exception as error:
            logger.error(f"❌ Failed to start orchestrators: {error}")
            raise

    async def handle(self, request: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Universal request handler with intelligent routing
        Combines our AI routing with production monitoring
        """
        start_time = asyncio.get_event_loop().time()
        self.metrics["total_requests"] += 1

        try:
            # Determine which orchestrator to use
            orchestrator_name = self._determine_orchestrator(request)
            orchestrator = self.orchestrators[orchestrator_name]

            # Add production context
            enhanced_context = await self._enhance_context(context or {})

            # Process request
            result = await orchestrator.handle(request, enhanced_context)

            # Update metrics
            duration = asyncio.get_event_loop().time() - start_time
            self.metrics["successful_requests"] += 1
            self._update_response_time(duration)

            # Store in Redis if available
            await self._store_request_log(request, result, duration)

            return {
                "success": True,
                "result": result,
                "duration": duration,
                "processed_by": orchestrator_name,
                "timestamp": start_time
            }

        except Exception as error:
            duration = asyncio.get_event_loop().time() - start_time
            self.metrics["failed_requests"] += 1
            self._update_response_time(duration)

            logger.error(f"Request handling failed: {error}")
            raise

    def _determine_orchestrator(self, request: Dict[str, Any]) -> str:
        """Intelligent orchestrator selection"""
        request_type = request.get('type', '').lower()

        # Client-level requests
        if request_type in ['authenticate', 'authorize', 'security-check']:
            return 'client'

        # Sandbox requests
        if request_type in ['experiment', 'evolve', 'optimize']:
            return 'sandbox'

        # Program/business logic
        if request.get('domain') or request.get('module') or request_type == 'business-logic':
            return 'program'

        # Bridge translation
        if request.get('from_level') or request.get('to_level') or request_type == 'translate':
            return 'bridge'

        # Default to system
        return 'system'

    async def _enhance_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance context with production data"""
        enhanced = context.copy()

        # Add Redis session data if available
        if 'redis_client' in self.integrations and context.get('session_id'):
            try:
                session_data = await self.integrations['redis_client'].get(f"session:{context['session_id']}")
                if session_data:
                    enhanced['session_data'] = json.loads(session_data)
            except Exception:
                pass

        # Add user data from PostgreSQL if available
        if 'postgres_client' in self.integrations and context.get('user_id'):
            try:
                user_data = await self.integrations['postgres_client'].fetchrow(
                    "SELECT * FROM users WHERE id = $1", context['user_id']
                )
                if user_data:
                    enhanced['user_profile'] = dict(user_data)
            except Exception:
                pass

        return enhanced

    async def _store_request_log(self, request: Dict[str, Any], result: Dict[str, Any], duration: float):
        """Store request log in Redis"""
        if 'redis_client' not in self.integrations:
            return

        try:
            log_entry = {
                "request_type": request.get('type'),
                "orchestrator": result.get('processed_by'),
                "duration": duration,
                "success": result.get('success'),
                "timestamp": asyncio.get_event_loop().time()
            }

            await self.integrations['redis_client'].lpush("request_logs", json.dumps(log_entry))
            await self.integrations['redis_client'].ltrim("request_logs", 0, 999)  # Keep last 1000

        except Exception as error:
            logger.warning(f"Failed to store request log: {error}")

    def _update_response_time(self, duration: float):
        """Update average response time"""
        total_requests = self.metrics["total_requests"]
        current_avg = self.metrics["average_response_time"]
        self.metrics["average_response_time"] = ((current_avg * (total_requests - 1)) + duration) / total_requests

    # Convenience methods for specific operations

    async def execute_business_logic(self, domain: str, module: str, action: str, data: Dict[str, Any], context: Dict[str, Any] = None):
        """Execute business logic in specific domain"""
        request = {
            "type": "business-logic",
            "domain": domain,
            "module": module,
            "action": action,
            "data": data
        }
        return await self.handle(request, context)

    async def create_experiment(self, code: str, config: Dict[str, Any] = None):
        """Create and optionally run experiment"""
        request = {
            "type": "create-experiment",
            "code": code,
            **(config or {})
        }
        return await self.handle(request)

    async def evolve_component(self, component: str, parameters: Dict[str, Any] = None):
        """Evolve system component using AI"""
        request = {
            "type": "evolve-component",
            "component": component,
            **(parameters or {})
        }
        return await self.handle(request)

    async def authenticate_user(self, credentials: Dict[str, Any]):
        """Authenticate user"""
        request = {
            "type": "authenticate",
            "credentials": credentials
        }
        return await self.handle(request)

    # System management methods

    async def get_system_health(self) -> Dict[str, Any]:
        """Get comprehensive system health"""
        health_data = {}

        for name, orchestrator in self.orchestrators.items():
            health_data[name] = await orchestrator.get_health_status()

        return {
            "status": "healthy" if all(h.get("status") == "ready" for h in health_data.values()) else "degraded",
            "orchestrators": health_data,
            "metrics": self.metrics
        }

    def get_metrics(self) -> Dict[str, Any]:
        """Get system metrics"""
        return {
            **self.metrics,
            "orchestrators_running": sum(1 for o in self.orchestrators.values() if o.is_running),
            "total_orchestrators": len(self.orchestrators)
        }

    async def shutdown(self):
        """Shutdown all orchestrators"""
        logger.info("🛑 Shutting down Cognitive Orchestration Controller...")

        stop_tasks = []
        for orchestrator in self.orchestrators.values():
            stop_tasks.append(orchestrator.stop())

        await asyncio.gather(*stop_tasks, return_exceptions=True)
        logger.info("✅ All orchestrators stopped")


# For backwards compatibility and easy access
system_orchestrator = None
bridge_orchestrator = None
program_orchestrator = None
client_orchestrator = None
sandbox_orchestrator = None

def get_orchestrator(name: str) -> JavaScriptOrchestratorWrapper:
    """Get specific orchestrator by name"""
    global system_orchestrator, bridge_orchestrator, program_orchestrator, client_orchestrator, sandbox_orchestrator

    orchestrator_instances = {
        'system': system_orchestrator,
        'bridge': bridge_orchestrator,
        'program': program_orchestrator,
        'client': client_orchestrator,
        'sandbox': sandbox_orchestrator
    }

    return orchestrator_instances.get(name)