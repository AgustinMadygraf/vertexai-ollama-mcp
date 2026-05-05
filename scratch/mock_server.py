from mcp.server.fastmcp import FastMCP

# Creamos un servidor MCP de prueba súper simple
mcp = FastMCP("mock-server")

@mcp.tool()
def ping() -> str:
    """Responde pong para verificar conectividad."""
    return "pong"

if __name__ == "__main__":
    mcp.run()
