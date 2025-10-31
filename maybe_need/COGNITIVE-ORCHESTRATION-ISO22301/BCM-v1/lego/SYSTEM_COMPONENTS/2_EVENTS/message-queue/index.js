const amqp = require('amqplib');
const Bull = require('bull');
const { EventEmitter } = require('events');
const { v4: uuidv4 } = require('uuid');

class UniversalMessageQueue extends EventEmitter {
  constructor(config = {}) {
    super();
    this.config = {
      type: config.type || 'redis',
      redis: config.redis || { host: 'localhost', port: 6379 },
      rabbitmq: config.rabbitmq || 'amqp://localhost',
      ...config
    };

    this.queues = new Map();
    this.processors = new Map();
    this.connection = null;
    this.channel = null;
  }

  async init() {
    if (this.config.type === 'rabbitmq') {
      await this.initRabbitMQ();
    }
    this.emit('queue:initialized', { type: this.config.type });
  }

  async initRabbitMQ() {
    try {
      this.connection = await amqp.connect(this.config.rabbitmq);
      this.channel = await this.connection.createChannel();
      console.log('RabbitMQ connection established');
    } catch (error) {
      console.error('RabbitMQ connection failed:', error);
      this.config.type = 'redis';
    }
  }

  createQueue(name, options = {}) {
    if (this.queues.has(name)) {
      return this.queues.get(name);
    }

    let queue;
    if (this.config.type === 'redis') {
      queue = new Bull(name, {
        redis: this.config.redis,
        defaultJobOptions: {
          removeOnComplete: true,
          removeOnFail: false,
          attempts: options.attempts || 3,
          backoff: {
            type: 'exponential',
            delay: 2000
          }
        }
      });

      queue.on('completed', (job, result) => {
        this.emit('job:completed', { queue: name, jobId: job.id, result });
      });

      queue.on('failed', (job, err) => {
        this.emit('job:failed', { queue: name, jobId: job.id, error: err.message });
      });
    } else if (this.config.type === 'rabbitmq' && this.channel) {
      this.channel.assertQueue(name, { durable: true });
      queue = {
        name,
        channel: this.channel,
        add: async (data, opts = {}) => {
          const message = {
            id: uuidv4(),
            data,
            timestamp: new Date(),
            ...opts
          };
          this.channel.sendToQueue(name, Buffer.from(JSON.stringify(message)));
          return { id: message.id };
        }
      };
    }

    this.queues.set(name, queue);
    this.emit('queue:created', { name, type: this.config.type });
    return queue;
  }

  async publish(queueName, data, options = {}) {
    const queue = this.createQueue(queueName);

    const job = await queue.add(data, {
      delay: options.delay || 0,
      priority: options.priority || 0,
      attempts: options.attempts || 3
    });

    this.emit('message:published', {
      queue: queueName,
      jobId: job.id || uuidv4(),
      data
    });

    return job;
  }

  subscribe(queueName, processor, options = {}) {
    const queue = this.createQueue(queueName);

    if (this.config.type === 'redis') {
      queue.process(options.concurrency || 1, async (job) => {
        try {
          const result = await processor(job.data);
          this.emit('message:processed', {
            queue: queueName,
            jobId: job.id,
            result
          });
          return result;
        } catch (error) {
          this.emit('message:error', {
            queue: queueName,
            jobId: job.id,
            error: error.message
          });
          throw error;
        }
      });
    } else if (this.config.type === 'rabbitmq' && this.channel) {
      this.channel.consume(queueName, async (msg) => {
        if (msg) {
          const content = JSON.parse(msg.content.toString());
          try {
            const result = await processor(content.data);
            this.channel.ack(msg);
            this.emit('message:processed', {
              queue: queueName,
              messageId: content.id,
              result
            });
          } catch (error) {
            this.channel.nack(msg, false, true);
            this.emit('message:error', {
              queue: queueName,
              messageId: content.id,
              error: error.message
            });
          }
        }
      });
    }

    this.processors.set(queueName, processor);
    this.emit('subscriber:registered', { queue: queueName });
  }

  async getQueueStats(queueName) {
    const queue = this.queues.get(queueName);
    if (!queue) return null;

    if (this.config.type === 'redis') {
      const [waiting, active, completed, failed] = await Promise.all([
        queue.getWaitingCount(),
        queue.getActiveCount(),
        queue.getCompletedCount(),
        queue.getFailedCount()
      ]);

      return { waiting, active, completed, failed };
    }

    return { status: 'statistics not available for current queue type' };
  }

  async purgeQueue(queueName) {
    const queue = this.queues.get(queueName);
    if (!queue) return { status: 'queue_not_found' };

    if (this.config.type === 'redis') {
      await queue.empty();
    } else if (this.config.type === 'rabbitmq' && this.channel) {
      await this.channel.purgeQueue(queueName);
    }

    this.emit('queue:purged', { queue: queueName });
    return { status: 'purged' };
  }

  async scheduleRecurring(queueName, data, cronExpression) {
    const queue = this.createQueue(queueName);

    if (this.config.type === 'redis') {
      await queue.add(data, {
        repeat: { cron: cronExpression }
      });
    }

    this.emit('job:scheduled', {
      queue: queueName,
      cron: cronExpression
    });
  }

  async close() {
    for (const [name, queue] of this.queues) {
      if (queue.close) await queue.close();
    }

    if (this.connection) {
      await this.connection.close();
    }

    this.emit('queue:closed');
  }
}

const express = require('express');
const app = express();
app.use(express.json());

const mq = new UniversalMessageQueue();

app.post('/publish/:queue', async (req, res) => {
  const job = await mq.publish(req.params.queue, req.body.data, req.body.options);
  res.json({ jobId: job.id || job.jobId, status: 'published' });
});

app.post('/subscribe/:queue', (req, res) => {
  mq.subscribe(req.params.queue, async (data) => {
    console.log(`Processing message in ${req.params.queue}:`, data);
    return { processed: true };
  });
  res.json({ status: 'subscribed' });
});

app.get('/stats/:queue', async (req, res) => {
  const stats = await mq.getQueueStats(req.params.queue);
  res.json(stats || { status: 'not_found' });
});

app.delete('/purge/:queue', async (req, res) => {
  const result = await mq.purgeQueue(req.params.queue);
  res.json(result);
});

const PORT = process.env.PORT || 3002;
app.listen(PORT, async () => {
  await mq.init();
  console.log(`Message Queue service running on port ${PORT}`);
});

module.exports = UniversalMessageQueue;