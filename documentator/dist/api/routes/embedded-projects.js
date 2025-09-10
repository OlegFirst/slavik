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
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.embeddedProjectsRoutes = embeddedProjectsRoutes;
const express_1 = require("express");
const multer_1 = __importDefault(require("multer"));
const path = __importStar(require("path"));
// Налаштування multer для завантаження файлів
const storage = multer_1.default.memoryStorage();
const upload = (0, multer_1.default)({
    storage,
    limits: {
        fileSize: 10 * 1024 * 1024, // 10MB
        files: 10
    },
    fileFilter: (req, file, cb) => {
        // Дозволені типи файлів
        const allowedTypes = ['.md', '.txt', '.json', '.html', '.css', '.js', '.ts', '.docx', '.pdf'];
        const ext = path.extname(file.originalname).toLowerCase();
        if (allowedTypes.includes(ext)) {
            cb(null, true);
        }
        else {
            cb(new Error(`Тип файлу ${ext} не підтримується`));
        }
    }
});
function embeddedProjectsRoutes(projectManager) {
    const router = (0, express_1.Router)();
    // Отримати список всіх проектів
    router.get('/', async (req, res) => {
        try {
            const projects = await projectManager.listProjects();
            res.json({
                success: true,
                projects: projects.map(project => ({
                    id: project.id,
                    name: project.name,
                    description: project.description,
                    templatesCount: project.templatesCount,
                    documentTypes: project.documentTypes,
                    createdAt: project.createdAt,
                    lastModified: project.lastModified
                }))
            });
        }
        catch (error) {
            console.error('Помилка отримання списку проектів:', error);
            res.status(500).json({
                error: error instanceof Error ? error.message : 'Помилка отримання проектів'
            });
        }
    });
    // Отримати інформацію про конкретний проект
    router.get('/:projectId', async (req, res) => {
        try {
            const { projectId } = req.params;
            const project = await projectManager.getProject(projectId);
            if (!project) {
                return res.status(404).json({
                    error: 'Проект не знайдено'
                });
            }
            const files = await projectManager.getProjectFiles(projectId);
            res.json({
                success: true,
                project,
                files
            });
        }
        catch (error) {
            console.error('Помилка отримання проекту:', error);
            res.status(500).json({
                error: error instanceof Error ? error.message : 'Помилка отримання проекту'
            });
        }
    });
    // Створити новий проект
    router.post('/', async (req, res) => {
        try {
            const request = req.body;
            if (!request.name) {
                return res.status(400).json({
                    error: 'Назва проекту обов\'язкова'
                });
            }
            const project = await projectManager.createProject(request);
            res.status(201).json({
                success: true,
                project,
                message: `Проект "${request.name}" успішно створено`
            });
        }
        catch (error) {
            console.error('Помилка створення проекту:', error);
            if (error instanceof Error && error.message.includes('вже існує')) {
                return res.status(409).json({
                    error: error.message
                });
            }
            res.status(500).json({
                error: error instanceof Error ? error.message : 'Помилка створення проекту'
            });
        }
    });
    // Оновити метадані проекту
    router.put('/:projectId', async (req, res) => {
        try {
            const { projectId } = req.params;
            const { name, description } = req.body;
            const project = await projectManager.updateProjectMetadata(projectId, { name, description });
            if (!project) {
                return res.status(404).json({
                    error: 'Проект не знайдено'
                });
            }
            res.json({
                success: true,
                project,
                message: 'Проект успішно оновлено'
            });
        }
        catch (error) {
            console.error('Помилка оновлення проекту:', error);
            res.status(500).json({
                error: error instanceof Error ? error.message : 'Помилка оновлення проекту'
            });
        }
    });
    // Видалити проект
    router.delete('/:projectId', async (req, res) => {
        try {
            const { projectId } = req.params;
            const success = await projectManager.deleteProject(projectId);
            if (!success) {
                return res.status(404).json({
                    error: 'Проект не знайдено'
                });
            }
            res.json({
                success: true,
                message: 'Проект успішно видалено'
            });
        }
        catch (error) {
            console.error('Помилка видалення проекту:', error);
            res.status(500).json({
                error: error instanceof Error ? error.message : 'Помилка видалення проекту'
            });
        }
    });
    // Аналізувати проект
    router.post('/:projectId/analyze', async (req, res) => {
        try {
            const { projectId } = req.params;
            const analysis = await projectManager.analyzeProject(projectId);
            res.json({
                success: true,
                analysis,
                analyzedBy: req.user?.username,
                analyzedAt: new Date().toISOString()
            });
        }
        catch (error) {
            console.error('Помилка аналізу проекту:', error);
            res.status(500).json({
                error: error instanceof Error ? error.message : 'Помилка аналізу проекту'
            });
        }
    });
    // Завантажити файли до проекту
    router.post('/:projectId/files', upload.array('files', 10), async (req, res) => {
        try {
            const { projectId } = req.params;
            const files = req.files;
            if (!files || files.length === 0) {
                return res.status(400).json({
                    error: 'Файли для завантаження не надано'
                });
            }
            const uploadedFiles = [];
            for (const file of files) {
                const filePath = await projectManager.uploadFile(projectId, file.originalname, file.buffer);
                uploadedFiles.push(path.basename(filePath));
            }
            res.json({
                success: true,
                uploadedFiles,
                message: `Завантажено ${uploadedFiles.length} файлів`
            });
        }
        catch (error) {
            console.error('Помилка завантаження файлів:', error);
            res.status(500).json({
                error: error instanceof Error ? error.message : 'Помилка завантаження файлів'
            });
        }
    });
    // Завантажити окремий файл
    router.post('/:projectId/files/:fileName', async (req, res) => {
        try {
            const { projectId, fileName } = req.params;
            const { content } = req.body;
            if (!content) {
                return res.status(400).json({
                    error: 'Контент файлу обов\'язковий'
                });
            }
            await projectManager.uploadFile(projectId, fileName, content);
            res.json({
                success: true,
                fileName,
                message: `Файл "${fileName}" успішно збережено`
            });
        }
        catch (error) {
            console.error('Помилка створення файлу:', error);
            res.status(500).json({
                error: error instanceof Error ? error.message : 'Помилка створення файлу'
            });
        }
    });
    // Видалити файл з проекту
    router.delete('/:projectId/files/:fileName', async (req, res) => {
        try {
            const { projectId, fileName } = req.params;
            const success = await projectManager.deleteFile(projectId, decodeURIComponent(fileName));
            if (!success) {
                return res.status(404).json({
                    error: 'Файл не знайдено'
                });
            }
            res.json({
                success: true,
                message: `Файл "${fileName}" успішно видалено`
            });
        }
        catch (error) {
            console.error('Помилка видалення файлу:', error);
            res.status(500).json({
                error: error instanceof Error ? error.message : 'Помилка видалення файлу'
            });
        }
    });
    // Отримати список файлів проекту
    router.get('/:projectId/files', async (req, res) => {
        try {
            const { projectId } = req.params;
            const files = await projectManager.getProjectFiles(projectId);
            res.json({
                success: true,
                files,
                projectId
            });
        }
        catch (error) {
            console.error('Помилка отримання файлів:', error);
            res.status(500).json({
                error: error instanceof Error ? error.message : 'Помилка отримання файлів'
            });
        }
    });
    // Отримати шаблони проекту
    router.get('/:projectId/templates', async (req, res) => {
        try {
            const { projectId } = req.params;
            const analysis = await projectManager.analyzeProject(projectId);
            res.json({
                success: true,
                templates: analysis.templates.map(template => ({
                    id: template.id,
                    name: template.name,
                    type: template.type,
                    variablesCount: template.variables.length,
                    sectionsCount: template.structure.sections.length,
                    format: template.structure.format,
                    filePath: template.filePath
                })),
                projectId,
                projectName: analysis.projectName
            });
        }
        catch (error) {
            console.error('Помилка отримання шаблонів:', error);
            res.status(500).json({
                error: error instanceof Error ? error.message : 'Помилка отримання шаблонів'
            });
        }
    });
    return router;
}
//# sourceMappingURL=embedded-projects.js.map