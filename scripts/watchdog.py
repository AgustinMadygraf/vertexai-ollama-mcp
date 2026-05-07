"""
Path: scripts/watchdog.py
Sistema de Auto-Recuperación y Monitoreo para MCP Bridge.
"""
import os
import time
import httpx
import subprocess
import signal
from rich.console import Console
from pathlib import Path

console = Console()

class MCPWatchdog:
    def __init__(self, target_script="web_main.py"):
        self.target_script = target_script
        self.process = None
        self.health_url = "http://localhost:8000/health"

    def get_env_with_healing(self):
        """Prepara el entorno resolviendo warnings conocidos."""
        env = os.environ.copy()
        
        # 1. Resolución para HuggingFace Hub Warning
        # Buscamos el modelo en la cache por defecto de transformers
        cache_dir = Path.home() / ".cache/huggingface/hub"
        model_exists = any(cache_dir.glob("**/models--sentence-transformers--all-MiniLM-L6-v2"))
        
        if model_exists:
            console.print("[bold green]✓[/bold green] Modelo local detectado. Activando [bold]HF_HUB_OFFLINE=1[/bold]")
            env["HF_HUB_OFFLINE"] = "1"
        else:
            console.print("[bold yellow]![/bold yellow] Modelo no encontrado en cache. Se requerirá descarga inicial.")

        return env

    def start_service(self):
        """Inicia el proceso del servidor web."""
        if self.process:
            self.stop_service()
        
        console.clear()
        console.print(f"[bold blue]🚀 Iniciando {self.target_script}...[/bold blue]")
        env = self.get_env_with_healing()
        
        self.process = subprocess.Popen(
            ["python3", self.target_script],
            env=env,
            # No capturamos stdout/stderr para que se vean en la consola principal
        )

    def stop_service(self):
        """Detiene el proceso del servidor web."""
        if self.process:
            console.print("[bold red]🛑 Deteniendo servicio...[/bold red]")
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            self.process = None

    async def run(self):
        """Bucle principal de monitoreo."""
        self.start_service()
        
        while True:
            try:
                # Esperamos un poco antes del primer chequeo
                time.sleep(10)
                
                async with httpx.AsyncClient() as client:
                    response = await client.get(self.health_url, timeout=5)
                    data = response.json()
                    
                    if data["status"] == "warning":
                        console.print("[bold yellow]⚠️ Alerta de Salud detectada:[/bold yellow]")
                        self.handle_warning(data)
                    
            except (httpx.ConnectError, httpx.TimeoutException):
                console.print("[bold red]🚨 El servicio no responde![/bold red] Intentando reiniciar...")
                self.start_service()
            except Exception as e:
                console.print(f"[dim]Watchdog check: {str(e)}[/dim]")
            
            time.sleep(30)

    def handle_warning(self, health_data):
        """Analiza y trata de resolver warnings específicos."""
        infra = health_data.get("infrastructure", {})
        cf = infra.get("cloudflare", {})
        
        if cf.get("status") == "unconfigured":
            console.print("   - [yellow]Cloudflare no está configurado.[/yellow] Revisa tu archivo .env")
        
        # Aquí se podrían añadir más lógicas de auto-reparación

if __name__ == "__main__":
    import asyncio
    watchdog = MCPWatchdog()
    
    # Manejo de cierre limpio
    def signal_handler(sig, frame):
        watchdog.stop_service()
        exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        asyncio.run(watchdog.run())
    except KeyboardInterrupt:
        watchdog.stop_service()
