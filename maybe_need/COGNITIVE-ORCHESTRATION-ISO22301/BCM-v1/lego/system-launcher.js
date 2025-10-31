#!/usr/bin/env node

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

console.log(`
╔══════════════════════════════════════════════════════════════╗
║     COGNITIVE ORCHESTRATION SYSTEM - UNIVERSAL LAUNCHER      ║
╚══════════════════════════════════════════════════════════════╝
`);

class SystemLauncher {
  constructor() {
    this.services = new Map();
    this.startOrder = [
      // Level 1: Core Infrastructure
      { name: 'service-registry', path: 'SYSTEM_COMPONENTS/1_ORCHESTRATION/service-registry', port: 3001, critical: true },
      { name: 'message-queue', path: 'SYSTEM_COMPONENTS/2_EVENTS/message-queue', port: 3002, critical: true },
      { name: 'cache-layer', path: 'SYSTEM_COMPONENTS/4_STORAGE/cache-layer', port: 3004, critical: true },

      // Level 2: Data & Processing
      { name: 'unified-db-gateway', path: 'SYSTEM_COMPONENTS/4_STORAGE/unified_database_gateway', port: 3100 },
      { name: 'task-scheduler', path: 'SYSTEM_COMPONENTS/3_PROCESSING/task-scheduler', port: 3003, critical: true },
      { name: 'event-bus', path: 'SYSTEM_COMPONENTS/2_EVENTS/event-bus', port: 3050 },

      // Level 3: Intelligence
      { name: 'prediction-engine', path: 'SYSTEM_COMPONENTS/5_INTELLIGENCE/prediction-engine', port: 3005, critical: true },
      { name: 'ai-orchestrator', path: 'SYSTEM_COMPONENTS/1_ORCHESTRATION/ai_orchestrator', port: 3060 },

      // Level 4: Bridge Layer
      { name: 'ai-bridge-manager', path: 'BRIDGE_LAYER/ai-bridge-manager', port: 3010, critical: true },

      // Level 5: Evolution
      { name: 'evolution-agent', path: 'SANDBOX/evolution-agent', port: 3011 },

      // Level 6: Interfaces
      { name: 'api-gateway', path: 'SYSTEM_COMPONENTS/6_TOOLS/gateway', port: 3000, critical: true }
    ];

    this.healthChecks = new Map();
    this.retryAttempts = new Map();
    this.maxRetries = 3;
  }

  async launch() {
    console.log('🚀 Starting Cognitive Orchestration System...\n');

    // Check prerequisites
    if (!await this.checkPrerequisites()) {
      console.error('❌ Prerequisites check failed!');
      process.exit(1);
    }

    // Start services in order
    for (const service of this.startOrder) {
      await this.startService(service);

      // Wait for critical services
      if (service.critical) {
        await this.waitForService(service);
      }
    }

    console.log('\n✅ All services started successfully!');
    this.printStatus();
    this.startMonitoring();
  }

  async checkPrerequisites() {
    console.log('🔍 Checking prerequisites...');

    // Check Node.js
    const nodeVersion = process.version;
    console.log(`  ✓ Node.js ${nodeVersion}`);

    // Check Redis
    const redisRunning = await this.checkRedis();
    if (!redisRunning) {
      console.log('  ⚠️  Redis not running - starting local instance...');
      await this.startRedis();
    } else {
      console.log('  ✓ Redis running');
    }

    // Check MongoDB (for persistent services)
    const mongoRunning = await this.checkMongoDB();
    if (!mongoRunning) {
      console.log('  ⚠️  MongoDB not running (optional)');
    } else {
      console.log('  ✓ MongoDB running');
    }

    return true;
  }

  async startService(service) {
    const fullPath = path.join(__dirname, service.path);

    // Check if service exists
    if (!fs.existsSync(fullPath)) {
      console.log(`  ⚠️  ${service.name} - path not found, skipping`);
      return;
    }

    // Check for package.json
    const packagePath = path.join(fullPath, 'package.json');
    if (!fs.existsSync(packagePath)) {
      console.log(`  ⚠️  ${service.name} - no package.json, skipping`);
      return;
    }

    // Check for index.js
    const indexPath = path.join(fullPath, 'index.js');
    if (!fs.existsSync(indexPath)) {
      console.log(`  ⚠️  ${service.name} - no index.js, skipping`);
      return;
    }

    console.log(`  🔄 Starting ${service.name} on port ${service.port}...`);

    // Install dependencies if needed
    await this.installDependencies(fullPath, service.name);

    // Start the service
    const env = {
      ...process.env,
      PORT: service.port,
      SERVICE_NAME: service.name,
      SERVICE_REGISTRY: 'http://localhost:3001',
      MESSAGE_QUEUE: 'http://localhost:3002',
      CACHE_LAYER: 'http://localhost:3004'
    };

    const proc = spawn('node', ['index.js'], {
      cwd: fullPath,
      env,
      detached: false,
      stdio: ['ignore', 'pipe', 'pipe']
    });

    // Handle output
    proc.stdout.on('data', (data) => {
      console.log(`    [${service.name}] ${data.toString().trim()}`);
    });

    proc.stderr.on('data', (data) => {
      console.error(`    [${service.name}] ERROR: ${data.toString().trim()}`);
    });

    proc.on('error', (error) => {
      console.error(`    ❌ ${service.name} failed to start: ${error.message}`);
      this.handleServiceFailure(service);
    });

    proc.on('exit', (code) => {
      if (code !== 0) {
        console.error(`    ❌ ${service.name} exited with code ${code}`);
        this.handleServiceFailure(service);
      }
    });

    this.services.set(service.name, {
      process: proc,
      service,
      status: 'starting',
      startedAt: new Date()
    });

    // Give service time to start
    await this.sleep(1000);
  }

  async waitForService(service, timeout = 30000) {
    console.log(`  ⏳ Waiting for ${service.name} to be ready...`);

    const startTime = Date.now();
    while (Date.now() - startTime < timeout) {
      const isReady = await this.checkServiceHealth(service);

      if (isReady) {
        console.log(`  ✅ ${service.name} is ready!`);
        this.services.get(service.name).status = 'running';
        return true;
      }

      await this.sleep(1000);
    }

    console.error(`  ❌ ${service.name} failed to start in ${timeout}ms`);

    if (service.critical) {
      console.error('  ❌ Critical service failed - shutting down');
      await this.shutdown();
      process.exit(1);
    }

    return false;
  }

  async checkServiceHealth(service) {
    try {
      const http = require('http');

      return new Promise((resolve) => {
        const req = http.get(`http://localhost:${service.port}/health`, (res) => {
          resolve(res.statusCode === 200);
        });

        req.on('error', () => resolve(false));
        req.setTimeout(1000, () => {
          req.destroy();
          resolve(false);
        });
      });
    } catch {
      return false;
    }
  }

  async installDependencies(servicePath, serviceName) {
    const nodeModulesPath = path.join(servicePath, 'node_modules');

    if (!fs.existsSync(nodeModulesPath)) {
      console.log(`    📦 Installing dependencies for ${serviceName}...`);

      return new Promise((resolve, reject) => {
        const npm = spawn('npm', ['install', '--production'], {
          cwd: servicePath,
          stdio: 'inherit'
        });

        npm.on('close', (code) => {
          if (code === 0) {
            console.log(`    ✅ Dependencies installed for ${serviceName}`);
            resolve();
          } else {
            console.error(`    ❌ Failed to install dependencies for ${serviceName}`);
            reject();
          }
        });
      });
    }
  }

  handleServiceFailure(service) {
    const attempts = this.retryAttempts.get(service.name) || 0;

    if (attempts < this.maxRetries) {
      console.log(`  🔄 Retrying ${service.name} (attempt ${attempts + 1}/${this.maxRetries})...`);
      this.retryAttempts.set(service.name, attempts + 1);

      setTimeout(() => {
        this.startService(service);
      }, 3000);
    } else if (service.critical) {
      console.error(`  ❌ Critical service ${service.name} failed after ${this.maxRetries} attempts`);
      this.shutdown();
      process.exit(1);
    }
  }

  startMonitoring() {
    console.log('\n📊 Starting health monitoring...\n');

    setInterval(() => {
      this.checkAllServices();
    }, 10000);

    // Handle shutdown
    process.on('SIGINT', async () => {
      console.log('\n🛑 Shutting down gracefully...');
      await this.shutdown();
      process.exit(0);
    });
  }

  async checkAllServices() {
    for (const [name, serviceInfo] of this.services) {
      const isHealthy = await this.checkServiceHealth(serviceInfo.service);

      if (!isHealthy && serviceInfo.status === 'running') {
        console.log(`  ⚠️  ${name} became unhealthy`);
        serviceInfo.status = 'unhealthy';
      } else if (isHealthy && serviceInfo.status === 'unhealthy') {
        console.log(`  ✅ ${name} recovered`);
        serviceInfo.status = 'running';
      }
    }
  }

  printStatus() {
    console.log('\n╔══════════════════════════════════════════════════════════════╗');
    console.log('║                     SYSTEM STATUS                            ║');
    console.log('╠══════════════════════════════════════════════════════════════╣');

    for (const [name, info] of this.services) {
      const status = info.status === 'running' ? '🟢' : info.status === 'starting' ? '🟡' : '🔴';
      const port = info.service.port;
      console.log(`║ ${status} ${name.padEnd(20)} http://localhost:${port}`.padEnd(63) + '║');
    }

    console.log('╚══════════════════════════════════════════════════════════════╝');
    console.log('\n🌐 Main Gateway: http://localhost:3000');
    console.log('📊 Service Registry: http://localhost:3001');
    console.log('🧠 AI Bridge: http://localhost:3010');
    console.log('🧪 Evolution Agent: http://localhost:3011\n');
  }

  async shutdown() {
    console.log('Stopping all services...');

    for (const [name, info] of this.services) {
      console.log(`  Stopping ${name}...`);

      if (info.process) {
        info.process.kill('SIGTERM');
      }
    }

    await this.sleep(2000);
  }

  async checkRedis() {
    try {
      const redis = require('redis');
      const client = redis.createClient();

      return new Promise((resolve) => {
        client.on('connect', () => {
          client.quit();
          resolve(true);
        });
        client.on('error', () => {
          resolve(false);
        });
      });
    } catch {
      return false;
    }
  }

  async startRedis() {
    // Try to start Redis
    const redis = spawn('redis-server', [], {
      detached: false,
      stdio: 'ignore'
    });

    await this.sleep(2000);
    return true;
  }

  async checkMongoDB() {
    // Simple check - can be enhanced
    return new Promise((resolve) => {
      const mongo = spawn('mongod', ['--version'], {
        stdio: 'ignore'
      });

      mongo.on('close', (code) => {
        resolve(code === 0);
      });

      mongo.on('error', () => {
        resolve(false);
      });
    });
  }

  sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

// Launch the system
const launcher = new SystemLauncher();
launcher.launch().catch((error) => {
  console.error('❌ Failed to launch system:', error);
  process.exit(1);
});