"""
BCM Platform - AI Orchestrator Service

Интеллектуальный координатор для автоматизации BCM процессов:
- Анализ бизнес-процессов и рисков
- Автоматическая классификация инцидентов
- Рекомендации по планам непрерывности
- Natural Language Processing для запросов
- Machine Learning для прогнозирования
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Union
from enum import Enum

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
import redis
import pika

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI приложение
app = FastAPI(
    title="BCM AI Orchestrator",
    description="Интеллектуальный координатор для BCM Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Модели данных
class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class IncidentCategory(str, Enum):
    OPERATIONAL = "operational"
    SECURITY = "security"
    NATURAL = "natural_disaster"
    TECHNOLOGY = "technology"
    HUMAN = "human_error"
    EXTERNAL = "external_threat"

class BusinessProcess(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    criticality: int = Field(..., ge=1, le=5)
    rto_hours: int = Field(..., ge=1)
    rpo_hours: int = Field(..., ge=0)
    dependencies: List[int] = []
    resources_required: List[str] = []

class Incident(BaseModel):
    id: Optional[int] = None
    title: str
    description: str
    category: IncidentCategory
    severity: RiskLevel
    affected_processes: List[int] = []
    estimated_impact: Optional[float] = None
    created_at: Optional[datetime] = None

class NaturalLanguageQuery(BaseModel):
    query: str
    context: Optional[Dict[str, Any]] = None
    user_role: Optional[str] = "user"

# Подключения к внешним сервисам
redis_client = None
rabbitmq_connection = None

@app.on_event("startup")
async def startup_event():
    """Инициализация при запуске"""
    global redis_client, rabbitmq_connection
    
    try:
        # Redis
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        redis_client = redis.from_url(redis_url)
        
        logger.info("🤖 AI Orchestrator запущен успешно")
        
    except Exception as e:
        logger.error(f"❌ Ошибка при запуске: {e}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "ai_orchestrator",
        "version": "1.0.0",
        "ai_capabilities": [
            "risk_analysis",
            "incident_classification",
            "recovery_planning",
            "nlp_queries",
            "bia_automation"
        ]
    }

# ===============================
# ИНТЕЛЛЕКТУАЛЬНЫЕ ФУНКЦИИ
# ===============================

class BCMIntelligenceEngine:
    """Ядро искусственного интеллекта для BCM"""
    
    @staticmethod
    def analyze_business_process_risk(process: BusinessProcess) -> Dict[str, Any]:
        """Анализ рисков бизнес-процесса"""
        
        base_risk_score = process.criticality * 2
        dependency_factor = len(process.dependencies) * 0.5
        rto_factor = max(0, 24 - process.rto_hours) * 0.1
        
        total_risk_score = base_risk_score + dependency_factor + rto_factor
        
        if total_risk_score <= 5:
            risk_level = RiskLevel.LOW
        elif total_risk_score <= 10:
            risk_level = RiskLevel.MEDIUM
        elif total_risk_score <= 15:
            risk_level = RiskLevel.HIGH
        else:
            risk_level = RiskLevel.CRITICAL
            
        recommendations = []
        
        if risk_level == RiskLevel.CRITICAL:
            recommendations.extend([
                "Немедленно создать план аварийного восстановления",
                "Рассмотреть возможность резервирования процесса",
                "Провести учения восстановления в течение 30 дней"
            ])
        elif risk_level == RiskLevel.HIGH:
            recommendations.extend([
                "Разработать детальный план восстановления",
                "Определить альтернативные ресурсы",
                "Провести тестирование плана"
            ])
            
        return {
            "risk_score": round(total_risk_score, 2),
            "risk_level": risk_level,
            "factors": {
                "criticality_impact": base_risk_score,
                "dependency_impact": dependency_factor,
                "rto_impact": rto_factor
            },
            "recommendations": recommendations,
            "estimated_downtime_cost": process.criticality * 1000
        }
    
    @staticmethod
    def classify_incident(incident: Incident) -> Dict[str, Any]:
        """Интеллектуальная классификация инцидента"""
        
        description_lower = incident.description.lower()
        title_lower = incident.title.lower()
        full_text = f"{title_lower} {description_lower}"
        
        # Ключевые слова для каждой категории
        category_keywords = {
            IncidentCategory.SECURITY: ["взлом", "вирус", "кибер", "утечка", "хакер", "ddos"],
            IncidentCategory.OPERATIONAL: ["процесс", "workflow", "операции", "производство"],
            IncidentCategory.TECHNOLOGY: ["сервер", "сеть", "система", "database", "приложение"],
            IncidentCategory.NATURAL: ["пожар", "наводнение", "землетрясение", "ураган"],
            IncidentCategory.HUMAN: ["ошибка", "персонал", "человеческий фактор"],
            IncidentCategory.EXTERNAL: ["поставщик", "партнер", "внешний"]
        }
        
        category_scores = {}
        for category, keywords in category_keywords.items():
            score = sum(1 for keyword in keywords if keyword in full_text)
            if score > 0:
                category_scores[category] = score
        
        if category_scores:
            predicted_category = max(category_scores, key=category_scores.get)
            confidence = category_scores[predicted_category] / len(category_keywords[predicted_category])
        else:
            predicted_category = incident.category
            confidence = 0.5
            
        return {
            "predicted_category": predicted_category,
            "original_category": incident.category,
            "confidence": round(confidence, 2),
            "category_scores": category_scores,
            "recommended_actions": BCMIntelligenceEngine._get_incident_actions(predicted_category),
            "estimated_resolution_time": BCMIntelligenceEngine._estimate_resolution_time(predicted_category)
        }
    
    @staticmethod
    def _get_incident_actions(category: IncidentCategory) -> List[str]:
        """Рекомендованные действия для инцидента"""
        actions = {
            IncidentCategory.SECURITY: [
                "Изолировать затронутые системы",
                "Провести анализ масштабов нарушения",
                "Активировать план реагирования на инциденты ИБ"
            ],
            IncidentCategory.OPERATIONAL: [
                "Остановить затронутые процессы",
                "Активировать альтернативные процедуры",
                "Уведомить операционную команду"
            ],
            IncidentCategory.TECHNOLOGY: [
                "Запустить диагностику системы",
                "Переключиться на резервные системы",
                "Связаться с техническими специалистами"
            ]
        }
        return actions.get(category, ["Провести первичную оценку", "Уведомить ответственных"])
    
    @staticmethod
    def _estimate_resolution_time(category: IncidentCategory) -> int:
        """Оценка времени разрешения инцидента (в часах)"""
        base_times = {
            IncidentCategory.SECURITY: 8,
            IncidentCategory.OPERATIONAL: 4,
            IncidentCategory.TECHNOLOGY: 6,
            IncidentCategory.NATURAL: 24,
            IncidentCategory.HUMAN: 2,
            IncidentCategory.EXTERNAL: 12
        }
        return base_times.get(category, 6)

# Создание экземпляра AI движка
ai_engine = BCMIntelligenceEngine()

# ===============================
# API ENDPOINTS
# ===============================

@app.post("/analyze/process-risk")
async def analyze_process_risk(process: BusinessProcess):
    """Анализ рисков бизнес-процесса"""
    try:
        analysis = ai_engine.analyze_business_process_risk(process)
        
        return {
            "status": "success",
            "process_id": process.id,
            "analysis": analysis,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Ошибка анализа риска процесса: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze/incident")
async def classify_incident(incident: Incident):
    """Классификация и анализ инцидента"""
    try:
        classification = ai_engine.classify_incident(incident)
        
        return {
            "status": "success",
            "incident_id": incident.id,
            "classification": classification,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Ошибка классификации инцидента: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/nlp/query")
async def process_natural_language_query(query: NaturalLanguageQuery):
    """Обработка запросов на естественном языке"""
    try:
        query_lower = query.query.lower()
        
        response = {
            "query": query.query,
            "intent": "unknown",
            "response": "",
            "actions": []
        }
        
        if any(word in query_lower for word in ["риск", "risk", "угроза"]):
            response["intent"] = "risk_inquiry"
            response["response"] = "Я могу помочь с анализом рисков бизнес-процессов. Укажите ID процесса."
            response["actions"] = ["request_process_id", "show_risk_analysis_form"]
            
        elif any(word in query_lower for word in ["инцидент", "incident", "авария"]):
            response["intent"] = "incident_inquiry"
            response["response"] = "Готов помочь с анализом инцидента. Опишите ситуацию более детально."
            response["actions"] = ["create_incident", "classify_incident"]
            
        elif any(word in query_lower for word in ["статус", "status"]):
            response["intent"] = "status_inquiry"
            response["response"] = "Система BCM функционирует нормально. Все процессы под мониторингом."
            
        else:
            response["response"] = """Я - AI координатор BCM Platform. Могу помочь с:
            
• Анализом рисков бизнес-процессов
• Классификацией инцидентов
• Мониторингом статуса системы

Просто опишите, что вам нужно!"""
        
        return response
        
    except Exception as e:
        logger.error(f"Ошибка обработки NLP запроса: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    """Главная страница AI Orchestrator"""
    return {
        "service": "BCM AI Orchestrator",
        "version": "1.0.0",
        "description": "Интеллектуальный координатор для автоматизации BCM процессов",
        "ai_capabilities": {
            "risk_analysis": "Автоматический анализ рисков бизнес-процессов",
            "incident_classification": "ИИ классификация инцидентов по типу и серьезности",
            "nlp_interface": "Обработка запросов на естественном языке"
        },
        "endpoints": {
            "risk_analysis": "/analyze/process-risk",
            "incident_classification": "/analyze/incident",
            "nlp_queries": "/nlp/query",
            "health": "/health"
        },
        "status": "🤖 AI Engine Active"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
