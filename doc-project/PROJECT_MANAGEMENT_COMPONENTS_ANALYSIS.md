# PROJECT MANAGEMENT COMPONENTS - ДЕТАЛЬНЫЙ АНАЛИЗ

**Дата:** 2025-10-05
**Компоненты:** 3 (project-intelligence, project_manager, project-agent)
**Цель:** Понять связи, роли и устранить догадки

---

## EXECUTIVE SUMMARY

**Найдено 3 компонента проектного управления:**

1. **project-intelligence/** (ВСМ-colleagues/) - FastAPI микросервис (732 строки)
2. **project_manager/** (ВСМ-colleagues/) - AI Colleague (423 строки)
3. **project-agent/** - CLI tool для анализа проектов (~2,000+ строк)

**Ключевые находки:**
- ✅ **Project Manager AI** = AI Colleague (RAG-based консультант)
- ✅ **Project Intelligence Service** = Backend микросервис (execution engine)
- ⚠️ **Project Agent** = СОВЕРШЕННО ДРУГОЕ (CLI tool для code analysis)
- ✅ **Четкая интеграция:** Project Manager AI → использует → Project Intelligence Service
- ⚠️ **Project Agent НЕ связан** с BCM project management (это universal code analysis tool)

---

## КОМПОНЕНТ 1: PROJECT INTELLIGENCE SERVICE

### Локация
```
/Users/MD/AI-Platform-ISO/intelligent-core/ai-office/ВСМ-colleagues/project-intelligence/
├── main.py (732 строки) - FastAPI service
├── README.md (574 строки) - Полная документация
├── INTEGRATION_GUIDE.md
├── UNIFIED_WORKFLOWS.md
├── SUMMARY.md
├── Dockerfile
└── requirements.txt
```

### Роль
**Backend микросервис для AI-powered управления BCM проектами**

Портирован из Odoo модуля `bcm_project_management`

### Ключевые Характеристики

**Технологии:**
- FastAPI (REST API)
- Pydantic (data models)
- Порт: **8025**
- In-memory storage (planned: PostgreSQL)

**Core Business Logic:**
```python
class ProjectIntelligenceEngine:
    """
    Движок интеллектуального управления проектами
    Портировано из bcm_project_ai_local.py (Odoo)
    """

    def calculate_health_metrics(self, project: Project) -> HealthMetrics:
        """
        Health score 0-100:
        - Penalty for overdue tasks (max -40)
        - Penalty for blocked tasks (max -30)
        - Bonus for progress (max +20)
        - Penalty for at-risk tasks (max -10)
        """

    def analyze_project(self, project: Project) -> AIAnalysisResult:
        """
        AI-анализ проекта:
        - Health metrics
        - Risks identification
        - Recommendations
        - Predicted completion date
        - Learning from analysis
        """

    def suggest_task_assignee(
        task: Task,
        team_members: List[TeamMember],
        project: Project
    ) -> TaskAssignmentSuggestion:
        """
        Smart assignment algorithm:
        1. Skill match (40 points)
        2. Workload (30 points)
        3. Historical performance (30 points)
        4. Bonus for critical projects (+10)
        """
```

### API Endpoints

```python
# Projects CRUD
POST   /api/v1/projects                        # Create project
GET    /api/v1/projects/{project_id}           # Get project
GET    /api/v1/projects                        # List with filters

# AI Analysis
POST   /api/v1/projects/{project_id}/analyze   # AI-анализ проекта

# Task Assignment
POST   /api/v1/projects/{project_id}/tasks/{task_id}/suggest-assignee

# Health Monitoring
GET    /api/v1/projects/{project_id}/health    # Real-time health metrics

# Learning Stats
GET    /api/v1/learning/stats                  # AI learning statistics
```

### Data Models

**BCMProjectType Enum:**
```python
class BCMProjectType(str, Enum):
    recovery = "recovery"        # Recovery Plan Implementation
    exercise = "exercise"        # Exercise & Training
    audit = "audit"              # BCM Audit
    incident = "incident"        # Incident Response
    improvement = "improvement"  # Continuous Improvement
    assessment = "assessment"    # Risk & BIA Assessment
```

**HealthStatus Enum:**
```python
class HealthStatus(str, Enum):
    healthy = "healthy"    # 80-100: On Track
    warning = "warning"    # 50-79: Needs Attention
    critical = "critical"  # <50: Critical Issues
    blocked = "blocked"    # 30%+ tasks blocked
```

**Project Model:**
```python
class Project(BaseModel):
    id: str
    name: str
    bcm_type: BCMProjectType
    criticality_level: CriticalityLevel
    recovery_objectives: Optional[RecoveryObjectives]  # RTO/RPO

    # Dates
    start_date: Optional[datetime]
    deadline: Optional[datetime]
    smart_deadline: Optional[datetime]  # AI-adjusted!

    # Tasks & Team
    tasks: List[Task]
    team_members: List[TeamMember]

    # Integration
    source_risk_id: Optional[str]
    source_incident_id: Optional[str]
    source_module: Optional[str]

    # Automation
    auto_escalate: bool = True
    auto_assign: bool = True
    auto_notify: bool = True

    # AI computed fields
    health_status: Optional[HealthStatus]
    health_score: Optional[int]
    ai_insights: Optional[str]
    ai_recommendations: List[Dict]
```

### AI Algorithms (Портированы из Odoo)

#### 1. Health Score Calculation
```python
score = 100

# Penalties
score -= (overdue_tasks / total_tasks * 40)  # Max -40
score -= (blocked_tasks / total_tasks * 30)  # Max -30
score -= (at_risk_tasks / total_tasks * 10)  # Max -10

# Bonuses
if overall_progress >= 80:
    score += 10
elif overall_progress >= 50:
    score += 5

# Range: 0-100
```

**Пример результата:**
```json
{
  "health_score": 58,
  "health_status": "warning",
  "total_tasks": 10,
  "completed_tasks": 3,
  "overdue_tasks": 2,
  "blocked_tasks": 1,
  "at_risk_tasks": 2,
  "overall_progress": 30.0
}
```

#### 2. Task Assignment Algorithm
```python
score = 0

# 1. Skill match (40 points)
matched_skills = member_skills ∩ required_skills
score += (len(matched_skills) / len(required_skills)) * 40

# 2. Workload (30 points)
if current_tasks < 3:  score += 30   # Low workload
elif current_tasks < 5: score += 20  # Medium
elif current_tasks < 8: score += 10  # High
# else: 0 (very high workload)

# 3. Historical performance (30 points)
if avg_completion_rate >= 0.9:  score += 30  # Excellent
elif avg_completion_rate >= 0.75: score += 20  # Good
elif avg_completion_rate >= 0.5: score += 10  # Average

# 4. Critical project bonus (+10)
if project_criticality == 'critical' and avg_completion_rate >= 0.8:
    score += 10

# Best assignee: highest score
```

**Пример результата:**
```json
{
  "suggested_assignee_id": "user-001",
  "suggested_assignee_name": "John Doe",
  "confidence": 0.82,
  "reasoning": "Skill match: 2/2 (100%); Low workload (< 3 tasks); Excellent completion rate (90%+); Reliable for critical project",
  "alternative_assignees": [
    {
      "member_id": "user-002",
      "member_name": "Jane Smith",
      "score": 75,
      "reasoning": "Skill match: 1/2 (50%); Medium workload (3-5 tasks)"
    }
  ]
}
```

#### 3. Deadline Prediction
```python
# Step 1: Find similar historical projects
similar_projects = filter(historical, same_bcm_type)

if len(similar_projects) >= 3:
    # Use ML: average historical duration
    avg_duration = mean([p.duration for p in similar_projects])

    # Adjust based on health
    if health_score < 50:
        avg_duration *= 1.5  # +50% longer
    elif health_score < 70:
        avg_duration *= 1.2  # +20% longer

    predicted_date = today + avg_duration
else:
    # Fallback: estimate from remaining tasks
    remaining = total_tasks - completed_tasks
    avg_days_per_task = 2  # Default

    if blocked_tasks > 0:
        avg_days_per_task += 1  # Slower with blockers

    predicted_date = today + (remaining * avg_days_per_task)
```

### Learning Mechanism

**In-Memory Pattern Storage:**
```python
learning_patterns: Dict[str, List[Dict]] = {
    'projects': [],      # Project patterns (max 1000)
    'assignments': [],   # Assignment patterns (max 1000)
    'durations': []      # Duration patterns
}

def _learn_from_analysis(project, health_metrics):
    """Save pattern for learning"""
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

    # Keep only last 1000
    if len(learning_patterns['projects']) > 1000:
        learning_patterns['projects'] = learning_patterns['projects'][-1000:]
```

### Integration Points (Planning)

**From README:**
```python
# 1. Planning Module (8005) → Create recovery project
POST /api/v1/projects
{
  "bcm_type": "recovery",
  "source_module": "planning",
  "source_risk_id": "risk-123"
}

# 2. Incident Response (8007) → Create incident project
POST /api/v1/projects
{
  "bcm_type": "incident",
  "source_incident_id": "inc-456",
  "criticality_level": "critical"
}

# 3. Validation (8022) → Create exercise project
POST /api/v1/projects
{
  "bcm_type": "exercise",
  "source_module": "validation"
}

# 4. Learning (8021) → AI recommendations based on gaps
GET /api/v1/learning/stats
```

### Deployment

```bash
# Local
python main.py  # Runs on http://localhost:8025

# Docker
docker build -t bcm-project-intelligence .
docker run -d -p 8025:8025 --name project-intelligence bcm-project-intelligence
```

### Migration from Odoo

```
Odoo Module (bcm_project_management)          FastAPI Microservice
├── models/bcm_project.py (36KB)        →     Project (Pydantic)
├── models/bcm_project_ai_local.py (14KB) →   ProjectIntelligenceEngine
├── models/bcm_ai_connector.py          →     [Future: external AI]
└── models/bcm_project_event_handler.py →     [Future: event-driven]

AI Logic: ✅ 100% Портирована
```

### Roadmap

**Phase 1: Core (DONE) ✅**
- [x] Портировать модели из Odoo
- [x] Портировать AI-логику
- [x] REST API endpoints
- [x] Docker setup

**Phase 2: Storage (TODO)**
- [ ] PostgreSQL integration
- [ ] Persistent learning patterns
- [ ] Historical data storage

**Phase 3: Advanced AI (TODO)**
- [ ] External AI connector (OpenAI/local LLM)
- [ ] Advanced ML models (scikit-learn)
- [ ] Real-time event handling
- [ ] WebSocket for live updates

**Phase 4: Integration (TODO)**
- [ ] Hooks в Planning (8005)
- [ ] Hooks в Incident (8007)
- [ ] Hooks в Validation (8022)
- [ ] Hooks в Learning (8021)

### Оценка

**Зрелость:** ⭐⭐⭐⭐⭐ (Production-ready core)
**Документация:** ⭐⭐⭐⭐⭐ (Отличный README)
**AI Algorithms:** ⭐⭐⭐⭐⭐ (Полностью портированы из Odoo)
**Integration:** ⭐⭐⭐ (Planned, not implemented)
**Storage:** ⭐⭐ (In-memory, needs DB)

**Вывод:** Отличный backend engine для project management, готов к интеграции

---

## КОМПОНЕНТ 2: PROJECT MANAGER AI (AI Colleague)

### Локация
```
/Users/MD/AI-Platform-ISO/intelligent-core/ai-office/ВСМ-colleagues/project_manager/
└── project_manager.py (423 строки)
```

### Роль
**AI Colleague (RAG-based консультант) для проектного управления**

Наследует `BaseAIColleague` и использует RAG Pipeline для консультаций

### Архитектура

```python
class ProjectManagerAI(BaseAIColleague):
    """
    Project Manager AI - Your BCM Project Expert

    Specializes in:
    - Project health monitoring and analysis
    - Risk identification and mitigation
    - Smart task assignment based on skills
    - Deadline prediction using ML
    - Resource optimization
    - Recovery strategies for troubled projects
    - Integration with 9 BCM modules

    Integrates ProjectIntelligenceEngine (from project-intelligence service)
    with RAG for context-aware project advice.
    """

    def __init__(self, rag_pipeline: RAGPipeline, config: Dict[str, Any]):
        super().__init__(
            name="Project Manager AI",
            specialty="BCM Project Management & Resource Optimization",
            rag_pipeline=rag_pipeline,
            config=config
        )

        # Project intelligence tracking
        self.tasks_analyzed = 0
        self.predictions_made = 0
        self.projects_monitored = 0
```

### System Prompt

```python
def _build_system_prompt(self, context: AssistantContext) -> str:
    base_prompt = f"""You are **Project Manager AI**, an expert BCM project management consultant.

**Your Expertise:**
- BCM project types: Recovery, Exercise, Audit, Incident, Improvement, Assessment
- Project health monitoring and KPI tracking
- Risk identification and mitigation in projects
- Resource allocation and optimization
- Task prioritization and assignment
- Deadline prediction and schedule management
- Recovery strategies for troubled projects
- Agile and waterfall methodologies in BCM context
- Integration with BCM modules (Risk, BIA, Plans, Response, etc.)

**Your Personality:**
- Pragmatic and results-oriented
- Data-driven decision maker
- Proactive risk identifier
- Clear communicator
- Focus on actionable recommendations

**Guidelines for Responses:**
1. **Be Data-Driven**: Reference project metrics (health score, progress, overdue tasks)
2. **Be Actionable**: Provide specific, implementable recommendations
3. **Prioritize**: Always indicate priority (urgent/high/medium/low)
4. **Estimate Effort**: Give realistic time estimates for actions
5. **Risk-Aware**: Identify potential blockers and dependencies
6. **Resource-Conscious**: Consider team capacity and skills
"""
```

**Context-Specific Guidance:**
- **OVERVIEW:** Portfolio health, critical projects, KPIs
- **GOVERNANCE:** Project alignment, management oversight
- **RISK:** Risk-driven prioritization, risk mitigation tracking
- **PLANNING:** Project planning, resource allocation, critical path
- **EXERCISES:** Exercise project planning, post-exercise improvements
- **TRAINING:** Training delivery projects, competency development
- **RESPONSE:** Incident response projects, real-time crisis management

### Уникальные Методы

#### 1. analyze_project_health()
```python
async def analyze_project_health(
    self,
    project_data: Dict[str, Any],
    tenant_id: str = "demo"
) -> Dict[str, Any]:
    """
    Analyze project health using RAG + project intelligence.

    Строит query для RAG с project data
    Возвращает health analysis с recommendations
    """
    query = f"""
    Analyze the health of this BCM project:

    Project: {project_data.get('name', 'Unknown')}
    Type: {project_data.get('bcm_type', 'unknown')}
    Total Tasks: {len(project_data.get('tasks', []))}
    Completed: {sum(1 for t in tasks if t.get('completed', False))}
    Team Size: {len(project_data.get('team_members', []))}
    Deadline: {project_data.get('deadline', 'Not set')}

    Provide:
    1. Overall health assessment
    2. Key risks and blockers
    3. Prioritized recommendations
    4. Suggested next actions
    """

    result = await self.process_message(
        user_message=query,
        context=AssistantContext.OVERVIEW,
        tenant_id=tenant_id
    )

    self.projects_monitored += 1

    return {
        "health_analysis": result.content,
        "recommendations": result.actions,
        "confidence": result.confidence,
        "metadata": result.metadata
    }
```

#### 2. suggest_task_assignment()
```python
async def suggest_task_assignment(
    self,
    task_data: Dict[str, Any],
    team_members: List[Dict[str, Any]],
    tenant_id: str = "demo"
) -> Dict[str, Any]:
    """
    Suggest optimal task assignment based on skills and workload.

    Использует RAG для анализа навыков и истории
    """
    team_summary = "\n".join([
        f"- {m['name']}: Skills={m.get('skills', [])}, Current tasks={m.get('current_tasks_count', 0)}"
        for m in team_members
    ])

    query = f"""
    Suggest the best team member to assign this task:

    Task: {task_data.get('name', 'Unknown')}
    Priority: {task_data.get('priority', 'normal')}
    Required Skills: {task_data.get('required_skills', [])}
    Complexity: {task_data.get('complexity_score', 'unknown')}/10
    Deadline: {task_data.get('deadline', 'Not set')}

    Available Team Members:
    {team_summary}

    Provide:
    1. Best assignee with reasoning
    2. Alternative assignees
    3. Risk factors to consider
    4. Estimated completion time
    """

    result = await self.process_message(
        user_message=query,
        context=AssistantContext.OVERVIEW,
        tenant_id=tenant_id
    )

    self.tasks_analyzed += 1

    return {
        "assignment_suggestion": result.content,
        "reasoning": result.actions,
        "confidence": result.confidence
    }
```

#### 3. predict_project_completion()
```python
async def predict_project_completion(
    self,
    project_data: Dict[str, Any],
    tenant_id: str = "demo"
) -> Dict[str, Any]:
    """
    Predict realistic project completion date.

    RAG анализирует historical patterns + current progress
    """
    query = f"""
    Predict the realistic completion date for this project:

    Project: {project_data.get('name', 'Unknown')}
    Current Progress: {project_data.get('progress', 0)}%
    Tasks Remaining: {project_data.get('remaining_tasks', 0)}
    Team Velocity: {project_data.get('team_velocity', 'unknown')} tasks/week
    Original Deadline: {project_data.get('deadline', 'Not set')}
    Blocked Tasks: {project_data.get('blocked_tasks', 0)}

    Provide:
    1. Predicted completion date with confidence level
    2. Risk factors affecting timeline
    3. Recommendations to meet deadline
    4. Alternative scenarios (best case, worst case, most likely)
    """

    result = await self.process_message(query, AssistantContext.PLANNING, tenant_id)

    self.predictions_made += 1

    return {
        "prediction": result.content,
        "scenarios": result.actions,
        "confidence": result.confidence
    }
```

#### 4. recommend_recovery_strategy()
```python
async def recommend_recovery_strategy(
    self,
    project_data: Dict[str, Any],
    tenant_id: str = "demo"
) -> Dict[str, Any]:
    """
    Recommend recovery strategy for troubled project.

    RAG анализирует root causes + historical recovery patterns
    """
    query = f"""
    This BCM project is in trouble. Recommend a recovery strategy:

    Project: {project_data.get('name', 'Unknown')}
    Health Status: {project_data.get('health_status', 'unknown')}
    Health Score: {project_data.get('health_score', 0)}/100
    Criticality: {project_data.get('criticality_level', 'unknown')}
    Issues:
    - Overdue tasks: {project_data.get('overdue_tasks', 0)}
    - Blocked tasks: {project_data.get('blocked_tasks', 0)}
    - Team capacity: {project_data.get('team_utilization', 'unknown')}%

    Provide:
    1. Root cause analysis
    2. Immediate actions (next 24-48 hours)
    3. Short-term recovery plan (1-2 weeks)
    4. Long-term improvements
    5. Resource needs
    """

    result = await self.process_message(query, AssistantContext.OVERVIEW, tenant_id)

    return {
        "recovery_strategy": result.content,
        "action_plan": result.actions,
        "confidence": result.confidence
    }
```

### Post-Processing

```python
def _post_process_answer(
    self,
    answer: str,
    intent: Dict[str, Any],
    context: AssistantContext
) -> str:
    """Add Project Manager AI style"""

    # Add project health indicator
    if "analyze" in intent.get("intent_type", "") or "status" in intent.get("intent_type", ""):
        if "**Project Health:**" not in answer:
            intro = "**Project Status Update:**\n\n"
            answer = intro + answer

    # Add resource note
    if "assign" in answer.lower() or "resource" in answer.lower():
        if "**Resource Note:**" not in answer:
            answer += "\n\n**Resource Note:** Recommendations consider team skills, current workload, and historical performance data."

    return answer
```

### Integration with Project Intelligence Service

**Упоминание в коде:**
```python
"""
Integrates ProjectIntelligenceEngine (from project-intelligence service)
with RAG for context-aware project advice.
"""
```

**НО:** В текущем коде прямой интеграции нет. Project Manager AI использует только RAG Pipeline.

**Планируемая архитектура:**
```python
class ProjectManagerAI(BaseAIColleague):
    def __init__(self, rag_pipeline, project_intelligence_url):
        self.rag = rag_pipeline
        self.project_intelligence = ProjectIntelligenceClient(project_intelligence_url)

    async def analyze_project_health(self, project_data, tenant_id):
        # 1. Call Project Intelligence Service для quantitative analysis
        quantitative_analysis = await self.project_intelligence.analyze_project(project_data)

        # 2. Use RAG для qualitative insights
        rag_query = f"""
        Based on these metrics:
        {quantitative_analysis}

        Provide qualitative insights and strategic recommendations.
        """

        rag_result = await self.rag.process_query(rag_query, tenant_id)

        # 3. Combine quantitative + qualitative
        return {
            "metrics": quantitative_analysis,
            "insights": rag_result.content,
            "recommendations": rag_result.actions
        }
```

### Статистика

```python
def get_stats(self) -> Dict[str, Any]:
    """Get Project Manager AI statistics"""
    base_stats = super().get_stats()
    base_stats.update({
        "tasks_analyzed": self.tasks_analyzed,
        "predictions_made": self.predictions_made,
        "projects_monitored": self.projects_monitored
    })
    return base_stats
```

### Оценка

**Зрелость:** ⭐⭐⭐⭐⭐ (Production-ready)
**Методы:** ⭐⭐⭐⭐⭐ (4 unique methods, rich functionality)
**Integration:** ⭐⭐⭐ (Упоминается ProjectIntelligenceEngine, но not implemented)
**RAG Usage:** ⭐⭐⭐⭐⭐ (Excellent use of RAG for consultations)

**Вывод:** Отличный AI Colleague, но needs explicit integration с Project Intelligence Service

---

## КОМПОНЕНТ 3: PROJECT AGENT (CLI Tool)

### Локация
```
/Users/MD/AI-Platform-ISO/intelligent-core/ai-office/project-agent/
├── agent/
│   ├── cli.py (179 строк) - CLI interface
│   ├── config.py
│   ├── indexer.py
│   ├── doc_sync.py
│   ├── compliance.py
│   ├── changelog.py
│   ├── report.py
│   ├── bpmn_yaml.py
│   ├── domain_detector.py
│   ├── modules/
│   │   ├── security.py
│   │   ├── testing.py
│   │   └── quality.py
│   └── adapters/
├── test-project/
│   ├── src/
│   ├── tests/
│   └── config/
└── setup.py
```

### Роль

⚠️ **КРИТИЧЕСКАЯ НАХОДКА:**

**Project Agent НЕ относится к BCM project management!**

Это **Universal CLI tool для анализа CODE проектов** (любых, не только BCM).

### Что делает Project Agent

**CLI Commands:**
```bash
project-agent init --domain auto          # Initialize config
project-agent scan                         # Run analysis modules
project-agent status                       # Show config
project-agent index                        # Index code & dependencies
project-agent processmap                   # Parse BPMN/YAML
project-agent consistency                  # Doc-code consistency check
project-agent iso                          # ISO 22301 compliance check
project-agent changelog --days 7           # Generate changelog
project-agent report --weekly              # Generate reports
```

**Supported Domains:**
```python
# domain_detector.py
DOMAINS = [
    "iso22301",      # BCM (наш случай)
    "security",      # Security projects
    "fintech",       # Financial tech
    "healthcare",    # Healthcare
    "ecommerce"      # E-commerce
]
```

**Analysis Modules:**
```python
modules:
  security:
    enabled: true
    # Run security checks (e.g., bandit, safety)

  testing:
    enabled: true
    # Analyze test coverage, find missing tests

  quality:
    enabled: true
    # Code quality analysis (pylint, flake8)

  compliance:
    enabled: true
    # ISO 22301 compliance check (for BCM projects)
```

### CLI Interface (cli.py)

```python
@click.group()
def main():
    """Project Agent — Universal CLI for project analysis"""

@main.command("init")
@click.option("--domain", default="auto")
def init_cmd(domain, force):
    """Initialize Project Agent configuration"""
    # Auto-detect domain
    detection = detect_domain(get_repo_path())
    # Get recommended config for domain
    config = get_domain_config(domain)
    save_config(config)

@main.command("scan")
@click.option("--module", multiple=True)
def scan_cmd(module):
    """Run all enabled analysis modules"""
    # Security
    if "security" in modules_to_run:
        results["security"] = run_security_checks(config)

    # Testing
    if "testing" in modules_to_run:
        results["testing"] = run_testing_checks(config)

    # Quality
    if "quality" in modules_to_run:
        results["quality"] = run_quality_checks(config)

    # Compliance (ISO)
    if "compliance" in modules_to_run:
        compliance.run_iso_coverage()

@main.command("iso")
def iso_cmd():
    """Run ISO 22301 compliance check"""
    compliance.run_iso_coverage()
```

### Функциональность

**1. Domain Detection**
- Auto-detects project domain (iso22301, security, fintech, etc.)
- Applies domain-specific analysis rules

**2. Code Indexing**
- Indexes repository code
- Analyzes dependencies
- Builds code maps

**3. Security Analysis**
- Runs security scanners (bandit, safety)
- Identifies vulnerabilities
- Generates security reports

**4. Testing Analysis**
- Calculates test coverage
- Finds missing tests
- Analyzes test quality

**5. Quality Analysis**
- Code quality metrics (pylint, flake8)
- Code smells detection
- Best practices violations

**6. Compliance Checks**
- ISO 22301 compliance verification (для BCM)
- Regulatory compliance checks
- Generates compliance reports

**7. Documentation**
- Doc-code consistency checks
- Changelog generation from git
- Process maps from BPMN/YAML

**8. Reporting**
- Daily reports
- Weekly summaries
- Donor summaries

### Test Project

```
test-project/
├── src/
│   ├── app.py
│   ├── risk_assessment.py          # BCM example
│   └── incident_manager.py         # BCM example
├── tests/
│   ├── test_risk.py
│   └── test_incident.py
└── config/
    └── .project-agent.yml
```

**Назначение:** Demo project для тестирования Project Agent на BCM коде

### Связь с BCM?

**Есть BCM-specific функциональность:**
1. `compliance.py` - ISO 22301 compliance check
2. `bpmn_yaml.py` - Parse BCM process maps
3. Test project с BCM примерами (risk, incident)

**НО:**
- Project Agent = general-purpose tool
- BCM = one of supported domains
- Не связан с Project Manager AI
- Не связан с Project Intelligence Service

### Оценка

**Назначение:** ⭐⭐⭐⭐⭐ (Universal code analysis tool)
**BCM Support:** ⭐⭐⭐⭐ (ISO 22301 compliance module)
**Connection to PM Components:** ⭐ (None - completely separate)

**Вывод:** Это НЕ часть Project Management экосистемы. Это separate CLI tool для code analysis.

---

## СИНТЕЗ: КАК ВСЕ СВЯЗАНО

### Реальная Архитектура

```
┌─────────────────────────────────────────────────────────────────┐
│ USER LAYER                                                      │
│ ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│ │ Web UI       │  │ Chat Bot     │  │ Developer CLI│          │
│ │              │  │              │  │ (proj-agent) │          │
│ └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
└────────┼──────────────────┼──────────────────┼─────────────────┘
         │                  │                  │
         │                  │                  │ (НЕ СВЯЗАН!)
         │                  │                  ▼
         │                  │          ┌───────────────────┐
         │                  │          │ Project Agent CLI │
         │                  │          │ Code analysis     │
         │                  │          │ ISO compliance    │
         │                  │          │ Testing/Quality   │
         │                  │          └───────────────────┘
         │                  │
         ▼                  ▼
┌─────────────────────────────────────────────────────────────────┐
│ AI COLLEAGUE LAYER                                              │
│ ┌──────────────────────────────────────────────────────────────┐│
│ │ Project Manager AI (RAG-based Consultant)                    ││
│ │ - Консультирует пользователя                                ││
│ │ - Дает qualitative insights                                  ││
│ │ - Использует RAG для advice                                  ││
│ └────────────────────────┬─────────────────────────────────────┘│
└──────────────────────────┼───────────────────────────────────────┘
                           │
                           │ Должен вызывать (planned, not implemented)
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ EXECUTION ENGINE LAYER                                          │
│ ┌──────────────────────────────────────────────────────────────┐│
│ │ Project Intelligence Service (FastAPI)                       ││
│ │ Port: 8025                                                    ││
│ │ - Quantitative analysis (health score)                       ││
│ │ - Smart assignment algorithm                                 ││
│ │ - Deadline prediction                                        ││
│ │ - Learning from patterns                                     ││
│ └──────────────────────────────────────────────────────────────┘│
└────────────────────────┬──────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ DATA LAYER (Planned)                                            │
│ ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│ │ PostgreSQL   │  │ Learning     │  │ Historical   │          │
│ │ (Projects)   │  │ Patterns     │  │ Data         │          │
│ └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

### Правильная Интеграция (Как Должно Быть)

```python
# Сценарий: Пользователь спрашивает про project health

# 1. User → Project Manager AI
user_query = "Как health моего проекта proj-001?"

# 2. Project Manager AI (Colleague)
class ProjectManagerAI:
    async def process_message(self, user_query, context):
        # Step 1: Получить quantitative metrics от Project Intelligence
        metrics = await self.project_intelligence_client.get_health(project_id="proj-001")
        # metrics = {health_score: 58, overdue_tasks: 2, ...}

        # Step 2: Построить RAG query с контекстом
        rag_query = f"""
        Project health metrics:
        - Health score: {metrics['health_score']}/100 (WARNING)
        - Overdue tasks: {metrics['overdue_tasks']}
        - Blocked tasks: {metrics['blocked_tasks']}

        User question: {user_query}

        Provide insights and recommendations.
        """

        # Step 3: RAG дает qualitative insights
        rag_result = await self.rag.process_query(rag_query, tenant_id)

        # Step 4: Combine quantitative + qualitative
        return {
            "metrics": metrics,
            "insights": rag_result.content,
            "recommendations": rag_result.actions
        }

# 3. Response to User
# Quantitative: Health score 58 (WARNING), 2 overdue, 1 blocked
# Qualitative (RAG): "Your project is at risk due to overdue tasks.
#                     I recommend prioritizing task-123 and task-456..."
```

### Реальное Разделение Ответственности

| Компонент | Роль | Что Делает | Что НЕ Делает |
|-----------|------|------------|---------------|
| **Project Manager AI** | Consultant (Manager) | - RAG-based консультации<br>- Qualitative insights<br>- Strategic advice<br>- User-facing | ✗ Расчеты health score<br>✗ Алгоритмы assignment<br>✗ ML predictions<br>✗ Data storage |
| **Project Intelligence** | Execution Engine (Worker) | - Quantitative analysis<br>- Health score calculation<br>- Smart assignment<br>- Deadline prediction<br>- Pattern learning | ✗ User interactions<br>✗ Qualitative advice<br>✗ RAG consultations<br>✗ Strategic recommendations |
| **Project Agent** | Code Analysis Tool | - Code quality checks<br>- Security scanning<br>- ISO compliance<br>- Testing analysis | ✗ BCM project management<br>✗ Task assignment<br>✗ Project health<br>✗ Связь с первыми двумя |

### Паттерн: Colleague → Service

```
User Question
    ↓
Project Manager AI (Colleague)
    ├─→ Project Intelligence Service (quantitative)
    │   └─→ Returns: metrics, scores, predictions
    │
    └─→ RAG Pipeline (qualitative)
        └─→ Returns: insights, recommendations

    ↓ Combine

Response to User (quantitative + qualitative)
```

---

## ВЫВОДЫ И РЕКОМЕНДАЦИИ

### ✅ Что Работает Хорошо

1. **Project Intelligence Service**
   - Отличная портация из Odoo
   - Production-ready AI algorithms
   - Полная документация
   - REST API готов к использованию

2. **Project Manager AI**
   - Хорошая реализация AI Colleague
   - 4 unique methods (rich functionality)
   - Отличное использование RAG
   - Production-ready

3. **Четкое Разделение**
   - Colleague = consult (qualitative)
   - Service = execute (quantitative)
   - Правильный паттерн!

### ⚠️ Проблемы

1. **Нет Реальной Интеграции**
   - Project Manager AI упоминает ProjectIntelligenceEngine
   - НО в коде нет HTTP calls к service
   - Нужно implement ProjectIntelligenceClient

2. **In-Memory Storage**
   - Project Intelligence использует in-memory
   - Нужна PostgreSQL для production
   - Learning patterns теряются при рестарте

3. **Project Agent - Confusion**
   - Имя вводит в заблуждение
   - Это НЕ часть project management
   - Это generic code analysis tool
   - Рассмотреть rename в "Code Agent" или перенести в tools/

### 🎯 Рекомендации

#### Приоритет 1: Implement Integration

```python
# 1. Создать клиент для Project Intelligence Service
class ProjectIntelligenceClient:
    def __init__(self, base_url="http://localhost:8025"):
        self.base_url = base_url

    async def analyze_project(self, project_data):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/projects/{project_id}/analyze"
            )
            return response.json()

    async def get_health(self, project_id):
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/v1/projects/{project_id}/health"
            )
            return response.json()

    async def suggest_assignee(self, project_id, task_id):
        # ...

# 2. Inject в Project Manager AI
class ProjectManagerAI(BaseAIColleague):
    def __init__(self, rag_pipeline, config):
        super().__init__(...)
        self.intelligence = ProjectIntelligenceClient(
            config.get("project_intelligence_url", "http://localhost:8025")
        )

    async def analyze_project_health(self, project_data, tenant_id):
        # Call service для quantitative
        metrics = await self.intelligence.analyze_project(project_data)

        # Use RAG для qualitative
        rag_result = await self.rag.process_query(...)

        # Combine
        return {
            "metrics": metrics,
            "insights": rag_result.content
        }
```

**Effort:** 1-2 дня

---

#### Приоритет 2: Add PostgreSQL to Project Intelligence

```python
# Вместо in-memory storage
projects_db: Dict[str, Project] = {}

# Использовать Supabase/PostgreSQL
from infrastructure.database.managers import SupabaseManager

class ProjectIntelligenceEngine:
    def __init__(self, db_manager: SupabaseManager):
        self.db = db_manager

    async def create_project(self, project: Project):
        result = await self.db.client.table("bcm_projects").insert({
            "id": project.id,
            "name": project.name,
            "bcm_type": project.bcm_type,
            # ...
        }).execute()
        return result

    async def _learn_from_analysis(self, project, metrics):
        # Persist learning patterns в БД
        await self.db.client.table("learning_patterns").insert({
            "project_id": project.id,
            "pattern_type": "project_analysis",
            "pattern_data": {...},
            "timestamp": datetime.now()
        }).execute()
```

**Effort:** 2-3 дня

---

#### Приоритет 3: Clarify Project Agent

**Опция A: Rename**
```bash
mv project-agent/ code-analysis-agent/
# Update docs, configs
```

**Опция B: Move to Tools**
```bash
mv intelligent-core/ai-office/project-agent/ tools/code-agent/
```

**Опция C: Keep but Document**
- Добавить README с четким объяснением
- Это universal code analysis tool
- Supports BCM projects через ISO compliance module
- NOT part of BCM project management (Project Manager AI)

**Effort:** 1 час (документация)

---

#### Приоритет 4: EventBus Integration

```python
# Project Intelligence Service публикует события
class ProjectIntelligenceEngine:
    async def analyze_project(self, project):
        analysis = self._perform_analysis(project)

        # Publish event
        await self.eventbus.publish("project_analyzed", {
            "project_id": project.id,
            "health_score": analysis.health_metrics.health_score,
            "health_status": analysis.health_metrics.health_status,
            "risks": analysis.risks,
            "timestamp": datetime.now()
        })

        return analysis

# Project Manager AI подписывается
class ProjectManagerAI:
    def __init__(self, ...):
        self.eventbus.subscribe("project_analyzed", self._on_project_analyzed)

    async def _on_project_analyzed(self, event):
        # Learn from patterns
        # Update recommendations
        # Trigger proactive alerts if needed
```

**Effort:** 1-2 дня

---

## ИТОГОВАЯ ТАБЛИЦА

| Компонент | Строк | Роль | Статус | Интеграция | Оценка |
|-----------|-------|------|--------|-----------|--------|
| **Project Intelligence Service** | 732 | Backend Engine (quantitative) | ✅ Production | ⚠️ API ready, not called | ⭐⭐⭐⭐⭐ |
| **Project Manager AI** | 423 | AI Colleague (qualitative) | ✅ Production | ⚠️ Needs HTTP client | ⭐⭐⭐⭐⭐ |
| **Project Agent** | ~2000 | Code Analysis CLI | ✅ Working | ❌ NOT related | ⭐⭐⭐ |

**Общая Оценка:** ⭐⭐⭐⭐ (4/5)

**Для 5/5 нужно:**
1. Implement integration (Colleague → Service)
2. Add PostgreSQL to Service
3. Clarify Project Agent role (rename/move/document)
4. EventBus integration

---

**Конец детального анализа**
**Теперь ВСЕ ясно - никаких догадок! 🎯**
