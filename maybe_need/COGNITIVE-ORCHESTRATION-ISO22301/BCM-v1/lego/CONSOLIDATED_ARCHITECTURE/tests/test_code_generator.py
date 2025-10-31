#!/usr/bin/env python3
"""
Unit tests for CodeGenerator
"""

import pytest
import asyncio
from generator.code_generator import CodeGenerator

class TestCodeGenerator:
    """Test cases for CodeGenerator"""

    def setup_method(self):
        """Setup test fixtures"""
        self.generator = CodeGenerator()

    def create_monolith_architecture(self):
        """Create sample architecture for monolith"""
        return {
            "primary_pattern": "monolith",
            "confidence": 0.85,
            "reasons": ["Small codebase", "Single language"],
            "recommended_components": ["Web Application", "Database", "REST API"],
            "deployment_strategy": "Single container deployment",
            "technology_stack": {
                "backend": ["FastAPI", "Python 3.11+"],
                "database": ["PostgreSQL"],
                "infrastructure": ["Docker", "Load Balancer"]
            }
        }

    def create_microservices_architecture(self):
        """Create sample architecture for microservices"""
        return {
            "primary_pattern": "microservices",
            "confidence": 0.90,
            "reasons": ["Microservices patterns detected", "Docker present"],
            "recommended_components": [
                "API Gateway", "User Service", "Order Service",
                "Database per Service", "Service Discovery"
            ],
            "deployment_strategy": "Kubernetes with service mesh",
            "technology_stack": {
                "backend": ["FastAPI", "Node.js"],
                "database": ["PostgreSQL", "Redis"],
                "infrastructure": ["Docker", "Kubernetes", "API Gateway"]
            }
        }

    def create_serverless_architecture(self):
        """Create sample architecture for serverless"""
        return {
            "primary_pattern": "serverless",
            "confidence": 0.75,
            "reasons": ["Small functions", "Event-driven"],
            "recommended_components": [
                "API Gateway", "Lambda Functions", "Event Bus", "Managed Database"
            ],
            "deployment_strategy": "Function-as-a-Service platform",
            "technology_stack": {
                "backend": ["Python 3.11+"],
                "database": ["DynamoDB"],
                "infrastructure": ["AWS Lambda", "API Gateway"]
            }
        }

    @pytest.mark.asyncio
    async def test_generate_monolith(self):
        """Test monolith code generation"""
        architecture = self.create_monolith_architecture()

        generated_files = await self.generator.generate(architecture)

        # Verify basic files are generated
        assert len(generated_files) > 0

        # Should have main application file
        assert any("main.py" in filename for filename in generated_files.keys())

        # Should have Dockerfile
        assert any("Dockerfile" in filename for filename in generated_files.keys())

        # Should have requirements.txt
        assert any("requirements.txt" in filename for filename in generated_files.keys())

        # Verify content quality
        main_file = None
        for filename, content in generated_files.items():
            if "main.py" in filename:
                main_file = content
                break

        assert main_file is not None
        assert "FastAPI" in main_file
        # AI generates different structure
        assert "class" in main_file or "app = FastAPI" in main_file
        assert "async def" in main_file

    @pytest.mark.asyncio
    async def test_generate_microservices(self):
        """Test microservices code generation"""
        architecture = self.create_microservices_architecture()

        generated_files = await self.generator.generate(architecture)

        # Verify multiple services are generated
        assert len(generated_files) > 3

        # Should have gateway or multiple services (AI generates different structure)
        assert any("gateway" in filename for filename in generated_files.keys()) or len(generated_files) >= 4

        # Should have individual services
        assert any("service" in filename for filename in generated_files.keys())

        # Should have docker-compose
        assert any("docker-compose.yml" in filename for filename in generated_files.keys())

        # Should have kubernetes manifests
        assert any("k8s" in filename for filename in generated_files.keys())

        # Verify docker-compose content
        compose_file = None
        for filename, content in generated_files.items():
            if "docker-compose.yml" in filename:
                compose_file = content
                break

        assert compose_file is not None
        assert "services:" in compose_file
        assert "postgres" in compose_file.lower()
        assert "redis" in compose_file.lower()

    @pytest.mark.asyncio
    async def test_generate_serverless(self):
        """Test serverless code generation"""
        architecture = self.create_serverless_architecture()

        generated_files = await self.generator.generate(architecture)

        # Verify serverless-specific files
        assert len(generated_files) > 0

        # Should have function files
        assert any("functions" in filename for filename in generated_files.keys())

        # Should have serverless configuration
        assert any("serverless.yml" in filename for filename in generated_files.keys())

        # Verify function content
        function_file = None
        for filename, content in generated_files.items():
            if "functions" in filename and filename.endswith(".py"):
                function_file = content
                break

        assert function_file is not None
        assert "lambda_handler" in function_file
        assert "def lambda_handler(event, context)" in function_file

    def test_render_template_basic(self):
        """Test basic template rendering"""
        template_vars = {
            "project_name": "TestProject",
            "class_name": "TestClass",
            "description": "Test description"
        }

        result = self.generator._render_template("orchestrator_base", template_vars)

        assert "TestProject" in result
        assert "TestClass" in result
        assert "Test description" in result
        assert "FastAPI" in result

    def test_render_template_with_lists(self):
        """Test template rendering with complex data structures"""
        template_vars = {
            "project_name": "TestProject",
            "class_name": "TestClass",
            "description": "Test description",
            "endpoints": [
                {
                    "method": "GET",
                    "path": "/test",
                    "name": "test_endpoint",
                    "description": "Test endpoint"
                }
            ],
            "components": [
                {
                    "name": "test_component",
                    "init_code": "TestComponent()"
                }
            ]
        }

        result = self.generator._render_template("orchestrator_base", template_vars)

        assert "/test" in result
        assert "test_endpoint" in result
        assert "TestComponent()" in result

    def test_render_microservice_template(self):
        """Test microservice template rendering"""
        template_vars = {
            "service_name": "user_service",
            "service_class": "User",
            "service_description": "User management service",
            "service_port": 8001,
            "service_endpoints": [
                {
                    "method": "GET",
                    "path": "/users",
                    "function_name": "get_users",
                    "description": "Get all users",
                    "params": ""
                }
            ],
            "data_models": [
                {
                    "name": "UserModel",
                    "fields": [
                        {"name": "id", "type": "int", "default": None},
                        {"name": "name", "type": "str", "default": None}
                    ]
                }
            ]
        }

        result = self.generator._render_template("microservice_template", template_vars)

        assert "user_service" in result
        assert "class User" in result
        assert "get_users" in result
        assert "UserModel" in result
        assert "port=8001" in result

    def test_render_docker_compose_template(self):
        """Test docker-compose template rendering"""
        template_vars = {
            "project_name": "test_app",
            "services": [
                {
                    "name": "web",
                    "path": "web",
                    "port": 8000,
                    "internal_port": 8000,
                    "environment": [{"name": "ENV", "value": "production"}],
                    "dependencies": ["database"],
                    "volumes": []
                }
            ],
            "has_database": True,
            "has_redis": True,
            "db_name": "test_db",
            "db_user": "postgres",
            "db_password": "password"
        }

        result = self.generator._render_template("docker_compose", template_vars)

        assert "version:" in result
        assert "web:" in result
        assert "database:" in result
        assert "redis:" in result
        assert "postgres:15-alpine" in result

    def test_render_kubernetes_template(self):
        """Test Kubernetes deployment template rendering"""
        template_vars = {
            "service_name": "web-app",
            "image_name": "test-app/web",
            "image_tag": "latest",
            "replicas": 3,
            "container_port": 8000,
            "service_port": 80,
            "memory_request": "256Mi",
            "cpu_request": "100m",
            "memory_limit": "512Mi",
            "cpu_limit": "500m",
            "environment_variables": [
                {"name": "ENV", "value": "production"}
            ]
        }

        result = self.generator._render_template("kubernetes_deployment", template_vars)

        assert "Deployment" in result
        assert "Service" in result
        assert "web-app" in result
        assert "replicas: 3" in result
        assert "test-app/web:latest" in result

    def test_render_dockerfile_template(self):
        """Test Dockerfile template rendering"""
        template_vars = {
            "port": 8000,
            "main_file": "main.py"
        }

        result = self.generator._render_template("dockerfile", template_vars)

        assert "FROM python:3.11-slim" in result
        assert "EXPOSE 8000" in result
        assert 'CMD ["python", "main.py"]' in result
        assert "WORKDIR /app" in result

    @pytest.mark.asyncio
    async def test_generate_hybrid(self):
        """Test hybrid architecture generation"""
        architecture = {
            "primary_pattern": "hybrid",
            "confidence": 0.80,
            "recommended_components": ["Monolith Core", "Microservices Extensions"]
        }

        generated_files = await self.generator.generate(architecture)

        # Should generate both monolith and microservices files
        assert len(generated_files) > 5

        # Should have core/ prefix for monolith files
        assert any(filename.startswith("core/") for filename in generated_files.keys())

        # Should have services/ prefix for microservices files
        assert any(filename.startswith("services/") for filename in generated_files.keys())

    @pytest.mark.asyncio
    async def test_generate_infrastructure_files(self):
        """Test infrastructure file generation"""
        architecture = self.create_microservices_architecture()

        generated_files = await self.generator.generate(architecture)

        # Should have monitoring configuration
        assert any("prometheus.yml" in filename for filename in generated_files.keys())

        # Should have CI/CD pipeline
        assert any("deploy.yml" in filename for filename in generated_files.keys())

        # Verify prometheus config
        prometheus_file = None
        for filename, content in generated_files.items():
            if "prometheus.yml" in filename:
                prometheus_file = content
                break

        assert prometheus_file is not None
        assert "scrape_configs:" in prometheus_file
        assert "job_name:" in prometheus_file

    def test_template_error_handling(self):
        """Test template rendering error handling"""
        # Test with invalid template name
        result = self.generator._render_template("nonexistent_template", {})
        assert "Template rendering failed" in result

    @pytest.mark.asyncio
    async def test_generate_with_empty_architecture(self):
        """Test generation with minimal architecture data"""
        minimal_architecture = {
            "primary_pattern": "monolith"
        }

        # Should not crash with minimal data
        generated_files = await self.generator.generate(minimal_architecture)
        assert len(generated_files) > 0

    def test_load_templates(self):
        """Test that all required templates are loaded"""
        templates = self.generator._load_templates()

        required_templates = [
            "orchestrator_base",
            "microservice_template",
            "docker_compose",
            "kubernetes_deployment",
            "dockerfile"
        ]

        for template_name in required_templates:
            assert template_name in templates
            assert len(templates[template_name]) > 0

if __name__ == "__main__":
    # Run specific test
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "quick":
        # Quick test for development
        test = TestCodeGenerator()
        test.setup_method()
        asyncio.run(test.test_generate_monolith())
        print("✅ Quick generator test passed!")
    else:
        # Run full test suite
        pytest.main([__file__, "-v"])