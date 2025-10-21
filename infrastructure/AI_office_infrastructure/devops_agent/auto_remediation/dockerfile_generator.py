#!/usr/bin/env python3
"""
Dockerfile Generator - AI-powered Dockerfile generation

Uses RAG + LLM to generate production-ready Dockerfiles for services
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional
import sys

# Add project root and ai-foundation to path
project_root = Path(__file__).parents[3]
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "intelligent-core" / "ai-foundation"))

# Now can import directly (Python sees ai-foundation as package)
from rag.pipeline import RAGPipeline
from llm.llm_router import LLMRouter

logger = logging.getLogger(__name__)


class DockerfileGenerator:
    """
    AI-powered Dockerfile Generator

    Uses RAG to retrieve similar Dockerfile patterns
    Uses LLM to generate optimized Dockerfiles
    """

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.llm: Optional[LLMRouter] = None
        self.rag: Optional[RAGPipeline] = None

    async def initialize(self):
        """Initialize AI components"""
        try:
            self.llm = LLMRouter()
            logger.info(" LLM Router initialized for Dockerfile generation")

            self.rag = RAGPipeline()
            logger.info(" RAG Pipeline initialized for Dockerfile patterns")

        except Exception as e:
            logger.error(f" Failed to initialize AI components: {e}")
            raise

    async def generate(self, action: Dict) -> Dict:
        """
        Generate Dockerfile for service using AI

        Args:
            action: Fix action with service metadata

        Returns:
            Generation result
        """

        service_metadata = action.get("service_metadata", {})
        service_name = service_metadata.get("name", "unknown_service")

        logger.info(f" Generating Dockerfile for {service_name}...")

        if not self.llm:
            await self.initialize()

        #  STEP 1: Retrieve similar Dockerfile patterns from RAG
        similar_patterns = []

        if self.rag:
            search_query = f"dockerfile for {service_metadata.get('language', 'python')} {service_metadata.get('framework', '')} service"

            try:
                similar_patterns = await self.rag.retrieve(
                    query=search_query,
                    context={
                        "language": service_metadata.get('language'),
                        "framework": service_metadata.get('framework', 'unknown')
                    },
                    top_k=3,
                    filters={"source_type": "dockerfile_patterns"},
                    enable_reranking=True
                )

                logger.info(f" Retrieved {len(similar_patterns)} similar Dockerfile patterns")

            except Exception as e:
                logger.warning(f"Failed to retrieve patterns from RAG: {e}")

        #  STEP 2: Generate Dockerfile using LLM
        if not self.llm:
            return {
                "success": False,
                "error": "LLM not available"
            }

        # Build context for LLM
        patterns_context = self._format_patterns(similar_patterns)

        dockerfile_prompt = f"""
        Generate a production-ready Dockerfile for the following service:

        === SERVICE DETAILS ===
        Service Name: {service_metadata.get('name', 'unknown')}
        Language: {service_metadata.get('language', 'python')}
        Framework: {service_metadata.get('framework', 'fastapi')}
        Dependencies: {', '.join(service_metadata.get('dependencies', []))}
        Port: {service_metadata.get('port', 8000)}

        === SIMILAR DOCKERFILE PATTERNS (from knowledge base) ===
        {patterns_context}

        === REQUIREMENTS ===
        1. Multi-stage build (builder + runtime stages)
        2. Security best practices:
           - Run as non-root user
           - Minimal base image (alpine or slim)
           - No unnecessary packages
        3. Health check endpoint
        4. Optimized layer caching
        5. Production-ready setup

        === OUTPUT FORMAT ===
        Return ONLY the Dockerfile content, no explanations.
        Start with "FROM" and end with HEALTHCHECK or CMD.
        """

        try:
            dockerfile_content = await self.llm.query(
                system_prompt="""You are a Docker expert specializing in production-ready containers.
                Generate secure, optimized Dockerfiles following best practices.
                Always use multi-stage builds and security hardening.""",
                user_prompt=dockerfile_prompt,
                task_type="content_generation",
                temperature=0.2,  # Low temperature for consistent Dockerfiles
                max_tokens=1500
            )

            #  STEP 3: Save generated Dockerfile
            service_path = service_metadata.get("path", "")
            if service_path:
                dockerfile_path = self.project_root / service_path / "Dockerfile"

                # Create directory if needed
                dockerfile_path.parent.mkdir(parents=True, exist_ok=True)

                # Write Dockerfile
                dockerfile_path.write_text(dockerfile_content)

                logger.info(f" Dockerfile saved: {dockerfile_path}")

                #  STEP 4: Store this pattern in RAG for future use
                if self.rag:
                    await self._store_dockerfile_pattern(
                        service_metadata=service_metadata,
                        dockerfile_content=dockerfile_content
                    )

                return {
                    "success": True,
                    "path": str(dockerfile_path),
                    "content": dockerfile_content,
                    "outcome": f"Generated Dockerfile for {service_name}"
                }

            else:
                return {
                    "success": False,
                    "error": "Service path not provided in metadata"
                }

        except Exception as e:
            logger.error(f" Dockerfile generation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def _format_patterns(self, patterns: List[Dict]) -> str:
        """Format similar patterns for LLM context"""

        if not patterns:
            return "No similar patterns found in knowledge base."

        formatted = []
        for i, pattern in enumerate(patterns, 1):
            formatted.append(f"""
            Pattern {i} (Relevance: {pattern.get('score', 0.0):.2f}):
            {pattern.get('content', '')}
            """)

        return "\n".join(formatted)

    async def _store_dockerfile_pattern(self, service_metadata: Dict, dockerfile_content: str):
        """Store generated Dockerfile pattern in RAG for future reference"""

        if not self.rag:
            return

        pattern_text = f"""
        DOCKERFILE PATTERN

        Language: {service_metadata.get('language', 'unknown')}
        Framework: {service_metadata.get('framework', 'unknown')}

        Dockerfile:
        {dockerfile_content}

        Features:
        - Multi-stage build
        - Security hardened
        - Health check included
        - Optimized for production
        """

        try:
            await self.rag.ingest_documents(
                documents=[{
                    "text": pattern_text,
                    "metadata": {
                        "source_type": "dockerfile_patterns",
                        "language": service_metadata.get('language'),
                        "framework": service_metadata.get('framework'),
                        "service_name": service_metadata.get('name'),
                        "success": True
                    }
                }],
                source_type="dockerfile_patterns"
            )

            logger.info(f" Dockerfile pattern stored in RAG: {service_metadata.get('language')}/{service_metadata.get('framework')}")

        except Exception as e:
            logger.warning(f"Failed to store Dockerfile pattern in RAG: {e}")

    async def generate_for_service(self, service_name: str, service_path: str, language: str = "python", framework: str = "fastapi", port: int = 8000) -> Dict:
        """
        Convenience method to generate Dockerfile for a service

        Args:
            service_name: Name of the service
            service_path: Path to service directory (relative to project root)
            language: Programming language
            framework: Framework name
            port: Service port

        Returns:
            Generation result
        """

        action = {
            "category": "missing_dockerfile",
            "service_metadata": {
                "name": service_name,
                "path": service_path,
                "language": language,
                "framework": framework,
                "port": port,
                "dependencies": []
            }
        }

        return await self.generate(action)


# CLI for standalone usage
if __name__ == "__main__":
    import asyncio
    import argparse

    async def main():
        parser = argparse.ArgumentParser(description="AI-powered Dockerfile Generator")
        parser.add_argument("--service-name", required=True, help="Service name")
        parser.add_argument("--service-path", required=True, help="Service path (relative to project root)")
        parser.add_argument("--language", default="python", help="Programming language")
        parser.add_argument("--framework", default="fastapi", help="Framework")
        parser.add_argument("--port", type=int, default=8000, help="Service port")
        parser.add_argument("--project-root", default="/Users/MD/AI-Platform-ISO", help="Project root")

        args = parser.parse_args()

        generator = DockerfileGenerator(args.project_root)
        await generator.initialize()

        result = await generator.generate_for_service(
            service_name=args.service_name,
            service_path=args.service_path,
            language=args.language,
            framework=args.framework,
            port=args.port
        )

        if result["success"]:
            print(f" Dockerfile generated successfully!")
            print(f" Location: {result['path']}")
            print(f"\n{result['content']}")
        else:
            print(f" Failed to generate Dockerfile: {result.get('error')}")

    asyncio.run(main())
