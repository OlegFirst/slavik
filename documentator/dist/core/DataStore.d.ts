export interface DataQuery {
    collection: string;
    filter?: Record<string, any>;
    sort?: {
        field: string;
        order: 'asc' | 'desc';
    };
    limit?: number;
    offset?: number;
}
export interface DataDocument {
    _id: string;
    _collection: string;
    _createdAt: Date;
    _updatedAt: Date;
    _version: number;
    [key: string]: any;
}
export interface DataStoreConfig {
    dataPath: string;
    enableCache: boolean;
    cacheSize: number;
    autoSave: boolean;
    saveInterval: number;
}
export declare class DataStore {
    private static instance;
    private config;
    private collections;
    private cache;
    private isDirty;
    private saveTimer;
    private eventBus;
    private initialized;
    private constructor();
    static getInstance(config?: Partial<DataStoreConfig>): DataStore;
    initialize(): Promise<void>;
    shutdown(): Promise<void>;
    get(collection: string, id: string): Promise<DataDocument | null>;
    set(collection: string, id: string, data: any): Promise<DataDocument>;
    create(collection: string, data: any): Promise<DataDocument>;
    update(collection: string, id: string, updates: any): Promise<DataDocument | null>;
    delete(collection: string, id: string): Promise<boolean>;
    query(query: DataQuery): Promise<DataDocument[]>;
    count(collection: string, filter?: Record<string, any>): Promise<number>;
    exists(collection: string, id: string): Promise<boolean>;
    listCollections(): Promise<string[]>;
    dropCollection(collection: string): Promise<void>;
    clearCollection(collection: string): Promise<void>;
    backup(backupPath?: string): Promise<string>;
    restore(backupPath: string): Promise<void>;
    private getCollection;
    private loadCollection;
    private loadCollections;
    private saveCollection;
    private saveAllCollections;
    private startAutoSave;
    private matchesFilter;
    private getNestedValue;
    private addToCache;
    private generateId;
    getCacheStats(): {
        size: number;
        maxSize: number;
        hitRate: number;
    };
    getCollectionStats(collection: string): {
        documentCount: number;
        sizeInBytes: number;
        isDirty: boolean;
    } | null;
}
//# sourceMappingURL=DataStore.d.ts.map