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
export declare class AuthService {
    private readonly JWT_SECRET;
    private readonly USERS_FILE;
    private readonly SALT_ROUNDS;
    constructor(dataDir?: string);
    private ensureDataDir;
    private createDefaultAdmin;
    login(credentials: LoginCredentials): Promise<{
        token: string;
        user: User;
    } | null>;
    register(data: RegisterData): Promise<User | null>;
    validateToken(token: string): Promise<AuthToken | null>;
    getUserById(userId: string): Promise<User | null>;
    updateUserRole(userId: string, newRole: 'admin' | 'user'): Promise<boolean>;
    changePassword(userId: string, oldPassword: string, newPassword: string): Promise<boolean>;
    private generateToken;
    private loadUsers;
    generateApiKey(userId: string): string;
    validateApiKey(apiKey: string): Promise<string | null>;
}
//# sourceMappingURL=AuthService.d.ts.map