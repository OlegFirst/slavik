"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.EventBus = void 0;
const events_1 = require("events");
class EventBus extends events_1.EventEmitter {
    constructor() {
        super();
        this.subscriptions = new Map();
        this.eventHistory = [];
        this.maxHistorySize = 1000;
        this.debugMode = false;
        this.setMaxListeners(100);
    }
    static getInstance() {
        if (!EventBus.instance) {
            EventBus.instance = new EventBus();
        }
        return EventBus.instance;
    }
    subscribe(event, handler, options = {}) {
        const subscription = {
            id: this.generateSubscriptionId(),
            event,
            handler,
            once: options.once || false,
            filter: options.filter
        };
        if (!this.subscriptions.has(event)) {
            this.subscriptions.set(event, []);
        }
        const subs = this.subscriptions.get(event);
        subs.push(subscription);
        if (options.priority !== undefined) {
            subs.sort((a, b) => {
                const aPriority = a.priority || 0;
                const bPriority = b.priority || 0;
                return bPriority - aPriority;
            });
        }
        if (this.debugMode) {
            console.log(`[EventBus] Subscribed to ${event} with ID ${subscription.id}`);
        }
        return subscription.id;
    }
    unsubscribe(subscriptionId) {
        for (const [event, subs] of this.subscriptions.entries()) {
            const index = subs.findIndex(sub => sub.id === subscriptionId);
            if (index !== -1) {
                subs.splice(index, 1);
                if (subs.length === 0) {
                    this.subscriptions.delete(event);
                }
                if (this.debugMode) {
                    console.log(`[EventBus] Unsubscribed ${subscriptionId} from ${event}`);
                }
                return true;
            }
        }
        return false;
    }
    async publish(event, source, data, metadata) {
        const payload = {
            source,
            timestamp: new Date(),
            data,
            metadata
        };
        this.addToHistory(event, payload);
        if (this.debugMode) {
            console.log(`[EventBus] Publishing ${event} from ${source}`);
        }
        const subscriptions = this.subscriptions.get(event) || [];
        const toRemove = [];
        for (const subscription of subscriptions) {
            if (subscription.filter && !subscription.filter(payload)) {
                continue;
            }
            try {
                await subscription.handler(payload);
                if (subscription.once) {
                    toRemove.push(subscription.id);
                }
            }
            catch (error) {
                console.error(`[EventBus] Error handling ${event}:`, error);
            }
        }
        for (const id of toRemove) {
            this.unsubscribe(id);
        }
        this.emit(event, payload);
    }
    publishSync(event, source, data, metadata) {
        const payload = {
            source,
            timestamp: new Date(),
            data,
            metadata
        };
        this.addToHistory(event, payload);
        if (this.debugMode) {
            console.log(`[EventBus] Publishing ${event} from ${source} (sync)`);
        }
        const subscriptions = this.subscriptions.get(event) || [];
        const toRemove = [];
        for (const subscription of subscriptions) {
            if (subscription.filter && !subscription.filter(payload)) {
                continue;
            }
            try {
                const result = subscription.handler(payload);
                if (result instanceof Promise) {
                    result.catch(error => {
                        console.error(`[EventBus] Async error handling ${event}:`, error);
                    });
                }
                if (subscription.once) {
                    toRemove.push(subscription.id);
                }
            }
            catch (error) {
                console.error(`[EventBus] Error handling ${event}:`, error);
            }
        }
        for (const id of toRemove) {
            this.unsubscribe(id);
        }
        this.emit(event, payload);
    }
    waitFor(event, timeout, filter) {
        return new Promise((resolve, reject) => {
            const timeoutId = timeout
                ? setTimeout(() => {
                    this.unsubscribe(subscriptionId);
                    reject(new Error(`Timeout waiting for event ${event}`));
                }, timeout)
                : null;
            const subscriptionId = this.subscribe(event, (payload) => {
                if (timeoutId)
                    clearTimeout(timeoutId);
                resolve(payload);
            }, { once: true, filter });
        });
    }
    getEventHistory(event, limit) {
        let history = this.eventHistory;
        if (event) {
            history = history.filter((_, index) => {
                const eventName = this.getEventNameFromHistory(index);
                return eventName === event;
            });
        }
        if (limit) {
            history = history.slice(-limit);
        }
        return history;
    }
    clearHistory() {
        this.eventHistory = [];
    }
    getSubscriptionCount(event) {
        if (event) {
            return this.subscriptions.get(event)?.length || 0;
        }
        let total = 0;
        for (const subs of this.subscriptions.values()) {
            total += subs.length;
        }
        return total;
    }
    getActiveEvents() {
        return Array.from(this.subscriptions.keys());
    }
    setDebugMode(enabled) {
        this.debugMode = enabled;
    }
    setMaxHistorySize(size) {
        this.maxHistorySize = size;
        if (this.eventHistory.length > size) {
            this.eventHistory = this.eventHistory.slice(-size);
        }
    }
    generateSubscriptionId() {
        return `sub_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }
    addToHistory(event, payload) {
        this.eventHistory.push(payload);
        payload.__eventName = event;
        if (this.eventHistory.length > this.maxHistorySize) {
            this.eventHistory.shift();
        }
    }
    getEventNameFromHistory(index) {
        const payload = this.eventHistory[index];
        return payload ? payload.__eventName : undefined;
    }
    reset() {
        this.subscriptions.clear();
        this.eventHistory = [];
        this.removeAllListeners();
    }
}
exports.EventBus = EventBus;
//# sourceMappingURL=EventBus.js.map