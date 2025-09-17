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
exports.WebScraperAgent = void 0;
const BaseAgent_1 = require("../../../core/BaseAgent");
const AgentInterface_1 = require("../../../types/AgentInterface");
const cheerio = __importStar(require("cheerio"));
const fs = __importStar(require("fs-extra"));
const path = __importStar(require("path"));
const node_fetch_1 = __importDefault(require("node-fetch"));
class WebScraperAgent extends BaseAgent_1.BaseAgent {
    constructor(config) {
        super(config);
        this.isProcessing = false;
        this.scrapingSessions = new Map();
        this.contentHashes = new Map(); // For change detection
        this.rateLimiter = new Map();
        this.failedUrls = new Set(); // Circuit breaker pattern
        this.metadata = {
            name: 'web-scraper',
            version: '1.0.0',
            description: 'Автономний агент для парсингу веб-сайтів та збереження даних у JSON',
            category: 'integration'
        };
        this.config = config;
    }
    getScheduleConfig() {
        const intervalMs = (this.config.scheduleIntervalMinutes || 60) * 60 * 1000;
        return {
            type: AgentInterface_1.ScheduleType.INTERVAL,
            enabled: this.config.enabled !== false,
            intervalMs,
            stopOnError: false,
            maxExecutions: undefined
        };
    }
    async onInitialize() {
        this.log('WebScraper Agent ініціалізується...');
        // Створюємо директорію для виводу
        const outputPath = path.resolve(this.config.outputPath || './data/scraped');
        await fs.ensureDir(outputPath);
        // Завантажуємо конфігурацію цілей з файлу, якщо є
        const configPath = path.join(outputPath, 'scraping-config.json');
        if (await fs.pathExists(configPath)) {
            try {
                const savedConfig = await fs.readJson(configPath);
                if (savedConfig.targets && savedConfig.targets.length > 0) {
                    this.config.targets = savedConfig.targets;
                    this.log(`Завантажено ${this.config.targets.length} цілей для скрапінгу`);
                }
            }
            catch (error) {
                this.log(`Помилка завантаження конфігурації: ${error}`, 'warn');
            }
        }
        // Підписуємося на події для динамічного додавання цілей
        await this.on('scraper.add_target', async (data) => {
            this.config.targets.push(data);
            await this.saveConfiguration();
            this.log(`Додано нову ціль: ${data.name}`);
        });
        await this.on('scraper.remove_target', async (data) => {
            this.config.targets = this.config.targets.filter(t => t.name !== data.name);
            await this.saveConfiguration();
            this.log(`Видалено ціль: ${data.name}`);
        });
        await this.on('scraper.scrape_now', async (data) => {
            if (data.targetName) {
                const target = this.config.targets.find(t => t.name === data.targetName);
                if (target) {
                    await this.scrapeTarget(target);
                }
            }
            else {
                await this.executeAutonomously();
            }
        });
    }
    async onShutdown() {
        this.log('WebScraper Agent зупиняється...');
        // Чекаємо завершення поточного процесу
        while (this.isProcessing) {
            await new Promise(resolve => setTimeout(resolve, 1000));
        }
    }
    async executeAutonomously() {
        if (this.isProcessing) {
            this.log('Попередній процес скрапінгу ще виконується, пропускаємо...', 'warn');
            return;
        }
        if (!this.config.targets || this.config.targets.length === 0) {
            this.log('Немає цілей для скрапінгу', 'warn');
            return;
        }
        this.isProcessing = true;
        const startTime = Date.now();
        try {
            this.log(`Початок скрапінгу ${this.config.targets.length} цілей...`);
            const results = [];
            if (this.config.concurrent) {
                // Паралельний скрапінг
                const maxConcurrent = this.config.maxConcurrent || 3;
                const chunks = this.chunkArray(this.config.targets, maxConcurrent);
                for (const chunk of chunks) {
                    const chunkResults = await Promise.all(chunk.map(target => this.scrapeTarget(target)));
                    results.push(...chunkResults);
                }
            }
            else {
                // Послідовний скрапінг
                for (const target of this.config.targets) {
                    const result = await this.scrapeTarget(target);
                    results.push(result);
                    // Затримка між запитами
                    if (target.waitTime) {
                        await new Promise(resolve => setTimeout(resolve, target.waitTime));
                    }
                }
            }
            // Зберігаємо зведені результати
            const summaryPath = path.join(this.config.outputPath || './data/scraped', 'summary.json');
            const summary = {
                timestamp: new Date().toISOString(),
                duration: Date.now() - startTime,
                targetsProcessed: results.length,
                results: results.map(r => ({
                    name: r.name,
                    success: r.success,
                    itemsCount: r.data ? r.data.length : 0,
                    error: r.error
                }))
            };
            await fs.writeJson(summaryPath, summary, { spaces: 2 });
            // Публікуємо подію з результатами
            await this.emit('scraper.completed', summary);
            // Зберігаємо статистику в DataStore
            await this.saveData('last_run', {
                timestamp: new Date(),
                targetsProcessed: results.length,
                duration: Date.now() - startTime,
                success: results.filter(r => r.success).length,
                failed: results.filter(r => !r.success).length
            });
            this.log(`Скрапінг завершено за ${Date.now() - startTime}мс`);
        }
        catch (error) {
            const errorMessage = error instanceof Error ? error.message : 'Невідома помилка';
            this.log(`Помилка під час скрапінгу: ${errorMessage}`, 'error');
            await this.emit('scraper.error', { error: errorMessage });
        }
        finally {
            this.isProcessing = false;
        }
    }
    async scrapeTarget(target) {
        const startTime = Date.now();
        try {
            this.log(`Скрапінг ${target.name} з ${target.url}`);
            const allData = [];
            let currentUrl = target.url;
            let pageNum = 1;
            const maxPages = target.pagination?.maxPages || 1;
            while (currentUrl && pageNum <= maxPages) {
                // Завантажуємо HTML
                const html = await this.fetchPage(currentUrl, target.headers);
                if (!html) {
                    throw new Error('Не вдалося завантажити сторінку');
                }
                // Парсимо HTML з cheerio
                const $ = cheerio.load(html);
                // Витягуємо дані за селекторами
                const pageData = this.extractData($, target.selectors);
                if (Array.isArray(pageData)) {
                    allData.push(...pageData);
                }
                else {
                    allData.push(pageData);
                }
                // Перевіряємо наявність наступної сторінки
                if (target.pagination?.nextSelector) {
                    const nextUrl = $(target.pagination.nextSelector).attr('href');
                    if (nextUrl) {
                        currentUrl = this.resolveUrl(nextUrl, currentUrl);
                        pageNum++;
                        // Затримка перед наступною сторінкою
                        if (target.waitTime) {
                            await new Promise(resolve => setTimeout(resolve, target.waitTime));
                        }
                    }
                    else {
                        break;
                    }
                }
                else {
                    break;
                }
            }
            // Зберігаємо результати у файл
            const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
            const outputPath = path.join(this.config.outputPath || './data/scraped', target.name, `${timestamp}.json`);
            await fs.ensureDir(path.dirname(outputPath));
            await fs.writeJson(outputPath, {
                target: target.name,
                url: target.url,
                timestamp: new Date().toISOString(),
                itemsCount: allData.length,
                data: allData
            }, { spaces: 2 });
            // Зберігаємо також останню версію
            const latestPath = path.join(this.config.outputPath || './data/scraped', target.name, 'latest.json');
            await fs.writeJson(latestPath, {
                target: target.name,
                url: target.url,
                timestamp: new Date().toISOString(),
                itemsCount: allData.length,
                data: allData
            }, { spaces: 2 });
            this.log(`${target.name}: зібрано ${allData.length} елементів за ${Date.now() - startTime}мс`);
            return {
                name: target.name,
                success: true,
                data: allData,
                duration: Date.now() - startTime
            };
        }
        catch (error) {
            const errorMessage = error instanceof Error ? error.message : 'Невідома помилка';
            this.log(`Помилка скрапінгу ${target.name}: ${errorMessage}`, 'error');
            return {
                name: target.name,
                success: false,
                error: errorMessage,
                duration: Date.now() - startTime
            };
        }
    }
    async fetchPage(url, headers) {
        try {
            const response = await (0, node_fetch_1.default)(url, {
                headers: {
                    'User-Agent': this.config.userAgent || 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    ...headers
                }
            });
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return await response.text();
        }
        catch (error) {
            this.log(`Помилка завантаження ${url}: ${error}`, 'error');
            return null;
        }
    }
    extractData($, selectors) {
        const result = {};
        for (const [key, selectorConfig] of Object.entries(selectors)) {
            const config = typeof selectorConfig === 'string'
                ? { selector: selectorConfig }
                : selectorConfig;
            if (config.multiple) {
                result[key] = [];
                $(config.selector).each((i, elem) => {
                    const value = this.extractValue($, elem, config);
                    if (value !== null) {
                        result[key].push(value);
                    }
                });
            }
            else {
                const elem = $(config.selector).first()[0];
                if (elem) {
                    result[key] = this.extractValue($, elem, config);
                }
            }
        }
        return result;
    }
    extractValue($, elem, config) {
        let value;
        if (config.attribute) {
            value = $(elem).attr(config.attribute);
        }
        else {
            value = $(elem).text().trim();
        }
        // Трансформація значення
        if (value && config.transform) {
            switch (config.transform) {
                case 'number':
                    value = parseFloat(value.replace(/[^\d.-]/g, ''));
                    break;
                case 'date':
                    value = new Date(value).toISOString();
                    break;
                case 'html':
                    value = $(elem).html();
                    break;
                case 'url':
                    if (!value.startsWith('http')) {
                        value = new URL(value, 'https://example.com').href;
                    }
                    break;
            }
        }
        return value;
    }
    resolveUrl(url, baseUrl) {
        if (url.startsWith('http')) {
            return url;
        }
        const base = new URL(baseUrl);
        return new URL(url, base.origin).href;
    }
    chunkArray(array, size) {
        const chunks = [];
        for (let i = 0; i < array.length; i += size) {
            chunks.push(array.slice(i, i + size));
        }
        return chunks;
    }
    async saveConfiguration() {
        const configPath = path.join(this.config.outputPath || './data/scraped', 'scraping-config.json');
        await fs.writeJson(configPath, {
            targets: this.config.targets,
            updatedAt: new Date().toISOString()
        }, { spaces: 2 });
    }
    // 🚀 ENHANCED METHODS
    // Smart content change detection
    async detectContentChanges(target, newContent) {
        if (!this.config.smartScraping?.detectChanges)
            return true;
        const contentHash = this.generateContentHash(newContent);
        const previousHash = this.contentHashes.get(target.name);
        if (previousHash && previousHash === contentHash) {
            this.log(`Контент для ${target.name} не змінився, пропускаю...`);
            return false; // No changes detected
        }
        this.contentHashes.set(target.name, contentHash);
        return true; // Changes detected or first time
    }
    generateContentHash(content) {
        // Simple hash function for content comparison
        let hash = 0;
        for (let i = 0; i < content.length; i++) {
            const char = content.charCodeAt(i);
            hash = ((hash << 5) - hash) + char;
            hash = hash & hash; // Convert to 32bit integer
        }
        return hash.toString();
    }
    // Adaptive rate limiting based on server response
    async adaptiveRateLimit(domain) {
        if (!this.config.smartScraping?.adaptiveRateLimiting)
            return;
        const now = Date.now();
        const domainLimiter = this.rateLimiter.get(domain) || { requests: 0, resetTime: now + 60000 };
        // Reset counter every minute
        if (now > domainLimiter.resetTime) {
            domainLimiter.requests = 0;
            domainLimiter.resetTime = now + 60000;
        }
        domainLimiter.requests++;
        // Dynamic delay based on request count
        const delay = Math.min(domainLimiter.requests * 100, 5000); // Max 5 seconds
        if (delay > 0) {
            await new Promise(resolve => setTimeout(resolve, delay));
        }
        this.rateLimiter.set(domain, domainLimiter);
    }
    // Circuit breaker pattern for failed URLs
    shouldSkipUrl(url) {
        return this.failedUrls.has(url);
    }
    markUrlAsFailed(url) {
        this.failedUrls.add(url);
        // Remove from failed list after 1 hour
        setTimeout(() => this.failedUrls.delete(url), 3600000);
    }
    // Enhanced error handling with retry logic
    async fetchPageWithRetry(url, headers) {
        const retryConfig = this.config.retryConfig || {
            maxRetries: 3,
            backoffMultiplier: 2,
            timeoutMs: 30000
        };
        let lastError = null;
        for (let attempt = 0; attempt <= retryConfig.maxRetries; attempt++) {
            try {
                if (attempt > 0) {
                    const delay = Math.pow(retryConfig.backoffMultiplier, attempt) * 1000;
                    await new Promise(resolve => setTimeout(resolve, delay));
                }
                const domain = new URL(url).hostname;
                await this.adaptiveRateLimit(domain);
                const response = await (0, node_fetch_1.default)(url, {
                    headers: {
                        'User-Agent': this.config.userAgent || 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                        ...headers
                    },
                    timeout: retryConfig.timeoutMs
                });
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                const html = await response.text();
                // Quality filtering
                if (this.config.smartScraping?.qualityFiltering && !this.isQualityContent(html)) {
                    throw new Error('Low quality content detected');
                }
                return html;
            }
            catch (error) {
                lastError = error instanceof Error ? error : new Error('Unknown error');
                this.log(`Спроба ${attempt + 1} не вдалася для ${url}: ${lastError.message}`, 'warn');
            }
        }
        this.markUrlAsFailed(url);
        return null;
    }
    // Quality content detection
    isQualityContent(html) {
        // Simple heuristics for content quality
        const $ = cheerio.load(html);
        const textContent = $('body').text().trim();
        // Check for minimum content length
        if (textContent.length < 100)
            return false;
        // Check for error indicators
        const errorIndicators = ['404', 'not found', 'error', 'blocked', 'captcha'];
        const lowerText = textContent.toLowerCase();
        for (const indicator of errorIndicators) {
            if (lowerText.includes(indicator) && lowerText.length < 1000) {
                return false;
            }
        }
        return true;
    }
    // Smart content deduplication
    deduplicateResults(results) {
        if (!this.config.smartScraping?.contentDeduplication)
            return results;
        const seen = new Set();
        return results.filter(item => {
            const key = JSON.stringify(item);
            const hash = this.generateContentHash(key);
            if (seen.has(hash)) {
                return false;
            }
            seen.add(hash);
            return true;
        });
    }
    // Enhanced scraping session management
    async createScrapingSession(targets) {
        const sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        const session = {
            id: sessionId,
            targets,
            startTime: new Date(),
            status: 'running',
            progress: 0,
            results: []
        };
        this.scrapingSessions.set(sessionId, session);
        await this.emit('scraping.session.started', {
            sessionId,
            targetCount: targets.length
        });
        return sessionId;
    }
    async getScrapingSession(sessionId) {
        return this.scrapingSessions.get(sessionId) || null;
    }
    // ML-based selector optimization (simplified)
    async optimizeSelectors(target, html) {
        if (!this.config.smartScraping?.enableML)
            return;
        const $ = cheerio.load(html);
        // Analyze selector performance and suggest improvements
        for (const [key, selectorConfig] of Object.entries(target.selectors)) {
            const config = typeof selectorConfig === 'string'
                ? { selector: selectorConfig }
                : selectorConfig;
            const elements = $(config.selector);
            if (elements.length === 0) {
                // Suggest alternative selectors
                const alternatives = this.suggestAlternativeSelectors($, key);
                if (alternatives.length > 0) {
                    this.log(`Пропоную альтернативні селектори для ${key}: ${alternatives.join(', ')}`, 'info');
                }
            }
        }
    }
    suggestAlternativeSelectors($, contentType) {
        const alternatives = [];
        // Common patterns for different content types
        const patterns = {
            title: ['h1', 'h2', '.title', '[data-title]', 'title'],
            price: ['.price', '.cost', '[data-price]', '.amount'],
            description: ['.description', '.desc', '[data-description]', 'p'],
            image: ['img', '.image', '[data-image]', 'picture img'],
            link: ['a[href]', '.link', '[data-link]']
        };
        const typePatterns = patterns[contentType.toLowerCase()] || [];
        for (const pattern of typePatterns) {
            const elements = $(pattern);
            if (elements.length > 0) {
                alternatives.push(pattern);
            }
        }
        return alternatives;
    }
    // Enhanced analytics and insights
    async generateScrapingInsights() {
        const insights = {
            totalTargets: this.config.targets.length,
            successRate: 0,
            averageResponseTime: 0,
            contentChanges: 0,
            qualityIssues: 0,
            recommendations: []
        };
        // Calculate success rate
        const totalAttempts = this.config.targets.length;
        const failedAttempts = this.failedUrls.size;
        insights.successRate = Math.round(((totalAttempts - failedAttempts) / totalAttempts) * 100);
        // Generate recommendations
        if (insights.successRate < 80) {
            insights.recommendations.push('Розглянути додавання proxy серверів для покращення доступності');
        }
        if (this.failedUrls.size > 0) {
            insights.recommendations.push('Перевірити failed URLs та оновити селектори');
        }
        return insights;
    }
    // MCP Tool handlers
    getTools() {
        return [
            {
                name: 'add_scraping_target',
                description: 'Додає нову ціль для веб-скрапінгу',
                inputSchema: {
                    type: 'object',
                    properties: {
                        name: { type: 'string', description: 'Унікальна назва цілі' },
                        url: { type: 'string', description: 'URL для скрапінгу' },
                        selectors: { type: 'object', description: 'CSS селектори для витягування даних' },
                        pagination: { type: 'object', description: 'Налаштування пагінації (опціонально)' }
                    },
                    required: ['name', 'url', 'selectors']
                }
            },
            {
                name: 'scrape_now',
                description: 'Запускає скрапінг негайно',
                inputSchema: {
                    type: 'object',
                    properties: {
                        targetName: { type: 'string', description: 'Назва цілі (опціонально, всі якщо не вказано)' }
                    }
                }
            },
            {
                name: 'list_scraping_targets',
                description: 'Показує список всіх налаштованих цілей скрапінгу',
                inputSchema: {
                    type: 'object',
                    properties: {}
                }
            },
            {
                name: 'get_scraped_data',
                description: 'Отримує останні зібрані дані',
                inputSchema: {
                    type: 'object',
                    properties: {
                        targetName: { type: 'string', description: 'Назва цілі' }
                    },
                    required: ['targetName']
                }
            }
        ];
    }
    async handleToolCall(toolName, args) {
        switch (toolName) {
            case 'add_scraping_target':
                await this.emit('scraper.add_target', args);
                return { success: true, message: `Додано ціль: ${args.name}` };
            case 'scrape_now':
                await this.emit('scraper.scrape_now', args);
                return { success: true, message: 'Скрапінг запущено' };
            case 'list_scraping_targets':
                return {
                    targets: this.config.targets.map(t => ({
                        name: t.name,
                        url: t.url,
                        selectorsCount: Object.keys(t.selectors).length,
                        hasPagination: !!t.pagination
                    }))
                };
            case 'get_scraped_data':
                const latestPath = path.join(this.config.outputPath || './data/scraped', args.targetName, 'latest.json');
                if (await fs.pathExists(latestPath)) {
                    return await fs.readJson(latestPath);
                }
                else {
                    throw new Error(`Дані для ${args.targetName} не знайдено`);
                }
            default:
                throw new Error(`Невідомий інструмент: ${toolName}`);
        }
    }
}
exports.WebScraperAgent = WebScraperAgent;
//# sourceMappingURL=index.js.map