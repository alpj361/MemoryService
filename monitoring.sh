#!/bin/bash

# Laura Memory Service - Production Monitoring Script
# ===================================================

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SERVICE_URL="http://localhost:5001"
NGINX_URL="http://localhost"

# Functions
log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }

# Health check
check_health() {
    log_info "Checking service health..."
    
    if curl -s -f "$SERVICE_URL/health" > /dev/null; then
        local health_data=$(curl -s "$SERVICE_URL/health")
        local status=$(echo "$health_data" | python3 -c "import sys, json; print(json.load(sys.stdin)['status'])")
        
        if [ "$status" = "healthy" ]; then
            log_success "Service is healthy"
            echo "$health_data" | python3 -m json.tool
        else
            log_warning "Service reports unhealthy status"
            echo "$health_data" | python3 -m json.tool
        fi
    else
        log_error "Health check failed - service unreachable"
        return 1
    fi
}

# Performance metrics
check_metrics() {
    log_info "Checking performance metrics..."
    
    if curl -s -f "$SERVICE_URL/metrics" > /dev/null; then
        local metrics=$(curl -s "$SERVICE_URL/metrics")
        
        echo "Recent request metrics:"
        echo "$metrics" | grep "laura_memory_requests_total" | head -5
        echo
        echo "Performance metrics:"
        echo "$metrics" | grep "laura_memory_request_duration" | head -5
    else
        log_warning "Metrics endpoint unavailable"
    fi
}

# Resource usage
check_resources() {
    log_info "Checking resource usage..."
    
    if command -v docker &> /dev/null; then
        echo "Container resource usage:"
        docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}" laura-memory-service 2>/dev/null || log_warning "Container not found"
        echo
        
        echo "Container processes:"
        docker exec laura-memory-service ps aux 2>/dev/null || log_warning "Cannot access container processes"
    else
        log_warning "Docker not available for resource checking"
    fi
}

# Log analysis
check_logs() {
    local lines=${1:-50}
    log_info "Analyzing recent logs ($lines lines)..."
    
    if command -v docker-compose &> /dev/null; then
        echo "Recent application logs:"
        docker-compose logs --tail="$lines" laura-memory 2>/dev/null | grep -E "(ERROR|WARNING|INFO)" | tail -10
        echo
        
        echo "Error summary:"
        local error_count=$(docker-compose logs laura-memory 2>/dev/null | grep -c "ERROR" || echo "0")
        local warning_count=$(docker-compose logs laura-memory 2>/dev/null | grep -c "WARNING" || echo "0")
        
        echo "- Errors in logs: $error_count"
        echo "- Warnings in logs: $warning_count"
        
        if [ "$error_count" -gt 0 ]; then
            log_warning "Found $error_count errors in logs"
            echo "Recent errors:"
            docker-compose logs laura-memory 2>/dev/null | grep "ERROR" | tail -3
        fi
    else
        log_warning "Docker Compose not available for log checking"
    fi
}

# Network connectivity
check_connectivity() {
    log_info "Checking network connectivity..."
    
    # Check internal connectivity
    if curl -s -f "$SERVICE_URL/health" > /dev/null; then
        log_success "Internal connectivity OK"
    else
        log_error "Internal connectivity failed"
    fi
    
    # Check Nginx if available
    if curl -s -f "$NGINX_URL/health" > /dev/null; then
        log_success "Nginx proxy connectivity OK"
    else
        log_warning "Nginx proxy not available or not configured"
    fi
    
    # Check external dependencies
    if curl -s -f "https://api.getzep.com" > /dev/null; then
        log_success "Zep API connectivity OK"
    else
        log_warning "Zep API connectivity issues"
    fi
}

# Load test
load_test() {
    local requests=${1:-10}
    log_info "Running basic load test ($requests requests)..."
    
    local success_count=0
    local total_time=0
    
    for i in $(seq 1 "$requests"); do
        local start_time=$(date +%s.%N)
        if curl -s -f "$SERVICE_URL/health" > /dev/null; then
            success_count=$((success_count + 1))
        fi
        local end_time=$(date +%s.%N)
        local duration=$(echo "$end_time - $start_time" | bc -l 2>/dev/null || echo "0")
        total_time=$(echo "$total_time + $duration" | bc -l 2>/dev/null || echo "$total_time")
        
        echo -n "."
    done
    echo
    
    local success_rate=$(echo "scale=2; $success_count * 100 / $requests" | bc -l 2>/dev/null || echo "0")
    local avg_time=$(echo "scale=3; $total_time / $requests" | bc -l 2>/dev/null || echo "0")
    
    echo "Load test results:"
    echo "- Success rate: $success_rate%"
    echo "- Average response time: ${avg_time}s"
    
    if [ "$success_count" -eq "$requests" ]; then
        log_success "All requests successful"
    else
        log_warning "Some requests failed"
    fi
}

# Full monitoring report
full_report() {
    echo "=========================================="
    echo "Laura Memory Service - Monitoring Report"
    echo "=========================================="
    echo "Timestamp: $(date)"
    echo
    
    check_health
    echo
    check_connectivity
    echo
    check_resources
    echo
    check_metrics
    echo
    check_logs 100
    echo
    load_test 5
    echo
    
    log_info "Monitoring report completed"
}

# Real-time monitoring
watch_service() {
    log_info "Starting real-time monitoring (Ctrl+C to stop)..."
    
    while true; do
        clear
        echo "Laura Memory Service - Live Monitor"
        echo "==================================="
        echo "$(date)"
        echo
        
        # Quick health check
        if curl -s -f "$SERVICE_URL/health" > /dev/null; then
            log_success "Service: UP"
        else
            log_error "Service: DOWN"
        fi
        
        # Resource usage
        if command -v docker &> /dev/null; then
            echo
            docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}" laura-memory-service 2>/dev/null || echo "Container not found"
        fi
        
        # Recent logs
        echo
        echo "Recent logs:"
        docker-compose logs --tail=5 laura-memory 2>/dev/null | tail -3 || echo "No logs available"
        
        sleep 5
    done
}

# Usage
usage() {
    echo "Usage: $0 [COMMAND]"
    echo
    echo "Commands:"
    echo "  health        Check service health"
    echo "  metrics       Show performance metrics"
    echo "  resources     Show resource usage"
    echo "  logs [lines]  Analyze logs (default: 50 lines)"
    echo "  connectivity  Check network connectivity"
    echo "  load [reqs]   Run load test (default: 10 requests)"
    echo "  report        Full monitoring report"
    echo "  watch         Real-time monitoring"
    echo
}

# Main execution
case "${1:-health}" in
    "health")
        check_health
        ;;
    "metrics")
        check_metrics
        ;;
    "resources")
        check_resources
        ;;
    "logs")
        check_logs "${2:-50}"
        ;;
    "connectivity")
        check_connectivity
        ;;
    "load")
        load_test "${2:-10}"
        ;;
    "report")
        full_report
        ;;
    "watch")
        watch_service
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