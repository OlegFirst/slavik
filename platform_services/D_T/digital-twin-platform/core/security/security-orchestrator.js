/**
 * Security Orchestrator - Standalone Implementation
 * Minimal security layer for Digital Twin Module
 */

import crypto from 'crypto';
import { EventEmitter } from 'events';

export class SecurityOrchestrator extends EventEmitter {
    constructor(config = {}) {
        super();
        this.config = {
            encryptionAlgorithm: 'aes-256-gcm',
            hashAlgorithm: 'sha256',
            saltRounds: 10,
            ...config
        };
        this.isInitialized = false;
    }

    async initialize() {
        this.isInitialized = true;
        this.emit('initialized');
        return true;
    }

    async validateRequest(request, context = {}) {
        // Basic request validation
        if (!request) {
            return { valid: false, reason: 'No request provided' };
        }

        // Check for required fields
        if (request.body && typeof request.body === 'object') {
            // Validate against XSS and injection
            const invalidPatterns = [/<script/i, /javascript:/i, /on\w+=/i];
            const jsonString = JSON.stringify(request.body);
            
            for (const pattern of invalidPatterns) {
                if (pattern.test(jsonString)) {
                    return { valid: false, reason: 'Potentially malicious content detected' };
                }
            }
        }

        return { valid: true };
    }

    async authorizeAction(action, user, resource) {
        // Simple authorization logic
        const allowedActions = ['read', 'write', 'execute', 'create', 'update', 'delete'];
        
        if (!allowedActions.includes(action)) {
            return { authorized: false, reason: 'Invalid action' };
        }

        // In standalone mode, allow all actions for demo
        return { authorized: true, permissions: allowedActions };
    }

    async encryptData(data, key = null) {
        try {
            const secretKey = key || crypto.randomBytes(32);
            const iv = crypto.randomBytes(16);
            const cipher = crypto.createCipheriv(this.config.encryptionAlgorithm, secretKey, iv);
            
            const encrypted = Buffer.concat([
                cipher.update(JSON.stringify(data), 'utf8'),
                cipher.final()
            ]);
            
            const authTag = cipher.getAuthTag();
            
            return {
                encrypted: encrypted.toString('base64'),
                iv: iv.toString('base64'),
                authTag: authTag.toString('base64'),
                key: secretKey.toString('base64')
            };
        } catch (error) {
            console.error('Encryption error:', error);
            return data; // Return original data in case of error
        }
    }

    async decryptData(encryptedData, key) {
        try {
            const secretKey = Buffer.from(key, 'base64');
            const iv = Buffer.from(encryptedData.iv, 'base64');
            const authTag = Buffer.from(encryptedData.authTag, 'base64');
            const encrypted = Buffer.from(encryptedData.encrypted, 'base64');
            
            const decipher = crypto.createDecipheriv(this.config.encryptionAlgorithm, secretKey, iv);
            decipher.setAuthTag(authTag);
            
            const decrypted = Buffer.concat([
                decipher.update(encrypted),
                decipher.final()
            ]);
            
            return JSON.parse(decrypted.toString('utf8'));
        } catch (error) {
            console.error('Decryption error:', error);
            return null;
        }
    }

    async hashData(data) {
        const hash = crypto.createHash(this.config.hashAlgorithm);
        hash.update(JSON.stringify(data));
        return hash.digest('hex');
    }

    async validateIntegrity(data, hash) {
        const computedHash = await this.hashData(data);
        return computedHash === hash;
    }

    async auditLog(action, user, resource, result) {
        const logEntry = {
            timestamp: new Date().toISOString(),
            action,
            user: user || 'system',
            resource,
            result,
            hash: await this.hashData({ action, user, resource, result })
        };
        
        console.log('[AUDIT]', JSON.stringify(logEntry));
        this.emit('audit', logEntry);
        return logEntry;
    }
}

export default SecurityOrchestrator;