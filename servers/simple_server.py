# server.py
from mcp.server.fastmcp import FastMCP

# Create an MCP server
mcp = FastMCP("SimpleServer")

# Add an addition tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b


@mcp.resource("resource://greeting")
def get_greeting() -> str:
    return "Hello from FastMCP Resources"



@mcp.prompt()
def math_assistant(problem: str) -> str:
    """Guide the agent to help solve a math problem using available tools."""
    return f"You are a math assistant. Help the user solve the following problem: {problem}. Use the add tool when you need to perform addition."


# Main execution block - this is required to run the server
if __name__ == "__main__":
    mcp.run()
    #mcp.run(transport='streamable-http')