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
exports.ProjectAnalyzer = void 0;
const fs = __importStar(require("fs-extra"));
const path = __importStar(require("path"));
class ProjectAnalyzer {
    constructor() {
        this.supportedExtensions = ['.md', '.txt', '.docx', '.pdf', '.html'];
        this.templatePatterns = [
            /template/i,
            /шаблон/i,
            /звіт/i,
            /report/i,
            /документ/i,
            /document/i
        ];
    }
    async analyzeProject(projectPath) {
        if (!await fs.pathExists(projectPath)) {
            throw new Error(`Шлях проекту не існує: ${projectPath}`);
        }
        const projectName = path.basename(projectPath);
        const documentTypes = [];
        const templates = [];
        await this.scanDirectory(projectPath, documentTypes, templates);
        return {
            projectPath,
            projectName,
            documentTypes: [...new Set(documentTypes)],
            templates,
            lastAnalyzed: new Date()
        };
    }
    async scanDirectory(dirPath, documentTypes, templates) {
        const items = await fs.readdir(dirPath, { withFileTypes: true });
        for (const item of items) {
            const fullPath = path.join(dirPath, item.name);
            if (item.isDirectory()) {
                await this.scanDirectory(fullPath, documentTypes, templates);
            }
            else if (item.isFile()) {
                const ext = path.extname(item.name).toLowerCase();
                if (this.supportedExtensions.includes(ext)) {
                    documentTypes.push(ext);
                    if (this.isTemplate(item.name)) {
                        const template = await this.analyzeTemplate(fullPath);
                        if (template) {
                            templates.push(template);
                        }
                    }
                }
            }
        }
    }
    isTemplate(fileName) {
        return this.templatePatterns.some(pattern => pattern.test(fileName));
    }
    async analyzeTemplate(filePath) {
        try {
            const content = await fs.readFile(filePath, 'utf-8');
            const ext = path.extname(filePath).toLowerCase();
            if (ext === '.md') {
                return this.analyzeMarkdownTemplate(filePath, content);
            }
            return null;
        }
        catch (error) {
            console.error(`Помилка аналізу шаблону ${filePath}:`, error);
            return null;
        }
    }
    analyzeMarkdownTemplate(filePath, content) {
        const variables = this.extractVariables(content);
        const structure = this.extractStructure(content);
        return {
            id: this.generateTemplateId(filePath),
            name: path.basename(filePath, path.extname(filePath)),
            type: 'markdown',
            filePath,
            variables,
            structure
        };
    }
    extractVariables(content) {
        const variables = [];
        const variablePattern = /\{\{(\w+)(?::(\w+))?(?:\|(.+?))?\}\}/g;
        const matches = content.matchAll(variablePattern);
        for (const match of matches) {
            const name = match[1];
            const type = match[2] || 'string';
            const defaultValue = match[3];
            if (!variables.find(v => v.name === name)) {
                variables.push({
                    name,
                    type,
                    required: !defaultValue,
                    defaultValue,
                    description: `Змінна ${name} типу ${type}`
                });
            }
        }
        return variables;
    }
    extractStructure(content) {
        const sections = [];
        const lines = content.split('\n');
        let currentSection = null;
        for (let i = 0; i < lines.length; i++) {
            const line = lines[i].trim();
            if (line.startsWith('#')) {
                if (currentSection) {
                    sections.push(currentSection);
                }
                const level = line.match(/^#+/)?.[0].length || 1;
                const title = line.replace(/^#+\s*/, '');
                currentSection = {
                    id: this.generateSectionId(title),
                    title,
                    content: '',
                    variables: []
                };
            }
            else if (currentSection && line) {
                currentSection.content += line + '\n';
                const variables = this.extractVariablesFromLine(line);
                currentSection.variables.push(...variables);
            }
        }
        if (currentSection) {
            sections.push(currentSection);
        }
        return {
            sections,
            format: 'markdown'
        };
    }
    extractVariablesFromLine(line) {
        const variables = [];
        const variablePattern = /\{\{(\w+)(?::(\w+))?(?:\|(.+?))?\}\}/g;
        const matches = line.matchAll(variablePattern);
        for (const match of matches) {
            variables.push(match[1]);
        }
        return variables;
    }
    generateTemplateId(filePath) {
        return Buffer.from(filePath).toString('base64').replace(/[^a-zA-Z0-9]/g, '').substring(0, 16);
    }
    generateSectionId(title) {
        return title.toLowerCase()
            .replace(/[^\w\s-]/g, '')
            .replace(/\s+/g, '-')
            .replace(/-+/g, '-')
            .trim();
    }
}
exports.ProjectAnalyzer = ProjectAnalyzer;
//# sourceMappingURL=ProjectAnalyzer.js.map