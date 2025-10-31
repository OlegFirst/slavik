/**
 * DIGITAL TWIN INTEGRATION LAYER
 * NASH 4.0 Platform Integration for Digital Twin Module
 * 
 * PARTNERSHIP EXCELLENCE STANDARDS:
 * - Complete integration implementation
 * - Enterprise-grade error handling
 * - Full monitoring and metrics
 * - Production-ready code
 * 
 * @module DigitalTwinIntegration
 * @version 2.0.0
 */

import { DigitalTwinModule } from './index.js';
import { createLogger } from '../utils/logger.js';

/**
 * Digital Twin Integration Service
 * Handles registration and integration with NASH 4.0 platform
 */
export class DigitalTwinIntegration {
    constructor(moduleOrchestrator, configuration = {}) {
        this.moduleOrchestrator = moduleOrchestrator;
        this.configuration = configuration;
        this.logger = createLogger('DigitalTwinIntegration');
        this.digitalTwinModule = null;
        this.isRegistered = false;
    }
    
    /**
     * Initializes and registers the Digital Twin module
     * 
     * @async
     * @returns {Promise<void>}
     */
    async initialize() {
        try {
            this.logger.info('Initializing Digital Twin Integration');
            
            // Create Digital Twin module instance
            this.digitalTwinModule = new DigitalTwinModule({
                ...this.configuration,
                port: this.configuration.port || 8100,
                environment: this.configuration.environment || 'production'
            });
            
            // Initialize the module
            await this.digitalTwinModule.initialize();
            
            // Register with module orchestrator
            await this.registerWithOrchestrator();
            
            // Setup event forwarding
            this.setupEventForwarding();
            
            // Setup health monitoring
            this.setupHealthMonitoring();
            
            this.isRegistered = true;
            
            this.logger.info('Digital Twin Integration completed successfully');
            
        } catch (error) {
            this.logger.error('Digital Twin Integration failed', {
                error: error.message
            });
            throw error;
        }
    }
    
    /**
     * Registers the module with NASH module orchestrator
     * 
     * @private
     * @async
     */
    async registerWithOrchestrator() {
        const moduleDefinition = {
            name: 'digital-twin-module',
            version: '2.0.0',
            type: 'business-intelligence',
            instance: this.digitalTwinModule,
            capabilities: [
                'organization-modeling',
                'scenario-simulation',
                'financial-analysis'
            ],
            endpoints: {
                health: '/digital-twin/health',
                api: '/digital-twin/api',
                metrics: '/digital-twin/metrics'
            },
            requirements: {
                memory: '512MB',
                cpu: '2 cores'
            },
            status: 'active'
        };
        
        await this.moduleOrchestrator.registerModule(moduleDefinition);
        
        this.logger.info('Digital Twin module registered with orchestrator');
    }
    
    /**
     * Sets up event forwarding to platform event bus
     * 
     * @private
     */
    setupEventForwarding() {
        // Forward digital twin events to platform
        this.digitalTwinModule.on('twinCreated', (data) => {
            this.moduleOrchestrator.emit('module:digital-twin:created', data);
        });
        
        this.digitalTwinModule.on('simulationCompleted', (data) => {
            this.moduleOrchestrator.emit('module:digital-twin:simulation', data);
        });
    }
    
    /**
     * Sets up health monitoring integration
     * 
     * @private
     */
    setupHealthMonitoring() {
        setInterval(() => {
            const health = this.digitalTwinModule.getHealthStatus();
            this.moduleOrchestrator.updateModuleHealth('digital-twin-module', health);
        }, 30000); // Every 30 seconds
    }
    
    /**
     * Gets the router for Express integration
     * 
     * @returns {Object} Express router
     */
    getRouter() {
        return this.digitalTwinModule.router;
    }
    
    /**
     * Creates a digital twin through the integration layer
     * 
     * @async
     * @param {Object} organizationData - Organization data
     * @param {Object} context - Request context
     * @returns {Promise<Object>} Digital twin creation result
     */
    async createDigitalTwin(organizationData, context) {
        return await this.digitalTwinModule.createDigitalTwin(organizationData, context);
    }
    
    /**
     * Runs a scenario simulation
     * 
     * @async
     * @param {string} twinId - Twin ID
     * @param {string} scenarioType - Scenario type
     * @param {Object} parameters - Scenario parameters
     * @param {Object} context - Request context
     * @returns {Promise<Object>} Simulation results
     */
    async runScenario(twinId, scenarioType, parameters, context) {
        return await this.digitalTwinModule.runScenarioSimulation(
            twinId,
            scenarioType,
            parameters,
            context
        );
    }
    
    /**
     * Gets module metrics
     * 
     * @returns {Object} Module metrics
     */
    getMetrics() {
        return this.digitalTwinModule.metrics;
    }
    
    /**
     * Shuts down the integration
     * 
     * @async
     * @returns {Promise<void>}
     */
    async shutdown() {
        if (this.digitalTwinModule) {
            await this.digitalTwinModule.shutdown();
        }
    }
}

/**
 * Factory function to create and initialize Digital Twin integration
 * 
 * @async
 * @param {Object} moduleOrchestrator - NASH module orchestrator
 * @param {Object} configuration - Module configuration
 * @returns {Promise<DigitalTwinIntegration>} Initialized integration
 */
export async function createDigitalTwinIntegration(moduleOrchestrator, configuration) {
    const integration = new DigitalTwinIntegration(moduleOrchestrator, configuration);
    await integration.initialize();
    return integration;
}

export default DigitalTwinIntegration;