# 1. Embedding model choice: nomic-embed-text-v1.5

## Status

Accepted

## Context

`lab3` needs a text embedding model that runs locally via llama.cpp
(a hard requirement of the lab), is small enough to run on a laptop CPU,
and produces good-enough retrieval quality for semantic search over
project docs/config files. The model was originally picked ad hoc; this
ADR reconsiders it against alternatives.

While using it, we hit a real limitation: even though nomic-embed-text-v1.5
is documented to extrapolate to an 8192-token context, the GGUF conversion
we run (`nomic-ai/nomic-embed-text-v1.5-GGUF`, Q8_0) doesn't carry the
context-extension metadata llama.cpp needs to unlock that — the server logs
"the slot context (8192) exceeds the training context of the model (2048) -
capping" and actually enforces 2048 tokens, regardless of `-c`/`-b`
flags. This forced `index.py` to split large files into ≤2048-token
chunks rather than embedding whole files.

## Alternatives considered

| Model | Dim | Native context | GGUF available | Notes |
|---|---|---|---|---|
| **nomic-embed-text-v1.5** (current) | 768 | 8192 (design), 2048 (this GGUF build) | Yes | Strong MTEB score, fully open (weights/data/training code), Matryoshka support. Context cap is a conversion artifact, not a model limit. |
| bge-small-en-v1.5 | 384 | 512 | Yes | Smaller/faster, but lower dimension (would require a `VECTOR_SIZE`/collection change) and a shorter native context than what we already hit limits on. |
| jina-embeddings-v2-base-en | 768 | 8192 (via ALiBi, holds in GGUF) | Yes | Same dimension as current (no vector-store schema change). ALiBi means the 8k context reliably survives GGUF conversion, unlike nomic's rope-scaling metadata. Scores below nomic-embed-text-v1 on MTEB long-context benchmarks. |
| mxbai-embed-large-v1 | 1024 | 512 | Yes | Larger and slower; context shorter than what we need. |

## Decision

Keep **nomic-embed-text-v1.5** (GGUF, Q8_0). It has the best retrieval
quality of the local, llama.cpp-compatible options considered, and its
768-dim output already matches the deployed Qdrant collection.

This choice was also shaped by constraints on this task: limited time and
limited firsthand expertise in evaluating embedding models, so the
comparison above leaned on published MTEB rankings and model-card
documentation rather than running our own benchmark against our own data.
Given those constraints, going with the model that the general
recommendation (MTEB leaderboard + community consensus) already favored
was the pragmatic choice, rather than an in-depth independent evaluation.

The 2048-token cap from this specific GGUF build is accepted, not fixed at
the model layer: `index.py` already chunks content to fit under it, so the
practical impact is bounded. If a future need requires embedding much
longer single passages without chunking, switch to
`jina-embeddings-v2-base-en` — same 768 dimensions, so no vector-store
change — rather than hunting for a nomic GGUF build with working
context-extension metadata.

## Consequences

- No change to `VECTOR_SIZE` / the existing Qdrant collection.
- Chunking in `index.py` remains necessary and is the correct fix, not a
  workaround to remove later.
- Revisit this ADR mainly if a code-specific (or otherwise
  domain-specialized) embedding model is found that's small and fast
  enough to run the same way — the point of this model is to be the
  foundation of the agent's memory system, so a model tuned for the kind
  of content actually being indexed would likely beat a general-purpose
  one at the same size/speed budget. Also revisit if we outgrow CPU-only
  local inference, need multilingual support (none of the above cover
  that well), or need genuinely long, unchunked context windows.
