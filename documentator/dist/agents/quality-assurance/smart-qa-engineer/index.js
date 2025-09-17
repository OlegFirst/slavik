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
exports.SmartQAEngineerAgent = void 0;
exports.createSmartQAEngineer = createSmartQAEngineer;
const BaseAgent_1 = require("../../../core/BaseAgent");
const AgentInterface_1 = require("../../../types/AgentInterface");
const fs = __importStar(require("fs-extra"));
const path = __importStar(require("path"));
class SmartQAEngineerAgent extends BaseAgent_1.BaseAgent {
    constructor(config) {
        super(config);
        this.testResults = new Map();
        this.bugReports = new Map();
        this.qualityMetrics = null;
        this.flakyTests = new Set();
        this.aiModels = new Map();
        this.metadata = {
            name: 'smart-qa-engineer',
            version: '2.0.0',
            description: 'AI-powered QA automation with intelligent testing and quality analysis',
            category: 'quality-assurance'
        };
        this.config = config;
    }
    getScheduleConfig() {
        return {
            type: AgentInterface_1.ScheduleType.INTERVAL,
            enabled: this.config.enabled !== false,
            intervalMs: 300000, // 5 minutes
            stopOnError: false
        };
    }
    async onInitialize() {
        this.log('🧪 Smart QA Engineer Agent з AI тестуванням ініціалізується...');
        // Initialize memory system
        await this.initializeMemory();
        // Configure memory providers for QA data
        this.configureMemoryProviders({
            mongodb: { enabled: true, database: 'qa_data' },
            elasticsearch: { enabled: true },
            redis: { enabled: true, database: 3 },
            file: { enabled: true, path: './data/qa' }
        });
        // Load historical QA data
        await this.loadHistoricalQAData();
        // Initialize AI models for testing
        if (this.config.aiTesting?.enabled) {
            await this.initializeAITestingModels();
        }
        // Set up event listeners
        await this.setupQAEventListeners();
        this.log('✅ Smart QA Engineer готовий до тестування');
    }
    async onShutdown() {
        this.log('🛑 Smart QA Engineer зупиняється...');
        // Save current test results and metrics
        await this.saveTestResults();
        await this.saveQualityMetrics();
        await this.saveAIInsights();
        await this.shutdownMemory();
        this.log('👋 Smart QA Engineer завершив роботу');
    }
    async executeAutonomously() {
        this.log('🤖 Виконую автономне тестування та аналіз якості...');
        try {
            // 1. Smart test execution based on changes
            if (this.config.aiTesting?.smartTestSelection) {
                await this.executeSmartTestSelection();
            }
            else {
                await this.executeScheduledTests();
            }
            // 2. AI-powered bug prediction
            if (this.config.aiTesting?.bugPrediction) {
                await this.predictPotentialBugs();
            }
            // 3. Flaky test detection and analysis
            if (this.config.aiTesting?.flakyTestDetection) {
                await this.analyzeFlakyTests();
            }
            // 4. Generate missing tests using AI
            if (this.config.aiTesting?.testGeneration) {
                await this.generateMissingTests();
            }
            // 5. Quality metrics analysis
            await this.analyzeQualityMetrics();
            // 6. Automated bug reporting
            await this.processAutomatedBugReports();
            // 7. Performance regression detection
            await this.detectPerformanceRegressions();
            // 8. Security vulnerability scanning
            await this.performSecurityScanning();
            // 9. Coordinate with other agents
            await this.coordinateWithOtherAgents();
        }
        catch (error) {
            const errorMessage = error instanceof Error ? error.message : 'Unknown error';
            this.log(`❌ Помилка автономного виконання: ${errorMessage}`, 'error');
            await this.storeMemory('analytics', {
                type: 'error',
                error: errorMessage,
                context: 'autonomous_qa_execution',
                timestamp: new Date()
            }, ['error', 'qa']);
        }
    }
    // AI-Enhanced Testing Methods
    async initializeAITestingModels() {
        this.log('🧠 Ініціалізую AI моделі для тестування...');
        // Load historical test data for training
        const historicalTests = await this.queryMemory({
            type: 'analytics',
            tags: ['test-results']
        });
        const historicalBugs = await this.queryMemory({
            type: 'analytics',
            tags: ['bugs']
        });
        // Train models
        this.aiModels.set('flaky_test_predictor', this.trainFlakyTestPredictor(historicalTests));
        this.aiModels.set('bug_predictor', this.trainBugPredictor(historicalBugs));
        this.aiModels.set('test_generator', this.initializeTestGenerator());
        this.aiModels.set('test_selector', this.trainSmartTestSelector(historicalTests));
        this.log(`🎯 AI моделі готові (${historicalTests.length} тестів, ${historicalBugs.length} багів)`);
    }
    async executeSmartTestSelection() {
        this.log('🎯 Виконую розумний вибір тестів...');
        // Get recent code changes
        const recentChanges = await this.getRecentCodeChanges();
        // Use AI to select relevant tests
        const selectedTests = await this.selectRelevantTests(recentChanges);
        for (const testSuite of selectedTests) {
            const results = await this.executeTestSuite(testSuite);
            await this.processTestResults(results);
        }
        await this.storeMemory('analytics', {
            type: 'smart_test_execution',
            selectedTests: selectedTests.length,
            totalAvailableTests: await this.getTotalTestCount(),
            executionTime: Date.now(),
            coverage: await this.getCurrentCoverage()
        }, ['ai', 'test-selection']);
    }
    async predictPotentialBugs() {
        this.log('🔮 Прогнозую потенційні баги...');
        const bugPredictor = this.aiModels.get('bug_predictor');
        if (!bugPredictor)
            return;
        // Analyze recent code changes
        const codeChanges = await this.getRecentCodeChanges();
        const codeMetrics = await this.analyzeCodeMetrics();
        for (const change of codeChanges) {
            const bugProbability = this.calculateBugProbability(change, codeMetrics);
            if (bugProbability > 0.7) {
                const predictedBug = await this.createPredictedBugReport(change, bugProbability);
                await this.storeMemory('analytics', {
                    type: 'predicted_bug',
                    bug: predictedBug,
                    probability: bugProbability,
                    timestamp: new Date()
                }, ['ai', 'bug-prediction']);
                // Notify team about high-risk changes
                await this.emit('qa.bug.predicted', {
                    change,
                    probability: bugProbability,
                    recommendations: this.generateBugPreventionRecommendations(change)
                });
            }
        }
    }
    async analyzeFlakyTests() {
        this.log('🔍 Аналізую нестабільні тести...');
        const recentTestResults = await this.getRecentTestResults();
        const flakyTestCandidates = this.identifyFlakyTestCandidates(recentTestResults);
        for (const testName of flakyTestCandidates) {
            const analysis = await this.analyzeFlakyTestPattern(testName);
            if (analysis.confidence > 0.8) {
                this.flakyTests.add(testName);
                await this.storeMemory('analytics', {
                    type: 'flaky_test',
                    testName,
                    analysis,
                    timestamp: new Date()
                }, ['flaky-tests', 'analysis']);
                // Create bug report for flaky test
                const bugReport = await this.createFlakyTestBugReport(testName, analysis);
                this.bugReports.set(bugReport.id, bugReport);
                await this.emit('qa.flaky_test.detected', {
                    testName,
                    analysis,
                    suggestions: analysis.suggestions
                });
            }
        }
    }
    async generateMissingTests() {
        this.log('🔧 Генерую відсутні тести за допомогою AI...');
        const uncoveredCode = await this.identifyUncoveredCode();
        const testGenerator = this.aiModels.get('test_generator');
        for (const file of uncoveredCode) {
            if (file.coveragePercentage < 80) {
                const generatedTests = await this.generateTestsForFile(file.path);
                if (generatedTests.length > 0) {
                    const testSuite = {
                        id: this.generateId(),
                        name: `AI Generated Tests for ${path.basename(file.path)}`,
                        tests: generatedTests,
                        coverage: await this.estimateTestCoverage(generatedTests),
                        aiGenerated: true,
                        lastUpdated: new Date()
                    };
                    await this.saveGeneratedTestSuite(testSuite);
                    await this.storeMemory('knowledge', {
                        type: 'generated_test_suite',
                        testSuite
                    }, ['ai', 'generated-tests', file.path]);
                    this.log(`🎨 Згенеровано ${generatedTests.length} тестів для ${file.path}`);
                }
            }
        }
    }
    // Core Testing Methods
    async runTestSuite(projectPath, options) {
        this.log(`🧪 Запускаю тести для проекту: ${projectPath}`);
        const testResults = [];
        try {
            // Run different types of tests based on configuration
            if (options.testType === 'all' || options.testType === 'unit') {
                const unitResults = await this.runUnitTests(projectPath, options);
                testResults.push(...unitResults);
            }
            if (options.testType === 'all' || options.testType === 'integration') {
                const integrationResults = await this.runIntegrationTests(projectPath, options);
                testResults.push(...integrationResults);
            }
            if (options.testType === 'all' || options.testType === 'e2e') {
                const e2eResults = await this.runE2ETests(projectPath, options);
                testResults.push(...e2eResults);
            }
            if (options.testType === 'all' || options.testType === 'performance') {
                const performanceResults = await this.runPerformanceTests(projectPath, options);
                testResults.push(...performanceResults);
            }
            // Store results in memory
            await this.storeTestResults(testResults);
            // Update quality metrics
            await this.updateQualityMetrics(testResults);
            // Emit test completion event
            await this.emit('qa.tests.completed', {
                projectPath,
                testResults,
                summary: this.generateTestSummary(testResults)
            });
            return testResults;
        }
        catch (error) {
            const errorMessage = error instanceof Error ? error.message : 'Unknown error';
            this.log(`❌ Помилка виконання тестів: ${errorMessage}`, 'error');
            throw error;
        }
    }
    async analyzeCodeQuality(projectPath, options) {
        this.log(`📊 Аналізую якість коду: ${projectPath}`);
        const analysis = {
            projectPath,
            timestamp: new Date(),
            coverage: await this.analyzeCoverage(projectPath),
            complexity: await this.analyzeComplexity(projectPath),
            duplicatedLines: await this.analyzeDuplication(projectPath),
            codeSmells: await this.analyzeCodeSmells(projectPath),
            security: await this.analyzeSecurity(projectPath),
            maintainability: await this.analyzeMaintainability(projectPath)
        };
        // Check quality gates
        const qualityGatesPassed = this.checkQualityGates(analysis);
        await this.storeMemory('analytics', {
            type: 'code_quality_analysis',
            analysis,
            qualityGatesPassed,
            timestamp: new Date()
        }, ['code-quality', 'analysis']);
        if (!qualityGatesPassed) {
            await this.emit('qa.quality.gate.failed', {
                projectPath,
                analysis,
                failedGates: this.getFailedQualityGates(analysis)
            });
        }
        return { analysis, qualityGatesPassed };
    }
    async generateTestCases(sourceFile, options) {
        this.log(`🎨 Генерую тест-кейси для: ${sourceFile}`);
        const sourceCode = await fs.readFile(sourceFile, 'utf-8');
        const testGenerator = this.aiModels.get('test_generator');
        const generatedTests = await this.generateTestsFromSource(sourceCode, options);
        await this.storeMemory('knowledge', {
            type: 'generated_tests',
            sourceFile,
            tests: generatedTests,
            options
        }, ['generated-tests', sourceFile]);
        this.log(`✅ Згенеровано ${generatedTests.length} тест-кейсів`);
        return generatedTests;
    }
    async reportBug(bugData) {
        const bug = {
            id: bugData.id || this.generateId(),
            title: bugData.title || 'Untitled Bug',
            description: bugData.description || '',
            severity: bugData.severity || 'medium',
            priority: bugData.priority || 'medium',
            status: 'open',
            assignee: bugData.assignee,
            reporter: bugData.reporter || 'smart-qa-agent',
            steps: bugData.steps || [],
            expectedResult: bugData.expectedResult || '',
            actualResult: bugData.actualResult || '',
            environment: bugData.environment || 'unknown',
            browser: bugData.browser,
            attachments: bugData.attachments || [],
            tags: bugData.tags || [],
            createdAt: new Date(),
            updatedAt: new Date()
        };
        this.bugReports.set(bug.id, bug);
        // Store in memory
        await this.storeMemory('analytics', {
            type: 'bug_report',
            bug
        }, ['bugs', 'reported', bug.severity]);
        // Auto-assign if enabled
        if (this.config.integrations.jira?.autoBugReporting) {
            await this.createJiraBug(bug);
        }
        await this.emit('qa.bug.found', { bug });
        this.log(`🐛 Створено звіт про баг: ${bug.title}`);
        return bug;
    }
    // AI Helper Methods
    trainFlakyTestPredictor(historicalTests) {
        // Analyze patterns in test failures to predict flaky tests
        const testStability = historicalTests
            .filter(record => record.data.testResults)
            .flatMap(record => record.data.testResults)
            .reduce((acc, result) => {
            const key = `${result.testSuite}:${result.testCase}`;
            if (!acc[key]) {
                acc[key] = { passed: 0, failed: 0, total: 0 };
            }
            acc[key].total++;
            if (result.status === 'passed') {
                acc[key].passed++;
            }
            else {
                acc[key].failed++;
            }
            return acc;
        }, {});
        return { testStability, lastUpdated: new Date() };
    }
    trainBugPredictor(historicalBugs) {
        // Analyze bug patterns to predict future bugs
        const bugPatterns = historicalBugs
            .filter(record => record.data.bug)
            .map(record => record.data.bug)
            .reduce((acc, bug) => {
            // Analyze patterns by severity, component, etc.
            acc.severityDistribution = acc.severityDistribution || {};
            acc.severityDistribution[bug.severity] = (acc.severityDistribution[bug.severity] || 0) + 1;
            acc.tagPatterns = acc.tagPatterns || {};
            bug.tags.forEach(tag => {
                acc.tagPatterns[tag] = (acc.tagPatterns[tag] || 0) + 1;
            });
            return acc;
        }, {});
        return { bugPatterns, lastUpdated: new Date() };
    }
    initializeTestGenerator() {
        // Initialize test generation templates and patterns
        return {
            templates: {
                unit: this.getUnitTestTemplates(),
                integration: this.getIntegrationTestTemplates(),
                e2e: this.getE2ETestTemplates()
            },
            patterns: this.getTestPatterns(),
            lastUpdated: new Date()
        };
    }
    // Utility Methods
    async loadHistoricalQAData() {
        this.log('📚 Завантажую історичні QA дані...');
        const testResultRecords = await this.queryMemory({
            type: 'analytics',
            tags: ['test-results']
        });
        for (const record of testResultRecords) {
            if (record.data.testResults) {
                const key = `${record.data.projectPath || 'unknown'}`;
                if (!this.testResults.has(key)) {
                    this.testResults.set(key, []);
                }
                this.testResults.get(key).push(...record.data.testResults);
            }
        }
        const bugRecords = await this.queryMemory({
            type: 'analytics',
            tags: ['bugs']
        });
        for (const record of bugRecords) {
            if (record.data.bug) {
                this.bugReports.set(record.data.bug.id, record.data.bug);
            }
        }
        this.log(`📊 Завантажено результати ${this.testResults.size} проектів та ${this.bugReports.size} багів`);
    }
    generateId() {
        return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    }
    // Tool Methods for MCP Integration
    getTools() {
        return [
            {
                name: 'run_test_suite',
                description: 'Запускає набір тестів з AI оптимізацією',
                inputSchema: {
                    type: 'object',
                    properties: {
                        projectPath: { type: 'string' },
                        testType: { type: 'string', enum: ['unit', 'integration', 'e2e', 'performance', 'security', 'all'] },
                        environment: { type: 'string' },
                        parallel: { type: 'boolean' },
                        coverage: { type: 'boolean' },
                        smartSelection: { type: 'boolean' }
                    },
                    required: ['projectPath']
                }
            },
            {
                name: 'analyze_code_quality',
                description: 'Аналізує якість коду з AI інсайтами',
                inputSchema: {
                    type: 'object',
                    properties: {
                        projectPath: { type: 'string' },
                        analyzeTypes: {
                            type: 'array',
                            items: { type: 'string', enum: ['complexity', 'coverage', 'security', 'style', 'maintainability'] }
                        },
                        threshold: { type: 'object' },
                        includeAIPredictions: { type: 'boolean' }
                    },
                    required: ['projectPath']
                }
            },
            {
                name: 'generate_test_cases',
                description: 'Генерує тест-кейси використовуючи AI',
                inputSchema: {
                    type: 'object',
                    properties: {
                        sourceFile: { type: 'string' },
                        testType: { type: 'string', enum: ['unit', 'integration', 'e2e'] },
                        framework: { type: 'string' },
                        includeEdgeCases: { type: 'boolean' },
                        mockDependencies: { type: 'boolean' },
                        aiEnhanced: { type: 'boolean' }
                    },
                    required: ['sourceFile', 'testType']
                }
            },
            {
                name: 'predict_bugs',
                description: 'Прогнозує потенційні баги з використанням AI',
                inputSchema: {
                    type: 'object',
                    properties: {
                        projectPath: { type: 'string' },
                        codeChanges: { type: 'array', items: { type: 'string' } },
                        confidenceThreshold: { type: 'number', minimum: 0, maximum: 1 },
                        categories: {
                            type: 'array',
                            items: { type: 'string', enum: ['logic', 'performance', 'security', 'integration'] }
                        }
                    },
                    required: ['projectPath']
                }
            },
            {
                name: 'detect_flaky_tests',
                description: 'Виявляє нестабільні тести з AI аналізом',
                inputSchema: {
                    type: 'object',
                    properties: {
                        projectPath: { type: 'string' },
                        timeRange: { type: 'string', enum: ['week', 'month', 'quarter'] },
                        confidenceLevel: { type: 'number', minimum: 0, maximum: 1 },
                        autoFix: { type: 'boolean' }
                    }
                }
            },
            {
                name: 'get_quality_insights',
                description: 'Отримує AI інсайти по якості проекту',
                inputSchema: {
                    type: 'object',
                    properties: {
                        projectPath: { type: 'string' },
                        includeRecommendations: { type: 'boolean' },
                        includeTrends: { type: 'boolean' }
                    },
                    required: ['projectPath']
                }
            }
        ];
    }
    async handleToolCall(toolName, args) {
        switch (toolName) {
            case 'run_test_suite':
                const results = await this.runTestSuite(args.projectPath, args);
                return {
                    success: true,
                    results,
                    summary: this.generateTestSummary(results),
                    aiInsights: args.smartSelection ? await this.generateTestInsights(results) : null
                };
            case 'analyze_code_quality':
                const qualityAnalysis = await this.analyzeCodeQuality(args.projectPath, args);
                return {
                    success: true,
                    analysis: qualityAnalysis.analysis,
                    qualityGatesPassed: qualityAnalysis.qualityGatesPassed,
                    aiPredictions: args.includeAIPredictions ? await this.generateQualityPredictions(args.projectPath) : null
                };
            case 'generate_test_cases':
                const generatedTests = await this.generateTestCases(args.sourceFile, args);
                return {
                    success: true,
                    tests: generatedTests,
                    coverage: await this.estimateTestCoverage(generatedTests)
                };
            case 'predict_bugs':
                const bugPredictions = await this.predictBugsForProject(args.projectPath, args);
                return {
                    success: true,
                    predictions: bugPredictions
                };
            case 'detect_flaky_tests':
                const flakyTestAnalysis = await this.detectFlakyTestsForProject(args.projectPath, args);
                return {
                    success: true,
                    flakyTests: flakyTestAnalysis
                };
            case 'get_quality_insights':
                const insights = await this.generateQualityInsights(args.projectPath, args);
                return {
                    success: true,
                    insights
                };
            default:
                throw new Error(`Unknown tool: ${toolName}`);
        }
    }
    // Placeholder implementations for referenced methods
    async setupQAEventListeners() { }
    async saveTestResults() { }
    async saveQualityMetrics() { }
    async saveAIInsights() { }
    async executeScheduledTests() { }
    async analyzeQualityMetrics() { }
    async processAutomatedBugReports() { }
    async detectPerformanceRegressions() { }
    async performSecurityScanning() { }
    async coordinateWithOtherAgents() { }
    async getRecentCodeChanges() { return []; }
    async selectRelevantTests(changes) { return []; }
    async executeTestSuite(testSuite) { return []; }
    async processTestResults(results) { }
    async getTotalTestCount() { return 0; }
    async getCurrentCoverage() { return {}; }
    async analyzeCodeMetrics() { return {}; }
    calculateBugProbability(change, metrics) { return 0; }
    async createPredictedBugReport(change, probability) {
        return {
            id: this.generateId(),
            title: 'Predicted Bug',
            description: 'AI predicted potential bug',
            severity: 'medium',
            priority: 'medium',
            status: 'open',
            reporter: 'ai-agent',
            steps: [],
            expectedResult: '',
            actualResult: '',
            environment: 'development',
            attachments: [],
            tags: ['ai-predicted'],
            createdAt: new Date(),
            updatedAt: new Date()
        };
    }
    generateBugPreventionRecommendations(change) { return []; }
    async getRecentTestResults() { return []; }
    identifyFlakyTestCandidates(results) { return []; }
    async analyzeFlakyTestPattern(testName) { return { confidence: 0 }; }
    async createFlakyTestBugReport(testName, analysis) {
        return {
            id: this.generateId(),
            title: `Flaky Test: ${testName}`,
            description: 'AI detected flaky test behavior',
            severity: 'medium',
            priority: 'medium',
            status: 'open',
            reporter: 'ai-agent',
            steps: [],
            expectedResult: '',
            actualResult: '',
            environment: 'test',
            attachments: [],
            tags: ['flaky-test'],
            createdAt: new Date(),
            updatedAt: new Date()
        };
    }
    async identifyUncoveredCode() { return []; }
    async generateTestsForFile(filePath) { return []; }
    async estimateTestCoverage(tests) { return 0; }
    async saveGeneratedTestSuite(testSuite) { }
    // ... other placeholder methods
    async runUnitTests(projectPath, options) { return []; }
    async runIntegrationTests(projectPath, options) { return []; }
    async runE2ETests(projectPath, options) { return []; }
    async runPerformanceTests(projectPath, options) { return []; }
    async storeTestResults(results) { }
    async updateQualityMetrics(results) { }
    generateTestSummary(results) { return {}; }
    async analyzeCoverage(projectPath) { return {}; }
    async analyzeComplexity(projectPath) { return {}; }
    async analyzeDuplication(projectPath) { return {}; }
    async analyzeCodeSmells(projectPath) { return {}; }
    async analyzeSecurity(projectPath) { return {}; }
    async analyzeMaintainability(projectPath) { return {}; }
    checkQualityGates(analysis) { return true; }
    getFailedQualityGates(analysis) { return []; }
    async generateTestsFromSource(sourceCode, options) { return []; }
    async createJiraBug(bug) { }
    getUnitTestTemplates() { return {}; }
    getIntegrationTestTemplates() { return {}; }
    getE2ETestTemplates() { return {}; }
    getTestPatterns() { return {}; }
    trainSmartTestSelector(historicalTests) { return {}; }
    async generateTestInsights(results) { return {}; }
    async generateQualityPredictions(projectPath) { return {}; }
    async predictBugsForProject(projectPath, options) { return []; }
    async detectFlakyTestsForProject(projectPath, options) { return []; }
    async generateQualityInsights(projectPath, options) { return {}; }
}
exports.SmartQAEngineerAgent = SmartQAEngineerAgent;
// Factory function
async function createSmartQAEngineer(config) {
    const defaultConfig = {
        enabled: true,
        testFrameworks: {
            unit: 'jest',
            e2e: 'playwright',
            api: 'supertest',
            performance: 'k6'
        },
        qualityGates: {
            unitTestCoverage: 80,
            codeComplexity: 10,
            duplicatedLines: 5,
            securityHotspots: 0,
            bugs: 0
        },
        testEnvironments: {
            local: { baseUrl: 'http://localhost:3000' },
            staging: { baseUrl: 'https://staging.example.com' }
        },
        integrations: {
            jira: { enabled: false, autoBugReporting: false },
            sonarqube: { enabled: false },
            slack: { enabled: false, channel: '#qa-alerts' }
        },
        aiTesting: {
            enabled: true,
            testGeneration: true,
            bugPrediction: true,
            flakyTestDetection: true,
            smartTestSelection: true
        },
        notifications: {
            testFailures: true,
            qualityGateFailures: true,
            newBugsFound: true,
            coverageDrops: true
        }
    };
    const mergedConfig = { ...defaultConfig, ...config };
    const agent = new SmartQAEngineerAgent(mergedConfig);
    await agent.initialize();
    return agent;
}
//# sourceMappingURL=index.js.map