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
COPY . .
RUN npm run build

# --- Production Stage (Nginx) ---
FROM nginx:alpine AS production
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
