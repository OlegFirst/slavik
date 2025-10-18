"""
Theory of Change (ToC) Engine
Implements causal graph optimization for impact measurement

Ported from: digital-twin-platform/src/theory-of-change-engine.js
Version: 2.0.0
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import numpy as np
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class Node:
    """ToC Graph Node (problem, mediator, outcome, impact)"""
    id: str
    type: str  # problem, mediator, outcome, impact
    label: str
    value: float = 0.0
    uncertainty: float = 0.1
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Edge:
    """Causal relationship between nodes"""
    from_node: str
    to_node: str
    strength: float = 0.5  # elasticity
    effect: str = "positive"  # positive or negative
    confidence: float = 0.8
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Intervention:
    """Policy intervention"""
    id: str
    label: str
    targets: List[str]  # Node IDs affected
    effect_size: float  # Impact per unit
    cost_per_unit: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Indicator:
    """Outcome indicator"""
    id: str
    node: str  # Node ID
    baseline: float
    target: float
    unit: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


class TheoryOfChangeEngine:
    """
    Theory of Change Engine for impact pathway modeling

    Features:
    - Causal graph modeling
    - Monte Carlo simulation
    - Policy optimization
    - Impact forecasting
    """

    def __init__(self):
        self.nodes: Dict[str, Node] = {}
        self.edges: List[Edge] = []
        self.interventions: List[Intervention] = []
        self.indicators: List[Indicator] = []

    def load_from_template(self, template: Dict[str, Any]) -> 'TheoryOfChangeEngine':
        """
        Load ToC from template dictionary

        Args:
            template: Dictionary with nodes, edges, interventions, indicators

        Returns:
            Self for chaining
        """
        # Parse nodes
        for node_data in template.get("nodes", []):
            node = Node(
                id=node_data["id"],
                type=node_data.get("type", "mediator"),
                label=node_data.get("label", node_data["id"]),
                value=node_data.get("value", 0.0),
                uncertainty=node_data.get("uncertainty", 0.1),
                metadata=node_data.get("metadata", {})
            )
            self.nodes[node.id] = node

        # Parse edges
        for edge_data in template.get("edges", []):
            edge = Edge(
                from_node=edge_data["from"],
                to_node=edge_data["to"],
                strength=edge_data.get("elasticity", edge_data.get("strength", 0.5)),
                effect=edge_data.get("effect", "positive"),
                confidence=edge_data.get("confidence", 0.8),
                metadata=edge_data.get("metadata", {})
            )
            self.edges.append(edge)

        # Parse interventions
        for intv_data in template.get("interventions", []):
            intervention = Intervention(
                id=intv_data["id"],
                label=intv_data.get("label", intv_data["id"]),
                targets=intv_data["targets"],
                effect_size=intv_data["effect_size"],
                cost_per_unit=intv_data["cost_per_unit"],
                metadata=intv_data.get("metadata", {})
            )
            self.interventions.append(intervention)

        # Parse indicators
        for ind_data in template.get("indicators", []):
            indicator = Indicator(
                id=ind_data["id"],
                node=ind_data["node"],
                baseline=ind_data["baseline"],
                target=ind_data["target"],
                unit=ind_data.get("unit", ""),
                metadata=ind_data.get("metadata", {})
            )
            self.indicators.append(indicator)

        logger.info(f"Loaded ToC: {len(self.nodes)} nodes, {len(self.edges)} edges, "
                    f"{len(self.interventions)} interventions, {len(self.indicators)} indicators")

        return self

    def run_monte_carlo(
        self,
        runs: int = 1000,
        intervention_intensities: Optional[Dict[str, float]] = None,
        budget: float = 50000
    ) -> Dict[str, Dict[str, float]]:
        """
        Run Monte Carlo simulation

        Args:
            runs: Number of Monte Carlo iterations
            intervention_intensities: Intervention intensity levels (0-N)
            budget: Budget constraint

        Returns:
            Aggregated results by indicator
        """
        if intervention_intensities is None:
            intervention_intensities = {}

        logger.info(f"Running Monte Carlo: {runs} iterations, budget=${budget:,.0f}")

        results = []

        for i in range(runs):
            # Create scenario with uncertainty
            scenario = self._create_scenario_with_uncertainty()

            # Apply interventions
            applied_interventions = self._apply_interventions(
                intervention_intensities,
                budget,
                scenario
            )

            # Propagate effects through causal graph
            outcomes = self._propagate_effects(scenario)

            results.append(outcomes)

        # Analyze aggregated results
        return self._analyze_results(results)

    def optimize_policy(
        self,
        objective: str = "maximize_outcome_per_cost",
        budget_cap: float = 50000,
        decision_variables: Optional[List[Dict[str, Any]]] = None,
        monte_carlo_runs: int = 1000
    ) -> Dict[str, Any]:
        """
        Optimize policy to maximize impact

        Args:
            objective: Optimization objective
            budget_cap: Maximum budget
            decision_variables: Variables to optimize over
            monte_carlo_runs: MC runs per policy evaluation

        Returns:
            Optimal policy and results
        """
        if decision_variables is None:
            decision_variables = []

        logger.info(f"Optimizing policy: objective={objective}, budget=${budget_cap:,.0f}")

        best_policy = None
        best_score = -np.inf

        # Generate policy space
        policies = self._generate_policy_space(decision_variables)

        logger.info(f"Evaluating {len(policies)} candidate policies...")

        for policy in policies:
            # Check budget constraint
            cost = self._calculate_policy_cost(policy)
            if cost > budget_cap:
                continue

            # Run simulation for this policy
            results = self.run_monte_carlo(
                runs=monte_carlo_runs,
                intervention_intensities=policy,
                budget=budget_cap
            )

            # Calculate objective score
            score = self._calculate_objective(results, cost, objective)

            if score > best_score:
                best_score = score
                best_policy = {
                    "policy": policy,
                    "results": results,
                    "cost": cost,
                    "score": score
                }

        return self._format_optimization_result(best_policy)

    def _create_scenario_with_uncertainty(self) -> Dict[str, Any]:
        """Create scenario with stochastic uncertainty"""
        scenario = {
            "nodes": {},
            "edges": []
        }

        # Add noise to node values
        for node_id, node in self.nodes.items():
            scenario["nodes"][node_id] = Node(
                id=node.id,
                type=node.type,
                label=node.label,
                value=node.value + self._gaussian_random() * node.uncertainty,
                uncertainty=node.uncertainty,
                metadata=node.metadata
            )

        # Add noise to edge strengths
        for edge in self.edges:
            noisy_edge = Edge(
                from_node=edge.from_node,
                to_node=edge.to_node,
                strength=edge.strength + self._gaussian_random() * 0.1,
                effect=edge.effect,
                confidence=edge.confidence,
                metadata=edge.metadata
            )
            scenario["edges"].append(noisy_edge)

        return scenario

    def _apply_interventions(
        self,
        intensities: Dict[str, float],
        budget: float,
        scenario: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Apply interventions to scenario"""
        applied = []
        total_cost = 0.0

        for intervention in self.interventions:
            intensity = intensities.get(intervention.id, 0.0)
            if intensity == 0:
                continue

            cost = intervention.cost_per_unit * intensity
            if total_cost + cost > budget:
                continue

            # Apply effect to target nodes
            for target_id in intervention.targets:
                if target_id in scenario["nodes"]:
                    node = scenario["nodes"][target_id]
                    node.value += intervention.effect_size * intensity

            applied.append({
                "intervention": intervention.id,
                "intensity": intensity,
                "cost": cost
            })

            total_cost += cost

        return applied

    def _propagate_effects(self, scenario: Dict[str, Any]) -> Dict[str, Dict[str, float]]:
        """Propagate effects through causal graph"""
        iterations = 10  # Convergence iterations

        # Iterative propagation
        for _ in range(iterations):
            for edge in scenario["edges"]:
                from_node = scenario["nodes"].get(edge.from_node)
                to_node = scenario["nodes"].get(edge.to_node)

                if from_node and to_node:
                    effect = from_node.value * edge.strength
                    multiplier = 1.0 if edge.effect == "positive" else -1.0
                    to_node.value += effect * multiplier

        # Extract outcome values
        outcomes = {}
        for indicator in self.indicators:
            node = scenario["nodes"].get(indicator.node)
            if node:
                achievement = (node.value - indicator.baseline) / \
                              (indicator.target - indicator.baseline) if indicator.target != indicator.baseline else 0

                outcomes[indicator.id] = {
                    "value": node.value,
                    "baseline": indicator.baseline,
                    "target": indicator.target,
                    "achievement": achievement
                }

        return outcomes

    def _analyze_results(self, results: List[Dict[str, Dict[str, float]]]) -> Dict[str, Dict[str, float]]:
        """Analyze Monte Carlo results"""
        aggregated = {}

        if not results:
            return aggregated

        # Get all outcome keys
        outcome_keys = list(results[0].keys())

        for key in outcome_keys:
            values = [r[key]["value"] for r in results]
            values_sorted = sorted(values)

            achievements = [r[key]["achievement"] for r in results]

            aggregated[key] = {
                "mean": float(np.mean(values)),
                "median": float(np.median(values)),
                "p10": float(np.percentile(values, 10)),
                "p90": float(np.percentile(values, 90)),
                "confidence": self._calculate_confidence(values),
                "achievement": float(np.mean(achievements))
            }

        return aggregated

    def _generate_policy_space(self, variables: List[Dict[str, Any]]) -> List[Dict[str, float]]:
        """Generate policy space for optimization"""
        if not variables:
            return [{}]

        policies = []

        def generate_combinations(index: int = 0, current: Optional[Dict[str, float]] = None):
            if current is None:
                current = {}

            if index >= len(variables):
                policies.append(current.copy())
                return

            variable = variables[index]
            min_val = variable.get("min", 0)
            max_val = variable.get("max", 2)
            step = variable.get("step", 0.5)

            val = min_val
            while val <= max_val:
                current[variable["id"]] = val
                generate_combinations(index + 1, current)
                val += step

        generate_combinations()

        # Limit to reasonable number (random sampling if too many)
        if len(policies) > 1000:
            indices = np.random.choice(len(policies), 1000, replace=False)
            policies = [policies[i] for i in indices]

        logger.info(f"Generated {len(policies)} candidate policies")

        return policies

    def _calculate_policy_cost(self, policy: Dict[str, float]) -> float:
        """Calculate total cost of a policy"""
        total_cost = 0.0

        for intervention in self.interventions:
            intensity = policy.get(intervention.id, 0.0)
            total_cost += intervention.cost_per_unit * intensity

        return total_cost

    def _calculate_objective(self, results: Dict[str, Dict[str, float]], cost: float, objective: str) -> float:
        """Calculate objective function value"""
        # Get primary outcome (first indicator or 'cov')
        primary_key = list(results.keys())[0] if results else "cov"
        outcome_value = results.get(primary_key, {}).get("mean", 0.0)

        if objective == "maximize_outcome_per_cost":
            return outcome_value / (cost / 10000 + 1)  # Normalize cost

        elif objective == "maximize_coverage":
            return outcome_value

        elif objective == "minimize_cost_per_beneficiary":
            beneficiaries = outcome_value * 100000  # Assume 100k population
            return beneficiaries / (cost + 1)

        elif objective == "maximize_net_monetary_benefit":
            benefit = outcome_value * 100000  # Value per coverage point
            return benefit - cost

        else:
            return outcome_value

    def _format_optimization_result(self, best_policy: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Format optimization result"""
        if not best_policy:
            return {
                "error": "No feasible policy found within budget constraints"
            }

        policy = best_policy["policy"]
        results = best_policy["results"]
        cost = best_policy["cost"]
        score = best_policy["score"]

        # Format policy intensities
        formatted_policy = {
            k.replace("_intensity", ""): round(v, 1)
            for k, v in policy.items()
        }

        # Get primary outcome
        primary_key = list(results.keys())[0] if results else "cov"
        primary_result = results.get(primary_key, {})

        return {
            "policy": formatted_policy,
            "coverage_forecast": {
                "mean": round(primary_result.get("mean", 0), 2),
                "p10": round(primary_result.get("p10", 0), 2),
                "p90": round(primary_result.get("p90", 0), 2)
            },
            "cost": round(cost),
            "nmb": round(score / 100, 2),  # Net Monetary Benefit
            "confidence": round(primary_result.get("confidence", 0), 2),
            "achievement_probability": f"{round(primary_result.get('achievement', 0) * 100)}%",
            "assumptions": [
                "Elasticities stable within pilot range",
                "No negative spillover effects",
                "Linear cost scaling"
            ],
            "recommendations": self._generate_recommendations(policy, results)
        }

    def _generate_recommendations(
        self,
        policy: Dict[str, float],
        results: Dict[str, Dict[str, float]]
    ) -> List[Dict[str, str]]:
        """Generate actionable recommendations"""
        recommendations = []

        # High intensity interventions
        for key, value in policy.items():
            if value > 1.5:
                recommendations.append({
                    "priority": "HIGH",
                    "intervention": key,
                    "action": f"Scale up {key} to {value:.1f}x current level",
                    "rationale": "High impact on outcome achievement"
                })

        # Low confidence areas
        primary_key = list(results.keys())[0] if results else "cov"
        confidence = results.get(primary_key, {}).get("confidence", 1.0)

        if confidence < 0.7:
            recommendations.append({
                "priority": "MEDIUM",
                "intervention": "data_collection",
                "action": "Improve measurement systems",
                "rationale": "Low confidence in current estimates"
            })

        # Achievement gap
        achievement = results.get(primary_key, {}).get("achievement", 1.0)

        if achievement < 0.8:
            recommendations.append({
                "priority": "HIGH",
                "intervention": "review",
                "action": "Review Theory of Change assumptions",
                "rationale": "Target achievement below 80%"
            })

        return recommendations

    # Utility functions

    @staticmethod
    def _gaussian_random() -> float:
        """Box-Muller transform for Gaussian random numbers"""
        u1 = np.random.random()
        u2 = np.random.random()
        return np.sqrt(-2.0 * np.log(u1)) * np.cos(2.0 * np.pi * u2)

    @staticmethod
    def _calculate_confidence(values: List[float]) -> float:
        """Calculate confidence score (0-1)"""
        if not values:
            return 0.0

        mean = np.mean(values)
        if mean == 0:
            return 0.0

        std = np.std(values)
        cv = std / abs(mean)  # Coefficient of variation

        # Lower CV = higher confidence
        return max(0.0, min(1.0, 1.0 - cv))
