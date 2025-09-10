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
exports.SimpleProjectManager = void 0;
const fs = __importStar(require("fs-extra"));
const path = __importStar(require("path"));
const ProjectAnalyzer_1 = require("./ProjectAnalyzer");
const TemplateGenerator_1 = require("./TemplateGenerator");
class SimpleProjectManager {
    constructor(baseDir) {
        if (baseDir) {
            this.projectsDir = path.join(baseDir, 'projects');
        }
        else {
            // Використовуємо папку projects всередині Documentator
            // __dirname вказує на dist/core, тому йдемо на 2 рівні вгору до кореня проекту
            const documentatorRoot = path.resolve(__dirname, '..', '..');
            this.projectsDir = path.join(documentatorRoot, 'projects');
        }
        this.projectAnalyzer = new ProjectAnalyzer_1.ProjectAnalyzer();
        this.templateGenerator = new TemplateGenerator_1.TemplateGenerator();
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
                projects.push({
                    id: item.name,
                    name: item.name,
                    path: projectPath
                });
            }
        }
        return projects;
    }
    async analyzeProject(projectId) {
        const projectPath = path.join(this.projectsDir, projectId);
        if (!await fs.pathExists(projectPath)) {
            throw new Error(`Проект "${projectId}" не знайдено`);
        }
        return await this.projectAnalyzer.analyzeProject(projectPath);
    }
    getProjectPath(projectId) {
        return path.join(this.projectsDir, projectId);
    }
    async projectExists(projectId) {
        const projectPath = path.join(this.projectsDir, projectId);
        return await fs.pathExists(projectPath);
    }
    getProjectsDirectory() {
        return this.projectsDir;
    }
    async generateTemplatesForProject(projectId, templateBaseName) {
        const projectPath = path.join(this.projectsDir, projectId);
        if (!await fs.pathExists(projectPath)) {
            throw new Error(`Проект "${projectId}" не знайдено`);
        }
        const baseName = templateBaseName || `${projectId}-template`;
        return await this.templateGenerator.generateTemplateFromProject(projectPath, baseName);
    }
    async saveGeneratedTemplate(projectId, template) {
        const projectPath = path.join(this.projectsDir, projectId);
        if (!await fs.pathExists(projectPath)) {
            throw new Error(`Проект "${projectId}" не знайдено`);
        }
        return await this.templateGenerator.saveTemplate(projectPath, template);
    }
}
exports.SimpleProjectManager = SimpleProjectManager;
//# sourceMappingURL=SimpleProjectManager.js.map