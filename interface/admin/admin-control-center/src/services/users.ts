// BCM User Management Service Architecture
// Интеграция: Admin Panel ↔ Odoo ↔ User Database

import { API_ENDPOINTS } from './bcm';

export interface User {
  id: string;
  name: string;
  email: string;
  username: string;
  role: 'admin' | 'manager' | 'analyst' | 'viewer';
  department: string;
  status: 'active' | 'inactive' | 'suspended';
  last_login: string;
  created_date: string;
  permissions: string[];
  bcm_modules_access: string[];
  client_access: string[];
  avatar?: string;
  phone?: string;
  location?: string;
  language: string;
  timezone: string;
  two_factor_enabled: boolean;
  login_count: number;
  odoo_user_id?: number;
}

export interface UserMetrics {
  total_users: number;
  active_users: number;
  new_users_this_month: number;
  users_by_role: Record<User['role'], number>;
  users_by_department: Record<string, number>;
  recent_logins: number;
  suspended_users: number;
}

export const userService = {

  // ======================================
  // LAYER 1: Admin Panel User Management
  // ======================================

  // Get all users for admin management
  async getAdminUsers(): Promise<User[]> {
    try {
      console.log(' Fetching users for admin management...');

      // Get users from Odoo res.users
      const odooUsers = await this.getOdooUsers();

      return odooUsers;
    } catch (error) {
      console.error(' Failed to fetch admin users:', error);
      return this.getFallbackUsers();
    }
  },

  // Get user metrics for dashboard
  async getUserMetrics(): Promise<UserMetrics> {
    try {
      const users = await this.getAdminUsers();

      return {
        total_users: users.length,
        active_users: users.filter(u => u.status === 'active').length,
        new_users_this_month: users.filter(u => {
          const createdDate = new Date(u.created_date);
          const oneMonthAgo = new Date();
          oneMonthAgo.setMonth(oneMonthAgo.getMonth() - 1);
          return createdDate >= oneMonthAgo;
        }).length,
        users_by_role: this.groupByField(users, 'role'),
        users_by_department: this.groupByField(users, 'department'),
        recent_logins: users.filter(u => {
          if (!u.last_login) return false;
          const lastLogin = new Date(u.last_login);
          const sevenDaysAgo = new Date();
          sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);
          return lastLogin >= sevenDaysAgo;
        }).length,
        suspended_users: users.filter(u => u.status === 'suspended').length
      };
    } catch (error) {
      console.error(' Failed to fetch user metrics:', error);
      return this.getFallbackMetrics();
    }
  },

  // Create new user
  async createUser(userData: Omit<User, 'id' | 'created_date' | 'last_login' | 'login_count'>): Promise<boolean> {
    try {
      console.log(' Creating new user...');

      const response = await fetch(`${API_ENDPOINTS.ODOO_BCM}/web/dataset/call_kw/res.users/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          params: {
            vals: {
              name: userData.name,
              email: userData.email,
              login: userData.username,
              bcm_role: userData.role,
              bcm_department: userData.department,
              bcm_status: userData.status,
              bcm_permissions: userData.permissions.join(','),
              bcm_modules_access: userData.bcm_modules_access.join(','),
              bcm_client_access: userData.client_access.join(','),
              phone: userData.phone,
              bcm_location: userData.location,
              lang: userData.language,
              tz: userData.timezone,
              bcm_two_factor_enabled: userData.two_factor_enabled,
              active: userData.status === 'active'
            }
          }
        })
      });

      return response.ok;
    } catch (error) {
      console.error(' Failed to create user:', error);
      return false;
    }
  },

  // Update user information
  async updateUser(userId: string, updates: Partial<User>): Promise<boolean> {
    try {
      console.log(` Updating user ${userId}...`);

      const response = await fetch(`${API_ENDPOINTS.ODOO_BCM}/web/dataset/call_kw/res.users/write`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          params: {
            ids: [parseInt(userId)],
            vals: this.mapUserToOdooVals(updates)
          }
        })
      });

      return response.ok;
    } catch (error) {
      console.error(' Failed to update user:', error);
      return false;
    }
  },

  // Suspend/unsuspend user
  async toggleUserStatus(userId: string, status: User['status']): Promise<boolean> {
    try {
      console.log(` Changing user ${userId} status to ${status}...`);

      const response = await fetch(`${API_ENDPOINTS.ODOO_BCM}/web/dataset/call_kw/res.users/write`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          params: {
            ids: [parseInt(userId)],
            vals: {
              bcm_status: status,
              active: status === 'active'
            }
          }
        })
      });

      return response.ok;
    } catch (error) {
      console.error(' Failed to toggle user status:', error);
      return false;
    }
  },

  // ======================================
  // LAYER 2: Odoo Integration
  // ======================================

  // Get users from Odoo res.users
  async getOdooUsers(): Promise<User[]> {
    try {
      const response = await fetch(`${API_ENDPOINTS.ODOO_BCM}/web/dataset/call_kw/res.users/search_read`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          params: {
            domain: [['bcm_user', '=', true]],
            fields: [
              'name', 'email', 'login', 'bcm_role', 'bcm_department', 'bcm_status',
              'bcm_permissions', 'bcm_modules_access', 'bcm_client_access',
              'phone', 'bcm_location', 'lang', 'tz', 'bcm_two_factor_enabled',
              'bcm_last_login', 'create_date', 'bcm_login_count', 'image_1920'
            ]
          }
        })
      });

      if (response.ok) {
        const result = await response.json();
        return (result.result || []).map(this.mapOdooToUser);
      }
      return [];
    } catch (error) {
      console.warn('Odoo users unavailable:', error);
      return [];
    }
  },

  // ======================================
  // UTILITY FUNCTIONS
  // ======================================

  // Map Odoo record to User interface
  mapOdooToUser(odooRecord: any): User {
    return {
      id: odooRecord.id.toString(),
      name: odooRecord.name || '',
      email: odooRecord.email || '',
      username: odooRecord.login || '',
      role: odooRecord.bcm_role || 'viewer',
      department: odooRecord.bcm_department || 'Operations',
      status: odooRecord.bcm_status || 'active',
      last_login: odooRecord.bcm_last_login || '',
      created_date: odooRecord.create_date,
      permissions: odooRecord.bcm_permissions ?
        odooRecord.bcm_permissions.split(',') : ['read'],
      bcm_modules_access: odooRecord.bcm_modules_access ?
        odooRecord.bcm_modules_access.split(',') : [],
      client_access: odooRecord.bcm_client_access ?
        odooRecord.bcm_client_access.split(',') : [],
      phone: odooRecord.phone || '',
      location: odooRecord.bcm_location || '',
      language: odooRecord.lang || 'en_US',
      timezone: odooRecord.tz || 'UTC',
      two_factor_enabled: odooRecord.bcm_two_factor_enabled || false,
      login_count: odooRecord.bcm_login_count || 0,
      avatar: odooRecord.image_1920,
      odoo_user_id: odooRecord.id
    };
  },

  // Map User updates to Odoo vals
  mapUserToOdooVals(user: Partial<User>): any {
    const vals: any = {};

    if (user.name) vals.name = user.name;
    if (user.email) vals.email = user.email;
    if (user.username) vals.login = user.username;
    if (user.role) vals.bcm_role = user.role;
    if (user.department) vals.bcm_department = user.department;
    if (user.status) {
      vals.bcm_status = user.status;
      vals.active = user.status === 'active';
    }
    if (user.permissions) vals.bcm_permissions = user.permissions.join(',');
    if (user.bcm_modules_access) vals.bcm_modules_access = user.bcm_modules_access.join(',');
    if (user.client_access) vals.bcm_client_access = user.client_access.join(',');
    if (user.phone) vals.phone = user.phone;
    if (user.location) vals.bcm_location = user.location;
    if (user.language) vals.lang = user.language;
    if (user.timezone) vals.tz = user.timezone;
    if (user.two_factor_enabled !== undefined) vals.bcm_two_factor_enabled = user.two_factor_enabled;

    return vals;
  },

  // Group users by field
  groupByField(users: User[], field: keyof User): Record<string, number> {
    return users.reduce((acc, user) => {
      const key = String(user[field]);
      acc[key] = (acc[key] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);
  },

  // Fallback users when Odoo unavailable
  getFallbackUsers(): User[] {
    return [
      {
        id: '1',
        name: 'Admin User',
        email: 'admin@bcm.system',
        username: 'admin',
        role: 'admin',
        department: 'IT',
        status: 'active',
        last_login: '2024-09-17T08:30:00Z',
        created_date: '2023-01-15T00:00:00Z',
        permissions: ['read', 'write', 'delete', 'admin'],
        bcm_modules_access: ['all'],
        client_access: ['all'],
        phone: '+1-555-0001',
        location: 'HQ Office',
        language: 'en_US',
        timezone: 'UTC',
        two_factor_enabled: true,
        login_count: 247
      },
      {
        id: '2',
        name: 'John Manager',
        email: 'john.manager@company.com',
        username: 'jmanager',
        role: 'manager',
        department: 'Operations',
        status: 'active',
        last_login: '2024-09-16T15:45:00Z',
        created_date: '2023-03-20T00:00:00Z',
        permissions: ['read', 'write'],
        bcm_modules_access: ['BCM Core', 'BCM Risk Management', 'BCM BIA'],
        client_access: ['client1', 'client2'],
        phone: '+1-555-0002',
        location: 'Remote',
        language: 'en_US',
        timezone: 'America/New_York',
        two_factor_enabled: true,
        login_count: 156
      },
      {
        id: '3',
        name: 'Sara Analyst',
        email: 'sara.analyst@company.com',
        username: 'sanalyst',
        role: 'analyst',
        department: 'Risk Management',
        status: 'active',
        last_login: '2024-09-17T09:15:00Z',
        created_date: '2024-01-10T00:00:00Z',
        permissions: ['read', 'write'],
        bcm_modules_access: ['BCM Risk Management', 'BCM BIA'],
        client_access: ['client1'],
        phone: '+1-555-0003',
        location: 'Branch Office',
        language: 'en_US',
        timezone: 'America/Los_Angeles',
        two_factor_enabled: false,
        login_count: 89
      }
    ];
  },

  // Fallback metrics when Odoo unavailable
  getFallbackMetrics(): UserMetrics {
    return {
      total_users: 15,
      active_users: 13,
      new_users_this_month: 2,
      users_by_role: {
        admin: 2,
        manager: 4,
        analyst: 6,
        viewer: 3
      },
      users_by_department: {
        'IT': 3,
        'Operations': 5,
        'Risk Management': 4,
        'Compliance': 2,
        'Finance': 1
      },
      recent_logins: 11,
      suspended_users: 1
    };
  }
};

// Export for admin panel integration
export default userService;