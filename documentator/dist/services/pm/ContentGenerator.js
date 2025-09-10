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
exports.ContentGenerator = void 0;
const fs = __importStar(require("fs-extra"));
const path = __importStar(require("path"));
class ContentGenerator {
    constructor() {
        this.prompts = new Map();
        // Загружаємо базові промпти
        this.loadBuiltInPrompts();
    }
    loadBuiltInPrompts() {
        // Будемо додавати промпти динамічно
    }
    registerPrompt(prompt) {
        this.prompts.set(prompt.id, prompt);
        console.log(`Промпт ${prompt.id} зареєстровано`);
    }
    getPrompt(id) {
        return this.prompts.get(id);
    }
    getAllPrompts() {
        return Array.from(this.prompts.values());
    }
    getPromptsByCategory(category) {
        return Array.from(this.prompts.values()).filter(p => p.category === category);
    }
    validateFieldData(field, value) {
        if (field.required && (!value || (typeof value === 'string' && value.trim().length === 0))) {
            return { valid: false, error: `Поле "${field.name}" є обов'язковим` };
        }
        if (!value && !field.required) {
            return { valid: true };
        }
        // Валідація типів
        switch (field.type) {
            case 'text':
            case 'textarea':
                if (typeof value !== 'string') {
                    return { valid: false, error: `Поле "${field.name}" повинно бути текстом` };
                }
                if (field.validation?.minLength && value.length < field.validation.minLength) {
                    return { valid: false, error: `Поле "${field.name}" повинно містити мінімум ${field.validation.minLength} символів` };
                }
                if (field.validation?.maxLength && value.length > field.validation.maxLength) {
                    return { valid: false, error: `Поле "${field.name}" повинно містити максимум ${field.validation.maxLength} символів` };
                }
                if (field.validation?.pattern && !new RegExp(field.validation.pattern).test(value)) {
                    return { valid: false, error: `Поле "${field.name}" має неправильний формат` };
                }
                break;
            case 'select':
                if (field.options && !field.options.includes(value)) {
                    return { valid: false, error: `Поле "${field.name}" має неприпустиме значення` };
                }
                break;
            case 'multiselect':
                if (!Array.isArray(value) || (field.options && !value.every(v => field.options.includes(v)))) {
                    return { valid: false, error: `Поле "${field.name}" має неприпустимі значення` };
                }
                break;
            case 'number':
                if (typeof value !== 'number' && isNaN(Number(value))) {
                    return { valid: false, error: `Поле "${field.name}" повинно бути числом` };
                }
                break;
            case 'date':
                if (isNaN(Date.parse(value))) {
                    return { valid: false, error: `Поле "${field.name}" повинно бути правильною датою` };
                }
                break;
        }
        return { valid: true };
    }
    validateRequest(request) {
        const prompt = this.getPrompt(request.promptId);
        if (!prompt) {
            return { valid: false, errors: [`Промпт з ID ${request.promptId} не знайдено`] };
        }
        const errors = [];
        // Перевіряємо обов'язкові поля
        for (const field of prompt.requiredFields) {
            const validation = this.validateFieldData(field, request.data[field.name]);
            if (!validation.valid) {
                errors.push(validation.error);
            }
        }
        // Перевіряємо опціональні поля (якщо вони надані)
        if (prompt.optionalFields) {
            for (const field of prompt.optionalFields) {
                if (request.data[field.name] !== undefined) {
                    const validation = this.validateFieldData(field, request.data[field.name]);
                    if (!validation.valid) {
                        errors.push(validation.error);
                    }
                }
            }
        }
        return { valid: errors.length === 0, errors };
    }
    async generateContent(request) {
        try {
            // Валідуємо запит
            const validation = this.validateRequest(request);
            if (!validation.valid) {
                return {
                    success: false,
                    error: `Помилки валідації: ${validation.errors.join(', ')}`,
                    generatedAt: new Date()
                };
            }
            const prompt = this.getPrompt(request.promptId);
            // Формуємо контент на основі промпту та даних
            const generatedContent = await this.processPrompt(prompt, request.data);
            // Зберігаємо файл, якщо вказано шлях
            let outputPath;
            if (request.outputPath) {
                await this.saveContent(generatedContent, request.outputPath, prompt.outputFormat);
                outputPath = request.outputPath;
            }
            return {
                success: true,
                content: generatedContent,
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
    async processPrompt(prompt, data) {
        // Базовий шаблонизатор - замінюємо змінні в системному промпті
        let processedPrompt = prompt.systemPrompt;
        // Додаємо дані користувача до промпту
        let userDataSection = '\n\nДАНІ ДЛЯ ОБРОБКИ:\n';
        // Обов'язкові поля
        for (const field of prompt.requiredFields) {
            if (data[field.name]) {
                userDataSection += `${field.description}: ${data[field.name]}\n`;
            }
        }
        // Опціональні поля
        if (prompt.optionalFields) {
            for (const field of prompt.optionalFields) {
                if (data[field.name]) {
                    userDataSection += `${field.description}: ${data[field.name]}\n`;
                }
            }
        }
        // Симуляція AI генерації (в реальності тут був би виклик до AI API)
        const fullPrompt = processedPrompt + userDataSection + '\n\nСТВОРІТЬ КОНТЕНТ ВІДПОВІДНО ДО ВКАЗАНИХ ПРИНЦИПІВ:';
        // Тимчасове заглушка - генеруємо базовий контент на основі шаблону
        const generatedContent = this.generateMockContent(prompt, data);
        return generatedContent;
    }
    generateMockContent(prompt, data) {
        // Базовий генератор контенту (заглушка для демо)
        // В реальності тут буде виклик до AI API (OpenAI, Claude, etc.)
        const timestamp = new Date().toLocaleString('uk-UA');
        if (prompt.id === 'press-release') {
            return this.generatePressReleaseMock(data);
        }
        else if (prompt.id === 'project-point') {
            return this.generateProjectPointMock(data);
        }
        return `# Згенерований контент\n\n*Створено ${timestamp}*\n\n` +
            `**Тип контенту:** ${prompt.name}\n` +
            `**Категорія:** ${prompt.category}\n\n` +
            `**Вхідні дані:**\n${Object.entries(data).map(([key, value]) => `- ${key}: ${value}`).join('\n')}\n\n` +
            `---\n\n*Це тестовий контент, згенерований системою Digital Office PM*`;
    }
    generatePressReleaseMock(data) {
        const date = new Date().toLocaleDateString('uk-UA', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
        const location = data.location || 'Україна';
        return `# 🚀 ${data.companyName} ${this.getAnnouncementTypeText(data.announcementType)}

## ${this.generateSubheadline(data)}

**${location}, ${date}** — ${data.mainNews}

### Ключові переваги

${data.keyBenefits}

${data.executiveQuote ? `### Коментар керівництва\n\n${data.executiveQuote}` : ''}

${data.statistics ? `### Статистика та показники\n\n${data.statistics}` : ''}

${data.timeline ? `### Терміни реалізації\n\n${data.timeline}` : ''}

${data.partnerInfo ? `### Партнерство\n\n${data.partnerInfo}` : ''}

---

${data.companyBackground ? `**Про ${data.companyName}**\n\n${data.companyBackground}` : ''}

${data.contactInfo ? `**Контакти для преси:**\n\n${data.contactInfo}` : ''}

*Цей прес-реліз згенеровано Digital Office PM з потужними AI промптами для максимального впливу на ${data.targetAudience}.*`;
    }
    generateProjectPointMock(data) {
        const date = new Date().toLocaleDateString('uk-UA');
        return `# ✅ ${data.projectName}: ${this.generateAchievementTitle(data.achievement)}

## 📊 Статус проекту: ${data.projectStage}

**Дата:** ${date}

### 🎯 Що досягнуто

${data.achievement}

### 📈 Вплив на проект

${data.impactDescription}

${data.metrics ? `### 📊 Ключові показники\n\n${data.metrics}` : ''}

${data.teamContribution ? `### 👥 Внесок команди\n\n${data.teamContribution}` : ''}

${data.challenges ? `### ⚠️ Виклики та рішення\n\n${data.challenges}` : ''}

${data.nextSteps ? `### ➡️ Наступні кроки\n\n${data.nextSteps}` : ''}

${data.businessValue ? `### 💼 Бізнес-цінність\n\n${data.businessValue}` : ''}

${data.timeline ? `### ⏱️ Хронометраж\n\n${data.timeline}` : ''}

${data.budget ? `### 💰 Бюджет\n\n${data.budget}` : ''}

---

*Повідомлення створено Digital Office PM для ${data.stakeholders || 'команди проекту'}*`;
    }
    getAnnouncementTypeText(type) {
        const typeMap = {
            'Запуск нового продукту': 'анонсує запуск інноваційного продукту',
            'Оновлення продукту/сервісу': 'представляє оновлену версію сервісу',
            'Партнерство/співпраця': 'оголошує про стратегічне партнерство',
            'Інвестиції/фінансування': 'залучає інвестиції для розвитку',
            'Нагороди/досягнення': 'отримує престижну нагороду',
            'Призначення керівництва': 'повідомляє про призначення в керівництві',
            'Експансія/відкриття офісів': 'розширює географію присутності',
            'Дослідження/статистика': 'представляє результати дослідження',
            'Подія/конференція': 'запрошує на важливу подію',
            'CSR ініціатива': 'запускає соціальну ініціативу'
        };
        return typeMap[type] || 'робить важливе оголошення';
    }
    generateSubheadline(data) {
        return `Нова веха у розвитку для ${data.targetAudience}`;
    }
    generateAchievementTitle(achievement) {
        // Витягуємо ключові слова з опису досягнення
        const words = achievement.split(' ').slice(0, 4);
        return words.join(' ') + (achievement.split(' ').length > 4 ? '...' : '');
    }
    async saveContent(content, filePath, format) {
        const dir = path.dirname(filePath);
        await fs.ensureDir(dir);
        let fileContent = content;
        let actualPath = filePath;
        // Додаємо розширення файлу відповідно до формату
        if (!path.extname(filePath)) {
            switch (format) {
                case 'markdown':
                    actualPath += '.md';
                    break;
                case 'text':
                    actualPath += '.txt';
                    break;
                case 'html':
                    actualPath += '.html';
                    // Обгортаємо контент в HTML теги
                    fileContent = `<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Generated Content</title>
</head>
<body>
${content.replace(/\n/g, '<br>\n')}
</body>
</html>`;
                    break;
            }
        }
        await fs.writeFile(actualPath, fileContent, 'utf-8');
    }
}
exports.ContentGenerator = ContentGenerator;
//# sourceMappingURL=ContentGenerator.js.map