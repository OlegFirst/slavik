"""
AI Service using Claude API
"""

import json
from typing import Optional, Dict, Any, List
from anthropic import Anthropic
from config import get_settings
from database import DatabaseClient


class AIService:
    """AI service for Claude API integration"""

    def __init__(self):
        settings = get_settings()
        self.client = Anthropic(api_key=settings.anthropic_api_key)
        self.model = settings.claude_model
        self.db = DatabaseClient()

    async def execute_prompt(
        self,
        prompt_name: str,
        variables: Dict[str, Any],
        user_id: Optional[str] = None,
        organization_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute an AI prompt

        Args:
            prompt_name: Name of the prompt template
            variables: Variables to substitute in template
            user_id: User ID for logging
            organization_id: Organization ID for logging

        Returns:
            AI response as dict
        """
        # Get prompt template
        prompt_template = await self.db.get_ai_prompt(prompt_name)
        if not prompt_template:
            raise ValueError(f"Prompt template '{prompt_name}' not found")

        # Substitute variables in template
        prompt_text = prompt_template["template"]
        for key, value in variables.items():
            placeholder = f"{{{key}}}"
            prompt_text = prompt_text.replace(placeholder, str(value))

        # Call Claude API
        start_time = None
        try:
            import time
            start_time = time.time()

            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                messages=[
                    {"role": "user", "content": prompt_text}
                ]
            )

            execution_time_ms = int((time.time() - start_time) * 1000)

            # Extract response text
            response_text = response.content[0].text

            # Try to parse as JSON
            try:
                response_data = json.loads(response_text)
            except json.JSONDecodeError:
                response_data = {"text": response_text}

            # Log usage
            await self.db.log_ai_usage({
                "user_id": user_id,
                "organization_id": organization_id,
                "prompt_name": prompt_name,
                "model": self.model,
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
                "execution_time_ms": execution_time_ms
            })

            return {
                "success": True,
                "data": response_data,
                "tokens_used": response.usage.input_tokens + response.usage.output_tokens,
                "execution_time_ms": execution_time_ms
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    async def generate_processes_for_industry(
        self,
        industry: str,
        size: int,
        country: str = "United States",
        user_id: Optional[str] = None,
        organization_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate business processes for an industry

        Returns:
            List of process suggestions
        """
        result = await self.execute_prompt(
            prompt_name="generate_processes_for_industry",
            variables={
                "industry": industry,
                "size": size,
                "country": country
            },
            user_id=user_id,
            organization_id=organization_id
        )

        if not result["success"]:
            raise Exception(f"AI generation failed: {result.get('error')}")

        # Return processes array
        data = result["data"]
        if isinstance(data, list):
            return data
        elif isinstance(data, dict) and "processes" in data:
            return data["processes"]
        else:
            return []

    async def calculate_process_rto(
        self,
        process_name: str,
        process_description: str,
        industry: str,
        criticality: str,
        user_id: Optional[str] = None,
        organization_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Calculate RTO/RPO for a process using AI

        Returns:
            RTO/RPO recommendations
        """
        result = await self.execute_prompt(
            prompt_name="calculate_process_rto",
            variables={
                "process_name": process_name,
                "process_description": process_description or "No description provided",
                "industry": industry,
                "criticality": criticality
            },
            user_id=user_id,
            organization_id=organization_id
        )

        if not result["success"]:
            raise Exception(f"AI calculation failed: {result.get('error')}")

        return result["data"]

    async def analyze_bia_questionnaire(
        self,
        responses: Dict[str, Any],
        user_id: Optional[str] = None,
        organization_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze BIA questionnaire responses using AI

        Returns:
            Analysis results with processes, dependencies, and findings
        """
        result = await self.execute_prompt(
            prompt_name="analyze_bia_questionnaire",
            variables={
                "responses": json.dumps(responses, indent=2)
            },
            user_id=user_id,
            organization_id=organization_id
        )

        if not result["success"]:
            raise Exception(f"AI analysis failed: {result.get('error')}")

        return result["data"]
