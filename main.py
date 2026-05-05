import asyncio
import argparse
import os
from src.infrastructure.factories.ai_engine_factory import AIEngineFactory
from src.infrastructure.factories.tool_gateway_factory import ToolGatewayFactory
from src.interface_adapters.controllers.telegram_controller import TelegramController
from src.interface_adapters.presenters.telegram_presenter import TelegramPresenter
from src.use_cases.process_message import ProcessMessageUseCase
from src.infrastructure.settings.config import settings
from src.infrastructure.persistence.sqlite_repository import SQLiteConversationRepository
from src.infrastructure.telegram.bot import TelegramBot
from src.infrastructure.telegram.handlers import TelegramHandlers
from src.infrastructure.settings.logger import configure_logger

from src.infrastructure.monitoring.system_monitor import SystemMonitor

from src.infrastructure.mcp.client import MCPClient

async def main():
    # Limpiar terminal al iniciar
    os.system('clear' if os.name != 'nt' else 'cls')
    
    # 0. Argument Parsing
    parser = argparse.ArgumentParser(description="Telegram Ollama MCP Bot")
    parser.add_argument("--debug", action="store_true", help="Habilita el modo de depuración")
    args = parser.parse_args()

    # Configurar logger según los argumentos
    configure_logger(args.debug)

    # 1. Start System Monitoring (Log mode)
    monitor = SystemMonitor()
    asyncio.create_task(monitor.start(interval=60))

    # 2. Infrastructure & Gateways
    ai_engine = AIEngineFactory.create()
    
    # Iniciamos el cliente MCP PERSISTENTE
    mcp_client = MCPClient(settings.mcp_command, settings.mcp_args)
    
    async with mcp_client:
        tool_gateway = ToolGatewayFactory.create(mcp_client)

        # --- NUEVO: Validador de Conexión ---
        print(f"🔍 Validando conexión con {settings.ai_provider.upper()}...")
        try:
            await ai_engine.validate_connection()
            print(f"✅ Conexión con {settings.ai_provider.upper()} exitosa.")
        except Exception as e:
            print(f"\n❌ ERROR DE CONEXIÓN: {str(e)}")
            print("Por favor, verifica tu configuración en el archivo .env\n")
            os._exit(1) # Salida inmediata y limpia para evitar ruidos de limpieza async
        # ------------------------------------

        # 3. Persistence (SQLite)
        conversation_repo = SQLiteConversationRepository("bot_data.db")
        await conversation_repo.initialize()

        # 4. Use Cases
        process_use_case = ProcessMessageUseCase(ai_engine, tool_gateway)

        # 5. Presenters
        telegram_presenter = TelegramPresenter()

        # 6. Controllers
        telegram_controller = TelegramController(
            process_message_use_case=process_use_case, 
            presenter=telegram_presenter,
            repository=conversation_repo
        )

        # 7. Telegram Infrastructure
        handlers = TelegramHandlers(telegram_controller)
        bot = TelegramBot(settings.telegram_token, handlers)

        # 8. Run
        await bot.run()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        # El bot ya maneja su propio log de salida, aquí solo salimos en silencio
        pass
