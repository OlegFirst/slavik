
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, Any
import numpy as np, time

app = FastAPI(title="SEH Mesa Adapter", version="1.0.0")

class MesaParams(BaseModel):
    steps: int = 200
    population_size: int = 2000
    policies: Dict[str, float] = {}

class RunRequest(BaseModel):
    experiment: str = "mesa_abm"
    params: MesaParams
    monte_carlo_runs: int = 100

def run_mesa_like(params: MesaParams):
    # Placeholder for a real Mesa model; emulate coverage uplift
    base_cov = 0.55
    uplift = 0.0
    for k,v in params.policies.items():
        if k == "sms": uplift += 0.08 * (v-1.0)
        if k == "vouchers": uplift += 0.12 * (v-1.0)
        if k == "counsel": uplift += 0.06 * (v-1.0)
    noise = np.random.normal(0, 0.01)
    cov = max(0.0, min(0.95, base_cov + uplift + noise))
    return {"coverage": float(cov)}

@app.post("/run")
def run(req: RunRequest):
    results = [run_mesa_like(req.params) for _ in range(max(1, req.monte_carlo_runs))]
    mean_cov = float(np.mean([r["coverage"] for r in results]))
    best = {"kpi": "coverage", "value": mean_cov}
    frontier = [{"policy":"baseline","coverage":0.55},{"policy":"tuned","coverage":mean_cov}]
    return {
        "run_id": f"mesa_{int(time.time())}",
        "experiment": "mesa_abm",
        "best": best,
        "frontier": frontier,
        "explain": "ABM-аппроксимация: coverage зависит от интенсивностей политик (sms/vouchers/counsel)."
    }
