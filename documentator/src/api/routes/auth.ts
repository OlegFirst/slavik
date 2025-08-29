import { Router, Request, Response } from 'express';
import { AuthService, LoginCredentials, RegisterData } from '../../auth/AuthService';
import { AuthMiddleware, AuthenticatedRequest } from '../../auth/middleware';

export function authRoutes(authService: AuthService): Router {
  const router = Router();
  const authMiddleware = new AuthMiddleware(authService);

  router.post('/login', async (req: Request, res: Response) => {
    try {
      const credentials: LoginCredentials = req.body;
      
      if (!credentials.username || !credentials.password) {
        return res.status(400).json({ 
          error: 'Логін та пароль обов\'язкові' 
        });
      }

      const result = await authService.login(credentials);
      
      if (!result) {
        return res.status(401).json({ 
          error: 'Невірний логін або пароль' 
        });
      }

      res.json({
        success: true,
        token: result.token,
        user: result.user
      });
    } catch (error) {
      console.error('Помилка авторизації:', error);
      res.status(500).json({ 
        error: 'Помилка сервера при авторизації' 
      });
    }
  });

  router.post('/register', async (req: Request, res: Response) => {
    try {
      const data: RegisterData = req.body;
      
      if (!data.username || !data.email || !data.password) {
        return res.status(400).json({ 
          error: 'Всі поля обов\'язкові для заповнення' 
        });
      }

      if (data.password.length < 6) {
        return res.status(400).json({ 
          error: 'Пароль повинен містити мінімум 6 символів' 
        });
      }

      const emailRegex = /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/;
      if (!emailRegex.test(data.email)) {
        return res.status(400).json({ 
          error: 'Невірний формат email' 
        });
      }

      const user = await authService.register(data);
      
      if (!user) {
        return res.status(409).json({ 
          error: 'Користувач з таким логіном або email вже існує' 
        });
      }

      res.status(201).json({
        success: true,
        user
      });
    } catch (error) {
      console.error('Помилка реєстрації:', error);
      res.status(500).json({ 
        error: 'Помилка сервера при реєстрації' 
      });
    }
  });

  router.get('/me', authMiddleware.authenticate, async (req: AuthenticatedRequest, res: Response) => {
    try {
      const user = await authService.getUserById(req.user!.userId);
      
      if (!user) {
        return res.status(404).json({ 
          error: 'Користувач не знайдений' 
        });
      }

      res.json({
        success: true,
        user
      });
    } catch (error) {
      console.error('Помилка отримання профілю:', error);
      res.status(500).json({ 
        error: 'Помилка сервера' 
      });
    }
  });

  router.post('/change-password', authMiddleware.authenticate, async (req: AuthenticatedRequest, res: Response) => {
    try {
      const { oldPassword, newPassword } = req.body;
      
      if (!oldPassword || !newPassword) {
        return res.status(400).json({ 
          error: 'Старий та новий пароль обов\'язкові' 
        });
      }

      if (newPassword.length < 6) {
        return res.status(400).json({ 
          error: 'Новий пароль повинен містити мінімум 6 символів' 
        });
      }

      const success = await authService.changePassword(req.user!.userId, oldPassword, newPassword);
      
      if (!success) {
        return res.status(400).json({ 
          error: 'Невірний старий пароль' 
        });
      }

      res.json({
        success: true,
        message: 'Пароль успішно змінено'
      });
    } catch (error) {
      console.error('Помилка зміни пароля:', error);
      res.status(500).json({ 
        error: 'Помилка сервера' 
      });
    }
  });

  router.post('/api-key', authMiddleware.authenticate, async (req: AuthenticatedRequest, res: Response) => {
    try {
      const apiKey = authService.generateApiKey(req.user!.userId);
      
      res.json({
        success: true,
        apiKey,
        message: 'API ключ згенеровано. Збережіть його в безпечному місці.'
      });
    } catch (error) {
      console.error('Помилка генерації API ключа:', error);
      res.status(500).json({ 
        error: 'Помилка сервера' 
      });
    }
  });

  router.put('/users/:userId/role', 
    authMiddleware.authenticate,
    authMiddleware.requireRole('admin'),
    async (req: AuthenticatedRequest, res: Response) => {
      try {
        const { userId } = req.params;
        const { role } = req.body;
        
        if (!['admin', 'user'].includes(role)) {
          return res.status(400).json({ 
            error: 'Невірна роль. Дозволені: admin, user' 
          });
        }

        if (userId === req.user!.userId) {
          return res.status(400).json({ 
            error: 'Не можна змінити власну роль' 
          });
        }

        const success = await authService.updateUserRole(userId, role);
        
        if (!success) {
          return res.status(404).json({ 
            error: 'Користувач не знайдений' 
          });
        }

        res.json({
          success: true,
          message: 'Роль користувача оновлено'
        });
      } catch (error) {
        console.error('Помилка оновлення ролі:', error);
        res.status(500).json({ 
          error: 'Помилка сервера' 
        });
      }
    }
  );

  return router;
}