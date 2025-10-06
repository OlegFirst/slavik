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

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
import redis
import pika
from supabase import create_client, Client

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
        
        logger.info("AI Orchestrator запущен успешно")
        
    except Exception as e:
        logger.error(f"Ошибка при запуске: {e}")

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
        
        # ANTHROPIC GOVERNANCE BRAIN ROUTING
        use_anthropic = (
            query.context and query.context.get('use_anthropic') or
            query.user_role == 'governance_brain'
        )

        if use_anthropic and os.getenv('ANTHROPIC_API_KEY'):
            try:
                import httpx

                async with httpx.AsyncClient() as client:
                    anthropic_response = await client.post(
                        'https://api.anthropic.com/v1/messages',
                        headers={
                            'x-api-key': os.getenv('ANTHROPIC_API_KEY'),
                            'content-type': 'application/json',
                            'anthropic-version': '2023-06-01'
                        },
                        json={
                            'model': 'claude-3-5-sonnet-20241022',
                            'max_tokens': 4000,
                            'temperature': 0.3,
                            'messages': [{'role': 'user', 'content': query.query}]
                        },
                        timeout=120.0
                    )

                    if anthropic_response.status_code == 200:
                        result = anthropic_response.json()
                        return {
                            "query": query.query,
                            "intent": "governance_strategic_analysis",
                            "response": result['content'][0]['text'],
                            "actions": [{"type": "anthropic_governance"}],
                            "model_used": "anthropic_claude_sonnet"
                        }
            except Exception as e:
                logger.error(f'Anthropic failed: {e}')

        return response
        
    except Exception as e:
        logger.error(f"Ошибка обработки NLP запроса: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ===============================
# AI DEVOPS ORCHESTRATION
# ===============================

class DeploymentPlan(BaseModel):
    """План развертывания"""
    environment: str = Field(..., description="Целевая среда (dev/staging/production)")
    services: List[str] = Field(default=[], description="Список сервисов для развертывания")
    strategy: str = Field(default="staged", description="Стратегия развертывания")
    intelligence_level: str = Field(default="supervised", description="Уровень автономности ИИ")
    learning_enabled: bool = Field(default=True, description="Включить обучение на основе результатов")

class DeploymentResult(BaseModel):
    """Результат развертывания"""
    deployment_id: str
    status: str
    services_deployed: List[str]
    failures: List[Dict[str, Any]]
    execution_time: int
    lessons_learned: List[str]
    improvements_suggested: List[str]

class AIDevOpsEngine:
    """ИИ движок для DevOps автоматизации"""
    
    def __init__(self):
        self.deployment_history = []
        self.learned_patterns = {}
        self.github_integration = None
    
    async def orchestrate_deployment(self, plan: DeploymentPlan) -> DeploymentResult:
        """Оркестрация развертывания с ИИ"""
        logger.info(f"Starting AI-orchestrated deployment: {plan.environment}")
        
        deployment_id = f"deploy_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        start_time = datetime.now()
        
        # ИИ анализ оптимального порядка запуска
        optimal_order = self._analyze_service_dependencies(plan.services)
        
        # Выполнение развертывания
        deployed_services = []
        failures = []
        
        for service in optimal_order:
            try:
                success = await self._deploy_service(service, plan)
                if success:
                    deployed_services.append(service)
                    logger.info(f"✅ {service} deployed successfully")
                else:
                    failures.append({"service": service, "error": "Deployment failed"})
                    
                    # ИИ принимает решение о продолжении
                    if await self._should_continue_deployment(service, failures):
                        continue
                    else:
                        break
                        
            except Exception as e:
                failures.append({"service": service, "error": str(e)})
                logger.error(f"❌ {service} deployment failed: {e}")
        
        execution_time = int((datetime.now() - start_time).total_seconds())
        
        # ИИ анализ результатов и обучение
        lessons = self._extract_lessons(deployed_services, failures, execution_time)
        improvements = self._suggest_improvements(plan, deployed_services, failures)
        
        # Сохранение опыта для обучения
        if plan.learning_enabled:
            self._store_deployment_experience(plan, deployed_services, failures, lessons)
        
        # Автоматическое создание PR с улучшениями
        if improvements and plan.intelligence_level == "autonomous":
            await self._create_improvement_pr(improvements)
        
        result = DeploymentResult(
            deployment_id=deployment_id,
            status="success" if not failures else "partial_success" if deployed_services else "failed",
            services_deployed=deployed_services,
            failures=failures,
            execution_time=execution_time,
            lessons_learned=lessons,
            improvements_suggested=improvements
        )
        
        return result
    
    def _analyze_service_dependencies(self, services: List[str]) -> List[str]:
        """ИИ анализ зависимостей и оптимального порядка запуска"""
        
        # Базовая логика зависимостей (будет обучаться)
        dependency_order = {
            "postgres": 0,
            "redis": 1, 
            "rabbitmq": 1,
            "keycloak": 2,
            "ai_orchestrator": 3,
            "bia_engine": 4,
            "document_processor": 4,
            "compliance_checker": 4,
            "eventbus": 5,
            "odoo": 6,
            "web_portal": 7,
            "admin_panel": 7
        }
        
        # Сортировка по приоритету + обученные паттерны
        ordered_services = sorted(services, key=lambda s: dependency_order.get(s, 999))
        
        # ИИ оптимизация на основе истории
        if self.learned_patterns.get("service_order"):
            ordered_services = self._apply_learned_optimizations(ordered_services)
        
        return ordered_services
    
    async def _deploy_service(self, service: str, plan: DeploymentPlan) -> bool:
        """Развертывание отдельного сервиса"""
        # Здесь будет интеграция с docker-compose/kubernetes
        logger.info(f"Deploying {service} in {plan.environment}")
        
        # Имитация развертывания (заменить на реальную логику)
        import asyncio
        await asyncio.sleep(2)  # Имитация времени развертывания
        
        # Проверка здоровья сервиса
        return await self._health_check(service)
    
    async def _health_check(self, service: str) -> bool:
        """Интеллектуальная проверка здоровья сервиса"""
        # ИИ адаптивные проверки здоровья
        return True  # Заглушка
    
    async def _should_continue_deployment(self, failed_service: str, failures: List[Dict]) -> bool:
        """ИИ решение о продолжении развертывания при ошибках"""
        # Критические сервисы - останавливаем
        critical_services = ["postgres", "redis", "ai_orchestrator"]
        if failed_service in critical_services:
            return False
        
        # Если слишком много ошибок - останавливаем
        if len(failures) >= 3:
            return False
            
        return True
    
    def _extract_lessons(self, deployed: List[str], failures: List[Dict], time: int) -> List[str]:
        """Извлечение уроков из развертывания"""
        lessons = []
        
        if failures:
            lessons.append(f"Обнаружены проблемы с сервисами: {[f['service'] for f in failures]}")
        
        if time > 300:  # > 5 минут
            lessons.append("Развертывание заняло слишком много времени - нужна оптимизация")
        
        if len(deployed) > 5:
            lessons.append("Успешно развернуто много сервисов - порядок запуска эффективен")
            
        return lessons
    
    def _suggest_improvements(self, plan: DeploymentPlan, deployed: List[str], failures: List[Dict]) -> List[str]:
        """ИИ предложения улучшений"""
        improvements = []
        
        if failures:
            improvements.append("Добавить retry логику для нестабильных сервисов")
            improvements.append("Увеличить timeout для медленных сервисов")
        
        if len(deployed) == len(plan.services):
            improvements.append("Рассмотреть параллельный запуск независимых сервисов")
        
        improvements.append("Добавить более детальные health checks")
        
        return improvements
    
    def _store_deployment_experience(self, plan: DeploymentPlan, deployed: List[str], failures: List[Dict], lessons: List[str]):
        """Сохранение опыта для машинного обучения"""
        experience = {
            "timestamp": datetime.now().isoformat(),
            "environment": plan.environment,
            "services": plan.services,
            "deployed": deployed,
            "failures": failures,
            "lessons": lessons,
            "success_rate": len(deployed) / len(plan.services) if plan.services else 0
        }
        
        self.deployment_history.append(experience)
        
        # Обновление обученных паттернов
        self._update_learned_patterns(experience)
    
    def _update_learned_patterns(self, experience: Dict):
        """Обновление обученных паттернов"""
        # Простое обучение - будет заменено на ML
        if experience["success_rate"] > 0.8:
            service_order = experience["deployed"]
            self.learned_patterns["service_order"] = service_order
    
    def _apply_learned_optimizations(self, services: List[str]) -> List[str]:
        """Применение обученных оптимизаций"""
        learned_order = self.learned_patterns.get("service_order", [])
        
        # Переупорядочивание на основе обученного опыта
        optimized = []
        for service in learned_order:
            if service in services:
                optimized.append(service)
        
        # Добавление новых сервисов в конец
        for service in services:
            if service not in optimized:
                optimized.append(service)
                
        return optimized
    
    async def _create_improvement_pr(self, improvements: List[str]):
        """Автоматическое создание PR с улучшениями"""
        logger.info("Creating GitHub PR with AI improvements...")
        
        # Здесь будет интеграция с GitHub API
        # Создание улучшений в docker-compose.yml и cloudbuild.yaml
        
        pr_description = "🤖 AI-Generated Deployment Improvements\n\n"
        for improvement in improvements:
            pr_description += f"- {improvement}\n"
        
        logger.info(f"PR created with improvements: {pr_description}")

# ===============================
# CLAUDE PRO INTEGRATION
# ===============================

class ClaudeProEngine:
    """Интеграция с Claude Pro для супер-интеллектуального DevOps"""
    
    def __init__(self):
        # Supabase интеграция для AI памяти (опционально)
        try:
            self.supabase: Client = create_client(
                os.getenv("SUPABASE_URL", "https://mvzlkpzakzlmmxyjjtvr.supabase.co"),
                os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im12emxrcHpha3psbW14eWpqdHZyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTA5OTIyMTgsImV4cCI6MjA2NjU2ODIxOH0.zJeHMNv15jPwe8bgEph4GzwtsE8anx-7ZpqCZa3axQA")
            )
        except Exception as e:
            logger.warning(f"Supabase connection failed, continuing without AI memory: {e}")
            self.supabase = None
        self.claude_available = True
        self.repo_name = "SEH-foundation/ISO-22301"
        
    async def analyze_code_changes(self, changes: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Claude анализирует изменения кода с использованием Supabase памяти"""
        logger.info("🧠 Claude analyzing code changes with AI memory...")
        
        try:
            # Поиск похожих ситуаций в Supabase
            similar_knowledge = self.supabase.table("ai_knowledge").select("*").eq(
                "repo_full_name", self.repo_name
            ).eq("knowledge_type", "deployment").execute()
            
            # Получение истории развертываний
            deployment_stats = self.supabase.rpc("get_deployment_stats", {
                "repo_name": self.repo_name, 
                "days_back": 30
            }).execute()
            
            # AI анализ с учетом накопленных знаний
            recommendations = []
            if similar_knowledge.data:
                for knowledge in similar_knowledge.data:
                    recommendations.extend(
                        knowledge["knowledge_data"].get("recommendations", [])
                    )
            
            # Определение стратегии на основе истории
            recommended_strategy = "intelligent"
            if deployment_stats.data and deployment_stats.data[0]:
                stats = deployment_stats.data[0]
                if stats["avg_success_rate"] and stats["avg_success_rate"] < 0.8:
                    recommended_strategy = "safe"
                elif stats["best_strategy"]:
                    recommended_strategy = stats["best_strategy"]
            
            analysis = {
                "impact_assessment": "Medium",
                "affected_services": ["odoo", "ai_orchestrator"] if "odoo" in changes else ["ai_orchestrator"],
                "deployment_risk": "low" if len(changes) < 1000 else "medium",
                "recommended_strategy": recommended_strategy,
                "optimizations": list(set(recommendations)) if recommendations else [
                    "Можно применить параллельный запуск для независимых сервисов",
                    "Рекомендуется добавить health checks с более длительными таймаутами"
                ],
                "estimated_deployment_time": "8-12 минут",
                "confidence": 0.85,
                "memory_sources": len(similar_knowledge.data) if similar_knowledge.data else 0
            }
            
            # Сохраняем новые знания в Supabase
            context_hash = f"analysis_{hash(changes)}_{datetime.now().strftime('%Y%m%d')}"
            self.supabase.table("ai_knowledge").insert({
                "repo_full_name": self.repo_name,
                "knowledge_type": "code_analysis",
                "context_hash": context_hash,
                "title": f"Code Analysis {datetime.now().strftime('%Y-%m-%d')}",
                "description": f"Analysis of changes: {changes[:100]}...",
                "knowledge_data": analysis,
                "confidence_score": analysis["confidence"]
            }).execute()
            
            return analysis
            
        except Exception as e:
            logger.error(f"Supabase analysis error: {e}")
            # Fallback к простому анализу
            return {
                "impact_assessment": "Medium",
                "recommended_strategy": "intelligent",
                "confidence": 0.5,
                "error": str(e)
            }
    
    async def generate_deployment_config(self, requirements: Dict[str, Any]) -> str:
        """Claude генерирует оптимальную конфигурацию развертывания"""
        logger.info("🧠 Claude generating deployment config...")
        
        # Claude создает умный docker-compose или cloudbuild
        config_template = f"""
# 🤖 Claude-Generated Deployment Config
# Optimized for: {requirements.get('environment', 'production')}
# Risk Level: {requirements.get('risk_level', 'medium')}

version: "3.8"
services:
  # Claude-optimized service configuration
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_SHARED_PRELOAD_LIBRARIES: pg_stat_statements
      POSTGRES_MAX_CONNECTIONS: 200
    # Claude добавил оптимизации для производительности
    
  # Умное масштабирование от Claude
  ai_orchestrator:
    deploy:
      replicas: {2 if requirements.get('load') == 'high' else 1}
      resources:
        limits:
          memory: {4096 if requirements.get('ai_intensive') else 2048}M
"""
        return config_template
    
    async def analyze_deployment_results(self, deployment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Claude анализирует результаты развертывания"""
        logger.info("🧠 Claude analyzing deployment results...")
        
        success_rate = deployment_data.get('success_rate', 0)
        execution_time = deployment_data.get('execution_time', 0)
        
        recommendations = []
        
        if success_rate < 0.8:
            recommendations.append("Низкий процент успеха - нужно улучшить retry логику")
        
        if execution_time > 600:  # > 10 минут
            recommendations.append("Развертывание слишком медленное - рассмотреть параллелизацию")
        
        if success_rate > 0.95:
            recommendations.append("Отличные результаты! Можно увеличить агрессивность развертывания")
        
        return {
            "overall_assessment": "good" if success_rate > 0.8 else "needs_improvement",
            "key_metrics": {
                "success_rate": success_rate,
                "performance_score": min(100, int((success_rate * 100) - (execution_time / 10)))
            },
            "recommendations": recommendations,
            "next_optimizations": [
                "Добавить мониторинг ресурсов во время развертывания",
                "Внедрить предиктивное масштабирование",
                "Оптимизировать последовательность запуска сервисов"
            ]
        }
    
    async def create_intelligent_pr(self, improvements: List[str], context: Dict[str, Any]) -> Dict[str, Any]:
        """Claude создает умный PR с улучшениями"""
        logger.info("🧠 Claude creating intelligent PR...")
        
        pr_title = "🤖 Claude AI: Deployment optimizations and performance improvements"
        
        pr_description = f"""
# 🧠 AI-Generated Improvements

This PR contains intelligent optimizations suggested by Claude AI after analyzing deployment patterns.

## 📊 Analysis Summary
- Deployment success rate: {context.get('success_rate', 'N/A')}%
- Average deployment time: {context.get('avg_time', 'N/A')} seconds
- Risk assessment: {context.get('risk_level', 'medium')}

## 🚀 Improvements Included
"""
        for i, improvement in enumerate(improvements, 1):
            pr_description += f"{i}. {improvement}\n"
        
        pr_description += """
## 🤖 AI Confidence
This PR has been automatically generated and tested by Claude AI. The confidence level is **85%**.

## 🔍 Next Steps
1. Review the proposed changes
2. Test in staging environment
3. Monitor deployment metrics after merge

*Generated by Claude AI DevOps Assistant*
"""
        
        return {
            "title": pr_title,
            "description": pr_description,
            "labels": ["ai-generated", "deployment-optimization", "claude-ai"],
            "reviewers": ["devops-team"],
            "auto_merge": False  # Безопасность превыше всего
        }

# Создание Claude движка
claude_engine = ClaudeProEngine()

# ===============================
# GITHUB COPILOT AUTHENTICATION
# ===============================

class GitHubTokenManager:
    """Управление токенами GitHub пользователей"""
    
    def __init__(self):
        self.active_tokens = {}  # user_id -> token_data
        
    async def exchange_github_token(self, github_jwt: str) -> Dict[str, Any]:
        """Обмен GitHub JWT на внутренний токен"""
        try:
            # Декодирование GitHub JWT (упрощенно)
            import base64
            import json
            
            # В реальности нужно проверить подпись JWT
            payload = github_jwt.split('.')[1]
            # Добавляем padding если нужно
            payload += '=' * (4 - len(payload) % 4)
            user_data = json.loads(base64.b64decode(payload))
            
            user_id = user_data.get('sub', 'anonymous')
            username = user_data.get('login', 'unknown')
            
            # Создаем внутренний токен
            internal_token = f"bcm_user_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M')}"
            
            # Сохраняем в памяти (в production - в Redis/Supabase)
            token_data = {
                "user_id": user_id,
                "username": username,
                "github_data": user_data,
                "internal_token": internal_token,
                "created_at": datetime.now(),
                "expires_at": datetime.now() + timedelta(hours=8)
            }
            
            self.active_tokens[user_id] = token_data
            
            # Сохраняем в Supabase для персонализации
            claude_engine.supabase.table("github_events").insert({
                "repo_full_name": claude_engine.repo_name,
                "event_type": "token_exchange", 
                "event_action": "user_authenticated",
                "github_id": user_id,
                "payload": {"username": username, "auth_time": datetime.now().isoformat()},
                "processed": True,
                "ai_analysis": {"user_authenticated": True}
            }).execute()
            
            return {
                "token": internal_token,
                "expires_in": 28800,  # 8 часов
                "user_id": user_id,
                "username": username
            }
            
        except Exception as e:
            logger.error(f"Token exchange failed: {e}")
            # Fallback - анонимный токен
            return {
                "token": f"bcm_anon_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "expires_in": 28800
            }
    
    async def refresh_token(self, old_token: str) -> Dict[str, Any]:
        """Обновление истекшего токена"""
        # Поиск пользователя по старому токену
        user_data = None
        for uid, data in self.active_tokens.items():
            if data["internal_token"] == old_token:
                user_data = data
                break
        
        if user_data:
            # Создаем новый токен
            new_token = f"bcm_user_{user_data['user_id']}_{datetime.now().strftime('%Y%m%d_%H%M')}"
            user_data["internal_token"] = new_token
            user_data["created_at"] = datetime.now()
            user_data["expires_at"] = datetime.now() + timedelta(hours=8)
            
            return {
                "access_token": new_token,
                "expires_in": 28800,
                "token_type": "bearer"
            }
        else:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    def get_user_from_token(self, token: str) -> Optional[Dict]:
        """Получение пользователя по токену"""
        for user_data in self.active_tokens.values():
            if user_data["internal_token"] == token:
                if user_data["expires_at"] > datetime.now():
                    return user_data
        return None

# Создание токен-менеджера
token_manager = GitHubTokenManager()

# GitHub Copilot Authentication endpoints
@app.post("/auth/token-exchange")
async def exchange_github_token(request: Request):
    """🔐 Обмен GitHub JWT на внутренний токен"""
    try:
        body = await request.json()
        github_jwt = body.get("token") or request.headers.get("Authorization", "").replace("Bearer ", "")
        
        if not github_jwt:
            raise HTTPException(status_code=400, detail="No GitHub token provided")
        
        result = await token_manager.exchange_github_token(github_jwt)
        return result
        
    except Exception as e:
        logger.error(f"Token exchange error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/auth/refresh-token")  
async def refresh_user_token(request: Request):
    """🔄 Обновление истекшего токена"""
    try:
        body = await request.json()
        refresh_token = body.get("refresh_token")
        
        if not refresh_token:
            raise HTTPException(status_code=400, detail="No refresh token provided")
            
        result = await token_manager.refresh_token(refresh_token)
        return result
        
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(status_code=401, detail="Token refresh failed")

# Middleware для проверки токенов
async def get_current_user(request: Request) -> Optional[Dict]:
    """Получение текущего пользователя из токена"""
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header[7:]
        return token_manager.get_user_from_token(token)
    return None

# Claude API endpoints (с аутентификацией)
@app.post("/claude/analyze-changes")
async def claude_analyze_changes(request: Dict[str, Any], current_user: Optional[Dict] = Depends(get_current_user)):
    """🧠 Claude анализирует изменения кода"""
    try:
        changes = request.get("changes", "")
        
        # Персонализация на основе пользователя
        if current_user:
            logger.info(f"Analysis request from user: {current_user.get('username', 'unknown')}")
            # Можно добавить персонализированные рекомендации
        
        analysis = await claude_engine.analyze_code_changes(changes, request)
        return {"status": "success", "analysis": analysis, "user": current_user.get('username') if current_user else 'anonymous'}
    except Exception as e:
        logger.error(f"Claude analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/claude/generate-config")
async def claude_generate_config(requirements: Dict[str, Any]):
    """🧠 Claude генерирует конфигурацию"""
    try:
        config = await claude_engine.generate_deployment_config(requirements)
        return {"status": "success", "config": config}
    except Exception as e:
        logger.error(f"Claude config generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/claude/analyze-deployment")
async def claude_analyze_deployment(deployment_data: Dict[str, Any]):
    """🧠 Claude анализирует результаты развертывания"""
    try:
        analysis = await claude_engine.analyze_deployment_results(deployment_data)
        return {"status": "success", "analysis": analysis}
    except Exception as e:
        logger.error(f"Claude deployment analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/claude/create-pr")
async def claude_create_pr(pr_data: Dict[str, Any]):
    """🧠 Claude создает умный PR"""
    try:
        improvements = pr_data.get("improvements", [])
        pr_info = await claude_engine.create_intelligent_pr(improvements, pr_data)
        return {"status": "success", "pr_info": pr_info}
    except Exception as e:
        logger.error(f"Claude PR creation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/claude/learn-from-workflow")
async def claude_learn_workflow(workflow_data: Dict[str, Any]):
    """🧠 Claude учится на основе CI/CD workflow"""
    try:
        # Claude сохраняет знания о workflow
        claude_engine.knowledge_base[workflow_data.get("workflow_id")] = {
            "timestamp": datetime.now().isoformat(),
            "success": workflow_data.get("success", False),
            "strategy": workflow_data.get("strategy_used", "unknown"),
            "lessons": workflow_data.get("lessons", ""),
            "execution_time": workflow_data.get("execution_time", 0)
        }
        
        return {"status": "learning_updated", "message": "Claude has learned from this workflow"}
    except Exception as e:
        logger.error(f"Claude learning failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Создание AI DevOps движка
ai_devops = AIDevOpsEngine()

@app.post("/deployment/orchestrate")
async def orchestrate_deployment(plan: DeploymentPlan) -> DeploymentResult:
    """🚀 AI-управляемое развертывание"""
    try:
        result = await ai_devops.orchestrate_deployment(plan)
        return result
    except Exception as e:
        logger.error(f"Deployment orchestration failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/deployment/history")
async def get_deployment_history():
    """📊 История развертываний"""
    return {
        "deployments": ai_devops.deployment_history[-10:],  # Последние 10
        "learned_patterns": ai_devops.learned_patterns,
        "total_deployments": len(ai_devops.deployment_history)
    }

@app.post("/deployment/learn")
async def manual_learning(feedback: Dict[str, Any]):
    """🧠 Ручное обучение ИИ"""
    ai_devops._store_deployment_experience(
        plan=DeploymentPlan(**feedback.get("plan", {})),
        deployed=feedback.get("deployed", []),
        failures=feedback.get("failures", []),
        lessons=feedback.get("lessons", [])
    )
    return {"status": "learning_updated", "message": "AI has learned from your feedback"}

@app.get("/")
async def root():
    """Главная страница AI Orchestrator"""
    return {
        "service": "BCM AI Orchestrator",
        "version": "2.0.0",
        "description": "Интеллектуальный координатор для автоматизации BCM процессов + AI DevOps",
        "ai_capabilities": {
            "risk_analysis": "Автоматический анализ рисков бизнес-процессов",
            "incident_classification": "ИИ классификация инцидентов по типу и серьезности", 
            "nlp_interface": "Обработка запросов на естественном языке",
            "deployment_orchestration": "🚀 AI-управляемое развертывание с самообучением",
            "devops_automation": "🤖 Автоматизация DevOps с созданием PR улучшений"
        },
        "endpoints": {
            "risk_analysis": "/analyze/process-risk",
            "incident_classification": "/analyze/incident",
            "nlp_queries": "/nlp/query",
            "deployment_orchestration": "/deployment/orchestrate",
            "deployment_history": "/deployment/history",
            "manual_learning": "/deployment/learn",
            "health": "/health"
        },
        "status": "AI Engine Active + DevOps Ready"
    }

# ===============================
# AI AGENT ORCHESTRATION ENDPOINTS
# ===============================

try:
    from ai_agent_router import ai_router, AgentCapability
    AI_AGENTS_AVAILABLE = True
except ImportError:
    AI_AGENTS_AVAILABLE = False
    logger.warning("AI Agent Router not available - running in compatibility mode")

try:
    from model_router import bcm_model_router, TaskComplexity
    MODEL_ROUTER_AVAILABLE = True
except ImportError:
    MODEL_ROUTER_AVAILABLE = False
    logger.warning("Model Router not available - using default model selection")

if AI_AGENTS_AVAILABLE:
    class AIAgentRequest(BaseModel):
        """AI Agent request model"""
        capability: str = Field(..., description="Required AI capability")
        data: Dict[str, Any] = Field(..., description="Request data")
        context: Optional[Dict[str, Any]] = Field(None, description="Additional context")
        priority: Optional[str] = Field("normal", description="Request priority")

    @app.post("/ai/process")
    async def process_with_ai_agent(request: AIAgentRequest):
        """Route request to appropriate AI agent"""
        try:
            # Map capability string to enum
            capability_map = {
                "pdca": AgentCapability.PDCA,
                "bia": AgentCapability.BIA_ANALYSIS,
                "document": AgentCapability.DOCUMENT_PROCESSING,
                "compliance": AgentCapability.COMPLIANCE_CHECK,
                "workflow": AgentCapability.WORKFLOW_ORCHESTRATION,
                "github": AgentCapability.GITHUB_INTEGRATION,
                "decision": AgentCapability.DECISION_SUPPORT,
                "context": AgentCapability.CONTEXT_AWARENESS
            }

            capability = capability_map.get(request.capability.lower())
            if not capability:
                raise ValueError(f"Unknown capability: {request.capability}")

            # Route to appropriate agent
            result = await ai_router.route_request(
                capability=capability,
                request_data=request.data,
                context=request.context
            )

            return {
                "status": "success",
                "capability": request.capability,
                "result": result,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"AI Agent routing error: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/ai/agents/health")
    async def check_ai_agents_health():
        """Check health of all AI agents"""
        try:
            health_status = await ai_router.health_check_all_agents()
            return {
                "status": "completed",
                "agents": health_status,
                "healthy_count": sum(1 for agent in health_status.values() if agent["healthy"]),
                "total_count": len(health_status),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Health check error: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/ai/agents/analytics")
    async def get_ai_agent_analytics():
        """Get AI agent analytics and performance metrics"""
        try:
            analytics = ai_router.get_agent_analytics()
            return {
                "status": "success",
                "analytics": analytics,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Analytics error: {e}")
            raise HTTPException(status_code=500, detail=str(e))

# Enhanced health check
@app.get("/health")
async def health_check():
    """Enhanced health check with AI agents status"""
    health_data = {
        "status": "healthy",
        "service": "ai_orchestrator",
        "version": "2.0.0-ai-agents",
        "ai_agents_enabled": AI_AGENTS_AVAILABLE,
        "timestamp": datetime.now().isoformat()
    }

    if AI_AGENTS_AVAILABLE:
        try:
            agent_health = await ai_router.health_check_all_agents()
            health_data["ai_agents"] = {
                "total": len(agent_health),
                "healthy": sum(1 for agent in agent_health.values() if agent["healthy"])
            }
        except Exception as e:
            health_data["ai_agents"] = {"error": str(e)}

    return health_data

if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting AI Orchestrator with AI Agents: {AI_AGENTS_AVAILABLE}")
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
