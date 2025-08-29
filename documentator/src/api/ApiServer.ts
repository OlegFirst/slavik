import express, { Application } from 'express';
import cors from 'cors';
import helmet from 'helmet';
import { AuthService } from '../auth/AuthService';
import { AuthMiddleware } from '../auth/middleware';
import { ProjectAnalyzer } from '../core/ProjectAnalyzer';
import { ReportGenerator } from '../core/ReportGenerator';
import { authRoutes } from './routes/auth';
import { projectRoutes } from './routes/projects';
import { reportRoutes } from './routes/reports';

export class ApiServer {
  private app: Application;
  private authService: AuthService;
  private authMiddleware: AuthMiddleware;
  private projectAnalyzer: ProjectAnalyzer;
  private reportGenerator: ReportGenerator;

  constructor(port: number = 3000) {
    this.app = express();
    this.authService = new AuthService();
    this.authMiddleware = new AuthMiddleware(this.authService);
    this.projectAnalyzer = new ProjectAnalyzer();
    this.reportGenerator = new ReportGenerator();

    this.setupMiddleware();
    this.setupRoutes();
    this.setupErrorHandling();

    this.app.listen(port, () => {
      console.log(`API сервер запущено на порту ${port}`);
    });
  }

  private setupMiddleware(): void {
    this.app.use(helmet());
    this.app.use(cors({
      origin: process.env.ALLOWED_ORIGINS?.split(',') || ['http://localhost:3000'],
      credentials: true
    }));
    this.app.use(express.json({ limit: '10mb' }));
    this.app.use(express.urlencoded({ extended: true }));

    this.app.use((req, res, next) => {
      console.log(`${new Date().toISOString()} ${req.method} ${req.path}`);
      next();
    });
  }

  private setupRoutes(): void {
    this.app.get('/health', (req, res) => {
      res.json({ 
        status: 'OK', 
        timestamp: new Date().toISOString(),
        service: 'Documentator API'
      });
    });

    this.app.use('/api/auth', authRoutes(this.authService));
    
    this.app.use('/api/projects', 
      this.authMiddleware.authenticate,
      projectRoutes(this.projectAnalyzer)
    );
    
    this.app.use('/api/reports', 
      this.authMiddleware.authenticate,
      reportRoutes(this.reportGenerator, this.projectAnalyzer)
    );

    this.app.use('/api/mcp', 
      this.authMiddleware.authenticateApi,
      projectRoutes(this.projectAnalyzer)
    );

    this.app.use('*', (req, res) => {
      res.status(404).json({ 
        error: 'Маршрут не знайдено',
        path: req.originalUrl,
        method: req.method
      });
    });
  }

  private setupErrorHandling(): void {
    this.app.use((error: any, req: express.Request, res: express.Response, next: express.NextFunction) => {
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

  getApp(): Application {
    return this.app;
  }
}