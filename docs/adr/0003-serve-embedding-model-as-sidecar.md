# 3. Serve the embedding model as a sidecar container

## Status

Accepted

## Context

`lab3` runs the embedding model (nomic-embed-text-v1.5 via llama.cpp) as a
local process reachable over HTTP on `localhost:8080`. Moving this to a
Kubernetes cluster requires deciding how the model server is deployed
relative to the application (the MCP server / indexer) that calls it.

The sidecar pattern runs the model server as a second container inside the
same pod as the application container, sharing the pod's network namespace.
The application keeps calling `http://localhost:8080`, unchanged from the
current local setup.

## Alternatives considered

- **`llm-d`** — a Kubernetes-native distributed inference project (built
  on vLLM) for serving models at cluster scale: disaggregated
  prefill/decode, KV-cache-aware routing, an inference gateway shared
  across many callers. Rejected for this lab: it's built for scaling a
  model independently from its callers under real request volume and
  GPU cost — solving a problem (shared, elastically-scaled inference
  capacity) `lab3` doesn't have. It also targets vLLM-served models, not
  a llama.cpp CPU embedding server, so adopting it here would mean
  swapping the serving stack, not just the deployment topology.
- **A single shared embedding `Deployment`/`Service`**, called by every
  app pod over the network. Rejected for the same reason as `llm-d` at
  smaller scale: it trades this lab's low, predictable per-pod latency
  for a network hop, with no compensating benefit here since there's
  only one low-throughput CPU model and no independent-scaling need.

## Decision

Deploy llama.cpp as a sidecar container in the same pod as the MCP
server/indexer, rather than as a separate centralized service or `llm-d`.

## Consequences

**Positive:**
- Lowest possible latency for the embedding call: same pod means same
  node, traffic stays on loopback and never crosses the CNI overlay,
  kube-proxy/iptables, or a service mesh sidecar proxy — no network hop,
  no DNS/service resolution, no TLS handshake if mTLS is enforced
  cluster-wide.
- Predictable latency: the model is dedicated to this pod's requests
  only, so there's no queueing behind other callers hitting a shared
  central service (no noisy-neighbor/head-of-line blocking under load).
- Failure is isolated per pod: one pod's model crash doesn't affect other
  pods, and the app pod is never "up" without its model also being
  reachable (fate-shared lifecycle, easy to express via `restartPolicy`/
  readiness probes on the sidecar).

**Negative:**
- The model is duplicated in every pod replica, wasting memory/CPU (or
  GPU) compared to a shared, centrally-scaled model service.
- Each pod pays the model's startup/load time independently.
- Not a fit if the model needs to scale independently from the
  application (e.g. GPU-bound inference serving many callers) — `llm-d`
  (see Alternatives) would be the better choice there.

This tradeoff is acceptable for `lab3`'s scale (a single low-throughput
embedding model, CPU-only, small footprint); it would need revisiting for
a production deployment with meaningful request volume or GPU cost.
