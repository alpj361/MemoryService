"""
Servidor HTTP para exponer la funcionalidad de Laura Memory al backend JavaScript.
Optimizado para producción con Gunicorn.
"""

from flask import Flask, request, jsonify, g
import logging
import structlog
import time
import os
from typing import Dict, Any
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

from integration import laura_memory_integration
from memory import search_public_memory, get_memory_stats
from political_graph import ensure_group_exists, search_political_context, ingest_batch
from config import get_config

# Configurar logging estructurado
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)

# Métricas de Prometheus
REQUEST_COUNT = Counter('laura_memory_requests_total', 'Total requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('laura_memory_request_duration_seconds', 'Request duration')

# Crear la aplicación Flask
def create_app():
    """Factory function para crear la aplicación Flask"""
    app = Flask(__name__)
    config = get_config()
    app.config.from_object(config)
    
    # Configurar logging para producción
    if not app.config['DEBUG']:
        logging.basicConfig(
            level=getattr(logging, config.LOG_LEVEL),
            format='%(asctime)s %(levelname)s %(name)s %(message)s'
        )
    
    return app

app = create_app()

# Middleware para métricas y seguridad
@app.before_request
def before_request():
    """Middleware ejecutado antes de cada request"""
    g.start_time = time.time()

@app.after_request
def after_request(response):
    """Middleware ejecutado después de cada request"""
    # Agregar headers de seguridad
    config = app.config
    if hasattr(config, 'SECURITY_HEADERS'):
        for header, value in config.SECURITY_HEADERS.items():
            response.headers[header] = value
    
    # Métricas
    if hasattr(g, 'start_time'):
        duration = time.time() - g.start_time
        REQUEST_DURATION.observe(duration)
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.endpoint or 'unknown',
            status=response.status_code
        ).inc()
    
    return response

@app.errorhandler(404)
def not_found(error):
    """Manejador de error 404"""
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    """Manejador de error 500"""
    logger.error("Internal server error", exc_info=True)
    return jsonify({"error": "Internal server error"}), 500

# Ensure the group graph exists at startup
try:
    ensure_group_exists()
    logger.info("✅ Political group graph initialized successfully")
except Exception as graph_err:
    logger.error("❌ Political group graph initialization failed", error=str(graph_err))


@app.route('/api/laura-memory/process-tool-result', methods=['POST'])
def process_tool_result():
    """
    Procesa el resultado de una herramienta y determina si guardarlo en memoria.
    
    Expected JSON:
    {
        "tool_name": "nitter_profile",
        "tool_result": {...},
        "user_query": "busca a Juan Pérez"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'tool_name' not in data or 'tool_result' not in data:
            return jsonify({"error": "Faltan campos requeridos"}), 400
        
        result = laura_memory_integration.process_tool_result(
            tool_name=data['tool_name'],
            tool_result=data['tool_result'],
            user_query=data.get('user_query', '')
        )
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"❌ Error procesando resultado de herramienta: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/laura-memory/enhance-query', methods=['POST'])
def enhance_query():
    """
    Mejora una query con información de la memoria.
    
    Expected JSON:
    {
        "query": "¿Qué pasó con el congreso?",
        "limit": 3
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({"error": "Falta el campo 'query'"}), 400
        
        result = laura_memory_integration.enhance_query_with_memory(
            query=data['query'],
            limit=data.get('limit', 3)
        )
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"❌ Error mejorando query: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/laura-memory/save-user-discovery', methods=['POST'])
def save_user_discovery():
    """
    Guarda información de un usuario descubierto con ML.
    
    Expected JSON:
    {
        "user_name": "Juan Pérez",
        "twitter_username": "juanperez_gt",
        "description": "Diputado del Congreso",
        "category": "politico"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'user_name' not in data or 'twitter_username' not in data:
            return jsonify({"error": "Faltan campos requeridos"}), 400
        
        success = laura_memory_integration.save_user_discovery(
            user_name=data['user_name'],
            twitter_username=data['twitter_username'],
            description=data.get('description', ''),
            category=data.get('category', '')
        )
        
        return jsonify({"success": success})
        
    except Exception as e:
        logger.error(f"❌ Error guardando usuario: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/laura-memory/search', methods=['POST'])
def search_memory():
    """
    Busca en la memoria pública.
    
    Expected JSON:
    {
        "query": "congreso",
        "limit": 5
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({"error": "Falta el campo 'query'"}), 400
        
        results = search_public_memory(
            query=data['query'],
            limit=data.get('limit', 5)
        )
        
        return jsonify({"results": results})
        
    except Exception as e:
        logger.error(f"❌ Error buscando en memoria: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/laura-memory/stats', methods=['GET'])
def memory_stats():
    """
    Obtiene estadísticas de la memoria.
    """
    try:
        stats = get_memory_stats()
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo estadísticas: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/politics/ingest', methods=['POST'])
def ingest_politics():
    """Ingest a batch of political facts into PulsePolitics group graph."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON body"}), 400
    try:
        ingest_batch(data)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/politics/search', methods=['POST'])
def search_politics():
    """Search PulsePolitics graph for relevant facts."""
    req = request.get_json()
    if not req or 'query' not in req:
        return jsonify({"error": "Field 'query' is required"}), 400
    query = req['query']
    limit = int(req.get('limit', 5))
    results = search_political_context(query, limit)
    return jsonify({"results": results})


@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint con información detallada.
    """
    try:
        # Verificar conexión a Zep
        stats = get_memory_stats()
        health_status = {
            "status": "healthy",
            "service": "laura-memory",
            "version": "1.0.0",
            "environment": app.config.get('FLASK_ENV', 'production'),
            "zep_connected": bool(stats),
            "timestamp": time.time()
        }
        return jsonify(health_status)
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        return jsonify({
            "status": "unhealthy",
            "service": "laura-memory",
            "error": str(e),
            "timestamp": time.time()
        }), 503

@app.route('/metrics', methods=['GET'])
def metrics():
    """
    Endpoint de métricas para Prometheus.
    """
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}


# Application factory para Gunicorn
def create_application():
    """Create and configure the Flask application for Gunicorn"""
    return app


if __name__ == '__main__':
    # Solo para desarrollo local - En producción usamos Gunicorn
    logger.warning("🚨 Running with Flask development server - Use Gunicorn for production!")
    config = get_config()
    app.run(
        host=config.HOST,
        port=config.PORT,
        debug=config.DEBUG
    )