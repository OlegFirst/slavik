"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.DataStore = void 0;
const fs = __importStar(require("fs-extra"));
const path = __importStar(require("path"));
const EventBus_1 = require("./EventBus");
class DataStore {
    constructor(config) {
        this.collections = new Map();
        this.cache = new Map();
        this.isDirty = new Set();
        this.saveTimer = null;
        this.initialized = false;
        this.config = {
            dataPath: './data/store',
            enableCache: true,
            cacheSize: 1000,
            autoSave: true,
            saveInterval: 30000,
            ...config
        };
        this.eventBus = EventBus_1.EventBus.getInstance();
    }
    static getInstance(config) {
        if (!DataStore.instance) {
            DataStore.instance = new DataStore(config);
        }
        return DataStore.instance;
    }
    async initialize() {
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
    async shutdown() {
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
    async get(collection, id) {
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
    async set(collection, id, data) {
        const coll = await this.getCollection(collection);
        const existingDoc = coll.get(id);
        const doc = {
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
    async create(collection, data) {
        const id = this.generateId();
        return this.set(collection, id, data);
    }
    async update(collection, id, updates) {
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
    async delete(collection, id) {
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
    async query(query) {
        const coll = await this.getCollection(query.collection);
        let results = Array.from(coll.values());
        if (query.filter) {
            results = results.filter(doc => this.matchesFilter(doc, query.filter));
        }
        if (query.sort) {
            results.sort((a, b) => {
                const aVal = this.getNestedValue(a, query.sort.field);
                const bVal = this.getNestedValue(b, query.sort.field);
                if (aVal < bVal)
                    return query.sort.order === 'asc' ? -1 : 1;
                if (aVal > bVal)
                    return query.sort.order === 'asc' ? 1 : -1;
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
    async count(collection, filter) {
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
    async exists(collection, id) {
        const coll = await this.getCollection(collection);
        return coll.has(id);
    }
    async listCollections() {
        return Array.from(this.collections.keys());
    }
    async dropCollection(collection) {
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
    async clearCollection(collection) {
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
    async backup(backupPath) {
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
    async restore(backupPath) {
        if (!await fs.pathExists(backupPath)) {
            throw new Error(`Backup не знайдено: ${backupPath}`);
        }
        const files = await fs.readdir(backupPath);
        const jsonFiles = files.filter(f => f.endsWith('.json'));
        for (const file of jsonFiles) {
            const collectionName = path.basename(file, '.json');
            const data = await fs.readJson(path.join(backupPath, file));
            const collection = new Map();
            for (const doc of data) {
                collection.set(doc._id, doc);
            }
            this.collections.set(collectionName, collection);
            this.isDirty.add(collectionName);
        }
        await this.saveAllCollections();
        console.log(`[DataStore] Відновлено з: ${backupPath}`);
    }
    async getCollection(name) {
        if (!this.collections.has(name)) {
            await this.loadCollection(name);
        }
        return this.collections.get(name);
    }
    async loadCollection(name) {
        const collectionPath = path.join(this.config.dataPath, `${name}.json`);
        const collection = new Map();
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
            }
            catch (error) {
                console.error(`[DataStore] Помилка завантаження колекції ${name}:`, error);
            }
        }
        this.collections.set(name, collection);
    }
    async loadCollections() {
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
    async saveCollection(name) {
        const collection = this.collections.get(name);
        if (!collection) {
            return;
        }
        const collectionPath = path.join(this.config.dataPath, `${name}.json`);
        const data = Array.from(collection.values());
        await fs.writeJson(collectionPath, data, { spaces: 2 });
        this.isDirty.delete(name);
    }
    async saveAllCollections() {
        for (const name of this.isDirty) {
            await this.saveCollection(name);
        }
    }
    startAutoSave() {
        this.saveTimer = setInterval(async () => {
            if (this.isDirty.size > 0) {
                await this.saveAllCollections();
                console.log(`[DataStore] Автозбереження: ${this.isDirty.size} колекцій`);
            }
        }, this.config.saveInterval);
    }
    matchesFilter(doc, filter) {
        for (const [key, value] of Object.entries(filter)) {
            const docValue = this.getNestedValue(doc, key);
            if (value && typeof value === 'object' && !Array.isArray(value) && !value._bsontype) {
                if (value.$eq !== undefined && docValue !== value.$eq)
                    return false;
                if (value.$ne !== undefined && docValue === value.$ne)
                    return false;
                if (value.$gt !== undefined && docValue <= value.$gt)
                    return false;
                if (value.$gte !== undefined && docValue < value.$gte)
                    return false;
                if (value.$lt !== undefined && docValue >= value.$lt)
                    return false;
                if (value.$lte !== undefined && docValue > value.$lte)
                    return false;
                if (value.$in !== undefined && !value.$in.includes(docValue))
                    return false;
                if (value.$nin !== undefined && value.$nin.includes(docValue))
                    return false;
                if (value.$exists !== undefined) {
                    const exists = docValue !== undefined;
                    if (value.$exists !== exists)
                        return false;
                }
                if (value.$regex !== undefined) {
                    const regex = new RegExp(value.$regex, value.$options);
                    if (!regex.test(docValue))
                        return false;
                }
            }
            else {
                if (docValue !== value)
                    return false;
            }
        }
        return true;
    }
    getNestedValue(obj, path) {
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
    addToCache(key, value) {
        this.cache.set(key, value);
        if (this.cache.size > this.config.cacheSize) {
            const firstKey = this.cache.keys().next().value;
            if (firstKey) {
                this.cache.delete(firstKey);
            }
        }
    }
    generateId() {
        return `${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }
    getCacheStats() {
        return {
            size: this.cache.size,
            maxSize: this.config.cacheSize,
            hitRate: 0
        };
    }
    getCollectionStats(collection) {
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
exports.DataStore = DataStore;
//# sourceMappingURL=DataStore.js.map