"""
AI Foundation Integration for Coordination Center

Integrates RAG Pipeline and LLM Router from ai-foundation:
- RAG: Retrieves similar coordination patterns (conflict resolution, multi-service orchestration)
- LLM: Generates execution plans and conflict resolution strategies
- Pattern storage: Stores successful coordination patterns
"""

import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime
import sys

# Add ai-foundation to path
project_root = Path(__file__).parents[3]
sys.path.insert(0, str(project_root / "intelligent-core" / "ai-foundation"))

from rag.pipeline import RAGPipeline
from llm.llm_router import LLMRouter

logger = logging.getLogger(__name__)


class CoordinationAIFoundation:
    """
    AI Foundation integration for Coordination Center

    Provides:
    - RAG-enhanced coordination pattern retrieval
    - LLM-powered execution plan generation
    - Conflict resolution strategy generation
    - Pattern storage for coordination learning
    """

    def __init__(self):
        self.rag: Optional[RAGPipeline] = None
        self.llm: Optional[LLMRouter] = None

    async def initialize(self):
        """Initialize AI Foundation components"""

        try:
            # Initialize RAG for coordination pattern retrieval
            self.rag = RAGPipeline()
            logger.info("✅ RAG Pipeline initialized for Coordination Center")

            # Initialize LLM Router for execution plan generation
            self.llm = LLMRouter()
            logger.info("✅ LLM Router initialized for Coordination Center")

        except Exception as e:
            logger.error(f"❌ AI Foundation initialization failed: {e}")
            raise

    async def retrieve_coordination_patterns(
        self,
        task_type: str,
        involved_services: List[str],
        context: Dict[str, Any],
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Retrieve similar coordination patterns from RAG

        Args:
            task_type: Type of coordination task (e.g., "multi_service_orchestration")
            involved_services: List of services involved in coordination
            context: Additional context about the task
            top_k: Number of similar patterns to retrieve

        Returns:
            List of similar coordination patterns with relevance scores
        """

        if not self.rag:
            logger.warning("RAG not initialized, skipping pattern retrieval")
            return []

        # Build search query
        search_query = f"""
        Coordination Task: {task_type}

        Involved Services:
        {', '.join(involved_services)}

        Context:
        - Domain: {context.get('domain', 'unknown')}
        - Complexity: {context.get('complexity', 'medium')}
        - Priority: {context.get('priority', 'normal')}

        Find successful coordination patterns for similar multi-service orchestration scenarios.
        """

        try:
            similar_patterns = await self.rag.retrieve(
                query=search_query,
                context={
                    "domain": "coordination",
                    "task_type": task_type,
                    "services": involved_services
                },
                top_k=top_k,
                filters={"source_type": "coordination_patterns", "task_type": task_type},
                enable_reranking=True
            )

            logger.info(f"📚 Retrieved {len(similar_patterns)} coordination patterns from RAG")

            return similar_patterns

        except Exception as e:
            logger.warning(f"RAG pattern retrieval failed: {e}")
            return []

    async def retrieve_conflict_resolutions(
        self,
        conflict_type: str,
        conflicting_services: List[str],
        top_k: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Retrieve similar conflict resolution strategies from RAG

        Args:
            conflict_type: Type of conflict (e.g., "resource_contention", "priority_mismatch")
            conflicting_services: Services involved in the conflict
            top_k: Number of resolution strategies to retrieve

        Returns:
            List of conflict resolution strategies
        """

        if not self.rag:
            logger.warning("RAG not initialized")
            return []

        search_query = f"""
        Conflict Resolution Needed

        Conflict Type: {conflict_type}
        Conflicting Services: {', '.join(conflicting_services)}

        Find successful resolution strategies for similar service conflicts.
        """

        try:
            resolutions = await self.rag.retrieve(
                query=search_query,
                context={"domain": "coordination", "task": "conflict_resolution"},
                top_k=top_k,
                filters={"source_type": "conflict_resolutions", "conflict_type": conflict_type},
                enable_reranking=True
            )

            logger.info(f"🔧 Retrieved {len(resolutions)} conflict resolution strategies from RAG")

            return resolutions

        except Exception as e:
            logger.warning(f"RAG conflict resolution retrieval failed: {e}")
            return []

    async def generate_execution_plan(
        self,
        task_description: str,
        services: List[str],
        coordination_patterns: List[Dict] = None,
        constraints: Dict[str, Any] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> Dict[str, Any]:
        """
        Generate execution plan using LLM Router

        Args:
            task_description: Description of the task to coordinate
            services: List of services to coordinate
            coordination_patterns: Similar patterns from RAG (optional)
            constraints: Resource/time constraints
            temperature: Sampling temperature
            max_tokens: Maximum response tokens

        Returns:
            {
                'execution_plan': Dict,
                'steps': List[Dict],
                'confidence': float,
                'reasoning': str
            }
        """

        if not self.llm:
            logger.error("LLM Router not initialized")
            return {'execution_plan': {}, 'steps': [], 'confidence': 0.0}

        # Build enriched context with RAG knowledge
        knowledge_context = ""
        if coordination_patterns:
            knowledge_context = "SIMILAR COORDINATION PATTERNS:\n"
            for i, pattern in enumerate(coordination_patterns[:3], 1):
                knowledge_context += f"{i}. {pattern.get('content', '')}\n"

        # Build system prompt
        system_prompt = f"""You are a Coordination Expert for multi-service orchestration.

Your task is to generate a detailed execution plan for coordinating multiple services.

{knowledge_context}

TASK:
{task_description}

SERVICES TO COORDINATE:
{', '.join(services)}

CONSTRAINTS:
{self._format_constraints(constraints) if constraints else 'None specified'}

Generate a step-by-step execution plan that ensures efficient coordination and conflict avoidance.
"""

        user_prompt = """Generate an execution plan with:

1. Sequential steps (with dependencies)
2. Service assignments for each step
3. Expected duration for each step
4. Potential conflicts and mitigation strategies
5. Rollback procedures if needed

Format as structured JSON with clear step ordering."""

        try:
            response_text = await self.llm.query(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                task_type="content_generation",
                temperature=temperature,
                max_tokens=max_tokens
            )

            # Parse execution plan
            execution_plan = self._parse_execution_plan(response_text)

            # Calculate confidence
            confidence = self._calculate_plan_confidence(coordination_patterns, services)

            logger.info(f"✅ Generated execution plan with {len(execution_plan.get('steps', []))} steps, confidence: {confidence:.2f}")

            return {
                'execution_plan': execution_plan,
                'steps': execution_plan.get('steps', []),
                'confidence': confidence,
                'reasoning': response_text
            }

        except Exception as e:
            logger.error(f"❌ LLM execution plan generation failed: {e}")
            return {'execution_plan': {}, 'steps': [], 'confidence': 0.0}

    async def generate_conflict_resolution_strategy(
        self,
        conflict_description: str,
        conflicting_services: List[str],
        similar_resolutions: List[Dict] = None,
        temperature: float = 0.7,
        max_tokens: int = 1500
    ) -> Dict[str, Any]:
        """
        Generate conflict resolution strategy using LLM Router

        Args:
            conflict_description: Description of the conflict
            conflicting_services: Services in conflict
            similar_resolutions: Similar resolutions from RAG (optional)
            temperature: Sampling temperature
            max_tokens: Maximum response tokens

        Returns:
            {
                'strategy': str,
                'steps': List[str],
                'confidence': float
            }
        """

        if not self.llm:
            logger.error("LLM Router not initialized")
            return {'strategy': '', 'steps': [], 'confidence': 0.0}

        # Build context with RAG knowledge
        resolution_context = ""
        if similar_resolutions:
            resolution_context = "SIMILAR CONFLICT RESOLUTIONS:\n"
            for i, res in enumerate(similar_resolutions[:3], 1):
                resolution_context += f"{i}. {res.get('content', '')}\n"

        system_prompt = f"""You are a Conflict Resolution Expert for service coordination.

Your task is to resolve conflicts between services in a multi-service orchestration.

{resolution_context}

CONFLICT:
{conflict_description}

CONFLICTING SERVICES:
{', '.join(conflicting_services)}

Generate a resolution strategy that minimizes disruption and maintains service quality.
"""

        user_prompt = """Provide a conflict resolution strategy including:

1. Root cause analysis
2. Resolution steps (prioritized)
3. Service adjustments needed
4. Expected resolution time
5. Prevention measures for future

Format as clear, actionable steps."""

        try:
            response_text = await self.llm.query(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                task_type="content_generation",
                temperature=temperature,
                max_tokens=max_tokens
            )

            # Parse strategy
            strategy = self._parse_resolution_strategy(response_text)

            # Calculate confidence
            confidence = self._calculate_resolution_confidence(similar_resolutions)

            logger.info(f"✅ Generated conflict resolution strategy, confidence: {confidence:.2f}")

            return {
                'strategy': response_text,
                'steps': strategy.get('steps', []),
                'confidence': confidence
            }

        except Exception as e:
            logger.error(f"❌ LLM conflict resolution generation failed: {e}")
            return {'strategy': '', 'steps': [], 'confidence': 0.0}

    async def store_successful_coordination(
        self,
        task_type: str,
        services: List[str],
        execution_plan: Dict,
        outcome: str,
        success_metrics: Dict[str, Any]
    ):
        """
        Store successful coordination pattern in RAG for learning

        Args:
            task_type: Type of coordination task
            services: Services that were coordinated
            execution_plan: The successful execution plan
            outcome: Final outcome/result
            success_metrics: Metrics showing success (completion time, conflicts avoided, etc.)
        """

        if not self.rag:
            return

        # Format as learnable pattern
        pattern_text = f"""
        COORDINATION PATTERN - Multi-Service Orchestration

        Task Type: {task_type}
        Services Coordinated: {', '.join(services)}

        Execution Plan:
        {self._format_execution_plan(execution_plan)}

        Outcome:
        {outcome}

        Success Metrics:
        - Completion Time: {success_metrics.get('completion_time', 'N/A')}
        - Conflicts Avoided: {success_metrics.get('conflicts_avoided', 0)}
        - Resource Efficiency: {success_metrics.get('resource_efficiency', 'N/A')}

        Key Success Factors:
        - Coordinated {len(services)} services successfully
        - Efficient multi-service orchestration
        - Conflict prevention and resolution
        """

        try:
            await self.rag.ingest_documents(
                documents=[{
                    "text": pattern_text,
                    "metadata": {
                        "source_type": "coordination_patterns",
                        "task_type": task_type,
                        "service_count": len(services),
                        "success": True,
                        "timestamp": str(datetime.now())
                    }
                }],
                source_type="coordination_patterns"
            )

            logger.info(f"💾 Stored successful coordination pattern: {task_type}")

        except Exception as e:
            logger.warning(f"Failed to store pattern in RAG: {e}")

    async def store_conflict_resolution(
        self,
        conflict_type: str,
        conflicting_services: List[str],
        resolution_strategy: str,
        resolution_time: float,
        success: bool
    ):
        """
        Store conflict resolution strategy for learning

        Args:
            conflict_type: Type of conflict resolved
            conflicting_services: Services involved
            resolution_strategy: The resolution strategy used
            resolution_time: Time taken to resolve (minutes)
            success: Whether resolution was successful
        """

        if not self.rag or not success:
            return

        pattern_text = f"""
        CONFLICT RESOLUTION PATTERN

        Conflict Type: {conflict_type}
        Conflicting Services: {', '.join(conflicting_services)}

        Resolution Strategy:
        {resolution_strategy}

        Resolution Time: {resolution_time} minutes
        Success: {success}

        Pattern:
        Conflicts of type '{conflict_type}' between {len(conflicting_services)} services
        can be resolved efficiently using this strategy.
        """

        try:
            await self.rag.ingest_documents(
                documents=[{
                    "text": pattern_text,
                    "metadata": {
                        "source_type": "conflict_resolutions",
                        "conflict_type": conflict_type,
                        "service_count": len(conflicting_services),
                        "resolution_time": resolution_time,
                        "success": success,
                        "timestamp": str(datetime.now())
                    }
                }],
                source_type="conflict_resolutions"
            )

            logger.info(f"💾 Stored conflict resolution: {conflict_type}")

        except Exception as e:
            logger.warning(f"Failed to store conflict resolution: {e}")

    # ===== INTERNAL HELPERS =====

    def _format_constraints(self, constraints: Dict) -> str:
        """Format constraints for prompt"""
        formatted = []
        for key, value in constraints.items():
            formatted.append(f"- {key}: {value}")
        return "\n".join(formatted)

    def _parse_execution_plan(self, response_text: str) -> Dict:
        """Parse LLM response into structured execution plan"""
        # Simplified parsing - real implementation would use JSON parsing
        steps = []

        lines = response_text.split('\n')
        for line in lines:
            if any(keyword in line.lower() for keyword in ['step', 'phase', 'stage']):
                steps.append({
                    'description': line.strip(),
                    'status': 'pending'
                })

        return {
            'steps': steps[:10],  # Max 10 steps
            'total_steps': len(steps)
        }

    def _parse_resolution_strategy(self, response_text: str) -> Dict:
        """Parse LLM response into resolution strategy"""
        steps = []

        lines = response_text.split('\n')
        for line in lines:
            if any(keyword in line.lower() for keyword in ['adjust', 'modify', 'prioritize', 'resolve']):
                steps.append(line.strip())

        return {
            'steps': steps[:5]  # Top 5 steps
        }

    def _calculate_plan_confidence(self, patterns: List, services: List) -> float:
        """Calculate execution plan confidence"""
        base_confidence = 0.7

        # More similar patterns = higher confidence
        if patterns:
            pattern_count = len(patterns)
            if pattern_count >= 5:
                base_confidence += 0.15
            elif pattern_count >= 3:
                base_confidence += 0.10

        # More services = slightly lower confidence (more complex)
        if len(services) > 5:
            base_confidence -= 0.05
        elif len(services) <= 2:
            base_confidence += 0.05

        return min(1.0, round(base_confidence, 2))

    def _calculate_resolution_confidence(self, similar_resolutions: List) -> float:
        """Calculate conflict resolution confidence"""
        base_confidence = 0.7

        if similar_resolutions:
            resolution_count = len(similar_resolutions)
            if resolution_count >= 3:
                base_confidence += 0.15
            elif resolution_count >= 2:
                base_confidence += 0.10

        return min(1.0, round(base_confidence, 2))

    def _format_execution_plan(self, plan: Dict) -> str:
        """Format execution plan for storage"""
        formatted = []
        for i, step in enumerate(plan.get('steps', []), 1):
            formatted.append(f"Step {i}: {step.get('description', 'N/A')}")
        return "\n".join(formatted)


# Singleton instance
_ai_foundation = None

async def get_coordination_ai_foundation() -> CoordinationAIFoundation:
    """Get or create CoordinationAIFoundation singleton"""

    global _ai_foundation

    if _ai_foundation is None:
        _ai_foundation = CoordinationAIFoundation()
        await _ai_foundation.initialize()

    return _ai_foundation
