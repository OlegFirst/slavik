"""
SimPy Adapter for Digital Twin Platform
Discrete Event Simulation for Queue Management and Capacity Planning

Ported from: digital-twin-platform/external-adapters/simpy-adapter/app.py
Version: 2.0.0
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import simpy
import numpy as np
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Digital Twin SimPy Adapter",
    version="2.0.0",
    description="Discrete Event Simulation for process optimization and capacity planning"
)


class ServiceTime(BaseModel):
    """Service time distribution parameters"""
    dist: str = Field(default="lognormal", description="Distribution type (lognormal, normal, exponential)")
    mu: str | float = Field(default="10m", description="Mean service time (can be string with 'm' or 'h' suffix)")
    sigma: float = Field(default=0.5, description="Standard deviation for lognormal distribution")


class SimParams(BaseModel):
    """Simulation parameters"""
    arrival_rate: float = Field(..., description="Arrival rate per hour")
    service_time: ServiceTime
    capacity_agents: List[int] = Field(..., description="List of capacity configurations to test")
    shift_calendar: Optional[Dict[str, str]] = Field(None, description="Shift calendar (future feature)")
    targets: Optional[Dict[str, Any]] = Field(None, description="Performance targets (sla_target, wait_p50_min)")
    constraints: Optional[Dict[str, Any]] = Field(None, description="Constraints (future feature)")


class RunRequest(BaseModel):
    """Simulation run request"""
    experiment: str = Field(default="simpy_queue", description="Experiment type")
    params: SimParams
    monte_carlo_runs: int = Field(default=200, description="Number of Monte Carlo iterations")


class SimulationResult(BaseModel):
    """Simulation results"""
    run_id: str
    experiment: str
    best: Dict[str, Any]
    frontier: List[Dict[str, Any]]
    explain: str


def minutes_to_seconds(v: str | float) -> float:
    """Convert time string to seconds"""
    if isinstance(v, (int, float)):
        return float(v) * 60.0

    s = str(v).strip().lower()
    if s.endswith("m"):
        return float(s[:-1]) * 60.0
    if s.endswith("h"):
        return float(s[:-1]) * 3600.0
    return float(s)


def sample_service_time(cfg: ServiceTime, size: int) -> np.ndarray:
    """Sample service times from distribution"""
    mu = cfg.mu
    sigma = cfg.sigma
    mu_s = minutes_to_seconds(mu) if isinstance(mu, str) else mu * 60.0

    if cfg.dist == "lognormal":
        # Convert to lognormal parameters on seconds
        return np.random.lognormal(
            mean=np.log(max(mu_s, 1e-3)),
            sigma=max(sigma, 1e-6),
            size=size
        )
    elif cfg.dist == "exponential":
        return np.random.exponential(mu_s, size=size)
    elif cfg.dist == "normal":
        return np.abs(np.random.normal(mu_s, mu_s * sigma, size=size))
    else:
        return np.random.lognormal(mean=np.log(max(mu_s, 1e-3)), sigma=max(sigma, 1e-6), size=size)


def simulate_once(
    capacity: int,
    p: SimParams,
    horizon_hours: float = 8.0,
    sla_threshold_min: Optional[float] = None
) -> Dict[str, float]:
    """Run single discrete event simulation"""
    env = simpy.Environment()
    server = simpy.Resource(env, capacity=capacity)

    arrival_rate_per_sec = p.arrival_rate / 3600.0  # per second
    horizon = horizon_hours * 3600.0
    waits = []

    def arrival_process():
        """Generate customer arrivals"""
        t = 0.0
        while t < horizon:
            # Exponential interarrival times
            inter = np.random.exponential(1.0 / arrival_rate_per_sec) if arrival_rate_per_sec > 0 else horizon
            t += inter
            if t >= horizon:
                break
            env.process(customer(t))

    def customer(arrival_time):
        """Customer service process"""
        with server.request() as req:
            yield req
            wait = env.now - arrival_time
            waits.append(wait)
            # Service time
            st = float(sample_service_time(p.service_time, 1)[0])
            yield env.timeout(st)

    env.process(arrival_process())
    env.run(until=horizon + 3600.0)

    if len(waits) == 0:
        return {"sla": 1.0, "wait_p50_min": 0.0, "cost": 0.0}

    p50 = float(np.percentile(waits, 50.0)) / 60.0

    # Calculate SLA (percentage meeting threshold)
    if sla_threshold_min is not None:
        sla = float((np.array(waits) / 60.0 <= sla_threshold_min).mean())
    else:
        sla = float((np.array(waits) / 60.0 <= 15.0).mean())

    # Naive cost model: agents * hours * $20/hour
    cost = capacity * 8 * 20

    return {
        "sla": sla,
        "wait_p50_min": p50,
        "cost": cost
    }


@app.post("/run", response_model=SimulationResult)
def run(req: RunRequest):
    """
    Run discrete event simulation for queue management

    Returns optimal capacity configuration based on SLA targets and cost
    """
    logger.info(f"Starting SimPy simulation with {len(req.params.capacity_agents)} capacity configurations")

    np.random.seed(int(time.time()) % 2**31)

    # Extract SLA threshold
    sla_threshold = None
    if req.params.targets and "wait_p50_min" in req.params.targets:
        try:
            v = req.params.targets["wait_p50_min"]
            sla_threshold = float(v.replace("m", "")) if isinstance(v, str) else float(v)
        except Exception as e:
            logger.warning(f"Could not parse SLA threshold: {e}")
            sla_threshold = None

    results = []

    for cap in req.params.capacity_agents:
        logger.info(f"Simulating capacity: {cap} agents")

        # Run Monte Carlo iterations (subsample for speed)
        metrics_runs = [
            simulate_once(cap, req.params, horizon_hours=8.0, sla_threshold_min=sla_threshold)
            for _ in range(max(1, req.monte_carlo_runs // 10))
        ]

        # Aggregate metrics (mean over MC runs)
        sla = float(np.mean([m["sla"] for m in metrics_runs]))
        p50 = float(np.mean([m["wait_p50_min"] for m in metrics_runs]))
        cost = float(np.mean([m["cost"] for m in metrics_runs]))

        results.append({
            "capacity": cap,
            "sla": sla,
            "wait_p50_min": p50,
            "cost": cost
        })

    # Pick best configuration
    target = req.params.targets.get("sla_target") if req.params.targets else None

    if isinstance(target, (int, float)):
        # Find minimum cost that meets SLA target
        feasible = [r for r in results if r["sla"] >= float(target)]
        best = min(feasible, key=lambda r: r["cost"]) if feasible else min(results, key=lambda r: r["wait_p50_min"])
    else:
        # Find minimum median wait time
        best = min(results, key=lambda r: r["wait_p50_min"])

    logger.info(f"Best configuration: {best['capacity']} agents (SLA: {best['sla']:.2%}, Wait: {best['wait_p50_min']:.1f}min)")

    return SimulationResult(
        run_id=f"simpy_{int(time.time())}",
        experiment="simpy_queue",
        best=best,
        frontier=results,
        explain="Bottleneck and SLA evaluated through Discrete Event Simulation. Cost formula: capacity*8h*$20. Adjust for your context."
    )


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "adapter": "simpy",
        "version": "2.0.0",
        "capabilities": ["discrete_event_simulation", "queue_management", "capacity_planning"]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7001)
