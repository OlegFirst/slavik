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
export declare class EventBus extends EventEmitter {
    private static instance;
    private subscriptions;
    private eventHistory;
    private maxHistorySize;
    private debugMode;
    private constructor();
    static getInstance(): EventBus;
    subscribe(event: string, handler: EventHandler, options?: {
        once?: boolean;
        filter?: (payload: EventPayload) => boolean;
        priority?: number;
    }): string;
    unsubscribe(subscriptionId: string): boolean;
    publish(event: string, source: string, data: any, metadata?: Record<string, any>): Promise<void>;
    publishSync(event: string, source: string, data: any, metadata?: Record<string, any>): void;
    waitFor(event: string, timeout?: number, filter?: (payload: EventPayload) => boolean): Promise<EventPayload>;
    getEventHistory(event?: string, limit?: number): EventPayload[];
    clearHistory(): void;
    getSubscriptionCount(event?: string): number;
    getActiveEvents(): string[];
    setDebugMode(enabled: boolean): void;
    setMaxHistorySize(size: number): void;
    private generateSubscriptionId;
    private addToHistory;
    private getEventNameFromHistory;
    reset(): void;
}
//# sourceMappingURL=EventBus.d.ts.map