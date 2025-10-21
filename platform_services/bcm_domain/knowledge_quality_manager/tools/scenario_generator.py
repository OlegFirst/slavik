"""
Scenario Generator - Transforms data into knowledge

Philosophy: Knowledge is the foundation of existence
- Data → Knowledge (understanding)
- Knowledge → Tools/Experience (implementation)
- Experience → Memory/Data (cycle continues)
"""

import logging
import json
import os
import random
from typing import List, Dict, Optional
from datetime import datetime
import httpx
from anthropic import Anthropic

from models import KnowledgeGap, Scenario, ScenarioType, GapType
from config.settings import settings

logger = logging.getLogger(__name__)

# Import Qdrant for local RAG
try:
    from qdrant_client import QdrantClient
except ImportError:
    QdrantClient = None
    logger.warning("qdrant-client not installed - RAG will be disabled")


class ScenarioGenerator:
    """
    Generates scenarios from multiple sources:
    1. Standards (ISO/NIST/WHO) - compliance knowledge
    2. Platform capabilities - implementation knowledge
    3. User requests - practical knowledge
    4. Community patterns - collective knowledge

    Trinity Integration:
    - KNOWLEDGE: Creates scenarios from gaps
    - PROTECTION: Ensures standards compliance
    - SELF-REALIZATION: Makes knowledge actionable
    """

    def __init__(self):
        self.anthropic = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.http_client = httpx.AsyncClient(timeout=30.0)

        # Knowledge economy metrics
        self.generation_count = 0
        self.knowledge_value = 0.0  # Economic value of generated knowledge

        # Initialize local RAG (Qdrant)
        self.qdrant_client = None
        self.qdrant_collection = "business_scenarios"
        self.vector_size = 384

        if QdrantClient:
            try:
                qdrant_path = os.path.join(
                    os.path.dirname(__file__),
                    "..",
                    "qdrant_local"
                )
                self.qdrant_client = QdrantClient(path=qdrant_path)
                logger.info(f" RAG initialized (local Qdrant at {qdrant_path})")
            except Exception as e:
                logger.warning(f"RAG initialization failed: {e}")
                self.qdrant_client = None

        logger.info(" ScenarioGenerator initialized")

    async def generate(self, gaps: List[KnowledgeGap]) -> List[Scenario]:
        """
        Generate scenarios from prioritized gaps

        Trinity cycle:
        1. KNOWLEDGE: Identify what we don't know
        2. PROTECTION: Ensure safety/compliance
        3. SELF-REALIZATION: Create actionable scenarios
        """
        scenarios = []

        for gap in gaps:
            try:
                logger.info(f" Generating scenario for gap: {gap.description[:50]}...")

                # Route to appropriate generator based on gap type
                if gap.type == GapType.STANDARD_REQUIREMENT:
                    scenario = await self.generate_from_standard(gap)
                elif gap.type == GapType.PLATFORM_CAPABILITY:
                    scenario = await self.generate_from_capability(gap)
                elif gap.type == GapType.USER_REQUEST:
                    scenario = await self.generate_from_request(gap)
                elif gap.type == GapType.COMMUNITY_PATTERN:
                    scenario = await self.generate_from_community(gap)
                else:
                    logger.warning(f"Unknown gap type: {gap.type}")
                    continue

                if scenario:
                    scenarios.append(scenario)
                    self.generation_count += 1
                    self.knowledge_value += self._calculate_knowledge_value(scenario)

                    # Auto-save to file system (Memory persistence)
                    await self._save_scenario(scenario)

            except Exception as e:
                logger.error(f"Generation error for gap {gap.id}: {e}")
                continue

        logger.info(f" Generated {len(scenarios)} scenarios")
        logger.info(f" Knowledge value: {self.knowledge_value:.2f} units")

        return scenarios

    async def generate_from_standard(self, gap: KnowledgeGap) -> Optional[Scenario]:
        """
        Generate from standard requirement (ISO/NIST/WHO)

        PROTECTION focus: Ensures compliance and safety
        """
        logger.info(f" Generating from standard: {gap.standard} {gap.clause}")

        # 1. Fetch RAG context (similar scenarios)
        rag_context = await self._get_rag_context(
            f"{gap.standard} {gap.clause} {gap.description}"
        )

        # 2. Get standard requirement details
        standard_details = await self._get_standard_details(gap.standard, gap.clause)

        # 3. Generate with LLM
        prompt = f"""You are a BCM expert creating a business scenario for ISO 22301 compliance.

**Standard**: {gap.standard}
**Clause**: {gap.clause}
**Requirement**: {gap.description}

**Standard Details**:
{standard_details}

**Similar Scenarios** (for reference):
{rag_context}

**Task**: Create a detailed business scenario that demonstrates compliance with this requirement.

**Format**:
Title: [Clear, action-oriented title]
Service: [Which BCM service: BIA, Risk, Planning, Response, etc.]
Category: [Core/Configuration/Reports/Integration]

**Description**:
[2-3 paragraphs explaining the scenario, business context, and compliance value]

**Inputs**:
- [Input parameter 1]
- [Input parameter 2]
...

**Outputs**:
- [Output 1]
- [Output 2]
...

**Events Triggered**:
- [event.name.1]
- [event.name.2]

**Components**:
Service → Component1 → Component2 → ...

**ISO 22301 Mapping**: {gap.clause}
**Compliance Value**: [How this meets the standard]

Generate ONLY the scenario content, no explanations."""

        try:
            message = self.anthropic.messages.create(
                model="claude-opus-4-20250514",
                max_tokens=2000,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}]
            )

            content = message.content[0].text

            # Parse LLM response into Scenario
            scenario = self._parse_llm_response(
                content=content,
                gap=gap,
                scenario_type=ScenarioType.STANDARD
            )

            return scenario

        except Exception as e:
            logger.error(f"LLM generation error: {e}")
            return None

    async def generate_from_capability(self, gap: KnowledgeGap) -> Optional[Scenario]:
        """
        Generate from platform capability

        SELF-REALIZATION focus: Turns capabilities into value
        """
        logger.info(f"️ Generating from capability: {gap.service} - {gap.capability}")

        # 1. Get platform API documentation
        api_docs = await self._get_api_docs(gap.service)

        # 2. Get similar scenarios
        rag_context = await self._get_rag_context(
            f"{gap.service} {gap.capability} {gap.description}"
        )

        # 3. Generate with LLM
        prompt = f"""You are a BCM platform expert creating a business scenario for a platform capability.

**Service**: {gap.service}
**Capability**: {gap.capability}
**Description**: {gap.description}

**Platform APIs**:
{api_docs}

**Similar Scenarios**:
{rag_context}

**Task**: Create a practical business scenario showing how users leverage this capability.

**Format**:
Title: [User-focused title: "Conduct AI-Assisted BIA"]
Service: {gap.service}
Category: [Core/Advanced/Integration]

**Description**:
[Business context, user goals, value proposition]

**Inputs**:
- [What user provides]

**Outputs**:
- [What user receives]

**Events**:
- [System events]

**Components**:
[Technical flow]

**Business Value**: [ROI, efficiency gain, risk reduction]

Generate ONLY the scenario content."""

        try:
            message = self.anthropic.messages.create(
                model="claude-opus-4-20250514",
                max_tokens=2000,
                temperature=0.4,
                messages=[{"role": "user", "content": prompt}]
            )

            content = message.content[0].text

            scenario = self._parse_llm_response(
                content=content,
                gap=gap,
                scenario_type=ScenarioType.GENERATED
            )

            return scenario

        except Exception as e:
            logger.error(f"LLM generation error: {e}")
            return None

    async def generate_from_request(self, gap: KnowledgeGap) -> Optional[Scenario]:
        """
        Generate from user request

        KNOWLEDGE focus: Answers user questions with actionable scenarios
        """
        logger.info(f" Generating from user request: {gap.user_question}")

        # 1. Search existing knowledge
        rag_context = await self._get_rag_context(gap.user_question)

        # 2. Analyze question intent
        intent = await self._analyze_user_intent(gap.user_question)

        # 3. Generate targeted scenario
        prompt = f"""You are a BCM assistant answering a user question with a practical scenario.

**User Question**: {gap.user_question}
**Intent**: {intent}

**Existing Knowledge**:
{rag_context}

**Task**: Create a scenario that directly answers the user's question.

**Format**:
Title: [Answer-oriented: "How to Conduct BIA with AI"]
Service: [Most relevant service]
Category: [Practical/Tutorial]

**Description**:
[Direct answer to user question, step-by-step guidance]

**Inputs**:
[What user needs to start]

**Outputs**:
[What user achieves]

**Step-by-Step**:
1. [Action 1]
2. [Action 2]
...

**Components**:
[System components involved]

**Tips**: [Best practices, common pitfalls]

Generate ONLY the scenario content."""

        try:
            message = self.anthropic.messages.create(
                model="claude-opus-4-20250514",
                max_tokens=2000,
                temperature=0.5,
                messages=[{"role": "user", "content": prompt}]
            )

            content = message.content[0].text

            scenario = self._parse_llm_response(
                content=content,
                gap=gap,
                scenario_type=ScenarioType.GENERATED
            )

            return scenario

        except Exception as e:
            logger.error(f"LLM generation error: {e}")
            return None

    async def generate_from_community(self, gap: KnowledgeGap) -> Optional[Scenario]:
        """
        Generate from community pattern (k≥5)

        KNOWLEDGE focus: Collective intelligence
        """
        logger.info(f" Generating from community pattern")

        # Get anonymized patterns from Community Intelligence
        try:
            response = await self.http_client.get(
                f"{settings.COMMUNITY_INTEL_URL}/api/patterns/find-similar",
                params={"description": gap.description, "k": 5}
            )

            if response.status_code == 200:
                patterns = response.json()

                # Generate scenario from patterns
                prompt = f"""Create a business scenario based on community patterns.

**Patterns** (k=5, anonymized):
{json.dumps(patterns, indent=2)}

**Task**: Synthesize a general scenario from these patterns.

Generate ONLY the scenario content."""

                message = self.anthropic.messages.create(
                    model="claude-opus-4-20250514",
                    max_tokens=2000,
                    temperature=0.6,
                    messages=[{"role": "user", "content": prompt}]
                )

                content = message.content[0].text

                scenario = self._parse_llm_response(
                    content=content,
                    gap=gap,
                    scenario_type=ScenarioType.COMMUNITY
                )

                return scenario

        except Exception as e:
            logger.error(f"Community pattern error: {e}")
            return None

    # ===== HELPER METHODS =====

    async def _get_rag_context(self, query: str, top_k: int = 5) -> str:
        """Get similar scenarios from RAG"""

        # Try local Qdrant first
        if self.qdrant_client:
            try:
                # Generate mock embedding for query (deterministic)
                query_vector = self._generate_mock_embedding(query)

                # Search in Qdrant
                results = self.qdrant_client.query_points(
                    collection_name=self.qdrant_collection,
                    query=query_vector,
                    limit=top_k
                )

                if results and len(results.points) > 0:
                    context = "\n\n".join([
                        f"**{r.payload['title']}**\n{r.payload['content'][:200]}..."
                        for r in results.points
                    ])
                    logger.info(f" RAG found {len(results.points)} similar scenarios")
                    return context

            except Exception as e:
                logger.warning(f"Local RAG error: {e}")

        # Fallback to HTTP API (if available)
        try:
            response = await self.http_client.post(
                f"{settings.AI_FOUNDATION_URL}/api/rag/search",
                json={
                    "query": query,
                    "collection": "business_scenarios",
                    "top_k": top_k
                }
            )

            if response.status_code == 200:
                results = response.json()
                context = "\n\n".join([
                    f"**{r['title']}**\n{r['content'][:200]}..."
                    for r in results.get('results', [])
                ])
                return context

        except Exception as e:
            logger.debug(f"HTTP RAG context error: {e}")

        return "No similar scenarios found."

    def _generate_mock_embedding(self, text: str) -> List[float]:
        """Generate mock embedding for development (matches load script)"""
        # Deterministic random based on text hash
        random.seed(hash(text) % (2**32))

        # Generate normalized random vector
        vector = [random.gauss(0, 1) for _ in range(self.vector_size)]

        # Normalize
        magnitude = sum(x**2 for x in vector) ** 0.5
        vector = [x / magnitude for x in vector]

        return vector

    async def _get_standard_details(self, standard: str, clause: str) -> str:
        """Get standard requirement details"""
        # Simplified - in production, fetch from standards database
        return f"{standard} Clause {clause}: Requirements and guidance"

    async def _get_api_docs(self, service: str) -> str:
        """Get platform API documentation"""
        # Simplified - in production, fetch from API registry
        return f"{service} Service API endpoints and capabilities"

    async def _analyze_user_intent(self, question: str) -> str:
        """Analyze user question intent"""
        # Simple intent analysis - can be enhanced with NLP
        if "how to" in question.lower():
            return "Tutorial/Guide"
        elif "what is" in question.lower():
            return "Explanation"
        elif "can i" in question.lower():
            return "Capability check"
        else:
            return "General inquiry"

    def _parse_llm_response(
        self,
        content: str,
        gap: KnowledgeGap,
        scenario_type: ScenarioType
    ) -> Scenario:
        """Parse LLM response into Scenario object"""

        # Simple parsing - extract title, service, description
        lines = content.split('\n')

        title = "Generated Scenario"
        service = gap.service or "General"
        category = "Generated"
        description = content[:500]

        # Try to extract structured fields
        for i, line in enumerate(lines):
            if line.startswith("Title:"):
                title = line.replace("Title:", "").strip()
            elif line.startswith("Service:"):
                service = line.replace("Service:", "").strip()
            elif line.startswith("Category:"):
                category = line.replace("Category:", "").strip()

        scenario = Scenario(
            id=f"gen_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{gap.id[:8]}",
            title=title,
            content=content,
            type=scenario_type,
            service=service,
            category=category,
            iso_clause=gap.clause,
            source=f"auto_generated_from_{gap.type}",
            confidence=0.75,  # Default confidence
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        return scenario

    async def _save_scenario(self, scenario: Scenario):
        """Save scenario to file system (memory persistence)"""
        try:
            # Determine directory
            service_dir = scenario.service.lower() if scenario.service else "general"
            month_dir = datetime.now().strftime("%Y-%m")

            output_dir = os.path.join(
                settings.GENERATED_PATH,
                month_dir,
                service_dir
            )

            os.makedirs(output_dir, exist_ok=True)

            # Save as markdown
            filename = f"{scenario.id}.md"
            filepath = os.path.join(output_dir, filename)

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"# {scenario.title}\n\n")
                f.write(f"**ID**: {scenario.id}\n")
                f.write(f"**Service**: {scenario.service}\n")
                f.write(f"**Category**: {scenario.category}\n")
                f.write(f"**Type**: {scenario.type}\n")
                f.write(f"**ISO Clause**: {scenario.iso_clause or 'N/A'}\n")
                f.write(f"**Confidence**: {scenario.confidence:.2f}\n")
                f.write(f"**Generated**: {scenario.created_at}\n\n")
                f.write("---\n\n")
                f.write(scenario.content)

            logger.info(f" Saved scenario: {filepath}")

        except Exception as e:
            logger.error(f"Save error: {e}")

    def _calculate_knowledge_value(self, scenario: Scenario) -> float:
        """
        Calculate economic value of generated knowledge

        Knowledge Economy Formula:
        Value = Confidence × Relevance × Reusability × Compliance
        """
        confidence = scenario.confidence
        relevance = 0.8  # Based on gap priority
        reusability = 0.9 if scenario.type == ScenarioType.STANDARD else 0.7
        compliance = 1.0 if scenario.iso_clause else 0.5

        value = confidence * relevance * reusability * compliance * 100

        return value
