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
exports.SeniorDataAnalystAgent = void 0;
const BaseAgent_1 = require("../../../core/BaseAgent");
const AgentInterface_1 = require("../../../types/AgentInterface");
const fs = __importStar(require("fs-extra"));
const path = __importStar(require("path"));
class SeniorDataAnalystAgent extends BaseAgent_1.BaseAgent {
    constructor(config) {
        super(config);
        this.analysisResults = new Map();
        this.mlModels = new Map();
        this.predictionCache = new Map();
        this.anomalyDetector = null;
        this.trendAnalyzer = null;
        this.metadata = {
            name: 'senior-data-analyst',
            version: '2.0.0',
            description: 'Автономний агент для аналізу даних з ML можливостями, генерації звітів та надання інсайтів',
            category: 'analytics'
        };
        this.config = config;
    }
    getScheduleConfig() {
        const intervalMs = (this.config.analysisInterval || 360) * 60 * 1000; // 6 годин за замовчуванням
        return {
            type: AgentInterface_1.ScheduleType.INTERVAL,
            enabled: this.config.enabled !== false,
            intervalMs,
            stopOnError: false
        };
    }
    async onInitialize() {
        this.log('Senior Data Analyst Agent ініціалізується...');
        // Створюємо директорії для аналітики
        const outputPath = path.resolve(this.config.outputPath || './data/analytics');
        await fs.ensureDir(outputPath);
        await fs.ensureDir(path.join(outputPath, 'projects'));
        await fs.ensureDir(path.join(outputPath, 'reports'));
        await fs.ensureDir(path.join(outputPath, 'dashboards'));
        await fs.ensureDir(path.join(outputPath, 'ml-models'));
        await fs.ensureDir(path.join(outputPath, 'predictions'));
        await fs.ensureDir(path.join(outputPath, 'anomalies'));
        // Ініціалізуємо Memory Manager для зберігання аналітичних даних
        await this.initializeMemory();
        // Конфігуруємо спеціальні провайдери для аналітики
        this.configureMemoryProviders({
            supabase: {
                enabled: false // Можна увімкнути для production
            },
            redis: {
                enabled: false // Для кешування аналітичних результатів
            },
            elasticsearch: {
                enabled: false // Для пошуку по аналітичних даних
            }
        });
        // Завантажуємо попередні дані з пам'яті
        await this.loadHistoricalData();
        // Ініціалізуємо ML компоненти
        if (this.config.machineLearning?.enabled) {
            await this.initializeMLComponents();
        }
        // Підписуємося на події від інших агентів
        await this.on('project.updated', async (data) => {
            await this.analyzeProject(data.projectPath);
        });
        await this.on('git.commit', async (data) => {
            await this.updateCommitMetrics(data.repository, data.commit);
        });
        await this.on('qa.tests.completed', async (data) => {
            await this.updateTestMetrics(data.projectName, data.results);
        });
        await this.on('ci.build.completed', async (data) => {
            await this.updateBuildMetrics(data.projectName, data.buildData);
        });
    }
    async onShutdown() {
        this.log('Senior Data Analyst Agent зупиняється...');
        // Зберігаємо поточний стан в пам'ять
        await this.saveCurrentState();
        await this.saveAllAnalysisResults();
        // Зупиняємо Memory Manager
        await this.shutdownMemory();
    }
    async executeAutonomously() {
        const startTime = Date.now();
        this.log('Початок циклу аналізу даних...');
        try {
            // 1. Аналізуємо всі проекти
            for (const projectPath of this.config.projects || []) {
                await this.analyzeProject(projectPath);
            }
            // 2. Генеруємо звіти
            await this.generateScheduledReports();
            // 3. Оновлюємо дашборди
            await this.updateDashboards();
            // 4. Перевіряємо пороги та алерти
            await this.checkThresholds();
            // 5. ML аналіз та прогнозування
            if (this.config.machineLearning?.enabled) {
                await this.performMLAnalysis();
            }
            // 6. Виявлення аномалій
            if (this.config.advancedAnalytics?.anomalyDetection) {
                await this.detectAnomalies();
            }
            // 7. Прогнозування трендів
            if (this.config.advancedAnalytics?.trendPrediction) {
                await this.predictTrends();
            }
            // 8. Оцінка ризиків
            if (this.config.advancedAnalytics?.riskAssessment) {
                await this.assessRisks();
            }
            // Публікуємо подію про завершення аналізу
            await this.emit('analysis.completed', {
                projectsAnalyzed: this.config.projects?.length || 0,
                duration: Date.now() - startTime,
                timestamp: new Date(),
                mlEnabled: this.config.machineLearning?.enabled || false
            });
            this.log(`Аналіз завершено за ${Date.now() - startTime}мс`);
        }
        catch (error) {
            const errorMessage = error instanceof Error ? error.message : 'Невідома помилка';
            this.log(`Помилка під час аналізу: ${errorMessage}`, 'error');
            throw error;
        }
    }
    async analyzeProject(projectPath) {
        const startTime = Date.now();
        this.log(`Аналізую проект: ${projectPath}`);
        const projectName = path.basename(projectPath);
        const metrics = {
            projectName,
            timestamp: new Date(),
            codeQuality: await this.analyzeCodeQuality(projectPath),
            testing: await this.analyzeTestingMetrics(projectPath),
            development: await this.analyzeDevelopmentMetrics(projectPath),
            performance: await this.analyzePerformanceMetrics(projectPath)
        };
        // Зберігаємо результати
        if (!this.analysisResults.has(projectName)) {
            this.analysisResults.set(projectName, []);
        }
        this.analysisResults.get(projectName).push(metrics);
        // Зберігаємо в файл
        await this.saveProjectMetrics(projectName, metrics);
        this.log(`Проект ${projectName} проаналізовано за ${Date.now() - startTime}мс`);
        return metrics;
    }
    async analyzeCodeQuality(projectPath) {
        try {
            // Аналізуємо структуру проекту
            const stats = await this.getProjectStats(projectPath);
            // Простий аналіз складності (можна розширити)
            const complexity = await this.calculateComplexity(projectPath);
            const maintainabilityIndex = Math.max(0, 100 - (complexity * 2));
            const technicalDebt = complexity > 10 ? complexity - 10 : 0;
            return {
                complexity: Math.round(complexity),
                maintainabilityIndex: Math.round(maintainabilityIndex),
                technicalDebt: Math.round(technicalDebt),
                codeSmells: Math.floor(stats.linesOfCode / 1000) // Приблизно
            };
        }
        catch (error) {
            this.log(`Помилка аналізу якості коду: ${error}`, 'warn');
            return {
                complexity: 0,
                maintainabilityIndex: 0,
                technicalDebt: 0,
                codeSmells: 0
            };
        }
    }
    async analyzeTestingMetrics(projectPath) {
        try {
            // Шукаємо тестові файли
            const testFiles = await this.findTestFiles(projectPath);
            // Пробуємо знайти coverage звіти
            const coverageData = await this.getCoverageData(projectPath);
            return {
                coverage: coverageData.percentage || 0,
                testCount: testFiles.length,
                passRate: coverageData.passRate || 100
            };
        }
        catch (error) {
            this.log(`Помилка аналізу тестів: ${error}`, 'warn');
            return {
                coverage: 0,
                testCount: 0,
                passRate: 0
            };
        }
    }
    async analyzeDevelopmentMetrics(projectPath) {
        try {
            const stats = await this.getProjectStats(projectPath);
            const gitStats = await this.getGitStats(projectPath);
            return {
                commits: gitStats.commits,
                contributors: gitStats.contributors,
                linesOfCode: stats.linesOfCode,
                filesChanged: gitStats.filesChanged
            };
        }
        catch (error) {
            this.log(`Помилка аналізу розробки: ${error}`, 'warn');
            return {
                commits: 0,
                contributors: 0,
                linesOfCode: 0,
                filesChanged: 0
            };
        }
    }
    async analyzePerformanceMetrics(projectPath) {
        try {
            // Аналізуємо CI/CD метрики (якщо доступні)
            const buildData = await this.getBuildMetrics(projectPath);
            return {
                buildTime: buildData.averageBuildTime || 0,
                testTime: buildData.averageTestTime || 0,
                deploymentFrequency: buildData.deploymentsPerWeek || 0
            };
        }
        catch (error) {
            this.log(`Помилка аналізу продуктивності: ${error}`, 'warn');
            return {
                buildTime: 0,
                testTime: 0,
                deploymentFrequency: 0
            };
        }
    }
    async getProjectStats(projectPath) {
        let linesOfCode = 0;
        let fileCount = 0;
        const countLines = async (dir) => {
            const entries = await fs.readdir(dir, { withFileTypes: true });
            for (const entry of entries) {
                const fullPath = path.join(dir, entry.name);
                if (entry.isDirectory() && !entry.name.startsWith('.') && entry.name !== 'node_modules') {
                    await countLines(fullPath);
                }
                else if (entry.isFile() && this.isCodeFile(entry.name)) {
                    try {
                        const content = await fs.readFile(fullPath, 'utf8');
                        linesOfCode += content.split('\n').length;
                        fileCount++;
                    }
                    catch (error) {
                        // Ігноруємо помилки читання файлів
                    }
                }
            }
        };
        if (await fs.pathExists(projectPath)) {
            await countLines(projectPath);
        }
        return { linesOfCode, fileCount };
    }
    async calculateComplexity(projectPath) {
        // Простий розрахунок складності на основі структури проекту
        let complexity = 0;
        const stats = await this.getProjectStats(projectPath);
        // Базова складність на основі кількості файлів
        complexity += stats.fileCount * 0.5;
        // Додаткова складність на основі кількості рядків коду
        complexity += stats.linesOfCode / 1000;
        return complexity;
    }
    async findTestFiles(projectPath) {
        const testFiles = [];
        const findTests = async (dir) => {
            try {
                const entries = await fs.readdir(dir, { withFileTypes: true });
                for (const entry of entries) {
                    const fullPath = path.join(dir, entry.name);
                    if (entry.isDirectory() && !entry.name.startsWith('.') && entry.name !== 'node_modules') {
                        await findTests(fullPath);
                    }
                    else if (entry.isFile() && this.isTestFile(entry.name)) {
                        testFiles.push(fullPath);
                    }
                }
            }
            catch (error) {
                // Ігноруємо помилки доступу до директорій
            }
        };
        if (await fs.pathExists(projectPath)) {
            await findTests(projectPath);
        }
        return testFiles;
    }
    async getCoverageData(projectPath) {
        // Пробуємо знайти файли coverage
        const coverageFiles = [
            path.join(projectPath, 'coverage', 'coverage-summary.json'),
            path.join(projectPath, 'coverage', 'lcov-report', 'index.html'),
            path.join(projectPath, 'jest-coverage', 'coverage-summary.json')
        ];
        for (const file of coverageFiles) {
            if (await fs.pathExists(file)) {
                try {
                    if (file.endsWith('.json')) {
                        const data = await fs.readJson(file);
                        return {
                            percentage: data.total?.lines?.pct || 0,
                            passRate: 100 // Припускаємо 100% якщо є coverage
                        };
                    }
                }
                catch (error) {
                    this.log(`Помилка читання coverage: ${error}`, 'warn');
                }
            }
        }
        return { percentage: 0, passRate: 0 };
    }
    async getGitStats(projectPath) {
        try {
            const gitDir = path.join(projectPath, '.git');
            if (!await fs.pathExists(gitDir)) {
                return { commits: 0, contributors: 0, filesChanged: 0 };
            }
            // Спрощений аналіз git (в реальності краще використовувати git API)
            const { stdout: commitCount } = await this.executeCommand(`cd "${projectPath}" && git rev-list --all --count`);
            const { stdout: contributors } = await this.executeCommand(`cd "${projectPath}" && git shortlog -sn | wc -l`);
            const { stdout: changedFiles } = await this.executeCommand(`cd "${projectPath}" && git diff --name-only HEAD~1 2>/dev/null | wc -l`);
            return {
                commits: parseInt(commitCount.trim()) || 0,
                contributors: parseInt(contributors.trim()) || 1,
                filesChanged: parseInt(changedFiles.trim()) || 0
            };
        }
        catch (error) {
            this.log(`Помилка аналізу git: ${error}`, 'warn');
            return { commits: 0, contributors: 0, filesChanged: 0 };
        }
    }
    async getBuildMetrics(projectPath) {
        // Тут можна додати інтеграцію з CI/CD системами
        return {
            averageBuildTime: 120, // секунди
            averageTestTime: 30,
            deploymentsPerWeek: 5
        };
    }
    isCodeFile(fileName) {
        const codeExtensions = ['.js', '.ts', '.jsx', '.tsx', '.py', '.java', '.cs', '.cpp', '.c', '.go', '.rb', '.php'];
        return codeExtensions.some(ext => fileName.endsWith(ext));
    }
    isTestFile(fileName) {
        return fileName.includes('.test.') ||
            fileName.includes('.spec.') ||
            fileName.includes('_test.') ||
            fileName.includes('Test.') ||
            fileName.includes('Spec.');
    }
    async generateScheduledReports() {
        const now = new Date();
        const timeString = now.toTimeString().substring(0, 5); // HH:MM
        // Перевіряємо чи потрібно генерувати щоденний звіт
        if (this.config.reportSchedule?.daily === timeString) {
            await this.generateDailyReport();
        }
        // Перевіряємо чи потрібно генерувати тижневий звіт
        const dayOfWeek = now.toLocaleDateString('en-US', { weekday: 'long' }).toLowerCase();
        const weeklySchedule = this.config.reportSchedule?.weekly;
        if (weeklySchedule && weeklySchedule === `${dayOfWeek}:${timeString}`) {
            await this.generateWeeklyReport();
        }
    }
    async generateDailyReport() {
        this.log('Генерую щоденний звіт...');
        const report = {
            date: new Date().toISOString().split('T')[0],
            summary: await this.generateSummary('daily'),
            projects: Array.from(this.analysisResults.entries()).map(([name, metrics]) => ({
                name,
                latestMetrics: metrics[metrics.length - 1]
            }))
        };
        const outputPath = path.join(this.config.outputPath || './data/analytics', 'reports', 'daily');
        await fs.ensureDir(outputPath);
        await fs.writeJson(path.join(outputPath, `${report.date}.json`), report, { spaces: 2 });
        await this.emit('report.generated', {
            type: 'daily',
            date: report.date,
            projectCount: report.projects.length
        });
    }
    async generateWeeklyReport() {
        this.log('Генерую тижневий звіт...');
        const report = {
            week: this.getWeekString(),
            summary: await this.generateSummary('weekly'),
            trends: await this.analyzeTrends(),
            recommendations: await this.generateRecommendations()
        };
        const outputPath = path.join(this.config.outputPath || './data/analytics', 'reports', 'weekly');
        await fs.ensureDir(outputPath);
        await fs.writeJson(path.join(outputPath, `${report.week}.json`), report, { spaces: 2 });
        await this.emit('report.generated', {
            type: 'weekly',
            week: report.week,
            trendsCount: Object.keys(report.trends).length
        });
    }
    async generateSummary(period) {
        const allMetrics = Array.from(this.analysisResults.values()).flat();
        if (allMetrics.length === 0) {
            return { message: 'Немає даних для аналізу' };
        }
        const avgQuality = allMetrics.reduce((sum, m) => sum + m.codeQuality.maintainabilityIndex, 0) / allMetrics.length;
        const avgCoverage = allMetrics.reduce((sum, m) => sum + m.testing.coverage, 0) / allMetrics.length;
        const totalCommits = allMetrics.reduce((sum, m) => sum + m.development.commits, 0);
        return {
            projectsAnalyzed: this.analysisResults.size,
            averageCodeQuality: Math.round(avgQuality),
            averageTestCoverage: Math.round(avgCoverage),
            totalCommits,
            period
        };
    }
    async analyzeTrends() {
        // Аналізуємо тренди по проектах
        const trends = {};
        for (const [projectName, metrics] of this.analysisResults.entries()) {
            if (metrics.length < 2)
                continue;
            const recent = metrics.slice(-7); // Останні 7 записів
            const old = metrics.slice(-14, -7); // Попередні 7 записів
            if (old.length === 0)
                continue;
            const recentAvg = recent.reduce((sum, m) => sum + m.codeQuality.maintainabilityIndex, 0) / recent.length;
            const oldAvg = old.reduce((sum, m) => sum + m.codeQuality.maintainabilityIndex, 0) / old.length;
            trends[projectName] = {
                qualityTrend: recentAvg > oldAvg ? 'improving' : 'declining',
                qualityChange: Math.round(recentAvg - oldAvg)
            };
        }
        return trends;
    }
    async generateRecommendations() {
        const recommendations = [];
        for (const [projectName, metrics] of this.analysisResults.entries()) {
            const latest = metrics[metrics.length - 1];
            if (latest.testing.coverage < this.config.thresholds?.testCoverage || 80) {
                recommendations.push(`${projectName}: Збільшити покриття тестами (поточне: ${latest.testing.coverage}%)`);
            }
            if (latest.codeQuality.maintainabilityIndex < this.config.thresholds?.codeQuality || 70) {
                recommendations.push(`${projectName}: Покращити якість коду (індекс: ${latest.codeQuality.maintainabilityIndex})`);
            }
            if (latest.codeQuality.technicalDebt > this.config.thresholds?.techDebt || 30) {
                recommendations.push(`${projectName}: Зменшити технічний борг (поточний: ${latest.codeQuality.technicalDebt})`);
            }
        }
        return recommendations;
    }
    async checkThresholds() {
        for (const [projectName, metrics] of this.analysisResults.entries()) {
            const latest = metrics[metrics.length - 1];
            // Перевіряємо пороги та відправляємо алерти
            if (latest.testing.coverage < (this.config.thresholds?.testCoverage || 80)) {
                await this.emit('alert.threshold', {
                    type: 'coverage',
                    project: projectName,
                    value: latest.testing.coverage,
                    threshold: this.config.thresholds?.testCoverage || 80
                });
            }
            if (latest.codeQuality.maintainabilityIndex < (this.config.thresholds?.codeQuality || 70)) {
                await this.emit('alert.threshold', {
                    type: 'quality',
                    project: projectName,
                    value: latest.codeQuality.maintainabilityIndex,
                    threshold: this.config.thresholds?.codeQuality || 70
                });
            }
        }
    }
    async updateDashboards() {
        const dashboardData = {
            summary: await this.generateSummary('daily'),
            projects: Array.from(this.analysisResults.entries()).map(([name, metrics]) => ({
                name,
                latest: metrics[metrics.length - 1],
                trend: metrics.length > 1 ? this.calculateTrend(metrics.slice(-2)) : 'stable'
            })),
            updatedAt: new Date().toISOString()
        };
        const dashboardPath = path.join(this.config.outputPath || './data/analytics', 'dashboards', 'main.json');
        await fs.ensureDir(path.dirname(dashboardPath));
        await fs.writeJson(dashboardPath, dashboardData, { spaces: 2 });
    }
    calculateTrend(metrics) {
        if (metrics.length < 2)
            return 'stable';
        const [old, recent] = metrics;
        const oldScore = old.codeQuality.maintainabilityIndex;
        const recentScore = recent.codeQuality.maintainabilityIndex;
        const diff = recentScore - oldScore;
        if (diff > 2)
            return 'improving';
        if (diff < -2)
            return 'declining';
        return 'stable';
    }
    async saveProjectMetrics(projectName, metrics) {
        const outputPath = path.join(this.config.outputPath || './data/analytics', 'projects', projectName);
        await fs.ensureDir(outputPath);
        // Зберігаємо поточні метрики
        await fs.writeJson(path.join(outputPath, 'latest.json'), metrics, { spaces: 2 });
        // Додаємо до історії
        const historyPath = path.join(outputPath, 'history.json');
        let history = [];
        if (await fs.pathExists(historyPath)) {
            history = await fs.readJson(historyPath);
        }
        history.push(metrics);
        // Зберігаємо останні 100 записів
        if (history.length > 100) {
            history = history.slice(-100);
        }
        await fs.writeJson(historyPath, history, { spaces: 2 });
    }
    async saveAllAnalysisResults() {
        for (const [projectName, metrics] of this.analysisResults.entries()) {
            if (metrics.length > 0) {
                await this.saveProjectMetrics(projectName, metrics[metrics.length - 1]);
            }
        }
    }
    getWeekString() {
        const now = new Date();
        const startOfYear = new Date(now.getFullYear(), 0, 1);
        const days = Math.floor((now.getTime() - startOfYear.getTime()) / (24 * 60 * 60 * 1000));
        const weekNumber = Math.ceil((days + startOfYear.getDay() + 1) / 7);
        return `${now.getFullYear()}-W${weekNumber.toString().padStart(2, '0')}`;
    }
    async updateCommitMetrics(repository, commitData) {
        // Оновлюємо метрики коммітів для проекту
        this.log(`Оновлюю метрики коммітів для ${repository}`);
    }
    async updateTestMetrics(projectName, testResults) {
        // Оновлюємо метрики тестування
        this.log(`Оновлюю метрики тестування для ${projectName}`);
    }
    async updateBuildMetrics(projectName, buildData) {
        // Оновлюємо метрики збірки
        this.log(`Оновлюю метрики збірки для ${projectName}`);
    }
    // MCP Tool handlers
    getTools() {
        return [
            {
                name: 'analyze_project',
                description: 'Аналізує вказаний проект та генерує звіт',
                inputSchema: {
                    type: 'object',
                    properties: {
                        projectPath: { type: 'string', description: 'Шлях до проекту' },
                        analysisType: { type: 'string', enum: ['full', 'quick', 'custom'], description: 'Тип аналізу' },
                        outputFormat: { type: 'string', enum: ['json', 'html', 'csv'], description: 'Формат звіту' }
                    },
                    required: ['projectPath']
                }
            },
            {
                name: 'generate_report',
                description: 'Генерує звіт на основі зібраних даних',
                inputSchema: {
                    type: 'object',
                    properties: {
                        reportType: { type: 'string', enum: ['daily', 'weekly', 'monthly', 'custom'] },
                        includeSections: { type: 'array', items: { type: 'string' } },
                        projects: { type: 'array', items: { type: 'string' } }
                    },
                    required: ['reportType']
                }
            },
            {
                name: 'get_metrics',
                description: 'Повертає поточні метрики проектів',
                inputSchema: {
                    type: 'object',
                    properties: {
                        projects: { type: 'array', items: { type: 'string' } },
                        timeRange: { type: 'string', enum: ['1d', '7d', '30d', 'custom'] },
                        metrics: { type: 'array', items: { type: 'string' } }
                    }
                }
            },
            {
                name: 'predict_timeline',
                description: 'Прогнозує терміни виконання на основі історичних даних',
                inputSchema: {
                    type: 'object',
                    properties: {
                        projectName: { type: 'string', description: 'Назва проекту' },
                        remainingTasks: { type: 'number', description: 'Кількість задач що залишились' },
                        confidence: { type: 'string', enum: ['low', 'medium', 'high'] }
                    },
                    required: ['projectName', 'remainingTasks']
                }
            }
        ];
    }
    // ML та розширені аналітичні методи
    async initializeMLComponents() {
        this.log('Ініціалізую ML компоненти...');
        try {
            // Ініціалізуємо базові ML моделі
            this.anomalyDetector = new SimpleAnomalyDetector();
            this.trendAnalyzer = new TrendAnalyzer();
            // Завантажуємо збережені моделі
            await this.loadMLModels();
            this.log('ML компоненти ініціалізовано успішно');
        }
        catch (error) {
            this.log(`Помилка ініціалізації ML: ${error}`, 'error');
        }
    }
    async loadMLModels() {
        const modelsPath = path.join(this.config.outputPath || './data/analytics', 'ml-models');
        try {
            const modelFiles = await fs.readdir(modelsPath);
            for (const modelFile of modelFiles) {
                if (modelFile.endsWith('.json')) {
                    const modelData = await fs.readJson(path.join(modelsPath, modelFile));
                    const modelName = path.basename(modelFile, '.json');
                    this.mlModels.set(modelName, modelData);
                }
            }
        }
        catch (error) {
            this.log(`Помилка завантаження ML моделей: ${error}`, 'warn');
        }
    }
    async performMLAnalysis() {
        this.log('Виконую ML аналіз...');
        for (const [projectName, metrics] of this.analysisResults.entries()) {
            if (metrics.length < 5)
                continue; // Потрібно мінімум 5 точок даних
            // Прогнозування якості коду
            const qualityPrediction = await this.predictCodeQuality(metrics);
            // Прогнозування термінів виконання
            const timelinePrediction = await this.predictProjectTimeline(metrics);
            // Оптимізація процесів
            const optimizationSuggestions = await this.generateOptimizationSuggestions(metrics);
            const prediction = {
                projectName,
                timestamp: new Date(),
                qualityPrediction,
                timelinePrediction,
                optimizationSuggestions
            };
            this.predictionCache.set(projectName, prediction);
            // Зберігаємо прогнози
            await this.savePrediction(projectName, prediction);
        }
    }
    async predictCodeQuality(metrics) {
        // Простий алгоритм прогнозування якості на основі тренду
        const qualityTrend = this.calculateQualityTrend(metrics);
        const currentQuality = metrics[metrics.length - 1].codeQuality.maintainabilityIndex;
        const prediction = {
            current: currentQuality,
            predicted30Days: Math.max(0, Math.min(100, currentQuality + (qualityTrend * 30))),
            confidence: this.calculateConfidence(metrics),
            trend: qualityTrend > 0 ? 'improving' : qualityTrend < 0 ? 'declining' : 'stable'
        };
        return prediction;
    }
    async predictProjectTimeline(metrics) {
        // Аналіз швидкості розробки
        const avgCommitsPerWeek = metrics.reduce((sum, m) => sum + m.development.commits, 0) / metrics.length;
        const avgVelocity = this.calculateVelocity(metrics);
        return {
            estimatedWeeksToCompletion: Math.ceil(100 / Math.max(avgVelocity, 1)),
            confidence: this.calculateTimelineConfidence(metrics),
            recommendedTeamSize: Math.ceil(avgCommitsPerWeek / 10), // 10 commits на особу на тиждень
            riskFactors: this.identifyRiskFactors(metrics)
        };
    }
    async generateOptimizationSuggestions(metrics) {
        const suggestions = [];
        const latest = metrics[metrics.length - 1];
        if (latest.testing.coverage < 80) {
            suggestions.push('Збільшити покриття тестами для покращення якості');
        }
        if (latest.codeQuality.complexity > 10) {
            suggestions.push('Рефакторинг складних компонентів для зменшення складності');
        }
        if (latest.performance.buildTime > 300) {
            suggestions.push('Оптимізувати процес збірки для зменшення часу');
        }
        const velocity = this.calculateVelocity(metrics);
        if (velocity < 5) {
            suggestions.push('Розглянути автоматизацію для підвищення швидкості розробки');
        }
        return suggestions;
    }
    async detectAnomalies() {
        this.log('Виявляю аномалії...');
        for (const [projectName, metrics] of this.analysisResults.entries()) {
            if (metrics.length < 10)
                continue; // Потрібно достатньо даних
            const anomalies = this.anomalyDetector.detect(metrics);
            if (anomalies.length > 0) {
                await this.handleAnomalies(projectName, anomalies);
            }
        }
    }
    async predictTrends() {
        this.log('Прогнозую тренди...');
        const trendPredictions = await this.trendAnalyzer.predictTrends(this.analysisResults);
        // Зберігаємо прогнози трендів
        const outputPath = path.join(this.config.outputPath || './data/analytics', 'predictions', 'trends.json');
        await fs.writeJson(outputPath, trendPredictions, { spaces: 2 });
    }
    async assessRisks() {
        this.log('Оцінюю ризики...');
        const risks = {};
        for (const [projectName, metrics] of this.analysisResults.entries()) {
            risks[projectName] = {
                qualityRisk: this.assessQualityRisk(metrics),
                timelineRisk: this.assessTimelineRisk(metrics),
                performanceRisk: this.assessPerformanceRisk(metrics),
                overallRisk: 'medium'
            };
        }
        // Зберігаємо оцінку ризиків
        const outputPath = path.join(this.config.outputPath || './data/analytics', 'risk-assessment.json');
        await fs.writeJson(outputPath, risks, { spaces: 2 });
    }
    // Допоміжні методи для ML
    calculateQualityTrend(metrics) {
        if (metrics.length < 2)
            return 0;
        const recent = metrics.slice(-5);
        let trend = 0;
        for (let i = 1; i < recent.length; i++) {
            trend += recent[i].codeQuality.maintainabilityIndex - recent[i - 1].codeQuality.maintainabilityIndex;
        }
        return trend / (recent.length - 1);
    }
    calculateConfidence(metrics) {
        // Більше даних = більше впевненості
        const dataPoints = metrics.length;
        const variance = this.calculateVarianceFromMetrics(metrics);
        return Math.max(0.1, Math.min(1.0, (dataPoints / 30) * (1 - variance / 100)));
    }
    calculateVarianceFromMetrics(metrics) {
        const values = metrics.map(m => m.codeQuality.maintainabilityIndex);
        return this.calculateVariance(values);
    }
    calculateVelocity(metrics) {
        if (metrics.length < 2)
            return 0;
        const totalProgress = metrics.reduce((sum, m) => sum + m.development.commits, 0);
        const timeSpan = metrics.length; // Approximation
        return totalProgress / timeSpan;
    }
    calculateTimelineConfidence(metrics) {
        const variance = this.calculateVarianceFromMetrics(metrics);
        return Math.max(0.1, 1 - (variance / 50));
    }
    identifyRiskFactors(metrics) {
        const risks = [];
        const latest = metrics[metrics.length - 1];
        if (latest.testing.coverage < 50)
            risks.push('Низьке покриття тестами');
        if (latest.codeQuality.technicalDebt > 20)
            risks.push('Високий технічний борг');
        if (latest.development.contributors < 2)
            risks.push('Залежність від одного розробника');
        return risks;
    }
    assessQualityRisk(metrics) {
        const latest = metrics[metrics.length - 1];
        const trend = this.calculateQualityTrend(metrics);
        if (latest.codeQuality.maintainabilityIndex < 50 || trend < -2)
            return 'high';
        if (latest.codeQuality.maintainabilityIndex < 70 || trend < 0)
            return 'medium';
        return 'low';
    }
    assessTimelineRisk(metrics) {
        const velocity = this.calculateVelocity(metrics);
        if (velocity < 2)
            return 'high';
        if (velocity < 5)
            return 'medium';
        return 'low';
    }
    assessPerformanceRisk(metrics) {
        const latest = metrics[metrics.length - 1];
        if (latest.performance.buildTime > 600)
            return 'high';
        if (latest.performance.buildTime > 300)
            return 'medium';
        return 'low';
    }
    async handleAnomalies(projectName, anomalies) {
        this.log(`Виявлено ${anomalies.length} аномалій в проекті ${projectName}`);
        await this.emit('anomaly.detected', {
            project: projectName,
            anomalies,
            timestamp: new Date()
        });
        // Зберігаємо аномалії
        const outputPath = path.join(this.config.outputPath || './data/analytics', 'anomalies', `${projectName}.json`);
        await fs.writeJson(outputPath, { projectName, anomalies, timestamp: new Date() }, { spaces: 2 });
    }
    async savePrediction(projectName, prediction) {
        const outputPath = path.join(this.config.outputPath || './data/analytics', 'predictions', `${projectName}.json`);
        await fs.writeJson(outputPath, prediction, { spaces: 2 });
    }
    async handleToolCall(toolName, args) {
        switch (toolName) {
            case 'analyze_project':
                const metrics = await this.analyzeProject(args.projectPath);
                return {
                    success: true,
                    metrics,
                    analysisType: args.analysisType || 'full'
                };
            case 'generate_report':
                if (args.reportType === 'daily') {
                    await this.generateDailyReport();
                }
                else if (args.reportType === 'weekly') {
                    await this.generateWeeklyReport();
                }
                return {
                    success: true,
                    reportType: args.reportType,
                    timestamp: new Date().toISOString()
                };
            case 'get_metrics':
                const projectMetrics = args.projects
                    ? args.projects.map((p) => ({
                        project: p,
                        metrics: this.analysisResults.get(p)?.slice(-1)[0]
                    }))
                    : Array.from(this.analysisResults.entries()).map(([name, metrics]) => ({
                        project: name,
                        metrics: metrics.slice(-1)[0]
                    }));
                return {
                    success: true,
                    data: projectMetrics,
                    timeRange: args.timeRange || '1d'
                };
            case 'predict_timeline':
                const projectHistory = this.analysisResults.get(args.projectName);
                if (!projectHistory || projectHistory.length < 5) {
                    return {
                        success: false,
                        message: 'Недостатньо історичних даних для ML прогнозування'
                    };
                }
                const mlPrediction = await this.predictProjectTimeline(projectHistory);
                return {
                    success: true,
                    projectName: args.projectName,
                    prediction: mlPrediction,
                    confidence: args.confidence || 'medium',
                    mlEnabled: true
                };
            default:
                throw new Error(`Невідомий інструмент: ${toolName}`);
        }
    }
    // Memory-enhanced methods for analytics
    async loadHistoricalData() {
        this.log('Завантажую історичні дані з пам\'яті...');
        // Завантажуємо попередні аналітичні результати
        const historicalMetrics = await this.queryMemory({
            type: 'analytics',
            tags: ['project-metrics']
        });
        historicalMetrics.forEach(record => {
            const projectName = record.data.projectName;
            if (!this.analysisResults.has(projectName)) {
                this.analysisResults.set(projectName, []);
            }
            this.analysisResults.get(projectName).push(record.data);
        });
        // Завантажуємо ML моделі з пам'яті
        const storedModels = await this.queryMemory({
            type: 'knowledge',
            tags: ['ml-model']
        });
        storedModels.forEach(record => {
            this.mlModels.set(record.data.modelName, record.data.modelData);
        });
        // Завантажуємо кеш прогнозів
        const cachedPredictions = await this.queryMemory({
            type: 'cache',
            tags: ['prediction']
        });
        cachedPredictions.forEach(record => {
            this.predictionCache.set(record.data.key, record.data.prediction);
        });
        this.log(`Завантажено ${historicalMetrics.length} історичних записів`);
    }
    async saveCurrentState() {
        this.log('Зберігаю поточний стан в пам\'ять...');
        const state = {
            totalProjects: this.analysisResults.size,
            lastAnalysisTime: new Date(),
            mlModelsCount: this.mlModels.size,
            predictionsCount: this.predictionCache.size,
            analysisResults: Array.from(this.analysisResults.entries())
        };
        await this.storeMemory('configuration', state, ['agent-state', 'current']);
    }
    // Enhanced project analysis with memory storage
    async analyzeProjectWithMemory(projectPath) {
        const projectName = path.basename(projectPath);
        // Перевіряємо, чи є кешовані результати
        const cachedAnalysis = await this.getCachedAnalysis(projectName);
        if (cachedAnalysis && this.isCacheValid(cachedAnalysis)) {
            this.log(`Використовую кешований аналіз для ${projectName}`);
            return cachedAnalysis.data;
        }
        // Виконуємо аналіз
        const metrics = await this.analyzeProject(projectPath);
        // Зберігаємо в пам'ять
        await this.storeProjectMetricsInMemory(metrics);
        // Зберігаємо в кеш
        await this.cacheAnalysisResult(projectName, metrics);
        return metrics;
    }
    async storeProjectMetricsInMemory(metrics) {
        // Основні метрики
        await this.storeMemory('analytics', metrics, ['project-metrics', metrics.projectName]);
        // Окремо зберігаємо тренди для ML
        const trendData = {
            projectName: metrics.projectName,
            qualityTrend: metrics.codeQuality.maintainabilityIndex,
            coverageTrend: metrics.testing.coverage,
            complexityTrend: metrics.codeQuality.complexity,
            timestamp: metrics.timestamp
        };
        await this.storeMemory('analytics', trendData, ['trend-data', 'ml-training']);
        // Зберігаємо аномалії, якщо вони є
        if (metrics.codeQuality.maintainabilityIndex < 30) {
            await this.storeMemory('analytics', {
                type: 'quality-anomaly',
                project: metrics.projectName,
                value: metrics.codeQuality.maintainabilityIndex,
                timestamp: metrics.timestamp
            }, ['anomaly', 'quality']);
        }
    }
    async getCachedAnalysis(projectName) {
        const cached = await this.queryMemory({
            type: 'cache',
            tags: ['analysis-cache', projectName],
            limit: 1
        });
        return cached.length > 0 ? cached[0] : null;
    }
    isCacheValid(cachedResult) {
        const cacheAge = Date.now() - new Date(cachedResult.metadata.createdAt).getTime();
        const maxAge = 30 * 60 * 1000; // 30 хвилин
        return cacheAge < maxAge;
    }
    async cacheAnalysisResult(projectName, metrics) {
        await this.storeMemory('cache', {
            projectName,
            data: metrics,
            analyzedAt: new Date()
        }, ['analysis-cache', projectName]);
    }
    // Enhanced ML analysis with memory
    async performMLAnalysisWithMemory() {
        this.log('Виконую ML аналіз з використанням пам\'яті...');
        // Завантажуємо тренувальні дані з пам'яті
        const trainingData = await this.queryMemory({
            type: 'analytics',
            tags: ['trend-data', 'ml-training'],
            limit: 1000
        });
        if (trainingData.length < 10) {
            this.log('Недостатньо даних для ML аналізу', 'warn');
            return;
        }
        for (const [projectName, metrics] of this.analysisResults.entries()) {
            if (metrics.length < 5)
                continue;
            // Використовуємо історичні дані для більш точного прогнозування
            const historicalData = trainingData
                .filter(record => record.data.projectName === projectName)
                .map(record => record.data);
            const enhancedPrediction = await this.enhancedMLPrediction(metrics, historicalData);
            // Зберігаємо прогноз в пам'ять
            await this.storePredictionInMemory(projectName, enhancedPrediction);
            this.predictionCache.set(projectName, enhancedPrediction);
        }
    }
    async enhancedMLPrediction(currentMetrics, historicalData) {
        const allData = [...historicalData, ...currentMetrics];
        // Розширений аналіз з використанням історичних даних
        const qualityTrend = this.calculateEnhancedTrend(allData, 'qualityTrend');
        const coverageTrend = this.calculateEnhancedTrend(allData, 'coverageTrend');
        const prediction = {
            quality: {
                current: currentMetrics[currentMetrics.length - 1].codeQuality.maintainabilityIndex,
                predicted30Days: this.predictValue(qualityTrend, 30),
                predicted90Days: this.predictValue(qualityTrend, 90),
                confidence: this.calculatePredictionConfidence(allData)
            },
            coverage: {
                current: currentMetrics[currentMetrics.length - 1].testing.coverage,
                predicted30Days: this.predictValue(coverageTrend, 30),
                predicted90Days: this.predictValue(coverageTrend, 90)
            },
            risk: this.assessProjectRisk(allData),
            recommendations: this.generateEnhancedRecommendations(allData),
            timestamp: new Date()
        };
        return prediction;
    }
    async storePredictionInMemory(projectName, prediction) {
        // Зберігаємо детальний прогноз
        await this.storeMemory('analytics', {
            type: 'ml-prediction',
            project: projectName,
            prediction,
            timestamp: new Date()
        }, ['prediction', 'ml', projectName]);
        // Зберігаємо короткий кешований варіант
        await this.storeMemory('cache', {
            key: `prediction_${projectName}`,
            prediction: {
                qualityDirection: prediction.quality.predicted30Days > prediction.quality.current ? 'improving' : 'declining',
                riskLevel: prediction.risk.level,
                nextReview: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000)
            }
        }, ['prediction', 'cache']);
    }
    // Memory-enhanced anomaly detection
    async detectAnomaliesWithMemory() {
        this.log('Виявляю аномалії з використанням пам\'яті...');
        // Завантажуємо базові показники з пам'яті
        const baselineData = await this.queryMemory({
            type: 'knowledge',
            tags: ['baseline', 'metrics']
        });
        let baseline = null;
        if (baselineData.length > 0) {
            baseline = baselineData[0].data;
        }
        else {
            // Створюємо базові показники
            baseline = await this.createBaseline();
            await this.storeKnowledge(baseline, ['baseline', 'metrics']);
        }
        for (const [projectName, metrics] of this.analysisResults.entries()) {
            const anomalies = this.enhancedAnomalyDetection(metrics, baseline);
            if (anomalies.length > 0) {
                // Зберігаємо аномалії в пам'ять
                await this.storeMemory('analytics', {
                    type: 'anomalies-detected',
                    project: projectName,
                    anomalies,
                    severity: this.calculateAnomalySeverity(anomalies),
                    timestamp: new Date()
                }, ['anomalies', projectName]);
                await this.handleAnomalies(projectName, anomalies);
            }
        }
    }
    async createBaseline() {
        const allMetrics = Array.from(this.analysisResults.values()).flat();
        const baseline = {
            qualityBaseline: allMetrics.reduce((sum, m) => sum + m.codeQuality.maintainabilityIndex, 0) / allMetrics.length,
            coverageBaseline: allMetrics.reduce((sum, m) => sum + m.testing.coverage, 0) / allMetrics.length,
            complexityBaseline: allMetrics.reduce((sum, m) => sum + m.codeQuality.complexity, 0) / allMetrics.length,
            createdAt: new Date()
        };
        return baseline;
    }
    enhancedAnomalyDetection(metrics, baseline) {
        const anomalies = [];
        const latest = metrics[metrics.length - 1];
        // Використовуємо базові показники для виявлення аномалій
        const qualityDeviation = Math.abs(latest.codeQuality.maintainabilityIndex - baseline.qualityBaseline);
        const coverageDeviation = Math.abs(latest.testing.coverage - baseline.coverageBaseline);
        if (qualityDeviation > 30) {
            anomalies.push({
                type: 'quality_deviation',
                severity: qualityDeviation > 50 ? 'high' : 'medium',
                current: latest.codeQuality.maintainabilityIndex,
                baseline: baseline.qualityBaseline,
                deviation: qualityDeviation
            });
        }
        if (coverageDeviation > 20) {
            anomalies.push({
                type: 'coverage_deviation',
                severity: coverageDeviation > 40 ? 'high' : 'medium',
                current: latest.testing.coverage,
                baseline: baseline.coverageBaseline,
                deviation: coverageDeviation
            });
        }
        return anomalies;
    }
    // Utility methods for enhanced analysis
    calculateEnhancedTrend(data, field) {
        if (data.length < 2)
            return 0;
        const values = data.map(d => d[field] || 0);
        return this.calculateLinearTrend(values);
    }
    calculateLinearTrend(values) {
        const n = values.length;
        const x = Array.from({ length: n }, (_, i) => i);
        const meanX = x.reduce((a, b) => a + b) / n;
        const meanY = values.reduce((a, b) => a + b) / n;
        const numerator = x.reduce((sum, xi, i) => sum + (xi - meanX) * (values[i] - meanY), 0);
        const denominator = x.reduce((sum, xi) => sum + (xi - meanX) ** 2, 0);
        return denominator === 0 ? 0 : numerator / denominator;
    }
    predictValue(trend, days) {
        return Math.max(0, Math.min(100, trend * days));
    }
    calculatePredictionConfidence(data) {
        const dataPoints = data.length;
        const variance = this.calculateVariance(data.map(d => d.qualityTrend || 0));
        return Math.max(0.1, Math.min(1.0, (dataPoints / 50) * (1 - variance / 100)));
    }
    calculateVariance(values) {
        const mean = values.reduce((sum, v) => sum + v, 0) / values.length;
        const variance = values.reduce((sum, v) => sum + Math.pow(v - mean, 2), 0) / values.length;
        return Math.sqrt(variance);
    }
    assessProjectRisk(data) {
        const latest = data[data.length - 1];
        let riskScore = 0;
        const risks = [];
        if (latest.qualityTrend < 50) {
            riskScore += 30;
            risks.push('Низька якість коду');
        }
        if (latest.coverageTrend < 60) {
            riskScore += 25;
            risks.push('Низьке покриття тестами');
        }
        const trend = this.calculateLinearTrend(data.map(d => d.qualityTrend || 0));
        if (trend < -1) {
            riskScore += 20;
            risks.push('Негативний тренд якості');
        }
        return {
            score: riskScore,
            level: riskScore > 50 ? 'high' : riskScore > 25 ? 'medium' : 'low',
            factors: risks
        };
    }
    generateEnhancedRecommendations(data) {
        const recommendations = [];
        const latest = data[data.length - 1];
        if (latest.qualityTrend < 50) {
            recommendations.push('Провести код-рев\'ю та рефакторинг критичних компонентів');
        }
        if (latest.coverageTrend < 60) {
            recommendations.push('Збільшити покриття тестами до рівня 80%+');
        }
        const trend = this.calculateLinearTrend(data.map(d => d.qualityTrend || 0));
        if (trend < -1) {
            recommendations.push('Запровадити щоденний моніторинг якості коду');
        }
        return recommendations;
    }
    calculateAnomalySeverity(anomalies) {
        const highSeverity = anomalies.filter(a => a.severity === 'high').length;
        const mediumSeverity = anomalies.filter(a => a.severity === 'medium').length;
        if (highSeverity > 0)
            return 'high';
        if (mediumSeverity > 1)
            return 'medium';
        return 'low';
    }
}
exports.SeniorDataAnalystAgent = SeniorDataAnalystAgent;
// Допоміжні класи для ML
class SimpleAnomalyDetector {
    detect(metrics) {
        const anomalies = [];
        // Виявляємо різкі зміни в якості
        for (let i = 1; i < metrics.length; i++) {
            const current = metrics[i].codeQuality.maintainabilityIndex;
            const previous = metrics[i - 1].codeQuality.maintainabilityIndex;
            const change = Math.abs(current - previous);
            if (change > 20) {
                anomalies.push({
                    type: 'quality_spike',
                    severity: change > 40 ? 'high' : 'medium',
                    timestamp: metrics[i].timestamp,
                    change: current - previous
                });
            }
        }
        return anomalies;
    }
}
class TrendAnalyzer {
    async predictTrends(analysisResults) {
        const trends = {};
        for (const [projectName, metrics] of analysisResults.entries()) {
            if (metrics.length < 5)
                continue;
            trends[projectName] = {
                quality: this.analyzeTrend(metrics.map(m => m.codeQuality.maintainabilityIndex)),
                coverage: this.analyzeTrend(metrics.map(m => m.testing.coverage)),
                velocity: this.analyzeTrend(metrics.map(m => m.development.commits))
            };
        }
        return trends;
    }
    analyzeTrend(values) {
        if (values.length < 3)
            return { direction: 'unknown', strength: 0 };
        const trend = this.calculateLinearTrend(values);
        return {
            direction: trend > 0.1 ? 'increasing' : trend < -0.1 ? 'decreasing' : 'stable',
            strength: Math.abs(trend),
            prediction30Days: values[values.length - 1] + (trend * 30)
        };
    }
    calculateLinearTrend(values) {
        const n = values.length;
        const x = Array.from({ length: n }, (_, i) => i);
        const meanX = x.reduce((a, b) => a + b) / n;
        const meanY = values.reduce((a, b) => a + b) / n;
        const numerator = x.reduce((sum, xi, i) => sum + (xi - meanX) * (values[i] - meanY), 0);
        const denominator = x.reduce((sum, xi) => sum + (xi - meanX) ** 2, 0);
        return denominator === 0 ? 0 : numerator / denominator;
    }
}
//# sourceMappingURL=index.js.map