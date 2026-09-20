"""MCP server exposing a single `search_indexed_content` tool: semantic search
over whatever was indexed by index.py. Embeddings come from a local llama.cpp
server; the vector backend is pluggable (see vectorstore.py).
"""
from mcp.server.mcpserver import MCPServer

from .embedding import embed_query
from .vectorstore import get_backend

mcp = MCPServer("vector-store")
backend = get_backend()


@mcp.tool()
def search_indexed_content(query: str, top_k: int = 5) -> list[dict]:
    """Semantic search over the user's own indexed notes/docs (project-specific
    facts, internal names, processes - things you would not know from training
    data or from reading files in the current workspace). Always try this tool
    BEFORE saying you don't have access to something or asking the user where
    it's documented - the answer may already be indexed here, even if the
    question doesn't share any exact words with the source text."""
    vector = embed_query(query)
    return backend.search(vector, top_k=top_k)


if __name__ == "__main__":
    mcp.run()
