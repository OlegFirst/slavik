import * as fs from 'fs-extra';
import * as path from 'path';
import { EventBus } from './EventBus';

export interface DataQuery {
  collection: string;
  filter?: Record<string, any>;
  sort?: { field: string; order: 'asc' | 'desc' };
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

export class DataStore {
  private static instance: DataStore;
  private config: DataStoreConfig;
  private collections: Map<string, Map<string, DataDocument>> = new Map();
  private cache: Map<string, any> = new Map();
  private isDirty: Set<string> = new Set();
  private saveTimer: NodeJS.Timeout | null = null;
  private eventBus: EventBus;
  private initialized: boolean = false;

  private constructor(config?: Partial<DataStoreConfig>) {
    this.config = {
      dataPath: './data/store',
      enableCache: true,
      cacheSize: 1000,
      autoSave: true,
      saveInterval: 30000,
      ...config
    };
    this.eventBus = EventBus.getInstance();
  }

  static getInstance(config?: Partial<DataStoreConfig>): DataStore {
    if (!DataStore.instance) {
      DataStore.instance = new DataStore(config);
    }
    return DataStore.instance;
  }

  async initialize(): Promise<void> {
    if (this.initialized) {
      return;
    }

    await fs.ensureDir(this.config.dataPath);
    await this.loadCollections();

    if (this.config.autoSave) {
      this.startAutoSave();
    }

    this.initialized = true;
    console.log(`[DataStore] Ініціалізовано з шляхом: ${this.config.dataPath}`);
  }

  async shutdown(): Promise<void> {
    if (!this.initialized) {
      return;
    }

    if (this.saveTimer) {
      clearInterval(this.saveTimer);
      this.saveTimer = null;
    }

    await this.saveAllCollections();
    this.collections.clear();
    this.cache.clear();
    this.isDirty.clear();

    this.initialized = false;
    console.log('[DataStore] Зупинено');
  }

  async get(collection: string, id: string): Promise<DataDocument | null> {
    const cacheKey = `${collection}:${id}`;

    if (this.config.enableCache && this.cache.has(cacheKey)) {
      return this.cache.get(cacheKey);
    }

    const coll = await this.getCollection(collection);
    const doc = coll.get(id) || null;

    if (doc && this.config.enableCache) {
      this.addToCache(cacheKey, doc);
    }

    return doc;
  }

  async set(collection: string, id: string, data: any): Promise<DataDocument> {
    const coll = await this.getCollection(collection);
    const existingDoc = coll.get(id);

    const doc: DataDocument = {
      ...data,
      _id: id,
      _collection: collection,
      _createdAt: existingDoc?._createdAt || new Date(),
      _updatedAt: new Date(),
      _version: (existingDoc?._version || 0) + 1
    };

    coll.set(id, doc);
    this.isDirty.add(collection);

    const cacheKey = `${collection}:${id}`;
    if (this.config.enableCache) {
      this.addToCache(cacheKey, doc);
    }

    this.eventBus.publishSync('datastore.document.updated', 'DataStore', {
      collection,
      id,
      document: doc,
      isNew: !existingDoc
    });

    if (!this.config.autoSave) {
      await this.saveCollection(collection);
    }

    return doc;
  }

  async create(collection: string, data: any): Promise<DataDocument> {
    const id = this.generateId();
    return this.set(collection, id, data);
  }

  async update(collection: string, id: string, updates: any): Promise<DataDocument | null> {
    const doc = await this.get(collection, id);
    if (!doc) {
      return null;
    }

    const updatedData = { ...doc, ...updates };
    delete updatedData._id;
    delete updatedData._collection;
    delete updatedData._createdAt;
    delete updatedData._updatedAt;
    delete updatedData._version;

    return this.set(collection, id, updatedData);
  }

  async delete(collection: string, id: string): Promise<boolean> {
    const coll = await this.getCollection(collection);
    const exists = coll.has(id);

    if (exists) {
      coll.delete(id);
      this.isDirty.add(collection);

      const cacheKey = `${collection}:${id}`;
      this.cache.delete(cacheKey);

      this.eventBus.publishSync('datastore.document.deleted', 'DataStore', {
        collection,
        id
      });

      if (!this.config.autoSave) {
        await this.saveCollection(collection);
      }
    }

    return exists;
  }

  async query(query: DataQuery): Promise<DataDocument[]> {
    const coll = await this.getCollection(query.collection);
    let results = Array.from(coll.values());

    if (query.filter) {
      results = results.filter(doc => this.matchesFilter(doc, query.filter!));
    }

    if (query.sort) {
      results.sort((a, b) => {
        const aVal = this.getNestedValue(a, query.sort!.field);
        const bVal = this.getNestedValue(b, query.sort!.field);

        if (aVal < bVal) return query.sort!.order === 'asc' ? -1 : 1;
        if (aVal > bVal) return query.sort!.order === 'asc' ? 1 : -1;
        return 0;
      });
    }

    if (query.offset) {
      results = results.slice(query.offset);
    }

    if (query.limit) {
      results = results.slice(0, query.limit);
    }

    return results;
  }

  async count(collection: string, filter?: Record<string, any>): Promise<number> {
    const coll = await this.getCollection(collection);

    if (!filter) {
      return coll.size;
    }

    let count = 0;
    for (const doc of coll.values()) {
      if (this.matchesFilter(doc, filter)) {
        count++;
      }
    }

    return count;
  }

  async exists(collection: string, id: string): Promise<boolean> {
    const coll = await this.getCollection(collection);
    return coll.has(id);
  }

  async listCollections(): Promise<string[]> {
    return Array.from(this.collections.keys());
  }

  async dropCollection(collection: string): Promise<void> {
    this.collections.delete(collection);
    this.isDirty.delete(collection);

    const collectionPath = path.join(this.config.dataPath, `${collection}.json`);
    if (await fs.pathExists(collectionPath)) {
      await fs.remove(collectionPath);
    }

    for (const [key] of this.cache) {
      if (key.startsWith(`${collection}:`)) {
        this.cache.delete(key);
      }
    }

    this.eventBus.publishSync('datastore.collection.dropped', 'DataStore', {
      collection
    });
  }

  async clearCollection(collection: string): Promise<void> {
    const coll = await this.getCollection(collection);
    coll.clear();
    this.isDirty.add(collection);

    for (const [key] of this.cache) {
      if (key.startsWith(`${collection}:`)) {
        this.cache.delete(key);
      }
    }

    if (!this.config.autoSave) {
      await this.saveCollection(collection);
    }

    this.eventBus.publishSync('datastore.collection.cleared', 'DataStore', {
      collection
    });
  }

  async backup(backupPath?: string): Promise<string> {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const backupDir = backupPath || path.join(this.config.dataPath, 'backups', timestamp);

    await fs.ensureDir(backupDir);
    await this.saveAllCollections();

    for (const [name, collection] of this.collections) {
      const data = Array.from(collection.values());
      const backupFile = path.join(backupDir, `${name}.json`);
      await fs.writeJson(backupFile, data, { spaces: 2 });
    }

    console.log(`[DataStore] Backup створено: ${backupDir}`);
    return backupDir;
  }

  async restore(backupPath: string): Promise<void> {
    if (!await fs.pathExists(backupPath)) {
      throw new Error(`Backup не знайдено: ${backupPath}`);
    }

    const files = await fs.readdir(backupPath);
    const jsonFiles = files.filter(f => f.endsWith('.json'));

    for (const file of jsonFiles) {
      const collectionName = path.basename(file, '.json');
      const data = await fs.readJson(path.join(backupPath, file));

      const collection = new Map<string, DataDocument>();
      for (const doc of data) {
        collection.set(doc._id, doc);
      }

      this.collections.set(collectionName, collection);
      this.isDirty.add(collectionName);
    }

    await this.saveAllCollections();
    console.log(`[DataStore] Відновлено з: ${backupPath}`);
  }

  private async getCollection(name: string): Promise<Map<string, DataDocument>> {
    if (!this.collections.has(name)) {
      await this.loadCollection(name);
    }
    return this.collections.get(name)!;
  }

  private async loadCollection(name: string): Promise<void> {
    const collectionPath = path.join(this.config.dataPath, `${name}.json`);
    const collection = new Map<string, DataDocument>();

    if (await fs.pathExists(collectionPath)) {
      try {
        const data = await fs.readJson(collectionPath);
        if (Array.isArray(data)) {
          for (const doc of data) {
            collection.set(doc._id, {
              ...doc,
              _createdAt: new Date(doc._createdAt),
              _updatedAt: new Date(doc._updatedAt)
            });
          }
        }
      } catch (error) {
        console.error(`[DataStore] Помилка завантаження колекції ${name}:`, error);
      }
    }

    this.collections.set(name, collection);
  }

  private async loadCollections(): Promise<void> {
    if (!await fs.pathExists(this.config.dataPath)) {
      return;
    }

    const files = await fs.readdir(this.config.dataPath);
    const jsonFiles = files.filter(f => f.endsWith('.json'));

    for (const file of jsonFiles) {
      const collectionName = path.basename(file, '.json');
      await this.loadCollection(collectionName);
    }
  }

  private async saveCollection(name: string): Promise<void> {
    const collection = this.collections.get(name);
    if (!collection) {
      return;
    }

    const collectionPath = path.join(this.config.dataPath, `${name}.json`);
    const data = Array.from(collection.values());

    await fs.writeJson(collectionPath, data, { spaces: 2 });
    this.isDirty.delete(name);
  }

  private async saveAllCollections(): Promise<void> {
    for (const name of this.isDirty) {
      await this.saveCollection(name);
    }
  }

  private startAutoSave(): void {
    this.saveTimer = setInterval(async () => {
      if (this.isDirty.size > 0) {
        await this.saveAllCollections();
        console.log(`[DataStore] Автозбереження: ${this.isDirty.size} колекцій`);
      }
    }, this.config.saveInterval);
  }

  private matchesFilter(doc: any, filter: Record<string, any>): boolean {
    for (const [key, value] of Object.entries(filter)) {
      const docValue = this.getNestedValue(doc, key);

      if (value && typeof value === 'object' && !Array.isArray(value) && !value._bsontype) {
        if (value.$eq !== undefined && docValue !== value.$eq) return false;
        if (value.$ne !== undefined && docValue === value.$ne) return false;
        if (value.$gt !== undefined && docValue <= value.$gt) return false;
        if (value.$gte !== undefined && docValue < value.$gte) return false;
        if (value.$lt !== undefined && docValue >= value.$lt) return false;
        if (value.$lte !== undefined && docValue > value.$lte) return false;
        if (value.$in !== undefined && !value.$in.includes(docValue)) return false;
        if (value.$nin !== undefined && value.$nin.includes(docValue)) return false;
        if (value.$exists !== undefined) {
          const exists = docValue !== undefined;
          if (value.$exists !== exists) return false;
        }
        if (value.$regex !== undefined) {
          const regex = new RegExp(value.$regex, value.$options);
          if (!regex.test(docValue)) return false;
        }
      } else {
        if (docValue !== value) return false;
      }
    }

    return true;
  }

  private getNestedValue(obj: any, path: string): any {
    const keys = path.split('.');
    let value = obj;

    for (const key of keys) {
      if (value === null || value === undefined) {
        return undefined;
      }
      value = value[key];
    }

    return value;
  }

  private addToCache(key: string, value: any): void {
    this.cache.set(key, value);

    if (this.cache.size > this.config.cacheSize) {
      const firstKey = this.cache.keys().next().value;
      if (firstKey) {
        this.cache.delete(firstKey);
      }
    }
  }

  private generateId(): string {
    return `${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  getCacheStats(): {
    size: number;
    maxSize: number;
    hitRate: number;
  } {
    return {
      size: this.cache.size,
      maxSize: this.config.cacheSize,
      hitRate: 0
    };
  }

  getCollectionStats(collection: string): {
    documentCount: number;
    sizeInBytes: number;
    isDirty: boolean;
  } | null {
    const coll = this.collections.get(collection);
    if (!coll) {
      return null;
    }

    const data = Array.from(coll.values());
    const sizeInBytes = JSON.stringify(data).length;

    return {
      documentCount: coll.size,
      sizeInBytes,
      isDirty: this.isDirty.has(collection)
    };
  }
}