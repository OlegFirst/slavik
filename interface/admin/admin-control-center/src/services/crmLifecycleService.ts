/**
 * CRM Lifecycle Integration Service
 *
 * This service acts as the "lifecycle engine" connecting user management
 * through Odoo CRM (res.users) with Digital Twin creation and lifecycle.
 *
 * Features:
 * - Integration with res.users for user lifecycle
 * - Personal Twin creation on user registration
 * - User activity tracking through CRM
 * - Role-based permissions through CRM
 * - Lifecycle events (user login/logout/activity)
 * - Real-time user status synchronization
 */

import { bcmAPI } from './api';
import { getEventBusService, publishPersonalTwinEvent, publishDataCollectionEvent } from './eventBusService';
import type { PersonalTwin } from './digitalTwinAPI';

// CRM User Types
export interface CRMUser {
  id: number;
  name: string;
  email: string;
  login: string;
  active: boolean;
  partner_id: number;
  groups_id: number[];
  company_id: number;
  company_ids: number[];
  lang: string;
  tz: string;
  image_1920?: string;
  phone?: string;
  mobile?: string;
  is_company: boolean;
  create_date: string;
  write_date: string;
  last_login?: string;
  login_count: number;
  share: boolean;
  sel_groups_1_9_10?: number;
  category_id: number[];
}

export interface CRMUserActivity {
  id: number;
  user_id: number;
  activity_type: string;
  description: string;
  timestamp: string;
  ip_address?: string;
  user_agent?: string;
  session_id?: string;
  module?: string;
  model?: string;
  record_id?: number;
}

export interface CRMUserSession {
  id: string;
  user_id: number;
  started_at: string;
  last_activity: string;
  ip_address: string;
  user_agent: string;
  active: boolean;
  expired_at?: string;
}

export interface UserLifecycleEvent {
  type: 'user_created' | 'user_updated' | 'user_activated' | 'user_deactivated' | 'user_login' | 'user_logout';
  user_id: number;
  user: Partial<CRMUser>;
  timestamp: string;
  metadata?: Record<string, any>;
}

export interface PersonalTwinCreationRequest {
  user_id: number;
  user_name: string;
  user_email: string;
  privacy_settings: {
    behaviorTracking: boolean;
    performanceMonitoring: boolean;
    aiInsights: boolean;
  };
  initial_data_sources: string[];
}

// API Endpoints
const CRM_API_BASE = '/web/dataset/call_kw/res.users';
const ACTIVITY_API_BASE = '/web/dataset/call_kw/bcm.user.activity';
const SESSION_API_BASE = '/web/dataset/call_kw/bcm.user.session';

class CRMLifecycleService {
  private eventBus = getEventBusService();
  private userCache = new Map<number, CRMUser>();
  private sessionCache = new Map<string, CRMUserSession>();
  private isInitialized = false;

  /**
   * Initialize CRM Lifecycle Service
   */
  public async initialize(): Promise<void> {
    if (this.isInitialized) {
      return;
    }

    try {
      // Initialize EventBus connection
      await this.eventBus.initialize();

      // Subscribe to user lifecycle events from CRM
      this.setupEventSubscriptions();

      // Load initial user data
      await this.loadActiveUsers();

      this.isInitialized = true;
      console.log(' CRM Lifecycle Service initialized successfully');

    } catch (error) {
      console.error(' Failed to initialize CRM Lifecycle Service:', error);
      throw error;
    }
  }

  /**
   * Get all active users from CRM
   */
  public async getActiveUsers(): Promise<CRMUser[]> {
    try {
      const response = await bcmAPI.post(CRM_API_BASE, {
        method: 'search_read',
        args: [[['active', '=', true]]],
        kwargs: {
          fields: [
            'id', 'name', 'email', 'login', 'active', 'partner_id',
            'groups_id', 'company_id', 'company_ids', 'lang', 'tz',
            'phone', 'mobile', 'create_date', 'write_date', 'last_login',
            'login_count', 'share', 'category_id'
          ]
        }
      });

      const users = response.data.result || [];

      // Update cache
      users.forEach((user: CRMUser) => {
        this.userCache.set(user.id, user);
      });

      console.log(` Loaded ${users.length} active users from CRM`);
      return users;

    } catch (error) {
      console.error(' Failed to load active users from CRM:', error);
      throw error;
    }
  }

  /**
   * Get user by ID from CRM
   */
  public async getUser(userId: number): Promise<CRMUser | null> {
    try {
      // Check cache first
      if (this.userCache.has(userId)) {
        return this.userCache.get(userId)!;
      }

      const response = await bcmAPI.post(CRM_API_BASE, {
        method: 'read',
        args: [userId],
        kwargs: {
          fields: [
            'id', 'name', 'email', 'login', 'active', 'partner_id',
            'groups_id', 'company_id', 'company_ids', 'lang', 'tz',
            'phone', 'mobile', 'create_date', 'write_date', 'last_login',
            'login_count', 'share', 'category_id'
          ]
        }
      });

      const user = response.data.result?.[0];
      if (user) {
        this.userCache.set(userId, user);
      }

      return user || null;

    } catch (error) {
      console.error(` Failed to load user ${userId} from CRM:`, error);
      return null;
    }
  }

  /**
   * Create new user in CRM and trigger Digital Twin creation
   */
  public async createUser(userData: {
    name: string;
    email: string;
    login: string;
    password: string;
    groups_id?: number[];
    company_id?: number;
    lang?: string;
    tz?: string;
    phone?: string;
    mobile?: string;
  }): Promise<CRMUser> {
    try {
      // Create user in CRM
      const response = await bcmAPI.post(CRM_API_BASE, {
        method: 'create',
        args: [userData],
        kwargs: {}
      });

      const userId = response.data.result;
      if (!userId) {
        throw new Error('Failed to create user in CRM');
      }

      // Get the created user data
      const user = await this.getUser(userId);
      if (!user) {
        throw new Error('Failed to retrieve created user');
      }

      // Trigger user creation event
      await this.publishUserLifecycleEvent({
        type: 'user_created',
        user_id: userId,
        user: user,
        timestamp: new Date().toISOString()
      });

      // Create Personal Twin for new user
      await this.createPersonalTwinForUser(user);

      console.log(` Created user ${user.name} (${user.email}) and Personal Twin`);
      return user;

    } catch (error) {
      console.error(' Failed to create user:', error);
      throw error;
    }
  }

  /**
   * Update user in CRM
   */
  public async updateUser(userId: number, updates: Partial<CRMUser>): Promise<CRMUser> {
    try {
      await bcmAPI.post(CRM_API_BASE, {
        method: 'write',
        args: [userId, updates],
        kwargs: {}
      });

      // Get updated user data
      const user = await this.getUser(userId);
      if (!user) {
        throw new Error('Failed to retrieve updated user');
      }

      // Trigger user update event
      await this.publishUserLifecycleEvent({
        type: 'user_updated',
        user_id: userId,
        user: user,
        timestamp: new Date().toISOString(),
        metadata: { changes: updates }
      });

      console.log(` Updated user ${user.name} (${user.email})`);
      return user;

    } catch (error) {
      console.error(` Failed to update user ${userId}:`, error);
      throw error;
    }
  }

  /**
   * Activate user
   */
  public async activateUser(userId: number): Promise<void> {
    const user = await this.updateUser(userId, { active: true });

    await this.publishUserLifecycleEvent({
      type: 'user_activated',
      user_id: userId,
      user: user,
      timestamp: new Date().toISOString()
    });

    // Reactivate or create Personal Twin
    await this.ensurePersonalTwinForUser(user);
  }

  /**
   * Deactivate user
   */
  public async deactivateUser(userId: number): Promise<void> {
    const user = await this.updateUser(userId, { active: false });

    await this.publishUserLifecycleEvent({
      type: 'user_deactivated',
      user_id: userId,
      user: user,
      timestamp: new Date().toISOString()
    });

    // Pause Personal Twin data collection
    await this.pausePersonalTwinDataCollection(userId);
  }

  /**
   * Record user login
   */
  public async recordUserLogin(userId: number, sessionData: {
    session_id: string;
    ip_address: string;
    user_agent: string;
  }): Promise<void> {
    try {
      const user = await this.getUser(userId);
      if (!user) {
        throw new Error(`User ${userId} not found`);
      }

      // Create session record
      const session: CRMUserSession = {
        id: sessionData.session_id,
        user_id: userId,
        started_at: new Date().toISOString(),
        last_activity: new Date().toISOString(),
        ip_address: sessionData.ip_address,
        user_agent: sessionData.user_agent,
        active: true
      };

      this.sessionCache.set(sessionData.session_id, session);

      // Update user last login
      await this.updateUser(userId, {
        last_login: new Date().toISOString(),
        login_count: user.login_count + 1
      });

      // Record activity
      await this.recordUserActivity({
        user_id: userId,
        activity_type: 'login',
        description: 'User logged in',
        timestamp: new Date().toISOString(),
        ip_address: sessionData.ip_address,
        user_agent: sessionData.user_agent,
        session_id: sessionData.session_id
      });

      // Trigger login event
      await this.publishUserLifecycleEvent({
        type: 'user_login',
        user_id: userId,
        user: user,
        timestamp: new Date().toISOString(),
        metadata: sessionData
      });

      // Resume Personal Twin data collection if paused
      await this.resumePersonalTwinDataCollection(userId);

      console.log(` Recorded login for user ${user.name} (${user.email})`);

    } catch (error) {
      console.error(` Failed to record user login for ${userId}:`, error);
      throw error;
    }
  }

  /**
   * Record user logout
   */
  public async recordUserLogout(sessionId: string): Promise<void> {
    try {
      const session = this.sessionCache.get(sessionId);
      if (!session) {
        console.warn(`Session ${sessionId} not found in cache`);
        return;
      }

      const user = await this.getUser(session.user_id);
      if (!user) {
        throw new Error(`User ${session.user_id} not found`);
      }

      // Update session
      session.active = false;
      session.expired_at = new Date().toISOString();
      this.sessionCache.set(sessionId, session);

      // Record activity
      await this.recordUserActivity({
        user_id: session.user_id,
        activity_type: 'logout',
        description: 'User logged out',
        timestamp: new Date().toISOString(),
        session_id: sessionId
      });

      // Trigger logout event
      await this.publishUserLifecycleEvent({
        type: 'user_logout',
        user_id: session.user_id,
        user: user,
        timestamp: new Date().toISOString(),
        metadata: { session_id: sessionId }
      });

      console.log(` Recorded logout for user ${user.name} (${user.email})`);

    } catch (error) {
      console.error(` Failed to record user logout for session ${sessionId}:`, error);
      throw error;
    }
  }

  /**
   * Record user activity
   */
  public async recordUserActivity(activity: Omit<CRMUserActivity, 'id'>): Promise<void> {
    try {
      await bcmAPI.post(ACTIVITY_API_BASE, {
        method: 'create',
        args: [activity],
        kwargs: {}
      });

      // Update Personal Twin with activity data
      await this.updatePersonalTwinActivity(activity.user_id, activity);

    } catch (error) {
      console.error(' Failed to record user activity:', error);
    }
  }

  /**
   * Get user activity history
   */
  public async getUserActivity(userId: number, limit: number = 100): Promise<CRMUserActivity[]> {
    try {
      const response = await bcmAPI.post(ACTIVITY_API_BASE, {
        method: 'search_read',
        args: [[['user_id', '=', userId]]],
        kwargs: {
          fields: ['id', 'user_id', 'activity_type', 'description', 'timestamp', 'ip_address', 'user_agent', 'session_id', 'module', 'model', 'record_id'],
          limit: limit,
          order: 'timestamp desc'
        }
      });

      return response.data.result || [];

    } catch (error) {
      console.error(` Failed to get user activity for ${userId}:`, error);
      return [];
    }
  }

  /**
   * Get active sessions
   */
  public async getActiveSessions(): Promise<CRMUserSession[]> {
    return Array.from(this.sessionCache.values()).filter(session => session.active);
  }

  /**
   * Get user permissions and roles
   */
  public async getUserPermissions(userId: number): Promise<{
    groups: string[];
    permissions: string[];
    is_admin: boolean;
    is_digital_twin_admin: boolean;
  }> {
    try {
      const user = await this.getUser(userId);
      if (!user) {
        throw new Error(`User ${userId} not found`);
      }

      // Get group information
      const groupResponse = await bcmAPI.post('/web/dataset/call_kw/res.groups', {
        method: 'read',
        args: [user.groups_id],
        kwargs: {
          fields: ['name', 'full_name', 'category_id', 'implied_ids']
        }
      });

      const groups = groupResponse.data.result || [];
      const groupNames = groups.map((g: any) => g.name);

      // Determine permissions
      const is_admin = groupNames.includes('Administration / Access Rights') ||
                      groupNames.includes('Administration / Settings');
      const is_digital_twin_admin = groupNames.includes('Digital Twin / Administrator') ||
                                   groupNames.includes('BCM / Administrator');

      return {
        groups: groupNames,
        permissions: [], // TODO: Implement detailed permissions
        is_admin,
        is_digital_twin_admin
      };

    } catch (error) {
      console.error(` Failed to get user permissions for ${userId}:`, error);
      return {
        groups: [],
        permissions: [],
        is_admin: false,
        is_digital_twin_admin: false
      };
    }
  }

  // Private methods

  private async loadActiveUsers(): Promise<void> {
    try {
      await this.getActiveUsers();
    } catch (error) {
      console.error(' Failed to load initial user data:', error);
    }
  }

  private setupEventSubscriptions(): void {
    // Subscribe to user activity events from EventBus
    this.eventBus.subscribeToUserActivityEvents(async (event) => {
      console.log(' Received user activity event:', event);

      // Update local cache if needed
      if (event.data.userId) {
        await this.getUser(parseInt(event.data.userId));
      }
    });
  }

  private async publishUserLifecycleEvent(event: UserLifecycleEvent): Promise<void> {
    await this.eventBus.publishEvent('crm.users', {
      type: event.type,
      source: 'crm_lifecycle_service',
      data: event
    });
  }

  private async createPersonalTwinForUser(user: CRMUser): Promise<void> {
    try {
      const request: PersonalTwinCreationRequest = {
        user_id: user.id,
        user_name: user.name,
        user_email: user.email,
        privacy_settings: {
          behaviorTracking: true,
          performanceMonitoring: true,
          aiInsights: true
        },
        initial_data_sources: [
          'bcm_core',
          'user_activity',
          'crm_data'
        ]
      };

      // Call Digital Twin API to create Personal Twin
      await bcmAPI.post('/api/digital-twin/personal-twins', request);

      // Publish event
      await publishPersonalTwinEvent({
        type: 'personal_twin.created',
        data: {
          twinId: `twin-${user.id}`,
          userId: user.id.toString(),
          twin: {
            userId: user.id.toString(),
            userName: user.name,
            userEmail: user.email,
            status: 'active'
          }
        }
      });

      console.log(` Created Personal Twin for user ${user.name}`);

    } catch (error) {
      console.error(` Failed to create Personal Twin for user ${user.id}:`, error);
    }
  }

  private async ensurePersonalTwinForUser(user: CRMUser): Promise<void> {
    try {
      // Check if Personal Twin exists
      const response = await bcmAPI.get(`/api/digital-twin/personal-twins/user/${user.id}`);

      if (!response.data) {
        // Create if doesn't exist
        await this.createPersonalTwinForUser(user);
      } else {
        // Reactivate if exists but inactive
        await bcmAPI.put(`/api/digital-twin/personal-twins/${response.data.id}/activate`);
      }

    } catch (error) {
      console.error(` Failed to ensure Personal Twin for user ${user.id}:`, error);
    }
  }

  private async pausePersonalTwinDataCollection(userId: number): Promise<void> {
    try {
      await bcmAPI.put(`/api/digital-twin/personal-twins/user/${userId}/pause-collection`);

      await publishDataCollectionEvent({
        type: 'data_collection.stopped',
        data: {
          serviceId: `personal-twin-${userId}`,
          service: {
            name: `Personal Twin Collection - User ${userId}`,
            status: 'inactive'
          }
        }
      });

    } catch (error) {
      console.error(` Failed to pause Personal Twin data collection for user ${userId}:`, error);
    }
  }

  private async resumePersonalTwinDataCollection(userId: number): Promise<void> {
    try {
      await bcmAPI.put(`/api/digital-twin/personal-twins/user/${userId}/resume-collection`);

      await publishDataCollectionEvent({
        type: 'data_collection.started',
        data: {
          serviceId: `personal-twin-${userId}`,
          service: {
            name: `Personal Twin Collection - User ${userId}`,
            status: 'active'
          }
        }
      });

    } catch (error) {
      console.error(` Failed to resume Personal Twin data collection for user ${userId}:`, error);
    }
  }

  private async updatePersonalTwinActivity(userId: number, activity: Omit<CRMUserActivity, 'id'>): Promise<void> {
    try {
      await bcmAPI.put(`/api/digital-twin/personal-twins/user/${userId}/activity`, {
        activity_type: activity.activity_type,
        description: activity.description,
        timestamp: activity.timestamp,
        metadata: {
          ip_address: activity.ip_address,
          user_agent: activity.user_agent,
          session_id: activity.session_id,
          module: activity.module,
          model: activity.model,
          record_id: activity.record_id
        }
      });

    } catch (error) {
      console.error(` Failed to update Personal Twin activity for user ${userId}:`, error);
    }
  }
}

// Global CRM Lifecycle service instance
let crmLifecycleService: CRMLifecycleService | null = null;

/**
 * Get or create the global CRM Lifecycle service instance
 */
export function getCRMLifecycleService(): CRMLifecycleService {
  if (!crmLifecycleService) {
    crmLifecycleService = new CRMLifecycleService();
  }
  return crmLifecycleService;
}

/**
 * Initialize CRM Lifecycle service
 */
export async function initializeCRMLifecycle(): Promise<CRMLifecycleService> {
  const service = getCRMLifecycleService();
  await service.initialize();
  return service;
}

export default CRMLifecycleService;