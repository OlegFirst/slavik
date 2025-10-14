# DevOps Agent - AI Foundation Tool Usage Fix

## 🚨 Проблема обнаружена

DevOps Agent **НЕ ИСПОЛЬЗУЕТ** ai-foundation инструменты правильно:

```python
# agent.py:72-76
self.rag = RAGPipeline()  # ✅ Инициализирован
self.llm = LLMRouter()     # ✅ Инициализирован

# НО:
# grep "self.rag." -> No matches found ❌
# grep "self.llm." -> Только 1 раз в строке 219 ❌
```

---

## ✅ Правильная интеграция

### **1. RAG для извлечения знаний перед анализом**

**Текущий код (agent.py:194-228):**
```python
async def ai_analysis(self, scan_results: Dict) -> Dict:
    """AI-powered analysis of scan results"""

    # ❌ Просто передаем результаты в LLM без знаний
    context = f"""
    Infrastructure Scan Results:
    {scan_results}

    Analyze these results...
    """

    response = await self.llm.route_request(
        prompt=context,
        task_type="infrastructure_analysis"
    )
```

**Исправленная версия:**
```python
async def ai_analysis(self, scan_results: Dict) -> Dict:
    """AI-powered analysis with knowledge retrieval"""

    logger.info("🧠 Running AI analysis with knowledge retrieval...")

    if not self.llm:
        logger.warning("LLM not initialized, skipping AI analysis")
        return {"recommendations": []}

    # 🔹 ШАГ 1: Извлечение релевантных знаний из RAG
    relevant_knowledge = []

    if self.rag:
        # Формируем поисковые запросы из результатов сканирования
        search_queries = []

        # Event architecture issues
        if scan_results.get("events", {}).get("critical_gaps", 0) > 0:
            search_queries.append("critical event architecture gaps solutions")

        # Container issues
        if scan_results.get("containers", {}).get("missing_dockerfiles", 0) > 0:
            search_queries.append("dockerfile best practices for microservices")

        # Port conflicts
        if scan_results.get("deployments", {}).get("port_conflicts", 0) > 0:
            search_queries.append("port conflict resolution deployment")

        # Retrieve knowledge for each query
        for query in search_queries:
            knowledge_chunks = await self.rag.retrieve(
                query=query,
                context={
                    "domain": "devops",
                    "task": "infrastructure_analysis"
                },
                top_k=3,
                filters={"source_type": "devops_patterns"},
                enable_reranking=True
            )
            relevant_knowledge.extend(knowledge_chunks)

        logger.info(f"📚 Retrieved {len(relevant_knowledge)} knowledge chunks from RAG")

    # 🔹 ШАГ 2: Формирование контекста с знаниями
    knowledge_context = self._format_knowledge_context(relevant_knowledge)

    # Build enriched context for LLM
    enriched_context = f"""
    === RELEVANT KNOWLEDGE FROM PAST EXPERIENCES ===
    {knowledge_context}

    === CURRENT INFRASTRUCTURE SCAN RESULTS ===
    {self._format_scan_results(scan_results)}

    === TASK ===
    Based on the relevant knowledge and current scan results:
    1. Identify the most critical issues
    2. Provide specific recommendations with priority ranking
    3. Assess risk level for each issue
    4. Suggest which issues can be auto-fixed safely

    Format response as JSON with structure:
    {{
      "recommendations": [
        {{
          "id": "unique_id",
          "category": "event_architecture|missing_dockerfile|port_conflict",
          "priority": "critical|high|medium|low",
          "description": "detailed description",
          "suggested_action": "specific action to take",
          "auto_fix_safe": true|false,
          "risk_level": "high|medium|low"
        }}
      ],
      "risk_level": "critical|high|medium|low",
      "auto_fix_approved": true|false
    }}
    """

    # 🔹 ШАГ 3: Запрос к LLM с полным контекстом
    response = await self.llm.query(
        system_prompt="""You are an expert DevOps infrastructure analyst.
        Analyze infrastructure issues based on historical patterns and current data.
        Provide actionable, specific recommendations.""",
        user_prompt=enriched_context,
        task_type="infrastructure_analysis",
        temperature=0.3,  # Low temperature for consistent analysis
        max_tokens=3000
    )

    # Parse JSON response
    try:
        import json
        ai_analysis = json.loads(response)
    except json.JSONDecodeError:
        logger.error("Failed to parse LLM response as JSON")
        ai_analysis = {"recommendations": [], "risk_level": "unknown"}

    return ai_analysis


def _format_knowledge_context(self, knowledge_chunks: List[Dict]) -> str:
    """Format knowledge chunks for LLM context"""
    if not knowledge_chunks:
        return "No relevant historical knowledge found."

    formatted = []
    for i, chunk in enumerate(knowledge_chunks, 1):
        formatted.append(f"""
        Knowledge {i}:
        Source: {chunk.get('source', 'unknown')}
        Content: {chunk.get('content', '')}
        Relevance Score: {chunk.get('score', 0.0):.2f}
        """)

    return "\n".join(formatted)


def _format_scan_results(self, scan_results: Dict) -> str:
    """Format scan results for LLM context"""
    formatted = []

    if "events" in scan_results:
        events = scan_results["events"]
        formatted.append(f"""
        EVENT ARCHITECTURE:
        - Schema Events: {events.get('schema_events', 0)}
        - Code Events: {events.get('code_events', 0)}
        - Gaps Found: {events.get('gaps_found', 0)}
        - Critical Gaps: {events.get('critical_gaps', 0)}
        - Potential Events: {events.get('potential_events', 0)}
        """)

    if "containers" in scan_results:
        containers = scan_results["containers"]
        formatted.append(f"""
        CONTAINERS:
        - Missing Dockerfiles: {containers.get('missing_dockerfiles', 0)}
        - Services Analyzed: {containers.get('services_analyzed', 0)}
        - Issues Found: {containers.get('issues_found', 0)}
        """)

    if "deployments" in scan_results:
        deployments = scan_results["deployments"]
        formatted.append(f"""
        DEPLOYMENTS:
        - Total Services: {deployments.get('total_services', 0)}
        - Healthy Services: {deployments.get('healthy_services', 0)}
        - Port Conflicts: {deployments.get('port_conflicts', 0)}
        """)

    return "\n".join(formatted)
```

---

### **2. Сохранение успешных паттернов в RAG**

**Добавить в метод apply_fixes (после строки 293):**

```python
async def apply_fixes(self, recommendations: List[Dict]) -> Dict:
    """Apply auto-remediation WITH BRAIN APPROVAL"""

    # ... existing code ...

    for action in approved_actions:
        fix_result = None

        # ... apply fix ...

        if fix_result and fix_result.get("success"):
            results["fixes_successful"] += 1
            self.fixes_applied += 1

            # ✅ НОВОЕ: Сохранить успешный паттерн в RAG
            if self.rag:
                await self._store_successful_pattern(action, fix_result)

            # Send feedback to brain
            if self.workflow_intelligence:
                await self.workflow_intelligence.report_fix_applied({...})

    return results


async def _store_successful_pattern(self, action: Dict, fix_result: Dict):
    """Store successful fix pattern in knowledge base"""

    pattern_text = f"""
    SUCCESSFUL FIX PATTERN

    Category: {action.get('category', 'unknown')}
    Priority: {action.get('priority', 'unknown')}

    Problem Description:
    {action.get('description', 'N/A')}

    Solution Applied:
    {action.get('suggested_action', 'N/A')}

    Outcome:
    {fix_result.get('outcome', 'Applied successfully')}

    Risk Level: {action.get('risk_level', 'unknown')}
    Auto-fix Safe: {action.get('auto_fix_safe', False)}

    Success Rate: 100% (verified)
    Applied At: {datetime.utcnow().isoformat()}
    """

    await self.rag.ingest_documents(
        documents=[{
            "text": pattern_text,
            "metadata": {
                "source_type": "devops_patterns",
                "pattern_category": action.get("category"),
                "priority": action.get("priority"),
                "auto_fix_safe": action.get("auto_fix_safe"),
                "success_rate": 1.0,
                "timestamp": datetime.utcnow().isoformat()
            }
        }],
        source_type="devops_patterns"
    )

    logger.info(f"💾 Successful pattern stored in RAG: {action.get('category')}")
```

---

### **3. Использование LLM для генерации Dockerfile**

**В auto_remediation/dockerfile_generator.py:**

```python
class DockerfileGenerator:
    """Generate Dockerfiles using AI"""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.llm: Optional[LLMRouter] = None
        self.rag: Optional[RAGPipeline] = None

    async def initialize(self):
        """Initialize AI components"""
        self.llm = LLMRouter()
        self.rag = RAGPipeline()

    async def generate(self, service_metadata: Dict) -> Dict:
        """Generate Dockerfile for service using AI"""

        # 1. Retrieve similar Dockerfile patterns from RAG
        similar_patterns = []
        if self.rag:
            similar_patterns = await self.rag.retrieve(
                query=f"dockerfile for {service_metadata['language']} {service_metadata['framework']} service",
                context={
                    "language": service_metadata['language'],
                    "framework": service_metadata.get('framework', 'unknown')
                },
                top_k=3,
                filters={"source_type": "dockerfile_patterns"}
            )

        # 2. Generate Dockerfile using LLM
        if self.llm:
            dockerfile_content = await self.llm.query(
                system_prompt="""You are a Docker expert. Generate production-ready Dockerfiles.""",
                user_prompt=f"""
                Generate a Dockerfile for:

                Service: {service_metadata['name']}
                Language: {service_metadata['language']}
                Framework: {service_metadata.get('framework', 'unknown')}
                Dependencies: {service_metadata.get('dependencies', [])}

                Similar patterns from knowledge base:
                {self._format_patterns(similar_patterns)}

                Requirements:
                - Multi-stage build
                - Security best practices
                - Health check
                - Non-root user
                - Optimized layers
                """,
                task_type="content_generation",
                temperature=0.2  # Low temp for consistent Dockerfiles
            )

            # 3. Save generated Dockerfile
            dockerfile_path = self.project_root / service_metadata['path'] / 'Dockerfile'
            dockerfile_path.write_text(dockerfile_content)

            # 4. Store this pattern in RAG for future use
            if self.rag:
                await self.rag.ingest_documents(
                    documents=[{
                        "text": f"Dockerfile for {service_metadata['language']} service:\n{dockerfile_content}",
                        "metadata": {
                            "source_type": "dockerfile_patterns",
                            "language": service_metadata['language'],
                            "framework": service_metadata.get('framework')
                        }
                    }],
                    source_type="dockerfile_patterns"
                )

            return {
                "success": True,
                "path": str(dockerfile_path),
                "content": dockerfile_content
            }

        return {"success": False, "error": "LLM not available"}
```

---

## 📊 Итоговое использование инструментов

### **RAG Pipeline использование:**

1. ✅ **Извлечение знаний** - `ai_analysis()` перед LLM запросом
2. ✅ **Сохранение паттернов** - после успешного fix
3. ✅ **Dockerfile генерация** - поиск похожих паттернов

### **LLM Router использование:**

1. ✅ **Анализ инфраструктуры** - `ai_analysis()` с полным контекстом
2. ✅ **Генерация Dockerfile** - AI-powered генерация
3. ✅ **Принятие решений** - оценка рисков и приоритетов

---

## 🔄 Цикл обучения DevOps Agent

```
1. Scan Infrastructure
   ↓
2. Retrieve Knowledge from RAG (historical patterns)
   ↓
3. AI Analysis with LLM (enriched context)
   ↓
4. Request Approval from Brain
   ↓
5. Apply Fixes
   ↓
6. Store Successful Patterns in RAG
   ↓
7. Report to Brain + Feedback Loop
   ↓
[Repeat - becomes smarter each cycle]
```

---

## 📈 Метрики для мониторинга

```python
# Добавить в agent.py
from intelligent_core.ai_foundation.rag.metrics import (
    retrieval_search_duration_seconds,
    retrieval_context_size_tokens
)
from intelligent_core.ai_foundation.llm.metrics import (
    llm_tokens_used_total,
    llm_cost_usd_total
)

async def ai_analysis(self, scan_results: Dict) -> Dict:
    # ... existing code ...

    # Track RAG usage
    retrieval_search_duration_seconds.labels(
        collection="devops_patterns"
    ).observe(rag_search_time)

    # Track LLM usage
    llm_tokens_used_total.labels(
        provider="anthropic",
        model="claude-3-5-sonnet-20241022",
        type="completion"
    ).inc(tokens_used)
```

---

## ✅ Checklist для имплементации

- [ ] Обновить `ai_analysis()` с RAG integration
- [ ] Добавить `_format_knowledge_context()` метод
- [ ] Добавить `_format_scan_results()` метод
- [ ] Добавить `_store_successful_pattern()` метод
- [ ] Обновить DockerfileGenerator с AI generation
- [ ] Добавить метрики для RAG и LLM
- [ ] Тестировать полный цикл обучения
- [ ] Документировать patterns в RAG

---

## 🎯 Результат

DevOps Agent станет **по-настоящему умным коллегой**:

✅ Использует историю успешных решений (RAG)
✅ Принимает решения на основе знаний (LLM + RAG)
✅ Обучается на каждом успешном fix
✅ Генерирует код (Dockerfile) с AI
✅ Становится умнее с каждым циклом

Вместо простого скрипта -> **AI Digital Colleague с памятью и обучением**! 🚀
