import { Request, Response, NextFunction } from 'express';
import { AuthService } from './AuthService';
export interface AuthenticatedRequest extends Request {
    user?: {
        userId: string;
        username: string;
        role: string;
    };
}
export declare class AuthMiddleware {
    private authService;
    constructor(authService: AuthService);
    authenticate: (req: AuthenticatedRequest, res: Response, next: NextFunction) => Promise<Response<any, Record<string, any>> | undefined>;
    requireRole: (requiredRole: "admin" | "user") => (req: AuthenticatedRequest, res: Response, next: NextFunction) => Response<any, Record<string, any>> | undefined;
    authenticateApi: (req: AuthenticatedRequest, res: Response, next: NextFunction) => Promise<Response<any, Record<string, any>> | undefined>;
    private extractToken;
}
//# sourceMappingURL=middleware.d.ts.map