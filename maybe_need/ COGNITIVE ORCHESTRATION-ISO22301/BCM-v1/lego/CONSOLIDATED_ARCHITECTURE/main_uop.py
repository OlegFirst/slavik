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
import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, List

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

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

# Pydantic models for API requests
class DirectoryAnalysisRequest(BaseModel):
    directory_path: str
    recursive: bool = True
    exclude_patterns: Optional[List[str]] = [
        "node_modules", ".git", "__pycache__", ".env", "venv", "build", "dist",
        "Library/Mobile Documents", "Library/CloudStorage", ".Trash",
        "Applications", "System", "private", "usr", "bin", "sbin", "var/log"
    ]

class GitHubAnalysisRequest(BaseModel):
    repo_url: str
    branch: str = "main"
    access_token: Optional[str] = None

class ProjectAnalysisResponse(BaseModel):
    task_id: str
    status: str
    message: Optional[str] = None

@app.get("/", response_class=HTMLResponse)
async def root():
    """Enhanced multi-channel interface"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Universal Orchestration Platform</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                max-width: 1000px; margin: 0 auto; padding: 20px;
                background: #f8fafc; color: #1f2937;
            }
            .header {
                text-align: center; margin-bottom: 30px;
                background: white; padding: 30px; border-radius: 12px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            .header h1 {
                color: #2563eb; margin: 0 0 10px 0; font-size: 2.5rem;
            }
            .methods-grid {
                display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px; margin-bottom: 30px;
            }
            .method-card {
                background: white; padding: 25px; border-radius: 12px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                transition: transform 0.2s ease;
            }
            .method-card:hover { transform: translateY(-2px); }
            .method-header {
                display: flex; align-items: center; margin-bottom: 15px;
            }
            .method-icon {
                font-size: 1.5rem; margin-right: 10px; color: #2563eb;
            }
            .method-title {
                font-size: 1.2rem; font-weight: 600; margin: 0;
            }
            .method-desc {
                color: #6b7280; margin-bottom: 20px; font-size: 0.9rem;
            }
            .upload-area {
                border: 2px dashed #d1d5db; padding: 30px; text-align: center;
                border-radius: 8px; cursor: pointer; transition: border-color 0.2s;
                margin-bottom: 15px;
            }
            .upload-area:hover { border-color: #2563eb; background: #f8faff; }
            .upload-area.dragover { border-color: #2563eb; background: #eff6ff; }
            .input-group { margin-bottom: 15px; }
            .input-label {
                display: block; margin-bottom: 5px; font-weight: 500;
                color: #374151; font-size: 0.9rem;
            }
            .text-input {
                width: 100%; padding: 10px; border: 2px solid #d1d5db;
                border-radius: 6px; font-size: 1rem;
                transition: border-color 0.2s;
            }
            .text-input:focus {
                outline: none; border-color: #2563eb;
                box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
            }
            .action-btn {
                background: #2563eb; color: white; border: none;
                padding: 12px 20px; border-radius: 6px;
                cursor: pointer; font-size: 1rem; font-weight: 500;
                width: 100%; transition: background-color 0.2s;
            }
            .action-btn:hover { background: #1d4ed8; }
            .action-btn:disabled { background: #9ca3af; cursor: not-allowed; }
            .btn-secondary {
                background: #6b7280; color: white; border: none;
                padding: 8px 16px; border-radius: 4px;
                cursor: pointer; font-size: 0.9rem; font-weight: 500;
                transition: background-color 0.2s; white-space: nowrap;
            }
            .btn-secondary:hover { background: #4b5563; }
            .progress {
                width: 100%; background: #e5e7eb; margin: 20px 0;
                border-radius: 10px; overflow: hidden; display: none;
            }
            .progress-bar {
                height: 20px; background: #2563eb; width: 0%;
                transition: width 0.3s ease;
            }
            .progress-text {
                text-align: center; margin-top: 10px; color: #6b7280;
            }
            .results {
                margin: 20px 0; padding: 25px; background: white;
                border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                display: none;
            }
            .result-item {
                background: #f0f9ff; padding: 15px; margin: 10px 0;
                border-radius: 8px; border-left: 4px solid #2563eb;
            }
            .download-btn {
                background: #10b981; color: white; padding: 12px 20px;
                text-decoration: none; border-radius: 6px;
                display: inline-block; margin-top: 15px; font-weight: 500;
            }
            .download-btn:hover { background: #059669; }
            .error-msg {
                background: #fef2f2; color: #dc2626; padding: 15px;
                border-radius: 8px; border-left: 4px solid #dc2626;
                margin: 15px 0; display: none;
            }
            .features {
                display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px; margin-top: 30px;
            }
            .feature-card {
                background: white; padding: 20px; border-radius: 12px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1); text-align: center;
            }
            .feature-icon { font-size: 2rem; margin-bottom: 10px; color: #2563eb; }
            .feature-title { font-weight: 600; margin-bottom: 10px; }
            .feature-desc { color: #6b7280; font-size: 0.9rem; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🚀 Universal Orchestration Platform</h1>
            <p>AI-powered multi-channel project analysis and intelligent architecture generation</p>
        </div>

        <div class="methods-grid">
            <!-- ZIP Upload Method -->
            <div class="method-card">
                <div class="method-header">
                    <div class="method-icon">📁</div>
                    <h3 class="method-title">ZIP File Upload</h3>
                </div>
                <div class="method-desc">
                    Upload a ZIP archive of your project for comprehensive analysis
                </div>
                <div class="upload-area" id="uploadArea">
                    <div style="font-size: 1.5rem; margin-bottom: 10px;">📁</div>
                    <div>Drop ZIP file here or click to browse</div>
                    <input type="file" id="fileInput" accept=".zip" style="display: none">
                </div>
                <button class="action-btn" onclick="document.getElementById('fileInput').click()">
                    Select ZIP File
                </button>
            </div>

            <!-- Directory Analysis Method -->
            <div class="method-card">
                <div class="method-header">
                    <div class="method-icon">📂</div>
                    <h3 class="method-title">Directory Analysis</h3>
                </div>
                <div class="method-desc">
                    Analyze a local directory directly
                </div>
                <div class="input-group">
                    <label class="input-label" for="directoryPath">Directory Path:</label>
                    <div style="display: flex; gap: 10px; align-items: center;">
                        <input type="text" id="directoryPath" class="text-input"
                               placeholder="/path/to/your/project" value="/Users/MD/ COGNITIVE ORCHESTRATION-ISO22301/BCM-v1/lego/CONSOLIDATED_ARCHITECTURE" style="flex: 1;">
                        <input type="file" id="directoryChooser" webkitdirectory directory multiple style="display: none;">
                        <button type="button" onclick="chooseDirectory()" class="btn btn-secondary">
                            📁 Choose Directory
                        </button>
                    </div>
                </div>
                <div class="input-group">
                    <label class="input-label" for="excludePatterns">Exclude Patterns:</label>
                    <input type="text" id="excludePatterns" class="text-input"
                           placeholder="node_modules,*.log,dist">
                </div>
                <button class="action-btn" onclick="analyzeDirectory()">
                    Analyze Directory
                </button>
            </div>

            <!-- GitHub Integration Method -->
            <div class="method-card">
                <div class="method-header">
                    <div class="method-icon">🐙</div>
                    <h3 class="method-title">GitHub Repository</h3>
                </div>
                <div class="method-desc">
                    Analyze a GitHub repository directly
                </div>
                <div class="input-group">
                    <label class="input-label" for="githubUrl">Repository URL:</label>
                    <input type="text" id="githubUrl" class="text-input"
                           placeholder="https://github.com/user/repo">
                </div>
                <div class="input-group">
                    <label class="input-label" for="githubBranch">Branch:</label>
                    <input type="text" id="githubBranch" class="text-input"
                           placeholder="main">
                </div>
                <div class="input-group">
                    <label class="input-label" for="githubToken">Access Token (optional):</label>
                    <input type="password" id="githubToken" class="text-input"
                           placeholder="ghp_...">
                </div>
                <button class="action-btn" onclick="analyzeGitHub()">
                    Analyze Repository
                </button>
            </div>
        </div>

        <div class="error-msg" id="errorMsg"></div>

        <div class="progress" id="progress">
            <div class="progress-bar" id="progressBar"></div>
            <div class="progress-text" id="progressText">Initializing...</div>
        </div>

        <div class="results" id="results">
            <h3>🎉 Processing Complete!</h3>
            <div id="resultsList"></div>
            <a href="#" class="download-btn" id="downloadBtn">Download Generated Files</a>
        </div>

        <div class="features">
            <div class="feature-card">
                <div class="feature-icon">🔍</div>
                <div class="feature-title">Multi-Channel Input</div>
                <div class="feature-desc">ZIP files, directories, and GitHub repos</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon">🤖</div>
                <div class="feature-title">AI Generation</div>
                <div class="feature-desc">Claude AI-powered intelligent code generation</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon">📊</div>
                <div class="feature-title">Visualization</div>
                <div class="feature-desc">Professional architecture diagrams</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon">⚡</div>
                <div class="feature-title">ML Optimization</div>
                <div class="feature-desc">Performance predictions and insights</div>
            </div>
        </div>

        <script>
            const uploadArea = document.getElementById('uploadArea');
            const fileInput = document.getElementById('fileInput');
            const progress = document.getElementById('progress');
            const progressBar = document.getElementById('progressBar');
            const progressText = document.getElementById('progressText');
            const results = document.getElementById('results');
            const downloadBtn = document.getElementById('downloadBtn');
            const errorMsg = document.getElementById('errorMsg');
            const resultsList = document.getElementById('resultsList');

            // Drag and drop for ZIP upload
            uploadArea.addEventListener('dragover', (e) => {
                e.preventDefault();
                uploadArea.classList.add('dragover');
            });

            uploadArea.addEventListener('dragleave', () => {
                uploadArea.classList.remove('dragover');
            });

            uploadArea.addEventListener('drop', (e) => {
                e.preventDefault();
                uploadArea.classList.remove('dragover');
                const files = e.dataTransfer.files;
                if (files.length > 0) {
                    handleFileUpload(files[0]);
                }
            });

            uploadArea.addEventListener('click', () => {
                fileInput.click();
            });

            fileInput.addEventListener('change', (e) => {
                if (e.target.files.length > 0) {
                    handleFileUpload(e.target.files[0]);
                }
            });

            // ZIP file upload
            async function handleFileUpload(file) {
                if (!file.name.endsWith('.zip')) {
                    showError('Please select a ZIP file.');
                    return;
                }

                hideError();
                showProgress();

                const formData = new FormData();
                formData.append('file', file);

                try {
                    const response = await fetch('/analyze-project', {
                        method: 'POST',
                        body: formData
                    });

                    if (!response.ok) throw new Error('Upload failed');

                    const result = await response.json();
                    if (result.task_id) {
                        pollTaskStatus(result.task_id);
                    }
                } catch (error) {
                    showError('Upload failed: ' + error.message);
                    hideProgress();
                }
            }

            // Directory analysis
            async function analyzeDirectory() {
                const directoryPath = document.getElementById('directoryPath').value.trim();
                const excludePatterns = document.getElementById('excludePatterns').value.trim();

                if (!directoryPath) {
                    showError('Please enter a directory path.');
                    return;
                }

                hideError();
                showProgress();

                try {
                    const requestData = {
                        directory_path: directoryPath,
                        exclude_patterns: excludePatterns ? excludePatterns.split(',').map(p => p.trim()) : []
                    };

                    const response = await fetch('/analyze-directory', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(requestData)
                    });

                    if (!response.ok) throw new Error('Directory analysis failed');

                    const result = await response.json();
                    if (result.task_id) {
                        pollTaskStatus(result.task_id);
                    }
                } catch (error) {
                    showError('Directory analysis failed: ' + error.message);
                    hideProgress();
                }
            }

            // GitHub analysis
            async function analyzeGitHub() {
                const githubUrl = document.getElementById('githubUrl').value.trim();
                const githubBranch = document.getElementById('githubBranch').value.trim();
                const githubToken = document.getElementById('githubToken').value.trim();

                if (!githubUrl) {
                    showError('Please enter a GitHub repository URL.');
                    return;
                }

                hideError();
                showProgress();

                try {
                    const requestData = {
                        repository_url: githubUrl,
                        branch: githubBranch || 'main',
                        access_token: githubToken || null
                    };

                    const response = await fetch('/analyze-github', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(requestData)
                    });

                    if (!response.ok) throw new Error('GitHub analysis failed');

                    const result = await response.json();
                    if (result.task_id) {
                        pollTaskStatus(result.task_id);
                    }
                } catch (error) {
                    showError('GitHub analysis failed: ' + error.message);
                    hideProgress();
                }
            }

            // Task status polling
            async function pollTaskStatus(taskId) {
                const maxAttempts = 60; // 5 minutes max
                let attempts = 0;

                const poll = async () => {
                    try {
                        const response = await fetch(`/status/${taskId}`);
                        const status = await response.json();

                        updateProgress(status.progress, status.message);

                        if (status.status === 'completed') {
                            showResults(status.result);
                        } else if (status.status === 'failed') {
                            showError('Processing failed: ' + status.error);
                            hideProgress();
                        } else {
                            attempts++;
                            if (attempts < maxAttempts) {
                                setTimeout(poll, 5000);
                            } else {
                                showError('Processing timeout. Please try again.');
                                hideProgress();
                            }
                        }
                    } catch (error) {
                        showError('Status check failed: ' + error.message);
                        hideProgress();
                    }
                };

                poll();
            }

            function updateProgress(percent, message) {
                progressBar.style.width = percent + '%';
                progressText.textContent = message;
            }

            function showProgress() {
                progress.style.display = 'block';
                results.style.display = 'none';
                progressBar.style.width = '0%';
                progressText.textContent = 'Initializing...';
            }

            function hideProgress() {
                progress.style.display = 'none';
            }

            function showResults(result) {
                hideProgress();

                resultsList.innerHTML = '';

                if (result.generated_files) {
                    Object.keys(result.generated_files).forEach(filename => {
                        const item = document.createElement('div');
                        item.className = 'result-item';
                        item.innerHTML = `
                            <strong>${filename}</strong>
                            <div style="font-size: 0.9rem; color: #6b7280; margin-top: 5px;">
                                Generated successfully
                            </div>
                        `;
                        resultsList.appendChild(item);
                    });
                }

                if (result.task_id) {
                    downloadBtn.href = `/download/${result.task_id}`;
                }

                results.style.display = 'block';
            }

            function showError(message) {
                errorMsg.textContent = message;
                errorMsg.style.display = 'block';
            }

            function hideError() {
                errorMsg.style.display = 'none';
            }

            function chooseDirectory() {
                const directoryChooser = document.getElementById('directoryChooser');
                directoryChooser.click();

                directoryChooser.addEventListener('change', function(e) {
                    if (e.target.files.length > 0) {
                        // Get the first file to extract the directory path
                        const firstFile = e.target.files[0];
                        // webkitRelativePath includes the full path from selected directory
                        const fullPath = firstFile.webkitRelativePath;
                        // Extract just the directory name (first part before /)
                        const directoryPath = fullPath.split('/')[0];

                        // For security reasons, browsers don't give full file system paths
                        // So we'll show the directory name and let user know
                        document.getElementById('directoryPath').value = directoryPath;

                        // Show info message
                        const pathInput = document.getElementById('directoryPath');
                        pathInput.title = `Selected: ${e.target.files.length} files from directory "${directoryPath}"`;
                        pathInput.style.borderColor = '#10b981';
                        pathInput.style.backgroundColor = '#f0fdf4';

                        // Store files for upload
                        window.selectedFiles = e.target.files;
                    }
                }, { once: true }); // Remove listener after first use
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

    # Read file content before background task
    file_content = await file.read()
    file_name = file.filename

    # Create task
    task_id = f"task_{len(tasks)}_{asyncio.get_event_loop().time()}"
    tasks[task_id] = {
        "status": "started",
        "progress": 0,
        "message": "Initializing...",
        "result": None,
        "error": None
    }

    # Start background processing with file content
    background_tasks.add_task(process_project, task_id, file_content, file_name)

    return {"task_id": task_id, "status": "started"}

@app.get("/task-status/{task_id}")
async def get_task_status(task_id: str):
    """Get task processing status"""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")

    return tasks[task_id]

@app.post("/analyze-directory", response_model=ProjectAnalysisResponse)
async def analyze_directory(
    request: DirectoryAnalysisRequest,
    background_tasks: BackgroundTasks
):
    """Analyze project directory directly"""

    # Validate directory exists
    directory_path = Path(request.directory_path)
    if not directory_path.exists():
        raise HTTPException(status_code=400, detail=f"Directory does not exist: {request.directory_path}")

    if not directory_path.is_dir():
        raise HTTPException(status_code=400, detail=f"Path is not a directory: {request.directory_path}")

    # Create task
    task_id = f"dir_task_{len(tasks)}_{asyncio.get_event_loop().time()}"
    tasks[task_id] = {
        "status": "started",
        "progress": 0,
        "message": "Initializing directory analysis...",
        "result": None,
        "error": None,
        "source_type": "directory",
        "source_path": str(directory_path)
    }

    # Start background processing
    background_tasks.add_task(
        process_directory_project,
        task_id,
        directory_path,
        request.exclude_patterns
    )

    return ProjectAnalysisResponse(
        task_id=task_id,
        status="started",
        message="Directory analysis started"
    )

@app.post("/analyze-github", response_model=ProjectAnalysisResponse)
async def analyze_github(
    request: GitHubAnalysisRequest,
    background_tasks: BackgroundTasks
):
    """Analyze GitHub repository"""

    # Validate GitHub URL
    if not ("github.com" in request.repo_url or "gitlab.com" in request.repo_url):
        raise HTTPException(status_code=400, detail="Only GitHub and GitLab repositories are supported")

    # Create task
    task_id = f"git_task_{len(tasks)}_{asyncio.get_event_loop().time()}"
    tasks[task_id] = {
        "status": "started",
        "progress": 0,
        "message": "Cloning repository...",
        "result": None,
        "error": None,
        "source_type": "github",
        "source_url": request.repo_url
    }

    # Start background processing
    background_tasks.add_task(
        process_github_project,
        task_id,
        request.repo_url,
        request.branch,
        request.access_token
    )

    return ProjectAnalysisResponse(
        task_id=task_id,
        status="started",
        message="Repository cloning started"
    )

async def process_project(task_id: str, file_content: bytes, file_name: str):
    """Background task for project processing"""
    try:
        # Update progress
        tasks[task_id].update({"progress": 10, "message": "Extracting project..."})

        # Extract ZIP file
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir) / "project"
            project_path.mkdir()

            # Save and extract ZIP
            zip_path = project_path / file_name
            with open(zip_path, "wb") as buffer:
                buffer.write(file_content)

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

async def process_directory_project(task_id: str, directory_path: Path, exclude_patterns: List[str]):
    """Background task for directory processing"""
    try:
        # Update progress
        tasks[task_id].update({"progress": 10, "message": "Scanning directory..."})

        # Count files for progress tracking
        file_count = sum(1 for _ in directory_path.rglob("*") if _.is_file())
        logger.info(f"Found {file_count} files to analyze")

        # Update progress
        tasks[task_id].update({"progress": 30, "message": "Analyzing code structure..."})

        # Analyze project directly from directory
        analysis_result = await project_analyzer.analyze(directory_path)

        # Update progress
        tasks[task_id].update({"progress": 60, "message": "Classifying architecture..."})

        # Classify architecture
        architecture = await architecture_classifier.classify(analysis_result)

        # Update progress
        tasks[task_id].update({"progress": 80, "message": "Generating AI-enhanced code..."})

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
            "download_url": f"/download/{task_id}",
            "source_info": {
                "type": "directory",
                "path": str(directory_path),
                "file_count": file_count
            }
        }

        tasks[task_id].update({
            "status": "completed",
            "result": result,
            "generated_code": generated_code
        })

        logger.info(f"✅ Directory analysis completed: {task_id}")

    except Exception as e:
        logger.error(f"❌ Directory analysis failed: {task_id}, error: {e}")
        tasks[task_id].update({
            "status": "failed",
            "error": str(e),
            "progress": 0
        })

async def process_github_project(task_id: str, repo_url: str, branch: str, access_token: Optional[str]):
    """Background task for GitHub repository processing"""
    try:
        import subprocess
        import shutil

        # Update progress
        tasks[task_id].update({"progress": 10, "message": "Cloning repository..."})

        # Create temporary directory for cloning
        with tempfile.TemporaryDirectory() as temp_dir:
            clone_path = Path(temp_dir) / "repo"

            # Prepare git clone command
            clone_cmd = ["git", "clone", "--depth", "1", "--branch", branch]

            # Add authentication if token provided
            if access_token:
                # For GitHub: https://token@github.com/user/repo.git
                auth_url = repo_url.replace("https://", f"https://{access_token}@")
                clone_cmd.extend([auth_url, str(clone_path)])
            else:
                clone_cmd.extend([repo_url, str(clone_path)])

            # Execute git clone
            result = subprocess.run(clone_cmd, capture_output=True, text=True, timeout=300)

            if result.returncode != 0:
                raise Exception(f"Git clone failed: {result.stderr}")

            # Update progress
            tasks[task_id].update({"progress": 30, "message": "Repository cloned, analyzing..."})

            # Check repository size
            file_count = sum(1 for _ in clone_path.rglob("*") if _.is_file())
            if file_count > 15000:  # Higher limit for repos
                logger.warning(f"Large repository detected: {file_count} files")

            # Analyze project
            analysis_result = await project_analyzer.analyze(clone_path)

            # Update progress
            tasks[task_id].update({"progress": 60, "message": "Classifying architecture..."})

            # Classify architecture
            architecture = await architecture_classifier.classify(analysis_result)

            # Update progress
            tasks[task_id].update({"progress": 80, "message": "Generating AI-enhanced code..."})

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
                "download_url": f"/download/{task_id}",
                "source_info": {
                    "type": "github",
                    "url": repo_url,
                    "branch": branch,
                    "file_count": file_count
                }
            }

            tasks[task_id].update({
                "status": "completed",
                "result": result,
                "generated_code": generated_code
            })

            logger.info(f"✅ GitHub analysis completed: {task_id}")

    except subprocess.TimeoutExpired:
        logger.error(f"❌ GitHub clone timeout: {task_id}")
        tasks[task_id].update({
            "status": "failed",
            "error": "Repository clone timeout (5 minutes limit)",
            "progress": 0
        })
    except Exception as e:
        logger.error(f"❌ GitHub analysis failed: {task_id}, error: {e}")
        tasks[task_id].update({
            "status": "failed",
            "error": str(e),
            "progress": 0
        })

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