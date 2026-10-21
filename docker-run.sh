#!/usr/bin/env bash
# =============================================================================
# SubscriptIQ - One-Click Academic Evaluator & Docker Runner
# =============================================================================
set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${BLUE}=================================================================${NC}"
echo -e "${GREEN}      SubscriptIQ: Enterprise Text-to-SQL Analytics Engine      ${NC}"
echo -e "${CYAN}             One-Command Docker Deployment Script                ${NC}"
echo -e "${BLUE}=================================================================${NC}"

# Detect if WSL Docker socket is needed
if [ -S "/var/run/docker.sock" ] && [ -z "$DOCKER_HOST" ]; then
    export DOCKER_HOST="unix:///var/run/docker.sock"
fi

# Ensure .env exists (fallback to .env.example)
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo -e "${YELLOW}[!] .env not found. Automatically initializing from .env.example...${NC}"
        cp .env.example .env
    else
        echo -e "${YELLOW}[!] Warning: Neither .env nor .env.example found. Proceeding with defaults.${NC}"
    fi
fi

# Check Docker availability
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}[ERROR] Docker is not installed or not in PATH. Please install Docker.${NC}"
    exit 1
fi

echo -e "\n${CYAN}[1/3] Building and starting containerized services...${NC}"
echo -e "      - PostgreSQL 16 (Relational Database with Auto-Seeding)"
echo -e "      - FastAPI Backend (Uvicorn + LangChain + Qdrant Embeddings)"
echo -e "      - Vue 3 Frontend (Nginx Production Reverse Proxy)\n"

docker compose up -d --build

echo -e "\n${CYAN}[2/3] Waiting for database initialization and health checks...${NC}"
RETRIES=30
while [ $RETRIES -gt 0 ]; do
    if curl -s -f http://localhost:8000/api/health > /dev/null 2>&1 || curl -s -f http://localhost:5173/api/health > /dev/null 2>&1; then
        break
    fi
    sleep 2
    RETRIES=$((RETRIES-1))
done

echo -e "\n${CYAN}[3/3] Service Status:${NC}"
docker compose ps

echo -e "\n${GREEN}=================================================================${NC}"
echo -e "${GREEN}   SubscriptIQ is running successfully!     ${NC}"
echo -e "${GREEN}=================================================================${NC}"
echo -e "  ${BLUE}● Web Dashboard (Vue 3 UI):${NC}    ${CYAN}http://localhost:5173${NC} (or http://localhost)"
echo -e "  ${BLUE}● Interactive Swagger Docs:${NC}    ${CYAN}http://localhost:5173/docs${NC} (or http://localhost:8000/docs)"
echo -e "  ${BLUE}● Backend Health Endpoint:${NC}     ${CYAN}http://localhost:5173/api/health${NC}"
echo -e "  ${BLUE}● PostgreSQL Port (Host):${NC}      ${CYAN}localhost:5434${NC} (Database: subscriptiq)"
echo -e "-----------------------------------------------------------------"
echo -e "  ${YELLOW}Admin Credentials (for Admin Console):${NC}"
echo -e "  Email:    ${CYAN}admin@subscriptiq.ai${NC}"
echo -e "  Password: ${CYAN}admin123${NC}"
echo -e "-----------------------------------------------------------------"
echo -e "  ${YELLOW}To view live logs:${NC}  docker compose logs -f"
echo -e "  ${YELLOW}To stop services:${NC}   docker compose down"
echo -e "${GREEN}=================================================================${NC}\n"
