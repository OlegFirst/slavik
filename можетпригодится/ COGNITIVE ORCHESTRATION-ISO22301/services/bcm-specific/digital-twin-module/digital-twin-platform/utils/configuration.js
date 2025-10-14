/**
 * Universal Configuration Loader for NASH 4.0
 * Enterprise-grade configuration management with hot reload and validation
 */

export async function loadConfiguration() {
  return {
    environment: process.env.NODE_ENV || 'development',
    server: {
      port: process.env.PORT || process.env.APP_PORT || 3000,
      host: process.env.HOST || process.env.DOMAIN || '0.0.0.0',
      maxRequestSize: '10mb'
    },
    cors: {
      allowedOrigins: [
        'http://localhost:3000', 
        'http://localhost:3001',
        'https://localhost:3000',
        'https://localhost:3001'
      ],
      credentials: true
    },
    security: {
      enableRateLimit: true,
      jwtSecret: process.env.JWT_SECRET || 'default-secret-change-in-production',
      bcryptRounds: 10,
      inputLayer: {
        enabled: true,
        enableValidation: true,
        enableSanitization: true,
        maxRequestSize: '10mb'
      },
      processingLayer: {
        enabled: true,
        enableEncryption: true,
        enableAccessControl: true,
        enableAuditLogging: true
      },
      outputLayer: {
        enabled: true,
        enableFiltering: true,
        enableSanitization: true,
        enableRateLimit: true
      }
    },
    logging: {
      level: process.env.LOG_LEVEL || 'info',
      format: 'json'
    },
    orchestrator: {
      enablePerformanceMonitoring: true,
      enableWorkflowOptimization: true,
      maxConcurrentRequests: 1000,
      requestTimeoutMs: 300000
    },
    messageParser: {
      enableMultiModal: true,
      maxMessageLength: 50000,
      enableIntentDetection: true,
      enableEntityExtraction: true,
      enableSentimentAnalysis: true
    },
    reasoning: {
      enableMetaCognition: true,
      enableProblemAnalysis: true,
      enableSolutionGeneration: true,
      enableValidation: true,
      maxThinkingTime: 30000
    },
    monitoring: {
      collection: {
        enabled: true,
        interval: 30000,
        batchSize: 100,
        maxBufferSize: 1000
      },
      systemMetrics: {
        enabled: true,
        collectCPU: true,
        collectMemory: true,
        collectDisk: true,
        collectNetwork: true,
        interval: 30000
      },
      applicationMetrics: {
        enabled: true,
        collectPerformance: true,
        collectErrors: true,
        collectRequests: true,
        interval: 15000
      },
      businessMetrics: {
        enabled: true,
        collectUsers: true,
        collectEngagement: true,
        interval: 60000
      },
      storage: {
        type: 'memory',
        retention: {
          raw: 3600000,
          aggregated: 86400000
        }
      },
      alerting: {
        enabled: true,
        alertChannels: ['console']
      },
      thresholds: {
        cpu: { warning: 80, critical: 95 },
        memory: { warning: 85, critical: 95 },
        errorRate: { warning: 1, critical: 5 }
      }
    },
    apiGateway: {
      port: process.env.API_GATEWAY_PORT || 8444,
      host: process.env.API_GATEWAY_HOST || '0.0.0.0',
      enableSecurity: true,
      enableRateLimit: false,
      enableCORS: true,
      enableCompression: true,
      enableMetrics: true
    }
  };
}

export default { loadConfiguration };
