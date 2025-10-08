// Environment configuration - убираем hardcoded credentials
export const config = {
  // API Configuration
  api: {
    baseUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8888',
    timeout: parseInt(import.meta.env.VITE_API_TIMEOUT || '30000'),
    retries: parseInt(import.meta.env.VITE_API_RETRIES || '3')
  },

  // Keycloak Configuration
  keycloak: {
    url: import.meta.env.VITE_KEYCLOAK_URL || 'http://localhost:8080',
    realm: import.meta.env.VITE_KEYCLOAK_REALM || 'bcm-platform',
    clientId: import.meta.env.VITE_KEYCLOAK_CLIENT_ID || 'bcm-admin-panel'
  },

  // WebSocket Configuration
  websocket: {
    url: import.meta.env.VITE_WS_URL || 'ws://localhost:8001',
    secure: import.meta.env.VITE_WS_SECURE === 'true',
    reconnection: true,
    maxReconnectAttempts: 5
  },

  // Database Configuration (убираем Supabase keys из кода)
  database: {
    // НЕ ХРАНИТЬ КЛЮЧИ В КОДЕ!
    apiUrl: import.meta.env.VITE_DB_API_URL || 'http://localhost:8069'
  },

  // CORS Configuration
  cors: {
    allowedOrigins: [
      'http://localhost:3000',
      'http://localhost:3001',
      'http://localhost:3003',
      'https://bcm-platform.com'
    ]
  },

  // Security Configuration
  security: {
    csrfEnabled: import.meta.env.VITE_CSRF_ENABLED !== 'false',
    httpsOnly: import.meta.env.NODE_ENV === 'production',
    cookieSecure: import.meta.env.NODE_ENV === 'production'
  },

  // Logging Configuration
  logging: {
    level: import.meta.env.VITE_LOG_LEVEL || 'info',
    enableConsole: import.meta.env.NODE_ENV !== 'production'
  }
};

// Production security checks
if (import.meta.env.NODE_ENV === 'production') {
  // Убираем console.log из production
  console.log = () => {};
  console.debug = () => {};
  console.info = () => {};

  // HTTPS enforcement
  if (location.protocol !== 'https:') {
    location.replace(`https:${location.href.substring(location.protocol.length)}`);
  }
}