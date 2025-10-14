"""
🎨 AI Example Generator

Generates perfect examples ON DEMAND for any scenario.

MAGIC:
- User asks: "Show me BIA for hospital supply chain"
- AI generates: Complete, realistic example in seconds
- Based on: Real anonymized data from collective intelligence
- Personalized: Matches user's exact context

No more generic examples. Every example is YOURS.

Example:
>>> generator = AIExampleGenerator()
>>>
>>> example = await generator.generate(
...     topic="bia_process_identification",
...     context={
...         "industry": "healthcare",
...         "org_type": "hospital",
...         "specific_area": "supply_chain"
...     }
... )
>>>
>>> print(example['content'])
>>> # Complete BIA example for hospital supply chain
>>> # - Critical processes identified
>>> # - Dependencies mapped
>>> # - RTOs calculated
>>> # - Based on real hospital data!
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)

class AIExampleGenerator:
    """
    Generates contextual examples using AI + Collective Intelligence

    Netflix recommendation engine for documentation examples!
    """

    def __init__(
        self,
        ai_client,
        collective_intelligence,
        case_library
    ):
        self.ai = ai_client
        self.collective = collective_intelligence
        self.cases = case_library

        logger.info("🎨 AI Example Generator initialized")

    async def generate(
        self,
        topic: str,
        context: Dict[str, Any],
        format_type: str = 'detailed'  # detailed, quick, step_by_step, visual
    ) -> Dict[str, Any]:
        """
        Generate AI-powered example

        Args:
            topic: What to generate example for
            context: User's specific context
            format_type: How to format example

        Returns:
            Complete example with metadata
        """

        logger.info(f"🎨 Generating example: {topic} for {context.get('industry')}")

        # Get real data from collective intelligence
        real_data = await self._get_real_data(topic, context)

        # Generate example using AI
        example_content = await self._generate_example_content(
            topic=topic,
            context=context,
            real_data=real_data,
            format_type=format_type
        )

        # Add interactive elements
        interactive_elements = await self._generate_interactive_elements(
            topic=topic,
            example_content=example_content
        )

        # Generate explanation
        explanation = await self._generate_explanation(
            topic=topic,
            example_content=example_content,
            context=context
        )

        return {
            'topic': topic,
            'content': example_content,
            'explanation': explanation,
            'interactive_elements': interactive_elements,
            'metadata': {
                'generated_at': datetime.utcnow().isoformat(),
                'based_on_real_data': True,
                'source_count': real_data.get('source_count', 0),
                'personalized_for': context,
                'format': format_type
            },
            'related_examples': await self._get_related_examples(topic, context)
        }

    async def _get_real_data(
        self,
        topic: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Get real data from collective intelligence

        Ensures examples are based on actual successful cases
        """

        # Map topic to problem type
        problem_type = self._topic_to_problem_type(topic)

        # Query collective intelligence
        wisdom = await self.collective.query_collective_wisdom(
            problem_type=problem_type,
            org_context=context,
            min_cases=3
        )

        return wisdom

    async def _generate_example_content(
        self,
        topic: str,
        context: Dict[str, Any],
        real_data: Dict[str, Any],
        format_type: str
    ) -> str:
        """
        Generate example content using AI

        Combines:
        - Topic template
        - User context
        - Real data from collective intelligence
        - AI creativity
        """

        # Build comprehensive prompt
        prompt = self._build_generation_prompt(
            topic=topic,
            context=context,
            real_data=real_data,
            format_type=format_type
        )

        # AI generates example
        example = await self.ai.generate(
            prompt=prompt,
            temperature=0.5,  # Balanced creativity
            max_tokens=2500
        )

        return example

    def _build_generation_prompt(
        self,
        topic: str,
        context: Dict[str, Any],
        real_data: Dict[str, Any],
        format_type: str
    ) -> str:
        """Build AI prompt for example generation"""

        # Extract relevant data
        patterns = real_data.get('patterns', {})
        timeline = real_data.get('timeline', {})
        challenges = real_data.get('common_challenges', [])
        success_factors = real_data.get('success_factors', [])

        prompt = f"""Generate a complete, realistic example for: {topic}

CONTEXT:
- Industry: {context.get('industry')}
- Organization type: {context.get('org_type')}
- Size: {context.get('org_size', 'medium')}
- Specific area: {context.get('specific_area', 'general')}

REAL DATA TO USE:
Based on {real_data.get('privacy', {}).get('source_count', 0)} similar organizations:

Patterns observed:
{self._format_patterns(patterns)}

Typical timeline:
{self._format_timeline(timeline)}

Common challenges:
{self._format_list(challenges)}

Success factors:
{self._format_list(success_factors)}

FORMAT: {format_type}
{self._get_format_instructions(format_type)}

REQUIREMENTS:
1. Make it REALISTIC - use real data above
2. Make it SPECIFIC - for {context.get('industry')} {context.get('org_type')}
3. Make it COMPLETE - full example, not partial
4. Make it PRACTICAL - actionable, not theoretical
5. Include NUMBERS - specific values, timelines, counts

Example should feel like it came from a real {context.get('industry')} {context.get('org_type')}.

GENERATED EXAMPLE:
"""

        return prompt

    def _get_format_instructions(self, format_type: str) -> str:
        """Get format-specific instructions"""

        instructions = {
            'detailed': """
Provide comprehensive example with:
- Overview
- Step-by-step process
- Specific data/numbers
- Challenges encountered
- Solutions implemented
- Results achieved
""",
            'quick': """
Provide concise example with:
- Key points only
- Essential data
- Main outcome
- 3-5 bullet points max
""",
            'step_by_step': """
Provide numbered steps with:
- What to do
- Example of doing it
- Expected result
- Next step
""",
            'visual': """
Provide example optimized for diagrams:
- Clear structure
- Relationships
- Flow/sequence
- Components
"""
        }

        return instructions.get(format_type, instructions['detailed'])

    async def _generate_interactive_elements(
        self,
        topic: str,
        example_content: str
    ) -> List[Dict[str, Any]]:
        """
        Generate interactive elements for example

        E.g., "Try it yourself", "Customize this", "Calculate for your org"
        """

        elements = []

        # Topic-specific interactive elements
        if 'rto' in topic.lower() or 'calculation' in topic.lower():
            elements.append({
                'type': 'calculator',
                'title': 'Calculate Your Own RTO',
                'description': 'Use this example as template for your calculations',
                'action': 'open_rto_calculator',
                'pre_filled': True  # Pre-fill with example values
            })

        if 'process' in topic.lower() or 'identification' in topic.lower():
            elements.append({
                'type': 'wizard',
                'title': 'Identify Your Processes',
                'description': 'Follow same approach for your organization',
                'action': 'start_process_wizard',
                'based_on_example': True
            })

        if 'dependency' in topic.lower() or 'mapping' in topic.lower():
            elements.append({
                'type': 'diagram_tool',
                'title': 'Map Your Dependencies',
                'description': 'Create similar dependency map',
                'action': 'open_dependency_mapper',
                'example_template': True
            })

        # Always add "customize" option
        elements.append({
            'type': 'customizer',
            'title': 'Customize This Example',
            'description': 'Adapt this example to your specific situation',
            'action': 'customize_example',
            'example_id': self._generate_example_id(topic)
        })

        return elements

    async def _generate_explanation(
        self,
        topic: str,
        example_content: str,
        context: Dict[str, Any]
    ) -> str:
        """
        Generate explanation of the example

        Helps user understand WHY things are done this way
        """

        prompt = f"""Explain this example:

{example_content}

Context: {context.get('industry')} {context.get('org_type')}

Provide clear explanation:
1. Why this approach was chosen
2. Key decisions and rationale
3. What to adapt for different situations
4. Common mistakes to avoid

Keep it practical and insightful.

EXPLANATION:
"""

        explanation = await self.ai.generate(
            prompt=prompt,
            temperature=0.3,
            max_tokens=800
        )

        return explanation

    async def _get_related_examples(
        self,
        topic: str,
        context: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """Get related examples user might find helpful"""

        related = []

        # Topic-based relations
        relations = {
            'bia_process_identification': [
                'bia_impact_analysis',
                'bia_dependency_mapping',
                'rto_calculation'
            ],
            'rto_calculation': [
                'rpo_determination',
                'recovery_strategy',
                'bia_process_identification'
            ],
            'dependency_mapping': [
                'bia_process_identification',
                'supplier_risk_assessment',
                'recovery_strategy'
            ]
        }

        related_topics = relations.get(topic, [])

        for related_topic in related_topics[:3]:
            related.append({
                'topic': related_topic,
                'title': related_topic.replace('_', ' ').title(),
                'description': f"See example for {related_topic.replace('_', ' ')}",
                'action': f'generate_example:{related_topic}'
            })

        return related

    def _format_patterns(self, patterns: Dict) -> str:
        """Format patterns for prompt"""
        lines = []
        for name, data in patterns.items():
            lines.append(
                f"• {name.replace('_', ' ').title()}: "
                f"{data.get('frequency', 'N/A')} "
                f"(confidence: {data.get('confidence', 0):.0%})"
            )
        return "\n".join(lines) if lines else "No specific patterns"

    def _format_timeline(self, timeline: Dict) -> str:
        """Format timeline for prompt"""
        if not timeline:
            return "Timeline not available"

        return (
            f"• Median: {timeline.get('median_days', 'N/A')} days\n"
            f"• Range: {timeline.get('range', 'N/A')}"
        )

    def _format_list(self, items: List[str]) -> str:
        """Format list for prompt"""
        if not items:
            return "None specified"
        return "\n".join(f"• {item}" for item in items)

    def _topic_to_problem_type(self, topic: str) -> str:
        """Map topic to problem type for collective intelligence"""

        mapping = {
            'bia_process_identification': 'critical_process_prioritization',
            'bia_impact_analysis': 'impact_assessment',
            'dependency_mapping': 'supply_chain_complexity',
            'rto_calculation': 'rto_determination',
            'rpo_determination': 'rpo_calculation',
            'recovery_strategy': 'recovery_planning',
            'risk_assessment': 'risk_identification'
        }

        return mapping.get(topic, 'general_bcm_challenge')

    def _generate_example_id(self, topic: str) -> str:
        """Generate unique example ID"""
        import hashlib
        return hashlib.md5(f"{topic}{datetime.utcnow()}".encode()).hexdigest()[:12]


class ExampleLibrary:
    """
    Library of generated examples

    Stores and indexes all AI-generated examples
    """

    def __init__(self, db, generator: AIExampleGenerator):
        self.db = db
        self.generator = generator

    async def get_or_generate(
        self,
        topic: str,
        context: Dict[str, Any],
        force_regenerate: bool = False
    ) -> Dict[str, Any]:
        """
        Get example from library or generate new one

        Caching strategy:
        - Check if similar example exists
        - If exists and good quality → return it
        - If doesn't exist or force_regenerate → generate new
        """

        if not force_regenerate:
            # Try to find existing example
            existing = await self._find_similar_example(topic, context)
            if existing:
                logger.info(f"📚 Returning cached example for {topic}")
                return existing

        # Generate new example
        logger.info(f"🎨 Generating new example for {topic}")
        example = await self.generator.generate(topic, context)

        # Store in library
        await self._store_example(example)

        return example

    async def _find_similar_example(
        self,
        topic: str,
        context: Dict[str, Any]
    ) -> Optional[Dict]:
        """Find similar cached example"""

        # Query database for similar examples
        # Match on: topic + industry + org_type
        # Placeholder
        return None

    async def _store_example(self, example: Dict):
        """Store example in library"""
        # Save to database
        # Placeholder
        logger.info(f"💾 Example stored: {example['topic']}")


class InteractiveExampleRunner:
    """
    Runs interactive examples

    User can customize and execute examples
    """

    def __init__(self, example_generator: AIExampleGenerator):
        self.generator = example_generator

    async def customize_and_run(
        self,
        example: Dict[str, Any],
        user_inputs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Customize example with user's data and run it

        Example:
        User has RTO example for hospital ER
        Wants to customize for their clinic pharmacy

        Result: AI adapts example with their inputs
        """

        # Extract original context
        original_context = example['metadata']['personalized_for']

        # Merge with user inputs
        new_context = {**original_context, **user_inputs}

        # Regenerate with new context
        customized = await self.generator.generate(
            topic=example['topic'],
            context=new_context,
            format_type=example['metadata']['format']
        )

        # Add customization metadata
        customized['customized_from'] = example['metadata']['generated_at']
        customized['user_customizations'] = user_inputs

        return customized

    async def try_yourself(
        self,
        example: Dict[str, Any],
        user_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        "Try it yourself" - apply example to user's actual data

        Example:
        RTO calculation example shown
        User clicks "Calculate mine"
        System pre-fills calculator with example values
        User adjusts for their situation
        Gets their own RTO
        """

        # Extract key parameters from example
        parameters = self._extract_parameters(example['content'])

        # Pre-fill with example values
        prefilled_tool = {
            'tool_type': self._detect_tool_type(example['topic']),
            'prefilled_values': parameters,
            'user_data': user_data,
            'instructions': f"This calculator is pre-filled with values from the example. Adjust them for your situation."
        }

        return prefilled_tool

    def _extract_parameters(self, content: str) -> Dict[str, Any]:
        """Extract key parameters from example content"""
        # Simple extraction - in production use NLP
        # Placeholder
        return {
            'process_name': 'Emergency Department',
            'rto_hours': 2,
            'impact_level': 'critical'
        }

    def _detect_tool_type(self, topic: str) -> str:
        """Detect which tool to use for topic"""
        if 'rto' in topic.lower():
            return 'rto_calculator'
        elif 'process' in topic.lower():
            return 'process_identifier'
        elif 'dependency' in topic.lower():
            return 'dependency_mapper'
        else:
            return 'generic_tool'
