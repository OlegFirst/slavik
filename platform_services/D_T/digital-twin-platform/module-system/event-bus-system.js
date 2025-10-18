/**
 * Module Event Bus - Standalone Implementation
 * Inter-module communication system
 */

import { EventEmitter } from 'events';

export class ModuleEventBus extends EventEmitter {
    constructor() {
        super();
        this.modules = new Map();
        this.channels = new Map();
        this.messageHistory = [];
        this.maxHistorySize = 100;
    }

    /**
     * Register a module
     */
    registerModule(moduleId, moduleInstance) {
        this.modules.set(moduleId, moduleInstance);
        this.emit('module:registered', { moduleId, timestamp: Date.now() });
        return this;
    }

    /**
     * Unregister a module
     */
    unregisterModule(moduleId) {
        const removed = this.modules.delete(moduleId);
        if (removed) {
            this.emit('module:unregistered', { moduleId, timestamp: Date.now() });
        }
        return removed;
    }

    /**
     * Create a communication channel
     */
    createChannel(channelName) {
        if (!this.channels.has(channelName)) {
            this.channels.set(channelName, new Set());
            this.emit('channel:created', { channelName, timestamp: Date.now() });
        }
        return this;
    }

    /**
     * Subscribe to a channel
     */
    subscribeToChannel(channelName, moduleId) {
        if (!this.channels.has(channelName)) {
            this.createChannel(channelName);
        }
        this.channels.get(channelName).add(moduleId);
        this.emit('channel:subscribed', { channelName, moduleId, timestamp: Date.now() });
        return this;
    }

    /**
     * Publish to a channel
     */
    publishToChannel(channelName, message, senderId) {
        if (!this.channels.has(channelName)) {
            return false;
        }

        const subscribers = this.channels.get(channelName);
        const messageData = {
            channel: channelName,
            message,
            senderId,
            timestamp: Date.now()
        };

        // Add to history
        this.addToHistory(messageData);

        // Notify subscribers
        for (const moduleId of subscribers) {
            if (moduleId !== senderId) { // Don't send to self
                const module = this.modules.get(moduleId);
                if (module) {
                    this.emit(`message:${moduleId}`, messageData);
                    if (typeof module.handleMessage === 'function') {
                        module.handleMessage(messageData);
                    }
                }
            }
        }

        this.emit('channel:message', messageData);
        return true;
    }

    /**
     * Send direct message to a module
     */
    sendMessage(targetModuleId, message, senderId) {
        const module = this.modules.get(targetModuleId);
        if (!module) {
            return false;
        }

        const messageData = {
            target: targetModuleId,
            message,
            senderId,
            timestamp: Date.now()
        };

        // Add to history
        this.addToHistory(messageData);

        // Deliver message
        this.emit(`message:${targetModuleId}`, messageData);
        if (typeof module.handleMessage === 'function') {
            module.handleMessage(messageData);
        }

        return true;
    }

    /**
     * Broadcast to all modules
     */
    broadcast(message, senderId) {
        const messageData = {
            type: 'broadcast',
            message,
            senderId,
            timestamp: Date.now()
        };

        // Add to history
        this.addToHistory(messageData);

        // Send to all modules except sender
        for (const [moduleId, module] of this.modules) {
            if (moduleId !== senderId) {
                this.emit(`message:${moduleId}`, messageData);
                if (typeof module.handleMessage === 'function') {
                    module.handleMessage(messageData);
                }
            }
        }

        this.emit('broadcast', messageData);
        return true;
    }

    /**
     * Add message to history
     */
    addToHistory(messageData) {
        this.messageHistory.push(messageData);
        if (this.messageHistory.length > this.maxHistorySize) {
            this.messageHistory.shift();
        }
    }

    /**
     * Get message history
     */
    getHistory(filter = {}) {
        let history = [...this.messageHistory];

        if (filter.channel) {
            history = history.filter(m => m.channel === filter.channel);
        }
        if (filter.senderId) {
            history = history.filter(m => m.senderId === filter.senderId);
        }
        if (filter.since) {
            history = history.filter(m => m.timestamp >= filter.since);
        }

        return history;
    }

    /**
     * Get statistics
     */
    getStats() {
        return {
            modulesCount: this.modules.size,
            channelsCount: this.channels.size,
            messageHistorySize: this.messageHistory.length,
            channels: Array.from(this.channels.keys()),
            modules: Array.from(this.modules.keys())
        };
    }

    /**
     * Clear all data
     */
    clear() {
        this.modules.clear();
        this.channels.clear();
        this.messageHistory = [];
        this.emit('cleared');
    }
}

export default ModuleEventBus;