# -*- coding: utf-8 -*-
"""
Anthropic MCP SDK Compliant BCM Platform Tools
Following @anthropic/mcp standards for tool integration
"""

import asyncio
import httpx
import json
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

logger = logging.getLogger(__name__)

# MCP Tool Schema following Anthropic standards
class MCPToolSchema:
    """Anthropic MCP SDK compliant tool definitions"""

    @staticmethod
    def get_bcm_tools():
        """Get all BCM Platform MCP tools following Anthropic schema"""
        return [
            {
                "name": "generate_bcm_scenario",
                "description": "Generate AI-powered BCM exercise scenario for business continuity training and testing",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "category": {
                            "type": "string",
                            "enum": ["cyber", "epidemic", "blackout", "supply", "natural", "terrorism", "financial", "other"],
                            "description": "Type of business continuity scenario to generate"
                        },
                        "complexity": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 5,
                            "default": 3,
                            "description": "Scenario complexity level (1=basic, 5=expert)"
                        },
                        "participants": {
                            "type": "integer",
                            "minimum": 3,
                            "maximum": 100,
                            "default": 8,
                            "description": "Number of exercise participants"
                        },
                        "duration_hours": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 24,
                            "default": 4,
                            "description": "Expected exercise duration in hours"
                        },
                        "organization_context": {
                            "type": "string",
                            "description": "Organization type and context (e.g., 'Healthcare hospital', 'Financial services')"
                        },
                        "creativity_level": {
                            "type": "string",
                            "enum": ["standard", "creative", "innovative"],
                            "default": "standard",
                            "description": "AI creativity level for scenario generation"
                        }
                    },
                    "required": ["category"],
                    "additionalProperties": False
                }
            },

            {
                "name": "governance_brain_consultation",
                "description": "Consult the AI Governance Brain for strategic BCM decisions and compliance analysis using Anthropic Claude",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "governance_question": {
                            "type": "string",
                            "description": "Strategic governance question or compliance topic to analyze"
                        },
                        "domain": {
                            "type": "string",
                            "enum": ["iso_22301", "policy_management", "risk_governance", "performance_oversight", "strategic_planning", "board_reporting", "regulatory_compliance", "crisis_governance"],
                            "default": "iso_22301",
                            "description": "Governance domain for specialized analysis"
                        },
                        "priority": {
                            "type": "string",
                            "enum": ["low", "medium", "high", "critical", "strategic"],
                            "default": "medium",
                            "description": "Priority level affecting analysis depth and urgency"
                        },
                        "emergency": {
                            "type": "boolean",
                            "default": False,
                            "description": "Emergency governance session requiring immediate response"
                        },
                        "organization_name": {
                            "type": "string",
                            "description": "Organization name for context-specific analysis"
                        }
                    },
                    "required": ["governance_question"],
                    "additionalProperties": False
                }
            },

            {
                "name": "emergency_incident_response",
                "description": "Activate AI Emergency Response System for immediate incident management and crisis response",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "incident_title": {
                            "type": "string",
                            "description": "Clear, descriptive title of the incident"
                        },
                        "severity": {
                            "type": "string",
                            "enum": ["low", "medium", "high", "critical"],
                            "default": "medium",
                            "description": "Incident severity level"
                        },
                        "incident_type": {
                            "type": "string",
                            "enum": ["operational", "security", "natural", "technology", "human", "external"],
                            "default": "operational",
                            "description": "Type of incident for specialized response"
                        },
                        "description": {
                            "type": "string",
                            "description": "Detailed incident description and context"
                        },
                        "affected_systems": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of affected systems or processes"
                        },
                        "immediate_response_needed": {
                            "type": "boolean",
                            "default": True,
                            "description": "Whether immediate AI response analysis is required"
                        }
                    },
                    "required": ["incident_title"],
                    "additionalProperties": False
                }
            },

            {
                "name": "check_organism_health",
                "description": "Check the health status of the Digital BCM Organism and all AI organs",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "detailed": {
                            "type": "boolean",
                            "default": False,
                            "description": "Include detailed health metrics for each AI organ"
                        },
                        "organ_filter": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "enum": ["governance_brain", "emergency_response", "impact_oracle", "scenario_creator", "compliance_guardian", "performance_analyst", "learning_coach"]
                            },
                            "description": "Filter to specific AI organs (empty = all organs)"
                        },
                        "include_memory_stats": {
                            "type": "boolean",
                            "default": False,
                            "description": "Include memory usage and learning statistics"
                        }
                    },
                    "additionalProperties": False
                }
            },

            {
                "name": "bcm_analytics_query",
                "description": "Query BCM Platform analytics and performance data across all modules",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "analytics_type": {
                            "type": "string",
                            "enum": ["overview", "scenarios", "exercises", "incidents", "compliance", "performance", "ai_insights"],
                            "default": "overview",
                            "description": "Type of analytics to retrieve"
                        },
                        "timeframe": {
                            "type": "string",
                            "enum": ["7days", "30days", "90days", "1year", "all"],
                            "default": "30days",
                            "description": "Time frame for analytics data"
                        },
                        "module_focus": {
                            "type": "string",
                            "enum": ["all", "governance", "incidents", "exercises", "scenarios", "compliance", "training"],
                            "default": "all",
                            "description": "Focus on specific module analytics"
                        },
                        "include_predictions": {
                            "type": "boolean",
                            "default": False,
                            "description": "Include AI-powered predictions and forecasting"
                        }
                    },
                    "additionalProperties": False
                }
            },

            {
                "name": "start_exercise_session",
                "description": "Start a BCM exercise session with workflow automation and participant coordination",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "exercise_name": {
                            "type": "string",
                            "description": "Name of the exercise session"
                        },
                        "exercise_type": {
                            "type": "string",
                            "enum": ["tabletop", "functional", "full_scale", "simulation"],
                            "default": "tabletop",
                            "description": "Type of BCM exercise to conduct"
                        },
                        "scenario_id": {
                            "type": "string",
                            "description": "Optional scenario ID to base exercise on"
                        },
                        "participants": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of participant email addresses"
                        },
                        "auto_notifications": {
                            "type": "boolean",
                            "default": True,
                            "description": "Automatically notify participants via Slack/Teams"
                        },
                        "workflow_automation": {
                            "type": "boolean",
                            "default": True,
                            "description": "Enable BPMN workflow automation for exercise"
                        }
                    },
                    "required": ["exercise_name"],
                    "additionalProperties": False
                }
            },

            {
                "name": "pdca_cycle_orchestration",
                "description": "Orchestrate Plan-Do-Check-Act cycle using appropriate AI organs for each phase",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "pdca_phase": {
                            "type": "string",
                            "enum": ["plan", "do", "check", "act"],
                            "description": "PDCA cycle phase to execute"
                        },
                        "topic": {
                            "type": "string",
                            "description": "Topic or process for PDCA cycle"
                        },
                        "context": {
                            "type": "object",
                            "description": "Additional context for PDCA phase execution"
                        },
                        "ai_orchestration": {
                            "type": "boolean",
                            "default": True,
                            "description": "Use AI organs for enhanced PDCA execution"
                        }
                    },
                    "required": ["pdca_phase", "topic"],
                    "additionalProperties": False
                }
            }
        ]

class MCPToolResponse:
    """Anthropic MCP compliant response format"""

    @staticmethod
    def success_response(text: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Create successful MCP response"""
        return {
            "content": [
                {
                    "type": "text",
                    "text": text
                }
            ],
            "isError": False,
            "_meta": {
                "timestamp": datetime.now().isoformat(),
                "platform": "bcm_digital_organism",
                "data": data
            }
        }

    @staticmethod
    def error_response(error: str) -> Dict[str, Any]:
        """Create error MCP response"""
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"❌ Error: {error}"
                }
            ],
            "isError": True,
            "_meta": {
                "timestamp": datetime.now().isoformat(),
                "platform": "bcm_digital_organism"
            }
        }

    @staticmethod
    def organism_response(organ_name: str, result: Dict[str, Any]) -> Dict[str, Any]:
        """Create AI organ specific response"""
        success = result.get('success', False)
        message = result.get('message', '')

        return {
            "content": [
                {
                    "type": "text",
                    "text": f"{'✅' if success else '❌'} {organ_name}: {message}"
                }
            ],
            "isError": not success,
            "_meta": {
                "timestamp": datetime.now().isoformat(),
                "platform": "bcm_digital_organism",
                "ai_organ": organ_name,
                "organism_data": result
            }
        }

# Global tool schema for MCP server integration
BCM_MCP_TOOLS = MCPToolSchema.get_bcm_tools()