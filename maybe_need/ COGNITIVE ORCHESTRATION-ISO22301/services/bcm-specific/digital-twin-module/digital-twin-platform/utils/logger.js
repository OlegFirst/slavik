/**
 * Logger Configuration
 * Simple logger using winston for the Universal AI Partnership Platform
 */

import winston from 'winston';

/**
 * Create logger instance with specific service name
 * @param {string} service - Service name for logging context
 * @returns {winston.Logger} Configured logger instance
 */
export function createLogger(service = 'universal-ai-platform') {
  return winston.createLogger({
    level: process.env.LOG_LEVEL || 'info',
    format: winston.format.combine(
      winston.format.timestamp(),
      winston.format.errors({ stack: true }),
      winston.format.colorize(),
      winston.format.simple()
    ),
    defaultMeta: { service },
    transports: [
      new winston.transports.File({ filename: 'logs/error.log', level: 'error' }),
      new winston.transports.File({ filename: 'logs/combined.log' }),
      new winston.transports.Console({
        format: winston.format.simple()
      })
    ]
  });
}

// Default logger instance
const logger = createLogger();

export default logger;