#!/usr/bin/env python3
"""
Test Universal Orchestration Platform
"""

import asyncio
import tempfile
import zipfile
import json
from pathlib import Path

# Test the complete workflow
async def test_complete_workflow():
    """Test the complete analysis → classification → generation → visualization workflow"""

    # Create a sample project for testing
    sample_project = create_sample_project()

    print("🚀 Testing Universal Orchestration Platform...")
    print("=" * 60)

    try:
        # Import our components
        from analyzer.project_analyzer import ProjectAnalyzer
        from analyzer.architecture_classifier import ArchitectureClassifier
        from generator.code_generator import CodeGenerator
        from visualizer.diagram_generator import DiagramGenerator

        # Initialize components
        analyzer = ProjectAnalyzer()
        classifier = ArchitectureClassifier()
        generator = CodeGenerator()
        visualizer = DiagramGenerator()

        print("✅ All components imported successfully")

        # Step 1: Analyze project
        print("\n📊 Step 1: Analyzing project structure...")
        analysis_result = await analyzer.analyze(sample_project)

        print(f"   • Project: {analysis_result['project_name']}")
        print(f"   • Files: {analysis_result['metrics']['files_count']}")
        print(f"   • Lines of code: {analysis_result['metrics']['lines_of_code']}")
        print(f"   • Languages: {list(analysis_result['languages'].keys())}")
        print(f"   • Frameworks: {analysis_result['frameworks']}")
        print(f"   • Complexity: {analysis_result['complexity_score']}")

        # Step 2: Classify architecture
        print("\n🏗️ Step 2: Classifying architecture...")
        architecture = await classifier.classify(analysis_result)

        print(f"   • Primary pattern: {architecture['primary_pattern']}")
        print(f"   • Confidence: {architecture['confidence']:.2f}")
        print(f"   • Reasons: {', '.join(architecture['reasons'][:2])}")
        print(f"   • Components: {len(architecture['recommended_components'])} recommended")

        # Step 3: Generate code
        print("\n💻 Step 3: Generating code...")
        generated_code = await generator.generate(architecture)

        print(f"   • Generated files: {len(generated_code)}")
        for filename in list(generated_code.keys())[:5]:
            print(f"     - {filename}")
        if len(generated_code) > 5:
            print(f"     ... and {len(generated_code) - 5} more files")

        # Step 4: Generate diagram
        print("\n🎨 Step 4: Generating architecture diagram...")
        diagram_html = await visualizer.generate(architecture)

        print(f"   • Diagram generated: {len(diagram_html)} characters")
        print(f"   • Pattern: {architecture['primary_pattern']}")

        # Save results for inspection
        results_dir = Path("test_results")
        results_dir.mkdir(exist_ok=True)

        # Save analysis result
        with open(results_dir / "analysis_result.json", "w") as f:
            json.dump(analysis_result, f, indent=2)

        # Save architecture classification
        with open(results_dir / "architecture.json", "w") as f:
            json.dump(architecture, f, indent=2)

        # Save diagram
        with open(results_dir / "architecture_diagram.html", "w") as f:
            f.write(diagram_html)

        # Save one generated file as example
        if generated_code:
            first_file = list(generated_code.keys())[0]
            with open(results_dir / f"generated_{first_file.replace('/', '_')}", "w") as f:
                f.write(generated_code[first_file])

        print(f"\n📁 Results saved to: {results_dir.absolute()}")

        # Final summary
        print("\n" + "=" * 60)
        print("🎉 UNIVERSAL ORCHESTRATION PLATFORM TEST COMPLETE!")
        print("✅ All components working correctly")
        print("✅ Complete workflow successful")
        print("✅ Phase 1 MVP Ready!")

        return True

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_sample_project():
    """Create a sample project for testing"""

    # Create temporary directory
    temp_dir = Path(tempfile.mkdtemp())
    project_dir = temp_dir / "sample_project"
    project_dir.mkdir()

    # Create sample Python files
    (project_dir / "main.py").write_text('''#!/usr/bin/env python3
"""
Sample E-commerce Application
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncio

app = FastAPI(title="E-commerce API")

class Product(BaseModel):
    id: int
    name: str
    price: float
    description: str

class User(BaseModel):
    id: int
    email: str
    name: str

@app.get("/")
async def root():
    return {"message": "E-commerce API"}

@app.get("/products")
async def get_products():
    # TODO: Implement product listing
    return {"products": []}

@app.post("/products")
async def create_product(product: Product):
    # TODO: Implement product creation
    return {"message": "Product created", "product": product}

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    # TODO: Implement user retrieval
    return {"user_id": user_id}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
''')

    (project_dir / "models.py").write_text('''"""
Database models
"""

from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    price = Column(Float, nullable=False)
    description = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(100), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    total_amount = Column(Float, nullable=False)
    status = Column(String(50), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
''')

    # Create package.json for Node.js detection
    (project_dir / "package.json").write_text('''{
  "name": "ecommerce-frontend",
  "version": "1.0.0",
  "description": "E-commerce frontend application",
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "express": "^4.18.2",
    "axios": "^1.5.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "typescript": "^5.0.0"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test"
  }
}''')

    # Create requirements.txt
    (project_dir / "requirements.txt").write_text('''fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
pydantic==2.5.0
psycopg2-binary==2.9.9
redis==5.0.1
pytest==7.4.3
''')

    # Create some directories
    (project_dir / "services").mkdir()
    (project_dir / "services" / "__init__.py").write_text("")
    (project_dir / "services" / "user_service.py").write_text('''"""User service module"""

class UserService:
    def __init__(self):
        self.users = {}

    async def get_user(self, user_id: int):
        return self.users.get(user_id)

    async def create_user(self, user_data):
        user_id = len(self.users) + 1
        self.users[user_id] = user_data
        return user_id
''')

    (project_dir / "tests").mkdir()
    (project_dir / "tests" / "test_main.py").write_text('''"""Tests for main application"""

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "E-commerce API"}

def test_products():
    response = client.get("/products")
    assert response.status_code == 200
''')

    # Create Docker files
    (project_dir / "Dockerfile").write_text('''FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "main.py"]
''')

    (project_dir / "docker-compose.yml").write_text('''version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
    environment:
      - DATABASE_URL=postgresql://user:password@postgres:5432/ecommerce
      - REDIS_URL=redis://redis:6379

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=ecommerce
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
''')

    print(f"📦 Created sample project at: {project_dir}")
    print(f"   • Files: {len(list(project_dir.rglob('*')))} total")
    print(f"   • Python files: {len(list(project_dir.rglob('*.py')))}")
    print(f"   • Config files: {len(list(project_dir.rglob('*.json'))) + len(list(project_dir.rglob('*.yml')))}")

    return project_dir

if __name__ == "__main__":
    success = asyncio.run(test_complete_workflow())
    if success:
        exit(0)
    else:
        exit(1)