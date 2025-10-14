"""
MiО Manager - Web Dashboard
============================

Web UI for monitoring and managing MiО Manager operations.
Includes integration with monitoring tools and resource management.
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

logger = logging.getLogger(__name__)

ui_router = APIRouter(prefix="/ui", tags=["MiО UI"])


# ============================================================================
# MODELS
# ============================================================================

class ResourceAllocationRequest(BaseModel):
    """Request to allocate resources"""
    resource_type: str
    quantity: int
    priority: str = "normal"
    metadata: Optional[Dict[str, Any]] = {}


class MonitoringQuery(BaseModel):
    """Query for monitoring data"""
    service_name: Optional[str] = None
    metric_type: Optional[str] = None
    time_range: str = "1h"  # 1h, 24h, 7d, 30d


# ============================================================================
# UI ENDPOINTS (HTML)
# ============================================================================

@ui_router.get("/", response_class=HTMLResponse)
async def mio_dashboard():
    """
    MiО Manager Dashboard

    Web UI for monitoring and managing AI Office resources.
    Integrated with monitoring backend and analytics.

    Access: http://localhost:8046/ui/
    """

    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MiО Manager - Resource Coordination Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #2d3748 0%, #1a202c 100%);
            min-height: 100vh;
            padding: 20px;
            color: #e2e8f0;
        }

        .container {
            max-width: 1600px;
            margin: 0 auto;
        }

        .header {
            background: linear-gradient(135deg, #4299e1 0%, #3182ce 100%);
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }

        .header h1 {
            color: white;
            font-size: 32px;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 15px;
        }

        .header p {
            color: #e6fffa;
            font-size: 16px;
        }

        .status-badge {
            display: inline-block;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: 600;
            background: #48bb78;
            color: white;
        }

        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .card {
            background: #2d3748;
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
            border: 1px solid #4a5568;
        }

        .card h2 {
            color: #4299e1;
            font-size: 20px;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .metric {
            display: flex;
            justify-content: space-between;
            padding: 12px 0;
            border-bottom: 1px solid #4a5568;
        }

        .metric:last-child {
            border-bottom: none;
        }

        .metric-label {
            color: #a0aec0;
            font-size: 14px;
        }

        .metric-value {
            color: #e2e8f0;
            font-weight: 600;
            font-size: 16px;
        }

        .metric-value.good {
            color: #48bb78;
        }

        .metric-value.warning {
            color: #ed8936;
        }

        .metric-value.critical {
            color: #f56565;
        }

        .services-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
        }

        .service-card {
            background: #1a202c;
            border-radius: 8px;
            padding: 15px;
            border-left: 4px solid #4299e1;
        }

        .service-card.running {
            border-left-color: #48bb78;
        }

        .service-card.stopped {
            border-left-color: #f56565;
        }

        .service-name {
            font-weight: 600;
            color: #e2e8f0;
            margin-bottom: 8px;
        }

        .service-status {
            font-size: 12px;
            color: #a0aec0;
        }

        .service-status.running {
            color: #48bb78;
        }

        .service-status.stopped {
            color: #f56565;
        }

        .action-buttons {
            display: flex;
            gap: 10px;
            margin-top: 20px;
            flex-wrap: wrap;
        }

        .btn {
            padding: 10px 20px;
            border: none;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .btn-primary {
            background: #4299e1;
            color: white;
        }

        .btn-primary:hover {
            background: #3182ce;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(66, 153, 225, 0.4);
        }

        .btn-success {
            background: #48bb78;
            color: white;
        }

        .btn-success:hover {
            background: #38a169;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(72, 187, 120, 0.4);
        }

        .btn-danger {
            background: #f56565;
            color: white;
        }

        .btn-danger:hover {
            background: #e53e3e;
        }

        .monitoring-section {
            background: #2d3748;
            border-radius: 12px;
            padding: 25px;
            margin-top: 20px;
            border: 1px solid #4a5568;
        }

        .chart-placeholder {
            background: #1a202c;
            border-radius: 8px;
            height: 300px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #a0aec0;
            margin-top: 15px;
        }

        .footer {
            text-align: center;
            margin-top: 40px;
            color: #a0aec0;
            font-size: 14px;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }

        .loading {
            animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>
                🎯 MiО Manager
                <span class="status-badge" id="systemStatus">● OPERATIONAL</span>
            </h1>
            <p>AI Office Resource Coordination & Monitoring Dashboard</p>
        </div>

        <!-- Main Dashboard Grid -->
        <div class="dashboard-grid">
            <!-- System Health Card -->
            <div class="card">
                <h2>🏥 System Health</h2>
                <div class="metric">
                    <span class="metric-label">Overall Status</span>
                    <span class="metric-value good" id="overallStatus">Healthy</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Uptime</span>
                    <span class="metric-value" id="uptime">Loading...</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Active Services</span>
                    <span class="metric-value" id="activeServices">4 / 8</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Database</span>
                    <span class="metric-value good" id="dbStatus">Connected</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Redis/EventBus</span>
                    <span class="metric-value good" id="redisStatus">Connected</span>
                </div>
            </div>

            <!-- Resource Allocation Card -->
            <div class="card">
                <h2>📊 Resource Allocation</h2>
                <div class="metric">
                    <span class="metric-label">CPU Usage</span>
                    <span class="metric-value" id="cpuUsage">Loading...</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Memory Usage</span>
                    <span class="metric-value" id="memUsage">Loading...</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Active Workflows</span>
                    <span class="metric-value" id="activeWorkflows">0</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Pending Tasks</span>
                    <span class="metric-value" id="pendingTasks">0</span>
                </div>
            </div>

            <!-- AI Orchestration Card -->
            <div class="card">
                <h2>🤖 AI Orchestration</h2>
                <div class="metric">
                    <span class="metric-label">Decision Engine</span>
                    <span class="metric-value good">Operational</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Digital Twin</span>
                    <span class="metric-value good">Operational</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Knowledge System</span>
                    <span class="metric-value good">Operational</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Requests Today</span>
                    <span class="metric-value" id="requestsToday">0</span>
                </div>
            </div>
        </div>

        <!-- Services Status -->
        <div class="card">
            <h2>🔧 AI Office Services Status</h2>
            <div class="services-grid" id="servicesGrid">
                <div class="service-card loading">
                    <div class="service-name">Loading services...</div>
                    <div class="service-status">Please wait...</div>
                </div>
            </div>
            <div class="action-buttons">
                <button class="btn btn-primary" onclick="refreshServices()">🔄 Refresh Services</button>
                <button class="btn btn-success" onclick="startAllServices()">▶️ Start All</button>
                <button class="btn btn-danger" onclick="stopAllServices()">⏸️ Stop All</button>
            </div>
        </div>

        <!-- Monitoring Integration -->
        <div class="monitoring-section">
            <h2 style="color: #4299e1; margin-bottom: 15px;">📈 Monitoring Integration</h2>
            <div class="action-buttons">
                <button class="btn btn-primary" onclick="openPrometheus()">📊 Prometheus Metrics</button>
                <button class="btn btn-primary" onclick="openMonitoringBackend()">🖥️ Monitoring Backend</button>
                <button class="btn btn-primary" onclick="openAnalytics()">📊 Analytics Specialist</button>
                <button class="btn btn-primary" onclick="openDBIntel()">💾 DB Intelligence</button>
            </div>
            <div class="chart-placeholder">
                <div>Real-time metrics charts will appear here</div>
            </div>
        </div>

        <!-- Footer -->
        <div class="footer">
            MiО Manager v1.0.0 | AI Office Infrastructure | Last Update: <span id="lastUpdate">...</span>
        </div>
    </div>

    <script>
        // ========================================================================
        // CONFIGURATION
        // ========================================================================

        const API_BASE = 'http://localhost:8046';
        const MONITORING_BASE = 'http://localhost:8050';
        const PROMETHEUS_BASE = 'http://localhost:9090';
        const ANALYTICS_BASE = 'http://localhost:8056';
        const DB_INTEL_BASE = 'http://localhost:8051';

        // ========================================================================
        // DATA FETCHING
        // ========================================================================

        async function fetchHealth() {
            try {
                const response = await fetch(`${API_BASE}/health`);
                const data = await response.json();
                updateHealthMetrics(data);
            } catch (error) {
                console.error('Failed to fetch health:', error);
                document.getElementById('overallStatus').textContent = 'Error';
                document.getElementById('overallStatus').className = 'metric-value critical';
            }
        }

        async function fetchServices() {
            const services = [
                { name: 'orchestrator', port: 8045 },
                { name: 'mio-manager', port: 8046 },
                { name: 'agent-router', port: 8047 },
                { name: 'project-agent', port: 8048 },
                { name: 'devops-agent', port: 8049 },
                { name: 'ai-event-manager', port: 8050 },
                { name: 'db-intelligence', port: 8051 },
                { name: 'analytics-specialist', port: 8056 }
            ];

            const servicesGrid = document.getElementById('servicesGrid');
            servicesGrid.innerHTML = '';

            let activeCount = 0;

            for (const service of services) {
                const isRunning = await checkService(service.port);
                if (isRunning) activeCount++;

                const card = document.createElement('div');
                card.className = `service-card ${isRunning ? 'running' : 'stopped'}`;
                card.innerHTML = `
                    <div class="service-name">${service.name}</div>
                    <div class="service-status ${isRunning ? 'running' : 'stopped'}">
                        ${isRunning ? '● Running' : '○ Stopped'} | Port ${service.port}
                    </div>
                `;
                servicesGrid.appendChild(card);
            }

            document.getElementById('activeServices').textContent = `${activeCount} / ${services.length}`;
        }

        async function checkService(port) {
            try {
                const response = await fetch(`http://localhost:${port}/health`, {
                    method: 'GET',
                    timeout: 2000
                });
                return response.ok;
            } catch (error) {
                return false;
            }
        }

        function updateHealthMetrics(data) {
            if (data.status === 'healthy') {
                document.getElementById('overallStatus').textContent = 'Healthy';
                document.getElementById('overallStatus').className = 'metric-value good';
                document.getElementById('systemStatus').textContent = '● OPERATIONAL';
            }

            if (data.components) {
                document.getElementById('dbStatus').textContent =
                    data.components.database === 'connected' ? 'Connected' : 'Disconnected';
                document.getElementById('redisStatus').textContent =
                    data.components.redis === 'connected' ? 'Connected' : 'Disconnected';
            }
        }

        // ========================================================================
        // ACTIONS
        // ========================================================================

        function refreshServices() {
            fetchServices();
            fetchHealth();
            updateTimestamp();
        }

        function startAllServices() {
            alert('Starting all services... (This would trigger service startup)');
            // TODO: Implement actual service startup logic
        }

        function stopAllServices() {
            if (confirm('Are you sure you want to stop all services?')) {
                alert('Stopping all services... (This would trigger service shutdown)');
                // TODO: Implement actual service shutdown logic
            }
        }

        function openPrometheus() {
            window.open(PROMETHEUS_BASE, '_blank');
        }

        function openMonitoringBackend() {
            window.open(`${MONITORING_BASE}/health`, '_blank');
        }

        function openAnalytics() {
            window.open(`${ANALYTICS_BASE}/ui/`, '_blank');
        }

        function openDBIntel() {
            window.open(`${DB_INTEL_BASE}/docs`, '_blank');
        }

        function updateTimestamp() {
            const now = new Date();
            document.getElementById('lastUpdate').textContent = now.toLocaleString();
        }

        // ========================================================================
        // INITIALIZATION
        // ========================================================================

        // Load data on page load
        window.addEventListener('load', () => {
            fetchHealth();
            fetchServices();
            updateTimestamp();

            // Auto-refresh every 30 seconds
            setInterval(() => {
                fetchHealth();
                fetchServices();
                updateTimestamp();
            }, 30000);
        });
    </script>
</body>
</html>
    """

    return HTMLResponse(content=html_content)


@ui_router.get("/resources", response_class=HTMLResponse)
async def resources_page():
    """
    Resource Management Page

    Detailed view of resource allocation and management.
    """

    # TODO: Implement detailed resource management UI
    return HTMLResponse(content="<h1>Resource Management - Coming Soon</h1>")


@ui_router.get("/monitoring", response_class=HTMLResponse)
async def monitoring_page():
    """
    Monitoring Integration Page

    Detailed monitoring metrics and charts.
    """

    # TODO: Implement detailed monitoring UI with charts
    return HTMLResponse(content="<h1>Monitoring - Coming Soon</h1>")
