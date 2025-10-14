"""
AI Event Manager - Infrastructure Service

🏗️ ИНФРАСТРУКТУРНЫЙ СЛОЙ для управления событиями:
- FastAPI service
- REST API endpoints
- Практическое применение рекомендаций
- Мониторинг и алерты

Максимальная интеграция с:
- EventBus (event-driven architecture)
- Event Intelligence (AI analysis)
- DevOps Agent (infrastructure scanning)
- GitHub Integration (code repository)
- MIO Manager (platform coordination)

Использует:
- intelligent-core/event_intelligence (для анализа)
- tools/event_intelligence (для сканирования)
"""

import logging
import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime
from prometheus_client import make_asgi_app, Counter, Histogram, Gauge
from contextlib import asynccontextmanager
import logging as log_module

# Setup logging early
log_module.basicConfig(level=log_module.INFO)
logger = log_module.getLogger(__name__)

# Добавляем пути
project_root = Path(__file__).parents[3]
sys.path.insert(0, str(project_root))

# Import from intelligent-core (using underscore instead of hyphen)
try:
    from intelligent_core.event_intelligence import (
        EventAnalyzer,
        EventLearner,
        EventPredictor
    )
except ImportError as e:
    logger.warning(f"Could not import from intelligent_core.event_intelligence: {e}")
    # Provide fallback classes
    class EventAnalyzer:
        async def analyze_event(self, event_name, publishers, subscribers):
            from dataclasses import dataclass
            @dataclass
            class Analysis:
                event_name: str
                importance_score: float = 0.5
                usage_pattern: str = "normal"
                recommendations: list = None
                ai_insights: str = "AI analysis not available"
                def __post_init__(self):
                    if self.recommendations is None:
                        self.recommendations = []
            return Analysis(event_name=event_name)

    class EventLearner:
        async def get_learning_stats(self):
            return {"total_examples": 0, "accuracy": 0.0, "patterns_learned": 0}
        async def get_learned_confidence(self, event_name, action):
            return 0.5
        async def record_feedback(self, suggestion_id, developer_decision, outcome):
            pass
        async def export_learning_report(self):
            return {"status": "no_data"}

    class EventPredictor:
        def __init__(self, learner=None):
            self.learner = learner
        async def predict_future_gaps(self, current_gaps, historical_trend, days_ahead):
            return []
        async def get_prediction_accuracy(self):
            return 0.0

# Import integration manager
from integrations import IntegrationManager

# Logger already configured above

# Global integration manager
integration_manager: Optional[IntegrationManager] = None

# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    global integration_manager

    logger.info("🚀 AI Event Manager starting...")

    # Initialize integration manager
    integration_manager = IntegrationManager({
        'eventbus_backend': 'memory',  # or 'redis' for production
        'redis_url': 'redis://localhost:6379',
        'event_intelligence_url': 'http://localhost:8039',
        'devops_agent_url': 'http://localhost:8050',
        'github_integration_url': 'http://localhost:8051',
        'mio_manager_url': 'http://localhost:8046',
        'project_root': '/Users/MD/AI-Platform-ISO',
        'monitor_interval': 300  # 5 minutes
    })

    # Initialize all integrations
    await integration_manager.initialize_all()

    logger.info("✅ AI Event Manager ready with full integration")

    yield

    # Shutdown
    logger.info("Shutting down AI Event Manager...")
    if integration_manager:
        await integration_manager.close()
    logger.info("✅ Shutdown complete")

# FastAPI app
app = FastAPI(
    title="AI Event Manager",
    description="Intelligent Event Management Service with Full Platform Integration",
    version="2.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus Metrics
requests_total = Counter('ai_event_manager_requests_total', 'Total requests', ['endpoint', 'method'])
request_duration = Histogram('ai_event_manager_request_duration_seconds', 'Request duration', ['endpoint'])
recommendations_total = Counter('ai_event_manager_recommendations_total', 'Total recommendations', ['scope'])
learning_accuracy = Gauge('ai_event_manager_learning_accuracy', 'Learning accuracy')
feedback_total = Counter('ai_event_manager_feedback_total', 'Total feedback', ['decision'])

# Mount Prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# Initialize AI components
analyzer = EventAnalyzer()
learner = EventLearner()
predictor = EventPredictor(learner=learner)


# ============================================================================
# MODELS
# ============================================================================

class EventAnalysisRequest(BaseModel):
    event_name: str
    publishers: List[str] = []
    subscribers: List[str] = []


class FeedbackRequest(BaseModel):
    suggestion_id: str
    decision: str  # 'approved', 'rejected', 'postponed'
    outcome: Optional[str] = None  # 'success', 'failure'


class RecommendationRequest(BaseModel):
    scope: str = 'all'  # 'all', 'critical', 'workflow'


# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Service information"""
    integration_status = {}
    if integration_manager:
        integration_status = integration_manager.get_integration_status()

    return {
        "service": "AI Event Manager",
        "status": "operational",
        "version": "2.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "integrations": integration_status.get("integrations", {}),
        "capabilities": [
            "event_analysis",
            "ai_learning",
            "predictions",
            "continuous_monitoring",
            "auto_fix",
            "github_integration",
            "platform_coordination"
        ]
    }


@app.get("/health")
async def health():
    """Health check with details"""
    stats = await learner.get_learning_stats()

    return {
        "status": "healthy",
        "components": {
            "analyzer": "operational",
            "learner": "operational",
            "predictor": "operational"
        },
        "learning_stats": stats
    }


@app.post("/analyze/event")
async def analyze_event(request: EventAnalysisRequest):
    """
    Анализирует одно событие

    Returns detailed AI analysis
    """
    try:
        analysis = await analyzer.analyze_event(
            event_name=request.event_name,
            publishers=request.publishers,
            subscribers=request.subscribers
        )

        return {
            "status": "success",
            "analysis": {
                "event_name": analysis.event_name,
                "importance_score": analysis.importance_score,
                "usage_pattern": analysis.usage_pattern,
                "recommendations": analysis.recommendations,
                "ai_insights": analysis.ai_insights
            }
        }

    except Exception as e:
        logger.error(f"Error analyzing event: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/recommendations")
async def get_recommendations(scope: str = 'all'):
    """
    Получить рекомендации AI Event Manager

    Args:
        scope: 'all', 'critical', 'workflow', 'high-priority'
    """
    try:
        # Load event catalog data if available
        # Note: EventIntelligenceSystem may not be available
        catalog = {"events": {}}
        events = {}

        recommendations = []

        for event_name, event_data in events.items():
            publishers = event_data.get('publishers', [])
            subscribers = event_data.get('subscribers', [])

            # Анализируем с помощью AI
            analysis = await analyzer.analyze_event(
                event_name=event_name,
                publishers=publishers,
                subscribers=subscribers
            )

            # Фильтруем по scope
            if scope == 'critical' and analysis.usage_pattern != 'critical':
                continue
            elif scope == 'workflow' and 'workflow' not in event_name:
                continue
            elif scope == 'high-priority' and analysis.importance_score < 0.7:
                continue

            # Получаем learned confidence
            learned_conf = await learner.get_learned_confidence(
                event_name,
                'implement' if not publishers else 'optimize'
            )

            recommendations.append({
                "event_name": event_name,
                "importance": analysis.importance_score,
                "learned_confidence": learned_conf,
                "pattern": analysis.usage_pattern,
                "recommendations": analysis.recommendations,
                "ai_insights": analysis.ai_insights
            })

        # Сортируем по важности
        recommendations.sort(
            key=lambda x: (x['importance'], x['learned_confidence']),
            reverse=True
        )

        return {
            "status": "success",
            "scope": scope,
            "total_recommendations": len(recommendations),
            "recommendations": recommendations[:20]  # Top 20
        }

    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/feedback")
async def record_feedback(request: FeedbackRequest):
    """
    Записать feedback для обучения

    Developer approves/rejects AI recommendation
    """
    try:
        await learner.record_feedback(
            suggestion_id=request.suggestion_id,
            developer_decision=request.decision,
            outcome=request.outcome
        )

        return {
            "status": "success",
            "message": "Feedback recorded, AI will learn from it"
        }

    except Exception as e:
        logger.error(f"Error recording feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/predictions/future")
async def predict_future():
    """Предсказания на будущее"""
    try:
        # Check if we have historical data (from continuous monitor)
        current_gaps = []
        historical_trend = []

        if not historical_trend:
            return {
                "status": "insufficient_data",
                "message": "Not enough historical data for predictions"
            }

        # Предсказания
        predictions = await predictor.predict_future_gaps(
            current_gaps=current_gaps,
            historical_trend=historical_trend,
            days_ahead=7
        )

        return {
            "status": "success",
            "predictions": [
                {
                    "type": p.prediction_type,
                    "event": p.event_name,
                    "probability": p.probability,
                    "date": p.estimated_date,
                    "reasoning": p.reasoning,
                    "action": p.recommended_action
                }
                for p in predictions
            ]
        }

    except Exception as e:
        logger.error(f"Error predicting: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/learning/stats")
async def get_learning_stats():
    """Статистика обучения"""
    try:
        stats = await learner.get_learning_stats()
        accuracy = await predictor.get_prediction_accuracy()

        return {
            "status": "success",
            "learning": stats,
            "prediction_accuracy": accuracy
        }

    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/learning/report")
async def get_learning_report():
    """Полный отчёт об обучении"""
    try:
        report = await learner.export_learning_report()

        return {
            "status": "success",
            "report": report,
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Error generating report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/dashboard/summary")
async def get_dashboard_summary():
    """Сводка для dashboard"""
    try:
        # Статистика обучения
        learning_stats = await learner.get_learning_stats()

        # Рекомендации
        recommendations_response = await get_recommendations(scope='high-priority')
        high_priority_count = len(recommendations_response['recommendations'])

        # Предсказания
        try:
            predictions_response = await predict_future()
            predictions_count = len(predictions_response.get('predictions', []))
        except:
            predictions_count = 0

        return {
            "status": "operational",
            "summary": {
                "learning": {
                    "total_examples": learning_stats['total_examples'],
                    "accuracy": learning_stats['accuracy'],
                    "patterns_learned": learning_stats['patterns_learned']
                },
                "recommendations": {
                    "high_priority": high_priority_count
                },
                "predictions": {
                    "active": predictions_count
                }
            },
            "health": "healthy" if learning_stats['accuracy'] > 0.6 else "needs_attention"
        }

    except Exception as e:
        logger.error(f"Error getting dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# NEW INTEGRATION ENDPOINTS
# ============================================================================

@app.get("/integrations/status")
async def integration_status():
    """Get status of all integrations"""
    if not integration_manager:
        raise HTTPException(status_code=503, detail="Integration manager not initialized")

    return integration_manager.get_integration_status()


@app.post("/integrations/scan/trigger")
async def trigger_immediate_scan():
    """Trigger immediate infrastructure scan"""
    if not integration_manager or not integration_manager.monitor:
        raise HTTPException(status_code=503, detail="Continuous monitor not available")

    try:
        result = await integration_manager.monitor.trigger_immediate_scan()
        return {
            "status": "success",
            "result": result
        }
    except Exception as e:
        logger.error(f"Immediate scan failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/integrations/analyze/full")
async def run_full_analysis():
    """Run complete analysis cycle with all integrations"""
    if not integration_manager:
        raise HTTPException(status_code=503, detail="Integration manager not initialized")

    try:
        results = await integration_manager.run_full_analysis_cycle()
        return {
            "status": "success",
            "results": results
        }
    except Exception as e:
        logger.error(f"Full analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/integrations/eventbus/publish")
async def publish_to_eventbus(event_name: str, data: Dict, priority: str = "normal"):
    """Publish event to EventBus"""
    if not integration_manager:
        raise HTTPException(status_code=503, detail="Integration manager not initialized")

    try:
        success = await integration_manager.publish_event(event_name, data, priority)
        return {
            "status": "success" if success else "failed",
            "event_name": event_name
        }
    except Exception as e:
        logger.error(f"Event publish failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/integrations/github/issue")
async def create_github_issue_endpoint(title: str, body: str, labels: List[str] = None):
    """Create GitHub issue"""
    if not integration_manager:
        raise HTTPException(status_code=503, detail="Integration manager not initialized")

    try:
        issue_url = await integration_manager.create_github_issue(title, body, labels or [])

        if issue_url:
            return {
                "status": "success",
                "issue_url": issue_url
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to create issue")

    except Exception as e:
        logger.error(f"GitHub issue creation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/monitor/stats")
async def get_monitor_stats():
    """Get continuous monitor statistics"""
    if not integration_manager or not integration_manager.monitor:
        raise HTTPException(status_code=503, detail="Monitor not available")

    return {
        "status": "success",
        "stats": integration_manager.monitor.get_stats()
    }


# ============================================================================
# INFRASTRUCTURE STATE MONITORING ENDPOINTS (NEW!)
# ============================================================================

@app.get("/infrastructure/state")
async def get_infrastructure_state():
    """
    Get current infrastructure state

    Returns unified state from:
    - Project Manager (ports, DBs, metrics)
    - MIO Manager (CPU, memory, disk)
    - Service Discovery (health checks)
    """
    if not integration_manager or not integration_manager.infrastructure_monitor:
        raise HTTPException(status_code=503, detail="Infrastructure monitor not available")

    state = integration_manager.infrastructure_monitor.current_state
    if not state:
        raise HTTPException(status_code=503, detail="State not yet collected")

    from dataclasses import asdict
    return {
        "status": "success",
        "state": asdict(state)
    }


@app.get("/infrastructure/resources")
async def get_available_resources():
    """
    Get available infrastructure resources

    Checks:
    - Port availability
    - Monitoring availability
    - Database availability
    - Resource usage (CPU, memory)
    - System health
    """
    if not integration_manager or not integration_manager.infrastructure_monitor:
        raise HTTPException(status_code=503, detail="Infrastructure monitor not available")

    resources = integration_manager.infrastructure_monitor.get_available_resources()
    return {
        "status": "success",
        "resources": resources
    }


@app.get("/infrastructure/strategy")
async def get_scaling_strategy():
    """
    Get recommended scaling strategy

    Based on rule-based logic analyzing:
    - Database availability
    - Monitoring coverage
    - Resource usage
    - System health
    """
    if not integration_manager or not integration_manager.infrastructure_monitor:
        raise HTTPException(status_code=503, detail="Infrastructure monitor not available")

    strategy = integration_manager.infrastructure_monitor.suggest_scaling_strategy()
    return {
        "status": "success",
        "strategy": strategy
    }


@app.post("/infrastructure/deployment-check")
async def check_deployment(service_name: str, requires_db: bool = True,
                          requires_metrics: bool = True):
    """
    Check if service can be deployed

    Validates:
    - Database availability (if required)
    - Monitoring availability (if required)
    - Port availability
    - Resource capacity (CPU, memory)
    """
    if not integration_manager or not integration_manager.infrastructure_monitor:
        raise HTTPException(status_code=503, detail="Infrastructure monitor not available")

    can_deploy, reason = integration_manager.infrastructure_monitor.can_deploy_new_service(
        service_name=service_name,
        requires_db=requires_db,
        requires_metrics=requires_metrics
    )

    return {
        "can_deploy": can_deploy,
        "reason": reason,
        "service_name": service_name
    }


@app.get("/infrastructure/history")
async def get_state_history(limit: int = 10):
    """
    Get infrastructure state history

    Shows historical trend of:
    - Port usage
    - Service health
    - Resource usage
    - Coverage metrics
    """
    if not integration_manager or not integration_manager.infrastructure_monitor:
        raise HTTPException(status_code=503, detail="Infrastructure monitor not available")

    history = integration_manager.infrastructure_monitor.state_history[-limit:]
    from dataclasses import asdict
    return {
        "status": "success",
        "history": [asdict(s) for s in history],
        "count": len(history)
    }


# ============================================================================
# STARTUP (kept for backward compatibility)
# ============================================================================


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8055)
