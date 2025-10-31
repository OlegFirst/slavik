#!/usr/bin/env python3
"""
BCM Deployment Service
Простой и надежный сервис для управления развертыванием
"""

import os
import time
import subprocess
import json
import logging
from datetime import datetime
from typing import List, Dict, Any
import asyncio

from fastapi import FastAPI, HTTPException
import requests
import docker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="BCM Deployer", version="1.0.0")

class BCMDeployer:
    """Простой деплойер без AI - только запуск и мониторинг"""
    
    def __init__(self):
        self.docker_client = docker.from_env()
        self.service_order = [
            "postgres", "redis", "rabbitmq",  # Инфраструктура
            "ai_orchestrator", "github_app",   # AI сервисы
            "odoo",                           # Core
            "web_portal", "admin_panel"       # Frontend
        ]
        self.critical_services = ["postgres", "redis"]
        self.monitoring = True
        
    def start_service(self, service_name: str) -> bool:
        """Запуск одного сервиса"""
        try:
            logger.info(f"🚀 Starting {service_name}...")
            result = subprocess.run([
                "docker-compose", "up", service_name, "-d"
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                logger.info(f"✅ {service_name} started successfully")
                return True
            else:
                logger.error(f"❌ {service_name} failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error(f"⏱️ {service_name} start timeout")
            return False
        except Exception as e:
            logger.error(f"❌ {service_name} start error: {e}")
            return False
    
    def check_service_health(self, service_name: str) -> bool:
        """Проверка здоровья сервиса"""
        try:
            container = self.docker_client.containers.get(f"iso-22301-{service_name}-1")
            return container.status == "running"
        except docker.errors.NotFound:
            return False
        except Exception as e:
            logger.error(f"Health check error for {service_name}: {e}")
            return False
    
    def restart_service(self, service_name: str) -> bool:
        """Перезапуск упавшего сервиса"""
        logger.warning(f"🔄 Restarting {service_name}...")
        try:
            subprocess.run(["docker-compose", "restart", service_name], 
                          capture_output=True, timeout=60)
            time.sleep(10)  # Ждем запуска
            return self.check_service_health(service_name)
        except Exception as e:
            logger.error(f"Restart failed for {service_name}: {e}")
            return False
    
    async def deploy_platform(self) -> Dict[str, Any]:
        """Последовательное развертывание платформы"""
        start_time = datetime.now()
        deployed_services = []
        failed_services = []
        
        for service in self.service_order:
            logger.info(f"📦 Deploying {service}...")
            
            if self.start_service(service):
                # Ждем готовности
                for attempt in range(30):  # 30 попыток по 10 сек = 5 минут
                    if self.check_service_health(service):
                        deployed_services.append(service)
                        logger.info(f"✅ {service} is healthy")
                        break
                    time.sleep(10)
                else:
                    logger.warning(f"⚠️ {service} started but not healthy")
                    failed_services.append(service)
                    
                    # Критические сервисы - останавливаем развертывание
                    if service in self.critical_services:
                        logger.error(f"💀 Critical service {service} failed - stopping deployment")
                        break
            else:
                failed_services.append(service)
                logger.error(f"❌ {service} deployment failed")
                
                if service in self.critical_services:
                    break
        
        execution_time = int((datetime.now() - start_time).total_seconds())
        
        return {
            "deployment_id": f"deploy_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "status": "success" if not failed_services else "partial",
            "deployed_services": deployed_services,
            "failed_services": failed_services,
            "execution_time": execution_time,
            "total_services": len(self.service_order)
        }
    
    async def monitor_services(self):
        """Непрерывный мониторинг и автоперезапуск"""
        logger.info("👀 Starting service monitoring...")
        
        while self.monitoring:
            try:
                for service in self.service_order:
                    if not self.check_service_health(service):
                        logger.warning(f"🚨 {service} is down - attempting restart")
                        
                        if self.restart_service(service):
                            logger.info(f"✅ {service} recovered")
                        else:
                            logger.error(f"❌ {service} restart failed")
                            
                            # Уведомление AI Orchestrator о проблеме
                            try:
                                requests.post("http://ai_orchestrator:8000/alerts/service-down", 
                                            json={"service": service, "timestamp": datetime.now().isoformat()},
                                            timeout=5)
                            except:
                                pass  # AI может быть недоступен
                
                await asyncio.sleep(60)  # Проверка каждую минуту
                
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                await asyncio.sleep(60)

# Создание деплойера
deployer = BCMDeployer()

@app.get("/")
async def root():
    return {
        "service": "BCM Deployer",
        "role": "Service deployment and monitoring",
        "status": "ready",
        "monitoring": deployer.monitoring,
        "service_order": deployer.service_order
    }

@app.get("/health") 
async def health():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

@app.post("/deploy")
async def deploy_platform():
    """🚀 Запуск полного развертывания"""
    try:
        result = await deployer.deploy_platform()
        return result
    except Exception as e:
        logger.error(f"Deployment failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status")
async def get_services_status():
    """📊 Статус всех сервисов"""
    status = {}
    for service in deployer.service_order:
        status[service] = {
            "healthy": deployer.check_service_health(service),
            "critical": service in deployer.critical_services
        }
    return {"services": status, "timestamp": datetime.now().isoformat()}

@app.post("/restart/{service_name}")
async def restart_service(service_name: str):
    """🔄 Перезапуск конкретного сервиса"""
    if service_name not in deployer.service_order:
        raise HTTPException(status_code=404, detail="Service not found")
    
    success = deployer.restart_service(service_name)
    return {
        "service": service_name,
        "restarted": success,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/monitoring/start")
async def start_monitoring():
    """👀 Запуск мониторинга"""
    deployer.monitoring = True
    asyncio.create_task(deployer.monitor_services())
    return {"monitoring": "started"}

@app.post("/monitoring/stop")
async def stop_monitoring():
    """⏹️ Остановка мониторинга"""
    deployer.monitoring = False
    return {"monitoring": "stopped"}

if __name__ == "__main__":
    import uvicorn
    print("🚀 BCM Deployer starting...")
    print("📋 Role: Simple, reliable deployment and monitoring")
    uvicorn.run(app, host="0.0.0.0", port=8002)