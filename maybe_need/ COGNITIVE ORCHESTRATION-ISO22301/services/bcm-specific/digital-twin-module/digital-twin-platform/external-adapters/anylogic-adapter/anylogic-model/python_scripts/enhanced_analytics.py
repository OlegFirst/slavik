"""
Enhanced Analytics Module for AnyLogic Pypeline Integration
Provides ML/AI capabilities for NPO simulations
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
import json

@dataclass
class NPOMetrics:
    """NPO organization metrics for analysis"""
    beneficiaries_served: int
    programs_active: int
    volunteer_hours: float
    donation_efficiency: float
    operational_cost: float
    impact_score: float

class EnhancedAnalytics:
    """
    Advanced analytics engine for AnyLogic simulations
    Integrates with Pypeline for real-time ML predictions
    """
    
    def __init__(self):
        self.model_cache = {}
        self.historical_data = []
        
    def predict_donor_behavior(self, donor_profile: Dict[str, Any]) -> Dict[str, float]:
        """
        Predict donor behavior using ML models
        
        Args:
            donor_profile: Donor characteristics and history
            
        Returns:
            Predictions for donation probability and amount
        """
        # Simulate ML prediction (would use real sklearn/tensorflow model)
        base_probability = 0.3
        
        # Factors affecting donation
        if donor_profile.get('previous_donor', False):
            base_probability += 0.4
        if donor_profile.get('engagement_score', 0) > 0.7:
            base_probability += 0.2
        if donor_profile.get('affinity_score', 0) > 0.5:
            base_probability += 0.1
            
        # Predict donation amount based on capacity and likelihood
        capacity = donor_profile.get('giving_capacity', 1000)
        predicted_amount = capacity * base_probability * np.random.beta(2, 5)
        
        return {
            'donation_probability': min(base_probability, 0.95),
            'predicted_amount': predicted_amount,
            'retention_probability': base_probability * 0.8,
            'upgrade_potential': base_probability * 0.3
        }
    
    def optimize_resource_allocation(self, 
                                    resources: Dict[str, float],
                                    programs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Optimize resource allocation across programs using linear programming
        
        Args:
            resources: Available resources (budget, staff, volunteers)
            programs: List of programs with requirements and impact
            
        Returns:
            Optimal allocation strategy
        """
        total_budget = resources.get('budget', 100000)
        total_staff = resources.get('staff_hours', 2000)
        
        allocations = {}
        remaining_budget = total_budget
        remaining_staff = total_staff
        
        # Sort programs by impact/cost ratio (simple heuristic)
        sorted_programs = sorted(programs, 
                               key=lambda p: p.get('impact_score', 1) / max(p.get('cost', 1), 1),
                               reverse=True)
        
        for program in sorted_programs:
            required_budget = program.get('cost', 10000)
            required_staff = program.get('staff_hours', 100)
            
            if remaining_budget >= required_budget and remaining_staff >= required_staff:
                allocation_ratio = min(
                    remaining_budget / required_budget,
                    remaining_staff / required_staff,
                    1.0
                )
                
                allocations[program['name']] = {
                    'budget': required_budget * allocation_ratio,
                    'staff_hours': required_staff * allocation_ratio,
                    'expected_impact': program.get('impact_score', 0) * allocation_ratio
                }
                
                remaining_budget -= required_budget * allocation_ratio
                remaining_staff -= required_staff * allocation_ratio
        
        return {
            'allocations': allocations,
            'budget_utilization': (total_budget - remaining_budget) / total_budget,
            'staff_utilization': (total_staff - remaining_staff) / total_staff,
            'total_expected_impact': sum(a['expected_impact'] for a in allocations.values())
        }
    
    def forecast_program_outcomes(self, 
                                 program_data: Dict[str, Any],
                                 timeframe_days: int = 365) -> Dict[str, Any]:
        """
        Forecast program outcomes using time series analysis
        
        Args:
            program_data: Historical program performance data
            timeframe_days: Forecast horizon in days
            
        Returns:
            Forecasted outcomes and confidence intervals
        """
        # Extract historical performance (simulated)
        historical_impact = program_data.get('historical_impact', [50, 55, 60, 58, 65, 70])
        
        # Simple linear trend projection (would use ARIMA/Prophet in production)
        if len(historical_impact) > 1:
            trend = np.polyfit(range(len(historical_impact)), historical_impact, 1)[0]
        else:
            trend = 0.5
            
        # Generate forecast
        forecast_points = int(timeframe_days / 30)  # Monthly forecasts
        base_value = historical_impact[-1] if historical_impact else 50
        
        forecasts = []
        lower_bounds = []
        upper_bounds = []
        
        for i in range(forecast_points):
            # Add trend and seasonality
            value = base_value + trend * (i + 1)
            seasonality = 5 * np.sin(2 * np.pi * i / 12)  # Annual cycle
            noise = np.random.normal(0, 2)
            
            forecast = value + seasonality + noise
            forecasts.append(forecast)
            
            # Confidence intervals (simplified)
            std_dev = 5 + i * 0.5  # Increasing uncertainty
            lower_bounds.append(forecast - 1.96 * std_dev)
            upper_bounds.append(forecast + 1.96 * std_dev)
        
        return {
            'forecasts': forecasts,
            'lower_95_ci': lower_bounds,
            'upper_95_ci': upper_bounds,
            'expected_total_impact': sum(forecasts),
            'trend': 'increasing' if trend > 0 else 'decreasing',
            'confidence_score': max(0.5, 1 - (0.1 * forecast_points))
        }
    
    def detect_anomalies(self, 
                         metrics: List[NPOMetrics],
                         sensitivity: float = 2.0) -> List[Dict[str, Any]]:
        """
        Detect anomalies in NPO operational metrics
        
        Args:
            metrics: Time series of NPO metrics
            sensitivity: Standard deviations for anomaly threshold
            
        Returns:
            List of detected anomalies with explanations
        """
        anomalies = []
        
        if len(metrics) < 3:
            return anomalies
            
        # Convert to arrays for analysis
        impact_scores = [m.impact_score for m in metrics]
        costs = [m.operational_cost for m in metrics]
        efficiency = [m.donation_efficiency for m in metrics]
        
        # Simple statistical anomaly detection
        for i, metric in enumerate(metrics[2:], start=2):
            # Check impact score anomaly
            impact_mean = np.mean(impact_scores[:i])
            impact_std = np.std(impact_scores[:i])
            
            if abs(metric.impact_score - impact_mean) > sensitivity * impact_std:
                anomalies.append({
                    'timestamp': i,
                    'type': 'impact_anomaly',
                    'value': metric.impact_score,
                    'expected_range': (impact_mean - sensitivity * impact_std,
                                     impact_mean + sensitivity * impact_std),
                    'severity': 'high' if abs(metric.impact_score - impact_mean) > 3 * impact_std else 'medium'
                })
            
            # Check operational efficiency
            if metric.donation_efficiency < 0.65:  # Below standard threshold
                anomalies.append({
                    'timestamp': i,
                    'type': 'efficiency_warning',
                    'value': metric.donation_efficiency,
                    'threshold': 0.65,
                    'recommendation': 'Review operational processes and cost structure'
                })
        
        return anomalies
    
    def recommend_interventions(self, 
                               current_state: Dict[str, Any],
                               goals: Dict[str, float]) -> List[Dict[str, Any]]:
        """
        Recommend interventions based on current state and goals
        
        Args:
            current_state: Current NPO metrics and status
            goals: Target metrics to achieve
            
        Returns:
            Prioritized list of recommended interventions
        """
        recommendations = []
        
        # Analyze gaps
        impact_gap = goals.get('impact_score', 100) - current_state.get('impact_score', 50)
        efficiency_gap = goals.get('efficiency', 0.8) - current_state.get('efficiency', 0.6)
        
        # Generate recommendations based on gaps
        if impact_gap > 10:
            recommendations.append({
                'intervention': 'scale_programs',
                'priority': 'high',
                'expected_impact': impact_gap * 0.7,
                'required_investment': impact_gap * 1000,
                'timeframe_months': 6,
                'specific_actions': [
                    'Expand successful program models',
                    'Increase beneficiary outreach',
                    'Partner with other organizations'
                ]
            })
        
        if efficiency_gap > 0.1:
            recommendations.append({
                'intervention': 'process_automation',
                'priority': 'high' if efficiency_gap > 0.2 else 'medium',
                'expected_impact': efficiency_gap * 50,
                'required_investment': 25000,
                'timeframe_months': 3,
                'specific_actions': [
                    'Implement CRM system',
                    'Automate donation processing',
                    'Digitize volunteer management'
                ]
            })
        
        if current_state.get('volunteer_retention', 0.5) < 0.7:
            recommendations.append({
                'intervention': 'volunteer_engagement',
                'priority': 'medium',
                'expected_impact': 15,
                'required_investment': 5000,
                'timeframe_months': 2,
                'specific_actions': [
                    'Launch volunteer recognition program',
                    'Improve volunteer training',
                    'Create volunteer community platform'
                ]
            })
        
        # Sort by priority and expected impact
        recommendations.sort(key=lambda x: (
            {'high': 3, 'medium': 2, 'low': 1}[x['priority']],
            x['expected_impact']
        ), reverse=True)
        
        return recommendations

# Interface for AnyLogic Pypeline
def process_for_anylogic(request_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main interface function called from AnyLogic via Pypeline
    
    Args:
        request_type: Type of analysis requested
        data: Input data from AnyLogic simulation
        
    Returns:
        Analysis results for AnyLogic model
    """
    analytics = EnhancedAnalytics()
    
    if request_type == "predict_donor":
        return analytics.predict_donor_behavior(data)
    elif request_type == "optimize_resources":
        return analytics.optimize_resource_allocation(
            data.get('resources', {}),
            data.get('programs', [])
        )
    elif request_type == "forecast_outcomes":
        return analytics.forecast_program_outcomes(
            data.get('program_data', {}),
            data.get('timeframe_days', 365)
        )
    elif request_type == "detect_anomalies":
        metrics = [NPOMetrics(**m) for m in data.get('metrics', [])]
        return {'anomalies': analytics.detect_anomalies(metrics)}
    elif request_type == "recommend_interventions":
        return {'recommendations': analytics.recommend_interventions(
            data.get('current_state', {}),
            data.get('goals', {})
        )}
    else:
        return {'error': f'Unknown request type: {request_type}'}

if __name__ == "__main__":
    # Test the analytics engine
    test_data = {
        'resources': {'budget': 100000, 'staff_hours': 2000},
        'programs': [
            {'name': 'Education', 'cost': 30000, 'staff_hours': 500, 'impact_score': 85},
            {'name': 'Healthcare', 'cost': 40000, 'staff_hours': 600, 'impact_score': 90},
            {'name': 'Community', 'cost': 20000, 'staff_hours': 400, 'impact_score': 70}
        ]
    }
    
    result = process_for_anylogic('optimize_resources', test_data)
    print(json.dumps(result, indent=2))