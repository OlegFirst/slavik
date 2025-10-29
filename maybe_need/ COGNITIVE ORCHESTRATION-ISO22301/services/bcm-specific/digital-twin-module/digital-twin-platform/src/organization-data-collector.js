/**
 * =====================================================================
 * NASH 4.0 - Organization Data Collection System
 * Enterprise-grade data collection and analysis for Digital Twin creation
 * =====================================================================
 * 
 * Purpose: Comprehensive data collection and analysis system for building
 *          accurate digital twins of organizations
 * Author: NASH 4.0 Technical Partnership Team
 * Version: 1.0.0
 * Date: 2025-08-12
 * 
 * Features:
 * - Multi-source data collection (interviews, documents, systems)
 * - Automated organizational structure analysis
 * - Process flow discovery and mapping
 * - Technology stack assessment
 * - Financial model extraction
 * - Risk assessment and compliance checking
 * - Real-time data validation and quality assurance
 * =====================================================================
 */

import { EventEmitter } from 'events';
import { createLogger } from '../utils/logger.js';
import { 
    ValidationError, 
    ProcessingError,
    ConfigurationError 
} from '../utils/errors.js';

/**
 * Data collection methods enumeration
 */
const DataCollectionMethod = {
    INTERVIEW: 'interview',
    DOCUMENT_ANALYSIS: 'document_analysis',
    SYSTEM_INTEGRATION: 'system_integration',
    SURVEY: 'survey',
    OBSERVATION: 'observation',
    API_EXTRACTION: 'api_extraction',
    DATABASE_QUERY: 'database_query',
    FILE_UPLOAD: 'file_upload'
};

/**
 * Organization data categories
 */
const DataCategory = {
    STRUCTURE: 'organizational_structure',
    PROCESSES: 'business_processes',
    TECHNOLOGY: 'technology_stack',
    FINANCIAL: 'financial_data',
    HUMAN_RESOURCES: 'human_resources',
    OPERATIONS: 'operations',
    COMPLIANCE: 'compliance_data',
    STRATEGIC: 'strategic_planning',
    PERFORMANCE: 'performance_metrics',
    STAKEHOLDERS: 'stakeholders'
};

/**
 * Data quality levels
 */
const DataQuality = {
    EXCELLENT: 'excellent',
    GOOD: 'good',
    ACCEPTABLE: 'acceptable',
    POOR: 'poor',
    INCOMPLETE: 'incomplete'
};

export class OrganizationDataCollector extends EventEmitter {
    constructor(config = {}) {
        super();
        
        this.logger = createLogger('OrganizationDataCollector');
        
        // Configuration
        this.config = {
            enableAutoValidation: config.enableAutoValidation !== false,
            enableRealTimeProcessing: config.enableRealTimeProcessing !== false,
            maxConcurrentCollections: config.maxConcurrentCollections || 5,
            dataRetentionDays: config.dataRetentionDays || 90,
            qualityThreshold: config.qualityThreshold || 0.7,
            enableMLAnalysis: config.enableMLAnalysis !== false,
            enableNLPProcessing: config.enableNLPProcessing !== false,
            ...config
        };
        
        // Data storage
        this.collectionSessions = new Map();
        this.organizationData = new Map();
        this.dataQualityMetrics = new Map();
        this.validationRules = new Map();
        
        // Collection methods registry
        this.collectionMethods = new Map();
        this.activeCollectors = new Map();
        
        // Analysis engines
        this.analysisEngines = {
            structureAnalyzer: null,
            processAnalyzer: null,
            technologyAnalyzer: null,
            financialAnalyzer: null,
            complianceAnalyzer: null
        };
        
        // Initialize built-in collection methods
        this.initializeCollectionMethods();
        this.initializeValidationRules();
        
        this.logger.info('Organization Data Collector initialized');
    }
    
    /**
     * Initialize built-in collection methods
     * @private
     */
    initializeCollectionMethods() {
        // Interview-based data collection
        this.collectionMethods.set(DataCollectionMethod.INTERVIEW, {
            name: 'Structured Interview',
            description: 'Guided interview process for comprehensive data collection',
            categories: Object.values(DataCategory),
            handler: this.handleInterviewCollection.bind(this)
        });
        
        // Document analysis
        this.collectionMethods.set(DataCollectionMethod.DOCUMENT_ANALYSIS, {
            name: 'Document Analysis',
            description: 'Automated analysis of organizational documents',
            categories: [DataCategory.STRUCTURE, DataCategory.PROCESSES, DataCategory.COMPLIANCE],
            handler: this.handleDocumentAnalysis.bind(this)
        });
        
        // System integration
        this.collectionMethods.set(DataCollectionMethod.SYSTEM_INTEGRATION, {
            name: 'System Integration',
            description: 'Direct integration with existing organizational systems',
            categories: [DataCategory.TECHNOLOGY, DataCategory.FINANCIAL, DataCategory.OPERATIONS],
            handler: this.handleSystemIntegration.bind(this)
        });
        
        // Survey collection
        this.collectionMethods.set(DataCollectionMethod.SURVEY, {
            name: 'Digital Survey',
            description: 'Comprehensive digital surveys for stakeholders',
            categories: [DataCategory.HUMAN_RESOURCES, DataCategory.PERFORMANCE, DataCategory.STAKEHOLDERS],
            handler: this.handleSurveyCollection.bind(this)
        });
        
        // File upload processing
        this.collectionMethods.set(DataCollectionMethod.FILE_UPLOAD, {
            name: 'File Upload Processing',
            description: 'Processing uploaded files for data extraction',
            categories: Object.values(DataCategory),
            handler: this.handleFileUpload.bind(this)
        });
    }
    
    /**
     * Initialize validation rules
     * @private
     */
    initializeValidationRules() {
        // Organizational structure validation
        this.validationRules.set(DataCategory.STRUCTURE, {
            required: ['departments', 'hierarchy', 'roles'],
            format: {
                departments: 'array',
                hierarchy: 'object',
                roles: 'array'
            },
            constraints: {
                'departments.length': { min: 1, max: 100 },
                'roles.length': { min: 1, max: 500 }
            }
        });
        
        // Process validation
        this.validationRules.set(DataCategory.PROCESSES, {
            required: ['core_processes', 'support_processes'],
            format: {
                core_processes: 'array',
                support_processes: 'array'
            },
            constraints: {
                'core_processes.length': { min: 1, max: 50 }
            }
        });
        
        // Technology validation
        this.validationRules.set(DataCategory.TECHNOLOGY, {
            required: ['systems', 'technologies', 'integrations'],
            format: {
                systems: 'array',
                technologies: 'array',
                integrations: 'array'
            }
        });
        
        // Financial validation
        this.validationRules.set(DataCategory.FINANCIAL, {
            required: ['budget', 'revenue_streams', 'cost_structure'],
            format: {
                budget: 'number',
                revenue_streams: 'array',
                cost_structure: 'object'
            },
            constraints: {
                budget: { min: 0 }
            }
        });
    }
    
    /**
     * Start data collection session for organization
     * @param {string} organizationId - Organization ID
     * @param {Object} collectionPlan - Collection plan configuration
     * @returns {Promise<Object>} Collection session
     */
    async startCollectionSession(organizationId, collectionPlan) {
        try {
            this.logger.info('Starting data collection session', { organizationId });
            
            // Validate collection plan
            this.validateCollectionPlan(collectionPlan);
            
            // Create collection session
            const sessionId = this.generateSessionId();
            const session = {
                id: sessionId,
                organizationId,
                plan: collectionPlan,
                status: 'active',
                startTime: new Date().toISOString(),
                progress: {
                    categories: {},
                    overallProgress: 0,
                    qualityScore: 0
                },
                collectedData: {},
                validationResults: {},
                methods: collectionPlan.methods || [DataCollectionMethod.INTERVIEW],
                completedSteps: [],
                nextSteps: []
            };
            
            // Initialize progress tracking for each category
            for (const category of collectionPlan.categories || Object.values(DataCategory)) {
                session.progress.categories[category] = {
                    status: 'pending',
                    progress: 0,
                    quality: DataQuality.INCOMPLETE,
                    dataPoints: 0,
                    validationsPassed: 0
                };
            }
            
            // Store session
            this.collectionSessions.set(sessionId, session);
            
            // Generate collection workflow
            const workflow = this.generateCollectionWorkflow(session);
            session.workflow = workflow;
            session.nextSteps = workflow.steps.slice(0, 3); // First 3 steps
            
            this.logger.info('Collection session created', { 
                sessionId, 
                organizationId,
                categories: Object.keys(session.progress.categories).length,
                methods: session.methods.length
            });
            
            this.emit('sessionStarted', { sessionId, organizationId, session });
            
            return {
                success: true,
                sessionId,
                session: this.sanitizeSession(session),
                nextSteps: session.nextSteps
            };
            
        } catch (error) {
            this.logger.error('Failed to start collection session', { 
                organizationId, 
                error: error.message 
            });
            throw error;
        }
    }
    
    /**
     * Collect data using specified method
     * @param {string} sessionId - Collection session ID
     * @param {string} method - Collection method
     * @param {string} category - Data category
     * @param {Object} data - Raw data to process
     * @returns {Promise<Object>} Collection result
     */
    async collectData(sessionId, method, category, data) {
        try {
            const session = this.collectionSessions.get(sessionId);
            if (!session) {
                throw new ValidationError(`Collection session not found: ${sessionId}`);
            }
            
            this.logger.info('Processing data collection', { 
                sessionId, 
                method, 
                category,
                dataSize: JSON.stringify(data).length
            });
            
            // Get collection method handler
            const methodConfig = this.collectionMethods.get(method);
            if (!methodConfig) {
                throw new ValidationError(`Unknown collection method: ${method}`);
            }
            
            // Validate category for method
            if (!methodConfig.categories.includes(category)) {
                throw new ValidationError(`Method ${method} does not support category ${category}`);
            }
            
            // Process data using method handler
            const processingResult = await methodConfig.handler(data, category, session);
            
            // Validate processed data
            const validationResult = this.validateCategoryData(category, processingResult.processedData);
            
            // Store collected data
            if (!session.collectedData[category]) {
                session.collectedData[category] = {};
            }
            
            session.collectedData[category] = {
                ...session.collectedData[category],
                ...processingResult.processedData,
                _metadata: {
                    method,
                    collectedAt: new Date().toISOString(),
                    quality: validationResult.quality,
                    completeness: validationResult.completeness,
                    confidence: processingResult.confidence || 0.8
                }
            };
            
            // Update progress
            this.updateSessionProgress(session, category, validationResult);
            
            // Store validation results
            session.validationResults[category] = validationResult;
            
            // Update next steps
            this.updateNextSteps(session);
            
            this.logger.info('Data collection completed', {
                sessionId,
                category,
                quality: validationResult.quality,
                completeness: validationResult.completeness
            });
            
            this.emit('dataCollected', { 
                sessionId, 
                category, 
                method, 
                quality: validationResult.quality,
                result: processingResult
            });
            
            return {
                success: true,
                quality: validationResult.quality,
                completeness: validationResult.completeness,
                confidence: processingResult.confidence,
                validationResult,
                nextSteps: session.nextSteps
            };
            
        } catch (error) {
            this.logger.error('Data collection failed', { 
                sessionId, 
                method, 
                category, 
                error: error.message 
            });
            throw error;
        }
    }
    
    /**
     * Handle interview-based data collection
     * @private
     * @param {Object} data - Interview data
     * @param {string} category - Data category
     * @param {Object} session - Collection session
     * @returns {Promise<Object>} Processing result
     */
    async handleInterviewCollection(data, category, session) {
        const { responses, interviewType, participantRole } = data;
        
        let processedData = {};
        let confidence = 0.7; // Default confidence for interview data
        
        switch (category) {
            case DataCategory.STRUCTURE:
                processedData = this.extractStructuralData(responses);
                confidence = this.calculateStructuralConfidence(responses, participantRole);
                break;
                
            case DataCategory.PROCESSES:
                processedData = this.extractProcessData(responses);
                confidence = this.calculateProcessConfidence(responses, participantRole);
                break;
                
            case DataCategory.TECHNOLOGY:
                processedData = this.extractTechnologyData(responses);
                confidence = this.calculateTechnologyConfidence(responses, participantRole);
                break;
                
            case DataCategory.FINANCIAL:
                processedData = this.extractFinancialData(responses);
                confidence = this.calculateFinancialConfidence(responses, participantRole);
                break;
                
            case DataCategory.HUMAN_RESOURCES:
                processedData = this.extractHRData(responses);
                confidence = 0.8; // HR interviews typically reliable
                break;
                
            default:
                processedData = this.extractGenericData(responses, category);
                break;
        }
        
        return {
            processedData,
            confidence,
            method: DataCollectionMethod.INTERVIEW,
            source: {
                type: interviewType,
                participant: participantRole,
                timestamp: new Date().toISOString()
            }
        };
    }
    
    /**
     * Handle document analysis
     * @private
     * @param {Object} data - Document data
     * @param {string} category - Data category
     * @param {Object} session - Collection session
     * @returns {Promise<Object>} Processing result
     */
    async handleDocumentAnalysis(data, category, session) {
        const { documents, documentTypes } = data;
        
        let processedData = {};
        let confidence = 0.6; // Lower confidence for document analysis
        
        // Process documents based on category
        for (const doc of documents) {
            const analysis = await this.analyzeDocument(doc, category);
            processedData = { ...processedData, ...analysis.extractedData };
            confidence = Math.max(confidence, analysis.confidence);
        }
        
        return {
            processedData,
            confidence,
            method: DataCollectionMethod.DOCUMENT_ANALYSIS,
            source: {
                documentCount: documents.length,
                types: documentTypes,
                timestamp: new Date().toISOString()
            }
        };
    }
    
    /**
     * Handle system integration data collection
     * @private
     * @param {Object} data - System data
     * @param {string} category - Data category  
     * @param {Object} session - Collection session
     * @returns {Promise<Object>} Processing result
     */
    async handleSystemIntegration(data, category, session) {
        const { systemType, connectionConfig, queryParams } = data;
        
        let processedData = {};
        let confidence = 0.9; // High confidence for system data
        
        try {
            // Connect to system and extract data
            const systemData = await this.connectAndExtractData(systemType, connectionConfig, queryParams);
            
            // Process system data based on category
            processedData = this.processSystemData(systemData, category, systemType);
            
        } catch (error) {
            this.logger.error('System integration failed', { systemType, error: error.message });
            confidence = 0.1;
            processedData = { error: error.message, partial: true };
        }
        
        return {
            processedData,
            confidence,
            method: DataCollectionMethod.SYSTEM_INTEGRATION,
            source: {
                systemType,
                timestamp: new Date().toISOString()
            }
        };
    }
    
    /**
     * Handle survey data collection
     * @private
     * @param {Object} data - Survey data
     * @param {string} category - Data category
     * @param {Object} session - Collection session
     * @returns {Promise<Object>} Processing result
     */
    async handleSurveyCollection(data, category, session) {
        const { responses, surveyType, responseCount, demographics } = data;
        
        // Aggregate survey responses
        const aggregatedData = this.aggregateSurveyResponses(responses, category);
        const confidence = this.calculateSurveyConfidence(responseCount, demographics);
        
        return {
            processedData: aggregatedData,
            confidence,
            method: DataCollectionMethod.SURVEY,
            source: {
                surveyType,
                responseCount,
                demographics,
                timestamp: new Date().toISOString()
            }
        };
    }
    
    /**
     * Handle file upload processing
     * @private  
     * @param {Object} data - File data
     * @param {string} category - Data category
     * @param {Object} session - Collection session
     * @returns {Promise<Object>} Processing result
     */
    async handleFileUpload(data, category, session) {
        const { files, fileTypes } = data;
        
        let processedData = {};
        let confidence = 0.5; // Variable confidence based on file content
        
        for (const file of files) {
            const fileAnalysis = await this.analyzeUploadedFile(file, category);
            processedData = { ...processedData, ...fileAnalysis.data };
            confidence = Math.max(confidence, fileAnalysis.confidence);
        }
        
        return {
            processedData,
            confidence,
            method: DataCollectionMethod.FILE_UPLOAD,
            source: {
                fileCount: files.length,
                types: fileTypes,
                timestamp: new Date().toISOString()
            }
        };
    }
    
    /**
     * Generate collection workflow for session
     * @private
     * @param {Object} session - Collection session
     * @returns {Object} Collection workflow
     */
    generateCollectionWorkflow(session) {
        const { plan, organizationId } = session;
        const workflow = {
            steps: [],
            estimatedDuration: 0,
            priority: 'medium'
        };
        
        // Generate steps based on categories and methods
        for (const category of plan.categories || Object.values(DataCategory)) {
            for (const method of plan.methods || [DataCollectionMethod.INTERVIEW]) {
                const methodConfig = this.collectionMethods.get(method);
                
                if (methodConfig && methodConfig.categories.includes(category)) {
                    workflow.steps.push({
                        id: `${method}_${category}`,
                        method,
                        category,
                        title: `Collect ${category} data via ${methodConfig.name}`,
                        description: `Use ${methodConfig.description} to gather ${category} information`,
                        estimatedDuration: this.estimateStepDuration(method, category),
                        priority: this.calculateStepPriority(category, method),
                        dependencies: this.getStepDependencies(category, method),
                        status: 'pending'
                    });
                }
            }
        }
        
        // Sort steps by priority and dependencies
        workflow.steps = this.sortWorkflowSteps(workflow.steps);
        workflow.estimatedDuration = workflow.steps.reduce((total, step) => total + step.estimatedDuration, 0);
        
        return workflow;
    }
    
    /**
     * Get collection session status
     * @param {string} sessionId - Session ID
     * @returns {Object} Session status
     */
    getSessionStatus(sessionId) {
        const session = this.collectionSessions.get(sessionId);
        if (!session) {
            throw new ValidationError(`Collection session not found: ${sessionId}`);
        }
        
        return {
            sessionId,
            status: session.status,
            progress: session.progress,
            nextSteps: session.nextSteps,
            completedCategories: Object.keys(session.collectedData),
            qualityScore: this.calculateOverallQualityScore(session),
            estimatedCompletion: this.estimateCompletionTime(session)
        };
    }
    
    /**
     * Complete collection session
     * @param {string} sessionId - Session ID
     * @returns {Promise<Object>} Completion result
     */
    async completeSession(sessionId) {
        try {
            const session = this.collectionSessions.get(sessionId);
            if (!session) {
                throw new ValidationError(`Collection session not found: ${sessionId}`);
            }
            
            // Validate completeness
            const completionCheck = this.validateSessionCompletion(session);
            if (!completionCheck.isComplete) {
                throw new ValidationError(`Session not ready for completion: ${completionCheck.reason}`);
            }
            
            // Generate final organization profile
            const organizationProfile = this.generateOrganizationProfile(session);
            
            // Update session
            session.status = 'completed';
            session.completedAt = new Date().toISOString();
            session.finalProfile = organizationProfile;
            
            // Store organization data
            this.organizationData.set(session.organizationId, {
                profile: organizationProfile,
                collectionData: session.collectedData,
                qualityMetrics: this.calculateQualityMetrics(session),
                sessionId,
                completedAt: session.completedAt
            });
            
            this.logger.info('Collection session completed', { 
                sessionId, 
                organizationId: session.organizationId,
                qualityScore: organizationProfile.qualityScore
            });
            
            this.emit('sessionCompleted', { 
                sessionId, 
                organizationId: session.organizationId,
                profile: organizationProfile
            });
            
            return {
                success: true,
                organizationProfile,
                qualityMetrics: this.calculateQualityMetrics(session)
            };
            
        } catch (error) {
            this.logger.error('Failed to complete session', { sessionId, error: error.message });
            throw error;
        }
    }
    
    /**
     * Get available collection methods
     * @returns {Array} Available collection methods
     */
    getAvailableCollectionMethods() {
        return Array.from(this.collectionMethods.entries()).map(([key, config]) => ({
            method: key,
            name: config.name,
            description: config.description,
            supportedCategories: config.categories
        }));
    }
    
    /**
     * Get data categories
     * @returns {Array} Available data categories
     */
    getDataCategories() {
        return Object.values(DataCategory).map(category => ({
            category,
            description: this.getCategoryDescription(category),
            required: this.isCategoryRequired(category),
            validationRules: this.validationRules.get(category)
        }));
    }
    
    /**
     * Validate collection plan
     * @private
     * @param {Object} plan - Collection plan
     */
    validateCollectionPlan(plan) {
        if (!plan.categories || !Array.isArray(plan.categories) || plan.categories.length === 0) {
            throw new ValidationError('Collection plan must specify at least one data category');
        }
        
        if (!plan.methods || !Array.isArray(plan.methods) || plan.methods.length === 0) {
            throw new ValidationError('Collection plan must specify at least one collection method');
        }
        
        // Validate categories
        for (const category of plan.categories) {
            if (!Object.values(DataCategory).includes(category)) {
                throw new ValidationError(`Invalid data category: ${category}`);
            }
        }
        
        // Validate methods
        for (const method of plan.methods) {
            if (!this.collectionMethods.has(method)) {
                throw new ValidationError(`Invalid collection method: ${method}`);
            }
        }
    }
    
    /**
     * Generate session ID
     * @private
     * @returns {string} Session ID
     */
    generateSessionId() {
        return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }
    
    /**
     * Calculate overall quality score for session
     * @private
     * @param {Object} session - Collection session
     * @returns {number} Quality score (0-1)
     */
    calculateOverallQualityScore(session) {
        const categories = Object.keys(session.progress.categories);
        if (categories.length === 0) return 0;
        
        let totalScore = 0;
        let weightSum = 0;
        
        for (const category of categories) {
            const progress = session.progress.categories[category];
            const weight = this.getCategoryWeight(category);
            const qualityValue = this.qualityToValue(progress.quality);
            
            totalScore += qualityValue * weight * (progress.progress / 100);
            weightSum += weight;
        }
        
        return weightSum > 0 ? totalScore / weightSum : 0;
    }
    
    /**
     * Convert quality level to numeric value
     * @private
     * @param {string} quality - Quality level
     * @returns {number} Quality value (0-1)
     */
    qualityToValue(quality) {
        const mapping = {
            [DataQuality.EXCELLENT]: 1.0,
            [DataQuality.GOOD]: 0.8,
            [DataQuality.ACCEPTABLE]: 0.6,
            [DataQuality.POOR]: 0.3,
            [DataQuality.INCOMPLETE]: 0.1
        };
        return mapping[quality] || 0;
    }
    
    /**
     * Sanitize session for external consumption
     * @private
     * @param {Object} session - Collection session
     * @returns {Object} Sanitized session
     */
    sanitizeSession(session) {
        return {
            id: session.id,
            organizationId: session.organizationId,
            status: session.status,
            startTime: session.startTime,
            progress: session.progress,
            methods: session.methods,
            nextSteps: session.nextSteps,
            completedSteps: session.completedSteps
        };
    }
    
    /**
     * Get category description
     * @private
     * @param {string} category - Data category
     * @returns {string} Category description
     */
    getCategoryDescription(category) {
        const descriptions = {
            [DataCategory.STRUCTURE]: 'Organizational hierarchy, departments, roles, and reporting structures',
            [DataCategory.PROCESSES]: 'Core business processes, workflows, and operational procedures',
            [DataCategory.TECHNOLOGY]: 'Technology stack, systems, software, and digital infrastructure',
            [DataCategory.FINANCIAL]: 'Budget, revenue streams, costs, and financial management',
            [DataCategory.HUMAN_RESOURCES]: 'Staff, roles, skills, and HR processes',
            [DataCategory.OPERATIONS]: 'Day-to-day operations, facilities, and resource management',
            [DataCategory.COMPLIANCE]: 'Regulatory compliance, policies, and governance',
            [DataCategory.STRATEGIC]: 'Vision, mission, goals, and strategic planning',
            [DataCategory.PERFORMANCE]: 'KPIs, metrics, and performance measurement',
            [DataCategory.STAKEHOLDERS]: 'Stakeholder relationships, partnerships, and engagement'
        };
        return descriptions[category] || 'Data category description not available';
    }
    
    /**
     * Check if category is required
     * @private
     * @param {string} category - Data category
     * @returns {boolean} Is required
     */
    isCategoryRequired(category) {
        const required = [
            DataCategory.STRUCTURE,
            DataCategory.PROCESSES,
            DataCategory.TECHNOLOGY,
            DataCategory.FINANCIAL
        ];
        return required.includes(category);
    }
    
    /**
     * Get system status
     * @returns {Object} System status
     */
    getStatus() {
        return {
            activeSessions: this.collectionSessions.size,
            completedOrganizations: this.organizationData.size,
            availableMethods: this.collectionMethods.size,
            validationRules: this.validationRules.size,
            config: {
                enableAutoValidation: this.config.enableAutoValidation,
                enableRealTimeProcessing: this.config.enableRealTimeProcessing,
                qualityThreshold: this.config.qualityThreshold
            }
        };
    }
    
    /**
     * Estimate step duration
     * @private
     * @param {string} method - Collection method
     * @param {string} category - Data category
     * @returns {number} Estimated duration in minutes
     */
    estimateStepDuration(method, category) {
        const baseDurations = {
            [DataCollectionMethod.INTERVIEW]: 45,
            [DataCollectionMethod.DOCUMENT_ANALYSIS]: 30,
            [DataCollectionMethod.SYSTEM_INTEGRATION]: 60,
            [DataCollectionMethod.SURVEY]: 20,
            [DataCollectionMethod.OBSERVATION]: 90,
            [DataCollectionMethod.API_EXTRACTION]: 15,
            [DataCollectionMethod.DATABASE_QUERY]: 10,
            [DataCollectionMethod.FILE_UPLOAD]: 25
        };
        
        const categoryMultipliers = {
            [DataCategory.STRUCTURE]: 1.2,
            [DataCategory.PROCESSES]: 1.5,
            [DataCategory.TECHNOLOGY]: 1.0,
            [DataCategory.FINANCIAL]: 1.3,
            [DataCategory.HUMAN_RESOURCES]: 1.1,
            [DataCategory.OPERATIONS]: 1.4,
            [DataCategory.COMPLIANCE]: 1.6,
            [DataCategory.STRATEGIC]: 1.3,
            [DataCategory.PERFORMANCE]: 1.0,
            [DataCategory.STAKEHOLDERS]: 1.2
        };
        
        const baseDuration = baseDurations[method] || 30;
        const multiplier = categoryMultipliers[category] || 1.0;
        
        return Math.round(baseDuration * multiplier);
    }
    
    /**
     * Calculate step priority
     * @private
     * @param {string} category - Data category
     * @param {string} method - Collection method
     * @returns {string} Priority level
     */
    calculateStepPriority(category, method) {
        const criticalCategories = [DataCategory.STRUCTURE, DataCategory.FINANCIAL];
        const highReliabilityMethods = [DataCollectionMethod.SYSTEM_INTEGRATION, DataCollectionMethod.API_EXTRACTION];
        
        if (criticalCategories.includes(category)) {
            return 'high';
        }
        
        if (highReliabilityMethods.includes(method)) {
            return 'high';
        }
        
        return 'medium';
    }
    
    /**
     * Get step dependencies
     * @private
     * @param {string} category - Data category
     * @param {string} method - Collection method
     * @returns {Array} Dependencies
     */
    getStepDependencies(category, method) {
        const dependencies = {
            [DataCategory.PROCESSES]: [DataCategory.STRUCTURE],
            [DataCategory.PERFORMANCE]: [DataCategory.PROCESSES, DataCategory.STRUCTURE],
            [DataCategory.STAKEHOLDERS]: [DataCategory.STRUCTURE]
        };
        
        return dependencies[category] || [];
    }
    
    /**
     * Sort workflow steps by priority and dependencies
     * @private
     * @param {Array} steps - Workflow steps
     * @returns {Array} Sorted steps
     */
    sortWorkflowSteps(steps) {
        const priorityOrder = { 'high': 3, 'medium': 2, 'low': 1 };
        
        return steps.sort((a, b) => {
            // First sort by priority
            const priorityDiff = priorityOrder[b.priority] - priorityOrder[a.priority];
            if (priorityDiff !== 0) return priorityDiff;
            
            // Then by dependencies (fewer dependencies first)
            return a.dependencies.length - b.dependencies.length;
        });
    }
    
    /**
     * Update session progress and next steps
     * @private
     * @param {Object} session - Collection session
     * @param {string} category - Completed category
     * @param {Object} validationResult - Validation result
     */
    updateSessionProgress(session, category, validationResult) {
        // Update category progress
        const categoryProgress = session.progress.categories[category];
        if (categoryProgress) {
            categoryProgress.status = 'completed';
            categoryProgress.progress = 100;
            categoryProgress.quality = validationResult.quality;
            categoryProgress.dataPoints = validationResult.dataPoints || 1;
            categoryProgress.validationsPassed = validationResult.valid ? 1 : 0;
        }
        
        // Update overall progress
        const categories = Object.keys(session.progress.categories);
        const completedCategories = categories.filter(cat => 
            session.progress.categories[cat].status === 'completed'
        );
        
        session.progress.overallProgress = Math.round((completedCategories.length / categories.length) * 100);
        
        // Calculate overall quality score
        session.progress.qualityScore = this.calculateOverallQualityScore(session);
    }
    
    /**
     * Update next steps for session
     * @private
     * @param {Object} session - Collection session
     */
    updateNextSteps(session) {
        if (!session.workflow) return;
        
        const completedStepIds = session.completedSteps.map(step => step.id || step);
        const pendingSteps = session.workflow.steps.filter(step => 
            !completedStepIds.includes(step.id) && step.status !== 'completed'
        );
        
        // Get next 3 steps that have no unmet dependencies
        session.nextSteps = pendingSteps
            .filter(step => {
                return step.dependencies.every(dep => 
                    session.collectedData.has(dep) || completedStepIds.includes(dep)
                );
            })
            .slice(0, 3);
    }
    
    /**
     * Validate session completion
     * @private
     * @param {Object} session - Collection session
     * @returns {Object} Completion validation result
     */
    validateSessionCompletion(session) {
        const { strategy } = session;
        const collectedCategories = Array.from(session.collectedData.keys());
        
        // Check required data
        const missingRequired = strategy.requiredData.filter(dataType => 
            !collectedCategories.includes(dataType)
        );
        
        if (missingRequired.length > 0) {
            return {
                isComplete: false,
                reason: `Missing required data: ${missingRequired.join(', ')}`
            };
        }
        
        // Check quality threshold
        const qualityScore = this.calculateOverallQualityScore(session);
        if (qualityScore < this.config.qualityThreshold) {
            return {
                isComplete: false,
                reason: `Quality score ${qualityScore.toFixed(2)} below threshold ${this.config.qualityThreshold}`
            };
        }
        
        return { isComplete: true };
    }
    
    /**
     * Generate organization profile from session data
     * @private
     * @param {Object} session - Collection session
     * @returns {Object} Organization profile
     */
    generateOrganizationProfile(session) {
        const profile = {
            organizationId: session.organizationId,
            organizationType: session.organizationType,
            collectionSessionId: session.id,
            createdAt: new Date().toISOString(),
            qualityScore: this.calculateOverallQualityScore(session),
            completeness: session.progress.overallProgress / 100,
            dataCategories: {}
        };
        
        // Process collected data into profile structure
        for (const [category, data] of session.collectedData) {
            profile.dataCategories[category] = {
                data: data.data,
                quality: data._metadata?.quality,
                confidence: data._metadata?.confidence,
                method: data._metadata?.method,
                collectedAt: data._metadata?.collectedAt
            };
            
            // Add data to top level for easy access
            if (category === DataCategory.STRUCTURE) {
                profile.basic_info = data.data;
            }
        }
        
        return profile;
    }
    
    /**
     * Calculate quality metrics for session
     * @private
     * @param {Object} session - Collection session
     * @returns {Object} Quality metrics
     */
    calculateQualityMetrics(session) {
        const categories = Object.keys(session.progress.categories);
        const metrics = {
            overallScore: this.calculateOverallQualityScore(session),
            completeness: session.progress.overallProgress / 100,
            categoryScores: {},
            reliability: 0,
            confidence: 0
        };
        
        let totalConfidence = 0;
        let confidenceCount = 0;
        
        for (const category of categories) {
            const categoryData = session.collectedData.get(category);
            if (categoryData) {
                const quality = this.qualityToValue(session.progress.categories[category].quality);
                metrics.categoryScores[category] = quality;
                
                if (categoryData._metadata?.confidence) {
                    totalConfidence += categoryData._metadata.confidence;
                    confidenceCount++;
                }
            }
        }
        
        metrics.confidence = confidenceCount > 0 ? totalConfidence / confidenceCount : 0;
        metrics.reliability = (metrics.overallScore + metrics.confidence) / 2;
        
        return metrics;
    }
    
    /**
     * Estimate completion time for session
     * @private
     * @param {Object} session - Collection session
     * @returns {Object} Time estimation
     */
    estimateCompletionTime(session) {
        if (!session.workflow || session.progress.overallProgress === 100) {
            return null;
        }
        
        const remainingSteps = session.workflow.steps.filter(step => 
            step.status !== 'completed'
        );
        
        const remainingMinutes = remainingSteps.reduce((total, step) => 
            total + (step.estimatedDuration || 30), 0
        );
        
        return {
            remainingMinutes,
            estimatedCompletion: new Date(Date.now() + remainingMinutes * 60000).toISOString(),
            remainingSteps: remainingSteps.length
        };
    }
    
    /**
     * Get category weight for scoring
     * @private
     * @param {string} category - Data category
     * @returns {number} Weight multiplier
     */
    getCategoryWeight(category) {
        const weights = {
            [DataCategory.STRUCTURE]: 1.5,
            [DataCategory.PROCESSES]: 1.3,
            [DataCategory.TECHNOLOGY]: 1.0,
            [DataCategory.FINANCIAL]: 1.4,
            [DataCategory.HUMAN_RESOURCES]: 1.1,
            [DataCategory.OPERATIONS]: 1.2,
            [DataCategory.COMPLIANCE]: 1.3,
            [DataCategory.STRATEGIC]: 1.2,
            [DataCategory.PERFORMANCE]: 1.1,
            [DataCategory.STAKEHOLDERS]: 1.0
        };
        
        return weights[category] || 1.0;
    }
}

export default OrganizationDataCollector;