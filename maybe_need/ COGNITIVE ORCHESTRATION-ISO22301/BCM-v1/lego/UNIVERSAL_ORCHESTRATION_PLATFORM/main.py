#!/usr/bin/env python3
"""
Universal Intelligent Orchestration Platform
Main FastAPI application for project analysis and architecture generation

Phase 1: Core Engine Implementation
"""

import asyncio
import logging
import zipfile
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

# Our analyzers
from analyzer.project_analyzer import ProjectAnalyzer
from analyzer.architecture_classifier import ArchitectureClassifier
from generator.code_generator import CodeGenerator
from visualizer.diagram_generator import DiagramGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Universal Orchestration Platform",
    description="AI-powered project analysis and architecture generation",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global components
project_analyzer = ProjectAnalyzer()
architecture_classifier = ArchitectureClassifier()
code_generator = CodeGenerator()
diagram_generator = DiagramGenerator()

# In-memory task storage (replace with Redis in production)
tasks = {}

@app.get("/", response_class=HTMLResponse)
async def root():
    """Main page with upload interface"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Universal Orchestration Platform</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            .upload-area { border: 2px dashed #ccc; padding: 40px; text-align: center; margin: 20px 0; }
            .upload-area:hover { border-color: #007bff; }
            .results { margin: 20px 0; padding: 20px; background: #f8f9fa; }
            .button { background: #007bff; color: white; padding: 10px 20px; border: none; cursor: pointer; }
            .progress { width: 100%; background: #f0f0f0; margin: 10px 0; }
            .progress-bar { height: 20px; background: #007bff; width: 0%; transition: width 0.3s; }
        </style>
    </head>
    <body>
        <h1>🚀 Universal Orchestration Platform</h1>
        <p>Upload your project and get AI-generated architecture!</p>

        <div class="upload-area" onclick="document.getElementById('fileInput').click()">
            <input type="file" id="fileInput" accept=".zip" style="display: none" onchange="uploadFile()">
            <h3>📦 Drop your project ZIP here or click to upload</h3>
            <p>Supports: Node.js, Python, Java projects</p>
        </div>

        <div id="progress" class="progress" style="display: none;">
            <div id="progressBar" class="progress-bar"></div>
        </div>

        <div id="results" class="results" style="display: none;">
            <h3>📊 Analysis Results</h3>
            <div id="analysisResults"></div>
            <h3>🎨 Architecture Diagram</h3>
            <div id="diagramResults"></div>
            <h3>💻 Generated Code</h3>
            <div id="codeResults"></div>
        </div>

        <script>
            async function uploadFile() {
                const fileInput = document.getElementById('fileInput');
                const file = fileInput.files[0];
                if (!file) return;

                document.getElementById('progress').style.display = 'block';
                document.getElementById('results').style.display = 'none';

                const formData = new FormData();
                formData.append('file', file);

                try {
                    updateProgress(10, 'Uploading project...');
                    const response = await fetch('/analyze-project', {
                        method: 'POST',
                        body: formData
                    });

                    if (!response.ok) throw new Error('Upload failed');

                    const result = await response.json();

                    if (result.task_id) {
                        pollTaskStatus(result.task_id);
                    } else {
                        showResults(result);
                    }
                } catch (error) {
                    alert('Error: ' + error.message);
                    document.getElementById('progress').style.display = 'none';
                }
            }

            async function pollTaskStatus(taskId) {
                const interval = setInterval(async () => {
                    try {
                        const response = await fetch(`/task-status/${taskId}`);
                        const status = await response.json();

                        updateProgress(status.progress, status.message);

                        if (status.status === 'completed') {
                            clearInterval(interval);
                            showResults(status.result);
                        } else if (status.status === 'failed') {
                            clearInterval(interval);
                            alert('Analysis failed: ' + status.error);
                            document.getElementById('progress').style.display = 'none';
                        }
                    } catch (error) {
                        clearInterval(interval);
                        alert('Error checking status: ' + error.message);
                        document.getElementById('progress').style.display = 'none';
                    }
                }, 1000);
            }

            function updateProgress(percent, message) {
                document.getElementById('progressBar').style.width = percent + '%';
                document.getElementById('progressBar').textContent = message;
            }

            function showResults(result) {
                document.getElementById('progress').style.display = 'none';
                document.getElementById('results').style.display = 'block';

                document.getElementById('analysisResults').innerHTML = `
                    <pre>${JSON.stringify(result.analysis, null, 2)}</pre>
                `;

                if (result.diagram) {
                    document.getElementById('diagramResults').innerHTML = result.diagram;
                }

                if (result.download_url) {
                    document.getElementById('codeResults').innerHTML = `
                        <a href="${result.download_url}" class="button">📥 Download Generated Code</a>
                    `;
                }
            }
        </script>
    </body>
    </html>
    """

@app.post("/analyze-project")
async def analyze_project(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """Upload and analyze project"""

    if not file.filename.endswith('.zip'):
        raise HTTPException(status_code=400, detail="Only ZIP files are supported")

    # Create task
    task_id = f"task_{len(tasks)}_{asyncio.get_event_loop().time()}"
    tasks[task_id] = {
        "status": "started",
        "progress": 0,
        "message": "Initializing...",
        "result": None,
        "error": None
    }

    # Start background processing
    background_tasks.add_task(process_project, task_id, file)

    return {"task_id": task_id, "status": "started"}

@app.get("/task-status/{task_id}")
async def get_task_status(task_id: str):
    """Get task processing status"""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")

    return tasks[task_id]

async def process_project(task_id: str, file: UploadFile):
    """Background task for project processing"""
    try:
        # Update progress
        tasks[task_id].update({"progress": 10, "message": "Extracting project..."})

        # Extract ZIP file
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir) / "project"
            project_path.mkdir()

            # Save and extract ZIP
            zip_path = project_path / file.filename
            with open(zip_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)

            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(project_path)

            # Remove ZIP file, keep extracted content
            zip_path.unlink()

            # Update progress
            tasks[task_id].update({"progress": 30, "message": "Analyzing code structure..."})

            # Analyze project
            analysis_result = await project_analyzer.analyze(project_path)

            # Update progress
            tasks[task_id].update({"progress": 60, "message": "Classifying architecture..."})

            # Classify architecture
            architecture = await architecture_classifier.classify(analysis_result)

            # Update progress
            tasks[task_id].update({"progress": 80, "message": "Generating code..."})

            # Generate code
            generated_code = await code_generator.generate(architecture)

            # Generate diagram
            diagram = await diagram_generator.generate(architecture)

            # Update progress
            tasks[task_id].update({"progress": 100, "message": "Complete!"})

            # Store result
            result = {
                "analysis": analysis_result,
                "architecture": architecture,
                "diagram": diagram,
                "download_url": f"/download/{task_id}"
            }

            tasks[task_id].update({
                "status": "completed",
                "result": result,
                "generated_code": generated_code
            })

    except Exception as e:
        logger.error(f"Task {task_id} failed: {e}")
        tasks[task_id].update({
            "status": "failed",
            "error": str(e)
        })

@app.get("/download/{task_id}")
async def download_generated_code(task_id: str):
    """Download generated code"""
    if task_id not in tasks or tasks[task_id]["status"] != "completed":
        raise HTTPException(status_code=404, detail="Generated code not found")

    # Create ZIP with generated code
    with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as temp_file:
        generated_code = tasks[task_id]["generated_code"]

        with zipfile.ZipFile(temp_file.name, 'w') as zip_file:
            for file_path, content in generated_code.items():
                zip_file.writestr(file_path, content)

        return FileResponse(
            temp_file.name,
            media_type='application/zip',
            filename=f'generated_orchestrators_{task_id}.zip'
        )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "Universal Orchestration Platform is running",
        "version": "1.0.0",
        "components": {
            "analyzer": "ready",
            "classifier": "ready",
            "generator": "ready",
            "visualizer": "ready"
        }
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Universal Orchestration Platform...")
    print("🌐 Web interface: http://localhost:8000")
    print("📚 API docs: http://localhost:8000/docs")

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )