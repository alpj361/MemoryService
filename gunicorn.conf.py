"""
Configuración de Gunicorn para Laura Memory Service
"""
import multiprocessing
import os

# Server socket
bind = f"0.0.0.0:{os.environ.get('PORT', 5001)}"
backlog = 2048

# Worker processes
workers = int(os.environ.get('GUNICORN_WORKERS', multiprocessing.cpu_count() * 2 + 1))
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 50

# Restart workers after this many requests, with up to 50 random requests variation
# This helps prevent memory leaks
preload_app = True

# Logging
accesslog = "/app/logs/gunicorn_access.log"
errorlog = "/app/logs/gunicorn_error.log" 
loglevel = os.environ.get('LOG_LEVEL', 'info').lower()
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = 'laura-memory-service'

# Server mechanics
daemon = False
pidfile = '/tmp/gunicorn.pid'
tmp_upload_dir = None

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Performance tuning
worker_tmp_dir = '/dev/shm'  # Use RAM for worker temp files

def when_ready(server):
    """Called just after the server is started."""
    server.log.info("Laura Memory Service started successfully")

def worker_int(worker):
    """Called just after a worker has been reapped."""
    worker.log.info("Worker %s was killed", worker.pid)

def on_exit(server):
    """Called just before exiting."""
    server.log.info("Laura Memory Service shutting down") 