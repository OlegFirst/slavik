"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.reportRoutes = reportRoutes;
const express_1 = require("express");
function reportRoutes(reportGenerator, projectAnalyzer) {
    const router = (0, express_1.Router)();
    router.post('/generate', async (req, res) => {
        try {
            const { projectPath, templateId, variables, outputPath, format } = req.body;
            if (!projectPath || !templateId || !variables) {
                return res.status(400).json({
                    error: 'Шлях проекту, ID шаблону та змінні обов\'язкові'
                });
            }
            const analysis = await projectAnalyzer.analyzeProject(projectPath);
            const template = analysis.templates.find(t => t.id === templateId);
            if (!template) {
                return res.status(404).json({
                    error: 'Шаблон не знайдено'
                });
            }
            const missingVariables = template.variables
                .filter(v => v.required && !(v.name in variables))
                .map(v => v.name);
            if (missingVariables.length > 0) {
                return res.status(400).json({
                    error: `Відсутні обов'язкові змінні: ${missingVariables.join(', ')}`
                });
            }
            const request = {
                templateId,
                projectPath,
                variables,
                outputPath,
                format: format || template.structure.format
            };
            const response = await reportGenerator.generateReport(request, template, analysis);
            if (!response.success) {
                return res.status(500).json({
                    error: response.error
                });
            }
            res.json({
                success: true,
                report: {
                    outputPath: response.outputPath,
                    generatedAt: response.generatedAt,
                    templateName: template.name,
                    format: request.format,
                    generatedBy: req.user?.username
                }
            });
        }
        catch (error) {
            console.error('Помилка генерації звіту:', error);
            res.status(500).json({
                error: error instanceof Error ? error.message : 'Помилка генерації звіту'
            });
        }
    });
    router.post('/validate-template', async (req, res) => {
        try {
            const { projectPath, templateId } = req.body;
            if (!projectPath || !templateId) {
                return res.status(400).json({
                    error: 'Шлях проекту та ID шаблону обов\'язкові'
                });
            }
            const analysis = await projectAnalyzer.analyzeProject(projectPath);
            const template = analysis.templates.find(t => t.id === templateId);
            if (!template) {
                return res.status(404).json({
                    error: 'Шаблон не знайдено'
                });
            }
            const errors = await reportGenerator.validateTemplate(template);
            res.json({
                success: true,
                valid: errors.length === 0,
                errors,
                template: {
                    id: template.id,
                    name: template.name,
                    type: template.type
                }
            });
        }
        catch (error) {
            console.error('Помилка валідації шаблону:', error);
            res.status(500).json({
                error: error instanceof Error ? error.message : 'Помилка валідації шаблону'
            });
        }
    });
    router.post('/preview', async (req, res) => {
        try {
            const { projectPath, templateId, variables } = req.body;
            if (!projectPath || !templateId) {
                return res.status(400).json({
                    error: 'Шлях проекту та ID шаблону обов\'язкові'
                });
            }
            const analysis = await projectAnalyzer.analyzeProject(projectPath);
            const template = analysis.templates.find(t => t.id === templateId);
            if (!template) {
                return res.status(404).json({
                    error: 'Шаблон не знайдено'
                });
            }
            const fs = require('fs-extra');
            const templateContent = await fs.readFile(template.filePath, 'utf-8');
            let previewContent = templateContent;
            const providedVars = variables || {};
            template.variables.forEach(variable => {
                const value = providedVars[variable.name] ||
                    variable.defaultValue ||
                    `[${variable.name.toUpperCase()}]`;
                const regex = new RegExp(`\\{\\{${variable.name}(?::[^}]*)?(?:\\|[^}]*)?\\}\\}`, 'g');
                previewContent = previewContent.replace(regex, String(value));
            });
            res.json({
                success: true,
                preview: {
                    content: previewContent,
                    templateName: template.name,
                    format: template.structure.format,
                    providedVariables: Object.keys(providedVars),
                    missingVariables: template.variables
                        .filter(v => v.required && !(v.name in providedVars))
                        .map(v => v.name)
                }
            });
        }
        catch (error) {
            console.error('Помилка створення превью:', error);
            res.status(500).json({
                error: error instanceof Error ? error.message : 'Помилка створення превью'
            });
        }
    });
    router.get('/history', async (req, res) => {
        try {
            const fs = require('fs-extra');
            const path = require('path');
            const historyFile = path.join('./data', 'reports-history.json');
            let history = [];
            if (await fs.pathExists(historyFile)) {
                history = await fs.readJson(historyFile);
            }
            const userHistory = history.filter((record) => record.userId === req.user?.userId);
            res.json({
                success: true,
                history: userHistory
            });
        }
        catch (error) {
            console.error('Помилка отримання історії звітів:', error);
            res.status(500).json({
                error: 'Помилка отримання історії звітів'
            });
        }
    });
    router.post('/save-to-history', async (req, res) => {
        try {
            const { templateId, projectPath, outputPath, templateName } = req.body;
            const fs = require('fs-extra');
            const path = require('path');
            const historyFile = path.join('./data', 'reports-history.json');
            let history = [];
            if (await fs.pathExists(historyFile)) {
                history = await fs.readJson(historyFile);
            }
            const record = {
                id: require('uuid').v4(),
                userId: req.user?.userId,
                username: req.user?.username,
                templateId,
                templateName,
                projectPath,
                outputPath,
                generatedAt: new Date().toISOString()
            };
            history.unshift(record);
            if (history.length > 1000) {
                history = history.slice(0, 1000);
            }
            await fs.ensureDir('./data');
            await fs.writeJson(historyFile, history, { spaces: 2 });
            res.json({
                success: true,
                message: 'Запис додано в історію'
            });
        }
        catch (error) {
            console.error('Помилка збереження в історію:', error);
            res.status(500).json({
                error: 'Помилка збереження в історію'
            });
        }
    });
    return router;
}
//# sourceMappingURL=reports.js.map