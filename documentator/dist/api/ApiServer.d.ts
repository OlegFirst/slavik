import { Application } from 'express';
export declare class ApiServer {
    private app;
    private authService;
    private authMiddleware;
    private projectAnalyzer;
    private reportGenerator;
    constructor(port?: number);
    private setupMiddleware;
    private setupRoutes;
    private setupErrorHandling;
    getApp(): Application;
}
//# sourceMappingURL=ApiServer.d.ts.map