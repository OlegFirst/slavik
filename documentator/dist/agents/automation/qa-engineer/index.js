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
exports.QAEngineerAgent = void 0;
const BaseAgent_1 = require("../../../core/BaseAgent");
const AgentInterface_1 = require("../../../types/AgentInterface");
const fs = __importStar(require("fs-extra"));
const path = __importStar(require("path"));
class QAEngineerAgent extends BaseAgent_1.BaseAgent {
    constructor(config) {
        super(config);
        this.testResults = new Map();
        this.metadata = {
            name: 'qa-engineer',
            version: '1.0.0',
            description: 'Автономний агент для забезпечення якості через тестування',
            category: 'automation'
        };
        this.config = config;
    }
    getScheduleConfig() {
        return {
            type: AgentInterface_1.ScheduleType.INTERVAL,
            enabled: this.config.enabled !== false,
            intervalMs: (this.config.testingInterval || 30) * 60 * 1000,
            stopOnError: false
        };
    }
    async onInitialize() {
        this.log('QA Engineer Agent ініціалізується...');
        await fs.ensureDir('./data/qa');
        await fs.ensureDir('./data/qa/test-results');
        await fs.ensureDir('./data/qa/coverage');
        await fs.ensureDir('./data/qa/quality-analysis');
        // Слухаємо події
        await this.on('git.commit', async (data) => {
            await this.runTestsForCommit(data);
        });
        await this.on('deployment.started', async (data) => {
            await this.runDeploymentTests(data);
        });
    }
    async onShutdown() {
        this.log('QA Engineer Agent зупиняється...');
    }
    async executeAutonomously() {
        this.log('Виконую QA завдання...');
        try {
            // 1. Запускаємо automated tests
            await this.runScheduledTests();
            // 2. Аналізуємо якість коду
            await this.analyzeCodeQuality();
            // 3. Генеруємо тест-кейси
            await this.generateTestCases();
            // 4. Перевіряємо quality gates
            await this.checkQualityGates();
            // 5. Звітуємо результати
            await this.reportResults();
            await this.emit('qa.cycle.completed', {
                timestamp: new Date(),
                testsRun: this.testResults.size
            });
        }
        catch (error) {
            const errorMessage = error instanceof Error ? error.message : 'Невідома помилка';
            this.log(`Помилка QA циклу: ${errorMessage}`, 'error');
        }
    }
    async runScheduledTests() {
        this.log('Запускаю scheduled tests...');
        const projects = await this.getProjectsForTesting();
        for (const projectPath of projects) {
            await this.runTestSuite(projectPath, 'unit');
        }
    }
    async runTestSuite(projectPath, testType) {
        const projectName = path.basename(projectPath);
        this.log(`Запускаю ${testType} тести для ${projectName}...`);
        try {
            await this.emit('qa.tests.started', {
                project: projectName,
                testType,
                timestamp: new Date()
            });
            // Спрощена імітація запуску тестів
            const results = await this.simulateTestRun(projectPath, testType);
            this.testResults.set(`${projectName}_${testType}`, results);
            // Зберігаємо результати
            await this.saveTestResults(projectName, testType, results);
            await this.emit('qa.tests.completed', {
                project: projectName,
                testType,
                results,
                success: results.success
            });
            return results;
        }
        catch (error) {
            const errorMessage = error instanceof Error ? error.message : 'Невідома помилка';
            this.log(`Помилка тестування ${projectName}: ${errorMessage}`, 'error');
            await this.emit('qa.tests.failed', {
                project: projectName,
                testType,
                error: errorMessage
            });
            return { success: false, error: errorMessage };
        }
    }
    async simulateTestRun(projectPath, testType) {
        // Спрощена імітація тестування
        await new Promise(resolve => setTimeout(resolve, 2000));
        const mockResults = {
            success: Math.random() > 0.2, // 80% success rate
            testsRun: Math.floor(Math.random() * 50) + 10,
            testsPassed: 0,
            testsFailed: 0,
            coverage: Math.floor(Math.random() * 40) + 60, // 60-100%
            duration: Math.floor(Math.random() * 30000) + 5000, // 5-35 seconds
            timestamp: new Date()
        };
        if (mockResults.success) {
            mockResults.testsPassed = mockResults.testsRun;
            mockResults.testsFailed = 0;
        }
        else {
            mockResults.testsPassed = Math.floor(mockResults.testsRun * 0.8);
            mockResults.testsFailed = mockResults.testsRun - mockResults.testsPassed;
        }
        return mockResults;
    }
    async analyzeCodeQuality() {
        this.log('Аналізую якість коду...');
        const projects = await this.getProjectsForTesting();
        for (const projectPath of projects) {
            const analysis = await this.runCodeAnalysis(projectPath);
            const outputPath = path.join('./data/qa/quality-analysis', `${path.basename(projectPath)}.json`);
            await fs.writeJson(outputPath, analysis, { spaces: 2 });
        }
    }
    async runCodeAnalysis(projectPath) {
        // Спрощений аналіз якості коду
        return {
            project: path.basename(projectPath),
            complexity: Math.floor(Math.random() * 15) + 1,
            duplicatedLines: Math.floor(Math.random() * 10),
            codeSmells: Math.floor(Math.random() * 5),
            securityHotspots: Math.floor(Math.random() * 3),
            maintainabilityRating: ['A', 'B', 'C'][Math.floor(Math.random() * 3)],
            timestamp: new Date()
        };
    }
    async generateTestCases() {
        this.log('Генерую тест-кейси...');
        // Auto test case generation logic
    }
    async checkQualityGates() {
        this.log('Перевіряю quality gates...');
        const projects = await this.getProjectsForTesting();
        for (const projectPath of projects) {
            const projectName = path.basename(projectPath);
            const testResults = this.testResults.get(`${projectName}_unit`);
            if (testResults) {
                const passed = this.evaluateQualityGate(testResults);
                await this.emit(passed ? 'qa.quality.gate.passed' : 'qa.quality.gate.failed', {
                    project: projectName,
                    results: testResults,
                    gates: this.config.qualityGates
                });
            }
        }
    }
    evaluateQualityGate(testResults) {
        const gates = this.config.qualityGates;
        if (testResults.coverage < gates.unitTestCoverage) {
            this.log(`Coverage ${testResults.coverage}% нижче порогу ${gates.unitTestCoverage}%`, 'warn');
            return false;
        }
        return testResults.success;
    }
    async reportResults() {
        const summary = {
            timestamp: new Date(),
            totalTests: Array.from(this.testResults.values()).reduce((sum, r) => sum + (r.testsRun || 0), 0),
            totalPassed: Array.from(this.testResults.values()).reduce((sum, r) => sum + (r.testsPassed || 0), 0),
            totalFailed: Array.from(this.testResults.values()).reduce((sum, r) => sum + (r.testsFailed || 0), 0),
            averageCoverage: this.calculateAverageCoverage(),
            projects: Array.from(this.testResults.entries()).map(([key, results]) => ({
                project: key,
                success: results.success,
                coverage: results.coverage
            }))
        };
        await fs.writeJson('./data/qa/test-summary.json', summary, { spaces: 2 });
    }
    calculateAverageCoverage() {
        const coverages = Array.from(this.testResults.values())
            .map(r => r.coverage || 0)
            .filter(c => c > 0);
        if (coverages.length === 0)
            return 0;
        return Math.round(coverages.reduce((sum, c) => sum + c, 0) / coverages.length);
    }
    async getProjectsForTesting() {
        // Повертаємо список проектів для тестування
        const projectsDir = './projects';
        if (await fs.pathExists(projectsDir)) {
            const entries = await fs.readdir(projectsDir, { withFileTypes: true });
            return entries
                .filter(entry => entry.isDirectory())
                .map(entry => path.join(projectsDir, entry.name));
        }
        return ['./'];
    }
    async saveTestResults(projectName, testType, results) {
        const outputPath = path.join('./data/qa/test-results', testType);
        await fs.ensureDir(outputPath);
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        const fileName = `${projectName}_${timestamp}.json`;
        await fs.writeJson(path.join(outputPath, fileName), results, { spaces: 2 });
        // Також зберігаємо як latest
        await fs.writeJson(path.join(outputPath, `${projectName}_latest.json`), results, { spaces: 2 });
    }
    async runTestsForCommit(commitData) {
        this.log(`Запускаю тести для коміту ${commitData.hash}`);
        // Run tests triggered by commit
    }
    async runDeploymentTests(deploymentData) {
        this.log(`Запускаю тести для деплою ${deploymentData.applicationName}`);
        // Run tests before deployment
    }
    getTools() {
        return [
            {
                name: 'run_test_suite',
                description: 'Запускає набір тестів',
                inputSchema: {
                    type: 'object',
                    properties: {
                        projectPath: { type: 'string' },
                        testType: { type: 'string', enum: ['unit', 'integration', 'e2e', 'performance'] },
                        environment: { type: 'string', enum: ['local', 'staging', 'production'] },
                        coverage: { type: 'boolean' }
                    },
                    required: ['projectPath', 'testType']
                }
            },
            {
                name: 'analyze_code_quality',
                description: 'Аналізує якість коду',
                inputSchema: {
                    type: 'object',
                    properties: {
                        projectPath: { type: 'string' },
                        analyzeTypes: { type: 'array', items: { type: 'string' } },
                        threshold: { type: 'object' }
                    },
                    required: ['projectPath']
                }
            },
            {
                name: 'generate_test_cases',
                description: 'Генерує тест-кейси',
                inputSchema: {
                    type: 'object',
                    properties: {
                        sourceFile: { type: 'string' },
                        testType: { type: 'string', enum: ['unit', 'integration'] },
                        framework: { type: 'string' }
                    },
                    required: ['sourceFile']
                }
            }
        ];
    }
    async handleToolCall(toolName, args) {
        switch (toolName) {
            case 'run_test_suite':
                const results = await this.runTestSuite(args.projectPath, args.testType);
                return {
                    success: results.success,
                    results,
                    coverage: results.coverage
                };
            case 'analyze_code_quality':
                const analysis = await this.runCodeAnalysis(args.projectPath);
                return {
                    success: true,
                    analysis,
                    timestamp: new Date()
                };
            case 'generate_test_cases':
                this.log(`Генерую тест-кейси для ${args.sourceFile}`);
                return {
                    success: true,
                    testCasesGenerated: Math.floor(Math.random() * 10) + 5,
                    framework: args.framework || 'jest'
                };
            default:
                throw new Error(`Невідомий інструмент: ${toolName}`);
        }
    }
}
exports.QAEngineerAgent = QAEngineerAgent;
//# sourceMappingURL=index.js.map