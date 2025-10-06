"""
Muscles - Execution Layer of Super-Orchestrator

Components:
- Multi-LLM Router - Route requests to optimal AI provider
- Model Selector - Select best model for task complexity
- Agent Router - Route to specialized AI agents
- AI Organs - 10 specialized AI components
- LLM Clients - Claude, GPT-4, Gemini, Local models
"""

from .agent_router import AIAgentRouter, AgentCapability, AgentRole
from .model_selector import BCMModelRouter, TaskComplexity

__all__ = [
    'AIAgentRouter',
    'AgentCapability',
    'AgentRole',
    'BCMModelRouter',
    'TaskComplexity',
]
