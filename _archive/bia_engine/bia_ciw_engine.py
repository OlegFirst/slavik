"""
BCM Platform - BIA Engine with Ciw Integration
Business Impact Analysis using Queue Theory and ML

Ciw is used for simulating business process queues and analyzing impact
"""

import ciw
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BCMQueueSimulator:
    """
    Simulates business processes as queuing systems using Ciw
    to analyze impact of disruptions
    """
    
    def __init__(self):
        self.simulation_results = []
        self.process_networks = {}
        
    def create_business_process_network(
        self,
        process_name: str,
        arrival_rate: float,
        service_rate: float,
        num_servers: int = 1,
        max_capacity: int = None
    ) -> ciw.Network:
        """
        Create a queuing network for a business process
        
        Args:
            process_name: Name of business process
            arrival_rate: Average arrival rate (Lambda)
            service_rate: Average service rate (Mu)
            num_servers: Number of servers/workers
            max_capacity: Maximum queue capacity
        """
        
        network = ciw.create_network(
            arrival_distributions=[ciw.dists.Exponential(arrival_rate)],
            service_distributions=[ciw.dists.Exponential(service_rate)],
            number_of_servers=[num_servers],
            routing=[[0.0]]  # Single node network
        )
        
        self.process_networks[process_name] = {
            'network': network,
            'arrival_rate': arrival_rate,
            'service_rate': service_rate,
            'num_servers': num_servers,
            'max_capacity': max_capacity
        }
        
        logger.info(f"Created queuing network for process: {process_name}")
        return network
    
    def simulate_process_disruption(
        self,
        process_name: str,
        disruption_duration_hours: float,
        disruption_severity: float = 0.5,
        simulation_time: float = 168  # 1 week in hours
    ) -> Dict[str, Any]:
        """
        Simulate impact of disruption on business process
        
        Args:
            process_name: Name of process to disrupt
            disruption_duration_hours: How long disruption lasts
            disruption_severity: 0-1, where 1 is complete failure
            simulation_time: Total simulation time in hours
        """
        
        if process_name not in self.process_networks:
            raise ValueError(f"Process {process_name} not found")
        
        process_config = self.process_networks[process_name]
        
        # Normal operation simulation
        normal_sim = ciw.Simulation(process_config['network'])
        normal_sim.simulate_until_max_time(simulation_time)
        normal_records = normal_sim.get_all_records()
        
        # Disrupted operation - reduce service rate
        disrupted_service_rate = process_config['service_rate'] * (1 - disruption_severity)
        disrupted_network = ciw.create_network(
            arrival_distributions=[ciw.dists.Exponential(process_config['arrival_rate'])],
            service_distributions=[ciw.dists.Exponential(disrupted_service_rate)],
            number_of_servers=[process_config['num_servers']],
            routing=[[0.0]]
        )
        
        disrupted_sim = ciw.Simulation(disrupted_network)
        disrupted_sim.simulate_until_max_time(disruption_duration_hours)
        disrupted_records = disrupted_sim.get_all_records()
        
        # Analyze impact
        impact_analysis = self._analyze_disruption_impact(
            normal_records,
            disrupted_records,
            disruption_duration_hours
        )
        
        impact_analysis['process_name'] = process_name
        impact_analysis['disruption_severity'] = disruption_severity
        impact_analysis['disruption_duration'] = disruption_duration_hours
        
        return impact_analysis
    
    def _analyze_disruption_impact(
        self,
        normal_records: List,
        disrupted_records: List,
        disruption_hours: float
    ) -> Dict[str, Any]:
        """Analyze the impact of disruption on process performance"""
        
        def calculate_metrics(records):
            if not records:
                return {
                    'avg_wait_time': 0,
                    'avg_service_time': 0,
                    'throughput': 0,
                    'queue_length': 0,
                    'utilization': 0
                }
            
            wait_times = [r.waiting_time for r in records if hasattr(r, 'waiting_time')]
            service_times = [r.service_time for r in records if hasattr(r, 'service_time')]
            
            return {
                'avg_wait_time': np.mean(wait_times) if wait_times else 0,
                'avg_service_time': np.mean(service_times) if service_times else 0,
                'throughput': len(records) / disruption_hours if disruption_hours > 0 else 0,
                'queue_length': np.mean([r.queue_size_at_arrival for r in records 
                                        if hasattr(r, 'queue_size_at_arrival')]),
                'utilization': len(service_times) / (disruption_hours * 60) if disruption_hours > 0 else 0
            }
        
        normal_metrics = calculate_metrics(normal_records)
        disrupted_metrics = calculate_metrics(disrupted_records)
        
        # Calculate impact percentages
        impact = {
            'wait_time_increase_pct': ((disrupted_metrics['avg_wait_time'] - 
                                       normal_metrics['avg_wait_time']) / 
                                      max(normal_metrics['avg_wait_time'], 0.01) * 100),
            'throughput_decrease_pct': ((normal_metrics['throughput'] - 
                                        disrupted_metrics['throughput']) / 
                                       max(normal_metrics['throughput'], 0.01) * 100),
            'queue_length_increase': disrupted_metrics['queue_length'] - 
                                    normal_metrics['queue_length'],
            'normal_metrics': normal_metrics,
            'disrupted_metrics': disrupted_metrics
        }
        
        return impact
    
    def calculate_rto_rpo_optimal(
        self,
        process_name: str,
        max_acceptable_wait: float,
        max_data_loss_hours: float
    ) -> Dict[str, float]:
        """
        Calculate optimal RTO/RPO based on queue theory
        
        Args:
            process_name: Name of business process
            max_acceptable_wait: Maximum acceptable customer wait time
            max_data_loss_hours: Maximum acceptable data loss in hours
        """
        
        if process_name not in self.process_networks:
            raise ValueError(f"Process {process_name} not found")
        
        config = self.process_networks[process_name]
        
        # Using Little's Law: L = λW
        # Where L = avg number in system, λ = arrival rate, W = avg time in system
        arrival_rate = config['arrival_rate']
        service_rate = config['service_rate']
        num_servers = config['num_servers']
        
        # Calculate utilization (ρ = λ / (c * μ))
        utilization = arrival_rate / (num_servers * service_rate)
        
        if utilization >= 1:
            # System is unstable
            logger.warning(f"Process {process_name} has unstable queue (utilization >= 1)")
            rto = max_acceptable_wait * 0.5  # Conservative estimate
            rpo = max_data_loss_hours * 0.5
        else:
            # M/M/c queue formulas
            # Average wait time in queue
            avg_wait = self._calculate_mm_c_wait_time(
                arrival_rate, service_rate, num_servers
            )
            
            # RTO based on queue recovery time
            rto = min(avg_wait * 2, max_acceptable_wait)
            
            # RPO based on transaction rate
            transactions_per_hour = arrival_rate * 60
            rpo = min(max_data_loss_hours, 1 / transactions_per_hour)
        
        return {
            'optimal_rto_hours': round(rto, 2),
            'optimal_rpo_hours': round(rpo, 4),
            'utilization': round(utilization, 2),
            'stability': 'stable' if utilization < 1 else 'unstable',
            'recommendations': self._generate_rto_rpo_recommendations(rto, rpo, utilization)
        }
    
    def _calculate_mm_c_wait_time(self, λ: float, μ: float, c: int) -> float:
        """Calculate average wait time for M/M/c queue"""
        ρ = λ / (c * μ)
        
        if ρ >= 1:
            return float('inf')
        
        # Erlang C formula for probability of waiting
        sum_terms = sum([(c * ρ) ** n / np.math.factorial(n) for n in range(c)])
        p0 = 1 / (sum_terms + (c * ρ) ** c / (np.math.factorial(c) * (1 - ρ)))
        
        pc = ((c * ρ) ** c / np.math.factorial(c)) * p0
        pw = pc / (1 - ρ)
        
        # Average wait time
        w = pw / (c * μ - λ)
        
        return w
    
    def _generate_rto_rpo_recommendations(
        self,
        rto: float,
        rpo: float,
        utilization: float
    ) -> List[str]:
        """Generate recommendations based on RTO/RPO analysis"""
        
        recommendations = []
        
        if rto < 1:
            recommendations.append("Critical process requires hot standby or active-active configuration")
        elif rto < 4:
            recommendations.append("Implement warm standby with automated failover")
        elif rto < 24:
            recommendations.append("Cold standby with documented recovery procedures sufficient")
        else:
            recommendations.append("Manual recovery procedures acceptable")
        
        if rpo < 0.1:
            recommendations.append("Implement synchronous replication")
        elif rpo < 1:
            recommendations.append("Use asynchronous replication with short intervals")
        else:
            recommendations.append("Daily backups may be sufficient")
        
        if utilization > 0.8:
            recommendations.append("System operating near capacity - consider scaling")
        elif utilization > 0.6:
            recommendations.append("System has moderate load - monitor for growth")
        
        return recommendations


class AdvancedBIAEngine:
    """
    Advanced Business Impact Analysis Engine combining Ciw queue simulation
    with financial modeling and ML predictions
    """
    
    def __init__(self):
        self.queue_simulator = BCMQueueSimulator()
        self.financial_impacts = {}
        self.ml_models = {}
        
    def comprehensive_bia_analysis(
        self,
        business_process: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Perform comprehensive BIA analysis combining queue theory,
        financial impact, and ML predictions
        """
        
        process_name = business_process['name']
        
        # 1. Queue Theory Analysis
        self.queue_simulator.create_business_process_network(
            process_name=process_name,
            arrival_rate=business_process.get('arrival_rate', 10),
            service_rate=business_process.get('service_rate', 12),
            num_servers=business_process.get('num_servers', 2)
        )
        
        # 2. Simulate various disruption scenarios
        disruption_scenarios = [
            {'duration': 1, 'severity': 0.3},   # Minor 1-hour disruption
            {'duration': 4, 'severity': 0.5},   # Moderate 4-hour disruption
            {'duration': 24, 'severity': 0.8},  # Major 1-day disruption
            {'duration': 72, 'severity': 1.0},  # Complete 3-day failure
        ]
        
        scenario_impacts = []
        for scenario in disruption_scenarios:
            impact = self.queue_simulator.simulate_process_disruption(
                process_name,
                scenario['duration'],
                scenario['severity']
            )
            
            # 3. Calculate financial impact
            financial_impact = self._calculate_financial_impact(
                impact,
                business_process.get('revenue_per_hour', 10000),
                business_process.get('cost_per_hour', 5000)
            )
            
            impact['financial_impact'] = financial_impact
            scenario_impacts.append(impact)
        
        # 4. Calculate optimal RTO/RPO
        rto_rpo = self.queue_simulator.calculate_rto_rpo_optimal(
            process_name,
            max_acceptable_wait=business_process.get('max_wait_hours', 2),
            max_data_loss_hours=business_process.get('max_data_loss', 1)
        )
        
        # 5. Generate comprehensive report
        return {
            'process_name': process_name,
            'criticality_score': self._calculate_criticality_score(scenario_impacts),
            'scenario_impacts': scenario_impacts,
            'rto_rpo_analysis': rto_rpo,
            'financial_summary': self._summarize_financial_impacts(scenario_impacts),
            'recommendations': self._generate_bia_recommendations(
                scenario_impacts,
                rto_rpo,
                business_process
            ),
            'analysis_timestamp': datetime.now().isoformat()
        }
    
    def _calculate_financial_impact(
        self,
        operational_impact: Dict,
        revenue_per_hour: float,
        cost_per_hour: float
    ) -> Dict[str, float]:
        """Calculate financial impact of disruption"""
        
        throughput_loss = operational_impact.get('throughput_decrease_pct', 0) / 100
        duration = operational_impact.get('disruption_duration', 0)
        
        # Direct revenue loss
        revenue_loss = revenue_per_hour * throughput_loss * duration
        
        # Additional costs (overtime, recovery, reputation)
        recovery_cost = cost_per_hour * duration * 1.5  # 50% premium for recovery
        reputation_cost = revenue_loss * 0.2  # 20% of revenue loss as reputation damage
        
        # Customer compensation (based on wait time increase)
        wait_increase = operational_impact.get('disrupted_metrics', {}).get('avg_wait_time', 0)
        compensation_cost = wait_increase * 100 * duration  # $100 per hour of excess wait
        
        total_impact = revenue_loss + recovery_cost + reputation_cost + compensation_cost
        
        return {
            'revenue_loss': round(revenue_loss, 2),
            'recovery_cost': round(recovery_cost, 2),
            'reputation_cost': round(reputation_cost, 2),
            'compensation_cost': round(compensation_cost, 2),
            'total_impact': round(total_impact, 2)
        }
    
    def _calculate_criticality_score(self, scenario_impacts: List[Dict]) -> float:
        """Calculate overall criticality score for the process"""
        
        # Weighted average based on scenario likelihood
        weights = [0.4, 0.3, 0.2, 0.1]  # Higher weight for more likely scenarios
        
        total_score = 0
        for impact, weight in zip(scenario_impacts, weights):
            financial = impact.get('financial_impact', {}).get('total_impact', 0)
            normalized_impact = min(financial / 1000000, 10)  # Normalize to 0-10 scale
            total_score += normalized_impact * weight
        
        return round(total_score, 2)
    
    def _summarize_financial_impacts(self, scenario_impacts: List[Dict]) -> Dict:
        """Summarize financial impacts across all scenarios"""
        
        total_impacts = [s.get('financial_impact', {}).get('total_impact', 0) 
                        for s in scenario_impacts]
        
        return {
            'min_impact': round(min(total_impacts), 2),
            'max_impact': round(max(total_impacts), 2),
            'avg_impact': round(np.mean(total_impacts), 2),
            'total_exposure': round(sum(total_impacts), 2)
        }
    
    def _generate_bia_recommendations(
        self,
        scenario_impacts: List[Dict],
        rto_rpo: Dict,
        business_process: Dict
    ) -> List[str]:
        """Generate comprehensive BIA recommendations"""
        
        recommendations = []
        
        # Add RTO/RPO recommendations
        recommendations.extend(rto_rpo.get('recommendations', []))
        
        # Financial impact recommendations
        max_impact = max([s.get('financial_impact', {}).get('total_impact', 0) 
                         for s in scenario_impacts])
        
        if max_impact > 1000000:
            recommendations.append("Critical financial exposure - implement comprehensive BCM program")
        elif max_impact > 100000:
            recommendations.append("Significant financial risk - develop detailed recovery procedures")
        
        # Operational recommendations
        for impact in scenario_impacts:
            if impact.get('wait_time_increase_pct', 0) > 200:
                recommendations.append("Implement queue management and overflow procedures")
                break
        
        return list(set(recommendations))  # Remove duplicates


# Integration with existing BIA Engine
def enhance_bia_engine_with_ciw(existing_bia_engine):
    """
    Enhance existing BIA engine with Ciw queue simulation capabilities
    """
    advanced_engine = AdvancedBIAEngine()
    
    # Merge capabilities
    existing_bia_engine.queue_simulator = advanced_engine.queue_simulator
    existing_bia_engine.comprehensive_bia = advanced_engine.comprehensive_bia_analysis
    
    logger.info("BIA Engine enhanced with Ciw queue simulation capabilities")
    return existing_bia_engine
