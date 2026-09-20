# 2. Custom Python MCP server with a backend-agnostic vector store

## Status

Accepted

## Context

We need an MCP tool that lets Claude Code search over locally-indexed
content. Retrieval requires: embedding the query via our local llama.cpp
server, then searching a vector database (Qdrant) for the closest stored
vectors.

The official `mcp-server-qdrant` package was considered first, since it
already exists and does exactly this on paper. It only supports embedding
through FastEmbed, an in-process ONNX runtime with its own bundled model
catalog — it has no way to call an external OpenAI-compatible endpoint.
Since testing llama.cpp itself is a hard requirement of this lab, that
package can't be used as-is.

## Decision

Write a small custom MCP server in Python, using the official `mcp` SDK
(`MCPServer`), rather than adapting `mcp-server-qdrant` or writing it in
another language:

- **Python**, because both the llama.cpp HTTP client and the Qdrant client
  library are simple `requests`/`qdrant-client` calls with no need for a
  different runtime, and the existing indexing script is already Python.
- **A single tool** (`search_indexed_content`) rather than exposing
  multiple low-level operations — the agent only ever needs retrieval;
  writes happen out-of-band via the one-time indexing script, not as an
  agent-facing tool.
- **A `VectorStore` `Protocol`** (`vectorstore.py`) sits between the MCP
  server / indexer and the concrete backend. Both `server.py` and
  `index.py` depend on `upsert`/`search`, never on `qdrant_client`
  directly. `get_backend()` reads `VECTOR_BACKEND` from the environment
  and returns the concrete implementation (`backends/qdrant_backend.py`
  today).

## Alternatives considered

- **Fork/patch `mcp-server-qdrant`** to add a llama.cpp embedding backend.
  Rejected: more code to understand and maintain in someone else's
  package structure than writing the ~30 lines this actually needs.
- **Call `qdrant_client` directly from `server.py`/`index.py`**, no
  abstraction layer. Rejected: couples both entry points to Qdrant
  specifically; the lab's own scope (evaluate different pieces of a local
  RAG stack) makes it likely the backend gets swapped or compared against
  alternatives later.
- **Expose separate `index`/`upsert` tools to the agent**, not just
  search. Rejected: indexing is a deliberate, reviewed, one-time bulk
  operation on the user's own data; letting the agent trigger writes
  turns an intentional pipeline into an implicit side effect of
  conversation.

## Consequences

- Swapping the vector backend later (e.g. to test an alternative to
  Qdrant) means adding one class under `backends/` — no change to
  `server.py` or `index.py`.
- The MCP server has no write path at all; re-indexing always requires
  explicitly running `index.py`, which is intentional but means content
  can go stale between indexing runs with no built-in staleness signal.
- Maintenance burden is on us, not upstream — the tradeoff for not being
  boxed in by `mcp-server-qdrant`'s embedding limitation.
