/**
 * Supabase Integration Module
 * Complete integration with Supabase for Digital Twin Standalone
 * 
 * @module SupabaseIntegration
 * @version 2.0.0
 */

import { createClient } from '@supabase/supabase-js';
import { EventEmitter } from 'events';

export class SupabaseIntegration extends EventEmitter {
    constructor() {
        super();
        this.client = null;
        this.realtimeSubscriptions = new Map();
        this.initialized = false;
    }

    /**
     * Initialize Supabase client
     */
    async initialize() {
        try {
            const supabaseUrl = process.env.SUPABASE_URL;
            const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.SUPABASE_ANON_KEY;

            if (!supabaseUrl || !supabaseKey) {
                throw new Error('Supabase credentials not configured');
            }

            this.client = createClient(supabaseUrl, supabaseKey, {
                auth: {
                    autoRefreshToken: true,
                    persistSession: true,
                    detectSessionInUrl: true
                },
                db: {
                    schema: 'public'
                },
                realtime: {
                    params: {
                        eventsPerSecond: 10
                    }
                }
            });

            // Test connection
            const { error } = await this.client.from('organizations').select('count').limit(1);
            if (error && error.code !== 'PGRST116') { // PGRST116 = no rows returned
                throw error;
            }

            this.initialized = true;
            this.emit('connected');
            console.log('Supabase connection established');
            
            return true;
        } catch (error) {
            console.error('Supabase initialization failed:', error);
            this.emit('error', error);
            throw error;
        }
    }

    /**
     * Organization operations
     */
    async createOrganization(data) {
        const { data: org, error } = await this.client
            .from('organizations')
            .insert({
                ...data,
                created_at: new Date().toISOString(),
                updated_at: new Date().toISOString()
            })
            .select()
            .single();

        if (error) throw error;
        return org;
    }

    async getOrganization(id) {
        const { data, error } = await this.client
            .from('organizations')
            .select(`
                *,
                digital_twins (*),
                departments (*)
            `)
            .eq('id', id)
            .single();

        if (error) throw error;
        return data;
    }

    async updateOrganization(id, updates) {
        const { data, error } = await this.client
            .from('organizations')
            .update({
                ...updates,
                updated_at: new Date().toISOString()
            })
            .eq('id', id)
            .select()
            .single();

        if (error) throw error;
        return data;
    }

    async listOrganizations(filters = {}) {
        let query = this.client.from('organizations').select('*');

        if (filters.type) {
            query = query.eq('type', filters.type);
        }
        if (filters.isActive !== undefined) {
            query = query.eq('is_active', filters.isActive);
        }
        if (filters.limit) {
            query = query.limit(filters.limit);
        }

        const { data, error } = await query.order('created_at', { ascending: false });
        if (error) throw error;
        return data;
    }

    /**
     * Digital Twin operations
     */
    async createDigitalTwin(data) {
        const { data: twin, error } = await this.client
            .from('digital_twins')
            .insert({
                ...data,
                created_at: new Date().toISOString(),
                updated_at: new Date().toISOString()
            })
            .select()
            .single();

        if (error) throw error;
        return twin;
    }

    async getDigitalTwin(id) {
        const { data, error } = await this.client
            .from('digital_twins')
            .select(`
                *,
                organizations (*),
                simulations (
                    *,
                    ORDER BY created_at DESC
                    LIMIT 10
                ),
                metrics (
                    *,
                    ORDER BY timestamp DESC
                    LIMIT 100
                )
            `)
            .eq('id', id)
            .single();

        if (error) throw error;
        return data;
    }

    async updateDigitalTwin(id, updates) {
        const { data, error } = await this.client
            .from('digital_twins')
            .update({
                ...updates,
                updated_at: new Date().toISOString()
            })
            .eq('id', id)
            .select()
            .single();

        if (error) throw error;
        return data;
    }

    async listDigitalTwins(filters = {}) {
        let query = this.client.from('digital_twins').select('*');

        if (filters.organizationId) {
            query = query.eq('organization_id', filters.organizationId);
        }
        if (filters.isActive !== undefined) {
            query = query.eq('is_active', filters.isActive);
        }

        const { data, error } = await query.order('created_at', { ascending: false });
        if (error) throw error;
        return data;
    }

    /**
     * Simulation operations
     */
    async createSimulation(data) {
        const simulationId = `sim_${Date.now()}_${Math.random().toString(36).substring(7)}`;
        
        const { data: simulation, error } = await this.client
            .from('simulations')
            .insert({
                simulation_id: simulationId,
                ...data,
                status: 'pending',
                created_at: new Date().toISOString()
            })
            .select()
            .single();

        if (error) throw error;
        return simulation;
    }

    async runSimulation(twinId, scenario, parameters = {}) {
        // Call Edge Function for simulation
        const { data, error } = await this.client.functions.invoke('simulate', {
            body: {
                twinId,
                scenario,
                parameters
            }
        });

        if (error) throw error;
        return data;
    }

    async getSimulation(id) {
        const { data, error } = await this.client
            .from('simulations')
            .select('*')
            .eq('id', id)
            .single();

        if (error) throw error;
        return data;
    }

    async listSimulations(twinId, limit = 10) {
        const { data, error } = await this.client
            .from('simulations')
            .select('*')
            .eq('twin_id', twinId)
            .order('created_at', { ascending: false })
            .limit(limit);

        if (error) throw error;
        return data;
    }

    /**
     * Metrics operations
     */
    async recordMetric(data) {
        const { error } = await this.client
            .from('metrics')
            .insert({
                ...data,
                timestamp: new Date().toISOString(),
                created_at: new Date().toISOString()
            });

        if (error) throw error;
        return true;
    }

    async recordMetrics(metrics) {
        const metricsData = metrics.map(m => ({
            ...m,
            timestamp: new Date().toISOString(),
            created_at: new Date().toISOString()
        }));

        const { error } = await this.client
            .from('metrics')
            .insert(metricsData);

        if (error) throw error;
        return true;
    }

    async getMetrics(twinId, filters = {}) {
        let query = this.client
            .from('metrics')
            .select('*')
            .eq('twin_id', twinId);

        if (filters.metricType) {
            query = query.eq('metric_type', filters.metricType);
        }
        if (filters.startDate) {
            query = query.gte('timestamp', filters.startDate);
        }
        if (filters.endDate) {
            query = query.lte('timestamp', filters.endDate);
        }
        if (filters.isCritical !== undefined) {
            query = query.eq('is_critical', filters.isCritical);
        }

        const limit = filters.limit || 100;
        const { data, error } = await query
            .order('timestamp', { ascending: false })
            .limit(limit);

        if (error) throw error;
        return data;
    }

    async getLatestMetrics(twinId) {
        const { data, error } = await this.client.rpc('get_latest_metrics', {
            p_twin_id: twinId,
            p_limit: 100
        });

        if (error) throw error;
        return data;
    }

    /**
     * Prediction operations
     */
    async createPrediction(twinId, predictionType, parameters = {}) {
        // Call Edge Function for prediction
        const { data, error } = await this.client.functions.invoke('predict', {
            body: {
                twinId,
                predictionType,
                ...parameters
            }
        });

        if (error) throw error;
        return data;
    }

    async getPredictions(twinId, filters = {}) {
        let query = this.client
            .from('predictions')
            .select('*')
            .eq('twin_id', twinId);

        if (filters.predictionType) {
            query = query.eq('prediction_type', filters.predictionType);
        }
        if (filters.targetDate) {
            query = query.eq('target_date', filters.targetDate);
        }

        const { data, error } = await query
            .order('created_at', { ascending: false })
            .limit(filters.limit || 10);

        if (error) throw error;
        return data;
    }

    /**
     * Report operations
     */
    async generateReport(twinId, reportType, format = 'json') {
        const { data: twin, error: twinError } = await this.getDigitalTwin(twinId);
        if (twinError) throw twinError;

        const { data: metrics } = await this.getLatestMetrics(twinId);
        const { data: simulations } = await this.listSimulations(twinId, 5);
        const { data: predictions } = await this.getPredictions(twinId, { limit: 5 });

        const reportContent = {
            twin,
            metrics,
            simulations,
            predictions,
            generatedAt: new Date().toISOString()
        };

        const { data: report, error } = await this.client
            .from('reports')
            .insert({
                twin_id: twinId,
                report_type: reportType,
                title: `${reportType} Report - ${new Date().toLocaleDateString()}`,
                content: reportContent,
                format,
                generated_at: new Date().toISOString()
            })
            .select()
            .single();

        if (error) throw error;
        return report;
    }

    async getReport(id) {
        const { data, error } = await this.client
            .from('reports')
            .select('*')
            .eq('id', id)
            .single();

        if (error) throw error;
        return data;
    }

    async listReports(twinId, limit = 10) {
        const { data, error } = await this.client
            .from('reports')
            .select('*')
            .eq('twin_id', twinId)
            .order('generated_at', { ascending: false })
            .limit(limit);

        if (error) throw error;
        return data;
    }

    /**
     * Real-time subscriptions
     */
    subscribeToTwinUpdates(twinId, callback) {
        const subscription = this.client
            .channel(`twin-${twinId}`)
            .on(
                'postgres_changes',
                {
                    event: '*',
                    schema: 'public',
                    table: 'digital_twins',
                    filter: `id=eq.${twinId}`
                },
                (payload) => {
                    callback(payload);
                }
            )
            .subscribe();

        this.realtimeSubscriptions.set(`twin-${twinId}`, subscription);
        return subscription;
    }

    subscribeToMetrics(twinId, callback) {
        const subscription = this.client
            .channel(`metrics-${twinId}`)
            .on(
                'postgres_changes',
                {
                    event: 'INSERT',
                    schema: 'public',
                    table: 'metrics',
                    filter: `twin_id=eq.${twinId}`
                },
                (payload) => {
                    callback(payload.new);
                }
            )
            .subscribe();

        this.realtimeSubscriptions.set(`metrics-${twinId}`, subscription);
        return subscription;
    }

    subscribeToSimulations(twinId, callback) {
        const subscription = this.client
            .channel(`simulations-${twinId}`)
            .on(
                'postgres_changes',
                {
                    event: '*',
                    schema: 'public',
                    table: 'simulations',
                    filter: `twin_id=eq.${twinId}`
                },
                (payload) => {
                    callback(payload);
                }
            )
            .subscribe();

        this.realtimeSubscriptions.set(`simulations-${twinId}`, subscription);
        return subscription;
    }

    unsubscribe(channelName) {
        const subscription = this.realtimeSubscriptions.get(channelName);
        if (subscription) {
            subscription.unsubscribe();
            this.realtimeSubscriptions.delete(channelName);
        }
    }

    unsubscribeAll() {
        for (const [name, subscription] of this.realtimeSubscriptions) {
            subscription.unsubscribe();
        }
        this.realtimeSubscriptions.clear();
    }

    /**
     * Audit logging
     */
    async logAudit(action, resourceType, resourceId, changes = null) {
        const { error } = await this.client
            .from('audit_logs')
            .insert({
                action,
                resource_type: resourceType,
                resource_id: resourceId,
                changes,
                created_at: new Date().toISOString()
            });

        if (error) {
            console.error('Audit log failed:', error);
        }
    }

    /**
     * Health check
     */
    async healthCheck() {
        try {
            const { data, error } = await this.client
                .from('organizations')
                .select('count')
                .limit(1);

            return {
                status: error ? 'unhealthy' : 'healthy',
                timestamp: new Date().toISOString(),
                error: error?.message
            };
        } catch (error) {
            return {
                status: 'unhealthy',
                timestamp: new Date().toISOString(),
                error: error.message
            };
        }
    }

    /**
     * Cleanup
     */
    async disconnect() {
        this.unsubscribeAll();
        this.initialized = false;
        this.emit('disconnected');
    }
}

// Export singleton instance
export const supabaseIntegration = new SupabaseIntegration();