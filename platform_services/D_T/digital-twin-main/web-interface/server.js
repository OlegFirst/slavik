#!/usr/bin/env node

/**
 * NASH 4.0 Digital Twin Web Interface Server
 * Simple Express server for Digital Twin visualization
 * 
 * Professional implementation following NASH standards
 */

import express from 'express';
import path from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';
import { DigitalTwinModule } from '../index.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const app = express();
const PORT = process.env.DIGITAL_TWIN_WEB_PORT || 8100;

// Initialize Digital Twin module
const digitalTwinModule = new DigitalTwinModule({
    environment: 'web',
    enableCache: true,
    enableAudit: false // Disable for demo
});

// Middleware
app.use(express.json());
app.use(express.static(path.join(__dirname, 'static')));

// CORS for development
app.use((req, res, next) => {
    res.header('Access-Control-Allow-Origin', '*');
    res.header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
    res.header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept, Authorization');
    next();
});

// Routes

// Serve main page
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'templates', 'index.html'));
});

// Health check
app.get('/api/health', (req, res) => {
    try {
        const healthStatus = digitalTwinModule.getHealthStatus();
        res.json({
            success: true,
            status: healthStatus.status,
            uptime: healthStatus.uptime,
            service: 'digital-twin-web',
            timestamp: Date.now()
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            error: 'Health check failed',
            timestamp: Date.now()
        });
    }
});

// Get system metrics
app.get('/api/metrics', (req, res) => {
    try {
        const metrics = digitalTwinModule.getMetrics();
        const healthStatus = digitalTwinModule.getHealthStatus();
        
        res.json({
            success: true,
            metrics: {
                ...metrics,
                status: healthStatus.status,
                uptime: healthStatus.uptime,
                memoryUsage: healthStatus.memoryUsage
            },
            timestamp: Date.now()
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            error: 'Failed to get metrics',
            timestamp: Date.now()
        });
    }
});

// Create digital twin
app.post('/api/twins', async (req, res) => {
    try {
        const context = {
            userId: 'web_user',
            organizationId: req.body.organizationId || 'web_org',
            permissions: { create: true, read: true, update: true },
            roles: ['digital_twin_user']
        };
        
        const result = await digitalTwinModule.createDigitalTwin(req.body, context);
        res.json(result);
    } catch (error) {
        console.error('Create twin error:', error);
        res.status(500).json({
            success: false,
            error: error.message,
            timestamp: Date.now()
        });
    }
});

// Get digital twin
app.get('/api/twins/:id', async (req, res) => {
    try {
        const context = {
            userId: 'web_user',
            organizationId: 'web_org',
            permissions: { read: true },
            roles: ['digital_twin_user']
        };
        
        const twin = await digitalTwinModule.getDigitalTwin(req.params.id, context);
        
        if (twin) {
            res.json({
                success: true,
                twin,
                timestamp: Date.now()
            });
        } else {
            res.status(404).json({
                success: false,
                error: 'Digital twin not found',
                timestamp: Date.now()
            });
        }
    } catch (error) {
        console.error('Get twin error:', error);
        res.status(500).json({
            success: false,
            error: error.message,
            timestamp: Date.now()
        });
    }
});

// Run scenario simulation
app.post('/api/twins/:id/scenarios', async (req, res) => {
    try {
        const context = {
            userId: 'web_user',
            organizationId: 'web_org',
            permissions: { read: true, simulate: true },
            roles: ['digital_twin_user']
        };
        
        const result = await digitalTwinModule.runScenarioSimulation(
            req.params.id,
            req.body.scenarioType,
            req.body.parameters,
            context
        );
        
        res.json({
            success: true,
            ...result,
            timestamp: Date.now()
        });
    } catch (error) {
        console.error('Scenario simulation error:', error);
        res.status(500).json({
            success: false,
            error: error.message,
            timestamp: Date.now()
        });
    }
});

// List digital twins
app.get('/api/twins', (req, res) => {
    try {
        // For demo purposes, return cached twins
        const twins = [];
        digitalTwinModule.twins.forEach((twin, twinId) => {
            twins.push({
                twinId,
                name: twin.name,
                organizationId: twin.organizationId,
                healthScore: twin.health.overallScore,
                createdAt: twin.metadata.createdAt
            });
        });
        
        res.json({
            success: true,
            twins,
            total: twins.length,
            timestamp: Date.now()
        });
    } catch (error) {
        console.error('List twins error:', error);
        res.status(500).json({
            success: false,
            error: error.message,
            timestamp: Date.now()
        });
    }
});

// Error handler
app.use((error, req, res, next) => {
    console.error('Server error:', error);
    res.status(500).json({
        success: false,
        error: 'Internal server error',
        timestamp: Date.now()
    });
});

// 404 handler
app.use((req, res) => {
    res.status(404).json({
        success: false,
        error: 'Endpoint not found',
        path: req.path,
        timestamp: Date.now()
    });
});

// Initialize and start server
async function startServer() {
    try {
        // Initialize Digital Twin module
        await digitalTwinModule.initialize();
        console.log(' Digital Twin module initialized');
        
        // Start web server
        app.listen(PORT, () => {
            console.log(` NASH Digital Twin Web Interface running on http://localhost:${PORT}`);
            console.log(` Dashboard: http://localhost:${PORT}/`);
            console.log(` API Health: http://localhost:${PORT}/api/health`);
            console.log(` API Metrics: http://localhost:${PORT}/api/metrics`);
        });
        
    } catch (error) {
        console.error(' Failed to start server:', error);
        process.exit(1);
    }
}

// Graceful shutdown
process.on('SIGTERM', async () => {
    console.log(' Graceful shutdown initiated...');
    
    try {
        await digitalTwinModule.shutdown();
        console.log(' Digital Twin module shut down gracefully');
        process.exit(0);
    } catch (error) {
        console.error(' Error during shutdown:', error);
        process.exit(1);
    }
});

process.on('SIGINT', async () => {
    console.log(' Interrupt signal received, shutting down...');
    
    try {
        await digitalTwinModule.shutdown();
        console.log(' Digital Twin module shut down gracefully');
        process.exit(0);
    } catch (error) {
        console.error(' Error during shutdown:', error);
        process.exit(1);
    }
});

// Start the server
startServer();