# MCP Server Update Guide - Anthropic SDK Compliance

## 🎯 **MCP SERVER ENHANCEMENT ПЛАН:**

### **CURRENT STATUS:**
- ✅ Basic MCP Server running на :8087
- ✅ BCM tools enhanced created
- ✅ Anthropic SDK compliance schemas ready

### **UPDATE REQUIREMENTS:**

#### **1. Update main.py с новыми tools:**
```python
# ADD to /integrations/mcp-server/main.py:

from .mcp_tools_anthropic_compliant import BCM_MCP_TOOLS, MCPToolResponse
from .bcm_tools_enhanced import bcm_chat_tools

# Register BCM Platform tools
@app.post("/mcp/tools/list")
async def list_bcm_tools():
    """List available BCM Platform tools"""
    return {
        "tools": BCM_MCP_TOOLS
    }

@app.post("/mcp/tools/call")
async def call_bcm_tool(tool_name: str, parameters: Dict[str, Any]):
    """Call BCM Platform tool following MCP standards"""

    try:
        if tool_name == "generate_bcm_scenario":
            result = await bcm_chat_tools.generate_scenario(**parameters)
            return MCPToolResponse.organism_response("Scenario Creator", result)

        elif tool_name == "governance_brain_consultation":
            result = await bcm_chat_tools.governance_consultation(**parameters)
            return MCPToolResponse.organism_response("Governance Brain", result)

        elif tool_name == "emergency_incident_response":
            result = await bcm_chat_tools.emergency_incident_response(**parameters)
            return MCPToolResponse.organism_response("Emergency Response", result)

        elif tool_name == "check_organism_health":
            result = await bcm_chat_tools.check_organism_health()
            return MCPToolResponse.organism_response("Lifecycle Monitor", result)

        elif tool_name == "bcm_analytics_query":
            result = await bcm_chat_tools.get_bcm_analytics(**parameters)
            return MCPToolResponse.organism_response("Performance Analyst", result)

        elif tool_name == "start_exercise_session":
            result = await bcm_chat_tools.start_exercise_session(**parameters)
            return MCPToolResponse.organism_response("Exercise Coordinator", result)

        elif tool_name == "pdca_cycle_orchestration":
            result = await bcm_chat_tools.pdca_orchestration(**parameters)
            return MCPToolResponse.organism_response("PDCA Orchestrator", result)

        else:
            return MCPToolResponse.error_response(f"Unknown tool: {tool_name}")

    except Exception as e:
        logger.error(f"MCP tool call failed: {e}")
        return MCPToolResponse.error_response(str(e))
```

#### **2. Update server.yaml config:**
```yaml
# /integrations/mcp-server/server.yaml
mcpServers:
  bcm-platform:
    command: "python"
    args: ["main.py"]
    env:
      BCM_PLATFORM_URL: "http://localhost:8069"
      AI_ORCHESTRATOR_URL: "http://localhost:8000"
      SCENARIO_ORCHESTRATOR_URL: "http://localhost:8085"
    capabilities:
      tools:
        - generate_bcm_scenario
        - governance_brain_consultation
        - emergency_incident_response
        - check_organism_health
        - bcm_analytics_query
        - start_exercise_session
        - pdca_cycle_orchestration
```

#### **3. Update requirements.txt:**
```txt
# ADD to requirements.txt:
mcp>=0.1.0                    # Anthropic MCP SDK
anthropic>=0.18.0            # Anthropic API client
httpx>=0.24.0                # Async HTTP client
pydantic>=2.5.0              # Data validation
```

---

## 💬 **CHAT USAGE EXAMPLES:**

### **Scenario Generation:**
```
User: "Create a cyber security scenario for a hospital with 15 participants"

Claude calls: generate_bcm_scenario
Parameters: {
  "category": "cyber",
  "participants": 15,
  "organization_context": "Hospital healthcare environment"
}

Response: ✅ Scenario Creator: Scenario 'Hospital Ransomware Crisis' generated successfully!
Platform URL: http://localhost:8069/scenarios/ai_20250915_123456
```

### **Governance Consultation:**
```
User: "What's our ISO 22301 compliance status and what improvements do we need?"

Claude calls: governance_brain_consultation
Parameters: {
  "governance_question": "ISO 22301 compliance status assessment and improvement recommendations",
  "domain": "iso_22301",
  "priority": "high"
}

Response: 🧠 Governance Brain: Current compliance 87%. Strategic analysis:
- Strong BIA and planning processes
- Minor gaps in testing documentation
- Recommendations: Enhanced exercise program, automated compliance monitoring
```

### **Emergency Response:**
```
User: "EMERGENCY: Our main data center is on fire and all systems are down!"

Claude calls: emergency_incident_response
Parameters: {
  "incident_title": "Data center fire - complete system outage",
  "severity": "critical",
  "incident_type": "natural",
  "description": "Physical fire in primary data center causing complete IT outage",
  "immediate_response_needed": True
}

Response: 🚨 Emergency Response: CRITICAL incident protocols activated!
AI Analysis: Immediate actions - activate backup site, implement emergency communications, notify crisis team
Platform URL: http://localhost:8069/incidents/INC_20250915_123456
```

---

## 🔧 **IMPLEMENTATION STEPS:**

### **1. Update MCP Server Files:**
```bash
# Files to update:
/integrations/mcp-server/main.py              # ADD tool endpoints
/integrations/mcp-server/server.yaml          # UPDATE configuration
/integrations/mcp-server/requirements.txt     # ADD dependencies
```

### **2. Test MCP Integration:**
```bash
# Test MCP server after update:
curl http://localhost:8087/mcp/tools/list
curl -X POST http://localhost:8087/mcp/tools/call \
  -d '{"tool_name": "check_organism_health", "parameters": {}}'
```

### **3. Claude Integration Test:**
```
# In Claude chat with MCP enabled:
User: "Check health of our BCM organism"
Expected: AI organs health report с detailed metrics
```

---

## 📋 **FILES TO CREATE/UPDATE:**

### **✅ CREATED:**
- `/integrations/mcp-server/bcm_tools_enhanced.py` ✅
- `/integrations/mcp-server/mcp_tools_anthropic_compliant.py` ✅

### **📝 NEED TO UPDATE:**
- `/integrations/mcp-server/main.py` - ADD tool endpoints
- `/integrations/mcp-server/server.yaml` - UPDATE config
- `/integrations/mcp-server/requirements.txt` - ADD dependencies

**Хочешь чтобы я обновил main.py и config files сейчас?** 🔧

**Или сначала проверим через inspector что нужно для Anthropic SDK compliance?** 🔍