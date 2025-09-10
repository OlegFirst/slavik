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
exports.AuthService = void 0;
const bcrypt = __importStar(require("bcrypt"));
const jwt = __importStar(require("jsonwebtoken"));
const fs = __importStar(require("fs-extra"));
const path = __importStar(require("path"));
const uuid_1 = require("uuid");
class AuthService {
    constructor(dataDir = './data') {
        this.SALT_ROUNDS = 10;
        this.JWT_SECRET = process.env.JWT_SECRET || 'documentator-secret-key-change-in-production';
        this.USERS_FILE = path.join(dataDir, 'users.json');
        this.ensureDataDir(dataDir);
    }
    async ensureDataDir(dataDir) {
        await fs.ensureDir(dataDir);
        if (!await fs.pathExists(this.USERS_FILE)) {
            await this.createDefaultAdmin();
        }
    }
    async createDefaultAdmin() {
        const defaultAdmin = {
            id: (0, uuid_1.v4)(),
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
    async login(credentials) {
        try {
            const users = await this.loadUsers();
            const userEntry = Object.entries(users).find(([_, userData]) => userData.username === credentials.username);
            if (!userEntry) {
                return null;
            }
            const [userId, userData] = userEntry;
            const isValidPassword = await bcrypt.compare(credentials.password, userData.passwordHash);
            if (!isValidPassword) {
                return null;
            }
            const token = this.generateToken(userId, userData);
            const user = {
                id: userId,
                username: userData.username,
                email: userData.email,
                role: userData.role,
                createdAt: userData.createdAt
            };
            return { token, user };
        }
        catch (error) {
            console.error('Помилка авторизації:', error);
            return null;
        }
    }
    async register(data) {
        try {
            const users = await this.loadUsers();
            const existingUser = Object.values(users).find(user => user.username === data.username || user.email === data.email);
            if (existingUser) {
                throw new Error('Користувач з таким логіном або email вже існує');
            }
            const hashedPassword = await bcrypt.hash(data.password, this.SALT_ROUNDS);
            const newUser = {
                id: (0, uuid_1.v4)(),
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
        }
        catch (error) {
            console.error('Помилка реєстрації:', error);
            return null;
        }
    }
    async validateToken(token) {
        try {
            const decoded = jwt.verify(token, this.JWT_SECRET);
            const users = await this.loadUsers();
            const user = users[decoded.userId];
            if (!user) {
                return null;
            }
            return decoded;
        }
        catch (error) {
            return null;
        }
    }
    async getUserById(userId) {
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
        }
        catch (error) {
            console.error('Помилка отримання користувача:', error);
            return null;
        }
    }
    async updateUserRole(userId, newRole) {
        try {
            const users = await this.loadUsers();
            if (!users[userId]) {
                return false;
            }
            users[userId].role = newRole;
            await fs.writeJson(this.USERS_FILE, users, { spaces: 2 });
            return true;
        }
        catch (error) {
            console.error('Помилка оновлення ролі:', error);
            return false;
        }
    }
    async changePassword(userId, oldPassword, newPassword) {
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
        }
        catch (error) {
            console.error('Помилка зміни пароля:', error);
            return false;
        }
    }
    generateToken(userId, userData) {
        const payload = {
            userId,
            username: userData.username,
            role: userData.role
        };
        return jwt.sign(payload, this.JWT_SECRET, { expiresIn: '7d' });
    }
    async loadUsers() {
        try {
            return await fs.readJson(this.USERS_FILE);
        }
        catch (error) {
            return {};
        }
    }
    generateApiKey(userId) {
        const payload = {
            userId,
            type: 'api',
            generatedAt: Date.now()
        };
        return jwt.sign(payload, this.JWT_SECRET);
    }
    async validateApiKey(apiKey) {
        try {
            const decoded = jwt.verify(apiKey, this.JWT_SECRET);
            if (decoded.type !== 'api') {
                return null;
            }
            const users = await this.loadUsers();
            const user = users[decoded.userId];
            if (!user) {
                return null;
            }
            return decoded.userId;
        }
        catch (error) {
            return null;
        }
    }
}
exports.AuthService = AuthService;
//# sourceMappingURL=AuthService.js.map