# 🚀 Quick Start - Laura Memory Service Production

## ⚡ Migración Rápida (5 minutos)

### 1. **Parar el servicio actual**
```bash
cd LauraMemoryService
docker-compose down
```

### 2. **Configurar variables de entorno**
```bash
# Copiar template
cp .env.example .env

# Editar configuración (IMPORTANTE: cambiar estos valores)
nano .env
```

**Variables críticas a configurar:**
```bash
ZEP_API_KEY=tu_api_key_de_zep_aqui
SECRET_KEY=genera_una_clave_secreta_aleatoria_aqui
```

### 3. **Hacer scripts ejecutables**
```bash
chmod +x deploy.sh monitoring.sh
```

### 4. **Deploy en producción**
```bash
# Opción A: Solo Laura Memory Service
./deploy.sh deploy

# Opción B: Con Nginx reverse proxy (RECOMENDADO)
./deploy.sh deploy-nginx
```

### 5. **Verificar que funciona**
```bash
# Ver estado
./deploy.sh status

# Health check
curl http://localhost:5001/health

# Ver métricas
curl http://localhost:5001/metrics
```

---

## 🎯 **¡Listo!** 

Tu servicio ahora corre con:
- ✅ **Gunicorn** (no más warnings de desarrollo)
- ✅ **4 workers** para mejor rendimiento  
- ✅ **Métricas** de Prometheus
- ✅ **Security headers** automáticos
- ✅ **Health checks** detallados
- ✅ **Logging estructurado**

---

## 📊 **Comandos Útiles**

```bash
# Monitoreo
./monitoring.sh health          # Estado de salud
./monitoring.sh watch           # Monitoreo en tiempo real
./monitoring.sh report          # Reporte completo

# Gestión
./deploy.sh restart             # Reiniciar servicio
./deploy.sh logs                # Ver logs
./deploy.sh stop                # Parar servicio

# Updates
./deploy.sh update              # Actualizar y redesplegar
```

---

**🎉 ¡Adiós advertencias de Flask dev server!** 

Ahora tienes un servicio **robusto** y **escalable** corriendo en **producción**. 