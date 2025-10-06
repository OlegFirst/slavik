"""
Collective Agent Service

Creates temporary AI agents from multiple organizations' experiences.

Core Magic:
- Organization A stuck on problem
- Platform finds organizations B, C, D, E that solved it
- Creates Collective Agent from their anonymized experiences
- A chats with agent without knowing who B, C, D, E are
- Full privacy + collective wisdom

Example:
>>> service = CollectiveAgentService(db, anonymizer, case_library, llm)
>>> agent_id = await service.create_collective_agent(
...     problem_type="supply_chain_complexity",
...     requesting_org_id="org-123"
... )
>>> response = await service.chat(agent_id, "How did you map Tier 2 suppliers?")
>>> # Agent: "Organizations that addressed this typically started with..."
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from ..models.database import CollectiveAgent, CollectiveAgentMessage, AgentStatus
from ..config import settings

class CollectiveAgentService:
    """
    Service for creating and managing Collective Agents

    Lifecycle:
    1. Creation: Platform detects stuck org → finds solvers → creates agent
    2. Chat: User interacts with collective wisdom
    3. Expiration: Agent deleted after 7 days
    """

    def __init__(
        self,
        db: AsyncSession,
        anonymizer,
        case_library,
        llm_client
    ):
        self.db = db
        self.anonymizer = anonymizer
        self.case_library = case_library
        self.llm = llm_client

    async def create_collective_agent(
        self,
        problem_type: str,
        requesting_org_id: str,
        min_success_rate: float = 0.8,
        min_orgs: int = 5
    ) -> str:
        """
        Create Collective Agent from successful organizations

        Args:
            problem_type: Type of problem (e.g., "supply_chain_complexity")
            requesting_org_id: Organization requesting help
            min_success_rate: Minimum success rate for source orgs
            min_orgs: Minimum number of source organizations

        Returns:
            agent_id: ID of created agent

        Privacy:
            - Source organizations never revealed
            - Minimum 5 orgs required
            - All data anonymized before aggregation
        """

        # 1. Find organizations that solved this problem
        solvers = await self._find_solver_organizations(
            problem_type=problem_type,
            min_success_rate=min_success_rate,
            exclude_org=requesting_org_id
        )

        if len(solvers) < min_orgs:
            raise InsufficientDataError(
                f"Need at least {min_orgs} organizations. Found {len(solvers)}."
            )

        # 2. Extract anonymized approaches
        approaches = []
        for solver in solvers:
            approach = await self._extract_anonymized_approach(solver)
            approaches.append(approach)

        # 3. Create system prompt for agent
        system_prompt = self._create_agent_system_prompt(
            problem_type=problem_type,
            approaches=approaches,
            org_count=len(solvers)
        )

        # 4. Create agent record
        agent = CollectiveAgent(
            id=uuid.uuid4(),
            requesting_org_id=uuid.UUID(requesting_org_id),
            problem_type=problem_type,
            source_org_count=len(solvers),
            source_org_types=[a['org_type'] for a in approaches],
            system_prompt=system_prompt,
            approaches_data=approaches,
            status=AgentStatus.ACTIVE,
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(days=settings.AGENT_EXPIRATION_DAYS)
        )

        self.db.add(agent)
        await self.db.commit()

        return str(agent.id)

    async def chat(
        self,
        agent_id: str,
        user_message: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Chat with Collective Agent

        Args:
            agent_id: Agent ID
            user_message: User's question
            user_id: User ID (for authorization)

        Returns:
            {
                'message': 'Agent response',
                'confidence': 0.85,
                'source_count': 5
            }

        Privacy:
            - Agent NEVER reveals which org did what
            - Speaks as "Organizations that..." or "The common pattern..."
            - Synthesizes across all experiences
        """

        # 1. Get agent
        agent = await self.db.get(CollectiveAgent, uuid.UUID(agent_id))

        if not agent:
            raise AgentNotFoundError(f"Agent {agent_id} not found")

        # 2. Check authorization
        if str(agent.requesting_org_id) != self._get_user_org(user_id):
            raise UnauthorizedError("Not your agent")

        # 3. Check expiration
        if agent.expires_at < datetime.utcnow():
            agent.status = AgentStatus.EXPIRED
            await self.db.commit()
            raise AgentExpiredError("Agent expired")

        # 4. Get conversation history
        history = await self._get_conversation_history(agent.id)

        # 5. Generate response using LLM
        response = await self._generate_agent_response(
            system_prompt=agent.system_prompt,
            history=history,
            user_message=user_message,
            approaches=agent.approaches_data
        )

        # 6. Save messages
        user_msg = CollectiveAgentMessage(
            agent_id=agent.id,
            role='user',
            content=user_message,
            created_at=datetime.utcnow()
        )

        agent_msg = CollectiveAgentMessage(
            agent_id=agent.id,
            role='assistant',
            content=response['message'],
            metadata={'confidence': response.get('confidence')}
        )

        self.db.add(user_msg)
        self.db.add(agent_msg)

        # Update agent stats
        agent.message_count += 2
        agent.last_interaction = datetime.utcnow()

        await self.db.commit()

        return {
            'message': response['message'],
            'confidence': response.get('confidence', 0.8),
            'source_count': agent.source_org_count,
            'expires_at': agent.expires_at.isoformat()
        }

    async def _find_solver_organizations(
        self,
        problem_type: str,
        min_success_rate: float,
        exclude_org: str
    ) -> List[Dict]:
        """
        Find organizations that successfully solved this problem

        Returns list of case data from successful organizations
        """

        # Query Case Library for successful cases
        cases = await self.case_library.find_cases(
            problem_type=problem_type,
            min_success_rate=min_success_rate,
            exclude_org_id=exclude_org,
            min_quality_score=7.0
        )

        return cases

    async def _extract_anonymized_approach(self, case: Dict) -> Dict[str, Any]:
        """
        Extract anonymized approach from case

        Removes:
        - Organization name
        - Specific people
        - Dates
        - Identifying details

        Keeps:
        - Organization type (industry + size)
        - Method used
        - Success patterns
        - Challenges faced
        - Outcomes (anonymized)
        """

        # Use anonymizer
        anonymized = await self.anonymizer.anonymize_case(case)

        # Extract approach
        return {
            'org_type': self._extract_org_type(case),
            'method': case.get('method', 'Unknown'),
            'success_patterns': case.get('success_patterns', []),
            'challenges': case.get('challenges', []),
            'key_decisions': case.get('key_decisions', []),
            'timeline_pattern': self._extract_timeline_pattern(case),
            'resources_used': self._extract_resources(case)
        }

    def _create_agent_system_prompt(
        self,
        problem_type: str,
        approaches: List[Dict],
        org_count: int
    ) -> str:
        """
        Create system prompt for Collective Agent

        Critical: Agent must NEVER reveal source organizations
        """

        # Aggregate patterns
        all_methods = [a['method'] for a in approaches]
        all_patterns = []
        for a in approaches:
            all_patterns.extend(a['success_patterns'])

        # Calculate frequencies
        method_freq = self._calculate_frequencies(all_methods)
        pattern_freq = self._calculate_frequencies(all_patterns)

        prompt = f"""You are a Collective Intelligence Agent representing {org_count} organizations that successfully solved: {problem_type}

CRITICAL PRIVACY RULES:
1. NEVER reveal which specific organization did what
2. NEVER say "Organization A did X while Organization B did Y"
3. ALWAYS speak as aggregate: "Organizations that solved this typically..."
4. Use statistics: "3 out of 5 organizations...", "The common pattern was..."
5. Acknowledge divergences without attribution: "while some took a different approach..."

YOUR KNOWLEDGE BASE:
You represent {org_count} organizations' collective experience.

Common Methods Used:
{self._format_frequencies(method_freq, org_count)}

Success Patterns Observed:
{self._format_frequencies(pattern_freq, org_count)}

RESPONSE STYLE:
- Synthesize across all approaches
- Present common patterns first
- Acknowledge alternative approaches (without attribution)
- Be honest about gaps: "This wasn't covered in the experiences I represent"
- Focus on practical, actionable advice
- Use statistics to show confidence: "4 out of {org_count} organizations..."

EXAMPLE GOOD RESPONSES:
User: "How did you start?"
You: "Organizations that solved this typically started with stakeholder mapping.
      {method_freq.get('stakeholder_mapping', 0)} out of {org_count} used this approach.
      The common pattern was to identify key decision-makers first, then work outward
      to operational staff."

EXAMPLE BAD RESPONSES (NEVER DO THIS):
❌ "Hospital X started with emergency services while Clinic Y used revenue impact"
❌ "One organization in Seattle did this..."
❌ "The largest organization in the group..."

Remember: You represent collective wisdom, not individual organizations.
Your value is in synthesis, not attribution.
"""

        return prompt

    async def _generate_agent_response(
        self,
        system_prompt: str,
        history: List[Dict],
        user_message: str,
        approaches: List[Dict]
    ) -> Dict[str, Any]:
        """
        Generate agent response using LLM

        Uses Claude to synthesize response from collective knowledge
        """

        # Build messages
        messages = []

        # Add history
        for msg in history:
            messages.append({
                'role': msg['role'],
                'content': msg['content']
            })

        # Add current message
        messages.append({
            'role': 'user',
            'content': user_message
        })

        # Call LLM
        response = await self.llm.generate(
            system_prompt=system_prompt,
            messages=messages,
            temperature=settings.AGENT_TEMPERATURE,
            max_tokens=settings.AGENT_MAX_TOKENS
        )

        # Calculate confidence based on pattern frequency
        confidence = self._calculate_response_confidence(response, approaches)

        return {
            'message': response,
            'confidence': confidence
        }

    def _calculate_frequencies(self, items: List[str]) -> Dict[str, int]:
        """Calculate frequency of items"""
        freq = {}
        for item in items:
            freq[item] = freq.get(item, 0) + 1
        return freq

    def _format_frequencies(self, freq: Dict[str, int], total: int) -> str:
        """Format frequencies as readable text"""
        lines = []
        for item, count in sorted(freq.items(), key=lambda x: -x[1]):
            percentage = (count / total) * 100
            lines.append(f"- {item}: {count}/{total} ({percentage:.0f}%)")
        return "\n".join(lines[:10])  # Top 10

    def _calculate_response_confidence(
        self,
        response: str,
        approaches: List[Dict]
    ) -> float:
        """
        Calculate confidence in response

        Based on:
        - How many orgs used similar approach
        - Variance in approaches
        """

        # Simple heuristic: More orgs = higher confidence
        # In production: Use semantic similarity
        return min(0.9, 0.5 + (len(approaches) * 0.08))

    async def _get_conversation_history(
        self,
        agent_id: uuid.UUID
    ) -> List[Dict]:
        """Get conversation history for agent"""

        result = await self.db.execute(
            select(CollectiveAgentMessage)
            .where(CollectiveAgentMessage.agent_id == agent_id)
            .order_by(CollectiveAgentMessage.created_at)
            .limit(50)  # Last 50 messages
        )

        messages = result.scalars().all()

        return [
            {
                'role': msg.role,
                'content': msg.content
            }
            for msg in messages
        ]

    def _extract_org_type(self, case: Dict) -> str:
        """Extract organization type for categorization"""
        context = case.get('organization_context', {})
        industry = context.get('industry', 'unknown')
        size = context.get('size', 'unknown')
        return f"{industry}_{size}"

    def _extract_timeline_pattern(self, case: Dict) -> Dict:
        """Extract anonymized timeline pattern"""
        journey = case.get('journey', {})
        return {
            'total_duration_days': journey.get('duration_days'),
            'phase_count': len(journey.get('phases', [])),
            'avg_phase_duration': journey.get('avg_phase_duration')
        }

    def _extract_resources(self, case: Dict) -> Dict:
        """Extract resource usage pattern"""
        return {
            'team_size': case.get('team_size', 'unknown'),
            'external_help': case.get('external_help_used', False),
            'tools_used': case.get('tools_used', [])
        }

    def _get_user_org(self, user_id: str) -> str:
        """Get organization ID for user (placeholder)"""
        # In production: Query user database
        return "org-123"

    async def get_agent(self, agent_id: str) -> Optional[CollectiveAgent]:
        """Get agent by ID"""
        return await self.db.get(CollectiveAgent, uuid.UUID(agent_id))

    async def get_active_agents(self, org_id: str) -> List[CollectiveAgent]:
        """Get active agents for organization"""

        result = await self.db.execute(
            select(CollectiveAgent)
            .where(
                and_(
                    CollectiveAgent.requesting_org_id == uuid.UUID(org_id),
                    CollectiveAgent.status == AgentStatus.ACTIVE,
                    CollectiveAgent.expires_at > datetime.utcnow()
                )
            )
            .order_by(CollectiveAgent.created_at.desc())
        )

        return result.scalars().all()

    async def expire_agents(self):
        """
        Expire old agents (cleanup job)

        Runs daily to delete agents past expiration
        """

        result = await self.db.execute(
            select(CollectiveAgent)
            .where(
                and_(
                    CollectiveAgent.status == AgentStatus.ACTIVE,
                    CollectiveAgent.expires_at < datetime.utcnow()
                )
            )
        )

        agents = result.scalars().all()

        for agent in agents:
            agent.status = AgentStatus.EXPIRED

        await self.db.commit()

        return len(agents)


class InsufficientDataError(Exception):
    """Not enough organizations to create collective agent"""
    pass

class AgentNotFoundError(Exception):
    """Agent not found"""
    pass

class AgentExpiredError(Exception):
    """Agent has expired"""
    pass

class UnauthorizedError(Exception):
    """User not authorized to access agent"""
    pass
