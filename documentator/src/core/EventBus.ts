import { EventEmitter } from 'events';

export interface EventPayload {
  source: string;
  timestamp: Date;
  data: any;
  metadata?: Record<string, any>;
}

export interface EventSubscription {
  id: string;
  event: string;
  handler: EventHandler;
  once: boolean;
  filter?: (payload: EventPayload) => boolean;
}

export type EventHandler = (payload: EventPayload) => void | Promise<void>;

export class EventBus extends EventEmitter {
  private static instance: EventBus;
  private subscriptions: Map<string, EventSubscription[]> = new Map();
  private eventHistory: EventPayload[] = [];
  private maxHistorySize: number = 1000;
  private debugMode: boolean = false;

  private constructor() {
    super();
    this.setMaxListeners(100);
  }

  static getInstance(): EventBus {
    if (!EventBus.instance) {
      EventBus.instance = new EventBus();
    }
    return EventBus.instance;
  }

  subscribe(
    event: string,
    handler: EventHandler,
    options: {
      once?: boolean;
      filter?: (payload: EventPayload) => boolean;
      priority?: number;
    } = {}
  ): string {
    const subscription: EventSubscription = {
      id: this.generateSubscriptionId(),
      event,
      handler,
      once: options.once || false,
      filter: options.filter
    };

    if (!this.subscriptions.has(event)) {
      this.subscriptions.set(event, []);
    }

    const subs = this.subscriptions.get(event)!;
    subs.push(subscription);

    if (options.priority !== undefined) {
      subs.sort((a, b) => {
        const aPriority = (a as any).priority || 0;
        const bPriority = (b as any).priority || 0;
        return bPriority - aPriority;
      });
    }

    if (this.debugMode) {
      console.log(`[EventBus] Subscribed to ${event} with ID ${subscription.id}`);
    }

    return subscription.id;
  }

  unsubscribe(subscriptionId: string): boolean {
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

  async publish(
    event: string,
    source: string,
    data: any,
    metadata?: Record<string, any>
  ): Promise<void> {
    const payload: EventPayload = {
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
    const toRemove: string[] = [];

    for (const subscription of subscriptions) {
      if (subscription.filter && !subscription.filter(payload)) {
        continue;
      }

      try {
        await subscription.handler(payload);

        if (subscription.once) {
          toRemove.push(subscription.id);
        }
      } catch (error) {
        console.error(`[EventBus] Error handling ${event}:`, error);
      }
    }

    for (const id of toRemove) {
      this.unsubscribe(id);
    }

    this.emit(event, payload);
  }

  publishSync(
    event: string,
    source: string,
    data: any,
    metadata?: Record<string, any>
  ): void {
    const payload: EventPayload = {
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
    const toRemove: string[] = [];

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
      } catch (error) {
        console.error(`[EventBus] Error handling ${event}:`, error);
      }
    }

    for (const id of toRemove) {
      this.unsubscribe(id);
    }

    this.emit(event, payload);
  }

  waitFor(
    event: string,
    timeout?: number,
    filter?: (payload: EventPayload) => boolean
  ): Promise<EventPayload> {
    return new Promise((resolve, reject) => {
      const timeoutId = timeout
        ? setTimeout(() => {
            this.unsubscribe(subscriptionId);
            reject(new Error(`Timeout waiting for event ${event}`));
          }, timeout)
        : null;

      const subscriptionId = this.subscribe(
        event,
        (payload) => {
          if (timeoutId) clearTimeout(timeoutId);
          resolve(payload);
        },
        { once: true, filter }
      );
    });
  }

  getEventHistory(event?: string, limit?: number): EventPayload[] {
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

  clearHistory(): void {
    this.eventHistory = [];
  }

  getSubscriptionCount(event?: string): number {
    if (event) {
      return this.subscriptions.get(event)?.length || 0;
    }

    let total = 0;
    for (const subs of this.subscriptions.values()) {
      total += subs.length;
    }
    return total;
  }

  getActiveEvents(): string[] {
    return Array.from(this.subscriptions.keys());
  }

  setDebugMode(enabled: boolean): void {
    this.debugMode = enabled;
  }

  setMaxHistorySize(size: number): void {
    this.maxHistorySize = size;
    if (this.eventHistory.length > size) {
      this.eventHistory = this.eventHistory.slice(-size);
    }
  }

  private generateSubscriptionId(): string {
    return `sub_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private addToHistory(event: string, payload: EventPayload): void {
    this.eventHistory.push(payload);
    (payload as any).__eventName = event;

    if (this.eventHistory.length > this.maxHistorySize) {
      this.eventHistory.shift();
    }
  }

  private getEventNameFromHistory(index: number): string | undefined {
    const payload = this.eventHistory[index];
    return payload ? (payload as any).__eventName : undefined;
  }

  reset(): void {
    this.subscriptions.clear();
    this.eventHistory = [];
    this.removeAllListeners();
  }
}