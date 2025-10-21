"""
Intent Analysis Engine (with ACE learning!)

Extended from PDCA Assistant's _analyze_user_intent() with improved
regex patterns and entity extraction for BCM-specific queries.
"""

import re
import logging
from typing import Dict, List, Optional, Any
from enum import Enum
from pydantic import BaseModel
import sys

# Add platform root for ACE integration
sys.path.insert(0, '/Users/MD/AI-Platform-ISO')
from shared.ace_integration import ACEIntegration

logger = logging.getLogger(__name__)


class IntentType(str, Enum):
    """Types of user intents in BCM context"""
    # Information retrieval
    QUERY_INFO = "query_info"
    GET_STATUS = "get_status"
    LIST_ITEMS = "list_items"
    SEARCH = "search"

    # Analysis requests
    ANALYZE_RISK = "analyze_risk"
    ANALYZE_BIA = "analyze_bia"
    ASSESS_COMPLIANCE = "assess_compliance"
    REVIEW_PLAN = "review_plan"

    # Creation/Generation
    CREATE_PLAN = "create_plan"
    GENERATE_DOCUMENT = "generate_document"
    DESIGN_EXERCISE = "design_exercise"
    CREATE_TRAINING = "create_training"

    # Actions
    UPDATE_ITEM = "update_item"
    APPROVE = "approve"
    REJECT = "reject"
    ESCALATE = "escalate"

    # Guidance
    RECOMMEND = "recommend"
    SUGGEST_ACTIONS = "suggest_actions"
    EXPLAIN = "explain"
    HELP = "help"

    # Unknown
    UNKNOWN = "unknown"


class BCMModule(str, Enum):
    """BCM Platform modules"""
    GOVERNANCE = "governance"
    BIA = "bia"
    RISK = "risk"
    PLANNING = "planning"
    PLANS = "plans"
    RESPONSE = "response"
    COMPLIANCE = "compliance"
    VALIDATION = "validation"
    DOCUMENTS = "documents"
    LEARNING = "learning"
    GENERAL = "general"


class IntentResult(BaseModel):
    """Result of intent analysis"""
    intent_type: IntentType
    confidence: float
    module: BCMModule
    entities: Dict[str, Any]
    keywords: List[str]
    is_question: bool
    requires_context: bool


class IntentAnalyzer:
    """
    Analyzes user messages to determine intent and extract entities.

    Extended from PDCA Assistant with:
    - Better regex patterns
    - Entity extraction (risks, processes, plans, etc.)
    - Module routing
    - Confidence scoring
    """

    def __init__(self):
        """Initialize intent analyzer with pattern rules"""
        # ACE Integration for continuous learning
        self.ace = ACEIntegration(module_name="ai_office_intent")

        self.patterns = self._build_patterns()

    async def analyze(self, message: str, conversation_history: Optional[List[Dict]] = None) -> IntentResult:
        """
        Analyze user message to determine intent (with ACE learning!)

        Args:
            message: User's message
            conversation_history: Optional previous messages for context

        Returns:
            IntentResult with detected intent and entities
        """

        # Use ACE for continuous learning of intent patterns!
        result = await self.ace.execute_with_learning(
            task_type="intent_analysis",
            base_context={
                "message": message,
                "has_history": conversation_history is not None
            },
            execute_fn=self._analyze_impl,
            message=message,
            conversation_history=conversation_history
        )

        return result.get('intent_result')

    async def _analyze_impl(
        self,
        context: Dict[str, Any],
        message: str,
        conversation_history: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """Internal intent analysis implementation (called by ACE)"""

        # ACE provides enhanced context!
        strategies = context.get('playbook_strategies', [])
        if strategies:
            logger.info(f" ACE enhanced intent analysis with {len(strategies)} strategies")

        message_lower = message.lower().strip()

        # Check if question
        is_question = self._is_question(message_lower)

        # Extract entities first
        entities = self._extract_entities(message)

        # Determine intent type
        intent_type, confidence = self._determine_intent(message_lower, entities)

        # Determine target module
        module = self._determine_module(message_lower, entities)

        # Extract keywords
        keywords = self._extract_keywords(message_lower)

        # Check if requires context retrieval
        requires_context = self._requires_context(intent_type, is_question)

        intent_result = IntentResult(
            intent_type=intent_type,
            confidence=confidence,
            module=module,
            entities=entities,
            keywords=keywords,
            is_question=is_question,
            requires_context=requires_context
        )

        # Effectiveness = confidence (ACE will learn to improve!)
        return {
            'intent_result': intent_result,
            'effectiveness': confidence
        }

    def _build_patterns(self) -> Dict[IntentType, List[re.Pattern]]:
        """Build regex patterns for intent detection"""
        return {
            # Queries
            IntentType.QUERY_INFO: [
                re.compile(r'\b(what|which|where|when|who)\b.*\b(is|are|was|were)\b'),
                re.compile(r'\b(tell me|show me|explain)\b.*\babout\b'),
                re.compile(r'\b(information|details|data)\b.*\b(on|about|for)\b'),
            ],
            IntentType.GET_STATUS: [
                re.compile(r'\b(status|state|progress)\b.*\b(of|for)\b'),
                re.compile(r'\b(how is|what\'s the)\b.*\b(going|progressing)\b'),
                re.compile(r'\b(current|latest)\b.*\b(status|state)\b'),
            ],
            IntentType.LIST_ITEMS: [
                re.compile(r'\b(list|show|display)\b.*\b(all|my|the)\b'),
                re.compile(r'\b(what are|give me)\b.*\b(risks|plans|processes|incidents)\b'),
                re.compile(r'\btop\s+\d+\b'),
            ],

            # Analysis
            IntentType.ANALYZE_RISK: [
                re.compile(r'\banalyze\b.*\b(risk|threat|vulnerability)\b'),
                re.compile(r'\brisk\b.*\b(assessment|analysis|evaluation)\b'),
                re.compile(r'\b(identify|assess|evaluate)\b.*\b(risks|threats)\b'),
            ],
            IntentType.ANALYZE_BIA: [
                re.compile(r'\banalyze\b.*\b(bia|impact|business impact)\b'),
                re.compile(r'\b(rto|rpo|mao|mtd)\b'),
                re.compile(r'\bcritical\b.*\b(processes|functions|activities)\b'),
            ],
            IntentType.ASSESS_COMPLIANCE: [
                re.compile(r'\b(compliance|conformance|conformity)\b.*\b(check|assessment|audit)\b'),
                re.compile(r'\b(iso|standard|regulation)\b.*\b(compliance|conformity)\b'),
                re.compile(r'\bgaps?\b.*\b(analysis|assessment)\b'),
            ],

            # Creation
            IntentType.CREATE_PLAN: [
                re.compile(r'\b(create|generate|develop|build)\b.*\b(plan|bcp|strategy)\b'),
                re.compile(r'\bplan\b.*\b(for|to)\b'),
                re.compile(r'\bnew\b.*\b(plan|bcp|strategy)\b'),
            ],
            IntentType.GENERATE_DOCUMENT: [
                re.compile(r'\b(generate|create|produce)\b.*\b(document|report|policy)\b'),
                re.compile(r'\bdocument\b.*\b(for|about)\b'),
            ],
            IntentType.DESIGN_EXERCISE: [
                re.compile(r'\b(design|create|plan)\b.*\b(exercise|test|drill)\b'),
                re.compile(r'\bexercise\b.*\b(for|to test)\b'),
            ],

            # Actions
            IntentType.UPDATE_ITEM: [
                re.compile(r'\b(update|modify|change|edit)\b'),
                re.compile(r'\bset\b.*\bto\b'),
            ],
            IntentType.APPROVE: [
                re.compile(r'\b(approve|accept|confirm)\b'),
            ],
            IntentType.REJECT: [
                re.compile(r'\b(reject|decline|deny)\b'),
            ],

            # Guidance
            IntentType.RECOMMEND: [
                re.compile(r'\b(recommend|suggest|advise)\b'),
                re.compile(r'\bwhat (should|would you|do you)\b.*\b(recommend|suggest)\b'),
            ],
            IntentType.SUGGEST_ACTIONS: [
                re.compile(r'\b(next steps|what should i do|what to do)\b'),
                re.compile(r'\b(actions|tasks)\b.*\b(needed|required|recommended)\b'),
            ],
            IntentType.EXPLAIN: [
                re.compile(r'\b(explain|describe|clarify)\b'),
                re.compile(r'\bhow (does|do|can|to)\b'),
                re.compile(r'\bwhy (is|are|does|do)\b'),
            ],
            IntentType.HELP: [
                re.compile(r'\b(help|assist|support|guide)\b'),
                re.compile(r'\b(can you|could you|please)\b.*\bhelp\b'),
            ],
        }

    def _determine_intent(self, message: str, entities: Dict[str, Any]) -> tuple[IntentType, float]:
        """
        Determine intent type with confidence score.

        Returns:
            (IntentType, confidence_score)
        """
        matched_intents = []

        # Check patterns
        for intent_type, patterns in self.patterns.items():
            for pattern in patterns:
                if pattern.search(message):
                    matched_intents.append(intent_type)
                    break

        if not matched_intents:
            return IntentType.UNKNOWN, 0.3

        # Return most specific match
        intent = matched_intents[0]

        # Calculate confidence based on entity presence
        confidence = 0.7
        if entities:
            confidence = 0.9

        return intent, confidence

    def _determine_module(self, message: str, entities: Dict[str, Any]) -> BCMModule:
        """Determine which BCM module the query is about"""

        # Check entities first
        if 'risk_id' in entities or 'risks' in message:
            return BCMModule.RISK
        if 'bia' in message or 'rto' in message or 'rpo' in message:
            return BCMModule.BIA
        if 'plan' in message or 'bcp' in message:
            return BCMModule.PLANS
        if 'compliance' in message or 'iso' in message or 'audit' in message:
            return BCMModule.COMPLIANCE
        if 'incident' in message or 'response' in message:
            return BCMModule.RESPONSE
        if 'exercise' in message or 'test' in message or 'drill' in message:
            return BCMModule.VALIDATION
        if 'training' in message or 'learning' in message:
            return BCMModule.LEARNING
        if 'document' in message or 'policy' in message:
            return BCMModule.DOCUMENTS
        if 'governance' in message or 'policy' in message:
            return BCMModule.GOVERNANCE
        if 'planning' in message or 'strategy' in message:
            return BCMModule.PLANNING

        return BCMModule.GENERAL

    def _extract_entities(self, message: str) -> Dict[str, Any]:
        """
        Extract BCM-specific entities from message.

        Entities:
        - risk_id: RISK-XXX
        - plan_id: PLAN-XXX
        - process_id: PROC-XXX
        - incident_id: INC-XXX
        - numbers: RTO/RPO values, priorities, etc.
        """
        entities = {}

        # Extract IDs
        risk_match = re.search(r'\bRISK-(\d+)', message, re.IGNORECASE)
        if risk_match:
            entities['risk_id'] = f"RISK-{risk_match.group(1)}"

        plan_match = re.search(r'\bPLAN-(\d+)', message, re.IGNORECASE)
        if plan_match:
            entities['plan_id'] = f"PLAN-{plan_match.group(1)}"

        process_match = re.search(r'\bPROC-(\d+)', message, re.IGNORECASE)
        if process_match:
            entities['process_id'] = f"PROC-{process_match.group(1)}"

        incident_match = re.search(r'\bINC-(\d+)', message, re.IGNORECASE)
        if incident_match:
            entities['incident_id'] = f"INC-{incident_match.group(1)}"

        # Extract numbers (for "top 5", "RTO 4 hours", etc.)
        top_n_match = re.search(r'\btop\s+(\d+)', message, re.IGNORECASE)
        if top_n_match:
            entities['top_n'] = int(top_n_match.group(1))

        # Extract time values
        time_match = re.search(r'(\d+)\s*(hour|minute|day|week)s?', message, re.IGNORECASE)
        if time_match:
            entities['time_value'] = int(time_match.group(1))
            entities['time_unit'] = time_match.group(2).lower()

        # Extract priority
        if re.search(r'\b(high|critical|urgent)\b', message, re.IGNORECASE):
            entities['priority'] = 'high'
        elif re.search(r'\b(medium|moderate)\b', message, re.IGNORECASE):
            entities['priority'] = 'medium'
        elif re.search(r'\b(low)\b', message, re.IGNORECASE):
            entities['priority'] = 'low'

        return entities

    def _extract_keywords(self, message: str) -> List[str]:
        """Extract important keywords for context retrieval"""
        # Remove common words
        stop_words = {
            'a', 'an', 'the', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'can', 'what', 'which', 'who', 'when', 'where',
            'how', 'why', 'my', 'me', 'i', 'you', 'we', 'they', 'to', 'from', 'for',
            'with', 'about', 'of', 'in', 'on', 'at', 'and', 'or', 'but'
        }

        # Extract words
        words = re.findall(r'\b[a-z]{3,}\b', message)

        # Filter and return
        keywords = [w for w in words if w not in stop_words]

        return keywords[:10]  # Top 10 keywords

    def _is_question(self, message: str) -> bool:
        """Check if message is a question"""
        return (
            message.endswith('?') or
            message.startswith(('what', 'which', 'where', 'when', 'who', 'how', 'why', 'is', 'are', 'do', 'does', 'can', 'could', 'should'))
        )

    def _requires_context(self, intent_type: IntentType, is_question: bool) -> bool:
        """Determine if intent requires context retrieval from BCM modules"""
        # These intents always need context
        context_required = {
            IntentType.QUERY_INFO,
            IntentType.GET_STATUS,
            IntentType.LIST_ITEMS,
            IntentType.ANALYZE_RISK,
            IntentType.ANALYZE_BIA,
            IntentType.ASSESS_COMPLIANCE,
            IntentType.REVIEW_PLAN,
        }

        # Questions usually need context
        if is_question:
            return True

        return intent_type in context_required
