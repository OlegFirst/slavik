#!/usr/bin/env python3
"""
Unit tests for ArchitectureClassifier
"""

import pytest
import asyncio
from analyzer.architecture_classifier import ArchitectureClassifier, ArchitectureRecommendation

class TestArchitectureClassifier:
    """Test cases for ArchitectureClassifier"""

    def setup_method(self):
        """Setup test fixtures"""
        self.classifier = ArchitectureClassifier()

    def create_monolith_analysis(self):
        """Create sample analysis result for monolith"""
        return {
            "project_name": "monolith_app",
            "metrics": {
                "lines_of_code": 5000,
                "files_count": 30,
                "test_files": 5
            },
            "dependencies": {
                "count": 15,
                "external": ["fastapi", "sqlalchemy", "pydantic"]
            },
            "languages": {"python": 25},
            "frameworks": ["FastAPI"],
            "patterns": [],
            "complexity_score": "medium"
        }

    def create_microservices_analysis(self):
        """Create sample analysis result for microservices"""
        return {
            "project_name": "microservices_app",
            "metrics": {
                "lines_of_code": 25000,
                "files_count": 150,
                "test_files": 30
            },
            "dependencies": {
                "count": 45,
                "external": ["express", "react", "docker", "kubernetes"]
            },
            "languages": {"javascript": 80, "python": 20},
            "frameworks": ["React", "Express.js", "Docker", "Docker Compose"],
            "patterns": ["microservices"],
            "complexity_score": "high"
        }

    def create_serverless_analysis(self):
        """Create sample analysis result for serverless"""
        return {
            "project_name": "serverless_app",
            "metrics": {
                "lines_of_code": 2000,
                "files_count": 15,
                "test_files": 8
            },
            "dependencies": {
                "count": 10,
                "external": ["aws-lambda", "boto3"]
            },
            "languages": {"python": 15},
            "frameworks": ["AWS Lambda"],
            "patterns": ["event"],
            "complexity_score": "low"
        }

    @pytest.mark.asyncio
    async def test_classify_monolith(self):
        """Test classification of monolith architecture"""
        analysis = self.create_monolith_analysis()

        result = await self.classifier.classify(analysis)

        # Verify basic structure
        assert "primary_pattern" in result
        assert "confidence" in result
        assert "reasons" in result
        assert "alternative_patterns" in result
        assert "recommended_components" in result
        assert "deployment_strategy" in result
        assert "implementation_steps" in result
        assert "estimated_complexity" in result
        assert "technology_stack" in result

        # Verify confidence is in valid range
        assert 0 <= result["confidence"] <= 1.0

        # Verify pattern makes sense
        assert result["primary_pattern"] in ["monolith", "microservices", "serverless", "hybrid"]

    @pytest.mark.asyncio
    async def test_classify_microservices(self):
        """Test classification of microservices architecture"""
        analysis = self.create_microservices_analysis()

        result = await self.classifier.classify(analysis)

        # Should likely classify as microservices
        assert result["primary_pattern"] == "microservices"
        assert result["confidence"] > 0.5

        # Should have microservices-specific components
        components = result["recommended_components"]
        assert any("gateway" in comp.lower() or "service" in comp.lower() for comp in components)

    @pytest.mark.asyncio
    async def test_classify_serverless(self):
        """Test classification of serverless architecture"""
        analysis = self.create_serverless_analysis()

        result = await self.classifier.classify(analysis)

        # Verify reasonable classification
        assert result["primary_pattern"] in ["serverless", "monolith"]
        assert 0 <= result["confidence"] <= 1.0

    def test_extract_features(self):
        """Test feature extraction"""
        analysis = self.create_microservices_analysis()

        features = self.classifier._extract_features(analysis)

        # Verify all expected features are present
        expected_features = [
            "lines_of_code", "files_count", "dependencies_count",
            "languages", "frameworks", "patterns", "complexity_score",
            "has_tests", "has_docker", "has_api", "has_database",
            "has_frontend", "has_services"
        ]

        for feature in expected_features:
            assert feature in features

        # Verify feature values
        assert features["lines_of_code"] == 25000
        assert features["files_count"] == 150
        assert features["dependencies_count"] == 45
        assert features["has_docker"] == True
        assert features["has_services"] == True

    def test_detect_api_pattern(self):
        """Test API pattern detection"""
        analysis_with_api = {
            "frameworks": ["FastAPI", "Express.js"]
        }

        analysis_without_api = {
            "frameworks": ["React"]
        }

        assert self.classifier._detect_api_pattern(analysis_with_api) == True
        assert self.classifier._detect_api_pattern(analysis_without_api) == False

    def test_detect_database_usage(self):
        """Test database usage detection"""
        analysis_with_db = {
            "dependencies": {
                "external": ["sqlalchemy", "mongoose", "sequelize"]
            }
        }

        analysis_without_db = {
            "dependencies": {
                "external": ["requests", "numpy"]
            }
        }

        assert self.classifier._detect_database_usage(analysis_with_db) == True
        assert self.classifier._detect_database_usage(analysis_without_db) == False

    def test_detect_frontend_pattern(self):
        """Test frontend pattern detection"""
        analysis_with_frontend = {
            "frameworks": ["React", "Vue.js"]
        }

        analysis_without_frontend = {
            "frameworks": ["FastAPI", "Django"]
        }

        assert self.classifier._detect_frontend_pattern(analysis_with_frontend) == True
        assert self.classifier._detect_frontend_pattern(analysis_without_frontend) == False

    def test_generate_pattern_components_monolith(self):
        """Test component generation for monolith"""
        features = {
            "has_api": True,
            "has_database": True,
            "has_frontend": False
        }

        components = self.classifier._generate_pattern_components("monolith", features)

        assert "Web Application" in components
        assert "Database" in components
        assert "REST API" in components

    def test_generate_pattern_components_microservices(self):
        """Test component generation for microservices"""
        features = {
            "has_api": True,
            "has_database": True,
            "has_frontend": True
        }

        components = self.classifier._generate_pattern_components("microservices", features)

        assert "API Gateway" in components
        assert "Service Discovery" in components
        assert any("Service" in comp for comp in components)

    def test_get_deployment_strategy(self):
        """Test deployment strategy selection"""
        strategies = {
            "monolith": self.classifier._get_deployment_strategy("monolith"),
            "microservices": self.classifier._get_deployment_strategy("microservices"),
            "serverless": self.classifier._get_deployment_strategy("serverless"),
            "hybrid": self.classifier._get_deployment_strategy("hybrid")
        }

        # Verify each pattern has a deployment strategy
        for pattern, strategy in strategies.items():
            assert strategy is not None
            assert len(strategy) > 0

    def test_generate_implementation_steps(self):
        """Test implementation steps generation"""
        recommendation = ArchitectureRecommendation(
            pattern="microservices",
            confidence=0.8,
            reasons=["Test"],
            components=["API Gateway"],
            deployment_strategy="Kubernetes"
        )

        steps = self.classifier._generate_implementation_steps(recommendation)

        assert len(steps) > 0
        assert any("service" in step.lower() for step in steps)

    def test_estimate_implementation_complexity(self):
        """Test implementation complexity estimation"""
        # High complexity features
        high_complexity_features = {
            "lines_of_code": 100000,
            "dependencies_count": 150
        }

        # Low complexity features
        low_complexity_features = {
            "lines_of_code": 1000,
            "dependencies_count": 5
        }

        high_complexity = self.classifier._estimate_implementation_complexity(high_complexity_features)
        low_complexity = self.classifier._estimate_implementation_complexity(low_complexity_features)

        assert high_complexity in ["high", "very_high"]
        assert low_complexity in ["low", "medium"]

    def test_suggest_technology_stack(self):
        """Test technology stack suggestions"""
        features = {
            "languages": ["python", "javascript"],
            "has_frontend": True,
            "has_database": True
        }

        recommendation = ArchitectureRecommendation(
            pattern="microservices",
            confidence=0.8,
            reasons=["Test"],
            components=["API Gateway"],
            deployment_strategy="Kubernetes"
        )

        stack = self.classifier._suggest_technology_stack(features, recommendation)

        # Verify stack structure
        expected_categories = ["backend", "frontend", "database", "infrastructure", "monitoring"]
        for category in expected_categories:
            assert category in stack
            assert isinstance(stack[category], list)

        # Verify some suggestions are present
        assert len(stack["backend"]) > 0
        assert len(stack["monitoring"]) > 0

    @pytest.mark.asyncio
    async def test_classify_edge_cases(self):
        """Test classification with edge cases"""
        # Empty analysis
        empty_analysis = {
            "project_name": "empty",
            "metrics": {"lines_of_code": 0, "files_count": 0, "test_files": 0},
            "dependencies": {"count": 0, "external": []},
            "languages": {},
            "frameworks": [],
            "patterns": [],
            "complexity_score": "low"
        }

        result = await self.classifier.classify(empty_analysis)

        # Should handle gracefully and provide default recommendation
        assert result["primary_pattern"] is not None
        assert 0 <= result["confidence"] <= 1.0

    @pytest.mark.asyncio
    async def test_classify_mixed_signals(self):
        """Test classification with mixed architectural signals"""
        mixed_analysis = {
            "project_name": "mixed_app",
            "metrics": {
                "lines_of_code": 15000,
                "files_count": 75,
                "test_files": 10
            },
            "dependencies": {
                "count": 30,
                "external": ["react", "express", "fastapi", "docker"]
            },
            "languages": {"javascript": 40, "python": 35},
            "frameworks": ["React", "Express.js", "FastAPI", "Docker"],
            "patterns": ["microservices", "mvc"],
            "complexity_score": "medium"
        }

        result = await self.classifier.classify(mixed_analysis)

        # Should make a reasonable decision
        assert result["primary_pattern"] in ["microservices", "hybrid"]
        assert result["confidence"] > 0.3  # Should have some confidence

if __name__ == "__main__":
    # Run specific test
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "quick":
        # Quick test for development
        test = TestArchitectureClassifier()
        test.setup_method()
        asyncio.run(test.test_classify_monolith())
        print("✅ Quick classifier test passed!")
    else:
        # Run full test suite
        pytest.main([__file__, "-v"])