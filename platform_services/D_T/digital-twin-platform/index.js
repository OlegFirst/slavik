#!/usr/bin/env node
/**
 * Digital Twin Standalone - Main Entry Point
 * Launches the Digital Twin Module as a standalone application
 */

import express from 'express';
import cors from 'cors';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

// Import with custom loader to handle path mappings
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Dynamic imports with path resolution
async function startApplication() {
    console.log('Starting Digital Twin Standalone Module...\n');

    try {
        // Load the Digital Twin Module with resolved paths
        const { DigitalTwinModule } = await import('./src/index.js');
        
        // Create Express app for web interface
        const app = express();
        app.use(cors());
        app.use(express.json());
        app.use(express.static(join(__dirname, 'web-interface/static')));

        // Initialize Digital Twin Module
        const digitalTwin = new DigitalTwinModule({
            environment: 'standalone',
            port: 8100,
            database: {
                adapter: 'memory',
                persistToFile: true,
                fileName: 'digital-twin-data.json'
            },
            security: {
                enabled: true,
                requireAuth: false // Disabled for standalone demo
            },
            features: {
                organizationModeling: true,
                scenarioSimulation: true,
                financialAnalysis: true,
                visualization3D: true,
                realTimeMonitoring: true
            }
        });

        await digitalTwin.initialize();
        console.log('✓ Digital Twin Module initialized\n');

        // API Routes
        app.get('/api/status', (req, res) => {
            res.json({
                status: 'active',
                module: 'Digital Twin Standalone',
                version: '2.0.0',
                uptime: process.uptime(),
                memory: process.memoryUsage()
            });
        });

        app.post('/api/organization/create', async (req, res) => {
            try {
                const result = await digitalTwin.createDigitalTwin(req.body);
                res.json({ success: true, data: result });
            } catch (error) {
                res.status(500).json({ success: false, error: error.message });
            }
        });

        app.post('/api/simulation/run', async (req, res) => {
            try {
                const { twinId, scenario, parameters } = req.body;
                const result = await digitalTwin.runSimulation(twinId, scenario, parameters);
                res.json({ success: true, data: result });
            } catch (error) {
                res.status(500).json({ success: false, error: error.message });
            }
        });

        app.get('/api/twins', async (req, res) => {
            try {
                const twins = await digitalTwin.listDigitalTwins();
                res.json({ success: true, data: twins });
            } catch (error) {
                res.status(500).json({ success: false, error: error.message });
            }
        });

        app.get('/api/metrics/:twinId', async (req, res) => {
            try {
                const metrics = await digitalTwin.getMetrics(req.params.twinId);
                res.json({ success: true, data: metrics });
            } catch (error) {
                res.status(500).json({ success: false, error: error.message });
            }
        });

        // Web UI route
        app.get('/', (req, res) => {
            res.sendFile(join(__dirname, 'web-interface/templates/index.html'));
        });

        // Start server
        const PORT = process.env.PORT || 3000;
        app.listen(PORT, () => {
            console.log('╔════════════════════════════════════════════════════╗');
            console.log('║       DIGITAL TWIN STANDALONE MODULE v2.0.0       ║');
            console.log('╠════════════════════════════════════════════════════╣');
            console.log(`║  Web Interface:   http://localhost:${PORT}            ║`);
            console.log(`║  API Endpoint:    http://localhost:${PORT}/api        ║`);
            console.log(`║  Health Check:    http://localhost:${PORT}/api/status ║`);
            console.log('╠════════════════════════════════════════════════════╣');
            console.log('║  Features:                                         ║');
            console.log('║  • 3D Organization Modeling                        ║');
            console.log('║  • Scenario Simulation Engine                      ║');
            console.log('║  • Financial Analysis & ROI                        ║');
            console.log('║  • Real-time Monitoring                            ║');
            console.log('║  • Predictive Analytics                            ║');
            console.log('╚════════════════════════════════════════════════════╝\n');
            console.log('Press Ctrl+C to stop the server\n');
        });

        // Graceful shutdown
        process.on('SIGINT', async () => {
            console.log('\nShutting down Digital Twin Module...');
            await digitalTwin.shutdown();
            process.exit(0);
        });

    } catch (error) {
        console.error('Failed to start Digital Twin Module:', error);
        console.error('\nTroubleshooting:');
        console.error('1. Make sure all dependencies are installed: npm install');
        console.error('2. Check that Node.js version is 18 or higher: node --version');
        console.error('3. Verify all required files are present');
        process.exit(1);
    }
}

// Start the application
startApplication().catch(console.error);