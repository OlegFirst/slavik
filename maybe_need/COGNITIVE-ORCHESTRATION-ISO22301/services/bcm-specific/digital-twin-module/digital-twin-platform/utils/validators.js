/**
 * Validation utilities for NASH 4.0
 */

export function validateString(value, minLength = 0, maxLength = Infinity) {
  return typeof value === 'string' && 
         value.length >= minLength && 
         value.length <= maxLength;
}

export function validateObject(value) {
  return value !== null && typeof value === 'object' && !Array.isArray(value);
}

export function validateArray(value) {
  return Array.isArray(value);
}

export function validateEmail(email) {
  const emailRegex = /^[^s@]+@[^s@]+.[^s@]+$/;
  return emailRegex.test(email);
}

export function validateURL(url) {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
}

export function validateJSON(str) {
  try {
    JSON.parse(str);
    return true;
  } catch {
    return false;
  }
}

export function sanitizeString(str) {
  return str.replace(/[<>]/g, '');
}

/**
 * Sanitizes input string by removing dangerous characters and patterns
 * 
 * @param {string} input - Input string to sanitize
 * @param {Object} options - Sanitization options
 * @returns {string} Sanitized input
 */
export function sanitizeInput(input, options = {}) {
  if (typeof input !== 'string') {
    return String(input);
  }

  const config = {
    allowHTML: false,
    maxLength: 10000,
    preserveWhitespace: false,
    ...options
  };

  let sanitized = input;

  // Remove dangerous HTML tags if not allowed
  if (!config.allowHTML) {
    sanitized = sanitized.replace(/<[^>]*>/g, '');
  }

  // Remove potential script injection patterns
  sanitized = sanitized.replace(/javascript:/gi, '');
  sanitized = sanitized.replace(/on\w+\s*=/gi, '');

  // Handle whitespace
  if (!config.preserveWhitespace) {
    sanitized = sanitized.replace(/\s+/g, ' ').trim();
  }

  // Truncate if too long
  if (sanitized.length > config.maxLength) {
    sanitized = sanitized.substring(0, config.maxLength);
  }

  return sanitized;
}

/**
 * Validates message structure for platform processing
 * 
 * @param {Object} message - Message object to validate
 * @param {Object} schema - Validation schema
 * @returns {Object} Validation result
 */
export function validateMessageStructure(message, schema = {}) {
  const result = {
    isValid: true,
    errors: [],
    sanitizedMessage: null
  };

  try {
    // Basic structure validation
    if (!message || typeof message !== 'object') {
      result.isValid = false;
      result.errors.push('Message must be a valid object');
      return result;
    }

    // Required fields validation
    const requiredFields = schema.required || ['type', 'content'];
    for (const field of requiredFields) {
      if (!(field in message)) {
        result.isValid = false;
        result.errors.push(`Required field '${field}' is missing`);
      }
    }

    // Type validation
    if (message.type) {
      const validTypes = schema.validTypes || [
        'text',
        'command',
        'query',
        'system',
        'notification',
        'error'
      ];
      
      if (!validTypes.includes(message.type)) {
        result.isValid = false;
        result.errors.push(`Invalid message type: ${message.type}`);
      }
    }

    // Content validation
    if (message.content) {
      if (typeof message.content !== 'string') {
        result.isValid = false;
        result.errors.push('Message content must be a string');
      } else {
        const maxContentLength = schema.maxContentLength || 50000;
        if (message.content.length > maxContentLength) {
          result.isValid = false;
          result.errors.push(`Content exceeds maximum length of ${maxContentLength} characters`);
        }
      }
    }

    // Metadata validation
    if (message.metadata && typeof message.metadata !== 'object') {
      result.isValid = false;
      result.errors.push('Message metadata must be an object');
    }

    // Create sanitized version if valid
    if (result.isValid) {
      result.sanitizedMessage = {
        type: message.type,
        content: sanitizeInput(message.content, { preserveWhitespace: true }),
        metadata: message.metadata || {},
        timestamp: message.timestamp || Date.now(),
        id: message.id || generateMessageId()
      };

      // Preserve additional valid fields
      const allowedFields = schema.allowedFields || [];
      for (const field of allowedFields) {
        if (field in message) {
          result.sanitizedMessage[field] = message[field];
        }
      }
    }

  } catch (error) {
    result.isValid = false;
    result.errors.push(`Validation error: ${error.message}`);
  }

  return result;
}

/**
 * Generates unique message ID
 * 
 * @private
 * @returns {string} Unique message ID
 */
function generateMessageId() {
  return `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

export default {
  validateString,
  validateObject,
  validateArray,
  validateEmail,
  validateURL,
  validateJSON,
  sanitizeString,
  sanitizeInput,
  validateMessageStructure
};
