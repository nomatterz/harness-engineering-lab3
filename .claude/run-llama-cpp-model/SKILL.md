---
name: run-llama-cpp-model
description: Run a user-specified model locally via llama.cpp. Use whenever the user asks to run, load, start, or serve a model locally, or mentions llama.cpp, GGUF, llama-server, or a local embedding/chat model for this project. Does NOT install llama.cpp itself — only verifies it's present and asks before doing anything else.
---

# Run a model locally with llama.cpp

This skill is scoped to the `lab3` project. Its job: get a model the user specifies actually running locally via llama.cpp, reachable over HTTP. It never installs llama.cpp itself without explicit approval, and it never picks a model on the user's behalf.

## 1. Verify llama.cpp is present

Current llama.cpp (per github.com/ggml-org/llama.cpp) ships a single unified `llama` CLI with subcommands (`llama serve`, `llama cli`), not separate `llama-server`/`llama-cli` binaries — those are the legacy names from older builds. Check both forms:

```
which llama-server llama-cli
which llama && llama version
```

If `llama` is found, confirm it's actually llama.cpp (not an unrelated tool of the same name) via `llama licenses` (should mention llama.cpp / ggml). This is the common case now — the rest of this skill leads with `llama serve`/`llama cli`; fall back to `llama-server`/`llama-cli` only when that's what `which` actually found.

If neither the legacy binaries nor the unified `llama` CLI are found:
- Stop here. Tell the user llama.cpp isn't installed and ask whether they want to install it themselves, or want you to install it (e.g. `brew install llama.cpp`).
- Do not install anything until they explicitly say yes. If they decline, stop — don't proceed to later steps.

If found, continue.

## 2. Ask the user which model to run

Don't guess or default to a specific model. Ask for:
- The model itself: a Hugging Face repo id + filename, a direct GGUF URL, or a local file path already on disk
- Quantization/variant, if the repo has multiple GGUF files (e.g. Q4_K_M vs Q8_0) and it isn't obvious which one they want
- Mode: chat/completion or embedding — this changes which server flags to use later

## 3. Get the model file

Depending on what they gave you:
- Hugging Face repo: prefer letting llama.cpp fetch it directly with `-hf <user>/<repo>[:quant]` at server-start time (step 4) — this needs no separate download step or `huggingface-cli`. Confirm the quant/tag with the user if the repo has multiple GGUF variants and it isn't obvious which one they want; `-hf` defaults to Q4_K_M or the first file in the repo if that quant doesn't exist. Use `-hff <file>` to pin an exact file instead of relying on the quant guess.
- Direct URL: download into `./models`
- Local path: confirm the file exists at that path; no need to copy it

This is a network fetch — treat it like any other internet access and get explicit user go-ahead before pulling from Hugging Face, whether via `-hf`, `huggingface-cli`, or a direct URL.

Verify it's a real GGUF file before trying to run it, e.g. `file ./models/<model>.gguf` should mention GGUF, or check the file starts with the GGUF magic bytes. (Not needed when using `-hf`/`-hff` — llama.cpp validates the file itself.)

## 4. Start the server

Chat/completion mode:
```
llama serve -m <model-path> --port 8080
# or, fetching straight from Hugging Face:
llama serve -hf <user>/<repo>[:quant] --port 8080
# legacy binary install:
llama-server -m <model-path> --port 8080
```

Embedding mode:
```
llama serve -m <model-path> --embedding --port 8080
# or:
llama serve -hf <user>/<repo>[:quant] --embedding --port 8080
# legacy binary install:
llama-server -m <model-path> --embedding --port 8080
```

If port 8080 is already in use, pick another free port and note it.

Run it in the background (e.g. Bash `run_in_background`) and capture the PID — you'll need it to stop the server later, since the unified `llama` CLI has no `stop`/`ps`/process-management subcommand (`llama help all` lists none). Stopping is always a plain `kill <pid>`, never a `llama` command.

The server logs a startup warning if CORS is open to all origins and no API key is set. That's fine for local-only use; if the port will be reachable beyond localhost, tell the user to add `--api-key <token>` and restrict CORS.

## 5. Confirm it's actually working

Don't just assume the server started — verify:
```
curl http://localhost:<port>/v1/models
```

Then smoke-test with a real request matching the mode:
- Chat: `curl http://localhost:<port>/v1/chat/completions -d '{"messages":[{"role":"user","content":"hello"}]}'`
- Embedding: `curl http://localhost:<port>/v1/embeddings -d '{"input":"test sentence"}'`

## 6. Report the outcome

Tell the user:
- Which model is running, in which mode, on which port
- How to stop it (`kill <pid>` — no `llama` subcommand does this; use Ctrl+C only if it was run in the foreground)
- How to restart it later (the exact `llama-server`/`llama serve`/`-hf` command used)
