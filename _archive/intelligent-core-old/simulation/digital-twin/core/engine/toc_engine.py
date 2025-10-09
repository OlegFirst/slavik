"""
Theory of Change (ToC) Engine for Digital Twin Universal Service

Generates and validates Theory of Change models for organizations:
- Input → Activities → Outputs → Outcomes → Impact chains
- Logic model validation
- Indicator mapping
- Pathway analysis
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import uuid4

from core.models.base import (
    Organization,
    TheoryOfChange,
)

logger = logging.getLogger(__name__)


# ============================================
# THEORY OF CHANGE ENGINE
# ============================================

class ToCEngine:
    """
    Theory of Change Engine

    Generates and validates Theory of Change models for organizations
    """

    def __init__(self):
        logger.info("Theory of Change Engine initialized")

    async def generate_toc(
        self,
        organization: Organization,
        focus_area: Optional[str] = None
    ) -> TheoryOfChange:
        """
        Generate Theory of Change for organization

        Args:
            organization: Organization digital twin
            focus_area: Optional focus area (e.g., 'financial_resilience', 'impact')

        Returns:
            TheoryOfChange model
        """
        logger.info(f"Generating Theory of Change for {organization.name}")

        # Determine focus based on org type
        if not focus_area:
            focus_area = self._determine_focus_area(organization)

        # Generate components
        inputs = self._generate_inputs(organization, focus_area)
        activities = self._generate_activities(organization, focus_area, inputs)
        outputs = self._generate_outputs(organization, focus_area, activities)
        outcomes = self._generate_outcomes(organization, focus_area, outputs)
        impact = self._generate_impact(organization, focus_area, outcomes)

        # Generate supporting elements
        assumptions = self._generate_assumptions(organization, focus_area)
        indicators = self._generate_indicators(organization, focus_area)
        pathways = self._generate_pathways(
            organization,
            inputs,
            activities,
            outputs,
            outcomes,
            impact
        )

        toc = TheoryOfChange(
            twin_id=organization.twin_id,
            inputs=inputs,
            activities=activities,
            outputs=outputs,
            outcomes=outcomes,
            impact=impact,
            assumptions=assumptions,
            indicators=indicators,
            pathways=pathways
        )

        logger.info(
            f"ToC generated: {len(inputs)} inputs → {len(activities)} activities → "
            f"{len(outputs)} outputs → {len(outcomes)} outcomes → impact"
        )

        return toc

    def _determine_focus_area(self, organization: Organization) -> str:
        """Determine primary focus area based on organization type"""
        focus_map = {
            'corporate': 'business_continuity',
            'government': 'service_delivery',
            'npo': 'social_impact',
            'infrastructure': 'operational_resilience'
        }

        return focus_map.get(organization.org_type.value, 'organizational_resilience')

    def _generate_inputs(
        self,
        organization: Organization,
        focus_area: str
    ) -> List[Dict[str, Any]]:
        """Generate inputs for ToC"""
        inputs = []

        # Financial resources
        if organization.annual_budget or organization.annual_revenue:
            budget = organization.annual_budget or organization.annual_revenue
            inputs.append({
                'id': str(uuid4()),
                'type': 'financial',
                'category': 'resources',
                'name': 'Financial Resources',
                'description': f'Annual budget: ${budget:,.0f}',
                'value': budget,
                'unit': 'USD',
                'criticality': 'high'
            })

        # Human resources
        if organization.employee_count:
            inputs.append({
                'id': str(uuid4()),
                'type': 'human',
                'category': 'resources',
                'name': 'Staff',
                'description': f'{organization.employee_count} employees',
                'value': organization.employee_count,
                'unit': 'people',
                'criticality': 'high'
            })

        # Data/Information resources
        if len(organization.sources) > 0:
            inputs.append({
                'id': str(uuid4()),
                'type': 'information',
                'category': 'resources',
                'name': 'Data Systems',
                'description': f'{len(organization.sources)} integrated data sources',
                'value': len(organization.sources),
                'unit': 'systems',
                'criticality': 'medium'
            })

        # Infrastructure
        if len(organization.locations) > 0:
            inputs.append({
                'id': str(uuid4()),
                'type': 'infrastructure',
                'category': 'resources',
                'name': 'Physical Infrastructure',
                'description': f'{len(organization.locations)} locations',
                'value': len(organization.locations),
                'unit': 'locations',
                'criticality': 'medium'
            })

        # BCM Inputs (if available)
        if organization.bcm_data:
            inputs.append({
                'id': str(uuid4()),
                'type': 'knowledge',
                'category': 'resources',
                'name': 'BCM Framework',
                'description': 'Business Continuity Management framework and processes',
                'value': True,
                'criticality': 'high'
            })

        # Maturity as input
        inputs.append({
            'id': str(uuid4()),
            'type': 'capability',
            'category': 'resources',
            'name': 'Organizational Maturity',
            'description': f'Maturity level {organization.maturity_level}/5',
            'value': organization.maturity_level,
            'unit': 'level',
            'criticality': 'medium'
        })

        return inputs

    def _generate_activities(
        self,
        organization: Organization,
        focus_area: str,
        inputs: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate activities for ToC"""
        activities = []

        # Map focus area to activities
        activity_templates = {
            'business_continuity': [
                {
                    'name': 'Risk Assessment',
                    'description': 'Conduct regular business impact analysis and risk assessments',
                    'frequency': 'quarterly',
                    'required_inputs': ['financial', 'human', 'information']
                },
                {
                    'name': 'Continuity Planning',
                    'description': 'Develop and maintain business continuity plans',
                    'frequency': 'ongoing',
                    'required_inputs': ['knowledge', 'human']
                },
                {
                    'name': 'Training & Exercises',
                    'description': 'Conduct staff training and simulation exercises',
                    'frequency': 'monthly',
                    'required_inputs': ['human', 'financial']
                }
            ],
            'social_impact': [
                {
                    'name': 'Beneficiary Engagement',
                    'description': 'Engage with target beneficiaries and stakeholders',
                    'frequency': 'ongoing',
                    'required_inputs': ['human', 'financial']
                },
                {
                    'name': 'Program Delivery',
                    'description': 'Deliver core programs and services',
                    'frequency': 'daily',
                    'required_inputs': ['financial', 'human', 'infrastructure']
                },
                {
                    'name': 'Impact Monitoring',
                    'description': 'Monitor and evaluate program impact',
                    'frequency': 'monthly',
                    'required_inputs': ['information', 'human']
                }
            ],
            'operational_resilience': [
                {
                    'name': 'Infrastructure Maintenance',
                    'description': 'Maintain critical infrastructure',
                    'frequency': 'ongoing',
                    'required_inputs': ['financial', 'human', 'infrastructure']
                },
                {
                    'name': 'Capacity Building',
                    'description': 'Build organizational capacity and capabilities',
                    'frequency': 'quarterly',
                    'required_inputs': ['financial', 'human', 'knowledge']
                },
                {
                    'name': 'Stakeholder Coordination',
                    'description': 'Coordinate with key stakeholders',
                    'frequency': 'monthly',
                    'required_inputs': ['human', 'information']
                }
            ]
        }

        # Get templates for focus area
        templates = activity_templates.get(
            focus_area,
            activity_templates['operational_resilience']
        )

        # Generate activities from templates
        for template in templates:
            # Check if required inputs are available
            input_types = [inp['type'] for inp in inputs]
            has_required = all(
                req in input_types for req in template.get('required_inputs', [])
            )

            activities.append({
                'id': str(uuid4()),
                'name': template['name'],
                'description': template['description'],
                'frequency': template['frequency'],
                'status': 'active' if has_required else 'planned',
                'required_inputs': template.get('required_inputs', []),
                'resource_allocation': self._estimate_resource_allocation(template, inputs)
            })

        return activities

    def _generate_outputs(
        self,
        organization: Organization,
        focus_area: str,
        activities: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate outputs for ToC"""
        outputs = []

        # Map activities to outputs
        output_templates = {
            'Risk Assessment': {
                'name': 'Risk Register',
                'description': 'Updated risk register with identified risks and mitigation strategies',
                'type': 'deliverable',
                'frequency': 'quarterly'
            },
            'Continuity Planning': {
                'name': 'Business Continuity Plans',
                'description': 'Documented and tested BCPs for critical functions',
                'type': 'deliverable',
                'frequency': 'annual'
            },
            'Training & Exercises': {
                'name': 'Trained Staff',
                'description': 'Staff trained in emergency response and continuity procedures',
                'type': 'capacity',
                'frequency': 'monthly'
            },
            'Beneficiary Engagement': {
                'name': 'Stakeholder Relationships',
                'description': 'Strong relationships with beneficiaries and stakeholders',
                'type': 'capacity',
                'frequency': 'ongoing'
            },
            'Program Delivery': {
                'name': 'Services Delivered',
                'description': 'Programs and services delivered to target beneficiaries',
                'type': 'service',
                'frequency': 'daily'
            },
            'Impact Monitoring': {
                'name': 'Impact Reports',
                'description': 'Regular impact measurement and evaluation reports',
                'type': 'deliverable',
                'frequency': 'monthly'
            },
            'Infrastructure Maintenance': {
                'name': 'Operational Infrastructure',
                'description': 'Maintained and reliable infrastructure',
                'type': 'asset',
                'frequency': 'ongoing'
            },
            'Capacity Building': {
                'name': 'Enhanced Capabilities',
                'description': 'Improved organizational capabilities and processes',
                'type': 'capacity',
                'frequency': 'quarterly'
            },
            'Stakeholder Coordination': {
                'name': 'Coordination Mechanisms',
                'description': 'Established coordination mechanisms with key stakeholders',
                'type': 'process',
                'frequency': 'monthly'
            }
        }

        for activity in activities:
            activity_name = activity['name']
            if activity_name in output_templates:
                template = output_templates[activity_name]
                outputs.append({
                    'id': str(uuid4()),
                    'activity_id': activity['id'],
                    'name': template['name'],
                    'description': template['description'],
                    'type': template['type'],
                    'frequency': template['frequency'],
                    'measurable': True,
                    'target': self._generate_output_target(template['type'])
                })

        return outputs

    def _generate_outcomes(
        self,
        organization: Organization,
        focus_area: str,
        outputs: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate outcomes for ToC"""
        outcomes = []

        # Short-term outcomes (0-12 months)
        outcomes.append({
            'id': str(uuid4()),
            'name': 'Enhanced Preparedness',
            'description': 'Organization is better prepared for disruptions',
            'timeframe': 'short',
            'months': '0-12',
            'indicators': ['Staff awareness', 'Plan coverage', 'Exercise completion'],
            'target_value': 80,
            'unit': 'percent',
            'contributing_outputs': [o['id'] for o in outputs[:3]]
        })

        # Medium-term outcomes (12-24 months)
        outcomes.append({
            'id': str(uuid4()),
            'name': 'Improved Resilience',
            'description': 'Organization demonstrates resilience to disruptions',
            'timeframe': 'medium',
            'months': '12-24',
            'indicators': ['Recovery time', 'Service continuity', 'Stakeholder confidence'],
            'target_value': 90,
            'unit': 'percent',
            'contributing_outputs': [o['id'] for o in outputs]
        })

        # Long-term outcomes (24+ months)
        outcomes.append({
            'id': str(uuid4()),
            'name': 'Sustainable Operations',
            'description': 'Organization maintains sustainable and resilient operations',
            'timeframe': 'long',
            'months': '24+',
            'indicators': ['Business continuity', 'Stakeholder trust', 'Operational efficiency'],
            'target_value': 95,
            'unit': 'percent',
            'contributing_outputs': [o['id'] for o in outputs]
        })

        # Focus-specific outcomes
        if focus_area == 'social_impact':
            outcomes.append({
                'id': str(uuid4()),
                'name': 'Beneficiary Well-being',
                'description': 'Improved well-being of target beneficiaries',
                'timeframe': 'medium',
                'months': '12-24',
                'indicators': ['Beneficiary satisfaction', 'Quality of life measures'],
                'target_value': 85,
                'unit': 'percent',
                'contributing_outputs': [o['id'] for o in outputs if o['type'] == 'service']
            })

        return outcomes

    def _generate_impact(
        self,
        organization: Organization,
        focus_area: str,
        outcomes: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate ultimate impact statement"""

        impact_statements = {
            'business_continuity': {
                'title': 'Business Continuity and Resilience',
                'description': 'Organization maintains continuity of critical functions during disruptions, protecting stakeholders and sustaining value delivery',
                'beneficiaries': ['Employees', 'Customers', 'Shareholders', 'Community'],
                'timeframe': '3-5 years'
            },
            'social_impact': {
                'title': 'Sustainable Social Impact',
                'description': 'Organization creates lasting positive change for beneficiaries and communities',
                'beneficiaries': ['Direct beneficiaries', 'Communities', 'Society'],
                'timeframe': '3-5 years'
            },
            'operational_resilience': {
                'title': 'Operational Excellence and Resilience',
                'description': 'Organization operates efficiently and adapts effectively to changing conditions',
                'beneficiaries': ['Stakeholders', 'Service recipients', 'Partners'],
                'timeframe': '3-5 years'
            },
            'service_delivery': {
                'title': 'Reliable Service Delivery',
                'description': 'Organization delivers essential services reliably and sustainably',
                'beneficiaries': ['Citizens', 'Service users', 'Community'],
                'timeframe': '3-5 years'
            }
        }

        impact_template = impact_statements.get(
            focus_area,
            impact_statements['operational_resilience']
        )

        return {
            'id': str(uuid4()),
            'title': impact_template['title'],
            'description': impact_template['description'],
            'beneficiaries': impact_template['beneficiaries'],
            'timeframe': impact_template['timeframe'],
            'contributing_outcomes': [o['id'] for o in outcomes],
            'measurement_approach': 'Longitudinal tracking of key impact indicators',
            'sdg_alignment': self._map_to_sdgs(focus_area)
        }

    def _generate_assumptions(
        self,
        organization: Organization,
        focus_area: str
    ) -> List[str]:
        """Generate key assumptions for ToC"""
        assumptions = [
            'Sufficient resources are available for planned activities',
            'External environment remains relatively stable',
            'Stakeholder cooperation continues',
            'Organizational leadership supports continuity',
        ]

        # Add focus-specific assumptions
        focus_assumptions = {
            'business_continuity': [
                'Critical functions are accurately identified',
                'Staff participate in training and exercises',
                'Technology systems remain operational',
            ],
            'social_impact': [
                'Beneficiary needs remain consistent with program design',
                'Community support continues',
                'Funding sources remain available',
            ],
            'operational_resilience': [
                'Infrastructure maintenance is prioritized',
                'Supply chains remain functional',
                'Regulatory environment supports operations',
            ]
        }

        assumptions.extend(focus_assumptions.get(focus_area, []))

        return assumptions

    def _generate_indicators(
        self,
        organization: Organization,
        focus_area: str
    ) -> List[Dict[str, Any]]:
        """Generate indicators for measurement"""
        indicators = []

        # Universal indicators
        base_indicators = [
            {
                'id': str(uuid4()),
                'level': 'input',
                'name': 'Budget Utilization',
                'description': 'Percentage of budget allocated and utilized',
                'measurement': 'Financial tracking',
                'frequency': 'monthly',
                'target': 95,
                'unit': 'percent'
            },
            {
                'id': str(uuid4()),
                'level': 'activity',
                'name': 'Activity Completion Rate',
                'description': 'Percentage of planned activities completed',
                'measurement': 'Project management tracking',
                'frequency': 'monthly',
                'target': 90,
                'unit': 'percent'
            },
            {
                'id': str(uuid4()),
                'level': 'output',
                'name': 'Output Quality',
                'description': 'Quality score of deliverables',
                'measurement': 'Quality assessment',
                'frequency': 'quarterly',
                'target': 85,
                'unit': 'score'
            },
            {
                'id': str(uuid4()),
                'level': 'outcome',
                'name': 'Resilience Score',
                'description': 'Overall organizational resilience score',
                'measurement': 'Digital Twin health score',
                'frequency': 'quarterly',
                'target': 80,
                'unit': 'score'
            }
        ]

        indicators.extend(base_indicators)

        # Focus-specific indicators
        if focus_area == 'business_continuity':
            indicators.append({
                'id': str(uuid4()),
                'level': 'outcome',
                'name': 'Recovery Time Objective Achievement',
                'description': 'Percentage of critical functions meeting RTO',
                'measurement': 'Exercise and incident tracking',
                'frequency': 'quarterly',
                'target': 95,
                'unit': 'percent'
            })

        return indicators

    def _generate_pathways(
        self,
        organization: Organization,
        inputs: List[Dict[str, Any]],
        activities: List[Dict[str, Any]],
        outputs: List[Dict[str, Any]],
        outcomes: List[Dict[str, Any]],
        impact: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate logical pathways through ToC"""
        pathways = []

        # Primary pathway
        pathways.append({
            'id': str(uuid4()),
            'name': 'Primary Pathway',
            'description': 'Main logic chain from inputs to impact',
            'steps': [
                {'stage': 'inputs', 'items': [i['id'] for i in inputs[:3]]},
                {'stage': 'activities', 'items': [a['id'] for a in activities]},
                {'stage': 'outputs', 'items': [o['id'] for o in outputs]},
                {'stage': 'outcomes', 'items': [oc['id'] for oc in outcomes]},
                {'stage': 'impact', 'items': [impact['id']]}
            ],
            'critical': True
        })

        return pathways

    def _estimate_resource_allocation(
        self,
        template: Dict[str, Any],
        inputs: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Estimate resource allocation for activity"""
        allocation = {
            'financial': 0,
            'human': 0,
            'time': template.get('frequency', 'monthly')
        }

        # Simple heuristic allocation
        required = template.get('required_inputs', [])

        if 'financial' in required:
            # Allocate based on total budget
            financial_inputs = [i for i in inputs if i['type'] == 'financial']
            if financial_inputs:
                total_budget = financial_inputs[0]['value']
                allocation['financial'] = total_budget * 0.1  # 10% allocation

        if 'human' in required:
            # Allocate based on total staff
            human_inputs = [i for i in inputs if i['type'] == 'human']
            if human_inputs:
                total_staff = human_inputs[0]['value']
                allocation['human'] = max(1, int(total_staff * 0.05))  # 5% of staff

        return allocation

    def _generate_output_target(self, output_type: str) -> Dict[str, Any]:
        """Generate target for output"""
        targets = {
            'deliverable': {'quantity': 1, 'quality': 90, 'unit': 'documents'},
            'capacity': {'increase': 20, 'unit': 'percent'},
            'service': {'coverage': 80, 'satisfaction': 85, 'unit': 'percent'},
            'asset': {'availability': 95, 'unit': 'percent'},
            'process': {'efficiency': 85, 'unit': 'score'}
        }

        return targets.get(output_type, {'value': 80, 'unit': 'percent'})

    def _map_to_sdgs(self, focus_area: str) -> List[int]:
        """Map focus area to UN Sustainable Development Goals"""
        sdg_mapping = {
            'business_continuity': [8, 9, 11],  # Decent Work, Industry, Sustainable Cities
            'social_impact': [1, 3, 10],  # No Poverty, Health, Reduced Inequalities
            'operational_resilience': [9, 11, 12],  # Industry, Cities, Responsible Consumption
            'service_delivery': [3, 6, 11]  # Health, Water, Sustainable Cities
        }

        return sdg_mapping.get(focus_area, [9, 11])
