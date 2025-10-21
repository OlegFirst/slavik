"""
Tools UI Routes
===============

Web UI for managing and running analysis tools.
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from config import settings
from core import AnalyticsCore

logger = logging.getLogger(__name__)

ui_router = APIRouter(prefix="/ui", tags=["Tools UI"])


# ============================================================================
# MODELS
# ============================================================================

class ToolExecutionRequest(BaseModel):
    """Request to execute a tool"""
    tool_name: str
    parameters: Optional[Dict[str, Any]] = {}
    async_execution: bool = False


class ToolScheduleRequest(BaseModel):
    """Request to schedule a tool"""
    tool_name: str
    schedule: str  # cron expression
    parameters: Optional[Dict[str, Any]] = {}
    enabled: bool = True


# ============================================================================
# UI ENDPOINTS (HTML)
# ============================================================================

@ui_router.get("/", response_class=HTMLResponse)
async def tools_dashboard():
    """
    Tools Management Dashboard

    Web UI for viewing and running all analysis tools.

    Access: http://localhost:8051/ui/
    """

    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Analytics Specialist - Tools Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
        }

        .header {
            background: white;
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }

        .header h1 {
            color: #333;
            font-size: 32px;
            margin-bottom: 10px;
        }

        .header p {
            color: #666;
            font-size: 16px;
        }

        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .stat-card {
            background: white;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }

        .stat-card h3 {
            color: #666;
            font-size: 14px;
            text-transform: uppercase;
            margin-bottom: 10px;
        }

        .stat-card .value {
            color: #667eea;
            font-size: 36px;
            font-weight: bold;
        }

        .tools-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 20px;
        }

        .tool-card {
            background: white;
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            transition: transform 0.2s, box-shadow 0.2s;
        }

        .tool-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        }

        .tool-card.junior {
            border-left: 4px solid #48bb78;
        }

        .tool-card.middle {
            border-left: 4px solid #ed8936;
        }

        .tool-card.senior {
            border-left: 4px solid #e53e3e;
        }

        .tool-header {
            display: flex;
            justify-content: space-between;
            align-items: start;
            margin-bottom: 15px;
        }

        .tool-name {
            font-size: 20px;
            font-weight: 600;
            color: #333;
        }

        .tool-badge {
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
        }

        .tool-badge.junior {
            background: #c6f6d5;
            color: #22543d;
        }

        .tool-badge.middle {
            background: #feebc8;
            color: #7c2d12;
        }

        .tool-badge.senior {
            background: #fed7d7;
            color: #742a2a;
        }

        .tool-description {
            color: #666;
            font-size: 14px;
            margin-bottom: 15px;
            line-height: 1.6;
        }

        .tool-status {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 15px;
            padding: 10px;
            background: #f7fafc;
            border-radius: 8px;
        }

        .status-indicator {
            width: 10px;
            height: 10px;
            border-radius: 50%;
        }

        .status-indicator.available {
            background: #48bb78;
        }

        .status-indicator.unavailable {
            background: #e53e3e;
        }

        .tool-actions {
            display: flex;
            gap: 10px;
        }

        .btn {
            flex: 1;
            padding: 12px 20px;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
        }

        .btn:hover {
            transform: translateY(-2px);
        }

        .btn-primary {
            background: #667eea;
            color: white;
        }

        .btn-primary:hover {
            background: #5a67d8;
        }

        .btn-secondary {
            background: #e2e8f0;
            color: #4a5568;
        }

        .btn-secondary:hover {
            background: #cbd5e0;
        }

        .btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }

        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            z-index: 1000;
            align-items: center;
            justify-content: center;
        }

        .modal.active {
            display: flex;
        }

        .modal-content {
            background: white;
            border-radius: 12px;
            padding: 30px;
            max-width: 600px;
            width: 90%;
            max-height: 80vh;
            overflow-y: auto;
        }

        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }

        .modal-title {
            font-size: 24px;
            font-weight: 600;
            color: #333;
        }

        .close-btn {
            background: none;
            border: none;
            font-size: 24px;
            cursor: pointer;
            color: #999;
        }

        .loading {
            text-align: center;
            padding: 40px;
        }

        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .result-section {
            background: #f7fafc;
            border-radius: 8px;
            padding: 20px;
            margin-top: 20px;
        }

        .result-section h3 {
            margin-bottom: 10px;
            color: #333;
        }

        pre {
            background: #2d3748;
            color: #e2e8f0;
            padding: 15px;
            border-radius: 8px;
            overflow-x: auto;
            font-size: 13px;
        }

        .schedule-form {
            display: flex;
            flex-direction: column;
            gap: 15px;
        }

        .form-group {
            display: flex;
            flex-direction: column;
            gap: 5px;
        }

        .form-group label {
            font-weight: 600;
            color: #4a5568;
        }

        .form-group input,
        .form-group select {
            padding: 10px;
            border: 1px solid #cbd5e0;
            border-radius: 6px;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1> Analytics Specialist - Tools Dashboard</h1>
            <p>Manage and execute analysis tools for AI Platform ISO</p>
        </div>

        <div class="stats" id="stats">
            <div class="stat-card">
                <h3>Total Tools</h3>
                <div class="value" id="total-tools">-</div>
            </div>
            <div class="stat-card">
                <h3>Available</h3>
                <div class="value" id="available-tools">-</div>
            </div>
            <div class="stat-card">
                <h3>Competency Level</h3>
                <div class="value" id="competency-level">-</div>
            </div>
            <div class="stat-card">
                <h3>Last Analysis</h3>
                <div class="value" id="last-analysis">Never</div>
            </div>
        </div>

        <div class="tools-grid" id="tools-grid">
            <!-- Tools will be loaded here -->
        </div>
    </div>

    <!-- Execution Modal -->
    <div class="modal" id="execution-modal">
        <div class="modal-content">
            <div class="modal-header">
                <div class="modal-title" id="modal-title">Running Tool...</div>
                <button class="close-btn" onclick="closeModal()">&times;</button>
            </div>
            <div id="modal-body">
                <div class="loading">
                    <div class="spinner"></div>
                    <p>Executing tool, please wait...</p>
                </div>
            </div>
        </div>
    </div>

    <!-- Schedule Modal -->
    <div class="modal" id="schedule-modal">
        <div class="modal-content">
            <div class="modal-header">
                <div class="modal-title">Schedule Tool</div>
                <button class="close-btn" onclick="closeScheduleModal()">&times;</button>
            </div>
            <div class="schedule-form">
                <div class="form-group">
                    <label>Tool</label>
                    <input type="text" id="schedule-tool-name" readonly>
                </div>
                <div class="form-group">
                    <label>Schedule (Cron)</label>
                    <select id="schedule-cron">
                        <option value="0 2 * * *">Daily at 02:00 UTC</option>
                        <option value="0 */6 * * *">Every 6 hours</option>
                        <option value="0 9 * * 1">Weekly on Monday at 09:00 UTC</option>
                        <option value="0 0 1 * *">Monthly on 1st at 00:00 UTC</option>
                        <option value="custom">Custom...</option>
                    </select>
                </div>
                <div class="form-group" id="custom-cron-group" style="display: none;">
                    <label>Custom Cron Expression</label>
                    <input type="text" id="custom-cron" placeholder="0 2 * * *">
                </div>
                <div class="tool-actions">
                    <button class="btn btn-secondary" onclick="closeScheduleModal()">Cancel</button>
                    <button class="btn btn-primary" onclick="saveSchedule()">Save Schedule</button>
                </div>
            </div>
        </div>
    </div>

    <script>
        let toolsData = {};

        // Load tools on page load
        window.addEventListener('DOMContentLoaded', loadTools);

        async function loadTools() {
            try {
                const response = await fetch('/api/v1/analytics/status');
                const data = await response.json();

                toolsData = data.tools || {};

                // Update stats
                document.getElementById('total-tools').textContent = Object.keys(toolsData).length;
                document.getElementById('available-tools').textContent =
                    Object.values(toolsData).filter(t => t.available).length;
                document.getElementById('competency-level').textContent =
                    data.competency_level || 'Unknown';

                // Render tools
                renderTools();
            } catch (error) {
                console.error('Failed to load tools:', error);
                document.getElementById('tools-grid').innerHTML =
                    '<p style="color: white;">Failed to load tools. Is the service running?</p>';
            }
        }

        function renderTools() {
            const grid = document.getElementById('tools-grid');
            grid.innerHTML = '';

            const toolDescriptions = {
                'metrics_discovery': 'Discovers and analyzes metrics from all services',
                'module_scanner': 'Scans and catalogs all Python modules',
                'ast_analyzer': 'Analyzes Python code structure using AST',
                'dependency_mapper': 'Maps dependencies between services',
                'api_mapper': 'Maps all API endpoints across services',
                'dependency_validator': 'Validates dependencies and checks for issues',
                'security_scanner': 'Scans code for security vulnerabilities'
            };

            for (const [name, tool] of Object.entries(toolsData)) {
                const card = document.createElement('div');
                card.className = `tool-card ${tool.competency_required}`;

                card.innerHTML = `
                    <div class="tool-header">
                        <div class="tool-name">${name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</div>
                        <div class="tool-badge ${tool.competency_required}">${tool.competency_required}</div>
                    </div>
                    <div class="tool-description">${toolDescriptions[name] || tool.description}</div>
                    <div class="tool-status">
                        <div class="status-indicator ${tool.available ? 'available' : 'unavailable'}"></div>
                        <span>${tool.available ? 'Available' : 'Unavailable'}</span>
                    </div>
                    <div class="tool-actions">
                        <button class="btn btn-primary" onclick="runTool('${name}')" ${!tool.available ? 'disabled' : ''}>
                            Run Now
                        </button>
                        <button class="btn btn-secondary" onclick="scheduleTool('${name}')" ${!tool.available ? 'disabled' : ''}>
                            Schedule
                        </button>
                    </div>
                `;

                grid.appendChild(card);
            }
        }

        async function runTool(toolName) {
            const modal = document.getElementById('execution-modal');
            const title = document.getElementById('modal-title');
            const body = document.getElementById('modal-body');

            title.textContent = `Running ${toolName}...`;
            body.innerHTML = `
                <div class="loading">
                    <div class="spinner"></div>
                    <p>Executing tool, please wait...</p>
                </div>
            `;
            modal.classList.add('active');

            try {
                const endpoint = getToolEndpoint(toolName);
                const response = await fetch(endpoint, { method: 'POST' });
                const result = await response.json();

                title.textContent = `${toolName} - Results`;
                body.innerHTML = `
                    <div class="result-section">
                        <h3>Execution Complete </h3>
                        <pre>${JSON.stringify(result, null, 2)}</pre>
                    </div>
                `;
            } catch (error) {
                title.textContent = `${toolName} - Error`;
                body.innerHTML = `
                    <div class="result-section">
                        <h3>Execution Failed </h3>
                        <pre>${error.message}</pre>
                    </div>
                `;
            }
        }

        function getToolEndpoint(toolName) {
            const endpoints = {
                'ast_analyzer': '/api/v1/analytics/tools/ast-analysis',
                'api_mapper': '/api/v1/analytics/tools/api-map',
                'dependency_validator': '/api/v1/analytics/tools/dependency-validation',
                'security_scanner': '/api/v1/analytics/tools/security-scan',
                'module_scanner': '/api/v1/analytics/tools/module-scan',
                'dependency_mapper': '/api/v1/analytics/tools/dependency-map',
                'metrics_discovery': '/api/v1/analytics/tools/metrics-discovery'
            };
            return endpoints[toolName] || `/api/v1/analytics/tools/${toolName}`;
        }

        function scheduleTool(toolName) {
            document.getElementById('schedule-tool-name').value = toolName;
            document.getElementById('schedule-modal').classList.add('active');
        }

        function closeModal() {
            document.getElementById('execution-modal').classList.remove('active');
        }

        function closeScheduleModal() {
            document.getElementById('schedule-modal').classList.remove('active');
        }

        document.getElementById('schedule-cron').addEventListener('change', (e) => {
            const customGroup = document.getElementById('custom-cron-group');
            customGroup.style.display = e.target.value === 'custom' ? 'block' : 'none';
        });

        async function saveSchedule() {
            const toolName = document.getElementById('schedule-tool-name').value;
            const cronSelect = document.getElementById('schedule-cron');
            let cron = cronSelect.value;

            if (cron === 'custom') {
                cron = document.getElementById('custom-cron').value;
            }

            alert(`Schedule saved for ${toolName}: ${cron}\n\nNote: This is a demo. Actual scheduling requires backend implementation.`);
            closeScheduleModal();
        }
    </script>
</body>
</html>
    """

    return HTMLResponse(content=html_content)


@ui_router.get("/tools/{tool_name}", response_class=HTMLResponse)
async def tool_detail(tool_name: str):
    """
    Detailed view for a specific tool

    Shows execution history, parameters, scheduling options.
    """
    # TODO: Implement detailed tool view
    return HTMLResponse(content=f"<h1>Tool: {tool_name}</h1><p>Detail view coming soon...</p>")


# ============================================================================
# API ENDPOINTS for UI
# ============================================================================

@ui_router.post("/api/execute")
async def execute_tool_from_ui(
    request: ToolExecutionRequest,
    background_tasks: BackgroundTasks
) -> Dict[str, Any]:
    """
    Execute a tool from the UI

    Supports both sync and async execution.
    """
    try:
        core = AnalyticsCore()
        await core.initialize()

        if request.tool_name not in core.tools:
            raise HTTPException(
                status_code=404,
                detail=f"Tool '{request.tool_name}' not found or not available"
            )

        tool = core.tools[request.tool_name]

        if request.async_execution:
            # Execute in background
            background_tasks.add_task(
                execute_tool_async,
                tool,
                request.parameters
            )

            return {
                "status": "started",
                "message": f"Tool '{request.tool_name}' execution started in background",
                "execution_id": f"{request.tool_name}_{int(datetime.now().timestamp())}"
            }
        else:
            # Execute synchronously
            # TODO: Add proper method dispatch based on tool type
            result = await tool.analyze_project(**request.parameters)

            return {
                "status": "completed",
                "tool": request.tool_name,
                "result": result,
                "executed_at": datetime.now().isoformat()
            }

    except Exception as e:
        logger.error(f"Tool execution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@ui_router.post("/api/schedule")
async def schedule_tool_from_ui(request: ToolScheduleRequest) -> Dict[str, Any]:
    """
    Schedule a tool execution

    Creates a scheduled job for the tool.
    """
    # TODO: Implement actual scheduling with APScheduler or similar
    return {
        "status": "scheduled",
        "tool": request.tool_name,
        "schedule": request.schedule,
        "message": "Tool scheduled successfully (demo mode)"
    }


@ui_router.get("/api/executions")
async def get_execution_history(
    tool_name: Optional[str] = None,
    limit: int = 50
) -> Dict[str, Any]:
    """
    Get execution history for tools

    Optionally filter by tool_name.
    """
    # TODO: Implement execution history tracking
    return {
        "executions": [],
        "total": 0,
        "message": "Execution history not yet implemented"
    }


async def execute_tool_async(tool: Any, parameters: Dict[str, Any]):
    """Execute tool in background"""
    try:
        # TODO: Add proper method dispatch
        result = await tool.analyze_project(**parameters)
        logger.info(f"Background tool execution completed: {result}")
    except Exception as e:
        logger.error(f"Background tool execution failed: {e}")
