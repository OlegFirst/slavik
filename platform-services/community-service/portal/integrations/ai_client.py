"""
AI Orchestrator Integration
Handles AI content generation for articles and scenarios
"""

import os
from typing import Optional
import httpx
from fastapi import HTTPException


class AIClient:
    """
    HTTP client for AI Orchestrator

    Responsibilities:
    - Generate knowledge articles from exercise data
    - Generate new scenarios from prompts
    - Enhance article content
    """

    def __init__(self):
        self.base_url = os.getenv("AI_ORCHESTRATOR_URL", "http://localhost:8000")
        self.timeout = 60.0  # Longer timeout for AI generation

    async def generate_article_from_exercise(
        self,
        exercise_data: dict,
        insights_data: dict,
        token: str
    ) -> dict:
        """
        Generate knowledge article from exercise results

        Args:
            exercise_data: Exercise basic info (name, type, objectives)
            insights_data: Exercise insights (lessons learned, findings, metrics)
            token: JWT token for authorization

        Returns:
            dict with:
            - title: Generated article title
            - summary: Article summary
            - content: Full article content (Markdown)
            - confidence_score: AI confidence (0.0-1.0)
            - suggested_tags: List of suggested tags
            - suggested_category: Suggested category

        Raises:
            HTTPException if generation fails
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                payload = {
                    "content_type": "knowledge_article",
                    "template": "exercise_insights",
                    "source_data": {
                        "exercise": exercise_data,
                        "insights": insights_data
                    }
                }

                response = await client.post(
                    f"{self.base_url}/api/ai/generate-content",
                    json=payload,
                    headers={"Authorization": f"Bearer {token}"}
                )

                response.raise_for_status()
                return response.json()

            except httpx.HTTPStatusError as e:
                raise HTTPException(
                    status_code=e.response.status_code,
                    detail=f"AI generation failed: {e.response.text}"
                )
            except httpx.RequestError:
                raise HTTPException(
                    status_code=503,
                    detail="AI Orchestrator unavailable"
                )

    async def generate_scenario(
        self,
        prompt: str,
        scenario_type: str,
        industry: Optional[str],
        threat_type: Optional[str],
        token: str
    ) -> dict:
        """
        Generate new scenario from user prompt

        Args:
            prompt: User prompt describing desired scenario
            scenario_type: Type of scenario (tabletop, functional, full_scale)
            industry: Target industry (optional)
            threat_type: Type of threat (optional)
            token: JWT token for authorization

        Returns:
            dict with:
            - scenario_name: Generated name
            - description: Scenario description
            - full_scenario: Complete scenario text
            - injects: List of inject objects
            - learning_objectives: List of objectives
            - confidence_score: AI confidence (0.0-1.0)

        Raises:
            HTTPException if generation fails
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                payload = {
                    "content_type": "scenario",
                    "template": "exercise_scenario",
                    "parameters": {
                        "prompt": prompt,
                        "scenario_type": scenario_type,
                        "industry": industry,
                        "threat_type": threat_type
                    }
                }

                response = await client.post(
                    f"{self.base_url}/api/ai/generate-content",
                    json=payload,
                    headers={"Authorization": f"Bearer {token}"}
                )

                response.raise_for_status()
                return response.json()

            except httpx.HTTPStatusError as e:
                raise HTTPException(
                    status_code=e.response.status_code,
                    detail=f"Scenario generation failed: {e.response.text}"
                )
            except httpx.RequestError:
                raise HTTPException(
                    status_code=503,
                    detail="AI Orchestrator unavailable"
                )

    async def enhance_article_content(
        self,
        content: str,
        enhancement_type: str,
        token: str
    ) -> dict:
        """
        Enhance existing article content

        Args:
            content: Original article content
            enhancement_type: Type of enhancement (grammar, clarity, structure, seo)
            token: JWT token for authorization

        Returns:
            dict with:
            - enhanced_content: Improved content
            - changes_summary: Summary of changes made

        Raises:
            HTTPException if enhancement fails
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                payload = {
                    "content_type": "article_enhancement",
                    "template": enhancement_type,
                    "source_data": {
                        "original_content": content
                    }
                }

                response = await client.post(
                    f"{self.base_url}/api/ai/generate-content",
                    json=payload,
                    headers={"Authorization": f"Bearer {token}"}
                )

                response.raise_for_status()
                return response.json()

            except httpx.HTTPStatusError as e:
                raise HTTPException(
                    status_code=e.response.status_code,
                    detail=f"Content enhancement failed: {e.response.text}"
                )
            except httpx.RequestError:
                raise HTTPException(
                    status_code=503,
                    detail="AI Orchestrator unavailable"
                )
