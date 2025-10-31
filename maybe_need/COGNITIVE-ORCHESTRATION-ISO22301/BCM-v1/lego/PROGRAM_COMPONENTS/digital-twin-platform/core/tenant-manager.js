/**
 * Tenant Manager - Production Multi-tenant Support
 * 
 * Поддерживает как standalone, так и multi-tenant режимы
 */

import { createLogger } from '../utils/logger.js';
import { EventEmitter } from 'events';

const logger = createLogger('TenantManager');

export class TenantManager extends EventEmitter {
    constructor(options = {}) {
        super();
        
        this.mode = options.mode || process.env.TENANT_MODE || 'standalone';
        this.tenants = new Map();
        this.tenantConfigs = new Map();
        this.resourceLimits = new Map();
        
        // Database adapter for persistent storage
        this.dbAdapter = options.dbAdapter || null;
        
        // Default resource limits
        this.defaultLimits = {
            maxOrganizations: this.mode === 'standalone' ? 1 : 100,
            maxSimulations: this.mode === 'standalone' ? 50 : 1000,
            maxStorageMB: this.mode === 'standalone' ? 100 : 1000,
            maxAPICallsPerMinute: this.mode === 'standalone' ? 100 : 500
        };
        
        logger.info(`TenantManager initialized in ${this.mode} mode`);
    }

    /**
     * Создать нового тенанта с полной конфигурацией
     */
    async createTenant(tenantId, data) {
        try {
            if (this.tenants.has(tenantId)) {
                throw new Error(`Tenant ${tenantId} already exists`);
            }

            const tenant = {
                id: tenantId,
                name: data.name,
                type: data.type || 'organization',
                status: 'active',
                plan: data.plan || 'basic',
                createdAt: new Date().toISOString(),
                updatedAt: new Date().toISOString(),
                settings: {
                    timezone: data.timezone || 'UTC',
                    language: data.language || 'en',
                    features: data.features || [],
                    ...data.settings
                },
                metadata: data.metadata || {},
                contacts: data.contacts || [],
                subscription: {
                    plan: data.plan || 'basic',
                    status: 'active',
                    startDate: new Date().toISOString(),
                    renewalDate: this.calculateRenewalDate(data.plan),
                    limits: this.calculateTenantLimits(data.plan)
                }
            };

            // Store in memory
            this.tenants.set(tenantId, tenant);
            this.resourceLimits.set(tenantId, tenant.subscription.limits);

            // Persist to database if available
            if (this.dbAdapter) {
                await this.dbAdapter.create('tenants', tenant);
            }

            this.emit('tenant:created', { tenantId, tenant });
            logger.info(`Tenant created: ${tenantId}`);

            return tenant;
        } catch (error) {
            logger.error(`Failed to create tenant ${tenantId}:`, error);
            throw error;
        }
    }

    /**
     * Получить тенанта с дополнительной информацией
     */
    async getTenant(tenantId) {
        let tenant = this.tenants.get(tenantId);
        
        // Load from database if not in memory
        if (!tenant && this.dbAdapter) {
            try {
                tenant = await this.dbAdapter.findById('tenants', tenantId);
                if (tenant) {
                    this.tenants.set(tenantId, tenant);
                    this.resourceLimits.set(tenantId, tenant.subscription?.limits || this.defaultLimits);
                }
            } catch (error) {
                logger.error(`Failed to load tenant ${tenantId} from database:`, error);
            }
        }

        return tenant;
    }

    /**
     * Обновить тенанта с валидацией
     */
    async updateTenant(tenantId, updates) {
        try {
            const tenant = await this.getTenant(tenantId);
            if (!tenant) {
                throw new Error(`Tenant ${tenantId} not found`);
            }

            // Validate updates
            if (updates.plan && updates.plan !== tenant.subscription.plan) {
                updates.subscription = {
                    ...tenant.subscription,
                    plan: updates.plan,
                    limits: this.calculateTenantLimits(updates.plan),
                    updatedAt: new Date().toISOString()
                };
            }

            const updatedTenant = {
                ...tenant,
                ...updates,
                updatedAt: new Date().toISOString()
            };

            this.tenants.set(tenantId, updatedTenant);
            this.resourceLimits.set(tenantId, updatedTenant.subscription.limits);

            // Persist to database
            if (this.dbAdapter) {
                await this.dbAdapter.update('tenants', tenantId, updatedTenant);
            }

            this.emit('tenant:updated', { tenantId, updates, tenant: updatedTenant });
            logger.info(`Tenant updated: ${tenantId}`);

            return updatedTenant;
        } catch (error) {
            logger.error(`Failed to update tenant ${tenantId}:`, error);
            throw error;
        }
    }

    /**
     * Удалить тенанта с очисткой ресурсов
     */
    async deleteTenant(tenantId) {
        try {
            const tenant = await this.getTenant(tenantId);
            if (!tenant) {
                return false;
            }

            // Cleanup resources
            this.tenants.delete(tenantId);
            this.resourceLimits.delete(tenantId);
            this.tenantConfigs.delete(tenantId);

            // Remove from database
            if (this.dbAdapter) {
                await this.dbAdapter.delete('tenants', tenantId);
            }

            this.emit('tenant:deleted', { tenantId, tenant });
            logger.info(`Tenant deleted: ${tenantId}`);

            return true;
        } catch (error) {
            logger.error(`Failed to delete tenant ${tenantId}:`, error);
            throw error;
        }
    }

    /**
     * Проверить лимиты ресурсов для тенанта
     */
    async checkResourceLimits(tenantId, resource, amount = 1) {
        const limits = this.resourceLimits.get(tenantId) || this.defaultLimits;
        const usage = await this.getCurrentUsage(tenantId);

        switch (resource) {
            case 'organizations':
                return usage.organizations + amount <= limits.maxOrganizations;
            case 'simulations':
                return usage.simulations + amount <= limits.maxSimulations;
            case 'storage':
                return usage.storageMB + amount <= limits.maxStorageMB;
            case 'api_calls':
                return usage.apiCallsThisMinute + amount <= limits.maxAPICallsPerMinute;
            default:
                return true;
        }
    }

    /**
     * Получить текущее использование ресурсов
     */
    async getCurrentUsage(tenantId) {
        // В реальной реализации это будет запрос к базе данных
        return {
            organizations: 0,
            simulations: 0,
            storageMB: 0,
            apiCallsThisMinute: 0
        };
    }

    /**
     * Рассчитать лимиты для плана подписки
     */
    calculateTenantLimits(plan) {
        const planLimits = {
            basic: {
                maxOrganizations: 1,
                maxSimulations: 50,
                maxStorageMB: 100,
                maxAPICallsPerMinute: 100
            },
            professional: {
                maxOrganizations: 10,
                maxSimulations: 500,
                maxStorageMB: 1000,
                maxAPICallsPerMinute: 500
            },
            enterprise: {
                maxOrganizations: 100,
                maxSimulations: 5000,
                maxStorageMB: 10000,
                maxAPICallsPerMinute: 2000
            }
        };

        return planLimits[plan] || planLimits.basic;
    }

    /**
     * Рассчитать дату продления подписки
     */
    calculateRenewalDate(plan) {
        const now = new Date();
        const renewalDate = new Date(now);
        renewalDate.setFullYear(renewalDate.getFullYear() + 1);
        return renewalDate.toISOString();
    }

    /**
     * Получить все тенанты (для администрирования)
     */
    async getAllTenants() {
        if (this.dbAdapter) {
            try {
                return await this.dbAdapter.findAll('tenants');
            } catch (error) {
                logger.error('Failed to load tenants from database:', error);
            }
        }
        
        return Array.from(this.tenants.values());
    }

    /**
     * Проверить статус тенанта
     */
    async getTenantStatus(tenantId) {
        const tenant = await this.getTenant(tenantId);
        if (!tenant) {
            return 'not_found';
        }

        // Проверить статус подписки
        if (tenant.subscription) {
            const renewalDate = new Date(tenant.subscription.renewalDate);
            if (renewalDate < new Date()) {
                return 'expired';
            }
        }

        return tenant.status || 'active';
    }

    /**
     * Получить конфигурацию для тенанта
     */
    getTenantConfig(tenantId) {
        return this.tenantConfigs.get(tenantId) || {
            features: [],
            limits: this.defaultLimits,
            settings: {}
        };
    }

    /**
     * Проверить является ли система standalone
     */
    isStandalone() {
        return this.mode === 'standalone';
    }

    /**
     * Получить статистику использования
     */
    async getUsageStats() {
        const stats = {
            totalTenants: this.tenants.size,
            activeTenants: 0,
            totalResources: {
                organizations: 0,
                simulations: 0,
                storage: 0
            }
        };

        for (const [tenantId, tenant] of this.tenants) {
            if (tenant.status === 'active') {
                stats.activeTenants++;
            }
            
            const usage = await this.getCurrentUsage(tenantId);
            stats.totalResources.organizations += usage.organizations;
            stats.totalResources.simulations += usage.simulations;
            stats.totalResources.storage += usage.storageMB;
        }

        return stats;
    }
}

export default TenantManager;