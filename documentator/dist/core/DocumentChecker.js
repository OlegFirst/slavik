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
exports.DocumentChecker = void 0;
const fs = __importStar(require("fs-extra"));
const path = __importStar(require("path"));
class DocumentChecker {
    constructor() {
        this.grammarRules = new Map();
        this.spellingDictionary = new Set();
        this.ukrainianRules = new Map();
        this.initializeRules();
        this.loadDictionary();
    }
    initializeRules() {
        // Граматичні правила для української мови
        this.ukrainianRules.set(/\bв коли\b/gi, 'в якому');
        this.ukrainianRules.set(/\bв які\b/gi, 'в яких');
        this.ukrainianRules.set(/\bв що\b/gi, 'в який');
        this.ukrainianRules.set(/\bз-за того що\b/gi, 'через те що');
        this.ukrainianRules.set(/\bвід самого початку\b/gi, 'з самого початку');
        this.ukrainianRules.set(/\bприйти к висновку\b/gi, 'дійти висновку');
        this.ukrainianRules.set(/\bв подальшому\b/gi, 'надалі');
        this.ukrainianRules.set(/\bв результаті\b/gi, 'внаслідок');
        this.ukrainianRules.set(/\bпо відношенню до\b/gi, 'щодо');
        this.ukrainianRules.set(/\bпо суті\b/gi, 'власне');
        // Англійські граматичні правила
        this.grammarRules.set(/\bit's\s+own\b/gi, 'its own');
        this.grammarRules.set(/\byour\s+welcome\b/gi, 'you\'re welcome');
        this.grammarRules.set(/\bthere\s+own\b/gi, 'their own');
        this.grammarRules.set(/\bshould\s+of\b/gi, 'should have');
        this.grammarRules.set(/\bcould\s+of\b/gi, 'could have');
        this.grammarRules.set(/\bwould\s+of\b/gi, 'would have');
        this.grammarRules.set(/\ba\s+lot\s+of\b/gi, 'a lot of');
        this.grammarRules.set(/\balot\b/gi, 'a lot');
        // Правила пунктуації
        this.grammarRules.set(/\s+,/g, ','); // Пробіл перед комою
        this.grammarRules.set(/,\s*,/g, ','); // Подвійні коми
        this.grammarRules.set(/\.\s*\./g, '.'); // Подвійні крапки
        this.grammarRules.set(/\?\s*\?/g, '?'); // Подвійні знаки питання
        this.grammarRules.set(/!\s*!/g, '!'); // Подвійні знаки оклику
        this.grammarRules.set(/\s+\./g, '.'); // Пробіл перед крапкою
        this.grammarRules.set(/\s+\?/g, '?'); // Пробіл перед знаком питання
        this.grammarRules.set(/\s+!/g, '!'); // Пробіл перед знаком оклику
        // Правила пробілів
        this.grammarRules.set(/\s{2,}/g, ' '); // Множинні пробіли
        this.grammarRules.set(/^\s+/gm, ''); // Пробіли на початку рядка
        this.grammarRules.set(/\s+$/gm, ''); // Пробіли в кінці рядка
    }
    loadDictionary() {
        // Базовий словник українських слів
        const ukrainianWords = [
            'автоматизація', 'документація', 'система', 'генерація', 'аналіз', 'проект',
            'шаблон', 'звіт', 'файл', 'директорія', 'конфігурація', 'сервіс', 'команда',
            'інструмент', 'функція', 'можливість', 'розробка', 'тестування', 'інтеграція'
        ];
        // Базовий словник англійських слів  
        const englishWords = [
            'documentation', 'system', 'generation', 'analysis', 'project', 'template',
            'report', 'file', 'directory', 'configuration', 'service', 'command', 'tool',
            'function', 'feature', 'development', 'testing', 'integration', 'automation'
        ];
        [...ukrainianWords, ...englishWords].forEach(word => {
            this.spellingDictionary.add(word.toLowerCase());
        });
    }
    async checkDocument(filePath) {
        const content = await fs.readFile(filePath, 'utf-8');
        return this.checkText(content, path.extname(filePath));
    }
    checkText(content, fileExtension = '.md') {
        const documentType = this.getDocumentType(fileExtension);
        const structure = this.parseDocumentStructure(content, documentType);
        const errors = [];
        // Витягуємо текст, зберігаючи структуру
        const textBlocks = this.extractTextBlocks(content, structure);
        let correctedText = content;
        let totalFixedErrors = 0;
        // Перевіряємо кожен текстовий блок
        for (const block of textBlocks) {
            const blockErrors = this.checkTextBlock(block.text, block.startLine);
            errors.push(...blockErrors);
            // Застосовуємо виправлення
            let correctedBlockText = block.text;
            for (const error of blockErrors) {
                if (this.shouldAutoFix(error)) {
                    correctedBlockText = correctedBlockText.replace(error.originalText, error.correctedText);
                    totalFixedErrors++;
                }
            }
            // Замінюємо в оригінальному тексті
            correctedText = correctedText.replace(block.text, correctedBlockText);
        }
        const errorsByType = this.groupErrorsByType(errors);
        return {
            errors,
            correctedText,
            structure,
            summary: {
                totalErrors: errors.length,
                fixedErrors: totalFixedErrors,
                errorsByType
            }
        };
    }
    getDocumentType(fileExtension) {
        switch (fileExtension.toLowerCase()) {
            case '.md':
            case '.markdown':
                return 'markdown';
            case '.html':
            case '.htm':
                return 'html';
            default:
                return 'text';
        }
    }
    parseDocumentStructure(content, type) {
        const structure = {
            type,
            headers: [],
            lists: [],
            codeBlocks: [],
            links: [],
            formatting: []
        };
        const lines = content.split('\n');
        if (type === 'markdown') {
            this.parseMarkdownStructure(lines, structure);
        }
        return structure;
    }
    parseMarkdownStructure(lines, structure) {
        let inCodeBlock = false;
        let codeBlockStart = -1;
        let codeBlockLanguage = '';
        for (let i = 0; i < lines.length; i++) {
            const line = lines[i];
            // Заголовки
            const headerMatch = line.match(/^(#{1,6})\s+(.+)$/);
            if (headerMatch && !inCodeBlock) {
                structure.headers.push({
                    level: headerMatch[1].length,
                    text: headerMatch[2],
                    line: i + 1,
                    originalMarkdown: line
                });
            }
            // Блоки коду
            if (line.startsWith('```')) {
                if (!inCodeBlock) {
                    inCodeBlock = true;
                    codeBlockStart = i;
                    codeBlockLanguage = line.slice(3).trim();
                }
                else {
                    structure.codeBlocks.push({
                        language: codeBlockLanguage || undefined,
                        content: lines.slice(codeBlockStart + 1, i).join('\n'),
                        startLine: codeBlockStart + 1,
                        endLine: i + 1
                    });
                    inCodeBlock = false;
                }
                continue;
            }
            if (!inCodeBlock) {
                // Посилання
                const linkMatches = line.matchAll(/\[([^\]]+)\]\(([^)]+)\)/g);
                for (const match of linkMatches) {
                    structure.links.push({
                        text: match[1],
                        url: match[2],
                        line: i + 1,
                        originalMarkdown: match[0]
                    });
                }
                // Форматування (жирний, курсив, код)
                const boldMatches = line.matchAll(/\*\*([^*]+)\*\*/g);
                for (const match of boldMatches) {
                    structure.formatting.push({
                        type: 'bold',
                        text: match[1],
                        line: i + 1,
                        originalMarkdown: match[0]
                    });
                }
                const italicMatches = line.matchAll(/\*([^*]+)\*/g);
                for (const match of italicMatches) {
                    structure.formatting.push({
                        type: 'italic',
                        text: match[1],
                        line: i + 1,
                        originalMarkdown: match[0]
                    });
                }
                const codeMatches = line.matchAll(/`([^`]+)`/g);
                for (const match of codeMatches) {
                    structure.formatting.push({
                        type: 'code',
                        text: match[1],
                        line: i + 1,
                        originalMarkdown: match[0]
                    });
                }
                // Списки
                const listMatch = line.match(/^(\s*)[-*+]\s+(.+)$/);
                if (listMatch) {
                    // Простий алгоритм для списків - можна покращити
                    structure.lists.push({
                        type: 'unordered',
                        items: [listMatch[2]],
                        startLine: i + 1,
                        endLine: i + 1
                    });
                }
            }
        }
    }
    extractTextBlocks(content, structure) {
        const blocks = [];
        const lines = content.split('\n');
        for (let i = 0; i < lines.length; i++) {
            const line = lines[i];
            // Пропускаємо заголовки, блоки коду тощо
            if (this.shouldSkipLine(line, i + 1, structure)) {
                continue;
            }
            // Витягуємо чистий текст з рядка (без markdown форматування)
            let cleanText = this.stripMarkdownFormatting(line);
            if (cleanText.trim().length > 0) {
                blocks.push({
                    text: cleanText,
                    startLine: i + 1
                });
            }
        }
        return blocks;
    }
    shouldSkipLine(line, lineNumber, structure) {
        // Пропускаємо заголовки
        if (line.match(/^#{1,6}\s/)) {
            return true;
        }
        // Пропускаємо блоки коду
        for (const codeBlock of structure.codeBlocks) {
            if (lineNumber >= codeBlock.startLine && lineNumber <= codeBlock.endLine) {
                return true;
            }
        }
        // Пропускаємо порожні рядки
        if (line.trim().length === 0) {
            return true;
        }
        return false;
    }
    stripMarkdownFormatting(line) {
        return line
            .replace(/\*\*([^*]+)\*\*/g, '$1') // Жирний текст
            .replace(/\*([^*]+)\*/g, '$1') // Курсив
            .replace(/`([^`]+)`/g, '$1') // Інлайн код
            .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1') // Посилання
            .replace(/^[-*+]\s+/, '') // Маркери списків
            .replace(/^\d+\.\s+/, '') // Нумеровані списки
            .trim();
    }
    checkTextBlock(text, startLine) {
        const errors = [];
        // Перевірка граматики
        errors.push(...this.checkGrammar(text, startLine));
        // Перевірка орфографії
        errors.push(...this.checkSpelling(text, startLine));
        // Перевірка пунктуації
        errors.push(...this.checkPunctuation(text, startLine));
        return errors;
    }
    checkGrammar(text, startLine) {
        const errors = [];
        // Перевіряємо українські правила
        for (const [pattern, correction] of this.ukrainianRules) {
            const matches = text.matchAll(pattern);
            for (const match of matches) {
                if (match.index !== undefined) {
                    errors.push({
                        type: 'grammar',
                        line: startLine,
                        column: match.index,
                        originalText: match[0],
                        correctedText: correction,
                        description: `Рекомендується замінити "${match[0]}" на "${correction}"`,
                        severity: 'medium'
                    });
                }
            }
        }
        // Перевіряємо загальні граматичні правила
        for (const [pattern, correction] of this.grammarRules) {
            const matches = text.matchAll(pattern);
            for (const match of matches) {
                if (match.index !== undefined) {
                    errors.push({
                        type: 'grammar',
                        line: startLine,
                        column: match.index,
                        originalText: match[0],
                        correctedText: correction,
                        description: `Граматична помилка: "${match[0]}" -> "${correction}"`,
                        severity: 'high'
                    });
                }
            }
        }
        return errors;
    }
    checkSpelling(text, startLine) {
        const errors = [];
        const words = text.split(/\s+/);
        let position = 0;
        for (const word of words) {
            const cleanWord = word.replace(/[^\w\u0400-\u04FF]/g, '').toLowerCase();
            if (cleanWord.length > 2 && !this.spellingDictionary.has(cleanWord)) {
                const suggestion = this.getSuggestion(cleanWord);
                if (suggestion) {
                    errors.push({
                        type: 'spelling',
                        line: startLine,
                        column: position,
                        originalText: word,
                        correctedText: word.replace(cleanWord, suggestion),
                        description: `Можлива орфографічна помилка: "${cleanWord}" -> "${suggestion}"`,
                        severity: 'low'
                    });
                }
            }
            position += word.length + 1;
        }
        return errors;
    }
    checkPunctuation(text, startLine) {
        const errors = [];
        // Перевірка подвійних пробілів
        const doubleSpaces = text.matchAll(/\s{2,}/g);
        for (const match of doubleSpaces) {
            if (match.index !== undefined) {
                errors.push({
                    type: 'punctuation',
                    line: startLine,
                    column: match.index,
                    originalText: match[0],
                    correctedText: ' ',
                    description: 'Множинні пробіли',
                    severity: 'low'
                });
            }
        }
        // Перевірка пробілів перед розділовими знаками
        const spaceBeforePunctuation = text.matchAll(/\s+([,.?!;:])/g);
        for (const match of spaceBeforePunctuation) {
            if (match.index !== undefined) {
                errors.push({
                    type: 'punctuation',
                    line: startLine,
                    column: match.index,
                    originalText: match[0],
                    correctedText: match[1],
                    description: `Зайвий пробіл перед "${match[1]}"`,
                    severity: 'medium'
                });
            }
        }
        return errors;
    }
    getSuggestion(word) {
        // Простий алгоритм пошуку найближчих слів
        let bestMatch = null;
        let minDistance = Infinity;
        for (const dictWord of this.spellingDictionary) {
            const distance = this.levenshteinDistance(word, dictWord);
            if (distance <= 2 && distance < minDistance) {
                minDistance = distance;
                bestMatch = dictWord;
            }
        }
        return bestMatch;
    }
    levenshteinDistance(str1, str2) {
        const matrix = Array(str2.length + 1).fill(null).map(() => Array(str1.length + 1).fill(null));
        for (let i = 0; i <= str1.length; i++) {
            matrix[0][i] = i;
        }
        for (let j = 0; j <= str2.length; j++) {
            matrix[j][0] = j;
        }
        for (let j = 1; j <= str2.length; j++) {
            for (let i = 1; i <= str1.length; i++) {
                const indicator = str1[i - 1] === str2[j - 1] ? 0 : 1;
                matrix[j][i] = Math.min(matrix[j][i - 1] + 1, // deletion
                matrix[j - 1][i] + 1, // insertion
                matrix[j - 1][i - 1] + indicator // substitution
                );
            }
        }
        return matrix[str2.length][str1.length];
    }
    shouldAutoFix(error) {
        // Автоматично виправляємо тільки прості помилки
        return error.type === 'punctuation' ||
            (error.type === 'grammar' && error.severity === 'high');
    }
    groupErrorsByType(errors) {
        const grouped = {};
        for (const error of errors) {
            grouped[error.type] = (grouped[error.type] || 0) + 1;
        }
        return grouped;
    }
    async saveCheckedDocument(filePath, correctedContent, originalBackup = true) {
        if (originalBackup) {
            const backupPath = filePath + '.backup';
            await fs.copy(filePath, backupPath);
        }
        await fs.writeFile(filePath, correctedContent, 'utf-8');
        return filePath;
    }
}
exports.DocumentChecker = DocumentChecker;
//# sourceMappingURL=DocumentChecker.js.map