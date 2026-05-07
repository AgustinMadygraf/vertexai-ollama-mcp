# Estrategia de Self-Healing (Auto-Recuperación)

Este documento describe el diseño de un script de "Watchdog" para detectar y resolver automáticamente estados de `warning` o `error` en el puente MCP.

## 1. Detección de Problemas
El script monitorea el endpoint `/health` cada N segundos.

### Escenarios de Warning detectados:
1.  **HuggingFace Hub Unauthenticated**: Detectado en los logs de arranque.
2.  **Cloudflare Unconfigured**: Detectado en el payload de salud.
3.  **MCP Server Down**: Detectado si la lista de servidores activos está incompleta.

## 2. Resoluciones Automáticas Propuestas

### A. Warning de HuggingFace (HF_TOKEN)
- **Causa**: El modelo intenta verificar actualizaciones en el Hub sin token.
- **Resolución**: 
    1.  Verificar si el modelo ya existe en `~/.cache/huggingface`.
    2.  Si existe, inyectar `HF_HUB_OFFLINE=1` en el entorno antes de arrancar.
    3.  Si no existe, intentar una descarga silenciosa previa.

### B. Cloudflare Unconfigured
- **Causa**: Faltan variables en el `.env`.
- **Resolución**: 
    1.  El script de watchdog verifica si hay un túnel local corriendo (`cloudflared`).
    2.  Si existe, intenta extraer el ID del túnel automáticamente para actualizar el entorno.

### C. MCP Server Crash
- **Causa**: El subproceso del servidor MCP terminó inesperadamente.
- **Resolución**: 
    1.  Petición de reinicio en caliente (Hot Reload) al servidor web.

## 3. Script de Watchdog (Conceptual)

```python
import httpx
import os
import time

def check_and_fix():
    try:
        res = httpx.get("http://localhost:8000/health")
        data = res.json()
        
        if data["status"] == "warning":
            # Lógica de resolución para Cloudflare
            if data["infrastructure"]["cloudflare"]["status"] == "unconfigured":
                print("🔧 Intentando auto-configurar Cloudflare...")
                # Lógica para buscar credenciales o túneles activos
                
    except Exception:
        print("🚨 El bridge no responde. Intentando reinicio forzado...")
        # Lógica de reinicio
```

---

## 4. Auditoría de Observabilidad para el Script
- El script debe registrar sus propias acciones en `logs/watchdog.log`.
- No debe entrar en bucles de reinicio infinitos (Backoff exponencial).
