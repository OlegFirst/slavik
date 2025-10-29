/**
 * DIGITAL TWIN MODULE TEST SUITE
 * Comprehensive testing for Digital Twin Module
 * 
 * @module DigitalTwinTest
 * @version 2.0.0
 */

import { DigitalTwinModule } from './index.js';
import { SimulationEngine } from './simulation-engine.js';
import { createLogger } from '../utils/logger.js';

const logger = createLogger('DigitalTwinTest');

/**
 * Test runner for Digital Twin Module
 */
async function runTests() {
    logger.info('Starting Digital Twin Module tests');
    
    try {
        // Test 1: Module initialization
        logger.info('Test 1: Module initialization');
        const module = new DigitalTwinModule({
            environment: 'test',
            port: 8101
        });
        
        await module.initialize();
        console.log('✓ Module initialized successfully');
        
        // Test 2: Create digital twin
        logger.info('Test 2: Creating digital twin');
        const organizationData = {
            organizationId: 'test_org_001',
            name: 'Test NPO Foundation',
            mission: 'Empowering communities through technology',
            size: 50,
            annualBudget: 2000000,
            departments: [
                {
                    name: 'Administration',
                    staff_count: 10,
                    budget_allocation: 400000,
                    responsibilities: ['Management', 'HR', 'Finance'],
                    dependencies: []
                },
                {
                    name: 'Programs',
                    staff_count: 25,
                    budget_allocation: 1000000,
                    responsibilities: ['Service delivery', 'Community outreach'],
                    dependencies: ['Administration']
                },
                {
                    name: 'Fundraising',
                    staff_count: 10,
                    budget_allocation: 300000,
                    responsibilities: ['Donor relations', 'Grant writing'],
                    dependencies: ['Administration']
                },
                {
                    name: 'Technology',
                    staff_count: 5,
                    budget_allocation: 300000,
                    responsibilities: ['IT support', 'Systems management'],
                    dependencies: ['Administration']
                }
            ],
            processes: [
                { name: 'Donor management', automated: false },
                { name: 'Financial reporting', automated: true },
                { name: 'Volunteer coordination', automated: false },
                { name: 'Program tracking', automated: true },
                { name: 'Grant applications', automated: false }
            ],
            technologyStack: ['CRM', 'Email', 'Basic accounting', 'Website']
        };
        
        const context = {
            userId: 'test_user',
            organizationId: 'test_org',
            permissions: { create: true, read: true, update: true }
        };
        
        const twinResult = await module.createDigitalTwin(organizationData, context);
        console.log('✓ Digital twin created:', {
            twinId: twinResult.twinId,
            healthScore: twinResult.healthScore,
            maturityLevel: twinResult.maturityLevel
        });
        
        // Test 3: Run automation scenario
        logger.info('Test 3: Running automation scenario');
        const automationResult = await module.runScenarioSimulation(
            twinResult.twinId,
            'automation',
            {
                investment: 75000,
                scope: 'full',
                timeline: 12
            },
            context
        );
        
        console.log('✓ Automation scenario completed:', {
            roi: automationResult.results.financial_impact.roi_percentage,
            payback: automationResult.results.financial_impact.payback_months,
            efficiency: automationResult.results.operational_impact.efficiency_gain_percentage
        });
        
        // Test 4: Run crisis scenario
        logger.info('Test 4: Running crisis scenario');
        const crisisResult = await module.runScenarioSimulation(
            twinResult.twinId,
            'crisis',
            {
                type: 'funding_loss',
                severity: 0.3,
                duration: 12,
                reserves: 250000
            },
            context
        );
        
        console.log('✓ Crisis scenario completed:', {
            survivalMonths: crisisResult.results.survival_analysis.survival_months,
            recoveryPotential: crisisResult.results.recovery_plan.total_recovery_potential
        });
        
        // Test 5: Simulation engine
        logger.info('Test 5: Testing simulation engine');
        const engine = new SimulationEngine();
        
        const monteCarloResult = await engine.monteCarloSimulation({
            iterations: 100,
            baseValue: 100000,
            volatility: 0.2
        });
        
        console.log('✓ Monte Carlo simulation completed:', {
            mean: monteCarloResult.mean,
            confidence: monteCarloResult.confidenceInterval
        });
        
        // Test 6: ROI calculation with uncertainty
        logger.info('Test 6: ROI with uncertainty');
        const roiResult = await engine.calculateROIWithUncertainty({
            costs: 100000,
            benefits: 150000,
            timeline: 3,
            discountRate: 0.1
        });
        
        console.log('✓ ROI analysis completed:', {
            expectedNPV: roiResult.expectedNPV,
            probabilityOfSuccess: roiResult.probabilityOfSuccess
        });
        
        // Test 7: Health status
        logger.info('Test 7: Checking health status');
        const health = module.getHealthStatus();
        console.log('✓ Health status:', health);
        
        // Test 8: Metrics
        logger.info('Test 8: Getting metrics');
        const metrics = module.metrics;
        console.log('✓ Metrics:', {
            totalTwins: metrics.totalTwins,
            completedScenarios: metrics.completedScenarios,
            averageSimulationTime: metrics.averageSimulationTime
        });
        
        // Cleanup
        await module.shutdown();
        await engine.shutdown();
        
        logger.info('All tests completed successfully!');
        console.log('\n[SUCCESS] All tests passed!');
        
    } catch (error) {
        logger.error('Test failed:', error);
        console.error('[ERROR] Test failed:', error.message);
        process.exit(1);
    }
}

// Run tests
runTests().catch(console.error);