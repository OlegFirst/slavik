/**
 * Simulation Router
 * Routes simulation experiments to appropriate engines/adapters
 */

import fetch from 'node-fetch';
import { createLogger } from '../utils/logger.js';
import { SimulationEngine } from './simulation-engine.js';
import { TheoryOfChangeEngine } from './theory-of-change-engine.js';
import { generateFallbackResult, checkAdapterAvailability } from './mocks/simulation-fallbacks.js';

const logger = createLogger('SimulationRouter');

// Adapter endpoints configuration
const ADAPTER_ENDPOINTS = {
    // External SEH adapters (now 4 with AnyLogic)
    simpy_queue: process.env.SIMPY_ADAPTER_URL || 'http://localhost:7001/run',
    mesa_abm: process.env.MESA_ADAPTER_URL || 'http://localhost:7002/run',
    epi_nowcasting_rt: process.env.EPINOW2_ADAPTER_URL || 'http://localhost:7003/run',
    anylogic_hybrid: process.env.ANYLOGIC_ADAPTER_URL || 'http://localhost:7004/run',
    
    // Internal Digital Twin scenarios
    automation: 'internal',
    crisis: 'internal',
    expansion: 'internal',
    integration: 'internal',
    
    // Internal simulation engines
    capacity_sweep: 'internal',
    bcm_outage: 'internal', 
    budget_optimization: 'internal',
    theory_of_change: 'internal',
    
    // Internal organizational scenarios
    digital_transformation: 'internal',
    ai_implementation: 'internal',
    cybersecurity: 'internal',
    compliance: 'internal',
    staff_training: 'internal',
    process_optimization: 'internal',
    stakeholder_engagement: 'internal',
    community_outreach: 'internal',
    resource_allocation: 'internal',
    capacity_building: 'internal',
    monitoring_evaluation: 'internal',
    knowledge_management: 'internal',
    innovation_research: 'internal',
    partnership_development: 'internal',
    sustainability_planning: 'internal',
    grant_management: 'internal',
    funding_diversification: 'internal',
    impact_assessment: 'internal'
};

export class SimulationRouter {
    constructor() {
        this.simEngine = new SimulationEngine();
        this.tocEngine = new TheoryOfChangeEngine();
    }
    
    /**
     * Route simulation request to appropriate engine
     */
    async runSimulation(experiment, params, options = {}) {
        logger.info(`Routing simulation: ${experiment}`);
        
        const endpoint = ADAPTER_ENDPOINTS[experiment];
        
        if (!endpoint) {
            throw new Error(`Unknown experiment type: ${experiment}`);
        }
        
        // Internal engines
        if (endpoint === 'internal') {
            return await this.runInternalSimulation(experiment, params, options);
        }
        
        // External adapters
        return await this.runExternalSimulation(experiment, endpoint, params, options);
    }
    
    /**
     * Run internal simulation
     */
    async runInternalSimulation(experiment, params, options) {
        switch (experiment) {
            case 'capacity_sweep':
                return await this.simEngine.runCapacitySweep({
                    ...params,
                    monte_carlo_runs: options.monte_carlo_runs || 200
                });
                
            case 'bcm_outage':
                return await this.simEngine.runBCMOutage({
                    ...params,
                    monte_carlo_runs: options.monte_carlo_runs || 200
                });
                
            case 'budget_optimization':
                return await this.simEngine.runBudgetOptimization(params);
                
            case 'theory_of_change':
                await this.tocEngine.loadFromTemplate(params.template || this.getDefaultToCTemplate());
                return await this.tocEngine.optimizePolicy({
                    objective: params.objective || 'maximize_outcome_per_cost',
                    budgetCap: params.budget_cap || 50000,
                    decisionVariables: params.decision_variables,
                    monteCarloRuns: options.monte_carlo_runs || 1000
                });
                
            // Digital Twin organizational scenarios
            case 'automation':
            case 'crisis':
            case 'expansion':
            case 'integration':
            case 'digital_transformation':
            case 'ai_implementation':
            case 'cybersecurity':
            case 'compliance':
            case 'staff_training':
            case 'process_optimization':
            case 'stakeholder_engagement':
            case 'community_outreach':
            case 'resource_allocation':
            case 'capacity_building':
            case 'monitoring_evaluation':
            case 'knowledge_management':
            case 'innovation_research':
            case 'partnership_development':
            case 'sustainability_planning':
            case 'grant_management':
            case 'funding_diversification':
            case 'impact_assessment':
                return await this.runDigitalTwinScenario(experiment, params, options);
                
            default:
                throw new Error(`Unknown internal experiment: ${experiment}`);
        }
    }
    
    /**
     * Run Digital Twin organizational scenario
     */
    async runDigitalTwinScenario(scenario, params, options) {
        // Import Digital Twin system dynamically to avoid circular dependencies
        const { DigitalTwinModule } = await import('./index.js');
        
        const digitalTwin = new DigitalTwinModule();
        
        // Create a mock organization for scenario simulation
        const mockOrganization = {
            id: params.organizationId || 'demo-org',
            name: params.organizationName || 'Demo Organization',
            type: params.orgType || 'npo',
            budget: params.budget || 100000,
            staff: params.staff || 25,
            processes: {
                total: params.totalProcesses || 50,
                automated: params.automatedProcesses || 10
            },
            ...params.organizationData
        };
        
        // Run scenario simulation
        const result = await digitalTwin.runScenarioSimulation(
            mockOrganization.id,
            scenario,
            params,
            { organization: mockOrganization }
        );
        
        // Convert to standard simulation format
        return {
            run_id: `dt_${scenario}_${Date.now()}`,
            experiment: scenario,
            best: {
                scenario: scenario,
                value: result.results?.roi || result.results?.score || 0,
                confidence: result.confidence || 0.8
            },
            frontier: [{
                scenario: 'baseline',
                value: 0,
                confidence: 1.0
            }, {
                scenario: 'optimized',
                value: result.results?.roi || result.results?.score || 0,
                confidence: result.confidence || 0.8
            }],
            explain: result.insights?.[0]?.insight || `Digital Twin scenario: ${scenario}`,
            metadata: {
                processingTime: result.processingTime,
                risks: result.risks,
                recommendations: result.recommendations,
                timeline: result.timeline
            }
        };
    }
    
    /**
     * Run external simulation via adapter
     */
    async runExternalSimulation(experiment, endpoint, params, options) {
        try {
            const payload = {
                experiment,
                params,
                monte_carlo_runs: options.monte_carlo_runs || 200
            };
            
            logger.info(`Calling external adapter: ${endpoint}`);
            
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${process.env.ADAPTER_API_KEY || ''}`
                },
                body: JSON.stringify(payload),
                timeout: 60000 // 60 second timeout
            });
            
            if (!response.ok) {
                const error = await response.text();
                throw new Error(`Adapter error: ${response.status} - ${error}`);
            }
            
            const result = await response.json();
            
            // Ensure standard format
            return this.normalizeResult(result, experiment);
            
        } catch (error) {
            logger.error(`External simulation failed: ${error.message}`);
            
            // Fallback to mock if adapter unavailable
            if (options.allowFallback !== false) {
                logger.warn(`Using fallback mode for ${experiment}`);
                return generateFallbackResult(experiment, params);
            }
            
            throw error;
        }
    }
    
    /**
     * Normalize adapter response to standard format
     */
    normalizeResult(result, experiment) {
        // Already in standard format
        if (result.run_id && result.best && result.frontier) {
            return result;
        }
        
        // Convert to standard format
        return {
            run_id: result.run_id || `${experiment}_${Date.now()}`,
            experiment: experiment,
            best: result.best || result.optimal || {},
            frontier: result.frontier || [],
            explain: result.explain || result.explanation || 'Simulation completed',
            metadata: result.metadata || {}
        };
    }
    
    
    /**
     * Get default Theory of Change template
     */
    getDefaultToCTemplate() {
        return {
            nodes: [
                { id: 'need_access', type: 'problem', label: 'Low Service Access' },
                { id: 'awareness', type: 'mediator', label: 'Awareness' },
                { id: 'uptake', type: 'mediator', label: 'Uptake' },
                { id: 'adherence', type: 'mediator', label: 'Adherence' },
                { id: 'outcome_cov', type: 'outcome', label: 'Coverage' },
                { id: 'impact_morb', type: 'impact', label: 'Reduced Morbidity' }
            ],
            edges: [
                { from: 'need_access', to: 'awareness', effect: 'negative', elasticity: -0.3 },
                { from: 'awareness', to: 'uptake', effect: 'positive', elasticity: 0.5 },
                { from: 'uptake', to: 'adherence', effect: 'positive', elasticity: 0.4 },
                { from: 'adherence', to: 'outcome_cov', effect: 'positive', elasticity: 0.6 },
                { from: 'outcome_cov', to: 'impact_morb', effect: 'negative', elasticity: -0.2 }
            ],
            interventions: [
                { id: 'outreach_sms', label: 'SMS outreach', targets: ['awareness'], cost_per_unit: 0.12, effect_size: 0.2 },
                { id: 'transport_vouchers', label: 'Transport vouchers', targets: ['uptake'], cost_per_unit: 2.50, effect_size: 0.35 },
                { id: 'counseling', label: 'Individual counseling', targets: ['adherence'], cost_per_unit: 3.80, effect_size: 0.25 }
            ],
            indicators: [
                { id: 'cov', node: 'outcome_cov', baseline: 0.52, target: 0.70 },
                { id: 'morb', node: 'impact_morb', baseline: 0.18, target: 0.15 }
            ]
        };
    }
    
    /**
     * Get available experiments
     */
    getAvailableExperiments() {
        return Object.keys(ADAPTER_ENDPOINTS).map(key => ({
            id: key,
            type: ADAPTER_ENDPOINTS[key] === 'internal' ? 'internal' : 'external',
            endpoint: ADAPTER_ENDPOINTS[key],
            available: true // Could check adapter health here
        }));
    }
}

export default SimulationRouter;