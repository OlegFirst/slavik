/**
 * SEH API Endpoints Implementation
 * Based on SEH OpenAPI v1 specification
 */

import express from 'express';
import { body, param, query, validationResult } from 'express-validator';
import { DigitalTwinDatabaseAdapter } from '../../infrastructure/database/database-adapter.js';
import { TheoryOfChangeEngine } from '../theory-of-change-engine.js';
import { SimulationEngine } from '../simulation-engine.js';
import { createLogger } from '../../utils/logger.js';

const router = express.Router();
const logger = createLogger('SEH-API');
const db = new DigitalTwinDatabaseAdapter();
const tocEngine = new TheoryOfChangeEngine();
const simEngine = new SimulationEngine();

// Middleware for validation errors
const handleValidationErrors = (req, res, next) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
        return res.status(400).json({ 
            error: 'Validation failed',
            details: errors.array() 
        });
    }
    next();
};

// ============================================
// MEASUREMENTS API
// ============================================

/**
 * POST /api/v1/measurements:batch
 * Batch import measurements with idempotency
 */
router.post('/api/v1/measurements:batch',
    [
        body('measurements').isArray().withMessage('Measurements must be an array'),
        body('measurements.*.indicator_id').notEmpty(),
        body('measurements.*.period_start').isISO8601(),
        body('measurements.*.period_end').isISO8601(),
        body('measurements.*.value').isNumeric(),
        body('idempotency_key').optional().isString()
    ],
    handleValidationErrors,
    async (req, res) => {
        try {
            const { measurements, idempotency_key } = req.body;
            
            // Check idempotency
            if (idempotency_key) {
                const existing = await db.query(
                    'SELECT id FROM batch_imports WHERE idempotency_key = $1',
                    [idempotency_key]
                );
                if (existing.length > 0) {
                    return res.status(200).json({
                        message: 'Batch already processed',
                        batch_id: existing[0].id,
                        count: 0
                    });
                }
            }
            
            // Process measurements
            const results = [];
            for (const measurement of measurements) {
                const result = await db.insert('measurements', {
                    ...measurement,
                    created_at: new Date().toISOString()
                });
                results.push(result);
                
                // Emit domain event
                await db.insert('domain_events', {
                    event_type: 'indicator.measured',
                    aggregate_id: result.id,
                    aggregate_type: 'measurement',
                    payload: measurement
                });
            }
            
            // Record batch import
            if (idempotency_key) {
                await db.insert('batch_imports', {
                    idempotency_key,
                    entity_type: 'measurements',
                    count: results.length,
                    created_at: new Date().toISOString()
                });
            }
            
            logger.info(`Batch imported ${results.length} measurements`);
            
            res.status(201).json({
                message: 'Measurements imported successfully',
                count: results.length,
                measurement_ids: results.map(r => r.id)
            });
            
        } catch (error) {
            logger.error('Batch measurement import failed:', error);
            res.status(500).json({ error: 'Internal server error' });
        }
    }
);

/**
 * GET /api/v1/indicators/{id}/measurements
 * Get measurements for an indicator
 */
router.get('/api/v1/indicators/:id/measurements',
    [
        param('id').isUUID(),
        query('from').optional().isISO8601(),
        query('to').optional().isISO8601(),
        query('limit').optional().isInt({ min: 1, max: 1000 })
    ],
    handleValidationErrors,
    async (req, res) => {
        try {
            const { id } = req.params;
            const { from, to, limit = 100 } = req.query;
            
            let query = 'SELECT * FROM measurements WHERE indicator_id = $1';
            const params = [id];
            
            if (from) {
                query += ' AND period_start >= $' + (params.length + 1);
                params.push(from);
            }
            
            if (to) {
                query += ' AND period_end <= $' + (params.length + 1);
                params.push(to);
            }
            
            query += ' ORDER BY period_start DESC LIMIT $' + (params.length + 1);
            params.push(limit);
            
            const measurements = await db.query(query, params);
            
            // Get indicator details
            const indicator = await db.getById('indicators', id);
            
            res.json({
                indicator,
                measurements,
                count: measurements.length
            });
            
        } catch (error) {
            logger.error('Failed to fetch measurements:', error);
            res.status(500).json({ error: 'Internal server error' });
        }
    }
);

// ============================================
// SIMULATION API
// ============================================

/**
 * POST /api/v1/sim/run
 * Run simulation experiment
 */
router.post('/api/v1/sim/run',
    [
        body('experiment').isIn(['capacity_sweep', 'routing_vrp', 'disbursement', 'bcm_outage']),
        body('params').isObject(),
        body('monte_carlo_runs').optional().isInt({ min: 1, max: 10000 })
    ],
    handleValidationErrors,
    async (req, res) => {
        try {
            const { experiment, params, monte_carlo_runs = 200 } = req.body;
            
            logger.info(`Running simulation: ${experiment}`);
            
            // Run simulation based on experiment type
            let result;
            switch (experiment) {
                case 'capacity_sweep':
                    result = await simEngine.runCapacitySweep({
                        ...params,
                        monte_carlo_runs
                    });
                    break;
                    
                case 'bcm_outage':
                    result = await simEngine.runBCMOutage({
                        ...params,
                        monte_carlo_runs
                    });
                    break;
                    
                case 'routing_vrp':
                    result = await simEngine.runRoutingVRP({
                        ...params,
                        monte_carlo_runs
                    });
                    break;
                    
                case 'disbursement':
                    result = await simEngine.runDisbursementOptimization({
                        ...params,
                        monte_carlo_runs
                    });
                    break;
                    
                default:
                    throw new Error('Unknown experiment type');
            }
            
            // Store simulation result
            const simulation = await db.insert('simulations', {
                scenario_type: experiment,
                parameters: params,
                results: result,
                status: 'completed',
                created_at: new Date().toISOString()
            });
            
            res.json({
                run_id: simulation.id,
                experiment,
                best: result.best,
                frontier: result.frontier || [],
                explain: result.explanation || 'Simulation completed successfully'
            });
            
        } catch (error) {
            logger.error('Simulation failed:', error);
            res.status(500).json({ error: 'Simulation failed', message: error.message });
        }
    }
);

// ============================================
// THEORY OF CHANGE API
// ============================================

/**
 * POST /api/v1/impact/optimize
 * Optimize ToC policy under budget constraints
 */
router.post('/api/v1/impact/optimize',
    [
        body('objective').isIn([
            'maximize_outcome_cov_per_cost',
            'maximize_coverage',
            'minimize_cost_per_beneficiary',
            'maximize_net_monetary_benefit'
        ]),
        body('budget_cap').isNumeric({ min: 0 }),
        body('decision_variables').isArray(),
        body('decision_variables.*.id').notEmpty(),
        body('decision_variables.*.min').isNumeric(),
        body('decision_variables.*.max').isNumeric(),
        body('decision_variables.*.step').isNumeric(),
        body('monte_carlo_runs').optional().isInt({ min: 100, max: 10000 })
    ],
    handleValidationErrors,
    async (req, res) => {
        try {
            const {
                objective,
                budget_cap,
                decision_variables,
                monte_carlo_runs = 1000
            } = req.body;
            
            logger.info(`Running ToC optimization: ${objective}`);
            
            // Load ToC template (could be from database or config)
            await tocEngine.loadFromTemplate({
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
            });
            
            // Run optimization
            const result = await tocEngine.optimizePolicy({
                objective,
                budgetCap: budget_cap,
                decisionVariables: decision_variables,
                monteCarloRuns: monte_carlo_runs
            });
            
            // Store optimization result
            await db.insert('predictions', {
                prediction_type: 'toc_optimization',
                parameters: req.body,
                predicted_value: result.coverage_forecast?.mean || 0,
                confidence_score: result.confidence || 0,
                metadata: result,
                created_at: new Date().toISOString()
            });
            
            res.json(result);
            
        } catch (error) {
            logger.error('ToC optimization failed:', error);
            res.status(500).json({ error: 'Optimization failed', message: error.message });
        }
    }
);

// ============================================
// GRANTS API
// ============================================

/**
 * GET /api/v1/grants/{id}/disbursements
 * Get disbursements for a grant
 */
router.get('/api/v1/grants/:id/disbursements',
    [
        param('id').isUUID(),
        query('status').optional().isIn(['pending', 'completed', 'cancelled'])
    ],
    handleValidationErrors,
    async (req, res) => {
        try {
            const { id } = req.params;
            const { status } = req.query;
            
            let query = 'SELECT * FROM disbursements WHERE grant_award_id = $1';
            const params = [id];
            
            if (status) {
                query += ' AND status = $2';
                params.push(status);
            }
            
            query += ' ORDER BY disbursement_date DESC';
            
            const disbursements = await db.query(query, params);
            
            // Calculate aggregates
            const total_disbursed = disbursements
                .filter(d => d.status === 'completed')
                .reduce((sum, d) => sum + parseFloat(d.amount), 0);
            
            const pending_amount = disbursements
                .filter(d => d.status === 'pending')
                .reduce((sum, d) => sum + parseFloat(d.amount), 0);
            
            res.json({
                grant_id: id,
                disbursements,
                summary: {
                    total_disbursed,
                    pending_amount,
                    count: disbursements.length
                }
            });
            
        } catch (error) {
            logger.error('Failed to fetch disbursements:', error);
            res.status(500).json({ error: 'Internal server error' });
        }
    }
);

// ============================================
// DASHBOARD API
// ============================================

/**
 * GET /api/v1/dashboards/{name}
 * Get dashboard data
 */
router.get('/api/v1/dashboards/:name',
    [
        param('name').isIn(['grant_burn_rate', 'outcome_vs_target', 'bcm_readiness'])
    ],
    handleValidationErrors,
    async (req, res) => {
        try {
            const { name } = req.params;
            
            let dashboardData;
            switch (name) {
                case 'grant_burn_rate':
                    dashboardData = await getDashboardGrantBurnRate();
                    break;
                    
                case 'outcome_vs_target':
                    dashboardData = await getDashboardOutcomeVsTarget();
                    break;
                    
                case 'bcm_readiness':
                    dashboardData = await getDashboardBCMReadiness();
                    break;
                    
                default:
                    throw new Error('Unknown dashboard');
            }
            
            res.json({
                dashboard: name,
                timestamp: new Date().toISOString(),
                data: dashboardData
            });
            
        } catch (error) {
            logger.error('Failed to fetch dashboard:', error);
            res.status(500).json({ error: 'Internal server error' });
        }
    }
);

// Dashboard data functions
async function getDashboardGrantBurnRate() {
    const grants = await db.query(`
        SELECT 
            ga.id,
            ga.awarded_amount,
            ga.award_period_start,
            ga.award_period_end,
            COALESCE(SUM(d.amount), 0) as total_disbursed,
            COUNT(d.id) as disbursement_count
        FROM grant_awards ga
        LEFT JOIN disbursements d ON d.grant_award_id = ga.id
        WHERE ga.status = 'active'
        GROUP BY ga.id
        LIMIT 10
    `);
    
    return {
        grants: grants.map(g => ({
            ...g,
            burn_rate: g.total_disbursed / g.awarded_amount,
            months_remaining: Math.max(0, 
                Math.floor((new Date(g.award_period_end) - new Date()) / (1000 * 60 * 60 * 24 * 30))
            )
        }))
    };
}

async function getDashboardOutcomeVsTarget() {
    const indicators = await db.query(`
        SELECT 
            i.id,
            i.name,
            t.target_value,
            m.value as actual_value,
            m.period_end
        FROM indicators i
        LEFT JOIN targets t ON t.indicator_id = i.id
        LEFT JOIN measurements m ON m.indicator_id = i.id
        WHERE t.period_end >= CURRENT_DATE
        ORDER BY m.period_end DESC
        LIMIT 3
    `);
    
    return {
        indicators: indicators.map(i => ({
            ...i,
            achievement_rate: i.actual_value / i.target_value,
            gap: i.target_value - i.actual_value
        }))
    };
}

async function getDashboardBCMReadiness() {
    const scenarios = await db.query(`
        SELECT 
            bs.id,
            bs.scenario_name,
            bs.rto_hours,
            bs.rpo_hours,
            bt.actual_rto_hours,
            bt.actual_rpo_hours,
            bt.test_date,
            bt.test_status
        FROM bcm_scenarios bs
        LEFT JOIN bcm_tests bt ON bt.scenario_id = bs.id
        WHERE bt.test_status = 'completed'
        ORDER BY bt.test_date DESC
        LIMIT 5
    `);
    
    return {
        scenarios: scenarios.map(s => ({
            ...s,
            rto_met: s.actual_rto_hours <= s.rto_hours,
            rpo_met: s.actual_rpo_hours <= s.rpo_hours,
            days_since_test: Math.floor((new Date() - new Date(s.test_date)) / (1000 * 60 * 60 * 24))
        }))
    };
}

export default router;