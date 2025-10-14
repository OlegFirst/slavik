/**
 * Context Bus - Standalone Implementation
 * Event-driven communication system for Digital Twin Module
 */

import { EventEmitter } from 'events';

export class ContextBus extends EventEmitter {
    constructor() {
        super();
        this.contexts = new Map();
        this.subscribers = new Map();
        this.messageQueue = [];
        this.isProcessing = false;
    }

    /**
     * Register a context
     */
    registerContext(name, context) {
        this.contexts.set(name, context);
        this.emit('context:registered', { name, context });
        return this;
    }

    /**
     * Get a registered context
     */
    getContext(name) {
        return this.contexts.get(name);
    }

    /**
     * Update context data
     */
    updateContext(name, updates) {
        const context = this.contexts.get(name);
        if (context) {
            Object.assign(context, updates);
            this.emit('context:updated', { name, updates });
        }
        return context;
    }

    /**
     * Subscribe to context changes
     */
    subscribe(contextName, callback) {
        if (!this.subscribers.has(contextName)) {
            this.subscribers.set(contextName, new Set());
        }
        this.subscribers.get(contextName).add(callback);
        
        return () => {
            const subs = this.subscribers.get(contextName);
            if (subs) {
                subs.delete(callback);
            }
        };
    }

    /**
     * Broadcast message to all contexts
     */
    async broadcast(event, data) {
        this.messageQueue.push({ event, data, timestamp: Date.now() });
        
        if (!this.isProcessing) {
            await this.processQueue();
        }
    }

    /**
     * Process message queue
     */
    async processQueue() {
        if (this.messageQueue.length === 0) {
            this.isProcessing = false;
            return;
        }

        this.isProcessing = true;
        
        while (this.messageQueue.length > 0) {
            const message = this.messageQueue.shift();
            
            // Emit to all listeners
            this.emit(message.event, message.data);
            
            // Notify specific subscribers
            const contextSubs = this.subscribers.get(message.event);
            if (contextSubs) {
                for (const callback of contextSubs) {
                    try {
                        await callback(message.data);
                    } catch (error) {
                        console.error('Error in context subscriber:', error);
                    }
                }
            }
        }
        
        this.isProcessing = false;
    }

    /**
     * Get all registered contexts
     */
    getAllContexts() {
        return Object.fromEntries(this.contexts);
    }

    /**
     * Clear all contexts
     */
    clearContexts() {
        this.contexts.clear();
        this.subscribers.clear();
        this.messageQueue = [];
        this.emit('contexts:cleared');
    }

    /**
     * Get context statistics
     */
    getStats() {
        return {
            contextsCount: this.contexts.size,
            subscribersCount: this.subscribers.size,
            queueLength: this.messageQueue.length,
            isProcessing: this.isProcessing
        };
    }
}

export default ContextBus;