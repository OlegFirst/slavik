#!/usr/bin/env node

/**
 * NASH 4.0 Digital Twin MCP Connector
 * One-click setup for Claude Desktop integration
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
    CallToolRequestSchema,
    ListToolsRequestSchema,
    ListResourcesRequestSchema,
    ReadResourceRequestSchema
} from '@modelcontextprotocol/sdk/types.js';
import { createClient } from '@supabase/supabase-js';
import fetch from 'node-fetch';
import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

class DigitalTwinMCPConnector {
    constructor() {
        this.config = null;
        this.supabase = null;
        this.apiBase = null;
        this.authToken = null;
        this.server = null;
    }

    async initialize() {
        try {
            // Load configuration
            await this.loadConfig();
            
            // Initialize MCP server
            this.server = new Server(
                {
                    name: 'nash-digital-twin',
                    version: '1.0.0'
                },
                {
                    capabilities: {
                        resources: {},
                        tools: {}
                    }
                }
            );

            // Setup handlers
            this.setupHandlers();
            
            // Initialize auth if configured
            if (this.config.auth?.enabled) {
                await this.initializeAuth();
            }

            console.error('[MCP] Digital Twin connector initialized');
            return true;
        } catch (error) {
            console.error('[MCP] Initialization failed:', error);
            return false;
        }
    }

    async loadConfig() {
        try {
            // Try to load config from user home
            const configPath = path.join(
                process.env.HOME || process.env.USERPROFILE,
                '.nash4',
                'digital-twin-config.json'
            );
            
            const configData = await fs.readFile(configPath, 'utf8');
            this.config = JSON.parse(configData);
            
            // Set API base URL
            this.apiBase = this.config.apiUrl || 'http://localhost:3000';
            
        } catch (error) {
            // Use default config if not found
            this.config = {
                apiUrl: process.env.DIGITAL_TWIN_API || 'http://localhost:3000',
                auth: {
                    enabled: false,
                    supabaseUrl: process.env.SUPABASE_URL,
                    supabaseKey: process.env.SUPABASE_ANON_KEY
                }
            };
            this.apiBase = this.config.apiUrl;
        }
    }

    async initializeAuth() {
        if (this.config.auth?.supabaseUrl && this.config.auth?.supabaseKey) {
            this.supabase = createClient(
                this.config.auth.supabaseUrl,
                this.config.auth.supabaseKey
            );
            
            // Check for stored session
            const storedToken = await this.getStoredToken();
            if (storedToken) {
                this.authToken = storedToken;
                console.error('[MCP] Using stored authentication');
            }
        }
    }

    async getStoredToken() {
        try {
            const tokenPath = path.join(
                process.env.HOME || process.env.USERPROFILE,
                '.nash4',
                'auth-token.json'
            );
            const tokenData = await fs.readFile(tokenPath, 'utf8');
            const { token, expires } = JSON.parse(tokenData);
            
            if (new Date(expires) > new Date()) {
                return token;
            }
        } catch {
            return null;
        }
    }

    setupHandlers() {
        // List available tools
        this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
            tools: [
                {
                    name: 'create_organization',
                    description: 'Create a new organization digital twin',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            name: { type: 'string', description: 'Organization name' },
                            type: { 
                                type: 'string', 
                                enum: ['non-profit', 'charity', 'foundation'],
                                description: 'Organization type' 
                            },
                            budget: { type: 'number', description: 'Annual budget' },
                            staff: { type: 'number', description: 'Number of staff' },
                            mission: { type: 'string', description: 'Mission statement' }
                        },
                        required: ['name', 'type']
                    }
                },
                {
                    name: 'run_simulation',
                    description: 'Run one of 30 available simulations',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            experiment: {
                                type: 'string',
                                description: 'Experiment type (e.g., simpy_queue, mesa_abm, anylogic_hybrid, automation, crisis)',
                                enum: [
                                    // External adapters
                                    'simpy_queue', 'mesa_abm', 'epi_nowcasting_rt', 'anylogic_hybrid',
                                    // Digital Twin scenarios
                                    'automation', 'crisis', 'expansion', 'integration',
                                    'digital_transformation', 'ai_implementation', 'cybersecurity',
                                    'compliance', 'staff_training', 'process_optimization',
                                    'stakeholder_engagement', 'community_outreach', 'resource_allocation',
                                    'capacity_building', 'monitoring_evaluation', 'knowledge_management',
                                    'innovation_research', 'partnership_development', 'sustainability_planning',
                                    'grant_management', 'funding_diversification', 'impact_assessment',
                                    // Internal engines
                                    'theory_of_change', 'capacity_sweep', 'bcm_outage', 'budget_optimization'
                                ]
                            },
                            organizationId: { type: 'string', description: 'Organization ID (optional)' },
                            params: { type: 'object', description: 'Simulation parameters' }
                        },
                        required: ['experiment']
                    }
                },
                {
                    name: 'analyze_impact',
                    description: 'Analyze organization impact and generate passport',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            organizationId: { type: 'string', description: 'Organization ID' },
                            analysisType: {
                                type: 'string',
                                enum: ['health', 'efficiency', 'impact', 'comprehensive'],
                                description: 'Type of analysis'
                            }
                        },
                        required: ['organizationId']
                    }
                },
                {
                    name: 'list_organizations',
                    description: 'List all available organizations',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            filter: { type: 'string', description: 'Optional filter' }
                        }
                    }
                },
                {
                    name: 'demo_mode',
                    description: 'Run demo with Hope Foundation International',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            scenario: {
                                type: 'string',
                                description: 'Demo scenario to run',
                                enum: ['quick', 'comprehensive', 'showcase']
                            }
                        }
                    }
                }
            ]
        }));

        // Handle tool calls
        this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
            const { name, arguments: args } = request.params;
            
            try {
                switch (name) {
                    case 'create_organization':
                        return await this.createOrganization(args);
                    
                    case 'run_simulation':
                        return await this.runSimulation(args);
                    
                    case 'analyze_impact':
                        return await this.analyzeImpact(args);
                    
                    case 'list_organizations':
                        return await this.listOrganizations(args);
                    
                    case 'demo_mode':
                        return await this.runDemo(args);
                    
                    default:
                        throw new Error(`Unknown tool: ${name}`);
                }
            } catch (error) {
                return {
                    content: [{
                        type: 'text',
                        text: `Error: ${error.message}`
                    }]
                };
            }
        });

        // List resources
        this.server.setRequestHandler(ListResourcesRequestSchema, async () => ({
            resources: [
                {
                    uri: 'nash://experiments',
                    name: 'Available Experiments',
                    description: 'List of all 30 simulation experiments',
                    mimeType: 'application/json'
                },
                {
                    uri: 'nash://documentation',
                    name: 'Platform Documentation',
                    description: 'Complete documentation for Digital Twin platform',
                    mimeType: 'text/markdown'
                }
            ]
        }));

        // Read resources
        this.server.setRequestHandler(ReadResourceRequestSchema, async (request) => {
            const { uri } = request.params;
            
            switch (uri) {
                case 'nash://experiments':
                    return {
                        contents: [{
                            uri,
                            mimeType: 'application/json',
                            text: JSON.stringify(this.getExperimentsList(), null, 2)
                        }]
                    };
                
                case 'nash://documentation':
                    return {
                        contents: [{
                            uri,
                            mimeType: 'text/markdown',
                            text: this.getDocumentation()
                        }]
                    };
                
                default:
                    throw new Error(`Unknown resource: ${uri}`);
            }
        });
    }

    async createOrganization(args) {
        const response = await this.apiCall('/api/organizations', 'POST', args);
        
        return {
            content: [{
                type: 'text',
                text: `Organization created: ${args.name}`
            }, {
                type: 'text',
                text: JSON.stringify(response, null, 2)
            }]
        };
    }

    async runSimulation(args) {
        const endpoint = '/api/impact/simulations/run';
        const response = await this.apiCall(endpoint, 'POST', args);
        
        return {
            content: [{
                type: 'text',
                text: `Simulation completed: ${args.experiment}`
            }, {
                type: 'text',
                text: JSON.stringify(response, null, 2)
            }]
        };
    }

    async analyzeImpact(args) {
        const endpoint = `/api/impact/analyze/${args.organizationId}`;
        const response = await this.apiCall(endpoint, 'GET');
        
        return {
            content: [{
                type: 'text',
                text: `Impact analysis complete`
            }, {
                type: 'text',
                text: JSON.stringify(response, null, 2)
            }]
        };
    }

    async listOrganizations(args) {
        const endpoint = '/api/organizations';
        const response = await this.apiCall(endpoint, 'GET');
        
        return {
            content: [{
                type: 'text',
                text: `Found ${response.length || 0} organizations`
            }, {
                type: 'text',
                text: JSON.stringify(response, null, 2)
            }]
        };
    }

    async runDemo(args) {
        const scenario = args.scenario || 'showcase';
        
        // Run demo simulation
        const response = await this.apiCall('/api/demo/start', 'POST', { scenario });
        
        return {
            content: [{
                type: 'text',
                text: 'Demo: Hope Foundation International loaded'
            }, {
                type: 'text',
                text: 'Organization with $75M budget, 350 staff, 5 programs'
            }, {
                type: 'text',
                text: 'All 30 experiments available for demonstration'
            }, {
                type: 'text',
                text: JSON.stringify(response, null, 2)
            }]
        };
    }

    async apiCall(endpoint, method = 'GET', data = null) {
        const url = `${this.apiBase}${endpoint}`;
        const headers = {
            'Content-Type': 'application/json'
        };
        
        if (this.authToken) {
            headers['Authorization'] = `Bearer ${this.authToken}`;
        }
        
        const options = {
            method,
            headers
        };
        
        if (data && method !== 'GET') {
            options.body = JSON.stringify(data);
        }
        
        try {
            const response = await fetch(url, options);
            if (!response.ok) {
                throw new Error(`API error: ${response.statusText}`);
            }
            return await response.json();
        } catch (error) {
            console.error(`API call failed: ${endpoint}`, error);
            throw error;
        }
    }

    getExperimentsList() {
        return {
            external_adapters: [
                { id: 'simpy_queue', name: 'SimPy Queue Optimization', type: 'discrete_event' },
                { id: 'mesa_abm', name: 'Mesa Agent-Based Model', type: 'agent_based' },
                { id: 'epi_nowcasting_rt', name: 'EpiNow2 Forecasting', type: 'epidemiological' },
                { id: 'anylogic_hybrid', name: 'AnyLogic Hybrid Simulation', type: 'hybrid' }
            ],
            digital_twin_scenarios: [
                'automation', 'crisis', 'expansion', 'integration',
                'digital_transformation', 'ai_implementation', 'cybersecurity',
                'compliance', 'staff_training', 'process_optimization',
                'stakeholder_engagement', 'community_outreach', 'resource_allocation',
                'capacity_building', 'monitoring_evaluation', 'knowledge_management',
                'innovation_research', 'partnership_development', 'sustainability_planning',
                'grant_management', 'funding_diversification', 'impact_assessment'
            ],
            internal_engines: [
                { id: 'theory_of_change', name: 'Theory of Change Optimizer' },
                { id: 'capacity_sweep', name: 'Capacity Sweep Analysis' },
                { id: 'bcm_outage', name: 'BCM Outage Simulation' },
                { id: 'budget_optimization', name: 'Budget Optimization Engine' }
            ],
            total_experiments: 30
        };
    }

    getDocumentation() {
        return `# NASH 4.0 Digital Twin MCP Connector

## Quick Start
\`\`\`bash
npx @nash4/digital-twin-mcp setup
\`\`\`

## Available Commands

### Create Organization
Create a new digital twin for your organization.

### Run Simulation
Choose from 30 different simulation experiments:
- 4 External adapters (SimPy, Mesa, EpiNow2, AnyLogic)
- 22 Digital Twin scenarios
- 4 Internal optimization engines

### Analyze Impact
Generate comprehensive impact analysis and validation passport.

### Demo Mode
Try the platform with Hope Foundation International demo data.

## Support
Visit: https://nash4.digital-twin.org
Email: support@nash4.org`;
    }

    async start() {
        const initialized = await this.initialize();
        if (!initialized) {
            console.error('Failed to initialize connector');
            process.exit(1);
        }

        const transport = new StdioServerTransport();
        await this.server.connect(transport);
        
        console.error('[MCP] Digital Twin connector running');
    }
}

// Start if run directly
if (import.meta.url === `file://${process.argv[1]}`) {
    const connector = new DigitalTwinMCPConnector();
    connector.start().catch(console.error);
}

export default DigitalTwinMCPConnector;