/**
 * Simple Logger for Digital Twin Integration
 */

class Logger {
    constructor() {
        this.logLevel = process.env.LOG_LEVEL || 'info';
    }

    formatMessage(level, message, meta = {}) {
        const timestamp = new Date().toISOString();
        const metaString = Object.keys(meta).length > 0 ? ` ${JSON.stringify(meta)}` : '';
        return `[${timestamp}] [${level.toUpperCase()}] ${message}${metaString}`;
    }

    log(level, message, meta = {}) {
        console.log(this.formatMessage(level, message, meta));
    }

    info(message, meta = {}) {
        this.log('info', message, meta);
    }

    warn(message, meta = {}) {
        this.log('warn', message, meta);
    }

    error(message, meta = {}) {
        this.log('error', message, meta);
    }

    debug(message, meta = {}) {
        if (this.logLevel === 'debug') {
            this.log('debug', message, meta);
        }
    }
}

export default new Logger();