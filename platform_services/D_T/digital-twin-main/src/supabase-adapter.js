/**
 * =====================================================================
 * NASH 4.0 - Digital Twin Supabase Database Adapter
 * Enterprise-grade database integration for Digital Twin functionality
 * =====================================================================
 * 
 * Purpose: Provide seamless integration between Digital Twin module and Supabase
 * Author: NASH 4.0 Technical Partnership Team
 * Version: 1.0.0
 * Date: 2025-08-12
 * 
 * Features:
 * - Complete CRUD operations for digital twins and organization data
 * - Real-time subscriptions for data changes
 * - Advanced query capabilities with filtering and pagination
 * - Comprehensive error handling and logging
 * - Performance optimization with connection pooling
 * - Security validation and RLS support
 * =====================================================================
 */

import { createClient } from '@supabase/supabase-js';
import { createLogger } from '../utils/logger.js';
import { 
    ValidationError, 
    DatabaseError, 
    NotFoundError,
    SecurityError 
} from '../utils/errors.js';

export class DigitalTwinSupabaseAdapter {
    constructor(config = {}) {
        this.logger = createLogger('DigitalTwinSupabaseAdapter');
        
        // Initialize Supabase client
        this.supabaseUrl = config.supabaseUrl || process.env.SUPABASE_URL;
        this.supabaseKey = config.supabaseKey || process.env.SUPABASE_ANON_KEY;
        this.supabaseServiceKey = config.supabaseServiceKey || process.env.SUPABASE_SERVICE_ROLE_KEY;
        
        if (!this.supabaseUrl || !this.supabaseKey) {
            throw new Error('Supabase configuration missing: URL and key required');
        }
        
        // Create clients
        this.supabase = createClient(this.supabaseUrl, this.supabaseKey);
        this.supabaseAdmin = this.supabaseServiceKey 
            ? createClient(this.supabaseUrl, this.supabaseServiceKey)
            : null;
        
        // Configuration
        this.config = {
            enableRealtime: config.enableRealtime !== false,
            enableCaching: config.enableCaching !== false,
            cacheTimeout: config.cacheTimeout || 300000, // 5 minutes
            maxRetries: config.maxRetries || 3,
            retryDelay: config.retryDelay || 1000,
            ...config
        };
        
        // Internal state
        this.cache = new Map();
        this.subscriptions = new Map();
        this.isInitialized = false;
        
        this.logger.info('DigitalTwinSupabaseAdapter initialized');
    }
    
    /**
     * Initialize the adapter
     * @async
     * @returns {Promise<boolean>}
     */
    async initialize() {
        try {
            this.logger.info('Initializing Supabase adapter...');
            
            // Test connection
            await this.testConnection();
            
            // Setup realtime subscriptions if enabled
            if (this.config.enableRealtime) {
                await this.setupRealtimeSubscriptions();
            }
            
            this.isInitialized = true;
            this.logger.info('Supabase adapter initialized successfully');
            
            return true;
        } catch (error) {
            this.logger.error('Failed to initialize Supabase adapter', { error: error.message });
            throw new DatabaseError(`Adapter initialization failed: ${error.message}`);
        }
    }
    
    /**
     * Test database connection
     * @private
     * @async
     */
    async testConnection() {
        try {
            const { data, error } = await this.supabase
                .from('platform.organizations')
                .select('count', { count: 'exact' })
                .limit(1);
                
            if (error) {
                throw new Error(`Connection test failed: ${error.message}`);
            }
            
            this.logger.debug('Database connection test successful');
        } catch (error) {
            throw new DatabaseError(`Database connection failed: ${error.message}`);
        }
    }
    
    /**
     * Create organization profile
     * @param {Object} organizationData - Organization profile data
     * @returns {Promise<Object>} Created organization profile
     */
    async createOrganizationProfile(organizationData) {
        try {
            this.validateOrganizationData(organizationData);
            
            const { data, error } = await this.supabase
                .from('platform.organization_profiles')
                .insert([organizationData])
                .select()
                .single();
                
            if (error) {
                throw new DatabaseError(`Failed to create organization profile: ${error.message}`);
            }
            
            this.logger.info('Organization profile created', { 
                organizationId: data.organization_id,
                slug: data.slug 
            });
            
            // Clear cache
            this.clearCacheForOrganization(data.organization_id);
            
            return data;
        } catch (error) {
            this.logger.error('Error creating organization profile', { error: error.message });
            throw error;
        }
    }
    
    /**
     * Get organization profile by ID
     * @param {string} organizationId - Organization ID
     * @param {Object} options - Query options
     * @returns {Promise<Object>} Organization profile
     */
    async getOrganizationProfile(organizationId, options = {}) {
        try {
            const cacheKey = `org_profile_${organizationId}`;
            
            // Check cache first
            if (this.config.enableCaching && this.cache.has(cacheKey)) {
                const cached = this.cache.get(cacheKey);
                if (Date.now() - cached.timestamp < this.config.cacheTimeout) {
                    return cached.data;
                }
            }
            
            let query = this.supabase
                .from('platform.organization_profiles')
                .select(`
                    *,
                    organization:platform.organizations(*),
                    departments:platform.organization_departments(*),
                    user_roles:platform.organization_user_roles(*)
                `)
                .eq('organization_id', organizationId);
                
            if (options.includeTwins) {
                query = query.select(`
                    *,
                    organization:platform.organizations(*),
                    departments:platform.organization_departments(*),
                    user_roles:platform.organization_user_roles(*),
                    digital_twins:platform.digital_twins(*)
                `);
            }
                
            const { data, error } = await query.single();
            
            if (error) {
                if (error.code === 'PGRST116') {
                    throw new NotFoundError(`Organization profile not found: ${organizationId}`);
                }
                throw new DatabaseError(`Failed to get organization profile: ${error.message}`);
            }
            
            // Cache result
            if (this.config.enableCaching) {
                this.cache.set(cacheKey, {
                    data,
                    timestamp: Date.now()
                });
            }
            
            return data;
        } catch (error) {
            this.logger.error('Error getting organization profile', { 
                organizationId, 
                error: error.message 
            });
            throw error;
        }
    }
    
    /**
     * Create digital twin
     * @param {Object} twinData - Digital twin data
     * @returns {Promise<Object>} Created digital twin
     */
    async createDigitalTwin(twinData) {
        try {
            this.validateDigitalTwinData(twinData);
            
            // Check if this is the first twin for the organization
            const { data: existingTwins, error: countError } = await this.supabase
                .from('platform.digital_twins')
                .select('id')
                .eq('organization_id', twinData.organization_id);
                
            if (countError) {
                throw new DatabaseError(`Failed to check existing twins: ${countError.message}`);
            }
            
            // Set as primary if it's the first twin
            if (existingTwins.length === 0) {
                twinData.is_primary = true;
            }
            
            const { data, error } = await this.supabase
                .from('platform.digital_twins')
                .insert([twinData])
                .select()
                .single();
                
            if (error) {
                throw new DatabaseError(`Failed to create digital twin: ${error.message}`);
            }
            
            this.logger.info('Digital twin created', { 
                twinId: data.id,
                organizationId: data.organization_id,
                twinName: data.twin_name
            });
            
            // Clear cache
            this.clearCacheForOrganization(data.organization_id);
            
            return data;
        } catch (error) {
            this.logger.error('Error creating digital twin', { error: error.message });
            throw error;
        }
    }
    
    /**
     * Get digital twin by ID
     * @param {string} twinId - Digital twin ID
     * @param {Object} options - Query options
     * @returns {Promise<Object>} Digital twin data
     */
    async getDigitalTwin(twinId, options = {}) {
        try {
            const cacheKey = `digital_twin_${twinId}`;
            
            // Check cache first
            if (this.config.enableCaching && this.cache.has(cacheKey)) {
                const cached = this.cache.get(cacheKey);
                if (Date.now() - cached.timestamp < this.config.cacheTimeout) {
                    return cached.data;
                }
            }
            
            let query = this.supabase
                .from('platform.digital_twins')
                .select(`
                    *,
                    organization:platform.organizations(*),
                    organization_profile:platform.organization_profiles(*)
                `)
                .eq('id', twinId);
                
            if (options.includeSimulations) {
                query = query.select(`
                    *,
                    organization:platform.organizations(*),
                    organization_profile:platform.organization_profiles(*),
                    simulations:platform.simulation_results(*)
                `);
            }
                
            const { data, error } = await query.single();
            
            if (error) {
                if (error.code === 'PGRST116') {
                    throw new NotFoundError(`Digital twin not found: ${twinId}`);
                }
                throw new DatabaseError(`Failed to get digital twin: ${error.message}`);
            }
            
            // Cache result
            if (this.config.enableCaching) {
                this.cache.set(cacheKey, {
                    data,
                    timestamp: Date.now()
                });
            }
            
            return data;
        } catch (error) {
            this.logger.error('Error getting digital twin', { 
                twinId, 
                error: error.message 
            });
            throw error;
        }
    }
    
    /**
     * Update digital twin
     * @param {string} twinId - Digital twin ID
     * @param {Object} updates - Update data
     * @returns {Promise<Object>} Updated digital twin
     */
    async updateDigitalTwin(twinId, updates) {
        try {
            const { data, error } = await this.supabase
                .from('platform.digital_twins')
                .update(updates)
                .eq('id', twinId)
                .select()
                .single();
                
            if (error) {
                if (error.code === 'PGRST116') {
                    throw new NotFoundError(`Digital twin not found: ${twinId}`);
                }
                throw new DatabaseError(`Failed to update digital twin: ${error.message}`);
            }
            
            this.logger.info('Digital twin updated', { 
                twinId: data.id,
                organizationId: data.organization_id
            });
            
            // Clear cache
            this.clearCacheForOrganization(data.organization_id);
            this.cache.delete(`digital_twin_${twinId}`);
            
            return data;
        } catch (error) {
            this.logger.error('Error updating digital twin', { 
                twinId, 
                error: error.message 
            });
            throw error;
        }
    }
    
    /**
     * Get digital twins for organization
     * @param {string} organizationId - Organization ID
     * @param {Object} options - Query options
     * @returns {Promise<Array>} Array of digital twins
     */
    async getOrganizationDigitalTwins(organizationId, options = {}) {
        try {
            let query = this.supabase
                .from('platform.digital_twins')
                .select('*')
                .eq('organization_id', organizationId);
                
            if (options.activeOnly) {
                query = query.eq('is_active', true);
            }
            
            if (options.limit) {
                query = query.limit(options.limit);
            }
            
            if (options.orderBy) {
                query = query.order(options.orderBy, { 
                    ascending: options.ascending !== false 
                });
            } else {
                query = query.order('created_at', { ascending: false });
            }
            
            const { data, error } = await query;
            
            if (error) {
                throw new DatabaseError(`Failed to get organization digital twins: ${error.message}`);
            }
            
            return data || [];
        } catch (error) {
            this.logger.error('Error getting organization digital twins', { 
                organizationId, 
                error: error.message 
            });
            throw error;
        }
    }
    
    /**
     * Create simulation result
     * @param {Object} simulationData - Simulation result data
     * @returns {Promise<Object>} Created simulation result
     */
    async createSimulationResult(simulationData) {
        try {
            this.validateSimulationData(simulationData);
            
            const { data, error } = await this.supabase
                .from('platform.simulation_results')
                .insert([simulationData])
                .select()
                .single();
                
            if (error) {
                throw new DatabaseError(`Failed to create simulation result: ${error.message}`);
            }
            
            this.logger.info('Simulation result created', { 
                simulationId: data.id,
                twinId: data.digital_twin_id,
                type: data.simulation_type
            });
            
            // Update twin's last simulation time and count
            await this.supabase
                .from('platform.digital_twins')
                .update({ 
                    last_simulation_at: new Date().toISOString(),
                    simulation_count: data.digital_twin_id // This will be incremented by trigger
                })
                .eq('id', data.digital_twin_id);
            
            // Clear relevant cache
            this.cache.delete(`digital_twin_${data.digital_twin_id}`);
            
            return data;
        } catch (error) {
            this.logger.error('Error creating simulation result', { error: error.message });
            throw error;
        }
    }
    
    /**
     * Get simulation results for digital twin
     * @param {string} twinId - Digital twin ID
     * @param {Object} options - Query options
     * @returns {Promise<Array>} Array of simulation results
     */
    async getSimulationResults(twinId, options = {}) {
        try {
            let query = this.supabase
                .from('platform.simulation_results')
                .select('*')
                .eq('digital_twin_id', twinId);
                
            if (options.simulationType) {
                query = query.eq('simulation_type', options.simulationType);
            }
            
            if (options.successOnly) {
                query = query.eq('success', true);
            }
            
            if (options.limit) {
                query = query.limit(options.limit);
            }
            
            query = query.order('created_at', { ascending: false });
            
            const { data, error } = await query;
            
            if (error) {
                throw new DatabaseError(`Failed to get simulation results: ${error.message}`);
            }
            
            return data || [];
        } catch (error) {
            this.logger.error('Error getting simulation results', { 
                twinId, 
                error: error.message 
            });
            throw error;
        }
    }
    
    /**
     * Record organization analytics
     * @param {Object} analyticsData - Analytics data
     * @returns {Promise<Object>} Created analytics record
     */
    async recordOrganizationAnalytics(analyticsData) {
        try {
            const { data, error } = await this.supabase
                .from('platform.organization_analytics')
                .insert([analyticsData])
                .select()
                .single();
                
            if (error) {
                throw new DatabaseError(`Failed to record analytics: ${error.message}`);
            }
            
            return data;
        } catch (error) {
            this.logger.error('Error recording organization analytics', { 
                error: error.message 
            });
            throw error;
        }
    }
    
    /**
     * Get organization analytics
     * @param {string} organizationId - Organization ID
     * @param {Object} options - Query options
     * @returns {Promise<Array>} Analytics data
     */
    async getOrganizationAnalytics(organizationId, options = {}) {
        try {
            let query = this.supabase
                .from('platform.organization_analytics')
                .select('*')
                .eq('organization_id', organizationId);
                
            if (options.startDate) {
                query = query.gte('date_recorded', options.startDate);
            }
            
            if (options.endDate) {
                query = query.lte('date_recorded', options.endDate);
            }
            
            if (options.periodType) {
                query = query.eq('period_type', options.periodType);
            }
            
            query = query.order('date_recorded', { ascending: false });
            
            if (options.limit) {
                query = query.limit(options.limit);
            }
            
            const { data, error } = await query;
            
            if (error) {
                throw new DatabaseError(`Failed to get organization analytics: ${error.message}`);
            }
            
            return data || [];
        } catch (error) {
            this.logger.error('Error getting organization analytics', { 
                organizationId, 
                error: error.message 
            });
            throw error;
        }
    }
    
    /**
     * Setup realtime subscriptions
     * @private
     * @async
     */
    async setupRealtimeSubscriptions() {
        try {
            // Subscribe to digital twins changes
            const twinSubscription = this.supabase
                .channel('digital_twins_changes')
                .on('postgres_changes', {
                    event: '*',
                    schema: 'platform',
                    table: 'digital_twins'
                }, (payload) => {
                    this.handleRealtimeUpdate('digital_twins', payload);
                })
                .subscribe();
                
            this.subscriptions.set('digital_twins', twinSubscription);
            
            // Subscribe to simulation results changes
            const simulationSubscription = this.supabase
                .channel('simulation_results_changes')
                .on('postgres_changes', {
                    event: '*',
                    schema: 'platform', 
                    table: 'simulation_results'
                }, (payload) => {
                    this.handleRealtimeUpdate('simulation_results', payload);
                })
                .subscribe();
                
            this.subscriptions.set('simulation_results', simulationSubscription);
            
            this.logger.info('Realtime subscriptions setup completed');
        } catch (error) {
            this.logger.error('Failed to setup realtime subscriptions', { 
                error: error.message 
            });
        }
    }
    
    /**
     * Handle realtime updates
     * @private
     * @param {string} table - Table name
     * @param {Object} payload - Update payload
     */
    handleRealtimeUpdate(table, payload) {
        const { eventType, new: newRecord, old: oldRecord } = payload;
        
        this.logger.debug('Received realtime update', { 
            table, 
            eventType, 
            recordId: newRecord?.id || oldRecord?.id 
        });
        
        // Clear relevant cache entries
        if (table === 'digital_twins') {
            const twinId = newRecord?.id || oldRecord?.id;
            const organizationId = newRecord?.organization_id || oldRecord?.organization_id;
            
            this.cache.delete(`digital_twin_${twinId}`);
            if (organizationId) {
                this.clearCacheForOrganization(organizationId);
            }
        }
        
        // Emit events for external listeners
        this.emit?.('realtimeUpdate', { table, eventType, newRecord, oldRecord });
    }
    
    /**
     * Validate organization data
     * @private
     * @param {Object} data - Organization data to validate
     */
    validateOrganizationData(data) {
        if (!data.organization_id) {
            throw new ValidationError('Organization ID is required');
        }
        
        if (!data.display_name || data.display_name.length < 2) {
            throw new ValidationError('Display name must be at least 2 characters');
        }
        
        if (data.slug && !/^[a-z0-9-]+$/.test(data.slug)) {
            throw new ValidationError('Slug must contain only lowercase letters, numbers, and hyphens');
        }
    }
    
    /**
     * Validate digital twin data
     * @private
     * @param {Object} data - Digital twin data to validate
     */
    validateDigitalTwinData(data) {
        if (!data.organization_id) {
            throw new ValidationError('Organization ID is required');
        }
        
        if (!data.twin_name || data.twin_name.length < 3) {
            throw new ValidationError('Twin name must be at least 3 characters');
        }
        
        if (typeof data.structure_data !== 'object') {
            throw new ValidationError('Structure data must be an object');
        }
    }
    
    /**
     * Validate simulation data
     * @private
     * @param {Object} data - Simulation data to validate
     */
    validateSimulationData(data) {
        if (!data.digital_twin_id) {
            throw new ValidationError('Digital twin ID is required');
        }
        
        if (!data.organization_id) {
            throw new ValidationError('Organization ID is required');
        }
        
        if (!data.simulation_type) {
            throw new ValidationError('Simulation type is required');
        }
        
        if (typeof data.results !== 'object') {
            throw new ValidationError('Results must be an object');
        }
    }
    
    /**
     * Clear cache for organization
     * @private
     * @param {string} organizationId - Organization ID
     */
    clearCacheForOrganization(organizationId) {
        const keysToDelete = [];
        for (const [key] of this.cache) {
            if (key.includes(organizationId)) {
                keysToDelete.push(key);
            }
        }
        keysToDelete.forEach(key => this.cache.delete(key));
    }
    
    /**
     * Get adapter status
     * @returns {Object} Adapter status
     */
    getStatus() {
        return {
            isInitialized: this.isInitialized,
            cacheSize: this.cache.size,
            subscriptions: Array.from(this.subscriptions.keys()),
            config: {
                enableRealtime: this.config.enableRealtime,
                enableCaching: this.config.enableCaching,
                cacheTimeout: this.config.cacheTimeout
            }
        };
    }
    
    /**
     * Cleanup and shutdown
     * @async
     */
    async shutdown() {
        try {
            this.logger.info('Shutting down Supabase adapter...');
            
            // Unsubscribe from realtime channels
            for (const [name, subscription] of this.subscriptions) {
                await subscription.unsubscribe();
                this.logger.debug(`Unsubscribed from ${name} channel`);
            }
            
            // Clear cache
            this.cache.clear();
            
            // Clear subscriptions
            this.subscriptions.clear();
            
            this.isInitialized = false;
            this.logger.info('Supabase adapter shutdown completed');
        } catch (error) {
            this.logger.error('Error during shutdown', { error: error.message });
        }
    }
}

export default DigitalTwinSupabaseAdapter;