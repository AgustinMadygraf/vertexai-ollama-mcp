"""
Path: src/adapters/cli/app.py
"""
import asyncio
import os
import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.live import Live
from rich.table import Table

from src.adapters.mcp.process_manager import MultiProcessManager
from src.adapters.ai.local_gpu_adapter import LocalGPUAdapter
from src.core.application.orchestrator import Orchestrator
from src.adapters.settings.logger import logger

app = typer.Typer(
    help="MCP CLI Bridge - High Performance Edition",
    add_completion=False,
    no_args_is_help=True
)
console = Console()

async def interactive_loop():
    # El clear se hace en el comando que invoca este loop
    console.print(Panel.fit(
        "[bold blue]MCP CLI Bridge[/bold blue]\n"
        "[green]Motor Local-GPU Activado (OpenVINO Optimized)[/green]\n"
        "Escribe 'salir' para terminar.",
        title="[bold white]V1.0.0[/bold white]"
    ))

    # Inicialización de componentes
    mcp_manager = MultiProcessManager()
    ai_adapter = LocalGPUAdapter()
    orchestrator = Orchestrator(ai_adapter, mcp_manager)

    try:
        with console.status("[bold green]Encendiendo motores MCP...") as status:
            await mcp_manager.initialize()
            tools = await mcp_manager.list_tools()
            console.print(f"✅ [bold]{len(tools)}[/bold] herramientas detectadas en el sistema.")

        while True:
            user_input = Prompt.ask("\n[bold cyan]👤 Pregunta[/bold cyan]")
            
            if user_input.lower() in ["salir", "exit", "quit"]:
                break

            with console.status("[bold yellow]Procesando semánticamente...") as status:
                response = await orchestrator.process_message(user_input)
            
            console.print(Panel(response, title="[bold green]🤖 Respuesta[/bold green]", border_style="green"))

    except Exception as e:
        console.print(f"[bold red]Error fatal:[/bold red] {str(e)}")
        logger.error(f"Error fatal en CLI: {str(e)}", exc_info=True)
    finally:
        await mcp_manager.stop()
        console.print("[yellow]Sesión finalizada. Servidores MCP detenidos.[/yellow]")

def start():
    """Inicia la consola interactiva del puente MCP."""
    os.system('clear')
    os.system('clear')
    asyncio.run(interactive_loop())

if __name__ == "__main__":
    start()
