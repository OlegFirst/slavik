"""
Monte Carlo Engine for Advanced Probabilistic Simulations

Provides probabilistic forecasting with thousands of iterations,
multiple distribution types, sensitivity analysis, and convergence detection.
"""

import logging
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class MonteCarloResult:
    """Monte Carlo simulation result with full probability distribution"""
    mean: float                    # Среднее значение
    median: float                  # Медиана
    std_dev: float                 # Стандартное отклонение
    percentile_5: float            # 5-й перцентиль (worst case)
    percentile_25: float           # 25-й перцентиль
    percentile_75: float           # 75-й перцентиль
    percentile_95: float           # 95-й перцентиль (best case)
    confidence_interval_95: Tuple[float, float]  # 95% доверительный интервал
    distribution: List[float]      # Полное распределение результатов (для viz)
    iterations: int                # Количество итераций
    convergence_reached: bool      # Достигнута ли сходимость


class MonteCarloEngine:
    """
    Advanced Monte Carlo simulation engine

    Features:
    - Probabilistic forecasting with thousands of iterations
    - Multiple distribution types (normal, lognormal, uniform, triangular)
    - Correlation between variables
    - Sensitivity analysis
    - Convergence detection
    """

    def __init__(self, n_iterations: int = 10000, random_seed: Optional[int] = None):
        """
        Initialize Monte Carlo engine

        Args:
            n_iterations: Number of Monte Carlo iterations (default: 10,000)
            random_seed: Random seed for reproducibility
        """
        self.n_iterations = n_iterations
        if random_seed:
            np.random.seed(random_seed)

        logger.info(f"Monte Carlo Engine initialized with {n_iterations} iterations")

    async def simulate_financial_forecast(
        self,
        current_value: float,
        mean_growth_rate: float,         # Средний рост (0.05 = 5%)
        volatility: float,                # Волатильность (std dev)
        timeframe_months: int = 12,
        distribution: str = "normal"      # normal, lognormal, uniform
    ) -> MonteCarloResult:
        """
        Run Monte Carlo simulation for financial forecast

        Generates thousands of possible outcomes based on growth rate and volatility

        Args:
            current_value: Current financial value (revenue, budget, etc.)
            mean_growth_rate: Expected growth rate (0.05 = 5%)
            volatility: Standard deviation of growth rate (0.15 = 15%)
            timeframe_months: Months to forecast ahead
            distribution: Distribution type (normal, lognormal, uniform)

        Returns:
            MonteCarloResult with full probability distribution

        Example:
            current_revenue = 1_000_000
            mean_growth = 0.05  # 5% expected growth
            volatility = 0.15   # 15% volatility

            result = await engine.simulate_financial_forecast(
                current_revenue, mean_growth, volatility, 12
            )

            # Result:
            # mean: $1,050,000
            # 5th percentile: $850,000  (worst case)
            # 95th percentile: $1,250,000 (best case)
        """
        logger.info(
            f"Running Monte Carlo financial forecast: "
            f"current=${current_value:,.0f}, growth={mean_growth_rate:.1%}, "
            f"volatility={volatility:.1%}, timeframe={timeframe_months}m"
        )

        results = []

        for i in range(self.n_iterations):
            # Generate random growth rate based on distribution
            if distribution == "normal":
                growth_rate = np.random.normal(mean_growth_rate, volatility)
            elif distribution == "lognormal":
                growth_rate = np.random.lognormal(
                    np.log(1 + mean_growth_rate), volatility
                ) - 1
            elif distribution == "uniform":
                low = mean_growth_rate - volatility * 1.5
                high = mean_growth_rate + volatility * 1.5
                growth_rate = np.random.uniform(low, high)
            else:
                raise ValueError(f"Unknown distribution: {distribution}")

            # Apply growth over timeframe
            years = timeframe_months / 12
            final_value = current_value * (1 + growth_rate) ** years

            results.append(final_value)

        # Calculate statistics
        results_array = np.array(results)

        monte_carlo_result = MonteCarloResult(
            mean=float(np.mean(results_array)),
            median=float(np.median(results_array)),
            std_dev=float(np.std(results_array)),
            percentile_5=float(np.percentile(results_array, 5)),
            percentile_25=float(np.percentile(results_array, 25)),
            percentile_75=float(np.percentile(results_array, 75)),
            percentile_95=float(np.percentile(results_array, 95)),
            confidence_interval_95=(
                float(np.percentile(results_array, 2.5)),
                float(np.percentile(results_array, 97.5))
            ),
            distribution=results[:1000],  # Store first 1000 for visualization
            iterations=self.n_iterations,
            convergence_reached=self._check_convergence(results_array)
        )

        logger.info(
            f"Monte Carlo complete: mean=${monte_carlo_result.mean:,.0f}, "
            f"95% CI=[${monte_carlo_result.confidence_interval_95[0]:,.0f}, "
            f"${monte_carlo_result.confidence_interval_95[1]:,.0f}]"
        )

        return monte_carlo_result

    async def simulate_impact_assessment(
        self,
        scenario_type: str,
        organization_params: Dict[str, float],  # revenue, employees, etc.
        scenario_params: Dict[str, Any]         # severity, duration, etc.
    ) -> MonteCarloResult:
        """
        Run Monte Carlo for BCM impact assessment

        Simulates thousands of possible outcomes for:
        - Financial impact (revenue loss)
        - Operational impact (downtime)
        - Recovery time
        - Total cost

        Args:
            scenario_type: Type of scenario (cyber_attack, natural_disaster, etc.)
            organization_params: Organization data (revenue, employees, maturity)
            scenario_params: Scenario parameters (severity, duration)

        Returns:
            MonteCarloResult with impact distribution

        Example:
            result = await engine.simulate_impact_assessment(
                scenario_type="cyber_attack",
                organization_params={
                    "revenue": 10_000_000,
                    "employees": 100,
                    "maturity": 3
                },
                scenario_params={
                    "severity": "high",
                    "attack_vector": "ransomware",
                    "backup_available": True
                }
            )
        """
        logger.info(f"Running Monte Carlo impact assessment: {scenario_type}")

        results = []

        for i in range(self.n_iterations):
            # Randomly vary scenario parameters
            severity_multiplier = self._sample_severity(
                scenario_params.get("severity", "medium")
            )

            # Random duration (days) - triangular distribution
            if scenario_type == "cyber_attack":
                duration_days = np.random.triangular(1, 7, 30)  # min, mode, max
            elif scenario_type == "natural_disaster":
                duration_days = np.random.triangular(3, 14, 60)
            elif scenario_type == "pandemic":
                duration_days = np.random.triangular(30, 90, 365)
            else:
                duration_days = np.random.triangular(1, 14, 90)

            # Calculate daily revenue
            annual_revenue = organization_params.get("revenue", 1_000_000)
            daily_revenue = annual_revenue / 365

            # Impact varies by maturity
            maturity = organization_params.get("maturity", 3)
            resilience_factor = 1.0 - (maturity / 10)  # Higher maturity = lower impact

            # Calculate impact
            revenue_loss = (
                daily_revenue * duration_days *
                severity_multiplier * resilience_factor
            )

            # Add recovery costs (random 10-50% of revenue loss)
            recovery_multiplier = np.random.uniform(0.1, 0.5)
            recovery_costs = revenue_loss * recovery_multiplier

            # Total impact
            total_impact = revenue_loss + recovery_costs

            results.append(total_impact)

        # Calculate statistics
        results_array = np.array(results)

        return MonteCarloResult(
            mean=float(np.mean(results_array)),
            median=float(np.median(results_array)),
            std_dev=float(np.std(results_array)),
            percentile_5=float(np.percentile(results_array, 5)),
            percentile_25=float(np.percentile(results_array, 25)),
            percentile_75=float(np.percentile(results_array, 75)),
            percentile_95=float(np.percentile(results_array, 95)),
            confidence_interval_95=(
                float(np.percentile(results_array, 2.5)),
                float(np.percentile(results_array, 97.5))
            ),
            distribution=results[:1000],
            iterations=self.n_iterations,
            convergence_reached=self._check_convergence(results_array)
        )

    async def sensitivity_analysis(
        self,
        base_params: Dict[str, float],
        param_ranges: Dict[str, Tuple[float, float]],  # {param: (min, max)}
        model_func: callable
    ) -> Dict[str, Dict[str, float]]:
        """
        Perform sensitivity analysis using Monte Carlo

        Determines which parameters have the biggest impact on outcome

        Args:
            base_params: Baseline parameter values
            param_ranges: Min/max ranges for each parameter
            model_func: Async function that takes params and returns result

        Returns:
            Dict with sensitivity scores for each parameter

        Example:
            sensitivity = await engine.sensitivity_analysis(
                base_params={
                    "revenue": 1_000_000,
                    "employees": 100,
                    "maturity": 3
                },
                param_ranges={
                    "revenue": (500_000, 2_000_000),
                    "employees": (50, 200),
                    "maturity": (1, 5)
                },
                model_func=my_impact_function
            )

            # Result:
            # {
            #   "revenue": {"correlation": 0.85, "importance": "high"},
            #   "employees": {"correlation": 0.32, "importance": "low"},
            #   "maturity": {"correlation": -0.65, "importance": "high"}
            # }
        """
        logger.info("Running sensitivity analysis with Monte Carlo")

        n_samples = min(1000, self.n_iterations)

        # Collect samples
        samples = {param: [] for param in param_ranges.keys()}
        outputs = []

        for i in range(n_samples):
            # Generate random parameter values
            params = base_params.copy()

            for param, (min_val, max_val) in param_ranges.items():
                random_value = np.random.uniform(min_val, max_val)
                params[param] = random_value
                samples[param].append(random_value)

            # Run model
            result = await model_func(params)
            outputs.append(result)

        # Calculate correlations
        sensitivity_results = {}
        outputs_array = np.array(outputs)

        for param in param_ranges.keys():
            param_array = np.array(samples[param])

            # Pearson correlation
            correlation = np.corrcoef(param_array, outputs_array)[0, 1]
            abs_corr = abs(correlation)

            # Importance classification
            if abs_corr > 0.7:
                importance = "critical"
            elif abs_corr > 0.4:
                importance = "high"
            elif abs_corr > 0.2:
                importance = "medium"
            else:
                importance = "low"

            sensitivity_results[param] = {
                "correlation": float(correlation),
                "absolute_correlation": float(abs_corr),
                "importance": importance,
                "effect": "positive" if correlation > 0 else "negative"
            }

        logger.info(f"Sensitivity analysis complete: {len(sensitivity_results)} parameters")

        return sensitivity_results

    def _sample_severity(self, severity: str) -> float:
        """
        Sample severity multiplier from triangular distribution

        Args:
            severity: Severity level (low, medium, high, critical)

        Returns:
            Severity multiplier (0.0 - 1.0)
        """
        if severity == "low":
            return np.random.triangular(0.1, 0.3, 0.5)
        elif severity == "medium":
            return np.random.triangular(0.3, 0.6, 0.8)
        elif severity == "high":
            return np.random.triangular(0.6, 0.8, 1.0)
        elif severity == "critical":
            return np.random.triangular(0.8, 0.95, 1.0)
        else:
            return 0.5

    def _check_convergence(
        self,
        results: np.ndarray,
        threshold: float = 0.01
    ) -> bool:
        """
        Check if Monte Carlo has converged

        Compares first half vs second half of results to check stability

        Args:
            results: Array of simulation results
            threshold: Convergence threshold (default 1%)

        Returns:
            True if converged, False otherwise
        """
        if len(results) < 100:
            return False

        mid = len(results) // 2
        first_half_mean = np.mean(results[:mid])
        second_half_mean = np.mean(results[mid:])

        if first_half_mean == 0:
            return False

        relative_diff = abs(second_half_mean - first_half_mean) / first_half_mean

        return relative_diff < threshold
