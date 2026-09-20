# Changelog

1. llama.cpp running locally in embedding mode (nomic-embed-text-v1.5, see `docs/adr/0001`).
2. Added `run-llama-cpp-model` skill — makes serving a model repeatable, not manual.
3. Qdrant set up via Docker Compose as the vector store (Docker Hub image, for native arm64 support).
4. Built a generic, `.gitignore`-aware indexer for any file or directory.
5. Built a custom MCP server exposing retrieval as `search_indexed_content` (see `docs/adr/0002`).
6. Restructured and cleaned up the project for public release.
7. Recorded key decisions as ADRs (`docs/adr/`).
8. Added an ADR + ToDo on running the model in a cluster (`docs/adr/0003`) — sidecar vs. `llm-d`, decision only, not implemented.
