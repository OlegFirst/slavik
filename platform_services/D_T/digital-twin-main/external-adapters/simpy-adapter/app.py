
from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import List, Dict, Any
import simpy, numpy as np
import time

app = FastAPI(title="SEH SimPy Adapter", version="1.0.0")

class ServiceTime(BaseModel):
    dist: str = Field("lognormal")
    mu: str | float = Field("10m")
    sigma: float = Field(0.5)

class SimParams(BaseModel):
    arrival_rate: float  # per hour
    service_time: ServiceTime
    capacity_agents: List[int]
    shift_calendar: Dict[str, str] | None = None
    targets: Dict[str, Any] | None = None
    constraints: Dict[str, Any] | None = None

class RunRequest(BaseModel):
    experiment: str = "simpy_queue"
    params: SimParams
    monte_carlo_runs: int = 200

def minutes_to_seconds(v):
    if isinstance(v, (int,float)):
        return float(v) * 60.0
    s = str(v).strip().lower()
    if s.endswith("m"):
        return float(s[:-1]) * 60.0
    if s.endswith("h"):
        return float(s[:-1]) * 3600.0
    return float(s)

def sample_service_time(cfg: ServiceTime, size: int):
    # Support a simple lognormal parameterization on minutes -> seconds
    mu = cfg.mu
    sigma = cfg.sigma
    mu_s = minutes_to_seconds(mu) if isinstance(mu, str) else mu*60.0
    # Convert to lognormal parameters on seconds
    # Assume mu_s is median; approximate
    # draw lognormal with log-mean = ln(mu_s) and sigma as given (rough)
    return np.random.lognormal(mean=np.log(max(mu_s, 1e-3)), sigma=max(sigma, 1e-6), size=size)

def simulate_once(capacity:int, p:SimParams, horizon_hours:float=8.0, sla_threshold_min:float|None=None):
    env = simpy.Environment()
    server = simpy.Resource(env, capacity=capacity)

    arrival_rate_per_sec = p.arrival_rate / 3600.0  # per second
    horizon = horizon_hours * 3600.0
    waits = []

    def arrival_process():
        t = 0.0
        while t < horizon:
            # exponential interarrival
            inter = np.random.exponential(1.0/arrival_rate_per_sec) if arrival_rate_per_sec>0 else horizon
            t += inter
            if t >= horizon: break
            env.process(customer(t))

    def customer(arrival_time):
        with server.request() as req:
            yield req
            wait = env.now - arrival_time
            waits.append(wait)
            # service
            st = float(sample_service_time(p.service_time, 1)[0])
            yield env.timeout(st)

    env.process(arrival_process())
    env.run(until=horizon+3600.0)

    if len(waits)==0:
        return {"sla": 1.0, "wait_p50_min": 0.0, "cost": 0.0}
    p50 = float(np.percentile(waits, 50.0))/60.0
    sla = None
    if sla_threshold_min is not None:
        sla = float((np.array(waits)/60.0 <= sla_threshold_min).mean())
    else:
        sla = float((np.array(waits)/60.0 <= 15.0).mean())
    cost = capacity * 8 * 20  # naive cost: agents * hours * $20
    return {"sla": sla, "wait_p50_min": p50, "cost": cost}

@app.post("/run")
def run(req: RunRequest):
    np.random.seed(int(time.time()) % 2**31)
    sla_threshold = None
    if req.params.targets and "wait_p50_min" in req.params.targets:
        # SLA target as median threshold proxy
        try:
            v = req.params.targets["wait_p50_min"]
            sla_threshold = float(v.replace("m","")) if isinstance(v, str) else float(v)
        except Exception:
            sla_threshold = None

    results = []
    for cap in req.params.capacity_agents:
        metrics_runs = [simulate_once(cap, req.params, horizon_hours=8.0, sla_threshold_min=sla_threshold) for _ in range(max(1, req.monte_carlo_runs//10))]
        # Aggregate simple (mean over MC subsamples)
        sla = float(np.mean([m["sla"] for m in metrics_runs]))
        p50 = float(np.mean([m["wait_p50_min"] for m in metrics_runs]))
        cost = float(np.mean([m["cost"] for m in metrics_runs]))
        results.append({"capacity": cap, "sla": sla, "wait_p50_min": p50, "cost": cost})

    # pick best by meeting sla_target (if provided) with min cost, else min p50
    target = req.params.targets.get("sla_target") if req.params.targets else None
    best = None
    if isinstance(target, (int,float)):
        feasible = [r for r in results if r["sla"] >= float(target)]
        best = min(feasible, key=lambda r: r["cost"]) if feasible else min(results, key=lambda r: r["wait_p50_min"])
    else:
        best = min(results, key=lambda r: r["wait_p50_min"])
    frontier = results

    return {
        "run_id": f"simpy_{int(time.time())}",
        "experiment": "simpy_queue",
        "best": best,
        "frontier": frontier,
        "explain": "Боттлнек и SLA оценены через DES. Стоимость ~ capacity*8h*$20. Настройте формулу под реальность."
    }
