# Multi-stage build for BCM Admin Control Center
FROM node:18-alpine AS builder

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./
COPY tsconfig*.json ./
COPY vite.config.ts ./
COPY tailwind.config.js ./
COPY postcss.config.js ./

# Install dependencies
RUN npm ci

# Copy source code
COPY src/ ./src/
COPY index.html ./
# .env file will be provided at runtime via environment variables or Docker secrets

# Build the application
RUN npm run build

# Production stage
FROM nginx:alpine AS production

# Copy custom nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built assets from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Create non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S admin -u 1001

# Set ownership
RUN chown -R admin:nodejs /usr/share/nginx/html
RUN chown -R admin:nodejs /var/cache/nginx

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:80/health || exit 1

# Expose port
EXPOSE 80

# Switch to non-root user
USER admin

# Start nginx
CMD ["nginx", "-g", "daemon off;"]

# Development stage (for development with hot reload)
FROM node:18-alpine AS development

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install all dependencies (including dev)
RUN npm install && npm install @rollup/rollup-linux-arm64-musl

# Copy configuration files
COPY tsconfig*.json ./
COPY vite.config.ts ./
COPY tailwind.config.js ./
COPY postcss.config.js ./
COPY .eslintrc.json ./

# Copy source code
COPY src/ ./src/
COPY index.html ./
# .env file will be provided at runtime via environment variables or Docker secrets

# Create non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S admin -u 1001

# Change ownership
RUN chown -R admin:nodejs /app

# Switch to non-root user
USER admin

# Expose development port
EXPOSE 3001

# Start development server
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "3001"]
