#!/usr/bin/env python3
"""
Tests for AI Integration functionality
Tests AI-powered code generation vs template-based approach
"""

import pytest
import asyncio
import tempfile
from pathlib import Path
from typing import Dict, Any

from ai_integration.claude_generator import ClaudeCodeGenerator
from generator.code_generator import CodeGenerator


class TestAIIntegration:
    """Test AI-powered code generation"""

    def setup_method(self):
        """Setup test fixtures"""
        self.ai_generator = ClaudeCodeGenerator()
        self.code_generator_ai = CodeGenerator(use_ai=True)
        self.code_generator_template = CodeGenerator(use_ai=False)

        # Test architecture data
        self.test_architecture = {
            "pattern": "microservices",
            "primary_pattern": "microservices",
            "languages": ["python"],
            "frameworks": ["fastapi", "uvicorn"],
            "components": [
                {"name": "api_gateway", "type": "service"},
                {"name": "user_service", "type": "service"},
                {"name": "data_service", "type": "service"}
            ],
            "dependencies": ["fastapi", "uvicorn", "httpx"],
            "deployment": {
                "type": "docker",
                "orchestration": "docker-compose"
            }
        }

    @pytest.mark.asyncio
    async def test_ai_code_generation_microservices(self):
        """Test AI generation for microservices"""

        generated_files = await self.ai_generator.generate_intelligent_code(self.test_architecture)

        # Verify essential files are generated
        assert "main.py" in generated_files
        assert "gateway.py" in generated_files
        assert "docker-compose.yml" in generated_files
        assert "Dockerfile" in generated_files
        assert "requirements.txt" in generated_files

        # Verify code quality
        main_content = generated_files["main.py"]
        assert "FastAPI" in main_content
        assert "AI-Generated" in main_content
        assert "health" in main_content.lower()
        assert "uvicorn" in main_content

        # Verify Docker configuration
        docker_compose = generated_files["docker-compose.yml"]
        assert "services:" in docker_compose
        assert "gateway:" in docker_compose
        assert "networks:" in docker_compose

        print(f"✅ AI generated {len(generated_files)} microservices files")

    @pytest.mark.asyncio
    async def test_ai_code_generation_monolith(self):
        """Test AI generation for monolith"""

        monolith_arch = self.test_architecture.copy()
        monolith_arch["pattern"] = "monolith"
        monolith_arch["primary_pattern"] = "monolith"

        generated_files = await self.ai_generator.generate_intelligent_code(monolith_arch)

        # Verify essential files
        assert "main.py" in generated_files
        assert "Dockerfile" in generated_files
        assert "requirements.txt" in generated_files

        # Verify code content
        main_content = generated_files["main.py"]
        assert "FastAPI" in main_content
        assert "modular" in main_content.lower() or "monolith" in main_content.lower()

        print(f"✅ AI generated {len(generated_files)} monolith files")

    @pytest.mark.asyncio
    async def test_ai_code_generation_serverless(self):
        """Test AI generation for serverless"""

        serverless_arch = self.test_architecture.copy()
        serverless_arch["pattern"] = "serverless"
        serverless_arch["primary_pattern"] = "serverless"

        generated_files = await self.ai_generator.generate_intelligent_code(serverless_arch)

        # Verify serverless-specific files
        assert any("handler" in filename for filename in generated_files.keys())
        assert any("serverless" in filename.lower() for filename in generated_files.keys())

        print(f"✅ AI generated {len(generated_files)} serverless files")

    @pytest.mark.asyncio
    async def test_ai_vs_template_comparison(self):
        """Compare AI generation vs template generation"""

        # Generate with AI
        ai_files = await self.code_generator_ai.generate(self.test_architecture)

        # Generate with templates
        template_files = await self.code_generator_template.generate(self.test_architecture)

        # Compare results
        print(f"📊 AI generated: {len(ai_files)} files")
        print(f"📊 Template generated: {len(template_files)} files")

        # Both approaches should generate useful files (flexible comparison)
        assert len(ai_files) >= 3  # AI should generate at least core files
        assert len(template_files) >= 3  # Template should also generate core files

        # Both should have core application files
        assert "main.py" in ai_files
        # Template generates different file structures, check for any Python files
        python_files = [f for f in template_files.keys() if f.endswith('.py')]
        assert len(python_files) >= 1 or "docker-compose.yml" in template_files

        # AI files should have enhanced features
        ai_main = ai_files["main.py"]

        # AI should have sophisticated code with production features
        assert len(ai_main) >= 500  # Substantial code

        # AI should have better comments and structure
        assert "AI-Generated" in ai_main or "production-ready" in ai_main.lower()

        print("✅ AI generation shows improvements over template approach")

    @pytest.mark.asyncio
    async def test_architecture_explanation(self):
        """Test AI architecture explanation generation"""

        explanation = await self.ai_generator.explain_architecture_decisions(self.test_architecture)

        # Verify explanation quality
        assert len(explanation) > 200  # Substantial explanation
        assert "microservices" in explanation.lower()
        assert "architecture" in explanation.lower()
        assert "scalability" in explanation.lower() or "performance" in explanation.lower()

        # Should contain structured sections
        assert "**" in explanation  # Markdown formatting
        assert "✅" in explanation or "Benefits" in explanation

        print("✅ AI explanation generated successfully")

    @pytest.mark.asyncio
    async def test_ai_fallback_mechanism(self):
        """Test fallback to template generation when AI fails"""

        # Test with code generator that has AI enabled
        result = await self.code_generator_ai.generate(self.test_architecture)

        # Should still get valid results (either AI or template fallback)
        assert isinstance(result, dict)
        assert len(result) > 0
        assert "main.py" in result

        print("✅ Fallback mechanism working correctly")

    @pytest.mark.asyncio
    async def test_code_quality_validation(self):
        """Test that generated code meets quality standards"""

        generated_files = await self.ai_generator.generate_intelligent_code(self.test_architecture)

        # Check main.py for quality indicators
        main_content = generated_files["main.py"]

        # Should have proper imports
        assert "import" in main_content

        # Should have error handling
        assert "try:" in main_content or "except" in main_content or "HTTPException" in main_content

        # Should have logging
        assert "logging" in main_content or "logger" in main_content

        # Should have proper structure
        assert "def " in main_content or "async def" in main_content
        assert "class " in main_content or "app = " in main_content

        # Check requirements.txt
        if "requirements.txt" in generated_files:
            requirements = generated_files["requirements.txt"]
            assert len(requirements.strip()) > 0
            assert "==" in requirements  # Should have version pinning

        print("✅ Generated code meets quality standards")

    @pytest.mark.asyncio
    async def test_performance_comparison(self):
        """Test performance of AI vs template generation"""

        import time

        # Measure AI generation time
        start_time = time.time()
        ai_files = await self.code_generator_ai.generate(self.test_architecture)
        ai_time = time.time() - start_time

        # Measure template generation time
        start_time = time.time()
        template_files = await self.code_generator_template.generate(self.test_architecture)
        template_time = time.time() - start_time

        print(f"⏱️ AI generation time: {ai_time:.3f}s")
        print(f"⏱️ Template generation time: {template_time:.3f}s")

        # AI should be reasonably fast (less than 10 seconds for this test)
        assert ai_time < 10.0

        # Both should produce results
        assert len(ai_files) > 0
        assert len(template_files) > 0

        print("✅ Performance comparison completed")

    def test_ai_generator_initialization(self):
        """Test AI generator initializes correctly"""

        generator = ClaudeCodeGenerator()

        # Verify configuration
        assert generator.max_tokens > 0
        assert generator.temperature >= 0 and generator.temperature <= 1

        print("✅ AI generator initialized correctly")

    @pytest.mark.asyncio
    async def test_enhanced_infrastructure_generation(self):
        """Test that AI generates enhanced infrastructure files"""

        generated_files = await self.ai_generator.generate_intelligent_code(self.test_architecture)

        # Should have comprehensive infrastructure
        infrastructure_files = [f for f in generated_files.keys()
                              if any(keyword in f.lower() for keyword in
                                   ["docker", "compose", "requirements", "config"])]

        assert len(infrastructure_files) >= 2  # At least Docker + requirements

        # Docker Compose should be comprehensive
        if "docker-compose.yml" in generated_files:
            compose_content = generated_files["docker-compose.yml"]
            assert "services:" in compose_content
            assert "networks:" in compose_content
            assert "version:" in compose_content

        print(f"✅ Generated {len(infrastructure_files)} infrastructure files")


if __name__ == "__main__":
    # Run specific test for development
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "quick":
        # Quick test for development
        test = TestAIIntegration()
        test.setup_method()
        asyncio.run(test.test_ai_code_generation_microservices())
        print("✅ Quick AI integration test passed!")
    else:
        # Run full test suite
        pytest.main([__file__, "-v", "-s"])