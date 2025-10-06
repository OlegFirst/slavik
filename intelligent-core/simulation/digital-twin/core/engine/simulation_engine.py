"""
Simulation Engine - портировано из digital-twin-platform/src/simulation-engine.js

Реализует все 10+ сценариев симуляций для Digital Twin
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging
import asyncio

from core.models.base import (
    Organization,
    SimulationResult,
    SimulationParameters,
    SimulationScenarioType,
    SimulationStatus
)

logger = logging.getLogger(__name__)


class SimulationScenario(ABC):
    """
    Abstract base class for simulation scenarios

    Каждый сценарий должен реализовать метод run()
    """

    def __init__(self):
        self.name = self.__class__.__name__
        self.scenario_type = None

    @abstractmethod
    async def run(
        self,
        organization: Organization,
        params: SimulationParameters
    ) -> SimulationResult:
        """Run simulation scenario"""
        pass

    def _build_timeline(
        self,
        duration_months: int,
        events: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Build timeline from events"""
        timeline = []
        start_date = datetime.utcnow()

        for i, event in enumerate(events):
            timeline.append({
                'month': i + 1,
                'date': (start_date + timedelta(days=30 * i)).isoformat(),
                'event': event.get('description', ''),
                'impact': event.get('impact', 0),
                'metrics': event.get('metrics', {})
            })

        return timeline


class FundingShockScenario(SimulationScenario):
    """
    Funding Shock Scenario

    Портировано из: digital-twin-platform/src/simulation-engine.js
    Симулирует внезапное сокращение финансирования
    """

    def __init__(self):
        super().__init__()
        self.scenario_type = SimulationScenarioType.FUNDING_SHOCK

    async def run(
        self,
        organization: Organization,
        params: SimulationParameters
    ) -> SimulationResult:
        """
        Run funding shock simulation

        Алгоритм из оригинала:
        1. Рассчитать размер шока (% падения финансирования)
        2. Оценить влияние на операции
        3. Определить время восстановления
        4. Сгенерировать план восстановления
        """
        logger.info(f"Running funding shock simulation for {organization.name}")

        # Parameters
        funding_drop_percent = params.custom_params.get('funding_drop_percent', 30)
        duration_months = params.duration_months

        current_budget = organization.annual_budget or 1000000
        shock_amount = current_budget * (funding_drop_percent / 100)
        new_budget = current_budget - shock_amount

        # Calculate impact
        financial_impact = self._calculate_financial_impact(
            current_budget,
            new_budget,
            duration_months
        )

        operational_impact = self._calculate_operational_impact(
            funding_drop_percent,
            organization.employee_count or 20
        )

        # Recovery timeline
        recovery_time_days = self._estimate_recovery_time(
            funding_drop_percent,
            organization.maturity_level
        )

        # Generate recovery plan
        recovery_plan = self._generate_recovery_plan(
            organization,
            funding_drop_percent,
            duration_months
        )

        # Build timeline
        events = self._generate_timeline_events(
            funding_drop_percent,
            duration_months
        )
        timeline = self._build_timeline(duration_months, events)

        # Calculate overall impact score
        impact_score = (financial_impact + operational_impact) / 2

        # Create result
        result = SimulationResult(
            twin_id=organization.twin_id,
            scenario=self.scenario_type,
            parameters=params,
            status=SimulationStatus.COMPLETED,
            impact_score=impact_score,
            financial_impact=financial_impact,
            operational_impact=operational_impact,
            recovery_time_days=recovery_time_days,
            timeline=timeline,
            recommendations=self._generate_recommendations(impact_score),
            recovery_plan=recovery_plan,
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
            duration_seconds=0.5
        )

        return result

    def _calculate_financial_impact(
        self,
        current_budget: float,
        new_budget: float,
        duration: int
    ) -> float:
        """Calculate financial impact (0-100)"""
        drop_percent = ((current_budget - new_budget) / current_budget) * 100

        # Impact score increases with drop percentage and duration
        base_impact = drop_percent
        duration_factor = min(duration / 12, 1.5)  # Max 1.5x multiplier

        impact = base_impact * duration_factor
        return min(impact, 100)

    def _calculate_operational_impact(
        self,
        funding_drop: float,
        staff_count: int
    ) -> float:
        """Calculate operational impact (0-100)"""
        # Operational impact depends on funding drop and staff size
        base_impact = funding_drop * 0.8  # Slightly less than financial

        # Smaller orgs are more vulnerable
        size_factor = 1 + (1 / max(staff_count, 1)) * 10

        impact = base_impact * min(size_factor, 1.5)
        return min(impact, 100)

    def _estimate_recovery_time(
        self,
        funding_drop: float,
        maturity_level: int
    ) -> int:
        """Estimate recovery time in days"""
        # Base recovery time
        base_days = 180  # 6 months

        # Impact increases recovery time
        impact_factor = funding_drop / 30  # 30% drop = 1x

        # Maturity reduces recovery time
        maturity_factor = 1 / max(maturity_level, 1)

        recovery_days = int(base_days * impact_factor * maturity_factor)
        return max(recovery_days, 30)  # Minimum 1 month

    def _generate_recovery_plan(
        self,
        org: Organization,
        funding_drop: float,
        duration: int
    ) -> Dict[str, Any]:
        """Generate recovery plan"""
        plan = {
            'phases': [],
            'actions': [],
            'milestones': [],
            'budget_allocation': {}
        }

        # Phase 1: Immediate response (0-30 days)
        plan['phases'].append({
            'name': 'Immediate Response',
            'duration_days': 30,
            'priority': 'critical',
            'actions': [
                'Assess financial situation',
                'Freeze non-essential spending',
                'Communicate with stakeholders',
                'Review all contracts'
            ]
        })

        # Phase 2: Stabilization (30-90 days)
        plan['phases'].append({
            'name': 'Stabilization',
            'duration_days': 60,
            'priority': 'high',
            'actions': [
                'Implement cost reduction measures',
                'Seek alternative funding sources',
                'Renegotiate with suppliers',
                'Optimize operations'
            ]
        })

        # Phase 3: Recovery (90-180 days)
        plan['phases'].append({
            'name': 'Recovery',
            'duration_days': 90,
            'priority': 'medium',
            'actions': [
                'Rebuild financial reserves',
                'Restore full operations',
                'Evaluate new opportunities',
                'Update risk management plans'
            ]
        })

        # Key actions
        if funding_drop > 40:
            plan['actions'].append('Consider emergency fundraising campaign')
            plan['actions'].append('Evaluate staff reductions')

        if funding_drop > 25:
            plan['actions'].append('Defer capital investments')
            plan['actions'].append('Renegotiate lease agreements')

        plan['actions'].extend([
            'Diversify funding sources',
            'Build emergency reserve fund',
            'Enhance financial monitoring'
        ])

        return plan

    def _generate_timeline_events(
        self,
        funding_drop: float,
        duration: int
    ) -> List[Dict[str, Any]]:
        """Generate timeline events"""
        events = []

        # Month 0: Shock occurs
        events.append({
            'description': f'Funding shock: {funding_drop}% reduction',
            'impact': funding_drop,
            'metrics': {'budget_change': -funding_drop}
        })

        # Subsequent months
        for month in range(1, duration + 1):
            recovery_percent = (month / duration) * 100

            if month == 1:
                events.append({
                    'description': 'Emergency measures implemented',
                    'impact': funding_drop * 0.9,
                    'metrics': {'recovery': recovery_percent}
                })
            elif month == 3:
                events.append({
                    'description': 'Stabilization phase begins',
                    'impact': funding_drop * 0.6,
                    'metrics': {'recovery': recovery_percent}
                })
            elif month == 6:
                events.append({
                    'description': 'Recovery phase initiated',
                    'impact': funding_drop * 0.3,
                    'metrics': {'recovery': recovery_percent}
                })
            else:
                events.append({
                    'description': f'Month {month}: Ongoing recovery',
                    'impact': max(0, funding_drop * (1 - recovery_percent / 100)),
                    'metrics': {'recovery': recovery_percent}
                })

        return events

    def _generate_recommendations(self, impact_score: float) -> List[str]:
        """Generate recommendations based on impact"""
        recommendations = []

        if impact_score > 70:
            recommendations.extend([
                'CRITICAL: Implement emergency cost reduction immediately',
                'Engage with board and key stakeholders urgently',
                'Consider emergency fundraising campaign',
                'Evaluate all operational expenses for immediate cuts'
            ])
        elif impact_score > 40:
            recommendations.extend([
                'HIGH: Review and reduce non-essential expenses',
                'Communicate funding situation to stakeholders',
                'Explore alternative funding sources',
                'Implement financial monitoring protocols'
            ])
        else:
            recommendations.extend([
                'MODERATE: Monitor financial situation closely',
                'Review contingency plans',
                'Build emergency reserve fund',
                'Diversify funding sources'
            ])

        # Always include
        recommendations.extend([
            'Conduct regular financial health assessments',
            'Maintain transparent communication with funders',
            'Develop robust financial risk management plan'
        ])

        return recommendations


class StaffDisruptionScenario(SimulationScenario):
    """
    Staff Disruption Scenario

    Симулирует потерю ключевых сотрудников или массовые увольнения
    """

    def __init__(self):
        super().__init__()
        self.scenario_type = SimulationScenarioType.STAFF_DISRUPTION

    async def run(
        self,
        organization: Organization,
        params: SimulationParameters
    ) -> SimulationResult:
        """Run staff disruption simulation"""
        logger.info(f"Running staff disruption simulation for {organization.name}")

        # Parameters
        staff_loss_percent = params.custom_params.get('staff_loss_percent', 25)
        duration_months = params.duration_months

        current_staff = organization.employee_count or 20
        staff_lost = int(current_staff * (staff_loss_percent / 100))

        # Calculate impacts
        operational_impact = self._calculate_operational_impact(
            staff_loss_percent,
            current_staff
        )

        financial_impact = self._calculate_financial_impact(
            staff_lost,
            organization.annual_budget or 1000000
        )

        # Recovery time
        recovery_time_days = self._estimate_recovery_time(
            staff_loss_percent,
            organization.maturity_level
        )

        # Timeline and recovery plan
        events = self._generate_timeline_events(staff_loss_percent, duration_months)
        timeline = self._build_timeline(duration_months, events)
        recovery_plan = self._generate_recovery_plan(staff_lost, duration_months)

        impact_score = (operational_impact + financial_impact) / 2

        result = SimulationResult(
            twin_id=organization.twin_id,
            scenario=self.scenario_type,
            parameters=params,
            status=SimulationStatus.COMPLETED,
            impact_score=impact_score,
            financial_impact=financial_impact,
            operational_impact=operational_impact,
            recovery_time_days=recovery_time_days,
            timeline=timeline,
            recommendations=self._generate_recommendations(impact_score),
            recovery_plan=recovery_plan,
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
            duration_seconds=0.5
        )

        return result

    def _calculate_operational_impact(self, staff_loss: float, staff_count: int) -> float:
        """Calculate operational impact of staff loss"""
        # Base impact from % loss
        base_impact = staff_loss * 1.2  # Staff loss hits operations hard

        # Smaller orgs suffer more
        size_factor = 1 + (50 / max(staff_count, 1))

        impact = base_impact * min(size_factor, 2.0)
        return min(impact, 100)

    def _calculate_financial_impact(self, staff_lost: int, budget: float) -> float:
        """Calculate financial impact"""
        # Recruitment, training, productivity loss costs
        cost_per_person = budget / 100  # Rough estimate
        total_cost = staff_lost * cost_per_person * 1.5  # 1.5x for indirect costs

        impact = (total_cost / budget) * 100
        return min(impact, 100)

    def _estimate_recovery_time(self, staff_loss: float, maturity: int) -> int:
        """Estimate recovery time"""
        base_days = 120  # 4 months
        impact_factor = staff_loss / 25  # 25% loss = 1x
        maturity_factor = 1 / max(maturity, 1)

        return int(base_days * impact_factor * maturity_factor)

    def _generate_timeline_events(self, staff_loss: float, duration: int) -> List[Dict]:
        """Generate timeline events"""
        events = [{
            'description': f'Staff disruption: {staff_loss}% loss',
            'impact': staff_loss,
            'metrics': {'staff_change': -staff_loss}
        }]

        for month in range(1, duration + 1):
            recovery = (month / duration) * 100
            events.append({
                'description': f'Month {month}: Recruitment and training',
                'impact': max(0, staff_loss * (1 - recovery / 100)),
                'metrics': {'recovery': recovery}
            })

        return events

    def _generate_recovery_plan(self, staff_lost: int, duration: int) -> Dict:
        """Generate recovery plan"""
        return {
            'phases': [
                {
                    'name': 'Immediate Stabilization',
                    'duration_days': 30,
                    'actions': [
                        'Redistribute critical responsibilities',
                        'Activate contingency staffing plans',
                        'Communicate with remaining staff',
                        'Begin recruitment process'
                    ]
                },
                {
                    'name': 'Recruitment & Training',
                    'duration_days': 60,
                    'actions': [
                        'Fast-track recruitment',
                        'Implement onboarding programs',
                        'Cross-train existing staff',
                        'Consider temporary contractors'
                    ]
                },
                {
                    'name': 'Stabilization',
                    'duration_days': 30,
                    'actions': [
                        'Complete training programs',
                        'Restore full operational capacity',
                        'Review retention strategies',
                        'Update succession plans'
                    ]
                }
            ],
            'key_actions': [
                f'Recruit {staff_lost} new staff members',
                'Enhance employee retention programs',
                'Develop succession planning',
                'Create knowledge transfer protocols'
            ]
        }

    def _generate_recommendations(self, impact_score: float) -> List[str]:
        """Generate recommendations"""
        recommendations = []

        if impact_score > 70:
            recommendations.extend([
                'CRITICAL: Activate emergency staffing protocols',
                'Consider hiring temporary contractors immediately',
                'Redistribute workload to prevent burnout',
                'Fast-track recruitment process'
            ])
        elif impact_score > 40:
            recommendations.extend([
                'HIGH: Begin recruitment immediately',
                'Implement retention bonuses',
                'Review compensation packages',
                'Enhance employee engagement'
            ])
        else:
            recommendations.extend([
                'MODERATE: Update succession plans',
                'Review retention strategies',
                'Implement knowledge management',
                'Enhance training programs'
            ])

        return recommendations


class SupplyChainBreakScenario(SimulationScenario):
    """Supply Chain Break Scenario - портировано из digital-twin-platform"""

    def __init__(self):
        super().__init__()
        self.scenario_type = SimulationScenarioType.SUPPLY_CHAIN_BREAK

    async def run(self, organization: Organization, params: SimulationParameters) -> SimulationResult:
        """Simulate supply chain disruption"""
        logger.info(f"Running supply chain disruption for {organization.name}")

        # Parameters
        disruption_severity = params.custom_params.get('disruption_severity', 60)  # 0-100
        duration_months = params.duration_months
        suppliers_affected = params.custom_params.get('suppliers_affected', 3)

        # Calculate impacts
        operational_impact = disruption_severity * 0.9  # Operations hit hard
        financial_impact = disruption_severity * 0.7  # Financial follows

        recovery_time_days = int(duration_months * 30 * (disruption_severity / 50))

        # Timeline and recovery
        events = self._generate_timeline_events(disruption_severity, duration_months)
        timeline = self._build_timeline(duration_months, events)
        recovery_plan = self._generate_recovery_plan(suppliers_affected, duration_months)

        impact_score = (operational_impact + financial_impact) / 2

        return SimulationResult(
            twin_id=organization.twin_id,
            scenario=self.scenario_type,
            parameters=params,
            status=SimulationStatus.COMPLETED,
            impact_score=impact_score,
            financial_impact=financial_impact,
            operational_impact=operational_impact,
            recovery_time_days=recovery_time_days,
            timeline=timeline,
            recommendations=self._generate_recommendations(impact_score),
            recovery_plan=recovery_plan,
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
            duration_seconds=0.5
        )

    def _generate_timeline_events(self, severity: float, duration: int) -> List[Dict]:
        events = [{'description': f'Supply chain disruption: {severity}% severity', 'impact': severity}]
        for month in range(1, duration + 1):
            recovery = (month / duration) * 100
            events.append({
                'description': f'Month {month}: Sourcing alternatives',
                'impact': max(0, severity * (1 - recovery / 100)),
                'metrics': {'recovery': recovery}
            })
        return events

    def _generate_recovery_plan(self, suppliers: int, duration: int) -> Dict:
        return {
            'phases': [
                {'name': 'Emergency Sourcing', 'duration_days': 30, 'actions': [
                    'Identify alternative suppliers', 'Expedite emergency orders',
                    'Activate backup suppliers', 'Assess inventory levels'
                ]},
                {'name': 'Stabilization', 'duration_days': 60, 'actions': [
                    'Establish new supplier relationships', 'Rebuild inventory',
                    'Optimize logistics', 'Review contracts'
                ]},
                {'name': 'Resilience', 'duration_days': 90, 'actions': [
                    'Diversify supplier base', 'Implement redundancy',
                    'Update risk assessments', 'Build strategic reserves'
                ]}
            ],
            'key_actions': [f'Source {suppliers} alternative suppliers', 'Diversify supply chain',
                           'Implement supply chain monitoring', 'Build inventory buffers']
        }

    def _generate_recommendations(self, impact: float) -> List[str]:
        recs = []
        if impact > 70:
            recs.extend(['CRITICAL: Activate emergency procurement', 'Seek alternative suppliers immediately',
                        'Consider temporary production halt', 'Communicate with customers urgently'])
        elif impact > 40:
            recs.extend(['HIGH: Fast-track alternative sourcing', 'Review supplier dependencies',
                        'Implement inventory management', 'Diversify supplier base'])
        else:
            recs.extend(['MODERATE: Monitor supply chain closely', 'Review supplier contracts',
                        'Build strategic reserves', 'Enhance supplier relationships'])
        recs.extend(['Implement supply chain risk management', 'Diversify supplier base',
                    'Develop contingency procurement plans'])
        return recs


class CyberAttackScenario(SimulationScenario):
    """Cyber Attack Scenario"""

    def __init__(self):
        super().__init__()
        self.scenario_type = SimulationScenarioType.CYBER_ATTACK

    async def run(self, organization: Organization, params: SimulationParameters) -> SimulationResult:
        logger.info(f"Running cyber attack simulation for {organization.name}")

        attack_type = params.custom_params.get('attack_type', 'ransomware')  # ransomware, data_breach, ddos
        severity = params.custom_params.get('severity', 70)
        duration_months = params.duration_months

        # Impacts vary by attack type
        if attack_type == 'ransomware':
            operational_impact = severity * 0.95
            financial_impact = severity * 0.8
            recovery_days = int(duration_months * 30)
        elif attack_type == 'data_breach':
            operational_impact = severity * 0.6
            financial_impact = severity * 0.9  # Legal costs, fines
            recovery_days = int(duration_months * 45)
        else:  # ddos
            operational_impact = severity * 0.7
            financial_impact = severity * 0.5
            recovery_days = int(duration_months * 20)

        events = [
            {'description': f'{attack_type} attack detected', 'impact': severity},
            {'description': 'Incident response activated', 'impact': severity * 0.8},
            {'description': 'Systems being restored', 'impact': severity * 0.5},
            {'description': 'Security hardening in progress', 'impact': severity * 0.3},
            {'description': 'Normal operations resumed', 'impact': 0}
        ]
        timeline = self._build_timeline(min(duration_months, 5), events)

        recovery_plan = {
            'phases': [
                {'name': 'Containment', 'duration_days': 3, 'actions': [
                    'Isolate affected systems', 'Activate incident response team',
                    'Assess damage scope', 'Notify stakeholders'
                ]},
                {'name': 'Recovery', 'duration_days': 30, 'actions': [
                    'Restore from backups', 'Rebuild systems', 'Enhance security',
                    'Conduct forensics'
                ]},
                {'name': 'Hardening', 'duration_days': 60, 'actions': [
                    'Implement additional security measures', 'Train staff',
                    'Update policies', 'Conduct security audit'
                ]}
            ]
        }

        impact_score = (operational_impact + financial_impact) / 2

        return SimulationResult(
            twin_id=organization.twin_id, scenario=self.scenario_type, parameters=params,
            status=SimulationStatus.COMPLETED, impact_score=impact_score,
            financial_impact=financial_impact, operational_impact=operational_impact,
            recovery_time_days=recovery_days, timeline=timeline,
            recommendations=['Implement zero-trust architecture', 'Conduct security training',
                           'Establish incident response plan', 'Regular security audits',
                           'Maintain offline backups', 'Implement MFA'],
            recovery_plan=recovery_plan, started_at=datetime.utcnow(),
            completed_at=datetime.utcnow(), duration_seconds=0.5
        )


class RegulatoryChangeScenario(SimulationScenario):
    """Regulatory Change Scenario"""

    def __init__(self):
        super().__init__()
        self.scenario_type = SimulationScenarioType.REGULATORY_CHANGE

    async def run(self, organization: Organization, params: SimulationParameters) -> SimulationResult:
        logger.info(f"Running regulatory change simulation for {organization.name}")

        compliance_gap = params.custom_params.get('compliance_gap', 50)  # % non-compliant
        implementation_cost = params.custom_params.get('cost_estimate', 100000)
        duration_months = params.duration_months

        financial_impact = min((implementation_cost / (organization.annual_budget or 1000000)) * 100, 100)
        operational_impact = compliance_gap * 0.6  # Operations affected

        recovery_days = int(duration_months * 30)

        events = [
            {'description': 'New regulation announced', 'impact': compliance_gap},
            {'description': 'Compliance assessment completed', 'impact': compliance_gap * 0.8},
            {'description': 'Implementation plan approved', 'impact': compliance_gap * 0.6},
            {'description': 'Systems being updated', 'impact': compliance_gap * 0.4},
            {'description': 'Compliance achieved', 'impact': 0}
        ]

        recovery_plan = {
            'phases': [
                {'name': 'Assessment', 'duration_days': 30, 'actions': [
                    'Conduct gap analysis', 'Identify requirements', 'Estimate costs',
                    'Engage legal counsel'
                ]},
                {'name': 'Planning', 'duration_days': 60, 'actions': [
                    'Develop compliance plan', 'Allocate budget', 'Assign responsibilities',
                    'Update policies'
                ]},
                {'name': 'Implementation', 'duration_days': 90, 'actions': [
                    'Update systems', 'Train staff', 'Document processes',
                    'Conduct audits'
                ]}
            ]
        }

        impact_score = (financial_impact + operational_impact) / 2

        return SimulationResult(
            twin_id=organization.twin_id, scenario=self.scenario_type, parameters=params,
            status=SimulationStatus.COMPLETED, impact_score=impact_score,
            financial_impact=financial_impact, operational_impact=operational_impact,
            recovery_time_days=recovery_days, timeline=self._build_timeline(min(duration_months, 5), events),
            recommendations=['Engage regulatory experts', 'Conduct compliance audit',
                           'Develop implementation roadmap', 'Budget for compliance costs',
                           'Train staff on new requirements', 'Establish compliance monitoring'],
            recovery_plan=recovery_plan, started_at=datetime.utcnow(),
            completed_at=datetime.utcnow(), duration_seconds=0.5
        )


class ReputationCrisisScenario(SimulationScenario):
    """Reputation Crisis Scenario"""

    def __init__(self):
        super().__init__()
        self.scenario_type = SimulationScenarioType.REPUTATION_CRISIS

    async def run(self, organization: Organization, params: SimulationParameters) -> SimulationResult:
        logger.info(f"Running reputation crisis for {organization.name}")

        crisis_severity = params.custom_params.get('severity', 60)
        media_attention = params.custom_params.get('media_attention', 'high')  # low/medium/high
        duration_months = params.duration_months

        # Media attention multiplier
        media_multiplier = {'low': 0.7, 'medium': 1.0, 'high': 1.3}.get(media_attention, 1.0)

        operational_impact = crisis_severity * 0.5
        financial_impact = (crisis_severity * 0.8 * media_multiplier)  # Revenue drop, PR costs

        recovery_days = int(duration_months * 30 * media_multiplier)

        recovery_plan = {
            'phases': [
                {'name': 'Crisis Response', 'duration_days': 7, 'actions': [
                    'Activate crisis management team', 'Issue public statement',
                    'Engage stakeholders', 'Monitor social media'
                ]},
                {'name': 'Damage Control', 'duration_days': 30, 'actions': [
                    'Launch PR campaign', 'Address root causes', 'Implement corrective actions',
                    'Rebuild trust'
                ]},
                {'name': 'Reputation Rebuild', 'duration_days': 90, 'actions': [
                    'Positive PR initiatives', 'Community engagement', 'Transparency reports',
                    'Brand rehabilitation'
                ]}
            ]
        }

        impact_score = (operational_impact + financial_impact) / 2

        return SimulationResult(
            twin_id=organization.twin_id, scenario=self.scenario_type, parameters=params,
            status=SimulationStatus.COMPLETED, impact_score=impact_score,
            financial_impact=financial_impact, operational_impact=operational_impact,
            recovery_time_days=recovery_days,
            timeline=self._build_timeline(duration_months, [
                {'description': 'Reputation crisis emerges', 'impact': crisis_severity},
                {'description': 'Crisis response initiated', 'impact': crisis_severity * 0.7},
                {'description': 'PR campaign launched', 'impact': crisis_severity * 0.5},
                {'description': 'Trust rebuilding', 'impact': crisis_severity * 0.3},
                {'description': 'Reputation stabilized', 'impact': 0}
            ]),
            recommendations=['Activate crisis communications plan', 'Be transparent and honest',
                           'Engage stakeholders proactively', 'Monitor social media',
                           'Implement corrective actions', 'Consider professional PR support'],
            recovery_plan=recovery_plan, started_at=datetime.utcnow(),
            completed_at=datetime.utcnow(), duration_seconds=0.5
        )


class EconomicDownturnScenario(SimulationScenario):
    """Economic Downturn Scenario"""

    def __init__(self):
        super().__init__()
        self.scenario_type = SimulationScenarioType.ECONOMIC_DOWNTURN

    async def run(self, organization: Organization, params: SimulationParameters) -> SimulationResult:
        logger.info(f"Running economic downturn simulation for {organization.name}")

        downturn_severity = params.custom_params.get('severity', 50)  # % GDP decline
        duration_months = params.duration_months

        financial_impact = downturn_severity * 0.9  # Revenue drop
        operational_impact = downturn_severity * 0.6  # Cost cutting impact

        recovery_days = int(duration_months * 45)  # Economic recovery is slow

        recovery_plan = {
            'phases': [
                {'name': 'Cost Reduction', 'duration_days': 60, 'actions': [
                    'Reduce discretionary spending', 'Negotiate better terms',
                    'Defer capital investments', 'Optimize operations'
                ]},
                {'name': 'Revenue Protection', 'duration_days': 90, 'actions': [
                    'Focus on core business', 'Enhance customer retention',
                    'Explore new markets', 'Diversify revenue streams'
                ]},
                {'name': 'Strategic Positioning', 'duration_days': 120, 'actions': [
                    'Invest in efficiency', 'Build competitive advantages',
                    'Prepare for recovery', 'Strategic partnerships'
                ]}
            ]
        }

        impact_score = (financial_impact + operational_impact) / 2

        return SimulationResult(
            twin_id=organization.twin_id, scenario=self.scenario_type, parameters=params,
            status=SimulationStatus.COMPLETED, impact_score=impact_score,
            financial_impact=financial_impact, operational_impact=operational_impact,
            recovery_time_days=recovery_days,
            timeline=self._build_timeline(duration_months, [
                {'description': 'Economic downturn begins', 'impact': downturn_severity},
                {'description': 'Cost reduction measures', 'impact': downturn_severity * 0.8},
                {'description': 'Revenue stabilization', 'impact': downturn_severity * 0.6},
                {'description': 'Gradual recovery', 'impact': downturn_severity * 0.3},
                {'description': 'Economic stabilization', 'impact': 0}
            ]),
            recommendations=['Build cash reserves', 'Reduce fixed costs', 'Focus on profitability',
                           'Maintain customer relationships', 'Invest counter-cyclically',
                           'Explore government support programs'],
            recovery_plan=recovery_plan, started_at=datetime.utcnow(),
            completed_at=datetime.utcnow(), duration_seconds=0.5
        )


class NaturalDisasterScenario(SimulationScenario):
    """Natural Disaster Scenario"""

    def __init__(self):
        super().__init__()
        self.scenario_type = SimulationScenarioType.NATURAL_DISASTER

    async def run(self, organization: Organization, params: SimulationParameters) -> SimulationResult:
        logger.info(f"Running natural disaster simulation for {organization.name}")

        disaster_type = params.custom_params.get('disaster_type', 'flood')
        severity = params.custom_params.get('severity', 70)
        infrastructure_damage = params.custom_params.get('infrastructure_damage', 60)
        duration_months = params.duration_months

        operational_impact = min(infrastructure_damage * 1.2, 100)
        financial_impact = severity * 0.8

        recovery_days = int((infrastructure_damage / 10) * 30)  # Higher damage = longer recovery

        recovery_plan = {
            'phases': [
                {'name': 'Emergency Response', 'duration_days': 7, 'actions': [
                    'Ensure staff safety', 'Assess damage', 'Activate disaster recovery',
                    'Communicate with stakeholders'
                ]},
                {'name': 'Business Continuity', 'duration_days': 30, 'actions': [
                    'Activate backup facilities', 'Restore critical operations',
                    'File insurance claims', 'Support affected staff'
                ]},
                {'name': 'Rebuild', 'duration_days': 180, 'actions': [
                    'Repair/rebuild facilities', 'Replace equipment',
                    'Resume full operations', 'Update disaster plans'
                ]}
            ]
        }

        impact_score = (operational_impact + financial_impact) / 2

        return SimulationResult(
            twin_id=organization.twin_id, scenario=self.scenario_type, parameters=params,
            status=SimulationStatus.COMPLETED, impact_score=impact_score,
            financial_impact=financial_impact, operational_impact=operational_impact,
            recovery_time_days=recovery_days,
            timeline=self._build_timeline(min(duration_months, 6), [
                {'description': f'{disaster_type} disaster strikes', 'impact': severity},
                {'description': 'Emergency response', 'impact': severity * 0.8},
                {'description': 'Business continuity activated', 'impact': severity * 0.6},
                {'description': 'Rebuilding in progress', 'impact': severity * 0.4},
                {'description': 'Operations restored', 'impact': 0}
            ]),
            recommendations=['Ensure adequate insurance coverage', 'Develop disaster recovery plan',
                           'Identify alternative facilities', 'Regular disaster drills',
                           'Backup critical data offsite', 'Establish emergency funds'],
            recovery_plan=recovery_plan, started_at=datetime.utcnow(),
            completed_at=datetime.utcnow(), duration_seconds=0.5
        )


class PandemicScenario(SimulationScenario):
    """Pandemic Scenario"""

    def __init__(self):
        super().__init__()
        self.scenario_type = SimulationScenarioType.PANDEMIC

    async def run(self, organization: Organization, params: SimulationParameters) -> SimulationResult:
        logger.info(f"Running pandemic simulation for {organization.name}")

        infection_rate = params.custom_params.get('infection_rate', 40)  # % staff affected
        duration_months = params.duration_months
        remote_work_capability = params.custom_params.get('remote_work', 50)  # % can work remote

        # Impact reduced by remote work capability
        operational_impact = infection_rate * (1 - remote_work_capability / 100) * 0.8
        financial_impact = operational_impact * 0.7

        recovery_days = int(duration_months * 30)

        recovery_plan = {
            'phases': [
                {'name': 'Immediate Response', 'duration_days': 14, 'actions': [
                    'Implement health protocols', 'Enable remote work',
                    'Communicate with staff', 'Assess business impact'
                ]},
                {'name': 'Adaptation', 'duration_days': 90, 'actions': [
                    'Optimize remote operations', 'Support affected staff',
                    'Adjust business model', 'Monitor health situation'
                ]},
                {'name': 'Recovery', 'duration_days': 180, 'actions': [
                    'Gradual return to office', 'Restore normal operations',
                    'Evaluate lessons learned', 'Update continuity plans'
                ]}
            ]
        }

        impact_score = (operational_impact + financial_impact) / 2

        return SimulationResult(
            twin_id=organization.twin_id, scenario=self.scenario_type, parameters=params,
            status=SimulationStatus.COMPLETED, impact_score=impact_score,
            financial_impact=financial_impact, operational_impact=operational_impact,
            recovery_time_days=recovery_days,
            timeline=self._build_timeline(duration_months, [
                {'description': 'Pandemic declared', 'impact': infection_rate},
                {'description': 'Remote work implemented', 'impact': operational_impact},
                {'description': 'Operations adapting', 'impact': operational_impact * 0.6},
                {'description': 'Gradual recovery', 'impact': operational_impact * 0.3},
                {'description': 'Normal operations resumed', 'impact': 0}
            ]),
            recommendations=['Develop remote work capabilities', 'Implement health protocols',
                           'Build flexible operations', 'Support employee wellbeing',
                           'Diversify supply chains', 'Maintain business continuity plans'],
            recovery_plan=recovery_plan, started_at=datetime.utcnow(),
            completed_at=datetime.utcnow(), duration_seconds=0.5
        )


class MarketShiftScenario(SimulationScenario):
    """Market Shift Scenario"""

    def __init__(self):
        super().__init__()
        self.scenario_type = SimulationScenarioType.MARKET_SHIFT

    async def run(self, organization: Organization, params: SimulationParameters) -> SimulationResult:
        logger.info(f"Running market shift simulation for {organization.name}")

        market_change = params.custom_params.get('market_change', 50)  # % market disruption
        adaptation_speed = params.custom_params.get('adaptation_speed', 'medium')  # slow/medium/fast
        duration_months = params.duration_months

        # Faster adaptation = less impact
        speed_factor = {'slow': 1.3, 'medium': 1.0, 'fast': 0.7}.get(adaptation_speed, 1.0)

        financial_impact = market_change * 0.7 * speed_factor
        operational_impact = market_change * 0.5 * speed_factor

        recovery_days = int(duration_months * 30 * speed_factor)

        recovery_plan = {
            'phases': [
                {'name': 'Market Analysis', 'duration_days': 30, 'actions': [
                    'Analyze market changes', 'Assess competitive landscape',
                    'Identify opportunities', 'Evaluate capabilities'
                ]},
                {'name': 'Strategy Pivot', 'duration_days': 60, 'actions': [
                    'Develop new strategy', 'Reallocate resources',
                    'Update offerings', 'Retrain staff'
                ]},
                {'name': 'Market Repositioning', 'duration_days': 90, 'actions': [
                    'Launch new products/services', 'Enter new markets',
                    'Build partnerships', 'Establish market position'
                ]}
            ]
        }

        impact_score = (financial_impact + operational_impact) / 2

        return SimulationResult(
            twin_id=organization.twin_id, scenario=self.scenario_type, parameters=params,
            status=SimulationStatus.COMPLETED, impact_score=impact_score,
            financial_impact=financial_impact, operational_impact=operational_impact,
            recovery_time_days=recovery_days,
            timeline=self._build_timeline(duration_months, [
                {'description': 'Market shift detected', 'impact': market_change},
                {'description': 'Strategy development', 'impact': market_change * 0.8},
                {'description': 'Business model adaptation', 'impact': market_change * 0.5},
                {'description': 'Market repositioning', 'impact': market_change * 0.3},
                {'description': 'New market position established', 'impact': 0}
            ]),
            recommendations=['Monitor market trends continuously', 'Build adaptable business model',
                           'Invest in innovation', 'Develop strategic partnerships',
                           'Maintain financial flexibility', 'Foster organizational agility'],
            recovery_plan=recovery_plan, started_at=datetime.utcnow(),
            completed_at=datetime.utcnow(), duration_seconds=0.5
        )


# ============================================
# SIMULATION ENGINE MANAGER
# ============================================

class SimulationEngine:
    """
    Main Simulation Engine

    Управляет всеми сценариями симуляций
    """

    def __init__(self):
        self.scenarios: Dict[SimulationScenarioType, SimulationScenario] = {
            SimulationScenarioType.FUNDING_SHOCK: FundingShockScenario(),
            SimulationScenarioType.STAFF_DISRUPTION: StaffDisruptionScenario(),
            SimulationScenarioType.SUPPLY_CHAIN_BREAK: SupplyChainBreakScenario(),
            SimulationScenarioType.CYBER_ATTACK: CyberAttackScenario(),
            SimulationScenarioType.REGULATORY_CHANGE: RegulatoryChangeScenario(),
            SimulationScenarioType.REPUTATION_CRISIS: ReputationCrisisScenario(),
            SimulationScenarioType.ECONOMIC_DOWNTURN: EconomicDownturnScenario(),
            SimulationScenarioType.NATURAL_DISASTER: NaturalDisasterScenario(),
            SimulationScenarioType.PANDEMIC: PandemicScenario(),
            SimulationScenarioType.MARKET_SHIFT: MarketShiftScenario(),
        }
        logger.info(f"Simulation Engine initialized with {len(self.scenarios)} scenarios")

    async def run_simulation(
        self,
        organization: Organization,
        params: SimulationParameters
    ) -> SimulationResult:
        """
        Run simulation for organization

        Args:
            organization: Organization digital twin
            params: Simulation parameters

        Returns:
            SimulationResult with complete analysis
        """
        scenario_type = params.scenario

        if scenario_type not in self.scenarios:
            raise ValueError(f"Unknown scenario: {scenario_type}")

        scenario = self.scenarios[scenario_type]

        logger.info(
            f"Running {scenario_type.value} simulation for {organization.name}"
        )

        try:
            result = await scenario.run(organization, params)
            logger.info(
                f"Simulation completed: impact={result.impact_score:.1f}, "
                f"recovery={result.recovery_time_days} days"
            )
            return result

        except Exception as e:
            logger.error(f"Simulation failed: {e}", exc_info=True)

            # Return failed result
            return SimulationResult(
                twin_id=organization.twin_id,
                scenario=scenario_type,
                parameters=params,
                status=SimulationStatus.FAILED,
                error_message=str(e)
            )

    def list_scenarios(self) -> List[Dict[str, Any]]:
        """List available scenarios"""
        return [
            {
                'type': scenario_type.value,
                'name': scenario.__class__.__name__,
                'description': scenario.__doc__ or ''
            }
            for scenario_type, scenario in self.scenarios.items()
        ]

    def get_scenario_info(self, scenario_type: SimulationScenarioType) -> Dict[str, Any]:
        """Get detailed info about specific scenario"""
        if scenario_type not in self.scenarios:
            raise ValueError(f"Unknown scenario: {scenario_type}")

        scenario = self.scenarios[scenario_type]
        return {
            'type': scenario_type.value,
            'name': scenario.__class__.__name__,
            'description': scenario.__doc__ or '',
            'parameters': self._get_scenario_parameters(scenario_type)
        }

    def _get_scenario_parameters(self, scenario_type: SimulationScenarioType) -> Dict[str, Any]:
        """Get default parameters for scenario"""
        defaults = {
            SimulationScenarioType.FUNDING_SHOCK: {
                'funding_drop_percent': 30,
                'duration_months': 6
            },
            SimulationScenarioType.STAFF_DISRUPTION: {
                'staff_loss_percent': 25,
                'duration_months': 4
            },
            # Add defaults for other scenarios
        }
        return defaults.get(scenario_type, {})
