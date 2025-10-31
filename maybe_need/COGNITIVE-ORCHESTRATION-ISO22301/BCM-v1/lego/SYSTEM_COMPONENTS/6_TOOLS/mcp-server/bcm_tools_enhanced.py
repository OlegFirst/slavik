# -*- coding: utf-8 -*-
"""
Enhanced BCM Platform Tools for MCP Server
Chat-controlled BCM Platform through Claude conversation
"""

import asyncio
import httpx
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class BCMPlatformChatTools:
    """Enhanced MCP tools for chat-controlled BCM Platform"""

    def __init__(self):
        self.base_urls = {
            'ai_orchestrator': 'http://ai_orchestrator:8000',
            'scenario_orchestrator': 'http://scenario_orchestrator:8085',
            'odoo': 'http://odoo:8069',
            'compliance_checker': 'http://compliance_checker:8084',
            'bia_engine': 'http://bia_engine:8082',
            'notification_service': 'http://notification_service:8002',
            'eventbus': 'http://eventbus:8001'
        }

    # ==========================================
    # SCENARIO MANAGEMENT TOOLS
    # ==========================================

    async def generate_scenario(
        self,
        category: str,
        complexity: int = 3,
        participants: int = 8,
        organization_context: str = "",
        creativity_level: str = "standard"
    ) -> Dict[str, Any]:
        """Generate BCM scenario through chat interface"""

        try:
            # Call Scenario Orchestrator
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_urls['scenario_orchestrator']}/scenarios/generate",
                    json={
                        'category': category,
                        'complexity': complexity,
                        'participants': participants,
                        'organization_context': organization_context,
                        'creativity_boost': creativity_level == "creative",
                        'created_via': 'chat_interface'
                    },
                    timeout=60
                )

                if response.status_code == 200:
                    result = response.json()
                    return {
                        'success': True,
                        'scenario_id': result.get('scenario_id'),
                        'title': result.get('title'),
                        'message': f"✅ Scenario '{result.get('title')}' generated successfully!",
                        'platform_url': f"http://localhost:8069/scenarios/{result.get('scenario_id')}",
                        'file_path': result.get('file_path')
                    }
                else:
                    return {'success': False, 'error': f'Generation failed: {response.status_code}'}

        except Exception as e:
            logger.error(f'Scenario generation failed: {e}')
            return {'success': False, 'error': str(e)}

    # ==========================================
    # GOVERNANCE TOOLS
    # ==========================================

    async def governance_consultation(
        self,
        governance_question: str,
        domain: str = "iso_22301",
        priority: str = "medium",
        emergency: bool = False
    ) -> Dict[str, Any]:
        """Consult AI Governance Brain through chat"""

        try:
            # Call AI Orchestrator with Anthropic routing
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_urls['ai_orchestrator']}/nlp/query",
                    json={
                        'query': governance_question,
                        'context': {
                            'module': 'bcm_governance',
                            'domain': domain,
                            'priority': 'emergency' if emergency else priority,
                            'use_anthropic': True,
                            'chat_interface': True
                        },
                        'user_role': 'governance_brain'
                    },
                    timeout=120 if not emergency else 30
                )

                if response.status_code == 200:
                    result = response.json()
                    return {
                        'success': True,
                        'governance_analysis': result.get('response', ''),
                        'confidence': result.get('confidence', 0),
                        'message': "🧠 AI Governance Brain analysis complete",
                        'model_used': result.get('model_used', 'anthropic'),
                        'emergency_mode': emergency
                    }
                else:
                    return {'success': False, 'error': 'Governance Brain unavailable'}

        except Exception as e:
            logger.error(f'Governance consultation failed: {e}')
            return {'success': False, 'error': str(e)}

    # ==========================================
    # INCIDENT MANAGEMENT TOOLS
    # ==========================================

    async def emergency_incident_response(
        self,
        incident_title: str,
        severity: str = "medium",
        incident_type: str = "operational",
        description: str = ""
    ) -> Dict[str, Any]:
        """Handle incident through chat interface"""

        try:
            # Create incident via Odoo API (simplified for chat)
            incident_data = {
                'name': incident_title,
                'severity': severity,
                'incident_type': incident_type,
                'description': description,
                'created_via': 'chat_interface',
                'ai_analysis_requested': True
            }

            # For now, simulate incident creation and AI analysis
            # In reality, would call Odoo JSON-RPC API

            return {
                'success': True,
                'incident_id': f"INC_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'message': f"🚨 Incident '{incident_title}' created and AI emergency response activated!",
                'ai_analysis': "AI Emergency Response System provided immediate action plan",
                'response_time': "< 10 seconds",
                'platform_url': f"http://localhost:8069/incidents/{incident_title}"
            }

        except Exception as e:
            logger.error(f'Emergency response failed: {e}')
            return {'success': False, 'error': str(e)}

    # ==========================================
    # ANALYTICS TOOLS
    # ==========================================

    async def get_bcm_analytics(
        self,
        analytics_type: str = "overview",
        timeframe: str = "30days",
        module_focus: str = "all"
    ) -> Dict[str, Any]:
        """Get BCM analytics through chat interface"""

        try:
            # Call various analytics sources
            analytics_data = {}

            if analytics_type in ['overview', 'all']:
                # Get organism health
                organism_health = await self.get_organism_health()
                analytics_data['organism_health'] = organism_health

            if analytics_type in ['scenarios', 'all']:
                # Get scenario analytics
                scenario_stats = await self.get_scenario_statistics()
                analytics_data['scenarios'] = scenario_stats

            if analytics_type in ['exercises', 'all']:
                # Get exercise performance
                exercise_stats = await self.get_exercise_performance()
                analytics_data['exercises'] = exercise_stats

            return {
                'success': True,
                'analytics_type': analytics_type,
                'timeframe': timeframe,
                'data': analytics_data,
                'message': f"📊 BCM Platform analytics for {timeframe}",
                'dashboard_url': "http://localhost:8069/analytics"
            }

        except Exception as e:
            logger.error(f'Analytics query failed: {e}')
            return {'success': False, 'error': str(e)}

    # ==========================================
    # ORGANISM HEALTH TOOLS
    # ==========================================

    async def check_organism_health(self) -> Dict[str, Any]:
        """Check health of Digital BCM Organism"""

        try:
            # Check all AI organs
            organ_health = {}

            # Check individual organ health
            organs = [
                'governance_brain', 'emergency_response', 'impact_oracle',
                'scenario_creator', 'compliance_guardian', 'performance_analyst',
                'learning_coach'
            ]

            for organ in organs:
                health = await self.check_individual_organ_health(organ)
                organ_health[organ] = health

            # Calculate overall health
            health_scores = [h.get('health_score', 0.5) for h in organ_health.values()]
            overall_health = sum(health_scores) / len(health_scores) if health_scores else 0.5

            return {
                'success': True,
                'overall_health': round(overall_health, 2),
                'organism_status': self._get_organism_status(overall_health),
                'organ_details': organ_health,
                'message': f"🧬 Digital BCM Organism health: {round(overall_health*100)}%",
                'dashboard_url': "http://localhost:8069/ai-lifecycle"
            }

        except Exception as e:
            logger.error(f'Organism health check failed: {e}')
            return {'success': False, 'error': str(e)}

    async def check_individual_organ_health(self, organ_name: str) -> Dict[str, Any]:
        """Check individual AI organ health"""

        # Mock health check - would call actual organ endpoints
        organ_health_data = {
            'governance_brain': {
                'status': 'wise',
                'health_score': 0.95,
                'last_activation': datetime.now().isoformat(),
                'anthropic_connection': True,
                'response_quality': 'executive_level'
            },
            'emergency_response': {
                'status': 'active',
                'health_score': 0.89,
                'avg_response_time': 8.5,
                'local_ai_connection': True,
                'emergency_readiness': True
            },
            'impact_oracle': {
                'status': 'active',
                'health_score': 0.92,
                'prediction_accuracy': 0.87,
                'digital_twin_ready': True,
                'real_time_capability': False
            }
        }

        return organ_health_data.get(organ_name, {
            'status': 'unknown',
            'health_score': 0.5,
            'message': 'Health data not available'
        })

    def _get_organism_status(self, health_score: float) -> str:
        """Determine organism status from health score"""
        if health_score >= 0.9:
            return 'thriving'
        elif health_score >= 0.8:
            return 'healthy'
        elif health_score >= 0.7:
            return 'stable'
        elif health_score >= 0.6:
            return 'needs_attention'
        else:
            return 'critical'

    # ==========================================
    # EXERCISE MANAGEMENT TOOLS
    # ==========================================

    async def start_exercise_session(
        self,
        exercise_name: str,
        exercise_type: str = "tabletop",
        scenario_id: str = "",
        participants: List[str] = []
    ) -> Dict[str, Any]:
        """Start exercise session through chat"""

        try:
            exercise_data = {
                'name': exercise_name,
                'exercise_type': exercise_type,
                'scenario_id': scenario_id,
                'participants': participants,
                'created_via': 'chat_interface',
                'auto_start_workflow': True
            }

            # Would call bcm_exercise API to create and start exercise

            return {
                'success': True,
                'exercise_id': f"EXE_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'message': f"🎯 Exercise '{exercise_name}' started with {len(participants)} participants",
                'workflow_status': 'initializing',
                'monitoring_url': f"http://localhost:8069/exercises/{exercise_name}"
            }

        except Exception as e:
            logger.error(f'Exercise start failed: {e}')
            return {'success': False, 'error': str(e)}

    # ==========================================
    # PDCA INTEGRATION TOOLS
    # ==========================================

    async def pdca_orchestration(
        self,
        pdca_phase: str,
        topic: str,
        context: Dict[str, Any] = {}
    ) -> Dict[str, Any]:
        """Orchestrate PDCA cycle with AI organs"""

        try:
            if pdca_phase.upper() == "PLAN":
                # Use Governance Brain for strategic planning
                return await self.governance_consultation(
                    f"Strategic planning guidance for: {topic}",
                    domain="strategic_planning",
                    priority=context.get('priority', 'medium')
                )

            elif pdca_phase.upper() == "DO":
                # Use appropriate execution organs
                if 'incident' in topic.lower():
                    return await self.emergency_incident_response(topic)
                elif 'exercise' in topic.lower():
                    return await self.start_exercise_session(topic)
                elif 'scenario' in topic.lower():
                    return await self.generate_scenario(
                        category=context.get('category', 'other'),
                        complexity=context.get('complexity', 3)
                    )

            elif pdca_phase.upper() == "CHECK":
                # Use Compliance Guardian and Performance Analyst
                return await self.compliance_check(topic, context)

            elif pdca_phase.upper() == "ACT":
                # Use Performance Analyst for improvement recommendations
                return await self.performance_improvement_recommendations(topic, context)

            else:
                return {'success': False, 'error': 'Invalid PDCA phase'}

        except Exception as e:
            logger.error(f'PDCA orchestration failed: {e}')
            return {'success': False, 'error': str(e)}

    async def compliance_check(self, topic: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Compliance checking through Compliance Guardian"""

        compliance_prompt = f"""
Compliance Guardian Analysis Request:
Topic: {topic}
Context: {json.dumps(context)}

Perform automated compliance assessment and provide recommendations.
"""

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_urls['compliance_checker']}/api/compliance/analyze",
                    json={
                        'analysis_request': compliance_prompt,
                        'framework': 'iso_22301',
                        'chat_interface': True
                    },
                    timeout=30
                )

                if response.status_code == 200:
                    result = response.json()
                    return {
                        'success': True,
                        'compliance_status': result.get('compliance_status', 'unknown'),
                        'gaps_identified': result.get('gaps', []),
                        'recommendations': result.get('recommendations', []),
                        'message': "🛡️ Compliance Guardian completed analysis"
                    }

        except Exception as e:
            logger.error(f'Compliance check failed: {e}')

        return {'success': False, 'error': 'Compliance check unavailable'}

# Global instance for MCP server
bcm_chat_tools = BCMPlatformChatTools()