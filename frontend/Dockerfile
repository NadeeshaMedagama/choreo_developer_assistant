# Multi-stage build for optimized frontend image
FROM node:18-alpine AS build

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Production stage - serve with nginx
FROM nginx:stable-alpine

# Copy built files to nginx
COPY --from=build /app/dist /usr/share/nginx/html

# Copy public directory (including config.js template)
COPY --from=build /app/public /usr/share/nginx/html

# Copy custom nginx config to proxy API requests to backend
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy startup script for dynamic config generation
COPY docs/scripts/docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Expose port 80
EXPOSE 80

# Use custom entrypoint to generate config.js with environment variables
ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["nginx", "-g", "daemon off;"]
