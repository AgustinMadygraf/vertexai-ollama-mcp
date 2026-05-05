"""
Main entry point for MCP CLI Bridge.
"""
import typer
from src.adapters.cli.app import start

if __name__ == "__main__":
    # Usamos typer.run para que la función start sea el punto de entrada directo
    # Esto evita el error de "unexpected extra argument"
    typer.run(start)
