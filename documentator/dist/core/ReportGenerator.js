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
exports.ReportGenerator = void 0;
const fs = __importStar(require("fs-extra"));
const path = __importStar(require("path"));
class ReportGenerator {
    async generateReport(request, template, projectAnalysis) {
        try {
            const templateContent = await fs.readFile(template.filePath, 'utf-8');
            const processedContent = this.processTemplate(templateContent, request.variables);
            const outputPath = request.outputPath || this.generateOutputPath(projectAnalysis.projectPath, template.name, request.format || template.structure.format);
            await fs.ensureDir(path.dirname(outputPath));
            await fs.writeFile(outputPath, processedContent, 'utf-8');
            return {
                success: true,
                outputPath,
                generatedAt: new Date()
            };
        }
        catch (error) {
            return {
                success: false,
                error: error instanceof Error ? error.message : 'Невідома помилка',
                generatedAt: new Date()
            };
        }
    }
    processTemplate(content, variables) {
        let processedContent = content;
        Object.entries(variables).forEach(([key, value]) => {
            const regex = new RegExp(`\\{\\{${key}(?::[^}]*)?(?:\\|[^}]*)?\\}\\}`, 'g');
            processedContent = processedContent.replace(regex, String(value));
        });
        processedContent = this.processDefaultValues(processedContent);
        processedContent = this.processConditionals(processedContent, variables);
        processedContent = this.processLoops(processedContent, variables);
        return processedContent;
    }
    processDefaultValues(content) {
        const defaultValuePattern = /\{\{(\w+)(?::(\w+))?\|(.+?)\}\}/g;
        return content.replace(defaultValuePattern, (match, varName, type, defaultValue) => {
            return defaultValue;
        });
    }
    processConditionals(content, variables) {
        const conditionalPattern = /\{\{#if\s+(\w+)\}\}(.*?)\{\{\/if\}\}/gs;
        return content.replace(conditionalPattern, (match, condition, block) => {
            const value = variables[condition];
            return value ? block : '';
        });
    }
    processLoops(content, variables) {
        const loopPattern = /\{\{#each\s+(\w+)\s+as\s+(\w+)\}\}(.*?)\{\{\/each\}\}/gs;
        return content.replace(loopPattern, (match, arrayName, itemName, block) => {
            const array = variables[arrayName];
            if (!Array.isArray(array))
                return '';
            return array.map(item => {
                let processedBlock = block;
                if (typeof item === 'object') {
                    Object.entries(item).forEach(([key, value]) => {
                        const regex = new RegExp(`\\{\\{${itemName}\\.${key}\\}\\}`, 'g');
                        processedBlock = processedBlock.replace(regex, String(value));
                    });
                }
                else {
                    const regex = new RegExp(`\\{\\{${itemName}\\}\\}`, 'g');
                    processedBlock = processedBlock.replace(regex, String(item));
                }
                return processedBlock;
            }).join('');
        });
    }
    generateOutputPath(projectPath, templateName, format) {
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        const fileName = `${templateName}-${timestamp}.${format}`;
        return path.join(projectPath, 'generated-reports', fileName);
    }
    async validateTemplate(template) {
        const errors = [];
        if (!await fs.pathExists(template.filePath)) {
            errors.push(`Файл шаблону не знайдено: ${template.filePath}`);
        }
        try {
            const content = await fs.readFile(template.filePath, 'utf-8');
            const variables = this.extractTemplateVariables(content);
            for (const variable of template.variables) {
                if (variable.required && !variables.includes(variable.name)) {
                    errors.push(`Обов'язкова змінна ${variable.name} не знайдена в шаблоні`);
                }
            }
        }
        catch (error) {
            errors.push(`Помилка читання шаблону: ${error instanceof Error ? error.message : 'Невідома помилка'}`);
        }
        return errors;
    }
    extractTemplateVariables(content) {
        const variables = [];
        const variablePattern = /\{\{(\w+)(?::(\w+))?(?:\|(.+?))?\}\}/g;
        const matches = content.matchAll(variablePattern);
        for (const match of matches) {
            if (!variables.includes(match[1])) {
                variables.push(match[1]);
            }
        }
        return variables;
    }
}
exports.ReportGenerator = ReportGenerator;
//# sourceMappingURL=ReportGenerator.js.map