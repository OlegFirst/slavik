#!/usr/bin/env node
/**
 * BCM Real-time Server - Socket.io
 * Handles all real-time communications for BCM platform
 */

const { Server } = require("socket.io");
const { createServer } = require("http");
const { createClient } = require("redis");

// Configuration
const PORT = process.env.SOCKETIO_PORT || 8889;
const REDIS_URL = process.env.REDIS_URL || "redis://localhost:6379";

// Create HTTP server
const httpServer = createServer();

// Create Socket.io server with CORS
const io = new Server(httpServer, {
  cors: {
    origin: [
      "http://localhost:3000",
      "http://localhost:3001",
      "http://localhost:5173",
      "http://localhost:8888"
    ],
    methods: ["GET", "POST"],
    credentials: true
  },
  transports: ['websocket', 'polling']
});

// Redis client for pub/sub (optional, for scaling)
let redisClient = null;
let redisSubscriber = null;

// Try to connect to Redis
try {
  const redis = require("redis");
  redisClient = redis.createClient({ url: REDIS_URL });
  redisSubscriber = redis.createClient({ url: REDIS_URL });

  redisClient.connect().catch(err => {
    console.warn("⚠️ Redis not available, running without Redis");
    redisClient = null;
  });
} catch (err) {
  console.log("ℹ️ Redis not installed, running in single-server mode");
}

// Store active connections
const connections = new Map();

// Middleware for authentication (optional)
io.use((socket, next) => {
  const token = socket.handshake.auth.token;
  // TODO: Validate token here if needed
  next();
});

// Connection handler
io.on("connection", (socket) => {
  console.log(`✅ Client connected: ${socket.id}`);
  connections.set(socket.id, {
    connectedAt: new Date(),
    subscriptions: new Set()
  });

  // Send welcome message
  socket.emit("connected", {
    message: "Connected to BCM Real-time Server",
    socketId: socket.id,
    timestamp: new Date().toISOString()
  });

  // Handle subscriptions
  socket.on("subscribe", (topics) => {
    const topicList = Array.isArray(topics) ? topics : [topics];
    const client = connections.get(socket.id);

    topicList.forEach(topic => {
      socket.join(topic);
      client.subscriptions.add(topic);
      console.log(`📡 ${socket.id} subscribed to ${topic}`);
    });

    socket.emit("subscribed", {
      topics: topicList,
      timestamp: new Date().toISOString()
    });
  });

  // Handle unsubscribe
  socket.on("unsubscribe", (topics) => {
    const topicList = Array.isArray(topics) ? topics : [topics];
    const client = connections.get(socket.id);

    topicList.forEach(topic => {
      socket.leave(topic);
      client.subscriptions.delete(topic);
      console.log(`🔕 ${socket.id} unsubscribed from ${topic}`);
    });

    socket.emit("unsubscribed", {
      topics: topicList,
      timestamp: new Date().toISOString()
    });
  });

  // Handle custom events
  socket.on("request-update", (data) => {
    // Trigger immediate update for specific data
    sendUpdate(data.type, data.params);
  });

  // Handle disconnect
  socket.on("disconnect", (reason) => {
    console.log(`❌ Client disconnected: ${socket.id} (${reason})`);
    connections.delete(socket.id);
  });

  // Ping-pong for connection health
  socket.on("ping", () => {
    socket.emit("pong", { timestamp: new Date().toISOString() });
  });
});

// Function to broadcast updates to specific topics
function broadcast(topic, event, data) {
  io.to(topic).emit(event, {
    ...data,
    timestamp: new Date().toISOString(),
    topic: topic
  });
}

// Simulate real-time data updates
function startDataStreams() {
  // System metrics update every 5 seconds
  setInterval(() => {
    const metrics = {
      cpu: Math.random() * 100,
      memory: Math.random() * 100,
      disk: Math.random() * 100,
      network: Math.random() * 1000,
      activeUsers: Math.floor(Math.random() * 100),
      requestsPerSecond: Math.floor(Math.random() * 1000)
    };
    broadcast("metrics", "metrics:update", metrics);
  }, 5000);

  // Service health update every 10 seconds
  setInterval(() => {
    const health = {
      services: [
        { name: "Odoo", status: "healthy", uptime: "24h 13m" },
        { name: "AI Orchestrator", status: "healthy", uptime: "24h 13m" },
        { name: "BIA Engine", status: "healthy", uptime: "23h 45m" },
        { name: "Document Processor", status: Math.random() > 0.8 ? "warning" : "healthy", uptime: "22h 30m" },
        { name: "Compliance Checker", status: "healthy", uptime: "24h 13m" }
      ]
    };
    broadcast("health", "health:update", health);
  }, 10000);

  // AI Organisms update every 7 seconds
  setInterval(() => {
    const organisms = [
      { id: 1, name: "Governance Brain", status: "active", load: Math.random() * 100 },
      { id: 2, name: "Risk Analyzer", status: "active", load: Math.random() * 100 },
      { id: 3, name: "Compliance Monitor", status: Math.random() > 0.9 ? "warning" : "active", load: Math.random() * 100 },
      { id: 4, name: "Document Processor", status: "active", load: Math.random() * 100 },
      { id: 5, name: "Training Assistant", status: "active", load: Math.random() * 100 }
    ];
    broadcast("organisms", "organisms:update", { organisms });
  }, 7000);

  // Notifications (random)
  setInterval(() => {
    if (Math.random() > 0.7) {
      const notifications = [
        { type: "info", message: "System backup completed successfully" },
        { type: "warning", message: "High memory usage detected on BIA Engine" },
        { type: "success", message: "New BCM module deployed successfully" },
        { type: "info", message: "5 new risk assessments pending review" }
      ];
      const notification = notifications[Math.floor(Math.random() * notifications.length)];
      broadcast("notifications", "notification:new", notification);
    }
  }, 15000);

  // Alerts (rare)
  setInterval(() => {
    if (Math.random() > 0.95) {
      const alert = {
        level: "warning",
        title: "Performance Degradation",
        message: "Response time increased by 45% in the last 5 minutes",
        service: "AI Orchestrator"
      };
      broadcast("alerts", "alert:new", alert);
    }
  }, 30000);
}

// Function to send specific updates
function sendUpdate(type, params = {}) {
  switch(type) {
    case 'metrics':
      // Fetch and send latest metrics
      const metrics = {
        cpu: Math.random() * 100,
        memory: Math.random() * 100,
        // ... more metrics
      };
      broadcast("metrics", "metrics:update", metrics);
      break;

    case 'health':
      // Fetch and send service health
      // Could call actual health check endpoints here
      break;

    default:
      console.log(`Unknown update type: ${type}`);
  }
}

// HTTP endpoints for triggering events from other services
httpServer.on('request', (req, res) => {
  if (req.url === '/health') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      status: 'healthy',
      connections: connections.size,
      timestamp: new Date().toISOString()
    }));
  } else if (req.url === '/stats') {
    const stats = {
      connections: connections.size,
      rooms: io.sockets.adapter.rooms.size,
      timestamp: new Date().toISOString()
    };
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(stats));
  } else {
    res.writeHead(404);
    res.end('Not found');
  }
});

// Start server
httpServer.listen(PORT, () => {
  console.log(`🚀 BCM Real-time Server running on port ${PORT}`);
  console.log(`📡 Socket.io endpoint: ws://localhost:${PORT}`);
  console.log(`🔗 Health check: http://localhost:${PORT}/health`);
  console.log(`📊 Stats: http://localhost:${PORT}/stats`);

  // Start simulated data streams
  startDataStreams();
  console.log(`📊 Real-time data streams started`);
});

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('SIGTERM received, closing connections...');
  io.close(() => {
    console.log('All connections closed');
    process.exit(0);
  });
});

module.exports = { io, broadcast };