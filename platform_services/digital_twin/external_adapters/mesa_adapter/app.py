"""
Mesa ABM Adapter for Digital Twin Platform
Agent-Based Modeling for stakeholder behavior simulation

Ported from: digital-twin-platform/external-adapters/mesa-adapter/app.py
Version: 2.0.0
"""

from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Dict, Any
import numpy as np
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Digital Twin Mesa ABM Adapter",
    version="2.0.0",
    description="Agent-Based Modeling for individual behavior and stakeholder dynamics"
)


class MesaParams(BaseModel):
    """Mesa ABM simulation parameters"""
    steps: int = Field(default=200, description="Number of simulation steps")
    population_size: int = Field(default=2000, description="Agent population size")
    policies: Dict[str, float] = Field(default_factory=dict, description="Policy interventions (sms, vouchers, counsel)")


class RunRequest(BaseModel):
    """ABM simulation run request"""
    experiment: str = Field(default="mesa_abm", description="Experiment type")
    params: MesaParams
    monte_carlo_runs: int = Field(default=100, description="Number of Monte Carlo iterations")


class SimulationResult(BaseModel):
    """Simulation results"""
    run_id: str
    experiment: str
    best: Dict[str, Any]
    frontier: List[Dict[str, Any]]
    explain: str


def run_mesa_like(params: MesaParams) -> Dict[str, float]:
    """
    Run simplified Mesa-like ABM simulation

    This is a placeholder for real Mesa model implementation.
    Emulates coverage uplift based on policy interventions.
    """
    # Baseline coverage
    base_cov = 0.55
    uplift = 0.0

    # Policy impacts
    for k, v in params.policies.items():
        if k == "sms":
            # SMS campaigns increase coverage by 8% per unit intensity above baseline
            uplift += 0.08 * (v - 1.0)
        if k == "vouchers":
            # Voucher programs increase coverage by 12% per unit
            uplift += 0.12 * (v - 1.0)
        if k == "counsel":
            # Counseling increases coverage by 6% per unit
            uplift += 0.06 * (v - 1.0)

    # Add stochastic noise
    noise = np.random.normal(0, 0.01)

    # Calculate final coverage (bounded 0-95%)
    cov = max(0.0, min(0.95, base_cov + uplift + noise))

    return {"coverage": float(cov)}


@app.post("/run", response_model=SimulationResult)
def run(req: RunRequest):
    """
    Run Agent-Based Model simulation

    Simulates individual agent behavior and policy interventions.
    Returns coverage metrics based on policy configurations.
    """
    logger.info(f"Starting Mesa ABM simulation: {req.params.population_size} agents, {req.params.steps} steps")

    # Run Monte Carlo iterations
    results = [
        run_mesa_like(req.params)
        for _ in range(max(1, req.monte_carlo_runs))
    ]

    # Aggregate results
    mean_cov = float(np.mean([r["coverage"] for r in results]))
    std_cov = float(np.std([r["coverage"] for r in results]))

    logger.info(f"Simulation complete: Coverage = {mean_cov:.2%} ± {std_cov:.2%}")

    # Best configuration
    best = {
        "kpi": "coverage",
        "value": mean_cov,
        "std": std_cov,
        "policies": req.params.policies
    }

    # Frontier (baseline vs tuned)
    frontier = [
        {"policy": "baseline", "coverage": 0.55},
        {"policy": "tuned", "coverage": mean_cov}
    ]

    return SimulationResult(
        run_id=f"mesa_{int(time.time())}",
        experiment="mesa_abm",
        best=best,
        frontier=frontier,
        explain="ABM approximation: coverage depends on policy intensities (sms/vouchers/counsel). Replace with real Mesa model for accurate agent interactions."
    )


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "adapter": "mesa",
        "version": "2.0.0",
        "capabilities": ["agent_based_modeling", "stakeholder_behavior", "policy_simulation"]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7002)
