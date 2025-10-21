# -*- coding: utf-8 -*-
"""
BCM Project Intelligence Service
Портировано из Odoo bcm_project_management модуля

AI-powered сервис для умного управления BCM проектами:
- Health monitoring в реальном времени
- AI-анализ проектов
- Автоматическое назначение задач
- Предсказание сроков
- Интеграция с 9 BCM модулями
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from enum import Enum
import logging
import json

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="BCM Project Intelligence Service",
    description="AI-powered project management for BCM",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============== ENUMS ==============

class BCMProjectType(str, Enum):
    """Типы BCM проектов"""
    recovery = "recovery"  # Recovery Plan Implementation
    exercise = "exercise"  # Exercise & Training
    audit = "audit"  # BCM Audit
    incident = "incident"  # Incident Response
    improvement = "improvement"  # Continuous Improvement
    assessment = "assessment"  # Risk & BIA Assessment


class CriticalityLevel(str, Enum):
    """Уровни критичности"""
    critical = "critical"
    high = "high"
    medium = "medium"
    low = "low"


class HealthStatus(str, Enum):
    """Статус здоровья проекта"""
    healthy = "healthy"  # On Track
    warning = "warning"  # Needs Attention
    critical = "critical"  # Critical Issues
    blocked = "blocked"  # Blocked


class TaskPriority(str, Enum):
    """Приоритет задачи"""
    urgent = "urgent"
    high = "high"
    normal = "normal"
    low = "low"


# ============== PYDANTIC MODELS ==============

class RecoveryObjectives(BaseModel):
    """Recovery objectives для recovery проектов"""
    rto_hours: Optional[float] = Field(None, description="Recovery Time Objective (hours)")
    rpo_hours: Optional[float] = Field(None, description="Recovery Point Objective (hours)")
    mtd_hours: Optional[float] = Field(None, description="Maximum Tolerable Downtime (hours)")


class Task(BaseModel):
    """Задача проекта"""
    id: str
    name: str
    description: Optional[str] = None
    priority: TaskPriority = TaskPriority.normal
    deadline: Optional[datetime] = None
    completed: bool = False
    blocked: bool = False
    assigned_to: Optional[str] = None
    complexity_score: Optional[float] = Field(None, ge=0, le=10)
    required_skills: List[str] = []


class TeamMember(BaseModel):
    """Член команды"""
    id: str
    name: str
    email: str
    skills: List[str] = []
    current_tasks_count: int = 0
    avg_completion_rate: float = Field(0.0, ge=0, le=1.0)
    availability_hours_per_week: float = 40.0


class Project(BaseModel):
    """BCM Проект (портировано из Odoo BCMProject)"""
    id: str
    name: str
    description: Optional[str] = None
    bcm_type: BCMProjectType
    criticality_level: CriticalityLevel = CriticalityLevel.medium

    # Recovery objectives
    recovery_objectives: Optional[RecoveryObjectives] = None

    # Dates
    start_date: Optional[datetime] = None
    deadline: Optional[datetime] = None
    smart_deadline: Optional[datetime] = None  # AI-adjusted

    # Tasks
    tasks: List[Task] = []

    # Team
    team_members: List[TeamMember] = []

    # Integration
    source_risk_id: Optional[str] = None
    source_incident_id: Optional[str] = None
    source_audit_finding_id: Optional[str] = None
    source_module: Optional[str] = None

    # Automation flags
    auto_escalate: bool = True
    auto_assign: bool = True
    auto_notify: bool = True

    # AI fields (computed)
    health_status: Optional[HealthStatus] = None
    health_score: Optional[int] = None
    ai_insights: Optional[str] = None
    ai_recommendations: List[Dict[str, Any]] = []
    ai_risk_score: Optional[float] = None


class HealthMetrics(BaseModel):
    """Метрики здоровья проекта"""
    total_tasks: int
    completed_tasks: int
    overdue_tasks: int
    blocked_tasks: int
    at_risk_tasks: int
    overall_progress: float
    health_score: int
    health_status: HealthStatus


class AIAnalysisResult(BaseModel):
    """Результат AI-анализа проекта"""
    project_id: str
    health_metrics: HealthMetrics
    risks: List[Dict[str, Any]]
    recommendations: List[Dict[str, Any]]
    predicted_completion_date: Optional[datetime]
    confidence_score: float


class TaskAssignmentSuggestion(BaseModel):
    """Предложение по назначению задачи"""
    task_id: str
    suggested_assignee_id: str
    suggested_assignee_name: str
    confidence: float
    reasoning: str
    alternative_assignees: List[Dict[str, Any]] = []


# ============== IN-MEMORY STORAGE (В продакшене: PostgreSQL/MongoDB) ==============

# В реальной реализации это будет БД
projects_db: Dict[str, Project] = {}
learning_patterns: Dict[str, List[Dict[str, Any]]] = {
    'projects': [],
    'assignments': [],
    'durations': []
}


# ============== CORE BUSINESS LOGIC (Портировано из Odoo) ==============

class ProjectIntelligenceEngine:
    """
    Движок интеллектуального управления проектами
    Портировано из bcm_project_ai_local.py
    """

    def __init__(self):
        self.tasks_analyzed = 0
        self.predictions_made = 0
        self.accuracy_rate = 0.0

    def calculate_health_metrics(self, project: Project) -> HealthMetrics:
        """
        Рассчитывает метрики здоровья проекта
        Портировано из _compute_health_status()
        """
        total_tasks = len(project.tasks)

        if total_tasks == 0:
            return HealthMetrics(
                total_tasks=0,
                completed_tasks=0,
                overdue_tasks=0,
                blocked_tasks=0,
                at_risk_tasks=0,
                overall_progress=0.0,
                health_score=100,
                health_status=HealthStatus.healthy
            )

        # Count tasks
        completed_tasks = sum(1 for t in project.tasks if t.completed)
        overdue_tasks = sum(
            1 for t in project.tasks
            if t.deadline and t.deadline < datetime.now() and not t.completed
        )
        blocked_tasks = sum(1 for t in project.tasks if t.blocked)

        # At risk tasks: deadline в ближайшие 3 дня и не начаты
        at_risk_tasks = sum(
            1 for t in project.tasks
            if t.deadline and
               datetime.now() <= t.deadline <= datetime.now() + timedelta(days=3) and
               not t.completed and
               not t.blocked
        )

        # Calculate progress
        overall_progress = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

        # Calculate health score (0-100)
        # Алгоритм из Odoo: _compute_health_status()
        score = 100

        # Penalty for overdue tasks (max -40)
        score -= (overdue_tasks / total_tasks * 40) if total_tasks else 0

        # Penalty for blocked tasks (max -30)
        score -= (blocked_tasks / total_tasks * 30) if total_tasks else 0

        # Bonus for progress (max +20)
        if overall_progress >= 80:
            score += 10
        elif overall_progress >= 50:
            score += 5

        # Penalty for at-risk tasks (max -10)
        score -= (at_risk_tasks / total_tasks * 10) if total_tasks else 0

        # Ensure 0-100 range
        score = max(0, min(100, int(score)))

        # Determine health status
        if score >= 80:
            health_status = HealthStatus.healthy
        elif score >= 50:
            health_status = HealthStatus.warning
        elif blocked_tasks > total_tasks * 0.3:
            health_status = HealthStatus.blocked
        else:
            health_status = HealthStatus.critical

        return HealthMetrics(
            total_tasks=total_tasks,
            completed_tasks=completed_tasks,
            overdue_tasks=overdue_tasks,
            blocked_tasks=blocked_tasks,
            at_risk_tasks=at_risk_tasks,
            overall_progress=round(overall_progress, 2),
            health_score=score,
            health_status=health_status
        )

    def analyze_project(self, project: Project) -> AIAnalysisResult:
        """
        AI-анализ проекта
        Портировано из analyze_project() и _local_project_analysis()
        """
        # Calculate health metrics
        health_metrics = self.calculate_health_metrics(project)

        # Identify risks
        risks = []

        if health_metrics.overdue_tasks > 0:
            risks.append({
                'type': 'deadline_risk',
                'severity': 'high' if health_metrics.overdue_tasks > 5 else 'medium',
                'description': f'{health_metrics.overdue_tasks} tasks are overdue',
                'impact': 'Project timeline at risk'
            })

        if health_metrics.blocked_tasks > 0:
            risks.append({
                'type': 'blocked_tasks',
                'severity': 'high' if health_metrics.blocked_tasks > 3 else 'medium',
                'description': f'{health_metrics.blocked_tasks} tasks are blocked',
                'impact': 'Team productivity compromised'
            })

        if project.criticality_level == CriticalityLevel.critical and health_metrics.health_score < 70:
            risks.append({
                'type': 'critical_project_at_risk',
                'severity': 'critical',
                'description': 'Critical project is not on track',
                'impact': 'Business continuity may be compromised'
            })

        # Generate recommendations
        recommendations = []

        if health_metrics.health_status == HealthStatus.critical:
            recommendations.append({
                'priority': 'urgent',
                'action': 'escalate',
                'title': 'Escalate to management',
                'description': 'Project health is critical. Schedule emergency review meeting.',
                'estimated_effort': '1 hour'
            })

        if health_metrics.overdue_tasks > 3:
            recommendations.append({
                'priority': 'high',
                'action': 'prioritize',
                'title': 'Focus on overdue tasks',
                'description': f'Prioritize {health_metrics.overdue_tasks} overdue tasks. Consider resource reallocation.',
                'estimated_effort': '2-3 days'
            })

        if health_metrics.blocked_tasks > 0:
            recommendations.append({
                'priority': 'high',
                'action': 'unblock',
                'title': 'Resolve blockers',
                'description': f'Identify and resolve blockers for {health_metrics.blocked_tasks} tasks.',
                'estimated_effort': '1-2 days'
            })

        if project.auto_assign and health_metrics.at_risk_tasks > 0:
            recommendations.append({
                'priority': 'medium',
                'action': 'assign',
                'title': 'Assign at-risk tasks',
                'description': f'{health_metrics.at_risk_tasks} tasks are at risk. Use AI to assign optimal resources.',
                'estimated_effort': '30 minutes'
            })

        # Predict completion date
        predicted_completion = self._predict_completion_date(project, health_metrics)

        # Calculate confidence
        confidence_score = self._calculate_confidence(project, health_metrics)

        # Learn from this analysis
        self._learn_from_analysis(project, health_metrics)

        self.tasks_analyzed += len(project.tasks)

        return AIAnalysisResult(
            project_id=project.id,
            health_metrics=health_metrics,
            risks=risks,
            recommendations=recommendations,
            predicted_completion_date=predicted_completion,
            confidence_score=confidence_score
        )

    def suggest_task_assignee(
        self,
        task: Task,
        team_members: List[TeamMember],
        project: Project
    ) -> TaskAssignmentSuggestion:
        """
        AI предлагает исполнителя для задачи
        Портировано из suggest_task_assignee()
        """
        if not team_members:
            raise HTTPException(status_code=400, detail="No team members available")

        best_match = None
        best_score = 0
        reasoning_parts = []
        alternatives = []

        for member in team_members:
            score = 0
            member_reasoning = []

            # 1. Skill match (40 points)
            if task.required_skills:
                matched_skills = set(member.skills) & set(task.required_skills)
                skill_match_ratio = len(matched_skills) / len(task.required_skills)
                skill_points = skill_match_ratio * 40
                score += skill_points
                member_reasoning.append(
                    f"Skill match: {len(matched_skills)}/{len(task.required_skills)} "
                    f"({int(skill_match_ratio * 100)}%)"
                )
            else:
                # No specific skills required
                score += 20
                member_reasoning.append("No specific skills required")

            # 2. Workload (30 points)
            if member.current_tasks_count < 3:
                score += 30
                member_reasoning.append("Low workload (< 3 tasks)")
            elif member.current_tasks_count < 5:
                score += 20
                member_reasoning.append("Medium workload (3-5 tasks)")
            elif member.current_tasks_count < 8:
                score += 10
                member_reasoning.append("High workload (5-8 tasks)")
            else:
                member_reasoning.append("Very high workload (8+ tasks)")

            # 3. Historical performance (30 points)
            if member.avg_completion_rate >= 0.9:
                score += 30
                member_reasoning.append("Excellent completion rate (90%+)")
            elif member.avg_completion_rate >= 0.75:
                score += 20
                member_reasoning.append("Good completion rate (75-90%)")
            elif member.avg_completion_rate >= 0.5:
                score += 10
                member_reasoning.append("Average completion rate (50-75%)")
            else:
                member_reasoning.append("Low completion rate (< 50%)")

            # 4. Bonus for critical projects
            if project.criticality_level == CriticalityLevel.critical:
                if member.avg_completion_rate >= 0.8:
                    score += 10
                    member_reasoning.append("Reliable for critical project")

            # Store alternative
            alternatives.append({
                'member_id': member.id,
                'member_name': member.name,
                'score': int(score),
                'reasoning': "; ".join(member_reasoning)
            })

            if score > best_score:
                best_score = score
                best_match = member
                reasoning_parts = member_reasoning

        if not best_match:
            raise HTTPException(status_code=404, detail="No suitable assignee found")

        # Sort alternatives by score
        alternatives.sort(key=lambda x: x['score'], reverse=True)
        alternatives = alternatives[:3]  # Top 3

        # Learn from this assignment
        self._learn_assignment_pattern(task, best_match.id, project)

        self.predictions_made += 1

        return TaskAssignmentSuggestion(
            task_id=task.id,
            suggested_assignee_id=best_match.id,
            suggested_assignee_name=best_match.name,
            confidence=best_score / 100,
            reasoning="; ".join(reasoning_parts),
            alternative_assignees=alternatives
        )

    def _predict_completion_date(
        self,
        project: Project,
        health_metrics: HealthMetrics
    ) -> Optional[datetime]:
        """Предсказывает дату завершения проекта"""
        if not project.tasks:
            return None

        # Find similar projects in history
        similar_projects = self._find_similar_projects(project.bcm_type)

        if similar_projects and len(similar_projects) >= 3:
            # Use historical data
            avg_duration_days = sum(p['duration_days'] for p in similar_projects) / len(similar_projects)

            # Adjust based on health
            if health_metrics.health_score < 50:
                avg_duration_days *= 1.5  # 50% longer
            elif health_metrics.health_score < 70:
                avg_duration_days *= 1.2  # 20% longer

            predicted_date = datetime.now() + timedelta(days=avg_duration_days)
        else:
            # Fallback: estimate based on remaining tasks
            remaining_tasks = health_metrics.total_tasks - health_metrics.completed_tasks

            # Average 2 days per task (can be refined)
            avg_days_per_task = 2

            # Adjust for blocked tasks
            if health_metrics.blocked_tasks > 0:
                avg_days_per_task += 1

            estimated_days = remaining_tasks * avg_days_per_task
            predicted_date = datetime.now() + timedelta(days=estimated_days)

        return predicted_date

    def _calculate_confidence(self, project: Project, health_metrics: HealthMetrics) -> float:
        """Рассчитывает уверенность в предсказаниях"""
        confidence = 0.5  # Base confidence

        # More data = more confidence
        if len(project.tasks) > 10:
            confidence += 0.2
        elif len(project.tasks) > 5:
            confidence += 0.1

        # Better health = more confidence
        if health_metrics.health_score >= 80:
            confidence += 0.2
        elif health_metrics.health_score >= 60:
            confidence += 0.1

        # Historical data availability
        similar_projects = self._find_similar_projects(project.bcm_type)
        if similar_projects and len(similar_projects) >= 5:
            confidence += 0.1

        return min(1.0, confidence)

    def _find_similar_projects(self, bcm_type: BCMProjectType) -> List[Dict[str, Any]]:
        """Найти похожие проекты в истории обучения"""
        return [
            p for p in learning_patterns['projects']
            if p.get('bcm_type') == bcm_type
        ]

    def _learn_from_analysis(self, project: Project, health_metrics: HealthMetrics):
        """Сохранить паттерн для обучения"""
        pattern = {
            'project_id': project.id,
            'bcm_type': project.bcm_type,
            'criticality_level': project.criticality_level,
            'team_size': len(project.team_members),
            'total_tasks': health_metrics.total_tasks,
            'health_score': health_metrics.health_score,
            'timestamp': datetime.now().isoformat()
        }

        learning_patterns['projects'].append(pattern)

        # Keep only last 1000 patterns
        if len(learning_patterns['projects']) > 1000:
            learning_patterns['projects'] = learning_patterns['projects'][-1000:]

    def _learn_assignment_pattern(self, task: Task, assignee_id: str, project: Project):
        """Сохранить паттерн назначения"""
        pattern = {
            'task_id': task.id,
            'task_priority': task.priority,
            'required_skills': task.required_skills,
            'assignee_id': assignee_id,
            'project_type': project.bcm_type,
            'timestamp': datetime.now().isoformat()
        }

        learning_patterns['assignments'].append(pattern)

        if len(learning_patterns['assignments']) > 1000:
            learning_patterns['assignments'] = learning_patterns['assignments'][-1000:]


# Singleton instance
intelligence_engine = ProjectIntelligenceEngine()


# ============== API ENDPOINTS ==============

@app.get("/")
async def root():
    """Health check"""
    return {
        "service": "BCM Project Intelligence",
        "status": "running",
        "version": "1.0.0",
        "tasks_analyzed": intelligence_engine.tasks_analyzed,
        "predictions_made": intelligence_engine.predictions_made
    }


@app.post("/api/v1/projects", response_model=Project)
async def create_project(project: Project):
    """Создать новый проект"""
    if project.id in projects_db:
        raise HTTPException(status_code=400, detail="Project with this ID already exists")

    # Calculate initial health
    analysis = intelligence_engine.analyze_project(project)
    project.health_status = analysis.health_metrics.health_status
    project.health_score = analysis.health_metrics.health_score
    project.ai_recommendations = analysis.recommendations
    project.smart_deadline = analysis.predicted_completion_date

    projects_db[project.id] = project

    logger.info(f"Created project: {project.id} ({project.bcm_type})")

    return project


@app.get("/api/v1/projects/{project_id}", response_model=Project)
async def get_project(project_id: str):
    """Получить проект по ID"""
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")

    return projects_db[project_id]


@app.get("/api/v1/projects", response_model=List[Project])
async def list_projects(
    bcm_type: Optional[BCMProjectType] = None,
    criticality_level: Optional[CriticalityLevel] = None,
    health_status: Optional[HealthStatus] = None
):
    """Получить список проектов с фильтрами"""
    projects = list(projects_db.values())

    if bcm_type:
        projects = [p for p in projects if p.bcm_type == bcm_type]

    if criticality_level:
        projects = [p for p in projects if p.criticality_level == criticality_level]

    if health_status:
        projects = [p for p in projects if p.health_status == health_status]

    return projects


@app.post("/api/v1/projects/{project_id}/analyze", response_model=AIAnalysisResult)
async def analyze_project(project_id: str):
    """AI-анализ проекта"""
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")

    project = projects_db[project_id]
    analysis = intelligence_engine.analyze_project(project)

    # Update project with analysis results
    project.health_status = analysis.health_metrics.health_status
    project.health_score = analysis.health_metrics.health_score
    project.ai_recommendations = analysis.recommendations
    project.smart_deadline = analysis.predicted_completion_date

    logger.info(f"Analyzed project {project_id}: health_score={analysis.health_metrics.health_score}")

    return analysis


@app.post("/api/v1/projects/{project_id}/tasks/{task_id}/suggest-assignee",
         response_model=TaskAssignmentSuggestion)
async def suggest_task_assignee(project_id: str, task_id: str):
    """AI предлагает исполнителя для задачи"""
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")

    project = projects_db[project_id]

    # Find task
    task = next((t for t in project.tasks if t.id == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if not project.team_members:
        raise HTTPException(status_code=400, detail="No team members in project")

    suggestion = intelligence_engine.suggest_task_assignee(task, project.team_members, project)

    logger.info(f"Suggested assignee for task {task_id}: {suggestion.suggested_assignee_name} (confidence: {suggestion.confidence})")

    return suggestion


@app.get("/api/v1/projects/{project_id}/health", response_model=HealthMetrics)
async def get_project_health(project_id: str):
    """Получить метрики здоровья проекта"""
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")

    project = projects_db[project_id]
    health_metrics = intelligence_engine.calculate_health_metrics(project)

    return health_metrics


@app.get("/api/v1/learning/stats")
async def get_learning_stats():
    """Получить статистику обучения AI"""
    return {
        "projects_learned": len(learning_patterns['projects']),
        "assignments_learned": len(learning_patterns['assignments']),
        "tasks_analyzed": intelligence_engine.tasks_analyzed,
        "predictions_made": intelligence_engine.predictions_made,
        "accuracy_rate": intelligence_engine.accuracy_rate
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8025)
