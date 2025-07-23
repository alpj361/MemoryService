"""
Configuración para Laura Memory Service - Producción
"""
import os
from typing import Optional


class Config:
    """Configuración base"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
    
    # Zep Configuration
    ZEP_API_KEY: Optional[str] = os.environ.get('ZEP_API_KEY')
    ZEP_URL: str = os.environ.get('ZEP_URL', 'https://api.getzep.com')
    
    # Laura Memory Configuration
    LAURA_SESSION_ID: str = os.environ.get('LAURA_SESSION_ID', 'laura_memory_session')
    LAURA_MEMORY_ENABLED: bool = os.environ.get('LAURA_MEMORY_ENABLED', 'true').lower() == 'true'
    LAURA_MEMORY_URL: str = os.environ.get('LAURA_MEMORY_URL', 'http://localhost:5001')
    
    # Server Configuration
    HOST: str = os.environ.get('HOST', '0.0.0.0')
    PORT: int = int(os.environ.get('PORT', 5001))
    DEBUG: bool = os.environ.get('DEBUG', 'false').lower() == 'true'
    
    # Production optimizations
    JSON_SORT_KEYS = False
    JSONIFY_PRETTYPRINT_REGULAR = False
    
    # Security headers
    SECURITY_HEADERS = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'Content-Security-Policy': "default-src 'self'"
    }


class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False
    TESTING = False
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', '/app/logs/laura-memory.log')
    
    # Performance
    SEND_FILE_MAX_AGE_DEFAULT = 31536000  # 1 year cache for static files


class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True
    TESTING = False
    LOG_LEVEL = 'DEBUG'


class TestingConfig(Config):
    """Configuración para testing"""
    DEBUG = True
    TESTING = True
    LOG_LEVEL = 'DEBUG'


# Mapping de configuraciones
config_mapping = {
    'production': ProductionConfig,
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'default': ProductionConfig
}


def get_config() -> Config:
    """Obtiene la configuración según el entorno"""
    env = os.environ.get('FLASK_ENV', 'production')
    return config_mapping.get(env, ProductionConfig)() 