"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.ProjectManager = void 0;
const fs = __importStar(require("fs-extra"));
const path = __importStar(require("path"));
const ProjectAnalyzer_1 = require("./ProjectAnalyzer");
class ProjectManager {
    constructor(baseDir = './') {
        this.projectsDir = path.join(baseDir, 'projects');
        this.projectAnalyzer = new ProjectAnalyzer_1.ProjectAnalyzer();
        this.ensureProjectsDirectory();
    }
    async ensureProjectsDirectory() {
        await fs.ensureDir(this.projectsDir);
    }
    async listProjects() {
        await this.ensureProjectsDirectory();
        const projects = [];
        const items = await fs.readdir(this.projectsDir, { withFileTypes: true });
        for (const item of items) {
            if (item.isDirectory()) {
                const projectPath = path.join(this.projectsDir, item.name);
                const projectInfo = await this.getProjectInfo(item.name, projectPath);
                projects.push(projectInfo);
            }
        }
        return projects.sort((a, b) => b.lastModified.getTime() - a.lastModified.getTime());
    }
    async getProject(projectId) {
        const projectPath = path.join(this.projectsDir, projectId);
        if (!await fs.pathExists(projectPath)) {
            return null;
        }
        return await this.getProjectInfo(projectId, projectPath);
    }
    async createProject(request) {
        const projectId = this.sanitizeProjectName(request.name);
        const projectPath = path.join(this.projectsDir, projectId);
        if (await fs.pathExists(projectPath)) {
            throw new Error(`Проект з назвою "${request.name}" вже існує`);
        }
        await fs.ensureDir(projectPath);
        // Створюємо базову структуру проекту
        await this.createProjectStructure(projectPath);
        // Додаємо метадані проекту
        const metadata = {
            name: request.name,
            description: request.description,
            createdAt: new Date().toISOString(),
            id: projectId
        };
        await fs.writeJson(path.join(projectPath, '.project-meta.json'), metadata, { spaces: 2 });
        // Якщо потрібно копіювати з шаблону
        if (request.copyFromTemplate) {
            await this.copyFromTemplate(projectPath, request.copyFromTemplate);
        }
        return await this.getProjectInfo(projectId, projectPath);
    }
    async deleteProject(projectId) {
        const projectPath = path.join(this.projectsDir, projectId);
        if (!await fs.pathExists(projectPath)) {
            return false;
        }
        await fs.remove(projectPath);
        return true;
    }
    async analyzeProject(projectId) {
        const projectPath = path.join(this.projectsDir, projectId);
        if (!await fs.pathExists(projectPath)) {
            throw new Error(`Проект "${projectId}" не знайдено`);
        }
        return await this.projectAnalyzer.analyzeProject(projectPath);
    }
    async updateProjectMetadata(projectId, updates) {
        const projectPath = path.join(this.projectsDir, projectId);
        const metaPath = path.join(projectPath, '.project-meta.json');
        if (!await fs.pathExists(projectPath)) {
            return null;
        }
        let metadata = {};
        if (await fs.pathExists(metaPath)) {
            metadata = await fs.readJson(metaPath);
        }
        metadata = {
            ...metadata,
            ...updates,
            updatedAt: new Date().toISOString()
        };
        await fs.writeJson(metaPath, metadata, { spaces: 2 });
        return await this.getProjectInfo(projectId, projectPath);
    }
    async uploadFile(projectId, fileName, content) {
        const projectPath = path.join(this.projectsDir, projectId);
        if (!await fs.pathExists(projectPath)) {
            throw new Error(`Проект "${projectId}" не знайдено`);
        }
        const filePath = path.join(projectPath, fileName);
        const dir = path.dirname(filePath);
        await fs.ensureDir(dir);
        await fs.writeFile(filePath, content);
        return filePath;
    }
    async deleteFile(projectId, fileName) {
        const projectPath = path.join(this.projectsDir, projectId);
        const filePath = path.join(projectPath, fileName);
        if (!await fs.pathExists(filePath)) {
            return false;
        }
        await fs.remove(filePath);
        return true;
    }
    async getProjectFiles(projectId) {
        const projectPath = path.join(this.projectsDir, projectId);
        if (!await fs.pathExists(projectPath)) {
            return [];
        }
        return await this.getFilesRecursively(projectPath, projectPath);
    }
    getProjectPath(projectId) {
        return path.join(this.projectsDir, projectId);
    }
    async getProjectInfo(projectId, projectPath) {
        const stats = await fs.stat(projectPath);
        const metaPath = path.join(projectPath, '.project-meta.json');
        let metadata = {};
        if (await fs.pathExists(metaPath)) {
            try {
                metadata = await fs.readJson(metaPath);
            }
            catch (error) {
                console.warn(`Помилка читання метаданих проекту ${projectId}:`, error);
            }
        }
        // Швидкий аналіз для отримання базової інформації
        const analysis = await this.projectAnalyzer.analyzeProject(projectPath);
        return {
            id: projectId,
            name: metadata.name || projectId,
            path: projectPath,
            description: metadata.description,
            createdAt: metadata.createdAt ? new Date(metadata.createdAt) : stats.birthtime,
            lastModified: stats.mtime,
            templatesCount: analysis.templates.length,
            documentTypes: analysis.documentTypes
        };
    }
    async createProjectStructure(projectPath) {
        // Створюємо базову структуру папок
        await fs.ensureDir(path.join(projectPath, 'templates'));
        await fs.ensureDir(path.join(projectPath, 'documents'));
        await fs.ensureDir(path.join(projectPath, 'generated-reports'));
        // Створюємо README файл
        const readmeContent = `# Проект

Цей проект створено за допомогою Documentator.

## Структура

- \`templates/\` - шаблони документів
- \`documents/\` - основні документи
- \`generated-reports/\` - згенеровані звіти

## Використання

1. Додайте свої шаблони до папки \`templates/\`
2. Використайте Documentator для генерації звітів
`;
        await fs.writeFile(path.join(projectPath, 'README.md'), readmeContent, 'utf-8');
    }
    async copyFromTemplate(projectPath, templateName) {
        const templatesDir = path.join(__dirname, '..', '..', 'project-templates');
        const templatePath = path.join(templatesDir, templateName);
        if (await fs.pathExists(templatePath)) {
            await fs.copy(templatePath, projectPath, {
                filter: (src) => !path.basename(src).startsWith('.')
            });
        }
    }
    async getFilesRecursively(dirPath, basePath) {
        const files = [];
        const items = await fs.readdir(dirPath, { withFileTypes: true });
        for (const item of items) {
            const fullPath = path.join(dirPath, item.name);
            if (item.name.startsWith('.')) {
                continue; // Пропускаємо системні файли
            }
            if (item.isDirectory()) {
                const subFiles = await this.getFilesRecursively(fullPath, basePath);
                files.push(...subFiles);
            }
            else {
                const relativePath = path.relative(basePath, fullPath);
                files.push(relativePath);
            }
        }
        return files;
    }
    sanitizeProjectName(name) {
        return name
            .toLowerCase()
            .replace(/[^a-z0-9\u0400-\u04ff\s-]/g, '') // Дозволяємо кирилицю
            .replace(/\s+/g, '-')
            .replace(/-+/g, '-')
            .replace(/^-|-$/g, '')
            .substring(0, 50);
    }
}
exports.ProjectManager = ProjectManager;
//# sourceMappingURL=ProjectManager.js.map