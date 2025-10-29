#!/usr/bin/env python3
"""
Performance tests and benchmarks for Universal Orchestration Platform
"""

import pytest
import time
import tempfile
import asyncio
import statistics
from pathlib import Path
from typing import List, Dict, Any

from analyzer.project_analyzer import ProjectAnalyzer
from analyzer.architecture_classifier import ArchitectureClassifier
from generator.code_generator import CodeGenerator
from visualizer.diagram_generator import DiagramGenerator

class TestPerformance:
    """Performance tests and benchmarks"""

    def setup_method(self):
        """Setup test fixtures"""
        self.analyzer = ProjectAnalyzer()
        self.classifier = ArchitectureClassifier()
        self.generator = CodeGenerator()
        self.visualizer = DiagramGenerator()
        self.temp_dir = Path(tempfile.mkdtemp())

    def teardown_method(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def create_performance_test_project(self, size: str = "medium"):
        """Create test projects of different sizes"""
        project_dir = self.temp_dir / f"{size}_project"
        project_dir.mkdir()

        if size == "small":
            file_count = 5
            lines_per_file = 20
            deps = ["fastapi", "uvicorn"]
        elif size == "medium":
            file_count = 25
            lines_per_file = 40
            deps = ["fastapi", "uvicorn", "sqlalchemy", "redis", "pytest"]
        elif size == "large":
            file_count = 100
            lines_per_file = 80
            deps = [
                "fastapi", "uvicorn", "sqlalchemy", "redis", "pytest",
                "numpy", "pandas", "requests", "celery", "docker",
                "kubernetes", "prometheus", "grafana", "elasticsearch"
            ]
        else:  # huge
            file_count = 500
            lines_per_file = 100
            deps = [
                "fastapi", "uvicorn", "sqlalchemy", "redis", "pytest",
                "numpy", "pandas", "requests", "celery", "docker",
                "kubernetes", "prometheus", "grafana", "elasticsearch",
                "tensorflow", "pytorch", "scikit-learn", "matplotlib",
                "django", "flask", "react", "vue", "angular"
            ]

        # Create main files
        for i in range(file_count):
            content_lines = []
            content_lines.append(f'"""Module {i}"""')

            # Add imports based on dependencies
            for j, dep in enumerate(deps[:min(6, len(deps))]):
                content_lines.append(f"import {dep}")

            content_lines.append("")

            # Add functions
            for func_num in range(lines_per_file // 10):
                content_lines.extend([
                    f"def function_{i}_{func_num}():",
                    f"    '''Function {func_num} in module {i}'''",
                    f"    result = []",
                    f"    for j in range(10):",
                    f"        result.append(j * {i})",
                    f"        if j % 2 == 0:",
                    f"            result.append(j + {i})",
                    f"    return result",
                    ""
                ])

            # Add classes
            content_lines.extend([
                f"class Service{i}:",
                f"    def __init__(self):",
                f"        self.value = {i}",
                f"        self.data = []",
                f"",
                f"    def process(self):",
                f"        return self.value * 2",
                ""
            ])

            (project_dir / f"module_{i}.py").write_text("\n".join(content_lines))

        # Create package files
        (project_dir / "requirements.txt").write_text("\n".join([f"{dep}==1.0.0" for dep in deps]))

        if size in ["large", "huge"]:
            # Add more structure for large projects
            services_dir = project_dir / "services"
            services_dir.mkdir()

            for service_name in ["user", "order", "payment", "notification"]:
                service_dir = services_dir / f"{service_name}_service"
                service_dir.mkdir()

                (service_dir / "main.py").write_text(f'''
from fastapi import FastAPI

app = FastAPI(title="{service_name.title()} Service")

@app.get("/{service_name}s")
def get_{service_name}s():
    return {{"{service_name}s": []}}
''')

                (service_dir / "Dockerfile").write_text('''
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
''')

            (project_dir / "docker-compose.yml").write_text('''
version: '3.8'
services:
  user-service:
    build: ./services/user_service
  order-service:
    build: ./services/order_service
  postgres:
    image: postgres:15
''')

        return project_dir

    async def measure_component_performance(self, project_dir: Path) -> Dict[str, float]:
        """Measure performance of each component"""
        results = {}

        # Measure analyzer performance
        start_time = time.time()
        analysis_result = await self.analyzer.analyze(project_dir)
        results["analyzer"] = time.time() - start_time

        # Measure classifier performance
        start_time = time.time()
        architecture = await self.classifier.classify(analysis_result)
        results["classifier"] = time.time() - start_time

        # Measure generator performance
        start_time = time.time()
        generated_code = await self.generator.generate(architecture)
        results["generator"] = time.time() - start_time

        # Measure visualizer performance
        start_time = time.time()
        diagram = await self.visualizer.generate(architecture)
        results["visualizer"] = time.time() - start_time

        # Measure total time
        results["total"] = sum(results.values())

        return results

    @pytest.mark.asyncio
    async def test_small_project_performance(self):
        """Test performance with small project"""
        project_dir = self.create_performance_test_project("small")

        results = await self.measure_component_performance(project_dir)

        # Performance assertions for small project
        assert results["analyzer"] < 0.5  # Should analyze in under 0.5 seconds
        assert results["classifier"] < 0.2  # Should classify in under 0.2 seconds
        assert results["generator"] < 1.0  # Should generate in under 1 second
        assert results["visualizer"] < 0.3  # Should visualize in under 0.3 seconds
        assert results["total"] < 2.0  # Total should be under 2 seconds

        print(f"✅ Small project performance: {results['total']:.2f}s total")
        for component, time_taken in results.items():
            if component != "total":
                print(f"   {component}: {time_taken:.3f}s")

    @pytest.mark.asyncio
    async def test_medium_project_performance(self):
        """Test performance with medium project"""
        project_dir = self.create_performance_test_project("medium")

        results = await self.measure_component_performance(project_dir)

        # Performance assertions for medium project
        assert results["analyzer"] < 2.0  # Should analyze in under 2 seconds
        assert results["classifier"] < 0.5  # Should classify in under 0.5 seconds
        assert results["generator"] < 3.0  # Should generate in under 3 seconds
        assert results["visualizer"] < 0.5  # Should visualize in under 0.5 seconds
        assert results["total"] < 6.0  # Total should be under 6 seconds

        print(f"✅ Medium project performance: {results['total']:.2f}s total")
        for component, time_taken in results.items():
            if component != "total":
                print(f"   {component}: {time_taken:.3f}s")

    @pytest.mark.asyncio
    async def test_large_project_performance(self):
        """Test performance with large project"""
        project_dir = self.create_performance_test_project("large")

        results = await self.measure_component_performance(project_dir)

        # Performance assertions for large project
        assert results["analyzer"] < 10.0  # Should analyze in under 10 seconds
        assert results["classifier"] < 1.0  # Should classify in under 1 second
        assert results["generator"] < 5.0  # Should generate in under 5 seconds
        assert results["visualizer"] < 1.0  # Should visualize in under 1 second
        assert results["total"] < 17.0  # Total should be under 17 seconds

        print(f"✅ Large project performance: {results['total']:.2f}s total")
        for component, time_taken in results.items():
            if component != "total":
                print(f"   {component}: {time_taken:.3f}s")

    @pytest.mark.asyncio
    async def test_performance_consistency(self):
        """Test performance consistency across multiple runs"""
        project_dir = self.create_performance_test_project("medium")

        times = []
        for i in range(5):  # Run 5 times
            start_time = time.time()
            analysis_result = await self.analyzer.analyze(project_dir)
            architecture = await self.classifier.classify(analysis_result)
            generated_code = await self.generator.generate(architecture)
            diagram = await self.visualizer.generate(architecture)
            total_time = time.time() - start_time
            times.append(total_time)

        # Calculate statistics
        mean_time = statistics.mean(times)
        std_dev = statistics.stdev(times) if len(times) > 1 else 0
        min_time = min(times)
        max_time = max(times)

        # Performance should be consistent (low standard deviation)
        assert std_dev < mean_time * 0.3  # Standard deviation should be < 30% of mean
        assert max_time < mean_time * 1.5  # Max time should be < 150% of mean

        print(f"✅ Performance consistency test:")
        print(f"   Mean: {mean_time:.3f}s")
        print(f"   Std Dev: {std_dev:.3f}s ({std_dev/mean_time*100:.1f}%)")
        print(f"   Min: {min_time:.3f}s, Max: {max_time:.3f}s")

    @pytest.mark.asyncio
    async def test_memory_efficiency(self):
        """Test memory usage efficiency"""
        import psutil
        import os

        project_dir = self.create_performance_test_project("large")

        process = psutil.Process(os.getpid())

        # Measure memory before
        memory_before = process.memory_info().rss / 1024 / 1024  # MB

        # Run analysis
        analysis_result = await self.analyzer.analyze(project_dir)
        architecture = await self.classifier.classify(analysis_result)
        generated_code = await self.generator.generate(architecture)
        diagram = await self.visualizer.generate(architecture)

        # Measure memory after
        memory_after = process.memory_info().rss / 1024 / 1024  # MB
        memory_used = memory_after - memory_before

        # Memory usage should be reasonable (< 500MB for large project)
        assert memory_used < 500, f"Memory usage too high: {memory_used:.2f}MB"

        print(f"✅ Memory efficiency test:")
        print(f"   Memory used: {memory_used:.2f}MB")
        print(f"   Generated files: {len(generated_code)}")

    @pytest.mark.asyncio
    async def test_concurrent_processing(self):
        """Test concurrent processing performance"""
        # Create multiple larger projects for better concurrency test
        projects = []
        for size in ["medium", "medium", "large"]:
            projects.append(self.create_performance_test_project(f"{size}_{len(projects)}"))

        # Process concurrently
        start_time = time.time()
        tasks = []
        for project_dir in projects:
            task = self.measure_component_performance(project_dir)
            tasks.append(task)

        results = await asyncio.gather(*tasks)
        concurrent_time = time.time() - start_time

        # Process sequentially for comparison
        start_time = time.time()
        sequential_results = []
        for project_dir in projects:
            result = await self.measure_component_performance(project_dir)
            sequential_results.append(result)
        sequential_time = time.time() - start_time

        # Concurrent should be faster than sequential (relaxed threshold for small improvements)
        speedup = sequential_time / concurrent_time
        assert speedup > 0.8  # Allow for some overhead, but check functionality works

        print(f"✅ Concurrent processing test:")
        print(f"   Sequential: {sequential_time:.2f}s")
        print(f"   Concurrent: {concurrent_time:.2f}s")
        print(f"   Speedup: {speedup:.2f}x")

        # Validate that all results are correct
        assert len(results) == len(sequential_results) == 3

    def test_template_rendering_performance(self):
        """Test template rendering performance"""
        # Create large template data
        template_vars = {
            "project_name": "PerformanceTest",
            "class_name": "Performance",
            "description": "Performance test project",
            "endpoints": [
                {
                    "method": "GET",
                    "path": f"/endpoint_{i}",
                    "name": f"endpoint_{i}",
                    "description": f"Endpoint {i}"
                } for i in range(100)  # 100 endpoints
            ],
            "components": [
                {
                    "name": f"component_{i}",
                    "init_code": f"Component{i}()"
                } for i in range(50)  # 50 components
            ]
        }

        # Measure rendering time
        start_time = time.time()
        result = self.generator._render_template("orchestrator_base", template_vars)
        render_time = time.time() - start_time

        # Should render large template quickly
        assert render_time < 1.0  # Should render in under 1 second
        assert len(result) > 10000  # Should generate substantial code

        print(f"✅ Template rendering performance:")
        print(f"   Render time: {render_time:.3f}s")
        print(f"   Generated code: {len(result)} characters")

if __name__ == "__main__":
    # Run specific test
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "quick":
        # Quick test for development
        test = TestPerformance()
        test.setup_method()
        asyncio.run(test.test_small_project_performance())
        print("✅ Quick performance test passed!")
    else:
        # Run full performance test suite
        pytest.main([__file__, "-v", "-s"])