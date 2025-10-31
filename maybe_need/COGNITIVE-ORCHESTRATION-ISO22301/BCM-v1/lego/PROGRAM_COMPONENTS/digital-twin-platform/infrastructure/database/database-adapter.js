/**
 * Database Adapter - Standalone Implementation
 * In-memory database for Digital Twin Module
 */

import { EventEmitter } from 'events';
import crypto from 'crypto';

export class DigitalTwinDatabaseAdapter extends EventEmitter {
    constructor(config = {}) {
        super();
        this.config = {
            persistToFile: false,
            fileName: 'digital-twin-data.json',
            ...config
        };
        
        // In-memory storage
        this.collections = {
            organizations: new Map(),
            twins: new Map(),
            simulations: new Map(),
            scenarios: new Map(),
            metrics: new Map(),
            insights: new Map()
        };
        
        this.isInitialized = false;
    }

    async initialize() {
        // Load data from file if persistence is enabled
        if (this.config.persistToFile) {
            await this.loadFromFile();
        }
        
        this.isInitialized = true;
        this.emit('initialized');
        return true;
    }

    /**
     * Create a new record
     */
    async create(collection, data) {
        if (!this.collections[collection]) {
            throw new Error(`Collection ${collection} does not exist`);
        }

        const id = data.id || this.generateId();
        const timestamp = new Date().toISOString();
        
        const record = {
            ...data,
            id,
            createdAt: timestamp,
            updatedAt: timestamp
        };

        this.collections[collection].set(id, record);
        this.emit('record:created', { collection, record });
        
        if (this.config.persistToFile) {
            await this.saveToFile();
        }

        return record;
    }

    /**
     * Read a record by ID
     */
    async findById(collection, id) {
        if (!this.collections[collection]) {
            throw new Error(`Collection ${collection} does not exist`);
        }

        return this.collections[collection].get(id) || null;
    }

    /**
     * Find records by query
     */
    async find(collection, query = {}) {
        if (!this.collections[collection]) {
            throw new Error(`Collection ${collection} does not exist`);
        }

        const records = Array.from(this.collections[collection].values());
        
        if (Object.keys(query).length === 0) {
            return records;
        }

        return records.filter(record => {
            return Object.entries(query).every(([key, value]) => {
                if (typeof value === 'object' && value !== null) {
                    // Handle complex queries
                    if (value.$eq !== undefined) return record[key] === value.$eq;
                    if (value.$ne !== undefined) return record[key] !== value.$ne;
                    if (value.$gt !== undefined) return record[key] > value.$gt;
                    if (value.$gte !== undefined) return record[key] >= value.$gte;
                    if (value.$lt !== undefined) return record[key] < value.$lt;
                    if (value.$lte !== undefined) return record[key] <= value.$lte;
                    if (value.$in !== undefined) return value.$in.includes(record[key]);
                    if (value.$nin !== undefined) return !value.$nin.includes(record[key]);
                    if (value.$contains !== undefined) {
                        return String(record[key]).includes(value.$contains);
                    }
                }
                return record[key] === value;
            });
        });
    }

    /**
     * Update a record
     */
    async update(collection, id, updates) {
        if (!this.collections[collection]) {
            throw new Error(`Collection ${collection} does not exist`);
        }

        const record = this.collections[collection].get(id);
        if (!record) {
            throw new Error(`Record with id ${id} not found in ${collection}`);
        }

        const updatedRecord = {
            ...record,
            ...updates,
            id: record.id, // Preserve ID
            createdAt: record.createdAt, // Preserve creation time
            updatedAt: new Date().toISOString()
        };

        this.collections[collection].set(id, updatedRecord);
        this.emit('record:updated', { collection, record: updatedRecord });
        
        if (this.config.persistToFile) {
            await this.saveToFile();
        }

        return updatedRecord;
    }

    /**
     * Delete a record
     */
    async delete(collection, id) {
        if (!this.collections[collection]) {
            throw new Error(`Collection ${collection} does not exist`);
        }

        const deleted = this.collections[collection].delete(id);
        
        if (deleted) {
            this.emit('record:deleted', { collection, id });
            
            if (this.config.persistToFile) {
                await this.saveToFile();
            }
        }

        return deleted;
    }

    /**
     * Count records in collection
     */
    async count(collection, query = {}) {
        const records = await this.find(collection, query);
        return records.length;
    }

    /**
     * Aggregate operations
     */
    async aggregate(collection, pipeline) {
        const records = await this.find(collection);
        let result = records;

        for (const stage of pipeline) {
            const [operation, params] = Object.entries(stage)[0];

            switch (operation) {
                case '$match':
                    result = result.filter(record => {
                        return Object.entries(params).every(([key, value]) => {
                            return record[key] === value;
                        });
                    });
                    break;

                case '$group':
                    const groups = new Map();
                    for (const record of result) {
                        const key = record[params._id];
                        if (!groups.has(key)) {
                            groups.set(key, []);
                        }
                        groups.get(key).push(record);
                    }
                    result = Array.from(groups.entries()).map(([key, records]) => ({
                        _id: key,
                        count: records.length,
                        records
                    }));
                    break;

                case '$sort':
                    const [field, order] = Object.entries(params)[0];
                    result.sort((a, b) => {
                        if (order === 1) return a[field] > b[field] ? 1 : -1;
                        return a[field] < b[field] ? 1 : -1;
                    });
                    break;

                case '$limit':
                    result = result.slice(0, params);
                    break;

                case '$skip':
                    result = result.slice(params);
                    break;
            }
        }

        return result;
    }

    /**
     * Generate unique ID
     */
    generateId() {
        return crypto.randomBytes(16).toString('hex');
    }

    /**
     * Clear a collection
     */
    async clearCollection(collection) {
        if (!this.collections[collection]) {
            throw new Error(`Collection ${collection} does not exist`);
        }

        this.collections[collection].clear();
        this.emit('collection:cleared', { collection });
        
        if (this.config.persistToFile) {
            await this.saveToFile();
        }
    }

    /**
     * Get collection statistics
     */
    getStats(collection) {
        if (collection) {
            return {
                collection,
                count: this.collections[collection]?.size || 0
            };
        }

        return Object.entries(this.collections).map(([name, coll]) => ({
            collection: name,
            count: coll.size
        }));
    }

    /**
     * Save data to file (for persistence)
     */
    async saveToFile() {
        if (!this.config.persistToFile) return;

        const data = {};
        for (const [name, collection] of Object.entries(this.collections)) {
            data[name] = Array.from(collection.entries());
        }

        const fs = await import('fs').then(m => m.promises);
        await fs.writeFile(
            this.config.fileName,
            JSON.stringify(data, null, 2),
            'utf8'
        );
    }

    /**
     * Load data from file
     */
    async loadFromFile() {
        if (!this.config.persistToFile) return;

        try {
            const fs = await import('fs').then(m => m.promises);
            const data = await fs.readFile(this.config.fileName, 'utf8');
            const parsed = JSON.parse(data);

            for (const [name, entries] of Object.entries(parsed)) {
                if (this.collections[name]) {
                    this.collections[name] = new Map(entries);
                }
            }
        } catch (error) {
            // File doesn't exist or is invalid, start fresh
            console.log('No existing data file found, starting with empty database');
        }
    }
}

export { DigitalTwinDatabaseAdapter as DigitalTwinSupabaseAdapter };
export default DigitalTwinDatabaseAdapter;