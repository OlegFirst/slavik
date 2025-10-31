# -*- coding: utf-8 -*-

from odoo import models, api, _
from odoo.exceptions import UserError
import requests
import json
import logging
import os
from datetime import datetime

_logger = logging.getLogger(__name__)

class BCMAIOrgansAPIIntegration(models.AbstractModel):
    """Real AI Organs with external API integrations"""
    _name = 'bcm.ai.organs.api.integration'
    _description = 'AI Organs External API Integration Layer'

    # AI Service Configuration
    @api.model
    def _get_ai_config(self):
        """Get AI service configuration from environment or system parameters"""
        params = self.env['ir.config_parameter'].sudo()

        return {
            'openai_api_key': os.environ.get('OPENAI_API_KEY') or params.get_param('ai.openai_api_key', ''),
            'anthropic_api_key': os.environ.get('ANTHROPIC_API_KEY') or params.get_param('ai.anthropic_api_key', ''),
            'ai_model': params.get_param('ai.default_model', 'gpt-4'),
            'timeout': int(params.get_param('ai.request_timeout', '30')),
            'max_retries': int(params.get_param('ai.max_retries', '3')),
            'use_mock_data': params.get_param('ai.use_mock_data', 'True').lower() == 'true'
        }

    @api.model
    def _make_ai_request(self, organ_name, prompt, twin_data, context=None):
        """Make request to AI service with proper error handling"""
        config = self._get_ai_config()

        # Use mock data if configured or no API key
        if config['use_mock_data'] or not config.get('openai_api_key'):
            _logger.info(f"Using mock data for AI organ: {organ_name}")
            return self._get_mock_response(organ_name, twin_data)

        try:
            # Prepare API request
            headers = {
                'Authorization': f"Bearer {config['openai_api_key']}",
                'Content-Type': 'application/json'
            }

            # Enhanced prompt with BCM context
            enhanced_prompt = self._enhance_prompt_with_context(prompt, twin_data, context)

            payload = {
                'model': config['ai_model'],
                'messages': [
                    {'role': 'system', 'content': f'You are the {organ_name} AI organ of a Business Continuity Management system. Provide structured, actionable insights based on the organization data.'},
                    {'role': 'user', 'content': enhanced_prompt}
                ],
                'max_tokens': 1000,
                'temperature': 0.7
            }

            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers=headers,
                json=payload,
                timeout=config['timeout']
            )

            response.raise_for_status()
            result = response.json()

            # Process and structure the response
            ai_content = result['choices'][0]['message']['content']
            return self._parse_ai_response(organ_name, ai_content)

        except Exception as e:
            _logger.error(f"AI API request failed for {organ_name}: {str(e)}")
            # Fallback to mock data on error
            return self._get_mock_response(organ_name, twin_data)

    @api.model
    def _enhance_prompt_with_context(self, base_prompt, twin_data, context=None):
        """Enhance prompt with organization and BCM context"""
        org_data = twin_data.get('organization', {})

        context_info = f"""
Organization Context:
- Name: {org_data.get('name', 'Unknown')}
- Domain: {org_data.get('domain_type', 'Unknown')}
- Industry: {org_data.get('industry_sector', 'Unknown')}
- BCM Maturity: {twin_data.get('bcm_maturity', 'Unknown')}

Current Status:
- Health Score: {twin_data.get('health_score', 'Unknown')}
- Last Analysis: {twin_data.get('last_analysis', 'Never')}
- Active Incidents: {len(twin_data.get('incidents', []))}

Business Context:
{json.dumps(twin_data.get('bcm_context', {}), indent=2)}

Analysis Request:
{base_prompt}

Please provide specific, actionable insights structured as JSON with the following format:
{{
    "insights": ["insight1", "insight2", "insight3"],
    "metrics": {{"key": "value"}},
    "recommendations": ["rec1", "rec2"],
    "confidence": 0.85,
    "priority": "high|medium|low"
}}
"""
        return context_info

    @api.model
    def _parse_ai_response(self, organ_name, ai_content):
        """Parse AI response and structure it"""
        try:
            # Try to extract JSON from response
            if '{' in ai_content and '}' in ai_content:
                json_start = ai_content.find('{')
                json_end = ai_content.rfind('}') + 1
                json_str = ai_content[json_start:json_end]
                parsed = json.loads(json_str)

                return {
                    'organ': organ_name,
                    'insights': parsed.get('insights', []),
                    'metrics': parsed.get('metrics', {}),
                    'recommendations': parsed.get('recommendations', []),
                    'confidence': float(parsed.get('confidence', 0.7)) * 100,
                    'priority': parsed.get('priority', 'medium'),
                    'timestamp': datetime.now().isoformat(),
                    'source': 'ai_api'
                }
            else:
                # Fallback - treat as plain text insights
                insights = [line.strip() for line in ai_content.split('\n') if line.strip()]
                return {
                    'organ': organ_name,
                    'insights': insights[:5],  # Limit to 5 insights
                    'confidence': 70.0,
                    'timestamp': datetime.now().isoformat(),
                    'source': 'ai_api_text'
                }

        except Exception as e:
            _logger.error(f"Failed to parse AI response for {organ_name}: {str(e)}")
            return self._get_mock_response(organ_name, {})

    @api.model
    def _get_mock_response(self, organ_name, twin_data):
        """Get mock response for testing when AI API is not available"""
        mock_responses = {
            'governance_brain': {
                'insights': [
                    'Strategic governance framework needs alignment with ISO 22301',
                    'Board oversight of BCM processes requires enhancement',
                    'Policy documentation completeness at 75%',
                    'Stakeholder engagement process optimization recommended'
                ],
                'metrics': {
                    'governance_score': 78.5,
                    'policy_coverage': 75.0,
                    'stakeholder_satisfaction': 82.0
                },
                'recommendations': [
                    'Implement quarterly BCM board reporting',
                    'Update governance policies to reflect current operations',
                    'Establish clear escalation procedures'
                ],
                'confidence': 82.0,
                'priority': 'high'
            },
            'risk_advisor': {
                'insights': [
                    'Critical operational risks identified in supply chain',
                    'Cybersecurity posture assessment reveals vulnerabilities',
                    'Financial risk exposure within acceptable parameters',
                    'Regulatory compliance risks require attention'
                ],
                'metrics': {
                    'overall_risk_score': 45.2,
                    'operational_risk': 38.5,
                    'financial_risk': 22.1,
                    'compliance_risk': 51.8
                },
                'recommendations': [
                    'Implement additional supply chain monitoring',
                    'Enhance cybersecurity training program',
                    'Review regulatory compliance procedures'
                ],
                'confidence': 88.5,
                'priority': 'high'
            },
            'impact_oracle': {
                'insights': [
                    'Market disruption probability increasing over next 6 months',
                    'Technology obsolescence risk moderate for current systems',
                    'Resource availability constraints forecasted',
                    'Positive impact from automation initiatives expected'
                ],
                'predictions': [
                    {
                        'scenario': 'Supply chain disruption',
                        'probability': 0.35,
                        'impact_level': 'medium',
                        'timeframe': '3-6 months'
                    },
                    {
                        'scenario': 'Technology upgrade benefits',
                        'probability': 0.78,
                        'impact_level': 'high',
                        'timeframe': '1-2 months'
                    }
                ],
                'confidence': 76.3,
                'priority': 'medium'
            },
            'compliance_guardian': {
                'insights': [
                    'ISO 22301 compliance level at 85%',
                    'Gap analysis reveals documentation shortcomings',
                    'Training compliance above industry standards',
                    'Audit preparation timeline requires acceleration'
                ],
                'metrics': {
                    'iso_22301_compliance': 85.0,
                    'documentation_completeness': 78.5,
                    'training_compliance': 92.3,
                    'audit_readiness': 71.2
                },
                'confidence': 91.0,
                'priority': 'high'
            }
        }

        base_response = mock_responses.get(organ_name, {
            'insights': [f'Mock insight from {organ_name}'],
            'confidence': 65.0,
            'priority': 'medium'
        })

        base_response.update({
            'organ': organ_name,
            'timestamp': datetime.now().isoformat(),
            'source': 'mock_data'
        })

        return base_response

    # Real AI Organ Implementations
    @api.model
    def governance_brain_analysis(self, twin_data):
        """Enhanced Governance Brain with real AI"""
        prompt = """
        Analyze the governance framework of this organization. Consider:
        - Strategic alignment with business continuity objectives
        - Board and executive oversight effectiveness
        - Policy framework completeness and currency
        - Stakeholder engagement processes
        - Decision-making structures

        Provide governance score (0-100) and specific improvement recommendations.
        """

        return self._make_ai_request('governance_brain', prompt, twin_data)

    @api.model
    def risk_advisor_analysis(self, twin_data):
        """Enhanced Risk Advisor with FAIR methodology"""
        prompt = """
        Conduct comprehensive risk analysis using FAIR (Factor Analysis of Information Risk) methodology:
        - Identify threat landscape and vulnerability assessment
        - Calculate loss event frequency and magnitude
        - Provide Monte Carlo risk simulation insights
        - Assess risk appetite vs current exposure
        - Recommend risk treatment strategies

        Include quantitative risk metrics and priority matrix.
        """

        return self._make_ai_request('risk_advisor', prompt, twin_data)

    @api.model
    def impact_oracle_predictions(self, twin_data):
        """Enhanced Impact Oracle with predictive analytics"""
        prompt = """
        Generate predictive insights and scenario forecasting:
        - Analyze trend patterns in organizational data
        - Predict potential disruption scenarios and probabilities
        - Assess impact magnitudes for different time horizons
        - Identify early warning indicators
        - Recommend proactive measures

        Provide probability-weighted impact assessments with confidence intervals.
        """

        return self._make_ai_request('impact_oracle', prompt, twin_data)

    @api.model
    def compliance_guardian_check(self, twin_data):
        """Enhanced Compliance Guardian with regulatory intelligence"""
        prompt = """
        Assess regulatory compliance status and requirements:
        - Evaluate ISO 22301 compliance level and gaps
        - Monitor regulatory changes affecting the organization
        - Assess documentation completeness and quality
        - Review training and awareness program effectiveness
        - Identify upcoming compliance deadlines

        Provide compliance score and remediation roadmap.
        """

        return self._make_ai_request('compliance_guardian', prompt, twin_data)