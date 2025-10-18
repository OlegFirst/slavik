/**
 * Simple Web Server for Digital Twin
 * Минимальный рабочий сервер
 */

import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import fetch from 'node-fetch';
import { createClient } from '@supabase/supabase-js';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import sehRouter from './api/seh-endpoints.js';
import { ImpactValidationBridge } from './src/impact-validation-bridge.js';
import { ImpactPassportGenerator } from './src/impact-passport-generator.js';
import { SimulationRouter } from './src/simulation-router.js';
import { createImpactRoutes } from './src/api/impact-endpoints.js';

// Load environment variables
dotenv.config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Initialize Supabase
const supabase = createClient(
    process.env.SUPABASE_URL,
    process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.SUPABASE_ANON_KEY
);

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());

// Initialize Impact components
const validationBridge = new ImpactValidationBridge();
const passportGenerator = new ImpactPassportGenerator();
const simulationRouter = new SimulationRouter();

// Initialize components with dependencies
async function initializeComponents() {
    try {
        // Initialize validation bridge with Impact Proof System (if available)
        await validationBridge.initialize(null); // IPS будет подключен позже
        
        // Initialize passport generator with Supabase
        await passportGenerator.initialize(null, supabase);
        
        console.log('[SUCCESS] Impact components initialized');
    } catch (error) {
        console.error('[ERROR] Failed to initialize Impact components:', error);
    }
}

// Initialize on startup
initializeComponents();

// Add supabase to all requests
app.use((req, res, next) => {
    req.supabase = supabase;
    req.validationBridge = validationBridge;
    req.passportGenerator = passportGenerator;
    req.simulationRouter = simulationRouter;
    next();
});

// Mount SEH API endpoints
app.use('/api/seh', sehRouter);

// Mount Impact API endpoints
const impactRoutes = createImpactRoutes(validationBridge, passportGenerator, simulationRouter);
app.use('/api/impact', impactRoutes);

// Serve static files from web-interface
app.use('/static', express.static(join(__dirname, 'web-interface', 'static')));

// Serve the main visualization interface
app.get('/', (req, res) => {
    res.sendFile(join(__dirname, 'web-interface', 'templates', 'index.html'));
});


// Health check
app.get('/health', async (req, res) => {
    try {
        const { data, error } = await supabase
            .from('organization_profiles')
            .select('count')
            .limit(1);
        
        // Check adapter status
        const adapters = {};
        const adapterUrls = {
            simpy: process.env.SIMPY_ADAPTER_URL || 'http://localhost:7001',
            mesa: process.env.MESA_ADAPTER_URL || 'http://localhost:7002',
            epinow2: process.env.EPINOW2_ADAPTER_URL || 'http://localhost:7003'
        };
        
        for (const [name, url] of Object.entries(adapterUrls)) {
            try {
                const response = await fetch(`${url.replace('/run', '/docs')}`, { timeout: 5000 });
                adapters[name] = response.ok ? 'healthy' : 'unhealthy';
            } catch (e) {
                adapters[name] = 'unreachable';
            }
        }
        
        res.json({
            status: 'healthy',
            database: error ? 'disconnected' : 'connected',
            adapters,
            timestamp: new Date().toISOString()
        });
    } catch (error) {
        res.status(500).json({
            status: 'unhealthy',
            error: error.message
        });
    }
});

// Get all organizations
app.get('/api/organizations', async (req, res) => {
    try {
        const { data, error } = await supabase
            .from('organization_profiles')
            .select('*')
            .eq('is_active', true);
        
        if (error) throw error;
        res.json(data);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Create organization
app.post('/api/organizations', async (req, res) => {
    try {
        const { data, error } = await supabase
            .from('organization_profiles')
            .insert(req.body)
            .select()
            .single();
        
        if (error) throw error;
        res.status(201).json(data);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Get organization by ID
app.get('/api/organizations/:id', async (req, res) => {
    try {
        const { data, error } = await supabase
            .from('organization_profiles')
            .select('*')
            .eq('id', req.params.id)
            .single();
        
        if (error) throw error;
        if (!data) return res.status(404).json({ error: 'Organization not found' });
        res.json(data);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Create digital twin
app.post('/api/digital-twins', async (req, res) => {
    try {
        const { data, error } = await supabase
            .from('digital_twins')
            .insert(req.body)
            .select()
            .single();
        
        if (error) throw error;
        res.status(201).json(data);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Get digital twin
app.get('/api/digital-twins/:id', async (req, res) => {
    try {
        const { data, error } = await supabase
            .from('digital_twins')
            .select('*')
            .eq('id', req.params.id)
            .single();
        
        if (error) throw error;
        if (!data) return res.status(404).json({ error: 'Digital twin not found' });
        res.json(data);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Create simulation
app.post('/api/simulations', async (req, res) => {
    try {
        const simulationData = {
            ...req.body,
            simulation_id: `sim_${Date.now()}`,
            status: 'running'
        };
        
        const { data, error } = await supabase
            .from('simulations')
            .insert(simulationData)
            .select()
            .single();
        
        if (error) throw error;
        
        // Simulate completion after 2 seconds
        setTimeout(async () => {
            await supabase
                .from('simulations')
                .update({ 
                    status: 'completed',
                    results: {
                        success: true,
                        optimizations: Math.floor(Math.random() * 10) + 1,
                        savings: Math.floor(Math.random() * 50000) + 10000
                    }
                })
                .eq('id', data.id);
        }, 2000);
        
        res.status(201).json(data);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Get metrics
app.get('/api/metrics/:twinId', async (req, res) => {
    try {
        const { data, error } = await supabase
            .from('metrics')
            .select('*')
            .eq('twin_id', req.params.twinId)
            .order('timestamp', { ascending: false })
            .limit(100);
        
        if (error) throw error;
        res.json(data);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Start server
app.listen(PORT, () => {
    console.log(`
╔═══════════════════════════════════════════╗
║   Digital Twin Server Started!            ║
║                                           ║
║   URL: http://localhost:${PORT}               ║
║   API: http://localhost:${PORT}/api           ║
║                                           ║
║   Press Ctrl+C to stop                   ║
╚═══════════════════════════════════════════╝
    `);
});