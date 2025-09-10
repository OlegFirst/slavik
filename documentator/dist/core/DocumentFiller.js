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
exports.DocumentFiller = void 0;
const fs = __importStar(require("fs-extra"));
const path = __importStar(require("path"));
class DocumentFiller {
    constructor() {
        this.sessions = new Map();
        this.fieldPatterns = [];
        this.initializePatterns();
        this.contextAnalyzer = new ContextAnalyzer();
    }
    initializePatterns() {
        // Патерни для виявлення полів що потребують заповнення
        this.fieldPatterns = [
            // Стандартні заповнювальні поля
            /\{\{([^}]+)\}\}/g, // {{назва_поля}}
            /\[([^\]]+)\]/g, // [поле для заповнення]
            /__([^_]+)__/g, // __поле__
            /\$\{([^}]+)\}/g, // ${поле}
            // Поля з підказками
            /\[ЗАПОВНИТИ:([^\]]+)\]/gi, // [ЗАПОВНИТИ: опис]
            /\[TODO:([^\]]+)\]/gi, // [TODO: опис]
            /\[ПОТРІБНО:([^\]]+)\]/gi, // [ПОТРІБНО: опис]
            // Поля дат
            /\b(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})\b/g, // дати
            /___\d{1,2}[\/\-\.]___\d{1,2}[\/\-\.]___\d{2,4}/g, // шаблони дат
            // Підписи та місця
            /Підпис:?\s*_+/gi, // Підпис: ______
            /П\.І\.Б\.?:?\s*_+/gi, // П.І.Б.: ______
            /Посада:?\s*_+/gi, // Посада: ______
            /Дата:?\s*_+/gi, // Дата: ______
            // Числові поля
            /№\s*_+/gi, // № _____
            /Кількість:?\s*_+/gi, // Кількість: ___
            /Сума:?\s*_+/gi, // Сума: ___
            // Адреси та контакти
            /Адреса:?\s*_+/gi, // Адреса: ______
            /Телефон:?\s*_+/gi, // Телефон: ____
            /Email:?\s*_+/gi, // Email: _____
            // Спеціальні маркери
            /\[ВСТАВИТИ\s+([^\]]+)\]/gi, // [ВСТАВИТИ дані]
            /\[ДОДАТИ\s+([^\]]+)\]/gi, // [ДОДАТИ інформацію]
        ];
    }
    async analyzeDocument(filePath, sourceDocuments) {
        const sessionId = this.generateSessionId();
        const content = await fs.readFile(filePath, 'utf-8');
        // Виявляємо поля для заповнення
        const fields = await this.detectFillableFields(content);
        // Аналізуємо додаткові документи
        const sourceDocs = [];
        if (sourceDocuments && sourceDocuments.length > 0) {
            for (const docPath of sourceDocuments) {
                const sourceDoc = await this.analyzeSourceDocument(docPath, fields);
                sourceDocs.push(sourceDoc);
            }
        }
        const session = {
            sessionId,
            targetDocument: filePath,
            fields,
            sourceDocuments: sourceDocs,
            currentFieldIndex: 0,
            responses: new Map(),
            status: 'analyzing',
            createdAt: new Date(),
            lastUpdated: new Date()
        };
        this.sessions.set(sessionId, session);
        // Автоматично заповнюємо поля з джерел, якщо є
        await this.autoFillFromSources(session);
        session.status = 'questioning';
        session.lastUpdated = new Date();
        return session;
    }
    async detectFillableFields(content) {
        const fields = [];
        const lines = content.split('\n');
        for (let lineIndex = 0; lineIndex < lines.length; lineIndex++) {
            const line = lines[lineIndex];
            for (const pattern of this.fieldPatterns) {
                let match;
                pattern.lastIndex = 0; // Скидаємо індекс для global regexp
                while ((match = pattern.exec(line)) !== null) {
                    const field = await this.createFieldFromMatch(match, lineIndex, line, lines, fields.length);
                    if (field && !this.isDuplicateField(field, fields)) {
                        fields.push(field);
                    }
                }
            }
        }
        // Сортуємо за позицією в документі
        fields.sort((a, b) => {
            if (a.position.line !== b.position.line) {
                return a.position.line - b.position.line;
            }
            return a.position.column - b.position.column;
        });
        // Присвоюємо ID та зв'язуємо пов'язані поля
        fields.forEach((field, index) => {
            field.id = `field_${index + 1}`;
        });
        this.identifyRelatedFields(fields);
        return fields;
    }
    async createFieldFromMatch(match, lineIndex, line, allLines, fieldIndex) {
        const fullMatch = match[0];
        const fieldContent = match[1] || match[0];
        const column = match.index || 0;
        // Аналізуємо контекст навколо поля
        const context = this.contextAnalyzer.analyzeContext(lineIndex, column, allLines);
        // Визначаємо тип поля
        const fieldType = this.determineFieldType(fieldContent, context);
        // Генеруємо питання для користувача
        const suggestedQuestions = this.generateQuestionsForField(fieldContent, context, fieldType);
        // Визначаємо валідацію
        const validation = this.determineValidation(fieldType, fieldContent, context);
        const field = {
            id: `temp_${fieldIndex}`,
            type: fieldType,
            placeholder: fieldContent.trim(),
            originalText: fullMatch,
            position: {
                line: lineIndex + 1,
                column: column,
                length: fullMatch.length
            },
            context: {
                beforeText: line.substring(0, column).trim(),
                afterText: line.substring(column + fullMatch.length).trim(),
                sectionTitle: context.sectionTitle
            },
            validation,
            suggestedQuestions
        };
        return field;
    }
    determineFieldType(content, context) {
        const lowerContent = content.toLowerCase();
        // Дата
        if (/дата|date|число|рік|місяць|день/.test(lowerContent) ||
            /\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}/.test(content)) {
            return 'date';
        }
        // Число
        if (/кількість|сума|номер|№|число|вартість|ціна|відсоток|процент/.test(lowerContent) ||
            /^\d+$/.test(content.trim())) {
            return 'number';
        }
        // Boolean
        if (/так\/ні|yes\/no|true\/false|є\/немає/.test(lowerContent)) {
            return 'boolean';
        }
        // Список/перечисления
        if (/список|перелік|варіанти/.test(lowerContent) || context.isInList) {
            return 'list';
        }
        // Таблица
        if (context.isInTable) {
            return 'table';
        }
        // Многострочный текст
        if (/опис|коментар|примітка|пояснення|детальн/.test(lowerContent) ||
            content.length > 50) {
            return 'multiline';
        }
        // По умолчанию текст
        return 'text';
    }
    generateQuestionsForField(content, context, fieldType) {
        const questions = [];
        const lowerContent = content.toLowerCase();
        // Базовое вопрос
        questions.push(`Яке значення для поля "${content}"?`);
        // Специфические вопросы по типу
        switch (fieldType) {
            case 'date':
                questions.push(`Яка дата для "${content}"? (формат: ДД.ММ.РРРР)`);
                questions.push(`Вкажіть дату у форматі день.місяць.рік`);
                break;
            case 'number':
                questions.push(`Яке числове значення для "${content}"?`);
                if (lowerContent.includes('сума') || lowerContent.includes('вартість')) {
                    questions.push(`Вкажіть суму у гривнях`);
                }
                break;
            case 'boolean':
                questions.push(`Оберіть варіант для "${content}": Так чи Ні?`);
                break;
            case 'multiline':
                questions.push(`Вкажіть детальний опис для "${content}"`);
                questions.push(`Надайте розширену інформацію про "${content}"`);
                break;
            case 'list':
                questions.push(`Вкажіть елементи списку для "${content}" (через кому)`);
                break;
        }
        // Контекстуальные вопросы
        if (context.sectionTitle) {
            questions.push(`У розділі "${context.sectionTitle}" потрібно заповнити "${content}". Яке значення?`);
        }
        // Специфические поля
        if (lowerContent.includes('піб') || lowerContent.includes('прізвище')) {
            questions.push(`Вкажіть повне прізвище, ім'я та по батькові`);
        }
        if (lowerContent.includes('посада') || lowerContent.includes('должность')) {
            questions.push(`Яка посада особи?`);
        }
        if (lowerContent.includes('організація') || lowerContent.includes('компанія')) {
            questions.push(`Назва організації/компанії?`);
        }
        if (lowerContent.includes('адреса')) {
            questions.push(`Повна адреса (місто, вулиця, будинок)?`);
        }
        return questions;
    }
    determineValidation(fieldType, content, context) {
        const validation = {};
        const lowerContent = content.toLowerCase();
        // Обязательность
        validation.required = !lowerContent.includes('опціональн') && !lowerContent.includes('за бажанн');
        switch (fieldType) {
            case 'date':
                validation.format = 'DD.MM.YYYY';
                break;
            case 'number':
                if (lowerContent.includes('телефон')) {
                    validation.format = '+380XXXXXXXXX';
                    validation.minLength = 10;
                    validation.maxLength = 13;
                }
                break;
            case 'text':
                if (lowerContent.includes('email')) {
                    validation.format = 'email';
                }
                if (lowerContent.includes('піб')) {
                    validation.minLength = 5;
                    validation.maxLength = 100;
                }
                break;
            case 'boolean':
                validation.options = ['Так', 'Ні', 'True', 'False'];
                break;
        }
        return validation;
    }
    isDuplicateField(field, existingFields) {
        return existingFields.some(existing => existing.position.line === field.position.line &&
            Math.abs(existing.position.column - field.position.column) < 5 &&
            existing.placeholder === field.placeholder);
    }
    identifyRelatedFields(fields) {
        // Простой алгоритм связи полей по близости и контексту
        fields.forEach((field, index) => {
            const related = [];
            fields.forEach((otherField, otherIndex) => {
                if (index !== otherIndex) {
                    // Поля в одной секции
                    if (field.context.sectionTitle === otherField.context.sectionTitle &&
                        field.context.sectionTitle) {
                        related.push(otherField.id);
                    }
                    // Поля на соседних строках
                    if (Math.abs(field.position.line - otherField.position.line) <= 2) {
                        related.push(otherField.id);
                    }
                }
            });
            if (related.length > 0) {
                field.relatedFields = related.slice(0, 3); // Максимум 3 связанных поля
            }
        });
    }
    async analyzeSourceDocument(docPath, targetFields) {
        const content = await fs.readFile(docPath, 'utf-8');
        const extractedData = new Map();
        // Извлекаем структурированные данные
        const dataExtractor = new DataExtractor();
        const extracted = await dataExtractor.extractData(content);
        // Сопоставляем с полями целевого документа
        let totalMatches = 0;
        let successfulMatches = 0;
        for (const field of targetFields) {
            totalMatches++;
            const matchedData = this.findMatchingData(field, extracted);
            if (matchedData) {
                extractedData.set(field.id, matchedData);
                successfulMatches++;
            }
        }
        const confidence = totalMatches > 0 ? successfulMatches / totalMatches : 0;
        return {
            path: docPath,
            type: this.determineDocumentType(docPath, content),
            content,
            extractedData,
            confidence
        };
    }
    findMatchingData(field, extractedData) {
        const fieldKeywords = this.extractKeywords(field.placeholder);
        let bestMatch = null;
        let bestScore = 0;
        for (const [key, value] of extractedData.entries()) {
            const score = this.calculateMatchScore(fieldKeywords, key, value);
            if (score > bestScore && score > 0.3) { // Минимальный порог соответствия
                bestMatch = value;
                bestScore = score;
            }
        }
        return bestMatch;
    }
    extractKeywords(text) {
        return text.toLowerCase()
            .replace(/[^\w\sіїєґ]/g, ' ')
            .split(/\s+/)
            .filter(word => word.length > 2);
    }
    calculateMatchScore(fieldKeywords, dataKey, dataValue) {
        const dataKeywords = this.extractKeywords(dataKey);
        const dataValueKeywords = typeof dataValue === 'string' ?
            this.extractKeywords(dataValue) : [];
        let matches = 0;
        let total = fieldKeywords.length;
        for (const fieldKeyword of fieldKeywords) {
            if (dataKeywords.some(dk => dk.includes(fieldKeyword) || fieldKeyword.includes(dk))) {
                matches++;
            }
            else if (dataValueKeywords.some(dv => dv.includes(fieldKeyword) || fieldKeyword.includes(dv))) {
                matches += 0.5; // Меньший вес для соответствия в значении
            }
        }
        return total > 0 ? matches / total : 0;
    }
    determineDocumentType(filePath, content) {
        const fileName = path.basename(filePath).toLowerCase();
        if (fileName.includes('template') || fileName.includes('шаблон')) {
            return 'template';
        }
        if (content.includes('{{') || content.includes('[ЗАПОВНИТИ') || content.includes('___')) {
            return 'template';
        }
        return 'reference';
    }
    async autoFillFromSources(session) {
        for (const field of session.fields) {
            let bestValue = null;
            let bestConfidence = 0;
            // Ищем лучшее соответствие среди источников
            for (const source of session.sourceDocuments) {
                if (source.extractedData.has(field.id)) {
                    const value = source.extractedData.get(field.id);
                    const confidence = source.confidence;
                    if (confidence > bestConfidence) {
                        bestValue = value;
                        bestConfidence = confidence;
                    }
                }
            }
            // Автоматически заполняем если уверенность высока
            if (bestValue && bestConfidence > 0.7) {
                session.responses.set(field.id, {
                    fieldId: field.id,
                    answer: bestValue,
                    confidence: bestConfidence,
                    source: 'auto'
                });
            }
        }
    }
    async getNextQuestion(sessionId) {
        const session = this.sessions.get(sessionId);
        if (!session || session.status !== 'questioning') {
            return null;
        }
        // Находим следующее незаполненное поле
        let currentIndex = session.currentFieldIndex;
        while (currentIndex < session.fields.length) {
            const field = session.fields[currentIndex];
            if (!session.responses.has(field.id)) {
                const question = this.generateContextualQuestion(field, session);
                const context = this.buildQuestionContext(field, session);
                session.currentFieldIndex = currentIndex;
                session.lastUpdated = new Date();
                return {
                    field,
                    question,
                    context,
                    isLastField: currentIndex === session.fields.length - 1
                };
            }
            currentIndex++;
        }
        // Все поля заполнены
        session.status = 'filling';
        return null;
    }
    generateContextualQuestion(field, session) {
        const questions = field.suggestedQuestions;
        // Выбираем наиболее подходящий вопрос
        let selectedQuestion = questions[0];
        // Если есть контекст секции, используем контекстуальный вопрос
        if (field.context.sectionTitle) {
            const contextualQ = questions.find(q => q.includes('розділ'));
            if (contextualQ)
                selectedQuestion = contextualQ;
        }
        // Добавляем подсказки из автозаполнения
        const autoFilled = session.responses.get(field.id);
        if (autoFilled && autoFilled.source === 'auto') {
            selectedQuestion += `\n\n💡 Знайдено автоматично: "${autoFilled.answer}" (впевненість: ${Math.round(autoFilled.confidence * 100)}%)`;
            selectedQuestion += `\nПідтвердити це значення? Або введіть інше:`;
        }
        return selectedQuestion;
    }
    buildQuestionContext(field, session) {
        return {
            fieldNumber: session.currentFieldIndex + 1,
            totalFields: session.fields.length,
            fieldType: field.type,
            isRequired: field.validation?.required || false,
            relatedFields: field.relatedFields ?
                field.relatedFields.map(id => session.fields.find(f => f.id === id)?.placeholder).filter(Boolean) :
                [],
            sectionTitle: field.context.sectionTitle,
            validation: field.validation,
            examples: this.generateExamples(field)
        };
    }
    generateExamples(field) {
        const examples = [];
        switch (field.type) {
            case 'date':
                examples.push('01.01.2024', '15.03.2024', '31.12.2024');
                break;
            case 'number':
                if (field.placeholder.toLowerCase().includes('сума')) {
                    examples.push('1000.50', '2500', '150.75');
                }
                else {
                    examples.push('1', '10', '100');
                }
                break;
            case 'text':
                if (field.placeholder.toLowerCase().includes('піб')) {
                    examples.push('Іванов Іван Іванович', 'Петренко Марія Олексанівна');
                }
                else if (field.placeholder.toLowerCase().includes('email')) {
                    examples.push('example@gmail.com', 'user@company.ua');
                }
                else {
                    examples.push('Приклад тексту');
                }
                break;
        }
        return examples;
    }
    async submitResponse(sessionId, fieldId, answer) {
        const session = this.sessions.get(sessionId);
        if (!session) {
            return { accepted: false, error: 'Сесія не знайдена' };
        }
        const field = session.fields.find(f => f.id === fieldId);
        if (!field) {
            return { accepted: false, error: 'Поле не знайдено' };
        }
        // Валидируем ответ
        const validation = this.validateResponse(field, answer);
        if (!validation.isValid) {
            return { accepted: false, error: validation.error };
        }
        // Сохраняем ответ
        session.responses.set(fieldId, {
            fieldId,
            answer: validation.normalizedValue,
            confidence: 1.0,
            source: 'user'
        });
        session.lastUpdated = new Date();
        // Получаем следующий вопрос
        const nextQuestion = await this.getNextQuestion(sessionId);
        return {
            accepted: true,
            nextField: nextQuestion || undefined
        };
    }
    validateResponse(field, answer) {
        if (!answer || (typeof answer === 'string' && answer.trim().length === 0)) {
            if (field.validation?.required) {
                return { isValid: false, error: 'Це поле є обов\'язковим' };
            }
            return { isValid: true, normalizedValue: '' };
        }
        const strAnswer = String(answer).trim();
        switch (field.type) {
            case 'date':
                const datePattern = /^\d{1,2}\.\d{1,2}\.\d{4}$/;
                if (!datePattern.test(strAnswer)) {
                    return { isValid: false, error: 'Формат дати має бути ДД.ММ.РРРР' };
                }
                return { isValid: true, normalizedValue: strAnswer };
            case 'number':
                const numValue = parseFloat(strAnswer.replace(',', '.'));
                if (isNaN(numValue)) {
                    return { isValid: false, error: 'Введіть правильне число' };
                }
                return { isValid: true, normalizedValue: numValue };
            case 'boolean':
                const boolValues = ['так', 'ні', 'true', 'false', '1', '0', 'yes', 'no'];
                if (!boolValues.includes(strAnswer.toLowerCase())) {
                    return { isValid: false, error: 'Введіть: Так/Ні, True/False або 1/0' };
                }
                const boolResult = ['так', 'true', '1', 'yes'].includes(strAnswer.toLowerCase());
                return { isValid: true, normalizedValue: boolResult };
            case 'text':
                if (field.validation?.minLength && strAnswer.length < field.validation.minLength) {
                    return { isValid: false, error: `Мінімальна довжина: ${field.validation.minLength} символів` };
                }
                if (field.validation?.maxLength && strAnswer.length > field.validation.maxLength) {
                    return { isValid: false, error: `Максимальна довжина: ${field.validation.maxLength} символів` };
                }
                if (field.validation?.format === 'email') {
                    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                    if (!emailPattern.test(strAnswer)) {
                        return { isValid: false, error: 'Введіть правильний email адрес' };
                    }
                }
                return { isValid: true, normalizedValue: strAnswer };
            default:
                return { isValid: true, normalizedValue: strAnswer };
        }
    }
    async fillDocument(sessionId) {
        const session = this.sessions.get(sessionId);
        if (!session) {
            return { success: false, error: 'Сесія не знайдена' };
        }
        session.status = 'filling';
        try {
            const originalContent = await fs.readFile(session.targetDocument, 'utf-8');
            let filledContent = originalContent;
            // Заполняем поля в обратном порядке (чтобы не сбить позиции)
            const sortedFields = [...session.fields].reverse();
            for (const field of sortedFields) {
                const response = session.responses.get(field.id);
                if (response) {
                    filledContent = this.replaceFieldInContent(filledContent, field, response.answer);
                }
            }
            // Генерируем путь для выходного файла
            const originalPath = session.targetDocument;
            const ext = path.extname(originalPath);
            const basename = path.basename(originalPath, ext);
            const dirname = path.dirname(originalPath);
            const outputPath = path.join(dirname, `${basename}_filled_${Date.now()}${ext}`);
            // Сохраняем заполненный документ
            await fs.writeFile(outputPath, filledContent, 'utf-8');
            session.status = 'completed';
            session.lastUpdated = new Date();
            return {
                success: true,
                filledDocument: filledContent,
                outputPath
            };
        }
        catch (error) {
            session.status = 'cancelled';
            return {
                success: false,
                error: error instanceof Error ? error.message : 'Невідома помилка'
            };
        }
    }
    replaceFieldInContent(content, field, value) {
        const lines = content.split('\n');
        const targetLine = field.position.line - 1;
        if (targetLine >= 0 && targetLine < lines.length) {
            const line = lines[targetLine];
            const before = line.substring(0, field.position.column);
            const after = line.substring(field.position.column + field.position.length);
            lines[targetLine] = before + String(value) + after;
        }
        return lines.join('\n');
    }
    getSession(sessionId) {
        return this.sessions.get(sessionId);
    }
    getAllSessions() {
        return Array.from(this.sessions.values());
    }
    cancelSession(sessionId) {
        const session = this.sessions.get(sessionId);
        if (session) {
            session.status = 'cancelled';
            session.lastUpdated = new Date();
            return true;
        }
        return false;
    }
    generateSessionId() {
        return `fill_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }
}
exports.DocumentFiller = DocumentFiller;
// Вспомогательные классы
class ContextAnalyzer {
    analyzeContext(lineIndex, column, allLines) {
        const line = allLines[lineIndex];
        const context = {
            isInList: false,
            isInTable: false,
            sectionTitle: null,
            indentLevel: 0
        };
        // Проверяем список
        if (/^\s*[-*+]\s/.test(line) || /^\s*\d+\.\s/.test(line)) {
            context.isInList = true;
        }
        // Проверяем таблицу
        if (line.includes('|') && line.split('|').length > 2) {
            context.isInTable = true;
        }
        // Ищем заголовок секции
        for (let i = lineIndex - 1; i >= 0; i--) {
            const prevLine = allLines[i].trim();
            if (prevLine.match(/^#{1,6}\s+(.+)$/)) {
                context.sectionTitle = prevLine.replace(/^#{1,6}\s+/, '');
                break;
            }
            if (prevLine.length === 0)
                continue;
            if (i < lineIndex - 10)
                break; // Не ищем слишком далеко
        }
        // Уровень отступа
        const leadingSpaces = line.match(/^\s*/)?.[0]?.length || 0;
        context.indentLevel = Math.floor(leadingSpaces / 2);
        return context;
    }
}
class DataExtractor {
    async extractData(content) {
        const extracted = new Map();
        // Извлекаем структурированные данные различными способами
        this.extractKeyValuePairs(content, extracted);
        this.extractDates(content, extracted);
        this.extractNumbers(content, extracted);
        this.extractNames(content, extracted);
        this.extractAddresses(content, extracted);
        this.extractContacts(content, extracted);
        return extracted;
    }
    extractKeyValuePairs(content, extracted) {
        // Шаблоны ключ-значение
        const patterns = [
            /([А-ЯІЇЄҐа-яіїєґA-Za-z\s]+):\s*([^\n\r]+)/g,
            /([А-ЯІЇЄҐа-яіїєґA-Za-z\s]+)\s*[-–—]\s*([^\n\r]+)/g,
            /([А-ЯІЇЄҐа-яіїєґA-Za-z\s]+)\s*=\s*([^\n\r]+)/g
        ];
        for (const pattern of patterns) {
            let match;
            while ((match = pattern.exec(content)) !== null) {
                const key = match[1].trim();
                const value = match[2].trim();
                if (key.length > 1 && value.length > 0) {
                    extracted.set(key.toLowerCase(), value);
                }
            }
        }
    }
    extractDates(content, extracted) {
        const datePattern = /\b(\d{1,2}[\.\/\-]\d{1,2}[\.\/\-]\d{2,4})\b/g;
        let match;
        while ((match = datePattern.exec(content)) !== null) {
            extracted.set('дата_' + extracted.size, match[1]);
        }
    }
    extractNumbers(content, extracted) {
        const numberPatterns = [
            /№\s*(\d+)/g,
            /(\d+(?:\.\d{2})?)\s*(?:грн|₴|UAH)/g
        ];
        for (const pattern of numberPatterns) {
            let match;
            while ((match = pattern.exec(content)) !== null) {
                extracted.set('число_' + extracted.size, match[1]);
            }
        }
    }
    extractNames(content, extracted) {
        // Простой паттерн для украинских имен
        const namePattern = /\b([А-ЯІЇЄҐ][а-яіїєґ]+(?:\s+[А-ЯІЇЄҐ][а-яіїєґ]+){1,2})\b/g;
        let match;
        while ((match = namePattern.exec(content)) !== null) {
            if (match[1].split(' ').length >= 2) {
                extracted.set('піб_' + extracted.size, match[1]);
            }
        }
    }
    extractAddresses(content, extracted) {
        // Простые паттерны адресов
        const addressPatterns = [
            /(?:вул|вулиця|проспект|пр|бульвар|б-р)\.?\s+[А-ЯІЇЄҐа-яіїєґ\s\d\-,]+/gi
        ];
        for (const pattern of addressPatterns) {
            let match;
            while ((match = pattern.exec(content)) !== null) {
                extracted.set('адреса_' + extracted.size, match[0]);
            }
        }
    }
    extractContacts(content, extracted) {
        // Телефоны
        const phonePattern = /(?:\+380|380|0)\d{9}/g;
        let match;
        while ((match = phonePattern.exec(content)) !== null) {
            extracted.set('телефон_' + extracted.size, match[0]);
        }
        // Email
        const emailPattern = /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g;
        while ((match = emailPattern.exec(content)) !== null) {
            extracted.set('email_' + extracted.size, match[0]);
        }
    }
}
//# sourceMappingURL=DocumentFiller.js.map