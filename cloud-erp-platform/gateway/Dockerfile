# =============================================================================
#  Gateway Service Dockerfile
#  Nginx-based API Gateway / Load Balancer
#  Runs in public subnet, routes to private services (ERP/CRM/WMS)
# =============================================================================

FROM nginx:alpine

# Install health check tools and logging utilities
RUN apk add --no-cache curl wget bash

# Copy nginx configuration
# COPY gateway/nginx.conf /etc/nginx/nginx.conf

# Copy dashboard files (static assets)
# COPY dashboard /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Copy dashboard files
COPY ../dashboard /usr/share/nginx/html

# Create nginx log directory with proper permissions
RUN mkdir -p /var/log/nginx && \
    touch /var/log/nginx/access.log /var/log/nginx/error.log && \
    chmod -R 755 /var/log/nginx

# Health check endpoint
HEALTHCHECK --interval=10s --timeout=5s --retries=3 \
    CMD wget -qO- http://127.0.0.1/health || exit 1

# Expose the gateway port
EXPOSE 80

# Start nginx in foreground
CMD ["nginx", "-g", "daemon off;"]
