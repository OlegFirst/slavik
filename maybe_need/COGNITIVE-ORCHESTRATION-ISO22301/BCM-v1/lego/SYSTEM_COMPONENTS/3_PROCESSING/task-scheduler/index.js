const cron = require('node-cron');
const Agenda = require('agenda');
const { EventEmitter } = require('events');
const { v4: uuidv4 } = require('uuid');
const moment = require('moment');

class UniversalTaskScheduler extends EventEmitter {
  constructor(config = {}) {
    super();
    this.config = {
      type: config.type || 'memory',
      mongodb: config.mongodb || 'mongodb://localhost:27017/scheduler',
      ...config
    };

    this.tasks = new Map();
    this.cronJobs = new Map();
    this.taskHistory = [];
    this.agenda = null;

    if (this.config.type === 'persistent') {
      this.initAgenda();
    }
  }

  async initAgenda() {
    this.agenda = new Agenda({
      db: { address: this.config.mongodb },
      processEvery: '10 seconds',
      maxConcurrency: 20
    });

    this.agenda.on('ready', () => {
      console.log('Agenda scheduler ready');
      this.emit('scheduler:ready');
    });

    this.agenda.on('complete', (job) => {
      this.emit('task:completed', {
        name: job.attrs.name,
        data: job.attrs.data,
        completedAt: new Date()
      });
    });

    this.agenda.on('fail', (err, job) => {
      this.emit('task:failed', {
        name: job.attrs.name,
        error: err.message,
        failedAt: new Date()
      });
    });

    await this.agenda.start();
  }

  scheduleTask(taskConfig) {
    const taskId = taskConfig.id || uuidv4();
    const task = {
      id: taskId,
      name: taskConfig.name,
      type: taskConfig.type || 'once',
      schedule: taskConfig.schedule,
      handler: taskConfig.handler,
      data: taskConfig.data || {},
      enabled: taskConfig.enabled !== false,
      createdAt: new Date(),
      lastRun: null,
      nextRun: null,
      runCount: 0
    };

    if (task.type === 'cron') {
      this.scheduleCronTask(task);
    } else if (task.type === 'interval') {
      this.scheduleIntervalTask(task);
    } else if (task.type === 'once') {
      this.scheduleOnceTask(task);
    } else if (task.type === 'recurring' && this.agenda) {
      this.scheduleRecurringTask(task);
    }

    this.tasks.set(taskId, task);
    this.emit('task:scheduled', task);

    return { id: taskId, status: 'scheduled' };
  }

  scheduleCronTask(task) {
    if (!cron.validate(task.schedule)) {
      throw new Error(`Invalid cron expression: ${task.schedule}`);
    }

    const job = cron.schedule(task.schedule, async () => {
      if (!task.enabled) return;

      try {
        task.lastRun = new Date();
        task.runCount++;

        const result = await this.executeTask(task);

        this.emit('task:executed', {
          id: task.id,
          name: task.name,
          result,
          executedAt: task.lastRun
        });

        this.addToHistory(task, 'success', result);
      } catch (error) {
        this.emit('task:error', {
          id: task.id,
          name: task.name,
          error: error.message
        });

        this.addToHistory(task, 'error', error.message);
      }
    });

    job.start();
    this.cronJobs.set(task.id, job);
  }

  scheduleIntervalTask(task) {
    const interval = this.parseInterval(task.schedule);

    const intervalId = setInterval(async () => {
      if (!task.enabled) return;

      try {
        task.lastRun = new Date();
        task.runCount++;

        const result = await this.executeTask(task);

        this.emit('task:executed', {
          id: task.id,
          name: task.name,
          result
        });

        this.addToHistory(task, 'success', result);
      } catch (error) {
        this.emit('task:error', {
          id: task.id,
          name: task.name,
          error: error.message
        });

        this.addToHistory(task, 'error', error.message);
      }
    }, interval);

    this.cronJobs.set(task.id, intervalId);
  }

  scheduleOnceTask(task) {
    const delay = this.parseDelay(task.schedule);

    setTimeout(async () => {
      if (!task.enabled) return;

      try {
        task.lastRun = new Date();
        task.runCount++;

        const result = await this.executeTask(task);

        this.emit('task:executed', {
          id: task.id,
          name: task.name,
          result
        });

        this.addToHistory(task, 'success', result);
        this.tasks.delete(task.id);
      } catch (error) {
        this.emit('task:error', {
          id: task.id,
          name: task.name,
          error: error.message
        });

        this.addToHistory(task, 'error', error.message);
      }
    }, delay);
  }

  async scheduleRecurringTask(task) {
    if (!this.agenda) return;

    this.agenda.define(task.name, async (job) => {
      try {
        const result = await this.executeTask(task);
        task.lastRun = new Date();
        task.runCount++;

        this.addToHistory(task, 'success', result);
      } catch (error) {
        this.addToHistory(task, 'error', error.message);
        throw error;
      }
    });

    await this.agenda.every(task.schedule, task.name, task.data);
  }

  async executeTask(task) {
    if (typeof task.handler === 'function') {
      return await task.handler(task.data);
    } else if (typeof task.handler === 'string') {
      this.emit('task:execute', {
        id: task.id,
        name: task.name,
        handler: task.handler,
        data: task.data
      });
      return { executed: task.handler };
    }
    return { executed: true };
  }

  pauseTask(taskId) {
    const task = this.tasks.get(taskId);
    if (task) {
      task.enabled = false;
      const job = this.cronJobs.get(taskId);
      if (job && job.stop) job.stop();

      this.emit('task:paused', { id: taskId });
      return { status: 'paused' };
    }
    return { status: 'not_found' };
  }

  resumeTask(taskId) {
    const task = this.tasks.get(taskId);
    if (task) {
      task.enabled = true;
      const job = this.cronJobs.get(taskId);
      if (job && job.start) job.start();

      this.emit('task:resumed', { id: taskId });
      return { status: 'resumed' };
    }
    return { status: 'not_found' };
  }

  deleteTask(taskId) {
    const task = this.tasks.get(taskId);
    if (task) {
      const job = this.cronJobs.get(taskId);
      if (job) {
        if (job.stop) job.stop();
        if (job.destroy) job.destroy();
        clearInterval(job);
      }

      this.tasks.delete(taskId);
      this.cronJobs.delete(taskId);

      this.emit('task:deleted', { id: taskId });
      return { status: 'deleted' };
    }
    return { status: 'not_found' };
  }

  getTask(taskId) {
    return this.tasks.get(taskId);
  }

  getAllTasks() {
    return Array.from(this.tasks.values());
  }

  getTaskHistory(taskId, limit = 10) {
    return this.taskHistory
      .filter(h => h.taskId === taskId)
      .slice(-limit);
  }

  addToHistory(task, status, result) {
    const historyEntry = {
      taskId: task.id,
      taskName: task.name,
      status,
      result,
      executedAt: new Date(),
      runCount: task.runCount
    };

    this.taskHistory.push(historyEntry);

    if (this.taskHistory.length > 1000) {
      this.taskHistory = this.taskHistory.slice(-500);
    }
  }

  parseInterval(schedule) {
    const match = schedule.match(/(\d+)([smhd])/);
    if (!match) throw new Error('Invalid interval format');

    const value = parseInt(match[1]);
    const unit = match[2];

    const multipliers = {
      's': 1000,
      'm': 60000,
      'h': 3600000,
      'd': 86400000
    };

    return value * multipliers[unit];
  }

  parseDelay(schedule) {
    if (typeof schedule === 'number') return schedule;
    if (schedule instanceof Date) return schedule.getTime() - Date.now();
    return this.parseInterval(schedule);
  }

  async shutdown() {
    for (const [id, job] of this.cronJobs) {
      if (job.stop) job.stop();
      if (job.destroy) job.destroy();
      clearInterval(job);
    }

    if (this.agenda) {
      await this.agenda.stop();
    }

    this.emit('scheduler:shutdown');
  }
}

const express = require('express');
const app = express();
app.use(express.json());

const scheduler = new UniversalTaskScheduler();

app.post('/schedule', (req, res) => {
  const result = scheduler.scheduleTask(req.body);
  res.json(result);
});

app.post('/pause/:id', (req, res) => {
  const result = scheduler.pauseTask(req.params.id);
  res.json(result);
});

app.post('/resume/:id', (req, res) => {
  const result = scheduler.resumeTask(req.params.id);
  res.json(result);
});

app.delete('/task/:id', (req, res) => {
  const result = scheduler.deleteTask(req.params.id);
  res.json(result);
});

app.get('/task/:id', (req, res) => {
  const task = scheduler.getTask(req.params.id);
  res.json(task || { status: 'not_found' });
});

app.get('/tasks', (req, res) => {
  const tasks = scheduler.getAllTasks();
  res.json(tasks);
});

app.get('/history/:id', (req, res) => {
  const history = scheduler.getTaskHistory(req.params.id);
  res.json(history);
});

const PORT = process.env.PORT || 3003;
app.listen(PORT, () => {
  console.log(`Task Scheduler running on port ${PORT}`);
});

module.exports = UniversalTaskScheduler;