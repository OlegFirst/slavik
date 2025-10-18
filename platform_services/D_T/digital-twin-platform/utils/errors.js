/**
 * Custom Error Classes
 * Standard error handling for the Universal AI Partnership Platform
 */

export class BaseError extends Error {
  constructor(message = 'Base error') {
    super(message);
    this.name = 'BaseError';
    this.statusCode = 500;
  }
}

export class ValidationError extends Error {
  constructor(message, field = null) {
    super(message);
    this.name = 'ValidationError';
    this.field = field;
    this.statusCode = 400;
  }
}

export class AuthenticationError extends Error {
  constructor(message = 'Authentication required') {
    super(message);
    this.name = 'AuthenticationError';
    this.statusCode = 401;
  }
}

export class AuthorizationError extends Error {
  constructor(message = 'Insufficient permissions') {
    super(message);
    this.name = 'AuthorizationError';
    this.statusCode = 403;
  }
}

export class NotFoundError extends Error {
  constructor(message = 'Resource not found') {
    super(message);
    this.name = 'NotFoundError';
    this.statusCode = 404;
  }
}

export class InternalServerError extends Error {
  constructor(message = 'Internal server error') {
    super(message);
    this.name = 'InternalServerError';
    this.statusCode = 500;
  }
}

export class OrchestrationError extends Error {
  constructor(message = 'Orchestration error') {
    super(message);
    this.name = 'OrchestrationError';
    this.statusCode = 500;
  }
}

export class ConfigurationError extends Error {
  constructor(message = 'Configuration error') {
    super(message);
    this.name = 'ConfigurationError';
    this.statusCode = 500;
  }
}

export class ProcessingError extends Error {
  constructor(message = 'Processing error') {
    super(message);
    this.name = 'ProcessingError';
    this.statusCode = 500;
  }
}

export class PlatformError extends Error {
  constructor(message = 'Platform error', originalError = null) {
    super(message);
    this.name = 'PlatformError';
    this.statusCode = 500;
    this.originalError = originalError;
  }
}

export class SecurityError extends Error {
  constructor(message = 'Security error') {
    super(message);
    this.name = 'SecurityError';
    this.statusCode = 403;
  }
}

export class NetworkError extends Error {
  constructor(message = 'Network error') {
    super(message);
    this.name = 'NetworkError';
    this.statusCode = 503;
  }
}

export class RateLimitError extends Error {
  constructor(message = 'Rate limit exceeded') {
    super(message);
    this.name = 'RateLimitError';
    this.statusCode = 429;
  }
}

export class ResourceError extends Error {
  constructor(message = 'Resource error') {
    super(message);
    this.name = 'ResourceError';
    this.statusCode = 503;
  }
}

export class IntegrationError extends Error {
  constructor(message = 'Integration error') {
    super(message);
    this.name = 'IntegrationError';
    this.statusCode = 502;
  }
}

export class SecurityViolationError extends Error {
  constructor(message = 'Security violation') {
    super(message);
    this.name = 'SecurityViolationError';
    this.statusCode = 403;
  }
}

export class InputValidationError extends Error {
  constructor(message = 'Input validation error') {
    super(message);
    this.name = 'InputValidationError';
    this.statusCode = 400;
  }
}

export class ModuleError extends Error {
  constructor(message = 'Module error', originalError = null) {
    super(message);
    this.name = 'ModuleError';
    this.statusCode = 500;
    this.originalError = originalError;
  }
}

export class DatabaseError extends Error {
  constructor(message = 'Database error', originalError = null) {
    super(message);
    this.name = 'DatabaseError';
    this.statusCode = 500;
    this.originalError = originalError;
  }
}