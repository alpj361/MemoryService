#!/bin/bash

# Laura Memory Service - Production Deployment Script
# ====================================================

set -e  # Exit on any error

echo "🚀 Laura Memory Service - Production Deployment"
echo "==============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker-compose.yml"
ENV_FILE=".env"
SERVICE_NAME="laura-memory"
NGINX_PROFILE="with-nginx"

# Functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check requirements
check_requirements() {
    log_info "Checking requirements..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed"
        exit 1
    fi
    
    if [ ! -f "$ENV_FILE" ]; then
        log_error "Environment file $ENV_FILE not found"
        log_info "Please copy .env.example to .env and configure it"
        exit 1
    fi
    
    log_success "Requirements check passed"
}

# Validate environment variables
validate_env() {
    log_info "Validating environment variables..."
    
    source "$ENV_FILE"
    
    if [ -z "$ZEP_API_KEY" ]; then
        log_error "ZEP_API_KEY is not set in $ENV_FILE"
        exit 1
    fi
    
    if [ -z "$SECRET_KEY" ] || [ "$SECRET_KEY" = "production-secret-key-change-me" ]; then
        log_warning "SECRET_KEY should be changed for production"
    fi
    
    log_success "Environment validation passed"
}

# Build and deploy
deploy() {
    local with_nginx=${1:-false}
    
    log_info "Building and deploying Laura Memory Service..."
    
    # Stop existing containers
    log_info "Stopping existing containers..."
    docker-compose down --remove-orphans || true
    
    # Build new image
    log_info "Building Docker image..."
    docker-compose build --no-cache "$SERVICE_NAME"
    
    # Start services
    if [ "$with_nginx" = true ]; then
        log_info "Starting services with Nginx..."
        docker-compose --profile "$NGINX_PROFILE" up -d
    else
        log_info "Starting services without Nginx..."
        docker-compose up -d "$SERVICE_NAME"
    fi
    
    # Wait for service to be healthy
    log_info "Waiting for service to be healthy..."
    timeout=60
    while [ $timeout -gt 0 ]; do
        if docker-compose exec -T "$SERVICE_NAME" curl -f http://localhost:5001/health > /dev/null 2>&1; then
            log_success "Service is healthy!"
            break
        fi
        sleep 2
        timeout=$((timeout - 2))
        echo -n "."
    done
    echo
    
    if [ $timeout -le 0 ]; then
        log_error "Service failed to become healthy"
        docker-compose logs "$SERVICE_NAME"
        exit 1
    fi
}

# Show status
show_status() {
    log_info "Service status:"
    docker-compose ps
    
    echo
    log_info "Service logs (last 20 lines):"
    docker-compose logs --tail=20 "$SERVICE_NAME"
    
    echo
    log_info "Health check:"
    curl -s http://localhost:5001/health | python3 -m json.tool || log_warning "Health check failed"
}

# Show usage
usage() {
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo
    echo "Commands:"
    echo "  deploy       Deploy the service (default)"
    echo "  deploy-nginx Deploy with Nginx reverse proxy"
    echo "  status       Show service status"
    echo "  logs         Show service logs"
    echo "  stop         Stop the service"
    echo "  restart      Restart the service"
    echo "  update       Update and redeploy"
    echo
    echo "Options:"
    echo "  -h, --help   Show this help message"
}

# Main execution
case "${1:-deploy}" in
    "deploy")
        check_requirements
        validate_env
        deploy false
        show_status
        ;;
    "deploy-nginx")
        check_requirements
        validate_env
        deploy true
        show_status
        ;;
    "status")
        show_status
        ;;
    "logs")
        docker-compose logs -f "$SERVICE_NAME"
        ;;
    "stop")
        log_info "Stopping services..."
        docker-compose down
        log_success "Services stopped"
        ;;
    "restart")
        log_info "Restarting services..."
        docker-compose restart "$SERVICE_NAME"
        show_status
        ;;
    "update")
        log_info "Updating and redeploying..."
        git pull || log_warning "Git pull failed - continuing with local changes"
        check_requirements
        validate_env
        deploy false
        show_status
        ;;
    "-h"|"--help"|"help")
        usage
        ;;
    *)
        log_error "Unknown command: $1"
        usage
        exit 1
        ;;
esac

log_success "🎉 Deployment completed successfully!"
echo
log_info "Service endpoints:"
echo "  Health check: http://localhost:5001/health"
echo "  API base:     http://localhost:5001/api/"
echo "  Metrics:      http://localhost:5001/metrics"

if docker-compose ps | grep -q nginx; then
    echo "  Nginx proxy:  http://localhost/"
fi 