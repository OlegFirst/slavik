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
exports.SeniorProjectManagerAgent = void 0;
const BaseAgent_1 = require("../../../core/BaseAgent");
const AgentInterface_1 = require("../../../types/AgentInterface");
const fs = __importStar(require("fs-extra"));
const path = __importStar(require("path"));
class SeniorProjectManagerAgent extends BaseAgent_1.BaseAgent {
    constructor(config) {
        super(config);
        this.projects = new Map();
        this.currentSprint = null;
        this.metadata = {
            name: 'senior-project-manager',
            version: '1.0.0',
            description: 'Автономний агент для управління проектами та координації команди',
            category: 'automation'
        };
        this.config = config;
    }
    getScheduleConfig() {
        return {
            type: AgentInterface_1.ScheduleType.INTERVAL,
            enabled: this.config.enabled !== false,
            intervalMs: (this.config.reportingInterval || 1440) * 60 * 1000, // щодня
            stopOnError: false
        };
    }
    async onInitialize() {
        this.log('Senior Project Manager Agent ініціалізується...');
        await fs.ensureDir('./data/projects');
        await fs.ensureDir('./data/projects/active');
        await fs.ensureDir('./data/projects/completed');
        // Завантажуємо існуючі проекти
        await this.loadProjects();
        // Слухаємо події
        await this.on('git.commit', async (data) => {
            await this.updateTaskProgress(data);
        });
        await this.on('qa.tests.completed', async (data) => {
            await this.updateProjectStatus(data);
        });
    }
    async onShutdown() {
        this.log('Senior Project Manager Agent зупиняється...');
        await this.saveProjects();
    }
    async executeAutonomously() {
        this.log('Виконую PM завдання...');
        try {
            // 1. Оновлюємо статус проектів
            await this.updateProjectStatuses();
            // 2. Аналізуємо прогрес спринту
            await this.analyzeSprint();
            // 3. Генеруємо звіти
            await this.generateStatusReports();
            // 4. Плануємо наступний спринт (якщо потрібно)
            await this.planNextSprint();
            // 5. Аналізуємо ризики
            await this.assessRisks();
            await this.emit('project.cycle.completed', {
                timestamp: new Date(),
                projectsActive: this.getActiveProjects().length
            });
        }
        catch (error) {
            const errorMessage = error instanceof Error ? error.message : 'Невідома помилка';
            this.log(`Помилка PM циклу: ${errorMessage}`, 'error');
        }
    }
    async loadProjects() {
        const activeProjectsDir = './data/projects/active';
        if (await fs.pathExists(activeProjectsDir)) {
            const files = await fs.readdir(activeProjectsDir);
            for (const file of files) {
                if (file.endsWith('.json')) {
                    const project = await fs.readJson(path.join(activeProjectsDir, file));
                    this.projects.set(project.id, project);
                }
            }
        }
    }
    async saveProjects() {
        for (const [id, project] of this.projects.entries()) {
            const filePath = project.status === 'completed'
                ? `./data/projects/completed/${id}.json`
                : `./data/projects/active/${id}.json`;
            await fs.writeJson(filePath, project, { spaces: 2 });
        }
    }
    async updateProjectStatuses() {
        for (const project of this.projects.values()) {
            const completedTasks = project.tasks.filter(t => t.status === 'done').length;
            const totalTasks = project.tasks.length;
            if (totalTasks > 0 && completedTasks === totalTasks) {
                project.status = 'completed';
                project.actualEndDate = new Date();
                await this.emit('project.completed', { project: project.name });
            }
        }
    }
    async analyzeSprint() {
        if (!this.currentSprint)
            return;
        const sprintTasks = this.getSprintTasks();
        const completedTasks = sprintTasks.filter(t => t.status === 'done');
        const velocity = completedTasks.length;
        this.log(`Поточна velocity: ${velocity} задач`);
        await this.emit('sprint.velocity.updated', {
            sprint: this.currentSprint.name,
            velocity,
            totalTasks: sprintTasks.length
        });
    }
    async generateStatusReports() {
        const report = {
            timestamp: new Date(),
            activeProjects: this.getActiveProjects().length,
            totalTasks: this.getAllTasks().length,
            completedTasks: this.getAllTasks().filter(t => t.status === 'done').length,
            projects: this.getActiveProjects().map(p => ({
                name: p.name,
                progress: this.calculateProjectProgress(p),
                tasksCompleted: p.tasks.filter(t => t.status === 'done').length,
                totalTasks: p.tasks.length
            }))
        };
        await fs.writeJson('./data/projects/status-report.json', report, { spaces: 2 });
        await this.emit('report.generated', {
            type: 'status',
            timestamp: report.timestamp
        });
    }
    async planNextSprint() {
        // Спрощена логіка планування спринту
        const backlogTasks = this.getAllTasks().filter(t => t.status === 'todo');
        const highPriorityTasks = backlogTasks.filter(t => t.priority === 'high').slice(0, 10);
        if (highPriorityTasks.length > 0) {
            this.log(`Планую наступний спринт з ${highPriorityTasks.length} задач`);
        }
    }
    async assessRisks() {
        const risks = [];
        for (const project of this.getActiveProjects()) {
            const progress = this.calculateProjectProgress(project);
            const daysToDeadline = Math.ceil((project.estimatedEndDate.getTime() - Date.now()) / (1000 * 60 * 60 * 24));
            if (progress < 50 && daysToDeadline < 30) {
                risks.push(`Проект ${project.name} відстає від графіку`);
            }
            if (project.tasks.filter(t => t.status === 'in_progress').length > 5) {
                risks.push(`Проект ${project.name} має забагато задач у роботі`);
            }
        }
        if (risks.length > 0) {
            await this.emit('risks.identified', { risks });
        }
    }
    getActiveProjects() {
        return Array.from(this.projects.values()).filter(p => p.status === 'active');
    }
    getAllTasks() {
        return Array.from(this.projects.values()).flatMap(p => p.tasks);
    }
    getSprintTasks() {
        // Спрощена логіка - повертаємо поточні задачі в роботі
        return this.getAllTasks().filter(t => t.status === 'in_progress' || t.status === 'review');
    }
    calculateProjectProgress(project) {
        if (project.tasks.length === 0)
            return 0;
        const completedTasks = project.tasks.filter(t => t.status === 'done').length;
        return Math.round((completedTasks / project.tasks.length) * 100);
    }
    async updateTaskProgress(commitData) {
        // Оновлюємо прогрес задач на основі коммітів
        this.log(`Оновлюю прогрес задач для коміту ${commitData.hash}`);
    }
    async updateProjectStatus(testData) {
        // Оновлюємо статус проекту на основі результатів тестів
        this.log(`Оновлюю статус проекту після тестів: ${testData.project}`);
    }
    getTools() {
        return [
            {
                name: 'create_project',
                description: 'Створює новий проект з планом',
                inputSchema: {
                    type: 'object',
                    properties: {
                        projectName: { type: 'string' },
                        description: { type: 'string' },
                        startDate: { type: 'string' },
                        estimatedDuration: { type: 'string' },
                        team: { type: 'array', items: { type: 'string' } },
                        priority: { type: 'string', enum: ['high', 'medium', 'low'] }
                    },
                    required: ['projectName', 'description']
                }
            },
            {
                name: 'update_task_status',
                description: 'Оновлює статус задачі',
                inputSchema: {
                    type: 'object',
                    properties: {
                        taskId: { type: 'string' },
                        status: { type: 'string', enum: ['todo', 'in_progress', 'review', 'done'] },
                        assignee: { type: 'string' },
                        actualHours: { type: 'number' }
                    },
                    required: ['taskId', 'status']
                }
            },
            {
                name: 'generate_report',
                description: 'Генерує звіт по проекту',
                inputSchema: {
                    type: 'object',
                    properties: {
                        projectId: { type: 'string' },
                        reportType: { type: 'string', enum: ['status', 'progress', 'velocity', 'budget'] },
                        timeRange: { type: 'string', enum: ['sprint', 'month', 'quarter'] }
                    },
                    required: ['reportType']
                }
            }
        ];
    }
    async handleToolCall(toolName, args) {
        switch (toolName) {
            case 'create_project':
                const newProject = {
                    id: `proj_${Date.now()}`,
                    name: args.projectName,
                    description: args.description,
                    status: 'planning',
                    startDate: args.startDate ? new Date(args.startDate) : new Date(),
                    estimatedEndDate: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000), // 30 днів
                    team: args.team || [],
                    tasks: []
                };
                this.projects.set(newProject.id, newProject);
                await this.saveProjects();
                await this.emit('project.created', { project: newProject.name });
                return {
                    success: true,
                    projectId: newProject.id,
                    message: `Проект ${newProject.name} створено`
                };
            case 'update_task_status':
                // Знаходимо задачу та оновлюємо статус
                for (const project of this.projects.values()) {
                    const task = project.tasks.find(t => t.id === args.taskId);
                    if (task) {
                        task.status = args.status;
                        task.updatedAt = new Date();
                        if (args.assignee)
                            task.assignee = args.assignee;
                        if (args.actualHours)
                            task.actualHours = args.actualHours;
                        await this.saveProjects();
                        await this.emit('task.updated', { taskId: args.taskId, status: args.status });
                        return { success: true, message: `Задача ${args.taskId} оновлена` };
                    }
                }
                return { success: false, message: 'Задачу не знайдено' };
            case 'generate_report':
                await this.generateStatusReports();
                return {
                    success: true,
                    reportType: args.reportType,
                    timestamp: new Date()
                };
            default:
                throw new Error(`Невідомий інструмент: ${toolName}`);
        }
    }
}
exports.SeniorProjectManagerAgent = SeniorProjectManagerAgent;
//# sourceMappingURL=index.js.map