/**
 * Event System - Central Nervous System of the Platform
 *
 * This is not just an event bus - it's the foundation for meta-consciousness.
 * Every event is a learning opportunity, every pattern is knowledge.
 */

import { EventEmitter } from 'events';
import { v4 as uuidv4 } from 'uuid';

class MetaEventSystem extends EventEmitter {
    constructor() {
        super();

        // Event history for pattern recognition
        this.eventHistory = [];

        // Event patterns for learning
        this.eventPatterns = new Map();

        // Correlation tracking
        this.correlations = new Map();

        // Meta-level: Self-awareness
        this.metaState = {
            totalEvents: 0,
            patterns: [],
            insights: [],
            performance: {},
            health: 'healthy'
        };

        // Intelligence hooks from day one
        this.intelligenceHooks = {
            beforeEmit: [],
            afterEmit: [],
            patternDetected: [],
            anomalyDetected: []
        };

        // Start self-monitoring
        this.startSelfMonitoring();
    }

    /**
     * Publish event with meta-tracking
     */
    async publish(eventType, data, metadata = {}) {
        const event = {
            id: uuidv4(),
            type: eventType,
            data,
            metadata: {
                ...metadata,
                timestamp: Date.now(),
                source: metadata.source || 'unknown',
                correlationId: metadata.correlationId || uuidv4(),
                priority: metadata.priority || 'normal'
            },
            metaInfo: {
                processingStarted: Date.now(),
                handlers: [],
                outcomes: []
            }
        };

        // Meta-level: Track every event
        this.trackEvent(event);

        // Intelligence hooks - before
        await this.runHooks('beforeEmit', event);

        // Check for patterns
        this.detectPatterns(event);

        // Emit with tracking
        const startTime = Date.now();

        try {
            // Emit to all listeners
            this.emit(eventType, event);

            // Emit to pattern listeners
            this.emit('*', event);

            event.metaInfo.processingTime = Date.now() - startTime;
            event.metaInfo.success = true;

        } catch (error) {
            event.metaInfo.processingTime = Date.now() - startTime;
            event.metaInfo.success = false;
            event.metaInfo.error = error.message;

            // Self-healing attempt
            this.attemptSelfHealing(event, error);
        }

        // Intelligence hooks - after
        await this.runHooks('afterEmit', event);

        // Store for learning
        this.storeForLearning(event);

        return event;
    }

    /**
     * Subscribe with intelligence
     */
    subscribe(eventType, handler, metadata = {}) {
        const wrappedHandler = async (event) => {
            const handlerInfo = {
                name: handler.name || 'anonymous',
                startTime: Date.now(),
                metadata
            };

            try {
                // Execute handler
                const result = await handler(event);

                handlerInfo.endTime = Date.now();
                handlerInfo.duration = handlerInfo.endTime - handlerInfo.startTime;
                handlerInfo.success = true;
                handlerInfo.result = result;

                // Track handler performance
                this.trackHandlerPerformance(eventType, handlerInfo);

                // Learn from outcomes
                if (event.metaInfo) {
                    event.metaInfo.handlers.push(handlerInfo);
                    event.metaInfo.outcomes.push(result);
                }

                return result;

            } catch (error) {
                handlerInfo.endTime = Date.now();
                handlerInfo.duration = handlerInfo.endTime - handlerInfo.startTime;
                handlerInfo.success = false;
                handlerInfo.error = error.message;

                // Track failure for learning
                this.trackHandlerFailure(eventType, handlerInfo, error);

                throw error;
            }
        };

        // Store handler metadata for introspection
        wrappedHandler.metadata = metadata;
        wrappedHandler.originalHandler = handler;

        this.on(eventType, wrappedHandler);

        return () => this.off(eventType, wrappedHandler);
    }

    /**
     * Pattern detection for meta-learning
     */
    detectPatterns(event) {
        // Simple pattern: Event sequences
        const recentEvents = this.eventHistory.slice(-10);
        const sequence = recentEvents.map(e => e.type).join('-');

        if (!this.eventPatterns.has(sequence)) {
            this.eventPatterns.set(sequence, 1);
        } else {
            const count = this.eventPatterns.get(sequence) + 1;
            this.eventPatterns.set(sequence, count);

            // Pattern detected
            if (count > 3) {
                const pattern = {
                    sequence,
                    count,
                    lastEvent: event,
                    timestamp: Date.now()
                };

                this.metaState.patterns.push(pattern);
                this.runHooks('patternDetected', pattern);

                // Generate insight
                this.generateInsight(pattern);
            }
        }

        // Anomaly detection
        this.detectAnomalies(event);
    }

    /**
     * Anomaly detection
     */
    detectAnomalies(event) {
        // Check if event is unusual
        const eventTypeHistory = this.eventHistory
            .filter(e => e.type === event.type)
            .slice(-100);

        if (eventTypeHistory.length > 10) {
            // Calculate average time between events
            const intervals = [];
            for (let i = 1; i < eventTypeHistory.length; i++) {
                intervals.push(
                    eventTypeHistory[i].metadata.timestamp -
                    eventTypeHistory[i-1].metadata.timestamp
                );
            }

            const avgInterval = intervals.reduce((a, b) => a + b, 0) / intervals.length;
            const currentInterval = Date.now() -
                (eventTypeHistory[eventTypeHistory.length - 1]?.metadata?.timestamp || 0);

            // Anomaly: Too fast or too slow
            if (currentInterval < avgInterval * 0.1 || currentInterval > avgInterval * 10) {
                const anomaly = {
                    type: 'timing',
                    event: event.type,
                    expected: avgInterval,
                    actual: currentInterval,
                    timestamp: Date.now()
                };

                this.runHooks('anomalyDetected', anomaly);
            }
        }
    }

    /**
     * Generate insights from patterns
     */
    generateInsight(pattern) {
        const insight = {
            id: uuidv4(),
            type: 'pattern_insight',
            pattern: pattern.sequence,
            frequency: pattern.count,
            recommendation: this.generateRecommendation(pattern),
            timestamp: Date.now()
        };

        this.metaState.insights.push(insight);

        // Publish insight as event (meta-event)
        this.publish('system:insight_generated', insight, {
            source: 'meta-event-system',
            priority: 'low'
        });
    }

    /**
     * Generate recommendations based on patterns
     */
    generateRecommendation(pattern) {
        // Simple heuristics for now, will be replaced with AI
        const sequence = pattern.sequence.split('-');

        if (sequence.includes('error') && sequence.includes('retry')) {
            return 'Consider implementing circuit breaker pattern';
        }

        if (sequence.filter(e => e === sequence[0]).length === sequence.length) {
            return 'Repetitive pattern detected, consider batching';
        }

        return 'Pattern recorded for future analysis';
    }

    /**
     * Self-monitoring
     */
    startSelfMonitoring() {
        setInterval(() => {
            const stats = {
                eventCount: this.eventHistory.length,
                patternCount: this.eventPatterns.size,
                insightCount: this.metaState.insights.length,
                listenerCount: this.eventNames().reduce((acc, name) =>
                    acc + this.listenerCount(name), 0
                ),
                memoryUsage: process.memoryUsage(),
                timestamp: Date.now()
            };

            this.metaState.performance = stats;

            // Check health
            if (stats.memoryUsage.heapUsed > 500 * 1024 * 1024) {
                this.metaState.health = 'memory_pressure';
                this.performCleanup();
            } else if (stats.eventCount > 10000) {
                this.metaState.health = 'high_load';
            } else {
                this.metaState.health = 'healthy';
            }

            // Publish self-monitoring event
            this.publish('system:self_monitoring', stats, {
                source: 'meta-event-system',
                priority: 'low'
            });

        }, 60000); // Every minute
    }

    /**
     * Self-healing mechanisms
     */
    attemptSelfHealing(event, error) {
        // Log for learning
        console.error(`Event processing failed: ${event.type}`, error);

        // Attempt recovery strategies
        if (error.message.includes('timeout')) {
            // Retry with increased timeout
            setTimeout(() => {
                this.publish(event.type, event.data, {
                    ...event.metadata,
                    retry: true,
                    originalId: event.id
                });
            }, 5000);
        }
    }

    /**
     * Cleanup old data
     */
    performCleanup() {
        // Keep only recent history
        const cutoff = Date.now() - (24 * 60 * 60 * 1000); // 24 hours

        this.eventHistory = this.eventHistory.filter(e =>
            e.metadata.timestamp > cutoff
        );

        // Clean patterns
        if (this.eventPatterns.size > 1000) {
            const sorted = Array.from(this.eventPatterns.entries())
                .sort((a, b) => b[1] - a[1])
                .slice(0, 500);

            this.eventPatterns = new Map(sorted);
        }
    }

    /**
     * Store for future learning
     */
    storeForLearning(event) {
        // In production, this would persist to database
        this.eventHistory.push(event);

        // Limit memory usage
        if (this.eventHistory.length > 10000) {
            this.eventHistory = this.eventHistory.slice(-5000);
        }
    }

    /**
     * Track event for meta-analysis
     */
    trackEvent(event) {
        this.metaState.totalEvents++;

        // Update correlations
        const correlationId = event.metadata.correlationId;
        if (!this.correlations.has(correlationId)) {
            this.correlations.set(correlationId, []);
        }
        this.correlations.get(correlationId).push(event);
    }

    /**
     * Track handler performance
     */
    trackHandlerPerformance(eventType, handlerInfo) {
        if (!this.metaState.performance[eventType]) {
            this.metaState.performance[eventType] = {
                calls: 0,
                totalDuration: 0,
                failures: 0,
                avgDuration: 0
            };
        }

        const perf = this.metaState.performance[eventType];
        perf.calls++;
        perf.totalDuration += handlerInfo.duration;
        perf.avgDuration = perf.totalDuration / perf.calls;
    }

    /**
     * Track handler failures
     */
    trackHandlerFailure(eventType, handlerInfo, error) {
        this.trackHandlerPerformance(eventType, handlerInfo);
        this.metaState.performance[eventType].failures++;

        // Learn from failures
        this.publish('system:handler_failure', {
            eventType,
            handler: handlerInfo.name,
            error: error.message,
            duration: handlerInfo.duration
        }, {
            source: 'meta-event-system',
            priority: 'high'
        });
    }

    /**
     * Run intelligence hooks
     */
    async runHooks(hookType, data) {
        const hooks = this.intelligenceHooks[hookType] || [];

        for (const hook of hooks) {
            try {
                await hook(data);
            } catch (error) {
                console.error(`Hook ${hookType} failed:`, error);
            }
        }
    }

    /**
     * Register intelligence hook
     */
    registerHook(hookType, handler) {
        if (!this.intelligenceHooks[hookType]) {
            this.intelligenceHooks[hookType] = [];
        }

        this.intelligenceHooks[hookType].push(handler);
    }

    /**
     * Get meta state
     */
    getMetaState() {
        return {
            ...this.metaState,
            correlationCount: this.correlations.size,
            activePatterns: this.eventPatterns.size
        };
    }

    /**
     * Get event correlation chain
     */
    getCorrelationChain(correlationId) {
        return this.correlations.get(correlationId) || [];
    }

    /**
     * Predict next event (placeholder for AI)
     */
    predictNextEvent(currentEvent) {
        // Simple prediction based on patterns
        const recentSequence = this.eventHistory
            .slice(-5)
            .map(e => e.type)
            .join('-');

        // Find patterns that start with this sequence
        const predictions = [];

        for (const [pattern, count] of this.eventPatterns) {
            if (pattern.startsWith(recentSequence)) {
                const next = pattern.split('-')[recentSequence.split('-').length];
                if (next) {
                    predictions.push({ event: next, confidence: count / 100 });
                }
            }
        }

        return predictions.sort((a, b) => b.confidence - a.confidence);
    }
}

// Singleton instance
let instance = null;

export function getEventSystem() {
    if (!instance) {
        instance = new MetaEventSystem();
    }
    return instance;
}

// Export for direct use
export default getEventSystem();