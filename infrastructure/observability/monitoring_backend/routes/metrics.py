"""Metrics Routes - Prometheus integration"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
import httpx
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/query")
async def query_prometheus(
    query: str = Query(..., description="PromQL query"),
    time: Optional[str] = Query(None, description="Evaluation timestamp")
):
    """Execute PromQL query"""
    try:
        params = {"query": query}
        if time:
            params["time"] = time

        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "http://localhost:9090/api/v1/query",
                params=params,
                timeout=10.0
            )
            return resp.json()
    except Exception as e:
        logger.error(f"Prometheus query error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/range")
async def query_range(
    query: str = Query(..., description="PromQL query"),
    start: str = Query(..., description="Start timestamp"),
    end: str = Query(..., description="End timestamp"),
    step: str = Query("15s", description="Query resolution step")
):
    """Execute PromQL range query"""
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "http://localhost:9090/api/v1/query_range",
                params={"query": query, "start": start, "end": end, "step": step},
                timeout=10.0
            )
            return resp.json()
    except Exception as e:
        logger.error(f"Prometheus range query error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
