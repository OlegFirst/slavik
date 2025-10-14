#!/usr/bin/env python3
"""
Unit tests for ProjectAnalyzer
"""

import pytest
import tempfile
import json
from pathlib import Path
import asyncio

from analyzer.project_analyzer import ProjectAnalyzer

class TestProjectAnalyzer:
    """Test cases for ProjectAnalyzer"""

    def setup_method(self):
        """Setup test fixtures"""
        self.analyzer = ProjectAnalyzer()
        self.temp_dir = Path(tempfile.mkdtemp())

    def teardown_method(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def create_sample_python_project(self):
        """Create a sample Python project for testing"""
        project_dir = self.temp_dir / "python_project"
        project_dir.mkdir()

        # Main Python file
        (project_dir / "main.py").write_text('''#!/usr/bin/env python3
"""Main application"""

import os
import sys
import json
from fastapi import FastAPI
from sqlalchemy import create_engine

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello World"}

@app.get("/users")
def get_users():
    # Sample function with 10 lines
    users = []
    for i in range(10):
        user = {
            "id": i,
            "name": f"User {i}"
        }
        users.append(user)
    return users

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app)
''')

        # Requirements file
        (project_dir / "requirements.txt").write_text('''fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
pytest==7.4.3
''')

        # Config file
        (project_dir / "config.json").write_text('{"debug": true, "port": 8000}')

        # Test file
        test_dir = project_dir / "tests"
        test_dir.mkdir()
        (test_dir / "test_main.py").write_text('''import pytest
from main import app

def test_root():
    assert True
''')

        return project_dir

    def create_sample_js_project(self):
        """Create a sample JavaScript project for testing"""
        project_dir = self.temp_dir / "js_project"
        project_dir.mkdir()

        # Package.json
        (project_dir / "package.json").write_text('''{
  "name": "sample-app",
  "version": "1.0.0",
  "dependencies": {
    "express": "^4.18.0",
    "react": "^18.2.0",
    "lodash": "^4.17.21"
  },
  "devDependencies": {
    "jest": "^29.0.0",
    "typescript": "^5.0.0"
  }
}''')

        # Main JS file
        (project_dir / "index.js").write_text('''const express = require('express');
const React = require('react');

const app = express();

app.get('/', (req, res) => {
  res.json({ message: 'Hello World' });
});

app.listen(3000, () => {
  console.log('Server running on port 3000');
});
''')

        return project_dir

    @pytest.mark.asyncio
    async def test_analyze_python_project(self):
        """Test analyzing a Python project"""
        project_dir = self.create_sample_python_project()

        result = await self.analyzer.analyze(project_dir)

        # Verify basic structure
        assert result["project_name"] == "python_project"
        assert "structure" in result
        assert "languages" in result
        assert "frameworks" in result
        assert "dependencies" in result
        assert "metrics" in result
        assert "patterns" in result
        assert "complexity_score" in result
        assert "recommendations" in result

        # Verify language detection
        assert "python" in result["languages"]
        assert result["languages"]["python"] > 0

        # Verify framework detection
        assert "FastAPI" in result["frameworks"]

        # Verify metrics
        assert result["metrics"]["files_count"] > 0
        assert result["metrics"]["lines_of_code"] > 0
        assert result["metrics"]["test_files"] > 0

        # Verify dependencies
        assert result["dependencies"]["count"] > 0
        assert "fastapi" in [dep.lower() for dep in result["dependencies"]["external"]]

    @pytest.mark.asyncio
    async def test_analyze_javascript_project(self):
        """Test analyzing a JavaScript project"""
        project_dir = self.create_sample_js_project()

        result = await self.analyzer.analyze(project_dir)

        # Verify basic structure
        assert result["project_name"] == "js_project"

        # Verify language detection
        assert "javascript" in result["languages"]

        # Verify framework detection
        assert "React" in result["frameworks"]
        assert "Express.js" in result["frameworks"]

    @pytest.mark.asyncio
    async def test_analyze_empty_project(self):
        """Test analyzing an empty project"""
        empty_dir = self.temp_dir / "empty_project"
        empty_dir.mkdir()

        result = await self.analyzer.analyze(empty_dir)

        # Should handle empty project gracefully
        assert result["project_name"] == "empty_project"
        assert result["metrics"]["files_count"] == 0
        assert result["metrics"]["lines_of_code"] == 0
        assert len(result["languages"]) == 0

    def test_detect_languages(self):
        """Test language detection"""
        project_dir = self.create_sample_python_project()

        languages = self.analyzer._detect_languages(project_dir)

        assert "python" in languages
        assert languages["python"] > 0

    def test_detect_frameworks_python(self):
        """Test framework detection for Python"""
        project_dir = self.create_sample_python_project()

        frameworks = self.analyzer._detect_frameworks(project_dir)

        assert "FastAPI" in frameworks

    def test_detect_frameworks_javascript(self):
        """Test framework detection for JavaScript"""
        project_dir = self.create_sample_js_project()

        frameworks = self.analyzer._detect_frameworks(project_dir)

        assert "React" in frameworks
        assert "Express.js" in frameworks

    def test_calculate_metrics(self):
        """Test metrics calculation"""
        project_dir = self.create_sample_python_project()

        metrics = self.analyzer._calculate_metrics(project_dir)

        assert metrics["files_count"] > 0
        assert metrics["lines_of_code"] > 0
        assert metrics["test_files"] > 0
        assert metrics["config_files"] > 0

    def test_detect_patterns(self):
        """Test pattern detection"""
        project_dir = self.create_sample_python_project()
        structure = {
            "directories": ["tests", "models", "views", "controllers"],
            "files": ["main.py", "requirements.txt"],
            "total_files": 10
        }

        patterns = self.analyzer._detect_patterns(project_dir, structure)

        assert "mvc" in patterns

    def test_calculate_complexity(self):
        """Test complexity calculation"""
        metrics = {
            "lines_of_code": 5000,
            "files_count": 50
        }
        dependencies = {
            "count": 25
        }

        complexity = self.analyzer._calculate_complexity(metrics, dependencies)

        assert complexity in ["low", "medium", "high", "very_high"]

    def test_generate_recommendations(self):
        """Test recommendation generation"""
        patterns = ["monolith"]
        metrics = {
            "lines_of_code": 15000,
            "test_files": 0
        }

        recommendations = self.analyzer._generate_recommendations(patterns, metrics)

        assert len(recommendations) > 0
        assert any("microservices" in rec.lower() for rec in recommendations)
        assert any("test" in rec.lower() for rec in recommendations)

    @pytest.mark.asyncio
    async def test_analyze_large_project(self):
        """Test analyzing a larger project"""
        project_dir = self.temp_dir / "large_project"
        project_dir.mkdir()

        # Create multiple files with imports for dependencies
        for i in range(25):  # Increased file count
            (project_dir / f"module_{i}.py").write_text(f'''"""Module {i}"""
import os
import sys
import json
import requests
import numpy
import pandas

def function_{i}():
    # This is a sample function with more lines
    result = []
    for j in range(10):
        result.append(j * {i})
        if j % 2 == 0:
            result.append(j + {i})
        else:
            result.append(j - {i})
    return result

class Class{i}:
    def __init__(self):
        self.value = {i}
        self.data = []
        self.config = {{"key": {i}}}

    def method_{i}(self):
        return self.value * 2

    def process_data(self):
        for item in self.data:
            yield item * self.value
''')

        result = await self.analyzer.analyze(project_dir)

        # Debug output
        print(f"Debug: files={result['metrics']['files_count']}, loc={result['metrics']['lines_of_code']}, deps={result['dependencies']['count']}, complexity={result['complexity_score']}")

        # Should detect as more complex
        assert result["metrics"]["files_count"] >= 25
        assert result["metrics"]["lines_of_code"] > 400
        assert result["complexity_score"] in ["medium", "high", "very_high"]

if __name__ == "__main__":
    # Run specific test
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "quick":
        # Quick test for development
        test = TestProjectAnalyzer()
        test.setup_method()
        asyncio.run(test.test_analyze_python_project())
        print("✅ Quick test passed!")
    else:
        # Run full test suite
        pytest.main([__file__, "-v"])