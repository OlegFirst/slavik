"""
Отдельный GitHub App сервис для webhooks и Copilot Extension
"""

from fastapi import FastAPI, Request
import uvicorn
import os
from datetime import datetime
from typing import Dict, Any

app = FastAPI(title="BCM GitHub App Service", version="1.0.0")

@app.get("/")
async def root():
    return {
        "service": "BCM GitHub App", 
        "status": "ready",
        "app_id": os.getenv("GITHUB_APP_ID"),
        "endpoints": ["webhook", "auth"]
    }

@app.post("/github/webhook")
async def github_webhook(request: Request):
    """GitHub webhooks"""
    payload = await request.json()
    event_type = request.headers.get("X-GitHub-Event")
    
    return {"status": "processed", "event": event_type}

@app.post("/auth/token-exchange")
async def token_exchange(request: Request):
    """GitHub Copilot token exchange"""
    return {
        "token": f"bcm_token_{datetime.now().strftime('%H%M%S')}",
        "expires_in": 28800
    }

# Прокси endpoints для GitHub Copilot Skills → AI Orchestrator
import httpx

@app.post("/claude/analyze-changes")
async def proxy_analyze_changes(request: Request):
    """Прокси для анализа изменений → AI Orchestrator"""
    body = await request.json()
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://ai_orchestrator:8000/claude/analyze-changes",
            json=body,
            headers=dict(request.headers)
        )
        return response.json()

@app.post("/claude/generate-config")
async def proxy_generate_config(request: Request):
    """Прокси для генерации конфигурации → AI Orchestrator"""
    body = await request.json()
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://ai_orchestrator:8000/claude/generate-config",
            json=body,
            headers=dict(request.headers)
        )
        return response.json()

@app.get("/deployment/history")
async def proxy_deployment_history(request: Request):
    """Прокси для истории развертываний → AI Orchestrator"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "http://ai_orchestrator:8000/deployment/history",
            headers=dict(request.headers)
        )
        return response.json()

@app.post("/claude/analyze-deployment")
async def proxy_analyze_deployment(request: Request):
    """Прокси для анализа развертывания → AI Orchestrator"""
    body = await request.json()
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://ai_orchestrator:8000/claude/analyze-deployment",
            json=body,
            headers=dict(request.headers)
        )
        return response.json()

@app.post("/deployment/orchestrate")
async def proxy_orchestrate(request: Request):
    """Прокси для оркестрации развертывания → AI Orchestrator"""
    body = await request.json()
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://ai_orchestrator:8000/deployment/orchestrate",
            json=body,
            headers=dict(request.headers)
        )
        return response.json()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)