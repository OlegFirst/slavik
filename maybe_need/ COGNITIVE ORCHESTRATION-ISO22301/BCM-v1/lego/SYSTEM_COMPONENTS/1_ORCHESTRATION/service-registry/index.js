const express = require('express');
const { EventEmitter } = require('events');
const { v4: uuidv4 } = require('uuid');

class ServiceRegistry extends EventEmitter {
  constructor() {
    super();
    this.services = new Map();
    this.healthChecks = new Map();
    this.dependencies = new Map();
  }

  register(service) {
    const id = service.id || uuidv4();
    const registration = {
      id,
      name: service.name,
      version: service.version || '1.0.0',
      endpoint: service.endpoint,
      capabilities: service.capabilities || [],
      metadata: service.metadata || {},
      status: 'registered',
      registeredAt: new Date(),
      lastHeartbeat: new Date()
    };

    this.services.set(id, registration);
    this.emit('service:registered', registration);

    if (service.dependencies) {
      this.dependencies.set(id, service.dependencies);
    }

    return { id, status: 'registered' };
  }

  deregister(serviceId) {
    if (this.services.has(serviceId)) {
      const service = this.services.get(serviceId);
      this.services.delete(serviceId);
      this.dependencies.delete(serviceId);
      this.healthChecks.delete(serviceId);
      this.emit('service:deregistered', service);
      return { status: 'deregistered' };
    }
    return { status: 'not_found' };
  }

  discover(query = {}) {
    const results = [];
    for (const [id, service] of this.services) {
      let match = true;

      if (query.name && service.name !== query.name) match = false;
      if (query.capability && !service.capabilities.includes(query.capability)) match = false;
      if (query.status && service.status !== query.status) match = false;

      if (match) results.push(service);
    }
    return results;
  }

  getService(serviceId) {
    return this.services.get(serviceId);
  }

  updateStatus(serviceId, status) {
    const service = this.services.get(serviceId);
    if (service) {
      service.status = status;
      service.lastHeartbeat = new Date();
      this.emit('service:status_changed', { serviceId, status });
      return { status: 'updated' };
    }
    return { status: 'not_found' };
  }

  checkDependencies(serviceId) {
    const deps = this.dependencies.get(serviceId);
    if (!deps) return { satisfied: true, missing: [] };

    const missing = [];
    for (const dep of deps) {
      const found = this.discover({ name: dep, status: 'healthy' });
      if (found.length === 0) missing.push(dep);
    }

    return {
      satisfied: missing.length === 0,
      missing
    };
  }

  startHealthChecking() {
    setInterval(() => {
      for (const [id, service] of this.services) {
        const timeSinceHeartbeat = Date.now() - service.lastHeartbeat.getTime();
        if (timeSinceHeartbeat > 30000) {
          service.status = 'unhealthy';
          this.emit('service:unhealthy', service);
        }
      }
    }, 10000);
  }
}

const registry = new ServiceRegistry();
const app = express();
app.use(express.json());

app.post('/register', (req, res) => {
  const result = registry.register(req.body);
  res.json(result);
});

app.delete('/deregister/:id', (req, res) => {
  const result = registry.deregister(req.params.id);
  res.json(result);
});

app.get('/discover', (req, res) => {
  const services = registry.discover(req.query);
  res.json(services);
});

app.get('/service/:id', (req, res) => {
  const service = registry.getService(req.params.id);
  res.json(service || { status: 'not_found' });
});

app.post('/heartbeat/:id', (req, res) => {
  const result = registry.updateStatus(req.params.id, 'healthy');
  res.json(result);
});

app.get('/dependencies/:id', (req, res) => {
  const result = registry.checkDependencies(req.params.id);
  res.json(result);
});

const PORT = process.env.PORT || 3001;
app.listen(PORT, () => {
  console.log(`Service Registry running on port ${PORT}`);
  registry.startHealthChecking();
});

module.exports = registry;