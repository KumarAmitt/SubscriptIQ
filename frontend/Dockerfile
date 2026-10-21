# Multi-stage Dockerfile for SubscriptIQ Frontend

# --- Base Dependencies ---
FROM node:22-alpine AS base
WORKDIR /app

# Copy package files first for better layer caching
COPY package*.json ./

# Install all dependencies
RUN npm install

# --- Production Build Stage ---
FROM base AS builder
ARG VITE_API_BASE_URL=/api
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
COPY . .
RUN npm run build

# --- Production Stage (Nginx Reverse Proxy & Static Host) ---
FROM nginx:alpine AS production
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]

# --- Development Stage (Default) ---
# Used for feature development with hot module reloading (HMR) and testing
FROM base AS development
ENV NODE_ENV=development
COPY . .
EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
