# Lab 3 — llama.cpp + Qdrant + MCP

A learning lab, not a production system: it wires together local
embeddings (llama.cpp), a vector store (Qdrant), and an MCP tool
(`search_indexed_content`) so Claude Code can search locally-indexed
content, in order to explore how these pieces fit together.

## Where to look

- **`ToDo.md`** — start here: step-by-step instructions to get this
  running from a fresh checkout, plus known follow-ups.
- **`docs/adr/`** — why things are built the way they are (model choice,
  MCP server design, sidecar deployment).
- **`CHANGELOG.md`** — what's been done so far.
- **`vector_store/`** — the actual code: the indexer (`index.py`) and the
  MCP server (`server.py`).

## Quick start

See `ToDo.md`.
