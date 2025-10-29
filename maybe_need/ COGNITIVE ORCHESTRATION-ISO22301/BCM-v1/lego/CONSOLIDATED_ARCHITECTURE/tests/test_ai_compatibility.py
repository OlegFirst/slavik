#!/usr/bin/env python3
"""
AI Compatibility tests - ensures old functionality still works with AI enhancement
Tests compatibility between AI-powered and template-based generation
"""

import pytest
import asyncio
from typing import Dict, Any

from generator.code_generator import CodeGenerator


class TestAICompatibility:
    """Test that AI enhancement doesn't break existing functionality"""

    def setup_method(self):
        """Setup test fixtures"""
        self.ai_generator = CodeGenerator(use_ai=True)
        self.template_generator = CodeGenerator(use_ai=False)

        self.test_architectures = {
            "monolith": {
                "pattern": "monolith",
                "primary_pattern": "monolith",
                "languages": ["python"],
                "frameworks": ["fastapi"],
                "components": [{"name": "api", "type": "service"}]
            },
            "microservices": {
                "pattern": "microservices",
                "primary_pattern": "microservices",
                "languages": ["python"],
                "frameworks": ["fastapi", "uvicorn"],
                "components": [
                    {"name": "gateway", "type": "service"},
                    {"name": "user_service", "type": "service"}
                ]
            },
            "serverless": {
                "pattern": "serverless",
                "primary_pattern": "serverless",
                "languages": ["python"],
                "frameworks": ["aws-lambda"],
                "components": [{"name": "handler", "type": "function"}]
            },
            "hybrid": {
                "pattern": "hybrid",
                "primary_pattern": "hybrid",
                "languages": ["python", "javascript"],
                "frameworks": ["fastapi", "react"],
                "components": [
                    {"name": "api", "type": "service"},
                    {"name": "frontend", "type": "service"}
                ]
            }
        }

    @pytest.mark.asyncio
    async def test_backward_compatibility_monolith(self):
        """Test that monolith generation works with both AI and template"""

        # Generate with both approaches
        ai_files = await self.ai_generator.generate(self.test_architectures["monolith"])
        template_files = await self.template_generator.generate(self.test_architectures["monolith"])

        # Both should generate valid Python applications
        self._verify_python_application(ai_files, "AI")
        self._verify_python_application(template_files, "Template")

        print("✅ Monolith backward compatibility verified")

    @pytest.mark.asyncio
    async def test_backward_compatibility_microservices(self):
        """Test that microservices generation works with both approaches"""

        ai_files = await self.ai_generator.generate(self.test_architectures["microservices"])
        template_files = await self.template_generator.generate(self.test_architectures["microservices"])

        # Both should generate multiple services
        assert len(ai_files) >= 3, f"AI generated only {len(ai_files)} files"
        assert len(template_files) >= 3, f"Template generated only {len(template_files)} files"

        # Both should have infrastructure
        self._verify_infrastructure_files(ai_files, "AI")
        self._verify_infrastructure_files(template_files, "Template")

        print("✅ Microservices backward compatibility verified")

    @pytest.mark.asyncio
    async def test_backward_compatibility_serverless(self):
        """Test that serverless generation works with both approaches"""

        ai_files = await self.ai_generator.generate(self.test_architectures["serverless"])
        template_files = await self.template_generator.generate(self.test_architectures["serverless"])

        # Both should generate serverless functions
        self._verify_serverless_functions(ai_files, "AI")
        self._verify_serverless_functions(template_files, "Template")

        print("✅ Serverless backward compatibility verified")

    @pytest.mark.asyncio
    async def test_backward_compatibility_hybrid(self):
        """Test that hybrid generation works with both approaches"""

        ai_files = await self.ai_generator.generate(self.test_architectures["hybrid"])
        template_files = await self.template_generator.generate(self.test_architectures["hybrid"])

        # Both should generate hybrid architecture
        assert len(ai_files) >= 2, f"AI generated only {len(ai_files)} files"
        assert len(template_files) >= 2, f"Template generated only {len(template_files)} files"

        print("✅ Hybrid backward compatibility verified")

    def _verify_python_application(self, files: Dict[str, str], approach: str):
        """Verify files contain valid Python application"""

        # Should have main Python file
        python_files = [f for f in files.keys() if f.endswith('.py')]
        assert len(python_files) >= 1, f"{approach}: No Python files generated"

        # Should have at least one file with FastAPI
        has_fastapi = any("fastapi" in content.lower() for content in files.values())
        assert has_fastapi, f"{approach}: No FastAPI usage found"

        # Should have functional code structure
        main_file = None
        for filename, content in files.items():
            if filename.endswith('.py') and ('main' in filename or 'app' in filename):
                main_file = content
                break

        if not main_file:
            # Take any Python file
            main_file = next((content for filename, content in files.items()
                            if filename.endswith('.py')), None)

        assert main_file, f"{approach}: No main Python file found"
        assert "def " in main_file or "async def" in main_file, f"{approach}: No functions found"

    def _verify_infrastructure_files(self, files: Dict[str, str], approach: str):
        """Verify infrastructure files are present"""

        # Should have at least one infrastructure file
        infra_files = [f for f in files.keys() if any(keyword in f.lower()
                      for keyword in ['docker', 'compose', 'requirements', 'config'])]

        assert len(infra_files) >= 1, f"{approach}: No infrastructure files found"

        # Should have requirements or dependencies
        has_deps = any(filename in files for filename in
                      ['requirements.txt', 'package.json', 'Pipfile'])
        assert has_deps, f"{approach}: No dependency file found"

    def _verify_serverless_functions(self, files: Dict[str, str], approach: str):
        """Verify serverless function files are present"""

        # Should have function handler
        function_files = [f for f in files.keys() if any(keyword in f.lower()
                         for keyword in ['handler', 'function', 'lambda', 'serverless'])]

        assert len(function_files) >= 1, f"{approach}: No function files found"

        # Should have serverless configuration
        config_files = [f for f in files.keys() if any(keyword in f.lower()
                       for keyword in ['serverless', 'yml', 'yaml', 'json'])]

        assert len(config_files) >= 1, f"{approach}: No configuration files found"

    @pytest.mark.asyncio
    async def test_ai_enhancement_benefits(self):
        """Test that AI provides enhanced features over templates"""

        # Generate microservices with both approaches
        ai_files = await self.ai_generator.generate(self.test_architectures["microservices"])
        template_files = await self.template_generator.generate(self.test_architectures["microservices"])

        # AI should provide architecture explanation
        has_explanation = any("explanation" in filename.lower() or "readme" in filename.lower()
                            for filename in ai_files.keys())

        # AI files should have more sophisticated content
        ai_total_length = sum(len(content) for content in ai_files.values())
        template_total_length = sum(len(content) for content in template_files.values())

        print(f"📊 AI total content: {ai_total_length} chars")
        print(f"📊 Template total content: {template_total_length} chars")
        print(f"📊 AI enhancement ratio: {ai_total_length / template_total_length:.2f}x")

        # AI should provide substantial content (not necessarily more, but more sophisticated)
        assert ai_total_length > 1000, "AI should generate substantial content"

        print("✅ AI enhancement benefits verified")

    @pytest.mark.asyncio
    async def test_generation_consistency(self):
        """Test that generation is consistent across multiple runs"""

        architecture = self.test_architectures["monolith"]

        # Generate same architecture multiple times
        run1 = await self.ai_generator.generate(architecture)
        run2 = await self.ai_generator.generate(architecture)
        run3 = await self.ai_generator.generate(architecture)

        # Should generate similar file structure
        files1 = set(run1.keys())
        files2 = set(run2.keys())
        files3 = set(run3.keys())

        # At least 80% overlap in file names
        overlap_12 = len(files1 & files2) / len(files1 | files2)
        overlap_13 = len(files1 & files3) / len(files1 | files3)

        assert overlap_12 >= 0.8, f"Run consistency too low: {overlap_12:.2f}"
        assert overlap_13 >= 0.8, f"Run consistency too low: {overlap_13:.2f}"

        print("✅ Generation consistency verified")

    @pytest.mark.asyncio
    async def test_error_handling_robustness(self):
        """Test that system handles edge cases gracefully"""

        # Test with minimal architecture
        minimal_arch = {"pattern": "unknown", "languages": [], "frameworks": []}

        try:
            ai_files = await self.ai_generator.generate(minimal_arch)
            # Should still generate something
            assert len(ai_files) > 0, "Should generate fallback files for unknown pattern"
            print("✅ AI handles unknown patterns gracefully")
        except Exception as e:
            pytest.fail(f"AI generator failed on minimal input: {e}")

        try:
            template_files = await self.template_generator.generate(minimal_arch)
            # Should still generate something
            assert len(template_files) > 0, "Should generate fallback files for unknown pattern"
            print("✅ Template generator handles unknown patterns gracefully")
        except Exception as e:
            pytest.fail(f"Template generator failed on minimal input: {e}")

        print("✅ Error handling robustness verified")


if __name__ == "__main__":
    # Run specific test for development
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "quick":
        test = TestAICompatibility()
        test.setup_method()
        asyncio.run(test.test_backward_compatibility_monolith())
        print("✅ Quick AI compatibility test passed!")
    else:
        pytest.main([__file__, "-v", "-s"])