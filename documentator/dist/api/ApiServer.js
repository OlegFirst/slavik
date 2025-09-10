"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.ApiServer = void 0;
const express_1 = __importDefault(require("express"));
const cors_1 = __importDefault(require("cors"));
const helmet_1 = __importDefault(require("helmet"));
const AuthService_1 = require("../auth/AuthService");
const middleware_1 = require("../auth/middleware");
const ProjectAnalyzer_1 = require("../core/ProjectAnalyzer");
const ReportGenerator_1 = require("../core/ReportGenerator");
const auth_1 = require("./routes/auth");
const projects_1 = require("./routes/projects");
const reports_1 = require("./routes/reports");
class ApiServer {
    constructor(port = 3000) {
        this.app = (0, express_1.default)();
        this.authService = new AuthService_1.AuthService();
        this.authMiddleware = new middleware_1.AuthMiddleware(this.authService);
        this.projectAnalyzer = new ProjectAnalyzer_1.ProjectAnalyzer();
        this.reportGenerator = new ReportGenerator_1.ReportGenerator();
        this.setupMiddleware();
        this.setupRoutes();
        this.setupErrorHandling();
        this.app.listen(port, () => {
            console.log(`API сервер запущено на порту ${port}`);
        });
    }
    setupMiddleware() {
        this.app.use((0, helmet_1.default)());
        this.app.use((0, cors_1.default)({
            origin: process.env.ALLOWED_ORIGINS?.split(',') || ['http://localhost:3000'],
            credentials: true
        }));
        this.app.use(express_1.default.json({ limit: '10mb' }));
        this.app.use(express_1.default.urlencoded({ extended: true }));
        this.app.use((req, res, next) => {
            console.log(`${new Date().toISOString()} ${req.method} ${req.path}`);
            next();
        });
    }
    setupRoutes() {
        this.app.get('/health', (req, res) => {
            res.json({
                status: 'OK',
                timestamp: new Date().toISOString(),
                service: 'Documentator API'
            });
        });
        this.app.use('/api/auth', (0, auth_1.authRoutes)(this.authService));
        this.app.use('/api/projects', this.authMiddleware.authenticate, (0, projects_1.projectRoutes)(this.projectAnalyzer));
        this.app.use('/api/reports', this.authMiddleware.authenticate, (0, reports_1.reportRoutes)(this.reportGenerator, this.projectAnalyzer));
        this.app.use('/api/mcp', this.authMiddleware.authenticateApi, (0, projects_1.projectRoutes)(this.projectAnalyzer));
        this.app.use('*', (req, res) => {
            res.status(404).json({
                error: 'Маршрут не знайдено',
                path: req.originalUrl,
                method: req.method
            });
        });
    }
    setupErrorHandling() {
        this.app.use((error, req, res, next) => {
            console.error('Глобальна помилка:', error);
            if (error.type === 'entity.parse.failed') {
                return res.status(400).json({
                    error: 'Невірний формат JSON'
                });
            }
            if (error.code === 'LIMIT_FILE_SIZE') {
                return res.status(413).json({
                    error: 'Файл занадто великий'
                });
            }
            res.status(500).json({
                error: 'Внутрішня помилка сервера',
                ...(process.env.NODE_ENV === 'development' && { details: error.message })
            });
        });
        process.on('unhandledRejection', (reason, promise) => {
            console.error('Необроблене відхилення промісу:', reason);
        });
        process.on('uncaughtException', (error) => {
            console.error('Необроблений виняток:', error);
            process.exit(1);
        });
    }
    getApp() {
        return this.app;
    }
}
exports.ApiServer = ApiServer;
//# sourceMappingURL=ApiServer.js.map