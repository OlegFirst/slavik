/**
 * Event System Server
 * HTTP API + WebSocket for real-time + Meta-monitoring
 */

import http from 'http';
import { WebSocketServer } from 'ws';
import eventSystem from './index.js';

const PORT = process.env.PORT || 3000;

// ============== HTTP API ==============

const server = http.createServer((req, res) => {
    // Enable CORS
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

    if (req.method === 'OPTIONS') {
        res.writeHead(204);
        res.end();
        return;
    }

    // Parse URL
    const url = new URL(req.url, `http://${req.headers.host}`);

    // Routes
    switch (url.pathname) {
        case '/':
            handleRoot(req, res);
            break;

        case '/health':
            handleHealth(req, res);
            break;

        case '/publish':
            handlePublish(req, res);
            break;

        case '/meta':
            handleMeta(req, res);
            break;

        case '/patterns':
            handlePatterns(req, res);
            break;

        case '/insights':
            handleInsights(req, res);
            break;

        case '/correlation':
            handleCorrelation(req, res, url);
            break;

        case '/predict':
            handlePredict(req, res);
            break;

        default:
            res.writeHead(404);
            res.end(JSON.stringify({ error: 'Not found' }));
    }
});

// Route handlers

function handleRoot(req, res) {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
        service: 'Cognitive Event System',
        version: '1.0.0',
        status: 'running',
        meta: 'enabled',
        endpoints: {
            health: '/health',
            publish: '/publish (POST)',
            meta: '/meta',
            patterns: '/patterns',
            insights: '/insights',
            correlation: '/correlation?id=xxx',
            predict: '/predict',
            websocket: 'ws://localhost:' + PORT
        }
    }));
}

function handleHealth(req, res) {
    const state = eventSystem.getMetaState();

    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
        status: state.health,
        totalEvents: state.totalEvents,
        activePatterns: state.activePatterns,
        correlations: state.correlationCount,
        uptime: process.uptime(),
        memory: process.memoryUsage()
    }));
}

async function handlePublish(req, res) {
    if (req.method !== 'POST') {
        res.writeHead(405);
        res.end(JSON.stringify({ error: 'Method not allowed' }));
        return;
    }

    let body = '';
    req.on('data', chunk => body += chunk);
    req.on('end', async () => {
        try {
            const data = JSON.parse(body);
            const { type, payload, metadata } = data;

            if (!type) {
                res.writeHead(400);
                res.end(JSON.stringify({ error: 'Event type required' }));
                return;
            }

            const event = await eventSystem.publish(type, payload, metadata);

            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({
                success: true,
                eventId: event.id,
                correlationId: event.metadata.correlationId
            }));

        } catch (error) {
            res.writeHead(400);
            res.end(JSON.stringify({ error: error.message }));
        }
    });
}

function handleMeta(req, res) {
    const state = eventSystem.getMetaState();

    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(state));
}

function handlePatterns(req, res) {
    const patterns = Array.from(eventSystem.eventPatterns.entries())
        .map(([sequence, count]) => ({ sequence, count }))
        .sort((a, b) => b.count - a.count)
        .slice(0, 20);

    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ patterns }));
}

function handleInsights(req, res) {
    const insights = eventSystem.metaState.insights.slice(-50);

    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ insights }));
}

function handleCorrelation(req, res, url) {
    const correlationId = url.searchParams.get('id');

    if (!correlationId) {
        res.writeHead(400);
        res.end(JSON.stringify({ error: 'Correlation ID required' }));
        return;
    }

    const chain = eventSystem.getCorrelationChain(correlationId);

    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
        correlationId,
        events: chain.map(e => ({
            id: e.id,
            type: e.type,
            timestamp: e.metadata.timestamp,
            success: e.metaInfo?.success
        }))
    }));
}

function handlePredict(req, res) {
    const predictions = eventSystem.predictNextEvent();

    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ predictions }));
}

// ============== WEBSOCKET ==============

const wss = new WebSocketServer({ server });

// Broadcast all events to WebSocket clients
eventSystem.subscribe('*', (event) => {
    const message = JSON.stringify({
        type: 'event',
        data: {
            id: event.id,
            type: event.type,
            timestamp: event.metadata.timestamp,
            source: event.metadata.source
        }
    });

    wss.clients.forEach(client => {
        if (client.readyState === 1) { // WebSocket.OPEN
            client.send(message);
        }
    });
});

// Broadcast insights
eventSystem.subscribe('system:insight_generated', (event) => {
    const message = JSON.stringify({
        type: 'insight',
        data: event.data
    });

    wss.clients.forEach(client => {
        if (client.readyState === 1) {
            client.send(message);
        }
    });
});

// WebSocket connection handling
wss.on('connection', (ws) => {
    console.log('New WebSocket connection');

    // Send current meta state on connection
    ws.send(JSON.stringify({
        type: 'meta',
        data: eventSystem.getMetaState()
    }));

    ws.on('message', async (message) => {
        try {
            const data = JSON.parse(message);

            if (data.type === 'subscribe') {
                // Client wants to subscribe to specific events
                const unsubscribe = eventSystem.subscribe(data.eventType, (event) => {
                    ws.send(JSON.stringify({
                        type: 'event',
                        eventType: data.eventType,
                        data: event
                    }));
                });

                ws.on('close', unsubscribe);
            }

        } catch (error) {
            ws.send(JSON.stringify({
                type: 'error',
                error: error.message
            }));
        }
    });

    ws.on('close', () => {
        console.log('WebSocket connection closed');
    });
});

// ============== META MONITORING ==============

// Periodic meta state broadcast
setInterval(() => {
    const metaState = eventSystem.getMetaState();

    const message = JSON.stringify({
        type: 'meta-update',
        data: metaState
    });

    wss.clients.forEach(client => {
        if (client.readyState === 1) {
            client.send(message);
        }
    });
}, 10000); // Every 10 seconds

// ============== SERVER START ==============

server.listen(PORT, () => {
    console.log(`
🧠 Cognitive Event System Started
================================
HTTP API:    http://localhost:${PORT}
WebSocket:   ws://localhost:${PORT}
Health:      http://localhost:${PORT}/health
Meta State:  http://localhost:${PORT}/meta

Meta-awareness: ENABLED
Pattern Recognition: ACTIVE
Insight Generation: ACTIVE
Self-monitoring: RUNNING

The system is learning from day one...
    `);

    // Initial self-test
    eventSystem.publish('system:started', {
        service: 'event-system',
        port: PORT,
        timestamp: Date.now()
    }, {
        source: 'event-system-server',
        priority: 'low'
    });
});

// Graceful shutdown
process.on('SIGTERM', () => {
    console.log('SIGTERM received, closing server...');

    server.close(() => {
        console.log('Server closed');
        process.exit(0);
    });
});