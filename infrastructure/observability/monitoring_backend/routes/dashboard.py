"""
Dashboard Routes
================

Real-time dashboard metrics aggregation.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime
import httpx
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

class DashboardMetrics(BaseModel):
    """Dashboard overview metrics"""
    total_services: int
    healthy_services: int
    warning_services: int
    error_services: int
    cpu_usage: float
    memory_usage: float
    active_pdca_cycles: int
    active_alerts: int
    last_updated: str

@router.get("/overview", response_model=DashboardMetrics)
async def get_dashboard_overview():
    """Get dashboard overview metrics"""
    try:
        async with httpx.AsyncClient() as client:
            # Get Prometheus targets (services)
            targets_resp = await client.get(
                "http://localhost:9090/api/v1/targets",
                timeout=5.0
            )
            targets_data = targets_resp.json()

            active_targets = targets_data.get("data", {}).get("activeTargets", [])

            # Count service health
            healthy = sum(1 for t in active_targets if t.get("health") == "up")
            total = len(active_targets)
            warning = 0  # TODO: Add warning logic
            error = total - healthy

            # Get CPU/Memory - использовать process метрики если node_exporter не установлен
            cpu_usage = 0.0
            memory_usage = 0.0

            # Try node_exporter first
            cpu_query = 'avg(rate(node_cpu_seconds_total{mode="idle"}[5m]))'
            try:
                cpu_resp = await client.get(
                    f"http://localhost:9090/api/v1/query?query={cpu_query}",
                    timeout=5.0
                )
                cpu_data = cpu_resp.json()
                results = cpu_data.get("data", {}).get("result", [])
                if results and len(results) > 0:
                    cpu_idle = float(results[0].get("value", [0, 0])[1])
                    cpu_usage = round((1 - cpu_idle) * 100, 1)
            except:
                pass

            # Fallback to process CPU if node_exporter unavailable
            if cpu_usage == 0.0:
                proc_cpu_query = 'sum(rate(process_cpu_seconds_total[5m])) * 100'
                try:
                    cpu_resp = await client.get(
                        f"http://localhost:9090/api/v1/query?query={proc_cpu_query}",
                        timeout=5.0
                    )
                    cpu_data = cpu_resp.json()
                    results = cpu_data.get("data", {}).get("result", [])
                    if results and len(results) > 0:
                        cpu_usage = round(float(results[0].get("value", [0, 1])[1]), 1)
                except:
                    cpu_usage = 0.0

            # Try node_exporter memory
            mem_query = '(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100'
            try:
                mem_resp = await client.get(
                    f"http://localhost:9090/api/v1/query?query={mem_query}",
                    timeout=5.0
                )
                mem_data = mem_resp.json()
                results = mem_data.get("data", {}).get("result", [])
                if results and len(results) > 0:
                    memory_usage = round(float(results[0].get("value", [0, 0])[1]), 1)
            except:
                pass

            # Fallback to process memory
            if memory_usage == 0.0:
                proc_mem_query = 'sum(process_resident_memory_bytes) / 1024 / 1024'
                try:
                    mem_resp = await client.get(
                        f"http://localhost:9090/api/v1/query?query={proc_mem_query}",
                        timeout=5.0
                    )
                    mem_data = mem_resp.json()
                    results = mem_data.get("data", {}).get("result", [])
                    if results and len(results) > 0:
                        memory_mb = float(results[0].get("value", [0, 0])[1])
                        # Estimate percentage (assume 16GB total)
                        memory_usage = round(memory_mb / 16384 * 100, 1)
                except:
                    memory_usage = 0.0

            # PDCA cycles (mock for now)
            pdca_cycles = 3  # TODO: Get from workflow_intelligence

            # Active alerts (optional - alertmanager may not be running)
            active_alerts = 0
            try:
                alerts_resp = await client.get(
                    "http://localhost:9093/api/v1/alerts",
                    timeout=2.0
                )
                if alerts_resp.status_code == 200:
                    alerts_data = alerts_resp.json()
                    active_alerts = len([a for a in alerts_data.get("data", []) if a.get("state") == "firing"])
            except:
                # Alertmanager not running - это OK
                pass

            return DashboardMetrics(
                total_services=total,
                healthy_services=healthy,
                warning_services=warning,
                error_services=error,
                cpu_usage=cpu_usage,
                memory_usage=memory_usage,
                active_pdca_cycles=pdca_cycles,
                active_alerts=active_alerts,
                last_updated=datetime.utcnow().isoformat()
            )

    except (httpx.TimeoutException, httpx.ConnectError) as e:
        logger.error(f"Prometheus unavailable: {e}")
        raise HTTPException(
            status_code=503,
            detail="Monitoring system (Prometheus) unavailable. Please ensure Prometheus is running on port 9090."
        )
    except Exception as e:
        logger.error(f"Error fetching dashboard metrics: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch dashboard metrics: {str(e)}"
        )

@router.get("/services")
async def get_services_status():
    """Get all services with their status"""
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "http://localhost:9090/api/v1/targets",
                timeout=5.0
            )
            data = resp.json()

            services = []
            for target in data.get("data", {}).get("activeTargets", []):
                services.append({
                    "name": target.get("labels", {}).get("job", "unknown"),
                    "instance": target.get("labels", {}).get("instance", ""),
                    "health": target.get("health", "unknown"),
                    "last_scrape": target.get("lastScrape", ""),
                    "scrape_duration": target.get("lastScrapeDuration", 0),
                    "labels": target.get("labels", {})
                })

            return {
                "services": services,
                "total": len(services),
                "timestamp": datetime.utcnow().isoformat()
            }

    except Exception as e:
        logger.error(f"Error fetching services: {e}")
        raise HTTPException(status_code=500, detail=str(e))
