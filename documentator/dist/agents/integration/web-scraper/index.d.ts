import { BaseAgent } from '../../../core/BaseAgent';
import { ScheduleConfig, AgentConfig } from '../../../types/AgentInterface';
export interface ScrapingSession {
    id: string;
    targets: string[];
    startTime: Date;
    status: 'running' | 'paused' | 'completed' | 'failed';
    progress: number;
    results: any[];
}
export interface SmartScrapingConfig {
    enableML: boolean;
    autoOptimize: boolean;
    detectChanges: boolean;
    adaptiveRateLimiting: boolean;
    contentDeduplication: boolean;
    qualityFiltering: boolean;
}
export interface ScrapingTarget {
    name: string;
    url: string;
    selectors: {
        [key: string]: string | SelectorConfig;
    };
    pagination?: {
        nextSelector: string;
        maxPages?: number;
    };
    headers?: Record<string, string>;
    waitTime?: number;
}
export interface SelectorConfig {
    selector: string;
    attribute?: string;
    multiple?: boolean;
    transform?: 'text' | 'html' | 'number' | 'date' | 'url';
}
export interface WebScraperConfig extends AgentConfig {
    targets: ScrapingTarget[];
    outputPath: string;
    scheduleIntervalMinutes: number;
    userAgent?: string;
    concurrent?: boolean;
    maxConcurrent?: number;
    smartScraping?: SmartScrapingConfig;
    proxyRotation?: {
        enabled: boolean;
        proxies: string[];
    };
    retryConfig?: {
        maxRetries: number;
        backoffMultiplier: number;
        timeoutMs: number;
    };
}
export declare class WebScraperAgent extends BaseAgent {
    private config;
    private isProcessing;
    private scrapingSessions;
    private contentHashes;
    private rateLimiter;
    private failedUrls;
    metadata: {
        name: string;
        version: string;
        description: string;
        category: string;
    };
    constructor(config: AgentConfig);
    getScheduleConfig(): ScheduleConfig;
    protected onInitialize(): Promise<void>;
    protected onShutdown(): Promise<void>;
    executeAutonomously(): Promise<void>;
    private scrapeTarget;
    private fetchPage;
    private extractData;
    private extractValue;
    private resolveUrl;
    private chunkArray;
    private saveConfiguration;
    private detectContentChanges;
    private generateContentHash;
    private adaptiveRateLimit;
    private shouldSkipUrl;
    private markUrlAsFailed;
    private fetchPageWithRetry;
    private isQualityContent;
    private deduplicateResults;
    createScrapingSession(targets: string[]): Promise<string>;
    getScrapingSession(sessionId: string): Promise<ScrapingSession | null>;
    private optimizeSelectors;
    private suggestAlternativeSelectors;
    private generateScrapingInsights;
    getTools(): any[];
    handleToolCall(toolName: string, args: any): Promise<any>;
}
//# sourceMappingURL=index.d.ts.map