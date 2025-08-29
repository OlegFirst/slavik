import * as bcrypt from 'bcrypt';
import * as jwt from 'jsonwebtoken';
import * as fs from 'fs-extra';
import * as path from 'path';
import { v4 as uuidv4 } from 'uuid';
import { User, AuthToken } from '../types';

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterData {
  username: string;
  email: string;
  password: string;
}

export class AuthService {
  private readonly JWT_SECRET: string;
  private readonly USERS_FILE: string;
  private readonly SALT_ROUNDS = 10;

  constructor(dataDir: string = './data') {
    this.JWT_SECRET = process.env.JWT_SECRET || 'documentator-secret-key-change-in-production';
    this.USERS_FILE = path.join(dataDir, 'users.json');
    this.ensureDataDir(dataDir);
  }

  private async ensureDataDir(dataDir: string): Promise<void> {
    await fs.ensureDir(dataDir);
    if (!await fs.pathExists(this.USERS_FILE)) {
      await this.createDefaultAdmin();
    }
  }

  private async createDefaultAdmin(): Promise<void> {
    const defaultAdmin: User = {
      id: uuidv4(),
      username: 'admin',
      email: 'admin@documentator.local',
      role: 'admin',
      createdAt: new Date()
    };

    const hashedPassword = await bcrypt.hash('admin123', this.SALT_ROUNDS);
    const users = {
      [defaultAdmin.id]: {
        ...defaultAdmin,
        passwordHash: hashedPassword
      }
    };

    await fs.writeJson(this.USERS_FILE, users, { spaces: 2 });
    console.log('Створено адміністратора за замовчуванням: admin/admin123');
  }

  async login(credentials: LoginCredentials): Promise<{ token: string; user: User } | null> {
    try {
      const users = await this.loadUsers();
      const userEntry = Object.entries(users).find(([_, userData]) => 
        userData.username === credentials.username
      );

      if (!userEntry) {
        return null;
      }

      const [userId, userData] = userEntry;
      const isValidPassword = await bcrypt.compare(credentials.password, userData.passwordHash);

      if (!isValidPassword) {
        return null;
      }

      const token = this.generateToken(userId, userData);
      const user: User = {
        id: userId,
        username: userData.username,
        email: userData.email,
        role: userData.role,
        createdAt: userData.createdAt
      };

      return { token, user };
    } catch (error) {
      console.error('Помилка авторизації:', error);
      return null;
    }
  }

  async register(data: RegisterData): Promise<User | null> {
    try {
      const users = await this.loadUsers();
      
      const existingUser = Object.values(users).find(user => 
        user.username === data.username || user.email === data.email
      );

      if (existingUser) {
        throw new Error('Користувач з таким логіном або email вже існує');
      }

      const hashedPassword = await bcrypt.hash(data.password, this.SALT_ROUNDS);
      const newUser: User = {
        id: uuidv4(),
        username: data.username,
        email: data.email,
        role: 'user',
        createdAt: new Date()
      };

      users[newUser.id] = {
        ...newUser,
        passwordHash: hashedPassword
      };

      await fs.writeJson(this.USERS_FILE, users, { spaces: 2 });
      return newUser;
    } catch (error) {
      console.error('Помилка реєстрації:', error);
      return null;
    }
  }

  async validateToken(token: string): Promise<AuthToken | null> {
    try {
      const decoded = jwt.verify(token, this.JWT_SECRET) as AuthToken;
      
      const users = await this.loadUsers();
      const user = users[decoded.userId];
      
      if (!user) {
        return null;
      }

      return decoded;
    } catch (error) {
      return null;
    }
  }

  async getUserById(userId: string): Promise<User | null> {
    try {
      const users = await this.loadUsers();
      const userData = users[userId];
      
      if (!userData) {
        return null;
      }

      return {
        id: userId,
        username: userData.username,
        email: userData.email,
        role: userData.role,
        createdAt: userData.createdAt
      };
    } catch (error) {
      console.error('Помилка отримання користувача:', error);
      return null;
    }
  }

  async updateUserRole(userId: string, newRole: 'admin' | 'user'): Promise<boolean> {
    try {
      const users = await this.loadUsers();
      
      if (!users[userId]) {
        return false;
      }

      users[userId].role = newRole;
      await fs.writeJson(this.USERS_FILE, users, { spaces: 2 });
      return true;
    } catch (error) {
      console.error('Помилка оновлення ролі:', error);
      return false;
    }
  }

  async changePassword(userId: string, oldPassword: string, newPassword: string): Promise<boolean> {
    try {
      const users = await this.loadUsers();
      const userData = users[userId];
      
      if (!userData) {
        return false;
      }

      const isValidOldPassword = await bcrypt.compare(oldPassword, userData.passwordHash);
      if (!isValidOldPassword) {
        return false;
      }

      const hashedNewPassword = await bcrypt.hash(newPassword, this.SALT_ROUNDS);
      userData.passwordHash = hashedNewPassword;
      
      await fs.writeJson(this.USERS_FILE, users, { spaces: 2 });
      return true;
    } catch (error) {
      console.error('Помилка зміни пароля:', error);
      return false;
    }
  }

  private generateToken(userId: string, userData: any): string {
    const payload: Omit<AuthToken, 'iat' | 'exp'> = {
      userId,
      username: userData.username,
      role: userData.role
    };

    return jwt.sign(payload, this.JWT_SECRET, { expiresIn: '7d' });
  }

  private async loadUsers(): Promise<Record<string, any>> {
    try {
      return await fs.readJson(this.USERS_FILE);
    } catch (error) {
      return {};
    }
  }

  generateApiKey(userId: string): string {
    const payload = {
      userId,
      type: 'api',
      generatedAt: Date.now()
    };

    return jwt.sign(payload, this.JWT_SECRET);
  }

  async validateApiKey(apiKey: string): Promise<string | null> {
    try {
      const decoded = jwt.verify(apiKey, this.JWT_SECRET) as any;
      
      if (decoded.type !== 'api') {
        return null;
      }

      const users = await this.loadUsers();
      const user = users[decoded.userId];
      
      if (!user) {
        return null;
      }

      return decoded.userId;
    } catch (error) {
      return null;
    }
  }
}