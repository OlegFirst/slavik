"""Alerts Management Routes"""

from fastapi import APIRouter, HTTPException
from typing import List
import httpx
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/")
async def get_alerts():
    """Get all alerts from AlertManager"""
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "http://localhost:9093/api/v1/alerts",
                timeout=5.0
            )
            if resp.status_code == 200:
                return resp.json()
            else:
                return {"data": [], "status": "alertmanager_unavailable"}
    except Exception as e:
        logger.error(f"Error fetching alerts: {e}")
        return {"data": [], "error": str(e)}

@router.get("/groups")
async def get_alert_groups():
    """Get alert groups"""
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "http://localhost:9093/api/v1/alerts/groups",
                timeout=5.0
            )
            if resp.status_code == 200:
                return resp.json()
            else:
                return {"data": [], "status": "alertmanager_unavailable"}
    except Exception as e:
        logger.error(f"Error fetching alert groups: {e}")
        return {"data": [], "error": str(e)}
