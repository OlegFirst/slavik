// Security Gateway - защита на уровне клиентской инфраструктуры

class SecurityGateway {
  constructor(config) {
    this.config = config;

    // WAF (Web Application Firewall)
    this.waf = {
      enabled: config.waf?.enabled || true,
      rules: [],
      customRules: [],
      blockedIPs: new Set(),
      suspiciousPatterns: []
    };

    // DDoS Protection
    this.ddosProtection = {
      enabled: config.ddosProtection?.enabled || true,
      requestCounts: new Map(), // IP -> count
      blacklist: new Map(),      // IP -> expiry time
      maxRequestsPerMinute: config.ddosProtection?.maxRequestsPerMinute || 1000
    };

    // Rate Limiting
    this.rateLimiting = {
      enabled: config.rateLimiting?.enabled || true,
      userLimits: new Map(),    // userId -> {count, resetTime}
      ipLimits: new Map(),       // IP -> {count, resetTime}
      defaultLimit: config.rateLimiting?.defaultLimit || 100
    };

    // Encryption
    this.encryption = {
      algorithm: config.encryption?.algorithm || 'AES-256-GCM',
      keys: new Map(),           // keyId -> key
      currentKeyId: null,
      rotationInterval: config.encryption?.rotationInterval || 86400000
    };

    // Security headers
    this.securityHeaders = {
      'X-Content-Type-Options': 'nosniff',
      'X-Frame-Options': 'DENY',
      'X-XSS-Protection': '1; mode=block',
      'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
      'Content-Security-Policy': "default-src 'self'",
      'Referrer-Policy': 'strict-origin-when-cross-origin'
    };

    this.stats = {
      blockedRequests: 0,
      passedRequests: 0,
      ddosAttacksDetected: 0,
      wafTriggered: 0
    };
  }

  async initialize() {
    console.log('🛡️ Initializing Security Gateway...');

    // Load WAF rules
    await this.loadWAFRules();

    // Initialize encryption
    await this.initializeEncryption();

    // Start monitoring
    this.startMonitoring();

    console.log('✅ Security Gateway initialized');
  }

  // WAF - проверка на вредоносные паттерны
  async loadWAFRules() {
    // OWASP Core Rule Set patterns
    this.waf.suspiciousPatterns = [
      // SQL Injection
      /(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER)\b.*\b(FROM|INTO|WHERE|TABLE)\b)/gi,
      /(\b(UNION|JOIN)\b.*\b(SELECT)\b)/gi,
      /('|(--|#|\/\*|\*\/)|;|\||\\x[0-9a-f]{2})/gi,

      // XSS
      /(<script[^>]*>|<\/script>|javascript:|on\w+\s*=)/gi,
      /(document\.|window\.|alert\(|prompt\(|confirm\()/gi,

      // Path Traversal
      /(\.\.\/|\.\.\\|%2e%2e%2f|%2e%2e\/|\.\.%2f|%c0%ae%c0%ae)/gi,

      // Command Injection
      /(;|\||`|&&|\$\(|\${)/gi,

      // XXE
      /<!DOCTYPE[^>]*\[[^>]*<!ENTITY/gi,

      // LDAP Injection
      /(\*|\(|\)|\||&|=)/gi
    ];

    // Custom rules specific to BCM
    if (this.config.waf?.customRules) {
      try {
        const customRules = require(this.config.waf.customRules);
        this.waf.customRules = customRules;
      } catch (error) {
        console.warn('Failed to load custom WAF rules:', error.message);
      }
    }
  }

  // Проверка запроса через WAF
  async validate(request) {
    const validationResult = {
      passed: true,
      reason: null,
      score: 0
    };

    // 1. Check IP blacklist
    if (this.isIPBlacklisted(request.ip)) {
      this.stats.blockedRequests++;
      return {
        passed: false,
        reason: 'IP blacklisted',
        score: 100
      };
    }

    // 2. Check DDoS
    if (this.checkDDoS(request.ip)) {
      this.stats.ddosAttacksDetected++;
      this.blacklistIP(request.ip, 3600000); // 1 hour
      return {
        passed: false,
        reason: 'DDoS detected',
        score: 100
      };
    }

    // 3. WAF checks
    const wafScore = await this.performWAFCheck(request);
    if (wafScore > 50) {
      this.stats.wafTriggered++;
      return {
        passed: false,
        reason: 'WAF: Suspicious pattern detected',
        score: wafScore
      };
    }

    // 4. Check security headers
    if (request.headers) {
      const headerCheck = this.validateHeaders(request.headers);
      if (!headerCheck.valid) {
        validationResult.score += 20;
        validationResult.reason = headerCheck.reason;
      }
    }

    // 5. Content validation
    if (request.body) {
      const contentCheck = await this.validateContent(request.body);
      if (!contentCheck.valid) {
        validationResult.score += contentCheck.score;
        validationResult.reason = contentCheck.reason;
      }
    }

    // Final decision
    if (validationResult.score > 30) {
      this.stats.blockedRequests++;
      validationResult.passed = false;
    } else {
      this.stats.passedRequests++;
    }

    return validationResult;
  }

  // WAF проверка
  async performWAFCheck(request) {
    let score = 0;
    const checkString = JSON.stringify(request);

    // Check against suspicious patterns
    for (const pattern of this.waf.suspiciousPatterns) {
      if (pattern.test(checkString)) {
        score += 25;
        console.warn(`WAF: Pattern matched: ${pattern}`);
      }
    }

    // Check custom rules
    for (const rule of this.waf.customRules) {
      if (rule.check && rule.check(request)) {
        score += rule.score || 20;
        console.warn(`WAF: Custom rule triggered: ${rule.name}`);
      }
    }

    // Check payload size
    if (request.body && JSON.stringify(request.body).length > 1000000) {
      score += 15; // Large payload
    }

    return score;
  }

  // DDoS проверка
  checkDDoS(ip) {
    const now = Date.now();
    const minute = 60000;

    if (!this.ddosProtection.requestCounts.has(ip)) {
      this.ddosProtection.requestCounts.set(ip, {
        count: 1,
        firstRequest: now
      });
      return false;
    }

    const ipData = this.ddosProtection.requestCounts.get(ip);

    // Reset counter if minute passed
    if (now - ipData.firstRequest > minute) {
      ipData.count = 1;
      ipData.firstRequest = now;
      return false;
    }

    ipData.count++;

    // Check if exceeded limit
    if (ipData.count > this.ddosProtection.maxRequestsPerMinute) {
      return true; // DDoS detected
    }

    return false;
  }

  // Rate Limiting
  async checkRateLimit(userId, ip) {
    const now = Date.now();
    const window = 60000; // 1 minute window

    // Check user rate limit
    if (userId) {
      if (!this.rateLimiting.userLimits.has(userId)) {
        this.rateLimiting.userLimits.set(userId, {
          count: 1,
          resetTime: now + window
        });
      } else {
        const userLimit = this.rateLimiting.userLimits.get(userId);

        if (now > userLimit.resetTime) {
          userLimit.count = 1;
          userLimit.resetTime = now + window;
        } else {
          userLimit.count++;

          if (userLimit.count > this.rateLimiting.defaultLimit) {
            return {
              allowed: false,
              retryAfter: Math.ceil((userLimit.resetTime - now) / 1000)
            };
          }
        }
      }
    }

    // Check IP rate limit
    if (!this.rateLimiting.ipLimits.has(ip)) {
      this.rateLimiting.ipLimits.set(ip, {
        count: 1,
        resetTime: now + window
      });
    } else {
      const ipLimit = this.rateLimiting.ipLimits.get(ip);

      if (now > ipLimit.resetTime) {
        ipLimit.count = 1;
        ipLimit.resetTime = now + window;
      } else {
        ipLimit.count++;

        if (ipLimit.count > this.rateLimiting.defaultLimit * 2) {
          return {
            allowed: false,
            retryAfter: Math.ceil((ipLimit.resetTime - now) / 1000)
          };
        }
      }
    }

    return { allowed: true };
  }

  // Управление черным списком IP
  blacklistIP(ip, duration = 3600000) {
    const expiryTime = Date.now() + duration;
    this.ddosProtection.blacklist.set(ip, expiryTime);
    this.waf.blockedIPs.add(ip);

    console.warn(`🚫 IP blacklisted: ${ip} until ${new Date(expiryTime).toISOString()}`);

    // Schedule removal
    setTimeout(() => {
      this.ddosProtection.blacklist.delete(ip);
      this.waf.blockedIPs.delete(ip);
      console.log(`✅ IP removed from blacklist: ${ip}`);
    }, duration);
  }

  isIPBlacklisted(ip) {
    if (this.waf.blockedIPs.has(ip)) {
      const expiry = this.ddosProtection.blacklist.get(ip);
      if (expiry && expiry > Date.now()) {
        return true;
      }
      // Clean up expired entry
      this.waf.blockedIPs.delete(ip);
      this.ddosProtection.blacklist.delete(ip);
    }
    return false;
  }

  // Валидация заголовков
  validateHeaders(headers) {
    // Check for required security headers in response
    const missingHeaders = [];

    // Check for suspicious request headers
    if (headers['x-forwarded-for']) {
      const ips = headers['x-forwarded-for'].split(',');
      if (ips.length > 5) {
        return {
          valid: false,
          reason: 'Too many proxy hops'
        };
      }
    }

    // Check user agent
    if (!headers['user-agent'] || headers['user-agent'].includes('bot')) {
      return {
        valid: false,
        reason: 'Suspicious user agent'
      };
    }

    return { valid: true };
  }

  // Валидация контента
  async validateContent(body) {
    // Check for malicious content patterns
    const bodyString = typeof body === 'string' ? body : JSON.stringify(body);

    // Check size
    if (bodyString.length > 10000000) { // 10MB
      return {
        valid: false,
        score: 50,
        reason: 'Payload too large'
      };
    }

    // Check for binary content in JSON
    if (/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/.test(bodyString)) {
      return {
        valid: false,
        score: 30,
        reason: 'Binary content in JSON'
      };
    }

    return { valid: true, score: 0 };
  }

  // Шифрование
  async initializeEncryption() {
    const crypto = require('crypto');

    // Generate initial key
    const keyId = crypto.randomBytes(16).toString('hex');
    const key = crypto.randomBytes(32);

    this.encryption.keys.set(keyId, key);
    this.encryption.currentKeyId = keyId;

    // Schedule key rotation
    if (this.encryption.rotationInterval > 0) {
      setInterval(() => {
        this.rotateEncryptionKey();
      }, this.encryption.rotationInterval);
    }
  }

  async encrypt(data) {
    const crypto = require('crypto');
    const key = this.encryption.keys.get(this.encryption.currentKeyId);

    const iv = crypto.randomBytes(16);
    const cipher = crypto.createCipheriv(this.encryption.algorithm, key, iv);

    let encrypted = cipher.update(JSON.stringify(data), 'utf8', 'hex');
    encrypted += cipher.final('hex');

    const authTag = cipher.getAuthTag();

    return {
      keyId: this.encryption.currentKeyId,
      iv: iv.toString('hex'),
      authTag: authTag.toString('hex'),
      data: encrypted
    };
  }

  async decrypt(encryptedData) {
    const crypto = require('crypto');
    const key = this.encryption.keys.get(encryptedData.keyId);

    if (!key) {
      throw new Error('Encryption key not found');
    }

    const decipher = crypto.createDecipheriv(
      this.encryption.algorithm,
      key,
      Buffer.from(encryptedData.iv, 'hex')
    );

    decipher.setAuthTag(Buffer.from(encryptedData.authTag, 'hex'));

    let decrypted = decipher.update(encryptedData.data, 'hex', 'utf8');
    decrypted += decipher.final('utf8');

    return JSON.parse(decrypted);
  }

  rotateEncryptionKey() {
    const crypto = require('crypto');
    const newKeyId = crypto.randomBytes(16).toString('hex');
    const newKey = crypto.randomBytes(32);

    this.encryption.keys.set(newKeyId, newKey);
    this.encryption.currentKeyId = newKeyId;

    // Keep old keys for decryption of old data
    // Clean up keys older than 7 days
    const weekAgo = Date.now() - 604800000;
    for (const [keyId, key] of this.encryption.keys) {
      if (keyId < weekAgo) {
        this.encryption.keys.delete(keyId);
      }
    }

    console.log('🔑 Encryption key rotated');
  }

  // Мониторинг
  startMonitoring() {
    setInterval(() => {
      // Clean up expired rate limits
      const now = Date.now();

      for (const [userId, limit] of this.rateLimiting.userLimits) {
        if (now > limit.resetTime + 60000) {
          this.rateLimiting.userLimits.delete(userId);
        }
      }

      for (const [ip, limit] of this.rateLimiting.ipLimits) {
        if (now > limit.resetTime + 60000) {
          this.rateLimiting.ipLimits.delete(ip);
        }
      }

      // Clean up DDoS tracking
      for (const [ip, data] of this.ddosProtection.requestCounts) {
        if (now - data.firstRequest > 300000) { // 5 minutes
          this.ddosProtection.requestCounts.delete(ip);
        }
      }
    }, 60000); // Every minute
  }

  // Статистика
  getStats() {
    return {
      ...this.stats,
      activeRateLimits: this.rateLimiting.userLimits.size + this.rateLimiting.ipLimits.size,
      blacklistedIPs: this.waf.blockedIPs.size,
      ddosTracking: this.ddosProtection.requestCounts.size
    };
  }

  // Health check
  async healthCheck() {
    return {
      status: 'healthy',
      components: {
        waf: this.waf.enabled ? 'active' : 'disabled',
        ddos: this.ddosProtection.enabled ? 'active' : 'disabled',
        rateLimiting: this.rateLimiting.enabled ? 'active' : 'disabled',
        encryption: this.encryption.currentKeyId ? 'active' : 'inactive'
      },
      stats: this.getStats()
    };
  }

  async shutdown() {
    console.log('Shutting down Security Gateway...');
    // Clean up resources
    this.ddosProtection.requestCounts.clear();
    this.rateLimiting.userLimits.clear();
    this.rateLimiting.ipLimits.clear();
  }
}

module.exports = SecurityGateway;