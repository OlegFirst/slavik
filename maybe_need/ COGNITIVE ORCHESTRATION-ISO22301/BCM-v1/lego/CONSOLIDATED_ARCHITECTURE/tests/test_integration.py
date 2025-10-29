#!/usr/bin/env python3
"""
Integration tests for complete Universal Orchestration Platform workflow
"""

import pytest
import tempfile
import zipfile
import json
import time
from pathlib import Path
import asyncio
from fastapi.testclient import TestClient

from analyzer.project_analyzer import ProjectAnalyzer
from analyzer.architecture_classifier import ArchitectureClassifier
from generator.code_generator import CodeGenerator
from visualizer.diagram_generator import DiagramGenerator
from main_uop import app

class TestIntegration:
    """Integration tests for complete workflow"""

    def setup_method(self):
        """Setup test fixtures"""
        self.analyzer = ProjectAnalyzer()
        self.classifier = ArchitectureClassifier()
        self.generator = CodeGenerator()
        self.visualizer = DiagramGenerator()
        self.client = TestClient(app)
        self.temp_dir = Path(tempfile.mkdtemp())

    def teardown_method(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def create_test_project_simple(self):
        """Create a simple test project"""
        project_dir = self.temp_dir / "simple_project"
        project_dir.mkdir()

        # Simple Python app
        (project_dir / "main.py").write_text('''#!/usr/bin/env python3
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello World"}

@app.get("/health")
def health():
    return {"status": "healthy"}
''')

        (project_dir / "requirements.txt").write_text('''fastapi==0.104.1
uvicorn==0.24.0
''')

        return project_dir

    def create_test_project_complex(self):
        """Create a complex test project for microservices detection"""
        project_dir = self.temp_dir / "complex_project"
        project_dir.mkdir()

        # Multiple services structure
        services_dir = project_dir / "services"
        services_dir.mkdir()

        # User service
        user_service_dir = services_dir / "user_service"
        user_service_dir.mkdir()
        (user_service_dir / "main.py").write_text('''#!/usr/bin/env python3
from fastapi import FastAPI
from sqlalchemy import create_engine

app = FastAPI(title="User Service")

@app.get("/users")
def get_users():
    return {"users": []}

@app.post("/users")
def create_user(user_data: dict):
    return {"message": "User created"}
''')

        # Order service
        order_service_dir = services_dir / "order_service"
        order_service_dir.mkdir()
        (order_service_dir / "main.py").write_text('''#!/usr/bin/env python3
from fastapi import FastAPI
import redis

app = FastAPI(title="Order Service")

@app.get("/orders")
def get_orders():
    return {"orders": []}

@app.post("/orders")
def create_order(order_data: dict):
    return {"message": "Order created"}
''')

        # Docker files
        (project_dir / "docker-compose.yml").write_text('''version: '3.8'
services:
  user-service:
    build: ./services/user_service
    ports:
      - "8001:8000"
  order-service:
    build: ./services/order_service
    ports:
      - "8002:8000"
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: myapp
''')

        (user_service_dir / "Dockerfile").write_text('''FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
''')

        (user_service_dir / "requirements.txt").write_text('''fastapi==0.104.1
sqlalchemy==2.0.23
''')

        (order_service_dir / "requirements.txt").write_text('''fastapi==0.104.1
redis==5.0.1
''')

        # Package.json for frontend detection
        (project_dir / "package.json").write_text('''{
  "name": "complex-app",
  "dependencies": {
    "react": "^18.2.0",
    "express": "^4.18.0"
  }
}''')

        return project_dir

    def create_project_zip(self, project_dir):
        """Create ZIP file from project directory"""
        zip_path = self.temp_dir / f"{project_dir.name}.zip"

        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in zip_path.parent.walk(project_dir):
                for file in files:
                    file_path = Path(root) / file
                    arc_name = file_path.relative_to(project_dir)
                    zipf.write(file_path, arc_name)

        return zip_path

    @pytest.mark.asyncio
    async def test_complete_workflow_simple_project(self):
        """Test complete workflow with simple project"""
        # Step 1: Create test project
        project_dir = self.create_test_project_simple()

        # Step 2: Analyze project
        analysis_result = await self.analyzer.analyze(project_dir)

        # Verify analysis
        assert analysis_result["project_name"] == "simple_project"
        assert "python" in analysis_result["languages"]
        assert "FastAPI" in analysis_result["frameworks"]
        assert analysis_result["metrics"]["lines_of_code"] > 0

        # Step 3: Classify architecture
        architecture = await self.classifier.classify(analysis_result)

        # Verify classification
        assert architecture["primary_pattern"] in ["monolith", "microservices", "serverless", "hybrid"]
        assert 0 <= architecture["confidence"] <= 1.0
        assert len(architecture["reasons"]) > 0

        # Step 4: Generate code
        generated_code = await self.generator.generate(architecture)

        # Verify code generation
        assert len(generated_code) > 0
        assert any("main.py" in filename or "orchestrator" in filename for filename in generated_code.keys())

        # Step 5: Generate diagram
        diagram_html = await self.visualizer.generate(architecture)

        # Verify diagram
        assert len(diagram_html) > 1000  # Should be substantial HTML
        assert "mermaid" in diagram_html.lower()
        assert architecture["primary_pattern"] in diagram_html.lower()

        print(f"✅ Complete workflow test passed!")
        print(f"   📊 Analysis: {analysis_result['complexity_score']} complexity")
        print(f"   🏗️ Architecture: {architecture['primary_pattern']} (confidence: {architecture['confidence']:.2f})")
        print(f"   💻 Generated: {len(generated_code)} files")
        print(f"   🎨 Diagram: {len(diagram_html)} characters")

    @pytest.mark.asyncio
    async def test_complete_workflow_complex_project(self):
        """Test complete workflow with complex microservices project"""
        # Step 1: Create complex test project
        project_dir = self.create_test_project_complex()

        # Step 2: Analyze project
        analysis_result = await self.analyzer.analyze(project_dir)

        # Verify analysis detects complexity
        assert analysis_result["metrics"]["files_count"] > 5
        assert "Docker" in analysis_result["frameworks"]
        assert "Docker Compose" in analysis_result["frameworks"]

        # Step 3: Classify architecture
        architecture = await self.classifier.classify(analysis_result)

        # Should detect microservices due to structure
        assert architecture["primary_pattern"] in ["microservices", "hybrid"]
        assert architecture["confidence"] > 0.5

        # Step 4: Generate code
        generated_code = await self.generator.generate(architecture)

        # Should generate microservices-specific files
        assert len(generated_code) > 3
        if architecture["primary_pattern"] == "microservices":
            assert any("service" in filename for filename in generated_code.keys())
            assert any("docker-compose.yml" in filename for filename in generated_code.keys())

        # Step 5: Generate diagram
        diagram_html = await self.visualizer.generate(architecture)

        # Verify microservices diagram elements
        assert "microservices" in diagram_html.lower() or "service" in diagram_html.lower()

        print(f"✅ Complex workflow test passed!")
        print(f"   📊 Detected: {len(analysis_result['frameworks'])} frameworks")
        print(f"   🏗️ Pattern: {architecture['primary_pattern']}")
        print(f"   💻 Files: {len(generated_code)} generated")

    def test_api_health_endpoint(self):
        """Test API health endpoint"""
        response = self.client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "components" in data
        assert data["components"]["analyzer"] == "ready"
        assert data["components"]["classifier"] == "ready"
        assert data["components"]["generator"] == "ready"
        assert data["components"]["visualizer"] == "ready"

    def test_api_root_endpoint(self):
        """Test API root endpoint returns web interface"""
        response = self.client.get("/")

        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "Universal Orchestration Platform" in response.text
        assert "upload" in response.text.lower()

    def test_api_analyze_project_no_file(self):
        """Test API analyze endpoint without file"""
        response = self.client.post("/analyze-project")

        assert response.status_code == 422  # Validation error

    def test_api_analyze_project_wrong_format(self):
        """Test API analyze endpoint with wrong file format"""
        # Create a text file instead of ZIP
        test_file = self.temp_dir / "test.txt"
        test_file.write_text("This is not a ZIP file")

        with open(test_file, "rb") as f:
            response = self.client.post(
                "/analyze-project",
                files={"file": ("test.txt", f, "text/plain")}
            )

        assert response.status_code == 400
        data = response.json()
        assert "ZIP" in data["detail"]

    def test_api_task_status_not_found(self):
        """Test API task status with invalid task ID"""
        response = self.client.get("/task-status/nonexistent_task")

        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_workflow_performance(self):
        """Test workflow performance with timing"""
        project_dir = self.create_test_project_simple()

        # Time each step
        start_time = time.time()

        # Step 1: Analysis
        analysis_start = time.time()
        analysis_result = await self.analyzer.analyze(project_dir)
        analysis_time = time.time() - analysis_start

        # Step 2: Classification
        classification_start = time.time()
        architecture = await self.classifier.classify(analysis_result)
        classification_time = time.time() - classification_start

        # Step 3: Generation
        generation_start = time.time()
        generated_code = await self.generator.generate(architecture)
        generation_time = time.time() - generation_start

        # Step 4: Visualization
        visualization_start = time.time()
        diagram_html = await self.visualizer.generate(architecture)
        visualization_time = time.time() - visualization_start

        total_time = time.time() - start_time

        # Performance assertions (should be reasonable for small project)
        assert analysis_time < 2.0  # Should analyze in under 2 seconds
        assert classification_time < 1.0  # Should classify in under 1 second
        assert generation_time < 3.0  # Should generate in under 3 seconds
        assert visualization_time < 1.0  # Should visualize in under 1 second
        assert total_time < 5.0  # Total should be under 5 seconds

        print(f"⚡ Performance test passed!")
        print(f"   📊 Analysis: {analysis_time:.2f}s")
        print(f"   🏗️ Classification: {classification_time:.2f}s")
        print(f"   💻 Generation: {generation_time:.2f}s")
        print(f"   🎨 Visualization: {visualization_time:.2f}s")
        print(f"   ⏱️ Total: {total_time:.2f}s")

    @pytest.mark.asyncio
    async def test_error_handling_invalid_project(self):
        """Test error handling with invalid project structure"""
        # Create empty directory
        empty_dir = self.temp_dir / "empty_project"
        empty_dir.mkdir()

        # Should handle gracefully
        analysis_result = await self.analyzer.analyze(empty_dir)
        architecture = await self.classifier.classify(analysis_result)
        generated_code = await self.generator.generate(architecture)
        diagram_html = await self.visualizer.generate(architecture)

        # All steps should complete without crashing
        assert analysis_result is not None
        assert architecture is not None
        assert generated_code is not None
        assert diagram_html is not None

        print("✅ Error handling test passed!")

    @pytest.mark.asyncio
    async def test_data_consistency(self):
        """Test data consistency across workflow steps"""
        project_dir = self.create_test_project_complex()

        # Run workflow
        analysis_result = await self.analyzer.analyze(project_dir)
        architecture = await self.classifier.classify(analysis_result)
        generated_code = await self.generator.generate(architecture)

        # Verify data consistency
        # Project name should be consistent
        assert analysis_result["project_name"] == "complex_project"

        # Architecture pattern should be reasonable given the analysis
        if "microservices" in analysis_result.get("patterns", []):
            assert architecture["primary_pattern"] in ["microservices", "hybrid"]

        # Generated code should match the architecture pattern
        if architecture["primary_pattern"] == "microservices":
            assert any("service" in filename or "gateway" in filename for filename in generated_code.keys())

        print("✅ Data consistency test passed!")

if __name__ == "__main__":
    # Run specific test
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "quick":
        # Quick test for development
        test = TestIntegration()
        test.setup_method()
        asyncio.run(test.test_complete_workflow_simple_project())
        print("✅ Quick integration test passed!")
    else:
        # Run full test suite
        pytest.main([__file__, "-v"])