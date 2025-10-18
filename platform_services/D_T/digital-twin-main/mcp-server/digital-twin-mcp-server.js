/**
 * DIGITAL TWIN MCP SERVER
 * PARTNERSHIP EXCELLENCE STANDARDS COMPLIANT
 * 
 * Complete MCP (Model Context Protocol) server implementation for Digital Twin
 * Enables AI agents to interact with Digital Twin system through standardized protocol
 * 
 * Based on official MCP SDK: https://github.com/anthropics/model-context-protocol
 * 
 * NO MOCKS - PRODUCTION READY
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
    CallToolRequestSchema,
    ListResourcesRequestSchema,
    ListToolsRequestSchema,
    ReadResourceRequestSchema,
    ListPromptsRequestSchema,
    GetPromptRequestSchema
} from '@modelcontextprotocol/sdk/types.js';
import { z } from 'zod';
import { EventEmitter } from 'events';
import { createLogger } from '../utils/logger.js';
import { DigitalTwinModule } from '../src/index.js';
import { AIOrchestrator } from '../core/ai/ai-orchestrator.js';
import { DatabaseManager } from '../infrastructure/database/database-manager.js';
import { SecurityManager } from '../core/security/security-manager.js';
import { organizationAuth } from '../core/auth/organization-auth-manager.js';
import { supabaseIntegration } from '../infrastructure/database/supabase-integration.js';

/**
 * Digital Twin MCP Server
 * Provides tools and resources for AI agents to interact with Digital Twin system
 */
export class DigitalTwinMCPServer extends EventEmitter {
    constructor() {
        super();
        
        this.logger = createLogger('DigitalTwinMCPServer');
        this.server = new Server(
            {
                name: 'digital-twin-mcp',
                version: '2.0.0'
            },
            {
                capabilities: {
                    resources: {},
                    tools: {},
                    prompts: {}
                }
            }
        );
        
        // Initialize core modules
        this.digitalTwin = null;
        this.aiOrchestrator = null;
        this.database = null;
        this.security = null;
        this.organizationAuth = organizationAuth;
        this.supabaseIntegration = supabaseIntegration;
        
        // Auth state
        this.currentSession = null;
        this.currentOrganization = null;
        
        this.isInitialized = false;
        
        // Setup handlers
        this.setupHandlers();
    }
    
    /**
     * Initialize server and modules
     */
    async initialize() {
        try {
            this.logger.info('Initializing Digital Twin MCP Server');
            
            // Initialize auth first
            await this.organizationAuth.initialize();
            this.logger.info('Auth system initialized');
            
            // Initialize Supabase integration
            await this.supabaseIntegration.initialize();
            this.logger.info('Supabase integration initialized');
            
            // Initialize security
            this.security = new SecurityManager();
            await this.security.initialize();
            
            // Initialize database
            this.database = new DatabaseManager();
            await this.database.initialize();
            
            // Initialize AI orchestrator
            this.aiOrchestrator = new AIOrchestrator();
            await this.aiOrchestrator.initialize();
            
            // Initialize Digital Twin module
            this.digitalTwin = new DigitalTwinModule({
                database: this.database,
                security: this.security,
                ai: this.aiOrchestrator
            });
            await this.digitalTwin.initialize();
            
            this.isInitialized = true;
            this.logger.info('Digital Twin MCP Server initialized successfully');
            
            return true;
            
        } catch (error) {
            this.logger.error('Failed to initialize MCP server', error);
            throw error;
        }
    }
    
    /**
     * Setup MCP request handlers
     */
    setupHandlers() {
        // List available tools
        this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
            tools: [
                {
                    name: 'create_digital_twin',
                    description: 'Create a new digital twin for an organization',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            organizationId: {
                                type: 'string',
                                description: 'Unique identifier for the organization'
                            },
                            name: {
                                type: 'string',
                                description: 'Organization name'
                            },
                            type: {
                                type: 'string',
                                enum: ['non-profit', 'charity', 'foundation', 'association'],
                                description: 'Type of organization'
                            },
                            mission: {
                                type: 'string',
                                description: 'Organization mission statement'
                            },
                            size: {
                                type: 'number',
                                description: 'Number of employees'
                            },
                            annualBudget: {
                                type: 'number',
                                description: 'Annual budget in USD'
                            },
                            departments: {
                                type: 'array',
                                items: {
                                    type: 'object',
                                    properties: {
                                        name: { type: 'string' },
                                        staff_count: { type: 'number' },
                                        budget_allocation: { type: 'number' }
                                    }
                                },
                                description: 'List of departments'
                            }
                        },
                        required: ['organizationId', 'name', 'type']
                    }
                },
                {
                    name: 'run_simulation',
                    description: 'Run a simulation scenario on a digital twin',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            twinId: {
                                type: 'string',
                                description: 'Digital twin identifier'
                            },
                            scenario: {
                                type: 'string',
                                enum: [
                                    'budget_optimization',
                                    'crisis_management',
                                    'scaling_analysis',
                                    'efficiency_improvement',
                                    'grant_impact',
                                    'staff_reorganization'
                                ],
                                description: 'Simulation scenario type'
                            },
                            parameters: {
                                type: 'object',
                                description: 'Scenario-specific parameters'
                            },
                            timeHorizon: {
                                type: 'number',
                                description: 'Simulation time horizon in days',
                                default: 365
                            }
                        },
                        required: ['twinId', 'scenario']
                    }
                },
                {
                    name: 'analyze_organization',
                    description: 'Perform AI-powered analysis of organization',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            twinId: {
                                type: 'string',
                                description: 'Digital twin identifier'
                            },
                            analysisType: {
                                type: 'string',
                                enum: [
                                    'health_check',
                                    'efficiency',
                                    'financial',
                                    'impact',
                                    'risk',
                                    'opportunities'
                                ],
                                description: 'Type of analysis to perform'
                            },
                            depth: {
                                type: 'string',
                                enum: ['quick', 'standard', 'comprehensive'],
                                default: 'standard',
                                description: 'Analysis depth'
                            }
                        },
                        required: ['twinId', 'analysisType']
                    }
                },
                {
                    name: 'predict_trends',
                    description: 'Predict future trends using AI',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            twinId: {
                                type: 'string',
                                description: 'Digital twin identifier'
                            },
                            metrics: {
                                type: 'array',
                                items: { type: 'string' },
                                description: 'Metrics to predict'
                            },
                            horizon: {
                                type: 'number',
                                description: 'Prediction horizon in days',
                                default: 90
                            },
                            confidence: {
                                type: 'boolean',
                                description: 'Include confidence intervals',
                                default: true
                            }
                        },
                        required: ['twinId']
                    }
                },
                {
                    name: 'optimize_parameters',
                    description: 'Optimize organization parameters using AI',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            twinId: {
                                type: 'string',
                                description: 'Digital twin identifier'
                            },
                            objective: {
                                type: 'string',
                                enum: [
                                    'maximize_efficiency',
                                    'minimize_costs',
                                    'maximize_impact',
                                    'balance_all'
                                ],
                                description: 'Optimization objective'
                            },
                            constraints: {
                                type: 'object',
                                description: 'Optimization constraints'
                            }
                        },
                        required: ['twinId', 'objective']
                    }
                },
                {
                    name: 'get_metrics',
                    description: 'Get current metrics for a digital twin',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            twinId: {
                                type: 'string',
                                description: 'Digital twin identifier'
                            },
                            metricTypes: {
                                type: 'array',
                                items: { type: 'string' },
                                description: 'Types of metrics to retrieve'
                            },
                            timeRange: {
                                type: 'object',
                                properties: {
                                    start: { type: 'string', format: 'date-time' },
                                    end: { type: 'string', format: 'date-time' }
                                },
                                description: 'Time range for metrics'
                            }
                        },
                        required: ['twinId']
                    }
                },
                {
                    name: 'list_twins',
                    description: 'List all available digital twins',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            organizationId: {
                                type: 'string',
                                description: 'Filter by organization ID'
                            },
                            status: {
                                type: 'string',
                                enum: ['active', 'inactive', 'all'],
                                default: 'active',
                                description: 'Filter by status'
                            }
                        }
                    }
                },
                {
                    name: 'generate_report',
                    description: 'Generate comprehensive report for organization',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            twinId: {
                                type: 'string',
                                description: 'Digital twin identifier'
                            },
                            reportType: {
                                type: 'string',
                                enum: [
                                    'executive_summary',
                                    'financial_analysis',
                                    'impact_assessment',
                                    'risk_report',
                                    'recommendations',
                                    'comprehensive'
                                ],
                                description: 'Type of report to generate'
                            },
                            format: {
                                type: 'string',
                                enum: ['json', 'markdown', 'html'],
                                default: 'json',
                                description: 'Report format'
                            }
                        },
                        required: ['twinId', 'reportType']
                    }
                }
            ]
        }));
        
        // Handle tool calls
        this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
            if (!this.isInitialized) {
                throw new Error('Server not initialized');
            }
            
            const { name, arguments: args } = request.params;
            
            // Validate request with security manager
            const validation = await this.security.validateRequest({
                tool: name,
                arguments: args
            });
            
            if (!validation.valid) {
                throw new Error(`Security validation failed: ${validation.reason}`);
            }
            
            try {
                switch (name) {
                    case 'create_digital_twin':
                        return await this.handleCreateDigitalTwin(args);
                        
                    case 'run_simulation':
                        return await this.handleRunSimulation(args);
                        
                    case 'analyze_organization':
                        return await this.handleAnalyzeOrganization(args);
                        
                    case 'predict_trends':
                        return await this.handlePredictTrends(args);
                        
                    case 'optimize_parameters':
                        return await this.handleOptimizeParameters(args);
                        
                    case 'get_metrics':
                        return await this.handleGetMetrics(args);
                        
                    case 'list_twins':
                        return await this.handleListTwins(args);
                        
                    case 'generate_report':
                        return await this.handleGenerateReport(args);
                        
                    default:
                        throw new Error(`Unknown tool: ${name}`);
                }
            } catch (error) {
                this.logger.error(`Tool execution failed: ${name}`, error);
                throw error;
            }
        });
        
        // List available resources
        this.server.setRequestHandler(ListResourcesRequestSchema, async () => ({
            resources: [
                {
                    uri: 'twin://documentation',
                    name: 'Digital Twin Documentation',
                    description: 'Complete documentation for Digital Twin system',
                    mimeType: 'text/markdown'
                },
                {
                    uri: 'twin://templates/organization',
                    name: 'Organization Templates',
                    description: 'Templates for different organization types',
                    mimeType: 'application/json'
                },
                {
                    uri: 'twin://scenarios',
                    name: 'Simulation Scenarios',
                    description: 'Available simulation scenarios and parameters',
                    mimeType: 'application/json'
                },
                {
                    uri: 'twin://metrics/definitions',
                    name: 'Metrics Definitions',
                    description: 'Definitions of all available metrics',
                    mimeType: 'application/json'
                }
            ]
        }));
        
        // Read resource content
        this.server.setRequestHandler(ReadResourceRequestSchema, async (request) => {
            const { uri } = request.params;
            
            switch (uri) {
                case 'twin://documentation':
                    return {
                        contents: [{
                            uri,
                            mimeType: 'text/markdown',
                            text: this.getDocumentation()
                        }]
                    };
                    
                case 'twin://templates/organization':
                    return {
                        contents: [{
                            uri,
                            mimeType: 'application/json',
                            text: JSON.stringify(this.getOrganizationTemplates(), null, 2)
                        }]
                    };
                    
                case 'twin://scenarios':
                    return {
                        contents: [{
                            uri,
                            mimeType: 'application/json',
                            text: JSON.stringify(this.getScenarioDefinitions(), null, 2)
                        }]
                    };
                    
                case 'twin://metrics/definitions':
                    return {
                        contents: [{
                            uri,
                            mimeType: 'application/json',
                            text: JSON.stringify(this.getMetricsDefinitions(), null, 2)
                        }]
                    };
                    
                default:
                    throw new Error(`Unknown resource: ${uri}`);
            }
        });
        
        // List available prompts
        this.server.setRequestHandler(ListPromptsRequestSchema, async () => ({
            prompts: [
                {
                    name: 'analyze_npo',
                    description: 'Analyze a non-profit organization',
                    arguments: [
                        {
                            name: 'organization_name',
                            description: 'Name of the organization',
                            required: true
                        }
                    ]
                },
                {
                    name: 'optimize_budget',
                    description: 'Optimize organization budget allocation',
                    arguments: [
                        {
                            name: 'current_budget',
                            description: 'Current budget amount',
                            required: true
                        },
                        {
                            name: 'priorities',
                            description: 'List of priorities',
                            required: false
                        }
                    ]
                },
                {
                    name: 'crisis_planning',
                    description: 'Create crisis management plan',
                    arguments: [
                        {
                            name: 'crisis_type',
                            description: 'Type of crisis to plan for',
                            required: true
                        }
                    ]
                }
            ]
        }));
        
        // Get prompt content
        this.server.setRequestHandler(GetPromptRequestSchema, async (request) => {
            const { name, arguments: args } = request.params;
            
            switch (name) {
                case 'analyze_npo':
                    return {
                        messages: [
                            {
                                role: 'user',
                                content: {
                                    type: 'text',
                                    text: `Please analyze the non-profit organization "${args.organization_name}" using the Digital Twin system. Create a comprehensive analysis including health metrics, efficiency scores, and recommendations.`
                                }
                            }
                        ]
                    };
                    
                case 'optimize_budget':
                    return {
                        messages: [
                            {
                                role: 'user',
                                content: {
                                    type: 'text',
                                    text: `Optimize the budget allocation for an organization with a budget of ${args.current_budget}. ${args.priorities ? `Priorities: ${args.priorities}` : ''} Use the Digital Twin system to simulate different allocation strategies and recommend the optimal distribution.`
                                }
                            }
                        ]
                    };
                    
                case 'crisis_planning':
                    return {
                        messages: [
                            {
                                role: 'user',
                                content: {
                                    type: 'text',
                                    text: `Create a comprehensive crisis management plan for ${args.crisis_type}. Use the Digital Twin system to simulate the crisis scenario and develop mitigation strategies.`
                                }
                            }
                        ]
                    };
                    
                default:
                    throw new Error(`Unknown prompt: ${name}`);
            }
        });
    }
    
    /**
     * Tool handler: Create Digital Twin
     */
    async handleCreateDigitalTwin(args) {
        try {
            const result = await this.digitalTwin.createDigitalTwin(args);
            
            // Store in database
            await this.database.create('digital_twins', {
                twin_id: result.id,
                organization_id: args.organizationId,
                name: args.name,
                configuration: args,
                state: result.state,
                metrics: result.metrics
            });
            
            return {
                content: [
                    {
                        type: 'text',
                        text: `Digital twin created successfully for ${args.name}`
                    },
                    {
                        type: 'text',
                        text: JSON.stringify(result, null, 2)
                    }
                ]
            };
        } catch (error) {
            throw new Error(`Failed to create digital twin: ${error.message}`);
        }
    }
    
    /**
     * Tool handler: Run Simulation
     */
    async handleRunSimulation(args) {
        try {
            // Get twin data
            const twin = await this.database.find('digital_twins', { twin_id: args.twinId });
            if (!twin || twin.length === 0) {
                throw new Error(`Twin not found: ${args.twinId}`);
            }
            
            // Run simulation
            const result = await this.digitalTwin.runSimulation(
                args.twinId,
                args.scenario,
                args.parameters
            );
            
            // Store results
            await this.database.create('simulations', {
                simulation_id: result.id,
                twin_id: args.twinId,
                scenario: args.scenario,
                parameters: args.parameters,
                results: result,
                status: 'completed'
            });
            
            return {
                content: [
                    {
                        type: 'text',
                        text: `Simulation completed: ${args.scenario}`
                    },
                    {
                        type: 'text',
                        text: JSON.stringify(result, null, 2)
                    }
                ]
            };
        } catch (error) {
            throw new Error(`Simulation failed: ${error.message}`);
        }
    }
    
    /**
     * Tool handler: Analyze Organization
     */
    async handleAnalyzeOrganization(args) {
        try {
            // Get twin data
            const twin = await this.database.find('digital_twins', { twin_id: args.twinId });
            if (!twin || twin.length === 0) {
                throw new Error(`Twin not found: ${args.twinId}`);
            }
            
            // Perform AI analysis
            const analysis = await this.aiOrchestrator.processTask({
                type: 'analyze',
                data: {
                    twin: twin[0],
                    analysisType: args.analysisType,
                    depth: args.depth
                }
            });
            
            return {
                content: [
                    {
                        type: 'text',
                        text: `Analysis complete: ${args.analysisType}`
                    },
                    {
                        type: 'text',
                        text: JSON.stringify(analysis, null, 2)
                    }
                ]
            };
        } catch (error) {
            throw new Error(`Analysis failed: ${error.message}`);
        }
    }
    
    /**
     * Tool handler: Predict Trends
     */
    async handlePredictTrends(args) {
        try {
            // Get historical metrics
            const metrics = await this.database.find('metrics', {
                twin_id: args.twinId
            }, {
                sort: { timestamp: -1 },
                limit: 100
            });
            
            // Prepare data for prediction
            const historicalData = {};
            for (const metric of metrics) {
                if (!historicalData[metric.metric_type]) {
                    historicalData[metric.metric_type] = [];
                }
                historicalData[metric.metric_type].push(metric.value);
            }
            
            // AI prediction
            const prediction = await this.aiOrchestrator.processTask({
                type: 'predict',
                data: {
                    historical: historicalData,
                    horizon: args.horizon,
                    metrics: args.metrics
                }
            });
            
            return {
                content: [
                    {
                        type: 'text',
                        text: `Trend prediction for next ${args.horizon} days`
                    },
                    {
                        type: 'text',
                        text: JSON.stringify(prediction, null, 2)
                    }
                ]
            };
        } catch (error) {
            throw new Error(`Prediction failed: ${error.message}`);
        }
    }
    
    /**
     * Tool handler: Optimize Parameters
     */
    async handleOptimizeParameters(args) {
        try {
            // Get current parameters
            const twin = await this.database.find('digital_twins', { twin_id: args.twinId });
            if (!twin || twin.length === 0) {
                throw new Error(`Twin not found: ${args.twinId}`);
            }
            
            // AI optimization
            const optimization = await this.aiOrchestrator.processTask({
                type: 'optimize',
                parameters: {
                    current: twin[0].configuration,
                    objective: args.objective,
                    constraints: args.constraints
                }
            });
            
            return {
                content: [
                    {
                        type: 'text',
                        text: `Optimization complete: ${args.objective}`
                    },
                    {
                        type: 'text',
                        text: JSON.stringify(optimization, null, 2)
                    }
                ]
            };
        } catch (error) {
            throw new Error(`Optimization failed: ${error.message}`);
        }
    }
    
    /**
     * Tool handler: Get Metrics
     */
    async handleGetMetrics(args) {
        try {
            const query = { twin_id: args.twinId };
            
            if (args.metricTypes && args.metricTypes.length > 0) {
                query.metric_type = { $in: args.metricTypes };
            }
            
            if (args.timeRange) {
                query.timestamp = {
                    $gte: new Date(args.timeRange.start),
                    $lte: new Date(args.timeRange.end)
                };
            }
            
            const metrics = await this.database.find('metrics', query, {
                sort: { timestamp: -1 }
            });
            
            return {
                content: [
                    {
                        type: 'text',
                        text: `Found ${metrics.length} metrics`
                    },
                    {
                        type: 'text',
                        text: JSON.stringify(metrics, null, 2)
                    }
                ]
            };
        } catch (error) {
            throw new Error(`Failed to get metrics: ${error.message}`);
        }
    }
    
    /**
     * Tool handler: List Twins
     */
    async handleListTwins(args) {
        try {
            const query = {};
            
            if (args.organizationId) {
                query.organization_id = args.organizationId;
            }
            
            if (args.status && args.status !== 'all') {
                query.status = args.status;
            }
            
            const twins = await this.database.find('digital_twins', query);
            
            return {
                content: [
                    {
                        type: 'text',
                        text: `Found ${twins.length} digital twins`
                    },
                    {
                        type: 'text',
                        text: JSON.stringify(twins.map(t => ({
                            id: t.twin_id,
                            name: t.name,
                            organization: t.organization_id,
                            created: t.created_at
                        })), null, 2)
                    }
                ]
            };
        } catch (error) {
            throw new Error(`Failed to list twins: ${error.message}`);
        }
    }
    
    /**
     * Tool handler: Generate Report
     */
    async handleGenerateReport(args) {
        try {
            // Get twin data
            const twin = await this.database.find('digital_twins', { twin_id: args.twinId });
            if (!twin || twin.length === 0) {
                throw new Error(`Twin not found: ${args.twinId}`);
            }
            
            // Get recent simulations
            const simulations = await this.database.find('simulations', {
                twin_id: args.twinId
            }, {
                sort: { created_at: -1 },
                limit: 10
            });
            
            // Get metrics
            const metrics = await this.database.find('metrics', {
                twin_id: args.twinId
            }, {
                sort: { timestamp: -1 },
                limit: 50
            });
            
            // Generate report using AI
            const report = await this.aiOrchestrator.processTask({
                type: 'generate',
                prompt: `Generate a ${args.reportType} report for the organization`,
                data: {
                    twin: twin[0],
                    simulations,
                    metrics,
                    reportType: args.reportType
                }
            });
            
            // Format based on requested format
            let formattedReport;
            switch (args.format) {
                case 'markdown':
                    formattedReport = this.formatReportAsMarkdown(report);
                    break;
                case 'html':
                    formattedReport = this.formatReportAsHTML(report);
                    break;
                default:
                    formattedReport = report;
            }
            
            return {
                content: [
                    {
                        type: 'text',
                        text: `Generated ${args.reportType} report`
                    },
                    {
                        type: 'text',
                        text: typeof formattedReport === 'string' 
                            ? formattedReport 
                            : JSON.stringify(formattedReport, null, 2)
                    }
                ]
            };
        } catch (error) {
            throw new Error(`Report generation failed: ${error.message}`);
        }
    }
    
    /**
     * Get documentation content
     */
    getDocumentation() {
        return `# Digital Twin MCP Server Documentation

## Overview
The Digital Twin MCP Server provides AI agents with tools to create, manage, and analyze digital twins of NPO organizations.

## Available Tools

### create_digital_twin
Creates a new digital twin for an organization with complete configuration.

### run_simulation
Runs various simulation scenarios to predict outcomes and test strategies.

### analyze_organization
Performs AI-powered analysis of organization health, efficiency, and opportunities.

### predict_trends
Uses AI to predict future trends based on historical data.

### optimize_parameters
Optimizes organization parameters to achieve specific objectives.

### get_metrics
Retrieves current and historical metrics for analysis.

### list_twins
Lists all available digital twins with filtering options.

### generate_report
Generates comprehensive reports in various formats.

## Simulation Scenarios

- **budget_optimization**: Optimize budget allocation across departments
- **crisis_management**: Test crisis response and recovery strategies
- **scaling_analysis**: Analyze scaling opportunities and challenges
- **efficiency_improvement**: Identify and implement efficiency gains
- **grant_impact**: Assess impact of grant funding
- **staff_reorganization**: Optimize staff structure and allocation

## Security
All requests are validated through the Security Manager with:
- Input sanitization
- Rate limiting
- Audit logging
- Token-based authentication

## AI Integration
The system uses advanced AI for:
- Predictive analytics
- Optimization algorithms
- Natural language processing
- Pattern recognition
- Anomaly detection`;
    }
    
    /**
     * Get organization templates
     */
    getOrganizationTemplates() {
        return {
            templates: [
                {
                    type: 'charity',
                    name: 'Standard Charity Template',
                    structure: {
                        departments: [
                            { name: 'Programs', staff_percentage: 0.5 },
                            { name: 'Fundraising', staff_percentage: 0.2 },
                            { name: 'Administration', staff_percentage: 0.2 },
                            { name: 'Volunteer Coordination', staff_percentage: 0.1 }
                        ],
                        metrics: ['donation_efficiency', 'program_impact', 'volunteer_hours']
                    }
                },
                {
                    type: 'foundation',
                    name: 'Grant-Making Foundation Template',
                    structure: {
                        departments: [
                            { name: 'Grant Management', staff_percentage: 0.4 },
                            { name: 'Research & Evaluation', staff_percentage: 0.3 },
                            { name: 'Operations', staff_percentage: 0.2 },
                            { name: 'Communications', staff_percentage: 0.1 }
                        ],
                        metrics: ['grant_effectiveness', 'application_processing', 'impact_measurement']
                    }
                }
            ]
        };
    }
    
    /**
     * Get scenario definitions
     */
    getScenarioDefinitions() {
        return {
            scenarios: {
                budget_optimization: {
                    description: 'Optimize budget allocation across departments',
                    parameters: {
                        optimization_goal: ['efficiency', 'impact', 'balanced'],
                        constraints: ['minimum_staffing', 'program_requirements'],
                        time_horizon: 'days'
                    }
                },
                crisis_management: {
                    description: 'Simulate crisis scenarios and response',
                    parameters: {
                        crisis_type: ['funding_loss', 'staff_shortage', 'demand_spike'],
                        severity: ['mild', 'moderate', 'severe'],
                        response_strategy: ['aggressive', 'conservative', 'adaptive']
                    }
                }
            }
        };
    }
    
    /**
     * Get metrics definitions
     */
    getMetricsDefinitions() {
        return {
            metrics: {
                efficiency: {
                    description: 'Operational efficiency score',
                    calculation: 'output / input',
                    range: [0, 1],
                    unit: 'ratio'
                },
                impact: {
                    description: 'Social impact measurement',
                    calculation: 'beneficiaries * outcome_quality',
                    range: [0, 100],
                    unit: 'score'
                },
                financial_health: {
                    description: 'Financial stability indicator',
                    calculation: 'reserves / monthly_expenses',
                    range: [0, 12],
                    unit: 'months'
                }
            }
        };
    }
    
    /**
     * Format report as Markdown
     */
    formatReportAsMarkdown(report) {
        return `# ${report.title || 'Organization Report'}

## Executive Summary
${report.summary || 'No summary available'}

## Key Findings
${report.findings ? report.findings.map(f => `- ${f}`).join('\n') : 'No findings'}

## Recommendations
${report.recommendations ? report.recommendations.map(r => `1. ${r}`).join('\n') : 'No recommendations'}

## Metrics
${report.metrics ? JSON.stringify(report.metrics, null, 2) : 'No metrics'}

---
*Generated by Digital Twin MCP Server*`;
    }
    
    /**
     * Format report as HTML
     */
    formatReportAsHTML(report) {
        return `<!DOCTYPE html>
<html>
<head>
    <title>${report.title || 'Organization Report'}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        h1 { color: #333; }
        h2 { color: #666; }
        ul { line-height: 1.6; }
    </style>
</head>
<body>
    <h1>${report.title || 'Organization Report'}</h1>
    <h2>Executive Summary</h2>
    <p>${report.summary || 'No summary available'}</p>
    <h2>Key Findings</h2>
    <ul>${report.findings ? report.findings.map(f => `<li>${f}</li>`).join('') : '<li>No findings</li>'}</ul>
    <h2>Recommendations</h2>
    <ol>${report.recommendations ? report.recommendations.map(r => `<li>${r}</li>`).join('') : '<li>No recommendations</li>'}</ol>
</body>
</html>`;
    }
    
    /**
     * Start the MCP server
     */
    async start() {
        try {
            // Initialize modules
            await this.initialize();
            
            // Create transport
            const transport = new StdioServerTransport();
            
            // Connect server to transport
            await this.server.connect(transport);
            
            this.logger.info('Digital Twin MCP Server started successfully');
            console.error('Digital Twin MCP Server is running');
            
        } catch (error) {
            this.logger.error('Failed to start MCP server', error);
            console.error('Failed to start server:', error);
            process.exit(1);
        }
    }
}

// Start server if run directly
if (import.meta.url === `file://${process.argv[1]}`) {
    const server = new DigitalTwinMCPServer();
    server.start().catch(console.error);
}

export default DigitalTwinMCPServer;