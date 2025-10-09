"""
Monte Carlo Simulation Engine

Statistical risk analysis using Monte Carlo method
"""

import sys
from pathlib import Path
import numpy as np
from typing import Dict, Any, List

sys.path.insert(0, str(Path(__file__).parent))
from base_engine import BaseSimulationEngine


class MonteCarloEngine(BaseSimulationEngine):
    """Monte Carlo simulation for risk quantification"""

    def validate_parameters(self) -> bool:
        """Validate parameters"""
        required = ['iterations', 'variables']

        for param in required:
            if param not in self.parameters:
                raise ValueError(f"Missing required parameter: {param}")

        if self.parameters['iterations'] < 100:
            raise ValueError("Iterations must be >= 100")

        return True

    async def run(self) -> Dict[str, Any]:
        """
        Run Monte Carlo simulation

        Parameters:
            - iterations: Number of Monte Carlo iterations (e.g., 10000)
            - variables: Dict of random variables with distributions
              Example: {
                  "recovery_time": {"distribution": "normal", "mean": 4, "std": 1},
                  "financial_loss": {"distribution": "lognormal", "mean": 100000, "std": 50000}
              }
            - calculation: Python expression using variables (e.g., "recovery_time * 1000 + financial_loss")

        Returns:
            Statistical results
        """
        self.validate_parameters()

        iterations = self.parameters['iterations']
        variables = self.parameters['variables']
        calculation = self.parameters.get('calculation', 'sum(variables.values())')

        self.log_progress("Starting Monte Carlo simulation", 0)

        # Generate random samples
        samples = self._generate_samples(variables, iterations)

        self.log_progress("Generated samples", 30)

        # Run calculations
        results = self._run_calculations(samples, calculation, iterations)

        self.log_progress("Completed calculations", 70)

        # Analyze statistics
        statistics = self._analyze_statistics(results)

        self.log_progress("Analyzed statistics", 100)

        return {
            "simulation_id": self.simulation_id,
            "iterations": iterations,
            "variables": variables,
            "statistics": statistics,
            "percentiles": {
                "p10": float(np.percentile(results, 10)),
                "p25": float(np.percentile(results, 25)),
                "p50": float(np.percentile(results, 50)),
                "p75": float(np.percentile(results, 75)),
                "p90": float(np.percentile(results, 90)),
                "p95": float(np.percentile(results, 95)),
                "p99": float(np.percentile(results, 99))
            },
            "confidence": 0.95
        }

    def _generate_samples(self, variables: Dict[str, Any], iterations: int) -> Dict[str, np.ndarray]:
        """Generate random samples for each variable"""
        samples = {}

        for var_name, var_config in variables.items():
            distribution = var_config.get('distribution', 'normal')

            if distribution == 'normal':
                mean = var_config['mean']
                std = var_config['std']
                samples[var_name] = np.random.normal(mean, std, iterations)

            elif distribution == 'lognormal':
                mean = var_config['mean']
                std = var_config['std']
                samples[var_name] = np.random.lognormal(np.log(mean), std, iterations)

            elif distribution == 'uniform':
                min_val = var_config['min']
                max_val = var_config['max']
                samples[var_name] = np.random.uniform(min_val, max_val, iterations)

            elif distribution == 'exponential':
                scale = var_config['scale']
                samples[var_name] = np.random.exponential(scale, iterations)

            elif distribution == 'triangular':
                left = var_config['left']
                mode = var_config['mode']
                right = var_config['right']
                samples[var_name] = np.random.triangular(left, mode, right, iterations)

            else:
                # Default to normal
                mean = var_config.get('mean', 0)
                std = var_config.get('std', 1)
                samples[var_name] = np.random.normal(mean, std, iterations)

        return samples

    def _run_calculations(self, samples: Dict[str, np.ndarray], calculation: str, iterations: int) -> np.ndarray:
        """Run calculation for each iteration"""
        results = []

        for i in range(iterations):
            # Build variables dict for this iteration
            iter_vars = {var_name: samples[var_name][i] for var_name in samples}

            # Evaluate calculation
            try:
                # Safe eval with limited scope
                result = eval(calculation, {"__builtins__": {}}, iter_vars)
                results.append(result)
            except Exception as e:
                self.logger.error(f"Calculation error at iteration {i}: {e}")
                results.append(0)

        return np.array(results)

    def _analyze_statistics(self, results: np.ndarray) -> Dict[str, float]:
        """Calculate statistical measures"""
        return {
            "mean": float(np.mean(results)),
            "median": float(np.median(results)),
            "std": float(np.std(results)),
            "variance": float(np.var(results)),
            "min": float(np.min(results)),
            "max": float(np.max(results)),
            "range": float(np.max(results) - np.min(results)),
            "coefficient_of_variation": float(np.std(results) / np.mean(results)) if np.mean(results) != 0 else 0
        }
