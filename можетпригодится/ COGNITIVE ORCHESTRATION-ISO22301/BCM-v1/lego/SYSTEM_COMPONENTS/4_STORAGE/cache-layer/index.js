const Redis = require('ioredis');
const NodeCache = require('node-cache');
const LRU = require('lru-cache');
const { EventEmitter } = require('events');

class UniversalCacheLayer extends EventEmitter {
  constructor(config = {}) {
    super();
    this.config = {
      type: config.type || 'memory',
      redis: config.redis || { host: 'localhost', port: 6379 },
      ttl: config.ttl || 3600,
      maxSize: config.maxSize || 1000,
      checkPeriod: config.checkPeriod || 600,
      ...config
    };

    this.stats = {
      hits: 0,
      misses: 0,
      sets: 0,
      deletes: 0,
      evictions: 0
    };

    this.initCache();
  }

  initCache() {
    switch (this.config.type) {
      case 'redis':
        this.cache = new Redis(this.config.redis);
        this.cache.on('connect', () => {
          console.log('Redis cache connected');
          this.emit('cache:connected');
        });
        this.cache.on('error', (err) => {
          console.error('Redis cache error:', err);
          this.emit('cache:error', err);
          this.fallbackToMemory();
        });
        break;

      case 'lru':
        this.cache = new LRU({
          max: this.config.maxSize,
          ttl: this.config.ttl * 1000,
          updateAgeOnGet: true,
          updateAgeOnHas: false,
          dispose: (value, key) => {
            this.stats.evictions++;
            this.emit('cache:evicted', { key, value });
          }
        });
        break;

      case 'memory':
      default:
        this.cache = new NodeCache({
          stdTTL: this.config.ttl,
          checkperiod: this.config.checkPeriod,
          maxKeys: this.config.maxSize,
          useClones: false
        });

        this.cache.on('expired', (key, value) => {
          this.stats.evictions++;
          this.emit('cache:expired', { key, value });
        });
        break;
    }
  }

  fallbackToMemory() {
    console.log('Falling back to memory cache');
    this.config.type = 'memory';
    this.initCache();
  }

  async get(key, options = {}) {
    try {
      let value;

      if (this.config.type === 'redis') {
        const data = await this.cache.get(key);
        value = data ? JSON.parse(data) : null;
      } else if (this.config.type === 'lru') {
        value = this.cache.get(key);
      } else {
        value = this.cache.get(key);
      }

      if (value !== undefined && value !== null) {
        this.stats.hits++;
        this.emit('cache:hit', { key, value });

        if (options.refresh && this.config.type === 'redis') {
          await this.cache.expire(key, this.config.ttl);
        }

        return value;
      } else {
        this.stats.misses++;
        this.emit('cache:miss', { key });

        if (options.loader) {
          const loadedValue = await options.loader();
          if (loadedValue !== undefined) {
            await this.set(key, loadedValue, options.ttl);
            return loadedValue;
          }
        }

        return null;
      }
    } catch (error) {
      this.emit('cache:error', { operation: 'get', key, error });
      return null;
    }
  }

  async set(key, value, ttl = null) {
    try {
      const effectiveTtl = ttl || this.config.ttl;
      this.stats.sets++;

      if (this.config.type === 'redis') {
        await this.cache.set(
          key,
          JSON.stringify(value),
          'EX',
          effectiveTtl
        );
      } else if (this.config.type === 'lru') {
        this.cache.set(key, value, { ttl: effectiveTtl * 1000 });
      } else {
        this.cache.set(key, value, effectiveTtl);
      }

      this.emit('cache:set', { key, value, ttl: effectiveTtl });
      return true;
    } catch (error) {
      this.emit('cache:error', { operation: 'set', key, error });
      return false;
    }
  }

  async delete(key) {
    try {
      this.stats.deletes++;

      if (this.config.type === 'redis') {
        await this.cache.del(key);
      } else if (this.config.type === 'lru') {
        this.cache.delete(key);
      } else {
        this.cache.del(key);
      }

      this.emit('cache:deleted', { key });
      return true;
    } catch (error) {
      this.emit('cache:error', { operation: 'delete', key, error });
      return false;
    }
  }

  async has(key) {
    try {
      if (this.config.type === 'redis') {
        return (await this.cache.exists(key)) === 1;
      } else if (this.config.type === 'lru') {
        return this.cache.has(key);
      } else {
        return this.cache.has(key);
      }
    } catch (error) {
      this.emit('cache:error', { operation: 'has', key, error });
      return false;
    }
  }

  async mget(keys) {
    try {
      if (this.config.type === 'redis') {
        const values = await this.cache.mget(keys);
        return values.map(v => v ? JSON.parse(v) : null);
      } else {
        return keys.map(key => this.cache.get(key));
      }
    } catch (error) {
      this.emit('cache:error', { operation: 'mget', keys, error });
      return keys.map(() => null);
    }
  }

  async mset(entries, ttl = null) {
    try {
      const effectiveTtl = ttl || this.config.ttl;

      if (this.config.type === 'redis') {
        const pipeline = this.cache.pipeline();
        for (const [key, value] of entries) {
          pipeline.set(key, JSON.stringify(value), 'EX', effectiveTtl);
        }
        await pipeline.exec();
      } else {
        for (const [key, value] of entries) {
          await this.set(key, value, effectiveTtl);
        }
      }

      this.stats.sets += entries.length;
      return true;
    } catch (error) {
      this.emit('cache:error', { operation: 'mset', error });
      return false;
    }
  }

  async flush() {
    try {
      if (this.config.type === 'redis') {
        await this.cache.flushdb();
      } else if (this.config.type === 'lru') {
        this.cache.clear();
      } else {
        this.cache.flushAll();
      }

      this.resetStats();
      this.emit('cache:flushed');
      return true;
    } catch (error) {
      this.emit('cache:error', { operation: 'flush', error });
      return false;
    }
  }

  async keys(pattern = '*') {
    try {
      if (this.config.type === 'redis') {
        return await this.cache.keys(pattern);
      } else if (this.config.type === 'lru') {
        return Array.from(this.cache.keys());
      } else {
        return this.cache.keys();
      }
    } catch (error) {
      this.emit('cache:error', { operation: 'keys', error });
      return [];
    }
  }

  async getOrSet(key, loader, ttl = null) {
    const value = await this.get(key);
    if (value !== null) return value;

    const loadedValue = await loader();
    await this.set(key, loadedValue, ttl);
    return loadedValue;
  }

  wrap(fn, keyGenerator, ttl = null) {
    return async (...args) => {
      const key = typeof keyGenerator === 'function'
        ? keyGenerator(...args)
        : `${keyGenerator}:${JSON.stringify(args)}`;

      return this.getOrSet(key, () => fn(...args), ttl);
    };
  }

  getStats() {
    const hitRate = this.stats.hits + this.stats.misses > 0
      ? (this.stats.hits / (this.stats.hits + this.stats.misses)) * 100
      : 0;

    return {
      ...this.stats,
      hitRate: hitRate.toFixed(2) + '%',
      size: this.getSize()
    };
  }

  getSize() {
    if (this.config.type === 'lru') {
      return this.cache.size;
    } else if (this.config.type === 'memory') {
      return this.cache.keys().length;
    }
    return 'N/A';
  }

  resetStats() {
    this.stats = {
      hits: 0,
      misses: 0,
      sets: 0,
      deletes: 0,
      evictions: 0
    };
  }

  async close() {
    if (this.config.type === 'redis') {
      await this.cache.quit();
    }
    this.emit('cache:closed');
  }
}

const express = require('express');
const app = express();
app.use(express.json());

const cache = new UniversalCacheLayer();

app.get('/get/:key', async (req, res) => {
  const value = await cache.get(req.params.key);
  res.json({ key: req.params.key, value, found: value !== null });
});

app.post('/set/:key', async (req, res) => {
  const success = await cache.set(req.params.key, req.body.value, req.body.ttl);
  res.json({ key: req.params.key, success });
});

app.delete('/delete/:key', async (req, res) => {
  const success = await cache.delete(req.params.key);
  res.json({ key: req.params.key, success });
});

app.post('/mset', async (req, res) => {
  const entries = Object.entries(req.body.data);
  const success = await cache.mset(entries, req.body.ttl);
  res.json({ success, count: entries.length });
});

app.get('/keys', async (req, res) => {
  const keys = await cache.keys(req.query.pattern);
  res.json({ keys, count: keys.length });
});

app.post('/flush', async (req, res) => {
  const success = await cache.flush();
  res.json({ success });
});

app.get('/stats', (req, res) => {
  res.json(cache.getStats());
});

const PORT = process.env.PORT || 3004;
app.listen(PORT, () => {
  console.log(`Cache Layer running on port ${PORT}`);
});

module.exports = UniversalCacheLayer;