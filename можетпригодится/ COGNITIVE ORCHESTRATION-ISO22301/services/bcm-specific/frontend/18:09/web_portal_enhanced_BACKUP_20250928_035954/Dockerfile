# Multi-stage Docker build for BCM Web Portal v2
# Stage 1: Build the application

FROM node:18-alpine AS builder

# Set working directory
WORKDIR /app

# Install build dependencies
RUN apk add --no-cache git

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production && npm cache clean --force

# Copy source code
COPY . .

# Build arguments for environment variables
ARG VITE_APP_TITLE="BCM Platform v2"
ARG VITE_API_BASE_URL="http://localhost:8000/api"
ARG VITE_API_VERSION="v1"
ARG VITE_APP_ENV="production"

# Set environment variables
ENV VITE_APP_TITLE=$VITE_APP_TITLE
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
ENV VITE_API_VERSION=$VITE_API_VERSION
ENV VITE_APP_ENV=$VITE_APP_ENV

# Build the application
RUN npm run build

# Stage 2: Serve with nginx
FROM nginx:1.25-alpine AS production

# Install additional packages for better security and monitoring
RUN apk add --no-cache \
    curl \
    tzdata \
    && rm -rf /var/cache/apk/*

# Set timezone
ENV TZ=UTC
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf
COPY nginx-default.conf /etc/nginx/conf.d/default.conf

# Copy built application from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy additional nginx configurations
COPY nginx-security.conf /etc/nginx/conf.d/security.conf

# Create nginx user for better security
RUN addgroup -g 1001 -S nginx && \
    adduser -S -D -H -u 1001 -h /var/cache/nginx -s /sbin/nologin -G nginx -g nginx nginx

# Set proper permissions
RUN chown -R nginx:nginx /usr/share/nginx/html && \
    chown -R nginx:nginx /var/cache/nginx && \
    chown -R nginx:nginx /var/log/nginx && \
    chown -R nginx:nginx /etc/nginx/conf.d

# Switch to non-root user
USER nginx

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:80/health || exit 1

# Expose port
EXPOSE 80

# Labels for better container management
LABEL maintainer="BCM Platform Team"
LABEL version="2.0.0"
LABEL description="BCM Web Portal v2 - Modern Vue.js Frontend"

# Start nginx
CMD ["nginx", "-g", "daemon off;"]