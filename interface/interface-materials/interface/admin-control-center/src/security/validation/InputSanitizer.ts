import DOMPurify from 'dompurify';

export class InputSanitizer {
  // Sanitize HTML input
  static sanitizeHTML(input: string): string {
    return DOMPurify.sanitize(input, {
      ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'p', 'br'],
      ALLOWED_ATTR: []
    });
  }

  // Sanitize plain text (remove all HTML)
  static sanitizeText(input: string): string {
    return DOMPurify.sanitize(input, { ALLOWED_TAGS: [] });
  }

  // Validate and sanitize API responses
  static validateApiResponse(data: any, schema: any): any {
    // Basic validation
    if (!data || typeof data !== 'object') {
      throw new Error('Invalid API response format');
    }

    // Recursively sanitize strings
    return this.recursiveSanitize(data);
  }

  // Validate WebSocket messages
  static validateWebSocketMessage(message: any): any {
    if (!message || !message.type) {
      throw new Error('Invalid WebSocket message format');
    }

    return this.recursiveSanitize(message);
  }

  private static recursiveSanitize(obj: any): any {
    if (typeof obj === 'string') {
      return this.sanitizeText(obj);
    }

    if (Array.isArray(obj)) {
      return obj.map(item => this.recursiveSanitize(item));
    }

    if (obj && typeof obj === 'object') {
      const sanitized: any = {};
      for (const [key, value] of Object.entries(obj)) {
        sanitized[key] = this.recursiveSanitize(value);
      }
      return sanitized;
    }

    return obj;
  }

  // SQL injection prevention
  static sanitizeSQL(input: string): string {
    return input.replace(/['";\\]/g, '');
  }

  // XSS prevention for URLs
  static validateURL(url: string): boolean {
    try {
      const parsed = new URL(url);
      return ['http:', 'https:', 'ws:', 'wss:'].includes(parsed.protocol);
    } catch {
      return false;
    }
  }
}