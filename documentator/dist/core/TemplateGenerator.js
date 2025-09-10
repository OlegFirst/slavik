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
exports.TemplateGenerator = void 0;
const fs = __importStar(require("fs-extra"));
const path = __importStar(require("path"));
class TemplateGenerator {
    async generateTemplateFromDocument(documentPath, templateName) {
        const documentContent = await fs.readFile(documentPath, 'utf-8');
        const fileName = path.basename(documentPath, path.extname(documentPath));
        const finalTemplateName = templateName || `${fileName}-template`;
        // Аналізуємо документ і виділяємо потенційні змінні
        const result = this.extractVariablesFromDocument(documentContent);
        return {
            templateName: finalTemplateName,
            templateContent: result.templateContent,
            extractedVariables: result.variables,
            originalDocument: documentPath
        };
    }
    extractVariablesFromDocument(content) {
        const variables = [];
        let templateContent = content;
        // Шукаємо дати в різних форматах
        templateContent = this.replacePattern(templateContent, /\b(\d{1,2}[\.\-\/]\d{1,2}[\.\-\/]\d{2,4})\b/g, '{{date}}', variables, 'date');
        templateContent = this.replacePattern(templateContent, /\b(\d{4}[\.\-\/]\d{1,2}[\.\-\/]\d{1,2})\b/g, '{{date}}', variables, 'date');
        // Шукаємо імена (великі букви + малі)
        templateContent = this.replacePattern(templateContent, /\b([А-ЯІЄЇҐA-Z][а-яієїґa-z]+ [А-ЯІЄЇҐA-Z][а-яієїґa-z]+)\b/g, '{{author}}', variables, 'author');
        // Шукаємо числа (можливі показники)
        templateContent = this.replacePattern(templateContent, /\b(\d+)\b/g, '{{number}}', variables, 'number');
        // Шукаємо назви місяців
        const months = ['січ', 'лют', 'бер', 'кві', 'тра', 'чер', 'лип', 'сер', 'вер', 'жов', 'лис', 'гру',
            'января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря',
            'january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december'];
        months.forEach(month => {
            const regex = new RegExp(`\\b(${month}[а-яa-z]*)\\b`, 'gi');
            templateContent = this.replacePattern(templateContent, regex, '{{month}}', variables, 'month');
        });
        // Шукаємо емейли
        templateContent = this.replacePattern(templateContent, /\b([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\b/g, '{{email}}', variables, 'email');
        // Шукаємо назви компаній/підрозділів (після двокрапки)
        templateContent = this.replacePattern(templateContent, /:\s*([А-ЯІЄЇҐA-Z][А-ЯІЄЇҐа-яієїґA-Za-z\s]+)/g, ': {{department}}', variables, 'department');
        return {
            templateContent,
            variables: [...new Set(variables)] // Прибираємо дублікати
        };
    }
    replacePattern(content, pattern, replacement, variables, variableName) {
        if (pattern.test(content)) {
            variables.push(variableName);
            return content.replace(pattern, replacement);
        }
        return content;
    }
    async generateTemplateFromProject(projectPath, templateName) {
        const results = [];
        // Читаємо всі файли в проекті
        const files = await this.getAllDocuments(projectPath);
        for (const filePath of files) {
            try {
                const result = await this.generateTemplateFromDocument(filePath, `${templateName}-${path.basename(filePath, path.extname(filePath))}`);
                results.push(result);
            }
            catch (error) {
                console.warn(`Не вдалося обробити файл ${filePath}:`, error);
            }
        }
        return results;
    }
    async getAllDocuments(projectPath) {
        const documents = [];
        const supportedExtensions = ['.md', '.txt', '.docx', '.doc'];
        const items = await fs.readdir(projectPath, { withFileTypes: true });
        for (const item of items) {
            const fullPath = path.join(projectPath, item.name);
            if (item.isFile()) {
                const ext = path.extname(item.name).toLowerCase();
                if (supportedExtensions.includes(ext)) {
                    documents.push(fullPath);
                }
            }
            else if (item.isDirectory()) {
                // Рекурсивно шукаємо в підпапках
                const subDocs = await this.getAllDocuments(fullPath);
                documents.push(...subDocs);
            }
        }
        return documents;
    }
    async saveTemplate(projectPath, template) {
        const templatePath = path.join(projectPath, `${template.templateName}.md`);
        // Додаємо коментар з інформацією про змінні
        const header = `<!-- Шаблон згенеровано з: ${path.basename(template.originalDocument)} -->\n`;
        const variablesComment = template.extractedVariables.length > 0
            ? `<!-- Змінні: ${template.extractedVariables.join(', ')} -->\n\n`
            : '\n';
        const fullContent = header + variablesComment + template.templateContent;
        await fs.writeFile(templatePath, fullContent, 'utf-8');
        return templatePath;
    }
}
exports.TemplateGenerator = TemplateGenerator;
//# sourceMappingURL=TemplateGenerator.js.map