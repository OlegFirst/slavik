# RTO Predictor - Анализ и Решение

## Текущее состояние

### Где сейчас RTO prediction логика?

#### 1. **Impact Oracle** ✅ (AI Office Organ)
**Файл:** `intelligent-core/ai-office/organs/impact_oracle.py`

**Что делает:**
```python
class ImpactOracle:
    """
    Predictive BIA organ
    - Predict business impact
    - Recommend RTO/RPO targets
    - Assess financial/operational impacts
    - Forecast cascading effects
    """
```

**Сильные стороны:**
- ✅ Интеграция с Digital Twin (реальное состояние организации)
- ✅ Industry benchmarks
- ✅ LLM-powered (адаптивные рекомендации)
- ✅ Учёт disruption scenario

**Пример использования:**
```python
result = await impact_oracle.analyze({
    'twin_id': 'org_123',
    'disruption_scenario': 'Ransomware attack on ERP',
    'process_data': {'name': 'Order Processing'}
})

# Возвращает:
# - recommended_rto_hours
# - financial_impact
# - operational_impact
# - reasoning
```

---

#### 2. **BIA Specialist AI** ✅ (AI Colleague)
**Файл:** `intelligent-core/ai-office/colleagues/bia_specialist/bia_specialist.py`

**Что делает:**
```python
class BIASpecialistAI:
    """
    BIA Expert
    - RTO/RPO determination
    - MTD/MBCO calculations
    - Criticality analysis
    - Dependency mapping
    """
```

**Критерии:**
```python
Criticality Tiers:
- Tier 1 (Critical):    RTO < 4h   - severe immediate impact
- Tier 2 (Important):   RTO 4-24h  - significant impact  
- Tier 3 (Necessary):   RTO 1-7d   - manageable impact
- Tier 4 (Deferrable):  RTO > 7d   - minimal impact
```

**Сильные стороны:**
- ✅ ISO 22301 compliance (clause 8.2.2)
- ✅ Structured methodology
- ✅ Tiered approach (4 tiers)
- ✅ RAG pipeline (использует знания из документов)
- ✅ Conversational AI (может задавать уточняющие вопросы)

---

#### 3. **Case Library Benchmarking** ✅ (Community Intelligence)
**Файл:** `intelligent-core/workflow_intelligence/case_library/repository.py`

**Что делает:**
```python
class CaseRepository:
    async def get_benchmarks(industry, size, module):
        """
        Returns statistical benchmarks:
        - avg_rto_hours (среднее по индустрии)
        - median_rto_hours (медиана)
        - p90_rto_hours (90-й перцентиль)
        - similar_cases_count
        """
```

**Сильные стороны:**
- ✅ Реальные данные от community
- ✅ Статистический подход
- ✅ Industry-specific
- ✅ Size-specific (small, medium, large orgs)

---

#### 4. **Creative Zones** ✅ (Governance)
**Файл:** `intelligent-core/Governance System/governance/creative_zones.py`

**Что делает:**
```python
CreativeZone(
    name="RTO Recommendation",
    description="AI recommends RTO with reasoning",
    creativity_level=CreativityLevel.MEDIUM,
    forbidden_actions=[
        "Recommend RTO without justification",
        "Ignore industry standards",
        "Skip dependency analysis"
    ]
)
```

**Сильные стороны:**
- ✅ Управление AI свободой
- ✅ Обязательные проверки
- ✅ Escalation если критичные нарушения

---

## Вопрос: Нужен ли отдельный RTO Predictor?

### Вариант А: ❌ НЕ создавать (использовать существующее)

**Обоснование:**
1. **Impact Oracle** уже делает prediction с учётом:
   - Digital Twin state
   - Industry benchmarks
   - Disruption scenarios
   - Financial/operational impact

2. **BIA Specialist AI** предоставляет:
   - Structured methodology (ISO 22301)
   - Tiered criticality
   - Conversational guidance

3. **Case Library** даёт:
   - Real-world benchmarks
   - Statistical data

4. **Комбинация даёт полную картину:**
   ```
   Impact Oracle → RTO recommendation (ML-based, contextual)
   +
   BIA Specialist → Validation (methodology, standards)
   +
   Case Library → Benchmarks (community data)
   =
   Comprehensive RTO Prediction
   ```

**Минусы:**
- Нет единой точки входа для "predict RTO"
- Логика распределена (нужно знать где что брать)

---

### Вариант B: ✅ Создать фасад (рекомендуется)

**Что:** Создать `RTOPredictor` как **унифицированный интерфейс** над существующими сервисами.

**Где:** `intelligent-core/ai-office/organs/predictors/rto_predictor.py`

**Архитектура:**
```python
class RTOPredictor(BaseAIOrgan):
    """
    Unified RTO Prediction Service
    
    Aggregates:
    - Impact Oracle (AI prediction)
    - BIA Specialist (methodology validation)
    - Case Library (benchmarks)
    - Creative Zones (governance)
    """
    
    def __init__(
        self,
        impact_oracle: ImpactOracle,
        bia_specialist: BIASpecialistAI,
        case_library: CaseRepository,
        creative_zones: CreativeZonesManager
    ):
        self.impact_oracle = impact_oracle
        self.bia_specialist = bia_specialist
        self.case_library = case_library
        self.zones = creative_zones
    
    async def predict_rto(
        self,
        process: Dict,
        organization: Dict,
        scenario: Optional[str] = None
    ) -> RTOPrediction:
        """
        Comprehensive RTO prediction
        
        Steps:
        1. Get AI prediction (Impact Oracle)
        2. Get benchmarks (Case Library)
        3. Validate methodology (BIA Specialist)
        4. Check governance (Creative Zones)
        5. Return unified result
        """
        
        # 1. AI Prediction
        ai_prediction = await self.impact_oracle.analyze({
            'twin_id': organization.get('twin_id'),
            'process_data': process,
            'disruption_scenario': scenario
        })
        
        # 2. Industry Benchmarks
        benchmarks = await self.case_library.get_benchmarks(
            industry=organization.get('industry'),
            size=organization.get('size'),
            module='bia'
        )
        
        # 3. Validate with BIA methodology
        validation = await self.bia_specialist.assist({
            'task': 'validate_rto',
            'ai_recommendation': ai_prediction['recommended_rto_hours'],
            'process_criticality': process.get('criticality'),
            'benchmarks': benchmarks
        })
        
        # 4. Governance check
        governance_check = await self.zones.validate_action(
            zone='rto_recommendation',
            proposed_rto=ai_prediction['recommended_rto_hours'],
            reasoning=ai_prediction.get('reasoning')
        )
        
        # 5. Unified result
        return RTOPrediction(
            recommended_rto_hours=ai_prediction['recommended_rto_hours'],
            confidence_score=self._calculate_confidence(
                ai_prediction, benchmarks, validation
            ),
            reasoning=ai_prediction['reasoning'],
            benchmark_avg=benchmarks['avg_rto_hours'],
            benchmark_range=(benchmarks['p10_rto_hours'], benchmarks['p90_rto_hours']),
            methodology_compliant=validation['compliant'],
            governance_approved=governance_check['approved'],
            alternative_scenarios=[
                # Pessimistic, optimistic scenarios
            ],
            recommendations=[
                # Action items to achieve this RTO
            ]
        )
    
    def _calculate_confidence(self, ai_pred, benchmarks, validation) -> float:
        """
        Calculate confidence score
        
        Factors:
        - How close to benchmark average (30%)
        - Methodology compliance (30%)
        - AI model confidence (20%)
        - Data quality (20%)
        """
        confidence = 0.0
        
        # Closeness to benchmark
        ai_rto = ai_pred['recommended_rto_hours']
        bench_avg = benchmarks['avg_rto_hours']
        deviation = abs(ai_rto - bench_avg) / bench_avg
        if deviation < 0.2:  # Within 20%
            confidence += 0.3
        elif deviation < 0.5:  # Within 50%
            confidence += 0.15
        
        # Methodology compliance
        if validation['compliant']:
            confidence += 0.3
        
        # AI confidence
        if 'confidence' in ai_pred:
            confidence += ai_pred['confidence'] * 0.2
        
        # Data quality (number of similar cases)
        if benchmarks['similar_cases_count'] > 10:
            confidence += 0.2
        elif benchmarks['similar_cases_count'] > 5:
            confidence += 0.1
        
        return min(confidence, 1.0)
```

**Использование:**
```python
# Simple usage
rto_predictor = RTOPredictor(impact_oracle, bia_specialist, case_library, zones)

result = await rto_predictor.predict_rto(
    process={
        'name': 'Order Processing',
        'criticality': 'high',
        'dependencies': ['ERP', 'Payment Gateway']
    },
    organization={
        'twin_id': 'org_123',
        'industry': 'healthcare',
        'size': 'medium'
    },
    scenario='Ransomware attack'
)

print(f"Recommended RTO: {result.recommended_rto_hours}h")
print(f"Confidence: {result.confidence_score * 100}%")
print(f"Benchmark average: {result.benchmark_avg}h")
print(f"Reasoning: {result.reasoning}")
```

**Преимущества Варианта B:**
1. ✅ **Единая точка входа** - разработчики знают куда идти
2. ✅ **Композиция существующих сервисов** - не дублируем код
3. ✅ **Confidence scoring** - оценка надёжности prediction
4. ✅ **Governance integration** - автоматические проверки
5. ✅ **Extensible** - легко добавить новые факторы
6. ✅ **Testable** - можно unit-тестировать логику композиции

---

## Рекомендация: ✅ Вариант B

**Создать RTOPredictor как фасад** над существующими сервисами.

### План реализации:

#### Шаг 1: Создать базовую структуру
```bash
mkdir -p intelligent-core/ai-office/organs/predictors
touch intelligent-core/ai-office/organs/predictors/__init__.py
touch intelligent-core/ai-office/organs/predictors/rto_predictor.py
```

#### Шаг 2: Реализовать RTOPredictor
- Композиция Impact Oracle + BIA Specialist + Case Library
- Confidence scoring
- Governance validation
- Structured RTOPrediction output

#### Шаг 3: Добавить REST API endpoint
```python
# intelligent-core/ai-office/api/rto_router.py

@router.post("/rto/predict", response_model=RTOPredictionResponse)
async def predict_rto(
    request: RTOPredictionRequest,
    predictor: RTOPredictor = Depends(get_rto_predictor)
):
    """
    Predict optimal RTO for process
    
    Uses:
    - AI prediction (Impact Oracle)
    - Industry benchmarks
    - BIA methodology validation
    - Governance checks
    """
    result = await predictor.predict_rto(
        process=request.process,
        organization=request.organization,
        scenario=request.scenario
    )
    return result
```

#### Шаг 4: Интеграция с Workflow Intelligence
```python
# В BIA Workflow Engine
class BIAWorkflowEngine:
    async def suggest_rto(self, process_id: str):
        """Get AI-recommended RTO for process"""
        process = self.context['processes'][process_id]
        
        rto_prediction = await self.rto_predictor.predict_rto(
            process=process,
            organization=self.org_context
        )
        
        return rto_prediction
```

#### Шаг 5: Тестирование
```python
# tests/test_rto_predictor.py

async def test_rto_predictor_confidence():
    """Test confidence calculation"""
    predictor = RTOPredictor(...)
    
    result = await predictor.predict_rto(
        process={'name': 'Test', 'criticality': 'high'},
        organization={'industry': 'healthcare', 'size': 'medium'}
    )
    
    assert 0.0 <= result.confidence_score <= 1.0
    assert result.methodology_compliant is True
    assert result.governance_approved is True
```

---

## Итого

### Что делать с ai_capabilities/rto_predictor/?

**Решение:**
1. ✅ Удалить заглушку `/intelligent-core/ai_capabilities/rto_predictor/`
2. ✅ Создать полноценный RTOPredictor в `/intelligent-core/ai-office/organs/predictors/`
3. ✅ Использовать композицию существующих сервисов (не дублировать логику)

### Файлы для создания:

```
intelligent-core/ai-office/organs/predictors/
├── __init__.py
├── rto_predictor.py           # Main predictor
├── confidence_scorer.py       # Confidence calculation logic
└── models.py                  # RTOPrediction, RTOPredictionRequest

intelligent-core/ai-office/api/
└── rto_router.py              # REST API endpoints

tests/
└── test_rto_predictor.py      # Unit tests
```

---

**Хочешь чтобы я создал RTOPredictor модуль?** 🚀

---

**Дата**: 2025-10-04  
**Статус**: Решение принято  
**Действие**: Создать RTOPredictor как фасад
