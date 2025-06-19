from mcp.server.fastmcp import FastMCP

mcp = FastMCP(name="my-mcp-server", version="1.0.0")


@mcp.tool()
def add(a: int, b: int) -> int:
    return a + b


@mcp.tool()
def subtract(a: int, b: int) -> int:
    return a - b
