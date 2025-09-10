"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.projectRoutes = projectRoutes;
const express_1 = require("express");
function projectRoutes(projectAnalyzer) {
    const router = (0, express_1.Router)();
    router.post('/analyze', async (req, res) => {
        try {
            const { projectPath, forceRefresh = false } = req.body;
            if (!projectPath) {
                return res.status(400).json({
                    error: 'Шлях проекту обов\'язковий'
                });
            }
            const analysis = await projectAnalyzer.analyzeProject(projectPath);
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
    router.get('/templates/:projectPath', async (req, res) => {
        try {
            const projectPath = decodeURIComponent(req.params.projectPath);
            const analysis = await projectAnalyzer.analyzeProject(projectPath);
            res.json({
                success: true,
                templates: analysis.templates.map(template => ({
                    id: template.id,
                    name: template.name,
                    type: template.type,
                    variablesCount: template.variables.length,
                    sectionsCount: template.structure.sections.length,
                    format: template.structure.format
                })),
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
    router.get('/templates/:projectPath/:templateId/variables', async (req, res) => {
        try {
            const projectPath = decodeURIComponent(req.params.projectPath);
            const { templateId } = req.params;
            const analysis = await projectAnalyzer.analyzeProject(projectPath);
            const template = analysis.templates.find(t => t.id === templateId);
            if (!template) {
                return res.status(404).json({
                    error: 'Шаблон не знайдено'
                });
            }
            res.json({
                success: true,
                template: {
                    id: template.id,
                    name: template.name,
                    type: template.type,
                    variables: template.variables,
                    structure: template.structure
                }
            });
        }
        catch (error) {
            console.error('Помилка отримання змінних шаблону:', error);
            res.status(500).json({
                error: error instanceof Error ? error.message : 'Помилка отримання змінних шаблону'
            });
        }
    });
    router.get('/validate-path', async (req, res) => {
        try {
            const { path: projectPath } = req.query;
            if (!projectPath || typeof projectPath !== 'string') {
                return res.status(400).json({
                    error: 'Шлях проекту обов\'язковий'
                });
            }
            const fs = require('fs-extra');
            const exists = await fs.pathExists(projectPath);
            if (!exists) {
                return res.json({
                    success: false,
                    valid: false,
                    error: 'Шлях не існує'
                });
            }
            const stats = await fs.stat(projectPath);
            if (!stats.isDirectory()) {
                return res.json({
                    success: false,
                    valid: false,
                    error: 'Шлях не є директорією'
                });
            }
            res.json({
                success: true,
                valid: true,
                path: projectPath,
                isDirectory: true
            });
        }
        catch (error) {
            console.error('Помилка валідації шляху:', error);
            res.status(500).json({
                error: 'Помилка валідації шляху'
            });
        }
    });
    router.get('/:projectPath/summary', async (req, res) => {
        try {
            const projectPath = decodeURIComponent(req.params.projectPath);
            const analysis = await projectAnalyzer.analyzeProject(projectPath);
            const summary = {
                projectName: analysis.projectName,
                projectPath: analysis.projectPath,
                documentTypes: analysis.documentTypes,
                templatesCount: analysis.templates.length,
                templates: analysis.templates.map(t => ({
                    id: t.id,
                    name: t.name,
                    type: t.type,
                    variablesCount: t.variables.length
                })),
                lastAnalyzed: analysis.lastAnalyzed
            };
            res.json({
                success: true,
                summary
            });
        }
        catch (error) {
            console.error('Помилка отримання резюме проекту:', error);
            res.status(500).json({
                error: error instanceof Error ? error.message : 'Помилка отримання резюме проекту'
            });
        }
    });
    return router;
}
//# sourceMappingURL=projects.js.map