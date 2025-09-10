"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.AuthMiddleware = void 0;
class AuthMiddleware {
    constructor(authService) {
        this.authService = authService;
        this.authenticate = async (req, res, next) => {
            try {
                const token = this.extractToken(req);
                if (!token) {
                    return res.status(401).json({
                        error: 'Токен авторизації відсутній'
                    });
                }
                const decodedToken = await this.authService.validateToken(token);
                if (!decodedToken) {
                    return res.status(401).json({
                        error: 'Недійсний токен авторизації'
                    });
                }
                req.user = {
                    userId: decodedToken.userId,
                    username: decodedToken.username,
                    role: decodedToken.role
                };
                next();
            }
            catch (error) {
                return res.status(401).json({
                    error: 'Помилка авторизації'
                });
            }
        };
        this.requireRole = (requiredRole) => {
            return (req, res, next) => {
                if (!req.user) {
                    return res.status(401).json({
                        error: 'Користувач не авторизований'
                    });
                }
                if (requiredRole === 'admin' && req.user.role !== 'admin') {
                    return res.status(403).json({
                        error: 'Недостатньо прав доступу'
                    });
                }
                next();
            };
        };
        this.authenticateApi = async (req, res, next) => {
            try {
                const apiKey = req.headers['x-api-key'];
                if (!apiKey) {
                    return res.status(401).json({
                        error: 'API ключ відсутній'
                    });
                }
                const userId = await this.authService.validateApiKey(apiKey);
                if (!userId) {
                    return res.status(401).json({
                        error: 'Недійсний API ключ'
                    });
                }
                const user = await this.authService.getUserById(userId);
                if (!user) {
                    return res.status(401).json({
                        error: 'Користувач не знайдений'
                    });
                }
                req.user = {
                    userId: user.id,
                    username: user.username,
                    role: user.role
                };
                next();
            }
            catch (error) {
                return res.status(401).json({
                    error: 'Помилка API авторизації'
                });
            }
        };
    }
    extractToken(req) {
        const authHeader = req.headers.authorization;
        if (authHeader && authHeader.startsWith('Bearer ')) {
            return authHeader.substring(7);
        }
        return req.query.token || null;
    }
}
exports.AuthMiddleware = AuthMiddleware;
//# sourceMappingURL=middleware.js.map