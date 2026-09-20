# Lab 3 — Getting started

Steps to get this lab running from a fresh checkout.

1. Start Qdrant: `docker compose up -d`.
2. Start llama.cpp in embedding mode — use the `run-llama-cpp-model`
   skill (it checks llama.cpp is installed first), or run it directly
   (see `docs/adr/0001` for the model choice).
3. Index some content: from `vector_store/`, run
   `uv run python -m vector_store.index <file-or-directory>`.
4. Open a Claude Code session in this directory — `.mcp.json` wires up
   the `vector-store` MCP server automatically.
5. Ask a question whose answer only exists in what you indexed, and
   confirm Claude Code calls `search_indexed_content` to answer it.

## Cluster deployment (not implemented — see `docs/adr/0003`)

If/when this moves to a cluster, the decision is to run llama.cpp as a
sidecar container in the same pod as the app, not a shared/centralized
service or `llm-d`:

1. Add a second container to the app's pod spec running the llama.cpp
   image in embedding mode, same flags as local (`--embedding --port
   8080`), with the app still calling `http://localhost:8080`.
2. Set a readiness probe on the sidecar (e.g. `GET /v1/models`) and make
   the app's own readiness depend on it, so the pod is never "ready"
   without its model reachable.
3. Size CPU/memory requests for the sidecar the same as the current local
   process; there's no GPU or shared-scaling need at this lab's scale.
4. Revisit `llm-d` only if the model needs to scale independently from
   the app (real request volume, GPU cost) — that also means switching
   the serving stack from llama.cpp to vLLM, not just the deployment
   topology.

## Known follow-ups

- Re-evaluate the embedding model if a code-specific model small/fast
  enough is found (`docs/adr/0001`).
- Guard `embed_query` against long input — `index.py` already chunks
  documents to stay under the model's 2048-token limit; queries don't.
- Hybrid retrieval: combine metadata filtering with vector search for
  exact-match structured lookups (pure vector search struggles here).
