/**
 * Impact API Endpoints
 * Endpoints for Impact Validation and Passport generation
 */

import { Router } from 'express';
import { createLogger } from '../../utils/logger.js';

const logger = createLogger('ImpactAPI');

/**
 * Create Impact API routes
 */
export function createImpactRoutes(validationBridge, passportGenerator, simulationRouter) {
    const router = Router();
    
    // ==============================
    // VALIDATION ENDPOINTS
    // ==============================
    
    /**
     * Register simulation for future validation
     */
    router.post('/validations/register', async (req, res) => {
        try {
            const { simulationResult, organizationId } = req.body;
            
            if (!simulationResult || !organizationId) {
                return res.status(400).json({
                    error: 'simulationResult and organizationId required'
                });
            }
            
            const validationRecord = await validationBridge.registerSimulation(
                simulationResult,
                organizationId
            );
            
            res.json({
                success: true,
                validationRecord
            });
            
        } catch (error) {
            logger.error('Failed to register simulation for validation:', error);
            res.status(500).json({ error: error.message });
        }
    });
    
    /**
     * Validate simulation with evidence
     */
    router.post('/validations/validate', async (req, res) => {
        try {
            const { simulationId, evidence } = req.body;
            
            if (!simulationId || !evidence) {
                return res.status(400).json({
                    error: 'simulationId and evidence required'
                });
            }
            
            const validationReport = await validationBridge.validateSimulation(
                simulationId,
                evidence
            );
            
            res.json({
                success: true,
                validationReport
            });
            
        } catch (error) {
            logger.error('Failed to validate simulation:', error);
            res.status(500).json({ error: error.message });
        }
    });
    
    /**
     * Get validation history for organization
     */
    router.get('/validations/history/:organizationId', async (req, res) => {
        try {
            const { organizationId } = req.params;
            
            const history = validationBridge.getValidationHistory(organizationId);
            
            res.json({
                organizationId,
                validations: history,
                count: history.length
            });
            
        } catch (error) {
            logger.error('Failed to get validation history:', error);
            res.status(500).json({ error: error.message });
        }
    });
    
    /**
     * Get organization validation score
     */
    router.get('/validations/score/:organizationId', async (req, res) => {
        try {
            const { organizationId } = req.params;
            
            const score = validationBridge.calculateOrganizationValidationScore(organizationId);
            
            res.json({
                organizationId,
                validationScore: score
            });
            
        } catch (error) {
            logger.error('Failed to calculate validation score:', error);
            res.status(500).json({ error: error.message });
        }
    });
    
    /**
     * Get pending validations
     */
    router.get('/validations/pending/:organizationId?', async (req, res) => {
        try {
            const { organizationId } = req.params;
            
            const pending = validationBridge.getPendingValidations(organizationId);
            
            res.json({
                pending,
                count: pending.length
            });
            
        } catch (error) {
            logger.error('Failed to get pending validations:', error);
            res.status(500).json({ error: error.message });
        }
    });
    
    // ==============================
    // PASSPORT ENDPOINTS
    // ==============================
    
    /**
     * Generate or update Impact Passport
     */
    router.post('/passports/generate', async (req, res) => {
        try {
            const { organizationData, simulationResult, validationReport } = req.body;
            
            if (!organizationData) {
                return res.status(400).json({
                    error: 'organizationData required'
                });
            }
            
            const passport = await passportGenerator.generatePassport(
                organizationData,
                simulationResult,
                validationReport
            );
            
            res.json({
                success: true,
                passport
            });
            
        } catch (error) {
            logger.error('Failed to generate passport:', error);
            res.status(500).json({ error: error.message });
        }
    });
    
    /**
     * Get Impact Passport
     */
    router.get('/passports/:organizationId', async (req, res) => {
        try {
            const { organizationId } = req.params;
            
            const passport = await passportGenerator.getPassport(organizationId);
            
            if (!passport) {
                return res.status(404).json({
                    error: 'Passport not found'
                });
            }
            
            res.json(passport);
            
        } catch (error) {
            logger.error('Failed to get passport:', error);
            res.status(500).json({ error: error.message });
        }
    });
    
    /**
     * Verify passport credentials
     */
    router.post('/passports/verify', async (req, res) => {
        try {
            const { passportId, verificationCode } = req.body;
            
            if (!passportId || !verificationCode) {
                return res.status(400).json({
                    error: 'passportId and verificationCode required'
                });
            }
            
            const isValid = passportGenerator.verifyPassport(passportId, verificationCode);
            
            res.json({
                valid: isValid,
                passportId
            });
            
        } catch (error) {
            logger.error('Failed to verify passport:', error);
            res.status(500).json({ error: error.message });
        }
    });
    
    /**
     * Export passport as Verifiable Credential
     */
    router.get('/passports/:organizationId/export', async (req, res) => {
        try {
            const { organizationId } = req.params;
            
            const passport = await passportGenerator.getPassport(organizationId);
            
            if (!passport) {
                return res.status(404).json({
                    error: 'Passport not found'
                });
            }
            
            const vc = passportGenerator.exportPassportAsVC(passport);
            
            res.json(vc);
            
        } catch (error) {
            logger.error('Failed to export passport:', error);
            res.status(500).json({ error: error.message });
        }
    });
    
    // ==============================
    // SIMULATION ROUTING ENDPOINTS
    // ==============================
    
    /**
     * Run simulation with automatic routing
     */
    router.post('/simulations/run', async (req, res) => {
        try {
            const { experiment, params, options } = req.body;
            
            if (!experiment || !params) {
                return res.status(400).json({
                    error: 'experiment and params required'
                });
            }
            
            const result = await simulationRouter.runSimulation(
                experiment,
                params,
                options || {}
            );
            
            res.json({
                success: true,
                result
            });
            
        } catch (error) {
            logger.error('Failed to run simulation:', error);
            res.status(500).json({ error: error.message });
        }
    });
    
    /**
     * Get available experiments
     */
    router.get('/simulations/experiments', async (req, res) => {
        try {
            const experiments = simulationRouter.getAvailableExperiments();
            
            res.json({
                experiments,
                count: experiments.length
            });
            
        } catch (error) {
            logger.error('Failed to get experiments:', error);
            res.status(500).json({ error: error.message });
        }
    });
    
    // ==============================
    // INTEGRATED WORKFLOW ENDPOINTS
    // ==============================
    
    /**
     * Run simulation and register for validation
     */
    router.post('/workflow/simulate-and-register', async (req, res) => {
        try {
            const { experiment, params, organizationData, options } = req.body;
            
            if (!experiment || !params || !organizationData) {
                return res.status(400).json({
                    error: 'experiment, params, and organizationData required'
                });
            }
            
            // Run simulation
            const simulationResult = await simulationRouter.runSimulation(
                experiment,
                params,
                options || {}
            );
            
            // Register for validation
            const validationRecord = await validationBridge.registerSimulation(
                simulationResult,
                organizationData.id
            );
            
            // Generate/update passport
            const passport = await passportGenerator.generatePassport(
                organizationData,
                simulationResult,
                null // No validation yet
            );
            
            res.json({
                success: true,
                simulationResult,
                validationRecord,
                passport: {
                    id: passport.id,
                    reputation: passport.reputation,
                    metrics: passport.metrics
                }
            });
            
        } catch (error) {
            logger.error('Failed to run integrated workflow:', error);
            res.status(500).json({ error: error.message });
        }
    });
    
    /**
     * Validate and update passport
     */
    router.post('/workflow/validate-and-update', async (req, res) => {
        try {
            const { simulationId, evidence, organizationData } = req.body;
            
            if (!simulationId || !evidence || !organizationData) {
                return res.status(400).json({
                    error: 'simulationId, evidence, and organizationData required'
                });
            }
            
            // Validate simulation
            const validationReport = await validationBridge.validateSimulation(
                simulationId,
                evidence
            );
            
            // Update passport with validation
            const passport = await passportGenerator.generatePassport(
                organizationData,
                null, // No new simulation
                validationReport
            );
            
            res.json({
                success: true,
                validationReport,
                passport: {
                    id: passport.id,
                    reputation: passport.reputation,
                    metrics: passport.metrics,
                    achievements: passport.achievements
                }
            });
            
        } catch (error) {
            logger.error('Failed to validate and update passport:', error);
            res.status(500).json({ error: error.message });
        }
    });
    
    /**
     * Get organization impact summary
     */
    router.get('/workflow/impact-summary/:organizationId', async (req, res) => {
        try {
            const { organizationId } = req.params;
            
            // Get passport
            const passport = await passportGenerator.getPassport(organizationId);
            
            // Get validation score
            const validationScore = validationBridge.calculateOrganizationValidationScore(organizationId);
            
            // Get pending validations
            const pendingValidations = validationBridge.getPendingValidations(organizationId);
            
            res.json({
                organizationId,
                passport: passport ? {
                    id: passport.id,
                    reputation: passport.reputation,
                    metrics: passport.metrics,
                    achievements: passport.achievements,
                    certifications: passport.certifications
                } : null,
                validationScore,
                pendingValidations: pendingValidations.length,
                summary: {
                    hasPassport: !!passport,
                    reputationLevel: passport?.reputation?.level || 'none',
                    totalSimulations: passport?.metrics?.totalSimulations || 0,
                    validatedSimulations: passport?.metrics?.validatedSimulations || 0,
                    predictionAccuracy: validationScore?.score || 0,
                    successRate: validationScore?.successRate || 0
                }
            });
            
        } catch (error) {
            logger.error('Failed to get impact summary:', error);
            res.status(500).json({ error: error.message });
        }
    });
    
    return router;
}

export default createImpactRoutes;