/**
 * DIGITAL TWIN MCP SERVER WITH AUTHENTICATION
 * Complete MCP server with full auth integration
 * 
 * @module DigitalTwinMCPServerAuth
 * @version 2.0.0
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
import { organizationAuth } from '../core/auth/organization-auth-manager.js';
import { supabaseIntegration } from '../infrastructure/database/supabase-integration.js';
import { DigitalTwinModule } from '../integrated-organization-twin.js';

export class DigitalTwinMCPServerAuth extends EventEmitter {
    constructor() {
        super();
        
        this.server = new Server(
            {
                name: 'digital-twin-mcp-auth',
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
        
        this.organizationAuth = organizationAuth;
        this.supabaseIntegration = supabaseIntegration;
        this.digitalTwin = null;
        
        // Auth state
        this.authToken = null;
        this.apiKey = null;
        
        this.setupHandlers();
    }
    
    /**
     * Initialize server with auth
     */
    async initialize() {
        try {
            console.log('Initializing MCP Server with Authentication...');
            
            // Initialize auth
            await this.organizationAuth.initialize();
            console.log(' Auth system initialized');
            
            // Initialize database
            await this.supabaseIntegration.initialize();
            console.log(' Database initialized');
            
            // Initialize Digital Twin
            this.digitalTwin = new DigitalTwinModule();
            await this.digitalTwin.initialize();
            console.log(' Digital Twin module initialized');
            
            return true;
        } catch (error) {
            console.error('Initialization failed:', error);
            throw error;
        }
    }
    
    /**
     * Check if user is authenticated
     */
    isAuthenticated() {
        // Check session auth
        if (this.organizationAuth.isAuthenticated()) {
            return true;
        }
        
        // Check API key auth
        if (this.apiKey) {
            return true;
        }
        
        return false;
    }
    
    /**
     * Authenticate with credentials
     */
    async authenticate(credentials) {
        try {
            if (credentials.type === 'password') {
                const result = await this.organizationAuth.signIn(
                    credentials.email,
                    credentials.password
                );
                this.authToken = result.session.access_token;
                return {
                    success: true,
                    organization: result.organization
                };
            } else if (credentials.type === 'api_key') {
                // Validate API key
                const keyHash = crypto.createHash('sha256').update(credentials.apiKey).digest('hex');
                const { data } = await this.supabaseIntegration.client
                    .rpc('validate_api_key', { p_key_hash: keyHash });
                
                if (data && data[0]?.is_valid) {
                    this.apiKey = credentials.apiKey;
                    return {
                        success: true,
                        organizationId: data[0].organization_id
                    };
                }
                throw new Error('Invalid API key');
            }
        } catch (error) {
            return {
                success: false,
                error: error.message
            };
        }
    }
    
    /**
     * Setup request handlers
     */
    setupHandlers() {
        // List available tools (including auth tools)
        this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
            tools: [
                // Auth tools
                {
                    name: 'authenticate',
                    description: 'Authenticate with email/password or API key',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            type: {
                                type: 'string',
                                enum: ['password', 'api_key'],
                                description: 'Authentication type'
                            },
                            email: {
                                type: 'string',
                                description: 'Email (for password auth)'
                            },
                            password: {
                                type: 'string',
                                description: 'Password (for password auth)'
                            },
                            apiKey: {
                                type: 'string',
                                description: 'API key (for API key auth)'
                            }
                        },
                        required: ['type']
                    }
                },
                {
                    name: 'logout',
                    description: 'Logout current session',
                    inputSchema: {
                        type: 'object',
                        properties: {}
                    }
                },
                {
                    name: 'get_current_organization',
                    description: 'Get current organization profile',
                    inputSchema: {
                        type: 'object',
                        properties: {}
                    }
                },
                
                // Twin management tools (require auth)
                {
                    name: 'create_digital_twin',
                    description: 'Create a new digital twin for organization (requires auth)',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            name: {
                                type: 'string',
                                description: 'Name of the digital twin'
                            },
                            configuration: {
                                type: 'object',
                                description: 'Twin configuration'
                            }
                        },
                        required: ['name']
                    }
                },
                {
                    name: 'list_twins',
                    description: 'List organization digital twins (requires auth)',
                    inputSchema: {
                        type: 'object',
                        properties: {}
                    }
                },
                {
                    name: 'run_simulation',
                    description: 'Run simulation on digital twin (requires auth)',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            twinId: {
                                type: 'string',
                                description: 'Digital twin ID'
                            },
                            scenario: {
                                type: 'string',
                                enum: ['budget_optimization', 'crisis_management', 'scaling_analysis', 'efficiency_improvement'],
                                description: 'Simulation scenario'
                            },
                            parameters: {
                                type: 'object',
                                description: 'Scenario parameters'
                            }
                        },
                        required: ['twinId', 'scenario']
                    }
                },
                {
                    name: 'predict_trends',
                    description: 'Predict future trends (requires auth)',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            twinId: {
                                type: 'string',
                                description: 'Digital twin ID'
                            },
                            predictionType: {
                                type: 'string',
                                enum: ['budget_forecast', 'staff_turnover', 'grant_success', 'program_impact'],
                                description: 'Type of prediction'
                            },
                            horizon: {
                                type: 'number',
                                description: 'Prediction horizon in days'
                            }
                        },
                        required: ['twinId', 'predictionType']
                    }
                },
                {
                    name: 'get_metrics',
                    description: 'Get performance metrics (requires auth)',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            twinId: {
                                type: 'string',
                                description: 'Digital twin ID'
                            },
                            metricType: {
                                type: 'string',
                                description: 'Type of metrics to retrieve'
                            },
                            limit: {
                                type: 'number',
                                description: 'Number of metrics to return'
                            }
                        },
                        required: ['twinId']
                    }
                }
            ]
        }));
        
        // Handle tool calls
        this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
            const { name, arguments: args } = request.params;
            
            // Auth tools (don't require authentication)
            if (name === 'authenticate') {
                const result = await this.authenticate(args);
                return {
                    content: [{
                        type: 'text',
                        text: result.success 
                            ? `Authentication successful. Organization: ${result.organization?.name || 'N/A'}`
                            : `Authentication failed: ${result.error}`
                    }]
                };
            }
            
            if (name === 'logout') {
                await this.organizationAuth.signOut();
                this.authToken = null;
                this.apiKey = null;
                return {
                    content: [{
                        type: 'text',
                        text: 'Logged out successfully'
                    }]
                };
            }
            
            if (name === 'get_current_organization') {
                if (!this.isAuthenticated()) {
                    return {
                        content: [{
                            type: 'text',
                            text: 'Error: Authentication required. Please use the authenticate tool first.'
                        }]
                    };
                }
                
                const org = this.organizationAuth.getCurrentOrganization();
                return {
                    content: [{
                        type: 'text',
                        text: org ? JSON.stringify(org, null, 2) : 'No organization loaded'
                    }]
                };
            }
            
            // All other tools require authentication
            if (!this.isAuthenticated()) {
                return {
                    content: [{
                        type: 'text',
                        text: 'Error: Authentication required. Please use the authenticate tool first with your email/password or API key.'
                    }]
                };
            }
            
            // Get current organization
            const organization = this.organizationAuth.getCurrentOrganization();
            if (!organization && name !== 'list_twins') {
                return {
                    content: [{
                        type: 'text',
                        text: 'Error: No organization found. Please register or login.'
                    }]
                };
            }
            
            // Handle authenticated tools
            switch (name) {
                case 'create_digital_twin':
                    return await this.handleCreateDigitalTwin({
                        ...args,
                        organizationId: organization.id
                    });
                
                case 'list_twins':
                    return await this.handleListTwins(organization.id);
                
                case 'run_simulation':
                    return await this.handleRunSimulation(args);
                
                case 'predict_trends':
                    return await this.handlePredictTrends(args);
                
                case 'get_metrics':
                    return await this.handleGetMetrics(args);
                
                default:
                    throw new Error(`Unknown tool: ${name}`);
            }
        });
        
        // List resources
        this.server.setRequestHandler(ListResourcesRequestSchema, async () => ({
            resources: [
                {
                    uri: 'twin://documentation',
                    name: 'Digital Twin Documentation',
                    description: 'Complete documentation for the Digital Twin system',
                    mimeType: 'text/markdown'
                },
                {
                    uri: 'twin://auth-guide',
                    name: 'Authentication Guide',
                    description: 'How to authenticate and use the system',
                    mimeType: 'text/markdown'
                }
            ]
        }));
        
        // Read resources
        this.server.setRequestHandler(ReadResourceRequestSchema, async (request) => {
            const { uri } = request.params;
            
            switch (uri) {
                case 'twin://documentation':
                    return {
                        contents: [{
                            uri,
                            mimeType: 'text/markdown',
                            text: `# Digital Twin MCP Server

## Authentication Required
All operations require authentication. Use one of these methods:

### Password Authentication
\`\`\`
Use tool: authenticate
Arguments: {
  "type": "password",
  "email": "your@email.com",
  "password": "yourpassword"
}
\`\`\`

### API Key Authentication
\`\`\`
Use tool: authenticate
Arguments: {
  "type": "api_key",
  "apiKey": "dtw_your_api_key_here"
}
\`\`\`

## Available Operations (after authentication)
- Create and manage digital twins
- Run simulations
- Generate predictions
- Analyze metrics
- Generate reports

## Security
All data is encrypted and access is controlled by organization ownership.`
                        }]
                    };
                
                case 'twin://auth-guide':
                    return {
                        contents: [{
                            uri,
                            mimeType: 'text/markdown',
                            text: `# Authentication Guide

## Quick Start
1. First authenticate using the authenticate tool
2. Then you can use all other tools
3. Your session persists until you logout

## Getting an API Key
1. Login to the web interface
2. Go to Settings > API Keys
3. Create a new key with desired permissions
4. Use it with the authenticate tool

## Security Best Practices
- Never share your API keys
- Rotate keys regularly
- Use minimal required permissions
- Monitor key usage in dashboard`
                        }]
                    };
                
                default:
                    throw new Error(`Unknown resource: ${uri}`);
            }
        });
    }
    
    // Tool handlers
    async handleCreateDigitalTwin(args) {
        try {
            const twin = await this.supabaseIntegration.createDigitalTwin({
                twin_id: `twin_${Date.now()}_${Math.random().toString(36).substring(7)}`,
                organization_id: args.organizationId,
                name: args.name,
                configuration: args.configuration || {}
            });
            
            return {
                content: [{
                    type: 'text',
                    text: `Digital twin created successfully!\n${JSON.stringify(twin, null, 2)}`
                }]
            };
        } catch (error) {
            return {
                content: [{
                    type: 'text',
                    text: `Error creating twin: ${error.message}`
                }]
            };
        }
    }
    
    async handleListTwins(organizationId) {
        try {
            const twins = await this.supabaseIntegration.listDigitalTwins({
                organizationId
            });
            
            return {
                content: [{
                    type: 'text',
                    text: `Found ${twins.length} digital twins:\n${JSON.stringify(twins, null, 2)}`
                }]
            };
        } catch (error) {
            return {
                content: [{
                    type: 'text',
                    text: `Error listing twins: ${error.message}`
                }]
            };
        }
    }
    
    async handleRunSimulation(args) {
        try {
            const result = await this.supabaseIntegration.runSimulation(
                args.twinId,
                args.scenario,
                args.parameters || {}
            );
            
            return {
                content: [{
                    type: 'text',
                    text: `Simulation completed!\n${JSON.stringify(result, null, 2)}`
                }]
            };
        } catch (error) {
            return {
                content: [{
                    type: 'text',
                    text: `Error running simulation: ${error.message}`
                }]
            };
        }
    }
    
    async handlePredictTrends(args) {
        try {
            const prediction = await this.supabaseIntegration.createPrediction(
                args.twinId,
                args.predictionType,
                {
                    horizon: args.horizon || 30
                }
            );
            
            return {
                content: [{
                    type: 'text',
                    text: `Prediction generated!\n${JSON.stringify(prediction, null, 2)}`
                }]
            };
        } catch (error) {
            return {
                content: [{
                    type: 'text',
                    text: `Error generating prediction: ${error.message}`
                }]
            };
        }
    }
    
    async handleGetMetrics(args) {
        try {
            const metrics = await this.supabaseIntegration.getMetrics(
                args.twinId,
                {
                    metricType: args.metricType,
                    limit: args.limit || 100
                }
            );
            
            return {
                content: [{
                    type: 'text',
                    text: `Retrieved ${metrics.length} metrics:\n${JSON.stringify(metrics, null, 2)}`
                }]
            };
        } catch (error) {
            return {
                content: [{
                    type: 'text',
                    text: `Error retrieving metrics: ${error.message}`
                }]
            };
        }
    }
    
    /**
     * Start server
     */
    async start() {
        await this.initialize();
        
        const transport = new StdioServerTransport();
        await this.server.connect(transport);
        
        console.log('MCP Server with Authentication started');
        console.log('Use the authenticate tool first to login');
    }
}

// Start server if run directly
if (import.meta.url === `file://${process.argv[1]}`) {
    const server = new DigitalTwinMCPServerAuth();
    server.start().catch(console.error);
}

export default DigitalTwinMCPServerAuth;