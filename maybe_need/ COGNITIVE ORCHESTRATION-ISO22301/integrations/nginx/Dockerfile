FROM nginx:alpine

# Default nginx configuration
RUN mkdir -p /usr/share/nginx/html

# Basic health check endpoint
RUN echo "OK" > /usr/share/nginx/html/health

# Copy custom config if exists
COPY nginx.conf /etc/nginx/nginx.conf 2>/dev/null || true

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]