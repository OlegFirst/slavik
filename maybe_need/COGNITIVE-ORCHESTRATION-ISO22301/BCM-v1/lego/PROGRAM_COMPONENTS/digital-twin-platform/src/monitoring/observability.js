/**
 * Observability and Monitoring System
 * Tracks metrics, performance, and system health
 */

import { EventEmitter } from 'events';
import { performance } from 'perf_hooks';
import { createLogger } from '../../utils/logger.js';

const logger = createLogger('Observability');

class ObservabilitySystem extends EventEmitter {
    constructor() {
        super();
        
        // Metrics storage
        this.metrics = {
            api: {
                requests: 0,
                errors: 0,
                latency: [],
                p95: 0,
                p99: 0
            },
            simulations: {
                total: 0,
                completed: 0,
                failed: 0,
                duration: []
            },
            database: {
                queries: 0,
                errors: 0,
                latency: []
            },
            events: {
                processed: 0,
                failed: 0,
                queueDepth: 0
            },
            system: {
                memory: {},
                cpu: {},
                uptime: 0
            }
        };
        
        // Start collectors
        this.startMetricsCollection();
    }
    
    /**
     * Track API request
     */
    trackAPIRequest(method, path, statusCode, duration) {
        this.metrics.api.requests++;
        
        if (statusCode >= 400) {
            this.metrics.api.errors++;
        }
        
        this.metrics.api.latency.push(duration);
        
        // Keep only last 1000 measurements
        if (this.metrics.api.latency.length > 1000) {
            this.metrics.api.latency.shift();
        }
        
        // Calculate percentiles
        this.calculatePercentiles();
        
        // Emit metric event
        this.emit('metric', {
            type: 'api_request',
            method,
            path,
            statusCode,
            duration
        });
        
        // Alert if high error rate
        const errorRate = this.metrics.api.errors / this.metrics.api.requests;
        if (errorRate > 0.05) { // 5% error rate threshold
            this.emit('alert', {
                severity: 'warning',
                message: `High API error rate: ${(errorRate * 100).toFixed(2)}%`
            });
        }
    }
    
    /**
     * Track simulation execution
     */
    trackSimulation(scenario, status, duration) {
        this.metrics.simulations.total++;
        
        if (status === 'completed') {
            this.metrics.simulations.completed++;
        } else {
            this.metrics.simulations.failed++;
        }
        
        this.metrics.simulations.duration.push(duration);
        
        // Keep only last 100 simulations
        if (this.metrics.simulations.duration.length > 100) {
            this.metrics.simulations.duration.shift();
        }
        
        this.emit('metric', {
            type: 'simulation',
            scenario,
            status,
            duration
        });
        
        // Alert if simulation takes too long
        if (duration > 30000) { // 30 seconds
            this.emit('alert', {
                severity: 'warning',
                message: `Slow simulation: ${scenario} took ${duration}ms`
            });
        }
    }
    
    /**
     * Track database query
     */
    trackDatabaseQuery(query, duration, error = null) {
        this.metrics.database.queries++;
        
        if (error) {
            this.metrics.database.errors++;
        }
        
        this.metrics.database.latency.push(duration);
        
        // Keep only last 1000 measurements
        if (this.metrics.database.latency.length > 1000) {
            this.metrics.database.latency.shift();
        }
        
        this.emit('metric', {
            type: 'database_query',
            query: query.substring(0, 100), // Truncate for logging
            duration,
            error: error?.message
        });
        
        // Alert if query is slow
        if (duration > 1000) { // 1 second
            this.emit('alert', {
                severity: 'info',
                message: `Slow query detected: ${duration}ms`
            });
        }
    }
    
    /**
     * Track event processing
     */
    trackEvent(eventType, status, queueDepth = 0) {
        this.metrics.events.processed++;
        
        if (status === 'failed') {
            this.metrics.events.failed++;
        }
        
        this.metrics.events.queueDepth = queueDepth;
        
        this.emit('metric', {
            type: 'event_processing',
            eventType,
            status,
            queueDepth
        });
        
        // Alert if queue is growing
        if (queueDepth > 100) {
            this.emit('alert', {
                severity: 'warning',
                message: `Event queue depth high: ${queueDepth}`
            });
        }
    }
    
    /**
     * Calculate percentiles for latency metrics
     */
    calculatePercentiles() {
        const latencies = [...this.metrics.api.latency].sort((a, b) => a - b);
        
        if (latencies.length > 0) {
            const p95Index = Math.floor(latencies.length * 0.95);
            const p99Index = Math.floor(latencies.length * 0.99);
            
            this.metrics.api.p95 = latencies[p95Index];
            this.metrics.api.p99 = latencies[p99Index];
        }
    }
    
    /**
     * Start system metrics collection
     */
    startMetricsCollection() {
        // Collect system metrics every 30 seconds
        setInterval(() => {
            const memUsage = process.memoryUsage();
            const cpuUsage = process.cpuUsage();
            
            this.metrics.system.memory = {
                rss: memUsage.rss / 1024 / 1024, // MB
                heapTotal: memUsage.heapTotal / 1024 / 1024,
                heapUsed: memUsage.heapUsed / 1024 / 1024,
                external: memUsage.external / 1024 / 1024
            };
            
            this.metrics.system.cpu = {
                user: cpuUsage.user / 1000000, // seconds
                system: cpuUsage.system / 1000000
            };
            
            this.metrics.system.uptime = process.uptime();
            
            // Check memory usage
            if (this.metrics.system.memory.heapUsed > 500) { // 500MB threshold
                this.emit('alert', {
                    severity: 'warning',
                    message: `High memory usage: ${this.metrics.system.memory.heapUsed.toFixed(2)}MB`
                });
            }
            
        }, 30000);
    }
    
    /**
     * Get current metrics snapshot
     */
    getMetrics() {
        return {
            timestamp: new Date().toISOString(),
            api: {
                ...this.metrics.api,
                errorRate: this.metrics.api.requests > 0 
                    ? this.metrics.api.errors / this.metrics.api.requests 
                    : 0,
                avgLatency: this.metrics.api.latency.length > 0
                    ? this.metrics.api.latency.reduce((a, b) => a + b, 0) / this.metrics.api.latency.length
                    : 0
            },
            simulations: {
                ...this.metrics.simulations,
                successRate: this.metrics.simulations.total > 0
                    ? this.metrics.simulations.completed / this.metrics.simulations.total
                    : 0,
                avgDuration: this.metrics.simulations.duration.length > 0
                    ? this.metrics.simulations.duration.reduce((a, b) => a + b, 0) / this.metrics.simulations.duration.length
                    : 0
            },
            database: {
                ...this.metrics.database,
                errorRate: this.metrics.database.queries > 0
                    ? this.metrics.database.errors / this.metrics.database.queries
                    : 0,
                avgLatency: this.metrics.database.latency.length > 0
                    ? this.metrics.database.latency.reduce((a, b) => a + b, 0) / this.metrics.database.latency.length
                    : 0
            },
            events: {
                ...this.metrics.events,
                failureRate: this.metrics.events.processed > 0
                    ? this.metrics.events.failed / this.metrics.events.processed
                    : 0
            },
            system: this.metrics.system
        };
    }
    
    /**
     * Reset metrics
     */
    resetMetrics() {
        this.metrics.api.latency = [];
        this.metrics.simulations.duration = [];
        this.metrics.database.latency = [];
        logger.info('Metrics reset');
    }
    
    /**
     * Export metrics in Prometheus format
     */
    getPrometheusMetrics() {
        const metrics = this.getMetrics();
        
        return `
# HELP api_requests_total Total number of API requests
# TYPE api_requests_total counter
api_requests_total ${metrics.api.requests}

# HELP api_errors_total Total number of API errors
# TYPE api_errors_total counter
api_errors_total ${metrics.api.errors}

# HELP api_latency_p95 95th percentile API latency in milliseconds
# TYPE api_latency_p95 gauge
api_latency_p95 ${metrics.api.p95}

# HELP api_latency_p99 99th percentile API latency in milliseconds
# TYPE api_latency_p99 gauge
api_latency_p99 ${metrics.api.p99}

# HELP simulations_total Total number of simulations
# TYPE simulations_total counter
simulations_total ${metrics.simulations.total}

# HELP simulations_completed_total Total number of completed simulations
# TYPE simulations_completed_total counter
simulations_completed_total ${metrics.simulations.completed}

# HELP simulations_failed_total Total number of failed simulations
# TYPE simulations_failed_total counter
simulations_failed_total ${metrics.simulations.failed}

# HELP database_queries_total Total number of database queries
# TYPE database_queries_total counter
database_queries_total ${metrics.database.queries}

# HELP database_errors_total Total number of database errors
# TYPE database_errors_total counter
database_errors_total ${metrics.database.errors}

# HELP events_processed_total Total number of processed events
# TYPE events_processed_total counter
events_processed_total ${metrics.events.processed}

# HELP events_queue_depth Current event queue depth
# TYPE events_queue_depth gauge
events_queue_depth ${metrics.events.queueDepth}

# HELP memory_heap_used_mb Heap memory used in MB
# TYPE memory_heap_used_mb gauge
memory_heap_used_mb ${metrics.system.memory.heapUsed}

# HELP uptime_seconds System uptime in seconds
# TYPE uptime_seconds gauge
uptime_seconds ${metrics.system.uptime}
        `.trim();
    }
}

// Create singleton instance
const observability = new ObservabilitySystem();

// Express middleware for tracking API requests
export function apiMetricsMiddleware(req, res, next) {
    const start = performance.now();
    
    // Intercept response
    const originalSend = res.send;
    res.send = function(data) {
        const duration = performance.now() - start;
        observability.trackAPIRequest(req.method, req.path, res.statusCode, duration);
        originalSend.call(this, data);
    };
    
    next();
}

// Database query wrapper
export function trackQuery(queryFunction) {
    return async function(...args) {
        const start = performance.now();
        let error = null;
        
        try {
            const result = await queryFunction.apply(this, args);
            return result;
        } catch (err) {
            error = err;
            throw err;
        } finally {
            const duration = performance.now() - start;
            observability.trackDatabaseQuery(args[0], duration, error);
        }
    };
}

// Simulation tracking wrapper
export function trackSimulation(simulationFunction) {
    return async function(scenario, ...args) {
        const start = performance.now();
        let status = 'completed';
        
        try {
            const result = await simulationFunction.apply(this, [scenario, ...args]);
            return result;
        } catch (error) {
            status = 'failed';
            throw error;
        } finally {
            const duration = performance.now() - start;
            observability.trackSimulation(scenario, status, duration);
        }
    };
}

// Alert handler
observability.on('alert', (alert) => {
    logger.warn(`ALERT [${alert.severity}]: ${alert.message}`);
    
    // Send to monitoring service (DataDog, New Relic, etc.)
    // sendAlertToMonitoring(alert);
});

export default observability;