# 🛠️ Tools Специалистов (Level 3)

## Где находятся
`/intelligent-core/ai_experts/tools/`

## Все Tools (12 штук)

### 📊 BIA Tools (`bia_tools.py` - 21KB)

#### 1. **BIAAnalysisTool**
**Что делает**: Анализ критичности бизнес-процессов
- Определяет criticality level (critical/important/normal)
- Рассчитывает RTO (Recovery Time Objective)
- Рассчитывает RPO (Recovery Point Objective)
- Оценивает impact over time

**Параметры**:
- `process_name` (required)
- `industry` (required)
- `process_description` (required)
- `annual_revenue` (optional)

**Пример**:
```python
result = await bia_tool.execute(
    process_name="Payment Processing",
    industry="finance",
    process_description="Real-time payment transactions"
)
# Returns: {
#   "criticality": "critical",
#   "rto": "4 hours",
#   "rpo": "1 hour",
#   "impact_analysis": {...}
# }
```

---

#### 2. **DependencyMapperTool**
**Что делает**: Картирует зависимости процессов
- Upstream dependencies (от чего зависит)
- Downstream dependencies (что зависит от этого)
- Critical path analysis

**Параметры**:
- `process_name` (required)
- `organization_context` (optional)

---

#### 3. **ImpactCalculatorTool**
**Что делает**: Рассчитывает финансовый/операционный impact
- Финансовый impact (revenue loss)
- Операционный impact (производительность)
- Репутационный impact
- Regulatory impact

**Параметры**:
- `process_name` (required)
- `downtime_hours` (required)
- `annual_revenue` (optional)

---

### ✅ Compliance Tools (`compliance_tools.py` - 23KB)

#### 4. **ComplianceCheckTool**
**Что делает**: Проверка соответствия ISO 22301
- Clause-by-clause assessment (4.1, 4.2, 5.1, etc)
- Compliance percentage
- Non-compliant clauses

**Параметры**:
- `organization_id` (required)
- `clauses_to_check` (optional, default: all)

**Пример**:
```python
result = await compliance_tool.execute(
    organization_id="org_123",
    clauses_to_check=["4.1", "5.2", "8.1"]
)
# Returns: {
#   "compliance_score": 73,
#   "compliant": ["4.1", "5.2"],
#   "non_compliant": ["8.1"],
#   "details": {...}
# }
```

---

#### 5. **GapAnalysisTool**
**Что делает**: Комплексный gap analysis
- Идентифицирует missing elements
- Приоритизирует remediation
- Создаёт action plan

**Параметры**:
- `organization_id` (required)
- `target_standard` (default: "ISO 22301:2019")

---

#### 6. **EvidenceValidatorTool**
**Что делает**: Валидация доказательств для аудита
- Проверяет качество evidence
- Completeness check
- Рекомендации по улучшению

**Параметры**:
- `clause` (required)
- `evidence_items` (required)

---

### 📈 Strategic Tools (`strategic_tools.py` - 37KB)

#### 7. **TimelinePredictorTool**
**Что делает**: Предсказывает сроки внедрения BCM
- На основе размера организации
- Complexity factors
- Resource availability

**Параметры**:
- `organization_size` (required: small/medium/large)
- `current_maturity` (required: 1-5)
- `target_maturity` (required: 1-5)
- `available_resources` (optional)

**Пример**:
```python
result = await timeline_tool.execute(
    organization_size="medium",
    current_maturity=2,
    target_maturity=4
)
# Returns: {
#   "estimated_months": 18,
#   "phases": [
#     {"name": "Foundation", "duration": 3},
#     {"name": "Implementation", "duration": 12},
#     {"name": "Optimization", "duration": 3}
#   ]
# }
```

---

#### 8. **ResourcePlannerTool**
**Что делает**: Планирование ресурсов для BCM программы
- Staff time allocation
- Budget estimation
- Skill requirements

**Параметры**:
- `program_scope` (required)
- `organization_size` (required)
- `timeline_months` (required)

---

#### 9. **MaturityAssessmentTool**
**Что делает**: Оценка зрелости BCM программы
- Матurity level (1-5)
- По каждому домену (Risk, BIA, Planning, etc)
- Improvement roadmap

**Параметры**:
- `organization_id` (required)
- `assessment_areas` (optional)

---

### 📚 Case Library Tool (`case_library_tool.py` - 30KB)

#### 10. **CaseSearchTool**
**Что делает**: Поиск похожих кейсов в Case Library
- Semantic search
- Industry/size filtering
- Success patterns

**Параметры**:
- `query` (required)
- `filters` (optional: industry, size, domain)
- `limit` (default: 5)

**Пример**:
```python
result = await case_search_tool.execute(
    query="BIA for payment processing",
    filters={"industry": "fintech", "size": "medium"},
    limit=3
)
# Returns: [
#   {
#     "case_id": "case_123",
#     "similarity": 0.89,
#     "summary": "...",
#     "outcome": "success",
#     "lessons_learned": [...]
#   }
# ]
```

---

#### 11. **BestPracticeLibraryTool**
**Что делает**: Библиотека best practices
- ISO 22301 best practices
- Industry-specific patterns
- Proven approaches

**Параметры**:
- `domain` (required: risk, bia, planning, etc)
- `industry` (optional)

---

### 🔧 Base Tool (`base_tool.py`)

#### 12. **BaseTool**
**Базовый класс** для всех Tools

**Возможности**:
- Валидация параметров
- Async execution
- Error handling
- Logging

---

## 🎯 Какой Специалист Использует Какие Tools

### BCMAdvisor (`bcm_advisor.py`)
```python
tools = [
    BIAAnalysisTool(db_session),         # BIA анализ
    DependencyMapperTool(case_library),   # Зависимости
    CaseSearchTool(case_library)          # Похожие кейсы
]
```

**Для чего**:
- BIA calculations
- Process dependency mapping
- Learning from similar cases

---

### ComplianceAuditor (`compliance_auditor.py`)
```python
tools = [
    ComplianceCheckTool(knowledge_graph),  # ISO 22301 check
    GapAnalysisTool(knowledge_graph),      # Gap analysis
    EvidenceValidatorTool()                # Evidence validation
]
```

**Для чего**:
- ISO 22301 compliance assessment
- Gap identification
- Audit preparation

---

### StrategicPlanner (`strategic_planner.py`)
```python
tools = [
    TimelinePredictorTool(),              # Сроки внедрения
    ResourcePlannerTool(),                # Ресурсы
    MaturityAssessmentTool()              # Зрелость программы
]
```

**Для чего**:
- BCM program planning
- Resource allocation
- Maturity roadmap

---

## 🔄 Как Коллеги Используют Tools

### Вариант 1: Делегирование Специалисту

```python
# platform-services/bia-service/colleague/bia_specialist.py
class BIASpecialistAI(BaseAIColleague):
    async def chat(self, message):
        if self._needs_calculation(message):
            # Делегируем BCMAdvisor (у него есть BIAAnalysisTool)
            specialist = BCMAdvisor(case_library, kg)
            result = await specialist.advise(message, context)
            return result
        else:
            # Простой анализ через орган
            analysis = await self.organ.analyze(context)
            return analysis
```

### Вариант 2: Прямой вызов Tools (если добавить в коллег)

```python
# Если хотим дать коллегам Tools напрямую
class BIASpecialistAI(BaseAIColleague):
    def __init__(self, rag_pipeline, db_session):
        super().__init__(...)

        # Добавляем нужные Tools
        self.bia_tool = BIAAnalysisTool(db_session)

    async def chat(self, message):
        # Используем Tool напрямую
        if "calculate bia" in message.lower():
            result = await self.bia_tool.execute(
                process_name=extract_process(message),
                industry=self.context['industry'],
                process_description=extract_desc(message)
            )
            return self._format_response(result)
```

---

## 💡 Рекомендация

**Для эффективности**:

1. **Коллеги** (Level 2) - без Tools
   - Диалог
   - PDCA
   - RAG
   - Используют органы для LLM анализа

2. **Специалисты** (Level 3) - с Tools
   - Координация
   - DB операции через Tools
   - Межмодульная работа
   - Передача в Learning/Predictive AI

**Когда коллеге нужен Tool** → делегирует Специалисту

**Пример**:
```
User: "Calculate BIA for payment processing"
     ↓
BIASpecialist (colleague) → определяет что нужен расчёт
     ↓
BCMAdvisor (specialist) → использует BIAAnalysisTool
     ↓
Result → BIASpecialist → User
```

Так **эффективно** и **разделяет ответственность**! ✅
