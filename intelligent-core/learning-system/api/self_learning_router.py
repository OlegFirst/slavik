"""
Self-Learning API Router

Endpoints для самообучения системы, сбора потребностей, интеграции с KB
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel
from datetime import datetime

from engines.learning_needs_collector import LearningNeedsCollector
from engines.knowledge_base_connector import (
    EnhancedKnowledgeIntegrator,
    KnowledgeBaseClient
)
from engines.self_learning_engine import SelfLearningEngine

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize engines
needs_collector = LearningNeedsCollector()
kb_integrator = EnhancedKnowledgeIntegrator(kb_base_url="http://localhost:8040")
self_learning = SelfLearningEngine()


# =====================================================
# Request/Response Models
# =====================================================

class CollectNeedsRequest(BaseModel):
    """Request for collecting learning needs"""
    exercise_results: Optional[List[dict]] = None
    user_competencies: Optional[List[dict]] = None
    user_requests: Optional[List[dict]] = None
    industry_benchmarks: Optional[dict] = None


class PredictionRecordRequest(BaseModel):
    """Request to record a prediction"""
    prediction_id: str
    predicted_score: float
    confidence: float
    model_version: str
    features_used: dict
    scenario_type: str
    team_id: Optional[str] = None


class OutcomeRecordRequest(BaseModel):
    """Request to record actual outcome"""
    prediction_id: str
    actual_score: float
    exercise_completed: bool
    exercise_id: str


class CreateLearningPathRequest(BaseModel):
    """Request to create learning path from KB"""
    user_id: str
    competency_gap: dict


# =====================================================
# Learning Needs Collection Endpoints
# =====================================================

@router.post("/needs/collect")
async def collect_learning_needs(request: CollectNeedsRequest):
    """
    Собрать потребности в обучении из всех источников

    Источники:
    - Exercise results (gaps → needs)
    - User competencies (low scores → needs)
    - ISO requirements (compliance → needs)
    - User requests (explicit needs)
    - Industry benchmarks (gaps to industry → needs)

    Returns:
        {
            'needs': [...],
            'prioritized_needs': [...],
            'training_plan': {...},
            'statistics': {...}
        }
    """
    try:
        result = needs_collector.collect_all_needs(
            exercise_results=request.exercise_results,
            user_competencies=request.user_competencies,
            user_requests=request.user_requests,
            industry_benchmarks=request.industry_benchmarks
        )

        return result

    except Exception as e:
        logger.error(f"Error collecting needs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/needs/training-plan")
async def get_training_plan(
    tenant_id: str = Query(..., description="Tenant ID")
):
    """
    Получить актуальный training plan

    TODO: Fetch from database
    """
    return {
        "message": "Training plan endpoint",
        "tenant_id": tenant_id,
        "note": "Database fetch not yet implemented"
    }


# =====================================================
# Knowledge Base Integration Endpoints
# =====================================================

@router.get("/kb/search")
async def search_knowledge_base(
    query: str = Query(..., description="Search query"),
    limit: int = Query(10, description="Max results")
):
    """
    Поиск в Knowledge Base

    Реальный поиск через KB Service
    """
    try:
        resources = await kb_integrator.fetch_resources_for_gap(
            gap_keyword=query,
            limit=limit
        )

        return {
            'query': query,
            'results': resources,
            'total': len(resources)
        }

    except Exception as e:
        logger.error(f"KB search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/kb/create-learning-path")
async def create_learning_path_from_kb(request: CreateLearningPathRequest):
    """
    Создать learning path из Knowledge Base

    На основе реальных ресурсов из KB
    """
    try:
        learning_path = await kb_integrator.create_learning_path_from_kb(
            user_id=request.user_id,
            competency_gap=request.competency_gap
        )

        return learning_path

    except Exception as e:
        logger.error(f"Error creating learning path: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/kb/auto-create-from-patterns")
async def auto_create_knowledge(
    patterns: List[dict],
    background_tasks: BackgroundTasks
):
    """
    Автоматически создать статьи из паттернов

    Паттерны с частотой >=5 → новые статьи в KB
    """
    try:
        # Run in background
        background_tasks.add_task(
            kb_integrator.auto_create_knowledge_from_patterns,
            patterns
        )

        return {
            'message': 'Auto-creation started',
            'patterns_count': len(patterns),
            'status': 'processing'
        }

    except Exception as e:
        logger.error(f"Error auto-creating knowledge: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/kb/sync-external")
async def sync_external_knowledge(background_tasks: BackgroundTasks):
    """
    Синхронизировать с внешними источниками знаний

    Источники:
    - ISO standards updates
    - Threat intelligence feeds
    - Industry best practices
    """
    try:
        # Run in background
        background_tasks.add_task(
            kb_integrator.sync_external_knowledge
        )

        return {
            'message': 'External knowledge sync started',
            'status': 'processing'
        }

    except Exception as e:
        logger.error(f"Error syncing external knowledge: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =====================================================
# Self-Learning Endpoints
# =====================================================

@router.post("/self-learn/record-prediction")
async def record_prediction(request: PredictionRecordRequest):
    """
    Записать предсказание ML модели

    Шаг 1 feedback loop
    """
    try:
        success = self_learning.record_prediction(
            prediction_id=request.prediction_id,
            prediction_data={
                'predicted_score': request.predicted_score,
                'confidence': request.confidence,
                'model_version': request.model_version,
                'features_used': request.features_used,
                'scenario_type': request.scenario_type,
                'team_id': request.team_id
            }
        )

        if success:
            return {
                'status': 'success',
                'prediction_id': request.prediction_id,
                'message': 'Prediction recorded'
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to record prediction")

    except Exception as e:
        logger.error(f"Error recording prediction: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/self-learn/record-outcome")
async def record_outcome(request: OutcomeRecordRequest):
    """
    Записать реальный результат

    Шаг 2 feedback loop - триггерит обучение модели
    """
    try:
        success = self_learning.record_actual_outcome(
            prediction_id=request.prediction_id,
            actual_data={
                'actual_score': request.actual_score,
                'exercise_completed': request.exercise_completed,
                'exercise_id': request.exercise_id
            }
        )

        if success:
            return {
                'status': 'success',
                'prediction_id': request.prediction_id,
                'message': 'Outcome recorded and model learning triggered'
            }
        else:
            raise HTTPException(status_code=404, detail="Prediction not found")

    except Exception as e:
        logger.error(f"Error recording outcome: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/self-learn/effectiveness")
async def analyze_learning_effectiveness():
    """
    Анализ эффективности самообучения

    Метрики:
    - Снижение ошибки со временем
    - Улучшение модели
    - Performance по версиям
    """
    try:
        analysis = self_learning.analyze_learning_effectiveness()
        return analysis

    except Exception as e:
        logger.error(f"Error analyzing effectiveness: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/self-learn/accuracy-report")
async def get_accuracy_report():
    """
    Отчет о точности предсказаний

    Breakdown:
    - By scenario type
    - By error type (over/under)
    - By time period
    """
    try:
        report = self_learning.get_prediction_accuracy_report()
        return report

    except Exception as e:
        logger.error(f"Error generating accuracy report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/self-learn/predictions")
async def get_predictions(
    status: str = Query('completed', description="pending, completed, all"),
    limit: int = Query(50, description="Max predictions to return")
):
    """
    Получить список предсказаний

    Для review и анализа
    """
    try:
        predictions = self_learning.get_predictions_for_review(
            status=status,
            limit=limit
        )

        return {
            'predictions': predictions,
            'total': len(predictions),
            'status_filter': status
        }

    except Exception as e:
        logger.error(f"Error getting predictions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/self-learn/feature-importance")
async def get_feature_importance():
    """
    Анализ важности фич

    Какие фичи больше всего влияют на точность предсказаний?
    """
    try:
        importance = self_learning.get_feature_importance()

        return {
            'feature_importance': importance,
            'note': 'Higher score = more important feature'
        }

    except Exception as e:
        logger.error(f"Error analyzing feature importance: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/self-learn/export-training-data")
async def export_training_data():
    """
    Export training data для offline анализа

    Возвращает dataset для ML training
    """
    try:
        dataset = self_learning.export_training_data()
        return dataset

    except Exception as e:
        logger.error(f"Error exporting training data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/self-learn/trigger-retrain")
async def trigger_model_retrain():
    """
    Manually trigger model retraining

    Обычно происходит автоматически при достижении threshold
    """
    try:
        # Force retrain
        self_learning._retrain_model()

        return {
            'status': 'success',
            'message': 'Model retraining triggered',
            'current_version': self_learning.current_model_version
        }

    except Exception as e:
        logger.error(f"Error triggering retrain: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =====================================================
# Combined Workflow Endpoints
# =====================================================

@router.post("/workflow/full-cycle")
async def run_full_learning_cycle(
    exercise_results: List[dict],
    user_competencies: List[dict],
    background_tasks: BackgroundTasks
):
    """
    Запустить полный цикл обучения

    1. Collect needs
    2. Search KB for resources
    3. Create learning paths
    4. Auto-create missing knowledge
    5. Sync external sources

    Returns immediate response, processing in background
    """
    try:
        # Step 1: Collect needs
        needs_result = needs_collector.collect_all_needs(
            exercise_results=exercise_results,
            user_competencies=user_competencies
        )

        # Background tasks
        background_tasks.add_task(
            _process_learning_cycle,
            needs_result
        )

        return {
            'status': 'started',
            'needs_collected': len(needs_result['needs']),
            'training_plan': needs_result['training_plan']['summary'],
            'message': 'Full learning cycle started in background'
        }

    except Exception as e:
        logger.error(f"Error running full cycle: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def _process_learning_cycle(needs_result: dict):
    """Background task для полного цикла"""
    try:
        logger.info("🔄 Processing full learning cycle...")

        # Step 2-3: Create learning paths from KB
        for need in needs_result['prioritized_needs'][:10]:  # Top 10
            if 'user_id' in need:
                await kb_integrator.create_learning_path_from_kb(
                    user_id=need['user_id'],
                    competency_gap=need
                )

        # Step 4: Auto-create knowledge
        # (patterns would be fetched from DB)

        # Step 5: Sync external
        await kb_integrator.sync_external_knowledge()

        logger.info("✅ Full learning cycle complete")

    except Exception as e:
        logger.error(f"Error in learning cycle: {e}")
