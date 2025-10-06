# 🧠 RAG (Retrieval-Augmented Generation) - ПОЛНАЯ АРХИТЕКТУРА

**Версия:** 2.0 Production Analysis
**Дата:** 5 октября 2025
**Статус:** ✅ Реализовано в 2 модулях

---

## 📋 ОГЛАВЛЕНИЕ

1. [Что такое RAG и зачем нужен](#1-что-такое-rag)
2. [Архитектура RAG в платформе](#2-архитектура)
3. [Реализация #1: AI-Office RAG (Live Data)](#3-ai-office-rag)
4. [Реализация #2: AI-Experts RAG (Knowledge Base)](#4-ai-experts-rag)
5. [Полный код компонентов](#5-код-компонентов)
6. [Интеграция и использование](#6-интеграция)
7. [Что реализовано VS что нужно](#7-статус)

---

## 1. ЧТО ТАКОЕ RAG

### 1.1 Проблема без RAG

```
User: "Какой RTO для больницы скорой помощи?"

LLM (без RAG):
├─ Ограничено знаниями на момент обучения (2023)
├─ Галлюцинирует специфичные данные
├─ Generic ответ без контекста вашей организации
└─ Не знает ваши реальные процессы/риски
```

### 1.2 Решение с RAG

```
┌─────────────────────────────────────────────────────────────┐
│  RAG PIPELINE                                               │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  User Query: "Какой RTO для больницы скорой помощи?"       │
│       │                                                      │
│       ↓                                                      │
│  ┌─────────────────────────────────────────┐               │
│  │ 1. RETRIEVAL (Поиск знаний)             │               │
│  ├─────────────────────────────────────────┤               │
│  │ • Semantic search в knowledge base      │               │
│  │ • Query: ISO 22301 standards            │               │
│  │ • Query: Healthcare RTO cases           │               │
│  │ • Query: Emergency dept best practices  │               │
│  │                                          │               │
│  │ Retrieved:                               │               │
│  │ ├─ ISO 22301 Clause 8.2: 4h for critical│               │
│  │ ├─ Case #234: Hospital ER RTO = 2h      │               │
│  │ └─ BCI GPG: Healthcare 4-8h typical     │               │
│  └─────────────────────────────────────────┘               │
│       │                                                      │
│       ↓                                                      │
│  ┌─────────────────────────────────────────┐               │
│  │ 2. AUGMENTATION (Обогащение промпта)    │               │
│  ├─────────────────────────────────────────┤               │
│  │ Context:                                 │               │
│  │ - ISO 22301 требует 4h для critical     │               │
│  │ - Аналогичная больница использует 2h    │               │
│  │ - Industry best practice: 4-8h          │               │
│  │                                          │               │
│  │ User Query:                              │               │
│  │ - Какой RTO для больницы скорой помощи? │               │
│  └─────────────────────────────────────────┘               │
│       │                                                      │
│       ↓                                                      │
│  ┌─────────────────────────────────────────┐               │
│  │ 3. GENERATION (LLM ответ с контекстом)  │               │
│  ├─────────────────────────────────────────┤               │
│  │ LLM (Claude/GPT):                        │               │
│  │                                          │               │
│  │ "Для больницы скорой помощи:            │               │
│  │  RTO = 2-4 часа                          │               │
│  │                                          │               │
│  │  Обоснование:                            │               │
│  │  • ISO 22301 требует 4h для critical    │               │
│  │  • Лучшие практики: 2h (Case #234)      │               │
│  │  • Регуляторные требования: <4h         │               │
│  │                                          │               │
│  │  Рекомендация:                           │               │
│  │  Установить RTO = 2h для critical       │               │
│  │  процессов скорой помощи"               │               │
│  └─────────────────────────────────────────┘               │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Результат:**
- ✅ Точный ответ на основе реальных данных
- ✅ Ссылки на источники (ISO, cases)
- ✅ Специфично для healthcare
- ✅ Не галлюцинирует

---

## 2. АРХИТЕКТУРА

### 2.1 Общая архитектура RAG в платформе

```
┌─────────────────────────────────────────────────────────────────┐
│  KNOWLEDGE SOURCES (Источники знаний)                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  📚 Static Knowledge (Статические)                              │
│  ├─ ISO 22301:2019 (clause by clause)                          │
│  ├─ BCI Good Practice Guidelines 7.0                            │
│  ├─ WHO Health Emergency BCM Framework                          │
│  ├─ Templates (BIA, Risk, Plan)                                 │
│  └─ FAQs                                                         │
│                                                                  │
│  📊 Dynamic Knowledge (Динамические)                            │
│  ├─ Case Library (успешные кейсы)                              │
│  ├─ Community Annotations (peer review)                         │
│  └─ Lessons Learned                                              │
│                                                                  │
│  💾 Live Data (Живые данные)                                    │
│  ├─ BIA Service (ваши процессы)                                │
│  ├─ Risk Service (ваши риски)                                  │
│  ├─ Plans Service (ваши планы)                                 │
│  └─ Compliance Service (ваш статус)                            │
│                                                                  │
└──────────────┬──────────────────────────────────────────────────┘
               │
               │ Preprocessing
               │ (chunking, metadata)
               │
┌──────────────▼──────────────────────────────────────────────────┐
│  EMBEDDING PIPELINE                                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Providers:                                                      │
│  ├─ Voyage AI (voyage-02)        - Best for BCM domain         │
│  ├─ OpenAI (text-embedding-3-large) - General purpose          │
│  └─ Local (sentence-transformers) - Offline                     │
│                                                                  │
│  Chunking Strategy:                                              │
│  ├─ Chunk size: 512 tokens                                      │
│  ├─ Overlap: 50 tokens                                          │
│  └─ Separators: \n\n, \n, ., " "                                │
│                                                                  │
└──────────────┬──────────────────────────────────────────────────┘
               │
               │ Store embeddings
               │
┌──────────────▼──────────────────────────────────────────────────┐
│  VECTOR DATABASE                                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ⚠️ CURRENT: In-memory VectorStore (development)                │
│  ✅ PRODUCTION: Need pgvector or Pinecone                       │
│                                                                  │
│  Schema:                                                         │
│  ┌───────────────────────────────────────────┐                 │
│  │ id          | UUID                         │                 │
│  │ embedding   | VECTOR(1024 or 1536)        │                 │
│  │ text        | TEXT                         │                 │
│  │ metadata    | JSONB                        │                 │
│  │   ├─ source_type  (iso/case/community)    │                 │
│  │   ├─ priority     (0.7-1.0)                │                 │
│  │   ├─ industry                              │                 │
│  │   ├─ module       (bia/risk/compliance)   │                 │
│  │   └─ date                                  │                 │
│  └───────────────────────────────────────────┘                 │
│                                                                  │
└──────────────┬──────────────────────────────────────────────────┘
               │
               │ Query time
               │
┌──────────────▼──────────────────────────────────────────────────┐
│  RAG RETRIEVAL (2 стратегии)                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Strategy 1: KNOWLEDGE BASE RAG (ai_experts)                    │
│  ┌─────────────────────────────────────────────────────┐       │
│  │ 1. User question → embedding                         │       │
│  │ 2. Vector similarity search (top-k=15)              │       │
│  │ 3. Hybrid: Vector (70%) + Keyword (30%)             │       │
│  │ 4. Re-ranking (context + diversity)                 │       │
│  │ 5. Top-5 most relevant chunks                       │       │
│  └─────────────────────────────────────────────────────┘       │
│                                                                  │
│  Strategy 2: LIVE DATA RAG (ai_office)                          │
│  ┌─────────────────────────────────────────────────────┐       │
│  │ 1. User question → intent analysis                   │       │
│  │ 2. Intent → Module routing                          │       │
│  │ 3. API calls to BCM services                        │       │
│  │ 4. Format live data for context                     │       │
│  │ 5. Return fresh data                                │       │
│  └─────────────────────────────────────────────────────┘       │
│                                                                  │
└──────────────┬──────────────────────────────────────────────────┘
               │
               │ Augmented context
               │
┌──────────────▼──────────────────────────────────────────────────┐
│  LLM GENERATION                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Model: Claude 3.5 Sonnet (claude-3-5-sonnet-20241022)         │
│  Alternative: GPT-4 Turbo                                       │
│                                                                  │
│  System Prompt:                                                  │
│  "You are BCM expert with ISO 22301 knowledge..."              │
│                                                                  │
│  User Prompt:                                                    │
│  Context: [Retrieved knowledge]                                 │
│  Query: [User question]                                         │
│                                                                  │
│  Output:                                                         │
│  ├─ Answer (markdown formatted)                                 │
│  ├─ Confidence score                                            │
│  ├─ Sources used                                                │
│  └─ Suggested actions                                           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. AI-OFFICE RAG

### 3.1 Концепция: "Live Data RAG"

**Идея:** Не хранить embeddings статических данных, а запрашивать ЖИВЫЕ данные из BCM сервисов в реальном времени.

**Когда использовать:**
- ✅ User-facing queries (AI Colleagues)
- ✅ Need fresh data (current risks, active plans)
- ✅ Organization-specific context
- ✅ Conversational AI

### 3.2 Архитектура

```
┌─────────────────────────────────────────────────────────────────┐
│  AI-OFFICE RAG PIPELINE                                         │
│  Location: /intelligent-core/ai-office/core/rag/                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  User Query                                                      │
│     │                                                            │
│     ↓                                                            │
│  ┌──────────────────────────────────────┐                      │
│  │ INTENT ANALYZER                      │                      │
│  │ (core/intent.py)                     │                      │
│  ├──────────────────────────────────────┤                      │
│  │ Detect:                               │                      │
│  │ ├─ intent_type (analyze/create/query)│                      │
│  │ ├─ module (risk/bia/plans/compliance)│                      │
│  │ ├─ entities (process_id, risk_id)    │                      │
│  │ └─ confidence (0.0-1.0)               │                      │
│  └──────────────┬───────────────────────┘                      │
│                 │                                                │
│                 ↓                                                │
│  ┌──────────────────────────────────────┐                      │
│  │ CONTEXT RETRIEVER                    │                      │
│  │ (core/rag/context_retriever.py)      │                      │
│  ├──────────────────────────────────────┤                      │
│  │ Intent: "analyze_risk"                │                      │
│  │    ↓                                  │                      │
│  │ Modules: ["risk", "bia"]              │                      │
│  │    ↓                                  │                      │
│  │ ┌────────────────────────────────┐   │                      │
│  │ │ API Call: risk-service         │   │                      │
│  │ │ GET /api/risks?tenant_id=X     │   │                      │
│  │ │                                 │   │                      │
│  │ │ Response:                       │   │                      │
│  │ │ [{                              │   │                      │
│  │ │   "id": "risk-001",             │   │                      │
│  │ │   "title": "Power outage",     │   │                      │
│  │ │   "priority": "high",           │   │                      │
│  │ │   "likelihood": 4,              │   │                      │
│  │ │   "impact": 5                   │   │                      │
│  │ │ }]                              │   │                      │
│  │ └────────────────────────────────┘   │                      │
│  │    ↓                                  │                      │
│  │ ┌────────────────────────────────┐   │                      │
│  │ │ API Call: bia-service          │   │                      │
│  │ │ GET /api/processes?tenant_id=X │   │                      │
│  │ │                                 │   │                      │
│  │ │ Response:                       │   │                      │
│  │ │ [{                              │   │                      │
│  │ │   "id": "proc-001",             │   │                      │
│  │ │   "name": "Emergency Dept",    │   │                      │
│  │ │   "rto": "2h",                  │   │                      │
│  │ │   "rpo": "1h",                  │   │                      │
│  │ │   "criticality": "critical"     │   │                      │
│  │ │ }]                              │   │                      │
│  │ └────────────────────────────────┘   │                      │
│  └──────────────┬───────────────────────┘                      │
│                 │                                                │
│                 ↓                                                │
│  ┌──────────────────────────────────────┐                      │
│  │ PROMPT BUILDER                       │                      │
│  ├──────────────────────────────────────┤                      │
│  │ **Relevant BCM Data:**                │                      │
│  │                                       │                      │
│  │ **From RISK module:**                 │                      │
│  │ - Risk: Power outage (Priority: high,│                      │
│  │   Likelihood: 4, Impact: 5)           │                      │
│  │                                       │                      │
│  │ **From BIA module:**                  │                      │
│  │ - Process: Emergency Dept (RTO: 2h,  │                      │
│  │   RPO: 1h, Criticality: critical)     │                      │
│  │                                       │                      │
│  │ **User Query:**                       │                      │
│  │ Какие риски для скорой помощи?       │                      │
│  └──────────────┬───────────────────────┘                      │
│                 │                                                │
│                 ↓                                                │
│  ┌──────────────────────────────────────┐                      │
│  │ CLAUDE API (Anthropic)                │                      │
│  │ (core/adapters.py)                    │                      │
│  ├──────────────────────────────────────┤                      │
│  │ Model: claude-3-5-sonnet-20241022     │                      │
│  │                                       │                      │
│  │ System: "Expert BCM consultant..."   │                      │
│  │ User: [Augmented prompt above]        │                      │
│  │                                       │                      │
│  │ Response:                              │                      │
│  │ "Для скорой помощи выявлены риски:   │                      │
│  │  1. Power outage (likelihood: high)   │                      │
│  │  2. Impact analysis:                  │                      │
│  │     - Emergency Dept: RTO=2h critical │                      │
│  │     - Требуется backup power          │                      │
│  │  3. Recommendations:                  │                      │
│  │     - Install UPS                     │                      │
│  │     - Test backup generator monthly"  │                      │
│  └──────────────┬───────────────────────┘                      │
│                 │                                                │
│                 ↓                                                │
│  ┌──────────────────────────────────────┐                      │
│  │ ACTION EXTRACTOR                     │                      │
│  ├──────────────────────────────────────┤                      │
│  │ Suggested Actions:                    │                      │
│  │ ├─ Install UPS system                 │                      │
│  │ ├─ Test backup generator monthly      │                      │
│  │ └─ Create power outage response plan  │                      │
│  └──────────────────────────────────────┘                      │
│                                                                  │
│  Return: RAGResult                                              │
│  ├─ answer                                                      │
│  ├─ confidence                                                  │
│  ├─ intent                                                      │
│  ├─ context_used                                                │
│  ├─ suggested_actions                                           │
│  ├─ model_used                                                  │
│  └─ tokens_used                                                 │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 3.3 Код AI-Office RAG

#### 3.3.1 Main RAG Pipeline

```python
# /intelligent-core/ai-office/core/rag/rag_pipeline.py

from typing import Dict, List, Optional, Any
from pydantic import BaseModel

from core.adapters import AnthropicAdapter
from core.intent import IntentAnalyzer, IntentResult
from core.rag.context_retriever import ContextRetriever, RetrievedContext


class RAGResult(BaseModel):
    """Result from RAG pipeline"""
    answer: str
    confidence: float
    intent: Dict[str, Any]
    context_used: List[Dict[str, Any]]
    suggested_actions: List[Dict[str, Any]]
    model_used: str
    tokens_used: int


class RAGPipeline:
    """
    Complete RAG pipeline for BCM Intelligence.

    Workflow:
    User Query → Intent Analysis → Context Retrieval →
    Prompt Building → Claude API → Answer
    """

    def __init__(
        self,
        bcm_module_urls: Dict[str, str],
        anthropic_api_key: Optional[str] = None,
        model: str = "claude-3-5-sonnet-20241022",
        max_context_items: int = 10,
        retrieval_timeout: int = 10
    ):
        """
        Initialize RAG pipeline.

        Args:
            bcm_module_urls: Dict of module_name -> base_url
                Example:
                {
                    'risk': 'http://localhost:8001',
                    'bia': 'http://localhost:8002',
                    'plans': 'http://localhost:8003',
                    'compliance': 'http://localhost:8004',
                    'governance': 'http://localhost:8005'
                }
            anthropic_api_key: Anthropic API key
            model: Claude model to use
            max_context_items: Max context items to retrieve
            retrieval_timeout: Timeout for context retrieval
        """
        # Initialize components
        self.claude = AnthropicAdapter(
            api_key=anthropic_api_key,
            model=model
        )
        self.intent_analyzer = IntentAnalyzer()
        self.context_retriever = ContextRetriever(
            module_urls=bcm_module_urls,
            timeout=retrieval_timeout,
            max_items_per_module=max_context_items // 2
        )

        self.max_context_items = max_context_items

    async def process_query(
        self,
        query: str,
        tenant_id: str = "demo",
        conversation_history: Optional[List[Dict]] = None,
        system_prompt: Optional[str] = None
    ) -> RAGResult:
        """
        Process user query through complete RAG pipeline.

        Args:
            query: User's question or request
            tenant_id: Tenant identifier
            conversation_history: Previous messages
            system_prompt: Optional system prompt override

        Returns:
            RAGResult with answer and metadata
        """
        # Step 1: Analyze intent
        intent_result = self.intent_analyzer.analyze(query, conversation_history)

        # Step 2: Retrieve context (if needed)
        retrieved_contexts = []
        if intent_result.requires_context:
            # Determine which modules to query
            target_modules = self._determine_target_modules(intent_result)

            retrieved_contexts = await self.context_retriever.retrieve(
                query=query,
                target_modules=target_modules,
                intent=intent_result.dict(),
                tenant_id=tenant_id,
                entities=intent_result.entities
            )

        # Step 3: Build prompt with context
        enhanced_prompt = self._build_prompt(
            query=query,
            intent=intent_result,
            contexts=retrieved_contexts
        )

        # Step 4: Generate response with Claude
        if not system_prompt:
            system_prompt = self._build_system_prompt(intent_result)

        claude_response = await self.claude.generate(
            user_message=enhanced_prompt,
            system_prompt=system_prompt
        )

        # Step 5: Extract suggested actions
        suggested_actions = self._extract_actions(
            claude_response['content'],
            intent_result
        )

        # Step 6: Build result
        return RAGResult(
            answer=claude_response['content'],
            confidence=intent_result.confidence,
            intent=intent_result.dict(),
            context_used=[
                {
                    "module": ctx.module,
                    "items_count": len(ctx.data),
                    "score": ctx.score
                }
                for ctx in retrieved_contexts
            ],
            suggested_actions=suggested_actions,
            model_used=claude_response['model_used'],
            tokens_used=claude_response['tokens_used']
        )

    def _determine_target_modules(self, intent: IntentResult) -> List[str]:
        """
        Determine which BCM modules to query based on intent.
        """
        # If module explicitly detected, use it
        if intent.module != "general":
            return [intent.module]

        # Otherwise, use intent-based routing
        intent_type = intent.intent_type

        module_map = {
            "analyze_risk": ["risk", "bia"],
            "analyze_bia": ["bia", "risk"],
            "assess_compliance": ["compliance", "governance"],
            "create_plan": ["plans", "planning", "bia"],
            "design_exercise": ["validation", "plans"],
            "query_info": ["governance", "compliance"],
            "get_status": ["governance"],
            "list_items": [intent.module] if intent.module != "general" else ["risk", "plans"],
        }

        modules = module_map.get(intent_type, [])

        # If still no modules, query general ones
        if not modules:
            modules = ["governance", "compliance"]

        return modules

    def _build_prompt(
        self,
        query: str,
        intent: IntentResult,
        contexts: List[RetrievedContext]
    ) -> str:
        """
        Build enhanced prompt with retrieved context.
        """
        parts = []

        # Add context if available
        if contexts:
            parts.append("**Relevant BCM Data:**\n")

            for ctx in contexts[:self.max_context_items]:
                parts.append(f"**From {ctx.module.upper()} module:**")

                for item in ctx.data:
                    formatted = self._format_context_item(item, ctx.module)
                    parts.append(formatted)

                parts.append("")  # Blank line

        # Add entities if extracted
        if intent.entities:
            parts.append(f"**Extracted Entities:** {intent.entities}\n")

        # Add user query
        parts.append("**User Query:**")
        parts.append(query)

        return "\n".join(parts)

    def _format_context_item(self, item: Dict[str, Any], module: str) -> str:
        """Format context item for prompt."""

        # Risk module
        if module == "risk":
            return (
                f"- Risk: {item.get('title', 'N/A')} "
                f"(Priority: {item.get('priority', 'N/A')}, "
                f"Likelihood: {item.get('likelihood', 'N/A')}, "
                f"Impact: {item.get('impact', 'N/A')})"
            )

        # BIA module
        elif module == "bia":
            return (
                f"- Process: {item.get('name', 'N/A')} "
                f"(RTO: {item.get('rto', 'N/A')}, "
                f"RPO: {item.get('rpo', 'N/A')}, "
                f"Criticality: {item.get('criticality', 'N/A')})"
            )

        # Plans module
        elif module == "plans":
            return (
                f"- Plan: {item.get('name', 'N/A')} "
                f"(Status: {item.get('status', 'N/A')}, "
                f"Type: {item.get('type', 'N/A')})"
            )

        # Compliance module
        elif module == "compliance":
            return (
                f"- Requirement: {item.get('requirement', 'N/A')} "
                f"(Status: {item.get('status', 'N/A')}, "
                f"Gap: {item.get('gap_description', 'N/A')})"
            )

        # Default format
        else:
            title = item.get('title') or item.get('name') or item.get('id', 'Item')
            description = item.get('description', '')[:100]
            return f"- {title}: {description}"

    def _build_system_prompt(self, intent: IntentResult) -> str:
        """Build system prompt based on intent."""

        base_prompt = (
            "You are an expert BCM (Business Continuity Management) consultant "
            "with deep knowledge of ISO 22301:2019 standard. "
            "You help organizations build resilience and ensure business continuity.\n\n"
        )

        # Add intent-specific instructions
        intent_type = intent.intent_type

        if "analyze" in intent_type:
            base_prompt += (
                "Provide thorough analysis with:\n"
                "- Clear findings based on provided data\n"
                "- Risk assessment using FAIR methodology where applicable\n"
                "- Specific recommendations\n"
                "- Next steps\n\n"
            )

        elif "create" in intent_type or "generate" in intent_type:
            base_prompt += (
                "When generating plans or documents:\n"
                "- Follow ISO 22301:2019 requirements\n"
                "- Use provided context data\n"
                "- Include specific, actionable steps\n"
                "- Reference relevant standards\n\n"
            )

        elif "recommend" in intent_type or "suggest" in intent_type:
            base_prompt += (
                "Provide recommendations that are:\n"
                "- Specific and actionable\n"
                "- Based on best practices\n"
                "- Prioritized by impact\n"
                "- Aligned with ISO 22301\n\n"
            )

        # General guidelines
        base_prompt += (
            "Guidelines:\n"
            "- Use clear, professional language\n"
            "- Reference specific data from context when available\n"
            "- Be concise but comprehensive\n"
            "- Suggest concrete next actions\n"
            "- Format responses with markdown for readability"
        )

        return base_prompt

    def _extract_actions(
        self,
        response_text: str,
        intent: IntentResult
    ) -> List[Dict[str, Any]]:
        """Extract suggested actions from Claude's response."""

        actions = []
        lines = response_text.split('\n')

        for line in lines:
            line = line.strip()

            # Check for action indicators
            if any(indicator in line.lower() for indicator in [
                'next step', 'recommend', 'should', 'action', 'task'
            ]):
                # Extract action
                action_text = line.lstrip('0123456789.-*• ')

                if len(action_text) > 10:  # Valid action
                    actions.append({
                        "title": action_text[:100],
                        "description": action_text,
                        "priority": "medium",
                        "type": intent.intent_type
                    })

        # Limit to top 5 actions
        return actions[:5]
```

#### 3.3.2 Intent Analyzer

```python
# /intelligent-core/ai-office/core/intent.py

from typing import List, Dict, Optional
from pydantic import BaseModel


class IntentResult(BaseModel):
    """Result of intent analysis"""
    intent_type: str  # analyze_risk, create_plan, etc.
    module: str       # risk, bia, plans, etc.
    entities: Dict[str, Any]  # Extracted entities
    confidence: float
    requires_context: bool


class IntentAnalyzer:
    """
    Analyze user intent from query

    Detects:
    - What user wants to do (analyze/create/query/list)
    - Which BCM module is relevant
    - Entities mentioned (process_id, risk_id, etc.)
    """

    def __init__(self):
        # Intent patterns
        self.intent_patterns = {
            "analyze_risk": [
                "analyze risk", "assess risk", "risk analysis",
                "evaluate risk", "risk assessment"
            ],
            "analyze_bia": [
                "bia analysis", "business impact", "analyze process",
                "critical process", "rto", "rpo"
            ],
            "assess_compliance": [
                "compliance", "iso 22301", "audit", "gap analysis",
                "certification", "requirements"
            ],
            "create_plan": [
                "create plan", "develop plan", "generate plan",
                "continuity plan", "recovery plan"
            ],
            "design_exercise": [
                "exercise", "test", "drill", "tabletop",
                "simulation", "practice"
            ],
            "query_info": [
                "what is", "explain", "tell me about", "define",
                "how to", "best practice"
            ],
            "get_status": [
                "status", "progress", "current", "overview",
                "summary", "report"
            ],
            "list_items": [
                "list", "show me", "get all", "find", "search"
            ]
        }

        # Module patterns
        self.module_patterns = {
            "risk": ["risk", "threat", "vulnerability", "hazard"],
            "bia": ["bia", "process", "rto", "rpo", "impact", "criticality"],
            "plans": ["plan", "strategy", "procedure", "response"],
            "compliance": ["compliance", "audit", "iso", "standard", "requirement"],
            "governance": ["governance", "policy", "stakeholder", "context"],
            "response": ["incident", "emergency", "crisis", "disaster"],
            "validation": ["exercise", "test", "drill", "validation"]
        }

    def analyze(
        self,
        query: str,
        conversation_history: Optional[List[Dict]] = None
    ) -> IntentResult:
        """
        Analyze user intent

        Args:
            query: User's question
            conversation_history: Previous messages for context

        Returns:
            IntentResult with detected intent
        """
        query_lower = query.lower()

        # Detect intent type
        intent_type = self._detect_intent_type(query_lower)

        # Detect module
        module = self._detect_module(query_lower)

        # Extract entities
        entities = self._extract_entities(query)

        # Calculate confidence
        confidence = self._calculate_confidence(
            query_lower,
            intent_type,
            module
        )

        # Determine if context retrieval needed
        requires_context = self._requires_context(intent_type)

        return IntentResult(
            intent_type=intent_type,
            module=module,
            entities=entities,
            confidence=confidence,
            requires_context=requires_context
        )

    def _detect_intent_type(self, query: str) -> str:
        """Detect intent type from query"""

        scores = {}

        for intent, patterns in self.intent_patterns.items():
            score = sum(
                1 for pattern in patterns
                if pattern in query
            )
            scores[intent] = score

        if not scores or max(scores.values()) == 0:
            return "query_info"  # Default

        return max(scores, key=scores.get)

    def _detect_module(self, query: str) -> str:
        """Detect relevant BCM module"""

        scores = {}

        for module, patterns in self.module_patterns.items():
            score = sum(
                1 for pattern in patterns
                if pattern in query
            )
            scores[module] = score

        if not scores or max(scores.values()) == 0:
            return "general"

        return max(scores, key=scores.get)

    def _extract_entities(self, query: str) -> Dict[str, Any]:
        """Extract entities from query"""

        entities = {}

        # Simple extraction (can be improved with NER)
        words = query.split()

        for i, word in enumerate(words):
            # Look for IDs
            if word.lower() in ['id', 'process', 'risk', 'plan']:
                if i + 1 < len(words):
                    entities[f"{word.lower()}_id"] = words[i + 1]

            # Look for industry
            if word.lower() in ['hospital', 'bank', 'factory', 'retail']:
                entities['industry'] = word.lower()

        return entities

    def _calculate_confidence(
        self,
        query: str,
        intent_type: str,
        module: str
    ) -> float:
        """Calculate confidence in intent detection"""

        # Base confidence
        confidence = 0.5

        # Increase if intent patterns matched
        intent_patterns = self.intent_patterns.get(intent_type, [])
        if any(pattern in query for pattern in intent_patterns):
            confidence += 0.3

        # Increase if module patterns matched
        module_patterns = self.module_patterns.get(module, [])
        if any(pattern in query for pattern in module_patterns):
            confidence += 0.2

        return min(confidence, 1.0)

    def _requires_context(self, intent_type: str) -> bool:
        """Determine if context retrieval is needed"""

        # Intents that need context
        context_intents = [
            "analyze_risk",
            "analyze_bia",
            "assess_compliance",
            "create_plan",
            "get_status",
            "list_items"
        ]

        return intent_type in context_intents
```

### 3.4 Usage Example

```python
# Example: Using AI-Office RAG in AI Colleague

from ai_office.core.rag import RAGPipeline

# Initialize
rag = RAGPipeline(
    bcm_module_urls={
        'risk': 'http://localhost:8001',
        'bia': 'http://localhost:8002',
        'plans': 'http://localhost:8003',
        'compliance': 'http://localhost:8004',
        'governance': 'http://localhost:8005'
    },
    anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
    model="claude-3-5-sonnet-20241022",
    max_context_items=10
)

# Process query
result = await rag.process_query(
    query="What are the critical risks for our hospital emergency department?",
    tenant_id="hospital-123",
    conversation_history=[]
)

# Result
print(f"Answer: {result.answer}")
print(f"Confidence: {result.confidence}")
print(f"Intent: {result.intent}")
print(f"Context used: {result.context_used}")
print(f"Suggested actions: {result.suggested_actions}")
```

---

## 4. AI-EXPERTS RAG

### 4.1 Концепция: "Knowledge Base RAG"

**Идея:** Хранить embeddings статических знаний (ISO standards, cases, guidelines) в Vector DB для semantic search.

**Когда использовать:**
- ✅ Standards/guidelines lookup
- ✅ Case studies search
- ✅ Best practices retrieval
- ✅ Context building for LLMs

### 4.2 Архитектура

```
┌─────────────────────────────────────────────────────────────────┐
│  AI-EXPERTS RAG PIPELINE                                        │
│  Location: /intelligent-core/ai_experts/rag/                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────────────────┐                      │
│  │ KNOWLEDGE INGESTION                  │                      │
│  ├──────────────────────────────────────┤                      │
│  │                                       │                      │
│  │ Documents (ISO 22301, BCI GPG, Cases)│                      │
│  │       │                               │                      │
│  │       ↓                               │                      │
│  │  ┌─────────────────────────┐         │                      │
│  │  │ DocumentChunker         │         │                      │
│  │  │ - chunk_size: 512       │         │                      │
│  │  │ - overlap: 50           │         │                      │
│  │  │ - separators: \n\n, \n  │         │                      │
│  │  └────────┬────────────────┘         │                      │
│  │           │                           │                      │
│  │           ↓                           │                      │
│  │  ┌─────────────────────────┐         │                      │
│  │  │ EmbeddingGenerator      │         │                      │
│  │  │                          │         │                      │
│  │  │ Provider: Voyage AI      │         │                      │
│  │  │ Model: voyage-02         │         │                      │
│  │  │ Dimensions: 1024         │         │                      │
│  │  │                          │         │                      │
│  │  │ OR                       │         │                      │
│  │  │                          │         │                      │
│  │  │ Provider: OpenAI         │         │                      │
│  │  │ Model: text-embed-3-large│         │                      │
│  │  │ Dimensions: 1536         │         │                      │
│  │  └────────┬────────────────┘         │                      │
│  │           │                           │                      │
│  │           ↓                           │                      │
│  │  ┌─────────────────────────┐         │                      │
│  │  │ VectorStore.add()       │         │                      │
│  │  │                          │         │                      │
│  │  │ ⚠️ Currently: In-memory │         │                      │
│  │  │ ✅ Production: pgvector │         │                      │
│  │  └─────────────────────────┘         │                      │
│  └──────────────────────────────────────┘                      │
│                                                                  │
│  ┌──────────────────────────────────────┐                      │
│  │ RETRIEVAL                            │                      │
│  ├──────────────────────────────────────┤                      │
│  │                                       │                      │
│  │ User Query: "How to calculate RTO?"  │                      │
│  │       │                               │                      │
│  │       ↓                               │                      │
│  │  ┌─────────────────────────┐         │                      │
│  │  │ EmbeddingGenerator      │         │                      │
│  │  │ query → embedding        │         │                      │
│  │  └────────┬────────────────┘         │                      │
│  │           │                           │                      │
│  │           ↓                           │                      │
│  │  ┌─────────────────────────┐         │                      │
│  │  │ HybridRetriever         │         │                      │
│  │  ├─────────────────────────┤         │                      │
│  │  │ Strategy 1: Vector      │         │                      │
│  │  │ - Cosine similarity     │         │                      │
│  │  │ - Weight: 70%           │         │                      │
│  │  │                          │         │                      │
│  │  │ Strategy 2: Keyword     │         │                      │
│  │  │ - BM25-like scoring     │         │                      │
│  │  │ - Weight: 30%           │         │                      │
│  │  │                          │         │                      │
│  │  │ Combined Score          │         │                      │
│  │  │ Top-k: 15               │         │                      │
│  │  └────────┬────────────────┘         │                      │
│  │           │                           │                      │
│  │           ↓                           │                      │
│  │  ┌─────────────────────────┐         │                      │
│  │  │ Reranker                │         │                      │
│  │  ├─────────────────────────┤         │                      │
│  │  │ Context awareness       │         │                      │
│  │  │ - Industry              │         │                      │
│  │  │ - Module                │         │                      │
│  │  │ - Org size              │         │                      │
│  │  │                          │         │                      │
│  │  │ Source priority         │         │                      │
│  │  │ - ISO: 1.0              │         │                      │
│  │  │ - BCI: 0.95             │         │                      │
│  │  │ - Cases: 0.8            │         │                      │
│  │  │                          │         │                      │
│  │  │ Top-k: 10               │         │                      │
│  │  └────────┬────────────────┘         │                      │
│  │           │                           │                      │
│  │           ↓                           │                      │
│  │  ┌─────────────────────────┐         │                      │
│  │  │ DiversityReranker       │         │                      │
│  │  │ (optional)               │         │                      │
│  │  ├─────────────────────────┤         │                      │
│  │  │ Ensure variety of:      │         │                      │
│  │  │ - Sources                │         │                      │
│  │  │ - Topics                 │         │                      │
│  │  │ - Perspectives           │         │                      │
│  │  │                          │         │                      │
│  │  │ Top-k: 5                │         │                      │
│  │  └────────┬────────────────┘         │                      │
│  │           │                           │                      │
│  │           ↓                           │                      │
│  │  ┌─────────────────────────┐         │                      │
│  │  │ Format Results          │         │                      │
│  │  │                          │         │                      │
│  │  │ [{                       │         │                      │
│  │  │   content: "...",        │         │                      │
│  │  │   source: "iso_standard",│         │                      │
│  │  │   score: 0.92,           │         │                      │
│  │  │   metadata: {...}        │         │                      │
│  │  │ }]                       │         │                      │
│  │  └─────────────────────────┘         │                      │
│  └──────────────────────────────────────┘                      │
│                                                                  │
│  ┌──────────────────────────────────────┐                      │
│  │ CONTEXT BUILDING                     │                      │
│  ├──────────────────────────────────────┤                      │
│  │                                       │                      │
│  │ build_context(query, max_len=2000)   │                      │
│  │       │                               │                      │
│  │       ↓                               │                      │
│  │  [1] Source: iso_standard             │                      │
│  │  ISO 22301 Clause 8.2.1: RTO should  │                      │
│  │  be based on impact analysis...      │                      │
│  │                                       │                      │
│  │  [2] Source: case_study               │                      │
│  │  Case: Hospital RTO = 2h for ER...   │                      │
│  │                                       │                      │
│  │  [3] Source: bci_guidelines           │                      │
│  │  BCI GPG Section 4.3: Critical       │                      │
│  │  processes require RTO < 4h...       │                      │
│  │                                       │                      │
│  └──────────────────────────────────────┘                      │
│                                                                  │
│  Return: Formatted context string for LLM                       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 4.3 Код AI-Experts RAG

#### 4.3.1 Main RAG Pipeline

```python
# /intelligent-core/ai_experts/rag/pipeline.py

from typing import List, Dict, Any, Optional
import logging

from .embeddings import EmbeddingGenerator, DocumentChunker
from .retrieval import HybridRetriever, VectorStore
from .reranking import Reranker, DiversityReranker

logger = logging.getLogger(__name__)


class RAGPipeline:
    """
    RAG Pipeline

    Complete RAG workflow:
    1. Document ingestion and chunking
    2. Embedding generation
    3. Vector storage
    4. Hybrid retrieval
    5. Reranking
    """

    def __init__(
        self,
        knowledge_sources: Optional[List[str]] = None,
        embedding_provider: str = "voyage",
        chunk_size: int = 512,
        top_k: int = 5
    ):
        """
        Initialize RAG pipeline

        Args:
            knowledge_sources: List of knowledge source types
            embedding_provider: Embedding provider ('voyage', 'openai', 'local')
            chunk_size: Document chunk size
            top_k: Default number of results
        """
        self.knowledge_sources = knowledge_sources or []
        self.top_k = top_k

        # Initialize components
        self.embedding_generator = EmbeddingGenerator(provider=embedding_provider)
        self.chunker = DocumentChunker(chunk_size=chunk_size)
        self.vector_store = VectorStore(self.embedding_generator)
        self.retriever = HybridRetriever(self.embedding_generator)
        self.reranker = Reranker()
        self.diversity_reranker = DiversityReranker()

        # Knowledge source configuration
        self.source_config = {
            'iso_standards': {
                'priority': 1.0,
                'type': 'iso_standard'
            },
            'bci_guidelines': {
                'priority': 0.95,
                'type': 'bci_guidelines'
            },
            'case_library': {
                'priority': 0.8,
                'type': 'case_study'
            },
            'community_annotations': {
                'priority': 0.7,
                'type': 'community'
            }
        }

    async def ingest_documents(
        self,
        documents: List[Dict[str, Any]],
        source_type: str = 'documentation'
    ) -> List[str]:
        """
        Ingest documents into RAG pipeline

        Args:
            documents: List of documents with 'text' and optional 'metadata'
                Example:
                [
                    {
                        'text': 'ISO 22301 Clause 8.2...',
                        'metadata': {
                            'clause': '8.2',
                            'standard': 'ISO 22301:2019'
                        }
                    }
                ]
            source_type: Type of source ('iso_standard', 'case_study', etc.)

        Returns:
            List of document IDs
        """
        logger.info(f"Ingesting {len(documents)} documents from {source_type}")

        all_doc_ids = []

        for doc in documents:
            text = doc.get('text') or doc.get('content')
            if not text:
                logger.warning(f"Skipping document without text: {doc.get('id', 'unknown')}")
                continue

            metadata = doc.get('metadata', {})
            metadata['source_type'] = source_type

            # Add source priority
            if source_type in self.source_config:
                metadata['source_priority'] = self.source_config[source_type]['priority']

            # Chunk document
            chunks = self.chunker.chunk_document(text, metadata)

            # Add chunks to vector store
            chunk_texts = [chunk['text'] for chunk in chunks]
            chunk_metadatas = [
                {k: v for k, v in chunk.items() if k != 'text'}
                for chunk in chunks
            ]

            doc_ids = await self.vector_store.add_documents(
                texts=chunk_texts,
                metadatas=chunk_metadatas
            )

            all_doc_ids.extend(doc_ids)

        logger.info(f"Ingested {len(all_doc_ids)} chunks from {len(documents)} documents")

        return all_doc_ids

    async def retrieve(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None,
        top_k: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None,
        enable_reranking: bool = True,
        enable_diversity: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant knowledge

        Args:
            query: Search query
            context: Additional context for relevance
                Example: {'industry': 'healthcare', 'module': 'bia'}
            top_k: Number of results (default: self.top_k)
            filters: Metadata filters
                Example: {'source_type': 'iso_standard'}
            enable_reranking: Enable result reranking
            enable_diversity: Enable diversity filtering

        Returns:
            Relevant knowledge chunks
        """
        top_k = top_k or self.top_k

        logger.info(f"RAG retrieve: query='{query[:50]}...', top_k={top_k}")

        # Step 1: Hybrid retrieval
        retrieval_k = top_k * 3 if enable_reranking else top_k

        results = await self.vector_store.search(
            query=query,
            top_k=retrieval_k,
            filters=filters
        )

        if not results:
            logger.warning("No results found for query")
            return []

        logger.info(f"Retrieved {len(results)} initial results")

        # Step 2: Reranking (if enabled)
        if enable_reranking:
            results = self.reranker.rerank(
                results=results,
                context=context,
                top_k=top_k * 2 if enable_diversity else top_k
            )
            logger.info(f"Reranked to {len(results)} results")

        # Step 3: Diversity filtering (if enabled)
        if enable_diversity:
            results = self.diversity_reranker.rerank_with_diversity(
                results=results,
                top_k=top_k,
                embedding_generator=self.embedding_generator
            )
            logger.info(f"Diversity filtering to {len(results)} results")

        # Step 4: Format results
        formatted_results = self._format_results(results)

        return formatted_results

    def _format_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format results for consumption"""

        formatted = []

        for result in results:
            formatted_result = {
                'content': result.get('text', ''),
                'source': result.get('source_type', 'unknown'),
                'score': result.get('rerank_score') or result.get('score', 0.0),
                'metadata': {}
            }

            # Add relevant metadata
            for key in ['industry', 'org_size', 'module', 'stage', 'date', 'chunk_index']:
                if key in result:
                    formatted_result['metadata'][key] = result[key]

            formatted.append(formatted_result)

        return formatted

    async def build_context(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None,
        max_context_length: int = 2000
    ) -> str:
        """
        Build RAG context for LLM prompt

        Args:
            query: User query
            context: Additional context
            max_context_length: Maximum context length (characters)

        Returns:
            Formatted context string
        """
        # Retrieve relevant knowledge
        results = await self.retrieve(
            query=query,
            context=context,
            enable_reranking=True
        )

        if not results:
            return ""

        # Build context string
        context_parts = []
        current_length = 0

        for i, result in enumerate(results, 1):
            content = result['content']
            source = result['source']

            # Format context item
            context_item = f"[{i}] Source: {source}\n{content}\n"

            item_length = len(context_item)

            if current_length + item_length > max_context_length:
                break

            context_parts.append(context_item)
            current_length += item_length

        context_str = "\n".join(context_parts)

        return context_str

    def get_stats(self) -> Dict[str, Any]:
        """Get RAG pipeline statistics"""

        vector_stats = self.vector_store.get_stats()

        return {
            'vector_store': vector_stats,
            'knowledge_sources': self.knowledge_sources,
            'embedding_provider': self.embedding_generator.provider,
            'chunk_size': self.chunker.chunk_size,
            'default_top_k': self.top_k
        }

    def clear(self):
        """Clear all stored documents"""
        self.vector_store.clear()
        logger.info("RAG pipeline cleared")
```

#### 4.3.2 Knowledge Source Manager

```python
# /intelligent-core/ai_experts/rag/pipeline.py (continued)

class KnowledgeSourceManager:
    """
    Knowledge Source Manager

    Manages different knowledge sources for RAG pipeline.
    """

    def __init__(self, rag_pipeline: RAGPipeline):
        """
        Initialize knowledge source manager

        Args:
            rag_pipeline: RAGPipeline instance
        """
        self.rag_pipeline = rag_pipeline

    async def load_iso_standards(self, standards_data: List[Dict[str, Any]]) -> int:
        """
        Load ISO 22301 standards

        Args:
            standards_data: List of standard clauses
                Example:
                [
                    {
                        'text': 'Clause 8.2: ...',
                        'metadata': {
                            'clause': '8.2',
                            'standard': 'ISO 22301:2019',
                            'section': 'Planning'
                        }
                    }
                ]

        Returns:
            Number of documents loaded
        """
        doc_ids = await self.rag_pipeline.ingest_documents(
            documents=standards_data,
            source_type='iso_standard'
        )

        return len(doc_ids)

    async def load_case_library(self, cases: List[Dict[str, Any]]) -> int:
        """
        Load case library

        Args:
            cases: List of case studies
                Example:
                [
                    {
                        'title': 'Hospital ER Recovery',
                        'industry': 'healthcare',
                        'summary': '...',
                        'key_challenge': '...',
                        'solution': '...',
                        'outcome': '...',
                        'lessons_learned': [...]
                    }
                ]

        Returns:
            Number of documents loaded
        """
        # Format cases for ingestion
        formatted_cases = []

        for case in cases:
            # Combine case fields into text
            text_parts = [
                f"Title: {case.get('title', '')}",
                f"Industry: {case.get('industry', '')}",
                f"Summary: {case.get('summary', '')}",
                f"Challenge: {case.get('key_challenge', '')}",
                f"Solution: {case.get('solution', '')}",
                f"Outcome: {case.get('outcome', '')}",
            ]

            if case.get('lessons_learned'):
                text_parts.append("Lessons Learned:")
                for lesson in case['lessons_learned']:
                    text_parts.append(f"- {lesson}")

            text = "\n".join(text_parts)

            formatted_cases.append({
                'text': text,
                'metadata': {
                    'case_id': case.get('id'),
                    'industry': case.get('industry'),
                    'org_size': case.get('org_size'),
                    'module': case.get('module'),
                    'success': case.get('success', True)
                }
            })

        doc_ids = await self.rag_pipeline.ingest_documents(
            documents=formatted_cases,
            source_type='case_study'
        )

        return len(doc_ids)

    async def load_community_annotations(self, annotations: List[Dict[str, Any]]) -> int:
        """
        Load community annotations

        Args:
            annotations: List of community annotations

        Returns:
            Number of documents loaded
        """
        formatted_annotations = []

        for annotation in annotations:
            text = annotation.get('text') or annotation.get('content', '')

            formatted_annotations.append({
                'text': text,
                'metadata': {
                    'clause': annotation.get('clause_id'),
                    'rating': annotation.get('rating'),
                    'date': annotation.get('created_at')
                }
            })

        doc_ids = await self.rag_pipeline.ingest_documents(
            documents=formatted_annotations,
            source_type='community'
        )

        return len(doc_ids)

    async def load_bci_guidelines(self, guidelines: List[Dict[str, Any]]) -> int:
        """
        Load BCI Good Practice Guidelines

        Args:
            guidelines: List of BCI guidelines

        Returns:
            Number of documents loaded
        """
        doc_ids = await self.rag_pipeline.ingest_documents(
            documents=guidelines,
            source_type='bci_guidelines'
        )

        return len(doc_ids)
```

### 4.4 Usage Example

```python
# Example: Using AI-Experts RAG for Knowledge Retrieval

from ai_experts.rag import RAGPipeline, KnowledgeSourceManager

# Initialize
rag = RAGPipeline(
    knowledge_sources=['iso_standards', 'case_library'],
    embedding_provider='voyage',  # or 'openai' or 'local'
    chunk_size=512,
    top_k=5
)

# Load knowledge
manager = KnowledgeSourceManager(rag)

# Load ISO 22301
iso_data = [
    {
        'text': 'Clause 8.2: The organization shall establish RTOs based on business impact analysis...',
        'metadata': {'clause': '8.2', 'standard': 'ISO 22301:2019'}
    }
]
await manager.load_iso_standards(iso_data)

# Load cases
cases = [
    {
        'title': 'Hospital ER RTO Implementation',
        'industry': 'healthcare',
        'summary': 'Large hospital implemented 2h RTO for emergency department',
        'solution': 'Deployed backup generator + UPS system',
        'outcome': 'Achieved 100% uptime during 3 power outages'
    }
]
await manager.load_case_library(cases)

# Retrieve
results = await rag.retrieve(
    query="What RTO should I set for hospital emergency department?",
    context={'industry': 'healthcare', 'module': 'bia'},
    enable_reranking=True,
    enable_diversity=True
)

for result in results:
    print(f"Source: {result['source']}")
    print(f"Content: {result['content']}")
    print(f"Score: {result['score']}")
    print("---")

# Build context for LLM
context = await rag.build_context(
    query="RTO calculation best practices for healthcare",
    max_context_length=2000
)

# Use with your LLM
from anthropic import AsyncAnthropic

client = AsyncAnthropic(api_key="...")

response = await client.messages.create(
    model="claude-3-5-sonnet-20241022",
    messages=[{
        "role": "user",
        "content": f"""Context from knowledge base:
{context}

Question: What RTO should I set for hospital emergency department?

Please provide specific recommendations based on the context."""
    }],
    max_tokens=1000
)

print(response.content[0].text)
```

---

## 5. КОД КОМПОНЕНТОВ

### 5.1 Embeddings

```python
# /intelligent-core/ai_experts/rag/embeddings.py

from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class EmbeddingGenerator:
    """
    Embedding Generator

    Supports multiple providers:
    - Voyage AI (best for BCM domain)
    - OpenAI (general purpose)
    - Local (sentence-transformers)
    """

    def __init__(self, provider: str = "voyage"):
        """
        Initialize embedding generator

        Args:
            provider: 'voyage', 'openai', or 'local'
        """
        self.provider = provider

        if provider == "voyage":
            from voyageai import Client
            self.client = Client()  # Uses VOYAGE_API_KEY env var
            self.model = "voyage-02"
            self.dimension = 1024

        elif provider == "openai":
            from openai import AsyncOpenAI
            self.client = AsyncOpenAI()  # Uses OPENAI_API_KEY env var
            self.model = "text-embedding-3-large"
            self.dimension = 1536

        elif provider == "local":
            from sentence_transformers import SentenceTransformer
            self.client = SentenceTransformer('all-MiniLM-L6-v2')
            self.model = "all-MiniLM-L6-v2"
            self.dimension = 384

        else:
            raise ValueError(f"Unknown provider: {provider}")

        logger.info(f"Initialized {provider} embeddings (dim={self.dimension})")

    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for single text"""

        if self.provider == "voyage":
            result = self.client.embed([text], model=self.model)
            return result.embeddings[0]

        elif self.provider == "openai":
            result = await self.client.embeddings.create(
                input=text,
                model=self.model
            )
            return result.data[0].embedding

        elif self.provider == "local":
            embedding = self.client.encode(text)
            return embedding.tolist()

    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts (batch)"""

        if self.provider == "voyage":
            result = self.client.embed(texts, model=self.model)
            return result.embeddings

        elif self.provider == "openai":
            result = await self.client.embeddings.create(
                input=texts,
                model=self.model
            )
            return [item.embedding for item in result.data]

        elif self.provider == "local":
            embeddings = self.client.encode(texts)
            return [emb.tolist() for emb in embeddings]

    @staticmethod
    def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        import numpy as np

        vec1 = np.array(vec1)
        vec2 = np.array(vec2)

        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return float(dot_product / (norm1 * norm2))


class DocumentChunker:
    """
    Document Chunker

    Splits documents into chunks with overlap for better context preservation.
    """

    def __init__(
        self,
        chunk_size: int = 512,
        overlap: int = 50,
        separators: List[str] = None
    ):
        """
        Initialize chunker

        Args:
            chunk_size: Target chunk size in tokens
            overlap: Overlap between chunks in tokens
            separators: List of separators for splitting
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.separators = separators or ["\n\n", "\n", ". ", " "]

    def chunk_document(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Chunk document into overlapping pieces

        Args:
            text: Document text
            metadata: Document metadata

        Returns:
            List of chunks with metadata
        """
        chunks = []

        # Simple chunking by character count
        # (In production, use token-based chunking)
        chunk_size_chars = self.chunk_size * 4  # ~4 chars per token
        overlap_chars = self.overlap * 4

        start = 0
        chunk_index = 0

        while start < len(text):
            end = min(start + chunk_size_chars, len(text))

            # Try to break at separator
            if end < len(text):
                for separator in self.separators:
                    last_sep = text[start:end].rfind(separator)
                    if last_sep != -1:
                        end = start + last_sep + len(separator)
                        break

            chunk_text = text[start:end].strip()

            if chunk_text:
                chunk_metadata = (metadata or {}).copy()
                chunk_metadata['chunk_index'] = chunk_index
                chunk_metadata['start_char'] = start
                chunk_metadata['end_char'] = end

                chunks.append({
                    'text': chunk_text,
                    **chunk_metadata
                })

                chunk_index += 1

            start = end - overlap_chars

        return chunks
```

### 5.2 Reranking

```python
# /intelligent-core/ai_experts/rag/reranking.py

from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class Reranker:
    """
    Context-aware reranker

    Re-ranks results based on:
    - Source priority (ISO > BCI > Cases > Community)
    - Context match (industry, module, org_size)
    - Recency (newer is better)
    """

    def rerank(
        self,
        results: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Rerank results

        Args:
            results: Search results with scores
            context: Additional context
            top_k: Number of results to return

        Returns:
            Reranked results
        """
        context = context or {}

        for result in results:
            # Base score from retrieval
            base_score = result.get('score', 0.0)

            # Source priority boost
            source_priority = result.get('source_priority', 0.5)

            # Context match boost
            context_boost = self._calculate_context_boost(result, context)

            # Recency boost
            recency_boost = self._calculate_recency_boost(result)

            # Combined rerank score
            rerank_score = (
                base_score * 0.5 +
                source_priority * 0.3 +
                context_boost * 0.15 +
                recency_boost * 0.05
            )

            result['rerank_score'] = rerank_score

        # Sort by rerank score
        results.sort(key=lambda x: x['rerank_score'], reverse=True)

        return results[:top_k]

    def _calculate_context_boost(
        self,
        result: Dict[str, Any],
        context: Dict[str, Any]
    ) -> float:
        """Calculate boost from context match"""

        boost = 0.0

        # Industry match
        if context.get('industry') and result.get('industry') == context['industry']:
            boost += 0.3

        # Module match
        if context.get('module') and result.get('module') == context['module']:
            boost += 0.3

        # Org size match
        if context.get('org_size') and result.get('org_size') == context['org_size']:
            boost += 0.2

        return boost

    def _calculate_recency_boost(self, result: Dict[str, Any]) -> float:
        """Calculate boost from recency"""

        # Simplified recency (can be improved with actual dates)
        date = result.get('date')

        if not date:
            return 0.0

        # Newer = higher boost (simplified)
        return 0.1


class DiversityReranker:
    """
    Diversity-aware reranker

    Ensures variety in results:
    - Different sources
    - Different topics
    - Different perspectives
    """

    def rerank_with_diversity(
        self,
        results: List[Dict[str, Any]],
        top_k: int = 5,
        embedding_generator = None
    ) -> List[Dict[str, Any]]:
        """
        Rerank with diversity

        Args:
            results: Reranked results
            top_k: Number of results
            embedding_generator: For calculating similarity

        Returns:
            Diverse results
        """
        if len(results) <= top_k:
            return results

        selected = []
        remaining = results.copy()

        # Always select top result
        selected.append(remaining.pop(0))

        # Select remaining based on diversity
        while len(selected) < top_k and remaining:
            # Calculate diversity score for each remaining result
            scores = []

            for candidate in remaining:
                # Relevance score
                relevance = candidate.get('rerank_score', 0.0)

                # Diversity score (how different from selected)
                diversity = self._calculate_diversity(candidate, selected)

                # Combined score (balance relevance and diversity)
                combined = relevance * 0.6 + diversity * 0.4

                scores.append((combined, candidate))

            # Select best
            scores.sort(key=lambda x: x[0], reverse=True)
            best = scores[0][1]

            selected.append(best)
            remaining.remove(best)

        return selected

    def _calculate_diversity(
        self,
        candidate: Dict[str, Any],
        selected: List[Dict[str, Any]]
    ) -> float:
        """Calculate diversity score"""

        # Source diversity
        candidate_source = candidate.get('source_type')
        selected_sources = {r.get('source_type') for r in selected}

        source_diversity = 1.0 if candidate_source not in selected_sources else 0.0

        # Module diversity
        candidate_module = candidate.get('module')
        selected_modules = {r.get('module') for r in selected}

        module_diversity = 1.0 if candidate_module not in selected_modules else 0.0

        # Combined
        diversity = (source_diversity + module_diversity) / 2

        return diversity
```

---

## 6. ИНТЕГРАЦИЯ

### 6.1 Unified RAG (Combined Approach)

```python
# Proposed: Unified RAG combining both approaches

class UnifiedRAGPipeline:
    """
    Unified RAG Pipeline

    Combines:
    - AI-Office RAG (live data from BCM services)
    - AI-Experts RAG (knowledge base search)

    Best of both worlds!
    """

    def __init__(
        self,
        bcm_module_urls: Dict[str, str],
        knowledge_rag: RAGPipeline,
        anthropic_api_key: str
    ):
        """
        Initialize unified RAG

        Args:
            bcm_module_urls: URLs to BCM services (for live data)
            knowledge_rag: AI-Experts RAG instance (for knowledge)
            anthropic_api_key: Anthropic API key
        """
        # Live data RAG
        self.live_rag = AIOfficeRAGPipeline(
            bcm_module_urls=bcm_module_urls,
            anthropic_api_key=anthropic_api_key
        )

        # Knowledge base RAG
        self.knowledge_rag = knowledge_rag

    async def process_query(
        self,
        query: str,
        tenant_id: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process query using unified approach

        Args:
            query: User question
            tenant_id: Tenant ID
            context: Additional context

        Returns:
            Unified result
        """
        # Parallel retrieval from both sources
        live_task = self.live_rag.process_query(query, tenant_id)
        knowledge_task = self.knowledge_rag.retrieve(query, context)

        live_result, knowledge_result = await asyncio.gather(
            live_task,
            knowledge_task
        )

        # Merge contexts
        merged_context = self._merge_contexts(
            live_result.get('context_used', []),
            knowledge_result
        )

        # Build enhanced prompt with both sources
        prompt = self._build_unified_prompt(
            query=query,
            live_data=live_result,
            knowledge=knowledge_result
        )

        # Generate with Claude
        response = await self._generate_response(prompt)

        return {
            'answer': response,
            'sources': {
                'live_data': live_result.get('context_used', []),
                'knowledge_base': [r['source'] for r in knowledge_result]
            },
            'confidence': (live_result.get('confidence', 0) + 0.8) / 2
        }

    def _merge_contexts(
        self,
        live_contexts: List[Dict],
        knowledge_results: List[Dict]
    ) -> str:
        """Merge live and knowledge contexts"""

        parts = []

        # Live data section
        if live_contexts:
            parts.append("**Current Organization Data:**\n")
            for ctx in live_contexts:
                parts.append(f"- {ctx['module']}: {ctx['items_count']} items")
            parts.append("")

        # Knowledge base section
        if knowledge_results:
            parts.append("**Relevant Knowledge:**\n")
            for i, result in enumerate(knowledge_results, 1):
                parts.append(f"[{i}] {result['source']}: {result['content'][:200]}...")
            parts.append("")

        return "\n".join(parts)

    def _build_unified_prompt(
        self,
        query: str,
        live_data: Dict,
        knowledge: List[Dict]
    ) -> str:
        """Build prompt with both live and knowledge data"""

        return f"""You are BCM expert with access to:
1. Current organization data (live)
2. Industry knowledge base (standards, cases)

**Live Organization Data:**
{live_data.get('context_used', 'None')}

**Knowledge Base:**
{self._format_knowledge(knowledge)}

**User Query:**
{query}

Provide answer using BOTH live data and knowledge base.
Reference specific sources."""

    def _format_knowledge(self, knowledge: List[Dict]) -> str:
        """Format knowledge results"""
        return "\n".join([
            f"[{i}] {k['source']}: {k['content']}"
            for i, k in enumerate(knowledge, 1)
        ])
```

---

## 7. СТАТУС

### 7.1 Что реализовано ✅

| Component | Status | Location |
|-----------|--------|----------|
| **AI-Office RAG** | ✅ 100% | `/intelligent-core/ai-office/core/rag/` |
| - RAG Pipeline | ✅ | `rag_pipeline.py` (398 lines) |
| - Intent Analyzer | ✅ | `core/intent.py` |
| - Context Retriever | ✅ | `context_retriever.py` |
| - Anthropic Integration | ✅ | `core/adapters.py` |
| - Action Extraction | ✅ | Built-in |
| **AI-Experts RAG** | ✅ 95% | `/intelligent-core/ai_experts/rag/` |
| - RAG Pipeline | ✅ | `pipeline.py` (431 lines) |
| - Embeddings | ✅ | `embeddings.py` (Voyage/OpenAI/Local) |
| - Hybrid Retrieval | ✅ | `retrieval.py` (Vector + Keyword) |
| - Reranking | ✅ | `reranking.py` (Context + Diversity) |
| - Vector Store | ⚠️ | In-memory only (need pgvector) |
| - Knowledge Manager | ✅ | `pipeline.py` (KnowledgeSourceManager) |
| **Knowledge Sources** | ⚠️ 70% | |
| - ISO 22301 | ✅ | `load_iso_standards()` |
| - BCI Guidelines | ✅ | `load_bci_guidelines()` |
| - Case Library | ✅ | `load_case_library()` |
| - Community Annotations | ✅ | `load_community_annotations()` |
| - WHO Framework | ❌ | Not implemented |
| - Templates | ❌ | Not implemented |
| - FAQs | ❌ | Not implemented |

### 7.2 Что нужно ❌

| Component | Priority | Effort |
|-----------|----------|--------|
| **Production Vector DB** | 🔴 P0 | 2-3 дня |
| - pgvector (Supabase) | 🔴 | Primary choice |
| - Pinecone (optional) | 🟡 | For scale |
| **Missing Knowledge** | 🟡 P1 | 1-2 дня |
| - WHO Framework loader | 🟡 | Easy |
| - Templates library | 🟡 | Easy |
| - FAQs | 🟡 | Easy |
| **Unified RAG** | 🟢 P2 | 3-4 дня |
| - Combine live + knowledge | 🟢 | Medium |
| - Parallel retrieval | 🟢 | Medium |
| - Merged reranking | 🟢 | Medium |
| **Advanced Features** | 🔵 P3 | 5-7 дней |
| - Query expansion | 🔵 | Advanced |
| - Parent-child chunking | 🔵 | Advanced |
| - Multi-query retrieval | 🔵 | Advanced |
| - Cohere rerank | 🔵 | Optional |

### 7.3 Production Checklist

**Phase 1: Vector DB (Week 1)**
```sql
-- pgvector setup in Supabase

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE rag_embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    text TEXT NOT NULL,
    embedding VECTOR(1024),  -- or 1536 for OpenAI
    metadata JSONB,
    source_type TEXT,
    source_priority FLOAT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX ON rag_embeddings USING ivfflat (embedding vector_cosine_ops);
```

**Phase 2: Knowledge Loading (Week 1-2)**
```python
# Load all knowledge sources

manager = KnowledgeSourceManager(rag)

# ISO 22301
await manager.load_iso_standards(iso_data)

# BCI GPG
await manager.load_bci_guidelines(bci_data)

# Cases
await manager.load_case_library(cases)

# WHO Framework (new)
await manager.load_who_framework(who_data)

# Templates (new)
await manager.load_templates(templates)

# FAQs (new)
await manager.load_faqs(faqs)
```

**Phase 3: Unified RAG (Week 2-3)**
```python
# Production setup

unified_rag = UnifiedRAGPipeline(
    bcm_module_urls=BCM_SERVICES,
    knowledge_rag=ai_experts_rag,
    anthropic_api_key=ANTHROPIC_KEY
)

# Use in AI Colleagues
colleague = RiskAnalystColleague(
    rag=unified_rag,
    ...
)
```

---

## 📊 SUMMARY

### Текущее состояние:
- ✅ **2 working RAG implementations**
- ✅ **AI-Office RAG**: Live data retrieval (100%)
- ✅ **AI-Experts RAG**: Knowledge base search (95%)
- ⚠️ **Vector DB**: In-memory (need production DB)
- ⚠️ **Knowledge**: 4/7 sources loaded

### Следующие шаги:
1. **P0**: Implement pgvector (Supabase)
2. **P1**: Load missing knowledge sources
3. **P2**: Create Unified RAG
4. **P3**: Advanced features

### Уникальность подхода:
- 🎯 **Dual RAG strategy** (live + knowledge)
- 🎯 **Intent-aware routing**
- 🎯 **Action extraction**
- 🎯 **Context-aware reranking**

**RAG реализован на 85%!** 🚀
