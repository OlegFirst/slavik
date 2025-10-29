/**
 * Impact Passport Generator
 * Creates and manages Impact Passports for organizations
 * Integrates simulation results into persistent identity records
 */

import { EventEmitter } from 'events';
import { createLogger } from '../utils/logger.js';
import crypto from 'crypto';

const logger = createLogger('ImpactPassportGenerator');

/**
 * Generator for organizational Impact Passports
 */
export class ImpactPassportGenerator extends EventEmitter {
    constructor(config = {}) {
        super();
        
        this.config = {
            passportVersion: config.passportVersion || '1.0.0',
            minSimulationsForPassport: config.minSimulationsForPassport || 1,
            reputationAlgorithm: config.reputationAlgorithm || 'weighted_average',
            ...config
        };
        
        // Store generated passports
        this.passports = new Map();
        
        // Store passport history
        this.passportHistory = new Map();
        
        // IPS connection (will be injected)
        this.impactProofSystem = null;
        
        // Supabase connection
        this.supabase = null;
    }
    
    /**
     * Initialize with dependencies
     */
    async initialize(impactProofSystem, supabase) {
        this.impactProofSystem = impactProofSystem;
        this.supabase = supabase;
        
        // Load existing passports from database
        if (this.supabase) {
            await this.loadExistingPassports();
        }
        
        logger.info('Impact Passport Generator initialized');
    }
    
    /**
     * Generate or update Impact Passport after simulation
     */
    async generatePassport(organizationData, simulationResult, validationReport = null) {
        try {
            logger.info('Generating Impact Passport', {
                organizationId: organizationData.id,
                simulationId: simulationResult?.simulationId
            });
            
            // Check if passport exists
            let passport = await this.getPassport(organizationData.id);
            
            if (passport) {
                // Update existing passport
                passport = await this.updatePassport(
                    passport,
                    simulationResult,
                    validationReport
                );
            } else {
                // Create new passport
                passport = await this.createNewPassport(
                    organizationData,
                    simulationResult,
                    validationReport
                );
            }
            
            // Calculate reputation score
            passport.reputation = await this.calculateReputationScore(passport);
            
            // Generate passport credentials
            passport.credentials = await this.generateCredentials(passport);
            
            // Store passport
            await this.storePassport(passport);
            
            // Create in IPS if available
            if (this.impactProofSystem && !passport.ipsPassportId) {
                const ipsPassport = await this.createIPSPassport(passport);
                passport.ipsPassportId = ipsPassport.id;
            }
            
            logger.info('Impact Passport generated successfully', {
                passportId: passport.id,
                organizationId: passport.organizationId
            });
            
            this.emit('passport:generated', passport);
            
            return passport;
            
        } catch (error) {
            logger.error('Failed to generate Impact Passport:', error);
            throw error;
        }
    }
    
    /**
     * Create new passport
     */
    async createNewPassport(organizationData, simulationResult, validationReport) {
        const passportId = this.generatePassportId(organizationData.id);
        
        const passport = {
            id: passportId,
            version: this.config.passportVersion,
            organizationId: organizationData.id,
            organizationName: organizationData.name,
            organizationType: organizationData.type || 'NPO',
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
            
            // Organization profile
            profile: {
                mission: organizationData.mission,
                focus_areas: organizationData.focus_areas || [],
                beneficiaries: organizationData.beneficiaries || [],
                geographic_scope: organizationData.geographic_scope,
                team_size: organizationData.team_size,
                annual_budget: organizationData.annual_budget
            },
            
            // Impact history
            impactHistory: [],
            
            // Simulation history
            simulations: [],
            
            // Validation history
            validations: [],
            
            // Achievements
            achievements: [],
            
            // Metrics summary
            metrics: {
                totalSimulations: 0,
                validatedSimulations: 0,
                averagePredictionAccuracy: 0,
                impactScore: 0,
                efficiencyScore: 0,
                innovationScore: 0
            },
            
            // Reputation
            reputation: {
                score: 0,
                level: 'newcomer',
                trend: 'neutral'
            },
            
            // Certifications
            certifications: [],
            
            // Status
            status: 'active'
        };
        
        // Add initial simulation if provided
        if (simulationResult) {
            passport.simulations.push(this.createSimulationRecord(simulationResult));
            passport.metrics.totalSimulations = 1;
        }
        
        // Add initial validation if provided
        if (validationReport) {
            passport.validations.push(this.createValidationRecord(validationReport));
            passport.metrics.validatedSimulations = 1;
            passport.metrics.averagePredictionAccuracy = validationReport.accuracyMetrics.overallAccuracy;
        }
        
        return passport;
    }
    
    /**
     * Update existing passport
     */
    async updatePassport(passport, simulationResult, validationReport) {
        passport.updatedAt = new Date().toISOString();
        
        // Add simulation record
        if (simulationResult) {
            passport.simulations.push(this.createSimulationRecord(simulationResult));
            passport.metrics.totalSimulations += 1;
            
            // Update impact history
            this.updateImpactHistory(passport, simulationResult);
        }
        
        // Add validation record
        if (validationReport) {
            passport.validations.push(this.createValidationRecord(validationReport));
            passport.metrics.validatedSimulations += 1;
            
            // Update accuracy metrics
            this.updateAccuracyMetrics(passport, validationReport);
            
            // Check for new achievements
            await this.checkAchievements(passport, validationReport);
        }
        
        // Update metrics summary
        this.updateMetricsSummary(passport);
        
        return passport;
    }
    
    /**
     * Create simulation record
     */
    createSimulationRecord(simulationResult) {
        return {
            simulationId: simulationResult.simulationId,
            timestamp: simulationResult.timestamp || new Date().toISOString(),
            scenario: simulationResult.scenario,
            predictions: simulationResult.predictions || simulationResult.results,
            confidence: simulationResult.confidence,
            insights: simulationResult.insights
        };
    }
    
    /**
     * Create validation record
     */
    createValidationRecord(validationReport) {
        return {
            simulationId: validationReport.simulationId,
            validatedAt: validationReport.validatedAt,
            status: validationReport.status,
            accuracy: validationReport.accuracyMetrics.overallAccuracy,
            mape: validationReport.accuracyMetrics.mape,
            certificate: validationReport.impactCertificate?.certificateId
        };
    }
    
    /**
     * Update impact history
     */
    updateImpactHistory(passport, simulationResult) {
        const impactRecord = {
            date: new Date().toISOString(),
            type: 'simulation',
            description: `${simulationResult.scenario} simulation completed`,
            metrics: simulationResult.results,
            verified: false
        };
        
        passport.impactHistory.push(impactRecord);
        
        // Keep only last 100 records
        if (passport.impactHistory.length > 100) {
            passport.impactHistory = passport.impactHistory.slice(-100);
        }
    }
    
    /**
     * Update accuracy metrics
     */
    updateAccuracyMetrics(passport, validationReport) {
        const validations = passport.validations;
        
        if (validations.length > 0) {
            const totalAccuracy = validations.reduce((sum, v) => sum + (v.accuracy || 0), 0);
            passport.metrics.averagePredictionAccuracy = totalAccuracy / validations.length;
        }
        
        // Mark impact as verified
        const impactRecord = passport.impactHistory.find(
            h => h.type === 'simulation' && !h.verified
        );
        if (impactRecord) {
            impactRecord.verified = true;
            impactRecord.verificationAccuracy = validationReport.accuracyMetrics.overallAccuracy;
        }
    }
    
    /**
     * Check for new achievements
     */
    async checkAchievements(passport, validationReport) {
        const achievements = [];
        
        // First validated simulation
        if (passport.metrics.validatedSimulations === 1) {
            achievements.push({
                id: 'first_validation',
                name: 'First Validation',
                description: 'Completed first simulation validation',
                earnedAt: new Date().toISOString(),
                icon: 'star'
            });
        }
        
        // High accuracy achievement
        if (validationReport.accuracyMetrics.overallAccuracy >= 0.9) {
            achievements.push({
                id: 'high_accuracy',
                name: 'High Accuracy Predictor',
                description: 'Achieved 90%+ prediction accuracy',
                earnedAt: new Date().toISOString(),
                icon: 'target'
            });
        }
        
        // Multiple validations
        if (passport.metrics.validatedSimulations >= 5) {
            achievements.push({
                id: 'verified_predictor',
                name: 'Verified Predictor',
                description: 'Completed 5+ validated simulations',
                earnedAt: new Date().toISOString(),
                icon: 'shield'
            });
        }
        
        // Add new achievements
        for (const achievement of achievements) {
            if (!passport.achievements.find(a => a.id === achievement.id)) {
                passport.achievements.push(achievement);
                
                this.emit('achievement:earned', {
                    passportId: passport.id,
                    achievement
                });
            }
        }
    }
    
    /**
     * Update metrics summary
     */
    updateMetricsSummary(passport) {
        const metrics = passport.metrics;
        
        // Calculate impact score
        metrics.impactScore = this.calculateImpactScore(passport);
        
        // Calculate efficiency score
        metrics.efficiencyScore = this.calculateEfficiencyScore(passport);
        
        // Calculate innovation score
        metrics.innovationScore = this.calculateInnovationScore(passport);
    }
    
    /**
     * Calculate impact score
     */
    calculateImpactScore(passport) {
        let score = 0;
        
        // Base score from simulations
        score += passport.metrics.totalSimulations * 10;
        
        // Bonus for validated simulations
        score += passport.metrics.validatedSimulations * 20;
        
        // Bonus for accuracy
        score += passport.metrics.averagePredictionAccuracy * 50;
        
        // Bonus for achievements
        score += passport.achievements.length * 15;
        
        return Math.min(100, score);
    }
    
    /**
     * Calculate efficiency score
     */
    calculateEfficiencyScore(passport) {
        if (passport.simulations.length === 0) return 0;
        
        let totalEfficiency = 0;
        let count = 0;
        
        for (const simulation of passport.simulations) {
            if (simulation.predictions?.efficiency) {
                totalEfficiency += simulation.predictions.efficiency;
                count++;
            }
        }
        
        return count > 0 ? (totalEfficiency / count) * 100 : 50;
    }
    
    /**
     * Calculate innovation score
     */
    calculateInnovationScore(passport) {
        let score = 0;
        
        // Variety of scenarios tested
        const uniqueScenarios = new Set(passport.simulations.map(s => s.scenario));
        score += uniqueScenarios.size * 10;
        
        // Use of advanced features
        const hasToC = passport.simulations.some(s => s.scenario?.includes('theory_of_change'));
        const hasABM = passport.simulations.some(s => s.scenario?.includes('mesa_abm'));
        
        if (hasToC) score += 25;
        if (hasABM) score += 25;
        
        return Math.min(100, score);
    }
    
    /**
     * Calculate reputation score
     */
    async calculateReputationScore(passport) {
        const weights = {
            predictionAccuracy: 0.3,
            simulationCount: 0.2,
            validationRate: 0.2,
            impactScore: 0.15,
            achievements: 0.15
        };
        
        let weightedScore = 0;
        
        // Prediction accuracy component
        weightedScore += passport.metrics.averagePredictionAccuracy * weights.predictionAccuracy;
        
        // Simulation count component (normalized to 0-1)
        const simScore = Math.min(1, passport.metrics.totalSimulations / 20);
        weightedScore += simScore * weights.simulationCount;
        
        // Validation rate component
        const validationRate = passport.metrics.totalSimulations > 0
            ? passport.metrics.validatedSimulations / passport.metrics.totalSimulations
            : 0;
        weightedScore += validationRate * weights.validationRate;
        
        // Impact score component
        weightedScore += (passport.metrics.impactScore / 100) * weights.impactScore;
        
        // Achievements component
        const achievementScore = Math.min(1, passport.achievements.length / 10);
        weightedScore += achievementScore * weights.achievements;
        
        // Determine level
        let level = 'newcomer';
        if (weightedScore >= 0.8) level = 'expert';
        else if (weightedScore >= 0.6) level = 'advanced';
        else if (weightedScore >= 0.4) level = 'intermediate';
        else if (weightedScore >= 0.2) level = 'beginner';
        
        // Determine trend
        let trend = 'neutral';
        if (passport.reputation?.score) {
            if (weightedScore > passport.reputation.score) trend = 'rising';
            else if (weightedScore < passport.reputation.score) trend = 'falling';
        }
        
        return {
            score: weightedScore,
            level,
            trend,
            components: {
                predictionAccuracy: passport.metrics.averagePredictionAccuracy,
                simulationCount: simScore,
                validationRate,
                impactScore: passport.metrics.impactScore / 100,
                achievements: achievementScore
            }
        };
    }
    
    /**
     * Generate passport credentials
     */
    async generateCredentials(passport) {
        const credentials = {
            passportId: passport.id,
            issuedAt: new Date().toISOString(),
            expiresAt: new Date(Date.now() + 365 * 24 * 60 * 60 * 1000).toISOString(), // 1 year
            verificationCode: this.generateVerificationCode(passport),
            publicKey: await this.generatePublicKey(passport),
            claims: {
                organizationId: passport.organizationId,
                organizationName: passport.organizationName,
                reputationScore: passport.reputation.score,
                reputationLevel: passport.reputation.level,
                totalSimulations: passport.metrics.totalSimulations,
                validatedSimulations: passport.metrics.validatedSimulations
            }
        };
        
        return credentials;
    }
    
    /**
     * Generate passport ID
     */
    generatePassportId(organizationId) {
        return `passport_${organizationId}_${Date.now()}`;
    }
    
    /**
     * Generate verification code
     */
    generateVerificationCode(passport) {
        const hash = crypto.createHash('sha256');
        hash.update(JSON.stringify({
            id: passport.id,
            organizationId: passport.organizationId,
            createdAt: passport.createdAt
        }));
        return hash.digest('hex').substring(0, 16);
    }
    
    /**
     * Generate public key for passport
     */
    async generatePublicKey(passport) {
        // Simplified - in production would use proper key generation
        const hash = crypto.createHash('sha256');
        hash.update(passport.id + passport.organizationId);
        return hash.digest('base64');
    }
    
    /**
     * Create passport in Impact Proof System
     */
    async createIPSPassport(passport) {
        if (!this.impactProofSystem) {
            logger.warn('Impact Proof System not available');
            return null;
        }
        
        const ipsData = {
            organizationId: passport.organizationId,
            name: passport.organizationName,
            type: passport.organizationType,
            profile: passport.profile,
            reputation: passport.reputation,
            achievements: passport.achievements,
            certifications: passport.certifications
        };
        
        return await this.impactProofSystem.createImpactPassport(ipsData);
    }
    
    /**
     * Store passport
     */
    async storePassport(passport) {
        // Store in memory
        this.passports.set(passport.organizationId, passport);
        
        // Store history
        if (!this.passportHistory.has(passport.organizationId)) {
            this.passportHistory.set(passport.organizationId, []);
        }
        this.passportHistory.get(passport.organizationId).push({
            version: passport.version,
            timestamp: passport.updatedAt,
            snapshot: JSON.parse(JSON.stringify(passport))
        });
        
        // Store in database if available
        if (this.supabase) {
            await this.savePassportToDatabase(passport);
        }
    }
    
    /**
     * Save passport to database
     */
    async savePassportToDatabase(passport) {
        try {
            const { error } = await this.supabase
                .from('impact_passports')
                .upsert({
                    id: passport.id,
                    organization_id: passport.organizationId,
                    passport_data: JSON.stringify(passport),
                    reputation_score: passport.reputation.score,
                    reputation_level: passport.reputation.level,
                    total_simulations: passport.metrics.totalSimulations,
                    validated_simulations: passport.metrics.validatedSimulations,
                    updated_at: passport.updatedAt
                });
                
            if (error) throw error;
            
        } catch (error) {
            logger.error('Failed to save passport to database:', error);
        }
    }
    
    /**
     * Load existing passports from database
     */
    async loadExistingPassports() {
        try {
            const { data: passports, error } = await this.supabase
                .from('impact_passports')
                .select('*');
                
            if (error) throw error;
            
            if (passports) {
                for (const record of passports) {
                    const passport = JSON.parse(record.passport_data);
                    this.passports.set(passport.organizationId, passport);
                }
                
                logger.info(`Loaded ${passports.length} existing passports`);
            }
            
        } catch (error) {
            logger.error('Failed to load existing passports:', error);
        }
    }
    
    /**
     * Get passport by organization ID
     */
    async getPassport(organizationId) {
        // Check memory first
        if (this.passports.has(organizationId)) {
            return this.passports.get(organizationId);
        }
        
        // Try to load from database
        if (this.supabase) {
            try {
                const { data, error } = await this.supabase
                    .from('impact_passports')
                    .select('passport_data')
                    .eq('organization_id', organizationId)
                    .single();
                    
                if (data) {
                    const passport = JSON.parse(data.passport_data);
                    this.passports.set(organizationId, passport);
                    return passport;
                }
            } catch (error) {
                logger.error('Failed to load passport from database:', error);
            }
        }
        
        return null;
    }
    
    /**
     * Verify passport credentials
     */
    verifyPassport(passportId, verificationCode) {
        for (const passport of this.passports.values()) {
            if (passport.id === passportId) {
                const expectedCode = this.generateVerificationCode(passport);
                return expectedCode === verificationCode;
            }
        }
        
        return false;
    }
    
    /**
     * Export passport as verifiable credential
     */
    exportPassportAsVC(passport) {
        return {
            "@context": [
                "https://www.w3.org/2018/credentials/v1",
                "https://schema.org"
            ],
            type: ["VerifiableCredential", "ImpactPassport"],
            issuer: "Digital Twin Impact System",
            issuanceDate: passport.createdAt,
            credentialSubject: {
                id: passport.organizationId,
                name: passport.organizationName,
                reputation: passport.reputation,
                metrics: passport.metrics,
                achievements: passport.achievements
            },
            proof: {
                type: "Ed25519Signature2020",
                created: new Date().toISOString(),
                verificationMethod: passport.credentials?.publicKey,
                proofPurpose: "assertionMethod",
                proofValue: passport.credentials?.verificationCode
            }
        };
    }
}

export default ImpactPassportGenerator;