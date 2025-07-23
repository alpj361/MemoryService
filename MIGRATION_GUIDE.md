# Laura Memory Service - Migration Guide

## 🏗️ **Service Migration: ExtractorW → Independent**

La migración del servicio Laura Memory fuera de ExtractorW está **completa**. Este documento detalla los cambios y cómo usar el servicio independiente.

## 📂 **Nueva Estructura**

```
/Users/pj/Desktop/Pulse Journal/
├── ExtractorW/                     # Proyecto principal
│   └── server/services/
│       └── lauraMemoryClient.js    # Cliente actualizado
└── LauraMemoryService/             # Servicio independiente
    ├── .env                        # Configuración independiente
    ├── docker-compose.yml          # Docker independiente
    ├── Dockerfile                  # Dockerfile mejorado
    ├── start.sh                    # Script de inicio
    ├── server.py                   # Servidor Flask
    ├── memory.py                   # Lógica de memoria
    └── logs/                       # Directorio de logs
```

## 🚀 **Modos de Ejecución**

### **Opción 1: Docker (Recomendado)**

```bash
cd /Users/pj/Desktop/Pulse\ Journal/LauraMemoryService

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tu ZEP_API_KEY

# Iniciar con Docker
docker-compose up -d

# Verificar estado
docker-compose ps
curl http://localhost:5001/health
```

### **Opción 2: Local Development**

```bash
cd /Users/pj/Desktop/Pulse\ Journal/LauraMemoryService

# Usar script de inicio
./start.sh

# O manualmente
source venv/bin/activate
python server.py
```

## 🔧 **Configuración ExtractorW**

Actualiza el `.env` de ExtractorW para apuntar al servicio independiente:

```bash
# ExtractorW/.env
LAURA_MEMORY_URL=http://localhost:5001
LAURA_MEMORY_ENABLED=true
```

## 📋 **Variables de Entorno**

### **LauraMemoryService/.env**
```env
# Zep Cloud Configuration
ZEP_API_KEY=tu_api_key_aqui
ZEP_URL=https://api.getzep.com
LAURA_SESSION_ID=laura_memory_session

# Service Configuration
LAURA_MEMORY_ENABLED=true
LAURA_MEMORY_URL=http://localhost:5001
DEBUG=false
```

### **ExtractorW/.env**
```env
# Laura Memory Client
LAURA_MEMORY_URL=http://localhost:5001
LAURA_MEMORY_ENABLED=true
```

## 🧪 **Testing del Servicio**

```bash
# Health check
curl http://localhost:5001/health

# Test search
curl -X POST http://localhost:5001/api/laura-memory/search \
  -H "Content-Type: application/json" \
  -d '{"query": "test", "limit": 2}'

# Test stats
curl http://localhost:5001/api/laura-memory/stats
```

## 🐳 **Docker Commands**

```bash
# Iniciar servicio
docker-compose up -d

# Ver logs
docker-compose logs -f

# Parar servicio
docker-compose down

# Rebuild
docker-compose build --no-cache
```

## 🔄 **Beneficios de la Migración**

1. **Independencia**: Servicio con su propio ciclo de vida
2. **Escalabilidad**: Puede ejecutarse en diferentes hosts
3. **Configuración**: .env independiente sin conflictos
4. **Mantenimiento**: Más fácil actualizar y debuggear
5. **Docker**: Mejor containerización y despliegue

## 🚨 **Puntos Importantes**

- ✅ **Cliente JS actualizado** para conectar al servicio externo
- ✅ **Puerto 5001** sigue siendo el mismo
- ✅ **API endpoints** sin cambios
- ✅ **Compatibilidad** completa con ExtractorW
- ⚠️ **Zep API Key** necesaria para funcionalidad completa

## 📞 **Endpoints Disponibles**

- `GET /health` - Health check
- `POST /api/laura-memory/search` - Búsqueda semántica
- `POST /api/laura-memory/process-tool-result` - Procesar resultados
- `POST /api/laura-memory/enhance-query` - Mejorar queries
- `POST /api/laura-memory/save-user-discovery` - Guardar usuarios
- `GET /api/laura-memory/stats` - Estadísticas

## 🎯 **Next Steps**

1. **Configurar Zep API Key** en LauraMemoryService/.env
2. **Iniciar servicio** con Docker o localmente
3. **Verificar** que ExtractorW puede conectar al servicio
4. **Monitorear logs** para asegurar funcionamiento correcto

¡La migración está completa y el servicio está listo para usar independientemente! 🎉