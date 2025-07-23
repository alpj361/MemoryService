# Laura Memory Service - Production Deployment Guide

## 🚀 Quick Start

### 1. Prerequisites

- Docker & Docker Compose installed
- Environment variables configured
- Minimum 256MB RAM, 0.5 CPU cores

### 2. Setup Environment

```bash
# Copy environment template
cp .env.example .env

# Edit with your configuration
nano .env
```

**Required variables:**
- `ZEP_API_KEY`: Your Zep API key
- `SECRET_KEY`: Generate a secure random string

### 3. Deploy

```bash
# Make deploy script executable
chmod +x deploy.sh

# Deploy basic setup
./deploy.sh deploy

# Or deploy with Nginx reverse proxy
./deploy.sh deploy-nginx
```

## 📋 Production Configuration

### Gunicorn Settings

- **Workers**: 4 (default) or `CPU_COUNT * 2 + 1`
- **Worker Class**: `sync` (CPU-bound tasks)
- **Timeout**: 30 seconds
- **Memory**: Restarts workers after 1000 requests (prevents leaks)

### Security Features

- ✅ Non-root user in container
- ✅ Security headers (XSS, CSRF, etc.)
- ✅ Rate limiting (via Nginx)
- ✅ Input validation
- ✅ Structured logging

### Performance Optimizations

- ✅ Prometheus metrics endpoint
- ✅ Gzip compression (Nginx)
- ✅ Connection pooling
- ✅ Memory-mapped temp files (`/dev/shm`)
- ✅ Log rotation

## 🔧 Architecture Options

### Option 1: Direct Deployment (Simple)

```
Client → Laura Memory Service (Port 5001)
```

```bash
./deploy.sh deploy
```

**Pros:** Simple, direct access
**Cons:** No rate limiting, basic security

### Option 2: With Nginx Reverse Proxy (Recommended)

```
Client → Nginx (Port 80/443) → Laura Memory Service
```

```bash
./deploy.sh deploy-nginx
```

**Pros:** Rate limiting, SSL termination, advanced routing
**Cons:** Additional complexity

## 📊 Monitoring & Health Checks

### Health Check Endpoint

```bash
curl http://localhost:5001/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "laura-memory",
  "version": "1.0.0",
  "environment": "production",
  "zep_connected": true,
  "timestamp": 1674567890
}
```

### Metrics (Prometheus)

```bash
curl http://localhost:5001/metrics
```

**Available metrics:**
- `laura_memory_requests_total`: Request counter by method/endpoint/status
- `laura_memory_request_duration_seconds`: Request duration histogram

### Log Files

| File | Description |
|------|-------------|
| `/app/logs/laura-memory.log` | Application logs |
| `/app/logs/gunicorn_access.log` | Gunicorn access logs |
| `/app/logs/gunicorn_error.log` | Gunicorn error logs |
| `/var/log/nginx/access.log` | Nginx access logs (if using) |
| `/var/log/nginx/error.log` | Nginx error logs (if using) |

## 🛠️ Management Commands

### Deployment Operations

```bash
# Deploy/redeploy
./deploy.sh deploy

# Deploy with Nginx
./deploy.sh deploy-nginx

# Check status
./deploy.sh status

# View logs
./deploy.sh logs

# Stop services
./deploy.sh stop

# Restart services
./deploy.sh restart

# Update from git and redeploy
./deploy.sh update
```

### Docker Operations

```bash
# Manual container management
docker-compose up -d
docker-compose down
docker-compose logs -f laura-memory
docker-compose exec laura-memory bash

# Resource monitoring
docker stats
docker-compose top
```

## 🔍 Troubleshooting

### Common Issues

**1. Service won't start**
```bash
# Check logs
./deploy.sh logs

# Check environment
docker-compose exec laura-memory env | grep -E "(ZEP|SECRET)"

# Verify Zep connection
docker-compose exec laura-memory python -c "
from memory import get_memory_stats
print(get_memory_stats())
"
```

**2. High memory usage**
```bash
# Check worker count
docker-compose exec laura-memory ps aux

# Reduce workers if needed
echo "GUNICORN_WORKERS=2" >> .env
./deploy.sh restart
```

**3. Slow response times**
```bash
# Check Gunicorn metrics
curl -s http://localhost:5001/metrics | grep laura_memory_request_duration

# Check system resources
docker stats
```

### Log Analysis

```bash
# Recent errors
docker-compose logs laura-memory | grep ERROR

# Request patterns
docker-compose logs nginx | grep "POST /api" | tail -50

# Performance metrics
docker-compose logs laura-memory | grep "duration"
```

## 🚨 Production Checklist

### Before Going Live

- [ ] Change default `SECRET_KEY`
- [ ] Configure proper `ZEP_API_KEY`
- [ ] Set `FLASK_ENV=production`
- [ ] Configure log rotation
- [ ] Set up monitoring/alerts
- [ ] Test health check endpoint
- [ ] Verify rate limiting works
- [ ] Test backup/restore procedures

### Security Hardening

- [ ] Use HTTPS in production (SSL certificate)
- [ ] Configure firewall rules
- [ ] Regularly update Docker base images
- [ ] Monitor security logs
- [ ] Implement proper authentication if needed
- [ ] Regular security audits

### Performance Tuning

- [ ] Profile memory usage under load
- [ ] Adjust worker count based on CPU cores
- [ ] Configure database connection pooling
- [ ] Implement caching if needed
- [ ] Monitor and tune timeouts

## 📈 Scaling

### Horizontal Scaling

```yaml
# docker-compose.yml
services:
  laura-memory:
    deploy:
      replicas: 3
  
  nginx:
    # Load balance between instances
```

### Resource Limits

```yaml
deploy:
  resources:
    limits:
      memory: 1G
      cpus: '2.0'
    reservations:
      memory: 512M
      cpus: '1.0'
```

## 🆘 Support

If you encounter issues:

1. Check logs: `./deploy.sh logs`
2. Verify environment: `./deploy.sh status`
3. Review this documentation
4. Check GitHub issues

## 🔄 Updates

To update to a new version:

```bash
# Automatic update
./deploy.sh update

# Manual update
git pull
docker-compose build --no-cache
./deploy.sh restart
``` 