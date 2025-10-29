#!/usr/bin/env node
/**
 * NASH 4.0 Digital Twin MCP Server
 * Desktop Extension Edition
 * 
 * This is the packaged version for .dxt distribution
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
    CallToolRequestSchema,
    ListResourcesRequestSchema,
    ListPromptsRequestSchema,
    GetPromptRequestSchema,
    ReadResourceRequestSchema,
    ListToolsRequestSchema,
    ErrorCode,
    McpError
} from '@modelcontextprotocol/sdk/types.js';

// Import core functionality
import { DigitalTwinEngine } from './digital-twin-engine.js';
import { SimulationRouter } from './simulation-router.js';
import { OrganizationAnalyzer } from './organization-analyzer.js';

/**
 * Digital Twin MCP Server for Desktop Extension
 */
class DigitalTwinMCPServer {
    constructor() {
        this.server = new Server(
            {
                name: 'nash-digital-twin',
                version: '3.0.0'
            },
            {
                capabilities: {
                    tools: {},
                    resources: {},
                    prompts: {}
                }
            }
        );

        // Initialize engines
        this.digitalTwinEngine = new DigitalTwinEngine();
        this.simulationRouter = new SimulationRouter();
        this.organizationAnalyzer = new OrganizationAnalyzer();
        
        // Store configuration from manifest
        this.config = {};
        
        this.setupHandlers();
    }

    setupHandlers() {
        // Handle configuration updates
        this.server.setRequestHandler('config/update', async (request) => {
            this.config = request.params.config || {};
            await this.initializeWithConfig();
            return { success: true };
        });

        // List available tools
        this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
            tools: [
                {
                    name: 'create_digital_twin',
                    description: 'Create a new digital twin of an organization',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            name: {
                                type: 'string',
                                description: 'Organization name'
                            },
                            type: {
                                type: 'string',
                                enum: ['nonprofit', 'foundation', 'charity', 'ngo', 'social_enterprise'],
                                description: 'Organization type'
                            },
                            budget: {
                                type: 'number',
                                description: 'Annual budget in USD'
                            },
                            staff_count: {
                                type: 'integer',
                                description: 'Number of staff members'
                            },
                            mission: {
                                type: 'string',
                                description: 'Organization mission statement'
                            }
                        },
                        required: ['name', 'type']
                    }
                },
                {
                    name: 'run_simulation',
                    description: 'Run simulation experiment (1 of 30 available)',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            twin_id: {
                                type: 'string',
                                description: 'Digital twin ID'
                            },
                            experiment: {
                                type: 'string',
                                enum: [
                                    // External Adapters (4)
                                    'donor_queue_optimization', 'volunteer_behavior_modeling',
                                    'need_forecasting', 'hybrid_system_simulation',
                                    // Digital Twin Scenarios (22)
                                    'operational_efficiency', 'resource_allocation',
                                    'crisis_response', 'growth_planning', 'budget_optimization',
                                    'capacity_planning', 'risk_assessment', 'impact_measurement',
                                    'stakeholder_engagement', 'volunteer_management',
                                    'donor_retention', 'program_effectiveness', 'compliance_check',
                                    'partnership_opportunities', 'innovation_potential',
                                    'sustainability_analysis', 'digital_transformation',
                                    'talent_optimization', 'communication_strategy',
                                    'fundraising_optimization', 'service_delivery',
                                    'community_impact',
                                    // Internal Engines (4)
                                    'theory_of_change', 'capacity_sweep',
                                    'optimal_routing', 'business_continuity'
                                ],
                                description: 'Experiment to run'
                            },
                            parameters: {
                                type: 'object',
                                description: 'Simulation parameters'
                            },
                            duration: {
                                type: 'integer',
                                description: 'Simulation duration in days',
                                default: 365
                            }
                        },
                        required: ['twin_id', 'experiment']
                    }
                },
                {
                    name: 'analyze_organization',
                    description: 'Perform AI-driven organizational analysis',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            twin_id: {
                                type: 'string',
                                description: 'Digital twin ID'
                            },
                            analysis_type: {
                                type: 'string',
                                enum: ['health', 'efficiency', 'impact', 'risk', 'opportunities'],
                                description: 'Type of analysis'
                            },
                            depth: {
                                type: 'string',
                                enum: ['quick', 'standard', 'deep'],
                                default: 'standard'
                            }
                        },
                        required: ['twin_id', 'analysis_type']
                    }
                },
                {
                    name: 'predict_trends',
                    description: 'Predict organizational trends',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            twin_id: {
                                type: 'string',
                                description: 'Digital twin ID'
                            },
                            metric: {
                                type: 'string',
                                enum: ['donations', 'volunteers', 'impact', 'costs', 'beneficiaries'],
                                description: 'Metric to predict'
                            },
                            horizon: {
                                type: 'integer',
                                description: 'Prediction horizon in months',
                                default: 12
                            }
                        },
                        required: ['twin_id', 'metric']
                    }
                },
                {
                    name: 'optimize_parameters',
                    description: 'Optimize organizational parameters',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            twin_id: {
                                type: 'string',
                                description: 'Digital twin ID'
                            },
                            objective: {
                                type: 'string',
                                enum: ['maximize_impact', 'minimize_costs', 'optimize_efficiency', 'balance_all'],
                                description: 'Optimization objective'
                            },
                            constraints: {
                                type: 'object',
                                properties: {
                                    max_budget: { type: 'number' },
                                    min_staff: { type: 'integer' },
                                    max_risk: { type: 'number' }
                                }
                            }
                        },
                        required: ['twin_id', 'objective']
                    }
                },
                {
                    name: 'get_metrics',
                    description: 'Get current metrics for a digital twin',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            twin_id: {
                                type: 'string',
                                description: 'Digital twin ID'
                            }
                        },
                        required: ['twin_id']
                    }
                },
                {
                    name: 'list_twins',
                    description: 'List all digital twins',
                    inputSchema: {
                        type: 'object',
                        properties: {}
                    }
                },
                {
                    name: 'generate_report',
                    description: 'Generate comprehensive report',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            twin_id: {
                                type: 'string',
                                description: 'Digital twin ID'
                            },
                            report_type: {
                                type: 'string',
                                enum: ['executive', 'operational', 'financial', 'impact', 'comprehensive'],
                                description: 'Type of report',
                                default: 'comprehensive'
                            },
                            format: {
                                type: 'string',
                                enum: ['markdown', 'json', 'html'],
                                default: 'markdown'
                            }
                        },
                        required: ['twin_id']
                    }
                }
            ]
        }));

        // Handle tool calls
        this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
            const { name, arguments: args } = request.params;

            try {
                let result;
                
                switch (name) {
                    case 'create_digital_twin':
                        result = await this.digitalTwinEngine.createTwin(args);
                        break;
                        
                    case 'run_simulation':
                        result = await this.simulationRouter.runExperiment(
                            args.twin_id,
                            args.experiment,
                            args.parameters,
                            args.duration
                        );
                        break;
                        
                    case 'analyze_organization':
                        result = await this.organizationAnalyzer.analyze(
                            args.twin_id,
                            args.analysis_type,
                            args.depth
                        );
                        break;
                        
                    case 'predict_trends':
                        result = await this.organizationAnalyzer.predictTrends(
                            args.twin_id,
                            args.metric,
                            args.horizon
                        );
                        break;
                        
                    case 'optimize_parameters':
                        result = await this.organizationAnalyzer.optimize(
                            args.twin_id,
                            args.objective,
                            args.constraints
                        );
                        break;
                        
                    case 'get_metrics':
                        result = await this.digitalTwinEngine.getMetrics(args.twin_id);
                        break;
                        
                    case 'list_twins':
                        result = await this.digitalTwinEngine.listTwins();
                        break;
                        
                    case 'generate_report':
                        result = await this.digitalTwinEngine.generateReport(
                            args.twin_id,
                            args.report_type,
                            args.format
                        );
                        break;
                        
                    default:
                        throw new McpError(ErrorCode.MethodNotFound, `Unknown tool: ${name}`);
                }

                return {
                    content: [
                        {
                            type: 'text',
                            text: typeof result === 'string' ? result : JSON.stringify(result, null, 2)
                        }
                    ]
                };
                
            } catch (error) {
                throw new McpError(ErrorCode.InternalError, error.message);
            }
        });

        // List resources
        this.server.setRequestHandler(ListResourcesRequestSchema, async () => ({
            resources: [
                {
                    uri: 'twin://documentation',
                    name: 'Platform Documentation',
                    description: 'Complete documentation for Digital Twin platform',
                    mimeType: 'text/markdown'
                },
                {
                    uri: 'twin://templates',
                    name: 'Organization Templates',
                    description: 'Pre-built templates for different organization types',
                    mimeType: 'application/json'
                },
                {
                    uri: 'twin://experiments',
                    name: 'Experiment Catalog',
                    description: 'Detailed information about all 30 experiments',
                    mimeType: 'application/json'
                },
                {
                    uri: 'twin://metrics',
                    name: 'Metrics Dictionary',
                    description: 'Description of all available metrics',
                    mimeType: 'application/json'
                }
            ]
        }));

        // Read resources
        this.server.setRequestHandler(ReadResourceRequestSchema, async (request) => {
            const { uri } = request.params;
            
            let content;
            switch (uri) {
                case 'twin://documentation':
                    content = await this.getDocumentation();
                    break;
                case 'twin://templates':
                    content = await this.getTemplates();
                    break;
                case 'twin://experiments':
                    content = await this.getExperimentCatalog();
                    break;
                case 'twin://metrics':
                    content = await this.getMetricsDictionary();
                    break;
                default:
                    throw new McpError(ErrorCode.InvalidRequest, `Unknown resource: ${uri}`);
            }

            return {
                contents: [
                    {
                        uri,
                        mimeType: uri.includes('documentation') ? 'text/markdown' : 'application/json',
                        text: typeof content === 'string' ? content : JSON.stringify(content, null, 2)
                    }
                ]
            };
        });

        // List prompts
        this.server.setRequestHandler(ListPromptsRequestSchema, async () => ({
            prompts: [
                {
                    name: 'analyze_npo',
                    description: 'Analyze non-profit organization efficiency',
                    arguments: [
                        {
                            name: 'organization_name',
                            description: 'Name of the NPO',
                            required: true
                        }
                    ]
                },
                {
                    name: 'optimize_budget',
                    description: 'Optimize budget allocation for maximum impact',
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
                    description: 'Create crisis response scenarios',
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

        // Get prompt
        this.server.setRequestHandler(GetPromptRequestSchema, async (request) => {
            const { name, arguments: args } = request.params;
            
            let messages;
            switch (name) {
                case 'analyze_npo':
                    messages = [{
                        role: 'user',
                        content: {
                            type: 'text',
                            text: `Analyze the efficiency and effectiveness of ${args.organization_name}. Consider operational efficiency, financial health, impact measurement, and provide specific recommendations for improvement.`
                        }
                    }];
                    break;
                    
                case 'optimize_budget':
                    messages = [{
                        role: 'user',
                        content: {
                            type: 'text',
                            text: `Optimize budget allocation for maximum impact. Current budget: ${args.current_budget}. ${args.priorities ? `Priorities: ${args.priorities}` : ''} Provide specific allocation recommendations with expected ROI.`
                        }
                    }];
                    break;
                    
                case 'crisis_planning':
                    messages = [{
                        role: 'user',
                        content: {
                            type: 'text',
                            text: `Create a comprehensive crisis response plan for ${args.crisis_type}. Include immediate actions, resource allocation, communication strategy, and recovery timeline.`
                        }
                    }];
                    break;
                    
                default:
                    throw new McpError(ErrorCode.InvalidRequest, `Unknown prompt: ${name}`);
            }

            return { messages };
        });
    }

    async initializeWithConfig() {
        // Initialize with configuration from manifest
        if (this.config.organization_name) {
            await this.digitalTwinEngine.setDefaultOrganization(this.config.organization_name);
        }
        
        if (this.config.api_key) {
            await this.digitalTwinEngine.authenticate(this.config.api_key);
        }
        
        if (this.config.supabase_url && this.config.supabase_key) {
            await this.digitalTwinEngine.connectDatabase(
                this.config.supabase_url,
                this.config.supabase_key
            );
        }
        
        // Configure simulation adapters
        if (this.config.simulation_adapters) {
            await this.simulationRouter.configureAdapters(this.config.simulation_adapters);
        }
    }

    async getDocumentation() {
        return `# NASH 4.0 Digital Twin Platform

## Overview
Advanced Digital Twin simulation platform with 30 experiments for organizational modeling.

## Available Experiments

### External Simulation Adapters (4)
1. **Donor Queue Optimization** (SimPy) - Optimize donor service processes
2. **Volunteer Behavior Modeling** (Mesa) - Agent-based volunteer dynamics
3. **Need Forecasting** (EpiNow2) - Predict future resource needs
4. **Hybrid System Simulation** (AnyLogic) - Combined modeling approaches

### Digital Twin Scenarios (22)
Comprehensive organizational scenarios covering operations, finance, HR, and strategy.

### Internal Engines (4)
- Theory of Change modeling
- Capacity sweep analysis
- Optimal routing algorithms
- Business continuity planning

## Usage Examples

### Create a Digital Twin
\`\`\`
Create a digital twin for "Hope Foundation" with a budget of 5 million
\`\`\`

### Run Simulation
\`\`\`
Run crisis response simulation for twin_001
\`\`\`

### Generate Report
\`\`\`
Generate comprehensive report for the organization
\`\`\`
`;
    }

    async getTemplates() {
        return {
            nonprofit: {
                name: 'Standard Non-Profit',
                type: 'nonprofit',
                default_budget: 1000000,
                default_staff: 20,
                structure: {
                    departments: ['Programs', 'Fundraising', 'Admin', 'Finance'],
                    governance: 'Board of Directors'
                }
            },
            foundation: {
                name: 'Private Foundation',
                type: 'foundation',
                default_budget: 10000000,
                default_staff: 50,
                structure: {
                    departments: ['Grants', 'Programs', 'Investment', 'Admin'],
                    governance: 'Board of Trustees'
                }
            },
            charity: {
                name: 'Charitable Organization',
                type: 'charity',
                default_budget: 500000,
                default_staff: 10,
                structure: {
                    departments: ['Services', 'Fundraising', 'Volunteers'],
                    governance: 'Executive Committee'
                }
            }
        };
    }

    async getExperimentCatalog() {
        return {
            categories: {
                external_adapters: {
                    name: 'External Simulation Adapters',
                    experiments: [
                        {
                            id: 'donor_queue_optimization',
                            name: 'Donor Queue Optimization',
                            engine: 'SimPy',
                            description: 'Optimize donor service processes and reduce wait times',
                            duration: '2-5 minutes'
                        },
                        {
                            id: 'volunteer_behavior_modeling',
                            name: 'Volunteer Behavior Modeling',
                            engine: 'Mesa',
                            description: 'Model volunteer recruitment and retention dynamics',
                            duration: '3-7 minutes'
                        },
                        {
                            id: 'need_forecasting',
                            name: 'Need Forecasting',
                            engine: 'EpiNow2',
                            description: 'Predict future resource and service needs',
                            duration: '5-10 minutes'
                        },
                        {
                            id: 'hybrid_system_simulation',
                            name: 'Hybrid System Simulation',
                            engine: 'AnyLogic',
                            description: 'Combined multi-method simulation',
                            duration: '10-15 minutes'
                        }
                    ]
                },
                digital_twin_scenarios: {
                    name: 'Digital Twin Scenarios',
                    count: 22,
                    description: 'Comprehensive organizational modeling scenarios'
                },
                internal_engines: {
                    name: 'Internal Processing Engines',
                    experiments: [
                        {
                            id: 'theory_of_change',
                            name: 'Theory of Change',
                            description: 'Model organizational impact pathways'
                        },
                        {
                            id: 'capacity_sweep',
                            name: 'Capacity Sweep Analysis',
                            description: 'Analyze organizational capacity limits'
                        },
                        {
                            id: 'optimal_routing',
                            name: 'Optimal Resource Routing',
                            description: 'Optimize resource distribution paths'
                        },
                        {
                            id: 'business_continuity',
                            name: 'Business Continuity Planning',
                            description: 'Plan for operational disruptions'
                        }
                    ]
                }
            },
            total_experiments: 30
        };
    }

    async getMetricsDictionary() {
        return {
            organizational_health: {
                name: 'Organizational Health Score',
                range: '0-100',
                description: 'Overall health indicator combining multiple factors'
            },
            efficiency_ratio: {
                name: 'Operational Efficiency',
                range: '0-1',
                description: 'Ratio of outputs to inputs'
            },
            impact_score: {
                name: 'Social Impact Score',
                range: '0-100',
                description: 'Measured social impact on beneficiaries'
            },
            financial_sustainability: {
                name: 'Financial Sustainability Index',
                range: '0-10',
                description: 'Long-term financial viability'
            },
            risk_level: {
                name: 'Risk Assessment Level',
                range: 'Low/Medium/High',
                description: 'Current organizational risk level'
            }
        };
    }

    async start() {
        const transport = new StdioServerTransport();
        await this.server.connect(transport);
        console.error('NASH Digital Twin MCP Server running (Desktop Extension)');
    }
}

// Start server
if (import.meta.url === `file://${process.argv[1]}`) {
    const server = new DigitalTwinMCPServer();
    server.start().catch(console.error);
}