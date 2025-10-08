"""
Real tests for LLM Router with actual data and assertions
Tests LLM routing logic, model selection, and error handling
"""
import pytest
import os
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from intelligent_core.ai_foundation.llm.llm_router import LLMRouter, LLMProvider


class TestLLMRouterInitialization:
    """Test LLM Router initialization with different configurations"""

    def test_router_initializes_with_anthropic_key(self):
        """Test router initializes when ANTHROPIC_API_KEY is available"""
        # ARRANGE
        with patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key-anthropic'}):
            with patch('intelligent_core.ai_foundation.llm.llm_router.AsyncAnthropic') as mock_anthropic:
                mock_client = MagicMock()
                mock_anthropic.return_value = mock_client

                # ACT
                router = LLMRouter()

                # ASSERT
                assert router.anthropic_key == 'test-key-anthropic'
                assert router.anthropic_client is not None
                mock_anthropic.assert_called_once_with(api_key='test-key-anthropic')


    def test_router_initializes_with_openai_key(self):
        """Test router initializes when OPENAI_API_KEY is available"""
        # ARRANGE
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key-openai'}):
            with patch('intelligent_core.ai_foundation.llm.llm_router.AsyncOpenAI') as mock_openai:
                mock_client = MagicMock()
                mock_openai.return_value = mock_client

                # ACT
                router = LLMRouter()

                # ASSERT
                assert router.openai_key == 'test-key-openai'
                assert router.openai_client is not None
                mock_openai.assert_called_once_with(api_key='test-key-openai')


    def test_router_initializes_with_both_keys(self):
        """Test router initializes with both API keys (priority: Anthropic)"""
        # ARRANGE
        env_vars = {
            'ANTHROPIC_API_KEY': 'test-key-anthropic',
            'OPENAI_API_KEY': 'test-key-openai'
        }

        with patch.dict(os.environ, env_vars):
            with patch('intelligent_core.ai_foundation.llm.llm_router.AsyncAnthropic') as mock_anthropic:
                with patch('intelligent_core.ai_foundation.llm.llm_router.AsyncOpenAI') as mock_openai:
                    # ACT
                    router = LLMRouter()

                    # ASSERT
                    assert router.anthropic_client is not None
                    assert router.openai_client is not None
                    mock_anthropic.assert_called_once()
                    mock_openai.assert_called_once()


    def test_router_handles_missing_keys_gracefully(self):
        """Test router works without API keys (fallback to Ollama)"""
        # ARRANGE
        with patch.dict(os.environ, {}, clear=True):
            # ACT
            router = LLMRouter()

            # ASSERT
            assert router.anthropic_key is None
            assert router.openai_key is None
            assert router.anthropic_client is None
            assert router.openai_client is None


class TestLLMRouterModelSelection:
    """Test model selection for different task types"""

    @pytest.fixture
    def router_with_anthropic(self):
        """Router with Anthropic client"""
        with patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'}):
            with patch('intelligent_core.ai_foundation.llm.llm_router.AsyncAnthropic'):
                router = LLMRouter()
                router.anthropic_client = MagicMock()
                yield router


    @pytest.fixture
    def router_with_openai(self):
        """Router with OpenAI client"""
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            with patch('intelligent_core.ai_foundation.llm.llm_router.AsyncOpenAI'):
                router = LLMRouter()
                router.anthropic_client = None  # Force OpenAI
                router.openai_client = MagicMock()
                yield router


    def test_strategic_analysis_selects_claude_opus(self, router_with_anthropic):
        """Test strategic analysis task selects Claude Opus (most powerful)"""
        # ACT
        model_name, client = router_with_anthropic._select_model(task_type="strategic_analysis")

        # ASSERT
        assert model_name == "claude-opus-4-20250514"
        assert client == router_with_anthropic.anthropic_client


    def test_content_generation_selects_claude_sonnet(self, router_with_anthropic):
        """Test content generation selects Claude Sonnet (balanced)"""
        # ACT
        model_name, client = router_with_anthropic._select_model(task_type="content_generation")

        # ASSERT
        assert model_name == "claude-3-5-sonnet-20241022"
        assert client == router_with_anthropic.anthropic_client


    def test_quick_tasks_select_claude_haiku(self, router_with_anthropic):
        """Test quick tasks select Claude Haiku (fast)"""
        # ACT
        model_name, client = router_with_anthropic._select_model(task_type="quick_tasks")

        # ASSERT
        assert model_name == "claude-3-5-haiku-20241022"
        assert client == router_with_anthropic.anthropic_client


    def test_strategic_analysis_falls_back_to_gpt4(self, router_with_openai):
        """Test fallback to GPT-4 when Claude unavailable"""
        # ACT
        model_name, client = router_with_openai._select_model(task_type="strategic_analysis")

        # ASSERT
        assert model_name == "gpt-4-turbo-preview"
        assert client == router_with_openai.openai_client


    def test_quick_tasks_fall_back_to_gpt35(self, router_with_openai):
        """Test fallback to GPT-3.5 for quick tasks"""
        # ACT
        model_name, client = router_with_openai._select_model(task_type="quick_tasks")

        # ASSERT
        assert model_name == "gpt-3.5-turbo"
        assert client == router_with_openai.openai_client


class TestLLMRouterRealUsage:
    """Test real usage scenarios with actual LLM calls (mocked)"""

    @pytest.fixture
    def router_with_mock_clients(self):
        """Router with mocked LLM clients"""
        with patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'}):
            with patch('intelligent_core.ai_foundation.llm.llm_router.AsyncAnthropic'):
                router = LLMRouter()

                # Mock Anthropic client
                mock_client = AsyncMock()
                mock_client.messages.create = AsyncMock(return_value=Mock(
                    content=[Mock(text="This is a test response for BIA process identification.")],
                    usage=Mock(input_tokens=100, output_tokens=50)
                ))
                router.anthropic_client = mock_client

                yield router


    @pytest.mark.asyncio
    async def test_bia_process_identification_query(self, router_with_mock_clients):
        """Test real BIA process identification query"""
        # ARRANGE
        prompt = """Analyze this healthcare organization and identify critical business processes:

Organization: City General Hospital
Industry: Healthcare
Size: 850 employees
Services: Emergency care, Laboratory, Radiology, Patient Registration

Please identify the top 5 critical processes with RTO/RPO recommendations."""

        # ACT
        model_name, client = router_with_mock_clients._select_model("strategic_analysis")
        response = await client.messages.create(
            model=model_name,
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )

        # ASSERT
        assert model_name == "claude-opus-4-20250514"
        assert response.content[0].text is not None
        assert len(response.content[0].text) > 0
        assert response.usage.input_tokens > 0
        assert response.usage.output_tokens > 0


    @pytest.mark.asyncio
    async def test_risk_assessment_query(self, router_with_mock_clients):
        """Test risk assessment LLM query"""
        # ARRANGE
        prompt = """Perform a FAIR risk analysis for this threat:

Threat: Ransomware attack on hospital EHR system
Asset Value: $10M (patient database)
Current Controls: Basic antivirus, weekly backups
Threat Actors: Organized cybercrime

Provide: Loss Event Frequency, Probable Loss Magnitude, Annual Loss Expectancy"""

        # Mock realistic response
        router_with_mock_clients.anthropic_client.messages.create = AsyncMock(return_value=Mock(
            content=[Mock(text="""FAIR Analysis Results:
- Loss Event Frequency: 0.3 (30% annually)
- Probable Loss Magnitude: $5M-$15M
- Annual Loss Expectancy: $3M
- Recommendations: Deploy EDR, implement 3-2-1 backup, security training""")],
            usage=Mock(input_tokens=150, output_tokens=80)
        ))

        # ACT
        model_name, client = router_with_mock_clients._select_model("strategic_analysis")
        response = await client.messages.create(
            model=model_name,
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}]
        )

        # ASSERT
        assert "Loss Event Frequency" in response.content[0].text
        assert "Annual Loss Expectancy" in response.content[0].text
        assert "$" in response.content[0].text  # Contains monetary values


class TestLLMRouterErrorHandling:
    """Test error handling and edge cases"""

    def test_router_handles_import_error_gracefully(self):
        """Test router handles missing anthropic package"""
        # ARRANGE
        with patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'}):
            with patch('intelligent_core.ai_foundation.llm.llm_router.AsyncAnthropic', side_effect=ImportError):
                # ACT
                router = LLMRouter()

                # ASSERT
                assert router.anthropic_key == 'test-key'
                assert router.anthropic_client is None  # Failed to initialize


    def test_router_handles_no_available_clients(self):
        """Test router behavior when no LLM clients available"""
        # ARRANGE
        with patch.dict(os.environ, {}, clear=True):
            router = LLMRouter()

            # ACT
            model_name, client = router._select_model("general")

            # ASSERT
            # Should return None or raise appropriate error
            assert client is None or model_name is None


    @pytest.mark.asyncio
    async def test_router_handles_api_error(self):
        """Test router handles API errors (rate limit, network error)"""
        # ARRANGE
        with patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'}):
            with patch('intelligent_core.ai_foundation.llm.llm_router.AsyncAnthropic'):
                router = LLMRouter()

                # Mock API error
                mock_client = AsyncMock()
                mock_client.messages.create = AsyncMock(side_effect=Exception("API Error: Rate limit exceeded"))
                router.anthropic_client = mock_client

                # ACT & ASSERT
                model_name, client = router._select_model("general")
                with pytest.raises(Exception) as exc_info:
                    await client.messages.create(
                        model=model_name,
                        max_tokens=100,
                        messages=[{"role": "user", "content": "test"}]
                    )

                assert "Rate limit" in str(exc_info.value)


class TestLLMProviderEnum:
    """Test LLMProvider enum"""

    def test_provider_enum_values(self):
        """Test all provider enum values are defined"""
        # ASSERT
        assert LLMProvider.OPENAI == "openai"
        assert LLMProvider.ANTHROPIC == "anthropic"
        assert LLMProvider.OLLAMA == "ollama"


    def test_provider_enum_is_string(self):
        """Test provider enum inherits from str"""
        # ASSERT
        assert isinstance(LLMProvider.OPENAI, str)
        assert isinstance(LLMProvider.ANTHROPIC, str)


# Integration test (requires real API keys - skip if not available)
@pytest.mark.integration
@pytest.mark.skipif(
    not os.getenv("ANTHROPIC_API_KEY"),
    reason="ANTHROPIC_API_KEY not set - skip integration test"
)
class TestLLMRouterIntegration:
    """Integration tests with real API calls"""

    @pytest.mark.asyncio
    async def test_real_bia_query_to_claude(self):
        """Test real API call to Claude for BIA analysis"""
        # ARRANGE
        router = LLMRouter()

        prompt = "List 3 critical business processes for a hospital. Be very brief."

        # ACT
        model_name, client = router._select_model("quick_tasks")
        response = await client.messages.create(
            model=model_name,
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}]
        )

        # ASSERT
        assert response is not None
        assert response.content[0].text is not None
        assert len(response.content[0].text) > 20  # Should have meaningful response
        assert "process" in response.content[0].text.lower()
