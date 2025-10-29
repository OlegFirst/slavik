"""
BCM Platform MCP Server
Model Context Protocol server for Docker AI integration
Provides BCM-specific tools and APIs for AI agents
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx
import redis.asyncio as redis
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="BCM Platform MCP Server - Enhanced",
    description="Anthropic MCP SDK compliant server for Digital BCM Organism",
    version="2.0.0"
)

# Import BCM Platform AI tools
try:
    from bcm_tools_enhanced import bcm_chat_tools
    from mcp_tools_anthropic_compliant import BCM_MCP_TOOLS, MCPToolResponse
except ImportError:
    logger.warning("BCM tools not found, running with basic functionality")
    bcm_chat_tools = []
    BCM_MCP_TOOLS = []
    MCPToolResponse = None

# Environment configuration
ODOO_URL = os.getenv("ODOO_URL", "http://localhost:8069")
KEYCLOAK_URL = os.getenv("KEYCLOAK_URL", "http://localhost:8080")
POSTGRES_URL = os.getenv("POSTGRES_URL", "postgresql://odoo:postgres123@localhost:5432/bcm_platform")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# MCP Models
class MCPRequest(BaseModel):
    tool: str
    parameters: Dict[str, Any]
    context: Optional[Dict[str, Any]] = None

class MCPResponse(BaseModel):
    success: bool
    data: Any
    error: Optional[str] = None
    timestamp: str = None

    def __init__(self, **data):
        if 'timestamp' not in data:
            data['timestamp'] = datetime.now().isoformat()
        super().__init__(**data)

class BCMTool:
    """Base class for BCM tools"""

    def __init__(self):
        self.redis_client = None
        self.postgres_conn = None
        self.http_client = httpx.AsyncClient()

    async def init_connections(self):
        """Initialize database connections"""
        try:
            self.redis_client = redis.from_url(REDIS_URL)
            self.postgres_conn = psycopg2.connect(POSTGRES_URL, cursor_factory=RealDictCursor)
        except Exception as e:
            logger.error(f"Connection initialization failed: {e}")

    async def close_connections(self):
        """Close database connections"""
        if self.redis_client:
            await self.redis_client.close()
        if self.postgres_conn:
            self.postgres_conn.close()
        await self.http_client.aclose()

class BCMProcessTool(BCMTool):
    """BCM Process Management Tool"""

    async def list_processes(self, tenant_id: str) -> Dict:
        """List all business processes"""
        try:
            cursor = self.postgres_conn.cursor()
            cursor.execute("""
                SELECT id, name, description, criticality, rto_hours, rpo_hours
                FROM bcm_business_process
                WHERE tenant_id = %s
                ORDER BY criticality DESC
            """, (tenant_id,))

            processes = cursor.fetchall()
            return {
                "processes": [dict(row) for row in processes],
                "count": len(processes)
            }
        except Exception as e:
            logger.error(f"Process list error: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    async def analyze_process(self, process_id: int, analysis_type: str) -> Dict:
        """Analyze business process for BIA/Risk/Dependencies"""
        try:
            if analysis_type == "bia":
                return await self._perform_bia_analysis(process_id)
            elif analysis_type == "risk":
                return await self._perform_risk_analysis(process_id)
            elif analysis_type == "dependencies":
                return await self._analyze_dependencies(process_id)
            else:
                raise ValueError(f"Unknown analysis type: {analysis_type}")
        except Exception as e:
            logger.error(f"Process analysis error: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    async def _perform_bia_analysis(self, process_id: int) -> Dict:
        """Perform Business Impact Analysis"""
        cursor = self.postgres_conn.cursor()
        cursor.execute("""
            SELECT name, criticality, rto_hours, rpo_hours, description
            FROM bcm_business_process
            WHERE id = %s
        """, (process_id,))

        process = cursor.fetchone()
        if not process:
            raise HTTPException(status_code=404, detail="Process not found")

        # Calculate impact scores
        impact_score = process['criticality'] * 20  # 1-5 scale to percentage
        financial_impact = "High" if process['criticality'] >= 4 else "Medium" if process['criticality'] >= 3 else "Low"

        return {
            "process_name": process['name'],
            "impact_analysis": {
                "overall_impact_score": impact_score,
                "financial_impact": financial_impact,
                "operational_impact": "Critical" if process['criticality'] >= 4 else "Medium",
                "rto_target": f"{process['rto_hours']} hours",
                "rpo_target": f"{process['rpo_hours']} hours"
            },
            "recommendations": self._generate_bia_recommendations(process)
        }

    async def _perform_risk_analysis(self, process_id: int) -> Dict:
        """Perform Risk Analysis"""
        # Simulate risk analysis
        return {
            "risk_assessment": {
                "operational_risk": "Medium",
                "technology_risk": "High",
                "human_risk": "Low",
                "external_risk": "Medium"
            },
            "mitigation_strategies": [
                "Implement backup systems",
                "Cross-train personnel",
                "Regular risk assessments"
            ]
        }

    async def _analyze_dependencies(self, process_id: int) -> Dict:
        """Analyze process dependencies"""
        return {
            "upstream_dependencies": ["Process A", "Process B"],
            "downstream_dependencies": ["Process X", "Process Y"],
            "critical_resources": ["Database", "Network", "Key personnel"]
        }

    def _generate_bia_recommendations(self, process: Dict) -> List[str]:
        """Generate BIA recommendations"""
        recommendations = []
        if process['rto_hours'] > 4:
            recommendations.append("Consider implementing hot standby systems to reduce RTO")
        if process['rpo_hours'] > 1:
            recommendations.append("Implement more frequent data backups to reduce RPO")
        if process['criticality'] >= 4:
            recommendations.append("Develop detailed incident response procedures")
        return recommendations

class BCMIncidentTool(BCMTool):
    """BCM Incident Management Tool"""

    async def create_incident(self, title: str, description: str, severity: str, category: str) -> Dict:
        """Create new incident record"""
        try:
            cursor = self.postgres_conn.cursor()
            cursor.execute("""
                INSERT INTO bcm_incident (title, description, severity, category, status, created_at)
                VALUES (%s, %s, %s, %s, 'open', NOW())
                RETURNING id
            """, (title, description, severity, category))

            incident_id = cursor.fetchone()['id']
            self.postgres_conn.commit()

            # Trigger notifications via Redis
            await self.redis_client.publish("bcm_incidents", json.dumps({
                "event": "incident_created",
                "incident_id": incident_id,
                "severity": severity,
                "category": category
            }))

            return {
                "incident_id": incident_id,
                "status": "created",
                "next_actions": self._suggest_incident_actions(severity, category)
            }
        except Exception as e:
            logger.error(f"Incident creation error: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    async def classify_incident(self, incident_description: str) -> Dict:
        """AI-powered incident classification"""
        # Simple keyword-based classification (in production, use proper ML)
        keywords = {
            "security": ["hack", "breach", "malware", "phishing", "unauthorized"],
            "technology": ["server", "network", "database", "application", "system"],
            "operational": ["process", "procedure", "workflow", "business"],
            "natural": ["flood", "fire", "earthquake", "storm", "natural"]
        }

        description_lower = incident_description.lower()
        category_scores = {}

        for category, words in keywords.items():
            score = sum(1 for word in words if word in description_lower)
            category_scores[category] = score

        predicted_category = max(category_scores, key=category_scores.get)

        # Simple severity assessment
        critical_words = ["critical", "urgent", "emergency", "down", "failure"]
        severity = "critical" if any(word in description_lower for word in critical_words) else "medium"

        return {
            "predicted_category": predicted_category,
            "predicted_severity": severity,
            "confidence": max(category_scores.values()) / len(keywords[predicted_category]),
            "analysis": category_scores
        }

    def _suggest_incident_actions(self, severity: str, category: str) -> List[str]:
        """Suggest incident response actions"""
        actions = ["Log incident details", "Assess impact"]

        if severity in ["high", "critical"]:
            actions.extend(["Notify stakeholders", "Activate response team"])

        if category == "security":
            actions.extend(["Isolate affected systems", "Contact security team"])
        elif category == "technology":
            actions.extend(["Check system status", "Contact IT support"])

        return actions

# Initialize tools
process_tool = BCMProcessTool()
incident_tool = BCMIncidentTool()

# MCP Endpoints
@app.post("/mcp/tools", response_model=MCPResponse)
async def execute_tool(request: MCPRequest):
    """Execute BCM MCP tool"""
    try:
        await process_tool.init_connections()
        await incident_tool.init_connections()

        result = None

        # Process Management Tools
        if request.tool == "bcm_process_list":
            result = await process_tool.list_processes(request.parameters["tenant_id"])
        elif request.tool == "bcm_process_analyze":
            result = await process_tool.analyze_process(
                request.parameters["process_id"],
                request.parameters["analysis_type"]
            )

        # Incident Management Tools
        elif request.tool == "bcm_incident_create":
            result = await incident_tool.create_incident(
                request.parameters["title"],
                request.parameters["description"],
                request.parameters["severity"],
                request.parameters["category"]
            )
        elif request.tool == "bcm_incident_classify":
            result = await incident_tool.classify_incident(
                request.parameters["incident_description"]
            )

        else:
            raise HTTPException(status_code=400, detail=f"Unknown tool: {request.tool}")

        return MCPResponse(success=True, data=result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Tool execution error: {e}")
        return MCPResponse(success=False, data=None, error=str(e))
    finally:
        await process_tool.close_connections()
        await incident_tool.close_connections()

@app.get("/mcp/tools/list")
async def list_available_tools():
    """List all available BCM MCP tools"""
    return {
        "tools": [
            {
                "name": "bcm_process_list",
                "description": "List all business processes with criticality ratings",
                "category": "process-management"
            },
            {
                "name": "bcm_process_analyze",
                "description": "Analyze business process for BIA/Risk/Dependencies",
                "category": "process-management"
            },
            {
                "name": "bcm_incident_create",
                "description": "Create new incident record in BCM system",
                "category": "incident-management"
            },
            {
                "name": "bcm_incident_classify",
                "description": "AI-powered incident classification",
                "category": "incident-management"
            }
        ]
    }

@app.get("/health")
async def health_check():
    """Health check for MCP server"""
    return {
        "status": "healthy",
        "service": "bcm-mcp-server",
        "version": "1.0.0",
        "tools_available": 4,
        "timestamp": datetime.now().isoformat()
    }

# ==========================================
# ANTHROPIC MCP SDK COMPLIANT ENDPOINTS
# ==========================================

@app.get("/mcp/tools")
async def list_mcp_tools():
    """List available MCP tools following Anthropic standards"""
    return {
        "tools": BCM_MCP_TOOLS,
        "server": {
            "name": "bcm-platform-organism",
            "version": "2.0.0",
            "description": "Digital BCM Organism MCP Server with 8 AI organs",
            "capabilities": ["tools", "chat", "organism_control"]
        }
    }

@app.post("/mcp/tools/call")
async def call_mcp_tool(tool_request: MCPRequest):
    """Execute MCP tool following Anthropic SDK standards"""

    tool_name = tool_request.tool
    parameters = tool_request.parameters
    context = tool_request.context or {}

    try:
        logger.info(f"MCP tool call: {tool_name}")

        # Route to appropriate AI organ
        if tool_name == "generate_bcm_scenario":
            result = await bcm_chat_tools.generate_scenario(**parameters)
            return MCPToolResponse.organism_response("🎭 Scenario Creator", result)

        elif tool_name == "governance_brain_consultation":
            result = await bcm_chat_tools.governance_consultation(**parameters)
            return MCPToolResponse.organism_response("🧠 Governance Brain", result)

        elif tool_name == "emergency_incident_response":
            result = await bcm_chat_tools.emergency_incident_response(**parameters)
            return MCPToolResponse.organism_response("🚨 Emergency Response", result)

        elif tool_name == "check_organism_health":
            result = await bcm_chat_tools.check_organism_health()
            return MCPToolResponse.organism_response("🧬 Digital Organism", result)

        elif tool_name == "bcm_analytics_query":
            result = await bcm_chat_tools.get_bcm_analytics(**parameters)
            return MCPToolResponse.organism_response("📊 Performance Analyst", result)

        elif tool_name == "start_exercise_session":
            result = await bcm_chat_tools.start_exercise_session(**parameters)
            return MCPToolResponse.organism_response("🎯 Exercise Coordinator", result)

        elif tool_name == "pdca_cycle_orchestration":
            result = await bcm_chat_tools.pdca_orchestration(**parameters)
            return MCPToolResponse.organism_response("🔄 PDCA Orchestrator", result)

        else:
            return MCPToolResponse.error_response(f"Unknown tool: {tool_name}")

    except Exception as e:
        logger.error(f"MCP tool execution failed: {e}")
        return MCPToolResponse.error_response(str(e))

@app.post("/chat/organism")
async def chat_with_digital_organism(chat_request: Dict[str, Any]):
    """Direct chat interface with Digital BCM Organism"""

    user_message = chat_request.get('message', '')
    context = chat_request.get('context', {})

    try:
        # Intelligent routing based on message content
        if any(word in user_message.lower() for word in ['governance', 'policy', 'compliance', 'board', 'strategic']):
            result = await bcm_chat_tools.governance_consultation(
                governance_question=user_message,
                priority=context.get('priority', 'medium')
            )
            organ_used = "🧠 Governance Brain"

        elif any(word in user_message.lower() for word in ['emergency', 'incident', 'crisis', 'urgent', 'help']):
            result = await bcm_chat_tools.emergency_incident_response(
                incident_title=user_message,
                severity=context.get('severity', 'high')
            )
            organ_used = "🚨 Emergency Response"

        elif any(word in user_message.lower() for word in ['scenario', 'create', 'generate', 'exercise']):
            result = await bcm_chat_tools.generate_scenario(
                category=context.get('category', 'other'),
                complexity=context.get('complexity', 3)
            )
            organ_used = "🎭 Scenario Creator"

        elif any(word in user_message.lower() for word in ['health', 'status', 'organism', 'monitor']):
            result = await bcm_chat_tools.check_organism_health()
            organ_used = "🧬 Lifecycle Monitor"

        elif any(word in user_message.lower() for word in ['analytics', 'performance', 'metrics', 'kpi']):
            result = await bcm_chat_tools.get_bcm_analytics()
            organ_used = "📊 Performance Analyst"

        else:
            # Route to AI Orchestrator for general queries
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    'http://ai_orchestrator:8000/nlp/query',
                    json={
                        'query': user_message,
                        'context': context,
                        'user_role': 'organism_chat_user'
                    }
                )
                if response.status_code == 200:
                    ai_result = response.json()
                    result = {
                        'success': True,
                        'message': ai_result.get('response', ''),
                        'intent': ai_result.get('intent', 'general_query')
                    }
                else:
                    result = {'success': False, 'error': 'AI Orchestrator unavailable'}

            organ_used = "🤖 AI Orchestrator"

        return {
            "success": result.get('success', False),
            "organism_response": result.get('message', ''),
            "organ_used": organ_used,
            "confidence": result.get('confidence', 0.0),
            "platform_url": result.get('platform_url', ''),
            "timestamp": datetime.now().isoformat(),
            "chat_interface": "digital_bcm_organism_v2"
        }

    except Exception as e:
        logger.error(f"Organism chat failed: {e}")
        return {
            "success": False,
            "organism_response": f"❌ Digital organism error: {str(e)}",
            "organ_used": "❌ Error Handler",
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)