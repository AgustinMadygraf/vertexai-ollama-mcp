"""
Path: scratch/smoke_test.py
"""
import asyncio
import sys
import os

# Añadimos el directorio raíz al path para poder importar src
sys.path.append(os.getcwd())

from src.adapters.mcp.process_manager import MultiProcessManager
from src.adapters.settings.logger import logger

async def run_smoke_test():
    print("🚀 Iniciando Smoke Test del MultiProcessManager...")
    manager = MultiProcessManager()
    
    try:
        print("📥 Inicializando servidores (esto puede tardar unos segundos)...")
        await manager.initialize()
        
        print("🔍 Listando herramientas detectadas:")
        tools = await manager.list_tools()
        
        if not tools:
            print("⚠️ No se detectaron herramientas. Revisa logs/app.log para más detalles.")
        else:
            for tool in tools:
                print(f" ✅ [{tool.server_name}] {tool.name}: {tool.description[:60]}...")
            print(f"\n✨ Éxito: Se detectaron {len(tools)} herramientas.")
            
    except Exception as e:
        print(f"❌ Error durante la prueba: {str(e)}")
    finally:
        print("🛑 Cerrando servidores...")
        await manager.stop()
        print("🏁 Prueba finalizada.")

if __name__ == "__main__":
    asyncio.run(run_smoke_test())
