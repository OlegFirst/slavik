/**
 * Organization Authentication Manager
 * Complete auth system for NPO organizations with Supabase Auth
 * 
 * @module OrganizationAuthManager
 * @version 2.0.0
 */

import { createClient } from '@supabase/supabase-js';
import { EventEmitter } from 'events';
import crypto from 'crypto';
import jwt from 'jsonwebtoken';

export class OrganizationAuthManager extends EventEmitter {
    constructor() {
        super();
        this.supabase = null;
        this.currentSession = null;
        this.currentUser = null;
        this.currentOrganization = null;
    }

    /**
     * Initialize auth manager with Supabase
     */
    async initialize() {
        try {
            this.supabase = createClient(
                process.env.SUPABASE_URL,
                process.env.SUPABASE_ANON_KEY,
                {
                    auth: {
                        autoRefreshToken: true,
                        persistSession: true,
                        detectSessionInUrl: true,
                        storage: {
                            getItem: (key) => {
                                if (typeof window !== 'undefined') {
                                    return window.localStorage.getItem(key);
                                }
                                return null;
                            },
                            setItem: (key, value) => {
                                if (typeof window !== 'undefined') {
                                    window.localStorage.setItem(key, value);
                                }
                            },
                            removeItem: (key) => {
                                if (typeof window !== 'undefined') {
                                    window.localStorage.removeItem(key);
                                }
                            }
                        }
                    }
                }
            );

            // Check for existing session
            const { data: { session } } = await this.supabase.auth.getSession();
            if (session) {
                this.currentSession = session;
                this.currentUser = session.user;
                await this.loadOrganizationProfile();
            }

            // Listen for auth changes
            this.supabase.auth.onAuthStateChange((event, session) => {
                this.handleAuthChange(event, session);
            });

            console.log('Organization Auth Manager initialized');
            return true;
        } catch (error) {
            console.error('Auth initialization failed:', error);
            throw error;
        }
    }

    /**
     * Register new organization
     */
    async registerOrganization(data) {
        try {
            const {
                email,
                password,
                organizationName,
                organizationType,
                mission,
                website,
                contactPerson,
                phone,
                address,
                size,
                annualBudget,
                taxId
            } = data;

            // Step 1: Create user account
            const { data: authData, error: authError } = await this.supabase.auth.signUp({
                email,
                password,
                options: {
                    data: {
                        organization_name: organizationName,
                        contact_person: contactPerson,
                        role: 'organization_admin'
                    },
                    emailRedirectTo: `${window.location.origin}/verify-email`
                }
            });

            if (authError) throw authError;

            // Step 2: Create organization profile
            const organizationId = `org_${Date.now()}_${crypto.randomBytes(4).toString('hex')}`;
            
            const { data: org, error: orgError } = await this.supabase
                .from('organizations')
                .insert({
                    organization_id: organizationId,
                    name: organizationName,
                    type: organizationType,
                    mission,
                    website,
                    size,
                    annual_budget: annualBudget,
                    contact_info: {
                        email,
                        phone,
                        address,
                        contact_person: contactPerson,
                        tax_id: taxId
                    },
                    metadata: {
                        registration_date: new Date().toISOString(),
                        verification_status: 'pending',
                        account_tier: 'free'
                    },
                    created_by: authData.user.id,
                    is_active: true
                })
                .select()
                .single();

            if (orgError) {
                // Rollback user creation if org creation fails
                await this.supabase.auth.admin.deleteUser(authData.user.id);
                throw orgError;
            }

            // Step 3: Create default digital twin
            const twinId = `twin_${organizationId}_${crypto.randomBytes(4).toString('hex')}`;
            
            const { data: twin, error: twinError } = await this.supabase
                .from('digital_twins')
                .insert({
                    twin_id: twinId,
                    organization_id: org.id,
                    name: `${organizationName} Digital Twin`,
                    configuration: {
                        modules: ['basic_analytics', 'reporting', 'simulations'],
                        features: {
                            realtime_metrics: true,
                            ai_predictions: false,
                            advanced_simulations: false
                        }
                    },
                    state: {
                        initialized: true,
                        last_sync: new Date().toISOString()
                    },
                    health_score: 0.5,
                    efficiency_score: 0.5,
                    is_active: true
                })
                .select()
                .single();

            if (twinError) {
                console.error('Twin creation failed:', twinError);
            }

            // Step 4: Send welcome email (handled by Supabase)
            
            // Step 5: Log registration
            await this.logAudit('organization_registered', 'organization', org.id, {
                organization_name: organizationName,
                email
            });

            this.emit('registration_complete', {
                user: authData.user,
                organization: org,
                twin: twin
            });

            return {
                success: true,
                user: authData.user,
                organization: org,
                twin: twin,
                message: 'Registration successful! Please check your email to verify your account.'
            };

        } catch (error) {
            console.error('Registration failed:', error);
            this.emit('registration_failed', error);
            throw error;
        }
    }

    /**
     * Sign in organization
     */
    async signIn(email, password) {
        try {
            // Sign in with Supabase Auth
            const { data, error } = await this.supabase.auth.signInWithPassword({
                email,
                password
            });

            if (error) throw error;

            this.currentSession = data.session;
            this.currentUser = data.user;

            // Load organization profile
            await this.loadOrganizationProfile();

            // Update last login
            await this.supabase
                .from('organizations')
                .update({
                    metadata: {
                        ...this.currentOrganization.metadata,
                        last_login: new Date().toISOString()
                    }
                })
                .eq('id', this.currentOrganization.id);

            // Log sign in
            await this.logAudit('user_signed_in', 'organization', this.currentOrganization.id);

            this.emit('signed_in', {
                user: this.currentUser,
                organization: this.currentOrganization
            });

            return {
                success: true,
                user: this.currentUser,
                organization: this.currentOrganization,
                session: this.currentSession
            };

        } catch (error) {
            console.error('Sign in failed:', error);
            this.emit('sign_in_failed', error);
            throw error;
        }
    }

    /**
     * Sign out
     */
    async signOut() {
        try {
            await this.logAudit('user_signed_out', 'organization', this.currentOrganization?.id);
            
            const { error } = await this.supabase.auth.signOut();
            if (error) throw error;

            this.currentSession = null;
            this.currentUser = null;
            this.currentOrganization = null;

            this.emit('signed_out');

            return { success: true };
        } catch (error) {
            console.error('Sign out failed:', error);
            throw error;
        }
    }

    /**
     * Reset password
     */
    async resetPassword(email) {
        try {
            const { error } = await this.supabase.auth.resetPasswordForEmail(email, {
                redirectTo: `${window.location.origin}/reset-password`
            });

            if (error) throw error;

            return {
                success: true,
                message: 'Password reset email sent. Please check your inbox.'
            };
        } catch (error) {
            console.error('Password reset failed:', error);
            throw error;
        }
    }

    /**
     * Update password
     */
    async updatePassword(newPassword) {
        try {
            const { error } = await this.supabase.auth.updateUser({
                password: newPassword
            });

            if (error) throw error;

            await this.logAudit('password_updated', 'user', this.currentUser.id);

            return {
                success: true,
                message: 'Password updated successfully'
            };
        } catch (error) {
            console.error('Password update failed:', error);
            throw error;
        }
    }

    /**
     * Load organization profile
     */
    async loadOrganizationProfile() {
        if (!this.currentUser) return null;

        try {
            const { data, error } = await this.supabase
                .from('organizations')
                .select(`
                    *,
                    digital_twins (
                        id,
                        twin_id,
                        name,
                        health_score,
                        efficiency_score,
                        last_simulation_at
                    )
                `)
                .eq('created_by', this.currentUser.id)
                .single();

            if (error) throw error;

            this.currentOrganization = data;
            return data;
        } catch (error) {
            console.error('Failed to load organization profile:', error);
            return null;
        }
    }

    /**
     * Update organization profile
     */
    async updateOrganizationProfile(updates) {
        if (!this.currentOrganization) {
            throw new Error('No organization loaded');
        }

        try {
            const { data, error } = await this.supabase
                .from('organizations')
                .update(updates)
                .eq('id', this.currentOrganization.id)
                .select()
                .single();

            if (error) throw error;

            this.currentOrganization = data;

            await this.logAudit('organization_updated', 'organization', data.id, updates);

            this.emit('profile_updated', data);

            return {
                success: true,
                organization: data
            };
        } catch (error) {
            console.error('Profile update failed:', error);
            throw error;
        }
    }

    /**
     * Get current session
     */
    async getSession() {
        const { data: { session } } = await this.supabase.auth.getSession();
        return session;
    }

    /**
     * Check if user is authenticated
     */
    isAuthenticated() {
        return !!this.currentSession && !!this.currentUser;
    }

    /**
     * Get current organization
     */
    getCurrentOrganization() {
        return this.currentOrganization;
    }

    /**
     * Get current user
     */
    getCurrentUser() {
        return this.currentUser;
    }

    /**
     * Handle auth state changes
     */
    handleAuthChange(event, session) {
        console.log('Auth state changed:', event);

        switch (event) {
            case 'SIGNED_IN':
                this.currentSession = session;
                this.currentUser = session?.user;
                this.loadOrganizationProfile();
                break;
            
            case 'SIGNED_OUT':
                this.currentSession = null;
                this.currentUser = null;
                this.currentOrganization = null;
                break;
            
            case 'TOKEN_REFRESHED':
                this.currentSession = session;
                break;
            
            case 'USER_UPDATED':
                this.currentUser = session?.user;
                break;
        }

        this.emit('auth_state_changed', { event, session });
    }

    /**
     * Verify email token
     */
    async verifyEmail(token) {
        try {
            const { error } = await this.supabase.auth.verifyOtp({
                token_hash: token,
                type: 'email'
            });

            if (error) throw error;

            await this.logAudit('email_verified', 'user', this.currentUser?.id);

            return {
                success: true,
                message: 'Email verified successfully'
            };
        } catch (error) {
            console.error('Email verification failed:', error);
            throw error;
        }
    }

    /**
     * Create API key for organization
     */
    async createAPIKey(name, permissions = []) {
        if (!this.currentOrganization) {
            throw new Error('No organization loaded');
        }

        try {
            const apiKey = `dtw_${crypto.randomBytes(32).toString('hex')}`;
            const hashedKey = crypto.createHash('sha256').update(apiKey).digest('hex');

            // Store API key metadata
            const { data, error } = await this.supabase
                .from('api_keys')
                .insert({
                    organization_id: this.currentOrganization.id,
                    name,
                    key_hash: hashedKey,
                    permissions,
                    last_used: null,
                    expires_at: new Date(Date.now() + 365 * 24 * 60 * 60 * 1000).toISOString(),
                    is_active: true
                })
                .select()
                .single();

            if (error) throw error;

            await this.logAudit('api_key_created', 'api_key', data.id, { name });

            return {
                success: true,
                apiKey, // Return plain key only once
                keyId: data.id,
                message: 'API key created. Please save it securely as it won\'t be shown again.'
            };
        } catch (error) {
            console.error('API key creation failed:', error);
            throw error;
        }
    }

    /**
     * List organization's API keys
     */
    async listAPIKeys() {
        if (!this.currentOrganization) {
            throw new Error('No organization loaded');
        }

        try {
            const { data, error } = await this.supabase
                .from('api_keys')
                .select('id, name, permissions, last_used, expires_at, is_active, created_at')
                .eq('organization_id', this.currentOrganization.id)
                .order('created_at', { ascending: false });

            if (error) throw error;

            return data;
        } catch (error) {
            console.error('Failed to list API keys:', error);
            throw error;
        }
    }

    /**
     * Revoke API key
     */
    async revokeAPIKey(keyId) {
        try {
            const { error } = await this.supabase
                .from('api_keys')
                .update({ is_active: false })
                .eq('id', keyId)
                .eq('organization_id', this.currentOrganization.id);

            if (error) throw error;

            await this.logAudit('api_key_revoked', 'api_key', keyId);

            return {
                success: true,
                message: 'API key revoked successfully'
            };
        } catch (error) {
            console.error('API key revocation failed:', error);
            throw error;
        }
    }

    /**
     * Get organization dashboard data
     */
    async getDashboardData() {
        if (!this.currentOrganization) {
            throw new Error('No organization loaded');
        }

        try {
            // Get organization's digital twins
            const { data: twins } = await this.supabase
                .from('digital_twins')
                .select('*')
                .eq('organization_id', this.currentOrganization.id);

            // Get recent simulations
            const { data: simulations } = await this.supabase
                .from('simulations')
                .select('*')
                .in('twin_id', twins?.map(t => t.id) || [])
                .order('created_at', { ascending: false })
                .limit(10);

            // Get recent metrics
            const { data: metrics } = await this.supabase
                .from('metrics')
                .select('*')
                .in('twin_id', twins?.map(t => t.id) || [])
                .order('timestamp', { ascending: false })
                .limit(100);

            // Get recent predictions
            const { data: predictions } = await this.supabase
                .from('predictions')
                .select('*')
                .in('twin_id', twins?.map(t => t.id) || [])
                .order('created_at', { ascending: false })
                .limit(10);

            // Get usage statistics
            const usage = {
                totalSimulations: simulations?.length || 0,
                totalPredictions: predictions?.length || 0,
                averageHealthScore: twins?.reduce((sum, t) => sum + (t.health_score || 0), 0) / (twins?.length || 1),
                averageEfficiencyScore: twins?.reduce((sum, t) => sum + (t.efficiency_score || 0), 0) / (twins?.length || 1)
            };

            return {
                organization: this.currentOrganization,
                twins,
                recentSimulations: simulations,
                recentMetrics: metrics,
                recentPredictions: predictions,
                usage
            };
        } catch (error) {
            console.error('Failed to load dashboard data:', error);
            throw error;
        }
    }

    /**
     * Log audit event
     */
    async logAudit(action, resourceType, resourceId, changes = null) {
        try {
            await this.supabase
                .from('audit_logs')
                .insert({
                    actor_id: this.currentUser?.id,
                    actor_email: this.currentUser?.email,
                    action,
                    resource_type: resourceType,
                    resource_id: resourceId,
                    changes,
                    ip_address: this.getClientIP(),
                    user_agent: this.getUserAgent(),
                    session_id: this.currentSession?.access_token?.substring(0, 20)
                });
        } catch (error) {
            console.error('Audit logging failed:', error);
        }
    }

    /**
     * Get client IP (placeholder - implement based on environment)
     */
    getClientIP() {
        if (typeof window !== 'undefined') {
            return 'browser-client';
        }
        return '127.0.0.1';
    }

    /**
     * Get user agent
     */
    getUserAgent() {
        if (typeof window !== 'undefined' && window.navigator) {
            return window.navigator.userAgent;
        }
        return 'node-client';
    }
}

// Export singleton instance
export const organizationAuth = new OrganizationAuthManager();